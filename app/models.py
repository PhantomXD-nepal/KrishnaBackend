from sqlalchemy import Boolean, Column, Integer, String, Float, DateTime, ForeignKey, Enum, Date
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from passlib.context import CryptContext
from datetime import datetime
import enum

Base = declarative_base()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class Role(enum.Enum):
    admin = "admin"
    teacher = "teacher"
    parent = "parent"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String)
    role = Column(Enum(Role))
    phone_number = Column(String)

    def verify_password(self, password: str) -> bool:
        return pwd_context.verify(password, self.password_hash)

    def set_password(self, password: str):
        self.password_hash = pwd_context.hash(password)

class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String)
    last_name = Column(String)
    date_of_birth = Column(Date)
    class_id = Column(Integer, ForeignKey("school_classes.id"))
    roll_number = Column(String)
    parent_id = Column(Integer, ForeignKey("users.id"))
    admission_date = Column(Date)

    school_class = relationship("SchoolClass", back_populates="students")
    parent = relationship("User")

class SchoolClass(Base):
    __tablename__ = "school_classes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    section = Column(String)
    teacher_id = Column(Integer, ForeignKey("users.id"))

    students = relationship("Student", back_populates="school_class")
    teacher = relationship("User")

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

    creator = relationship("User")

class SchoolInfo(Base):
    __tablename__ = "school_info"

    id = Column(Integer, primary_key=True, index=True)
    school_name = Column(String)
    address = Column(String)
    phone = Column(String)
    email = Column(String)
    academic_year = Column(String)
    principal_name = Column(String)

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
