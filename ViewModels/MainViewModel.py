from PyQt6.QtCore import QObject, pyqtSignal
from Models.UserModel import UserModel

class MainViewModel(QObject):
    @staticmethod
    def get_role_id(login: str):
        return UserModel.get_user_role_id(login)