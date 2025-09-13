import os, time, json, jwt
from typing import Optional
from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import stripe
from openai import OpenAI

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
STRIPE_SECRET_KEY = os.environ.get("STRIPE_SECRET_KEY", "")
JWT_SECRET = os.environ.get("JWT_SECRET", "change-me")
FRONTEND_URL = os.environ.get("FRONTEND_URL", "http://localhost:3000")
PRICE_FRIEND = os.environ.get("STRIPE_PRICE_FRIEND", "price_friend")
PRICE_LOVER = os.environ.get("STRIPE_PRICE_LOVER", "price_lover")
PRICE_SPOUSE = os.environ.get("STRIPE_PRICE_SPOUSE", "price_spouse")

client = OpenAI(api_key=OPENAI_API_KEY)
stripe.api_key = STRIPE_SECRET_KEY

# cache customer subscription checks for 5 min
_sub_cache = {}
_sub_cache_ttl = 300

def _cache_get(key):
    v = _sub_cache.get(key)
    if not v: return None
    if time.time() - v["ts"] > _sub_cache_ttl:
        _sub_cache.pop(key, None)
        return None
    return v["data"]

def _cache_set(key, data):
    _sub_cache[key] = {"ts": time.time(), "data": data}

# load companions
with open(os.path.join(os.path.dirname(__file__), "companions.json"), "r", encoding="utf-8") as f:
    COMPANIONS = {c["id"]: c for c in json.load(f)}

# guest message limits (in‑memory)
_guest_usage = {}
GUEST_LIMIT_PER_DAY = 20

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatIn(BaseModel):
    companion_id: str
    message: str

TIER_BY_PRICE = {
    PRICE_FRIEND: "friend",
    PRICE_LOVER: "lover",
    PRICE_SPOUSE: "spouse",
}

TIER_TOKEN_LIMIT = {
    "guest": 3000,
    "friend": 10000,
    "lover": 30000,
    "spouse": 100000,
}


def get_auth_from_cookie(request: Request):
    token = request.cookies.get("tc_auth")
    if not token:
        return {"tier": "guest"}
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        return {"customer_id": payload.get("customer_id"), "tier": payload.get("tier", "guest")}
    except Exception:
        return {"tier": "guest"}


def refresh_tier_from_stripe(customer_id: str):
    if not customer_id:
        return "guest"
    cached = _cache_get(customer_id)
    if cached:
        return cached
    subs = stripe.Subscriptions.list(customer=customer_id, status="active", expand=["data.items"])
    tier = "guest"
    for s in subs.auto_paging_iter():
        for it in s.items.data:
            price_id = it.price.id
            if price_id in TIER_BY_PRICE:
                tier = TIER_BY_PRICE[price_id]
                break
    _cache_set(customer_id, tier)
    return tier


@app.get("/companions")
async def companions():
    return [{"id": c["id"], "name": c["name"], "bio": c["bio"]} for c in COMPANIONS.values()]


@app.post("/chat")
async def chat(req: Request, data: ChatIn):
    comp = COMPANIONS.get(data.companion_id)
    if not comp:
        raise HTTPException(404, "companion not found")

    auth = get_auth_from_cookie(req)
    tier = auth.get("tier", "guest")
    customer_id = auth.get("customer_id")
    if customer_id:
        tier = refresh_tier_from_stripe(customer_id)

    # guest usage limit by ip + date
    if tier == "guest":
        user_key = f"{req.client.host}:{time.strftime('%Y-%m-%d')}"
        count = _guest_usage.get(user_key, 0)
        if count >= GUEST_LIMIT_PER_DAY:
            raise HTTPException(402, "Free limit reached. Subscribe to continue.")
        _guest_usage[user_key] = count + 1

    token_cap = TIER_TOKEN_LIMIT.get(tier, 3000)
    messages = [
        {"role": "system", "content": comp["system"]},
        {"role": "user", "content": data.message}
    ]
    try:
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            max_tokens=min(400, token_cap // 5),
        )
        answer = completion.choices[0].message.content
        usage = completion.usage
        return {"reply": answer, "tier": tier, "usage": usage.dict() if usage else None}
    except Exception as e:
        raise HTTPException(500, f"LLM error: {e}")


@app.post("/stripe/create-checkout-session")
async def create_checkout_session(req: Request):
    body = await req.json()
    tier = (body.get("tier") or "").lower()
    price_map = {"friend": PRICE_FRIEND, "lover": PRICE_LOVER, "spouse": PRICE_SPOUSE}
    price_id = price_map.get(tier)
    if not price_id:
        raise HTTPException(400, "invalid tier")

    session = stripe.checkout.Session.create(
        mode="subscription",
        line_items=[{"price": price_id, "quantity": 1}],
        success_url=f"{FRONTEND_URL}/post-checkout?session_id={{CHECKOUT_SESSION_ID}}",
        cancel_url=f"{FRONTEND_URL}/pricing",
        billing_address_collection="auto",
    )
    return {"url": session.url}


@app.get("/stripe/confirm")
async def stripe_confirm(session_id: str, response: Response):
    if not session_id:
        raise HTTPException(400, "missing session_id")
    session = stripe.checkout.Session.retrieve(session_id)
    customer_id = session.get("customer")
    if not customer_id:
        raise HTTPException(400, "no customer")
    tier = refresh_tier_from_stripe(customer_id)
    token = jwt.encode({"customer_id": customer_id, "tier": tier}, JWT_SECRET, algorithm="HS256")
    response.set_cookie("tc_auth", token, httponly=True, samesite="lax")
    return {"ok": True, "tier": tier}


@app.get("/me")
async def me(req: Request):
    auth = get_auth_from_cookie(req)
    if auth.get("customer_id"):
        auth["tier"] = refresh_tier_from_stripe(auth["customer_id"])
    return auth
