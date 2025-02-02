import sqlite3
import streamlit as st
from Process.database import get_db_connection

# ✅ Check if a user is an admin
def is_admin(username):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM admins WHERE username = ?", (username,))
    result = cursor.fetchone()
    conn.close()
    return result is not None  # Returns True if user is an admin

# ✅ Add a new admin user (Manually run once)
def add_admin(username):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO admins (username) VALUES (?)", (username,))
    conn.commit()
    conn.close()
    st.success(f"{username} has been added as an admin!")

# ✅ Add a new quote
def add_quote(category, quote):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO motivational_quotes (category, quote) VALUES (?, ?)", (category, quote))
    conn.commit()
    conn.close()

# ✅ Fetch all quotes for admin management
def get_all_quotes():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, category, quote FROM motivational_quotes")
    quotes = cursor.fetchall()
    conn.close()
    return quotes

# ✅ Delete a quote (Admin-only)
def delete_quote(quote_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM motivational_quotes WHERE id = ?", (quote_id,))
    conn.commit()
    conn.close()
    st.success("Quote deleted successfully!")

# ✅ Admin Panel UI
def admin_panel():
    if "logged_in" in st.session_state and st.session_state.logged_in:
        username = st.session_state.username

        if is_admin(username):
            st.title("Admin Panel - Manage Motivational Quotes")

            # Add New Quote
            st.subheader("Add a New Motivational Quote")
            category = st.selectbox("Select Category", ["saving", "budgeting", "debt management", "success"])
            quote = st.text_area("Enter Quote")

            if st.button("Add Quote"):
                add_quote(category, quote)
                st.success("Quote added successfully!")
                st.experimental_rerun()

            # View Existing Quotes
            st.subheader("Existing Quotes")
            quotes = get_all_quotes()
            for q_id, q_category, q_text in quotes:
                st.write(f"📌 **Category:** {q_category}")
                st.write(f"💬 {q_text}")
                if st.button(f"Delete Quote {q_id}", key=f"delete_{q_id}"):
                    delete_quote(q_id)
                    st.experimental_rerun()  # ✅ Move outside the `if`

        else:
            st.warning("You are not authorized to access the admin panel.")
    else:
        st.warning("Please log in first.")