"""
Budget API routes.

Provides:
GET /budget  - fetch the current monthly budget and category limits
PUT /budget  - update the monthly budget and/or category limits
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from .. import schemas, crud
from ..database import get_db

router = APIRouter(prefix="/budget", tags=["Budget"])


@router.get("", response_model=schemas.BudgetOut)
def get_budget(db: Session = Depends(get_db)):
    """Return the current monthly budget and all category limits."""
    try:
        user = crud.get_or_create_default_user(db)
        category_limits = crud.get_category_budgets(db)
    except SQLAlchemyError as exc:
        raise HTTPException(status_code=500, detail=f"Database error: {str(exc)}")

    return schemas.BudgetOut(
        monthly_budget=user.monthly_budget,
        category_limits=category_limits,
    )


@router.put("", response_model=schemas.BudgetOut)
def update_budget(budget_update: schemas.BudgetUpdate, db: Session = Depends(get_db)):
    """
    Update the overall monthly budget and/or one or more category limits.
    Both fields are optional — send only what you want to change.
    """
    if budget_update.monthly_budget is None and not budget_update.category_limits:
        raise HTTPException(
            status_code=400,
            detail="Provide at least monthly_budget or category_limits to update.",
        )

    try:
        if budget_update.monthly_budget is not None:
            crud.set_monthly_budget(db, budget_update.monthly_budget)

        if budget_update.category_limits:
            for item in budget_update.category_limits:
                crud.upsert_category_budget(db, item)

        user = crud.get_or_create_default_user(db)
        category_limits = crud.get_category_budgets(db)
    except SQLAlchemyError as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(exc)}")

    return schemas.BudgetOut(
        monthly_budget=user.monthly_budget,
        category_limits=category_limits,
    )
