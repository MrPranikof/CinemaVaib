import re
from PyQt6.QtCore import QObject, pyqtSignal

from Models.LogModel import LogModel
from Models.UserModel import UserModel

class RegisterViewModel(QObject):
    register_success = pyqtSignal(str)
    register_failed = pyqtSignal(str)

    def register(self, login, email, password):
        # Проверка на заполненность
        if not login or not email or not password:
            self.register_failed.emit("Заполните все поля")
            return

        # Проверка минимальной длины
        if len(login) < 3:
            self.register_failed.emit("Логин должен содержать минимум 3 символа")
            return
        if len(password) < 6:
            self.register_failed.emit("Пароль должен содержать минимум 6 символов")
            return

        # Проверка формата e-mail
        email_pattern = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
        if not re.match(email_pattern, email):
            self.register_failed.emit("Введите корректный адрес электронной почты")
            return

        # Проверка логина и почты на занятость
        if UserModel.find_by_login(login):
            self.register_failed.emit("Ваш логин занят другим пользователем, придумайте другой")
            return

        if UserModel.find_by_email(email):
            self.register_failed.emit("Эта электронная почта уже есть в системе, используйте другую")
            return

        # Всё ок — создаём пользователя
        user_id = UserModel.create_user(login, email, password)
        if user_id:
            LogModel.log_user_register(user_id, login)
            self.register_success.emit(login)
        else:
            LogModel.log_error(None, "USER_REGISTER", "Ошибка создания пользователя")
            self.register_failed.emit("Ошибка при создании пользователя")
