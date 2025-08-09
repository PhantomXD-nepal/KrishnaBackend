from pydantic import BaseModel, EmailStr
from datetime import datetime

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class User(BaseModel):
    id: int
    username: str
    email: EmailStr
    is_verified: bool

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
