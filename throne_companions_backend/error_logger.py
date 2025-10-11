"""
Error and Loop Logging System
Tracks agent malfunctions: loopbacks, off-topic resets, repeated openers
"""

import logging
import json
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
import uuid

class ErrorLogger:
    """
    Logs and tracks agent conversation errors and malfunctions
    """
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.logger = logging.getLogger(__name__)
        
        # Patterns that indicate problems
        self.loopback_indicators = [
            "hello", "hey there", "hi there", "good morning", "good afternoon",
            "it seems you're ready", "i sense that you", "it sounds like you're looking"
        ]
        
        self.off_topic_indicators = [
            "let me help you with something else", "changing the subject",
            "let's talk about", "speaking of which", "on a different note"
        ]
        
        self.repeated_opener_cache = {}
    
    async def log_error(self, error_type: str, message: str, context: Dict[str, Any] = None):
        """Log an error to the database"""
        try:
            error_entry = {
                "id": str(uuid.uuid4()),
                "type": error_type,
                "message": message,
                "context": context or {},
                "timestamp": datetime.now(timezone.utc),
                "session_id": context.get("session_id") if context else None,
                "user_id": context.get("user_id") if context else None
            }
            
            await self.db.error_logs.insert_one(error_entry)
            self.logger.warning(f"AGENT ERROR [{error_type}]: {message}")
            
        except Exception as e:
            self.logger.error(f"Failed to log error: {e}")
    
    async def check_loopback_error(self, response: str, user_message: str, session_id: str, user_id: str):
        """Check for loopback errors (inappropriate conversation resets)"""
        response_lower = response.lower().strip()
        
        # Check if response starts with greeting patterns inappropriately
        for indicator in self.loopback_indicators:
            if response_lower.startswith(indicator):
                await self.log_error(
                    error_type="loopback",
                    message=f"Agent started response with inappropriate greeting: '{indicator}'",
                    context={
                        "user_message": user_message,
                        "response_start": response[:100],
                        "session_id": session_id,
                        "user_id": user_id,
                        "indicator_matched": indicator
                    }
                )
                return True
        
        return False
    
    async def check_off_topic_reset(self, response: str, user_message: str, session_id: str, user_id: str, expected_topic: str = None):
        """Check for off-topic resets (agent changing subject inappropriately)"""
        response_lower = response.lower()
        
        for indicator in self.off_topic_indicators:
            if indicator in response_lower:
                await self.log_error(
                    error_type="off_topic",
                    message=f"Agent went off-topic with pattern: '{indicator}'",
                    context={
                        "user_message": user_message,
                        "response": response[:200],
                        "session_id": session_id,
                        "user_id": user_id,
                        "expected_topic": expected_topic,
                        "indicator_matched": indicator
                    }
                )
                return True
        
        return False
    
    async def check_repeated_opener(self, response: str, session_id: str, user_id: str):
        """Check for repeated opener patterns"""
        response_start = response[:50].lower().strip()
        
        cache_key = f"{user_id}:{session_id}"
        
        if cache_key not in self.repeated_opener_cache:
            self.repeated_opener_cache[cache_key] = []
        
        session_openers = self.repeated_opener_cache[cache_key]
        
        # Check if this opener was used recently in this session
        if response_start in session_openers:
            await self.log_error(
                error_type="repeated_opener",
                message=f"Agent repeated opener pattern: '{response_start}'",
                context={
                    "response_start": response_start,
                    "session_id": session_id,
                    "user_id": user_id,
                    "previous_openers": session_openers.copy()
                }
            )
            return True
        
        # Add to cache (keep last 5 openers)
        session_openers.append(response_start)
        if len(session_openers) > 5:
            session_openers.pop(0)
        
        return False
    
    async def analyze_response_quality(self, response: str, user_message: str, session_id: str, user_id: str, expected_topic: str = None):
        """Comprehensive response quality analysis"""
        errors_found = []
        
        # Check all error types
        if await self.check_loopback_error(response, user_message, session_id, user_id):
            errors_found.append("loopback")
        
        if await self.check_off_topic_reset(response, user_message, session_id, user_id, expected_topic):
            errors_found.append("off_topic")
        
        if await self.check_repeated_opener(response, session_id, user_id):
            errors_found.append("repeated_opener")
        
        return errors_found
    
    async def get_error_logs(self, limit: int = 100, error_type: str = None) -> List[Dict[str, Any]]:
        """Get recent error logs"""
        try:
            query = {}
            if error_type:
                query["type"] = error_type
            
            logs = await self.db.error_logs.find(query).sort("timestamp", -1).limit(limit).to_list(length=limit)
            
            # Convert datetime objects to strings for JSON serialization
            for log in logs:
                if isinstance(log.get("timestamp"), datetime):
                    log["timestamp"] = log["timestamp"].isoformat()
            
            return logs
            
        except Exception as e:
            self.logger.error(f"Failed to get error logs: {e}")
            return []
    
    async def clear_error_logs(self) -> int:
        """Clear all error logs"""
        try:
            result = await self.db.error_logs.delete_many({})
            self.logger.info(f"Cleared {result.deleted_count} error logs")
            return result.deleted_count
        except Exception as e:
            self.logger.error(f"Failed to clear error logs: {e}")
            return 0
    
    async def get_error_stats(self) -> Dict[str, int]:
        """Get error statistics"""
        try:
            pipeline = [
                {"$group": {"_id": "$type", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}}
            ]
            
            results = await self.db.error_logs.aggregate(pipeline).to_list(length=None)
            return {result["_id"]: result["count"] for result in results}
            
        except Exception as e:
            self.logger.error(f"Failed to get error stats: {e}")
            return {}

# Global instance
error_logger: Optional[ErrorLogger] = None

def get_error_logger() -> ErrorLogger:
    """Get the global error logger instance"""
    if error_logger is None:
        raise RuntimeError("Error logger not initialized")
    return error_logger

def initialize_error_logger(db: AsyncIOMotorDatabase) -> ErrorLogger:
    """Initialize the global error logger instance"""
    global error_logger
    error_logger = ErrorLogger(db)
    return error_logger