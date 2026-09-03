from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.exceptions import custom_http_exception_handler
from app.db.database import Base, engine
import app.models  # Import để SQLAlchemy nhận diện các models
from app.routers import (
    auth_router,
    event_router,
    event_task_router,
    users_router,
)

# Tạo bảng trong DB nếu chưa có
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
)

# Custom Exception Handler
app.add_exception_handler(HTTPException, custom_http_exception_handler)

# Cấu hình CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Thêm các Routers với Prefix API V1
app.include_router(auth_router, prefix=settings.API_V1_STR)
app.include_router(users_router, prefix=settings.API_V1_STR)
app.include_router(event_router, prefix=settings.API_V1_STR)
app.include_router(event_task_router, prefix=settings.API_V1_STR)


@app.get("/health-check", tags=["Health Check"])
def health_check():
    return {"status": "ok", "message": "Server đang hoạt động bình thường!"}