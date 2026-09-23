"""
Expense category predictor for SpendWise AI.

Uses:
- Built-in seed training data
- User's stored expenses
- TF-IDF
- Logistic Regression

The trained model is saved with joblib.
"""

import os
from typing import List, Tuple, Optional

import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sqlalchemy.orm import Session

from .. import models


MODEL_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "model_store"
)

MODEL_PATH = os.path.join(
    MODEL_DIR,
    "category_model.joblib"
)

MIN_SAMPLES_REQUIRED = 4
MIN_CATEGORIES_REQUIRED = 2


# ============================================================
# SEED TRAINING DATA
# ============================================================

SEED_TRAINING_DATA: List[Tuple[str, str]] = [

    # ---------------- FOOD ----------------
    ("chicken biryani", "Food"),
    ("mutton biryani", "Food"),
    ("veg biryani", "Food"),
    ("biryani", "Food"),
    ("dosa", "Food"),
    ("idli", "Food"),
    ("chapati", "Food"),
    ("parotta", "Food"),
    ("fried rice", "Food"),
    ("noodles", "Food"),
    ("pizza", "Food"),
    ("burger", "Food"),
    ("sandwich", "Food"),
    ("restaurant dinner", "Food"),
    ("restaurant lunch", "Food"),
    ("lunch", "Food"),
    ("dinner", "Food"),
    ("breakfast", "Food"),
    ("coffee", "Food"),
    ("tea", "Food"),
    ("snacks", "Food"),
    ("ice cream", "Food"),
    ("cake", "Food"),
    ("bakery", "Food"),
    ("swiggy", "Food"),
    ("zomato", "Food"),
    ("food delivery", "Food"),
    ("street food", "Food"),
    ("meals", "Food"),

    # ---------------- GROCERIES ----------------
    ("milk", "Groceries"),
    ("vegetables", "Groceries"),
    ("fruits", "Groceries"),
    ("rice", "Groceries"),
    ("wheat flour", "Groceries"),
    ("groceries", "Groceries"),
    ("grocery shopping", "Groceries"),
    ("grocery store", "Groceries"),
    ("supermarket", "Groceries"),
    ("eggs", "Groceries"),
    ("bread", "Groceries"),
    ("cooking oil", "Groceries"),
    ("salt", "Groceries"),
    ("sugar", "Groceries"),
    ("spices", "Groceries"),
    ("dal", "Groceries"),
    ("pulses", "Groceries"),
    ("vegetable shopping", "Groceries"),

    # ---------------- SHOPPING ----------------
    ("amazon shoes", "Shopping"),
    ("amazon order", "Shopping"),
    ("clothes shopping", "Shopping"),
    ("new dress", "Shopping"),
    ("shoes", "Shopping"),
    ("handbag", "Shopping"),
    ("mobile accessories", "Shopping"),
    ("headphones", "Shopping"),
    ("online shopping", "Shopping"),
    ("cosmetics", "Shopping"),
    ("perfume", "Shopping"),
    ("watch", "Shopping"),
    ("flipkart order", "Shopping"),
    ("myntra order", "Shopping"),
    ("t shirt", "Shopping"),
    ("jeans", "Shopping"),
    ("shirt", "Shopping"),
    ("dress", "Shopping"),
    ("shopping", "Shopping"),

    # ---------------- TRANSPORT ----------------
    ("bus ticket", "Transport"),
    ("bus pass", "Transport"),
    ("bus fare", "Transport"),
    ("train ticket", "Transport"),
    ("train fare", "Transport"),
    ("auto fare", "Transport"),
    ("auto ride", "Transport"),
    ("cab ride", "Transport"),
    ("uber ride", "Transport"),
    ("ola ride", "Transport"),
    ("petrol", "Transport"),
    ("fuel", "Transport"),
    ("diesel", "Transport"),
    ("travel expense", "Transport"),
    ("metro", "Transport"),
    ("metro card recharge", "Transport"),
    ("parking fee", "Transport"),
    ("flight ticket", "Transport"),
    ("vehicle service", "Transport"),

    # ---------------- EDUCATION ----------------
    ("college fees", "Education"),
    ("college fee", "Education"),
    ("tuition fees", "Education"),
    ("tuition fee", "Education"),
    ("school fees", "Education"),
    ("books", "Education"),
    ("book purchase", "Education"),
    ("notebook", "Education"),
    ("exam fees", "Education"),
    ("exam fee", "Education"),
    ("course fee", "Education"),
    ("stationery", "Education"),
    ("college supplies", "Education"),
    ("online course", "Education"),
    ("library fine", "Education"),
    ("project materials", "Education"),
    ("printing charges", "Education"),
    ("certification exam", "Education"),
    ("coaching class", "Education"),

    # ---------------- HEALTH ----------------
    ("medicine", "Health"),
    ("medicines", "Health"),
    ("pharmacy", "Health"),
    ("doctor consultation", "Health"),
    ("doctor fee", "Health"),
    ("hospital bill", "Health"),
    ("hospital", "Health"),
    ("tablets", "Health"),
    ("medical checkup", "Health"),
    ("health insurance", "Health"),
    ("dental checkup", "Health"),
    ("eye checkup", "Health"),
    ("first aid", "Health"),
    ("lab test", "Health"),
    ("vitamins", "Health"),
    ("medical expense", "Health"),

    # ---------------- UTILITIES ----------------
    ("electricity bill", "Utilities"),
    ("electricity payment", "Utilities"),
    ("water bill", "Utilities"),
    ("water payment", "Utilities"),
    ("internet bill", "Utilities"),
    ("internet recharge", "Utilities"),
    ("mobile recharge", "Utilities"),
    ("phone recharge", "Utilities"),
    ("phone bill", "Utilities"),
    ("wifi bill", "Utilities"),
    ("wifi recharge", "Utilities"),
    ("broadband bill", "Utilities"),
    ("dth recharge", "Utilities"),
    ("gas bill", "Utilities"),
    ("gas cylinder", "Utilities"),
    ("house rent", "Utilities"),
    ("rent payment", "Utilities"),
    ("maintenance charges", "Utilities"),

    # ---------------- ENTERTAINMENT ----------------
    ("netflix subscription", "Entertainment"),
    ("movie ticket", "Entertainment"),
    ("cinema ticket", "Entertainment"),
    ("cinema", "Entertainment"),
    ("spotify subscription", "Entertainment"),
    ("spotify", "Entertainment"),
    ("games", "Entertainment"),
    ("gaming", "Entertainment"),
    ("gaming purchase", "Entertainment"),
    ("amazon prime", "Entertainment"),
    ("prime subscription", "Entertainment"),
    ("amusement park", "Entertainment"),
    ("concert ticket", "Entertainment"),
    ("gaming subscription", "Entertainment"),
    ("youtube premium", "Entertainment"),
    ("theme park", "Entertainment"),
]


