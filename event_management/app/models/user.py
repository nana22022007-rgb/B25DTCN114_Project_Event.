from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, Enum, Integer, String
from sqlalchemy.orm import relationship

from app.db.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    role = Column(String(50), default="USER", nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    owned_events = relationship("Event", back_populates="owner", cascade="all, delete-orphan")
    staff_memberships = relationship("EventStaff", back_populates="user", cascade="all, delete-orphan")
    
    # Chỉ định rõ foreign_keys để tránh xung đột giữa creator_id và assigned_to
    assigned_tasks = relationship(
        "EventTask", 
        foreign_keys="EventTask.assigned_to", 
        back_populates="assignee"
    )
    created_tasks = relationship(
        "EventTask", 
        foreign_keys="EventTask.creator_id", 
        back_populates="creator"
    )