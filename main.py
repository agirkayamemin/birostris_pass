import sys
from PyQt5.QtWidgets import QApplication
from models.models import init_db
from ui.login_window import LoginWindow
from ui.main_window import MainWindow

def main():
    init_db()
    app = QApplication(sys.argv)
    login = LoginWindow()
    main_win = None

    def on_login_success(master_password):
        nonlocal main_win
        login.close()
        main_win = MainWindow(master_password)
        main_win.show()

    login.login_success.connect(on_login_success)
    login.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
