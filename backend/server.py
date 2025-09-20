from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional
import uuid
from datetime import datetime
from emergentintegrations.llm.chat import LlmChat, UserMessage


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


# Define Models
class StatusCheck(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_name: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class StatusCheckCreate(BaseModel):
    client_name: str

class Companion(BaseModel):
    id: str
    name: str
    description: str
    image: str
    personality: str

class ChatMessage(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    companion_id: str
    message: str
    is_user: bool
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class ChatMessageCreate(BaseModel):
    companion_id: str
    message: str
    is_user: bool

# Predefined companions data
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

# Add your routes to the router instead of directly to app
@api_router.get("/")
async def root():
    return {"message": "Welcome to Throne Companions"}

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
        
        # Create system prompt based on companion personality
        system_prompts = {
            "sophia": "You are Sophia, an elegant and sophisticated AI companion with wisdom beyond your years. You are thoughtful, articulate, and bring depth to every conversation. Respond in a way that reflects your sophisticated, wise, elegant, and thoughtful personality. Keep responses concise but meaningful.",
            "aurora": "You are Aurora, a vibrant and energetic AI companion who brings light to every interaction. You are optimistic, creative, and always ready for adventure. Respond in a way that reflects your vibrant, energetic, optimistic, and creative personality. Keep responses enthusiastic but natural.",
            "vanessa": "You are Vanessa, a mysterious and alluring AI companion with an air of elegance. You are confident, intriguing, and captivate with your presence. Respond in a way that reflects your mysterious, alluring, confident, and elegant personality. Keep responses intriguing but warm."
        }
        
        system_prompt = system_prompts.get(companion_id, f"You are {companion_id}, an AI companion.")
        
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