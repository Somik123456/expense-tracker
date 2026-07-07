# Expense Tracker — Python Flask

A full-stack personal finance web app built with Python (Flask) and SQLite. Track your daily expenses, set monthly budgets, view spending summaries, and export your data to CSV for further analysis (e.g., Power BI dashboard).

---

## What This Project Does

- **User authentication** — register and log in securely (passwords hashed with Werkzeug)
- **Add / Edit / Delete expenses** — title, amount, category, date, optional notes
- **10 categories** — Food, Transport, Housing, Healthcare, Entertainment, Shopping, Education, Travel, Utilities, Others
- **Dashboard** — monthly spend totals, category breakdown with progress bars, recent transactions, budget alerts
- **Monthly budgets** — set a limit per category; get visual warnings when approaching or exceeding it
- **Monthly summary** — view month-by-month totals and transaction counts
- **CSV export** — download all your expenses as a CSV file (feeds directly into the Power BI dashboard project)
- **Filter expenses** — filter by month or category

---

## Tech Stack

| Layer     | Technology              |
|-----------|-------------------------|
| Backend   | Python 3, Flask 3.x     |
| Database  | SQLite (via Python stdlib) |
| Frontend  | Jinja2 templates, Bootstrap 5, Bootstrap Icons |
| Auth      | Werkzeug password hashing, Flask session |

---

## Project Structure

```
expense-tracker/
├── app.py                  # Main Flask application (routes, DB logic)
├── requirements.txt        # Python dependencies
├── expenses.db             # SQLite DB (auto-created on first run)
└── templates/
    ├── base.html           # Shared layout with navbar + sidebar
    ├── login.html
    ├── register.html
    ├── dashboard.html      # Home screen with stats and charts
    ├── expenses.html       # Full expense list with filters
    ├── add_expense.html
    ├── edit_expense.html
    ├── summary.html        # Monthly summary table
    └── budget.html         # Budget setting and tracking
```

---

## How to Run

### Prerequisites
- Python 3.8+

### Steps

```bash
# 1. Navigate to the project folder
cd expense-tracker

# 2. Create a virtual environment
python3 -m venv venv
source venv/bin/activate        # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the app
python app.py

# 5. Open in browser
# http://127.0.0.1:5000
```

The SQLite database (`expenses.db`) is created automatically on first run. No setup required.

---

## Key Pages

| Route         | Description                          |
|---------------|--------------------------------------|
| `/`           | Redirects to dashboard or login      |
| `/login`      | Login page                           |
| `/register`   | New user registration                |
| `/dashboard`  | Overview: totals, categories, alerts |
| `/expenses`   | All expenses with filter/search      |
| `/add`        | Add new expense                      |
| `/edit/<id>`  | Edit existing expense                |
| `/summary`    | Month-by-month summary               |
| `/budget`     | Set and track monthly budgets        |
| `/export`     | Download all expenses as CSV         |

---

## Connecting to Power BI

1. Go to `/export` while logged in and download your CSV
2. Open Power BI Desktop → Get Data → Text/CSV → load the file
3. Build dashboards using the Category, Month, and Amount columns
4. See the `powerbi-dashboard` project for a full guide

---

## Screenshots

> Add screenshots of the dashboard, expense list, and budget page here after running the app.
