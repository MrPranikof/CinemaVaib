from PyQt6.QtCore import QObject, pyqtSignal, QSettings
from Models.UserModel import UserModel


class ProfileViewModel(QObject):
    logged_out = pyqtSignal()
    user_loaded = pyqtSignal(str)

    password_changed = pyqtSignal()
    password_failed = pyqtSignal(str)

    def __init__(self):
        super().__init__()

    # --- загрузка текущего пользователя ---
    def load_user(self):
        settings = QSettings("CinemaVaib", "UserConfig")
        login = settings.value("login", "")
        if login:
            self.user_loaded.emit(login)

    # --- выход из аккаунта ---
    def logout(self):
        settings = QSettings("CinemaVaib", "UserConfig")
        settings.clear()
        self.logged_out.emit()

    def change_password(self, login: str, old_pass: str, new_pass: str):
        if not login or not old_pass or not new_pass:
            self.password_failed.emit("Все поля обязательны")
            return

        if old_pass == new_pass:
            self.password_failed.emit("Новый пароль не может совпадать со старым")
            return

        success = UserModel.update_password(login, old_pass, new_pass)
        if success:
            self.password_changed.emit()
        else:
            self.password_failed.emit("Неверный текущий пароль")