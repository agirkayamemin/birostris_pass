from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QLineEdit, QLabel, QMessageBox, QInputDialog, QDialog, QSpinBox, QCheckBox, QFormLayout, QDialogButtonBox, QApplication, QStyle, QMenu, QSizePolicy, QSpacerItem)
from logic.password_manager import get_all_entries, add_entry, update_entry, delete_entry
from utils.helpers import generate_password
from PyQt5.QtGui import QClipboard, QFont, QColor, QPainter, QBrush, QPen
from PyQt5.QtCore import Qt
from models.models import get_user_by_email, User
import sqlite3
import datetime

class AvatarLabel(QLabel):
    def __init__(self, initials, parent=None):
        super().__init__(parent)
        self.initials = initials
        self.setFixedSize(48, 48)
        self.setFont(QFont('Arial', 16, QFont.Bold))
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet('''
            border-radius: 12px;
            background: #8b8892;
            color: #fff;
            font: bold 16px "Segoe UI", "Arial";
        ''')
        self.setText(initials)

class EntryCard(QWidget):
    def __init__(self, entry, parent, on_edit, on_delete, on_copy_user, on_copy_pw):
        super().__init__(parent)
        self.entry = entry
        self.setStyleSheet('''
            QWidget {
                background: #23272f;
                border-radius: 12px;
                margin-bottom: 14px;
                border: 1.5px solid #2c313c;
            }
            QWidget:hover {
                border: 1.5px solid #00bcd4;
                background: #263238;
            }
        ''')
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 8, 16, 8)
        layout.setSpacing(12)
        avatar = AvatarLabel(self.get_initials(entry.site))
        layout.addWidget(avatar)
        text_layout = QVBoxLayout()
        text_layout.setSpacing(0)
        # Title (site)
        title = QLabel(entry.site)
        title.setStyleSheet('color: white; font: bold 17px "Segoe UI", "Arial";')
        # Email/username
        subtitle = QLabel(entry.username)
        subtitle.setStyleSheet('color: #b0b3b8; font: 13px "Segoe UI", "Arial";')
        text_layout.addWidget(title)
        text_layout.addWidget(subtitle)
        text_layout.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        layout.addLayout(text_layout)
        layout.addStretch(1)
        # Menu button
        menu_btn = QPushButton('⋮')
        menu_btn.setFixedSize(36, 36)
        menu_btn.setStyleSheet('font-size: 22px; background: #263238; color: #00bcd4; border: none; border-radius: 18px;')
        menu = QMenu()
        menu.setStyleSheet('''
            QMenu { background: #2c313c; color: #f5f6fa; border: 1px solid #444; }
            QMenu::item { padding: 8px 24px; }
            QMenu::item:selected { background: #00bcd4; color: #23272f; }
        ''')
        copy_user_action = menu.addAction('Copy Username')
        copy_pw_action = menu.addAction('Copy Password')
        menu.addSeparator()
        edit_action = menu.addAction('Edit')
        delete_action = menu.addAction('Delete')
        def on_menu_action(action):
            if action == copy_user_action:
                on_copy_user(entry)
            elif action == copy_pw_action:
                on_copy_pw(entry)
            elif action == edit_action:
                on_edit(entry)
            elif action == delete_action:
                on_delete(entry)
        menu.triggered.connect(on_menu_action)
        menu_btn.setMenu(menu)
        layout.addWidget(menu_btn)
    def get_initials(self, text):
        parts = text.strip().split()
        if len(parts) == 1:
            return (parts[0][:2]).capitalize()
        return (parts[0][0] + parts[1][0]).upper()
    def get_last_used(self, updated_at):
        try:
            dt = datetime.datetime.fromisoformat(str(updated_at))
            delta = datetime.datetime.now() - dt
            if delta.days > 0:
                return f"{delta.days} days ago"
            elif delta.seconds > 3600:
                return f"{delta.seconds // 3600} hours ago"
            elif delta.seconds > 60:
                return f"{delta.seconds // 60} minutes ago"
            else:
                return "Less than a minute ago"
        except Exception:
            return str(updated_at)

