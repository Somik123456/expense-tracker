# Interview Prep — Python Expense Tracker

---

## 1. One-Line Project Description (say this first)
> "I built a full-stack web app using Python and Flask where users can log in, track daily expenses by category, set monthly budgets, and export their data as CSV."

---

## 2. Core Concepts You Must Know

### Python & Flask
**Q: What is Flask?**
> Flask is a lightweight Python web framework. It lets you define URL routes and connect them to Python functions that return HTML pages or data.

**Q: How does routing work in Flask?**
> You use the `@app.route('/path')` decorator above a function. When someone visits that URL, Flask runs that function and returns the response.
> Example from the project:
> ```python
> @app.route('/add', methods=['GET', 'POST'])
> def add_expense():
>     ...
> ```

**Q: What is the difference between GET and POST?**
> GET is used to fetch/display data (like loading a page). POST is used to submit data (like submitting a form to add an expense).

**Q: How did you store data?**
> I used SQLite, which is a file-based database built into Python. I used the `sqlite3` library to write SQL queries directly — CREATE TABLE, INSERT, SELECT, UPDATE, DELETE.

**Q: What is a session in Flask?**
> A session stores small pieces of data on the server between requests. I used it to remember which user is logged in — after login I store `session['user_id']`, and on every protected page I check if that key exists.

**Q: How did you protect passwords?**
> I never store plain text passwords. I used `werkzeug.security.generate_password_hash()` to hash the password before saving it, and `check_password_hash()` to verify it during login.

**Q: What is the `login_required` decorator in your code?**
> It's a function I wrote that wraps other route functions. Before running the actual route, it checks if the user is logged in. If not, it redirects to the login page. This way I don't have to repeat that check in every route.

### Database
**Q: What SQL queries did you use?**
> - `INSERT INTO expenses ...` — add a new expense
> - `SELECT * FROM expenses WHERE user_id=?` — get all expenses for a user
> - `UPDATE expenses SET ... WHERE id=?` — edit an expense
> - `DELETE FROM expenses WHERE id=?` — delete an expense
> - `SUM(amount)` with `GROUP BY category` — for the dashboard totals

**Q: Why SQLite and not MySQL?**
> SQLite is serverless and requires no setup — perfect for a personal app or development. For a production app with multiple users, I'd switch to MySQL or PostgreSQL.

**Q: What are parameterized queries? Why did you use them?**
> Instead of putting user input directly into SQL strings (which causes SQL injection), I used `?` placeholders and passed values separately. Example: `conn.execute('SELECT * FROM users WHERE username=?', (username,))`. This keeps the app secure.

---

## 3. Features You Should Be Able to Explain

| Feature | What to say |
|---------|-------------|
| Login/Register | "User enters credentials, password is hashed and stored. On login, the hash is compared." |
| Add/Edit/Delete expense | "Standard CRUD — forms POST to Flask routes, which run SQL queries." |
| Dashboard category breakdown | "I query SUM of amounts grouped by category for the current month, then show progress bars." |
| Monthly budget alerts | "User sets a limit per category. Dashboard compares actual spend vs limit and shows red/yellow/green." |
| CSV Export | "I query all expenses, write them to an in-memory CSV using Python's `csv` module, and send it as a file download." |
| Filters | "The expenses page accepts `month` and `category` as URL query parameters and adds them to the SQL WHERE clause." |

---

## 4. Interview Demo Steps (do these in order)

> Open browser at `http://127.0.0.1:5000` before the interview starts.

**Step 1 — Register**
- Go to `/register`, create a new account
- Say: "Passwords are hashed using Werkzeug before being stored in SQLite"

**Step 2 — Add 3-4 expenses**
- Add expenses in different categories (Food, Transport, Entertainment)
- Use different dates — add a couple from the current month
- Say: "Each expense is tied to the logged-in user's ID so data is isolated per user"

**Step 3 — Show the Dashboard**
- Point to the category breakdown bars
- Point to the KPI cards (this month total, all time total)
- Say: "This uses a GROUP BY SQL query to aggregate spending per category"

**Step 4 — Set a Budget**
- Go to `/budget`, set a limit for Food (set it lower than what you already spent)
- Go back to Dashboard — show the red "over budget" alert
- Say: "The dashboard compares actual spend against the budget and highlights it visually"

**Step 5 — Filter Expenses**
- Go to `/expenses`, filter by category
- Say: "Filters are passed as query parameters and appended to the SQL WHERE clause dynamically"

**Step 6 — Export CSV**
- Click Export CSV
- Open the downloaded file in Excel/Numbers
- Say: "This CSV can be loaded directly into Power BI for visualization"

**Step 7 — Show the Code (if asked)**
- Open `app.py` and show the `add_expense` route — it's clean and easy to follow
- Show the `login_required` decorator

---

## 5. Likely Follow-up Questions

**Q: What would you improve if you had more time?**
> "I'd add multi-user support with better role management, add charts using Chart.js directly in the dashboard, and deploy it on Render or Railway so it's accessible online."

**Q: What was the hardest part?**
> "Getting the budget alert logic right on the dashboard — I had to join the monthly spending data with the budget data in Python since SQLite doesn't have a clean way to do conditional aggregation across two tables."

**Q: Have you used any ORM?**
> "In this project I used raw SQL with sqlite3 for learning purposes. I know that Flask-SQLAlchemy is the standard ORM for Flask apps and Spring Boot uses Hibernate — I used that in my Java project."
