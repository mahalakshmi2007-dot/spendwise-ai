"""
CRUD and aggregation functions for SpendWise AI.

This module contains all direct database operations so that
route handlers stay thin and focused on HTTP concerns.

NOTE: Authentication is not part of this backend part yet, so all
operations run against a single default demo user (id=1). A real
auth system (login, JWT, multiple users) can be added in a later part.
"""

from datetime import date
from typing import List, Optional

from sqlalchemy import func, extract
from sqlalchemy.orm import Session

from . import models, schemas

DEFAULT_USER_ID = 1


# ---------------------------------------------------------------------------
# User helpers
# ---------------------------------------------------------------------------

def get_or_create_default_user(db: Session) -> models.User:
    """Fetch the default demo user, creating it if it doesn't exist yet."""
    user = db.query(models.User).filter(models.User.id == DEFAULT_USER_ID).first()
    if user is None:
        user = models.User(
            id=DEFAULT_USER_ID,
            name="Demo User",
            email="demo@spendwise.ai",
            password_hash="not_set",
            monthly_budget=0.0,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    return user


# ---------------------------------------------------------------------------
# Expense CRUD
# ---------------------------------------------------------------------------

def create_expense(
    db: Session, expense: schemas.ExpenseCreate, user_id: int = DEFAULT_USER_ID
) -> models.Expense:
    # Ensure the owning user exists before inserting the expense.
    get_or_create_default_user(db)

    db_expense = models.Expense(
        user_id=user_id,
        amount=expense.amount,
        description=expense.description,
        category=expense.category,
        payment_method=expense.payment_method,
        expense_date=expense.expense_date,
    )
    db.add(db_expense)
    db.commit()
    db.refresh(db_expense)
    return db_expense


def get_expenses(
    db: Session, user_id: int = DEFAULT_USER_ID, skip: int = 0, limit: int = 100
) -> List[models.Expense]:
    return (
        db.query(models.Expense)
        .filter(models.Expense.user_id == user_id)
        .order_by(models.Expense.expense_date.desc(), models.Expense.id.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_expense(
    db: Session, expense_id: int, user_id: int = DEFAULT_USER_ID
) -> Optional[models.Expense]:
    return (
        db.query(models.Expense)
        .filter(models.Expense.id == expense_id, models.Expense.user_id == user_id)
        .first()
    )


def update_expense(
    db: Session,
    expense_id: int,
    expense_update: schemas.ExpenseUpdate,
    user_id: int = DEFAULT_USER_ID,
) -> Optional[models.Expense]:
    db_expense = get_expense(db, expense_id, user_id)
    if db_expense is None:
        return None

    update_data = expense_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_expense, field, value)

    db.commit()
    db.refresh(db_expense)
    return db_expense


def delete_expense(
    db: Session, expense_id: int, user_id: int = DEFAULT_USER_ID
) -> bool:
    db_expense = get_expense(db, expense_id, user_id)
    if db_expense is None:
        return False

    db.delete(db_expense)
    db.commit()
    return True


# ---------------------------------------------------------------------------
# Budget CRUD
# ---------------------------------------------------------------------------

def set_monthly_budget(
    db: Session, amount: float, user_id: int = DEFAULT_USER_ID
) -> models.User:
    user = get_or_create_default_user(db)
    user.monthly_budget = amount
    db.commit()
    db.refresh(user)
    return user


def upsert_category_budget(
    db: Session, item: schemas.CategoryBudgetItem, user_id: int = DEFAULT_USER_ID
) -> models.Budget:
    """
    Insert a new category budget, or update the limit if one already
    exists for that category/month/year combination.
    """
    db_budget = (
        db.query(models.Budget)
        .filter(
            models.Budget.user_id == user_id,
            models.Budget.category == item.category,
            models.Budget.month == item.month,
            models.Budget.year == item.year,
        )
        .first()
    )

    if db_budget:
        db_budget.limit_amount = item.limit_amount
    else:
        db_budget = models.Budget(
            user_id=user_id,
            category=item.category,
            limit_amount=item.limit_amount,
            month=item.month,
            year=item.year,
        )
        db.add(db_budget)

    db.commit()
    db.refresh(db_budget)
    return db_budget


def get_category_budgets(
    db: Session, user_id: int = DEFAULT_USER_ID
) -> List[models.Budget]:
    return db.query(models.Budget).filter(models.Budget.user_id == user_id).all()


# ---------------------------------------------------------------------------
# Dashboard Aggregations
# ---------------------------------------------------------------------------

def get_dashboard_data(db: Session, user_id: int = DEFAULT_USER_ID) -> dict:
    """
    Compute all dashboard figures directly from the database.
    Nothing here is hard-coded — every value reflects current data.
    """
    user = get_or_create_default_user(db)
    today = date.today()

    total_monthly_spending = (
        db.query(func.coalesce(func.sum(models.Expense.amount), 0.0))
        .filter(
            models.Expense.user_id == user_id,
            extract("month", models.Expense.expense_date) == today.month,
            extract("year", models.Expense.expense_date) == today.year,
        )
        .scalar()
    )

    today_spending = (
        db.query(func.coalesce(func.sum(models.Expense.amount), 0.0))
        .filter(
            models.Expense.user_id == user_id,
            models.Expense.expense_date == today,
        )
        .scalar()
    )

    transaction_count = (
        db.query(func.count(models.Expense.id))
        .filter(
            models.Expense.user_id == user_id,
            extract("month", models.Expense.expense_date) == today.month,
            extract("year", models.Expense.expense_date) == today.year,
        )
        .scalar()
    )

    category_rows = (
        db.query(
            models.Expense.category,
            func.coalesce(func.sum(models.Expense.amount), 0.0),
        )
        .filter(
            models.Expense.user_id == user_id,
            extract("month", models.Expense.expense_date) == today.month,
            extract("year", models.Expense.expense_date) == today.year,
        )
        .group_by(models.Expense.category)
        .all()
    )
    spending_by_category = {category: float(total) for category, total in category_rows}

    recent_transactions = (
        db.query(models.Expense)
        .filter(models.Expense.user_id == user_id)
        .order_by(models.Expense.created_at.desc())
        .limit(5)
        .all()
    )

    remaining_budget = float(user.monthly_budget) - float(total_monthly_spending)

    return {
        "total_monthly_spending": float(total_monthly_spending),
        "today_spending": float(today_spending),
        "remaining_budget": remaining_budget,
        "transaction_count": int(transaction_count),
        "spending_by_category": spending_by_category,
        "recent_transactions": recent_transactions,
    }
