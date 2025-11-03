from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QScrollArea, QGridLayout, QComboBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from Views.Components.MovieCard import MovieCard
from Models.MovieModel import MovieModel


class MovieGridView(QWidget):
    """Сетка карточек фильмов с поиском, фильтрацией и ПАГИНАЦИЕЙ"""
    movie_clicked = pyqtSignal(int)

    def __init__(self, parent=None, user_id=None):
        super().__init__(parent)
        self.current_movies = []
        self.user_id = user_id
        self.current_page = 1
        self.movies_per_page = 20  # 5 рядов по 4 фильма = 20 фильмов на странице
        self.total_movies = 0

        self.setup_ui()
        self.load_movies()

    def setup_ui(self):
        """Настройка интерфейса с пагинацией"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

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

        # Панель пагинации
        self.pagination_panel = self.create_pagination_panel()
        layout.addWidget(self.pagination_panel)

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

    def create_pagination_panel(self):
        """Панель пагинации с крупными кнопками (35px)"""
        panel = QWidget()
        panel.setFixedHeight(35)  # ✅ Увеличенная высота
        panel_layout = QHBoxLayout(panel)
        panel_layout.setContentsMargins(0, 2, 0, 2)
        panel_layout.setSpacing(8)

        # Информация (более крупный шрифт)
        self.page_info_label = QLabel("Страница 1 из 1")
        self.page_info_label.setStyleSheet("""
            color: #CCCCCC; 
            font-size: 13px;
            font-weight: 500;
        """)
        panel_layout.addWidget(self.page_info_label)

        panel_layout.addStretch()
        self.prev_btn = QPushButton("◀ Назад")
        self.prev_btn.setFixedSize(80, 33)
        self.prev_btn.setStyleSheet("""
            QPushButton {
                background-color: #2A2C32;
                color: #FFFFFF;
                border: 1px solid #35383D;
                border-radius: 5px;
                font-size: 12px;
                font-weight: 500;
            }
            QPushButton:hover:enabled {
                background-color: #00A8E8;
                border-color: #00A8E8;
            }
            QPushButton:disabled {
                color: #666666;
                background-color: #1C1E22;
            }
        """)
        self.prev_btn.clicked.connect(self.prev_page)
        panel_layout.addWidget(self.prev_btn)

        # Номера страниц
        self.pages_layout = QHBoxLayout()
        self.pages_layout.setSpacing(5)
        panel_layout.addLayout(self.pages_layout)

        self.next_btn = QPushButton("Вперед ▶")
        self.next_btn.setFixedSize(80, 33)
        self.next_btn.setStyleSheet("""
            QPushButton {
                background-color: #2A2C32;
                color: #FFFFFF;
                border: 1px solid #35383D;
                border-radius: 5px;
                font-size: 12px;
                font-weight: 500;
            }
            QPushButton:hover:enabled {
                background-color: #00A8E8;
                border-color: #00A8E8;
            }
            QPushButton:disabled {
                color: #666666;
                background-color: #1C1E22;
            }
        """)
        self.next_btn.clicked.connect(self.next_page)
        panel_layout.addWidget(self.next_btn)

        return panel

    def load_movies(self, page=None):
        """Загрузить фильмы для указанной страницы"""
        # ✅ Если page не указан или является bool - используем 1
        if page is None or isinstance(page, bool):
            page = 1

        self.current_page = page

        # Сбрасываем фильтры при обычной загрузке
        if not hasattr(self, 'search_text') and not hasattr(self, 'current_genre_id'):
            movies = MovieModel.get_all_movies()
            self.display_movies(movies, page)
        else:
            # Используем текущие фильтры
            self.apply_filters()

    def on_search(self, text):
        """Обработка поиска"""
        self.search_text = text.strip()
        if len(self.search_text) >= 2:
            self.current_page = 1
            self.apply_filters()
        elif len(self.search_text) == 0:
            self.current_page = 1
            if hasattr(self, 'search_text'):
                delattr(self, 'search_text')
            self.load_movies(1)

    def on_genre_changed(self, index):
        """Обработка изменения жанра"""
        genre_id = self.genre_combo.currentData()
        self.current_genre_id = genre_id
        self.current_page = 1
        self.apply_filters()

    def apply_filters(self):
        """Применить фильтры и пагинацию"""
        try:
            # Определяем какие фильмы загружать
            if hasattr(self, 'search_text') and self.search_text:
                movies = MovieModel.search_movies(self.search_text)
            elif hasattr(self, 'current_genre_id') and self.current_genre_id != 0:
                movies = MovieModel.get_movies_by_genre(self.current_genre_id)
            else:
                movies = MovieModel.get_all_movies()

            self.display_movies(movies, self.current_page)

        except Exception as e:
            print(f"Ошибка при применении фильтров: {e}")

    def display_movies(self, movies, page=1):
        """Отобразить карточки фильмов для указанной страницы"""
        # Очищаем старые карточки
        while self.cards_layout.count():
            item = self.cards_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Очищаем номера страниц
        while self.pages_layout.count():
            item = self.pages_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        self.current_movies = movies
        self.total_movies = len(movies)

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
            self.update_pagination(0)
            return

        # Рассчитываем пагинацию
        total_pages = (self.total_movies + self.movies_per_page - 1) // self.movies_per_page
        start_index = (page - 1) * self.movies_per_page
        end_index = min(start_index + self.movies_per_page, self.total_movies)

        current_page_movies = movies[start_index:end_index]

        # Отображаем карточки в сетке (4 в ряд)
        row, col = 0, 0
        max_cols = 4

        for movie_data in current_page_movies:
            card = MovieCard(movie_data)
            card.clicked.connect(self.on_movie_clicked)

            self.cards_layout.addWidget(card, row, col)

            col += 1
            if col >= max_cols:
                col = 0
                row += 1

        # Обновляем пагинацию
        self.update_pagination(total_pages)

    def update_pagination(self, total_pages):
        """Обновить пагинацию с крупными кнопками"""
        self.page_info_label.setText(f"Страница {self.current_page} из {total_pages if total_pages > 0 else 1}")

        self.prev_btn.setEnabled(self.current_page > 1)
        self.next_btn.setEnabled(self.current_page < total_pages)

        while self.pages_layout.count():
            item = self.pages_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if total_pages > 1:
            # ✅ Показываем только 5 страниц для экономии места
            start_page = max(1, self.current_page - 2)
            end_page = min(total_pages, start_page + 4)

            if start_page == 1:
                end_page = min(total_pages, 5)
            if end_page == total_pages:
                start_page = max(1, total_pages - 4)

            for page_num in range(start_page, end_page + 1):
                page_btn = QPushButton(str(page_num))
                page_btn.setFixedSize(30, 30)  # ✅ Крупные кнопки страниц

                if page_num == self.current_page:
                    page_btn.setStyleSheet("""
                        QPushButton {
                            background-color: #00A8E8;
                            color: #FFFFFF;
                            border: none;
                            border-radius: 5px;
                            font-weight: bold;
                            font-size: 13px;
                        }
                    """)
                else:
                    page_btn.setStyleSheet("""
                        QPushButton {
                            background-color: #2A2C32;
                            color: #FFFFFF;
                            border: 1px solid #35383D;
                            border-radius: 5px;
                            font-size: 12px;
                        }
                        QPushButton:hover {
                            background-color: #00A8E8;
                            border-color: #00A8E8;
                        }
                    """)

                page_btn.clicked.connect(lambda checked, p=page_num: self.go_to_page(p))
                self.pages_layout.addWidget(page_btn)

    def go_to_page(self, page):
        """Перейти на указанную страницу"""
        self.current_page = page
        self.apply_filters()

    def prev_page(self):
        """Перейти на предыдущую страницу"""
        if self.current_page > 1:
            self.go_to_page(self.current_page - 1)

    def next_page(self):
        """Перейти на следующую страницу"""
        total_pages = (self.total_movies + self.movies_per_page - 1) // self.movies_per_page
        if self.current_page < total_pages:
            self.go_to_page(self.current_page + 1)

    def on_movie_clicked(self, movie_id):
        """Обработчик клика по карточке"""
        self.movie_clicked.emit(movie_id)