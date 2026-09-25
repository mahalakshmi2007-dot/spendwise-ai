import { useEffect, useMemo, useState } from "react";
import "./index.css";

const API = "https://spendwise-ai-daj4.onrender.com";
const MONTHLY_BUDGET = 15000;

type Expense = {
  id: number;
  user_id: number;
  amount: number;
  description: string;
  category: string;
  payment_method: string;
  expense_date: string;
  created_at: string;
};

type ForecastItem = {
  year: number;
  month: number;
  total: number;
};

type Forecast = {
  history: ForecastItem[];
  predicted_next_month_total: number;
  trend: string;
  monthly_change_rate: number;
  note: string | null;
};

type Anomaly = {
  expense_id: number;
  description: string;
  category: string;
  amount: number;
  expense_date: string;
  anomaly_score: number;
};

type PredictionResponse = {
  predicted_category?: string;
  category?: string;
  prediction?: string;
  confidence?: number;
  probabilities?: Record<string, number>;
};

function formatMoney(value: number) {
  return `Rs.${Number(value || 0).toLocaleString("en-IN", {
    maximumFractionDigits: 0,
  })}`;
}

function formatMonth(month: number) {
  const names = [
    "Jan",
    "Feb",
    "Mar",
    "Apr",
    "May",
    "Jun",
    "Jul",
    "Aug",
    "Sep",
    "Oct",
    "Nov",
    "Dec",
  ];

  return names[month - 1] || "";
}

