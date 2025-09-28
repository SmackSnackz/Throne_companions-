from fastapi import FastAPI, APIRouter, HTTPException, Header
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
import time
from pathlib import Path
from typing import List, Optional
import uuid
from datetime import datetime, timedelta
from emergentintegrations.llm.chat import LlmChat, UserMessage

# Import tier system, content packs, analytics, and auth utils
from tier_configs import TIER_CONFIGS, get_tier_config, mode_required_tier
from tier_system import build_behavior_config, render_upgrade_cta, check_feature_access, get_memory_expiry_date
from content_packs import get_intro_script, get_starter_ritual, get_fallback_prompt
from analytics import get_analytics_tracker
from dashboard import create_dashboard_routes
from auth_utils import (
    decode_jwt, is_admin_user, incr_count, get_count, reset_count, 
    set_expiry, generate_session_key, get_upgrade_message, FREE_LIMIT
)
from solicitation import detect_and_solicit, build_llm_preface
from tier_prompt_manager import tier_prompt_manager
from unified_prompt_system import unified_prompt_system
from tone_anchor_system import tone_anchor_system
from master_prompt_system import master_prompt_system
from memory_system import initialize_memory_system, get_memory_system
from mixpanel_events import initialize_mixpanel_tracker, get_mixpanel_tracker
from temp_admin_override import temp_admin_override
from models import *

from pydantic import BaseModel

# Add request models for API endpoints
class CreateTokenRequest(BaseModel):
    email: str
    role: str = "user"

class ChatRequest(BaseModel):
    companion_id: str
    message: str
    session_id: Optional[str] = None
    solicitation_answers: Optional[dict] = None
    chosen_starter: Optional[str] = None
    session_starter_count: Optional[int] = 0
    deep_dive_requested: Optional[bool] = False
    expansion_requested: Optional[bool] = False
    # Master Prompt System Variables
    user_mode: Optional[str] = "Confidant"
    affection_dial: Optional[int] = 2
    memory_summary: Optional[str] = ""


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

# Initialize Memory System
memory_system = initialize_memory_system(db)

# Initialize Mixpanel Tracker (in mock mode for testing)
mixpanel_tracker = initialize_mixpanel_tracker(db, mock_mode=True)

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

