import sqlite3
import bcrypt
from Process.database import get_db_connection  # ✅ Ensure this exists

# ✅ Register a new user
def register_user(name, email, password, region, currency):
    conn = get_db_connection()
    cursor = conn.cursor()

    hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode('utf-8')  # ✅ Ensure utf-8 encoding

    try:
        cursor.execute("INSERT INTO users (name, email, password, region, currency) VALUES (?, ?, ?, ?, ?)", 
                       (name, email, hashed_password, region, currency))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False  # Email already exists
    finally:
        conn.close()

# ✅ Login function
def login_user(email, password):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id, name, password FROM users WHERE email=?", (email,))
    user = cursor.fetchone()

    if user and bcrypt.checkpw(password.encode(), user[2].encode()):  # ✅ Ensure password comparison works
        return {"id": user[0], "name": user[1]}
    
    conn.close()
    return None

# ✅ Password reset function
def reset_password(email, new_password):
    conn = get_db_connection()
    cursor = conn.cursor()

    hashed_password = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt()).decode('utf-8')  # ✅ Encode properly
    cursor.execute("UPDATE users SET password=? WHERE email=?", (hashed_password, email))
    conn.commit()
    conn.close()  
