# Birostris Pass - Password Manager

A modern, secure, and user-friendly password manager desktop app built with Python and PyQt5.

## Features
- Master password protection
- Encrypted local storage (SQLite + cryptography)
- Add, edit, and delete password entries
- Password generator (minimal and customizable)
- Modern dark theme UI
- Copy username/password to clipboard
- All actions accessible via a clean context menu

## Setup
1. **Clone the repository:**
   ```sh
   git clone https://github.com/yourusername/birostris_pass.git
   cd birostris_pass
   ```
2. **Create a virtual environment (optional but recommended):**
   ```sh
   python -m venv .venv
   .venv\Scripts\activate  # On Windows
   ```
3. **Install dependencies:**
   ```sh
   pip install -r requirements.txt
   ```

## Usage
Run the app with:
```sh
python main.py
```

- Set a master password on first launch.
- Add, edit, and manage your passwords securely.

## Notes
- Your data is stored locally and encrypted.
- The database file is at `data/database.db` (excluded from git).
- For any issues or feature requests, open an issue on GitHub. 