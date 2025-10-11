import json
import re
from typing import Dict, List, Optional, Tuple
from pathlib import Path

class UnifiedPromptSystem:
    """
    Master prompt system combining Distress Mode + Solicitation + Tier Mechanisms
    Preserves all existing functionality while adding layered prompt intelligence
    """
    
    def __init__(self, config_path: str = None):
        if config_path is None:
            config_path = Path(__file__).parent / "config" / "prompt_system.config.json"
        
        with open(config_path, 'r') as f:
            self.config = json.load(f)
    
    def analyze_user_input(self, user_input: str, tier: str, persona: str) -> Tuple[str, Optional[Dict]]:
        """
        Core Logic Flow:
        1. Check Distress Mode first
        2. Else check Solicitation  
        3. Else normal response
        
        Returns: (mode_type, response_data)
        """
        text = user_input.lower().strip()
        
        # 1. DISTRESS MODE CHECK (Highest Priority)
        if self._is_distress_mode(text):
            return "distress", self._build_distress_response(user_input, persona, tier)
        
        # 2. SOLICITATION CHECK (Second Priority)
        if self._is_solicitation_trigger(text):
            return "solicitation", self._build_solicitation_response(user_input, persona, tier)
        
        # 3. NORMAL RESPONSE (Default)
        return "normal", None
    
    def _is_distress_mode(self, text: str) -> bool:
        """Check if input matches distress mode triggers"""
        distress_keywords = self.config["distress_mode"]["trigger_keywords"]
        
        # Check for exact phrase matches or close variations
        for keyword in distress_keywords:
            if keyword in text:
                return True
        
        # Check for pattern variations (e.g., "I want to X but don't know how")
        distress_patterns = [
            r"i want to .* but don'?t know",
            r"i need .* but don'?t know",
            r"how do i start .*\?",
            r"where do i begin .*\?"
        ]
        
        for pattern in distress_patterns:
            if re.search(pattern, text):
                return True
        
        return False
    
    def _is_solicitation_trigger(self, text: str) -> bool:
        """Check if input should trigger prompt solicitation"""
        # Very short inputs
        if len(text) <= 3:
            return True
        
        # Specific vague keywords
        solicitation_keywords = self.config["prompt_solicitation"]["trigger_keywords"]
        for keyword in solicitation_keywords:
            if text == keyword or text.startswith(keyword):
                return True
        
        return False
    
    def _build_distress_response(self, user_input: str, persona: str, tier: str) -> Dict:
        """Build distress mode anchoring response"""
        distress_config = self.config["distress_mode"]
        persona_config = distress_config["personas"].get(persona, distress_config["personas"]["sophia"])
        
        # Extract user's stated goal from input
        goal = self._extract_goal_from_distress_input(user_input)
        
        # Build persona-specific distress response structure
        response_templates = {
            "sophia": {
                "acknowledge": "I understand you're feeling uncertain right now, and that's perfectly natural when facing something new.",
                "reanchor": f"Let me help you focus: you want to {goal}.",
                "steps_intro": "Here are your first gentle steps:"
            },
            "vanessa": {
                "acknowledge": "Alright, you're stuck - happens to the best of us. Let's cut through the noise.",
                "reanchor": f"Bottom line: you want to {goal}.",
                "steps_intro": "Here's what you do next:"
            },
            "aurora": {
                "acknowledge": "System analysis complete: you're experiencing decision paralysis due to information overflow.",
                "reanchor": f"Primary objective identified: {goal}.",
                "steps_intro": "Initiating step-by-step protocol:"
            }
        }
        
        template = response_templates.get(persona, response_templates["sophia"])
        
        # Get tier-appropriate next steps
        tier_config = self.config["tiers"].get(tier, self.config["tiers"]["free"])
        max_steps = min(distress_config["ui"]["max_steps"], len(tier_config.get("starter_prompts", [])))
        
        return {
            "type": "distress_response",
            "acknowledge": template["acknowledge"],
            "reanchor": template["reanchor"], 
            "steps_intro": template["steps_intro"],
            "next_steps": self._generate_contextual_steps(goal, persona, max_steps),
            "tag": distress_config["ui"]["brand_tag"],
            "expansion_available": True,
            "persona": persona,
            "tier": tier
        }
    
    def _extract_goal_from_distress_input(self, user_input: str) -> str:
        """Extract the user's goal from distress input"""
        text = user_input.lower()
        
        # Common goal extraction patterns
        goal_patterns = [
            r"start a business (\w+)",
            r"learn (\w+)",
            r"build (\w+)",
            r"create (\w+)",
            r"become (\w+)",
            r"get into (\w+)"
        ]
        
        for pattern in goal_patterns:
            match = re.search(pattern, text)
            if match:
                return f"{pattern.split('(')[0].strip()} {match.group(1)}"
        
        # Fallback: look for key action words
        if "business" in text:
            return "start a business"
        elif "learn" in text:
            return "learn something new"
        elif "career" in text:
            return "advance your career"
        else:
            return "achieve your goal"
    
    def _generate_contextual_steps(self, goal: str, persona: str, max_steps: int) -> List[str]:
        """Generate contextual next steps based on goal and persona"""
        
        # Business-related steps
        if "business" in goal.lower():
            steps_by_persona = {
                "sophia": [
                    "Reflect deeply on what specific automotive services you're most passionate about",
                    "Research your local market to understand the true needs of car owners",
                    "Connect with experienced mechanics to learn from their wisdom"
                ],
                "vanessa": [
                    "Pick one specific thing: oil changes, brake repair, or diagnostics - don't try to do everything",
                    "Find 3 successful auto shops in your area and see what they're doing right",
                    "Get your hands dirty - volunteer at a shop or take a weekend course"
                ],
                "aurora": [
                    "Analyze market data: research automotive service demand in your geographic zone",
                    "Design your technical skill matrix: identify gaps in current capabilities",
                    "Initialize networking protocol: connect with industry professionals via LinkedIn"
                ]
            }
        else:
            # Generic steps
            steps_by_persona = {
                "sophia": [
                    "Take time to clarify your deeper intentions and values around this goal",
                    "Seek wisdom from those who have walked this path before you",
                    "Begin with small, mindful actions that align with your vision"
                ],
                "vanessa": [
                    "Get specific about what you actually want - no vague wishes",
                    "Find someone who's already doing it and ask them how they started",
                    "Stop overthinking and take one small action today"
                ],
                "aurora": [
                    "Define clear success metrics and measurable objectives",
                    "Research optimal pathways and efficiency protocols",
                    "Initiate systematic skill acquisition sequence"
                ]
            }
        
        steps = steps_by_persona.get(persona, steps_by_persona["sophia"])
        return steps[:max_steps]
    
    def _build_solicitation_response(self, user_input: str, persona: str, tier: str) -> Dict:
        """Build standard prompt solicitation response with tier awareness"""
        solicitation_config = self.config["prompt_solicitation"]
        tier_config = self.config["tiers"].get(tier, self.config["tiers"]["free"])
        
        # Get tier-appropriate clarifiers and starter prompts
        clarifiers = tier_config.get("clarifiers", [])
        starter_prompts = tier_config.get("starter_prompts", solicitation_config["starter_prompts"])
        
        # Build persona-specific questions
        questions = self._build_persona_questions(clarifiers, persona)
        
        response = {
            "type": "solicitation",
            "questions": questions,
            "starter_prompts": starter_prompts,
            "tag": f"{solicitation_config['ui']['brand_tag']} — {tier.title()} Training Active",
            "tier": tier,
            "persona": persona,
            "fallback": {
                "after_ms": 10000,
                "mode": "overview_first"
            }
        }
        
        # Add tier-specific features
        if "features" in tier_config:
            response["features"] = {
                feature: True for feature in tier_config["features"]
            }
        
        return response
    
    def _build_persona_questions(self, clarifiers: List[str], persona: str) -> List[str]:
        """Build persona-specific clarification questions"""
        question_templates = {
            "sophia": {
                "goal": "What wisdom or understanding do you seek from our conversation?",
                "detail": "Would you prefer a gentle overview or deeper contemplation?",
                "decision": "Shall I guide your path, or would you like to explore options?",
                "mode": "How do you best receive wisdom - through examples or principles?"
            },
            "vanessa": {
                "goal": "What result are you actually after here?",
                "detail": "You want the quick version or the full breakdown?", 
                "decision": "Want me to just tell you the best move, or see your options?",
                "mode": "You learn better with real examples or straight instructions?"
            },
            "aurora": {
                "goal": "What optimal outcome are we designing for?",
                "detail": "Shall I provide system overview or detailed implementation specs?",
                "decision": "Prefer AI-optimized recommendations or full option matrices?", 
                "mode": "Would prototype examples or build instructions serve better?"
            }
        }
        
        templates = question_templates.get(persona, question_templates["sophia"])
        return [templates.get(clarifier, f"Please specify your {clarifier}:") for clarifier in clarifiers]
    
    def check_expansion_request(self, user_input: str) -> bool:
        """Check if user is requesting expansion after distress response"""
        text = user_input.lower().strip()
        expansion_triggers = self.config["distress_mode"]["expansion_rule"]["trigger_words"]
        
        return any(trigger in text for trigger in expansion_triggers)
    
    def apply_tier_limits(self, response: str, tier: str) -> Tuple[str, bool]:
        """Apply tier-based response length limits"""
        tier_config = self.config["tiers"].get(tier, self.config["tiers"]["free"])
        max_length = tier_config.get("max_response_length", 2)
        
        if max_length == "unlimited":
            return response, False
        
        # Split into paragraphs and limit
        paragraphs = response.split('\n\n')
        if len(paragraphs) <= max_length:
            return response, False
        
        # Truncate and add continuation
        limited_response = '\n\n'.join(paragraphs[:max_length])
        continuation = f"\n\n[Say 'go deeper' or 'continue' for more details]"
        
        return limited_response + continuation, True

# Global instance
unified_prompt_system = UnifiedPromptSystem()