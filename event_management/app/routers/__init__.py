from app.routers.auth import router as auth_router
from app.routers.event import router as event_router
from app.routers.event_task import router as event_task_router
from app.routers.users import router as users_router

__all__ = [
    "auth_router",
    "event_router",
    "event_task_router",
    "users_router",
]