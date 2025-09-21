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

# Import tier system
from tier_configs import TIER_CONFIGS, get_tier_config, mode_required_tier
from tier_system import build_behavior_config, render_upgrade_cta, check_feature_access, get_memory_expiry_date
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

@api_router.put("/user", response_model=dict)
async def update_user(user_update: UserUpdate):
    # In production, update authenticated user
    global DEFAULT_USER
    if user_update.tier:
        DEFAULT_USER["tier"] = user_update.tier
        # Update features based on tier
        tier_config = get_tier_config(user_update.tier)
        DEFAULT_USER["memory_retention_days"] = tier_config["memory_retention_days"]
        
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
    
    # If it's a user message, generate a companion response
    if message_data.is_user:
        # Check for upgrade requirement
        if request_result["upgrade_required"]:
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
            # Fallback response based on tier
            tier = user["tier"]
            fallback_responses = {
                "novice": f"I'm here to help briefly. Let me give you one clear action.",
                "apprentice": f"I'm ready to provide you with a detailed exercise and actionable steps.",
                "regent": f"I can offer you comprehensive guidance and track your progress over time.",
                "sovereign": f"I'm prepared for deep co-creation and personalized assistance."
            }
            response_text = fallback_responses.get(tier, "Thank you for sharing that with me.")
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

# Include the router in the main app
app.include_router(api_router)

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