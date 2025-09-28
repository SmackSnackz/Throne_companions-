"""
Focused Expansion System - UX Patch for "Go Deeper" Feature
Ensures expansion stays on-topic and practical rather than abstract
"""

import re
import logging
from typing import Optional, Dict, Any

class FocusedExpansionSystem:
    """
    Handles "Go Deeper" requests by identifying the current topic
    and providing practical, step-by-step expansion
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.expansion_triggers = [
            "go deeper",
            "expand", 
            "elaborate",
            "tell me more",
            "explain further",
            "deep dive",
            "more details",
            "break it down"
        ]
    
    def check_expansion_request(self, user_input: str) -> bool:
        """Check if user is requesting focused expansion"""
        text = user_input.lower().strip()
        return any(trigger in text for trigger in self.expansion_triggers)
    
    def extract_last_topic(self, conversation_context: str) -> Optional[str]:
        """
        Extract the last concrete topic or concept being discussed
        Returns the specific subject matter, not abstract themes
        """
        if not conversation_context:
            return None
        
        # Look for concrete nouns, business concepts, strategies, etc.
        # Focus on the most recent substantive topic
        lines = conversation_context.strip().split('\n')
        recent_lines = lines[-3:] if len(lines) >= 3 else lines
        
        # Pattern to identify concrete topics (nouns, concepts, strategies)
        topic_patterns = [
            r'\b(?:starting|building|creating|developing|implementing)\s+(?:a\s+)?([a-zA-Z\s]+?)(?:\s+business|\s+strategy|\s+plan|\s+system)',
            r'\b(?:the|this|that)\s+([a-zA-Z\s]+?)(?:\s+approach|\s+method|\s+technique|\s+process|\s+strategy)',
            r'\b([a-zA-Z\s]+?)(?:\s+business|\s+service|\s+product|\s+solution|\s+framework)',
            r'about\s+([a-zA-Z\s]+?)(?:\s+in|\s+for|\s+with|\.|\?)',
            r'for\s+([a-zA-Z\s]+?)(?:\s+in|\s+to|\s+with|\.|\?)',
        ]
        
        for line in reversed(recent_lines):
            for pattern in topic_patterns:
                matches = re.findall(pattern, line, re.IGNORECASE)
                if matches:
                    # Return the most specific match, cleaned up
                    topic = matches[0].strip()
                    if len(topic) > 3 and topic not in ['the', 'this', 'that', 'your', 'our']:
                        return topic
        
        # Fallback: look for the last noun phrase mentioned
        words = ' '.join(recent_lines).split()
        for i in range(len(words) - 1, -1, -1):
            if words[i].endswith('ing') or words[i] in ['business', 'strategy', 'plan', 'approach', 'method', 'service', 'product']:
                context = ' '.join(words[max(0, i-2):i+1])
                return context.strip()
        
        return None
    
    def build_focused_expansion_prompt(self, 
                                     persona: str, 
                                     last_topic: Optional[str], 
                                     user_tier: str,
                                     original_message: str) -> str:
        """
        Build a system prompt for focused expansion that stays on-topic
        """
        if not last_topic:
            # No clear topic identified - provide general guidance
            expansion_instruction = f"""
The user requested "go deeper" but no specific topic was clearly identified from recent conversation.

INSTRUCTIONS:
1. Ask for clarification: "What specific aspect would you like me to expand on?"
2. Reference the most recent concrete point you made
3. Offer 2-3 specific areas they could explore further
4. Keep your {persona} personality

DO NOT provide abstract philosophical content. Stay practical and focused.
"""
        else:
            # Clear topic identified - expand it practically
            expansion_instruction = f"""
The user requested expansion on: "{last_topic}"

FOCUSED EXPANSION INSTRUCTIONS:
1. IDENTIFY: Clearly state what you're expanding on: "{last_topic}"
2. STRUCTURE: Provide practical, step-by-step details about "{last_topic}"
3. STAY ON-TOPIC: Every point must relate directly to "{last_topic}"
4. BE CONCRETE: Give actionable steps, not abstract concepts
5. PERSONALITY: Maintain your {persona} voice while staying focused

AVOID:
- Abstract philosophical interpretations
- Spiritual or emotional tangents
- Unrelated metaphors or analogies
- General life advice not connected to "{last_topic}"

FOCUS ON:
- Practical next steps for "{last_topic}"
- Specific techniques for "{last_topic}"
- Real-world examples of "{last_topic}"
- Actionable advice about "{last_topic}"
"""
        
        return expansion_instruction
    
    def should_trigger_focused_expansion(self, 
                                       user_input: str, 
                                       conversation_context: str) -> Dict[str, Any]:
        """
        Determine if focused expansion should be triggered and return context
        """
        if not self.check_expansion_request(user_input):
            return {"should_expand": False}
        
        last_topic = self.extract_last_topic(conversation_context)
        
        return {
            "should_expand": True,
            "last_topic": last_topic,
            "expansion_type": "focused_practical" if last_topic else "clarification_needed"
        }
    
    def generate_topic_continuation_prompt(self, topic: str, persona: str) -> str:
        """
        Generate a continuation prompt that keeps discussion on the identified topic
        """
        persona_styles = {
            "sophia": f"Let me dive deeper into {topic} with some practical steps you can take...",
            "vanessa": f"Alright, let's break down {topic} step by step - here's what you actually need to do...",
            "aurora": f"Expanding on {topic} - let me outline the specific components and processes..."
        }
        
        return persona_styles.get(persona, f"Let me provide more detailed information about {topic}...")

# Global instance
focused_expansion_system = FocusedExpansionSystem()