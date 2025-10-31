from PyQt6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QPushButton, QHBoxLayout,
    QTableView, QSizePolicy, QMessageBox, QSpacerItem, QDialog,
    QLineEdit, QFormLayout, QDialogButtonBox, QFileDialog
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from core.database import datagrid_model
from Models.ActorModel import ActorModel


class AdminPanelActorsView(QWidget):
    def __init__(self, go_back=None):
        super().__init__()
        self.go_back = go_back

        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 30, 40, 30)
        layout.setSpacing(25)

        # Заголовок
        header = QHBoxLayout()
        title = QLabel("🎭 Управление актёрами")
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
        self.search_input.setPlaceholderText("🔍 Поиск по имени...")
        self.search_input.textChanged.connect(self.on_search)
        search_layout.addWidget(self.search_input)
        layout.addLayout(search_layout)

        # Таблица актёров
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

        self.btn_add = QPushButton("➕ Добавить актёра")
        self.btn_add.clicked.connect(self.add_actor)
        btns.addWidget(self.btn_add)

        self.btn_edit = QPushButton("✏️ Редактировать")
        self.btn_edit.clicked.connect(self.edit_actor)
        btns.addWidget(self.btn_edit)

        self.btn_delete = QPushButton("🗑 Удалить")
        self.btn_delete.setObjectName("LogoutButton")
        self.btn_delete.clicked.connect(self.delete_actor)
        btns.addWidget(self.btn_delete)

        self.btn_refresh = QPushButton("🔄 Обновить")
        self.btn_refresh.clicked.connect(self.refresh_table)
        btns.addWidget(self.btn_refresh)

        btns.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        layout.addLayout(btns)

    def refresh_table(self):
        """Обновить таблицу актёров"""
        self.model = datagrid_model(
            "SELECT actor_id, fullname, created_at, updated_at FROM actor ORDER BY fullname"
        )

        if hasattr(self, 'view'):
            self.view.setModel(self.model)

        # Делаем все колонки нередактируемыми
        for row in range(self.model.rowCount()):
            for col in range(self.model.columnCount()):
                item = self.model.item(row, col)
                if item:
                    item.setEditable(False)

    def on_search(self, text):
        """Поиск актёров"""
        if len(text.strip()) >= 2:
            self.model = datagrid_model(
                "SELECT actor_id, fullname, created_at, updated_at FROM actor WHERE fullname ILIKE %s ORDER BY fullname",
                (f"%{text.strip()}%",)
            )
            self.view.setModel(self.model)
        elif len(text.strip()) == 0:
            self.refresh_table()

    def get_selected_actor(self):
        """Получить выбранного актёра"""
        selection = self.view.selectionModel().selectedRows()
        if not selection:
            return None

        row = selection[0].row()
        actor_id = self.model.item(row, 0).text()
        fullname = self.model.item(row, 1).text()

        return {'actor_id': actor_id, 'fullname': fullname}

    def add_actor(self):
        """Добавить актёра"""
        dialog = ActorDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            fullname = dialog.fullname_input.text().strip()
            photo_path = dialog.photo_path

            if not fullname:
                QMessageBox.warning(self, "Ошибка", "Введите имя актёра")
                return

            if not photo_path:
                QMessageBox.warning(self, "Ошибка", "Выберите фотографию")
                return

            try:
                ActorModel.create_actor(fullname, photo_path)
                QMessageBox.information(self, "Успех", f"Актёр '{fullname}' добавлен")
                self.refresh_table()
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось добавить актёра:\n{e}")

    def edit_actor(self):
        """Редактировать актёра"""
        actor = self.get_selected_actor()
        if not actor:
            QMessageBox.warning(self, "Внимание", "Выберите актёра из таблицы")
            return

        dialog = ActorDialog(self, actor['fullname'])
        if dialog.exec() == QDialog.DialogCode.Accepted:
            fullname = dialog.fullname_input.text().strip()
            photo_path = dialog.photo_path

            if not fullname:
                QMessageBox.warning(self, "Ошибка", "Введите имя актёра")
                return

            try:
                ActorModel.update_actor(actor['actor_id'], fullname, photo_path)
                QMessageBox.information(self, "Успех", f"Актёр '{fullname}' обновлён")
                self.refresh_table()
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось обновить актёра:\n{e}")

    def delete_actor(self):
        """Удалить актёра"""
        actor = self.get_selected_actor()
        if not actor:
            QMessageBox.warning(self, "Внимание", "Выберите актёра из таблицы")
            return

        confirm = QMessageBox.question(
            self,
            "Подтверждение",
            f"Удалить актёра '<b>{actor['fullname']}</b>'?<br><br>"
            f"⚠️ <b>Это действие необратимо!</b>",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if confirm == QMessageBox.StandardButton.Yes:
            try:
                ActorModel.delete_actor(actor['actor_id'])
                QMessageBox.information(self, "Успех", f"Актёр '{actor['fullname']}' удалён")
                self.refresh_table()
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось удалить актёра:\n{e}")


class ActorDialog(QDialog):
    """Диалог добавления/редактирования актёра"""

    def __init__(self, parent=None, fullname=""):
        super().__init__(parent)
        self.photo_path = None
        self.setWindowTitle("Актёр")
        self.setFixedWidth(500)

        layout = QFormLayout(self)

        self.fullname_input = QLineEdit(fullname)
        self.fullname_input.setPlaceholderText("Введите полное имя")
        layout.addRow("ФИО:", self.fullname_input)

        # Кнопка выбора фото
        photo_layout = QHBoxLayout()
        self.photo_label = QLabel("Фото не выбрано")
        self.photo_label.setStyleSheet("color: #AAAAAA;")
        self.btn_choose_photo = QPushButton("📁 Выбрать фото")
        self.btn_choose_photo.clicked.connect(self.choose_photo)
        photo_layout.addWidget(self.photo_label, stretch=1)
        photo_layout.addWidget(self.btn_choose_photo)
        layout.addRow("Фотография:", photo_layout)

        # Превью фото
        self.photo_preview = QLabel()
        self.photo_preview.setFixedSize(150, 200)
        self.photo_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.photo_preview.setStyleSheet("""
            QLabel {
                border: 2px dashed #35383D;
                border-radius: 8px;
                background-color: #1C1E22;
                color: #666;
            }
        """)
        self.photo_preview.setText("Превью фото")
        layout.addRow("Превью:", self.photo_preview)

        # Кнопки
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

    def choose_photo(self):
        """Выбрать фото"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Выберите фотографию",
            "",
            "Images (*.png *.jpg *.jpeg *.bmp)"
        )

        if file_path:
            self.photo_path = file_path
            self.photo_label.setText(file_path.split('/')[-1])
            self.photo_label.setStyleSheet("color: #00A8E8; font-weight: 600;")

            # Обработка изображения
            pixmap = QPixmap(file_path)
            if not pixmap.isNull():
                scaled_pixmap = pixmap.scaled(
                    150, 200,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
                self.photo_preview.setPixmap(scaled_pixmap)

            self.photo_preview.setStyleSheet("""
                QLabel {
                    border: 2px solid #00A8E8;
                    border-radius: 8px;
                    background-color: #16181C;
                }
            """)