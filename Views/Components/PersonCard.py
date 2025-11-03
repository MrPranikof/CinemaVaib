# Views/Components/PersonCard.py - ПРЯМОУГОЛЬНЫЕ КАРТОЧКИ
from PyQt6.QtWidgets import QFrame, QVBoxLayout, QLabel, QWidget
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap


class PersonCard(QFrame):
    """Прямоугольная карточка для отображения актера/режиссера в стиле фильмов"""

    def __init__(self, person_data, is_director=False, parent=None):
        super().__init__(parent)
        self.person_id = person_data[0]
        self.fullname = person_data[1]
        self.photo_bytes = person_data[2] if len(person_data) > 2 else None
        self.role = person_data[3] if len(person_data) > 3 else None
        self.is_director = is_director

        self.setup_ui()

    def setup_ui(self):
        self.setFixedSize(180, 280)  # Увеличили высоту
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Фото (прямоугольное как у фильмов)
        self.photo_label = QLabel()
        self.photo_label.setFixedSize(177, 200)
        self.photo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.photo_label.setStyleSheet("""
            QLabel {
                background-color: #16181C;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
            }
        """)

        if self.photo_bytes:
            try:
                pixmap = QPixmap()
                pixmap.loadFromData(bytes(self.photo_bytes))
                if not pixmap.isNull():
                    scaled_pixmap = pixmap.scaled(
                        180, 200,
                        Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.SmoothTransformation
                    )
                    self.photo_label.setPixmap(scaled_pixmap)
                else:
                    self.set_placeholder_photo()
            except Exception as e:
                print(f"Ошибка загрузки фото: {e}")
                self.set_placeholder_photo()
        else:
            self.set_placeholder_photo()

        layout.addWidget(self.photo_label)

        # Информационная панель
        info_container = QWidget()
        info_container.setFixedHeight(85)  # Увеличили высоту панели
        info_container.setStyleSheet("""
            QWidget {
                background-color: #1C1E22;
                border-bottom-left-radius: 8px;
                border-bottom-right-radius: 8px;
                padding: 8px;
            }
        """)

        info_layout = QVBoxLayout(info_container)
        info_layout.setContentsMargins(10, 8, 10, 8)
        info_layout.setSpacing(4)

        # Имя
        name_label = QLabel(self.fullname)
        name_label.setWordWrap(True)
        name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        name_label.setStyleSheet("""
            QLabel {
                color: #FFFFFF;
                font-weight: 600;
                font-size: 13px;
                background-color: transparent;
            }
        """)
        name_label.setMaximumHeight(35)  # Увеличили высоту для имени
        info_layout.addWidget(name_label)

        # Роль для актеров или метка "Режиссёр"
        if self.is_director:
            # Метка "Режиссёр" для режиссера
            director_label = QLabel("Режиссёр")
            director_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            director_label.setStyleSheet("""
                QLabel {
                    color: #FFD700;
                    font-size: 11px;
                    background-color: transparent;
                    font-weight: 600;
                }
            """)
            info_layout.addWidget(director_label)
        elif self.role:
            # Роль для актера
            role_label = QLabel(self.role)
            role_label.setWordWrap(True)
            role_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            role_label.setStyleSheet("""
                QLabel {
                    color: #00A8E8;
                    font-size: 11px;
                    background-color: transparent;
                    font-style: italic;
                }
            """)
            role_label.setMaximumHeight(30)  # Увеличили высоту для роли
            info_layout.addWidget(role_label)

        info_layout.addStretch()
        layout.addWidget(info_container)

        self.setStyleSheet("""
            QFrame {
                background-color: #1C1E22;
                border: 2px solid #2A2C32;
                border-radius: 8px;
            }
            QFrame:hover {
                border-color: #00A8E8;
                background-color: #20222A;
            }
        """)

    def set_placeholder_photo(self):
        """Заглушка для фото в стиле фильмов"""
        placeholder_text = "🎬\n\nРежиссёр" if self.is_director else "🎭\n\nАктёр"
        self.photo_label.setText(placeholder_text)
        self.photo_label.setStyleSheet("""
            QLabel {
                background-color: #16181C;
                color: #666666;
                font-size: 16px;
                font-weight: 600;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                border: 2px dashed #2A2C32;
            }
        """)