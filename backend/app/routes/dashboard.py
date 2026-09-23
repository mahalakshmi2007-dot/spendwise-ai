"""
Dashboard API routes.

Provides GET /dashboard, returning live calculated figures
from the database — nothing is hard-coded.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from .. import schemas, crud
from ..database import get_db

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("", response_model=schemas.DashboardOut)
def get_dashboard(db: Session = Depends(get_db)):
    """Return total monthly spending, today's spending, remaining budget,
    transaction count, spending by category, and recent transactions."""
    try:
        return crud.get_dashboard_data(db)
    except SQLAlchemyError as exc:
        raise HTTPException(status_code=500, detail=f"Database error: {str(exc)}")
