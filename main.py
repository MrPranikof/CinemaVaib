import sys

from PyQt6.QtCore import QSettings
from PyQt6.QtGui import QFontDatabase, QIcon
from PyQt6.QtWidgets import QApplication, QStackedWidget
from Views.LoginView import LoginView
from Views.RegisterView import RegisterView
from Views.MainView import MainView

class App(QStackedWidget):
    def __init__(self):
        super().__init__()
        self.setWindowIcon(QIcon('images/iconLogo.png'))
        self.setWindowTitle('CinemaVaib')
        self.setFixedSize(1024, 600)

        self.login = LoginView(self.show_register, self.show_main)
        self.register = RegisterView(self.show_login)
        self.main = MainView(self.show_login)

        self.addWidget(self.login)
        self.addWidget(self.register)
        self.addWidget(self.main)

        settings = QSettings("CinemaVaib", "UserConfig")
        if settings.value("remember_login", False, type=bool):
            login = settings.value("login", "")
            self.show_main(login)
        else:
            self.show_login()

    def show_login(self):
        self.setCurrentWidget(self.login)

    def show_register(self):
        self.setCurrentWidget(self.register)

    def show_main(self, login):
        self.main.set_user(login)
        self.setCurrentWidget(self.main)

    def apply_style(app):
        QFontDatabase.addApplicationFont("fonts/Oswald-Regular.ttf")
        QFontDatabase.addApplicationFont("fonts/Montserrat-Regular.ttf")
        QFontDatabase.addApplicationFont("fonts/Roboto-Regular.ttf")
        QFontDatabase.addApplicationFont("fonts/OpenSans-Regular.ttf")

        with open("core/style/CinemaVaib.qss", "r", encoding="utf-8") as f:
            app.setStyleSheet(f.read())


def main():
    app = QApplication(sys.argv)
    App.apply_style(app)
    win = App()
    win.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()