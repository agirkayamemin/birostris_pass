import sqlite3
from datetime import datetime
from models.models import DB_PATH, PasswordEntry, User
from logic.encryption import hash_password, verify_password, encrypt_password, decrypt_password

# --- Master Password Management ---
def is_master_password_set():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT COUNT(*) FROM users')
    result = c.fetchone()[0]
    conn.close()
    return result > 0

def set_master_password(password: str):
    password_hash, salt = hash_password(password)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('INSERT INTO users (password_hash, salt) VALUES (?, ?)', (password_hash, salt))
    conn.commit()
    conn.close()

def verify_master_password(password: str):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT password_hash, salt FROM users LIMIT 1')
    row = c.fetchone()
    conn.close()
    if row:
        return verify_password(password, row[0], row[1])
    return False

def get_user_salt():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT salt FROM users LIMIT 1')
    row = c.fetchone()
    conn.close()
    return row[0] if row else None

# --- Password Entry Management ---
def add_entry(site, username, plain_password, notes, master_password):
    salt = get_user_salt()
    password_enc = encrypt_password(plain_password, master_password, salt)
    now = datetime.now()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''INSERT INTO password_entries (site, username, password_enc, notes, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?)''',
              (site, username, password_enc, notes, now, now))
    conn.commit()
    conn.close()

def get_all_entries(master_password):
    salt = get_user_salt()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT id, site, username, password_enc, notes, created_at, updated_at FROM password_entries')
    rows = c.fetchall()
    conn.close()
    entries = []
    for row in rows:
        try:
            password = decrypt_password(row[3], master_password, salt)
        except Exception:
            password = '<decryption failed>'
        entry = PasswordEntry(
            id=row[0],
            site=row[1],
            username=row[2],
            password_enc=password,  # decrypted password for UI use
            notes=row[4],
            created_at=row[5],
            updated_at=row[6]
        )
        entries.append(entry)
    return entries

def update_entry(entry_id, site, username, plain_password, notes, master_password):
    salt = get_user_salt()
    password_enc = encrypt_password(plain_password, master_password, salt)
    now = datetime.now()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''UPDATE password_entries SET site=?, username=?, password_enc=?, notes=?, updated_at=? WHERE id=?''',
              (site, username, password_enc, notes, now, entry_id))
    conn.commit()
    conn.close()

def delete_entry(entry_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('DELETE FROM password_entries WHERE id=?', (entry_id,))
    conn.commit()
    conn.close()
