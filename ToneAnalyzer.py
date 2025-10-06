
from typing import List
from enum import Enum


class ToneType(Enum):
    """Player communication tone"""
    SERIOUS = "serious"
    CASUAL = "casual"
    HUMOROUS = "humorous"
    DRAMATIC = "dramatic"
    NEUTRAL = "neutral"
    
class ToneAnalyzer:
    """Analyzes player input to determine communication tone"""
    
    TONE_KEYWORDS = {
        ToneType.SERIOUS: [
            'oath', 'honor', 'duty', 'swear', 'justice', 'investigate',
            'carefully', 'vigilant', 'pledge', 'vow', 'sacred'
        ],
        ToneType.HUMOROUS: [
            'lol', 'haha', 'lmao', 'joke', 'funny', 'ridiculous',
            'absurd', 'ironic', 'sarcastic', 'meme'
        ],
        ToneType.CASUAL: [
            'yo', 'hey', 'sup', 'cool', 'chill', 'yeah', 'gonna',
            'wanna', 'kinda', 'sorta', 'nah'
        ],
        ToneType.DRAMATIC: [
            'fate', 'destiny', 'doom', 'glory', 'epic', 'legendary',
            'heroic', 'sacrifice', 'prophecy', 'ancient'
        ]
    }
    
    @staticmethod
    def analyze(text: str, history: List[str] = None) -> ToneType:
        """Analyze text to determine tone"""
        text_lower = text.lower()
        
        # Count keyword matches
        scores = {tone: 0 for tone in ToneType}
        
        for tone, keywords in ToneAnalyzer.TONE_KEYWORDS.items():
            for keyword in keywords:
                if keyword in text_lower:
                    scores[tone] += 1
        
        # Check formality through sentence structure
        if '.' in text and len(text.split('.')) > 2:
            scores[ToneType.SERIOUS] += 1
            
        if '!' in text or '?' in text:
            scores[ToneType.DRAMATIC] += 1
            
        # Return highest scoring tone, default to neutral
        max_score = max(scores.values())
        if max_score == 0:
            return ToneType.NEUTRAL
            
        return max(scores, key=scores.get)