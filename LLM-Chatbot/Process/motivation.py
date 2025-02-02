from database import get_db_connection
import random

# ✅ Add a new motivational quote
def add_quote(category, quote):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("INSERT INTO motivational_quotes (category, quote) VALUES (?, ?)", (category, quote))
    conn.commit()
    conn.close()

# ✅ Fetch a motivational quote based on category
def get_motivational_quote(category=None):
    conn = get_db_connection()
    cursor = conn.cursor()

    if category:
        cursor.execute("SELECT quote FROM motivational_quotes WHERE category = ?", (category,))
    else:
        cursor.execute("SELECT quote FROM motivational_quotes")

    quotes = cursor.fetchall()
    conn.close()

    return random.choice(quotes)[0] if quotes else "Keep pushing forward!"