@api_router.post("/chat")
async def chat_endpoint(
    request: ChatRequest,
    authorization: Optional[str] = Header(None)
):
    """
    Chat endpoint with optional solicitation layer and guaranteed fallback
    """
    # 1) Verify companion exists
    companions_data = [
        {"id": "sophia", "name": "Sophia"},
        {"id": "aurora", "name": "Aurora"}, 
        {"id": "vanessa", "name": "Vanessa"}
    ]
    companion = next((c for c in companions_data if c["id"] == request.companion_id), None)
    if not companion:
        raise HTTPException(status_code=404, detail="Companion not found")
    
    # 2) Identify user/role from JWT
    payload = decode_jwt(authorization)
    email = payload.get("email")
    role = payload.get("role", "user")
    is_admin = is_admin_user(payload)
    
    # Get user ID for memory system
    user_id = email or "demo_user"
    
    # 3) Ensure session ID
    session_id = request.session_id or f"session:{email or 'anon'}:{int(time.time())}"
    session_key = generate_session_key(session_id)
    
    # 3.1) MEMORY SYSTEM - Get memory summaries for injection
    user_tier = "sovereign" if is_admin else DEFAULT_USER.get("tier", "novice")
    memory_injection = ""
    try:
        memory_injection = await memory_system.get_memory_summaries_for_injection(user_id, user_tier)
        if memory_injection:
            logging.info(f"Memory injection for user {user_id}: {memory_injection[:100]}...")
    except Exception as e:
        logging.error(f"Memory injection failed: {e}")
        memory_injection = ""
    
    # 4) SESSION START SOLICITATION CHECK - Check if this is a new session without previous messages
    try:
        # Check if this is the first message in the session
        session_message_count = await memory_system.get_session_message_count(user_id, session_id)
        is_new_session = session_message_count == 0
        
        # If new session and no solicitation answers provided, trigger session start solicitation
        if is_new_session and not request.solicitation_answers and not request.chosen_starter:
            session_start_response = {
                "type": "solicitation",
                "tag": "Session Start - How should I support you?",
                "companion_id": request.companion_id,
                "questions": [
                    {"id": "support_style", "text": "How would you like me to support you today?", "options": ["Soft & gentle", "Honest & direct", "Funny & light", "Wise & firm"]},
                    {"id": "conversation_goal", "text": "What kind of conversation are you looking for?", "options": ["Deep emotional support", "Light conversation", "Real advice", "Ask questions & explore"]}
                ],
                "starter_prompts": [
                    "I need emotional support right now",
                    "Give me some real advice about life", 
                    "Let's have something fun and light",
                    "I want to ask you some questions"
                ],
                "tier": user_tier,
                "session_id": session_id
            }
            return session_start_response
    except Exception as e:
        logging.error(f"Session start solicitation failed: {e}")
    
    # 5) UNIFIED PROMPT SYSTEM - Master logic flow (PRESERVES all existing functionality)
    if not request.solicitation_answers and not request.chosen_starter:
        try:
            # Get user tier for analysis
            user_tier = "sovereign" if is_admin else DEFAULT_USER.get("tier", "novice")
            
            # Master analysis: Distress → Solicitation → Normal
            mode_type, response_data = unified_prompt_system.analyze_user_input(
                request.message, 
                user_tier, 
                request.companion_id
            )
            
            # Handle distress mode (highest priority)
            if mode_type == "distress":
                return response_data
            
            # Handle solicitation mode (second priority)  
            elif mode_type == "solicitation":
                return response_data
            
            # Normal mode continues to existing LLM flow below
            
        except Exception as e:
            logging.warning(f"Unified prompt system failed: {e}, proceeding with normal response")
            # Continue to normal response if system fails
    
    # 6) Check message cap for non-admin users
    if not is_admin:
        current_count = get_count(session_key)
        if current_count >= FREE_LIMIT:
            # Track upgrade CTA shown
            try:
                await mixpanel_tracker.track_upgrade_tier_clicked(
                    user_id=user_id,
                    current_tier="novice",
                    target_tier="apprentice",
                    source="chat_limit",
                    session_id=session_id
                )
            except Exception as e:
                logging.error(f"Upgrade CTA tracking failed: {e}")
            
            # Send upgrade CTA
            upgrade_msg = get_upgrade_message(request.companion_id)
            return {
                "reply": upgrade_msg,
                "upgrade": True,
                "used": current_count,
                "limit": FREE_LIMIT,
                "session_id": session_id
            }
    
    # 7) Get user tier (admin gets best tier, others get their actual tier)  
    user_tier = "sovereign" if is_admin else DEFAULT_USER.get("tier", "novice")
    
    # 8) Handle expansion requests for both distress mode and general responses
    is_expansion_request = False
    if (request.expansion_requested or 
        unified_prompt_system.check_expansion_request(request.message) or 
        tone_anchor_system.check_expansion_request(request.message)):
        is_expansion_request = True
    
    # 9) Prepare message (with solicitation context if provided) - EXISTING LOGIC PRESERVED
    final_message = request.message
    if request.solicitation_answers or request.chosen_starter:
        # Build preface based on user clarifications
        try:
            preface = build_llm_preface(
                request.solicitation_answers or {}, 
                request.companion_id,
                request.chosen_starter
            )
            final_message = preface + (request.chosen_starter or request.message)
        except Exception as e:
            logging.warning(f"Failed to build solicitation preface: {e}")
            final_message = request.chosen_starter or request.message
    
    # 10) MASTER PROMPT SYSTEM - Insert Master Prompt as global system prompt (King Sol Specification)
    try:
        # Get user tier for additional context
        user_tier = "sovereign" if is_admin else DEFAULT_USER.get("tier", "novice")
        
        # Build Master Prompt with dynamic variables (UserMode, AffectionDial, MemorySummary)
        additional_context = f"""
User tier: {user_tier}
Memory: {'Unlimited conversation history' if is_admin else 'Limited to current session for novice tier'}

Current session context: This is an active conversation. Stay present and emotionally connected.
"""
        
        # Inject memory summaries if available
        effective_memory_summary = memory_injection or request.memory_summary or ""
        
        # MASTER PROMPT INSERTION (Following Developer Note exactly)
        system_prompt = master_prompt_system.build_complete_system_prompt(
            companion_id=request.companion_id,
            user_mode=request.user_mode or "Confidant",
            affection_dial=request.affection_dial or 2,
            memory_summary=effective_memory_summary,
            additional_context=additional_context
        )
        
        # Use emergentintegrations LLM (EXISTING INTEGRATION PRESERVED)
        user_message = UserMessage(text=final_message)
        companion_chat = LlmChat(
            api_key=os.environ.get("EMERGENT_LLM_KEY"),
            session_id=session_id,
            system_message=system_prompt
        ).with_model("openai", "gpt-4o-mini")
        
        # Get LLM response
        llm_response = await companion_chat.send_message(user_message)
        reply_text = llm_response if llm_response else "I apologize, but I'm having difficulty connecting right now. Please try again."
        
        # ENHANCED: Apply tone anchor grounding filter (ADDITIVE)
        reply_text = tone_anchor_system.apply_grounding_filter(
            reply_text, 
            request.companion_id, 
            is_expansion_request
        )
        
        # Apply unified tier-based response limits (ADDITIVE feature)
        if not request.deep_dive_requested and not is_expansion_request:
            reply_text, was_capped = unified_prompt_system.apply_tier_limits(reply_text, user_tier)
            if was_capped:
                logging.info(f"Response capped for tier: {user_tier}")
        
    except Exception as e:
        logging.error(f"LLM call failed: {e}")
        # Fallback response to guarantee user always gets a response (EXISTING LOGIC PRESERVED)
        reply_text = f"I apologize, but I'm having some technical difficulties right now. Please try again in a moment, or let me know if you'd like me to help you with something specific."
    
    # 11) Increment counter for non-admin users AFTER successful reply
    if not is_admin:
        new_count = incr_count(session_key)
        # Set TTL to 1 hour to expire session counters
        set_expiry(session_key, 3600)
    else:
        new_count = get_count(session_key)
    
    # 12) Save messages to database (existing logic)
    try:
        # Save user message
        user_msg = ChatMessage(
            companion_id=request.companion_id,
            message=request.message,
            is_user=True,
            tier=user_tier,
            mode="text"
        )
        await db.chat_messages.insert_one(user_msg.dict())
        
        # Save companion response  
        companion_msg = ChatMessage(
            companion_id=request.companion_id,
            message=reply_text,
            is_user=False,
            tier=user_tier,
            mode="text"
        )
        await db.chat_messages.insert_one(companion_msg.dict())
        
    except Exception as e:
        logging.error(f"Database save failed: {e}")
    
    # 12.1) MEMORY SYSTEM - Store chat history
    try:
        # Store user message in memory system
        await memory_system.store_chat_message(
            user_id=user_id,
            session_id=session_id,
            message=request.message,
            direction="user",
            role=request.user_mode or "Friend",
            affection_dial=request.affection_dial or 2
        )
        
        # Store companion response in memory system
        await memory_system.store_chat_message(
            user_id=user_id,
            session_id=session_id,
            message=reply_text,
            direction="companion",
            role=request.user_mode or "Friend",
            affection_dial=request.affection_dial or 2
        )
        
        logging.info(f"Stored memory for session {session_id}")
        
    except Exception as e:
        logging.error(f"Memory storage failed: {e}")
    
    # 13.1) MIXPANEL EVENT TRACKING - Track message sent
    try:
        await mixpanel_tracker.track_message_sent(
            user_id=user_id,
            session_id=session_id,
            companion_id=request.companion_id,
            message_length=len(request.message),
            user_tier=user_tier
        )
        
        # Track session started if this is the first message in session
        message_count = await memory_system.get_session_message_count(user_id, session_id)
        if message_count <= 2:  # User message + companion response = 2
            await mixpanel_tracker.track_session_started(
                user_id=user_id,
                session_id=session_id,
                companion_id=request.companion_id,
                user_tier=user_tier
            )
            
        # Track memory system usage if summaries were injected
        if memory_injection:
            summaries_count = len(memory_injection.split(" | ")) if " | " in memory_injection else 1
            await mixpanel_tracker.track_memory_system_usage(
                user_id=user_id,
                session_id=session_id,
                memory_summaries_count=summaries_count,
                user_tier=user_tier
            )
            
    except Exception as e:
        logging.error(f"Mixpanel tracking failed: {e}")
    
    # 13) GUARANTEED RESPONSE - Always return a proper chat response
    return {
        "type": "answer",
        "reply": reply_text,
        "used": new_count,
        "limit": FREE_LIMIT,
        "upgrade": False,
        "session_id": session_id,
        "is_admin": is_admin
    }

