from sqlalchemy.orm import Session
from app.models.user import User


def get_all_users(
    db: Session, search: str | None = None, is_active: bool | None = None
) -> list[User]:
    query = db.query(User)

    # Search theo tên hoặc email
    if search:
        query = query.filter(
            (User.full_name.ilike(f"%{search}%")) | (User.email.ilike(f"%{search}%"))
        )

    # Lọc theo trạng thái is_active
    if is_active is not None:
        query = query.filter(User.is_active == is_active)

    return query.all()