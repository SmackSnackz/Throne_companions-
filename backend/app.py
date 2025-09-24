from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json
import os
import stripe
from datetime import datetime, timedelta
from typing import Optional, Dict

app = FastAPI()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")

stripe.api_key = STRIPE_SECRET_KEY

# Load companions
with open("companions.json", "r") as f:
    companions_data = json.load(f)
    COMPANIONS = {comp["id"]: comp for comp in companions_data}

# In-memory storage (replace with database in production)
users_db = {}
chat_memory = {}

# Pydantic models
class ChatRequest(BaseModel):
    companion_id: str
    message: str
    user_id: Optional[str] = "demo_user"

class CheckoutRequest(BaseModel):
    tier: str

def get_tier_limits(tier: str) -> Dict:
    """Define limits for each tier"""
    limits = {
        "novice": {
            "max_messages": 20,
            "memory_hours": 24,
            "companions": ["aurora"],
            "features": ["basic"]
        },
        "apprentice": {
            "max_messages": -1,  # Unlimited
            "memory_hours": 168,  # 7 days
            "companions": ["aurora", "sophia", "vanessa", "cassian", "lysander"],
            "features": ["voice", "rituals"]
        },
        "regent": {
            "max_messages": -1,
            "memory_hours": -1,  # Permanent
            "companions": ["aurora", "sophia", "vanessa", "cassian", "lysander"],
            "features": ["all_companions", "advanced"]
        },
        "sovereign": {
            "max_messages": -1,
            "memory_hours": -1,
            "companions": ["aurora", "sophia", "vanessa", "cassian", "lysander"],
            "features": ["custom", "transcendence"]
        }
    }
    return limits.get(tier, limits["novice"])

def store_message(user_id: str, companion_id: str, role: str, content: str):
    """Store message in MCV memory system"""
    if user_id not in chat_memory:
        chat_memory[user_id] = {}
    if companion_id not in chat_memory[user_id]:
        chat_memory[user_id][companion_id] = []
    
    chat_memory[user_id][companion_id].append({
        "role": role,
        "content": content,
        "timestamp": datetime.utcnow()
    })

@app.get("/")
def root():
    return {"status": "Throne Companions API", "version": "1.0"}

@app.get("/companions")
def get_companions():
    """Return all available companions"""
    return list(companions_data)

@app.post("/chat")
async def chat(request: ChatRequest):
    """Chat with a companion"""
    user_id = request.user_id
    
    # Initialize user if not exists
    if user_id not in users_db:
        users_db[user_id] = {
            "tier": "novice",
            "message_count": 0,
            "created_at": datetime.utcnow()
        }
    
    user = users_db[user_id]
    limits = get_tier_limits(user["tier"])
    
    # Check if companion is available for user's tier
    if request.companion_id not in limits["companions"]:
        raise HTTPException(
            status_code=403, 
            detail=f"Companion {request.companion_id} not available for {user['tier']} tier. Please upgrade."
        )
    
    # Check message limits for novice tier
    if limits["max_messages"] > 0 and user["message_count"] >= limits["max_messages"]:
        raise HTTPException(
            status_code=429,
            detail="Message limit reached. Please upgrade to continue chatting."
        )
    
    # Store user message
    store_message(user_id, request.companion_id, "user", request.message)
    
    # Generate companion response
    companion = COMPANIONS[request.companion_id]
    
    # Simple response generation (replace with OpenAI API when ready)
    if not OPENAI_API_KEY:
        reply = f"Hello! I'm {companion['name']}. {companion['bio']} You said: '{request.message}'. This is a demo response - configure OpenAI API for full functionality."
    else:
        # TODO: Add OpenAI API integration here
        reply = f"[{companion['name']}]: I understand your message about '{request.message}'. Full AI integration coming soon!"
    
    # Store companion response
    store_message(user_id, request.companion_id, "assistant", reply)
    
    # Increment message count for novice users
    if user["tier"] == "novice":
        users_db[user_id]["message_count"] += 1
    
    return {"reply": reply, "companion": companion["name"]}

@app.post("/stripe/create-checkout-session")
async def create_checkout(request: CheckoutRequest):
    """Create Stripe checkout session"""
    if not STRIPE_SECRET_KEY:
        raise HTTPException(status_code=500, detail="Stripe not configured")
    
    # Stripe price IDs (you'll need to create these in Stripe dashboard)
    prices = {
        "apprentice": "price_apprentice_replace_with_real_id",
        "regent": "price_regent_replace_with_real_id", 
        "sovereign": "price_sovereign_replace_with_real_id"
    }
    
    if request.tier not in prices:
        raise HTTPException(status_code=400, detail="Invalid tier")
    
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price': prices[request.tier],
                'quantity': 1,
            }],
            mode='subscription',
            success_url=f"{FRONTEND_URL}/post-checkout?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{FRONTEND_URL}/pricing",
            metadata={'tier': request.tier}
        )
        return {"url": session.url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stripe/confirm")
async def confirm_payment(session_id: str):
    """Confirm Stripe payment and upgrade user"""
    if not STRIPE_SECRET_KEY:
        raise HTTPException(status_code=500, detail="Stripe not configured")
    
    try:
        session = stripe.checkout.Session.retrieve(session_id)
        if session.payment_status == 'paid':
            tier = session.metadata.get('tier')
            
            # Update user tier (simplified - in production get user from JWT)
            user_id = "demo_user"
            if user_id in users_db:
                users_db[user_id]["tier"] = tier
                users_db[user_id]["subscription_id"] = session.subscription
            
            return {"status": "confirmed", "tier": tier}
        else:
            raise HTTPException(status_code=400, detail="Payment not completed")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/user/status")
async def get_user_status(user_id: str = "demo_user"):
    """Get user's current tier and limits"""
    if user_id not in users_db:
        return {
            "tier": "novice",
            "message_count": 0,
            "limits": get_tier_limits("novice")
        }
    
    user = users_db[user_id]
    limits = get_tier_limits(user["tier"])
    
    return {
        "tier": user["tier"],
        "message_count": user["message_count"],
        "limits": limits,
        "remaining_messages": limits["max_messages"] - user["message_count"] if limits["max_messages"] > 0 else -1
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
