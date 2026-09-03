from enum import Enum
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.dependencies import get_current_user, require_admin
from app.models.user import User
from app.schemas.user import UserResponse
from app.services import user_service


class UserStatusFilter(str, Enum):
    ALL = "all"
    ACTIVE = "active"
    INACTIVE = "inactive"


router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserResponse)
def get_my_profile(current_user: User = Depends(get_current_user)):
    return current_user


@router.get("", response_model=list[UserResponse])
def get_all_users(
    search: str | None = None,
    status: UserStatusFilter = Query(
        default=UserStatusFilter.ALL,
        description="Lọc theo trạng thái: all (Tất cả), active (Hoạt động), inactive (Bị khóa)",
    ),
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin),
):
    is_active_bool = None
    if status == UserStatusFilter.ACTIVE:
        is_active_bool = True
    elif status == UserStatusFilter.INACTIVE:
        is_active_bool = False

    return user_service.get_all_users(
        db=db, search=search, is_active=is_active_bool
    )