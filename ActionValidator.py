# ============================================================================
# TURN VALIDATOR: Final Validation Before Action Execution
# ============================================================================
from typing import Dict, List
from IntentAnalyzer import detect_intent, INTENT_DEFINITIONS
from ContextManager import ContextManager

class ActionValidator:
    """
    Validates player actions based on current context and turn limits.
    """
        

    def validate_action(self, action_text: str) -> Dict:
        """
        Complete validation pipeline: Intent detection + context checking + turn limits.
        Returns comprehensive response for DM engine.
        """
        
        # Step 1: Detect intent
        detection = detect_intent(action_text, ContextManager.current_context)
        
        # Handle unclear intents
        if detection["status"] == "unclear":
            return {
                "valid": False,
                "reason": "Intent unclear",
                **detection,
            }
        
        # Handle conditionals
        if detection["status"] == "conditional":
            intent = detection["intent"]
            allowed = ContextManager.get_allowed_intents()
            
            if intent not in allowed:
                return {
                    "valid": False,
                    "reason": f"Cannot perform '{intent}' during {ContextManager.current_context}.",
                    **detection,
                }
            
            if not ContextManager.record_action(intent):
                max_allowed = INTENT_DEFINITIONS[intent]["max_per_turn"]
                return {
                    "valid": False,
                    "reason": f"Cannot perform '{intent}' more than {max_allowed} time(s) per turn.",
                    **detection,
                }
            
            return {
                "valid": True,
                "reason": "Conditional action valid and within turn limits.",
                **detection,
            }
        
        # Handle multi-intent
        if detection["status"] == "multi_intent":
            intents = detection["intents"]
            allowed = ContextManager.get_allowed_intents()
            
            for intent_obj in intents:
                intent = intent_obj["intent"]
                
                if intent not in allowed:
                    return {
                        "valid": False,
                        "reason": f"Cannot perform '{intent}' during {ContextManager.current_context}.",
                        **detection,
                    }

                if not ContextManager.record_action(intent):
                    max_allowed = INTENT_DEFINITIONS[intent]["max_per_turn"]
                    return {
                        "valid": False,
                        "reason": f"Cannot perform '{intent}' more than {max_allowed} time(s) per turn.",
                        **detection,
                    }
            
            return {
                "valid": True,
                "reason": "All intents valid and within turn limits.",
                **detection,
            }
        
        # Handle single intent (status: "valid" or "negation_detected")
        if detection["status"] == "negation_detected":
            return {
                "valid": False,
                "reason": "Action is negated.",
                **detection,
            }
        
        intent = detection["intent"]
        allowed = ContextManager.get_allowed_intents()
        
        if intent not in allowed:
            return {
                "valid": False,
                "reason": f"Cannot perform '{intent}' during {ContextManager.current_context}.",
                **detection,
            }
        
        if not ContextManager.record_action(intent):
            max_allowed = INTENT_DEFINITIONS[intent]["max_per_turn"]
            return {
                "valid": False,
                "reason": f"Cannot perform '{intent}' more than {max_allowed} time(s) per turn.",
                **detection,
            }
        
        return {
            "valid": True,
            "reason": "Action valid and within turn limits.",
            **detection,
        }