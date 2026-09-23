# SpendWise AI — Part 2 Add-on (Machine Learning)

This package adds real, local, free ML features on top of your working
Part 1 backend. Nothing here calls any paid API — everything runs on
your own machine using scikit-learn.

## What's inside this ZIP

```
app/
├── ml/
│   ├── __init__.py
│   ├── category_predictor.py   # TF-IDF + Logistic Regression
│   ├── forecasting.py          # Linear Regression monthly forecast
│   ├── anomaly_detector.py     # Isolation Forest anomaly detection
│   └── insights.py             # Combines the above into plain-English insights
├── routes/
│   └── ml.py                   # New /ml/* API endpoints
├── main.py                     # UPDATED — now also registers the ml router
└── schemas.py                  # UPDATED — now also includes ML request/response schemas
requirements.txt                # UPDATED — now also includes scikit-learn, numpy, joblib
```

`app/ml/`, `app/routes/ml.py` are **brand-new files**.
`app/main.py`, `app/schemas.py`, and `requirements.txt` are **updated versions**
of your existing Part 1 files — your original Expense/Dashboard/Budget code
inside them is unchanged; only the ML additions are new.

## How to merge this into your project

Copy everything inside this ZIP's `app/` folder and `requirements.txt`
straight into your existing `spendwise-ai\backend` folder, allowing it
to overwrite `app/main.py`, `app/schemas.py`, and `requirements.txt`.
This will not touch `models.py`, `crud.py`, `database.py`, or any of
your `routes/expenses.py`, `routes/dashboard.py`, `routes/budget.py`,
or your existing `spendwise.db` database file.

## New API endpoints

| Method | Path | What it does |
|---|---|---|
| POST | `/ml/train` | Trains the TF-IDF + Logistic Regression category model on your current expenses |
| POST | `/ml/predict-category` | Predicts a category for a new expense description |
| GET | `/ml/forecast` | Forecasts next month's total spending |
| GET | `/ml/anomalies` | Lists expenses flagged as unusual by Isolation Forest |
| GET | `/ml/insights` | Generates plain-English insights from your real data |

You must call `POST /ml/train` at least once before `POST /ml/predict-category`
will work — that's what creates the saved model file.
