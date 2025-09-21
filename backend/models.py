from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime
import uuid

# Existing models
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
    tier: str = Field(default="novice")
    mode: str = Field(default="text")

class ChatMessageCreate(BaseModel):
    companion_id: str
    message: str
    is_user: bool
    mode: str = Field(default="text")

# New tier system models
class UserFeatures(BaseModel):
    voice: bool = False
    visuals: bool = False
    finance_tools: bool = False
    intimacy_modes: bool = False
    custom_persona: bool = False
    private_hosting: bool = False

class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: Optional[str] = None
    tier: str = Field(default="novice")
    chosen_companion: str = Field(default="sophia")
    memory_retention_days: int = Field(default=1)
    features: UserFeatures = Field(default_factory=UserFeatures)
    prompting_mastery: str = Field(default="clarity")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_active: datetime = Field(default_factory=datetime.utcnow)

class UserCreate(BaseModel):
    email: Optional[str] = None
    tier: str = Field(default="novice")
    chosen_companion: str = Field(default="sophia")

class UserUpdate(BaseModel):
    tier: Optional[str] = None
    chosen_companion: Optional[str] = None
    features: Optional[UserFeatures] = None

class ConsentLog(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    consent_type: str  # "intimacy", "therapy", "finance"
    granted: bool
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    session_id: str

class MemorySummary(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    companion_id: str
    summary_text: str
    period_start: datetime
    period_end: datetime
    created_at: datetime = Field(default_factory=datetime.utcnow)

class TierUpgradeRequest(BaseModel):
    current_tier: str
    target_tier: str
    requested_feature: str