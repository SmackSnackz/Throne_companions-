# Throne Companions Analytics & Metrics System
# This is the royal control room for monitoring the kingdom

import uuid
import json
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class AnalyticsTracker:
    """Central analytics tracking system for Throne Companions"""
    
    def __init__(self, db_client=None):
        self.db = db_client
        
    async def track_event(self, event_type: str, user_id: str, session_id: str, 
                         payload: Dict[str, Any] = None, tier: str = "novice", 
                         companion: str = None, device: str = "web", region: str = "unknown"):
        """Track an analytics event"""
        
        event_record = {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "session_id": session_id,
            "event_type": event_type,
            "event_payload": payload or {},
            "tier": tier,
            "companion": companion,
            "device": device,
            "region": region,
            "created_at": datetime.utcnow()
        }
        
        try:
            # Store in MongoDB (in production would also send to external analytics)
            if self.db:
                await self.db.analytics_events.insert_one(event_record)
            
            # Log for debugging
            logger.info(f"Analytics Event: {event_type} - {user_id} - {payload}")
            
            return event_record
            
        except Exception as e:
            logger.error(f"Failed to track analytics event {event_type}: {e}")
            return None

    # Convenience methods for specific events
    async def track_signup(self, user_id: str, session_id: str, tier: str = "novice", **kwargs):
        return await self.track_event("signup", user_id, session_id, tier=tier, **kwargs)
    
    async def track_compliance_completed(self, user_id: str, session_id: str, tier: str = "novice", **kwargs):
        return await self.track_event("compliance_completed", user_id, session_id, tier=tier, **kwargs)
    
    async def track_onboarding_step(self, user_id: str, session_id: str, step: str, status: str, tier: str = "novice", **kwargs):
        payload = {"step": step, "status": status}
        return await self.track_event("onboarding_step", user_id, session_id, payload, tier=tier, **kwargs)
    
    async def track_onboarding_completed(self, user_id: str, session_id: str, completion_time_ms: int, tier: str = "novice", **kwargs):
        payload = {"completion_time_ms": completion_time_ms}
        return await self.track_event("onboarding_completed", user_id, session_id, payload, tier=tier, **kwargs)
    
    async def track_first_chat_started(self, user_id: str, session_id: str, companion: str, tier: str = "novice", **kwargs):
        return await self.track_event("first_chat_started", user_id, session_id, companion=companion, tier=tier, **kwargs)
    
    async def track_first_ritual_delivered(self, user_id: str, session_id: str, ritual_id: str, companion: str, tier: str = "novice", **kwargs):
        payload = {"ritual_id": ritual_id}
        return await self.track_event("first_ritual_delivered", user_id, session_id, payload, companion=companion, tier=tier, **kwargs)
    
    async def track_message_sent(self, user_id: str, session_id: str, message_id: str, length_chars: int, mode: str, companion: str, tier: str = "novice", **kwargs):
        payload = {"message_id": message_id, "length_chars": length_chars, "mode": mode}
        return await self.track_event("message_sent", user_id, session_id, payload, companion=companion, tier=tier, **kwargs)
    
    async def track_upgrade_cta_shown(self, user_id: str, session_id: str, target_tier: str, feature: str, companion: str, tier: str = "novice", **kwargs):
        payload = {"target_tier": target_tier, "feature": feature}
        return await self.track_event("upgrade_cta_shown", user_id, session_id, payload, companion=companion, tier=tier, **kwargs)
    
    async def track_upgrade_attempt(self, user_id: str, session_id: str, target_tier: str, companion: str, payment_method: str = None, tier: str = "novice", **kwargs):
        payload = {"target_tier": target_tier, "payment_method": payment_method}
        return await self.track_event("upgrade_attempt", user_id, session_id, payload, companion=companion, tier=tier, **kwargs)
    
    async def track_upgrade_success(self, user_id: str, session_id: str, target_tier: str, companion: str, previous_tier: str = "novice", **kwargs):
        payload = {"target_tier": target_tier, "previous_tier": previous_tier}
        return await self.track_event("upgrade_success", user_id, session_id, payload, companion=companion, tier=target_tier, **kwargs)
    
    async def track_tier_change(self, user_id: str, session_id: str, from_tier: str, to_tier: str, companion: str, **kwargs):
        payload = {"from_tier": from_tier, "to_tier": to_tier}
        return await self.track_event("tier_change", user_id, session_id, payload, companion=companion, tier=to_tier, **kwargs)
    
    async def track_session_end(self, user_id: str, session_id: str, session_length_seconds: int, companion: str, tier: str = "novice", **kwargs):
        payload = {"session_length_seconds": session_length_seconds}
        return await self.track_event("session_end", user_id, session_id, payload, companion=companion, tier=tier, **kwargs)
    
    async def track_feature_used(self, user_id: str, session_id: str, feature: str, companion: str, tier: str = "novice", **kwargs):
        payload = {"feature": feature}
        return await self.track_event("feature_used", user_id, session_id, payload, companion=companion, tier=tier, **kwargs)
    
    async def track_ritual_saved(self, user_id: str, session_id: str, ritual_id: str, companion: str, tier: str = "novice", **kwargs):
        payload = {"ritual_id": ritual_id}
        return await self.track_event("ritual_saved", user_id, session_id, payload, companion=companion, tier=tier, **kwargs)
    
    async def track_consent_requested(self, user_id: str, session_id: str, consent_type: str, companion: str, tier: str = "novice", **kwargs):
        payload = {"consent_type": consent_type}
        return await self.track_event("consent_requested", user_id, session_id, payload, companion=companion, tier=tier, **kwargs)
    
    async def track_consent_granted(self, user_id: str, session_id: str, consent_type: str, companion: str, tier: str = "novice", **kwargs):
        payload = {"consent_type": consent_type}
        return await self.track_event("consent_granted", user_id, session_id, payload, companion=companion, tier=tier, **kwargs)
    
    async def track_consent_denied(self, user_id: str, session_id: str, consent_type: str, companion: str, tier: str = "novice", **kwargs):
        payload = {"consent_type": consent_type}
        return await self.track_event("consent_denied", user_id, session_id, payload, companion=companion, tier=tier, **kwargs)
    
    async def track_safety_fallback_triggered(self, user_id: str, session_id: str, reason: str, companion: str, tier: str = "novice", **kwargs):
        payload = {"reason": reason}
        return await self.track_event("safety_fallback_triggered", user_id, session_id, payload, companion=companion, tier=tier, **kwargs)
    
    async def track_llm_request(self, user_id: str, session_id: str, latency_ms: int, success: bool, error_code: str = None, companion: str, tier: str = "novice", **kwargs):
        payload = {"latency_ms": latency_ms, "success": success, "error_code": error_code}
        return await self.track_event("llm_request", user_id, session_id, payload, companion=companion, tier=tier, **kwargs)
    
    async def track_memory_prune(self, user_id: str, session_id: str, items_pruned: int, retention_policy: str, companion: str, tier: str = "novice", **kwargs):
        payload = {"items_pruned": items_pruned, "retention_policy": retention_policy}
        return await self.track_event("memory_prune", user_id, session_id, payload, companion=companion, tier=tier, **kwargs)
    
    async def track_api_error(self, user_id: str, session_id: str, endpoint: str, error_code: str, companion: str = None, tier: str = "novice", **kwargs):
        payload = {"endpoint": endpoint, "error_code": error_code}
        return await self.track_event("api_error", user_id, session_id, payload, companion=companion, tier=tier, **kwargs)

# Global analytics instance
analytics_tracker = None

def get_analytics_tracker(db_client=None):
    """Get the global analytics tracker instance"""
    global analytics_tracker
    if analytics_tracker is None:
        analytics_tracker = AnalyticsTracker(db_client)
    return analytics_tracker