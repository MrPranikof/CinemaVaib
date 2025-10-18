from PyQt6.QtCore import QObject, pyqtSignal
from Models.UserModel import UserModel

class LoginViewModel(QObject):
    login_success = pyqtSignal(str)
    login_failed = pyqtSignal(str)

    def login(self, login, password):
        if not login or not password:
            self.login_failed.emit("Заполните все поля")
            return

        user = UserModel.find_by_login(login)
        if not user:
            self.login_failed.emit("Пользователь не найден")
            return

        if UserModel.check_password(login, password):
            self.login_success.emit(login)
            UserModel.last_login(login)

        else:
            self.login_failed.emit("Неверный пароль")