"""
Seed script for SpendWise AI.

Creates a demo user and inserts realistic sample expenses and
category budgets for local testing.

Run with: python seed.py
"""

import os
import sys
from datetime import date, timedelta

# Ensure the "app" package is importable when running this script directly.
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal, Base, engine
from app import models

DEMO_USER_ID = 1


def seed():
    # Make sure tables exist before seeding.
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    try:
        # ---------------- User ----------------
        user = db.query(models.User).filter(models.User.id == DEMO_USER_ID).first()
        if user is None:
            user = models.User(
                id=DEMO_USER_ID,
                name="Mahalakshmi S",
                email="demo@spendwise.ai",
                password_hash="not_set",
                monthly_budget=15000.0,
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            print("Created demo user (id=1).")
        else:
            print("Demo user already exists. Skipping user creation.")

        # ---------------- Expenses ----------------
        existing_expense_count = (
            db.query(models.Expense)
            .filter(models.Expense.user_id == DEMO_USER_ID)
            .count()
        )

        if existing_expense_count > 0:
            print(f"{existing_expense_count} expenses already exist. Skipping expense seeding.")
        else:
            today = date.today()

            sample_expenses = [
                {"amount": 350.0, "description": "Swiggy dinner", "category": "Food", "payment_method": "UPI", "days_ago": 0},
                {"amount": 180.0, "description": "Uber ride", "category": "Transport", "payment_method": "UPI", "days_ago": 1},
                {"amount": 2499.0, "description": "Amazon shoes", "category": "Shopping", "payment_method": "Credit Card", "days_ago": 2},
                {"amount": 120.0, "description": "College notebook", "category": "Education", "payment_method": "Cash", "days_ago": 3},
                {"amount": 1450.0, "description": "Electricity bill", "category": "Utilities", "payment_method": "Debit Card", "days_ago": 4},
                {"amount": 250.0, "description": "Movie ticket", "category": "Entertainment", "payment_method": "UPI", "days_ago": 5},
                {"amount": 300.0, "description": "Medicine", "category": "Health", "payment_method": "Cash", "days_ago": 6},
                {"amount": 1600.0, "description": "Grocery shopping", "category": "Groceries", "payment_method": "Debit Card", "days_ago": 7},
                {"amount": 220.0, "description": "Swiggy lunch", "category": "Food", "payment_method": "UPI", "days_ago": 8},
                {"amount": 90.0, "description": "Auto ride", "category": "Transport", "payment_method": "Cash", "days_ago": 9},
                {"amount": 599.0, "description": "Netflix subscription", "category": "Entertainment", "payment_method": "Credit Card", "days_ago": 10},
                {"amount": 850.0, "description": "College fest ticket", "category": "Education", "payment_method": "UPI", "days_ago": 11},
                {"amount": 450.0, "description": "Pharmacy essentials", "category": "Health", "payment_method": "Debit Card", "days_ago": 12},
                {"amount": 1200.0, "description": "Amazon books", "category": "Shopping", "payment_method": "Credit Card", "days_ago": 13},
                {"amount": 300.0, "description": "Mobile recharge", "category": "Utilities", "payment_method": "UPI", "days_ago": 14},
                {"amount": 400.0, "description": "Swiggy dinner", "category": "Food", "payment_method": "UPI", "days_ago": 15},
                {"amount": 150.0, "description": "Uber ride", "category": "Transport", "payment_method": "UPI", "days_ago": 16},
                {"amount": 2200.0, "description": "Grocery shopping", "category": "Groceries", "payment_method": "Debit Card", "days_ago": 18},
                {"amount": 199.0, "description": "Movie ticket", "category": "Entertainment", "payment_method": "UPI", "days_ago": 20},
                {"amount": 500.0, "description": "Medicine", "category": "Health", "payment_method": "Cash", "days_ago": 22},
            ]

            for item in sample_expenses:
                expense_date = today - timedelta(days=item["days_ago"])
                db_expense = models.Expense(
                    user_id=DEMO_USER_ID,
                    amount=item["amount"],
                    description=item["description"],
                    category=item["category"],
                    payment_method=item["payment_method"],
                    expense_date=expense_date,
                )
                db.add(db_expense)

            db.commit()
            print(f"Inserted {len(sample_expenses)} sample expenses.")

        # ---------------- Category Budgets ----------------
        existing_budget_count = (
            db.query(models.Budget)
            .filter(models.Budget.user_id == DEMO_USER_ID)
            .count()
        )

        if existing_budget_count > 0:
            print(f"{existing_budget_count} category budgets already exist. Skipping budget seeding.")
        else:
            today = date.today()
            sample_budgets = [
                {"category": "Food", "limit_amount": 3000.0},
                {"category": "Shopping", "limit_amount": 4000.0},
                {"category": "Transport", "limit_amount": 1500.0},
                {"category": "Groceries", "limit_amount": 5000.0},
            ]
            for item in sample_budgets:
                db_budget = models.Budget(
                    user_id=DEMO_USER_ID,
                    category=item["category"],
                    limit_amount=item["limit_amount"],
                    month=today.month,
                    year=today.year,
                )
                db.add(db_budget)

            db.commit()
            print(f"Inserted {len(sample_budgets)} sample category budgets.")

        print("Seeding complete.")

    finally:
        db.close()


if __name__ == "__main__":
    seed()
