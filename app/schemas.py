from pydantic import BaseModel, EmailStr
from datetime import datetime, date
from app.models import Role

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: Role = Role.parent

class User(BaseModel):
    id: int
    name: str
    email: EmailStr
    is_verified: bool
    role: Role

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TransactionBase(BaseModel):
    name: str
    price: float
    category: str
    notes: str | None = None
    date_created: datetime | None = None

class TransactionCreate(TransactionBase):
    pass

class Transaction(TransactionBase):
    id: int
    owner_id: int

    class Config:
        from_attributes = True

class StudentCreate(BaseModel):
    first_name: str
    last_name: str
    date_of_birth: date
    class_id: int | None = None
    roll_number: str | None = None
    admission_date: date

class StudentRead(StudentCreate):
    id: int
    user_id: int

    class Config:
        from_attributes = True

# SchoolClass Schemas
class SchoolClassCreate(BaseModel):
    name: str
    section: str
    teacher_id: int

class SchoolClassRead(SchoolClassCreate):
    id: int

    class Config:
        from_attributes = True

# Attendance Schemas
class AttendanceCreate(BaseModel):
    student_id: int
    date: date
    present: bool
    marked_by: int

class AttendanceRead(AttendanceCreate):
    id: int

    class Config:
        from_attributes = True

# FeePayment Schemas
class FeePaymentCreate(BaseModel):
    student_id: int
    amount: float
    month: str
    payment_date: date
    status: str
    remarks: str | None = None

class FeePaymentRead(FeePaymentCreate):
    id: int

    class Config:
        from_attributes = True

# SchoolEvent Schemas
class SchoolEventCreate(BaseModel):
    title: str
    description: str
    date: date
    created_by: int

class SchoolEventRead(SchoolEventCreate):
    id: int

    class Config:
        from_attributes = True

# SchoolInfo Schemas
class SchoolInfoCreate(BaseModel):
    school_name: str
    address: str
    phone: str
    email: str
    academic_year: str
    principal_name: str
    user_id: int | None = None # user_id is optional for creation, can be linked later

class SchoolInfoRead(SchoolInfoCreate):
    id: int

    class Config:
        from_attributes = True

# SchoolTransaction Schemas
class SchoolTransactionCreate(BaseModel):
    title: str
    description: str
    amount: float
    type: str
    date: date
    recorded_by: int

class SchoolTransactionRead(SchoolTransactionCreate):
    id: int

    class Config:
        from_attributes = True

# Announcement Schemas
class AnnouncementCreate(BaseModel):
    title: str
    message: str
    created_by: int
    audience: str

class AnnouncementRead(AnnouncementCreate):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
