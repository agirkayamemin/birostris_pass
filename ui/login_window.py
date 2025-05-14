from PyQt5.QtWidgets import (QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, QCheckBox, QMessageBox)
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QFont
from logic.password_manager import create_user_account, verify_user_login
from utils.email_utils import send_verification_email
import random
import os

# --- Stylized button/field style ---
BTN_STYLE = '''
    QPushButton {
        background: transparent;
        color: #f5f6fa;
        border: 2px solid #f5f6fa;
        border-radius: 16px;
        font-size: 24px;
        font-family: Comic Sans MS, Comic Sans, cursive;
        padding: 12px 0;
        margin: 12px 0;
    }
    QPushButton:pressed {
        background: #00bcd4;
        color: #23272f;
    }
'''
FIELD_STYLE = '''
    QLineEdit {
        background: transparent;
        color: #f5f6fa;
        border: 2px solid #f5f6fa;
        border-radius: 16px;
        font-size: 24px;
        font-family: Comic Sans MS, Comic Sans, cursive;
        padding: 12px 0;
        margin: 12px 0;
        qproperty-alignment: AlignCenter;
    }
'''
LABEL_STYLE = 'color: #f5f6fa; font-size: 24px; font-family: Comic Sans MS, Comic Sans, cursive;'

REMEMBER_EMAIL_FILE = 'remembered_email.txt'

class WelcomeWindow(QWidget):
    show_signup = pyqtSignal()
    show_login = pyqtSignal()
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Welcome')
        self.setGeometry(600, 300, 320, 320)
        self.setStyleSheet('background: #23272f;')
        layout = QVBoxLayout()
        layout.addStretch(1)
        self.signup_btn = QPushButton('SIGN UP')
        self.signup_btn.setStyleSheet(BTN_STYLE)
        self.signup_btn.clicked.connect(self.show_signup)
        layout.addWidget(self.signup_btn)
        self.login_btn = QPushButton('LOGIN')
        self.login_btn.setStyleSheet(BTN_STYLE)
        self.login_btn.clicked.connect(self.show_login)
        layout.addWidget(self.login_btn)
        layout.addStretch(1)
        self.setLayout(layout)

class SignUpWindow(QWidget):
    signup_submitted = pyqtSignal(str, str, str)
    show_login = pyqtSignal(int)
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Sign Up')
        self.setGeometry(600, 300, 340, 380)
        self.setStyleSheet('background: #23272f;')
        layout = QVBoxLayout()
        self.email = QLineEdit()
        self.email.setPlaceholderText('EMAIL')
        self.email.setStyleSheet(FIELD_STYLE)
        layout.addWidget(self.email)
        self.name = QLineEdit()
        self.name.setPlaceholderText('NAME')
        self.name.setStyleSheet(FIELD_STYLE)
        layout.addWidget(self.name)
        self.password = QLineEdit()
        self.password.setPlaceholderText('PASSWORD')
        self.password.setEchoMode(QLineEdit.Password)
        self.password.setStyleSheet(FIELD_STYLE)
        layout.addWidget(self.password)
        self.submit_btn = QPushButton('SIGN UP')
        self.submit_btn.setStyleSheet(BTN_STYLE)
        self.submit_btn.clicked.connect(self.submit)
        layout.addWidget(self.submit_btn)
        # Add small login link at the bottom
        self.login_link = QPushButton('Login')
        self.login_link.setStyleSheet('''
            QPushButton {
                background: transparent;
                color: #00bcd4;
                border: none;
                font-size: 14px;
                font-family: Comic Sans MS, Comic Sans, cursive;
                text-decoration: underline;
            }
            QPushButton:pressed {
                color: #f5f6fa;
            }
        ''')
        self.login_link.clicked.connect(self._on_login_link_clicked)
        layout.addWidget(self.login_link, alignment=Qt.AlignHCenter)
        self.setLayout(layout)
    def submit(self):
        email = self.email.text().strip()
        name = self.name.text().strip()
        password = self.password.text().strip()
        if not email or not name or not password:
            QMessageBox.warning(self, 'Error', 'All fields are required!')
            return
        ok, result = create_user_account(email, name, password)
        if ok:
            user_id = result
            QMessageBox.information(self, 'Success', 'Account created! Please log in.')
            self.show_login.emit(user_id)
        else:
            QMessageBox.warning(self, 'Error', result)
    def _on_login_link_clicked(self):
        self.show_login.emit(-1)  # Use -1 or None to indicate no user_id

