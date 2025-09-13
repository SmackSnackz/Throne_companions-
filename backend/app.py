import os, time, json, jwt
from typing import Optional
from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import stripe
from openai import OpenAI

# ---- App & CORS ----
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---- Env ----
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", "")
JWT_SECRET = os.getenv("JWT_SECRET", "change-me")
FRONTEND_URL = os.getenv("FRONTEND_URL", "https://example.com")

# OpenAI client (reads key from env). We'll also check key at call time.
client = OpenAI()

# Stripe
stripe.api_key = STRIPE_SECRET_KEY

# ---- Companions ----
COMPANIONS = {}
try:
    with open(os.path.join(os.path.dirname(__file__), "companions.json"), "r", encoding="utf-8") as f:
        COMPANIONS = {c["id"]: c for c in json.load(f)}
except Exception:
    COMPANIONS = {
        "sophia": {"id": "sophia", "name": "Sophia", "bio": "Poetic mystic.", "system": "You are Sophia: poetic and wise."},
        "vanessa": {"id": "vanessa", "name": "Vanessa", "bio": "Bold and playful.", "system": "You are Vanessa: confident and playful."},
        "aurora": {"id": "aurora", "name": "Aurora", "bio": "Futuristic strategist.", "system": "You are Aurora: precise and visionary."},
    }

# ---- Models ----
class ChatIn(BaseModel):
    companion_id: str
    message: str

# ---- Health & Basics ----
@app.get("/")
def root():
    return {"ok": True, "service": "throne-backend"}

@app.get("/healthz")
def healthz():
    return {"status": "ok"}

@app.get("/companions")
def companions():
    return [{"id": c["id"], "name": c["name"], "bio": c["bio"]} for c in COMPANIONS.values()]

# ---- Chat ----
@app.post("/chat")
def chat(data: ChatIn, request: Request):
    if not OPENAI_API_KEY:
        raise HTTPException(500, "OPENAI_API_KEY is not set on the server.")

    comp = COMPANIONS.get(data.companion_id)
    if not comp:
        raise HTTPException(404, "Companion not found.")

    messages = [
        {"role": "system", "content": comp["system"]},
        {"role": "user", "content": data.message}
    ]
    try:
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            max_tokens=300
        )
        reply = completion.choices[0].message.content
        return {"reply": reply, "companion": comp["id"]}
    except Exception as e:
        raise HTTPException(500, f"LLM error: {e}")

# ---- Stripe ----
@app.post("/stripe/create-checkout-session")
def create_checkout_session(tier: str):
    if not STRIPE_SECRET_KEY:
        raise HTTPException(500, "STRIPE_SECRET_KEY is not set on the server.")
    price_map = {
        "friend": os.getenv("STRIPE_PRICE_FRIEND", ""),
        "lover": os.getenv("STRIPE_PRICE_LOVER", ""),
        "spouse": os.getenv("STRIPE_PRICE_SPOUSE", "")
    }
    price_id = price_map.get((tier or "").lower())
    if not price_id:
        raise HTTPException(400, "Invalid tier.")
    try:
        session = stripe.checkout.Session.create(
            mode="subscription",
            line_items=[{"price": price_id, "quantity": 1}],
            success_url=f"{FRONTEND_URL}/post-checkout?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{FRONTEND_URL}/pricing",
            billing_address_collection="auto",
        )
        return {"url": session.url}
    except Exception as e:
        raise HTTPException(500, f"Stripe error: {e}")

@app.get("/stripe/confirm")
def stripe_confirm(session_id: str, response: Response):
    if not STRIPE_SECRET_KEY:
        raise HTTPException(500, "STRIPE_SECRET_KEY is not set on the server.")
    if not session_id:
        raise HTTPException(400, "Missing session_id.")
    try:
        session = stripe.checkout.Session.retrieve(session_id)
        customer_id = session.get("customer")
        if not customer_id:
            raise HTTPException(400, "No customer on session.")
        token = jwt.encode({"customer_id": customer_id}, JWT_SECRET, algorithm="HS256")
        response.set_cookie("tc_auth", token, httponly=True, samesite="lax")
        return {"ok": True}
    except Exception as e:
        raise HTTPException(500, f"Stripe confirm error: {e}")
