import sys
from PyQt5.QtWidgets import QApplication
from models.models import init_db, init_user_db
from ui.login_window import WelcomeWindow, SignUpWindow, LoginWindow
from ui.main_window import MainWindow

def main():
    init_db()
    app = QApplication(sys.argv)
    welcome = WelcomeWindow()
    signup = SignUpWindow()
    login = LoginWindow()
    main_win = None

    def show_signup():
        welcome.hide()
        login.hide()
        signup.show()

    def show_login(user_id=None):
        welcome.hide()
        signup.hide()
        login.show()
        # Optionally, auto-fill login for new user
        # if user_id is not None:
        #     pass

    def on_login_success(user_id):
        nonlocal main_win
        init_user_db(user_id)  # Ensure the table exists
        login.hide()
        main_win = MainWindow(user_id, show_login_callback=show_login)
        main_win.show()

    welcome.show_signup.connect(show_signup)
    welcome.show_login.connect(show_login)
    login.show_signup.connect(show_signup)
    signup.show_login.connect(show_login)
    login.login_success.connect(on_login_success)

    welcome.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
