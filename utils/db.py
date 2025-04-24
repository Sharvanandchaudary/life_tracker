import sqlite3
import os
from datetime import date

# Ensure data folder exists
DB_FOLDER = "data"
os.makedirs(DB_FOLDER, exist_ok=True)

DB_PATH = os.path.join(DB_FOLDER, "life.db")

def connect_db():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def init_db():
    conn = connect_db()
    cursor = conn.cursor()

    # Create study_logs table (support multiple topics per day)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS study_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            log_date TEXT,
            topic TEXT,
            summary TEXT,
            duration REAL
        )
    ''')

    # Create job applications table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS job_apps (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            log_date TEXT NOT NULL,
            count INTEGER NOT NULL
        )
    ''')

    # Create learn_list table (Things to Learn)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS learn_list (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            log_date TEXT,
            topic TEXT
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
