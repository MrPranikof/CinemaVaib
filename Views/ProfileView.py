from PyQt6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QPushButton,
    QLineEdit, QFormLayout, QMessageBox, QGroupBox, QHBoxLayout
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from ViewModels.ProfileViewModel import ProfileViewModel
from Models.UserModel import UserModel


class ProfileView(QWidget):
    def __init__(self, user_id, go_back=None, go_login=None):
        super().__init__()
        self.vm = ProfileViewModel()
        self.go_back = go_back
        self.go_login = go_login
        self.user_id = user_id

        # Загружаем АКТУАЛЬНЫЕ данные пользователя из БД
        self.user_data = UserModel.get_user_data(user_id)

        if not self.user_data:
            QMessageBox.critical(self, "Ошибка", "Не удалось загрузить данные пользователя")
            if go_back:
                go_back()
            return

        # --- Основное расположение ---
        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # --- Карточка профиля ---
        card = QGroupBox()
        card.setObjectName("ProfileCard")
        card.setFixedSize(600, 500)
        card_layout = QVBoxLayout(card)
        card_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.label_title = QLabel("👤 Профиль пользователя")
        self.label_title.setObjectName("ProfileTitle")

        # Отображаем АКТУАЛЬНЫЕ данные
        self.label_user = QLabel(
            f"Логин: {self.user_data['login']}\n"
            f"Email: {self.user_data['email']}\n"
            f"Роль: {self.user_data['role_name']}\n"
            f"Статус: {self.user_data['status']}"
        )
        self.label_user.setObjectName("ProfileInfo")
        self.label_user.setWordWrap(True)

        # --- Поля для смены пароля ---
        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        # --- Поле "старый пароль" ---
        old_pass_layout = QHBoxLayout()
        self.old_pass = QLineEdit()
        self.old_pass.setEchoMode(QLineEdit.EchoMode.Password)
        self.btn_show_old = QPushButton()
        self.btn_show_old.setIcon(QIcon("images/showPassword.png"))
        self.btn_show_old.setFlat(True)
        self.btn_show_old.setFixedSize(28, 28)
        self.btn_show_old.clicked.connect(lambda: self._toggle_password(self.old_pass, self.btn_show_old))
        old_pass_layout.addWidget(self.old_pass)
        old_pass_layout.addWidget(self.btn_show_old)

        # --- Поле "новый пароль" ---
        new_pass_layout = QHBoxLayout()
        self.new_pass = QLineEdit()
        self.new_pass.setEchoMode(QLineEdit.EchoMode.Password)
        self.btn_show_new = QPushButton()
        self.btn_show_new.setIcon(QIcon("images/showPassword.png"))
        self.btn_show_new.setFlat(True)
        self.btn_show_new.setFixedSize(28, 28)
        self.btn_show_new.clicked.connect(lambda: self._toggle_password(self.new_pass, self.btn_show_new))
        new_pass_layout.addWidget(self.new_pass)
        new_pass_layout.addWidget(self.btn_show_new)

        form.addRow("Текущий пароль:", old_pass_layout)
        form.addRow("Новый пароль:", new_pass_layout)

        self.btn_change_pass = QPushButton("Изменить пароль")
        self.btn_change_pass.setObjectName("ChangePasswordButton")

        card_layout.addWidget(self.label_title)
        card_layout.addWidget(self.label_user)
        card_layout.addSpacing(10)
        card_layout.addLayout(form)
        card_layout.addSpacing(10)
        card_layout.addWidget(self.btn_change_pass)

        main_layout.addWidget(card)

        # --- Нижние кнопки ---
        self.btn_logout = QPushButton("Выйти из аккаунта")
        self.btn_logout.setObjectName("LogoutButton")

        self.btn_back = QPushButton("⬅ Назад")
        self.btn_back.setObjectName("BackButton")

        main_layout.addWidget(self.btn_logout)
        main_layout.addWidget(self.btn_back)

        # --- Сигналы ---
        self.btn_logout.clicked.connect(self.vm.logout)
        self.vm.logged_out.connect(self.go_login)

        if self.go_back:
            self.btn_back.clicked.connect(self.go_back)

        # Изменение пароля
        self.btn_change_pass.clicked.connect(self.change_password)
        self.vm.password_changed.connect(self._on_password_changed)
        self.vm.password_failed.connect(self._on_password_failed)

    def change_password(self):
        """Изменить пароль через user_id"""
        old_p = self.old_pass.text().strip()
        new_p = self.new_pass.text().strip()
        self.vm.change_password(self.user_id, old_p, new_p)

    def _on_password_changed(self):
        QMessageBox.information(self, "Успешно", "Пароль успешно изменён!")
        self.old_pass.clear()
        self.new_pass.clear()

    def _on_password_failed(self, message):
        QMessageBox.warning(self, "Ошибка", message)

    def _toggle_password(self, line_edit: QLineEdit, button: QPushButton):
        if line_edit.echoMode() == QLineEdit.EchoMode.Password:
            line_edit.setEchoMode(QLineEdit.EchoMode.Normal)
            button.setIcon(QIcon("images/hidePassword.png"))
        else:
            line_edit.setEchoMode(QLineEdit.EchoMode.Password)
            button.setIcon(QIcon("images/showPassword.png"))

    def showEvent(self, event):
        super().showEvent(event)
        try:
            from core.animation import AnimationHelper
            AnimationHelper.fade_in(self, 200)
        except:
            pass  # Если модуль анимаций не нужен - игнорируем