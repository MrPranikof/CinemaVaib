from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QGridLayout, QComboBox, QFrame, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from Views.Components.WatchlistMovieCard import WatchlistMovieCard
from Models.WatchlistModel import WatchlistModel


class WatchlistView(QWidget):
    """Виджет избранных фильмов"""
    movie_clicked = pyqtSignal(int)  # movie_id

    def __init__(self, user_id, go_back=None):
        super().__init__()
        self.user_id = user_id
        self.go_back = go_back
        self.current_watchlist = []
        self.setup_ui()
        self.load_watchlist()

    def setup_ui(self):
        """Настройка интерфейса как в MovieDetailView"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Scroll Area для ВСЕГО контента
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setObjectName("ContentArea")

        # Контейнер контента
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(20)

        # Заголовок и кнопка назад
        header_layout = QHBoxLayout()

        title = QLabel("❤️ Мое избранное")
        title.setObjectName("TitleLabel")
        header_layout.addWidget(title)

        header_layout.addStretch()

        if self.go_back:
            btn_back = QPushButton("⬅ Назад")
            btn_back.setObjectName("BackButton")
            btn_back.clicked.connect(self.go_back)
            header_layout.addWidget(btn_back)

        content_layout.addLayout(header_layout)

        # Статистика
        self.stats_frame = self.create_stats_frame()
        content_layout.addWidget(self.stats_frame)

        # Панель фильтров
        filter_panel = self.create_filter_panel()
        content_layout.addWidget(filter_panel)

        # Контейнер для карточек фильмов
        self.cards_container = QWidget()
        self.cards_layout = QGridLayout(self.cards_container)
        self.cards_layout.setSpacing(20)
        self.cards_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)

        content_layout.addWidget(self.cards_container, stretch=1)

        scroll.setWidget(content_widget)
        main_layout.addWidget(scroll)

    def create_stats_frame(self):
        """Создать фрейм со статистикой"""
        frame = QFrame()
        frame.setObjectName("StatsFrame")
        frame.setStyleSheet("""
            QFrame#StatsFrame {
                background-color: #1C1E22;
                border: 1px solid #2A2C32;
                border-radius: 8px;
                padding: 15px;
            }
        """)

        layout = QHBoxLayout(frame)

        stats = WatchlistModel.get_watchlist_stats(self.user_id)
        if stats:
            total, watched, planned, watching = stats
        else:
            total, watched, planned, watching = 0, 0, 0, 0

        stats_text = f"""
            <div style='color: #FFFFFF; font-weight: 600; font-size: 16px;'>📊 Статистика избранного</div>
            <div style='color: #CCCCCC; font-size: 14px; margin-top: 8px;'>
                📁 Всего: <span style='color: #00A8E8;'>{total}</span> | 
                ✅ Просмотрено: <span style='color: #55C78C;'>{watched}</span> | 
                📝 Запланировано: <span style='color: #FFD700;'>{planned}</span> | 
                🎬 Смотрю: <span style='color: #FF6B6B;'>{watching}</span>
            </div>
        """

        stats_label = QLabel(stats_text)
        stats_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(stats_label)

        layout.addStretch()

        return frame

    def create_filter_panel(self):
        """Создать панель фильтров"""
        panel = QWidget()
        panel.setFixedHeight(50)
        panel_layout = QHBoxLayout(panel)
        panel_layout.setContentsMargins(0, 0, 0, 0)
        panel_layout.setSpacing(15)

        # Фильтр по статусу
        self.status_combo = QComboBox()
        self.status_combo.setFixedHeight(40)
        self.status_combo.addItem("🎬 Все фильмы", "all")
        self.status_combo.addItem("📝 Запланировано", "Planned")
        self.status_combo.addItem("🎬 Смотрю", "Watching")
        self.status_combo.addItem("✅ Просмотрено", "Watched")

        self.status_combo.currentIndexChanged.connect(self.apply_filters)
        panel_layout.addWidget(self.status_combo)

        # Кнопка обновления
        btn_refresh = QPushButton("🔄 Обновить")
        btn_refresh.setFixedHeight(40)
        btn_refresh.clicked.connect(self.load_watchlist)
        panel_layout.addWidget(btn_refresh)

        panel_layout.addStretch()
        return panel

    def load_watchlist(self):
        """Загрузить избранные фильмы"""
        try:
            self.current_watchlist = WatchlistModel.get_user_watchlist(self.user_id)
            self.apply_filters()
            self.update_stats()
        except Exception as e:
            print(f"Ошибка при загрузке избранного: {e}")
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить избранное: {str(e)}")

    def apply_filters(self):
        """Применить фильтры"""
        try:
            status_filter = self.status_combo.currentData()

            if status_filter == "all":
                filtered_movies = self.current_watchlist
            else:
                filtered_movies = [movie for movie in self.current_watchlist if movie[7] == status_filter]

            self.display_movies(filtered_movies)
        except Exception as e:
            print(f"Ошибка при применении фильтров: {e}")

    def display_movies(self, movies):
        """Отобразить карточки фильмов"""
        try:
            # Очищаем старые карточки
            while self.cards_layout.count():
                item = self.cards_layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()

            if not movies:
                # Показать сообщение "Ничего не найдено"
                no_result = QLabel("❤️ В избранном пока нет фильмов")
                no_result.setAlignment(Qt.AlignmentFlag.AlignCenter)
                no_result.setStyleSheet("""
                    QLabel {
                        color: #666;
                        font-size: 18px;
                        padding: 50px;
                    }
                """)
                self.cards_layout.addWidget(no_result, 0, 0)
                return

            # Отображаем карточки в сетке (4 в ряд)
            row, col = 0, 0
            max_cols = 4

            for movie_data in movies:
                try:
                    card = WatchlistMovieCard(movie_data, self.user_id)
                    card.clicked.connect(self.on_movie_clicked)
                    card.status_changed.connect(self.on_status_changed)

                    self.cards_layout.addWidget(card, row, col)

                    col += 1
                    if col >= max_cols:
                        col = 0
                        row += 1

                except Exception as e:
                    print(f"Ошибка при создании карточки фильма: {e}")
                    continue

        except Exception as e:
            print(f"Ошибка при отображении фильмов: {e}")

    def update_stats(self):
        """Обновить статистику"""
        try:
            stats = WatchlistModel.get_watchlist_stats(self.user_id)
            if stats:
                total, watched, planned, watching = stats
            else:
                total, watched, planned, watching = 0, 0, 0, 0

            stats_text = f"""
                <div style='color: #FFFFFF; font-weight: 600; font-size: 16px;'>📊 Статистика избранного</div>
                <div style='color: #CCCCCC; font-size: 14px; margin-top: 8px;'>
                    📁 Всего: <span style='color: #00A8E8;'>{total}</span> | 
                    ✅ Просмотрено: <span style='color: #55C78C;'>{watched}</span> | 
                    📝 Запланировано: <span style='color: #FFD700;'>{planned}</span> | 
                    🎬 Смотрю: <span style='color: #FF6B6B;'>{watching}</span>
                </div>
            """

            # Находим QLabel в stats_frame и обновляем его
            stats_label = self.stats_frame.findChild(QLabel)
            if stats_label:
                stats_label.setText(stats_text)
        except Exception as e:
            print(f"Ошибка при обновлении статистики: {e}")

    def on_movie_clicked(self, movie_id):
        """Обработчик клика по карточке"""
        self.movie_clicked.emit(movie_id)

    def on_status_changed(self):
        try:
            self.update_stats()

        except Exception as e:
            print(f"КРИТИЧЕСКАЯ ОШИБКА в on_status_changed: {e}")