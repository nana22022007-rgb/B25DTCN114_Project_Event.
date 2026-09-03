from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.dependencies import get_current_user
from app.models.event_task import TaskPriority, TaskStatus
from app.models.user import User
from app.schemas.event_task import (
    EventTaskCreate,
    EventTaskListResponse,
    EventTaskResponse,
    EventTaskUpdate,
)
from app.services.event_task_service import (
    create_task,
    delete_task,
    get_event_tasks,
    get_task_detail,
    update_task,
)

router = APIRouter(prefix="", tags=["Event Tasks"])


# --- 1. TẠO TASK ---
@router.post(
    "/events/{event_id}/tasks",
    response_model=EventTaskResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Tạo task",
)
def create_new_task(
    event_id: int,
    task_in: EventTaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return create_task(
        db=db,
        event_id=event_id,
        task_in=task_in,
        current_user_id=current_user.id,
    )


# --- 2. LẤY DANH SÁCH TASK (PHÂN TRANG, FILTER, SEARCH, SORT) ---
@router.get(
    "/events/{event_id}/tasks",
    response_model=EventTaskListResponse,
    summary="Search, Filter, Sort",
)
def read_event_tasks(
    event_id: int,
    status_filter: Optional[TaskStatus] = Query(None, alias="status"),
    priority_filter: Optional[TaskPriority] = Query(None, alias="priority"),
    assigned_to_filter: Optional[int] = Query(None, alias="assigned_to"),
    search: Optional[str] = Query(
        None, description="Tìm kiếm theo tiêu đề task"
    ),
    sort_by: str = Query("created_at", description="Trường cần sắp xếp"),
    order: str = Query("desc", description="Thứ tự: asc hoặc desc"),
    page: int = Query(1, ge=1, description="Trang hiện tại"),
    size: int = Query(
        10, ge=1, le=100, description="Số lượng mục trên mỗi trang"
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_event_tasks(
        db=db,
        event_id=event_id,
        current_user_id=current_user.id,
        status_filter=status_filter,
        priority_filter=priority_filter,
        assigned_to_filter=assigned_to_filter,
        search=search,
        sort_by=sort_by,
        order=order,
        page=page,
        size=size,
    )


# --- 3. XEM CHI TIẾT TASK ---
@router.get(
    "/event-tasks/{task_id}",
    response_model=EventTaskResponse,
    description="Lấy thông tin chi tiết của 1 task theo task_id",
)
def read_task_detail(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_task_detail(
        db=db,
        task_id=task_id,
        current_user_id=current_user.id,
    )


# --- 4. CẬP NHẬT TASK ---
@router.patch("/event-tasks/{task_id}", response_model=EventTaskResponse)
def update_existing_task(
    task_id: int,
    task_update: EventTaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return update_task(
        db=db,
        task_id=task_id,
        task_update=task_update,
        current_user_id=current_user.id,
    )


# --- 5. XÓA TASK ---
@router.delete("/event-tasks/{task_id}", status_code=status.HTTP_200_OK)
def remove_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return delete_task(
        db=db,
        task_id=task_id,
        current_user_id=current_user.id,
    )