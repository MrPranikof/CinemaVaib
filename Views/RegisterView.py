from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QLabel,
    QLineEdit, QHBoxLayout, QFrame
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon
from ViewModels.RegisterViewModel import RegisterViewModel


class RegisterView(QWidget):
    def __init__(self, go_login):
        super().__init__()
        self.vm = RegisterViewModel()
        self.go_login = go_login

        self.setWindowTitle("Регистрация")

        self.brand_label = QLabel("CinemaVaib")
        self.brand_label.setObjectName("BrandLabel")
        self.brand_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Основной макет
        layout = QVBoxLayout(self)

        # Поля формы
        self.label = QLabel("Создайте новый аккаунт")
        self.loginInput = QLineEdit(placeholderText="Логин")
        self.emailInput = QLineEdit(placeholderText="Email")
        self.passwordInput = QLineEdit(placeholderText="Пароль")
        self.passwordInput.setEchoMode(QLineEdit.EchoMode.Password)

        # Кнопка-глаз для пароля
        self.show_pass_btn = QPushButton()
        self.show_pass_btn.setIcon(QIcon("images/showPassword.png"))
        self.show_pass_btn.setCheckable(True)
        self.show_pass_btn.setIconSize(QSize(28, 28))
        self.show_pass_btn.setFixedSize(32, 32)
        self.show_pass_btn.setFlat(True)
        self.show_pass_btn.clicked.connect(self.toggle_password)

        # Компоновка поля пароля + глазик
        pass_layout = QHBoxLayout()
        pass_layout.addWidget(self.passwordInput)
        pass_layout.addWidget(self.show_pass_btn)

        # Статус и кнопки
        self.status = QLabel("")
        self.btn_register = QPushButton("Зарегистрироваться")

        # Ссылка "Уже есть аккаунт?"
        self.link_login = QLabel('<a href="#">Уже есть аккаунт? Войти</a>')
        self.link_login.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.link_login.setOpenExternalLinks(False)
        self.link_login.linkActivated.connect(lambda _: self.go_login())

        # Карточка формы
        card = QFrame()
        card.setObjectName("FormContainer")
        card.setFixedSize(500, 400)
        form_layout = QVBoxLayout(card)
        form_layout.addWidget(self.label)
        form_layout.addWidget(self.loginInput)
        form_layout.addWidget(self.emailInput)
        form_layout.addLayout(pass_layout)
        form_layout.addWidget(self.status)
        form_layout.addWidget(self.btn_register)
        form_layout.addWidget(self.link_login)
        form_layout.setSpacing(10)

        # Размещение карточки по центру
        layout.addWidget(self.brand_label)
        layout.addWidget(card)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Сигналы
        self.btn_register.clicked.connect(self.try_register)
        self.vm.register_failed.connect(self.failed_register)
        self.vm.register_success.connect(self.success_register)

    # === Логика ===
    def try_register(self):
        login = self.loginInput.text().strip()
        email = self.emailInput.text().strip()
        password = self.passwordInput.text().strip()
        self.vm.register(login, email, password)

    def failed_register(self, msg):
        self.status.setText(f"❌ {msg}")

    def success_register(self, login):
        self.status.setText(f"✅ Регистрация успешно прошла, {login}")
        self.go_login()

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