class EmailCodeWindow(QWidget):
    code_submitted = pyqtSignal(str)
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Email Code')
        self.setGeometry(600, 300, 320, 320)
        self.setStyleSheet('background: #23272f;')
        layout = QVBoxLayout()
        self.code = QLineEdit()
        self.code.setPlaceholderText('EMAIL-code')
        self.code.setStyleSheet(FIELD_STYLE)
        layout.addWidget(self.code)
        self.submit_btn = QPushButton('SUBMIT')
        self.submit_btn.setStyleSheet(BTN_STYLE)
        self.submit_btn.clicked.connect(self.submit)
        layout.addWidget(self.submit_btn)
        self.setLayout(layout)
    def submit(self):
        code = self.code.text().strip()
        if not code:
            QMessageBox.warning(self, 'Error', 'Code required!')
            return
        self.code_submitted.emit(code)

class LoginWindow(QWidget):
    login_success = pyqtSignal(int)
    show_signup = pyqtSignal()
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Login')
        self.setGeometry(600, 300, 340, 340)
        self.setStyleSheet('background: #23272f;')
        layout = QVBoxLayout()
        self.email = QLineEdit()
        self.email.setPlaceholderText('EMAIL')
        self.email.setStyleSheet(FIELD_STYLE)
        self.remember = QCheckBox('Remember This Email')
        self.remember.setStyleSheet(LABEL_STYLE)
        # Pre-fill email if remembered
        if os.path.exists(REMEMBER_EMAIL_FILE):
            with open(REMEMBER_EMAIL_FILE, 'r', encoding='utf-8') as f:
                remembered = f.read().strip()
                self.email.setText(remembered)
                self.remember.setChecked(True)
        layout.addWidget(self.email)
        self.password = QLineEdit()
        self.password.setPlaceholderText('Password')
        self.password.setEchoMode(QLineEdit.Password)
        self.password.setStyleSheet(FIELD_STYLE)
        layout.addWidget(self.password)
        self.login_btn = QPushButton('LOGIN')
        self.login_btn.setStyleSheet(BTN_STYLE)
        self.login_btn.clicked.connect(self.login)
        layout.addWidget(self.login_btn)
        # Add small sign up button at the bottom
        self.signup_link = QPushButton('Sign Up')
        self.signup_link.setStyleSheet('''
            QPushButton {
                background: transparent;
                color: #00bcd4;
                border: none;
                font-size: 14px;
                font-family: Comic Sans MS, Comic Sans, cursive;
                text-decoration: underline;
            }
            QPushButton:pressed {
                color: #f5f6fa;
            }
        ''')
        self.signup_link.clicked.connect(self.show_signup)
        layout.addWidget(self.signup_link, alignment=Qt.AlignHCenter)
        self.setLayout(layout)
    def login(self):
        email = self.email.text().strip()
        password = self.password.text().strip()
        if not email or not password:
            QMessageBox.warning(self, 'Error', 'Email and password required!')
            return
        ok, result = verify_user_login(email, password)
        if ok:
            user = result
            # Save email if remember is checked, else remove file
            if self.remember.isChecked():
                with open(REMEMBER_EMAIL_FILE, 'w', encoding='utf-8') as f:
                    f.write(email)
            else:
                if os.path.exists(REMEMBER_EMAIL_FILE):
                    os.remove(REMEMBER_EMAIL_FILE)
            self.login_success.emit(user.id)
        else:
            QMessageBox.warning(self, 'Error', result)

# --- Navigation logic for main.py ---
# In main.py, you will need to use these windows and connect their signals to navigate between them.
