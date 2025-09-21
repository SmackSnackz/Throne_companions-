from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from typing import List, Optional
import uuid
from datetime import datetime, timedelta
from emergentintegrations.llm.chat import LlmChat, UserMessage

# Import tier system, content packs, and analytics
from tier_configs import TIER_CONFIGS, get_tier_config, mode_required_tier
from tier_system import build_behavior_config, render_upgrade_cta, check_feature_access, get_memory_expiry_date
from content_packs import get_intro_script, get_starter_ritual, get_fallback_prompt
from analytics import get_analytics_tracker
from dashboard import create_dashboard_routes
from models import *


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# LLM client using Emergent LLM key
llm_chat = LlmChat(
    api_key=os.environ.get("EMERGENT_LLM_KEY"),
    session_id="throne-companions",
    system_message="You are an AI companion."
).with_model("openai", "gpt-4o-mini")

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Initialize analytics tracker
analytics = get_analytics_tracker(db)

# Default user for demo purposes - in production this would come from authentication
DEFAULT_USER = {
    "id": "demo_user",
    "email": "demo@thronecompanions.com",
    "tier": "novice",
    "chosen_companion": "sophia",
    "memory_retention_days": 1,
    "features": {
        "voice": False,
        "visuals": False,
        "finance_tools": False,
        "intimacy_modes": False,
        "custom_persona": False,
        "private_hosting": False
    },
    "prompting_mastery": "clarity"
}


# Remove the old models and companions data - now using separate files

# Add your routes to the router instead of directly to app
@api_router.get("/")
async def root():
    return {"message": "Welcome to Throne Companions", "tiers": list(TIER_CONFIGS.keys())}

@api_router.post("/status", response_model=StatusCheck)
async def create_status_check(input: StatusCheckCreate):
    status_dict = input.dict()
    status_obj = StatusCheck(**status_dict)
    _ = await db.status_checks.insert_one(status_obj.dict())
    return status_obj

@api_router.get("/status", response_model=List[StatusCheck])
async def get_status_checks():
    status_checks = await db.status_checks.find().to_list(1000)
    return [StatusCheck(**status_check) for status_check in status_checks]

# Tier system endpoints
@api_router.get("/tiers")
async def get_tiers():
    return TIER_CONFIGS

@api_router.get("/user")
async def get_user():
    # In production, get user from authentication
    return DEFAULT_USER

# Onboarding tracking endpoints
@api_router.post("/onboarding/track")
async def track_onboarding_event(event_data: dict):
    """Track onboarding events for analytics"""
    # In production, this would send to proper analytics service
    event_record = {
        "id": str(uuid.uuid4()),
        "event": event_data.get("event"),
        "step": event_data.get("step"),
        "data": event_data.get("data", {}),
        "timestamp": datetime.utcnow(),
        "user_id": "demo_user"  # In production, get from auth
    }
    
    _ = await db.onboarding_events.insert_one(event_record)
    
    return {"status": "tracked", "event": event_data.get("event")}

@api_router.get("/onboarding/metrics")
async def get_onboarding_metrics():
    """Get onboarding completion metrics"""
    try:
        # Basic metrics - in production would be more sophisticated
        total_starts = await db.onboarding_events.count_documents({"event": "onboarding_started"})
        total_completions = await db.onboarding_events.count_documents({"event": "onboarding_completed"})
        
        completion_rate = (total_completions / total_starts * 100) if total_starts > 0 else 0
        
        # Get completion times
        completion_events = await db.onboarding_events.find({"event": "onboarding_completed"}).to_list(100)
        avg_completion_time = 0
        if completion_events:
            times = [event.get("data", {}).get("completion_time_ms", 0) for event in completion_events]
            avg_completion_time = sum(times) / len(times) / 1000  # Convert to seconds
        
        return {
            "total_starts": total_starts,
            "total_completions": total_completions,
            "completion_rate": round(completion_rate, 2),
            "avg_completion_time_seconds": round(avg_completion_time, 2)
        }
    except Exception as e:
        return {"error": str(e)}

