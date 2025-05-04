from dataclasses import dataclass
from datetime import datetime
import sqlite3

DB_PATH = 'data/database.db'

@dataclass
class User:
    id: int
    password_hash: str
    salt: str

@dataclass
class PasswordEntry:
    id: int
    site: str
    username: str
    password_enc: str  # Encrypted password
    notes: str
    created_at: datetime
    updated_at: datetime

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # Create users table
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            password_hash TEXT NOT NULL,
            salt TEXT NOT NULL
        )
    ''')
    # Create password entries table
    c.execute('''
        CREATE TABLE IF NOT EXISTS password_entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            site TEXT NOT NULL,
            username TEXT NOT NULL,
            password_enc TEXT NOT NULL,
            notes TEXT,
            created_at DATETIME NOT NULL,
            updated_at DATETIME NOT NULL
        )
    ''')
    conn.commit()
    conn.close()
