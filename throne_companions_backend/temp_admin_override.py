"""
Temporary Administrative Tier Override System
For Roy Carnell Johnson - Quantum Sovereign Access Level Investigation
Session-based, reversible, no permanent changes to core systems
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime, timezone, timedelta

class TempAdminOverride:
    """
    Temporary admin override system for tier investigation
    Session-based with automatic expiry
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.active_overrides = {}  # In-memory storage for session-based overrides
        self.authorized_investigators = [
            "roy@thronecompanions.com",
            "roy.carnell.johnson@gmail.com", 
            "roycarnelljohnson@gmail.com",
            "roy@emergent.com"
        ]
    
    def activate_sovereign_investigation(self, user_email: str, session_id: str) -> bool:
        """
        Activate Quantum Sovereign Access Level for authorized investigator
        Returns True if activation successful
        """
        if not self._is_authorized_investigator(user_email):
            self.logger.warning(f"Unauthorized tier investigation attempt by {user_email}")
            return False
        
        # Create temporary override with 24-hour expiry
        override_data = {
            "user_email": user_email,
            "session_id": session_id,
            "activated_at": datetime.now(timezone.utc),
            "expires_at": datetime.now(timezone.utc) + timedelta(hours=24),
            "tier_override": "sovereign",
            "feature_unlocks": {
                "voice": True,
                "visuals": True,
                "finance_tools": True,
                "intimacy_modes": True,
                "custom_persona": True,
                "private_hosting": True
            },
            "memory_retention_override": -1,  # Unlimited
            "prompting_mastery_override": "quantum_sovereign"
        }
        
        override_key = f"{user_email}:{session_id}"
        self.active_overrides[override_key] = override_data
        
        self.logger.info(f"Quantum Sovereign Access activated for {user_email} (session: {session_id})")
        return True
    
    def check_tier_override(self, user_email: str, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Check if user has active tier override
        Returns override data if active, None otherwise
        """
        override_key = f"{user_email}:{session_id}"
        
        if override_key not in self.active_overrides:
            return None
        
        override_data = self.active_overrides[override_key]
        
        # Check if override has expired
        if datetime.now(timezone.utc) > override_data["expires_at"]:
            self.logger.info(f"Expired tier override removed for {user_email}")
            del self.active_overrides[override_key]
            return None
        
        return override_data
    
    def get_effective_tier_config(self, user_email: str, session_id: str, base_tier: str = "novice") -> Dict[str, Any]:
        """
        Get effective tier configuration with override applied
        """
        override_data = self.check_tier_override(user_email, session_id)
        
        if not override_data:
            # No override active, return base tier
            from tier_configs import get_tier_config
            return get_tier_config(base_tier)
        
        # Return Quantum Sovereign configuration
        return {
            "display_name": "Quantum Sovereign (Investigation Mode)",
            "price": "INVESTIGATION_PASS",
            "memory_retention_days": override_data["memory_retention_override"],
            "prompting_mastery": override_data["prompting_mastery_override"],
            "features": override_data["feature_unlocks"],
            "tier_level": "sovereign",
            "investigation_mode": True,
            "finance_access": True,
            "custom_logic_access": True,
            "memory_tier_breakdown": {
                "novice": 3,
                "apprentice": 10,
                "regent": 50,
                "sovereign": -1
            },
            "response_style_shifts": {
                "base": "quantum_sovereign",
                "emotional_depth": "unlimited",
                "context_awareness": "maximum",
                "personalization": "complete"
            }
        }
    
    def get_all_tier_preview(self, user_email: str, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get preview of all tier configurations for investigation
        Only available to authorized investigators with active override
        """
        override_data = self.check_tier_override(user_email, session_id)
        
        if not override_data:
            return None
        
        from tier_configs import TIER_CONFIGS
        
        # Enhanced tier preview with finance and custom features
        tier_preview = {}
        for tier_name, config in TIER_CONFIGS.items():
            enhanced_config = config.copy()
            
            # Add finance module information
            enhanced_config["finance_features"] = self._get_finance_features_for_tier(tier_name)
            
            # Add memory breakdown details
            enhanced_config["memory_details"] = self._get_memory_details_for_tier(tier_name)
            
            # Add response style information
            enhanced_config["response_styles"] = self._get_response_styles_for_tier(tier_name)
            
            tier_preview[tier_name] = enhanced_config
        
        return {
            "investigation_mode": True,
            "investigator": user_email,
            "tier_configurations": tier_preview,
            "finance_modules": self._get_all_finance_modules(),
            "custom_logic": self._get_custom_logic_preview()
        }
    
    def deactivate_override(self, user_email: str, session_id: str) -> bool:
        """
        Manually deactivate tier override
        """
        override_key = f"{user_email}:{session_id}"
        
        if override_key in self.active_overrides:
            del self.active_overrides[override_key]
            self.logger.info(f"Tier override deactivated for {user_email}")
            return True
        
        return False
    
    def _is_authorized_investigator(self, user_email: str) -> bool:
        """Check if user is authorized for tier investigation"""
        return user_email.lower() in [email.lower() for email in self.authorized_investigators]
    
    def _get_finance_features_for_tier(self, tier_name: str) -> Dict[str, Any]:
        """Get finance features available for specific tier"""
        finance_features = {
            "novice": {
                "expense_tracking": False,
                "budget_planning": False,
                "investment_advice": False,
                "tax_optimization": False,
                "wealth_management": False
            },
            "apprentice": {
                "expense_tracking": True,
                "budget_planning": True,
                "investment_advice": False,
                "tax_optimization": False,
                "wealth_management": False
            },
            "regent": {
                "expense_tracking": True,
                "budget_planning": True,
                "investment_advice": True,
                "tax_optimization": True,
                "wealth_management": False
            },
            "sovereign": {
                "expense_tracking": True,
                "budget_planning": True,
                "investment_advice": True,
                "tax_optimization": True,
                "wealth_management": True
            }
        }
        return finance_features.get(tier_name, {})
    
    def _get_memory_details_for_tier(self, tier_name: str) -> Dict[str, Any]:
        """Get detailed memory configuration for tier"""
        memory_details = {
            "novice": {
                "retention_days": 1,
                "summary_count": 3,
                "context_depth": "shallow",
                "personalization": "basic"
            },
            "apprentice": {
                "retention_days": 7,
                "summary_count": 10,
                "context_depth": "moderate",
                "personalization": "enhanced"
            },
            "regent": {
                "retention_days": 30,
                "summary_count": 50,
                "context_depth": "deep",
                "personalization": "advanced"
            },
            "sovereign": {
                "retention_days": -1,
                "summary_count": -1,
                "context_depth": "unlimited",
                "personalization": "quantum"
            }
        }
        return memory_details.get(tier_name, {})
    
    def _get_response_styles_for_tier(self, tier_name: str) -> Dict[str, Any]:
        """Get response style configurations for tier"""
        response_styles = {
            "novice": {
                "depth": "surface",
                "personalization": "generic",
                "emotional_intelligence": "basic",
                "context_awareness": "limited"
            },
            "apprentice": {
                "depth": "moderate", 
                "personalization": "tailored",
                "emotional_intelligence": "enhanced",
                "context_awareness": "good"
            },
            "regent": {
                "depth": "comprehensive",
                "personalization": "sophisticated",
                "emotional_intelligence": "advanced",
                "context_awareness": "excellent"
            },
            "sovereign": {
                "depth": "quantum",
                "personalization": "transcendent",
                "emotional_intelligence": "empathic_ai",
                "context_awareness": "omniscient"
            }
        }
        return response_styles.get(tier_name, {})
    
    def _get_all_finance_modules(self) -> Dict[str, Any]:
        """Get all available finance modules for investigation"""
        return {
            "expense_tracking": {
                "description": "Track and categorize personal expenses",
                "features": ["receipt_ocr", "category_automation", "spending_analytics"],
                "integration": "banking_apis"
            },
            "budget_planning": {
                "description": "Create and manage personal budgets",
                "features": ["goal_setting", "progress_tracking", "alerts"],
                "integration": "financial_planning_engine"
            },
            "investment_advice": {
                "description": "Personalized investment recommendations",
                "features": ["portfolio_analysis", "risk_assessment", "market_insights"],
                "integration": "investment_data_feeds"
            },
            "tax_optimization": {
                "description": "Tax planning and optimization strategies",
                "features": ["deduction_finder", "tax_planning", "document_prep"],
                "integration": "tax_calculation_engine"
            },
            "wealth_management": {
                "description": "Comprehensive wealth management suite",
                "features": ["estate_planning", "retirement_planning", "insurance_analysis"],
                "integration": "wealth_management_platform"
            }
        }
    
    def _get_custom_logic_preview(self) -> Dict[str, Any]:
        """Get custom logic configurations for investigation"""
        return {
            "persona_adaptation": {
                "description": "Dynamic persona adaptation based on user interaction",
                "triggers": ["emotional_state", "conversation_context", "time_of_day"],
                "customization_levels": ["basic", "advanced", "quantum"]
            },
            "response_generation": {
                "description": "Advanced response generation algorithms",
                "methods": ["template_based", "ai_generated", "hybrid_quantum"],
                "personalization_factors": ["history", "preferences", "emotional_profile"]
            },
            "tier_progression": {
                "description": "Intelligent tier progression recommendations",
                "analysis": ["usage_patterns", "feature_requests", "engagement_metrics"],
                "triggers": ["feature_gates", "usage_limits", "value_demonstration"]
            }
        }

# Global instance
temp_admin_override = TempAdminOverride()