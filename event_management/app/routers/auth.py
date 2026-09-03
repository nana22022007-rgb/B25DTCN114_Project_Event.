from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.auth import LoginRequest, MessageResponse, RefreshTokenRequest, Token
from app.schemas.user import UserCreate
from app.services import auth_service

router = APIRouter(prefix="/auth", tags=["Auth"])

FAILED_ATTEMPTS = {}


@router.post(
    "/register",
    response_model=MessageResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    return auth_service.register_user(db=db, user_in=user_in)


@router.post("/login", response_model=Token)
def login(
    request: Request, login_in: LoginRequest, db: Session = Depends(get_db)
):
    client_ip = request.client.host
    now = datetime.now(timezone.utc)

    if client_ip in FAILED_ATTEMPTS:
        attempt_info = FAILED_ATTEMPTS[client_ip]

        if attempt_info["count"] >= 5:
            if now - attempt_info["last_attempt"] < timedelta(minutes=1):
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Bạn đã thử quá 5 lần. Vui lòng thử lại sau 1 phút!",
                )
            else:
                FAILED_ATTEMPTS[client_ip] = {"count": 0, "last_attempt": now}

    try:
        token = auth_service.authenticate_user(db=db, login_in=login_in)

        if client_ip in FAILED_ATTEMPTS:
            del FAILED_ATTEMPTS[client_ip]

        return token

    except HTTPException as exc:
        if exc.status_code == status.HTTP_401_UNAUTHORIZED:
            if client_ip not in FAILED_ATTEMPTS:
                FAILED_ATTEMPTS[client_ip] = {"count": 1, "last_attempt": now}
            else:
                FAILED_ATTEMPTS[client_ip]["count"] += 1
                FAILED_ATTEMPTS[client_ip]["last_attempt"] = now

        raise exc


@router.post("/refresh", response_model=Token)
def refresh_token(body: RefreshTokenRequest, db: Session = Depends(get_db)):
    return auth_service.refresh_access_token(
        db=db, refresh_token=body.refresh_token
    )