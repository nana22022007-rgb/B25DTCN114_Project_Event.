from datetime import datetime, timedelta, timezone
from app.core.security import get_password_hash
from app.db.database import SessionLocal
from app.models.event import Event
from app.models.event_staff import EventStaff
from app.models.event_task import (
    EventTask,
    TaskComment,
    TaskPriority,
    TaskStatus,
)
from app.models.user import User


def seed_data():
    db = SessionLocal()
    try:
        print("🌱 Đang bắt đầu seed dữ liệu mẫu...")

        # ------------------------------------------------------------------
        # 1. SEED USERS
        # ------------------------------------------------------------------
        users_data = [
            {
                "email": "admin@gmail.com",
                "full_name": "System Admin",
                "password_hash": get_password_hash("admin123"),
                "role": "ADMIN",
                "is_active": True,
            },
            {
                "email": "manager@gmail.com",
                "full_name": "Nguyễn Văn Quản Lý",
                "password_hash": get_password_hash("123456"),
                "role": "USER",
                "is_active": True,
            },
            {
                "email": "staff1@gmail.com",
                "full_name": "Trần Thị Nhân Viên 1",
                "password_hash": get_password_hash("123456"),
                "role": "USER",
                "is_active": True,
            },
            {
                "email": "staff2@gmail.com",
                "full_name": "Lê Văn Nhân Viên 2",
                "password_hash": get_password_hash("123456"),
                "role": "USER",
                "is_active": True,
            },
        ]

        users_db = {}
        for u_info in users_data:
            user = db.query(User).filter(User.email == u_info["email"]).first()
            if not user:
                user = User(**u_info)
                db.add(user)
                db.flush()
                print(f" -> Đã tạo User: {user.email}")
            else:
                print(f" -> User đã tồn tại: {user.email}")
            users_db[u_info["email"]] = user

        manager = users_db["manager@gmail.com"]
        staff1 = users_db["staff1@gmail.com"]
        staff2 = users_db["staff2@gmail.com"]

        # ------------------------------------------------------------------
        # 2. SEED EVENT & EVENT STAFF
        # ------------------------------------------------------------------
        event_title = "Sự kiện Tech Conference 2026"
        event = db.query(Event).filter(Event.title == event_title).first()

        now = datetime.now(timezone.utc)

        if not event:
            event = Event(
                title=event_title,
                description="Hội thảo công nghệ quy mô 500 khách mời.",
                location="Trung tâm Hội nghị Quốc gia",
                start_time=now + timedelta(days=7),
                end_time=now + timedelta(days=8),
                owner_id=manager.id,
            )
            db.add(event)
            db.flush()
            print(f" -> Đã tạo Event: {event.title} (Owner: {manager.full_name})")

            # Gán Manager và Staff vào EventStaff
            staff_list = [
                EventStaff(
                    event_id=event.id, user_id=manager.id, role_in_event="MANAGER"
                ),
                EventStaff(
                    event_id=event.id, user_id=staff1.id, role_in_event="STAFF"
                ),
                EventStaff(
                    event_id=event.id, user_id=staff2.id, role_in_event="STAFF"
                ),
            ]
            db.add_all(staff_list)
            print(" -> Đã gán manager, staff1 & staff2 vào EventStaff.")

        # ------------------------------------------------------------------
        # 3. SEED EVENT TASKS
        # ------------------------------------------------------------------
        task_check = (
            db.query(EventTask).filter(EventTask.event_id == event.id).first()
        )
        if not task_check:
            tasks = [
                EventTask(
                    event_id=event.id,
                    creator_id=manager.id,
                    assigned_to=staff1.id,
                    title="Lên kịch bản MC và chương trình",
                    description="Chuẩn bị file timeline chi tiết từng phút cho MC.",
                    status=TaskStatus.IN_PROGRESS,
                    priority=TaskPriority.HIGH,
                    due_date=now + timedelta(days=3),
                ),
                EventTask(
                    event_id=event.id,
                    creator_id=manager.id,
                    assigned_to=staff2.id,
                    title="Thiết kế Banner & Standee",
                    description="In ấn 2 standee đặt ở sảnh chính và 1 backdrop sân khấu.",
                    status=TaskStatus.TODO,
                    priority=TaskPriority.MEDIUM,
                    due_date=now + timedelta(days=4),
                ),
                EventTask(
                    event_id=event.id,
                    creator_id=staff1.id,
                    assigned_to=staff1.id,
                    title="Đặt tiệc Teabreak",
                    description="Liên hệ bên catering chốt menu 500 suất bánh ngọt & nước trái cây.",
                    status=TaskStatus.DONE,
                    priority=TaskPriority.LOW,
                    due_date=now + timedelta(days=1),
                ),
            ]
            db.add_all(tasks)
            db.flush()
            print(" -> Đã tạo 3 Task mẫu cho Event.")

            # Add comment mẫu vào task đầu tiên
            sample_comment = TaskComment(
                task_id=tasks[0].id,
                user_id=staff1.id,
                content="Em đã gửi bản draft kịch bản qua Zalo, anh Manager xem qua giúp em nhé!",
            )
            db.add(sample_comment)
            print(" -> Đã tạo Comment mẫu cho Task.")

        db.commit()
        print("✅ Seed dữ liệu hoàn tất thành công!")

    except Exception as e:
        db.rollback()
        print(f"❌ Lỗi khi seed dữ liệu: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    seed_data()