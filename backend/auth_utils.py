import os
import time
import jwt
from typing import Dict, Set, Optional
import logging

# Environment variables
JWT_SECRET = os.getenv("JWT_SECRET", "throne_companions_secret_key_2024")
ADMIN_EMAILS = set(e.strip() for e in os.getenv("ADMIN_EMAILS", "admin@thronecompanions.com").split(","))
FREE_LIMIT = int(os.getenv("FREE_TIER_MESSAGE_LIMIT", "20"))

# Redis setup with fallback to in-memory
try:
    import redis
    redis_client = redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379"))
    # Test connection
    redis_client.ping()
    use_redis = True
    logging.info("Redis connected successfully")
except Exception as e:
    logging.warning(f"Redis connection failed: {e}. Using in-memory storage.")
    redis_client = None
    use_redis = False
    # Fallback in-memory store (not persistent across process restarts)
    inmem_counts = {}

def incr_count(session_key: str) -> int:
    """Increment message count for session"""
    if use_redis:
        return redis_client.incr(session_key)
    else:
        global inmem_counts
        v = inmem_counts.get(session_key, 0) + 1
        inmem_counts[session_key] = v
        return v

def get_count(session_key: str) -> int:
    """Get current message count for session"""
    if use_redis:
        v = redis_client.get(session_key)
        return int(v) if v else 0
    else:
        return inmem_counts.get(session_key, 0)

def reset_count(session_key: str) -> None:
    """Reset message count for session"""
    if use_redis:
        redis_client.delete(session_key)
    else:
        global inmem_counts
        inmem_counts.pop(session_key, None)

def set_expiry(session_key: str, ttl_seconds: int = 3600) -> None:
    """Set TTL for session counter (1 hour default)"""
    if use_redis:
        redis_client.expire(session_key, ttl_seconds)

def decode_jwt(auth_header: Optional[str]) -> Dict:
    """Decode JWT token from Authorization header"""
    if not auth_header:
        return {}
    
    try:
        # Handle "Bearer TOKEN" format
        token = auth_header.split(" ")[1] if " " in auth_header else auth_header
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        return payload
    except Exception as e:
        logging.warning(f"JWT decode failed: {e}")
        return {}

def is_admin_user(payload: Dict) -> bool:
    """Check if user has admin privileges"""
    email = payload.get("email")
    role = payload.get("role", "user")
    
    # Admin if role is explicitly admin OR email is in admin list
    return (role == "admin") or (email in ADMIN_EMAILS)

def generate_session_key(session_id: str) -> str:
    """Generate Redis/storage key for session message count"""
    return f"msgcount:{session_id}"

def create_jwt_token(email: str, role: str = "user") -> str:
    """Create JWT token for testing purposes"""
    payload = {
        "email": email,
        "role": role,
        "exp": int(time.time()) + (24 * 3600),  # 24 hours
        "iat": int(time.time())
    }
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")

# Companion-specific upgrade messages
COMPANION_UPGRADE_MESSAGES = {
    "aurora": "We've only just opened the candlelight; to keep building clarity together, unlock the next Scroll. ✨",
    "vanessa": "This is where the real work starts — unlock the next tier if you're serious. 💫", 
    "sophia": "Our thread pauses here. Continue the inquiry with a Sovereign subscription. 🔮"
}

def get_upgrade_message(companion_id: str) -> str:
    """Get companion-specific upgrade CTA message"""
    return COMPANION_UPGRADE_MESSAGES.get(
        companion_id, 
        "I loved our time together — to continue our deeper journey, unlock the next scroll.\n\nUpgrade here: /tiers"
    )