from PyQt6.QtCore import QObject, pyqtSignal
from Models.UserModel import UserModel

class RegisterViewModel(QObject):
    register_success = pyqtSignal(str)
    register_failed = pyqtSignal(str)

    def register(self, login, email, password):
        if not login or not email or not password:
            self.register_failed.emit("Заполните все поля")
            return
        if UserModel.find_by_login(login):
            self.register_failed.emit("Ваш логин занят другим пользователем, придумайте другой")

        if UserModel.find_by_email(login):
            self.register_failed.emit("Ваша электронная почта уже есть в системе, используйте другую")

        self.register_success.emit(login)
        UserModel.create_user(login, email, password)