class EntryDialog(QDialog):
    def __init__(self, parent=None, site='', username='', password='', notes='', is_edit=False):
        super().__init__(parent)
        self.setWindowTitle('Edit Entry' if is_edit else 'Add Entry')
        self.setFixedWidth(400)
        self.setStyleSheet(parent.styleSheet())
        layout = QFormLayout(self)
        self.site_input = QLineEdit(site)
        self.site_input.setPlaceholderText('Title (required)')
        layout.addRow(self.site_input)
        layout.addRow(QLabel('Login Details'))
        self.username_input = QLineEdit(username)
        self.username_input.setPlaceholderText('Email or Username')
        layout.addRow(self.username_input)
        pw_layout = QHBoxLayout()
        self.password_input = QLineEdit(password)
        self.password_input.setPlaceholderText('Password')
        self.password_input.setEchoMode(QLineEdit.Password)
        self.show_pw_btn = QPushButton()
        self.show_pw_btn.setCheckable(True)
        self.show_pw_btn.setFixedWidth(30)
        self.show_pw_btn.setText('👁️')
        self.show_pw_btn.clicked.connect(self.toggle_password)
        pw_layout.addWidget(self.password_input)
        pw_layout.addWidget(self.show_pw_btn)
        pw_widget = QWidget()
        pw_widget.setLayout(pw_layout)
        layout.addRow(pw_widget)
        self.gen_btn = QPushButton('Generate Password')
        self.gen_btn.setFlat(True)
        self.gen_btn.setStyleSheet('color: #00bcd4; text-align: right;')
        self.gen_btn.clicked.connect(self.generate_password)
        layout.addRow(self.gen_btn)
        self.notes_input = QLineEdit(notes)
        self.notes_input.setPlaceholderText('Notes (optional)')
        layout.addRow(self.notes_input)
        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        layout.addRow(self.button_box)
    def toggle_password(self):
        if self.show_pw_btn.isChecked():
            self.password_input.setEchoMode(QLineEdit.Normal)
        else:
            self.password_input.setEchoMode(QLineEdit.Password)
    def generate_password(self):
        pwd = generate_password()
        self.password_input.setText(pwd)
    def get_data(self):
        return (self.site_input.text(), self.username_input.text(), self.password_input.text(), self.notes_input.text())

class PasswordGeneratorDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Password Generator')
        self.setFixedWidth(400)
        self.setStyleSheet(parent.styleSheet())
        self.is_custom = False
        self.init_ui()

    def init_ui(self):
        self.layout = QVBoxLayout(self)
        # Toggle for minimal/custom
        self.toggle_btn = QPushButton('Customize')
        self.toggle_btn.setCheckable(True)
        self.toggle_btn.setChecked(False)
        self.toggle_btn.clicked.connect(self.toggle_mode)
        self.layout.addWidget(self.toggle_btn, alignment=Qt.AlignRight)
        # Password display
        pw_layout = QHBoxLayout()
        self.pw_field = QLineEdit()
        self.pw_field.setReadOnly(True)
        self.pw_field.setStyleSheet('font-size: 18px;')
        pw_layout.addWidget(self.pw_field)
        self.copy_btn = QPushButton('📋')
        self.copy_btn.setFixedWidth(40)
        self.copy_btn.clicked.connect(self.copy_password)
        pw_layout.addWidget(self.copy_btn)
        self.layout.addLayout(pw_layout)
        # Generate button
        self.gen_btn = QPushButton('Generate')
        self.gen_btn.clicked.connect(self.generate)
        self.layout.addWidget(self.gen_btn)
        # Customization options
        self.options_widget = QWidget()
        options_layout = QFormLayout(self.options_widget)
        self.length_spin = QSpinBox()
        self.length_spin.setRange(8, 64)
        self.length_spin.setValue(16)
        self.upper_cb = QCheckBox('Uppercase')
        self.upper_cb.setChecked(True)
        self.lower_cb = QCheckBox('Lowercase')
        self.lower_cb.setChecked(True)
        self.digits_cb = QCheckBox('Digits')
        self.digits_cb.setChecked(True)
        self.symbols_cb = QCheckBox('Symbols')
        self.symbols_cb.setChecked(True)
        options_layout.addRow('Length:', self.length_spin)
        options_layout.addRow(self.upper_cb)
        options_layout.addRow(self.lower_cb)
        options_layout.addRow(self.digits_cb)
        options_layout.addRow(self.symbols_cb)
        self.layout.addWidget(self.options_widget)
        self.options_widget.hide()
        self.generate()

    def toggle_mode(self):
        self.is_custom = not self.is_custom
        if self.is_custom:
            self.options_widget.show()
            self.toggle_btn.setText('Minimal')
        else:
            self.options_widget.hide()
            self.toggle_btn.setText('Customize')
        self.generate()

    def generate(self):
        from utils.helpers import generate_password
        try:
            if self.is_custom:
                pwd = generate_password(
                    length=self.length_spin.value(),
                    use_upper=self.upper_cb.isChecked(),
                    use_lower=self.lower_cb.isChecked(),
                    use_digits=self.digits_cb.isChecked(),
                    use_symbols=self.symbols_cb.isChecked()
                )
            else:
                pwd = generate_password()
            self.pw_field.setText(pwd)
        except ValueError as e:
            self.pw_field.setText('')
            QMessageBox.warning(self, 'Error', str(e))

    def copy_password(self):
        QApplication.clipboard().setText(self.pw_field.text(), QClipboard.Clipboard)
        QMessageBox.information(self, 'Copied', 'Password copied to clipboard!')

