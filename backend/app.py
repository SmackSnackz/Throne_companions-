import os, json, jwt, stripe
from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
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

client = OpenAI(api_key=OPENAI_API_KEY)
stripe.api_key = STRIPE_SECRET_KEY

# ---- Models ----
class ChatIn(BaseModel):
    companion_id: str
    message: str

# ---- Routes ----
@app.get("/")
def root():
    return {"ok": True, "service": "throne-backend"}

@app.get("/healthz")
def healthz():
    return {"status": "ok"}