@api_router.post("/auth/create-token")
async def create_test_token(request: CreateTokenRequest):
    """Create JWT token for testing (remove in production)"""
    from auth_utils import create_jwt_token
    token = create_jwt_token(request.email, request.role)
    return {"token": token, "email": request.email, "role": request.role}

@api_router.get("/auth/verify")
async def verify_token(authorization: Optional[str] = Header(None)):
    """Verify JWT token and return user info"""
    payload = decode_jwt(authorization)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or missing token")
    
    is_admin = is_admin_user(payload)
    return {
        "email": payload.get("email"),
        "role": payload.get("role", "user"),
        "is_admin": is_admin,
        "exp": payload.get("exp")
    }

@api_router.post("/session/complete")
async def complete_session(
    session_data: dict,
    authorization: Optional[str] = Header(None)
):
    """Complete a session and generate memory summary"""
    try:
        # Identify user from JWT
        payload = decode_jwt(authorization)
        user_id = payload.get("email") or "demo_user"
        session_id = session_data.get("session_id")
        
        if not session_id:
            raise HTTPException(status_code=400, detail="Session ID required")
        
        # Generate and store memory summary
        summary = await memory_system.complete_session_and_summarize(user_id, session_id)
        
        # Track session ended
        try:
            message_count = await memory_system.get_session_message_count(user_id, session_id)
            companion_id = session_data.get("companion_id", "unknown")
            
            await mixpanel_tracker.track_session_ended(
                user_id=user_id,
                session_id=session_id,
                companion_id=companion_id,
                message_count=message_count
            )
        except Exception as e:
            logging.error(f"Session end tracking failed: {e}")
        
        if summary:
            return {
                "status": "completed",
                "session_id": session_id,
                "summary": summary
            }
        else:
            return {
                "status": "completed",
                "session_id": session_id,
                "summary": "No summary generated"
            }
            
    except Exception as e:
        logging.error(f"Session completion failed: {e}")
        raise HTTPException(status_code=500, detail="Session completion failed")

