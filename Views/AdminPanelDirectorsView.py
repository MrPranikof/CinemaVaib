from PyQt6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QPushButton, QHBoxLayout,
    QTableView, QSizePolicy, QMessageBox, QSpacerItem, QDialog,
    QLineEdit, QFormLayout, QDialogButtonBox, QFileDialog
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from core.database import datagrid_model
from Models.DirectorModel import DirectorModel


class AdminPanelDirectorsView(QWidget):
    def __init__(self, go_back=None):
        super().__init__()
        self.go_back = go_back

        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 30, 40, 30)
        layout.setSpacing(25)

        # Заголовок
        header = QHBoxLayout()
        title = QLabel("🎬 Управление режиссёрами")
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

        # Таблица
        self.refresh_table()

        self.view = QTableView()
        self.view.setModel(self.model)
        self.view.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self.view.setSelectionMode(QTableView.SelectionMode.SingleSelection)
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.view.horizontalHeader().setStretchLastSection(True)
        self.view.setAlternatingRowColors(True)

        layout.addWidget(self.view, stretch=1)

        # Кнопки
        btns = QHBoxLayout()
        btns.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))

        self.btn_add = QPushButton("➕ Добавить режиссёра")
        self.btn_add.clicked.connect(self.add_director)
        btns.addWidget(self.btn_add)

        self.btn_edit = QPushButton("✏️ Редактировать")
        self.btn_edit.clicked.connect(self.edit_director)
        btns.addWidget(self.btn_edit)

        self.btn_delete = QPushButton("🗑 Удалить")
        self.btn_delete.setObjectName("LogoutButton")
        self.btn_delete.clicked.connect(self.delete_director)
        btns.addWidget(self.btn_delete)

        self.btn_refresh = QPushButton("🔄 Обновить")
        self.btn_refresh.clicked.connect(self.refresh_table)
        btns.addWidget(self.btn_refresh)

        btns.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        layout.addLayout(btns)

    def refresh_table(self):
        self.model = datagrid_model(
            "SELECT director_id, fullname, created_at, updated_at FROM director ORDER BY fullname"
        )

        if hasattr(self, 'view'):
            self.view.setModel(self.model)

        for row in range(self.model.rowCount()):
            for col in range(self.model.columnCount()):
                item = self.model.item(row, col)
                if item:
                    item.setEditable(False)

    def on_search(self, text):
        if len(text.strip()) >= 2:
            self.model = datagrid_model(
                "SELECT director_id, fullname, created_at, updated_at FROM director WHERE fullname ILIKE %s ORDER BY fullname",
                (f"%{text.strip()}%",)
            )
            self.view.setModel(self.model)
        elif len(text.strip()) == 0:
            self.refresh_table()

    def get_selected_director(self):
        selection = self.view.selectionModel().selectedRows()
        if not selection:
            return None

        row = selection[0].row()
        return {
            'director_id': self.model.item(row, 0).text(),
            'fullname': self.model.item(row, 1).text()
        }

    def add_director(self):
        dialog = DirectorDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            fullname = dialog.fullname_input.text().strip()
            photo_path = dialog.photo_path

            if not fullname or not photo_path:
                QMessageBox.warning(self, "Ошибка", "Заполните все поля")
                return

            try:
                DirectorModel.create_director(fullname, photo_path)
                QMessageBox.information(self, "Успех", f"Режиссёр '{fullname}' добавлен")
                self.refresh_table()
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", str(e))

    def edit_director(self):
        director = self.get_selected_director()
        if not director:
            QMessageBox.warning(self, "Внимание", "Выберите режиссёра")
            return

        dialog = DirectorDialog(self, director['fullname'])
        if dialog.exec() == QDialog.DialogCode.Accepted:
            fullname = dialog.fullname_input.text().strip()
            photo_path = dialog.photo_path

            try:
                DirectorModel.update_director(director['director_id'], fullname, photo_path)
                QMessageBox.information(self, "Успех", "Режиссёр обновлён")
                self.refresh_table()
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", str(e))

    def delete_director(self):
        director = self.get_selected_director()
        if not director:
            QMessageBox.warning(self, "Внимание", "Выберите режиссёра")
            return

        confirm = QMessageBox.question(
            self, "Подтверждение",
            f"Удалить режиссёра '<b>{director['fullname']}</b>'?<br><br>⚠️ <b>Это действие необратимо!</b>",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if confirm == QMessageBox.StandardButton.Yes:
            try:
                DirectorModel.delete_director(director['director_id'])
                QMessageBox.information(self, "Успех", "Режиссёр удалён")
                self.refresh_table()
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", str(e))


class DirectorDialog(QDialog):
    def __init__(self, parent=None, fullname=""):
        super().__init__(parent)
        self.photo_path = None
        self.setWindowTitle("Режиссёр")
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
            self, "Выберите фотографию", "",
            "Images (*.png *.jpg *.jpeg *.bmp)"
        )

        if file_path:
            self.photo_path = file_path
            self.photo_label.setText(file_path.split('/')[-1])
            self.photo_label.setStyleSheet("color: #00A8E8; font-weight: 600;")

            pixmap = QPixmap(file_path)
            if not pixmap.isNull():
                scaled_pixmap = pixmap.scaled(
                    150, 200,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
                self.photo_preview.setPixmap(scaled_pixmap)