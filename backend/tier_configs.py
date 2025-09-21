# Throne Companions Tier Configuration
# This is the single source of truth for tier behavior

TIER_CONFIGS = {
    "novice": {
        "display_name": "Novice - Scroll of Truth",
        "price": 0,
        "memory_retention_days": 1,
        "allowed_modes": ["text"],
        "tools_enabled": [],
        "prompting_mastery": "clarity",
        "response_style": {"length": "short", "formality": "warm"}
    },
    "apprentice": {
        "display_name": "Apprentice - Scroll of Power & Humility",
        "price": 19,
        "memory_retention_days": 7,
        "allowed_modes": ["text", "voice", "visuals"],
        "tools_enabled": ["rituals", "growth_tracking"],
        "prompting_mastery": "depth",
        "response_style": {"length": "medium", "formality": "warm"}
    },
    "regent": {
        "display_name": "Regent - Scroll of Dominion",
        "price": 49,
        "memory_retention_days": 3650,
        "allowed_modes": ["text", "voice", "visuals", "finance"],
        "tools_enabled": ["rituals", "growth_tracking", "finance", "custom_packs"],
        "prompting_mastery": "creation",
        "response_style": {"length": "long", "formality": "regal"}
    },
    "sovereign": {
        "display_name": "Sovereign - Scroll of Conjoint Minds",
        "price": 99,
        "memory_retention_days": 36500,
        "allowed_modes": ["all"],
        "tools_enabled": ["rituals", "growth_tracking", "finance", "custom_packs", "persona_customizer", "private_hosting"],
        "prompting_mastery": "co-creation",
        "response_style": {"length": "long", "formality": "regal"}
    }
}

def get_tier_config(tier_name):
    """Get configuration for a specific tier"""
    return TIER_CONFIGS.get(tier_name, TIER_CONFIGS["novice"])

def get_all_tiers():
    """Get all available tiers"""
    return TIER_CONFIGS

def mode_required_tier(mode):
    """Get the minimum tier required for a specific mode"""
    mode_requirements = {
        "text": "novice",
        "voice": "apprentice",
        "visuals": "apprentice",
        "finance": "regent",
        "persona_customizer": "sovereign",
        "private_hosting": "sovereign"
    }
    return mode_requirements.get(mode, "sovereign")