@api_router.post("/events/companion_selected")
async def track_companion_selected(event_data: dict):
    """Track companion selection event"""
    try:
        user_id = event_data.get("user_id", "demo_user")
        companion_id = event_data.get("companion_id")
        companion_name = event_data.get("companion_name")  
        session_id = event_data.get("session_id", f"onboarding_{user_id}")
        
        await mixpanel_tracker.track_companion_selected(
            user_id=user_id,
            companion_id=companion_id,
            companion_name=companion_name,
            session_id=session_id
        )
        
        return {"status": "tracked", "event": "companion_selected"}
        
    except Exception as e:
        logging.error(f"Companion selection tracking failed: {e}")
        raise HTTPException(status_code=500, detail="Event tracking failed")

@api_router.post("/events/tier_selected") 
async def track_tier_selected(event_data: dict):
    """Track tier selection event"""
    try:
        user_id = event_data.get("user_id", "demo_user")
        tier_name = event_data.get("tier_name")
        tier_price = event_data.get("tier_price", "Free")
        session_id = event_data.get("session_id", f"onboarding_{user_id}")
        
        await mixpanel_tracker.track_tier_selected(
            user_id=user_id,
            tier_name=tier_name,
            tier_price=tier_price,
            session_id=session_id
        )
        
        return {"status": "tracked", "event": "tier_selected"}
        
    except Exception as e:
        logging.error(f"Tier selection tracking failed: {e}")
        raise HTTPException(status_code=500, detail="Event tracking failed")

@api_router.post("/events/upgrade_clicked")
async def track_upgrade_clicked(event_data: dict):
    """Track upgrade CTA clicked event"""
    try:
        user_id = event_data.get("user_id", "demo_user")
        current_tier = event_data.get("current_tier", "novice")
        target_tier = event_data.get("target_tier", "apprentice")
        source = event_data.get("source", "tier_page")
        session_id = event_data.get("session_id", f"upgrade_{user_id}")
        
        await mixpanel_tracker.track_upgrade_tier_clicked(
            user_id=user_id,
            current_tier=current_tier,
            target_tier=target_tier,
            source=source,
            session_id=session_id
        )
        
        return {"status": "tracked", "event": "upgrade_tier_clicked"}
        
    except Exception as e:
        logging.error(f"Upgrade click tracking failed: {e}")
        raise HTTPException(status_code=500, detail="Event tracking failed")

@api_router.get("/events/mock")
async def get_mock_events(user_id: Optional[str] = None, event_name: Optional[str] = None):
    """Get mock events for verification (mock mode only)"""
    try:
        events = await mixpanel_tracker.get_mock_events(user_id, event_name)
        return {
            "mock_mode": True,
            "events": events,
            "count": len(events)
        }
    except Exception as e:
        logging.error(f"Failed to get mock events: {e}")
        raise HTTPException(status_code=500, detail="Failed to get events")

@api_router.get("/events/stats")
async def get_event_stats():
    """Get event statistics"""
    try:
        event_counts = await mixpanel_tracker.get_event_counts()
        return {
            "mock_mode": True,
            "event_counts": event_counts,
            "total_events": sum(event_counts.values())
        }
    except Exception as e:
        logging.error(f"Failed to get event stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to get stats")

