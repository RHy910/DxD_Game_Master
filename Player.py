
from dataclasses import dataclass
from typing import Dict


@dataclass
class Character:
    """Player character data"""
    name: str
    race: str
    char_class: str
    level: int
    background: str
    alignment: str
    stats: Dict[str, int]
    backstory: str
    hp_current: int
    hp_max: int
    
    def to_context(self) -> str:
        """Convert character to context string for LLM"""
        return f"""
            Character: {self.name}
            Race: {self.race} | Class: {self.char_class} | Level: {self.level}
            Background: {self.background} | Alignment: {self.alignment}
            Stats: STR {self.stats['str']}, DEX {self.stats['dex']}, CON {self.stats['con']}, 
                INT {self.stats['int']}, WIS {self.stats['wis']}, CHA {self.stats['cha']}
            HP: {self.hp_current}/{self.hp_max}
            Backstory: {self.backstory}
            """