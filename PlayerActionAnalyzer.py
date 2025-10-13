"""Heuristic player action analyzer

This module provides a lightweight analyzer that converts free-form player input
into a small structured intent representation the DM agent can use to decide
whether a mechanical check is needed and which ability/DC to request.

It is intentionally heuristic and small and should not be relied on!!!!.

API:
    analyze_action(text: str) -> dict

Returned dict keys:
  - intent: one of ('move','attack','investigate',' persuade','sneak','interact','other')
  - ability: suggested ability short name ('str','dex','int','wis','cha','con')
  - dc: suggested difficulty class (int)
  - requires_check: bool
  - reason: short text explaining suggestion

Examples:
    analyze_action("I try to pick the lock on the chest")
    -> {intent: 'investigate', ability: 'dex', dc: 15, requires_check: True, ...}
"""

import re
from DcAnalyzer import DCAnalyzer


class PlayerActionAnalyzer:
    DEFAULT_DCS = {
        'easy': 10,
        'medium': 15,
        'hard': 20
    }

    # Intent keywords mapping
    INTENT_KEYWORDS = {
        'attack': ['attack', 'hit', 'strike', 'swing', 'shoot', 'stab', 'bash'],
        'investigate': ['search', 'look', 'inspect', 'investigate', 'examine', 'check', 'open', 'pick'],
        'persuade': ['persuade', 'convince', 'bribe', 'charm', 'negotiate', 'ask'],
        'sneak': ['sneak', 'hide', 'stealth', 'creep', 'tiptoe'],
        'interact': ['take', 'grab', 'use', 'pick up', 'talk to', 'speak to', 'trade', 'give'],
        'move': ['go', 'move', 'walk', 'run', 'approach', 'enter', 'leave'],
    }

    INTENT_TO_ABILITY = {
        'attack': 'str',
        'investigate': 'int',
        'persuade': 'cha',
        'sneak': 'dex',
        'interact': 'dex',
        'move': 'dex'
    }

    def __init__(self):
        pass

    @staticmethod
    def find_intent(text: str) -> str:
        t = text.lower()
        for intent, keywords in PlayerActionAnalyzer.INTENT_KEYWORDS.items():
            for k in keywords:
                if k in t:
                    return intent
        return 'other'

    @staticmethod
    def analyze_action(text: str) -> dict:
        intent = PlayerActionAnalyzer.find_intent(text)
        ability = PlayerActionAnalyzer.INTENT_TO_ABILITY.get(intent, 'str')
        dc = DCAnalyzer.suggest_dc(text)

        # decide if this action should require a check
        requires_check = False
        reason_parts = []

        if intent in ('attack', 'investigate', 'persuade', 'sneak'):
            requires_check = True
            reason_parts.append(f"intent '{intent}' typically requires a check")

        # Some verbs strongly indicate checks
        if re.search(r'pick the lock|disarm trap|climb|jump|leap|pickpocket', text.lower()):
            requires_check = True
            reason_parts.append('detected risky verb (lock/trap/climb)')

        # If the player explicitly says they will try something, prefer a check
        if re.search(r'try to |attempt to |i try to', text.lower()):
            requires_check = True
            reason_parts.append('player used "try/attempt"')

        return {
            'intent': intent,
            'ability': ability,
            'dc': dc,
            'requires_check': requires_check,
            'reason': '; '.join(reason_parts) if reason_parts else 'heuristic default'
        }


# Simple module-level helper
_analyzer = PlayerActionAnalyzer()

def analyze_action(text: str) -> dict:
    return _analyzer.analyze_action(text)
