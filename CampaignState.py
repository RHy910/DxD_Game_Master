from SceneManager import Scene
from ToneAnalyzer import ToneType
from Player import Character
from Party import PartyMember
from dataclasses import dataclass, field
from typing import List, Dict
from datetime import datetime



@dataclass
class CampaignState:
    """Maintains the entire campaign state"""
    campaign_id: str
    campaign_name: str
    current_scene: Scene
    player_character: Character
    party_members: List[PartyMember]
    
    # State tracking
    player_tone: ToneType = ToneType.NEUTRAL
    story_beats_completed: List[str] = field(default_factory=list)
    decisions_made: List[Dict] = field(default_factory=list)
    scenes_visited: List[str] = field(default_factory=list)
    
    # Narrative tracking
    main_quest_progress: int = 0
    side_quests: List[Dict] = field(default_factory=list)
    npcs_met: Dict[str, Dict] = field(default_factory=dict)
    world_state: Dict[str, any] = field(default_factory=dict)
    
    # Session info
    turn_count: int = 0
    scenes_generated: int = 0
    # Pending roll/check awaiting player to type "roll"
    pending_check: dict = None
    
    def add_story_beat(self, beat: str):
        """Track major story progression"""
        if beat not in self.story_beats_completed:
            self.story_beats_completed.append(beat)
            
    def record_decision(self, decision: str, outcome: str):
        """Record player decision for branching"""
        self.decisions_made.append({
            'turn': self.turn_count,
            'decision': decision,
            'outcome': outcome,
            'timestamp': datetime.now().isoformat()
        })
        
    def change_scene(self, new_scene: Scene):
        """Transition to new scene"""
        self.scenes_visited.append(self.current_scene.id)
        self.current_scene = new_scene
        self.scenes_generated += 1

    def set_pending_check(self, action: str, ability: str, dc: int):
        """Register a pending mechanical check that the player must 'roll' to resolve."""
        self.pending_check = {
            'action': action,
            'ability': ability,
            'dc': dc,
            'turn': self.turn_count,
        }

    def clear_pending_check(self):
        self.pending_check = None
        
    def to_context(self) -> str:
        """Generate context for LLM"""
        party_context = "\n".join([p.to_context() for p in self.party_members])
        
        return f"""
            === CAMPAIGN STATE ===
            Campaign: {self.campaign_name}
            Turn: {self.turn_count}

            {self.player_character.to_context()}

            Party Members:
            {party_context if party_context else "None"}

            Current Location: {self.current_scene.location}
            Scene: {self.current_scene.title}
            {self.current_scene.description}

            NPCs Present: {', '.join(self.current_scene.npcs_present) if self.current_scene.npcs_present else 'None'}

            Story Progress: {len(self.story_beats_completed)} major beats completed
            Recent Decisions: {len(self.decisions_made)} choices made

            Player Tone: {self.player_tone} (adapt your language accordingly)
            """