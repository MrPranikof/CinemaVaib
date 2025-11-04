import sys
from PyQt6.QtCore import QSettings
from PyQt6.QtGui import QFontDatabase, QIcon
from PyQt6.QtWidgets import QApplication, QStackedWidget
from Views.LoginView import LoginView
from Views.RegisterView import RegisterView
from Views.MainView import MainView
from Models.UserModel import UserModel


class App(QStackedWidget):
    def __init__(self):
        super().__init__()
        self.setWindowIcon(QIcon('images/iconLogo.png'))
        self.setWindowTitle('CinemaVaib')
        self.setFixedSize(1024, 600)

        self.current_user_id = None

        # Создаем ТОЛЬКО login view изначально
        self.login = LoginView(self.show_register, self.show_main)
        self.addWidget(self.login)

        # Остальные виды создадим по требованию (lazy loading)
        self.register = None
        self.main = None

        settings = QSettings("CinemaVaib", "UserConfig")

        if settings.value("remember_login", False, type=bool):
            user_id = settings.value("user_id", type=int)
            if user_id and UserModel.find_by_id(user_id):
                self.show_main(user_id)
            else:
                settings.clear()
                self.show_login()
        else:
            self.show_login()

    def show_login(self):
        """Показать страницу входа"""
        self.current_user_id = None

        # Пересоздаем login для сброса формы
        if self.login is not None:
            self.removeWidget(self.login)
            self.login.deleteLater()

        self.login = LoginView(self.show_register, self.show_main)
        self.addWidget(self.login)
        self.setCurrentWidget(self.login)

    def show_register(self):
        """Показать страницу регистрации"""
        if self.register is None:
            self.register = RegisterView(self.show_login)
            self.addWidget(self.register)
        else:
            # Сбрасываем форму
            self.register.reset()

        self.setCurrentWidget(self.register)

    def show_main(self, user_id):
        self.current_user_id = user_id
        if self.main is not None:
            self.removeWidget(self.main)
            self.main.deleteLater()

        self.main = MainView(user_id, self.show_login)
        self.addWidget(self.main)
        self.setCurrentWidget(self.main)

    @staticmethod
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