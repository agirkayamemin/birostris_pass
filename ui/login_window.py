from PyQt5.QtWidgets import (QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QMessageBox)
from PyQt5.QtCore import pyqtSignal
from logic.password_manager import is_master_password_set, set_master_password, verify_master_password

class LoginWindow(QWidget):
    login_success = pyqtSignal(str)  # emits the master password on success

    def __init__(self):
        super().__init__()
        self.setWindowTitle('Password Manager - Login')
        self.setGeometry(600, 300, 350, 180)
        self.init_ui()

    def init_ui(self):
        self.label = QLabel()
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.button = QPushButton()
        self.button.clicked.connect(self.handle_action)

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.password_input)
        layout.addWidget(self.button)
        self.setLayout(layout)

        if is_master_password_set():
            self.label.setText('Enter Master Password:')
            self.button.setText('Unlock')
            self.is_setup = False
        else:
            self.label.setText('Set a Master Password:')
            self.button.setText('Set Password')
            self.is_setup = True

    def handle_action(self):
        password = self.password_input.text()
        if not password:
            QMessageBox.warning(self, 'Error', 'Password cannot be empty!')
            return
        if self.is_setup:
            set_master_password(password)
            QMessageBox.information(self, 'Success', 'Master password set!')
            self.login_success.emit(password)
        else:
            if verify_master_password(password):
                self.login_success.emit(password)
            else:
                QMessageBox.critical(self, 'Error', 'Incorrect master password!')
