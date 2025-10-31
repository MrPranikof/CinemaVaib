from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap, QCursor


class MovieCard(QFrame):
    """Карточка фильма"""
    clicked = pyqtSignal(int)

    def __init__(self, movie_data, parent=None):
        super().__init__(parent)
        self.movie_id = movie_data[0]
        self.title = movie_data[1]
        self.description = movie_data[2]
        self.image_bytes = movie_data[3]
        self.rating = movie_data[5]

        self.is_hovered = False
        self.setup_ui()

    def setup_ui(self):
        """Настройка интерфейса карточки"""
        self.setObjectName("MovieCard")
        self.setFixedSize(220, 360)
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        self.update_styles()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Контейнер для постера
        self.poster_label = QLabel()
        self.poster_label.setFixedSize(215, 280)
        self.poster_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.poster_label.setScaledContents(False)
        self.poster_label.setStyleSheet("""
            QLabel {
                background-color: #16181C;
                border-top-left-radius: 10px;
                border-top-right-radius: 10px;
            }
        """)

        # Загружаем изображение
        if self.image_bytes:
            try:
                pixmap = QPixmap()
                pixmap.loadFromData(bytes(self.image_bytes))

                if not pixmap.isNull():
                    scaled_pixmap = pixmap.scaled(
                        215, 275,
                        Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.SmoothTransformation
                    )
                    self.poster_label.setPixmap(scaled_pixmap)
                else:
                    self.set_placeholder()
            except Exception as e:
                print(f"Ошибка загрузки изображения: {e}")
                self.set_placeholder()
        else:
            self.set_placeholder()

        layout.addWidget(self.poster_label)

        # Информация о фильме
        info_container = QWidget()
        info_container.setStyleSheet("background-color: transparent;")
        info_layout = QVBoxLayout(info_container)
        info_layout.setContentsMargins(10, 8, 10, 8)
        info_layout.setSpacing(4)

        # Название
        self.title_label = QLabel(self.title)
        self.title_label.setWordWrap(True)
        self.title_label.setMaximumHeight(40)
        self.title_label.setStyleSheet("""
            QLabel {
                color: #FFFFFF;
                font-weight: 600;
                font-size: 14px;
                background-color: transparent;
            }
        """)
        info_layout.addWidget(self.title_label)

        # Рейтинг и цена
        bottom_info = QLabel(f"⭐ {self.rating:.1f}")
        bottom_info.setStyleSheet("""
            QLabel {
                color: #00A8E8;
                font-size: 13px;
                font-weight: 600;
                background-color: transparent;
            }
        """)
        info_layout.addWidget(bottom_info)

        layout.addWidget(info_container)

    def set_placeholder(self):
        """Заглушка для отсутствующего изображения"""
        self.poster_label.clear()
        self.poster_label.setText("🎬\n\nНет постера")
        self.poster_label.setStyleSheet("""
            QLabel {
                background-color: #16181C;
                color: #666;
                font-size: 16px;
                border-top-left-radius: 10px;
                border-top-right-radius: 10px;
            }
        """)

    def update_styles(self):
        """Обновить стили"""
        if self.is_hovered:
            self.setStyleSheet("""
                QFrame#MovieCard {
                    background-color: #20222A;
                    border-radius: 12px;
                    border: 2px solid #00A8E8;
                }
            """)
        else:
            self.setStyleSheet("""
                QFrame#MovieCard {
                    background-color: #1C1E22;
                    border-radius: 12px;
                    border: 2px solid #2A2C32;
                }
            """)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.movie_id)
        super().mousePressEvent(event)

    def enterEvent(self, event):
        self.is_hovered = True
        self.update_styles()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.is_hovered = False
        self.update_styles()
        super().leaveEvent(event)