# ============================================================
# DATA FUNCTIONS
# ============================================================

def _get_seed_data() -> Tuple[List[str], List[str]]:
    """
    Return built-in training descriptions and categories.
    """

    descriptions = [
        description
        for description, category in SEED_TRAINING_DATA
    ]

    categories = [
        category
        for description, category in SEED_TRAINING_DATA
    ]

    return descriptions, categories


def _get_db_data(db: Session) -> Tuple[List[str], List[str]]:
    """
    Get expense descriptions and categories from database.
    """

    expenses = db.query(models.Expense).all()

    descriptions = []
    categories = []

    for expense in expenses:

        if expense.description and expense.category:

            descriptions.append(str(expense.description))
            categories.append(str(expense.category))

    return descriptions, categories


def _get_training_data(
    db: Session
) -> Tuple[List[str], List[str]]:
    """
    Combine seed data and user's database expenses.
    """

    seed_descriptions, seed_categories = _get_seed_data()

    db_descriptions, db_categories = _get_db_data(db)

    descriptions = seed_descriptions + db_descriptions
    categories = seed_categories + db_categories

    return descriptions, categories


# ============================================================
# TRAIN MODEL
# ============================================================

def train_category_model(db: Session) -> dict:
    """
    Train the category prediction model.
    """

    descriptions, categories = _get_training_data(db)

    unique_categories = set(categories)

    # Safety check
    if len(descriptions) < MIN_SAMPLES_REQUIRED:

        raise ValueError(
            f"Not enough training samples. "
            f"Found {len(descriptions)}, "
            f"need at least {MIN_SAMPLES_REQUIRED}."
        )

    if len(unique_categories) < MIN_CATEGORIES_REQUIRED:

        raise ValueError(
            f"Not enough categories. "
            f"Found {len(unique_categories)}, "
            f"need at least {MIN_CATEGORIES_REQUIRED}."
        )

    # --------------------------------------------------------
    # TF-IDF + Logistic Regression
    # --------------------------------------------------------

    pipeline = Pipeline(
        [
            (
                "tfidf",
                TfidfVectorizer(
                    lowercase=True,
                    ngram_range=(1, 2),
                    min_df=1,
                    sublinear_tf=True
                )
            ),
            (
                "clf",
                LogisticRegression(
                    max_iter=2000,
                    class_weight="balanced",
                    C=2.0
                )
            )
        ]
    )

    # Train
    pipeline.fit(descriptions, categories)

    # Training accuracy
    training_accuracy = float(
        pipeline.score(
            descriptions,
            categories
        )
    )

    # Save model
    os.makedirs(
        MODEL_DIR,
        exist_ok=True
    )

    joblib.dump(
        pipeline,
        MODEL_PATH
    )

    return {
        "trained_on_samples": len(descriptions),
        "distinct_categories": len(unique_categories),
        "training_accuracy": round(
            training_accuracy,
            4
        )
    }


# ============================================================
# LOAD MODEL
# ============================================================

def load_category_model() -> Optional[Pipeline]:
    """
    Load saved model from disk.
    """

    if not os.path.exists(MODEL_PATH):

        return None

    return joblib.load(MODEL_PATH)


# ============================================================
# PREDICT CATEGORY
# ============================================================

def predict_category(description: str) -> dict:
    """
    Predict expense category from description.
    """

    description = description.strip()

    if not description:

        raise ValueError(
            "Expense description cannot be empty."
        )

    pipeline = load_category_model()

    if pipeline is None:

        raise ValueError(
            "No trained model found. "
            "Call POST /ml/train first."
        )

    # Prediction
    predicted = pipeline.predict(
        [description]
    )[0]

    # Probabilities
    probabilities = pipeline.predict_proba(
        [description]
    )[0]

    classes = pipeline.classes_

    probability_map = {
        category: round(
            float(probability),
            4
        )
        for category, probability
        in zip(classes, probabilities)
    }

    confidence = probability_map[
        predicted
    ]

    return {
        "predicted_category": predicted,
        "confidence": confidence,
        "probabilities": probability_map
    }