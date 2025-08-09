from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app import models, schemas
from app.database import get_db
from app.routes import get_current_user
from datetime import datetime, timedelta

transaction_router = APIRouter()

@transaction_router.post("/transactions", response_model=schemas.Transaction)
def create_transaction(transaction: schemas.TransactionCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    db_transaction = models.Transaction(**transaction.dict(), owner_id=current_user.id)
    if not db_transaction.date_created:
        db_transaction.date_created = datetime.utcnow()
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    return db_transaction

@transaction_router.get("/transactions", response_model=List[schemas.Transaction])
def read_transactions(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    transactions = db.query(models.Transaction).filter(models.Transaction.owner_id == current_user.id).offset(skip).limit(limit).all()
    return transactions

@transaction_router.get("/transactions/{transaction_id}", response_model=schemas.Transaction)
def read_transaction(transaction_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    db_transaction = db.query(models.Transaction).filter(models.Transaction.id == transaction_id, models.Transaction.owner_id == current_user.id).first()
    if db_transaction is None:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return db_transaction

@transaction_router.put("/transactions/{transaction_id}", response_model=schemas.Transaction)
def update_transaction(transaction_id: int, transaction: schemas.TransactionCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    db_transaction = db.query(models.Transaction).filter(models.Transaction.id == transaction_id, models.Transaction.owner_id == current_user.id).first()
    if db_transaction is None:
        raise HTTPException(status_code=404, detail="Transaction not found")
    for var, value in vars(transaction).items():
        setattr(db_transaction, var, value) if value else None
    db.commit()
    db.refresh(db_transaction)
    return db_transaction

@transaction_router.delete("/transactions/{transaction_id}", response_model=schemas.Transaction)
def delete_transaction(transaction_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    db_transaction = db.query(models.Transaction).filter(models.Transaction.id == transaction_id, models.Transaction.owner_id == current_user.id).first()
    if db_transaction is None:
        raise HTTPException(status_code=404, detail="Transaction not found")
    db.delete(db_transaction)
    db.commit()
    return db_transaction

@transaction_router.get("/summary")
def get_summary(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    today = datetime.utcnow().date()
    start_of_week = today - timedelta(days=today.weekday())
    start_of_month = today.replace(day=1)

    transactions = db.query(models.Transaction).filter(models.Transaction.owner_id == current_user.id).all()

    total_income = sum(t.price for t in transactions if t.price > 0)
    total_expense = sum(t.price for t in transactions if t.price < 0)

    daily_transactions = [t for t in transactions if t.date_created.date() == today]
    weekly_transactions = [t for t in transactions if t.date_created.date() >= start_of_week]
    monthly_transactions = [t for t in transactions if t.date_created.date() >= start_of_month]

    return {
        "total_income": total_income,
        "total_expense": total_expense,
        "net_flow": total_income + total_expense,
        "daily_summary": {
            "count": len(daily_transactions),
            "income": sum(t.price for t in daily_transactions if t.price > 0),
            "expense": sum(t.price for t in daily_transactions if t.price < 0),
        },
        "weekly_summary": {
            "count": len(weekly_transactions),
            "income": sum(t.price for t in weekly_transactions if t.price > 0),
            "expense": sum(t.price for t in weekly_transactions if t.price < 0),
        },
        "monthly_summary": {
            "count": len(monthly_transactions),
            "income": sum(t.price for t in monthly_transactions if t.price > 0),
            "expense": sum(t.price for t in monthly_transactions if t.price < 0),
        },
    }