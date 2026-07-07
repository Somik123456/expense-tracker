from flask import Flask, render_template, request, redirect, url_for, flash, session, send_file
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import csv
import io
import os
from datetime import datetime, date
from functools import wraps

app = Flask(__name__)
app.secret_key = 'expense-tracker-secret-key-2024'

DATABASE = 'expenses.db'

CATEGORIES = ['Food', 'Transport', 'Housing', 'Healthcare', 'Entertainment',
              'Shopping', 'Education', 'Travel', 'Utilities', 'Others']


def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.executescript('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            date TEXT NOT NULL,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );
        CREATE TABLE IF NOT EXISTS budgets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            category TEXT NOT NULL,
            monthly_limit REAL NOT NULL,
            month TEXT NOT NULL,
            UNIQUE(user_id, category, month)
        );
    ''')
    conn.commit()
    conn.close()


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated


@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']
        if not username or not password:
            flash('Username and password are required.', 'danger')
            return render_template('register.html')
        if len(password) < 6:
            flash('Password must be at least 6 characters.', 'danger')
            return render_template('register.html')
        conn = get_db()
        try:
            conn.execute('INSERT INTO users (username, password) VALUES (?, ?)',
                         (username, generate_password_hash(password)))
            conn.commit()
            flash('Account created! Please log in.', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Username already taken.', 'danger')
        finally:
            conn.close()
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']
        conn = get_db()
        user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        conn.close()
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            return redirect(url_for('dashboard'))
        flash('Invalid credentials.', 'danger')
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


@app.route('/dashboard')
@login_required
def dashboard():
    conn = get_db()
    uid = session['user_id']
    current_month = date.today().strftime('%Y-%m')

    # Monthly totals per category
    monthly = conn.execute('''
        SELECT category, SUM(amount) as total
        FROM expenses WHERE user_id=? AND strftime('%Y-%m', date)=?
        GROUP BY category ORDER BY total DESC
    ''', (uid, current_month)).fetchall()

    # Recent 5 expenses
    recent = conn.execute('''
        SELECT * FROM expenses WHERE user_id=?
        ORDER BY date DESC, created_at DESC LIMIT 5
    ''', (uid,)).fetchall()

    # Total this month
    total_month = conn.execute('''
        SELECT COALESCE(SUM(amount), 0) as total
        FROM expenses WHERE user_id=? AND strftime('%Y-%m', date)=?
    ''', (uid, current_month)).fetchone()['total']

    # Total all time
    total_all = conn.execute(
        'SELECT COALESCE(SUM(amount), 0) as total FROM expenses WHERE user_id=?', (uid,)
    ).fetchone()['total']

    # Budgets for this month
    budgets = conn.execute(
        'SELECT * FROM budgets WHERE user_id=? AND month=?', (uid, current_month)
    ).fetchall()
    budget_map = {b['category']: b['monthly_limit'] for b in budgets}

    conn.close()
    return render_template('dashboard.html',
                           monthly=monthly, recent=recent,
                           total_month=total_month, total_all=total_all,
                           budget_map=budget_map, current_month=current_month,
                           categories=CATEGORIES)


@app.route('/expenses')
@login_required
def expenses():
    conn = get_db()
    uid = session['user_id']
    month = request.args.get('month', '')
    category = request.args.get('category', '')

    query = 'SELECT * FROM expenses WHERE user_id=?'
    params = [uid]
    if month:
        query += " AND strftime('%Y-%m', date)=?"
        params.append(month)
    if category:
        query += ' AND category=?'
        params.append(category)
    query += ' ORDER BY date DESC, created_at DESC'

    rows = conn.execute(query, params).fetchall()
    total = sum(r['amount'] for r in rows)
    conn.close()
    return render_template('expenses.html', expenses=rows, total=total,
                           categories=CATEGORIES, month=month, category=category)


@app.route('/add', methods=['GET', 'POST'])
@login_required
def add_expense():
    if request.method == 'POST':
        title = request.form['title'].strip()
        amount = request.form['amount']
        category = request.form['category']
        exp_date = request.form['date']
        notes = request.form.get('notes', '').strip()
        try:
            amount = float(amount)
            if amount <= 0:
                raise ValueError
        except ValueError:
            flash('Amount must be a positive number.', 'danger')
            return render_template('add_expense.html', categories=CATEGORIES,
                                   today=date.today().isoformat())
        if not title or not category or not exp_date:
            flash('Title, category and date are required.', 'danger')
            return render_template('add_expense.html', categories=CATEGORIES,
                                   today=date.today().isoformat())
        conn = get_db()
        conn.execute(
            'INSERT INTO expenses (user_id, title, amount, category, date, notes) VALUES (?,?,?,?,?,?)',
            (session['user_id'], title, amount, category, exp_date, notes)
        )
        conn.commit()
        conn.close()
        flash('Expense added!', 'success')
        return redirect(url_for('dashboard'))
    return render_template('add_expense.html', categories=CATEGORIES,
                           today=date.today().isoformat())


@app.route('/edit/<int:expense_id>', methods=['GET', 'POST'])
@login_required
def edit_expense(expense_id):
    conn = get_db()
    expense = conn.execute(
        'SELECT * FROM expenses WHERE id=? AND user_id=?', (expense_id, session['user_id'])
    ).fetchone()
    if not expense:
        conn.close()
        flash('Expense not found.', 'danger')
        return redirect(url_for('expenses'))
    if request.method == 'POST':
        title = request.form['title'].strip()
        amount = request.form['amount']
        category = request.form['category']
        exp_date = request.form['date']
        notes = request.form.get('notes', '').strip()
        try:
            amount = float(amount)
            if amount <= 0:
                raise ValueError
        except ValueError:
            flash('Amount must be a positive number.', 'danger')
            return render_template('edit_expense.html', expense=expense, categories=CATEGORIES)
        conn.execute(
            'UPDATE expenses SET title=?, amount=?, category=?, date=?, notes=? WHERE id=?',
            (title, amount, category, exp_date, notes, expense_id)
        )
        conn.commit()
        conn.close()
        flash('Expense updated!', 'success')
        return redirect(url_for('expenses'))
    conn.close()
    return render_template('edit_expense.html', expense=expense, categories=CATEGORIES)


@app.route('/delete/<int:expense_id>', methods=['POST'])
@login_required
def delete_expense(expense_id):
    conn = get_db()
    conn.execute('DELETE FROM expenses WHERE id=? AND user_id=?',
                 (expense_id, session['user_id']))
    conn.commit()
    conn.close()
    flash('Expense deleted.', 'info')
    return redirect(url_for('expenses'))


@app.route('/export')
@login_required
def export_csv():
    conn = get_db()
    rows = conn.execute(
        'SELECT title, amount, category, date, notes FROM expenses WHERE user_id=? ORDER BY date DESC',
        (session['user_id'],)
    ).fetchall()
    conn.close()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Title', 'Amount', 'Category', 'Date', 'Notes'])
    for row in rows:
        writer.writerow([row['title'], row['amount'], row['category'], row['date'], row['notes'] or ''])
    output.seek(0)
    return send_file(
        io.BytesIO(output.getvalue().encode()),
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'expenses_{session["username"]}_{date.today()}.csv'
    )


@app.route('/summary')
@login_required
def summary():
    conn = get_db()
    uid = session['user_id']
    monthly = conn.execute('''
        SELECT strftime('%Y-%m', date) as month, SUM(amount) as total, COUNT(*) as count
        FROM expenses WHERE user_id=?
        GROUP BY month ORDER BY month DESC
    ''', (uid,)).fetchall()
    conn.close()
    return render_template('summary.html', monthly=monthly)


@app.route('/budget', methods=['GET', 'POST'])
@login_required
def budget():
    conn = get_db()
    uid = session['user_id']
    current_month = date.today().strftime('%Y-%m')
    if request.method == 'POST':
        category = request.form['category']
        limit = request.form['limit']
        try:
            limit = float(limit)
            if limit <= 0:
                raise ValueError
        except ValueError:
            flash('Budget limit must be a positive number.', 'danger')
        else:
            conn.execute('''
                INSERT INTO budgets (user_id, category, monthly_limit, month)
                VALUES (?,?,?,?)
                ON CONFLICT(user_id, category, month)
                DO UPDATE SET monthly_limit=excluded.monthly_limit
            ''', (uid, category, limit, current_month))
            conn.commit()
            flash(f'Budget set for {category}!', 'success')
    budgets = conn.execute(
        'SELECT * FROM budgets WHERE user_id=? AND month=?', (uid, current_month)
    ).fetchall()
    # spending this month per category
    spending = {r['category']: r['total'] for r in conn.execute('''
        SELECT category, SUM(amount) as total FROM expenses
        WHERE user_id=? AND strftime('%Y-%m', date)=?
        GROUP BY category
    ''', (uid, current_month)).fetchall()}
    conn.close()
    return render_template('budget.html', budgets=budgets, spending=spending,
                           categories=CATEGORIES, current_month=current_month)


if __name__ == '__main__':
    init_db()
    app.run(debug=True)
