from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.db.database import get_db
from app.models.user import User

security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
  token = credentials.credentials

  if not token:
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Thiếu Token xác thực",
    )

  payload = decode_access_token(token)

  # 1. Bắt lỗi Token HẾT HẠN
  if payload == {"error": "token_expired"}:
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token đã hết hạn, vui lòng đăng nhập lại",
    )

  # 2. Bắt lỗi Token SAI / BỊ SỬA ĐỔI
  if not payload or payload == {"error": "token_invalid"}:
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token không hợp lệ",
    )

  # 3. Kiểm tra ĐÚNG LOẠI Access Token (chặn dùng Refresh Token để gọi API)
  if payload.get("type") != "access":
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token không đúng loại (yêu cầu Access Token)",
    )

  user_id = payload.get("sub")
  if not user_id:
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token thiếu thông tin người dùng",
    )

  user = db.query(User).filter(User.id == int(user_id)).first()
  if not user:
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Không tìm thấy người dùng",
    )

  # 4. Kiểm tra tài khoản còn HOẠT ĐỘNG không
  if not user.is_active:
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Tài khoản đã bị vô hiệu hóa",
    )

  return user


def require_admin(current_user: User = Depends(get_current_user)) -> User:
  """Gác cổng: Chỉ cho phép tài khoản có role ADMIN đi qua"""
  if current_user.role != "ADMIN":
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Chỉ Admin mới có quyền truy cập",
    )
  return current_user