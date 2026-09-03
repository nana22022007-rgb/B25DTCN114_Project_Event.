from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas import (
    EventCreate,
    EventResponse,
    EventResponseUpdate,
    EventUpdate,
    StaffAdd,
    StaffResponse,
)
from app.services import event_service

router = APIRouter(prefix="/events", tags=["Events"])


@router.post("", response_model=EventResponse, status_code=status.HTTP_201_CREATED)
def create_event(
    event_in: EventCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return event_service.create_event(db, event_in, current_user)


@router.get("", response_model=list[EventResponse])
def get_my_events(
    search: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return event_service.get_user_events(db, current_user.id, search)


@router.get("/{event_id}", response_model=EventResponse)
def get_event_detail(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return event_service.check_event_access(db, event_id, current_user.id)


@router.patch("/{event_id}", response_model=EventResponseUpdate)
def update_event(
    event_id: int,
    event_in: EventUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return event_service.update_event(db, event_id, event_in, current_user)


@router.delete("/{event_id}", status_code=status.HTTP_200_OK)
def delete_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    event_service.delete_event(db, event_id, current_user)
    return {"message": f"Xóa sự kiện có ID {event_id} thành công"}


@router.get("/{event_id}/members", response_model=list[StaffResponse])
def get_members(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return event_service.get_event_staffs(db, event_id, current_user)


@router.post("/{event_id}/members", status_code=status.HTTP_201_CREATED)
def add_member(
    event_id: int,
    staff_in: StaffAdd,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    event_service.add_staff(
        db,
        event_id,
        staff_in.user_id,
        staff_in.role_in_event,
        current_user,
    )
    return {"message": "Thêm nhân sự thành công"}


@router.delete("/{event_id}/members/{user_id}", status_code=status.HTTP_200_OK)
def remove_member(
    event_id: int,
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    event_service.remove_staff(db, event_id, user_id, current_user)
    return {"message": "Xóa thành viên khỏi sự kiện thành công"}