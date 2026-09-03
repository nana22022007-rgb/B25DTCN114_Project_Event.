from typing import Any, Dict, Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.event import Event
from app.models.event_staff import EventStaff
from app.models.event_task import EventTask, TaskPriority, TaskStatus
from app.schemas.event_task import EventTaskCreate, EventTaskUpdate


# --- HÀM BỔ TRỢ (HELPER) ---
def check_event_member(db: Session, event_id: int, user_id: int) -> Event:
    """Kiểm tra Event có tồn tại (chưa xóa mềm) và User có thuộc Event không."""
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

    is_owner = event.owner_id == user_id
    is_member = (
        db.query(EventStaff)
        .filter(EventStaff.event_id == event_id, EventStaff.user_id == user_id)
        .first()
        is not None
    )

    if not is_owner and not is_member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn không có quyền tham gia vào công việc của Event này",
        )
    return event


# --- 1. TẠO TASK ---
def create_task(
    db: Session, event_id: int, task_in: EventTaskCreate, current_user_id: int
) -> EventTask:
    check_event_member(db, event_id, current_user_id)

    if task_in.assigned_to:
        check_event_member(db, event_id, task_in.assigned_to)

    new_task = EventTask(
        event_id=event_id, creator_id=current_user_id, **task_in.model_dump()
    )
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task


# --- 2. LẤY DANH SÁCH TASK (FILTER, SEARCH, SORT, PAGINATION) ---
def get_event_tasks(
    db: Session,
    event_id: int,
    current_user_id: int,
    status_filter: Optional[TaskStatus] = None,
    priority_filter: Optional[TaskPriority] = None,
    assigned_to_filter: Optional[int] = None,
    search: Optional[str] = None,
    sort_by: str = "created_at",
    order: str = "desc",
    page: int = 1,
    size: int = 10,
) -> Dict[str, Any]:
    check_event_member(db, event_id, current_user_id)

    query = db.query(EventTask).filter(EventTask.event_id == event_id)

    if status_filter:
        query = query.filter(EventTask.status == status_filter)
    if priority_filter:
        query = query.filter(EventTask.priority == priority_filter)
    if assigned_to_filter:
        query = query.filter(EventTask.assigned_to == assigned_to_filter)

    if search:
        query = query.filter(EventTask.title.ilike(f"%{search}%"))

    sort_column = getattr(EventTask, sort_by, EventTask.created_at)
    if order.lower() == "desc":
        query = query.order_by(sort_column.desc())
    else:
        query = query.order_by(sort_column.asc())

    total_items = query.count()
    total_pages = (total_items + size - 1) // size if total_items > 0 else 1
    offset = (page - 1) * size

    tasks = query.offset(offset).limit(size).all()

    return {
        "items": tasks,
        "total_items": total_items,
        "page": page,
        "size": size,
        "total_pages": total_pages,
    }


# --- 3. XEM CHI TIẾT TASK ---
def get_task_detail(
    db: Session, task_id: int, current_user_id: int
) -> EventTask:
    task = db.query(EventTask).filter(EventTask.id == task_id).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task không tồn tại"
        )

    check_event_member(db, task.event_id, current_user_id)
    return task


# --- 4. CẬP NHẬT TASK ---
def update_task(
    db: Session,
    task_id: int,
    task_update: EventTaskUpdate,
    current_user_id: int,
) -> EventTask:
    task = db.query(EventTask).filter(EventTask.id == task_id).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task không tồn tại"
        )

    event = check_event_member(db, task.event_id, current_user_id)

    is_owner = event.owner_id == current_user_id
    is_creator = task.creator_id == current_user_id
    is_assignee = task.assigned_to == current_user_id

    update_data = task_update.model_dump(exclude_unset=True)

    if is_assignee and not is_owner and not is_creator:
        allowed_keys = {"status"}
        if any(key not in allowed_keys for key in update_data.keys()):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Bạn chỉ có quyền cập nhật trạng thái (status) của task này",
            )

    if "assigned_to" in update_data and update_data["assigned_to"] is not None:
        check_event_member(db, task.event_id, update_data["assigned_to"])

    for key, value in update_data.items():
        setattr(task, key, value)

    db.commit()
    db.refresh(task)
    return task


# --- 5. XÓA TASK ---
def delete_task(db: Session, task_id: int, current_user_id: int) -> dict:
    task = db.query(EventTask).filter(EventTask.id == task_id).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task không tồn tại"
        )

    event = check_event_member(db, task.event_id, current_user_id)

    if event.owner_id != current_user_id and task.creator_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn không có quyền xóa Task này",
        )

    db.delete(task)
    db.commit()
    return {"message": "Xóa task thành công"}