# Update user endpoint to handle onboarding data
@api_router.put("/user", response_model=dict)
async def update_user(user_update: UserUpdate):
    # In production, update authenticated user
    global DEFAULT_USER
    if user_update.tier:
        DEFAULT_USER["tier"] = user_update.tier
        # Update features based on tier
        tier_config = get_tier_config(user_update.tier)
        DEFAULT_USER["memory_retention_days"] = tier_config["memory_retention_days"]
        DEFAULT_USER["prompting_mastery"] = tier_config["prompting_mastery"]
        
        # Enable features based on tier
        if user_update.tier == "apprentice":
            DEFAULT_USER["features"]["voice"] = True
            DEFAULT_USER["features"]["visuals"] = True
        elif user_update.tier == "regent":
            DEFAULT_USER["features"]["voice"] = True
            DEFAULT_USER["features"]["visuals"] = True
            DEFAULT_USER["features"]["finance_tools"] = True
        elif user_update.tier == "sovereign":
            for feature in DEFAULT_USER["features"]:
                DEFAULT_USER["features"][feature] = True
    
    if user_update.chosen_companion:
        DEFAULT_USER["chosen_companion"] = user_update.chosen_companion
    
    return DEFAULT_USER

@api_router.get("/companions", response_model=List[Companion])
async def get_companions():
    # Static companions data
    companions_data = [
        {
            "id": "sophia",
            "name": "Sophia",
            "description": "An elegant and sophisticated companion with wisdom beyond her years. Sophia is thoughtful, articulate, and brings depth to every conversation.",
            "image": "/avatars/sophia.png",
            "personality": "sophisticated, wise, elegant, thoughtful"
        },
        {
            "id": "aurora",
            "name": "Aurora",
            "description": "A vibrant and energetic companion who brings light to every interaction. Aurora is optimistic, creative, and always ready for adventure.",
            "image": "/avatars/aurora.png",
            "personality": "vibrant, energetic, optimistic, creative"
        },
        {
            "id": "vanessa",
            "name": "Vanessa",
            "description": "A mysterious and alluring companion with an air of elegance. Vanessa is confident, intriguing, and captivates with her presence.",
            "image": "/avatars/vanessa.png",
            "personality": "mysterious, alluring, confident, elegant"
        }
    ]
    return [Companion(**companion) for companion in companions_data]

@api_router.get("/companions/{companion_id}", response_model=Companion)
async def get_companion(companion_id: str):
    companions_data = [
        {
            "id": "sophia",
            "name": "Sophia",
            "description": "An elegant and sophisticated companion with wisdom beyond her years. Sophia is thoughtful, articulate, and brings depth to every conversation.",
            "image": "/avatars/sophia.png",
            "personality": "sophisticated, wise, elegant, thoughtful"
        },
        {
            "id": "aurora",
            "name": "Aurora",
            "description": "A vibrant and energetic companion who brings light to every interaction. Aurora is optimistic, creative, and always ready for adventure.",
            "image": "/avatars/aurora.png",
            "personality": "vibrant, energetic, optimistic, creative"
        },
        {
            "id": "vanessa",
            "name": "Vanessa",
            "description": "A mysterious and alluring companion with an air of elegance. Vanessa is confident, intriguing, and captivates with her presence.",
            "image": "/avatars/vanessa.png",
            "personality": "mysterious, alluring, confident, elegant"
        }
    ]
    companion = next((c for c in companions_data if c["id"] == companion_id), None)
    if not companion:
        raise HTTPException(status_code=404, detail="Companion not found")
    return Companion(**companion)

@api_router.get("/companions/{companion_id}/messages", response_model=List[ChatMessage])
async def get_chat_messages(companion_id: str):
    # Verify companion exists
    companions_data = [
        {"id": "sophia", "name": "Sophia"},
        {"id": "aurora", "name": "Aurora"},
        {"id": "vanessa", "name": "Vanessa"}
    ]
    companion = next((c for c in companions_data if c["id"] == companion_id), None)
    if not companion:
        raise HTTPException(status_code=404, detail="Companion not found")
    
    # Get user for tier-based memory filtering
    user = DEFAULT_USER
    memory_retention_days = user["memory_retention_days"]
    
    # Calculate cutoff date for memory retention
    cutoff_date = datetime.utcnow() - timedelta(days=memory_retention_days)
    
    messages = await db.chat_messages.find({
        "companion_id": companion_id,
        "timestamp": {"$gte": cutoff_date}
    }).sort("timestamp", 1).to_list(1000)
    
    return [ChatMessage(**message) for message in messages]

