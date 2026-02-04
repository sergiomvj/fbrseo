from fastapi import Request
from app.models.auth import UsageLog
from app.database import SessionLocal
import time

async def log_api_usage(request: Request, call_next):
    """Middleware para logar uso da API"""
    start_time = time.time()
    
    response = await call_next(request)
    
    process_time = int((time.time() - start_time) * 1000)
    
    if hasattr(request.state, "client_id") and hasattr(request.state, "api_key_id"):
        db = SessionLocal()
        try:
            log = UsageLog(
                client_id=request.state.client_id,
                api_key_id=request.state.api_key_id,
                endpoint=request.url.path,
                method=request.method,
                status_code=response.status_code,
                ip_address=request.client.host if request.client else None,
                user_agent=request.headers.get("user-agent"),
                response_time_ms=process_time
            )
            db.add(log)
            db.commit()
        except:
            pass
        finally:
            db.close()
    
    response.headers["X-Process-Time-MS"] = str(process_time)
    return response
