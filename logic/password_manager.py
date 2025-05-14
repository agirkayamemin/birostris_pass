import sqlite3
from datetime import datetime
from models.models import DB_PATH, PasswordEntry, User, create_user, get_user_by_email, get_user_db_path
import hashlib

# --- User Account Management ---
def hash_pw(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def create_user_account(email, name, password):
    if get_user_by_email(email):
        return False, 'Email already registered.'
    password_hash = hash_pw(password)
    user_id = create_user(email, name, password_hash)
    return True, user_id

def verify_user_login(email, password):
    user = get_user_by_email(email)
    if not user:
        return False, 'User not found.'
    if user.password_hash != hash_pw(password):
        return False, 'Incorrect password.'
    return True, user

# --- Password Entry Management ---
def add_entry(user_id, site, username, plain_password, notes):
    db_path = get_user_db_path(user_id)
    now = datetime.now()
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('''INSERT INTO password_entries (site, username, password_enc, notes, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?)''',
              (site, username, plain_password, notes, now, now))
    conn.commit()
    conn.close()

def get_all_entries(user_id):
    db_path = get_user_db_path(user_id)
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('SELECT id, site, username, password_enc, notes, created_at, updated_at FROM password_entries')
    rows = c.fetchall()
    conn.close()
    entries = []
    for row in rows:
        entry = PasswordEntry(
            id=row[0],
            site=row[1],
            username=row[2],
            password_enc=row[3],
            notes=row[4],
            created_at=row[5],
            updated_at=row[6]
        )
        entries.append(entry)
    return entries

def update_entry(user_id, entry_id, site, username, plain_password, notes):
    db_path = get_user_db_path(user_id)
    now = datetime.now()
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('''UPDATE password_entries SET site=?, username=?, password_enc=?, notes=?, updated_at=? WHERE id=?''',
              (site, username, plain_password, notes, now, entry_id))
    conn.commit()
    conn.close()

def delete_entry(user_id, entry_id):
    db_path = get_user_db_path(user_id)
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('DELETE FROM password_entries WHERE id=?', (entry_id,))
    conn.commit()
    conn.close()
