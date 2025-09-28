"""
Memory System Implementation for Throne Companions
Handles chat history collection, memory summarization, and injection logic.
"""

import logging
from datetime import datetime, timezone, timedelta
from typing import List, Optional, Dict, Any, Tuple
from motor.motor_asyncio import AsyncIOMotorDatabase
from pydantic import BaseModel, Field
import uuid
from emergentintegrations.llm.chat import LlmChat, UserMessage
import os

# Memory System Models
class ChatHistoryEntry(BaseModel):
    """Chat history entry with exact fields as specified"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    session_id: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    role: str  # Friend, Wife, etc.
    affection_dial: int  # 0-3
    message: str
    direction: str  # "user" or "companion"

class MemorySummaryEntry(BaseModel):
    """Memory summary entry with exact fields as specified"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    session_id: str
    summary: str  # 2-3 lines summary
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class MemorySystem:
    """
    Memory System Implementation
    - Stores chat history in chat_history collection
    - Generates memory summaries in memory_summary collection
    - Provides tier-based memory injection
    """

    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.logger = logging.getLogger(__name__)
        
        # Retention policies by tier (as specified)
        self.tier_retention = {
            "novice": 3,      # last 3 summaries
            "apprentice": 10, # last 10 summaries
            "regent": 50,     # last 50 summaries
            "sovereign": -1   # full history (unlimited)
        }

    async def store_chat_message(
        self,
        user_id: str,
        session_id: str,
        message: str,
        direction: str,  # "user" or "companion"
        role: str = "Friend",
        affection_dial: int = 2
    ) -> str:
        """
        Store a chat message in chat_history collection
        Returns the stored message ID
        """
        try:
            chat_entry = ChatHistoryEntry(
                user_id=user_id,
                session_id=session_id,
                timestamp=datetime.now(timezone.utc),
                role=role,
                affection_dial=affection_dial,
                message=message,
                direction=direction
            )
            
            result = await self.db.chat_history.insert_one(chat_entry.dict())
            self.logger.info(f"Stored chat message: {chat_entry.id} for session {session_id}")
            return chat_entry.id
            
        except Exception as e:
            self.logger.error(f"Failed to store chat message: {e}")
            raise

    async def generate_session_summary(self, user_id: str, session_id: str) -> Optional[str]:
        """
        Generate a 2-3 line memory summary for a completed session
        Uses the exact summarization prompt as specified
        """
        try:
            # Get all messages from the session
            messages = await self.db.chat_history.find({
                "user_id": user_id,
                "session_id": session_id
            }).sort("timestamp", 1).to_list(length=None)
            
            if not messages:
                self.logger.warning(f"No messages found for session {session_id}")
                return None
            
            # Format conversation for summarization
            conversation_text = ""
            for msg in messages:
                speaker = "User" if msg["direction"] == "user" else "Companion"
                conversation_text += f"{speaker}: {msg['message']}\n"
            
            if not conversation_text.strip():
                return None
            
            # Use exact summarization prompt as specified
            summarization_prompt = (
                "Summarize this session into 2–3 lines. "
                "Capture emotional tone and key details. "
                "Write as if preparing memory for a companion to recall next time."
            )
            
            # Generate summary using LLM
            try:
                llm_chat = LlmChat(
                    api_key=os.environ.get("EMERGENT_LLM_KEY"),
                    session_id=f"memory-summary-{session_id}",
                    system_message=summarization_prompt
                ).with_model("openai", "gpt-4o-mini")
                
                user_message = UserMessage(text=conversation_text)
                summary_response = await llm_chat.send_message(user_message)
                
                if summary_response:
                    summary_text = summary_response.strip()
                    self.logger.info(f"Generated summary for session {session_id}: {summary_text[:100]}...")
                    return summary_text
                else:
                    self.logger.warning(f"No response from LLM for session {session_id}")
                    return None
                    
            except Exception as llm_error:
                self.logger.error(f"LLM summarization failed for session {session_id}: {llm_error}")
                # Fallback summary generation
                role = messages[0].get("role", "Friend")
                affection = messages[0].get("affection_dial", 2)
                msg_count = len([m for m in messages if m["direction"] == "user"])
                return f"Session with {role} (affection level {affection}). User shared {msg_count} messages with emotional connection."
                
        except Exception as e:
            self.logger.error(f"Failed to generate session summary: {e}")
            return None

    async def store_memory_summary(self, user_id: str, session_id: str, summary: str) -> str:
        """
        Store a memory summary in memory_summary collection
        Returns the stored summary ID
        """
        try:
            memory_entry = MemorySummaryEntry(
                user_id=user_id,
                session_id=session_id,
                summary=summary,
                timestamp=datetime.now(timezone.utc)
            )
            
            result = await self.db.memory_summary.insert_one(memory_entry.dict())
            self.logger.info(f"Stored memory summary: {memory_entry.id} for session {session_id}")
            return memory_entry.id
            
        except Exception as e:
            self.logger.error(f"Failed to store memory summary: {e}")
            raise

    async def get_memory_summaries_for_injection(self, user_id: str, user_tier: str) -> str:
        """
        Get memory summaries for injection based on tier retention policy
        Returns formatted memory string for system prompt injection
        """
        try:
            retention_count = self.tier_retention.get(user_tier, 3)
            
            # Build query
            query = {"user_id": user_id}
            
            # Get summaries based on retention policy
            if retention_count == -1:  # Sovereign - unlimited
                summaries = await self.db.memory_summary.find(query).sort("timestamp", -1).to_list(length=None)
            else:
                summaries = await self.db.memory_summary.find(query).sort("timestamp", -1).limit(retention_count).to_list(length=None)
            
            if not summaries:
                return ""
            
            # Format for injection (reverse chronological order for context)
            memory_text = "Memory summary: "
            formatted_summaries = []
            
            for summary in reversed(summaries):  # Most recent last for better context
                timestamp = summary["timestamp"]
                if isinstance(timestamp, str):
                    timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                formatted_summaries.append(f"{summary['summary']}")
            
            memory_text += " | ".join(formatted_summaries)
            
            self.logger.info(f"Retrieved {len(summaries)} memory summaries for user {user_id} (tier: {user_tier})")
            return memory_text
            
        except Exception as e:
            self.logger.error(f"Failed to get memory summaries: {e}")
            return ""

    async def complete_session_and_summarize(self, user_id: str, session_id: str) -> Optional[str]:
        """
        Complete a session by generating and storing its memory summary
        Returns the generated summary text
        """
        try:
            # Generate summary
            summary_text = await self.generate_session_summary(user_id, session_id)
            
            if summary_text:
                # Store summary
                summary_id = await self.store_memory_summary(user_id, session_id, summary_text)
                self.logger.info(f"Session {session_id} completed with summary {summary_id}")
                return summary_text
            else:
                self.logger.warning(f"No summary generated for session {session_id}")
                return None
                
        except Exception as e:
            self.logger.error(f"Failed to complete session {session_id}: {e}")
            return None

    async def get_session_message_count(self, user_id: str, session_id: str) -> int:
        """Get the number of messages in a session"""
        try:
            count = await self.db.chat_history.count_documents({
                "user_id": user_id,
                "session_id": session_id
            })
            return count
        except Exception as e:
            self.logger.error(f"Failed to get session message count: {e}")
            return 0

    async def cleanup_old_data(self, days_to_keep: int = 90):
        """
        Cleanup old chat history and memory summaries
        (Optional maintenance function)
        """
        try:
            cutoff_date = datetime.now(timezone.utc) - timedelta(days=days_to_keep)
            
            # Cleanup old chat history
            chat_result = await self.db.chat_history.delete_many({
                "timestamp": {"$lt": cutoff_date}
            })
            
            # Cleanup old memory summaries
            memory_result = await self.db.memory_summary.delete_many({
                "timestamp": {"$lt": cutoff_date}
            })
            
            self.logger.info(f"Cleanup completed: {chat_result.deleted_count} chat entries, {memory_result.deleted_count} memory summaries")
            
        except Exception as e:
            self.logger.error(f"Cleanup failed: {e}")


# Global memory system instance (will be initialized in server.py)
memory_system: Optional[MemorySystem] = None


def get_memory_system() -> MemorySystem:
    """Get the global memory system instance"""
    if memory_system is None:
        raise RuntimeError("Memory system not initialized")
    return memory_system


def initialize_memory_system(db: AsyncIOMotorDatabase) -> MemorySystem:
    """Initialize the global memory system instance"""
    global memory_system
    memory_system = MemorySystem(db)
    return memory_system