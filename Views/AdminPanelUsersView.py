from PyQt6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QPushButton, QHBoxLayout,
    QTableView, QSizePolicy, QMessageBox, QSpacerItem, QDialog,
    QComboBox, QFormLayout, QDialogButtonBox
)
from PyQt6.QtCore import Qt
from core.database import query, datagrid_model


class AdminPanelUsersView(QWidget):
    def __init__(self, go_back=None):
        super().__init__()
        self.go_back = go_back

        # Основной layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 30, 40, 30)
        layout.setSpacing(25)

        # Заголовок
        header = QHBoxLayout()
        title = QLabel("👥 Управление пользователями")
        title.setObjectName("TitleLabel")
        title.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        header.addWidget(title)
        header.addStretch()

        self.btn_back = QPushButton("⬅ Назад")
        self.btn_back.setObjectName("BackButton")
        self.btn_back.setFixedWidth(150)
        if self.go_back:
            self.btn_back.clicked.connect(self.go_back)
        header.addWidget(self.btn_back)

        layout.addLayout(header)

        # Таблица пользователей
        self.refresh_table()

        self.view = QTableView()
        self.view.setModel(self.model)
        self.view.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self.view.setSelectionMode(QTableView.SelectionMode.SingleSelection)
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.view.horizontalHeader().setStretchLastSection(True)
        self.view.setAlternatingRowColors(True)

        # Подключаем обработчик выбора строки для обновления текста кнопки
        self.view.selectionModel().selectionChanged.connect(self.on_selection_changed)

        layout.addWidget(self.view, stretch=1)

        # Кнопки управления ролями и статусами
        management_btns = QHBoxLayout()
        management_btns.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))

        self.btn_change_role = QPushButton("👑 Изменить роль")
        self.btn_change_role.clicked.connect(self.change_user_role)
        management_btns.addWidget(self.btn_change_role)

        self.btn_toggle_ban = QPushButton("🔒 Управление статусом")
        self.btn_toggle_ban.setObjectName("LogoutButton")
        self.btn_toggle_ban.clicked.connect(self.toggle_user_ban)
        self.btn_toggle_ban.setEnabled(False)  # Отключена по умолчанию
        management_btns.addWidget(self.btn_toggle_ban)

        management_btns.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        layout.addLayout(management_btns)

        # Нижние кнопки
        btns = QHBoxLayout()
        btns.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))

        self.btn_refresh = QPushButton("🔄 Обновить")
        self.btn_refresh.clicked.connect(self.refresh_table)
        btns.addWidget(self.btn_refresh)

        self.btn_save = QPushButton("💾 Сохранить изменения")
        self.btn_save.clicked.connect(self.save_changes)
        btns.addWidget(self.btn_save)

        self.btn_delete = QPushButton("🗑 Удалить выбранного")
        self.btn_delete.setObjectName("LogoutButton")
        self.btn_delete.clicked.connect(self.delete_selected_user)
        btns.addWidget(self.btn_delete)

        btns.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        layout.addLayout(btns)

    # ----------------------------------------------------------
    def refresh_table(self):
        """Обновить таблицу пользователей"""
        self.model = datagrid_model(
            "SELECT u.user_id, u.login, u.email, r.role_name, u.status, "
            "u.created_at, u.updated_at, u.last_login "
            "FROM users u JOIN roles r ON u.role_id = r.role_id "
            "ORDER BY u.user_id"
        )

        if hasattr(self, 'view'):
            self.view.setModel(self.model)
            # Переподключаем обработчик после обновления модели
            self.view.selectionModel().selectionChanged.connect(self.on_selection_changed)

        # Делаем определенные колонки нередактируемыми
        for row in range(self.model.rowCount()):
            # user_id, role_name, status, created_at, updated_at, last_login - только для чтения
            for col in [0, 3, 4, 5, 6, 7]:
                item = self.model.item(row, col)
                if item:
                    item.setEditable(False)

    # ----------------------------------------------------------
    def on_selection_changed(self):
        """Обработчик изменения выбора в таблице - обновляет текст кнопки бана"""
        user = self.get_selected_user()

        if user:
            # Включаем кнопку и меняем текст в зависимости от статуса
            self.btn_toggle_ban.setEnabled(True)

            if user['status'] == 'Active':
                self.btn_toggle_ban.setText("⛔ Забанить пользователя")
                self.btn_toggle_ban.setObjectName("LogoutButton")
            else:
                self.btn_toggle_ban.setText("✅ Разбанить пользователя")
                self.btn_toggle_ban.setObjectName("ChangePasswordButton")

            # Обновляем стиль кнопки
            self.btn_toggle_ban.style().unpolish(self.btn_toggle_ban)
            self.btn_toggle_ban.style().polish(self.btn_toggle_ban)
        else:
            # Если ничего не выбрано - отключаем кнопку
            self.btn_toggle_ban.setEnabled(False)
            self.btn_toggle_ban.setText("🔒 Управление статусом")
            self.btn_toggle_ban.setObjectName("LogoutButton")

    # ----------------------------------------------------------
    def get_selected_user(self):
        """Получить данные выбранного пользователя"""
        selection = self.view.selectionModel().selectedRows()
        if not selection:
            return None

        row = selection[0].row()
        user_id = self.model.item(row, 0).text()
        login = self.model.item(row, 1).text()
        current_role = self.model.item(row, 3).text()
        current_status = self.model.item(row, 4).text()

        return {
            'user_id': user_id,
            'login': login,
            'role': current_role,
            'status': current_status
        }

    # ----------------------------------------------------------
    def change_user_role(self):
        """Изменить роль пользователя через диалог"""
        user = self.get_selected_user()
        if not user:
            QMessageBox.warning(self, "Внимание", "Выберите пользователя из таблицы")
            return

        # Получаем список всех ролей из БД
        roles_data = query("SELECT role_id, role_name FROM roles ORDER BY role_id")
        if not roles_data:
            QMessageBox.warning(self, "Ошибка", "Не удалось загрузить список ролей")
            return

        # Создаем диалог
        dialog = QDialog(self)
        dialog.setWindowTitle("Изменение роли пользователя")
        dialog.setFixedWidth(400)

        layout = QFormLayout(dialog)

        info_label = QLabel(f"Пользователь: <b>{user['login']}</b><br>"
                            f"Текущая роль: <b>{user['role']}</b>")
        layout.addRow(info_label)

        role_combo = QComboBox()
        for role_id, role_name in roles_data:
            role_combo.addItem(role_name, role_id)

        # Устанавливаем текущую роль
        current_index = role_combo.findText(user['role'])
        if current_index >= 0:
            role_combo.setCurrentIndex(current_index)

        layout.addRow("Новая роль:", role_combo)

        # Кнопки
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addRow(buttons)

        # Показываем диалог
        if dialog.exec() == QDialog.DialogCode.Accepted:
            new_role_id = role_combo.currentData()
            new_role_name = role_combo.currentText()

            try:
                query(
                    "UPDATE users SET role_id = %s WHERE user_id = %s",
                    (new_role_id, user['user_id'])
                )
                QMessageBox.information(
                    self,
                    "Успех",
                    f"Роль пользователя '{user['login']}' изменена на '{new_role_name}'"
                )
                self.refresh_table()
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось изменить роль:\n{e}")

    # ----------------------------------------------------------
    def toggle_user_ban(self):
        """Забанить или разбанить пользователя"""
        user = self.get_selected_user()
        if not user:
            QMessageBox.warning(self, "Внимание", "Выберите пользователя из таблицы")
            return

        # Определяем новый статус (переключаем)
        new_status = "Inactive" if user['status'] == "Active" else "Active"

        # Формируем текст для подтверждения
        if user['status'] == "Active":
            action = "заблокировать"
            icon = "⛔"
            result_text = "заблокирован"
        else:
            action = "разблокировать"
            icon = "✅"
            result_text = "разблокирован"

        # Подтверждение
        confirm = QMessageBox.question(
            self,
            "Подтверждение",
            f"{icon} Вы уверены, что хотите {action} пользователя '<b>{user['login']}</b>'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if confirm == QMessageBox.StandardButton.Yes:
            try:
                query(
                    "UPDATE users SET status = %s WHERE user_id = %s",
                    (new_status, user['user_id'])
                )
                QMessageBox.information(
                    self,
                    "Успех",
                    f"Пользователь '{user['login']}' {result_text}"
                )
                self.refresh_table()
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось изменить статус:\n{e}")

    # ----------------------------------------------------------
    def save_changes(self):
        """Сохранить изменения логина и email (редактируемые поля)"""
        try:
            updated_count = 0
            for row in range(self.model.rowCount()):
                user_id = self.model.item(row, 0).text()
                login = self.model.item(row, 1).text().strip()
                email = self.model.item(row, 2).text().strip()

                # Валидация
                if not login or not email:
                    QMessageBox.warning(
                        self,
                        "Ошибка валидации",
                        f"Логин и email не могут быть пустыми (строка {row + 1})"
                    )
                    return

                # Обновляем только логин и email
                query(
                    "UPDATE users SET login = %s, email = %s WHERE user_id = %s",
                    (login, email, user_id)
                )
                updated_count += 1

            QMessageBox.information(
                self,
                "Успех",
                f"Обновлено записей: {updated_count}"
            )
            self.refresh_table()

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить изменения:\n{e}")

    # ----------------------------------------------------------
    def delete_selected_user(self):
        """Удалить выбранного пользователя"""
        user = self.get_selected_user()
        if not user:
            QMessageBox.warning(self, "Удаление", "Выберите пользователя для удаления")
            return

        confirm = QMessageBox.question(
            self,
            "Подтверждение удаления",
            f"Удалить пользователя '<b>{user['login']}</b>' (ID: {user['user_id']})?<br><br>"
            f"⚠️ <b>Это действие необратимо!</b>",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if confirm == QMessageBox.StandardButton.Yes:
            try:
                query("DELETE FROM users WHERE user_id = %s", (user['user_id'],))
                QMessageBox.information(self, "Готово", f"Пользователь '{user['login']}' удален")
                self.refresh_table()
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось удалить пользователя:\n{e}")

    def showEvent(self, event):
        super().showEvent(event)
        try:
            from core.animation import AnimationHelper
            AnimationHelper.fade_in(self, 200)
        except:
            pass