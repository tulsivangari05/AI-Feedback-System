import sqlite3
from datetime import datetime
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_NAME = os.path.join(BASE_DIR, "reviews.db")


def get_connection():
    return sqlite3.connect(DB_NAME)

def init_db():
    """Initialize the reviews database and table"""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_rating INTEGER,
            user_review TEXT,
            ai_response TEXT,
            ai_summary TEXT,
            ai_action TEXT,
            created_at TEXT
        )
    """)
    conn.commit()
    conn.close()

def save_review(rating, review, ai_response, summary, action):
    """Save a review submission to the DB"""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO reviews 
        (user_rating, user_review, ai_response, ai_summary, ai_action, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        rating,
        review,
        ai_response,
        summary,
        action,
        datetime.utcnow().isoformat()
    ))
    conn.commit()
    conn.close()

def get_all_reviews():
    """Retrieve all reviews, latest first"""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT user_rating, user_review, ai_response, ai_summary, ai_action, created_at
        FROM reviews
        ORDER BY created_at DESC
    """)
    rows = cur.fetchall()
    conn.close()

    return [
        {
            "rating": r[0],
            "review": r[1],
            "ai_response": r[2],
            "summary": r[3],
            "action": r[4],
            "created_at": r[5]
        }
        for r in rows
    ]

def get_filtered_reviews(search="", rating=None, page=1, per_page=5):
    conn = get_connection()
    cur = conn.cursor()

    query = """
        SELECT user_rating, user_review, ai_response, ai_summary, ai_action, created_at
        FROM reviews
        WHERE 1=1
    """
    params = []

    if search:
        query += " AND user_review LIKE ?"
        params.append(f"%{search}%")

    if rating:
        query += " AND user_rating = ?"
        params.append(rating)

    query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
    params.extend([per_page, (page - 1) * per_page])

    cur.execute(query, params)
    rows = cur.fetchall()

    conn.close()

    return [
        {
            "rating": r[0],
            "review": r[1],
            "ai_response": r[2],
            "summary": r[3],
            "action": r[4],
            "created_at": r[5]
        }
        for r in rows
    ]


# import sqlite3

# conn = sqlite3.connect("reviews.db")
# cur = conn.cursor()

# cur.execute("DELETE FROM reviews;")  # deletes all rows
# conn.commit()

# conn.close()

# print("All review data deleted successfully.")





