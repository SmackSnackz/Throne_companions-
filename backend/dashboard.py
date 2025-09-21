# Throne Companions Dashboard System
# Royal control room for monitoring the kingdom

from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from datetime import datetime, timedelta
import logging
from metrics_calculator import MetricsCalculator

logger = logging.getLogger(__name__)

# Create dashboard router
dashboard_router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])

def create_dashboard_routes(db_client):
    """Create dashboard routes with database client"""
    
    metrics_calc = MetricsCalculator(db_client)
    
    @dashboard_router.get("/")
    async def dashboard_home():
        """Dashboard home - basic info"""
        return {
            "message": "Welcome to the Throne Companions Royal Control Room",
            "version": "1.0.0",
            "endpoints": [
                "/kpis - Executive KPI overview",
                "/funnel - Onboarding funnel metrics", 
                "/content - Content performance metrics",
                "/upgrades - Upgrade and monetization metrics",
                "/health - System health metrics",
                "/events - Recent events"
            ]
        }
    
    @dashboard_router.get("/kpis")
    async def get_kpi_overview(days: int = Query(7, ge=1, le=90)):
        """Get executive KPI overview"""
        try:
            return await metrics_calc.get_kpi_overview(days)
        except Exception as e:
            logger.error(f"Error fetching KPI overview: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @dashboard_router.get("/funnel")
    async def get_onboarding_funnel(days: int = Query(7, ge=1, le=90)):
        """Get onboarding funnel metrics"""
        try:
            return await metrics_calc.get_onboarding_funnel(days)
        except Exception as e:
            logger.error(f"Error fetching onboarding funnel: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @dashboard_router.get("/content")
    async def get_content_performance(days: int = Query(30, ge=1, le=365)):
        """Get content performance metrics"""
        try:
            return await metrics_calc.get_content_performance(days)
        except Exception as e:
            logger.error(f"Error fetching content performance: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @dashboard_router.get("/upgrades")
    async def get_upgrade_metrics(days: int = Query(30, ge=1, le=365)):
        """Get upgrade and monetization metrics"""
        try:
            return await metrics_calc.get_upgrade_metrics(days)
        except Exception as e:
            logger.error(f"Error fetching upgrade metrics: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @dashboard_router.get("/health")
    async def get_system_health(hours: int = Query(24, ge=1, le=168)):
        """Get system health metrics"""
        try:
            return await metrics_calc.get_system_health(hours)
        except Exception as e:
            logger.error(f"Error fetching system health: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @dashboard_router.get("/events")
    async def get_recent_events(
        limit: int = Query(100, ge=1, le=1000),
        event_type: Optional[str] = None,
        user_id: Optional[str] = None,
        companion: Optional[str] = None
    ):
        """Get recent analytics events"""
        try:
            # Build filter
            filter_query = {}
            if event_type:
                filter_query["event_type"] = event_type
            if user_id:
                filter_query["user_id"] = user_id
            if companion:
                filter_query["companion"] = companion
            
            # Get recent events
            events = await db_client.analytics_events.find(filter_query).sort("created_at", -1).limit(limit).to_list(limit)
            
            # Sanitize events (remove sensitive data)
            sanitized_events = []
            for event in events:
                sanitized_event = {
                    "id": event.get("id"),
                    "event_type": event.get("event_type"),
                    "user_id": event.get("user_id", "")[:8] + "..." if event.get("user_id") else None,  # Partially anonymize
                    "session_id": event.get("session_id", "")[:8] + "..." if event.get("session_id") else None,
                    "tier": event.get("tier"),
                    "companion": event.get("companion"),
                    "device": event.get("device"),
                    "region": event.get("region"),
                    "created_at": event.get("created_at"),
                    "event_payload": event.get("event_payload", {})
                }
                sanitized_events.append(sanitized_event)
            
            return {
                "events": sanitized_events,
                "total_returned": len(sanitized_events),
                "filters_applied": filter_query,
                "retrieved_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error fetching recent events: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @dashboard_router.get("/alerts")
    async def get_alert_status():
        """Get current alert status and thresholds"""
        try:
            # Check various alert conditions
            alerts = []
            
            # Check onboarding completion rate (last 24h vs previous 24h)
            now = datetime.utcnow()
            yesterday = now - timedelta(days=1)
            day_before = now - timedelta(days=2)
            
            current_signups = await db_client.analytics_events.count_documents({
                "event_type": "signup",
                "created_at": {"$gte": yesterday}
            })
            
            current_completions = await db_client.analytics_events.count_documents({
                "event_type": "onboarding_completed", 
                "created_at": {"$gte": yesterday}
            })
            
            previous_signups = await db_client.analytics_events.count_documents({
                "event_type": "signup",
                "created_at": {"$gte": day_before, "$lt": yesterday}
            })
            
            previous_completions = await db_client.analytics_events.count_documents({
                "event_type": "onboarding_completed",
                "created_at": {"$gte": day_before, "$lt": yesterday}
            })
            
            current_rate = (current_completions / max(current_signups, 1)) * 100
            previous_rate = (previous_completions / max(previous_signups, 1)) * 100
            
            if previous_rate > 0 and ((previous_rate - current_rate) / previous_rate) > 0.20:
                alerts.append({
                    "type": "onboarding_drop",
                    "severity": "warning",
                    "message": f"Onboarding completion rate dropped from {previous_rate:.1f}% to {current_rate:.1f}%",
                    "threshold": "20% drop",
                    "current_value": current_rate,
                    "previous_value": previous_rate
                })
            
            # Check LLM error rate
            llm_requests = await db_client.analytics_events.count_documents({
                "event_type": "llm_request",
                "created_at": {"$gte": yesterday}
            })
            
            llm_errors = await db_client.analytics_events.count_documents({
                "event_type": "llm_request",
                "event_payload.success": False,
                "created_at": {"$gte": yesterday}
            })
            
            llm_error_rate = (llm_errors / max(llm_requests, 1)) * 100
            
            if llm_error_rate > 2.0:
                alerts.append({
                    "type": "llm_error_rate",
                    "severity": "critical" if llm_error_rate > 5.0 else "warning",
                    "message": f"LLM error rate is {llm_error_rate:.2f}%",
                    "threshold": "2%",
                    "current_value": llm_error_rate,
                    "errors": llm_errors,
                    "total_requests": llm_requests
                })
            
            # Check safety fallback spikes
            safety_events = await db_client.analytics_events.count_documents({
                "event_type": "safety_fallback_triggered",
                "created_at": {"$gte": yesterday}
            })
            
            if safety_events > 10:  # Arbitrary threshold
                alerts.append({
                    "type": "safety_spike",
                    "severity": "warning",
                    "message": f"Safety fallback triggered {safety_events} times in 24h",
                    "threshold": "10 events",
                    "current_value": safety_events
                })
            
            return {
                "alerts": alerts,
                "alert_count": len(alerts),
                "status": "healthy" if len(alerts) == 0 else "attention_required",
                "checked_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error checking alert status: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @dashboard_router.get("/export")
    async def export_metrics(
        format: str = Query("json", regex="^(json|csv)$"),
        days: int = Query(7, ge=1, le=90)
    ):
        """Export metrics data"""
        try:
            # Get all key metrics
            kpis = await metrics_calc.get_kpi_overview(days)
            funnel = await metrics_calc.get_onboarding_funnel(days)
            content = await metrics_calc.get_content_performance(days)
            upgrades = await metrics_calc.get_upgrade_metrics(days)
            health = await metrics_calc.get_system_health(24)
            
            export_data = {
                "export_info": {
                    "generated_at": datetime.utcnow().isoformat(),
                    "period_days": days,
                    "format": format
                },
                "kpis": kpis,
                "onboarding_funnel": funnel,
                "content_performance": content,
                "upgrade_metrics": upgrades,
                "system_health": health
            }
            
            if format == "json":
                return export_data
            elif format == "csv":
                # For CSV, flatten the data structure
                flattened_data = []
                for category, data in export_data.items():
                    if isinstance(data, dict):
                        for key, value in data.items():
                            flattened_data.append({
                                "category": category,
                                "metric": key,
                                "value": value
                            })
                
                return {"csv_data": flattened_data, "note": "Flattened for CSV export"}
            
        except Exception as e:
            logger.error(f"Error exporting metrics: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    return dashboard_router