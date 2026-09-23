"""
AI insight generation (Part 2).

Turns the outputs of the dashboard, forecasting, and anomaly-detection
modules into short, plain-English insights. Every insight is computed
directly from real numbers in the database — none of these strings
are canned or hard-coded to a scenario.
"""

from typing import List

from sqlalchemy.orm import Session

from .. import crud
from . import forecasting, anomaly_detector


def generate_insights(db: Session, user_id: int = 1) -> List[str]:
    insights: List[str] = []

    dashboard = crud.get_dashboard_data(db, user_id)

    total = dashboard["total_monthly_spending"]
    remaining = dashboard["remaining_budget"]
    tx_count = dashboard["transaction_count"]
    by_category = dashboard["spending_by_category"]

    # --- Budget-based insight ---
    if remaining < 0:
        insights.append(
            f"You have exceeded your monthly budget by Rs. {abs(remaining):,.2f}."
        )
    elif total > 0:
        budget_total = total + remaining
        if budget_total > 0:
            percent_used = (total / budget_total) * 100
            insights.append(
                f"You have spent Rs. {total:,.2f} so far this month, "
                f"which is {percent_used:.1f}% of your monthly budget. "
                f"Rs. {remaining:,.2f} remains."
            )

    # --- Category insight ---
    if by_category:
        top_category = max(by_category, key=by_category.get)
        top_amount = by_category[top_category]
        insights.append(
            f"Your highest spending category this month is '{top_category}' "
            f"at Rs. {top_amount:,.2f}."
        )

    # --- Transaction volume insight ---
    if tx_count > 0:
        avg_transaction = total / tx_count
        insights.append(
            f"You made {tx_count} transaction(s) this month, "
            f"averaging Rs. {avg_transaction:,.2f} per transaction."
        )

    # --- Forecast insight ---
    try:
        forecast = forecasting.forecast_next_month(db, user_id)
        predicted = forecast["predicted_next_month_total"]
        trend = forecast["trend"]
        if trend == "increasing":
            insights.append(
                f"Your spending trend is increasing. "
                f"Next month is projected at Rs. {predicted:,.2f}."
            )
        elif trend == "decreasing":
            insights.append(
                f"Your spending trend is decreasing. "
                f"Next month is projected at Rs. {predicted:,.2f}."
            )
        else:
            insights.append(
                f"Your spending has been fairly stable. "
                f"Next month is projected at around Rs. {predicted:,.2f}."
            )
    except ValueError:
        pass  # not enough history yet

    # --- Anomaly insight ---
    try:
        anomalies = anomaly_detector.detect_anomalies(db, user_id)
        if anomalies:
            worst = anomalies[0]
            insights.append(
                f"{len(anomalies)} unusual expense(s) detected. "
                f"The most unusual is '{worst['description']}' "
                f"(Rs. {worst['amount']:,.2f} in {worst['category']} on {worst['expense_date']})."
            )
    except ValueError:
        pass  # not enough data yet

    if not insights:
        insights.append("Add a few more expenses to start generating insights.")

    return insights
