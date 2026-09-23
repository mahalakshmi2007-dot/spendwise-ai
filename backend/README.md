# SpendWise AI — Backend (Part 1)

Personal expense intelligence backend built with FastAPI, SQLAlchemy, and SQLite.

This part implements only the backend foundation: database models, the
Expense API, the Dashboard API, and the Budget API. No frontend and no
machine learning are included yet — those come in later parts.

## Tech Stack
- Python 3
- FastAPI
- SQLAlchemy
- SQLite
- Pydantic
- Uvicorn

## Project Structure
```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py          # FastAPI app, CORS, routers, error handlers
│   ├── database.py       # SQLAlchemy engine/session setup
│   ├── models.py         # User, Expense, Budget ORM models
│   ├── schemas.py        # Pydantic request/response schemas
│   ├── crud.py           # Database operations and dashboard aggregations
│   └── routes/
│       ├── __init__.py
│       ├── expenses.py   # Expense CRUD endpoints
│       ├── dashboard.py  # Dashboard summary endpoint
│       └── budget.py     # Budget endpoints
├── seed.py                # Inserts demo user + sample expenses/budgets
├── requirements.txt
├── .env.example
└── README.md
```

## Database
SQLite file: `spendwise.db` (created automatically on first run in the
`backend/` folder).

Tables:
- **users** — id, name, email, password_hash, monthly_budget, created_at
- **expenses** — id, user_id, amount, description, category, payment_method, expense_date, created_at
- **budgets** — id, user_id, category, limit_amount, month, year

> Note: This part does not include login/authentication endpoints. All
> data operations run against a single demo user (id=1), which is
> created automatically the first time it's needed. Multi-user auth can
> be added in a future part.

## API Endpoints

### Expenses
| Method | Path | Description |
|---|---|---|
| POST | `/expenses` | Create a new expense |
| GET | `/expenses` | List expenses (supports `skip` and `limit` query params) |
| GET | `/expenses/{expense_id}` | Get one expense |
| PUT | `/expenses/{expense_id}` | Update an expense |
| DELETE | `/expenses/{expense_id}` | Delete an expense |

### Dashboard
| Method | Path | Description |
|---|---|---|
| GET | `/dashboard` | Total monthly spending, today's spending, remaining budget, transaction count, spending by category, recent transactions |

### Budget
| Method | Path | Description |
|---|---|---|
| GET | `/budget` | Get current monthly budget and category limits |
| PUT | `/budget` | Update monthly budget and/or category limits |

Full interactive documentation is available at **`/docs`** (Swagger UI)
once the server is running.

## CORS
Configured to allow requests from common local frontend dev ports:
`http://localhost:5173`, `http://127.0.0.1:5173`, `http://localhost:3000`,
`http://127.0.0.1:3000`.

## Error Handling
- Invalid amount (≤ 0) → `422 Unprocessable Entity`
- Missing required fields → `422 Unprocessable Entity`
- Invalid dates → `422 Unprocessable Entity`
- Expense not found → `404 Not Found`
- Database errors → `500 Internal Server Error` with a clear message
