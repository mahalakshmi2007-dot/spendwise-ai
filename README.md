# 💰 SpendWise AI

**SpendWise AI** is a personal expense management and financial analysis application that helps users record expenses, understand spending patterns, and receive machine-learning-based insights.

The application combines **expense tracking, automatic category prediction, anomaly detection, spending insights, and monthly forecasting** in a simple dashboard.

🔗 **Live Demo:** https://spendwise-ai-lake.vercel.app/

---

## ✨ Features

### 📊 Expense Management

* Add and store daily expenses
* Track amount, description, category, payment method, and date
* View recorded expenses in the dashboard

### 🤖 AI Category Prediction

* Predicts an expense category from its description
* Uses **TF-IDF and Logistic Regression**
* Provides the predicted category, confidence, and probability distribution

**Example:**

`Chicken biryani → Food`

### 🚨 Anomaly Detection

* Identifies unusual expenses using **Isolation Forest**
* Considers expense amount, date information, and category-level spending
* Displays the most unusual expenses with anomaly scores

### 📈 Monthly Forecast

* Analyzes monthly spending history
* Provides a projected spending amount for the next month
* Handles insufficient historical data instead of generating a misleading trend

### 💡 Spending Insights

Generates useful insights such as:

* Monthly budget status
* Highest spending category
* Average transaction amount
* Spending stability
* Unusual expenses
* Forecast information

### 🎨 Dashboard

* Clean and responsive web interface
* Expense overview
* Budget information
* Forecast
* Anomaly detection
* AI-generated insights
* Category prediction

---

## 🧠 Machine Learning

SpendWise AI currently uses the following machine-learning techniques:

| Feature             | Technique                        |
| ------------------- | -------------------------------- |
| Category Prediction | TF-IDF + Logistic Regression     |
| Anomaly Detection   | Isolation Forest                 |
| Spending Forecast   | Monthly spending analysis        |
| Insights            | Rule-based + ML-derived analysis |

### Category Prediction

The category prediction model is trained on labeled expense descriptions and categories.

For example:

```text
Input:  chicken biryani
Output: Food
```

The prediction API also returns probability values for the available categories.

### Anomaly Detection

Isolation Forest is used to identify expenses that appear unusual compared with the user's expense history.

The system requires a minimum number of expenses before running anomaly detection.

### Forecasting

The forecasting module analyzes monthly expense totals. When only one month of data is available, the system reports insufficient historical data and uses the available month's spending as a simple continuation estimate.

---

## 🛠️ Tech Stack

### Frontend

* React
* TypeScript
* Vite
* CSS

### Backend

* Python
* FastAPI
* Uvicorn
* SQLAlchemy

### Machine Learning

* Scikit-learn
* NumPy

### Database

* SQLite

### Deployment

* Vercel — Frontend
* Render — Backend

---

## 🏗️ Project Architecture

```text
SpendWise AI
│
├── Frontend
│   ├── React
│   ├── TypeScript
│   └── Vite
│
├── Backend
│   ├── FastAPI
│   ├── SQLAlchemy
│   └── SQLite
│
└── Machine Learning
    ├── TF-IDF
    ├── Logistic Regression
    ├── Isolation Forest
    └── Forecasting
```

### Application Flow

```text
User
  │
  ▼
React Frontend
  │
  ▼
FastAPI Backend
  │
  ├── Expense Management
  │
  ├── SQLite Database
  │
  └── Machine Learning
        │
        ├── Category Prediction
        ├── Anomaly Detection
        ├── Forecast
        └── Insights
```

---

## 🔌 API Endpoints

The backend provides REST API endpoints for the main application features.

| Endpoint               | Method | Purpose                             |
| ---------------------- | ------ | ----------------------------------- |
| `/expenses`            | GET    | Retrieve expenses                   |
| `/expenses`            | POST   | Add an expense                      |
| `/ml/train`            | POST   | Train the category prediction model |
| `/ml/predict-category` | POST   | Predict an expense category         |
| `/ml/anomalies`        | GET    | Detect unusual expenses             |
| `/ml/forecast`         | GET    | Generate spending forecast          |
| `/ml/insights`         | GET    | Generate spending insights          |

Interactive API documentation is available through FastAPI/Swagger when the backend is running.

---

## 🚀 Local Setup

### 1. Clone the repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd spendwise-ai
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

### 3. Activate the virtual environment

**Windows:**

```bash
venv\Scripts\activate
```

### 4. Install backend dependencies

```bash
pip install -r requirements.txt
```

### 5. Start the FastAPI backend

```bash
uvicorn app.main:app --reload
```

The backend will be available at:

```text
http://127.0.0.1:8000
```

Swagger API documentation:

```text
http://127.0.0.1:8000/docs
```

### 6. Start the frontend

Install frontend dependencies:

```bash
npm install
```

Then start the development server:

```bash
npm run dev
```

---

## 📌 Current ML Model Status

The deployed category prediction model has been trained on **159 samples across 10 categories** during the current training run.

For example:

```text
Input:
chicken biryani

Prediction:
Food

Confidence:
40.9%
```

The confidence value represents the model's estimated probability for its predicted category and should not be interpreted as guaranteed correctness.

---

## ⚠️ Current Limitations

* Forecast quality improves with more historical monthly data.
* Category prediction confidence can vary depending on the expense description.
* SQLite is currently suitable for this academic/demo deployment but is not intended as a production-scale persistent database.
* The ML model should be retrained when the underlying training data is updated.

---

## 🔮 Future Improvements

* User authentication and multiple user accounts
* Persistent production database such as PostgreSQL
* Improved category prediction with a larger and cleaner dataset
* More historical data for forecasting
* Advanced financial visualizations
* Custom monthly budgets
* Export expenses to CSV/Excel
* Improved mobile responsiveness
* More personalized financial recommendations

---

## 🎓 Project Purpose

SpendWise AI was developed as an academic/personal project to explore the practical use of **Python, FastAPI, SQL databases, React, and machine learning** in a real-world expense management application.

The project demonstrates how machine learning can be integrated into a web application to provide useful analysis instead of only storing financial records.

---

## 👩‍💻 Author

**Mahalakshmi S**

B.Tech — Artificial Intelligence & Data Science

Tamil Nadu, India

* GitHub: https://github.com/mahalakshmi2007-dot
* LinkedIn: https://linkedin.com/in/mahalakshmi-s-7aa78b36b

---

## 📄 License

This project is created for educational and portfolio purposes.
