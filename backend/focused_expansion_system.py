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
        
        self.logger.info(f"Extracting topic from context: {conversation_context[:200]}...")
        
        # Look for concrete business/topic patterns in the conversation
        lines = conversation_context.strip().split('\n')
        
        # Enhanced patterns to catch more business/topic scenarios
        topic_patterns = [
            # Money/financial topics
            r'(?:extra|more|additional|passive|side)\s+(money|income|cash)\s*([^.?!\n]*)',
            r'([^.?!\n]*money[^.?!\n]*ideas[^.?!\n]*)',
            r'([^.?!\n]*ideas[^.?!\n]*money[^.?!\n]*)',
            # "I want to start X" patterns
            r'(?:want to|going to|plan to|thinking about|interested in)\s+(?:start|starting|create|creating|build|building)\s+(?:a\s+)?([^.?!\n]+)',
            # "X business/agency/service" patterns  
            r'(?:a\s+)?([a-zA-Z\s]+?)\s+(?:business|agency|service|company|startup|venture)',
            # Direct business mentions
            r'\b([a-zA-Z\s]+?)\s+(?:business|agency|service|company)',
            # "starting X" patterns
            r'starting\s+(?:a\s+)?([^.?!\n]+)',
            # General topic extraction
            r'about\s+([^.?!\n]+)',
            # Direct topic mentions
            r'([a-zA-Z\s]*ideas[a-zA-Z\s]*)',
        ]
        
        for line in reversed(lines):
            if line.strip() and 'User:' in line:
                user_text = line.split('User:')[-1].strip()
                self.logger.info(f"Analyzing user text: {user_text}")
                
                for pattern in topic_patterns:
                    matches = re.findall(pattern, user_text, re.IGNORECASE)
                    for match in matches:
                        topic = match.strip().lower()
                        # Clean up the topic
                        topic = re.sub(r'\s+', ' ', topic)  # normalize whitespace
                        topic = topic.strip('.,!?')  # remove punctuation
                        
                        # Filter out very generic terms
                        if (len(topic) > 3 and 
                            topic not in ['the', 'this', 'that', 'your', 'our', 'and', 'with'] and
                            not topic.startswith('go ') and
                            'deeper' not in topic):
                            self.logger.info(f"Extracted topic: {topic}")
                            return topic
        
        # Fallback: look for key business and money terms
        business_keywords = ['money', 'income', 'cash', 'ideas', 'marketing', 'business', 'agency', 'service', 'company', 'startup', 'venture', 'consulting']
        for line in reversed(lines):
            if 'User:' in line:
                user_text = line.split('User:')[-1].strip().lower()
                for keyword in business_keywords:
                    if keyword in user_text:
                        # For money-related topics, extract the full phrase
                        if keyword in ['money', 'income', 'cash', 'ideas']:
                            # Extract broader context for money topics
                            words = user_text.split()
                            for i, word in enumerate(words):
                                if keyword in word:
                                    start = max(0, i-3)
                                    end = min(len(words), i+4)
                                    context = ' '.join(words[start:end])
                                    return context.strip()
                        else:
                            # Try to extract context around the keyword
                            words = user_text.split()
                            for i, word in enumerate(words):
                                if keyword in word:
                                    start = max(0, i-2)
                                    end = min(len(words), i+3)
                                    context = ' '.join(words[start:end])
                                    return context.strip()
        
        self.logger.info("No specific topic extracted")
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

STRICT TOPIC FOCUS - DO NOT DEVIATE:
You MUST expand ONLY on "{last_topic}" - nothing else.

MANDATORY REQUIREMENTS:
1. START by stating: "Let me expand on {last_topic}..."
2. Every single point must be about "{last_topic}" specifically
3. Provide 3-5 concrete, actionable steps about "{last_topic}"
4. Use bullet points or numbered lists
5. Give specific examples related to "{last_topic}"

ABSOLUTELY FORBIDDEN:
- Talking about anything other than "{last_topic}"
- General life advice unrelated to "{last_topic}"
- Abstract concepts not connected to "{last_topic}"
- Emotional or spiritual interpretations unless "{last_topic}" is specifically about emotions/spirituality
- Changing the subject or introducing new topics

IF "{last_topic}" contains "money" or "income" or "ideas":
- Focus exclusively on practical ways to achieve that specific financial goal
- Give concrete steps, methods, and strategies
- Mention specific dollar amounts, timeframes, or measurable outcomes when possible

REMEMBER: The user wants MORE DETAIL about "{last_topic}" - stay laser-focused on that exact topic.
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