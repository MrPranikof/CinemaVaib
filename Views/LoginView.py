from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QLineEdit, QHBoxLayout, QFrame, QCheckBox
from PyQt6.QtCore import Qt, QSize, QSettings
from PyQt6.QtGui import QIcon
from ViewModels.LoginViewModel import LoginViewModel
from Models.UserModel import UserModel


class LoginView(QWidget):
    def __init__(self, go_register, go_main):
        super().__init__()
        self.vm = LoginViewModel()
        self.go_register = go_register
        self.go_main = go_main
        self.setWindowTitle('Авторизация')

        self.brand_label = QLabel("CinemaVaib")
        self.brand_label.setObjectName("BrandLabel")
        self.brand_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout = QVBoxLayout(self)

        self.label = QLabel("Авторизация")
        self.loginInput = QLineEdit(placeholderText="Логин")
        self.passwordInput = QLineEdit(placeholderText="Пароль")
        self.passwordInput.setEchoMode(QLineEdit.EchoMode.Password)

        self.show_pass_btn = QPushButton()
        self.show_pass_btn.setIcon(QIcon("images/showPassword.png"))
        self.show_pass_btn.setCheckable(True)
        self.show_pass_btn.setIconSize(QSize(28, 28))
        self.show_pass_btn.setFixedSize(32, 32)
        self.show_pass_btn.setFlat(True)
        self.show_pass_btn.clicked.connect(self.toggle_password)

        pass_layout = QHBoxLayout()
        pass_layout.addWidget(self.passwordInput)
        pass_layout.addWidget(self.show_pass_btn)

        self.status = QLabel("")
        self.status.setWordWrap(True)
        self.btn_login = QPushButton("Войти")

        self.remember_checkbox = QCheckBox("Запомнить меня")
        self.remember_checkbox.setObjectName("RememberCheckBox")

        self.link_register = QLabel('<a href="#">Нет аккаунта? Зарегистрируйтесь</a>')
        self.link_register.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.link_register.setOpenExternalLinks(False)
        self.link_register.linkActivated.connect(lambda _: self.go_register())

        card = QFrame()
        card.setObjectName("FormContainer")
        card.setFixedSize(500, 400)
        form_layout = QVBoxLayout(card)
        form_layout.addWidget(self.label)
        form_layout.addWidget(self.loginInput)
        form_layout.addLayout(pass_layout)
        form_layout.addWidget(self.status)
        form_layout.addWidget(self.btn_login)
        form_layout.addWidget(self.remember_checkbox)
        form_layout.addWidget(self.link_register)

        layout.addWidget(self.brand_label)
        layout.addWidget(card)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.btn_login.clicked.connect(self.try_login)
        self.vm.login_success.connect(self.on_login_success)
        self.vm.login_failed.connect(self.on_login_failed)

    def try_login(self):
        login = self.loginInput.text().strip()
        password = self.passwordInput.text().strip()
        self.vm.login(login, password)

    def on_login_success(self, user_id):
        """Получаем user_id из сигнала"""
        # Получаем актуальный логин из БД
        user_data = UserModel.get_user_data(user_id)
        if user_data:
            self.status.setText(f"✅ Добро пожаловать, {user_data['login']}")

        settings = QSettings("CinemaVaib", "UserConfig")

        if self.remember_checkbox.isChecked():
            settings.setValue("remember_login", True)
            settings.setValue("user_id", user_id)  # Сохраняем ТОЛЬКО user_id
        else:
            settings.clear()

        self.go_main(user_id)  # Передаем user_id

    def on_login_failed(self, msg):
        self.status.setText(f"❌ {msg}")

    def toggle_password(self):
        if self.show_pass_btn.isChecked():
            self.passwordInput.setEchoMode(QLineEdit.EchoMode.Normal)
            self.show_pass_btn.setIcon(QIcon("images/hidePassword.png"))
        else:
            self.passwordInput.setEchoMode(QLineEdit.EchoMode.Password)
            self.show_pass_btn.setIcon(QIcon("images/showPassword.png"))

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            self.try_login()

    def reset(self):
        """Сбросить форму"""
        self.loginInput.clear()
        self.passwordInput.clear()
        self.status.clear()
        self.remember_checkbox.setChecked(False)
        if self.show_pass_btn.isChecked():
            self.toggle_password()

    def showEvent(self, event):
        super().showEvent(event)
        try:
            from core.animation import AnimationHelper
            AnimationHelper.fade_in(self, 200)
        except:
            pass  # Если модуль анимаций не нужен - игнорируем