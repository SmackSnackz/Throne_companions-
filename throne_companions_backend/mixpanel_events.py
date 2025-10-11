"""
Mixpanel Event Tracking System for Throne Companions
Implements event tracking for user actions with mock/test mode
"""

import logging
import json
import os
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
import uuid

try:
    import mixpanel
    MIXPANEL_AVAILABLE = True
except ImportError:
    MIXPANEL_AVAILABLE = False
    logging.warning("Mixpanel not available - running in mock mode")


class MixpanelTracker:
    """
    Mixpanel Event Tracking with mock mode support
    Tracks all user actions and stores events for proof/verification
    """

    def __init__(self, db: AsyncIOMotorDatabase, project_token: Optional[str] = None, mock_mode: bool = True):
        self.db = db
        self.mock_mode = mock_mode or not MIXPANEL_AVAILABLE or not project_token
        self.logger = logging.getLogger(__name__)
        
        if not self.mock_mode and MIXPANEL_AVAILABLE and project_token:
            self.mp = mixpanel.Mixpanel(project_token)
            self.logger.info("Mixpanel initialized with live tracking")
        else:
            self.mp = None
            self.logger.info("Mixpanel running in MOCK MODE - events logged to database")

    async def _log_mock_event(self, event_name: str, user_id: str, properties: Dict[str, Any]):
        """Log event to database for mock mode verification"""
        try:
            event_record = {
                "id": str(uuid.uuid4()),
                "event_name": event_name,
                "user_id": user_id,
                "properties": properties,
                "timestamp": datetime.now(timezone.utc),
                "mock_mode": True
            }
            
            await self.db.mixpanel_events.insert_one(event_record)
            self.logger.info(f"MOCK EVENT LOGGED: {event_name} for user {user_id}")
            
        except Exception as e:
            self.logger.error(f"Failed to log mock event: {e}")

    async def track_event(self, event_name: str, user_id: str, properties: Dict[str, Any] = None):
        """Track an event (live or mock mode)"""
        if properties is None:
            properties = {}
        
        # Add standard properties
        properties.update({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "platform": "throne_companions"
        })
        
        try:
            if self.mock_mode:
                # Mock mode - log to database
                await self._log_mock_event(event_name, user_id, properties)
            else:
                # Live mode - send to Mixpanel
                self.mp.track(user_id, event_name, properties)
                self.logger.info(f"LIVE EVENT TRACKED: {event_name} for user {user_id}")
                
        except Exception as e:
            self.logger.error(f"Event tracking failed: {e}")
            # Fallback to mock logging
            await self._log_mock_event(event_name, user_id, properties)

    # Event tracking methods for specific user actions

    async def track_companion_selected(self, user_id: str, companion_id: str, companion_name: str, session_id: str):
        """Track when user selects a companion during onboarding"""
        properties = {
            "companion_id": companion_id,
            "companion_name": companion_name,
            "session_id": session_id,
            "event_category": "onboarding",
            "step": "companion_selection"
        }
        await self.track_event("companion_selected", user_id, properties)

    async def track_tier_selected(self, user_id: str, tier_name: str, tier_price: str, session_id: str):
        """Track when user selects a subscription tier"""
        properties = {
            "tier_name": tier_name,
            "tier_price": tier_price,
            "session_id": session_id,
            "event_category": "onboarding",
            "step": "tier_selection"
        }
        await self.track_event("tier_selected", user_id, properties)

    async def track_message_sent(self, user_id: str, session_id: str, companion_id: str, message_length: int, user_tier: str):
        """Track when user sends a message"""
        properties = {
            "session_id": session_id,
            "companion_id": companion_id,
            "message_length": message_length,
            "user_tier": user_tier,
            "event_category": "engagement",
            "interaction_type": "message"
        }
        await self.track_event("message_sent", user_id, properties)

    async def track_session_started(self, user_id: str, session_id: str, companion_id: str, user_tier: str):
        """Track when user starts a new chat session"""
        properties = {
            "session_id": session_id,
            "companion_id": companion_id,
            "user_tier": user_tier,
            "event_category": "engagement",
            "session_type": "chat"
        }
        await self.track_event("session_started", user_id, properties)

    async def track_session_ended(self, user_id: str, session_id: str, companion_id: str, message_count: int, duration_minutes: Optional[int] = None):
        """Track when user ends a chat session"""
        properties = {
            "session_id": session_id,
            "companion_id": companion_id,
            "message_count": message_count,
            "event_category": "engagement",
            "session_type": "chat"
        }
        
        if duration_minutes is not None:
            properties["duration_minutes"] = duration_minutes
            
        await self.track_event("session_ended", user_id, properties)

    async def track_upgrade_tier_clicked(self, user_id: str, current_tier: str, target_tier: str, source: str, session_id: str):
        """Track when user clicks upgrade CTA"""
        properties = {
            "current_tier": current_tier,
            "target_tier": target_tier,
            "source": source,  # "chat_limit", "feature_gate", "tier_page"
            "session_id": session_id,
            "event_category": "conversion",
            "cta_type": "upgrade"
        }
        await self.track_event("upgrade_tier_clicked", user_id, properties)

    async def track_admin_mode_toggled(self, user_id: str, admin_enabled: bool, session_id: str):
        """Track when admin toggles admin mode (for testing)"""
        properties = {
            "admin_enabled": admin_enabled,
            "session_id": session_id,
            "event_category": "admin",
            "action_type": "mode_toggle"
        }
        await self.track_event("admin_mode_toggled", user_id, properties)

    async def track_memory_system_usage(self, user_id: str, session_id: str, memory_summaries_count: int, user_tier: str):
        """Track memory system usage"""
        properties = {
            "session_id": session_id,
            "memory_summaries_count": memory_summaries_count,
            "user_tier": user_tier,
            "event_category": "feature_usage",
            "feature": "memory_system"
        }
        await self.track_event("memory_system_used", user_id, properties)

    # Utility methods for verification

    async def get_mock_events(self, user_id: Optional[str] = None, event_name: Optional[str] = None) -> list:
        """Get mock events for verification (mock mode only)"""
        if not self.mock_mode:
            return []
        
        try:
            query = {}
            if user_id:
                query["user_id"] = user_id
            if event_name:
                query["event_name"] = event_name
            
            events = await self.db.mixpanel_events.find(query).sort("timestamp", -1).to_list(length=100)
            
            # Convert ObjectId to string for JSON serialization
            for event in events:
                if '_id' in event:
                    event['_id'] = str(event['_id'])
                # Convert datetime to ISO string if needed
                if 'timestamp' in event and hasattr(event['timestamp'], 'isoformat'):
                    event['timestamp'] = event['timestamp'].isoformat()
            
            return events
            
        except Exception as e:
            self.logger.error(f"Failed to get mock events: {e}")
            return []

    async def get_event_counts(self) -> Dict[str, int]:
        """Get event counts by event name"""
        try:
            pipeline = [
                {"$group": {"_id": "$event_name", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}}
            ]
            
            results = await self.db.mixpanel_events.aggregate(pipeline).to_list(length=None)
            return {result["_id"]: result["count"] for result in results}
            
        except Exception as e:
            self.logger.error(f"Failed to get event counts: {e}")
            return {}

    async def clear_mock_events(self):
        """Clear all mock events (for testing)"""
        if self.mock_mode:
            try:
                result = await self.db.mixpanel_events.delete_many({})
                self.logger.info(f"Cleared {result.deleted_count} mock events")
                return result.deleted_count
            except Exception as e:
                self.logger.error(f"Failed to clear mock events: {e}")
                return 0
        return 0


# Global tracker instance
mixpanel_tracker: Optional[MixpanelTracker] = None


def get_mixpanel_tracker() -> MixpanelTracker:
    """Get the global Mixpanel tracker instance"""
    if mixpanel_tracker is None:
        raise RuntimeError("Mixpanel tracker not initialized")
    return mixpanel_tracker


def initialize_mixpanel_tracker(db: AsyncIOMotorDatabase, project_token: Optional[str] = None, mock_mode: bool = True) -> MixpanelTracker:
    """Initialize the global Mixpanel tracker instance"""
    global mixpanel_tracker
    mixpanel_tracker = MixpanelTracker(db, project_token, mock_mode)
    return mixpanel_tracker