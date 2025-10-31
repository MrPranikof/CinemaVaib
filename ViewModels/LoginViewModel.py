from PyQt6.QtCore import QObject, pyqtSignal
from Models.UserModel import UserModel


class LoginViewModel(QObject):
    login_success = pyqtSignal(int)  # Передаем user_id
    login_failed = pyqtSignal(str)

    def login(self, login, password):
        # Проверка на заполненность полей
        if not login or not password:
            self.login_failed.emit("Заполните все поля")
            return

        # Поиск пользователя
        user = UserModel.find_by_login(login)
        if not user:
            self.login_failed.emit("Пользователь не найден")
            return

        # Проверка пароля
        if not UserModel.check_password(login, password):
            self.login_failed.emit("Неверный пароль")
            return

        # Проверка статуса аккаунта (Active/Inactive)
        user_status = user[5]  # status - 6-е поле в таблице users
        if user_status != 'Active':
            self.login_failed.emit(
                "Ваш аккаунт заблокирован. Обратитесь к администратору."
            )
            return

        # Успешный вход
        user_id = user[0]  # user_id - первое поле
        UserModel.last_login(user_id)
        self.login_success.emit(user_id)