from dataclasses import dataclass
from datetime import datetime
import sqlite3
import hashlib
import os

DB_PATH = 'data/database.db'  # Only for users table

@dataclass
class User:
    id: int
    email: str
    name: str
    password_hash: str

@dataclass
class PasswordEntry:
    id: int
    site: str
    username: str
    password_enc: str  # Encrypted password or plain
    notes: str
    created_at: datetime
    updated_at: datetime

def init_db():
    os.makedirs('data', exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # Create users table
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            password_hash TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def get_user_db_path(user_id):
    return f'data/user_{user_id}.db'

def init_user_db(user_id):
    db_path = get_user_db_path(user_id)
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
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

def create_user(email, name, password_hash):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('INSERT INTO users (email, name, password_hash) VALUES (?, ?, ?)', (email, name, password_hash))
    user_id = c.lastrowid
    conn.commit()
    conn.close()
    init_user_db(user_id)
    return user_id

def get_user_by_email(email):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT id, email, name, password_hash FROM users WHERE email=?', (email,))
    row = c.fetchone()
    conn.close()
    if row:
        return User(*row)
    return None
