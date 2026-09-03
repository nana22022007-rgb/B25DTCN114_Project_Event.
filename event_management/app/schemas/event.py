from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


# Event Schemas
class EventCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = None


class EventUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None


class EventResponse(BaseModel):
    id: int
    name: str
    description: str | None
    owner_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class EventResponseUpdate(BaseModel):
    id: int
    name: str
    description: str | None
    owner_id: int
    updated_at: datetime | None
    
    model_config = ConfigDict(from_attributes=True)


# Staff Schemas
class StaffAdd(BaseModel):
    user_id: int
    role_in_event: str = "STAFF"


class StaffResponse(BaseModel):
    user_id: int
    full_name: str
    email: str
    role_in_event: str

    model_config = ConfigDict(from_attributes=True)