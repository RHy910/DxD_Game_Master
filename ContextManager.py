# ============================================================================
# CONTEXT MANAGER: Validates Actions Against Game State
# ============================================================================
from collections import defaultdict
from typing import Dict, List
from IntentAnalyzer import INTENT_DEFINITIONS

class ContextManager:
    def __init__(self, initial_context: str = "exploration"):
        self.current_context = initial_context
        self.action_history = defaultdict(int)  # Track actions this turn
        self.valid_contexts = ["battle", "exploration", "dialogue"]
    
    def set_context(self, new_context: str) -> bool:
        """Set game context and reset action history."""
        if new_context in self.valid_contexts:
            self.current_context = new_context
            self.action_history.clear()
            return True
        return False
    
    def get_allowed_intents(self) -> List[str]:
        """Return intents allowed in current context."""
        allowed = []
        for intent, data in INTENT_DEFINITIONS.items():
            if self.current_context in data["contexts"]:
                allowed.append(intent)
        return allowed
    
    def record_action(self, intent: str) -> bool:
        """Record action attempt. Returns True if within limits, False if exceeded."""
        if intent == "unclear":
            return False
        
        max_allowed = INTENT_DEFINITIONS.get(intent, {}).get("max_per_turn", 1)
        current_count = self.action_history[intent]
        
        if current_count < max_allowed:
            self.action_history[intent] += 1
            return True
        
        return False
    
    def reset_turn(self):
        """Reset action history for new turn."""
        self.action_history.clear()
