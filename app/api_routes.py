from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app import models, schemas
from app.database import get_db
from app.dependencies import get_current_user
from app.middleware import role_required
from typing import List

api_router = APIRouter()

# Student Endpoints
@api_router.get("/students/", response_model=List[schemas.StudentRead], dependencies=[Depends(role_required([models.Role.admin, models.Role.teacher]))])
async def list_students(db: Session = Depends(get_db)):
    students = db.query(models.Student).all()
    return students

@api_router.get("/students/{student_id}", response_model=schemas.StudentRead, dependencies=[Depends(role_required([models.Role.admin, models.Role.teacher, models.Role.parent]))])
async def get_student(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    student = db.query(models.Student).filter(models.Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    # Parents can only view their own children
    if current_user.role == models.Role.parent and student.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view this student")

    return student

@api_router.put("/students/{student_id}", response_model=schemas.StudentRead, dependencies=[Depends(role_required([models.Role.admin, models.Role.teacher]))])
async def update_student(
    student_id: int,
    student_update: schemas.StudentCreate, # Using StudentCreate for update, can create StudentUpdate if needed
    db: Session = Depends(get_db)
):
    student = db.query(models.Student).filter(models.Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    for field, value in student_update.dict(exclude_unset=True).items():
        setattr(student, field, value)
    
    db.add(student)
    db.commit()
    db.refresh(student)
    return student

@api_router.delete("/students/{student_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(role_required([models.Role.admin]))])
async def delete_student(
    student_id: int,
    db: Session = Depends(get_db)
):
    student = db.query(models.Student).filter(models.Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    db.delete(student)
    db.commit()
    return

# SchoolClass Endpoints
@api_router.post("/classes/", response_model=schemas.SchoolClassRead, dependencies=[Depends(role_required([models.Role.admin, models.Role.teacher]))])
async def create_class(
    school_class: schemas.SchoolClassCreate,
    db: Session = Depends(get_db)
):
    db_class = models.SchoolClass(**school_class.dict())
    db.add(db_class)
    db.commit()
    db.refresh(db_class)
    return db_class

@api_router.get("/classes/", response_model=List[schemas.SchoolClassRead], dependencies=[Depends(role_required([models.Role.admin, models.Role.teacher]))])
async def list_classes(db: Session = Depends(get_db)):
    classes = db.query(models.SchoolClass).all()
    return classes

@api_router.get("/classes/{class_id}", response_model=schemas.SchoolClassRead, dependencies=[Depends(role_required([models.Role.admin, models.Role.teacher]))])
async def get_class(
    class_id: int,
    db: Session = Depends(get_db)
):
    school_class = db.query(models.SchoolClass).filter(models.SchoolClass.id == class_id).first()
    if not school_class:
        raise HTTPException(status_code=404, detail="Class not found")
    return school_class

@api_router.put("/classes/{class_id}", response_model=schemas.SchoolClassRead, dependencies=[Depends(role_required([models.Role.admin, models.Role.teacher]))])
async def update_class(
    class_id: int,
    school_class_update: schemas.SchoolClassCreate, # Using create schema for update
    db: Session = Depends(get_db)
):
    school_class = db.query(models.SchoolClass).filter(models.SchoolClass.id == class_id).first()
    if not school_class:
        raise HTTPException(status_code=404, detail="Class not found")
    
    for field, value in school_class_update.dict(exclude_unset=True).items():
        setattr(school_class, field, value)
    
    db.add(school_class)
    db.commit()
    db.refresh(school_class)
    return school_class

@api_router.delete("/classes/{class_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(role_required([models.Role.admin]))])
async def delete_class(
    class_id: int,
    db: Session = Depends(get_db)
):
    school_class = db.query(models.SchoolClass).filter(models.SchoolClass.id == class_id).first()
    if not school_class:
        raise HTTPException(status_code=404, detail="Class not found")
    
    db.delete(school_class)
    db.commit()
    return

# Attendance Endpoints
@api_router.post("/attendance/", response_model=schemas.AttendanceRead, dependencies=[Depends(role_required([models.Role.admin, models.Role.teacher]))])
async def create_attendance(
    attendance: schemas.AttendanceCreate,
    db: Session = Depends(get_db)
):
    db_attendance = models.Attendance(**attendance.dict())
    db.add(db_attendance)
    db.commit()
    db.refresh(db_attendance)
    return db_attendance

@api_router.get("/attendance/", response_model=List[schemas.AttendanceRead], dependencies=[Depends(role_required([models.Role.admin, models.Role.teacher]))])
async def list_attendance(db: Session = Depends(get_db)):
    attendance_records = db.query(models.Attendance).all()
    return attendance_records

@api_router.get("/attendance/{attendance_id}", response_model=schemas.AttendanceRead, dependencies=[Depends(role_required([models.Role.admin, models.Role.teacher]))])
async def get_attendance(
    attendance_id: int,
    db: Session = Depends(get_db)
):
    attendance = db.query(models.Attendance).filter(models.Attendance.id == attendance_id).first()
    if not attendance:
        raise HTTPException(status_code=404, detail="Attendance record not found")
    return attendance

@api_router.put("/attendance/{attendance_id}", response_model=schemas.AttendanceRead, dependencies=[Depends(role_required([models.Role.admin, models.Role.teacher]))])
async def update_attendance(
    attendance_id: int,
    attendance_update: schemas.AttendanceCreate, # Using create schema for update
    db: Session = Depends(get_db)
):
    attendance = db.query(models.Attendance).filter(models.Attendance.id == attendance_id).first()
    if not attendance:
        raise HTTPException(status_code=404, detail="Attendance record not found")
    
    for field, value in attendance_update.dict(exclude_unset=True).items():
        setattr(attendance, field, value)
    
    db.add(attendance)
    db.commit()
    db.refresh(attendance)
    return attendance

@api_router.delete("/attendance/{attendance_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(role_required([models.Role.admin]))])
async def delete_attendance(
    attendance_id: int,
    db: Session = Depends(get_db)
):
    attendance = db.query(models.Attendance).filter(models.Attendance.id == attendance_id).first()
    if not attendance:
        raise HTTPException(status_code=404, detail="Attendance record not found")
    
    db.delete(attendance)
    db.commit()
    return

# FeePayment Endpoints
@api_router.post("/fee_payments/", response_model=schemas.FeePaymentRead, dependencies=[Depends(role_required([models.Role.admin, models.Role.teacher]))])
async def create_fee_payment(
    fee_payment: schemas.FeePaymentCreate,
    db: Session = Depends(get_db)
):
    db_fee_payment = models.FeePayment(**fee_payment.dict())
    db.add(db_fee_payment)
    db.commit()
    db.refresh(db_fee_payment)
    return db_fee_payment

@api_router.get("/fee_payments/", response_model=List[schemas.FeePaymentRead], dependencies=[Depends(role_required([models.Role.admin, models.Role.teacher, models.Role.parent]))])
async def list_fee_payments(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    if current_user.role == models.Role.parent:
        # Parents can only see their children's fee payments
        # This requires joining FeePayment with Student and User
        # For simplicity, let's assume FeePayment has a direct link to user_id or student_id can be used to find user_id
        # FeePayment has student_id, so we need to check if the student belongs to the current parent
        fee_payments = db.query(models.FeePayment).join(models.Student).filter(models.Student.user_id == current_user.id).all()
    else:
        fee_payments = db.query(models.FeePayment).all()
    return fee_payments

@api_router.get("/fee_payments/{fee_payment_id}", response_model=schemas.FeePaymentRead, dependencies=[Depends(role_required([models.Role.admin, models.Role.teacher, models.Role.parent]))])
async def get_fee_payment(
    fee_payment_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    fee_payment = db.query(models.FeePayment).filter(models.FeePayment.id == fee_payment_id).first()
    if not fee_payment:
        raise HTTPException(status_code=404, detail="Fee payment record not found")
    
    if current_user.role == models.Role.parent:
        # Check if the fee payment belongs to the current parent's child
        student = db.query(models.Student).filter(models.Student.id == fee_payment.student_id).first()
        if not student or student.user_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view this fee payment")

    return fee_payment

@api_router.put("/fee_payments/{fee_payment_id}", response_model=schemas.FeePaymentRead, dependencies=[Depends(role_required([models.Role.admin, models.Role.teacher]))])
async def update_fee_payment(
    fee_payment_id: int,
    fee_payment_update: schemas.FeePaymentCreate, # Using create schema for update
    db: Session = Depends(get_db)
):
    fee_payment = db.query(models.FeePayment).filter(models.FeePayment.id == fee_payment_id).first()
    if not fee_payment:
        raise HTTPException(status_code=404, detail="Fee payment record not found")
    
    for field, value in fee_payment_update.dict(exclude_unset=True).items():
        setattr(fee_payment, field, value)
    
    db.add(fee_payment)
    db.commit()
    db.refresh(fee_payment)
    return fee_payment

@api_router.delete("/fee_payments/{fee_payment_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(role_required([models.Role.admin]))])
async def delete_fee_payment(
    fee_payment_id: int,
    db: Session = Depends(get_db)
):
    fee_payment = db.query(models.FeePayment).filter(models.FeePayment.id == fee_payment_id).first()
    if not fee_payment:
        raise HTTPException(status_code=404, detail="Fee payment record not found")
    
    db.delete(fee_payment)
    db.commit()
    return

# SchoolEvent Endpoints
@api_router.post("/school_events/", response_model=schemas.SchoolEventRead, dependencies=[Depends(role_required([models.Role.admin, models.Role.teacher]))])
async def create_school_event(
    school_event: schemas.SchoolEventCreate,
    db: Session = Depends(get_db)
):
    db_school_event = models.SchoolEvent(**school_event.dict())
    db.add(db_school_event)
    db.commit()
    db.refresh(db_school_event)
    return db_school_event

@api_router.get("/school_events/", response_model=List[schemas.SchoolEventRead], dependencies=[Depends(role_required([models.Role.admin, models.Role.teacher, models.Role.parent, models.Role.student]))])
async def list_school_events(db: Session = Depends(get_db)):
    school_events = db.query(models.SchoolEvent).all()
    return school_events

@api_router.get("/school_events/{school_event_id}", response_model=schemas.SchoolEventRead, dependencies=[Depends(role_required([models.Role.admin, models.Role.teacher, models.Role.parent, models.Role.student]))])
async def get_school_event(
    school_event_id: int,
    db: Session = Depends(get_db)
):
    school_event = db.query(models.SchoolEvent).filter(models.SchoolEvent.id == school_event_id).first()
    if not school_event:
        raise HTTPException(status_code=404, detail="School event not found")
    return school_event

@api_router.put("/school_events/{school_event_id}", response_model=schemas.SchoolEventRead, dependencies=[Depends(role_required([models.Role.admin, models.Role.teacher]))])
async def update_school_event(
    school_event_id: int,
    school_event_update: schemas.SchoolEventCreate, # Using create schema for update
    db: Session = Depends(get_db)
):
    school_event = db.query(models.SchoolEvent).filter(models.SchoolEvent.id == school_event_id).first()
    if not school_event:
        raise HTTPException(status_code=404, detail="School event not found")
    
    for field, value in school_event_update.dict(exclude_unset=True).items():
        setattr(school_event, field, value)
    
    db.add(school_event)
    db.commit()
    db.refresh(school_event)
    return school_event

@api_router.delete("/school_events/{school_event_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(role_required([models.Role.admin]))])
async def delete_school_event(
    school_event_id: int,
    db: Session = Depends(get_db)
):
    school_event = db.query(models.SchoolEvent).filter(models.SchoolEvent.id == school_event_id).first()
    if not school_event:
        raise HTTPException(status_code=404, detail="School event not found")
    
    db.delete(school_event)
    db.commit()
    return

# SchoolInfo Endpoints
@api_router.post("/school_info/", response_model=schemas.SchoolInfoRead, dependencies=[Depends(role_required([models.Role.admin]))])
async def create_school_info(
    school_info: schemas.SchoolInfoCreate,
    db: Session = Depends(get_db)
):
    db_school_info = models.SchoolInfo(**school_info.dict())
    db.add(db_school_info)
    db.commit()
    db.refresh(db_school_info)
    return db_school_info

@api_router.get("/school_info/", response_model=List[schemas.SchoolInfoRead], dependencies=[Depends(role_required([models.Role.admin, models.Role.teacher, models.Role.parent, models.Role.student]))])
async def list_school_info(db: Session = Depends(get_db)):
    school_info_records = db.query(models.SchoolInfo).all()
    return school_info_records

@api_router.get("/school_info/{school_info_id}", response_model=schemas.SchoolInfoRead, dependencies=[Depends(role_required([models.Role.admin, models.Role.teacher, models.Role.parent, models.Role.student]))])
async def get_school_info(
    school_info_id: int,
    db: Session = Depends(get_db)
):
    school_info = db.query(models.SchoolInfo).filter(models.SchoolInfo.id == school_info_id).first()
    if not school_info:
        raise HTTPException(status_code=404, detail="School info record not found")
    return school_info

@api_router.put("/school_info/{school_info_id}", response_model=schemas.SchoolInfoRead, dependencies=[Depends(role_required([models.Role.admin]))])
async def update_school_info(
    school_info_id: int,
    school_info_update: schemas.SchoolInfoCreate, # Using create schema for update
    db: Session = Depends(get_db)
):
    school_info = db.query(models.SchoolInfo).filter(models.SchoolInfo.id == school_info_id).first()
    if not school_info:
        raise HTTPException(status_code=404, detail="School info record not found")
    
    for field, value in school_info_update.dict(exclude_unset=True).items():
        setattr(school_info, field, value)
    
    db.add(school_info)
    db.commit()
    db.refresh(school_info)
    return school_info

@api_router.delete("/school_info/{school_info_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(role_required([models.Role.admin]))])
async def delete_school_info(
    school_info_id: int,
    db: Session = Depends(get_db)
):
    school_info = db.query(models.SchoolInfo).filter(models.SchoolInfo.id == school_info_id).first()
    if not school_info:
        raise HTTPException(status_code=404, detail="School info record not found")
    
    db.delete(school_info)
    db.commit()
    return

# SchoolTransaction Endpoints
@api_router.post("/school_transactions/", response_model=schemas.SchoolTransactionRead, dependencies=[Depends(role_required([models.Role.admin, models.Role.teacher]))])
async def create_school_transaction(
    school_transaction: schemas.SchoolTransactionCreate,
    db: Session = Depends(get_db)
):
    db_school_transaction = models.SchoolTransaction(**school_transaction.dict())
    db.add(db_school_transaction)
    db.commit()
    db.refresh(db_school_transaction)
    return db_school_transaction

@api_router.get("/school_transactions/", response_model=List[schemas.SchoolTransactionRead], dependencies=[Depends(role_required([models.Role.admin, models.Role.teacher]))])
async def list_school_transactions(db: Session = Depends(get_db)):
    school_transactions = db.query(models.SchoolTransaction).all()
    return school_transactions

@api_router.get("/school_transactions/{school_transaction_id}", response_model=schemas.SchoolTransactionRead, dependencies=[Depends(role_required([models.Role.admin, models.Role.teacher]))])
async def get_school_transaction(
    school_transaction_id: int,
    db: Session = Depends(get_db)
):
    school_transaction = db.query(models.SchoolTransaction).filter(models.SchoolTransaction.id == school_transaction_id).first()
    if not school_transaction:
        raise HTTPException(status_code=404, detail="School transaction record not found")
    return school_transaction

@api_router.put("/school_transactions/{school_transaction_id}", response_model=schemas.SchoolTransactionRead, dependencies=[Depends(role_required([models.Role.admin, models.Role.teacher]))])
async def update_school_transaction(
    school_transaction_id: int,
    school_transaction_update: schemas.SchoolTransactionCreate, # Using create schema for update
    db: Session = Depends(get_db)
):
    school_transaction = db.query(models.SchoolTransaction).filter(models.SchoolTransaction.id == school_transaction_id).first()
    if not school_transaction:
        raise HTTPException(status_code=404, detail="School transaction record not found")
    
    for field, value in school_transaction_update.dict(exclude_unset=True).items():
        setattr(school_transaction, field, value)
    
    db.add(school_transaction)
    db.commit()
    db.refresh(school_transaction)
    return school_transaction

@api_router.delete("/school_transactions/{school_transaction_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(role_required([models.Role.admin]))])
async def delete_school_transaction(
    school_transaction_id: int,
    db: Session = Depends(get_db)
):
    school_transaction = db.query(models.SchoolTransaction).filter(models.SchoolTransaction.id == school_transaction_id).first()
    if not school_transaction:
        raise HTTPException(status_code=404, detail="School transaction record not found")
    
    db.delete(school_transaction)
    db.commit()
    return

# Announcement Endpoints
@api_router.post("/announcements/", response_model=schemas.AnnouncementRead, dependencies=[Depends(role_required([models.Role.admin, models.Role.teacher]))])
async def create_announcement(
    announcement: schemas.AnnouncementCreate,
    db: Session = Depends(get_db)
):
    db_announcement = models.Announcement(**announcement.dict())
    db.add(db_announcement)
    db.commit()
    db.refresh(db_announcement)
    return db_announcement

@api_router.get("/announcements/", response_model=List[schemas.AnnouncementRead], dependencies=[Depends(role_required([models.Role.admin, models.Role.teacher, models.Role.parent, models.Role.student]))])
async def list_announcements(db: Session = Depends(get_db)):
    announcements = db.query(models.Announcement).all()
    return announcements

@api_router.get("/announcements/{announcement_id}", response_model=schemas.AnnouncementRead, dependencies=[Depends(role_required([models.Role.admin, models.Role.teacher, models.Role.parent, models.Role.student]))])
async def get_announcement(
    announcement_id: int,
    db: Session = Depends(get_db)
):
    announcement = db.query(models.Announcement).filter(models.Announcement.id == announcement_id).first()
    if not announcement:
        raise HTTPException(status_code=404, detail="Announcement not found")
    return announcement

@api_router.put("/announcements/{announcement_id}", response_model=schemas.AnnouncementRead, dependencies=[Depends(role_required([models.Role.admin, models.Role.teacher]))])
async def update_announcement(
    announcement_id: int,
    announcement_update: schemas.AnnouncementCreate, # Using create schema for update
    db: Session = Depends(get_db)
):
    announcement = db.query(models.Announcement).filter(models.Announcement.id == announcement_id).first()
    if not announcement:
        raise HTTPException(status_code=404, detail="Announcement not found")
    
    for field, value in announcement_update.dict(exclude_unset=True).items():
        setattr(announcement, field, value)
    
    db.add(announcement)
    db.commit()
    db.refresh(announcement)
    return announcement

@api_router.delete("/announcements/{announcement_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(role_required([models.Role.admin]))])
async def delete_announcement(
    announcement_id: int,
    db: Session = Depends(get_db)
):
    announcement = db.query(models.Announcement).filter(models.Announcement.id == announcement_id).first()
    if not announcement:
        raise HTTPException(status_code=404, detail="Announcement not found")
    
    db.delete(announcement)
    db.commit()
    return