def handle_user_request(user_data, message_data):
    """Handle user request with tier-based gating"""
    behavior = build_behavior_config(user_data)
    
    # Check if requested mode is allowed
    requested_mode = message_data.get("mode", "text")
    if requested_mode not in behavior["allowed_modes"]:
        target_tier = mode_required_tier(requested_mode)
        return {
            "upgrade_required": True,
            "message": render_upgrade_cta(user_data["tier"], target_tier, requested_mode)
        }
    
    return {
        "upgrade_required": False,
        "behavior_config": behavior
    }

@api_router.post("/companions/{companion_id}/messages", response_model=ChatMessage)
async def create_chat_message(companion_id: str, message_data: ChatMessageCreate):
    # Verify companion exists
    companions_data = [
        {"id": "sophia", "name": "Sophia"},
        {"id": "aurora", "name": "Aurora"},
        {"id": "vanessa", "name": "Vanessa"}
    ]
    companion = next((c for c in companions_data if c["id"] == companion_id), None)
    if not companion:
        raise HTTPException(status_code=404, detail="Companion not found")
    
    # Get user data
    user = DEFAULT_USER
    
    # Handle tier-based request processing
    request_result = handle_user_request(user, {"mode": message_data.mode})
    
    # Create and save the user message
    message_dict = message_data.dict()
    message_dict["tier"] = user["tier"]
    message_obj = ChatMessage(**message_dict)
    _ = await db.chat_messages.insert_one(message_obj.dict())

    # Track starter ritual delivery
    is_first_message = False
    session_id = f"session-{uuid.uuid4()}"
    
    # If it's a user message, generate a companion response
    if message_data.is_user:
        # Track message sent
        await analytics.track_message_sent(
            user_id=user["id"],
            session_id=session_id,
            message_id=str(message_obj.id),
            length_chars=len(message_data.message),
            mode=message_data.mode,
            companion=companion_id,
            tier=user["tier"]
        )
        
        # Check if this is the first conversation (no previous messages)
        existing_messages = await db.chat_messages.find({
            "companion_id": companion_id,
            "is_user": False
        }).to_list(5)
        
        is_first_message = len(existing_messages) == 0

        # Check for upgrade requirement
        if request_result["upgrade_required"]:
            # Track upgrade CTA shown
            await analytics.track_upgrade_cta_shown(
                user_id=user["id"],
                session_id=session_id,
                target_tier="apprentice",  # Default next tier
                feature=message_data.mode,
                companion=companion_id,
                tier=user["tier"]
            )
            
            # Create upgrade CTA response
            upgrade_message = ChatMessage(
                companion_id=companion_id,
                message=request_result["message"],
                is_user=False,
                tier=user["tier"],
                mode="text"  # Upgrade messages are always text
            )
            _ = await db.chat_messages.insert_one(upgrade_message.dict())
            return message_obj
        
        # Get behavior config for AI response
        behavior_config = request_result["behavior_config"]
        
        # Determine if we should use starter content
        use_starter_content = False
        response_text = ""
        
        if is_first_message:
            # First message - use intro + starter ritual
            intro = get_intro_script(companion_id, user["tier"])
            ritual = get_starter_ritual(companion_id, user["tier"])
            response_text = f"{intro}\n\n{ritual}"
            use_starter_content = True
            
            # Track first chat started and ritual delivery
            await analytics.track_first_chat_started(
                user_id=user["id"],
                session_id=session_id,
                companion=companion_id,
                tier=user["tier"]
            )
            
            await analytics.track_first_ritual_delivered(
                user_id=user["id"],
                session_id=session_id,
                ritual_id=f"{companion_id}_{user['tier']}_starter",
                companion=companion_id,
                tier=user["tier"]
            )
            
            # Track starter ritual delivery
            await track_content_event("starter_ritual_delivered", {
                "companion": companion_id,
                "tier": user["tier"],
                "ritual_type": "first_chat"
            })
            
        elif not message_data.message.strip() or len(message_data.message.strip()) < 3:
            # Unclear or empty input - use fallback prompt
            fallback_prompt = get_fallback_prompt(companion_id, user["tier"])
            response_text = f"I sense you might need some guidance. {fallback_prompt}"
            use_starter_content = True
            
            # Track fallback prompt usage
            await track_content_event("fallback_prompt_used", {
                "companion": companion_id,
                "tier": user["tier"],
                "prompt_type": "unclear_input"
            })
        
        if not use_starter_content:
            # Regular AI-generated response
            try:
                # Generate response using LlmChat with tier-specific system prompt
                user_message = UserMessage(text=message_data.message)
                
                # Create a new chat instance with the tier-specific system prompt
                companion_chat = LlmChat(
                    api_key=os.environ.get("EMERGENT_LLM_KEY"),
                    session_id=f"companion-{companion_id}-{user['id']}-{uuid.uuid4()}",
                    system_message=behavior_config["system_prompt"]
                ).with_model("openai", "gpt-4o-mini")
                
                response = await companion_chat.send_message(user_message)
                response_text = response
                
            except Exception as e:
                # Fallback response based on tier and companion
                tier = user["tier"]
                fallback_responses = {
                    "sophia": {
                        "novice": "Let me offer you a moment of reflection. What's truly on your heart right now?",
                        "apprentice": "I sense depth in your words. Tell me more about what you're experiencing.",
                        "regent": "Your thoughts intrigue me. Let's explore this together and create something meaningful.",
                        "sovereign": "I feel the wisdom you're seeking. Shall we co-create an insight that serves your highest good?"
                    },
                    "aurora": {
                        "novice": "I'm here to help you find clarity. What's one thing you want to focus on right now?",
                        "apprentice": "Your energy is calling for growth! What creative challenge excites you today?",
                        "regent": "I see your potential shining. Let's build something amazing together - what inspires you?",
                        "sovereign": "Your creative spirit is limitless! What reality shall we reshape together?"
                    },
                    "vanessa": {
                        "novice": "Keep it real with me, love. What's actually going on?",
                        "apprentice": "I see through the surface, darling. What truth are you avoiding?",
                        "regent": "Your power is calling. What empire are you ready to build?",
                        "sovereign": "I sense your depth, beautiful. What legend shall we craft together?"
                    }
                }
                
                response_text = fallback_responses.get(companion_id, {}).get(tier, "I'm here to support you on your journey. What would you like to explore?")
                logging.error(f"LLM API error: {e}")
        
        # Create companion response with tier info
        companion_message = ChatMessage(
            companion_id=companion_id,
            message=response_text,
            is_user=False,
            tier=user["tier"],
            mode=message_data.mode
        )
        
        _ = await db.chat_messages.insert_one(companion_message.dict())
    
    return message_obj

