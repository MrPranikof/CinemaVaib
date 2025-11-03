from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame, QComboBox, QHBoxLayout
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap, QCursor
from Models.WatchlistModel import WatchlistModel


class WatchlistMovieCard(QFrame):
    """Карточка фильма в избранном с выбором статуса просмотра"""
    clicked = pyqtSignal(int)  # movie_id
    status_changed = pyqtSignal(int, str)  # movie_id, new_status

    def __init__(self, watchlist_data, user_id, parent=None):
        super().__init__(parent)
        self.watchlist_id = watchlist_data[0]
        self.movie_id = watchlist_data[1]
        self.title = watchlist_data[2]
        self.description = watchlist_data[3]
        self.image_bytes = watchlist_data[4]
        self.rating = watchlist_data[6]
        self.current_status = watchlist_data[7]  # статус из БД
        self.user_id = user_id

        self.is_hovered = False
        self.setup_ui()

    def setup_ui(self):
        """Настройка интерфейса карточки"""
        self.setObjectName("MovieCard")
        self.setFixedSize(220, 400)  # Увеличили высоту для комбобокса
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
        info_layout.setSpacing(8)

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
        stats_layout = QHBoxLayout()

        rating_label = QLabel(f"⭐ {self.rating:.1f}")
        rating_label.setStyleSheet("""
            QLabel {
                color: #00A8E8;
                font-size: 13px;
                font-weight: 600;
                background-color: transparent;
            }
        """)
        stats_layout.addWidget(rating_label)

        stats_layout.addStretch()

        info_layout.addLayout(stats_layout)

        # Выбор статуса просмотра
        status_layout = QHBoxLayout()
        status_layout.setSpacing(5)

        status_label = QLabel("Статус:")
        status_label.setStyleSheet("""
            QLabel {
                color: #AAAAAA;
                font-size: 12px;
                background-color: transparent;
            }
        """)
        status_layout.addWidget(status_label)

        self.status_combo = QComboBox()
        self.status_combo.setFixedHeight(28)
        self.status_combo.addItem("📝 Запланировано", "Planned")
        self.status_combo.addItem("🎬 Смотрю", "Watching")
        self.status_combo.addItem("✅ Просмотрено", "Watched")

        # Устанавливаем текущий статус
        self.set_current_status()

        self.status_combo.currentIndexChanged.connect(self.on_status_changed)
        self.status_combo.setStyleSheet("""
            QComboBox {
                background-color: #2A2C32;
                color: #FFFFFF;
                border: 1px solid #35383D;
                border-radius: 5px;
                padding: 2px 8px;
                font-size: 11px;
            }
            QComboBox:hover {
                border-color: #00A8E8;
            }
            QComboBox::drop-down {
                border: none;
                width: 15px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 4px solid #EAEAEA;
            }
        """)

        status_layout.addWidget(self.status_combo)
        info_layout.addLayout(status_layout)

        layout.addWidget(info_container)

    def set_current_status(self):
        """Установить текущий статус в комбобоксе"""
        status_mapping = {
            "Planned": 0,
            "Watching": 1,
            "Watched": 2
        }

        current_index = status_mapping.get(self.current_status, 0)
        self.status_combo.setCurrentIndex(current_index)

    def on_status_changed(self):
        """Обработчик изменения статуса"""
        new_status = self.status_combo.currentData()
        if new_status != self.current_status:
            try:
                # Обновляем в базе данных
                success = WatchlistModel.update_watchlist_status(self.watchlist_id, new_status)
                if success:
                    self.current_status = new_status
                    self.status_changed.emit(self.movie_id, new_status)

                    # Визуальная обратная связь
                    self.show_status_change_effect()
            except Exception as e:
                print(f"Ошибка при изменении статуса: {e}")

    def show_status_change_effect(self):
        """Показать визуальный эффект изменения статуса"""
        original_style = self.styleSheet()
        self.setStyleSheet("""
            QFrame#MovieCard {
                background-color: #1C1E22;
                border-radius: 12px;
                border: 2px solid #55C78C;
            }
        """)

        # Возвращаем исходный стиль через 500ms
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(500, lambda: self.setStyleSheet(original_style))

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
            # Проверяем, не было ли нажатия на комбобокс
            if self.status_combo and self.status_combo.underMouse():
                return
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