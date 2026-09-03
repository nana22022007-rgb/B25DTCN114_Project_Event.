from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_access_token,
    get_password_hash,
    verify_password,
)
from app.models.user import User
from app.schemas.auth import LoginRequest
from app.schemas.user import UserCreate


def register_user(db: Session, user_in: UserCreate) -> dict:
    # 1. Kiểm tra email tồn tại
    existing_user = db.query(User).filter(User.email == user_in.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email này đã được đăng ký trên hệ thống.",
        )

    # 2. Hash mật khẩu và lưu DB
    hashed_pass = get_password_hash(user_in.password)
    new_user = User(
        email=user_in.email,
        password_hash=hashed_pass,
        full_name=user_in.full_name,
        role="USER",
        is_active=True,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "Đăng ký thành công"}


def authenticate_user(db: Session, login_in: LoginRequest) -> dict:
    # 1. Tìm user theo email
    user = db.query(User).filter(User.email == login_in.email).first()

    # 2. Kiểm tra mật khẩu
    if not user or not verify_password(login_in.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email hoặc mật khẩu không chính xác",
        )

    # 3. Kiểm tra tài khoản bị khóa
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tài khoản đã bị khóa",
        )

    # 4. Tạo cả Access Token & Refresh Token
    user_role = str(user.role) if user.role else "USER"
    access_token = create_access_token(user_id=user.id, role=user_role)
    refresh_token = create_refresh_token(user_id=user.id)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


def refresh_access_token(db: Session, refresh_token: str) -> dict:
    # 1. Giải mã refresh_token
    payload = decode_access_token(refresh_token)

    # 2. Kiểm tra token có bị lỗi / hết hạn không
    if not payload or "error" in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token không hợp lệ hoặc đã hết hạn",
        )

    # 3. Kiểm tra đúng loại token là 'refresh' hay không
    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Loại token không hợp lệ",
        )

    # 4. Kiểm tra User trong Database
    user_id = int(payload.get("sub"))
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Người dùng không tồn tại",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tài khoản đã bị khóa",
        )

    # 5. Tạo Access Token mới
    user_role = str(user.role) if user.role else "USER"
    new_access_token = create_access_token(user_id=user.id, role=user_role)

    return {
        "access_token": new_access_token,
        "refresh_token": refresh_token,  # Giữ nguyên refresh token cũ
        "token_type": "bearer",
    }