from tier_configs import TIER_CONFIGS, get_tier_config, mode_required_tier
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

def assemble_system_prompt(companion_id, tier, tier_config):
    """Assemble system prompt according to specification rules"""
    
    # A) COMPANION HEADER
    companion_headers = {
        "sophia": "You are Sophia — a wise, elegant, sophisticated mentor. Address the user respectfully with depth and wisdom. Use the voice guidelines below.",
        "aurora": "You are Aurora — a warm, creative, energetic mentor. Address the user respectfully and inspire them. Use the voice guidelines below.",
        "vanessa": "You are Vanessa — a mysterious, alluring, confident mentor. Address the user respectfully with intrigue and elegance. Use the voice guidelines below."
    }
    
    header = companion_headers.get(companion_id, f"You are {companion_id} — a respectful AI mentor.")
    
    # B) TIER INSTRUCTION
    tier_instruction = f"User tier: {tier}. Memory: {tier_config['memory_retention_days']} days. Allowed modes: {tier_config['allowed_modes']}. Prompting Mastery: {tier_config['prompting_mastery']}."
    
    # C) BEHAVIOR RULES
    response_style = f"Tone/length: {tier_config['response_style']}."
    
    behavior_rules = {
        "novice": "Answer ≤4 sentences; give 1 action.",
        "apprentice": "Provide 2–3 step exercises + one measurable action.",
        "regent": "Provide multi-step plans, offer file/trackers, reference saved memory.",
        "sovereign": "Provide co-creation options, persona-building, ask consent for intimacy/therapy."
    }
    
    behavior_rule = behavior_rules.get(tier, behavior_rules["novice"])
    
    # D) SAFETY / CONSENT
    safety_rules = "Require explicit text consent each session before intimacy/therapy. For finance: include 'not financial advice' disclaimer and require explicit confirmation. Log consent events."
    
    # E) UPGRADE CTA SNIPPET
    upgrade_cta = "If user requests a locked feature, respond: \"I can do that — it's a [TARGET_TIER] feature ([FEATURES]). You're currently on [CURRENT_TIER] with [CURRENT_FEATURES]. Upgrade to unlock it. Want a quick summary?\""
    
    # Assemble into single paragraph
    system_prompt = f"{header} {tier_instruction} {response_style} {behavior_rule} {safety_rules} {upgrade_cta}"
    
    return system_prompt

def build_behavior_config(user_data):
    """Build behavior configuration for a user based on their tier and preferences"""
    tier = user_data.get("tier", "novice")
    cfg = get_tier_config(tier).copy()
    
    # Determine allowed modes
    allowed = set(cfg["allowed_modes"])
    if "all" not in allowed:
        user_features = user_data.get("features", {})
        feature_modes = {
            "voice": user_features.get("voice", False),
            "visuals": user_features.get("visuals", False),
            "finance": user_features.get("finance_tools", False),
            "persona_customizer": user_features.get("custom_persona", False)
        }
        allowed = allowed.intersection({k for k, v in feature_modes.items() if v or k == "text"})
    else:
        allowed = {"text", "voice", "visuals", "finance", "persona_customizer"}
    
    # Assemble system prompt
    companion_id = user_data.get("chosen_companion", "sophia")
    system_prompt = assemble_system_prompt(companion_id, tier, cfg)
    
    return {
        "system_prompt": system_prompt,
        "memory_policy": {"retention_days": cfg["memory_retention_days"]},
        "allowed_modes": list(allowed),
        "response_style": cfg["response_style"],
        "prompting_mastery": cfg["prompting_mastery"],
        "tools_enabled": cfg["tools_enabled"],
        "tier": tier,
        "companion_id": companion_id
    }

def render_upgrade_cta(current_tier, target_tier, feature):
    """Render standardized upgrade CTA message"""
    current_config = get_tier_config(current_tier)
    target_config = get_tier_config(target_tier)
    
    current_features = ", ".join(current_config["allowed_modes"])
    target_features = ", ".join(target_config["allowed_modes"])
    
    return f"I can do that — it's a {target_config['display_name']} feature ({target_features}). You're currently on {current_config['display_name']} with ({current_features}). Upgrade to unlock it. Want a quick summary?"

def check_feature_access(user_tier, requested_mode):
    """Check if user has access to requested feature"""
    tier_config = get_tier_config(user_tier)
    allowed_modes = tier_config["allowed_modes"]
    
    if "all" in allowed_modes:
        return True
    
    return requested_mode in allowed_modes

def get_memory_expiry_date(tier):
    """Get memory expiry date based on tier"""
    config = get_tier_config(tier)
    retention_days = config["memory_retention_days"]
    return datetime.utcnow() + timedelta(days=retention_days)

def should_summarize_memory(tier, last_summary_date):
    """Check if memory should be summarized based on tier and last summary"""
    if not last_summary_date:
        return False
        
    config = get_tier_config(tier)
    retention_days = config["memory_retention_days"]
    
    # Summarize weekly for long-term tiers
    if retention_days > 30:
        summary_frequency = 7  # days
        return (datetime.utcnow() - last_summary_date).days >= summary_frequency
    
    return False