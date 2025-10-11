import json
from typing import Dict, Optional
from pathlib import Path

class ToneAnchorSystem:
    """
    Grounding layer that ensures all companions start with practical, real-world advice
    while maintaining their unique personalities - ADDITIVE to existing persona system
    """
    
    def __init__(self, config_path: str = None):
        if config_path is None:
            config_path = Path(__file__).parent / "config" / "tone_anchors.config.json"
        
        with open(config_path, 'r') as f:
            self.config = json.load(f)
    
    def get_tone_anchor(self, persona: str) -> str:
        """Get the tone anchor for a specific persona"""
        return self.config["personas"].get(persona, {}).get("tone_anchor", "")
    
    def build_grounded_system_prompt(self, persona: str, base_personality: str, user_tier: str, is_expansion: bool = False) -> str:
        """
        Build system prompt with tone anchoring while preserving existing personality
        ADDITIVE - does not replace existing system prompt logic
        """
        tone_anchor = self.get_tone_anchor(persona)
        
        # Build layered prompt: Base Personality + Tone Anchor + Tier Context
        if is_expansion:
            # User requested expansion - allow deeper content
            expansion_guidance = f"""
The user has requested expansion or deeper insights. You may now provide:
- Detailed explanations and theory
- Advanced concepts and nuanced perspectives
- {persona}-specific wisdom and philosophical insights

Still maintain your {persona} personality while going deeper.
"""
            grounding_instruction = expansion_guidance
        else:
            # Default grounded response
            grounding_instruction = f"""
GROUNDING RULE: {tone_anchor}

Focus on:
1. Practical, actionable advice first
2. Real-world examples people can use today
3. Clear, straightforward explanations
4. Everyday language (while maintaining your {persona} style)

Only expand into deeper insights if the user specifically asks with phrases like "go deeper", "elaborate", or "explain more".
"""
        
        # Combine with existing personality (ADDITIVE approach)
        enhanced_prompt = f"""{base_personality}

{grounding_instruction}

User tier: {user_tier}
Response style: Maintain your {persona} personality while following the grounding rule above.
"""
        
        return enhanced_prompt
    
    def check_expansion_request(self, user_input: str) -> bool:
        """Check if user is requesting expansion beyond grounded response"""
        text = user_input.lower().strip()
        expansion_triggers = self.config["expansion_triggers"]
        
        return any(trigger in text for trigger in expansion_triggers)
    
    def get_persona_grounding_examples(self, persona: str) -> Dict[str, str]:
        """Get persona-specific examples of how grounding should work"""
        examples = {
            "sophia": {
                "grounded": "For starting a car repair business, begin with these three practical steps: 1) Get basic tools (wrench set, diagnostic scanner), 2) Practice on friends' cars to build skills, 3) Get proper licensing in your area.",
                "expansion": "The deeper wisdom of entrepreneurship lies in understanding that every master craftsperson began as an apprentice. Consider how ancient guilds..."
            },
            "vanessa": {
                "grounded": "You want to fix cars? Here's what you actually do: 1) Start with oil changes - easy money, 2) Get a cheap diagnostic tool from Amazon, 3) Practice on your own car first.",
                "expansion": "Look, the real game here is understanding market psychology. People don't just want their car fixed..."
            },
            "aurora": {
                "grounded": "To initiate automotive repair operations: 1) Acquire standard diagnostic hardware (OBD-II scanner), 2) Establish practice protocols on accessible vehicles, 3) Secure regulatory compliance certificates.",
                "expansion": "The future of automotive repair integrates AI diagnostics with predictive maintenance algorithms..."
            }
        }
        
        return examples.get(persona, examples["sophia"])
    
    def apply_grounding_filter(self, response: str, persona: str, user_requested_expansion: bool) -> str:
        """
        Apply post-processing filter to ensure response stays grounded unless expansion requested
        """
        if user_requested_expansion:
            return response  # Allow full response when expansion requested
        
        # Check if response is getting too theoretical/abstract for grounded mode
        abstract_indicators = [
            "the deeper meaning", "philosophical implications", "the essence of",
            "transcendental", "metaphysical", "the universe", "cosmic",
            "existential", "the nature of reality", "consciousness"
        ]
        
        response_lower = response.lower()
        if any(indicator in response_lower for indicator in abstract_indicators):
            # Add grounding footer
            grounding_footer = f"\n\n[Want me to go deeper into the philosophical aspects? Just say 'expand' or 'go deeper']"
            
            # For now, return original response with footer
            # In production, you might want to truncate abstract content
            return response + grounding_footer
        
        return response

# Global instance  
tone_anchor_system = ToneAnchorSystem()