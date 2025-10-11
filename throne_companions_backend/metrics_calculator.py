# Throne Companions Metrics Calculator
# Calculates key metrics and KPIs from analytics events

from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)

class MetricsCalculator:
    """Calculates key metrics for the Throne Companions dashboard"""
    
    def __init__(self, db_client):
        self.db = db_client
    
    async def get_kpi_overview(self, days: int = 7) -> Dict[str, Any]:
        """Get executive KPI overview"""
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        try:
            # Daily Active Users
            dau_pipeline = [
                {"$match": {"created_at": {"$gte": start_date}, "event_type": {"$in": ["message_sent", "first_chat_started"]}}},
                {"$group": {"_id": {"$dateToString": {"format": "%Y-%m-%d", "date": "$created_at"}}, "active_users": {"$addToSet": "$user_id"}}},
                {"$project": {"date": "$_id", "active_users": {"$size": "$active_users"}}},
                {"$sort": {"date": -1}}
            ]
            dau_result = await self.db.analytics_events.aggregate(dau_pipeline).to_list(days)
            current_dau = dau_result[0]["active_users"] if dau_result else 0
            
            # New Signups (24h)
            yesterday = end_date - timedelta(days=1)
            new_signups = await self.db.analytics_events.count_documents({
                "event_type": "signup",
                "created_at": {"$gte": yesterday}
            })
            
            # Onboarding Completion Rate (24h)
            signups_24h = await self.db.analytics_events.count_documents({
                "event_type": "signup",
                "created_at": {"$gte": yesterday}
            })
            
            onboarding_completed_24h = await self.db.analytics_events.count_documents({
                "event_type": "onboarding_completed",
                "created_at": {"$gte": yesterday}
            })
            
            onboarding_completion_rate = (onboarding_completed_24h / max(signups_24h, 1)) * 100
            
            # Free→Paid Conversion (30d) - placeholder since payments not implemented
            upgrade_attempts_30d = await self.db.analytics_events.count_documents({
                "event_type": "upgrade_attempt",
                "created_at": {"$gte": end_date - timedelta(days=30)}
            })
            
            upgrade_success_30d = await self.db.analytics_events.count_documents({
                "event_type": "upgrade_success",
                "created_at": {"$gte": end_date - timedelta(days=30)}
            })
            
            conversion_rate = (upgrade_success_30d / max(upgrade_attempts_30d, 1)) * 100
            
            # LLM Error Rate
            llm_requests = await self.db.analytics_events.count_documents({
                "event_type": "llm_request",
                "created_at": {"$gte": start_date}
            })
            
            llm_errors = await self.db.analytics_events.count_documents({
                "event_type": "llm_request",
                "event_payload.success": False,
                "created_at": {"$gte": start_date}
            })
            
            llm_error_rate = (llm_errors / max(llm_requests, 1)) * 100
            
            return {
                "daily_active_users": current_dau,
                "new_signups_24h": new_signups,
                "onboarding_completion_rate": round(onboarding_completion_rate, 2),
                "free_to_paid_conversion_30d": round(conversion_rate, 2),
                "churn_rate_30d": 0,  # Placeholder - would need retention analysis
                "llm_error_rate": round(llm_error_rate, 2),
                "period": f"{days} days",
                "calculated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error calculating KPI overview: {e}")
            return {"error": str(e)}
    
    async def get_onboarding_funnel(self, days: int = 7) -> Dict[str, Any]:
        """Get onboarding funnel metrics"""
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        try:
            # Count events in funnel
            signups = await self.db.analytics_events.count_documents({
                "event_type": "signup",
                "created_at": {"$gte": start_date}
            })
            
            onboarding_completed = await self.db.analytics_events.count_documents({
                "event_type": "onboarding_completed",
                "created_at": {"$gte": start_date}
            })
            
            first_chat_started = await self.db.analytics_events.count_documents({
                "event_type": "first_chat_started",
                "created_at": {"$gte": start_date}
            })
            
            first_ritual_delivered = await self.db.analytics_events.count_documents({
                "event_type": "first_ritual_delivered",
                "created_at": {"$gte": start_date}
            })
            
            # Users with 3+ messages (activation threshold)
            three_message_users_pipeline = [
                {"$match": {"event_type": "message_sent", "created_at": {"$gte": start_date}}},
                {"$group": {"_id": "$user_id", "message_count": {"$sum": 1}}},
                {"$match": {"message_count": {"$gte": 3}}},
                {"$count": "active_users"}
            ]
            
            three_message_result = await self.db.analytics_events.aggregate(three_message_users_pipeline).to_list(1)
            three_message_users = three_message_result[0]["active_users"] if three_message_result else 0
            
            # Calculate conversion rates
            funnel_steps = [
                {"step": "signups", "count": signups, "conversion": 100.0},
                {"step": "onboarding_completed", "count": onboarding_completed, "conversion": (onboarding_completed / max(signups, 1)) * 100},
                {"step": "first_chat_started", "count": first_chat_started, "conversion": (first_chat_started / max(signups, 1)) * 100},
                {"step": "first_ritual_delivered", "count": first_ritual_delivered, "conversion": (first_ritual_delivered / max(signups, 1)) * 100},
                {"step": "three_message_activation", "count": three_message_users, "conversion": (three_message_users / max(signups, 1)) * 100}
            ]
            
            return {
                "funnel_steps": funnel_steps,
                "period": f"{days} days",
                "calculated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error calculating onboarding funnel: {e}")
            return {"error": str(e)}
    
    async def get_content_performance(self, days: int = 30) -> Dict[str, Any]:
        """Get content performance metrics"""
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        try:
            # Most delivered rituals
            ritual_delivery_pipeline = [
                {"$match": {"event_type": "first_ritual_delivered", "created_at": {"$gte": start_date}}},
                {"$group": {"_id": "$event_payload.ritual_id", "delivery_count": {"$sum": 1}}},
                {"$sort": {"delivery_count": -1}},
                {"$limit": 10}
            ]
            
            top_rituals = await self.db.analytics_events.aggregate(ritual_delivery_pipeline).to_list(10)
            
            # Ritual save rate
            total_rituals_delivered = await self.db.analytics_events.count_documents({
                "event_type": "first_ritual_delivered",
                "created_at": {"$gte": start_date}
            })
            
            rituals_saved = await self.db.analytics_events.count_documents({
                "event_type": "ritual_saved",
                "created_at": {"$gte": start_date}
            })
            
            save_rate = (rituals_saved / max(total_rituals_delivered, 1)) * 100
            
            # Content engagement by companion
            companion_engagement_pipeline = [
                {"$match": {"event_type": {"$in": ["first_ritual_delivered", "message_sent"]}, "created_at": {"$gte": start_date}}},
                {"$group": {"_id": {"companion": "$companion", "event": "$event_type"}, "count": {"$sum": 1}}},
                {"$group": {"_id": "$_id.companion", "events": {"$push": {"event": "$_id.event", "count": "$count"}}}},
                {"$sort": {"_id": 1}}
            ]
            
            companion_engagement = await self.db.analytics_events.aggregate(companion_engagement_pipeline).to_list(10)
            
            return {
                "top_rituals": [{"ritual_id": r["_id"], "delivery_count": r["delivery_count"]} for r in top_rituals],
                "ritual_save_rate": round(save_rate, 2),
                "total_rituals_delivered": total_rituals_delivered,
                "companion_engagement": companion_engagement,
                "period": f"{days} days",
                "calculated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error calculating content performance: {e}")
            return {"error": str(e)}
    
    async def get_upgrade_metrics(self, days: int = 30) -> Dict[str, Any]:
        """Get upgrade and monetization metrics"""
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        try:
            # Upgrade CTA performance
            cta_shown = await self.db.analytics_events.count_documents({
                "event_type": "upgrade_cta_shown",
                "created_at": {"$gte": start_date}
            })
            
            upgrade_attempts = await self.db.analytics_events.count_documents({
                "event_type": "upgrade_attempt",
                "created_at": {"$gte": start_date}
            })
            
            upgrade_successes = await self.db.analytics_events.count_documents({
                "event_type": "upgrade_success",
                "created_at": {"$gte": start_date}
            })
            
            cta_ctr = (upgrade_attempts / max(cta_shown, 1)) * 100
            conversion_rate = (upgrade_successes / max(upgrade_attempts, 1)) * 100
            
            # Upgrade performance by target tier
            tier_performance_pipeline = [
                {"$match": {"event_type": {"$in": ["upgrade_cta_shown", "upgrade_attempt", "upgrade_success"]}, "created_at": {"$gte": start_date}}},
                {"$group": {"_id": {"tier": "$event_payload.target_tier", "event": "$event_type"}, "count": {"$sum": 1}}},
                {"$group": {"_id": "$_id.tier", "events": {"$push": {"event": "$_id.event", "count": "$count"}}}},
                {"$sort": {"_id": 1}}
            ]
            
            tier_performance = await self.db.analytics_events.aggregate(tier_performance_pipeline).to_list(10)
            
            return {
                "cta_shown": cta_shown,
                "upgrade_attempts": upgrade_attempts,
                "upgrade_successes": upgrade_successes,
                "cta_click_through_rate": round(cta_ctr, 2),
                "attempt_to_success_rate": round(conversion_rate, 2),
                "tier_performance": tier_performance,
                "period": f"{days} days",
                "calculated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error calculating upgrade metrics: {e}")
            return {"error": str(e)}
    
    async def get_system_health(self, hours: int = 24) -> Dict[str, Any]:
        """Get system health metrics"""
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(hours=hours)
        
        try:
            # LLM performance
            llm_performance_pipeline = [
                {"$match": {"event_type": "llm_request", "created_at": {"$gte": start_date}}},
                {"$group": {
                    "_id": None,
                    "total_requests": {"$sum": 1},
                    "successful_requests": {"$sum": {"$cond": [{"$eq": ["$event_payload.success", True]}, 1, 0]}},
                    "avg_latency": {"$avg": "$event_payload.latency_ms"},
                    "max_latency": {"$max": "$event_payload.latency_ms"}
                }}
            ]
            
            llm_result = await self.db.analytics_events.aggregate(llm_performance_pipeline).to_list(1)
            llm_stats = llm_result[0] if llm_result else {"total_requests": 0, "successful_requests": 0, "avg_latency": 0, "max_latency": 0}
            
            # API errors
            api_errors = await self.db.analytics_events.count_documents({
                "event_type": "api_error",
                "created_at": {"$gte": start_date}
            })
            
            # Safety events
            safety_events = await self.db.analytics_events.count_documents({
                "event_type": "safety_fallback_triggered",
                "created_at": {"$gte": start_date}
            })
            
            error_rate = ((llm_stats["total_requests"] - llm_stats["successful_requests"]) / max(llm_stats["total_requests"], 1)) * 100
            
            return {
                "llm_total_requests": llm_stats["total_requests"],
                "llm_success_rate": round(((llm_stats["successful_requests"] / max(llm_stats["total_requests"], 1)) * 100), 2),
                "llm_error_rate": round(error_rate, 2),
                "llm_avg_latency_ms": round(llm_stats["avg_latency"] or 0, 2),
                "llm_max_latency_ms": llm_stats["max_latency"] or 0,
                "api_errors": api_errors,
                "safety_events": safety_events,
                "period": f"{hours} hours",
                "calculated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error calculating system health: {e}")
            return {"error": str(e)}