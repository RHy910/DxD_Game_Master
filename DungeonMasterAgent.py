from datetime import datetime
from typing import List, Optional, Tuple
from langchain.chat_models import ChatOpenAI
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.schema import SystemMessage, HumanMessage, AIMessage

from ToneAnalyzer import ToneAnalyzer, ToneType
from CampaignState import CampaignState
from SceneManager import SceneManager,Scene, SceneType
from Player import Character
from Party import PartyMember





class DungeonMasterAgent:
    """Main LangChain agent that orchestrates the game"""
    
    def __init__(self, openai_api_key: str, model: str = "gpt-4"):
        self.llm = ChatOpenAI(
            temperature=0.8,  # Creative but consistent
            model=model,
            openai_api_key=openai_api_key
        )
        
        self.memory = ConversationBufferMemory(
            return_messages=True,
            memory_key="chat_history"
        )
        
        self.tone_analyzer = ToneAnalyzer()
        self.scene_manager = SceneManager()
        
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

    def process_turn(
        self, 
        player_input: str, 
        state: CampaignState
    ) -> Tuple[str, bool, Optional[str]]:
        """
        Process a single turn of gameplay
        
        Returns:
            (dm_response, should_generate_scene, sora_prompt)
        """
        state.turn_count += 1
        
        # Analyze player tone
        new_tone = self.tone_analyzer.analyze(player_input)
        if new_tone != state.player_tone:
            state.player_tone = new_tone
        
        # Create messages for LLM
        system_prompt = self.create_system_prompt(state)
        
        messages = [
            SystemMessage(content=system_prompt),
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
            # Extract location from response (simplified)
            new_location = state.current_scene.location  # Could parse from response
            new_scene = self.scene_manager.create_scene_from_narrative(
                dm_response,
                new_location
            )
            state.change_scene(new_scene)
            sora_prompt = new_scene.sora_prompt
        
        # Update memory
        self.memory.chat_memory.add_user_message(player_input)
        self.memory.chat_memory.add_ai_message(dm_response)
        
        return dm_response, should_generate, sora_prompt
    
    def start_campaign(
        self,
        campaign_name: str,
        player_character: Character,
        party_members: List[PartyMember] = None
    ) -> Tuple[CampaignState, str]:
        """
        Initialize a new campaign
        
        Returns:
            (initial_state, opening_narration)
        """
        # Load campaign template (in production, this would load from DB/files)
        opening_scene = Scene(
            id="scene_start",
            title="The Journey Begins",
            description="The adventure starts in the bustling market square of Millhaven",
            scene_type=SceneType.EXPLORATION,
            location="Millhaven Market Square",
            npcs_present=["Town Guard Captain", "Merchant Vendors"],
            exits=["East Road", "Town Hall", "Tavern"]
        )
        opening_scene.generate_sora_prompt()
        
        state = CampaignState(
            campaign_id=f"campaign_{datetime.now().timestamp()}",
            campaign_name=campaign_name,
            current_scene=opening_scene,
            player_character=player_character,
            party_members=party_members or []
        )
        
        # Generate opening narration
        system_prompt = self.create_system_prompt(state)
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content="Begin the campaign with an engaging introduction that sets the scene and presents the initial hook.")
        ]
        
        response = self.llm(messages)
        opening_narration = response.content
        
        self.memory.chat_memory.add_ai_message(opening_narration)
        
        return state, opening_narration