
from dataclasses import dataclass, field
from sqlalchemy import Enum

from datetime import datetime
from typing import Optional, List
from enum import Enum

class SceneType(Enum):
    """Types of scenes for Sora generation"""
    EXPLORATION = "exploration"
    COMBAT = "combat"
    DIALOGUE = "dialogue"
    REVELATION = "revelation"
    TRANSITION = "transition"

@dataclass
class Scene:
    """Represents a game scene/location"""
    id: str
    title: str
    description: str
    scene_type: SceneType
    location: str
    npcs_present: List[str] = field(default_factory=list)
    items_present: List[str] = field(default_factory=list)
    exits: List[str] = field(default_factory=list)
    danger_level: int = 0
    sora_prompt: Optional[str] = None
    
    def generate_sora_prompt(self) -> str:
        """Generate visual prompt for Sora"""
        style = "cinematic fantasy art style, detailed environment, atmospheric lighting"
        
        if self.scene_type == SceneType.COMBAT:
            action = "dynamic action scene, weapons drawn, intense atmosphere"
        elif self.scene_type == SceneType.DIALOGUE:
            action = "character interaction, detailed facial expressions, tavern or gathering place"
        elif self.scene_type == SceneType.EXPLORATION:
            action = "wide establishing shot, sense of adventure and discovery"
        else:
            action = "dramatic storytelling moment, emotional depth"
            
        prompt = f"{self.description}. {action}. {style}. High quality render, 4K."
        self.sora_prompt = prompt
        return prompt


class SceneManager:
    
    """Manages scene transitions and generation"""
    
    @staticmethod
    def should_trigger_new_scene(dm_response: str, state: "CampaignState") -> bool:
        """Determine if response warrants new Sora scene"""
        trigger_phrases = [
            'you enter', 'you arrive', 'you see', 'appears before you',
            'the scene changes', 'you find yourself', 'reveals',
            'emerges', 'you discover', 'landscape', 'chamber', 'room'
        ]
        
        response_lower = dm_response.lower()
        
        # Check for trigger phrases
        for phrase in trigger_phrases:
            if phrase in response_lower:
                return True
                
        # Check if significant state change
        if state.turn_count % 5 == 0:  # Every 5 turns, consider new scene
            return True
            
        return False
    
    @staticmethod
    def create_scene_from_narrative(narrative: str, location: str) -> Scene:
        """Create scene object from DM narrative"""
        # This is simplified - in production you'd use another LLM call
        # to extract structured scene data
        
        scene_id = f"scene_{datetime.now().timestamp()}"
        
        # Determine scene type from narrative
        scene_type = SceneType.EXPLORATION
        if any(word in narrative.lower() for word in ['attack', 'combat', 'fight', 'battle']):
            scene_type = SceneType.COMBAT
        elif any(word in narrative.lower() for word in ['talk', 'speak', 'conversation', 'asks']):
            scene_type = SceneType.DIALOGUE
        elif any(word in narrative.lower() for word in ['discover', 'reveal', 'ancient', 'secret']):
            scene_type = SceneType.REVELATION
            
        scene = Scene(
            id=scene_id,
            title=location,
            description=narrative[:200],  # First 200 chars
            scene_type=scene_type,
            location=location
        )
        
        scene.generate_sora_prompt()
        return scene