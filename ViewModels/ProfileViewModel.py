from PyQt6.QtCore import QObject, pyqtSignal, QSettings

class ProfileViewModel(QObject):
    logged_out = pyqtSignal()
    user_loaded = pyqtSignal(str)

    def __init__(self):
        super().__init__()

    def load_user(self):
        settings = QSettings("CinemaVaib", "UserConfig")
        login = settings.value("login", "")
        if login:
            self.user_loaded.emit(login)

    def logout(self):
        settings = QSettings("CinemaVaib", "UserConfig")
        settings.clear()
        self.logged_out.emit()