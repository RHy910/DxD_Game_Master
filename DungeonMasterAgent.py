from typing import Optional, Tuple
from langchain.chat_models import ChatOpenAI
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.schema import SystemMessage, HumanMessage

from ToneAnalyzer import ToneAnalyzer, ToneType
from CampaignState import CampaignState
from SceneManager import SceneManager
import dice
from tts import TTS





class DungeonMasterAgent:
    """Main LangChain agent that orchestrates the game"""
    
    def __init__(self, openai_api_key: str, model: str = "gpt-3.5-turbo", tts_enabled: bool = True):
        self.llm = ChatOpenAI(
            temperature=0.8,  # Creative but consistent
            model=model,
            openai_api_key=openai_api_key
        )

        # Initialize memory to keep track of conversation
        self.memory = ConversationBufferMemory(
            return_messages=True,
            memory_key="chat_history"
        )
        
        self.tone_analyzer = ToneAnalyzer()
        self.scene_manager = SceneManager()
        self.tts = TTS() if tts_enabled else None
        
    def create_system_prompt(self, state: CampaignState) -> str:
        """Generate dynamic system prompt based on campaign state"""
        
        tone_instructions = {
            ToneType.SERIOUS: "Use formal, dramatic language. Be descriptive and weighty.",
            ToneType.CASUAL: "Use casual, friendly language. Keep it conversational and light.",
            ToneType.HUMOROUS: "Match the player's humor. Add wit and levity where appropriate.",
            ToneType.DRAMATIC: "Use epic, sweeping language. Emphasize stakes and grandeur.",
            ToneType.NEUTRAL: "Use balanced, clear language. Adapt to player cues."
        }
        
        return f"""You are an expert Dungeon Master running a D&D 5e campaign. 

{state.to_context()}

=== YOUR ROLE ===
- Guide the story dynamically based on player choices
- Maintain consistency with established lore and decisions
- Create engaging NPCs with distinct personalities
- Balance challenge with fun
- ALWAYS respond to player actions with narrative consequences
- Use the pre-defined campaign structure but allow procedural branching

=== TONE ADAPTATION ===
Player's current tone: {state.player_tone}
{tone_instructions[state.player_tone]}

=== IMPORTANT RULES ===
1. NEVER control the player character's actions - only describe consequences
2. When combat occurs, ask for player's action before resolving
3. Track resources (HP, spell slots, items) implicitly
4. Weave in character backstory when relevant
5. Party members should occasionally contribute to conversations
6. End responses with a clear prompt for player action
7. Keep responses under 300 words unless describing a major scene

=== SCENE GENERATION ===
When describing new locations or major events, include vivid sensory details.
These moments may trigger cinematic video generation.

Continue the adventure based on the player's input."""

    def _analyze_player_tone(self, player_input: str, state: CampaignState) -> str:
        """Analyze player tone"""
        new_tone = self.tone_analyzer.analyze(player_input)
        if new_tone != state.player_tone:
            state.player_tone = new_tone
        return new_tone

    def _process_pending_check(self, player_input: str, state: CampaignState) -> Tuple[str, bool, Optional[str]]:
        """Process a pending mechanical check"""
        if state.pending_check is not None:
            if player_input.strip().lower().startswith('roll'):
                # Resolve the pending check using player's ability score
                pending = state.pending_check
                ability = pending.get('ability', 'str')
                dc = pending.get('dc', 10)

                # Map ability shorthand to player's stat (default to str)
                stat_map = {
                    'str': 'str', 'dex': 'dex', 'con': 'con',
                    'int': 'int', 'wis': 'wis', 'cha': 'cha'
                }
                stat_key = stat_map.get(ability.lower(), 'str')
                player_score = state.player_character.stats.get(stat_key, 10)

                # Optional: allow "roll 15" to force a roll (for testing)
                parts = player_input.strip().split()
                roll_override = None
                if len(parts) > 1 and parts[1].isdigit():
                    roll_override = int(parts[1])

                roll, mod, success, critical = dice.resolve_check(player_score, dc, roll_override)

                # Build a small narrative result for the player
                result_text = f"You rolled a {roll} + {mod} = {roll + mod} (DC {dc})."
                if critical:
                    result_text += " Critical success!" if roll == 20 else ""
                elif roll == 1:
                    result_text += " Critical failure!"

                result_text += "\n"

                # Ask the LLM to describe the consequence briefly, passing the mechanical result
                system_prompt = self.create_system_prompt(state)
                messages = [
                    SystemMessage(content=system_prompt),
                    HumanMessage(content=(f"Resolve the pending action: {pending['action']}. "
                                               f"Mechanical result: roll={roll}, modifier={mod}, total={roll+mod}, "
                                               f"DC={dc}, success={success}, critical={critical}. "
                                               "Return a short narrative consequence and any state changes."))
                ]

                response = self.llm(messages)
                dm_response = result_text + "\n" + response.content

                # Clear pending check
                state.clear_pending_check()
                # Speak the DM response if TTS enabled
                if getattr(self, 'tts', None):
                    try:
                        self.tts.speak(dm_response)
                    except Exception:
                        pass

            else:
                # Prompt the player to type 'roll' to resolve the pending check
                dm_response = ("A mechanical check is pending: please type 'roll' to resolve the action "
                                   f"(pending: {state.pending_check['action']}, DC {state.pending_check['dc']}).")

                # Update memory and return early (no scene generation)
                self.memory.chat_memory.add_user_message(player_input)
                self.memory.chat_memory.add_ai_message(dm_response)

                return dm_response, False, None

        else:
            # First, check if the player's action requires a roll
            system_prompt = self.create_system_prompt(state)
            
            # Ask LLM to determine if a roll is needed
            check_messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=(
                    f"Player action: '{player_input}'\n\n"
                    "Determine if this action requires a mechanical check (dice roll). "
                    "Respond with ONLY a JSON object in this exact format:\n"
                    '{"requires_roll": true/false, "ability": "str/dex/con/int/wis/cha", '
                    '"dc": 10-20, "action_description": "brief description"}\n\n'
                    "Require rolls for: risky physical actions, attempts to persuade/receive, "
                    "difficult knowledge checks, perception checks in important situations, "
                    "anything with meaningful chance of failure.\n"
                    "Don't require rolls for: simple conversation, looking around casually, "
                    "walking to obvious places, trivial actions."
                ))
            ]
            
            check_response = self.llm(check_messages)
            check_content = check_response.content.strip()
            
            # Parse the response to determine if roll is needed
            requires_roll = False
            try:
                # Try to extract JSON from the response
                import json
                import re
                
                # Look for JSON object in the response
                json_match = re.search(r'\{[^}]+\}', check_content)
                if json_match:
                    roll_info = json.loads(json_match.group())
                    requires_roll = roll_info.get('requires_roll', False)
                    
                    if requires_roll:
                        # Set up a pending check
                        state.set_pending_check(
                            action=roll_info.get('action_description', player_input),
                            ability=roll_info.get('ability', 'str'),
                            dc=roll_info.get('dc', 10)
                        )
                        
                        dm_response = (
                            f"You attempt to {roll_info.get('action_description', player_input)}.\n"
                            f"This requires a {roll_info.get('ability', 'STR').upper()} check "
                            f"(DC {roll_info.get('dc', 10)}).\n"
                            "Type 'roll' to make your attempt!"
                        )
                        
                        # Update memory and return
                        self.memory.chat_memory.add_user_message(player_input)
                        self.memory.chat_memory.add_ai_message(dm_response)
                        
                        # Speak if TTS enabled
                        if getattr(self, 'tts', None):
                            try:
                                self.tts.speak(dm_response)
                            except Exception:
                                pass
                         
                        return dm_response, False, None
                        
            except (json.JSONDecodeError, ValueError) as e:
                # If parsing fails, assume no roll needed and continue normally
                print(f"Failed to parse roll check response: {e}")
                requires_roll = False

    def process_turn(self, player_input: str, state: CampaignState) -> Tuple[str, bool, Optional[str]]:
        """Process a single turn of gameplay"""
        state.turn_count += 1

        # Analyze player tone
        new_tone = self._analyze_player_tone(player_input, state)
        
        # If there's a pending mechanical check, expect the player to type 'roll'
        if state.pending_check is not None:
            result = self._process_pending_check(player_input, state)
            return result
        
        else:
            # First, check if the player's action requires a roll
            system_prompt = self.create_system_prompt(state)
            
            # Ask LLM to determine if a roll is needed
            check_messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=(
                    f"Player action: '{player_input}'\n\n"
                    "Determine if this action requires a mechanical check (dice roll). "
                    "Respond with ONLY a JSON object in this exact format:\n"
                    '{"requires_roll": true/false, "ability": "str/dex/con/int/wis/cha", '
                    '"dc": 10-20, "action_description": "brief description"}\n\n'
                    "Require rolls for: risky physical actions, attempts to persuade/receive, "
                    "difficult knowledge checks, perception checks in important situations, "
                    "anything with meaningful chance of failure.\n"
                    "Don't require rolls for: simple conversation, looking around casually, "
                    " walking to obvious places, trivial actions."
                ))
            ]
            
            check_response = self.llm(check_messages)
            check_content = check_response.content.strip()
            
            # Parse the response to determine if roll is needed
            requires_roll = False
            try:
                # Try to extract JSON from the response
                import json
                import re
                
                # Look for JSON object in the response
                json_match = re.search(r'\{[^}]+\}', check_content)
                if json_match:
                    roll_info = json.loads(json_match.group())
                    requires_roll = roll_info.get('requires_roll', False)
                    
                    if requires_roll:
                        # Set up a pending check
                        state.set_pending_check(
                            action=roll_info.get('action_description', player_input),
                            ability=roll_info.get('ability', 'str'),
                            dc=roll_info.get('dc', 10)
                        )
                        
                        dm_response = (
                            f"You attempt to {roll_info.get('action_description', player_input)}.\n"
                            f"This requires a {roll_info.get('ability', 'STR').upper()} check "
                            f"(DC {roll_info.get('dc', 10)}).\n"
                            "Type 'roll' to make your attempt!"
                        )
                        
                        # Update memory and return
                        self.memory.chat_memory.add_user_message(player_input)
                        self.memory.chat_memory.add_ai_message(dm_response)
                        
                        # Speak if TTS enabled
                        if getattr(self, 'tts', None):
                            try:
                                self.tts.speak(dm_response)
                            except Exception:
                                pass
                         
                        return dm_response, False, None
                        
            except (json.JSONDecodeError, ValueError) as e:
                # If parsing fails, assume no roll needed and continue normally
                print(f"Failed to parse roll check response: {e}")
                requires_roll = False

        # If no roll needed, proceed with normal LLM response
        messages = [
            SystemMessage(content=self.create_system_prompt(state)),
            HumanMessage(content=player_input)
        ]

        # Get DM response
        response = self.llm(messages)
        dm_response = response.content

        # Determine if new scene needed
        should_generate = self.scene_manager.should_trigger_new_scene(
            dm_response,
            state
        )

        sora_prompt = None
        if should_generate:
            new_location = state.current_scene.location
            new_scene = self.scene_manager.create_scene_from_narrative(dm_response, new_location)
            state.change_scene(new_scene)
            sora_prompt = new_scene.sora_prompt

        # Update memory
        self.memory.chat_memory.add_user_message(player_input)
        self.memory.chat_memory.add_ai_message(dm_response)

        # Speak if TTS enabled
        if getattr(self, 'tts', None):
            try:
                self.tts.speak(dm_response)
            except Exception:
                pass

        return dm_response, should_generate, sora_prompt

