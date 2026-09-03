from datetime import datetime
import enum
from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.db.database import Base


class TaskStatus(str, enum.Enum):
    TODO = "TODO"
    IN_PROGRESS = "IN_PROGRESS"
    DONE = "DONE"


class TaskPriority(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class EventTask(Base):
    __tablename__ = "event_tasks"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(
        Integer, ForeignKey("events.id", ondelete="CASCADE"), nullable=False
    )
    creator_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    assigned_to = Column(Integer, ForeignKey("users.id"), nullable=True)

    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(Enum(TaskStatus), default=TaskStatus.TODO, nullable=False)
    priority = Column(
        Enum(TaskPriority), default=TaskPriority.MEDIUM, nullable=False
    )
    due_date = Column(DateTime, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # 1. Bổ sung relationship event bị thiếu
    event = relationship("Event", back_populates="tasks")

    # 2. Relationships nối về User
    creator = relationship(
        "User", foreign_keys=[creator_id], back_populates="created_tasks"
    )
    assignee = relationship(
        "User", foreign_keys=[assigned_to], back_populates="assigned_tasks"
    )


# class TaskComment(Base):
#     __tablename__ = "task_comments"

#     id = Column(Integer, primary_key=True, index=True)
#     task_id = Column(
#         Integer, ForeignKey("event_tasks.id", ondelete="CASCADE"), nullable=False
#     )
#     user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
#     content = Column(Text, nullable=False)
#     created_at = Column(DateTime, default=datetime.utcnow)

#     user = relationship("User")


# class TaskAttachment(Base):
#     __tablename__ = "task_attachments"

#     id = Column(Integer, primary_key=True, index=True)
#     task_id = Column(
#         Integer, ForeignKey("event_tasks.id", ondelete="CASCADE"), nullable=False
#     )
#     uploaded_by = Column(Integer, ForeignKey("users.id"), nullable=False)

#     file_name = Column(String(255), nullable=False)
#     file_path = Column(String(500), nullable=False)
#     file_type = Column(String(50), nullable=False)
#     file_size = Column(Integer, nullable=False)
#     created_at = Column(DateTime, default=datetime.utcnow)