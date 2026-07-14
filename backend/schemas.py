from pydantic import BaseModel
from typing import Optional
from datetime import date, time

class HCPBase(BaseModel):
    name: str
    specialty: str

class HCPCreate(HCPBase):
    pass

class HCP(HCPBase):
    id: int

    class Config:
        from_attributes = True

class InteractionLogBase(BaseModel):
    hcp_id: int
    date: date
    time: time
    attendees: Optional[str] = None
    topics_discussed: Optional[str] = None
    materials_shared: Optional[str] = None
    key_outcomes: Optional[str] = None
    follow_up_actions: Optional[str] = None
    samples_distributed: Optional[str] = None

class InteractionLogCreate(InteractionLogBase):
    pass

class InteractionLog(InteractionLogBase):
    id: int

    class Config:
        from_attributes = True

class ChatRequest(BaseModel):
    thread_id: str
    message: str

