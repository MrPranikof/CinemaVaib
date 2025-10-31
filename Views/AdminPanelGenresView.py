from PyQt6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QPushButton, QHBoxLayout,
    QTableView, QSizePolicy, QMessageBox, QSpacerItem, QDialog,
    QLineEdit, QFormLayout, QDialogButtonBox
)
from PyQt6.QtCore import Qt
from core.database import datagrid_model
from Models.GenreModel import GenreModel


class AdminPanelGenresView(QWidget):
    def __init__(self, go_back=None):
        super().__init__()
        self.go_back = go_back

        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 30, 40, 30)
        layout.setSpacing(25)

        # Заголовок
        header = QHBoxLayout()
        title = QLabel("🎭 Управление жанрами")
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

        # Поиск
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Поиск жанров...")
        self.search_input.textChanged.connect(self.on_search)
        search_layout.addWidget(self.search_input)
        layout.addLayout(search_layout)

        # Таблица жанров
        self.refresh_table()

        self.view = QTableView()
        self.view.setModel(self.model)
        self.view.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self.view.setSelectionMode(QTableView.SelectionMode.SingleSelection)
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.view.horizontalHeader().setStretchLastSection(True)
        self.view.setAlternatingRowColors(True)

        layout.addWidget(self.view, stretch=1)

        # Кнопки управления
        btns = QHBoxLayout()
        btns.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))

        self.btn_add = QPushButton("➕ Добавить жанр")
        self.btn_add.clicked.connect(self.add_genre)
        btns.addWidget(self.btn_add)

        self.btn_edit = QPushButton("✏️ Редактировать")
        self.btn_edit.clicked.connect(self.edit_genre)
        btns.addWidget(self.btn_edit)

        self.btn_delete = QPushButton("🗑 Удалить")
        self.btn_delete.setObjectName("LogoutButton")
        self.btn_delete.clicked.connect(self.delete_genre)
        btns.addWidget(self.btn_delete)

        self.btn_refresh = QPushButton("🔄 Обновить")
        self.btn_refresh.clicked.connect(self.refresh_table)
        btns.addWidget(self.btn_refresh)

        btns.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        layout.addLayout(btns)

    def refresh_table(self):
        """Обновить таблицу жанров"""
        self.model = datagrid_model(
            "SELECT genre_id, name, created_at, updated_at FROM genres ORDER BY name"
        )

        if hasattr(self, 'view'):
            self.view.setModel(self.model)

        for row in range(self.model.rowCount()):
            for col in range(self.model.columnCount()):
                item = self.model.item(row, col)
                if item:
                    item.setEditable(False)

    def on_search(self, text):
        """Поиск жанров"""
        if len(text.strip()) >= 1:
            self.model = datagrid_model(
                "SELECT genre_id, name, created_at, updated_at FROM genres WHERE name ILIKE %s ORDER BY name",
                (f"%{text.strip()}%",)
            )
            self.view.setModel(self.model)
        elif len(text.strip()) == 0:
            self.refresh_table()

    def get_selected_genre(self):
        """Получить выбранный жанр"""
        selection = self.view.selectionModel().selectedRows()
        if not selection:
            return None

        row = selection[0].row()
        return {
            'genre_id': self.model.item(row, 0).text(),
            'name': self.model.item(row, 1).text()
        }

    def add_genre(self):
        """Добавить жанр"""
        dialog = GenreDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            name = dialog.name_input.text().strip()

            if not name:
                QMessageBox.warning(self, "Ошибка", "Введите название жанра")
                return

            try:
                GenreModel.create_genre(name)
                QMessageBox.information(self, "Успех", f"Жанр '{name}' добавлен")
                self.refresh_table()
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось добавить жанр:\n{e}")

    def edit_genre(self):
        """Редактировать жанр"""
        genre = self.get_selected_genre()
        if not genre:
            QMessageBox.warning(self, "Внимание", "Выберите жанр из таблицы")
            return

        dialog = GenreDialog(self, genre['name'])
        if dialog.exec() == QDialog.DialogCode.Accepted:
            name = dialog.name_input.text().strip()

            if not name:
                QMessageBox.warning(self, "Ошибка", "Введите название жанра")
                return

            try:
                GenreModel.update_genre(genre['genre_id'], name)
                QMessageBox.information(self, "Успех", f"Жанр обновлён на '{name}'")
                self.refresh_table()
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось обновить жанр:\n{e}")

    def delete_genre(self):
        """Удалить жанр"""
        genre = self.get_selected_genre()
        if not genre:
            QMessageBox.warning(self, "Внимание", "Выберите жанр из таблицы")
            return

        confirm = QMessageBox.question(
            self,
            "Подтверждение",
            f"Удалить жанр '<b>{genre['name']}</b>'?<br><br>"
            f"⚠️ <b>Это действие необратимо!</b>",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if confirm == QMessageBox.StandardButton.Yes:
            try:
                GenreModel.delete_genre(genre['genre_id'])
                QMessageBox.information(self, "Успех", f"Жанр '{genre['name']}' удалён")
                self.refresh_table()
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось удалить жанр:\n{e}")


class GenreDialog(QDialog):
    """Диалог добавления/редактирования жанра"""

    def __init__(self, parent=None, name=""):
        super().__init__(parent)
        self.setWindowTitle("Жанр")
        self.setFixedWidth(400)

        layout = QFormLayout(self)

        self.name_input = QLineEdit(name)
        self.name_input.setPlaceholderText("Введите название жанра")
        layout.addRow("Название:", self.name_input)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)