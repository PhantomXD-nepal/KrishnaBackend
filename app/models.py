from __future__ import annotations
from sqlalchemy import Boolean, Column, Integer, String, Float, DateTime, ForeignKey, Enum, Date, Table
from sqlalchemy.orm import relationship, Mapped, mapped_column
from passlib.context import CryptContext
from datetime import datetime
import enum
from fastapi_users.db import SQLAlchemyBaseUserTable
from typing import List, Optional
from app.database import Base # Import Base from app.database

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class Role(enum.Enum):
    admin = "admin"
    teacher = "teacher"
    parent = "parent"
    student = "student"

class Transaction(Base): # Moved Transaction class here
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    price = Column(Float)
    category = Column(String)
    notes = Column(String, nullable=True)
    date_created = Column(DateTime, default=datetime.now)
    owner_id = Column(Integer, ForeignKey("users.id"))

    user = relationship("User", back_populates="transactions")

class User(SQLAlchemyBaseUserTable["User"], Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(1024), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_staff: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    role = Column(Enum(Role), default=Role.parent, nullable=False) # Changed to use Enum and default to parent
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)

    # Relationships
    transactions: Mapped[List["Transaction"]] = relationship("Transaction", back_populates="user")
    school_info: Mapped[Optional["SchoolInfo"]] = relationship("SchoolInfo", back_populates="user", uselist=False)
    school_events: Mapped[List["SchoolEvent"]] = relationship("SchoolEvent", back_populates="creator")
    student: Mapped[Optional["Student"]] = relationship("Student", back_populates="user", uselist=False) # Added student relationship


class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String)
    last_name = Column(String)
    date_of_birth = Column(Date)
    class_id = Column(Integer, ForeignKey("school_classes.id"))
    roll_number = Column(String)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True) # Changed from parent_id to user_id
    admission_date = Column(Date)

    school_class = relationship("SchoolClass", back_populates="students")
    user = relationship("User", back_populates="student") # Changed from parent to user

class SchoolClass(Base):
    __tablename__ = "school_classes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    section = Column(String)
    teacher_id = Column(Integer, ForeignKey("users.id"))

    students = relationship("Student", back_populates="school_class")
    teacher = relationship("User")
    subjects = relationship("Subject", secondary=class_subject_association, back_populates="classes")

class Attendance(Base):
    __tablename__ = "attendances"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"))
    date = Column(Date)
    present = Column(Boolean)
    marked_by = Column(Integer, ForeignKey("users.id"))

    student = relationship("Student")
    marker = relationship("User")

class FeePayment(Base):
    __tablename__ = "fee_payments"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"))
    amount = Column(Float)
    month = Column(String)
    payment_date = Column(Date)
    status = Column(String) # pending/paid/failed
    remarks = Column(String)

    student = relationship("Student")

class SchoolEvent(Base):
    __tablename__ = "school_events"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(String)
    date = Column(Date)
    created_by = Column(Integer, ForeignKey("users.id"))

    creator = relationship("User", back_populates="school_events")

class SchoolInfo(Base):
    __tablename__ = "school_info"

    id = Column(Integer, primary_key=True, index=True)
    school_name = Column(String)
    address = Column(String)
    phone = Column(String)
    email = Column(String)
    academic_year = Column(String)
    principal_name = Column(String)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True) # Added foreign key to users

    user = relationship("User", back_populates="school_info") # Added relationship

class SchoolTransaction(Base):
    __tablename__ = "school_transactions"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(String)
    amount = Column(Float)
    type = Column(String) # income/expense
    date = Column(Date)
    recorded_by = Column(Integer, ForeignKey("users.id"))

    recorder = relationship("User")

class Announcement(Base):
    __tablename__ = "announcements"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    message = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(Integer, ForeignKey("users.id"))
    audience = Column(String) # all/teachers/parents

    creator = relationship("User")

# Association table for SchoolClass and Subject
class_subject_association = Table(
    "class_subject_association",
    Base.metadata,
    Column("class_id", Integer, ForeignKey("school_classes.id"), primary_key=True),
    Column("subject_id", Integer, ForeignKey("subjects.id"), primary_key=True)
)

class Subject(Base):
    __tablename__ = "subjects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)

    classes = relationship("SchoolClass", secondary=class_subject_association, back_populates="subjects")