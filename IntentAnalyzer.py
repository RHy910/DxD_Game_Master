import re
from collections import defaultdict
from typing import List, Dict, Tuple, Optional
from ActionValidator import ActionValidator
from ContextManager import ContextManager
# ============================================================================
# SCALABLE KEYWORD STORAGE: Grouped by Intent Category
# ============================================================================

INTENT_DEFINITIONS = {
    "attack": {
        "keywords": ["attack", "strike", "hit", "stab", "shoot", "slash", "cast", "punch", "kick", "swing"],
        "requires_roll": True,
        "category": "combat",
        "max_per_turn": 1,
        "contexts": ["battle", "combat"]
    },
    "persuade": {
        "keywords": ["persuade", "convince", "negotiate", "deceive", "intimidate", "charm", "bribe", "threaten"],
        "requires_roll": True,
        "category": "social",
        "max_per_turn": 2,
        "contexts": ["dialogue", "exploration"]
    },
    "investigate": {
        "keywords": ["search", "investigate", "look for", "examine", "inspect", "analyze", "study", "scan"],
        "requires_roll": True,
        "category": "exploration",
        "max_per_turn": 3,
        "contexts": ["exploration", "battle"]
    },
    "move": {
        "keywords": ["walk", "run", "move", "approach", "go to", "travel", "step", "dash", "crawl", "climb"],
        "requires_roll": False,
        "category": "exploration",
        "max_per_turn": 1,
        "contexts": ["battle", "exploration"]
    },
    "interact": {
        "keywords": ["talk", "ask", "speak", "listen", "greet", "communicate", "converse"],
        "requires_roll": False,
        "category": "social",
        "max_per_turn": 3,
        "contexts": ["dialogue", "exploration"]
    },
    "utility": {
        "keywords": ["use", "equip", "drop", "pick", "grab", "draw", "sheathe", "open", "close"],
        "requires_roll": False,
        "category": "utility",
        "max_per_turn": 2,
        "contexts": ["battle", "exploration", "dialogue"]
    },
    "wait": {
        "keywords": ["wait", "rest", "sleep", "think", "hold", "pause"],
        "requires_roll": False,
        "category": "utility",
        "max_per_turn": 1,
        "contexts": ["battle", "exploration", "dialogue"]
    },
}

# ============================================================================
# CONDITIONAL & NEGATION PATTERNS
# ============================================================================

CONDITIONAL_PATTERNS = [
    r"if\s+(.+?),\s*(?:then\s+)?(.+)",
    r"when\s+(.+?),\s*(?:i\s+)?(.+)",
    r"assuming\s+(.+?),\s*(?:i\s+)?(.+)",
    r"(?:i\s+)?(.+?)\s+if\s+(.+)",
]

NEGATION_PATTERNS = [
    r"i\s+(?:don't|do not|won't|will not|can't|cannot)\s+(.+)",
    r"don't\s+(.+)",
    r"no\s+(.+)",
]

# ============================================================================
# PHRASE CONTEXT DETECTION
# ============================================================================

PHRASE_CONTEXTS = [
    {"pattern": r"\bwith\s+(sword|dagger|bow|axe|weapon|magic|spell)\b", "context": "equipped"},
    {"pattern": r"\bverbally|say|shout|yell|taunt|whisper\b", "context": "verbal"},
    {"pattern": r"\bspell|magic|fireball|cast|enchant\b", "context": "magical"},
    {"pattern": r"\bstealthily|quietly|sneakily|hidden\b", "context": "stealth"},
]

# ============================================================================
# COMPILED REGEX FOR EFFICIENCY
# ============================================================================

def build_compiled_patterns():
    """Pre-compile regex patterns for fast matching."""
    compiled = {}
    for intent, data in INTENT_DEFINITIONS.items():
        keywords = data["keywords"]
        pattern = r"\b(" + "|".join(re.escape(kw) for kw in keywords) + r")\b"
        compiled[intent] = re.compile(pattern, re.IGNORECASE)
    return compiled

COMPILED_PATTERNS = build_compiled_patterns()

# ============================================================================
# CORE DETECTION FUNCTIONS
# ============================================================================

def detect_conditionals(text: str) -> Optional[Dict]:
    """Detect if action is conditional. Returns condition and actual action if found."""
    text_lower = text.lower()
    
    for pattern in CONDITIONAL_PATTERNS:
        match = re.search(pattern, text_lower)
        if match:
            groups = match.groups()
            if len(groups) == 2:
                condition = groups[0].strip()
                action = groups[1].strip()
                return {
                    "is_conditional": True,
                    "condition": condition,
                    "action": action
                }
    
    return {"is_conditional": False, "condition": None, "action": text}

def detect_negation(text: str) -> Tuple[bool, str]:
    """Detect if action is negated."""
    text_lower = text.lower()
    
    for pattern in NEGATION_PATTERNS:
        match = re.search(pattern, text_lower)
        if match:
            return True, match.group(1).strip()
    
    return False, text

