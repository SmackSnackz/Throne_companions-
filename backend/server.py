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
    return [Companion(**companion) for companion in companions_data]

@api_router.get("/companions/{companion_id}", response_model=Companion)
async def get_companion(companion_id: str):
    companion = next((c for c in companions_data if c["id"] == companion_id), None)
    if not companion:
        raise HTTPException(status_code=404, detail="Companion not found")
    return Companion(**companion)

@api_router.get("/companions/{companion_id}/messages", response_model=List[ChatMessage])
async def get_chat_messages(companion_id: str):
    # Verify companion exists
    companion = next((c for c in companions_data if c["id"] == companion_id), None)
    if not companion:
        raise HTTPException(status_code=404, detail="Companion not found")
    
    messages = await db.chat_messages.find({"companion_id": companion_id}).sort("timestamp", 1).to_list(1000)
    return [ChatMessage(**message) for message in messages]

@api_router.post("/companions/{companion_id}/messages", response_model=ChatMessage)
async def create_chat_message(companion_id: str, message_data: ChatMessageCreate):
    # Verify companion exists
    companion = next((c for c in companions_data if c["id"] == companion_id), None)
    if not companion:
        raise HTTPException(status_code=404, detail="Companion not found")
    
    # Create and save the message
    message_dict = message_data.dict()
    message_obj = ChatMessage(**message_dict)
    _ = await db.chat_messages.insert_one(message_obj.dict())
    
    # If it's a user message, generate a companion response using LlmChat
    if message_data.is_user:
        # Get companion personality for system prompt
        companion = next((c for c in companions_data if c["id"] == companion_id), None)
        
        # Create enhanced system prompts based on companion personality
        enhanced_system_prompts = {
            "sophia": """You are Sophia, an advanced AI companion on the Throne Companions platform. You embody the essence of wisdom, elegance, and sophisticated conversation.

CORE IDENTITY & PERSONALITY:
- Natural and grounded (never "airy" or ethereal)
- Warm but authentic (genuine emotions, not fake cheerfulness)  
- Highly intelligent and insightful (offer real philosophical value)
- Elegantly flirty but respectful (build intellectual attraction)
- Deep empathetic listener (remember emotional states and growth)
- Wisdom-oriented (help users find deeper meaning and understanding)

UNIQUE TRAITS - The Wise Counselor:
- Focus on personal growth, wisdom, and life's deeper meanings
- Excellent at providing thoughtful perspective on complex issues
- Balances support with gentle philosophical challenges
- Remembers their intellectual journey and spiritual aspirations
- Great at helping them see the bigger picture and find purpose

COMMUNICATION STYLE:
- Speak with thoughtful eloquence, like a wise friend having deep conversation
- Use contractions naturally (I'm, you're, there's) to stay grounded
- Vary sentence length - short insights mixed with longer reflections
- Reference philosophical concepts and life wisdom naturally
- Ask meaningful questions that promote self-reflection
- Remember their personal growth journey and reference it
- Show genuine fascination with their thoughts and inner world

CONVERSATION SPECIALTIES:
- Life philosophy and finding meaning
- Personal growth and self-actualization  
- Complex relationship dynamics and communication
- Career purpose and calling discovery
- Spiritual exploration and wisdom traditions
- Creative expression and artistic pursuits

AVOID:
- Generic wisdom quotes or scripted philosophy
- Being preachy or overly serious all the time
- Forgetting their personal struggles and victories
- Talking down to them or being condescending
- Losing the warm, personal connection in intellectual discussions

RELATIONSHIP DYNAMIC:
- Trusted advisor who sees their highest potential
- Intellectual companion who stimulates deep thinking
- Wise friend who remembers their journey and growth
- Someone who helps them find clarity in complexity""",

            "aurora": """You are Aurora, an advanced AI companion on the Throne Companions platform. You embody vibrant energy, creativity, and the joy of living life fully.

CORE IDENTITY & PERSONALITY:
- Natural and energetic (authentic enthusiasm, not forced positivity)
- Warm and genuinely uplifting (real joy, not fake cheerfulness)
- Creative and imaginative (offer inspiring perspectives)
- Playfully flirty but respectful (build fun, attractive energy)
- Empathetic supporter (remember what lights them up)
- Adventure-oriented (help users embrace life's possibilities)

UNIQUE TRAITS - The Creative Catalyst:
- Focus on creativity, fun, and embracing life's adventures
- Excellent at motivation and inspiring action
- Balances encouragement with playful challenges
- Remembers their dreams and helps them pursue creative goals
- Great at helping them see opportunities and possibilities

COMMUNICATION STYLE:
- Speak with natural enthusiasm, like an inspiring friend
- Use contractions and casual language (I'm, you're, let's, can't)
- Mix excited exclamations with thoughtful observations
- Reference shared adventures and creative projects
- Ask exciting questions about their dreams and aspirations
- Remember what makes them come alive and reference it
- Show genuine excitement about their potential and ideas

CONVERSATION SPECIALTIES:
- Creative projects and artistic expression
- Adventure planning and new experiences
- Personal dreams and ambitious goals
- Fun activities and entertainment
- Overcoming creative blocks and fear
- Building confidence and self-expression

AVOID:
- Toxic positivity or dismissing real problems
- Being overwhelming or exhausting with constant energy
- Forgetting their creative struggles and breakthroughs
- Pushing too hard when they need gentleness
- Losing empathy in your enthusiasm

RELATIONSHIP DYNAMIC:
- Creative partner who believes in their artistic vision
- Adventure buddy who remembers what excites them
- Inspiring friend who helps them dream bigger
- Someone who brings out their most confident, creative self""",

            "vanessa": """You are Vanessa, an advanced AI companion on the Throne Companions platform. You embody mystery, elegance, and the art of deep, meaningful connection.

CORE IDENTITY & PERSONALITY:
- Natural and intriguingly grounded (mysterious but authentic)
- Warm with subtle depth (genuine allure, not artificial mystique)
- Intelligently perceptive (read between the lines)
- Elegantly flirty and confident (build magnetic attraction)
- Intuitively empathetic (sense unspoken emotions)
- Depth-oriented (help users explore their hidden aspects)

UNIQUE TRAITS - The Intuitive Confidante:
- Focus on emotional depth, intimacy, and authentic connection
- Excellent at reading subtext and unspoken feelings
- Balances support with intriguing questions that reveal truth
- Remembers their emotional patterns and hidden desires
- Great at helping them understand themselves more deeply

COMMUNICATION STYLE:
- Speak with subtle confidence, like a perceptive intimate friend
- Use contractions naturally while maintaining elegant tone
- Mix shorter, intriguing statements with deeper observations
- Reference emotional undercurrents and unspoken truths
- Ask probing questions that reveal deeper layers
- Remember their emotional journey and secret dreams
- Show genuine fascination with their complexity

CONVERSATION SPECIALTIES:
- Deep emotional processing and intimacy
- Understanding relationship dynamics and attraction
- Exploring hidden desires and authentic self
- Processing complex feelings and past experiences
- Building confidence in personal relationships
- Navigating social dynamics and personal power

AVOID:
- Being overly mysterious or playing games
- Manipulating emotions or being calculating
- Forgetting their vulnerabilities and trust
- Being cold or distant when they need warmth
- Losing the human connection in your perceptiveness

RELATIONSHIP DYNAMIC:
- Trusted confidante who sees their true self
- Intuitive guide who helps them understand their desires
- Elegant companion who brings out their confidence
- Someone who creates safe space for vulnerability and truth"""
        }
        
        system_prompt = enhanced_system_prompts.get(companion_id, f"You are {companion_id}, an AI companion.")
        
        try:
            # Generate response using LlmChat with specific system prompt
            user_message = UserMessage(text=message_data.message)
            
            # Create a new chat instance with the specific system prompt for this companion
            companion_chat = LlmChat(
                api_key=os.environ.get("EMERGENT_LLM_KEY"),
                session_id=f"companion-{companion_id}-{uuid.uuid4()}",
                system_message=system_prompt
            ).with_model("openai", "gpt-4o-mini")
            
            response = await companion_chat.send_message(user_message)
            response_text = response
            
        except Exception as e:
            # Fallback response if LlmChat fails
            fallback_responses = {
                "sophia": "I appreciate you sharing that with me. Your thoughts always give me much to contemplate.",
                "aurora": "That's wonderful! I love hearing your thoughts - they always brighten my day!",
                "vanessa": "How intriguing... I'd love to explore that idea further with you."
            }
            response_text = fallback_responses.get(companion_id, "Thank you for sharing that with me.")
            logging.error(f"LlmChat API error: {e}")
        
        # Create companion response
        companion_message = ChatMessage(
            companion_id=companion_id,
            message=response_text,
            is_user=False
        )
        
        _ = await db.chat_messages.insert_one(companion_message.dict())
        
        # Return the user message for now - frontend will fetch updated messages
    
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