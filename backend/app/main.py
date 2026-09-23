"""
SpendWise AI - FastAPI application entry point.

Wires together the database, routers, CORS configuration,
and global error handling.
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from .database import Base, engine
from .routes import expenses, dashboard, budget, ml

# Create all tables on startup if they don't already exist.
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="SpendWise AI",
    description="Backend API for SpendWise AI - a personal expense intelligence application.",
    version="0.2.0",
)

# Allow the future React frontend (running on Vite's default port) to call this API.
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers.
app.include_router(expenses.router)
app.include_router(dashboard.router)
app.include_router(budget.router)
app.include_router(ml.router)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Return a clear 422 response when request data fails validation
    (e.g. missing required fields, invalid dates, amount <= 0)."""
    return JSONResponse(
        status_code=422,
        content={"detail": "Invalid request data.", "errors": exc.errors()},
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    """Catch-all handler so unexpected errors return clean JSON instead of a raw traceback."""
    return JSONResponse(
        status_code=500,
        content={"detail": f"Unexpected server error: {str(exc)}"},
    )


@app.get("/")
def root():
    """Simple health-check / welcome route."""
    return {"message": "SpendWise AI backend is running. Visit /docs for API documentation."}
