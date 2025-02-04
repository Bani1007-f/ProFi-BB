import sqlite3
import bcrypt
import os

# ✅ Function to connect to SQLite database
def get_db_connection():
    db_path = os.path.join(os.getcwd(), "LLM-Chatbot", "Process", "users.db")  # ✅ Use the correct path

    # Debugging: Print database path
    print(f"🔍 Attempting to connect to: {db_path}")

    return sqlite3.connect(db_path, check_same_thread=False)

# ✅ Debugging function for database initialization
def init_db():
    try:
        # ✅ Ensure 'Process/' folder exists
        db_folder = os.path.join("LLM-Chatbot", "Process")  # ✅ Corrected variable name
        if not os.path.exists(db_folder):
            print("⚠️ 'Process/' folder missing! Creating it now...")
            os.makedirs(db_folder)

        db_path = os.path.join(db_folder, "users.db")
        if not os.path.exists(db_path):
            print("⚠️ Database file does NOT exist. It will be created now.")
            open(db_path, "w").close()  # ✅ Create an empty database file

        conn = get_db_connection()
        cursor = conn.cursor()

        # ✅ Create Users Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT,
            email TEXT UNIQUE,
            region TEXT,
            currency TEXT
        )
        """)

        # ✅ Create Financial Goals Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS financial_goals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            goal_name TEXT,
            target_amount REAL,
            current_savings REAL DEFAULT 0.0,
            deadline TEXT
        )
        """)

        # ✅ Create User Interactions Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_interactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            question TEXT,
            bot_response TEXT
        )
        """)

        # ✅ Create Admins Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS admins (
            username TEXT PRIMARY KEY  -- Admin username
        )
        """)

        # ✅ Create Motivation Table (for mood-based quotes)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS motivational_quotes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            mood_level INTEGER CHECK(mood_level BETWEEN 0 AND 5),  -- 0 = Sad, 5 = Happy
            quote TEXT
        )
        """)

        conn.commit()
        conn.close()
        print("✅ Database initialized successfully!")

    except sqlite3.OperationalError as e:
        print(f"❌ SQLite OperationalError: {e}")

    except Exception as e:
        print(f"❌ General Error: {e}")

# ✅ Run database initialization
if __name__ == "__main__":
    init_db()

# 🚀 Add User
def add_user(username, password, email, region, currency):
    conn = get_db_connection()
    cursor = conn.cursor()
    hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode('utf-8')  # ✅ Store as string

    try:
        cursor.execute("INSERT INTO users (username, password, email, region, currency) VALUES (?, ?, ?, ?, ?)", 
                       (username, hashed_pw, email, region, currency))
        conn.commit()
    except sqlite3.IntegrityError:
        return "Username or email already exists."
    
    conn.close()
    return "User registered successfully!"

# 🚀 Check User Credentials
def check_user(username, password):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT password FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()

    if user and bcrypt.checkpw(password.encode(), user[0].encode()):  # ✅ Fix password check
        return True
    return False

# 🚀 Add Budget Category
def add_budget_category(username, category_type, category_name, planned_amount):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("INSERT INTO budget_categories (username, category_type, category_name, planned_amount) VALUES (?, ?, ?, ?)", 
                   (username, category_type, category_name, planned_amount))
    conn.commit()
    conn.close()

# 🚀 Log Income/Expense Transaction
def log_transaction(username, category_type, category_name, amount):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("INSERT INTO transactions (username, category_type, category_name, amount) VALUES (?, ?, ?, ?)", 
                   (username, category_type, category_name, amount))
    conn.commit()
    conn.close()

# 🚀 Get Budget Summary
def get_budget_summary(username):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT SUM(amount) FROM transactions WHERE username = ? AND category_type = 'Income'", (username,))
    total_income = cursor.fetchone()[0] or 0.0

    cursor.execute("SELECT SUM(amount) FROM transactions WHERE username = ? AND category_type = 'Expense'", (username,))
    total_expenses = cursor.fetchone()[0] or 0.0

    conn.close()
    return total_income, total_expenses, total_income - total_expenses

# 🚀 Set Financial Goal
def add_financial_goal(username, goal_name, target_amount, deadline):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("INSERT INTO financial_goals (username, goal_name, target_amount, deadline) VALUES (?, ?, ?, ?)", 
                   (username, goal_name, target_amount, deadline))
    conn.commit()
    conn.close()

# 🚀 Track Savings
def update_savings(username, goal_name, amount):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("UPDATE financial_goals SET current_savings = current_savings + ? WHERE username = ? AND goal_name = ?", 
                   (amount, username, goal_name))
    conn.commit()
    conn.close()