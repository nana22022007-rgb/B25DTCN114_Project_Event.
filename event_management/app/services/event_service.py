from datetime import datetime
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models import Event, EventStaff, User
from app.schemas.event import EventCreate, EventUpdate


# Hàm gác cổng kiểm tra quyền thành viên / Owner
def check_event_access(
    db: Session, event_id: int, user_id: int, require_owner: bool = False
) -> Event:
    # 1. Bổ sung lọc Event chưa bị xóa (deleted_at == None)
    event = (
        db.query(Event)
        .filter(Event.id == event_id, Event.deleted_at == None)
        .first()
    )
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sự kiện không tồn tại hoặc đã bị xóa",
        )

    # 1. Owner chính -> Cho qua luôn
    if event.owner_id == user_id:
        return event

    # 2. Nếu bắt buộc quyền OWNER nhưng user không phải là owner_id
    if require_owner:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Chỉ OWNER mới có quyền thực hiện thao tác này",
        )

    # 3. Nếu chỉ cần quyền MEMBER/STAFF -> Kiểm tra trong bảng EventStaff
    is_staff = (
        db.query(EventStaff)
        .filter(EventStaff.event_id == event_id, EventStaff.user_id == user_id)
        .first()
    )
    if not is_staff:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn không phải thành viên của sự kiện này",
        )

    return event


def create_event(
    db: Session, event_in: EventCreate, current_user: User
) -> Event:
    # Tạo sự kiện mới
    event = Event(
        name=event_in.name,
        description=event_in.description,
        owner_id=current_user.id,
    )
    db.add(event)
    db.flush()

    # Thêm người tạo vào bảng EventStaff với role OWNER
    owner_staff = EventStaff(
        event_id=event.id, user_id=current_user.id, role_in_event="OWNER"
    )
    db.add(owner_staff)

    db.commit()
    db.refresh(event)
    return event


def get_user_events(
    db: Session, user_id: int, search: str | None = None
) -> list[Event]:
    # Lấy các event chưa bị xóa (deleted_at == None) mà user là OWNER hoặc Staff
    query = (
        db.query(Event)
        .outerjoin(EventStaff)
        .filter(Event.deleted_at == None)  # 2. Chỉ lấy những event chưa bị xóa
        .filter((Event.owner_id == user_id) | (EventStaff.user_id == user_id))
        .distinct()
    )

    if search:
        query = query.filter(Event.name.ilike(f"%{search}%"))

    return query.all()


def update_event(
    db: Session, event_id: int, event_in: EventUpdate, current_user: User
) -> Event:
    event = check_event_access(
        db, event_id, current_user.id, require_owner=True
    )

    if event_in.name is not None:
        event.name = event_in.name
    if event_in.description is not None:
        event.description = event_in.description

    event.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(event)
    return event


# 3. SỬA HÀM DELETE THÀNH SOFT DELETE
def delete_event(db: Session, event_id: int, current_user: User):
    event = check_event_access(
        db, event_id, current_user.id, require_owner=True
    )

    # Thay vì db.delete(event), ta gán thời gian bị xóa vào deleted_at
    event.deleted_at = datetime.utcnow()
    db.commit()
    return {"message": "Xóa sự kiện thành công (Soft Delete)"}



def add_staff(
    db: Session,
    event_id: int,
    target_user_id: int,
    role_in_event: str,
    current_user: User,
):
    check_event_access(db, event_id, current_user.id, require_owner=True)

    target_user = db.query(User).filter(User.id == target_user_id).first()
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Người dùng không tồn tại",
        )

    existing = (
        db.query(EventStaff)
        .filter(
            EventStaff.event_id == event_id,
            EventStaff.user_id == target_user_id,
        )
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Người dùng đã là nhân sự của sự kiện",
        )

    new_staff = EventStaff(
        event_id=event_id,
        user_id=target_user_id,
        role_in_event=role_in_event,
    )
    db.add(new_staff)
    db.commit()


def remove_staff(
    db: Session, event_id: int, target_user_id: int, current_user: User
):
    event = check_event_access(
        db, event_id, current_user.id, require_owner=True
    )

    if target_user_id == event.owner_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Không thể xóa Owner khỏi sự kiện",
        )

    staff_to_remove = (
        db.query(EventStaff)
        .filter(
            EventStaff.event_id == event_id,
            EventStaff.user_id == target_user_id,
        )
        .first()
    )
    if not staff_to_remove:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Nhân sự không nằm trong sự kiện",
        )

    db.delete(staff_to_remove)
    db.commit()


def get_event_staffs(
    db: Session, event_id: int, current_user: User
) -> list[dict]:
    check_event_access(db, event_id, current_user.id)
    staff_list = (
        db.query(EventStaff).filter(EventStaff.event_id == event_id).all()
    )

    return [
        {
            "user_id": s.user.id,
            "full_name": s.user.full_name,
            "email": s.user.email,
            "role_in_event": s.role_in_event,
        }
        for s in staff_list
    ]