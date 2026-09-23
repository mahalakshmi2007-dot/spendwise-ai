"""
Monthly spending forecast (Part 2).

Aggregates historical monthly totals from the expenses table and fits
a simple linear regression (month index -> total spend) to project
next month's spending. This is a lightweight, explainable approach
that works well even with a small amount of personal-finance history.
"""

from collections import defaultdict
from typing import List, Dict

import numpy as np
from sklearn.linear_model import LinearRegression
from sqlalchemy.orm import Session

from .. import models


def _monthly_totals(db: Session, user_id: int = 1) -> List[Dict]:
    """
    Group all of a user's expenses by (year, month) and sum their
    amounts, returned in chronological order.
    """
    expenses = (
        db.query(models.Expense)
        .filter(models.Expense.user_id == user_id)
        .all()
    )

    totals = defaultdict(float)
    for e in expenses:
        key = (e.expense_date.year, e.expense_date.month)
        totals[key] += e.amount

    sorted_keys = sorted(totals.keys())
    return [
        {"year": y, "month": m, "total": round(totals[(y, m)], 2)}
        for (y, m) in sorted_keys
    ]


def forecast_next_month(db: Session, user_id: int = 1) -> dict:
    """
    Predict next month's total spending.

    - With 2+ months of history: fits a LinearRegression model on
      month index vs. total spend and extrapolates one step forward.
    - With exactly 1 month of history: forecasts the same amount,
      since there isn't enough data yet to detect a trend.
    - With 0 months of history: raises ValueError.
    """
    history = _monthly_totals(db, user_id)

    if len(history) == 0:
        raise ValueError("No expense history available to forecast from.")

    if len(history) == 1:
        only_month_total = history[0]["total"]
        return {
            "history": history,
            "predicted_next_month_total": round(only_month_total, 2),
            "trend": "insufficient_data",
            "monthly_change_rate": None,
            "note": "Only one month of data available; forecast assumes similar spending continues.",
        }

    X = np.arange(len(history)).reshape(-1, 1)
    y = np.array([h["total"] for h in history])

    model = LinearRegression()
    model.fit(X, y)

    next_index = np.array([[len(history)]])
    prediction = float(model.predict(next_index)[0])
    prediction = max(prediction, 0.0)  # spending can never be negative

    slope = float(model.coef_[0])
    if slope > 1.0:
        trend = "increasing"
    elif slope < -1.0:
        trend = "decreasing"
    else:
        trend = "stable"

    return {
        "history": history,
        "predicted_next_month_total": round(prediction, 2),
        "trend": trend,
        "monthly_change_rate": round(slope, 2),
        "note": None,
    }
