import sqlite3

DB_NAME = "neuro_tutor.db"

def get_connection():
    return sqlite3.connect(DB_NAME)

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS concept_mastery (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        concept_name TEXT,
        mastery_score REAL,
        last_reviewed TEXT,
        times_quizzed INTEGER,
        times_correct INTEGER,
        notes TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS quiz_attempts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        concept_name TEXT,
        question TEXT,
        user_answer TEXT,
        score REAL,
        feedback TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()