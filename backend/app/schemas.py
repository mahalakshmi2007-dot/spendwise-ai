"""
Pydantic schemas for request validation and response serialization.
"""

from datetime import date, datetime
from typing import Optional, List, Dict

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Expense Schemas
# ---------------------------------------------------------------------------

class ExpenseBase(BaseModel):
    amount: float = Field(
        ...,
        gt=0,
        description="Amount must be greater than 0"
    )

    description: str = Field(
        ...,
        min_length=1,
        max_length=255
    )

    category: str = Field(
        ...,
        min_length=1,
        max_length=100
    )

    payment_method: str = Field(
        ...,
        min_length=1,
        max_length=50
    )

    expense_date: date


class ExpenseCreate(ExpenseBase):
    """Schema used when creating a new expense."""
    pass


class ExpenseUpdate(BaseModel):
    """Schema used when updating an expense."""

    amount: Optional[float] = Field(
        None,
        gt=0
    )

    description: Optional[str] = Field(
        None,
        min_length=1,
        max_length=255
    )

    category: Optional[str] = Field(
        None,
        min_length=1,
        max_length=100
    )

    payment_method: Optional[str] = Field(
        None,
        min_length=1,
        max_length=50
    )

    expense_date: Optional[date] = None


class ExpenseOut(ExpenseBase):
    """Schema returned to the client."""

    id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True


# ---------------------------------------------------------------------------
# Budget Schemas
# ---------------------------------------------------------------------------

class CategoryBudgetItem(BaseModel):
    """A single category budget limit."""

    category: str = Field(
        ...,
        min_length=1,
        max_length=100
    )

    limit_amount: float = Field(
        ...,
        gt=0
    )

    month: int = Field(
        ...,
        ge=1,
        le=12
    )

    year: int = Field(
        ...,
        ge=2000,
        le=2100
    )


class CategoryBudgetOut(CategoryBudgetItem):
    id: int

    class Config:
        from_attributes = True


class BudgetUpdate(BaseModel):
    """Update monthly budget and/or category limits."""

    monthly_budget: Optional[float] = Field(
        None,
        ge=0
    )

    category_limits: Optional[
        List[CategoryBudgetItem]
    ] = None


class BudgetOut(BaseModel):
    """Current budget state."""

    monthly_budget: float

    category_limits: List[
        CategoryBudgetOut
    ] = []

    class Config:
        from_attributes = True


# ---------------------------------------------------------------------------
# Dashboard Schemas
# ---------------------------------------------------------------------------

class DashboardOut(BaseModel):
    """Dashboard summary."""

    total_monthly_spending: float
    today_spending: float
    remaining_budget: float
    transaction_count: int

    spending_by_category: Dict[
        str,
        float
    ]

    recent_transactions: List[
        ExpenseOut
    ]


# ---------------------------------------------------------------------------
# Machine Learning Schemas
# ---------------------------------------------------------------------------

class TrainResponse(BaseModel):
    """Response returned after training the category model."""

    trained_on_samples: int
    distinct_categories: int
    training_accuracy: float


class CategoryPredictionRequest(BaseModel):
    """Request for category prediction."""

    description: str = Field(
        ...,
        min_length=1,
        max_length=255
    )


class CategoryPredictionOut(BaseModel):
    """Category prediction response."""

    predicted_category: str
    confidence: float
    probabilities: Dict[
        str,
        float
    ]


class MonthlyTotal(BaseModel):
    """Monthly spending total."""

    year: int
    month: int
    total: float


class ForecastOut(BaseModel):
    """Next month's spending forecast."""

    history: List[
        MonthlyTotal
    ]

    predicted_next_month_total: float

    trend: str

    monthly_change_rate: Optional[
        float
    ] = None

    note: Optional[
        str
    ] = None


class AnomalyOut(BaseModel):
    """Unusual expense detected by Isolation Forest."""

    expense_id: int
    description: str
    category: str
    amount: float
    expense_date: str
    anomaly_score: float


class InsightsOut(BaseModel):
    """AI-generated spending insights."""

    insights: List[str]