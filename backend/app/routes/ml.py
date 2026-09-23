"""
Machine Learning API routes for SpendWise AI.
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
    try:
        stats = category_predictor.train_category_model(db)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return stats


@router.post(
    "/predict-category",
    response_model=schemas.CategoryPredictionOut,
)
def predict_category(payload: schemas.CategoryPredictionRequest):
    try:
        result = category_predictor.predict_category(payload.description)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return result


@router.get("/forecast", response_model=schemas.ForecastOut)
def get_forecast(db: Session = Depends(get_db)):
    try:
        return forecasting.forecast_next_month(db)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.get(
    "/anomalies",
    response_model=List[schemas.AnomalyOut],
)
def get_anomalies(db: Session = Depends(get_db)):
    try:
        return anomaly_detector.detect_anomalies(db)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.get("/insights", response_model=schemas.InsightsOut)
def get_insights(db: Session = Depends(get_db)):
    try:
        text_insights = insights.generate_insights(db)
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate insights: {str(exc)}",
        )
    return {"insights": text_insights}