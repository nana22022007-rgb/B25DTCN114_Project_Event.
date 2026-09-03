from datetime import datetime, timedelta
import bcrypt
from jose import ExpiredSignatureError, JWTError, jwt
from app.core.config import settings


# Mã hóa mật khẩu
def get_password_hash(password: str) -> str:
    byte_pass = password.encode('utf-8')
    salte = bcrypt.gensalt()
    return bcrypt.hashpw(byte_pass, salte).decode('utf-8')


# Kiểm tra mật khẩu
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))


# 3. Tạo Access Token (Sống ngắn, ví dụ: 30 phút)
def create_access_token(user_id: int, role: str) -> str:
    expire = datetime.utcnow() + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    payload = {
        "sub": str(user_id),
        "role": role,
        "type": "access",  # Đánh dấu loại token
        "exp": expire,
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


# 4. BỔ SUNG: Tạo Refresh Token (Sống dài, ví dụ: 7 ngày)
def create_refresh_token(user_id: int) -> str:
    # Lấy REFRESH_TOKEN_EXPIRE_DAYS từ config (hoặc mặc định 7 ngày)
    expire_days = getattr(settings, "REFRESH_TOKEN_EXPIRE_DAYS", 7)
    expire = datetime.utcnow() + timedelta(days=expire_days)
    
    payload = {
        "sub": str(user_id),
        "type": "refresh",  # Đánh dấu loại token
        "exp": expire,
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


# 5. Giải mã Token
def decode_access_token(token: str) -> dict | None:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        return payload
    except ExpiredSignatureError:
        return {"error": "token_expired"}
    except JWTError:
        return {"error": "token_invalid"}