import enum
from datetime import datetime
from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import relationship

from app.db.database import Base


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    # ĐÂY LÀ CỘT DÙNG ĐỂ SOFT DELETE
    deleted_at = Column(DateTime, nullable=True, default=None)

    # Relationships
    owner = relationship("User", back_populates="owned_events")
    staffs = relationship("EventStaff", back_populates="event", cascade="all, delete-orphan")
    tasks = relationship("EventTask", back_populates="event", cascade="all, delete-orphan")

