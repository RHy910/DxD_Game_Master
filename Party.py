from attr import dataclass


@dataclass
class PartyMember:
    """AI-controlled party member"""
    name: str
    race: str
    char_class: str
    level: int
    personality: str
    relationship_with_player: str
    
    def to_context(self) -> str:
        return f"{self.name} ({self.race} {self.char_class} Lvl {self.level}) - {self.personality}"
