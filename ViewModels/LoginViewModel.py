from PyQt6.QtCore import QObject, pyqtSignal
from Models.LogModel import LogModel
from Models.UserModel import UserModel


class LoginViewModel(QObject):
    login_success = pyqtSignal(int)
    login_failed = pyqtSignal(str)

    def login(self, login, password):
        if not login or not password:
            self.login_failed.emit("Заполните все поля")
            LogModel.log_action(None, "System", "USER_LOGIN", None,
                                f"Неудачная попытка входа: пустые поля", "FAILED")
            return

        user = UserModel.find_by_login(login)
        if not user:
            self.login_failed.emit("Пользователь не найден")
            LogModel.log_action(None, "System", "USER_LOGIN", None,
                                f"Неудачная попытка входа: пользователь '{login}' не найден", "FAILED")
            return

        if not UserModel.check_password(login, password):
            self.login_failed.emit("Неверный пароль")
            LogModel.log_action(user[0], "User", "USER_LOGIN", user[0],
                                f"Неудачная попытка входа: неверный пароль для '{login}'", "FAILED")
            return

        user_status = user[5]
        if user_status != 'Active':
            error_msg = "Ваш аккаунт заблокирован. Обратитесь к администратору."
            self.login_failed.emit(error_msg)
            LogModel.log_action(user[0], "User", "USER_LOGIN", user[0],
                                f"Неудачная попытка входа: аккаунт заблокирован '{login}'", "FAILED")
            return

        user_id = user[0]
        UserModel.last_login(user_id)

        user_role = UserModel.get_user_role_name_by_id(user_id)
        LogModel.log_user_login(user_id, True, None, user_role)

        self.login_success.emit(user_id)