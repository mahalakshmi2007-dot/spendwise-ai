"""
Unusual spending detection using Isolation Forest (Part 2).

Flags individual expenses whose amount looks unusual compared to the
rest of the user's expense history, taking into account what's normal
for that expense's category.
"""

from typing import List, Dict

import numpy as np
from sklearn.ensemble import IsolationForest
from sqlalchemy.orm import Session

from .. import models

MIN_EXPENSES_REQUIRED = 5


def detect_anomalies(db: Session, user_id: int = 1, contamination: float = 0.1) -> List[Dict]:
    """
    Run Isolation Forest over the user's expenses and return the ones
    flagged as unusual, sorted by how unusual they are (most unusual first).

    Features used per expense:
      - amount
      - day of the month (captures unusual timing)
      - that expense's category average amount (lets the model judge
        "high for this category", not just "high overall")
    """
    expenses = (
        db.query(models.Expense)
        .filter(models.Expense.user_id == user_id)
        .order_by(models.Expense.expense_date.asc())
        .all()
    )

    if len(expenses) < MIN_EXPENSES_REQUIRED:
        raise ValueError(
            f"Not enough expenses to run anomaly detection. "
            f"Found {len(expenses)}, need at least {MIN_EXPENSES_REQUIRED}."
        )

    category_totals: Dict[str, List[float]] = {}
    for e in expenses:
        category_totals.setdefault(e.category, []).append(e.amount)
    category_avg = {cat: sum(vals) / len(vals) for cat, vals in category_totals.items()}

    features = []
    for e in expenses:
        features.append([
            e.amount,
            e.expense_date.day,
            category_avg[e.category],
        ])

    X = np.array(features)

    model = IsolationForest(
        n_estimators=200,
        contamination=contamination,
        random_state=42,
    )
    model.fit(X)

    # decision_function: higher = more normal, lower/negative = more unusual
    scores = model.decision_function(X)
    predictions = model.predict(X)  # -1 = anomaly, 1 = normal

    results = []
    for e, score, pred in zip(expenses, scores, predictions):
        if pred == -1:
            results.append({
                "expense_id": e.id,
                "description": e.description,
                "category": e.category,
                "amount": e.amount,
                "expense_date": e.expense_date.isoformat(),
                "anomaly_score": round(float(score), 4),
            })

    results.sort(key=lambda r: r["anomaly_score"])
    return results