class MainWindow(QWidget):
    def __init__(self, user_id, show_login_callback=None):
        super().__init__()
        self.user_id = user_id
        self.user_name = self.get_user_name()
        self.show_login_callback = show_login_callback
        self.setWindowTitle('Birostris Pass')
        self.setGeometry(200, 100, 1100, 700)
        self.init_ui()
        self.load_entries()

    def get_user_name(self):
        from models.models import DB_PATH
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('SELECT name FROM users WHERE id=?', (self.user_id,))
        row = c.fetchone()
        conn.close()
        return row[0] if row else 'User'

    def init_ui(self):
        self.setStyleSheet('''
            QWidget { background: #23272f; color: #f5f6fa; font-size: 16px; }
            QPushButton#addItemBtn {
                background: transparent;
                color: #00bcd4;
                border: 2px solid #00bcd4;
                border-radius: 18px;
                padding: 8px 32px;
                font-size: 18px;
                font-weight: bold;
            }
            QPushButton#addItemBtn:pressed {
                background: #00bcd4;
                color: #23272f;
            }
            QPushButton#logoutBtn {
                background: #263238;
                color: #f5f6fa;
                border: none;
                border-radius: 18px;
                padding: 8px 32px;
                font-size: 18px;
                font-weight: bold;
            }
            QPushButton#logoutBtn:pressed {
                background: #00bcd4;
                color: #23272f;
            }
            QLabel#mainTitle { font-size: 32px; font-weight: bold; margin-bottom: 8px; }
            QLineEdit#searchBar { background: #263238; border: 1.5px solid #00bcd4; border-radius: 12px; color: #f5f6fa; font-size: 18px; padding: 10px; }
        ''')
        main_layout = QVBoxLayout(self)
        # Top bar
        top_bar = QHBoxLayout()
        app_label = QLabel('🔒 Birostris Pass')
        app_label.setFont(QFont('Arial', 20, QFont.Bold))
        top_bar.addWidget(app_label)
        top_bar.addStretch(1)
        user_label = QLabel(self.user_name)
        user_label.setFont(QFont('Arial', 14, QFont.Bold))
        top_bar.addWidget(user_label)
        self.logout_btn = QPushButton('Logout')
        self.logout_btn.setObjectName('logoutBtn')
        self.logout_btn.setFixedWidth(140)
        self.logout_btn.setMinimumHeight(40)
        self.logout_btn.clicked.connect(self.logout)
        top_bar.addWidget(self.logout_btn)
        main_layout.addLayout(top_bar)
        # Title and Add button
        title_bar = QHBoxLayout()
        title = QLabel('All Items')
        title.setObjectName('mainTitle')
        title_bar.addWidget(title)
        title_bar.addStretch(1)
        self.add_btn = QPushButton('Add Item')
        self.add_btn.setObjectName('addItemBtn')
        self.add_btn.clicked.connect(self.add_entry_dialog)
        title_bar.addWidget(self.add_btn)
        main_layout.addLayout(title_bar)
        # Search bar
        search_layout = QHBoxLayout()
        self.search_bar = QLineEdit()
        self.search_bar.setObjectName('searchBar')
        self.search_bar.setPlaceholderText('Search...')
        self.search_bar.textChanged.connect(self.load_entries)
        search_layout.addWidget(self.search_bar)
        main_layout.addLayout(search_layout)
        # Card list area
        self.card_area = QVBoxLayout()
        self.card_area.setSpacing(0)
        main_layout.addLayout(self.card_area)
        self.setLayout(main_layout)

    def load_entries(self):
        # Clear old cards
        while self.card_area.count():
            item = self.card_area.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        search_text = self.search_bar.text().lower() if hasattr(self, 'search_bar') else ''
        entries = get_all_entries(self.user_id)
        filtered = [e for e in entries if search_text in e.site.lower() or search_text in e.username.lower() or search_text in e.notes.lower()]
        for entry in filtered:
            card = EntryCard(
                entry,
                self,
                on_edit=self.edit_entry_dialog,
                on_delete=self.delete_entry_confirm,
                on_copy_user=self.copy_username,
                on_copy_pw=self.copy_password
            )
            self.card_area.addWidget(card)
        self.card_area.addStretch(1)

    def add_entry_dialog(self):
        dialog = EntryDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            site, username, password, notes = dialog.get_data()
            if not site or not username or not password:
                QMessageBox.warning(self, 'Error', 'All fields except notes are required!')
                return
            add_entry(self.user_id, site, username, password, notes)
            QMessageBox.information(self, 'Success', 'Entry added!')
            self.load_entries()

    def edit_entry_dialog(self, entry):
        dialog = EntryDialog(self, site=entry.site, username=entry.username, password=entry.password_enc, notes=entry.notes, is_edit=True)
        if dialog.exec_() == QDialog.Accepted:
            site, username, password, notes = dialog.get_data()
            if not site or not username or not password:
                QMessageBox.warning(self, 'Error', 'All fields except notes are required!')
                return
            update_entry(self.user_id, entry.id, site, username, password, notes)
            QMessageBox.information(self, 'Success', 'Entry updated!')
            self.load_entries()

    def delete_entry_confirm(self, entry):
        reply = QMessageBox.question(self, 'Delete Entry', 'Are you sure you want to delete this entry?', QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            delete_entry(self.user_id, entry.id)
            QMessageBox.information(self, 'Deleted', 'Entry deleted!')
            self.load_entries()

    def copy_username(self, entry):
        QApplication.clipboard().setText(entry.username, QClipboard.Clipboard)
        QMessageBox.information(self, 'Copied', 'Username copied!')

    def copy_password(self, entry):
        QApplication.clipboard().setText(entry.password_enc, QClipboard.Clipboard)
        QMessageBox.information(self, 'Copied', 'Password copied!')

    def logout(self):
        self.close()
        if self.show_login_callback:
            self.show_login_callback()
