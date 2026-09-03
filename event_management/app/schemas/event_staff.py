from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict

class EventStaffBase(BaseModel):
    event_id: int
    user_id: int
    role_in_event: Optional[str] = "STAFF"

class EventStaffCreate(EventStaffBase):
    pass


class EventStaffResponse(EventStaffBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

