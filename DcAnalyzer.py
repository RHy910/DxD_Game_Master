from typing import Tuple
from enum import IntEnum

class DifficultyLevel(IntEnum):
    VERY_EASY = 5
    EASY = 10
    MODERATE = 15
    HARD = 20
    VERY_HARD = 25
    NEARLY_IMPOSSIBLE = 30

class DCAnalyzer:
    """Analyzes natural language to suggest appropriate Difficulty Classes"""
    
    # Base DCs for different contexts
    BASE_DCS = {
        'very_easy': DifficultyLevel.VERY_EASY,
        'easy': DifficultyLevel.EASY,
        'moderate': DifficultyLevel.MODERATE,
        'hard': DifficultyLevel.HARD,
        'very_hard': DifficultyLevel.VERY_HARD,
        'nearly_impossible': DifficultyLevel.NEARLY_IMPOSSIBLE,
    }
    
    # Difficulty modifiers by environment/condition
    ENVIRONMENT_MODIFIERS = {
        'dark': 5,
        'wet': 3,
        'icy': 5,
        'slick': 4,
        'storm': 5,
        'fog': 3,
        'underground': 2,
        'shallow': -3,
        'calm': -2,
        'ideal': -3,
        'perfect': -4,
    }
    
    # Task complexity keywords
    TASK_KEYWORDS = {
        'climb': {'base': 'moderate', 'skill': 'Athletics'},
        'swim': {'base': 'moderate', 'skill': 'Athletics'},
        'jump': {'base': 'easy', 'skill': 'Athletics'},
        'persuade': {'base': 'moderate', 'skill': 'Persuasion'},
        'deceive': {'base': 'moderate', 'skill': 'Deception'},
        'sneak': {'base': 'moderate', 'skill': 'Stealth'},
        'hide': {'base': 'moderate', 'skill': 'Stealth'},
        'pick': {'base': 'moderate', 'skill': 'Sleight of Hand'},
        'lock': {'base': 'hard', 'skill': 'Lockpicking'},
        'trap': {'base': 'hard', 'skill': 'Investigation'},
        'magic': {'base': 'hard', 'skill': 'Arcana'},
        'ancient': {'base': 'hard', 'skill': 'History'},
        'arcane': {'base': 'hard', 'skill': 'Arcana'},
        'identify': {'base': 'moderate', 'skill': 'Investigation'},
        'track': {'base': 'hard', 'skill': 'Survival'},
        'recall': {'base': 'easy', 'skill': 'Knowledge'},
    }
    
    # Intensity modifiers
    INTENSITY_KEYWORDS = {
        'trivial': -5,
        'simple': -3,
        'basic': -2,
        'challenging': 3,
        'difficult': 5,
        'very difficult': 8,
        'extremely': 7,
        'nearly impossible': 10,
        'masterwork': 4,
        'ornate': 3,
        'intricate': 5,
        'elaborate': 4,
    }
    
    # Danger/consequence keywords
    CONSEQUENCE_KEYWORDS = {
        'deadly': 8,
        'lethal': 8,
        'dangerous': 5,
        'risky': 3,
        'fail': 2,
        'fall': 4,
        'combat': 3,
        'guarded': 4,
        'watched': 3,
    }
    
    @staticmethod
    def suggest_dc(text: str) -> Tuple[int, str]:
        """
        Analyze natural language to suggest an appropriate DC.
        
        Args:
            text: Natural language description (e.g., "try to climb the icy wall")
        
        Returns:
            Tuple of (suggested_dc, reasoning)
        """
        if not text or not isinstance(text, str):
            return DifficultyLevel.MODERATE, "No input provided; assuming moderate task."
        
        t = text.lower()
        base_dc = DifficultyLevel.MODERATE
        modifiers = []
        identified_skill = None
        
        # Step 1: Identify task type from keywords
        for keyword, task_info in DCAnalyzer.TASK_KEYWORDS.items():
            if keyword in t:
                base_dc = DCAnalyzer.BASE_DCS[task_info['base']]
                identified_skill = task_info['skill']
                modifiers.append(f"Task type: {keyword} ({task_info['skill']}) → base DC {base_dc}")
                break
        
        # Step 2: Check environment/condition modifiers
        for condition, modifier in DCAnalyzer.ENVIRONMENT_MODIFIERS.items():
            if condition in t:
                modifiers.append(f"Environment: {condition} ({modifier:+d})")
                base_dc += modifier
        
        # Step 3: Check intensity modifiers
        for intensity, modifier in DCAnalyzer.INTENSITY_KEYWORDS.items():
            if intensity in t:
                modifiers.append(f"Intensity: {intensity} ({modifier:+d})")
                base_dc += modifier
                break  # Use first matched intensity
        
        # Step 4: Check consequence modifiers
        for consequence, modifier in DCAnalyzer.CONSEQUENCE_KEYWORDS.items():
            if consequence in t:
                modifiers.append(f"Consequence: {consequence} ({modifier:+d})")
                base_dc += modifier
                break  # Use first matched consequence
        
        # Step 5: Clamp DC to valid range
        final_dc = max(5, min(base_dc, 30))
        
        # Build reasoning string
        reasoning = " → ".join(modifiers) if modifiers else "Standard moderate task"
        if final_dc != base_dc:
            reasoning += f" → clamped to {final_dc}"
        
        return final_dc, reasoning
    
    @staticmethod
    def get_difficulty_name(dc: int) -> str:
        """Convert DC number to difficulty name"""
        for name, value in DCAnalyzer.BASE_DCS.items():
            if value == dc:
                return name.replace('_', ' ').title()
        return "Custom"


# Example usage
if __name__ == "__main__":
    test_cases = [
        "try to climb the icy wall",
        "persuade the guard to let us pass",
        "pick the ancient lock in the dark",
        "sneak past the guards",
        "recall information about arcane magic",
        "swim across the stormy river",
        "deceive the merchant",
    ]
    
    for test in test_cases:
        dc, reasoning = DCAnalyzer.suggest_dc(test)
        difficulty = DCAnalyzer.get_difficulty_name(dc)
        print(f"\n📋 '{test}'")
        print(f"   DC: {dc} ({difficulty})")
        print(f"   Reasoning: {reasoning}")