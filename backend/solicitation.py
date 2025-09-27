import json
import os
from typing import Dict, List, Optional, Literal, TypedDict
from pathlib import Path

# Types
PersonaKey = Literal["sophia", "vanessa", "aurora"]

class DetectionContext(TypedDict):
    user_input: str
    intent_score: Optional[float]

class SolicitationResponse(TypedDict):
    type: str
    questions: List[str]
    starter_prompts: List[str]
    tag: str
    fallback: Dict[str, any]

class SolicitationConfig:
    def __init__(self, config_path: str = None):
        if config_path is None:
            config_path = Path(__file__).parent / "config" / "solicitation.config.json"
        
        with open(config_path, 'r') as f:
            self.config = json.load(f)
    
    def is_vague(self, ctx: DetectionContext) -> bool:
        """Detect if user input is vague and needs solicitation"""
        text = (ctx.get("user_input", "") or "").lower().strip()
        
        # Check minimum length
        if len(text) < self.config["trigger"]["min_length"]:
            return True
        
        # Check for vague keywords
        vague_keywords = self.config["trigger"]["vague_keywords"]
        if any(keyword in text for keyword in vague_keywords):
            return True
        
        # Check intent score if available
        if self.config["trigger"]["require_low_intent_score"]:
            intent_score = ctx.get("intent_score", 0.0)
            if intent_score < 0.3:
                return True
        
        return False
    
    def build_solicitation(self, persona: PersonaKey) -> Dict:
        """Build solicitation response for a specific persona"""
        persona_config = self.config["personas"][persona]
        ui_config = self.config["ui"]
        
        return {
            "questions": persona_config["questions"][:ui_config["max_questions"]],
            "starter_prompts": persona_config["starter_prompts"][:ui_config["starter_count"]],
            "brand_tag": ui_config["brand_tag"]
        }
    
    def maybe_solicit(self, ctx: DetectionContext, persona: PersonaKey) -> Optional[SolicitationResponse]:
        """Main entry point: check if solicitation is needed"""
        if not self.is_vague(ctx):
            return None  # Proceed with normal answer
        
        solicitation_data = self.build_solicitation(persona)
        ui_config = self.config["ui"]
        
        return {
            "type": "solicitation",
            "questions": solicitation_data["questions"],
            "starter_prompts": solicitation_data["starter_prompts"],
            "tag": solicitation_data["brand_tag"],
            "fallback": {
                "after_ms": ui_config["fallback_after_ms"],
                "mode": ui_config["fallback_mode"]
            }
        }
    
    def build_preface(self, answers: Dict[str, str], persona: PersonaKey, chosen_starter: Optional[str] = None) -> str:
        """Build preface to prepend to LLM prompt based on user clarifications"""
        preface_lines = ["User intent (solicited):"]
        
        # Map question indices to clarifier types (simplified approach)
        clarifier_mapping = {
            "0": "Goal",
            "1": "Detail", 
            "2": "Decision",
            "3": "Level",
            "4": "Teaching"
        }
        
        for idx, answer in answers.items():
            if answer.strip():
                clarifier_name = clarifier_mapping.get(idx, f"Question {idx}")
                preface_lines.append(f"- {clarifier_name}: {answer}")
        
        if chosen_starter:
            preface_lines.append(f"- Chosen starter: {chosen_starter}")
        
        persona_styles = {
            "sophia": "elegant, wise, thoughtful teacher",
            "vanessa": "direct, confident, street-smart advisor", 
            "aurora": "futuristic, tech-savvy, divine guide"
        }
        
        preface_lines.extend([
            f"",
            f"Persona: {persona.title()} ({persona_styles[persona]})",
            f"Instruction: Answer accordingly with your natural personality.",
            f""
        ])
        
        return "\n".join(preface_lines)

# Global instance
solicitation_engine = SolicitationConfig()

def detect_and_solicit(user_input: str, persona: PersonaKey, intent_score: Optional[float] = None) -> Optional[SolicitationResponse]:
    """Convenience function for the main detection flow"""
    ctx: DetectionContext = {
        "user_input": user_input,
        "intent_score": intent_score
    }
    return solicitation_engine.maybe_solicit(ctx, persona)

def build_llm_preface(answers: Dict[str, str], persona: PersonaKey, chosen_starter: Optional[str] = None) -> str:
    """Convenience function to build LLM preface"""
    return solicitation_engine.build_preface(answers, persona, chosen_starter)