function App() {
  const [amount, setAmount] = useState("");
  const [description, setDescription] = useState("");
  const [category, setCategory] = useState("Food");
  const [paymentMethod, setPaymentMethod] = useState("UPI");
  const [expenseDate, setExpenseDate] = useState("2026-09-23");

  const [addingExpense, setAddingExpense] = useState(false);
  const [addExpenseMessage, setAddExpenseMessage] = useState("");
  const [addExpenseError, setAddExpenseError] = useState("");

  const [prediction, setPrediction] = useState("");
  const [predictionConfidence, setPredictionConfidence] =
    useState<number | null>(null);
  const [predictionError, setPredictionError] = useState("");
  const [predicting, setPredicting] = useState(false);

  const [expenses, setExpenses] = useState<Expense[]>([]);
  const [forecast, setForecast] = useState<Forecast | null>(null);
  const [anomalies, setAnomalies] = useState<Anomaly[]>([]);
  const [insights, setInsights] = useState<string[]>([]);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const loadDashboard = async () => {
    try {
      setLoading(true);
      setError("");

      const [expensesRes, forecastRes, anomalyRes, insightRes] =
        await Promise.all([
          fetch(`${API}/expenses`),
          fetch(`${API}/ml/forecast`),
          fetch(`${API}/ml/anomalies`),
          fetch(`${API}/ml/insights`),
        ]);

      if (
        !expensesRes.ok ||
        !forecastRes.ok ||
        !anomalyRes.ok ||
        !insightRes.ok
      ) {
        throw new Error("Unable to load dashboard data.");
      }

      const expensesData: Expense[] = await expensesRes.json();
      const forecastData: Forecast = await forecastRes.json();
      const anomalyData: Anomaly[] = await anomalyRes.json();
      const insightData = await insightRes.json();

      setExpenses(expensesData);
      setForecast(forecastData);
      setAnomalies(anomalyData);
      setInsights(insightData.insights || []);
    } catch (err) {
      console.error(err);

      setError(
        "Could not connect to the backend. Make sure FastAPI is running on port 8000."
      );
    } finally {
      setLoading(false);
    }
  };

  const predictCategory = async () => {
    const text = description.trim();

    if (!text) {
      setPredictionError("Please enter an expense description.");
      return;
    }

    try {
      setPredicting(true);
      setPrediction("");
      setPredictionConfidence(null);
      setPredictionError("");

      const response = await fetch(`${API}/ml/predict-category`, {
        method: "POST",
        headers: {
          Accept: "application/json",
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          description: text,
        }),
      });

      if (!response.ok) {
        const errorText = await response.text().catch(() => "");

        throw new Error(
          `Backend returned status ${response.status}. ${errorText}`.trim()
        );
      }

      const data: PredictionResponse = await response.json();

      const predicted =
        data.predicted_category ||
        data.category ||
        data.prediction;

      if (!predicted) {
        throw new Error(
          "Backend response did not include a category."
        );
      }

      setPrediction(predicted);
      setCategory(predicted);

      if (typeof data.confidence === "number") {
        setPredictionConfidence(data.confidence);
      }
    } catch (err) {
      console.error("Prediction failed:", err);

      const message =
        err instanceof Error
          ? err.message
          : "Unknown error occurred.";

      setPredictionError(
        message.includes("Failed to fetch")
          ? "Could not reach the backend. Check that FastAPI is running."
          : `Prediction failed: ${message}`
      );
    } finally {
      setPredicting(false);
    }
  };

  const addExpense = async () => {
    setAddExpenseMessage("");
    setAddExpenseError("");

    const numericAmount = Number(amount);

    if (!amount || numericAmount <= 0) {
      setAddExpenseError("Please enter a valid amount.");
      return;
    }

    if (!description.trim()) {
      setAddExpenseError("Please enter an expense description.");
      return;
    }

    if (!category.trim()) {
      setAddExpenseError("Please select a category.");
      return;
    }

    try {
      setAddingExpense(true);

      const response = await fetch(`${API}/expenses`, {
        method: "POST",
        headers: {
          Accept: "application/json",
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          amount: numericAmount,
          description: description.trim(),
          category: category.trim(),
          payment_method: paymentMethod,
          expense_date: expenseDate,
        }),
      });

      if (!response.ok) {
        const errorText = await response.text().catch(() => "");

        throw new Error(
          `Failed to add expense. ${errorText}`.trim()
        );
      }

      await response.json();

      setAmount("");
      setDescription("");
      setCategory("Food");
      setPaymentMethod("UPI");
      setPrediction("");
      setPredictionConfidence(null);
      setPredictionError("");

      setAddExpenseMessage(
        "Expense added successfully! Dashboard updated."
      );

      await loadDashboard();
    } catch (err) {
      console.error("Add expense failed:", err);

      const message =
        err instanceof Error
          ? err.message
          : "Unable to add expense.";

      setAddExpenseError(message);
    } finally {
      setAddingExpense(false);
    }
  };

  useEffect(() => {
    loadDashboard();
  }, []);

  const currentMonthExpenses = useMemo(() => {
    const now = new Date();

    const currentYear = now.getFullYear();
    const currentMonth = now.getMonth() + 1;

    return expenses.filter((expense) => {
      const date = new Date(
        `${expense.expense_date}T00:00:00`
      );

      return (
        date.getFullYear() === currentYear &&
        date.getMonth() + 1 === currentMonth
      );
    });
  }, [expenses]);

  const currentSpending = useMemo(() => {
    return currentMonthExpenses.reduce(
      (total, expense) =>
        total + Number(expense.amount),
      0
    );
  }, [currentMonthExpenses]);

  const previousSpending = useMemo(() => {
    const now = new Date();

    const currentYear = now.getFullYear();
    const currentMonth = now.getMonth() + 1;

    let previousYear = currentYear;
    let previousMonth = currentMonth - 1;

    if (previousMonth === 0) {
      previousMonth = 12;
      previousYear -= 1;
    }

    return expenses
      .filter((expense) => {
        const date = new Date(
          `${expense.expense_date}T00:00:00`
        );

        return (
          date.getFullYear() === previousYear &&
          date.getMonth() + 1 === previousMonth
        );
      })
      .reduce(
        (total, expense) =>
          total + Number(expense.amount),
        0
      );
  }, [expenses]);

  const budgetUsed = Math.min(
    (currentSpending / MONTHLY_BUDGET) * 100,
    100
  );

  const remainingBudget = Math.max(
    MONTHLY_BUDGET - currentSpending,
    0
  );

  const highestCategory = useMemo(() => {
    if (!currentMonthExpenses.length) {
      return {
        name: "Not available",
        amount: 0,
      };
    }

    const categoryTotals: Record<string, number> = {};

    currentMonthExpenses.forEach((expense) => {
      categoryTotals[expense.category] =
        (categoryTotals[expense.category] || 0) +
        Number(expense.amount);
    });

    const sorted = Object.entries(
      categoryTotals
    ).sort((a, b) => b[1] - a[1]);

    return {
      name: sorted[0]?.[0] || "Not available",
      amount: sorted[0]?.[1] || 0,
    };
  }, [currentMonthExpenses]);

  const transactionCount =
    currentMonthExpenses.length;

  const averageTransaction = useMemo(() => {
    if (!currentMonthExpenses.length) {
      return 0;
    }

    return (
      currentSpending /
      currentMonthExpenses.length
    );
  }, [
    currentMonthExpenses,
    currentSpending,
  ]);

  const spendingChange = useMemo(() => {
    if (!previousSpending) {
      return 0;
    }

    return (
      ((currentSpending - previousSpending) /
        previousSpending) *
      100
    );
  }, [
    currentSpending,
    previousSpending,
  ]);

  const chartPoints = useMemo(() => {
    if (!forecast?.history?.length) {
      return "";
    }

    const data = forecast.history;

    const maxValue = Math.max(
      ...data.map((item) => item.total),
      forecast.predicted_next_month_total
    );

    const width = 700;
    const height = 260;
    const padding = 35;

    return data
      .map((item, index) => {
        const x =
          padding +
          (index /
            Math.max(data.length - 1, 1)) *
            (width - padding * 2);

        const y =
          height -
          padding -
          (item.total /
            Math.max(maxValue, 1)) *
            (height - padding * 2);

        return `${x},${y}`;
      })
      .join(" ");
  }, [forecast]);

  const scrollToSection = (id: string) => {
    document
      .getElementById(id)
      ?.scrollIntoView({
        behavior: "smooth",
        block: "start",
      });
  };

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-logo">S</div>

          <div>
            <h2>SpendWise</h2>
            <span>AI Finance</span>
          </div>
        </div>

        <nav className="navigation">
          <button
            className="nav-item active"
            type="button"
            onClick={() =>
              scrollToSection("dashboard-section")
            }
          >
            <span>⌂</span>
            Dashboard
          </button>

          <button
            className="nav-item"
            type="button"
            onClick={() =>
              scrollToSection("expenses-section")
            }
          >
            <span>Rs.</span>
            Expenses
          </button>

          <button
            className="nav-item"
            type="button"
            onClick={() =>
              scrollToSection("forecast-section")
            }
          >
            <span>↗</span>
            Forecast
          </button>

          <button
            className="nav-item"
            type="button"
            onClick={() =>
              scrollToSection("anomalies-section")
            }
          >
            <span>⚠</span>
            Anomalies
          </button>

          <button
            className="nav-item"
            type="button"
            onClick={() =>
              scrollToSection("insights-section")
            }
          >
            <span>✦</span>
            AI Insights
          </button>
        </nav>

        <div className="sidebar-bottom">
          <div className="ai-mini-card">
            <div className="ai-icon">✦</div>

            <div>
              <strong>AI Assistant</strong>

              <p>
                Your spending is being analyzed.
              </p>
            </div>
          </div>

          <div className="profile">
            <div className="profile-avatar">M</div>

            <div>
              <strong>Mahalakshmi</strong>

              <span>Student</span>
            </div>
          </div>
        </div>
      </aside>

      <main
        className="main-content"
        id="dashboard-section"
      >
        <header className="topbar">
          <div>
            <p className="eyebrow">
              PERSONAL FINANCE
            </p>

            <h1>
              Good afternoon 👋
            </h1>

            <p className="subtitle">
              Here's what's happening with your money.
            </p>
          </div>

          <button
            className="refresh-button"
            type="button"
            onClick={loadDashboard}
            disabled={loading}
          >
            <span>
              {loading ? "⟳" : "↻"}
            </span>

            {loading
              ? "Refreshing..."
              : "Refresh"}
          </button>
        </header>

        {error && (
          <div className="error-box">
            {error}
          </div>
        )}

        <section className="panel add-expense-panel">
          <div className="panel-header">
            <div>
              <h2>Add New Expense</h2>

              <p>
                Save your expense directly to SpendWise AI.
              </p>
            </div>

            <div className="budget-icon">+</div>
          </div>

          <div className="expense-form-grid">
            <div className="form-group">
              <label>Amount</label>

              <input
                type="number"
                min="1"
                value={amount}
                onChange={(event) =>
                  setAmount(event.target.value)
                }
                placeholder="Example: 250"
              />
            </div>

            <div className="form-group">
              <label>Description</label>

              <input
                value={description}
                onChange={(event) => {
                  setDescription(
                    event.target.value
                  );

                  setPrediction("");
                  setPredictionConfidence(null);
                  setPredictionError("");
                }}
                onKeyDown={(event) => {
                  if (
                    event.key === "Enter" &&
                    !predicting &&
                    description.trim()
                  ) {
                    predictCategory();
                  }
                }}
                placeholder="Example: chicken biryani"
              />
            </div>

            <div className="form-group">
              <label>Category</label>

              <select
                value={category}
                onChange={(event) =>
                  setCategory(
                    event.target.value
                  )
                }
              >
                <option value="Food">
                  Food
                </option>

                <option value="Transport">
                  Transport
                </option>

                <option value="Shopping">
                  Shopping
                </option>

                <option value="Utilities">
                  Utilities
                </option>

                <option value="Entertainment">
                  Entertainment
                </option>

                <option value="Healthcare">
                  Healthcare
                </option>

                <option value="Education">
                  Education
                </option>

                <option value="Other">
                  Other
                </option>
              </select>
            </div>

            <div className="form-group">
              <label>Payment Method</label>

              <select
                value={paymentMethod}
                onChange={(event) =>
                  setPaymentMethod(
                    event.target.value
                  )
                }
              >
                <option value="UPI">
                  UPI
                </option>

                <option value="Cash">
                  Cash
                </option>

                <option value="Card">
                  Card
                </option>

                <option value="Net Banking">
                  Net Banking
                </option>
              </select>
            </div>

            <div className="form-group">
              <label>Date</label>

              <input
                type="date"
                value={expenseDate}
                onChange={(event) =>
                  setExpenseDate(
                    event.target.value
                  )
                }
              />
            </div>
          </div>

          <div className="expense-actions">
            <button
              type="button"
              className="secondary-button"
              onClick={predictCategory}
              disabled={
                predicting ||
                !description.trim()
              }
            >
              {predicting
                ? "Predicting..."
                : "✦ Predict Category"}
            </button>

            <button
              type="button"
              className="primary-button"
              onClick={addExpense}
              disabled={addingExpense}
            >
              {addingExpense
                ? "Saving..."
                : "＋ Add Expense"}
            </button>
          </div>

          {prediction && (
            <div className="prediction-result">
              <span>
                AI predicted category
              </span>

              <strong>
                {prediction}
              </strong>

              {predictionConfidence !== null && (
                <em className="prediction-confidence">
                  {(
                    predictionConfidence *
                    100
                  ).toFixed(1)}
                  % confidence
                </em>
              )}
            </div>
          )}

          {predictionError && (
            <div className="prediction-result prediction-error">
              <span>Prediction Error</span>

              <strong>
                {predictionError}
              </strong>
            </div>
          )}

          {addExpenseMessage && (
            <div className="success-box">
              ✓ {addExpenseMessage}
            </div>
          )}

          {addExpenseError && (
            <div className="error-box">
              {addExpenseError}
            </div>
          )}
        </section>

        <section className="stats-grid">
          <div className="stat-card">
            <div className="stat-top">
              <span className="stat-label">
                Spent this month
              </span>

              <div className="stat-icon blue">
                Rs.
              </div>
            </div>

            <div className="stat-value">
              {formatMoney(currentSpending)}
            </div>

            <div
              className={`stat-change ${
                spendingChange > 0
                  ? "danger-text"
                  : "success-text"
              }`}
            >
              {spendingChange > 0
                ? "↑"
                : "↓"}{" "}
              {Math.abs(
                spendingChange
              ).toFixed(1)}
              % from last month
            </div>
          </div>

          <div className="stat-card">
            <div className="stat-top">
              <span className="stat-label">
                Monthly budget
              </span>

              <div className="stat-icon purple">
                ◫
              </div>
            </div>

            <div className="stat-value">
              {formatMoney(MONTHLY_BUDGET)}
            </div>

            <div className="stat-change neutral-text">
              {budgetUsed.toFixed(1)}% used
            </div>
          </div>

          <div className="stat-card">
            <div className="stat-top">
              <span className="stat-label">
                Remaining
              </span>

              <div className="stat-icon green">
                ✓
              </div>
            </div>

            <div className="stat-value">
              {formatMoney(remainingBudget)}
            </div>

            <div className="stat-change success-text">
              Available budget
            </div>
          </div>

          <div className="stat-card">
            <div className="stat-top">
              <span className="stat-label">
                Next month forecast
              </span>

              <div className="stat-icon orange">
                ↗
              </div>
            </div>

            <div className="stat-value">
              {formatMoney(
                forecast?.predicted_next_month_total ||
                  0
              )}
            </div>

            <div
              className={`stat-change ${
                forecast?.trend ===
                "increasing"
                  ? "danger-text"
                  : "success-text"
              }`}
            >
              {forecast?.trend ===
              "increasing"
                ? "↑"
                : "↓"}{" "}
              {forecast?.trend ||
                "No trend"}
            </div>
          </div>
        </section>

        <section
          className="dashboard-grid"
          id="forecast-section"
        >
          <div className="panel trend-panel">
            <div className="panel-header">
              <div>
                <h2>
                  Spending overview
                </h2>

                <p>
                  Monthly spending and AI forecast
                </p>
              </div>

              <div className="trend-badge">
                {forecast?.trend ===
                "increasing"
                  ? "↑ Increasing"
                  : "↓ Decreasing"}
              </div>
            </div>

            <div className="chart-wrapper">
              {forecast?.history?.length ? (
                <svg
                  className="spending-chart"
                  viewBox="0 0 700 260"
                  preserveAspectRatio="none"
                >
                  <line
                    x1="35"
                    y1="225"
                    x2="665"
                    y2="225"
                    stroke="#e5e7eb"
                  />

                  <line
                    x1="35"
                    y1="145"
                    x2="665"
                    y2="145"
                    stroke="#eef0f4"
                  />

                  <line
                    x1="35"
                    y1="65"
                    x2="665"
                    y2="65"
                    stroke="#eef0f4"
                  />

                  <polyline
                    points={chartPoints}
                    fill="none"
                    stroke="#4f46e5"
                    strokeWidth="4"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  />

                  {forecast.history.map(
                    (item, index) => {
                      const maxValue =
                        Math.max(
                          ...forecast.history.map(
                            (entry) =>
                              entry.total
                          ),
                          forecast.predicted_next_month_total
                        );

                      const x =
                        35 +
                        (index /
                          Math.max(
                            forecast.history
                              .length - 1,
                            1
                          )) *
                          630;

                      const y =
                        225 -
                        (item.total /
                          Math.max(
                            maxValue,
                            1
                          )) *
                          190;

                      return (
                        <circle
                          key={`${item.year}-${item.month}`}
                          cx={x}
                          cy={y}
                          r="6"
                          fill="white"
                          stroke="#4f46e5"
                          strokeWidth="3"
                        />
                      );
                    }
                  )}
                </svg>
              ) : (
                <div className="empty-state">
                  No spending history available.
                </div>
              )}

              <div className="chart-labels">
                {forecast?.history?.map(
                  (item) => (
                    <span
                      key={`${item.year}-${item.month}`}
                    >
                      {formatMonth(
                        item.month
                      )}
                    </span>
                  )
                )}
              </div>
            </div>

            <div className="chart-summary">
              <div>
                <span>Current month</span>

                <strong>
                  {formatMoney(
                    currentSpending
                  )}
                </strong>
              </div>

              <div>
                <span>Forecast</span>

                <strong>
                  {formatMoney(
                    forecast?.predicted_next_month_total ||
                      0
                  )}
                </strong>
              </div>

              <div>
                <span>Monthly change</span>

                <strong>
                  {(
                    forecast?.monthly_change_rate ||
                    0
                  ).toFixed(1)}
                  %
                </strong>
              </div>
            </div>
          </div>

          <div className="panel budget-panel">
            <div className="panel-header">
              <div>
                <h2>Monthly budget</h2>

                <p>
                  Current month spending
                </p>
              </div>

              <div className="budget-icon">
                Rs.
              </div>
            </div>

            <div className="budget-circle">
              <div className="budget-circle-inner">
                <strong>
                  {budgetUsed.toFixed(0)}%
                </strong>

                <span>used</span>
              </div>
            </div>

            <div className="budget-details">
              <div>
                <span>Spent</span>

                <strong>
                  {formatMoney(
                    currentSpending
                  )}
                </strong>
              </div>

              <div>
                <span>Remaining</span>

                <strong>
                  {formatMoney(
                    remainingBudget
                  )}
                </strong>
              </div>
            </div>

            <div className="progress-track">
              <div
                className="progress-fill"
                style={{
                  width: `${budgetUsed}%`,
                }}
              />
            </div>

            <p className="budget-note">
              {budgetUsed >= 80
                ? "You're getting close to your monthly budget."
                : "Your spending is within your monthly budget."}
            </p>
          </div>
        </section>

        <section className="bottom-grid">
          <div className="panel">
            <div className="panel-header">
              <div>
                <h2>
                  Spending category
                </h2>

                <p>
                  Your highest spending category
                </p>
              </div>
            </div>

            <div className="category-highlight">
              <div className="category-icon">
                🛒
              </div>

              <div className="category-info">
                <span>
                  {highestCategory.name}
                </span>

                <strong>
                  {formatMoney(
                    highestCategory.amount
                  )}
                </strong>
              </div>

              <div className="category-percent">
                {currentSpending
                  ? (
                      (highestCategory.amount /
                        currentSpending) *
                      100
                    ).toFixed(0)
                  : 0}
                %
              </div>
            </div>

            <div className="category-progress">
              <div
                style={{
                  width: `${
                    currentSpending
                      ? Math.min(
                          (highestCategory.amount /
                            currentSpending) *
                            100,
                          100
                        )
                      : 0
                  }%`,
                }}
              />
            </div>

            <div className="mini-stats">
              <div>
                <span>
                  Transactions
                </span>

                <strong>
                  {transactionCount}
                </strong>
              </div>

              <div>
                <span>Average</span>

                <strong>
                  {formatMoney(
                    averageTransaction
                  )}
                </strong>
              </div>
            </div>
          </div>

          <div
            className="panel"
            id="anomalies-section"
          >
            <div className="panel-header">
              <div>
                <h2>
                  Unusual expenses
                </h2>

                <p>
                  Detected by AI anomaly detection
                </p>
              </div>

              <span className="count-badge">
                {anomalies.length}
              </span>
            </div>

            {anomalies.length === 0 ? (
              <div className="empty-state small">
                No unusual expenses detected.
              </div>
            ) : (
              <div className="anomaly-list">
                {anomalies
                  .slice(0, 4)
                  .map((item) => (
                    <div
                      className="anomaly-item"
                      key={item.expense_id}
                    >
                      <div className="anomaly-warning">
                        !
                      </div>

                      <div className="anomaly-content">
                        <strong>
                          {item.description}
                        </strong>

                        <span>
                          {item.category} •{" "}
                          {item.expense_date}
                        </span>
                      </div>

                      <strong className="anomaly-amount">
                        {formatMoney(
                          item.amount
                        )}
                      </strong>
                    </div>
                  ))}
              </div>
            )}
          </div>
        </section>

        <section
          className="panel insights-panel"
          id="insights-section"
        >
          <div className="panel-header">
            <div>
              <h2>AI insights</h2>

              <p>
                Personalized observations from your spending data
              </p>
            </div>

            <div className="ai-badge">
              ✦ AI Powered
            </div>
          </div>

          <div className="insights-grid">
            {insights.length === 0 ? (
              <div className="empty-state">
                No AI insights available.
              </div>
            ) : (
              insights.map(
                (insight, index) => (
                  <div
                    className="insight-card"
                    key={index}
                  >
                    <div className="insight-number">
                      {index + 1}
                    </div>

                    <p>{insight}</p>
                  </div>
                )
              )
            )}
          </div>
        </section>

        <section className="prediction-panel">
          <div className="prediction-left">
            <div className="prediction-icon">
              ✦
            </div>

            <div>
              <p className="eyebrow">
                MACHINE LEARNING
              </p>

              <h2>
                AI Expense Categorizer
              </h2>

              <p>
                Test the ML model with an expense description.
              </p>
            </div>
          </div>

          <div className="prediction-form">
            <input
              value={description}
              onChange={(event) => {
                setDescription(
                  event.target.value
                );

                setPrediction("");
                setPredictionConfidence(null);
                setPredictionError("");
              }}
              onKeyDown={(event) => {
                if (
                  event.key === "Enter" &&
                  !predicting &&
                  description.trim()
                ) {
                  predictCategory();
                }
              }}
              placeholder="Example: chicken biryani"
            />

            <button
              type="button"
              onClick={predictCategory}
              disabled={
                predicting ||
                !description.trim()
              }
            >
              {predicting
                ? "Predicting..."
                : "Predict"}
            </button>
          </div>

          {predictionError && (
            <div className="prediction-result prediction-error">
              <span>Error</span>

              <strong>
                {predictionError}
              </strong>
            </div>
          )}

          {!predictionError &&
            prediction && (
              <div className="prediction-result">
                <span>
                  Predicted category
                </span>

                <strong>
                  {prediction}
                </strong>

                {predictionConfidence !==
                  null && (
                  <em className="prediction-confidence">
                    {(
                      predictionConfidence *
                      100
                    ).toFixed(1)}
                    % confidence
                  </em>
                )}
              </div>
            )}
        </section>

        <section
          className="panel"
          id="expenses-section"
        >
          <div className="panel-header">
            <div>
              <h2>Recent expenses</h2>

              <p>
                Expenses saved in your SQLite database
              </p>
            </div>

            <span className="count-badge">
              {expenses.length}
            </span>
          </div>

          {expenses.length === 0 ? (
            <div className="empty-state">
              No expenses found.
            </div>
          ) : (
            <div className="expense-table-wrapper">
              <table className="expense-table">
                <thead>
                  <tr>
                    <th>
                      Description
                    </th>

                    <th>
                      Category
                    </th>

                    <th>
                      Payment
                    </th>

                    <th>
                      Date
                    </th>

                    <th>
                      Amount
                    </th>
                  </tr>
                </thead>

                <tbody>
                  {expenses
                    .slice()
                    .reverse()
                    .slice(0, 8)
                    .map((expense) => (
                      <tr
                        key={expense.id}
                      >
                        <td>
                          <strong>
                            {expense.description}
                          </strong>
                        </td>

                        <td>
                          <span className="table-category">
                            {expense.category}
                          </span>
                        </td>

                        <td>
                          {expense.payment_method}
                        </td>

                        <td>
                          {expense.expense_date}
                        </td>

                        <td>
                          <strong>
                            {formatMoney(
                              expense.amount
                            )}
                          </strong>
                        </td>
                      </tr>
                    ))}
                </tbody>
              </table>
            </div>
          )}
        </section>

        <footer className="footer">
          <span>SpendWise AI</span>

          <span>
            Smart expense tracking with Machine Learning
          </span>
        </footer>
      </main>
    </div>
  );
}

export default App;