import sqlite3
import streamlit as st
from datetime import datetime

# ✅ Ensure the budget tables exist
def create_budget_tables():
    conn = sqlite3.connect("Process/users.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS monthly_budget (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        month TEXT,
        category TEXT,
        planned_amount REAL,
        UNIQUE(username, month, category)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS daily_transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        date TEXT,
        category TEXT,
        amount REAL
    )
    """)

    conn.commit()
    conn.close()

# ✅ Add a planned budget for the month
def add_monthly_budget(username, category, planned_amount):
    month = datetime.today().strftime("%Y-%m")  # Current month
    conn = sqlite3.connect("Process/users.db")
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO monthly_budget (username, month, category, planned_amount)
    VALUES (?, ?, ?, ?)
    ON CONFLICT(username, month, category) DO UPDATE SET planned_amount = excluded.planned_amount
    """, (username, month, category, planned_amount))

    conn.commit()
    conn.close()
    st.success(f"Planned amount set for {category}: {planned_amount}")

# ✅ Update monthly budget
def update_budget(username, category, new_planned_amount):
    month = datetime.today().strftime("%Y-%m")  # Current month
    conn = sqlite3.connect("Process/users.db")
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE monthly_budget 
    SET planned_amount = ? 
    WHERE username = ? AND month = ? AND category = ?
    """, (new_planned_amount, username, month, category))

    conn.commit()
    conn.close()
    st.success(f"Updated planned amount for {category}: {new_planned_amount}")

# ✅ UI: Set monthly budget
def set_monthly_budget():
    if "logged_in" in st.session_state and st.session_state.logged_in:
        username = st.session_state.username
        st.subheader("Set Monthly Planned Budget")

        category = st.text_input("Category (e.g., Rent, Food, Transport)")
        planned_amount = st.number_input("Planned Amount", min_value=0.0, format="%.2f")

        if st.button("Save Budget"):
            add_monthly_budget(username, category, planned_amount)
    else:
        st.warning("Please log in first.")

# ✅ Add a daily income/expense transaction
def add_daily_transaction(username, category, amount):
    date = datetime.today().strftime("%Y-%m-%d")  # Current date
    conn = sqlite3.connect("Process/users.db")
    cursor = conn.cursor()

    cursor.execute("INSERT INTO daily_transactions (username, date, category, amount) VALUES (?, ?, ?, ?)", 
                   (username, date, category, amount))

    conn.commit()
    conn.close()
    st.success(f"Transaction logged: {amount} for {category} on {date}")

# ✅ UI: Log daily transactions
def log_daily_amount():
    if "logged_in" in st.session_state and st.session_state.logged_in:
        username = st.session_state.username
        st.subheader("Log Daily Income/Expense")

        category = st.text_input("Category (e.g., Salary, Food, Transport)")
        amount = st.number_input("Amount", min_value=0.0, format="%.2f")

        if st.button("Log Transaction"):
            add_daily_transaction(username, category, amount)
    else:
        st.warning("Please log in first.")

# ✅ Fetch budget progress for the current month
def get_budget_progress(username):
    month = datetime.today().strftime("%Y-%m")  # Current month
    conn = sqlite3.connect("Process/users.db")
    cursor = conn.cursor()

    # Get planned budget
    cursor.execute("SELECT category, planned_amount FROM monthly_budget WHERE username = ? AND month = ?", 
                   (username, month))
    planned_data = cursor.fetchall()

    # Get actual expenses
    cursor.execute("""
    SELECT category, SUM(amount) FROM daily_transactions 
    WHERE username = ? AND date LIKE ? 
    GROUP BY category
    """, (username, f"{month}-%"))
    
    actual_data = {row[0]: row[1] for row in cursor.fetchall()}
    conn.close()

    return planned_data, actual_data

# ✅ UI: Show budget progress
def show_budget_progress():
    if "logged_in" in st.session_state and st.session_state.logged_in:
        username = st.session_state.username
        st.subheader("Budget Progress for This Month")

        planned_data, actual_data = get_budget_progress(username)

        for category, planned_amount in planned_data:
            actual_spent = actual_data.get(category, 0.0)
            progress = min(actual_spent / planned_amount, 1.0) if planned_amount > 0 else 0  # Prevent division by zero
            
            st.write(f"**{category}**: Planned {planned_amount}, Spent {actual_spent}")
            st.progress(progress)
    else:
        st.warning("Please log in first.")

# ✅ Get a summary of the current month's budget
def get_budget_summary(username):
    month = datetime.today().strftime("%Y-%m")  # Current month
    conn = sqlite3.connect("Process/users.db")
    cursor = conn.cursor()

    # Get the total planned budget and actual expenses for each category
    cursor.execute("""
    SELECT category, planned_amount FROM monthly_budget WHERE username = ? AND month = ?
    """, (username, month))
    planned_data = cursor.fetchall()

    cursor.execute("""
    SELECT category, SUM(amount) FROM daily_transactions 
    WHERE username = ? AND date LIKE ? 
    GROUP BY category
    """, (username, f"{month}-%"))
    actual_data = {row[0]: row[1] for row in cursor.fetchall()}

    total_planned = sum([row[1] for row in planned_data])
    total_spent = sum([actual_data.get(row[0], 0) for row in planned_data])

    conn.close()

    summary = {
        "total_planned": total_planned,
        "total_spent": total_spent,
        "remaining_budget": total_planned - total_spent
    }

    return summary