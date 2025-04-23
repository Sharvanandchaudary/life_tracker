import sqlite3
from datetime import date

DB_PATH = "data/life.db"

def connect_db():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def init_db():
    conn = connect_db()
    cursor = conn.cursor()

    # Create study_logs table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS study_logs (
            log_date TEXT PRIMARY KEY,
            topic TEXT,
            summary TEXT,
            duration REAL,
            interview_given TEXT,
            book_read TEXT,
            next_plan TEXT
        )
    ''')

    # Create finance_logs table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS finance_logs (
            log_date TEXT,
            income REAL,
            expense REAL
        )
    ''')

    # Create debts table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS debts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT,
            name TEXT,
            amount REAL
        )
    ''')

    # Create sleep_logs table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sleep_logs (
            log_date TEXT PRIMARY KEY,
            bed_time TEXT,
            wake_time TEXT,
            sleep_quality INTEGER,
            core_sleep TEXT,
            duration REAL
        )
    ''')

    # Create diary_logs table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS diary_logs (
            log_date TEXT PRIMARY KEY,
            entry TEXT
        )
    ''')

    conn.commit()
    conn.close()

def get_today_log_status(table_name):
    conn = connect_db()
    cursor = conn.cursor()
    today = str(date.today())
    cursor.execute(f"SELECT 1 FROM {table_name} WHERE log_date = ?", (today,))
    result = cursor.fetchone()
    conn.close()
    return result is not None
