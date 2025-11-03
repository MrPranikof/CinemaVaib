from PyQt6.QtCore import QObject, pyqtSignal, QSettings

from Models.LogModel import LogModel
from Models.UserModel import UserModel


class ProfileViewModel(QObject):
    logged_out = pyqtSignal()
    password_changed = pyqtSignal()
    password_failed = pyqtSignal(str)

    def __init__(self):
        super().__init__()

    def logout(self):
        """Выход из аккаунта"""
        if hasattr(self, 'user_id') and self.user_id:
            LogModel.log_user_logout(self.user_id)
        settings = QSettings("CinemaVaib", "UserConfig")
        settings.clear()
        self.logged_out.emit()

    def change_password(self, user_id: int, old_pass: str, new_pass: str):
        """Изменить пароль по user_id"""
        if not old_pass or not new_pass:
            self.password_failed.emit("Все поля обязательны")
            return

        if old_pass == new_pass:
            self.password_failed.emit("Новый пароль не может совпадать со старым")
            return

        if len(new_pass) < 6:
            self.password_failed.emit("Новый пароль должен содержать минимум 6 символов")
            return

        success = UserModel.update_password_by_id(user_id, old_pass, new_pass)

        if success:
            LogModel.log_password_change(user_id, True)
            self.password_changed.emit()
        else:
            LogModel.log_password_change(user_id, False, "Неверный текущий пароль")
            self.password_failed.emit("Неверный текущий пароль")