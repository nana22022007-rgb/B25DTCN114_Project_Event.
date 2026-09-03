from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse


# Hàm định dạng JSON lỗi thống nhất cho toàn bộ hệ thống
def custom_http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "code": exc.status_code,
                "message": exc.detail,
            },
        },
    )