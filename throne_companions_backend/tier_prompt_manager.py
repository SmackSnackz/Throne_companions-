import json
import os
from typing import Dict, List, Optional, Literal
from pathlib import Path

class TierPromptManager:
    """Manages tier-specific prompt mechanisms while preserving existing functionality"""
    
    def __init__(self, config_path: str = None):
        if config_path is None:
            config_path = Path(__file__).parent / "config" / "tier_prompts.config.json"
        
        with open(config_path, 'r') as f:
            self.config = json.load(f)
    
    def get_tier_config(self, tier: str) -> Dict:
        """Get configuration for specific tier"""
        return self.config["tiers"].get(tier, self.config["tiers"]["novice"])
    
    def should_trigger_prompting(self, user_input: str, tier: str, session_starter_count: int = 0) -> bool:
        """
        Determine if prompt mechanisms should trigger - ADDITIVE to existing solicitation
        Only triggers if:
        1. Input is genuinely vague (preserve existing logic)
        2. User hasn't exceeded their tier's starter limit
        3. Tier supports prompt mechanisms
        """
        tier_config = self.get_tier_config(tier)
        
        # Check session limits for non-unlimited tiers
        max_starters = tier_config.get("max_starters_per_session")
        if max_starters != "unlimited" and session_starter_count >= max_starters:
            return False
        
        # Use existing vague detection logic - don't override
        vague_indicators = ["help", "idk", "?", "not sure", "what do i do"]
        text = user_input.lower().strip()
        
        # Only trigger for genuinely vague inputs
        return any(indicator in text for indicator in vague_indicators) or len(text) <= 3
    
    def get_tier_starters(self, tier: str, persona: str) -> List[str]:
        """Get tier-appropriate starter prompts for persona"""
        tier_config = self.get_tier_config(tier)
        base_starters = tier_config.get("starter_prompts", [])
        
        # Add persona-specific modifications for higher tiers
        if tier in ["regent", "sovereign"]:
            persona_prefix = self._get_persona_prefix(persona)
            starters = [f"{persona_prefix} {starter}" for starter in base_starters]
        else:
            starters = base_starters
            
        return starters
    
    def _get_persona_prefix(self, persona: str) -> str:
        """Get persona-specific prefix for starters"""
        prefixes = {
            "sophia": "With wisdom:",
            "vanessa": "Straight up:",
            "aurora": "Innovatively:"
        }
        return prefixes.get(persona, "")
    
    def get_coaching_message(self, tier: str, persona: str, user_input: str) -> Optional[str]:
        """Generate coaching message for higher tiers"""
        tier_config = self.get_tier_config(tier)
        
        if not tier_config.get("coaching_enabled", False):
            return None
        
        persona_config = self.config["persona_coaching"].get(persona, {})
        
        if tier_config.get("coaching_style") == "persona_tailored":
            prefix = persona_config.get("coaching_prefix", "Here's a better way to ask:")
            examples = persona_config.get("examples", [])
            if examples:
                example = examples[0]  # Use first example for simplicity
                return f"{prefix}\n\n{example}"
        
        return None
    
    def apply_response_limits(self, response: str, tier: str) -> tuple[str, bool]:
        """Apply tier-based response length limits"""
        tier_config = self.get_tier_config(tier)
        max_length = tier_config.get("max_response_length")
        
        if max_length == "unlimited":
            return response, False
        
        if isinstance(max_length, int) and len(response) > max_length:
            # For Regent tier, check for "deep dive" request
            if tier == "regent":
                return response, False  # Will be handled by deep dive logic
            
            # Truncate and add continuation prompt
            truncated = response[:max_length] + "..."
            continuation_prompt = "\n\n[Say 'continue' for more details]"
            return truncated + continuation_prompt, True
        
        return response, False
    
    def get_brand_tag(self, tier: str) -> str:
        """Get tier-appropriate branding tag"""
        tier_config = self.get_tier_config(tier)
        return tier_config.get("brand_tag", "Powered by Prompt Solicitation Layer™")
    
    def build_enhanced_solicitation(self, user_input: str, persona: str, tier: str, session_starter_count: int = 0) -> Optional[Dict]:
        """
        Build enhanced solicitation with tier-specific features
        PRESERVES existing solicitation logic - only adds tier-aware enhancements
        """
        if not self.should_trigger_prompting(user_input, tier, session_starter_count):
            return None
        
        tier_config = self.get_tier_config(tier)
        
        # Get tier-appropriate clarifiers and starters
        clarifiers = tier_config.get("clarifiers", [])
        starter_prompts = self.get_tier_starters(tier, persona)
        
        # Add coaching message for higher tiers
        coaching_message = self.get_coaching_message(tier, persona, user_input)
        
        solicitation = {
            "type": "solicitation",
            "questions": self._build_questions_for_clarifiers(clarifiers, persona),
            "starter_prompts": starter_prompts,
            "tag": self.get_brand_tag(tier),
            "tier": tier,
            "fallback": {
                "after_ms": 10000,
                "mode": tier_config.get("response_style", "overview_first")
            }
        }
        
        if coaching_message:
            solicitation["coaching"] = coaching_message
        
        # Add tier-specific features
        if tier in ["regent", "sovereign"]:
            solicitation["features"] = {
                "save_prompt": tier_config.get("prompt_save_enabled", False),
                "search_history": tier_config.get("searchable_history", False),
                "voice_toggle": tier_config.get("voice_text_toggle", False)
            }
        
        return solicitation
    
    def _build_questions_for_clarifiers(self, clarifiers: List[str], persona: str) -> List[str]:
        """Build persona-specific questions for clarifiers"""
        question_templates = {
            "sophia": {
                "goal": "What wisdom do you seek to gain from our exchange?",
                "detail": "Would you prefer a gentle exploration or deep contemplation?",
                "decision": "Shall I guide your path, or would you like to choose your direction?",
                "level": "Where do you find yourself in your journey - beginning, progressing, or advanced?",
                "teaching": "Would an example illuminate your understanding, or shall we start with principles?"
            },
            "vanessa": {
                "goal": "What result are you actually after here?", 
                "detail": "You want the quick version or the full breakdown?",
                "decision": "Want me to just tell you the best move, or see your options?",
                "level": "Where you at - new to this, got some experience, or pretty seasoned?",
                "teaching": "You learn better with examples first, or straight instructions?"
            },
            "aurora": {
                "goal": "What optimal outcome are we designing for?",
                "detail": "Shall I provide a system overview or detailed implementation specs?",
                "decision": "Would you prefer AI-optimized recommendations or full option matrices?",
                "level": "Select your expertise calibration - novice, intermediate, or advanced user?",
                "teaching": "Would a working prototype example or step-by-step build instructions serve better?"
            }
        }
        
        templates = question_templates.get(persona, question_templates["sophia"])
        return [templates.get(clarifier, f"Please specify your {clarifier}:") for clarifier in clarifiers]
    
    def track_prompt_event(self, event_type: str, data: Dict = None):
        """Track prompt mechanism usage events"""
        # This would integrate with existing analytics system
        # For now, just log the event
        import logging
        logging.info(f"Prompt event: {event_type}, data: {data}")

# Global instance
tier_prompt_manager = TierPromptManager()