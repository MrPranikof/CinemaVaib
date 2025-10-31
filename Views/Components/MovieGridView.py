# Views/Components/MovieGridView.py
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QScrollArea, QGridLayout, QComboBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from Views.Components.MovieCard import MovieCard
from Models.MovieModel import MovieModel


class MovieGridView(QWidget):
    """Сетка карточек фильмов с поиском и фильтрацией"""
    movie_clicked = pyqtSignal(int)  # movie_id

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_movies = []
        self.setup_ui()
        self.load_movies()

    def setup_ui(self):
        """Настройка интерфейса"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # Панель поиска и фильтров
        search_panel = self.create_search_panel()
        layout.addWidget(search_panel)

        # Область прокрутки для карточек
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
        """)

        # Контейнер для карточек
        self.cards_container = QWidget()
        self.cards_layout = QGridLayout(self.cards_container)
        self.cards_layout.setSpacing(20)
        self.cards_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)

        scroll.setWidget(self.cards_container)
        layout.addWidget(scroll, stretch=1)

    def create_search_panel(self):
        """Создать панель поиска и фильтров"""
        panel = QWidget()
        panel.setFixedHeight(60)
        panel_layout = QHBoxLayout(panel)
        panel_layout.setContentsMargins(0, 0, 0, 0)
        panel_layout.setSpacing(15)

        # Поиск
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Поиск фильмов...")
        self.search_input.setFixedHeight(40)
        self.search_input.textChanged.connect(self.on_search)
        panel_layout.addWidget(self.search_input, stretch=2)

        # Фильтр по жанру
        self.genre_combo = QComboBox()
        self.genre_combo.setFixedHeight(40)
        self.genre_combo.addItem("Все жанры", 0)

        genres = MovieModel.get_all_genres()
        for genre_id, genre_name in genres:
            self.genre_combo.addItem(genre_name, genre_id)

        self.genre_combo.currentIndexChanged.connect(self.on_genre_changed)
        panel_layout.addWidget(self.genre_combo, stretch=1)

        # Кнопка обновления
        btn_refresh = QPushButton("🔄 Обновить")
        btn_refresh.setFixedHeight(40)
        btn_refresh.clicked.connect(self.load_movies)
        panel_layout.addWidget(btn_refresh)

        return panel

    def load_movies(self):
        """Загрузить все фильмы"""
        movies = MovieModel.get_all_movies()
        self.display_movies(movies)

    def on_search(self, text):
        """Обработка поиска"""
        if len(text.strip()) >= 2:
            movies = MovieModel.search_movies(text.strip())
            self.display_movies(movies)
        elif len(text.strip()) == 0:
            self.load_movies()

    def on_genre_changed(self, index):
        """Обработка изменения жанра"""
        genre_id = self.genre_combo.currentData()

        if genre_id == 0:
            self.load_movies()
        else:
            movies = MovieModel.get_movies_by_genre(genre_id)
            self.display_movies(movies)

    def display_movies(self, movies):
        """Отобразить карточки фильмов"""
        # Очищаем старые карточки
        while self.cards_layout.count():
            item = self.cards_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        self.current_movies = movies

        if not movies:
            # Показать сообщение "Ничего не найдено"
            no_result = QLabel("🎬 Фильмы не найдены")
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
            card = MovieCard(movie_data)
            card.clicked.connect(self.on_movie_clicked)

            self.cards_layout.addWidget(card, row, col)

            col += 1
            if col >= max_cols:
                col = 0
                row += 1

    def on_movie_clicked(self, movie_id):
        """Обработка клика по карточке"""
        self.movie_clicked.emit(movie_id)