"""
Expense category predictor (Part 2).

Trains a TF-IDF + Logistic Regression pipeline on the descriptions
and categories of the user's existing expenses, then uses it to
predict a category for new, unseen expense descriptions.

The trained pipeline is saved to disk with joblib so it doesn't need
to be retrained every time the server restarts. Call POST /ml/train
whenever you want to retrain it on the latest data (e.g. after adding
a lot of new expenses).
"""

import os
from typing import List, Tuple, Optional

import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sqlalchemy.orm import Session

from .. import models

MODEL_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "model_store")
MODEL_PATH = os.path.join(MODEL_DIR, "category_model.joblib")

# A real model needs at least a handful of examples and at least two
# different categories to learn anything meaningful.
MIN_SAMPLES_REQUIRED = 4
MIN_CATEGORIES_REQUIRED = 2


def _get_training_data(db: Session) -> Tuple[List[str], List[str]]:
    """Pull (description, category) pairs from every stored expense."""
    expenses = db.query(models.Expense).all()
    descriptions = [e.description for e in expenses]
    categories = [e.category for e in expenses]
    return descriptions, categories


def train_category_model(db: Session) -> dict:
    """
    Train a TF-IDF + Logistic Regression pipeline on current expense data
    and save it to disk. Returns basic training statistics so the caller
    can see how the model did.
    """
    descriptions, categories = _get_training_data(db)
    unique_categories = set(categories)

    if len(descriptions) < MIN_SAMPLES_REQUIRED:
        raise ValueError(
            f"Not enough expenses to train a model. "
            f"Found {len(descriptions)}, need at least {MIN_SAMPLES_REQUIRED}. "
            f"Add a few more expenses first."
        )

    if len(unique_categories) < MIN_CATEGORIES_REQUIRED:
        raise ValueError(
            f"Not enough distinct categories to train a model. "
            f"Found {len(unique_categories)}, need at least {MIN_CATEGORIES_REQUIRED}."
        )

    pipeline = Pipeline([
        ("tfidf", TfidfVectorizer(lowercase=True, ngram_range=(1, 2), min_df=1)),
        ("clf", LogisticRegression(max_iter=1000, class_weight="balanced")),
    ])

    pipeline.fit(descriptions, categories)

    # Training accuracy (fit on all data, since a small personal dataset
    # doesn't have enough rows per category to hold out a test split).
    training_accuracy = float(pipeline.score(descriptions, categories))

    os.makedirs(MODEL_DIR, exist_ok=True)
    joblib.dump(pipeline, MODEL_PATH)

    return {
        "trained_on_samples": len(descriptions),
        "distinct_categories": len(unique_categories),
        "training_accuracy": round(training_accuracy, 4),
    }


def load_category_model() -> Optional[Pipeline]:
    """Load the trained pipeline from disk, or None if it hasn't been trained yet."""
    if not os.path.exists(MODEL_PATH):
        return None
    return joblib.load(MODEL_PATH)


def predict_category(description: str) -> dict:
    """
    Predict the most likely category for a new expense description.
    Returns the predicted category, a confidence score, and the full
    probability breakdown across every category the model has learned.
    """
    pipeline = load_category_model()
    if pipeline is None:
        raise ValueError("No trained model found. Call POST /ml/train first.")

    predicted = pipeline.predict([description])[0]
    probabilities = pipeline.predict_proba([description])[0]
    classes = pipeline.classes_

    prob_map = {cls: float(round(prob, 4)) for cls, prob in zip(classes, probabilities)}
    confidence = prob_map[predicted]

    return {
        "predicted_category": predicted,
        "confidence": confidence,
        "probabilities": prob_map,
    }
