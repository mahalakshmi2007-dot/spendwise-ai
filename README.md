# 💰 SpendWise AI

An AI-powered personal finance management application that helps users track expenses, analyze spending patterns, forecast future expenses, detect unusual transactions, and generate personalized financial insights.

## 🚀 Features

* 📊 **Expense Dashboard** — View spending summaries and recent transactions.
* ➕ **Expense Management** — Add and manage daily expenses.
* 🤖 **AI Expense Categorization** — Predict expense categories from descriptions using Machine Learning.
* 📈 **Spending Forecast** — Predict next month's spending using historical expense data.
* 🚨 **Anomaly Detection** — Identify unusual or potentially abnormal expenses.
* 💡 **AI Insights** — Generate automatic insights from spending and budget data.
* 💰 **Budget Tracking** — Monitor monthly spending against a defined budget.
* 🔄 **Live Dashboard Updates** — Refresh the dashboard to view updated financial data.

## 🧠 Machine Learning

SpendWise AI uses multiple Machine Learning techniques:

### 1. Expense Category Prediction

* TF-IDF Vectorization
* Logistic Regression
* Predicts categories such as:

  * Food
  * Groceries
  * Shopping
  * Transport
  * Education
  * Health
  * Utilities
  * Entertainment

### 2. Spending Forecast

* Linear Regression
* Uses historical monthly spending to estimate the next month's total.

### 3. Anomaly Detection

* Isolation Forest
* Detects unusual expense transactions based on spending patterns.

### 4. AI Insights

The application generates insights about:

* Monthly spending
* Budget usage
* Highest spending category
* Average transaction amount
* Spending trend
* Forecasted spending
* Unusual expenses

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
* SQLite

### Machine Learning

* Scikit-learn
* NumPy
* Joblib

## 📁 Project Structure

```text
spendwise-ai/
│
├── backend/
│   ├── app/
│   │   ├── ml/
│   │   │   ├── anomaly_detector.py
│   │   │   ├── category_predictor.py
│   │   │   ├── forecasting.py
│   │   │   └── insights.py
│   │   │
│   │   ├── routes/
│   │   ├── crud.py
│   │   ├── database.py
│   │   ├── main.py
│   │   ├── models.py
│   │   └── schemas.py
│   │
│   ├── requirements.txt
│   └── seed.py
│
├── src/
│   ├── App.tsx
│   ├── App.css
│   ├── index.css
│   └── main.tsx
│
├── public/
├── package.json
├── vite.config.ts
├── README.md
└── .gitignore
```

## ⚙️ Installation

### 1. Clone the repository

```bash
git clone https://github.com/mahalakshmi2007-dot/spendwise-ai.git
cd spendwise-ai
```

### 2. Frontend setup

```bash
npm install
npm run dev
```

Frontend runs on:

```text
http://localhost:5173
```

### 3. Backend setup

Open another terminal:

```bash
cd backend
python -m venv venv
```

Activate the virtual environment on Windows:

```powershell
venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Start the backend:

```bash
uvicorn app.main:app --reload
```

Backend runs on:

```text
http://127.0.0.1:8000
```

API documentation:

```text
http://127.0.0.1:8000/docs
```

## 🔌 Main API Endpoints

| Method | Endpoint               | Purpose                          |
| ------ | ---------------------- | -------------------------------- |
| POST   | `/ml/train`            | Train the expense category model |
| POST   | `/ml/predict-category` | Predict an expense category      |
| GET    | `/ml/forecast`         | Forecast next month's spending   |
| GET    | `/ml/anomalies`        | Detect unusual expenses          |
| GET    | `/ml/insights`         | Generate financial insights      |

## 🧪 ML Testing

The implemented ML features were tested through the FastAPI Swagger documentation.

Example:

```text
"chicken biryani" → Food
"electricity bill" → Utilities
```

The ML endpoints returned successful `200 OK` responses during testing.

## 🎯 Project Goal

SpendWise AI was developed as a practical project to combine:

* Web Development
* Data Analysis
* Machine Learning
* Database Management
* REST API Development
* Financial Data Visualization

The goal is to provide a simple interface for understanding personal spending patterns and making data-driven financial observations.

## 👩‍💻 Developer

**Mahalakshmi S**

B.Tech Artificial Intelligence & Data Science
V.S.B College of Engineering & Technical Campus, Coimbatore

GitHub:
https://github.com/mahalakshmi2007-dot

## 📌 Project Status

**Current Status: Working Prototype**

The core expense management, dashboard, Machine Learning, forecasting, anomaly detection, and AI insight features have been implemented and tested.
