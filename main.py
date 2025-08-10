from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from app.routes import auth_router
from app.transactions import transaction_router
from app.database import engine, Base
from app.models import User
from jose import JWTError, jwt
from app.config import settings
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_ip
from slowapi.errors import RateLimitExceeded

Base.metadata.create_all(bind=engine)

limiter = Limiter(key_func=get_ip, default_limits=["5/minute"])
app = FastAPI()
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    if request.url.path not in ["/register", "/token", "/docs", "/openapi.json"] and not request.url.path.startswith("/verify-email"):
        try:
            token = request.headers["Authorization"].split(" ")[1]
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            username: str = payload.get("sub")

            if username is None:
                return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content={"detail": "Could not validate credentials"})
        except (JWTError, KeyError):
            return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content={"detail": "Could not validate credentials"})
    response = await call_next(request)
    return response

app.include_router(auth_router)
app.include_router(transaction_router)