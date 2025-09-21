# Throne Companions Mixpanel Integration
# Royal analytics for tracking seeker behavior and throne progression

import os
import uuid
import json
from datetime import datetime
from typing import Dict, Any, Optional
import logging
from mixpanel import Mixpanel

logger = logging.getLogger(__name__)

class MixpanelTracker:
    """Royal analytics tracker using Mixpanel for behavioral insights"""
    
    def __init__(self):
        # Get Mixpanel token from environment
        self.mixpanel_token = os.environ.get('MIXPANEL_TOKEN')
        
        if self.mixpanel_token:
            self.mp = Mixpanel(self.mixpanel_token)
            logger.info("Mixpanel tracker initialized successfully")
        else:
            self.mp = None
            logger.warning("MIXPANEL_TOKEN not found - using mock tracker")
    
    def _get_base_properties(self, user_id: str, session_id: str, tier: str = "novice", 
                           companion: str = None, device_type: str = "web", region: str = "unknown") -> Dict[str, Any]:
        """Get base properties for all events"""
        return {
            "distinct_id": user_id,
            "session_id": session_id,
            "tier": tier,
            "companion": companion,
            "device_type": device_type,
            "region": region,
            "timestamp": datetime.utcnow().isoformat(),
            "app_version": "1.0.0",
            "platform": "throne_companions"
        }
    
    def track_event(self, event_name: str, user_id: str, properties: Dict[str, Any] = None):
        """Track an event to Mixpanel"""
        if not self.mp:
            logger.debug(f"Mock Mixpanel Event: {event_name} - {user_id} - {properties}")
            return
        
        try:
            final_properties = properties or {}
            final_properties["distinct_id"] = user_id
            
            self.mp.track(user_id, event_name, final_properties)
            logger.debug(f"Mixpanel Event Tracked: {event_name}")
            
        except Exception as e:
            logger.error(f"Failed to track Mixpanel event {event_name}: {e}")
    
    def set_user_profile(self, user_id: str, properties: Dict[str, Any]):
        """Set user profile properties in Mixpanel People"""
        if not self.mp:
            logger.debug(f"Mock Mixpanel Profile: {user_id} - {properties}")
            return
        
        try:
            self.mp.people_set(user_id, properties)
            logger.debug(f"Mixpanel Profile Updated: {user_id}")
            
        except Exception as e:
            logger.error(f"Failed to update Mixpanel profile for {user_id}: {e}")
    
    def update_user_profile(self, user_id: str, properties: Dict[str, Any]):
        """Update user profile properties (alias for set_user_profile)"""
        self.set_user_profile(user_id, properties)
    
    # Event tracking methods per royal order
    
    def track_signup(self, user_id: str, session_id: str, method: str = "direct", source: str = "organic", **kwargs):
        """Track user signup"""
        properties = self._get_base_properties(user_id, session_id, **kwargs)
        properties.update({
            "method": method,
            "source": source
        })
        self.track_event("Signup", user_id, properties)
    
    def track_compliance_completed(self, user_id: str, session_id: str, compliance_version: str = "1.0", **kwargs):
        """Track compliance flow completion"""
        properties = self._get_base_properties(user_id, session_id, **kwargs)
        properties.update({
            "compliance_version": compliance_version
        })
        self.track_event("Compliance Completed", user_id, properties)
    
    def track_onboarding_step(self, user_id: str, session_id: str, step: str, status: str, **kwargs):
        """Track onboarding step progression"""
        properties = self._get_base_properties(user_id, session_id, **kwargs)
        properties.update({
            "step": step,
            "status": status
        })
        self.track_event("Onboarding Step", user_id, properties)
    
    def track_onboarding_completed(self, user_id: str, session_id: str, time_to_complete_seconds: int, **kwargs):
        """Track onboarding completion"""
        properties = self._get_base_properties(user_id, session_id, **kwargs)
        properties.update({
            "time_to_complete_seconds": time_to_complete_seconds,
            "time_to_complete_minutes": round(time_to_complete_seconds / 60, 2)
        })
        self.track_event("Onboarding Completed", user_id, properties)
    
    def track_first_chat_started(self, user_id: str, session_id: str, **kwargs):
        """Track first chat session started"""
        properties = self._get_base_properties(user_id, session_id, **kwargs)
        self.track_event("First Chat Started", user_id, properties)
    
    def track_first_ritual_delivered(self, user_id: str, session_id: str, ritual_id: str, ritual_tier: str, ritual_type: str = "starter", **kwargs):
        """Track first ritual delivery"""
        properties = self._get_base_properties(user_id, session_id, **kwargs)
        properties.update({
            "ritual_id": ritual_id,
            "ritual_tier": ritual_tier,
            "ritual_type": ritual_type
        })
        self.track_event("First Ritual Delivered", user_id, properties)
    
    def track_message_sent(self, user_id: str, session_id: str, message_id: str, length_chars: int, mode: str, **kwargs):
        """Track message sent by user"""
        properties = self._get_base_properties(user_id, session_id, **kwargs)
        properties.update({
            "message_id": message_id,
            "length_chars": length_chars,
            "mode": mode,
            "message_category": "short" if length_chars < 50 else "medium" if length_chars < 200 else "long"
        })
        self.track_event("Message Sent", user_id, properties)
    
    def track_upgrade_cta_shown(self, user_id: str, session_id: str, target_tier: str, feature_requested: str, placement: str = "chat", **kwargs):
        """Track upgrade CTA display"""
        properties = self._get_base_properties(user_id, session_id, **kwargs)
        properties.update({
            "target_tier": target_tier,
            "feature_requested": feature_requested,
            "placement": placement
        })
        self.track_event("Upgrade CTA Shown", user_id, properties)
    
    def track_upgrade_attempt(self, user_id: str, session_id: str, target_tier: str, payment_method: str = "none", **kwargs):
        """Track upgrade attempt"""
        properties = self._get_base_properties(user_id, session_id, **kwargs)
        properties.update({
            "target_tier": target_tier,
            "payment_method": payment_method
        })
        self.track_event("Upgrade Attempt", user_id, properties)
    
    def track_upgrade_success(self, user_id: str, session_id: str, target_tier: str, price: float = 0, previous_tier: str = "novice", **kwargs):
        """Track successful upgrade"""
        properties = self._get_base_properties(user_id, session_id, **kwargs)
        properties.update({
            "target_tier": target_tier,
            "previous_tier": previous_tier,
            "price": price
        })
        self.track_event("Upgrade Success", user_id, properties)
        
        # Update user profile with new tier
        self.update_user_profile(user_id, {
            "tier": target_tier,
            "last_upgrade_date": datetime.utcnow().isoformat()
        })
    
    def track_feature_used(self, user_id: str, session_id: str, feature: str, **kwargs):
        """Track feature usage"""
        properties = self._get_base_properties(user_id, session_id, **kwargs)
        properties.update({
            "feature": feature
        })
        self.track_event("Feature Used", user_id, properties)
    
    def track_ritual_saved(self, user_id: str, session_id: str, ritual_id: str, **kwargs):
        """Track ritual saved by user"""
        properties = self._get_base_properties(user_id, session_id, **kwargs)
        properties.update({
            "ritual_id": ritual_id
        })
        self.track_event("Ritual Saved", user_id, properties)
    
    def track_consent_requested(self, user_id: str, session_id: str, consent_type: str, **kwargs):
        """Track consent request"""
        properties = self._get_base_properties(user_id, session_id, **kwargs)
        properties.update({
            "consent_type": consent_type
        })
        self.track_event("Consent Requested", user_id, properties)
    
    def track_consent_granted(self, user_id: str, session_id: str, consent_type: str, **kwargs):
        """Track consent granted"""
        properties = self._get_base_properties(user_id, session_id, **kwargs)
        properties.update({
            "consent_type": consent_type
        })
        self.track_event("Consent Granted", user_id, properties)
    
    def track_consent_denied(self, user_id: str, session_id: str, consent_type: str, **kwargs):
        """Track consent denied"""
        properties = self._get_base_properties(user_id, session_id, **kwargs)
        properties.update({
            "consent_type": consent_type
        })
        self.track_event("Consent Denied", user_id, properties)
    
    def track_safety_fallback_triggered(self, user_id: str, session_id: str, reason: str, **kwargs):
        """Track safety fallback trigger"""
        properties = self._get_base_properties(user_id, session_id, **kwargs)
        properties.update({
            "reason": reason
        })
        self.track_event("Safety Fallback Triggered", user_id, properties)
    
    def track_llm_request(self, user_id: str, session_id: str, latency_ms: int, success: bool, error_code: str = None, **kwargs):
        """Track LLM request performance"""
        properties = self._get_base_properties(user_id, session_id, **kwargs)
        properties.update({
            "latency_ms": latency_ms,
            "success": success,
            "error_code": error_code,
            "latency_category": "fast" if latency_ms < 1000 else "medium" if latency_ms < 3000 else "slow"
        })
        self.track_event("LLM Request", user_id, properties)
    
    def track_api_error(self, user_id: str, session_id: str, endpoint: str, error_code: str, **kwargs):
        """Track API error"""
        properties = self._get_base_properties(user_id, session_id, **kwargs)
        properties.update({
            "endpoint": endpoint,
            "error_code": error_code
        })
        self.track_event("API Error", user_id, properties)
    
    def initialize_user_profile(self, user_id: str, email: str = None, tier: str = "novice", 
                              chosen_companion: str = "sophia", memory_retention_days: int = 1, 
                              features_enabled: Dict[str, bool] = None):
        """Initialize user profile in Mixpanel People"""
        features_enabled = features_enabled or {
            "voice": False,
            "visuals": False,
            "finance_tools": False,
            "intimacy_modes": False,
            "custom_persona": False,
            "private_hosting": False
        }
        
        profile_properties = {
            "email": email,
            "tier": tier,
            "chosen_companion": chosen_companion,
            "memory_retention_days": memory_retention_days,
            "features_enabled": json.dumps(features_enabled),
            "created_at": datetime.utcnow().isoformat(),
            "last_seen_at": datetime.utcnow().isoformat(),
            "onboarding_completed": False
        }
        
        self.set_user_profile(user_id, profile_properties)
    
    def update_user_activity(self, user_id: str):
        """Update user's last seen timestamp"""
        self.update_user_profile(user_id, {
            "last_seen_at": datetime.utcnow().isoformat()
        })

# Global Mixpanel tracker instance
mixpanel_tracker = None

def get_mixpanel_tracker():
    """Get the global Mixpanel tracker instance"""
    global mixpanel_tracker
    if mixpanel_tracker is None:
        mixpanel_tracker = MixpanelTracker()
    return mixpanel_tracker