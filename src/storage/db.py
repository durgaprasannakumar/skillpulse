import sqlite3
from datetime import datetime
from src.config import Config

def get_connection():
    return sqlite3.connect(Config.DB_PATH)

def init_db():
    conn = get_connection()
    with open("src/storage/schema.sql") as f:
        conn.executescript(f.read())
    conn.close()

def insert_jobs(jobs):
    conn = get_connection()
    now = datetime.utcnow().isoformat()
    for job in jobs:
        conn.execute("""
            INSERT OR IGNORE INTO jobs VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            job["id"], job["title"], job["company"],
            job["location"], job["description"],
            job["created"], now
        ))
    conn.commit()
    conn.close()