def detect_phrase_context(text: str) -> str:
    """Detect contextual modifiers (equipped, verbal, magical, stealth)."""
    text_lower = text.lower()
    
    for rule in PHRASE_CONTEXTS:
        if re.search(rule["pattern"], text_lower):
            return rule["context"]
    
    return "neutral"

def find_matching_intents(text: str) -> List[Tuple[str, int]]:
    """Find all matching intents with match positions. Returns (intent, position) tuples."""
    matches = []
    text_lower = text.lower()
    
    for intent, compiled_pattern in COMPILED_PATTERNS.items():
        match = compiled_pattern.search(text_lower)
        if match:
            matches.append((intent, match.start()))
    
    # Sort by position (first mention takes precedence)
    matches.sort(key=lambda x: x[1])
    return matches

def detect_intent(action_text: str, current_context: str = "exploration") -> Dict:
    """
    Enhanced intent detector with conditional handling, negation, and clarity checks.
    Returns a structured response for the DM engine to process.
    """
    
    # Step 1: Check for negation
    is_negated, effective_text = detect_negation(action_text)
    
    if is_negated:
        return {
            "status": "negation_detected",
            "original_action": action_text,
            "negated_action": effective_text,
            "intent": "unknown",
            "requires_roll": False,
            "message": "Action is negated. DM engine should handle accordingly.",
        }
    
    # Step 2: Check for conditionals
    conditional_result = detect_conditionals(action_text)
    
    if conditional_result["is_conditional"]:
        condition_text = conditional_result["condition"]
        action_text_to_parse = conditional_result["action"]
        
        # Parse the actual action within the conditional
        matches = find_matching_intents(action_text_to_parse)
        
        if not matches:
            return {
                "status": "conditional_unclear",
                "original_action": action_text,
                "condition": condition_text,
                "action": action_text_to_parse,
                "intent": "unclear",
                "requires_roll": False,
                "message": "Conditional detected but action within condition is unclear.",
            }
        
        primary_intent = matches[0][0]
        intent_data = INTENT_DEFINITIONS[primary_intent]
        
        return {
            "status": "conditional",
            "original_action": action_text,
            "condition": condition_text,
            "action": action_text_to_parse,
            "intent": primary_intent,
            "requires_roll": intent_data["requires_roll"],
            "category": intent_data["category"],
            "context": detect_phrase_context(action_text_to_parse),
            "confidence": 0.9,
            "message": f"Conditional action detected. Will execute '{primary_intent}' if: {condition_text}",
        }
    
    # Step 3: Find matching intents (no conditionals)
    matches = find_matching_intents(action_text)
    
    if not matches:
        return {
            "status": "unclear",
            "original_action": action_text,
            "intent": "unclear",
            "requires_roll": False,
            "message": "Intent could not be determined. Please clarify your action.",
        }
    
    # Step 4: Check for multiple intents (action chaining)
    if len(matches) > 1:
        return {
            "status": "multi_intent",
            "original_action": action_text,
            "intents": [
                {
                    "intent": intent,
                    "requires_roll": INTENT_DEFINITIONS[intent]["requires_roll"],
                    "category": INTENT_DEFINITIONS[intent]["category"],
                    "context": detect_phrase_context(action_text),
                    "confidence": 1.0 / len(matches),
                }
                for intent, _ in matches
            ],
            "message": "Multiple intents detected in single action.",
        }
    
    # Step 5: Return single intent result
    intent = matches[0][0]
    intent_data = INTENT_DEFINITIONS[intent]
    
    return {
        "status": "valid",
        "original_action": action_text,
        "intent": intent,
        "requires_roll": intent_data["requires_roll"],
        "category": intent_data["category"],
        "context": detect_phrase_context(action_text),
        "confidence": 1.0,
        "message": f"Intent detected: {intent}",
    }

# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    cm = ContextManager("battle")
    
    test_cases = [
        "I swing my sword at the goblin!",
        "If the goblin moves, I'll attack it.",
        "I don't attack the merchant.",
        "I move closer and slash at the goblin with my sword.",
        "I persuade the guard and convince the captain.",
        "I look everywhere for hidden treasure.",
        "Hmmmm maybe I do something?",
        "I attack, then attack again, then attack once more.",
        "I rest and think about my next move.",
    ]
    
    print("=" * 80)
    print("INTENT DETECTOR TEST SUITE")
    print("=" * 80)
    
    for test in test_cases:
        print(f"\nInput: {test}")
        result = ActionValidator.validate_action(test, cm)
        print(f"Valid: {result['valid']}")
        print(f"Reason: {result['reason']}")
        print(f"Status: {result['status']}")
        print(f"Intent: {result.get('intent', 'N/A')}")
        print("-" * 80)
        
        if result["valid"]:
            cm.reset_turn()  # Reset for next test