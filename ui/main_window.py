from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QLineEdit, QLabel, QMessageBox, QInputDialog, QDialog, QSpinBox, QCheckBox, QFormLayout, QDialogButtonBox, QApplication, QStyle, QMenu)
from logic.password_manager import get_all_entries, add_entry, update_entry, delete_entry
from utils.helpers import generate_password
from PyQt5.QtGui import QClipboard
from PyQt5.QtCore import Qt

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
    def __init__(self, master_password):
        super().__init__()
        self.master_password = master_password
        self.setWindowTitle('Password Manager')
        self.setGeometry(500, 200, 700, 400)
        self.init_ui()
        self.load_entries()

    def init_ui(self):
        layout = QVBoxLayout()
        header_layout = QHBoxLayout()
        # Add empty labels for other columns
        for title in ['Site', 'Username', 'Password', 'Notes']:
            lbl = QLabel(title)
            lbl.setStyleSheet('font-weight: bold; color: #00bcd4; padding: 6px;')
            header_layout.addWidget(lbl)
        # Add the '...' button for actions
        self.actions_btn = QPushButton()
        self.actions_btn.setFixedSize(40, 40)
        self.actions_btn.setText('...')
        self.actions_btn.setStyleSheet('font-size: 20px; border-radius: 20px; background: #2c313c; color: #f5f6fa; border: 1px solid #444;')
        header_layout.addWidget(self.actions_btn)
        header_layout.addStretch()
        layout.addLayout(header_layout)
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(['Site', 'Username', 'Password', 'Notes', ''])
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.horizontalHeader().setVisible(False)
        layout.addWidget(self.table)
        btn_layout = QHBoxLayout()
        self.add_btn = QPushButton('Add Entry')
        self.add_btn.clicked.connect(self.add_entry_dialog)
        btn_layout.addWidget(self.add_btn)
        self.gen_btn = QPushButton('Generate Password')
        self.gen_btn.clicked.connect(self.show_password_generator)
        btn_layout.addWidget(self.gen_btn)
        layout.addLayout(btn_layout)
        self.setLayout(layout)

    def load_entries(self):
        entries = get_all_entries(self.master_password)
        self.table.setRowCount(len(entries))
        for row_idx, entry in enumerate(entries):
            self.table.setItem(row_idx, 0, QTableWidgetItem(entry.site))
            self.table.setItem(row_idx, 1, QTableWidgetItem(entry.username))
            self.table.setItem(row_idx, 2, QTableWidgetItem(entry.password_enc))
            self.table.setItem(row_idx, 3, QTableWidgetItem(entry.notes))
            # Actions: '...' menu button
            menu_btn = QPushButton('...')
            menu_btn.setFixedSize(40, 40)
            menu_btn.setStyleSheet('font-size: 20px; border-radius: 20px; background: #2c313c; color: #f5f6fa; border: 1px solid #444;')
            menu = QMenu()
            menu.setStyleSheet('''
                QMenu { background: #2c313c; color: #f5f6fa; border: 1px solid #444; }
                QMenu::item { padding: 8px 24px; }
                QMenu::item:selected { background: #00bcd4; color: #23272f; }
            ''')
            copy_user_action = menu.addAction('Copy Email or Username')
            copy_pw_action = menu.addAction('Copy Password')
            menu.addSeparator()
            move_action = menu.addAction('Move to Folder')
            menu.addSeparator()
            edit_action = menu.addAction('Edit')
            delete_action = menu.addAction('Delete')
            def on_menu_action(action, eid=entry.id, entry=entry):
                if action == copy_user_action:
                    QApplication.clipboard().setText(entry.username, QClipboard.Clipboard)
                    QMessageBox.information(self, 'Copied', 'Username copied!')
                elif action == copy_pw_action:
                    QApplication.clipboard().setText(entry.password_enc, QClipboard.Clipboard)
                    QMessageBox.information(self, 'Copied', 'Password copied!')
                elif action == move_action:
                    QMessageBox.information(self, 'Move', 'Move to Folder (not implemented)')
                elif action == edit_action:
                    self.edit_entry_dialog(eid)
                elif action == delete_action:
                    self.delete_entry_confirm(eid)
            menu.triggered.connect(lambda act, eid=entry.id: on_menu_action(act, eid, entry))
            menu_btn.setMenu(menu)
            action_layout = QHBoxLayout()
            action_layout.setContentsMargins(0, 0, 0, 0)
            action_layout.setSpacing(4)
            action_layout.addWidget(menu_btn)
            action_widget = QWidget()
            action_widget.setLayout(action_layout)
            self.table.setCellWidget(row_idx, 4, action_widget)

    def add_entry_dialog(self):
        dialog = EntryDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            site, username, password, notes = dialog.get_data()
            if not site or not username or not password:
                QMessageBox.warning(self, 'Error', 'All fields except notes are required!')
                return
            add_entry(site, username, password, notes, self.master_password)
            QMessageBox.information(self, 'Success', 'Entry added!')
            self.load_entries()

    def edit_entry_dialog(self, entry_id):
        entries = get_all_entries(self.master_password)
        entry = next((e for e in entries if e.id == entry_id), None)
        if not entry:
            QMessageBox.warning(self, 'Error', 'Entry not found!')
            return
        dialog = EntryDialog(self, site=entry.site, username=entry.username, password=entry.password_enc, notes=entry.notes, is_edit=True)
        if dialog.exec_() == QDialog.Accepted:
            site, username, password, notes = dialog.get_data()
            if not site or not username or not password:
                QMessageBox.warning(self, 'Error', 'All fields except notes are required!')
                return
            update_entry(entry_id, site, username, password, notes, self.master_password)
            QMessageBox.information(self, 'Success', 'Entry updated!')
            self.load_entries()

    def delete_entry_confirm(self, entry_id):
        reply = QMessageBox.question(self, 'Delete Entry', 'Are you sure you want to delete this entry?', QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            delete_entry(entry_id)
            QMessageBox.information(self, 'Deleted', 'Entry deleted!')
            self.load_entries()

    def show_password_generator(self):
        dialog = PasswordGeneratorDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            pass  # Optionally, you could auto-fill the password field in EntryDialog if desired

    def showEvent(self, event):
        self.setStyleSheet('''
            QWidget { background: #23272f; color: #f5f6fa; font-size: 14px; }
            QLineEdit, QTableWidget, QTableWidgetItem { background: #2c313c; color: #f5f6fa; border: 1px solid #444; border-radius: 4px; padding: 6px; }
            QHeaderView::section {
                background-color: #23272f;
                color: #00bcd4;
                font-weight: bold;
                border: 1px solid #444;
                padding: 6px;
            }
            QPushButton {
                background: #23272f;
                color: #00bcd4;
                border: 1px solid #00bcd4;
                border-radius: 4px;
                padding: 6px 12px;
                margin: 2px;
            }
            QPushButton:pressed {
                background: #00bcd4;
                color: #23272f;
            }
            QPushButton:focus {
                outline: none;
                border: 2px solid #f5f6fa;
            }
            QDialog { background: #23272f; }
            QLabel { color: #f5f6fa; }
        ''')
        super().showEvent(event)