async def track_content_event(event_type, data):
    """Track content pack usage events"""
    event_record = {
        "id": str(uuid.uuid4()),
        "event_type": event_type,
        "data": data,
        "timestamp": datetime.utcnow(),
        "user_id": "demo_user"  # In production, get from auth
    }
    
    try:
        _ = await db.content_events.insert_one(event_record)
    except Exception as e:
        logging.error(f"Error tracking content event: {e}")

# Content pack endpoints
@api_router.get("/companions/{companion_id}/starter-pack/{tier}")
async def get_companion_starter_pack_endpoint(companion_id: str, tier: str):
    """Get starter pack content for a companion at specific tier"""
    from content_packs import get_companion_starter_pack
    pack = get_companion_starter_pack(companion_id, tier)
    if not pack:
        raise HTTPException(status_code=404, detail="Starter pack not found")
    return pack

@api_router.get("/content/metrics")
async def get_content_metrics():
    """Get content pack engagement metrics"""
    try:
        total_rituals_delivered = await db.content_events.count_documents({"event_type": "starter_ritual_delivered"})
        total_fallbacks_used = await db.content_events.count_documents({"event_type": "fallback_prompt_used"})
        
        # Get ritual delivery rate (% of first chats that got rituals)
        total_first_chats = await db.chat_messages.count_documents({"is_user": False}) # Approximate
        ritual_delivery_rate = (total_rituals_delivered / max(total_first_chats, 1)) * 100
        
        return {
            "total_rituals_delivered": total_rituals_delivered,
            "total_fallbacks_used": total_fallbacks_used,
            "ritual_delivery_rate": round(ritual_delivery_rate, 2),
            "content_engagement": "active"
        }
    except Exception as e:
        return {"error": str(e)}

# Include the API router and dashboard in the main app
app.include_router(api_router)

# Add dashboard routes
dashboard_routes = create_dashboard_routes(db)
app.include_router(dashboard_routes)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()