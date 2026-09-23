"""
Machine Learning API routes for SpendWise AI (Part 2).

POST /ml/train              - (re)train the category prediction model
POST /ml/predict-category   - predict a category for a new description
GET  /ml/forecast           - forecast next month's total spending
GET  /ml/anomalies          - list unusual expenses
GET  /ml/insights           - generate plain-English insights
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import schemas
from ..database import get_db
from ..ml import category_predictor, forecasting, anomaly_detector, insights

router = APIRouter(prefix="/ml", tags=["Machine Learning"])


@router.post("/train", response_model=schemas.TrainResponse)
def train_model(db: Session = Depends(get_db)):
    """Train (or retrain) the TF-IDF + Logistic Regression category model
    on every expense currently stored in the database."""
    try:
        stats = category_predictor.train_category_model(db)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return stats


@router.post("/predict-category", response_model=schemas.CategoryPredictionOut)
def predict_category(payload: schemas.CategoryPredictionRequest):
    """Predict the most likely category for a new expense description."""
    try:
        result = category_predictor.predict_category(payload.description)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return result


@router.get("/forecast", response_model=schemas.ForecastOut)
def get_forecast(db: Session = Depends(get_db)):
    """Forecast next month's total spending based on monthly history."""
    try:
        return forecasting.forecast_next_month(db)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.get("/anomalies", response_model=List[schemas.AnomalyOut])
def get_anomalies(db: Session = Depends(get_db)):
    """Detect unusual expenses using Isolation Forest."""
    try:
        return anomaly_detector.detect_anomalies(db)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.get("/insights", response_model=schemas.InsightsOut)
def get_insights(db: Session = Depends(get_db)):
    """Generate plain-English insights from dashboard, forecast, and anomaly data."""
    try:
        text_insights = insights.generate_insights(db)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to generate insights: {str(exc)}")
    return {"insights": text_insights}
