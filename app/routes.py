from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app import models, schemas
from app.database import get_db
from app.config import settings
from jose import JWTError, jwt
from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
from fastapi_mail import ConnectionConfig
from fastapi_users.password import PasswordHelper
from app.middleware import role_required
from app.dependencies import get_current_user # Import get_current_user from dependencies
from typing import Optional # Import Optional

auth_router = APIRouter()

# Removed SECRET_KEY, ALGORITHM, oauth2_scheme as they are now in app.dependencies

s = URLSafeTimedSerializer(settings.SECRET_KEY)

conf = ConnectionConfig(
    MAIL_USERNAME=settings.EMAIL_USERNAME,
    MAIL_PASSWORD=settings.EMAIL_PASSWORD,
    MAIL_FROM=settings.EMAIL_FROM,
    MAIL_PORT=settings.EMAIL_PORT,
    MAIL_SERVER=settings.EMAIL_HOST,
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=True,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True
)

password_helper = PasswordHelper() # Instantiate PasswordHelper

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256") # Use settings.SECRET_KEY and hardcode ALGORITHM
    return encoded_jwt

@auth_router.post("/register", response_model=schemas.User)
async def register(
    user: schemas.UserCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
    student_data: Optional[schemas.StudentCreate] = None # Added student_data
):
    # Admin-only registration check
    if current_user.name != "admin" or current_user.email != "admin" or current_user.role != models.Role.admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admin can register new users")

    # Validate role
    allowed_roles = [role.value for role in models.Role]
    if user.role.value not in allowed_roles:
        raise HTTPException(status_code=400, detail=f"Role must be one of {allowed_roles}")

    # If registering a student, student_data must be provided
    if user.role == models.Role.student and not student_data:
        raise HTTPException(status_code=400, detail="Student data is required for student registration")

    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    db_user = db.query(models.User).filter(models.User.name == user.name).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Name already registered")
    
    hashed_password = password_helper.hash(user.password)

    new_user = models.User(
        name=user.name,
        email=user.email,
        hashed_password=hashed_password,
        role=user.role
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # If registering a student, create the student entry
    if user.role == models.Role.student and student_data:
        new_student = models.Student(
            user_id=new_user.id,
            first_name=student_data.first_name,
            last_name=student_data.last_name,
            date_of_birth=student_data.date_of_birth,
            class_id=student_data.class_id,
            roll_number=student_data.roll_number,
            admission_date=student_data.admission_date
        )
        db.add(new_student)
        db.commit()
        db.refresh(new_student)

    return new_user

@auth_router.get("/verify-email/{token}")
async def verify_email(token: str, db: Session = Depends(get_db)):
    try:
        email = s.loads(token, salt='email-confirm', max_age=3600)
    except SignatureExpired:
        raise HTTPException(status_code=400, detail="Token expired")
    
    user = db.query(models.User).filter(models.User.email == email).first()
    if user:
        user.is_verified = True
        db.commit()
        return {"message": "Email verified successfully"}
    else:
        raise HTTPException(status_code=404, detail="User not found")

@auth_router.post("/token", response_model=schemas.Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    if not user or not password_helper.verify_and_update(form_data.password, user.hashed_password)[0]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@auth_router.get("/protected", dependencies=[Depends(role_required([models.Role.teacher]))])
async def protected_route(current_user: models.User = Depends(get_current_user)):
    return {"message": f"Hello {current_user.name}, you are accessing a protected route."}