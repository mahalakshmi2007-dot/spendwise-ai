"""
Expense API routes.

Provides full CRUD for expenses:
POST /expenses
GET /expenses
GET /expenses/{expense_id}
PUT /expenses/{expense_id}
DELETE /expenses/{expense_id}
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from .. import schemas, crud
from ..database import get_db

router = APIRouter(prefix="/expenses", tags=["Expenses"])


@router.post("", response_model=schemas.ExpenseOut, status_code=status.HTTP_201_CREATED)
def create_expense(expense: schemas.ExpenseCreate, db: Session = Depends(get_db)):
    """Create a new expense. Amount must be greater than 0 (enforced by schema)."""
    try:
        return crud.create_expense(db, expense)
    except SQLAlchemyError as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(exc)}")


@router.get("", response_model=List[schemas.ExpenseOut])
def list_expenses(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """List expenses, most recent first, with basic pagination."""
    try:
        return crud.get_expenses(db, skip=skip, limit=limit)
    except SQLAlchemyError as exc:
        raise HTTPException(status_code=500, detail=f"Database error: {str(exc)}")


@router.get("/{expense_id}", response_model=schemas.ExpenseOut)
def get_expense(expense_id: int, db: Session = Depends(get_db)):
    """Fetch a single expense by its ID."""
    db_expense = crud.get_expense(db, expense_id)
    if db_expense is None:
        raise HTTPException(
            status_code=404, detail=f"Expense with id {expense_id} not found"
        )
    return db_expense


@router.put("/{expense_id}", response_model=schemas.ExpenseOut)
def update_expense(
    expense_id: int, expense_update: schemas.ExpenseUpdate, db: Session = Depends(get_db)
):
    """Update one or more fields of an existing expense."""
    try:
        db_expense = crud.update_expense(db, expense_id, expense_update)
    except SQLAlchemyError as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(exc)}")

    if db_expense is None:
        raise HTTPException(
            status_code=404, detail=f"Expense with id {expense_id} not found"
        )
    return db_expense


@router.delete("/{expense_id}", status_code=status.HTTP_200_OK)
def delete_expense(expense_id: int, db: Session = Depends(get_db)):
    """Delete an expense by its ID."""
    try:
        deleted = crud.delete_expense(db, expense_id)
    except SQLAlchemyError as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(exc)}")

    if not deleted:
        raise HTTPException(
            status_code=404, detail=f"Expense with id {expense_id} not found"
        )
    return {"message": f"Expense {expense_id} deleted successfully"}
