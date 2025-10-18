from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QPushButton
from PyQt6.QtCore import Qt
from ViewModels.ProfileViewModel import ProfileViewModel

class ProfileView(QWidget):
    def __init__(self, user_login=None, go_back=None):
        super().__init__()
        self.vm = ProfileViewModel()
        self.go_back = go_back

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.label_title = QLabel("👤 Профиль пользователя")
        self.label_title.setObjectName("ProfileTitle")

        self.label_user = QLabel("")
        self.label_user.setObjectName("ProfileInfo")

        self.btn_logout = QPushButton("Выйти из аккаунта")
        self.btn_logout.setObjectName("LogoutButton")
        self.btn_back = QPushButton("⬅ Назад")
        self.btn_back.setObjectName("BackButton")

        layout.addWidget(self.label_title)
        layout.addSpacing(20)
        layout.addWidget(self.label_user)
        layout.addSpacing(40)
        layout.addWidget(self.btn_logout)
        layout.addWidget(self.btn_back)

        self.btn_back.clicked.connect(self.go_back)
        self.btn_logout.clicked.connect(self.vm.logout)
        self.vm.logged_out.connect(self.go_back)
        self.vm.user_loaded.connect(self.set_user)

        if user_login:
            self.set_user(user_login)
        else:
            self.vm.load_user()

    def set_user(self, login):
        self.user_login = login
        self.label_user.setText(f"Логин: {login}")