# TEMPORARY ADMIN OVERRIDE ENDPOINTS - SESSION BASED ONLY
@api_router.post("/admin/activate_sovereign_investigation")
async def activate_sovereign_investigation(
    activation_data: dict,
    authorization: Optional[str] = Header(None)
):
    """Activate Quantum Sovereign Access Level for tier investigation"""
    try:
        # Get user from JWT
        payload = decode_jwt(authorization)
        user_email = payload.get("email")
        
        if not user_email:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        session_id = activation_data.get("session_id")
        if not session_id:
            raise HTTPException(status_code=400, detail="Session ID required")
        
        # Activate override
        success = temp_admin_override.activate_sovereign_investigation(user_email, session_id)
        
        if success:
            return {
                "status": "activated",
                "access_level": "quantum_sovereign",
                "investigator": user_email,
                "session_id": session_id,
                "expires_in_hours": 24,
                "message": "Quantum Sovereign Access Level activated for tier investigation"
            }
        else:
            raise HTTPException(status_code=403, detail="Unauthorized for tier investigation")
            
    except Exception as e:
        logging.error(f"Sovereign investigation activation failed: {e}")
        raise HTTPException(status_code=500, detail="Activation failed")

@api_router.get("/admin/tier_investigation_preview")
async def get_tier_investigation_preview(
    session_id: str,
    authorization: Optional[str] = Header(None)
):
    """Get comprehensive tier preview for investigation (authorized users only)"""
    try:
        # Get user from JWT
        payload = decode_jwt(authorization)
        user_email = payload.get("email")
        
        if not user_email:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        # Get tier preview with override check
        tier_preview = temp_admin_override.get_all_tier_preview(user_email, session_id)
        
        if not tier_preview:
            raise HTTPException(status_code=403, detail="Tier investigation access not active")
        
        return tier_preview
        
    except Exception as e:
        logging.error(f"Tier investigation preview failed: {e}")
        raise HTTPException(status_code=500, detail="Preview failed")

@api_router.get("/admin/effective_tier_config")
async def get_effective_tier_config(
    session_id: str,
    authorization: Optional[str] = Header(None)
):
    """Get effective tier configuration with any overrides applied"""
    try:
        # Get user from JWT
        payload = decode_jwt(authorization)
        user_email = payload.get("email")
        
        if not user_email:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        # Get base tier from user (would normally come from database)
        base_tier = DEFAULT_USER.get("tier", "novice")
        
        # Get effective config with override
        effective_config = temp_admin_override.get_effective_tier_config(
            user_email, session_id, base_tier
        )
        
        return {
            "base_tier": base_tier,
            "effective_config": effective_config,
            "has_override": temp_admin_override.check_tier_override(user_email, session_id) is not None
        }
        
    except Exception as e:
        logging.error(f"Effective tier config failed: {e}")
        raise HTTPException(status_code=500, detail="Config retrieval failed")

@api_router.post("/admin/deactivate_override")
async def deactivate_tier_override(
    deactivation_data: dict,
    authorization: Optional[str] = Header(None)
):
    """Deactivate tier override"""
    try:
        # Get user from JWT
        payload = decode_jwt(authorization)
        user_email = payload.get("email")
        
        if not user_email:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        session_id = deactivation_data.get("session_id")
        if not session_id:
            raise HTTPException(status_code=400, detail="Session ID required")
        
        # Deactivate override
        success = temp_admin_override.deactivate_override(user_email, session_id)
        
        return {
            "status": "deactivated" if success else "not_found",
            "message": "Tier override deactivated" if success else "No active override found"
        }
        
    except Exception as e:
        logging.error(f"Override deactivation failed: {e}")
        raise HTTPException(status_code=500, detail="Deactivation failed")

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
            start_time = datetime.utcnow()
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
                
                # Track successful LLM request
                end_time = datetime.utcnow()
                latency_ms = int((end_time - start_time).total_seconds() * 1000)
                
                await analytics.track_llm_request(
                    user_id=user["id"],
                    session_id=session_id,
                    latency_ms=latency_ms,
                    success=True,
                    companion=companion_id,
                    tier=user["tier"]
                )
                
            except Exception as e:
                # Track failed LLM request
                end_time = datetime.utcnow()
                latency_ms = int((end_time - start_time).total_seconds() * 1000)
                
                await analytics.track_llm_request(
                    user_id=user["id"],
                    session_id=session_id,
                    latency_ms=latency_ms,
                    success=False,
                    error_code=str(type(e).__name__),
                    companion=companion_id,
                    tier=user["tier"]
                )
                
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