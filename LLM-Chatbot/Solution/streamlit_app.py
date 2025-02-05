import sys
import os
import streamlit as st
import time
from groq import Groq
import sqlite3
import datetime
import requests
import pandas as pd
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from Process.auth import login_user, register_user

from Process.database import init_db
from Process.budget import update_budget, get_budget_summary

# Initialize database
init_db()

# 🚀 Connect to Database

def get_db_connection():
    db_path = os.path.join(os.getcwd(), "Process", "users.db")  # Full path to the db
    return sqlite3.connect(db_path, check_same_thread=False)

# Load API Key
GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
groq_client = Groq(api_key=GROQ_API_KEY)

# System Message for Chatbot Personality
system_message = (
    "You are a highly relatable budget assistant for teenagers and young adults."
    "Your name is ProFi (short for ProFi-Budget Buddy)."
    "Your ultimate goal is to empower users to manage their budgets and achieve their financial goals while feeling inspired and supported."
    "You have a friendly, supportive, and motivational personality designed to make financial management approachable and engaging."
    "You use a conversational tone with light humor and empathetic responses to help users feel understood and encouraged."
    "You celebrate small wins, offer gentle nudges to stay on track, and adapt your tone to users’ emotions, whether they’re facing setbacks or achieving milestones."
    "You are proactive in offering suggestions, flexible in adjusting to user preferences, and use relatable touches like emojis sparingly to add personality without being overwhelming."
    "REMEMBER: Always keep your response short and concise - Less than 200 words."
)

system_prompt = {
    "role": "system",
    "content": system_message
}
# ---------------- Chatbot Functionality ----------------
def get_response(chat_history):
    response = groq_client.chat.completions.create(
        model="llama3-70b-8192",
        messages=chat_history,
        max_tokens=300,
        temperature=1.2
    )

    chat_response = response.choices[0].message.content

    # Simulated typing effect
    for word in chat_response.split():
        yield word + " "
        time.sleep(0.05)

def main():
   st.set_page_config(page_title="ProFi-Budget Buddy", layout="wide")
   st.title("ProFi-Budget Buddy")
   with st.expander("About ProFi"):
        st.write("Meet Your Budget & Motivation Buddy! Your personal assistant for managing finances and staying motivated. 💼💪")

if "messages" not in st.session_state:
        st.session_state.messages = [system_prompt]

for message in st.session_state.messages:
        if message != system_prompt:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

if prompt := st.chat_input("Talk to ProFi"):
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.chat_message("user"):
            st.markdown(prompt)

        response = get_response(st.session_state.messages)
        
        with st.chat_message("assistant"):
            chat_response = st.write_stream(response)
        
        st.session_state.messages.append({"role": "assistant", "content": chat_response})



# --- Utility Functions ---
def get_weather(city):
    API_KEY = st.secrets["OPENWEATHER_API_KEY"]  # Replace with actual weather API key
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
    
    try:
        response = requests.get(url).json()
        temp = response["main"]["temp"]
        return f"🌤 {city}: {temp}°C"
    except:
        return "Weather data unavailable"

# --- Sidebar Navigation ---
menu = ["Login", "Register", "Dashboard", "Admin Panel"]
choice = st.sidebar.selectbox("Navigation", menu)

# --- Login Page ---
if choice == "Login":
    st.title("Login to ProFi")

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        user = login_user(email, password)
        if user:
            st.session_state["user"] = user
            st.success(f"Welcome, {user['name']}!")
            st.experimental_rerun()
        else:
            st.error("Invalid email or password.")

# --- Registration Page ---
elif choice == "Register":
    st.title("Register for ProFi")

    name = st.text_input("Name")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    region = st.text_input("Please enter your region")
    currency = st.text_input("Please enter your preferred Currency")

    if st.button("Register"):
        if register_user(name, email, password, region, currency):
            st.success("Registration successful! Please log in.")
            st.experimental_rerun()
        else:
            st.error("Email already exists.")

# --- Dashboard ---
elif choice == "Dashboard":
    if "user" not in st.session_state:
        st.warning("Please log in first.")
        st.stop()

    user = st.session_state["user"]
    st.title(f"Welcome, {user['name']}! 🎉")

    # Date and Time Display
    col1, col2 = st.columns([2, 1])
    col1.subheader(f"📅 {datetime.datetime.now().strftime('%A, %B %d, %Y')}")
    
    # Weather Display
    city = col2.text_input("Enter your city for weather update", value="New York")
    col2.write(get_weather(city))

   

    # Budget Summary
    conn = sqlite3.connect("process/.streamlit/users.db", check_same_thread=False)
    cursor = conn.cursor()

    # Get today's date
    today_date = datetime.today().strftime('%Y-%m-%d')

    # Sidebar for Budget Inputs
    st.sidebar.header("📅 Set Your Budget")
    planned_income = st.sidebar.number_input("Planned Income ($)", min_value=0.0, value=0.0, step=100.0)
    planned_expenses = st.sidebar.number_input("Planned Expenses ($)", min_value=0.0, value=0.0, step=50.0)
    actual_income = st.sidebar.number_input("Actual Income ($)", min_value=0.0, value=0.0, step=100.0)
    actual_expenses = st.sidebar.number_input("Actual Expenses ($)", min_value=0.0, value=0.0, step=50.0)

    # Calculate savings
    planned_savings = planned_income - planned_expenses
    actual_savings = actual_income - actual_expenses

    # Submit button to save budget
    if st.sidebar.button("Save Budget"):
      update_budget(today_date, planned_income, planned_expenses, planned_savings, actual_income, actual_expenses, actual_savings)
    st.sidebar.success("✅ Budget updated successfully!")

    # Display Budget Summary
    st.subheader("📈 Budget Overview")
    budget_summary = get_budget_summary()

    if budget_summary:
      st.write(f"### Today's Budget ({today_date})")
      st.metric(label="Planned Income", value=f"${budget_summary['planned_income']:.2f}")
      st.metric(label="Planned Expenses", value=f"${budget_summary['planned_expenses']:.2f}")
      st.metric(label="Planned Savings", value=f"${budget_summary['planned_savings']:.2f}")

      st.write("### 📌 Actual Financials")
      st.metric(label="Actual Income", value=f"${budget_summary['actual_income']:.2f}")
      st.metric(label="Actual Expenses", value=f"${budget_summary['actual_expenses']:.2f}")
      st.metric(label="Actual Savings", value=f"${budget_summary['actual_savings']:.2f}")

    else:
     st.warning("No budget data found for today. Please enter your budget in the sidebar.")

    # Close Database Connection
    conn.close()


    # Financial Goals
    st.subheader("🎯 Financial Goals")
    conn = sqlite3.connect("Process/users.db")
    cursor = conn.cursor()
    cursor.execute("SELECT goal_name, target_amount, current_amount FROM financial_goals WHERE user_id=?", (user["id"],))
    goals = cursor.fetchall()
    conn.close()

    if goals:
        for goal in goals:
            st.progress(goal[2] / goal[1])
            st.text(f"{goal[0]}: {goal[2]}/{goal[1]} {user['currency']}")
    else:
        st.info("No financial goals set yet.")

    # Budget Analytics
    st.subheader("📊 Expense Trends")
    df = pd.DataFrame(
        {
            "Category": ["Food", "Rent", "Entertainment", "Savings"],
            "Amount": [400, 1200, 200, 500],
        }
    )
    st.bar_chart(df.set_index("Category"))

# --- Logout Button ---
if "user" in st.session_state:
    st.sidebar.button("Logout", on_click=lambda: st.session_state.pop("user"))