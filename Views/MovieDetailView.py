from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout,
    QScrollArea, QFrame, QTextEdit, QComboBox, QMessageBox,
    QGridLayout, QTabWidget, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap
from Models.MovieModel import MovieModel
from Models.ReviewModel import ReviewModel
from Models.SessionModel import SessionModel
from Views.Components.PersonCard import PersonCard
from Views.Components.SeatSelectionView import SeatSelectionView


class SessionCard(QFrame):
    """Карточка сеанса в стиле приложения"""
    book_clicked = pyqtSignal(int, str, str)

    def __init__(self, session_data, parent=None):
        super().__init__(parent)
        self.session_id = session_data[0]
        self.movie_title = session_data[1]
        self.hall_name = session_data[3]
        self.session_time = session_data[4]
        self.price = session_data[5]
        self.setup_ui()

    def setup_ui(self):
        self.setObjectName("SessionCard")
        self.setFixedSize(320, 140)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(12)

        # Название зала
        hall_label = QLabel(f"🎭 {self.hall_name}")
        hall_label.setStyleSheet("""
            color: #FFFFFF;
            font-weight: 600;
            font-size: 16px;
            font-family: 'Montserrat', sans-serif;
        """)
        layout.addWidget(hall_label)

        # Время сеанса
        time_label = QLabel(f"🕒 {self.session_time.strftime('%d.%m.%Y в %H:%M')}")
        time_label.setStyleSheet("""
            color: #CCCCCC;
            font-size: 14px;
            font-family: 'Roboto', sans-serif;
        """)
        layout.addWidget(time_label)

        layout.addStretch()

        # Разделитель
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet("background-color: #2A2C32; max-height: 1px;")
        layout.addWidget(line)

        # Нижняя панель: цена + кнопка
        bottom_layout = QHBoxLayout()
        bottom_layout.setSpacing(15)

        price_label = QLabel(f"{int(self.price)} ₽")
        price_label.setStyleSheet("""
            color: #00A8E8;
            font-weight: 700;
            font-size: 22px;
            font-family: 'Oswald', sans-serif;
        """)
        bottom_layout.addWidget(price_label)

        bottom_layout.addStretch()

        book_btn = QPushButton("Забронировать")
        book_btn.setFixedSize(150, 36)
        book_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        book_btn.clicked.connect(self.on_book_clicked)
        bottom_layout.addWidget(book_btn)

        layout.addLayout(bottom_layout)

        self.setStyleSheet("""
            QFrame#SessionCard {
                background-color: #1C1E22;
                border: 2px solid #2A2C32;
                border-radius: 8px;
            }
            QFrame#SessionCard:hover {
                border-color: #00A8E8;
                background-color: #20222A;
            }
        """)

    def on_book_clicked(self):
        self.book_clicked.emit(
            self.session_id,
            self.movie_title,
            self.session_time.strftime('%d.%m.%Y %H:%M')
        )


class ReviewWidget(QFrame):
    """Виджет отзыва в стиле приложения"""

    def __init__(self, review_data, parent=None):
        super().__init__(parent)
        self.review_id = review_data[0]
        self.username = review_data[1]
        self.rating = review_data[2]
        self.comment = review_data[3]
        self.created_at = review_data[4]
        self.setup_ui()

    def setup_ui(self):
        self.setObjectName("ReviewWidget")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(10)

        # Шапка отзыва
        header_layout = QHBoxLayout()
        header_layout.setSpacing(12)

        # Аватар (первая буква)
        avatar = QLabel(self.username[0].upper())
        avatar.setFixedSize(44, 44)
        avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        avatar.setStyleSheet("""
            background-color: #00A8E8;
            color: #FFFFFF;
            border-radius: 22px;
            font-weight: 700;
            font-size: 20px;
            font-family: 'Montserrat', sans-serif;
        """)
        header_layout.addWidget(avatar)

        # Информация о пользователе
        user_info = QVBoxLayout()
        user_info.setSpacing(2)

        user_label = QLabel(self.username)
        user_label.setStyleSheet("""
            font-weight: 600;
            color: #FFFFFF;
            font-size: 15px;
            font-family: 'Montserrat', sans-serif;
        """)
        user_info.addWidget(user_label)

        date_label = QLabel(self.created_at.strftime("%d.%m.%Y в %H:%M"))
        date_label.setStyleSheet("""
            color: #7A7A7A;
            font-size: 12px;
            font-family: 'Roboto', sans-serif;
        """)
        user_info.addWidget(date_label)

        header_layout.addLayout(user_info)
        header_layout.addStretch()

        # Звезды рейтинга
        stars = "★" * self.rating + "☆" * (5 - self.rating)
        rating_label = QLabel(stars)
        rating_label.setStyleSheet("""
            color: #FFD700;
            font-weight: 600;
            font-size: 16px;
            letter-spacing: 1px;
        """)
        header_layout.addWidget(rating_label)

        layout.addLayout(header_layout)

        # Комментарий
        if self.comment:
            comment_label = QLabel(self.comment)
            comment_label.setWordWrap(True)
            comment_label.setStyleSheet("""
                color: #DDDDDD;
                margin-top: 8px;
                font-size: 14px;
                line-height: 1.5;
                font-family: 'Open Sans', sans-serif;
            """)
            comment_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
            layout.addWidget(comment_label)

        self.setStyleSheet("""
            QFrame#ReviewWidget {
                background-color: #1C1E22;
                border: 1px solid #2A2C32;
                border-radius: 8px;
            }
        """)


class MovieDetailView(QWidget):
    """Детальная страница фильма в стиле приложения"""
    go_back = pyqtSignal()
    show_seat_selection = pyqtSignal(int, str, str)

    def __init__(self, movie_id, user_id, parent=None):
        super().__init__(parent)
        self.movie_id = movie_id
        self.user_id = user_id
        self.setup_ui()
        self.load_movie_data()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Header
        self.create_header(main_layout)

        # Scroll Area для контента
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setObjectName("ContentArea")

        # Контейнер контента
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(30, 20, 30, 30)
        content_layout.setSpacing(30)

        # Верхний блок: постер + информация
        self.create_movie_info_section(content_layout)

        # Секция с актерами и режиссерами (ДОБАВЛЯЕМ ЭТО)
        self.create_people_section(content_layout)

        # Вкладки
        self.create_tabs_section(content_layout)

        scroll.setWidget(content_widget)
        main_layout.addWidget(scroll)

    def create_header(self, parent_layout):
        """Шапка в стиле приложения"""
        header = QWidget()
        header.setObjectName("HeaderBar")
        header.setFixedHeight(60)

        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(20, 10, 20, 10)

        # Кнопка назад
        back_btn = QPushButton("⬅ Назад к фильмам")
        back_btn.setObjectName("HeaderButton")
        back_btn.clicked.connect(self.go_back.emit)
        header_layout.addWidget(back_btn)

        header_layout.addStretch()

        parent_layout.addWidget(header)

    def create_movie_info_section(self, parent_layout):
        """Секция с информацией о фильме"""
        info_container = QHBoxLayout()
        info_container.setSpacing(30)

        self.poster_label = QLabel()
        self.poster_label.setFixedSize(250, 370)
        self.poster_label.setStyleSheet("""
            QLabel {
                background-color: #0F1115;
                border-radius: 8px;
                border: 2px solid #2A2C32;
            }
        """)

        info_container.addWidget(self.poster_label)

        # Информация о фильме
        info_widget = QWidget()
        info_layout = QVBoxLayout(info_widget)
        info_layout.setContentsMargins(0, 0, 0, 0)
        info_layout.setSpacing(15)

        # Заголовок и кнопка избранного в одной строке
        title_layout = QHBoxLayout()

        # Название
        self.title_label = QLabel()
        self.title_label.setObjectName("TitleLabel")
        self.title_label.setWordWrap(True)
        title_layout.addWidget(self.title_label)

        title_layout.addStretch()

        # Кнопка избранного (только для авторизованных пользователей)
        if self.user_id:
            self.favorite_btn = QPushButton()
            self.favorite_btn.setFixedSize(150, 40)
            self.favorite_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            self.favorite_btn.setStyleSheet("""
                QPushButton {
                    background-color: #2A2C32;
                    color: #FFFFFF;
                    border: 2px solid #00A8E8;
                    border-radius: 8px;
                    font-weight: 600;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background-color: #00A8E8;
                    color: #FFFFFF;
                }
            """)
            self.favorite_btn.clicked.connect(self.toggle_favorite)
            title_layout.addWidget(self.favorite_btn)

        info_layout.addLayout(title_layout)

        # Жанры
        self.genres_label = QLabel()
        self.genres_label.setWordWrap(True)
        self.genres_label.setStyleSheet("""
            color: #AAAAAA;
            font-size: 14px;
            font-family: 'Roboto', sans-serif;
        """)
        info_layout.addWidget(self.genres_label)

        # Рейтинг и цена
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(30)

        # Рейтинг
        rating_box = QVBoxLayout()
        rating_box.setSpacing(5)

        rating_title = QLabel("Рейтинг")
        rating_title.setStyleSheet("""
            color: #7A7A7A;
            font-size: 12px;
            font-family: 'Roboto', sans-serif;
        """)
        rating_box.addWidget(rating_title)

        self.rating_label = QLabel()
        self.rating_label.setStyleSheet("""
            color: #FFD700;
            font-weight: 700;
            font-size: 28px;
            font-family: 'Oswald', sans-serif;
        """)
        rating_box.addWidget(self.rating_label)

        stats_layout.addLayout(rating_box)

        # Цена
        price_box = QVBoxLayout()
        price_box.setSpacing(5)

        price_title = QLabel("Цена от")
        price_title.setStyleSheet("""
            color: #7A7A7A;
            font-size: 12px;
            font-family: 'Roboto', sans-serif;
        """)
        price_box.addWidget(price_title)

        self.price_label = QLabel()
        self.price_label.setStyleSheet("""
            color: #00A8E8;
            font-weight: 700;
            font-size: 28px;
            font-family: 'Oswald', sans-serif;
        """)
        price_box.addWidget(self.price_label)

        stats_layout.addLayout(price_box)
        stats_layout.addStretch()

        info_layout.addLayout(stats_layout)

        # Описание
        desc_label = QLabel("📖 Описание")
        desc_label.setObjectName("SectionLabel")
        info_layout.addWidget(desc_label)

        self.description_label = QLabel()
        self.description_label.setWordWrap(True)
        self.description_label.setStyleSheet("""
            color: #CCCCCC;
            line-height: 1.6;
            font-size: 14px;
            font-family: 'Open Sans', sans-serif;
        """)
        self.description_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        info_layout.addWidget(self.description_label)

        info_layout.addStretch()

        info_container.addWidget(info_widget, stretch=1)
        parent_layout.addLayout(info_container)

    def create_people_section(self, parent_layout):
        """Создать секцию с актерами и режиссерами - только если они есть"""
        # Сначала создаем временный контейнер
        self.people_section_container = QVBoxLayout()
        self.people_section_container.setSpacing(30)

        # Добавляем в основной layout, но секции будут добавлены позже
        parent_layout.addLayout(self.people_section_container)

    def create_directors_section(self):
        """Создать секцию режиссёров"""
        layout = QVBoxLayout()
        layout.setSpacing(15)

        # Заголовок
        title = QLabel("🎬 Режиссёры")
        title.setObjectName("SectionLabel")
        layout.addWidget(title)

        # Контейнер для карточек режиссёров - ГОРИЗОНТАЛЬНО
        self.directors_container = QHBoxLayout()
        self.directors_container.setSpacing(20)
        self.directors_container.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout.addLayout(self.directors_container)

        return layout

    def create_actors_section(self):
        """Создать секцию актеров"""
        layout = QVBoxLayout()
        layout.setSpacing(15)

        # Заголовок
        title = QLabel("🎭 В ролях")
        title.setObjectName("SectionLabel")
        layout.addWidget(title)

        # Контейнер для карточек актеров - ГОРИЗОНТАЛЬНО С ПРОКРУТКОЙ
        scroll = QScrollArea()
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setFixedHeight(280)  # Увеличили высоту для больших карточек
        scroll.setStyleSheet("""
            QScrollArea {
                background-color: transparent;
                border: none;
            }
            QScrollBar:horizontal {
                background: #1C1E22;
                height: 12px;
                margin: 0px;
                border-radius: 6px;
            }
            QScrollBar::handle:horizontal {
                background: #00A8E8;
                border-radius: 6px;
                min-width: 20px;
            }
            QScrollBar::handle:horizontal:hover {
                background: #03B7F5;
            }
        """)

        scroll_widget = QWidget()
        self.actors_container = QHBoxLayout(scroll_widget)
        self.actors_container.setSpacing(20)
        self.actors_container.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.actors_container.setContentsMargins(5, 5, 5, 5)

        scroll.setWidget(scroll_widget)
        scroll.setWidgetResizable(True)

        layout.addWidget(scroll)

        return layout

    def create_tabs_section(self, parent_layout):
        """Секция с вкладками"""
        self.tabs = QTabWidget()
        self.tabs.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        # Вкладка сеансов
        self.create_sessions_tab()

        # Вкладка отзывов
        self.create_reviews_tab()

        parent_layout.addWidget(self.tabs)

    def create_sessions_tab(self):
        """Вкладка с сеансами"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(15, 20, 15, 15)
        layout.setSpacing(20)

        # Заголовок
        header = QLabel("🎫 Расписание сеансов")
        header.setObjectName("SectionLabel")
        layout.addWidget(header)

        # Контейнер для сеансов
        self.sessions_container = QWidget()
        self.sessions_layout = QGridLayout(self.sessions_container)
        self.sessions_layout.setSpacing(20)
        self.sessions_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)

        layout.addWidget(self.sessions_container)
        layout.addStretch()

        self.tabs.addTab(tab, "Сеансы")

    def create_reviews_tab(self):
        """Вкладка с отзывами"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(15, 20, 15, 15)
        layout.setSpacing(25)

        # Форма добавления отзыва
        self.create_review_form(layout)

        # Заголовок отзывов
        header = QLabel("💬 Отзывы зрителей")
        header.setObjectName("SectionLabel")
        layout.addWidget(header)

        self.reviews_container = QWidget()
        self.reviews_container.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.reviews_layout = QVBoxLayout(self.reviews_container)
        self.reviews_layout.setSpacing(15)
        self.reviews_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        layout.addWidget(self.reviews_container)
        layout.addStretch()

        self.tabs.addTab(tab, "Отзывы")

    def create_review_form(self, parent_layout):
        """Форма добавления отзыва"""
        form = QFrame()
        form.setObjectName("FormContainer")

        form_layout = QVBoxLayout(form)
        form_layout.setSpacing(15)

        # Заголовок
        title = QLabel("✍️ Оставьте свой отзыв")
        title.setStyleSheet("""
            color: #FFFFFF;
            font-weight: 600;
            font-size: 16px;
            font-family: 'Montserrat', sans-serif;
            margin-bottom: 5px;
        """)
        form_layout.addWidget(title)

        # Выбор рейтинга
        rating_layout = QHBoxLayout()
        rating_layout.setSpacing(12)

        rating_label = QLabel("Ваша оценка:")
        rating_label.setStyleSheet("""
            color: #CCCCCC;
            font-size: 14px;
            font-family: 'Roboto', sans-serif;
        """)
        rating_layout.addWidget(rating_label)

        self.rating_combo = QComboBox()
        self.rating_combo.addItems([
            "5 ⭐⭐⭐⭐⭐",
            "4 ⭐⭐⭐⭐",
            "3 ⭐⭐⭐",
            "2 ⭐⭐",
            "1 ⭐"
        ])
        self.rating_combo.setFixedWidth(180)
        rating_layout.addWidget(self.rating_combo)
        rating_layout.addStretch()

        form_layout.addLayout(rating_layout)

        # Поле комментария
        self.comment_input = QTextEdit()
        self.comment_input.setPlaceholderText("Напишите ваше мнение о фильме...")
        self.comment_input.setMaximumHeight(100)
        form_layout.addWidget(self.comment_input)

        # Кнопка отправки
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        self.submit_review_btn = QPushButton("📤 Отправить отзыв")
        self.submit_review_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.submit_review_btn.clicked.connect(self.submit_review)
        btn_layout.addWidget(self.submit_review_btn)

        form_layout.addLayout(btn_layout)

        parent_layout.addWidget(form)

    def load_movie_data(self):
        """Загрузить данные фильма"""
        movie_data = MovieModel.get_movie_by_id(self.movie_id)
        if not movie_data:
            QMessageBox.critical(self, "Ошибка", "Фильм не найден")
            self.go_back.emit()
            return

        if movie_data[3]:
            pixmap = QPixmap()
            pixmap.loadFromData(bytes(movie_data[3]))
            if not pixmap.isNull():
                scaled_pixmap = pixmap.scaled(
                    250, 370,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
                self.poster_label.setPixmap(scaled_pixmap)
            else:
                self.set_placeholder_poster()
        else:
            self.set_placeholder_poster()

        # Информация
        self.title_label.setText(movie_data[1])
        self.description_label.setText(movie_data[2])
        self.rating_label.setText(f"⭐ {movie_data[5]:.1f}")
        self.price_label.setText(f"{int(movie_data[4])} ₽")

        # Жанры
        genres = MovieModel.get_movie_genres(self.movie_id)
        genre_names = [genre[1] for genre in genres]
        if genre_names:
            self.genres_label.setText("🎭 " + " • ".join(genre_names))
        else:
            self.genres_label.setText("🎭 Жанр не указан")

        # Обновляем кнопку избранного
        self.update_favorite_button()

        self.load_sessions()
        self.load_reviews()
        self.load_directors()
        self.load_actors()

    def set_placeholder_poster(self):
        """Заглушка для постера"""
        self.poster_label.setText("🎬\n\nПостер\nотсутствует")
        self.poster_label.setStyleSheet("""
            QLabel {
                background-color: #0F1115;
                color: #666666;
                font-size: 16px;
                font-weight: 600;
                border-radius: 8px;
                border: 2px dashed #2A2C32;
            }
        """)

    def load_sessions(self):
        """Загрузить сеансы"""
        sessions = SessionModel.get_sessions_by_movie(self.movie_id)

        # Очистка
        while self.sessions_layout.count():
            item = self.sessions_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if not sessions:
            no_sessions = QLabel("🎭 Сеансы временно отсутствуют")
            no_sessions.setAlignment(Qt.AlignmentFlag.AlignCenter)
            no_sessions.setStyleSheet("""
                color: #666666;
                font-size: 16px;
                padding: 60px;
                font-family: 'Roboto', sans-serif;
            """)
            self.sessions_layout.addWidget(no_sessions, 0, 0)
            return

        # Сетка 2 колонки
        row, col = 0, 0
        for session_data in sessions:
            card = SessionCard(session_data)
            card.book_clicked.connect(self.on_session_selected)
            self.sessions_layout.addWidget(card, row, col)
            col += 1
            if col >= 2:
                col = 0
                row += 1

    def load_reviews(self):
        """Загрузить отзывы"""
        reviews = ReviewModel.get_movie_reviews(self.movie_id)

        # Очистка
        while self.reviews_layout.count():
            item = self.reviews_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if not reviews:
            no_reviews = QLabel("💬 Пока нет отзывов. Будьте первым!")
            no_reviews.setAlignment(Qt.AlignmentFlag.AlignCenter)
            no_reviews.setStyleSheet("""
                color: #666666;
                font-size: 16px;
                padding: 60px;
                font-family: 'Roboto', sans-serif;
            """)
            self.reviews_layout.addWidget(no_reviews)
            return

        for review_data in reviews:
            review_widget = ReviewWidget(review_data)
            self.reviews_layout.addWidget(review_widget)

    def load_directors(self):
        """Загрузить режиссёров фильма"""
        try:
            directors = MovieModel.get_movie_directors(self.movie_id)

            # Если режиссёров нет, не создаем секцию
            if not directors:
                return

            # Создаем секцию только если есть режиссёры
            directors_section = QVBoxLayout()
            directors_section.setSpacing(15)

            # Заголовок
            title = QLabel("🎬 Режиссёры")
            title.setObjectName("SectionLabel")
            title.setStyleSheet("""
                color: #FFFFFF;
                font-size: 18px;
                font-weight: 600;
                margin-bottom: 10px;
            """)
            directors_section.addWidget(title)

            # Контейнер для карточек режиссёров
            directors_container = QHBoxLayout()
            directors_container.setSpacing(20)
            directors_container.setAlignment(Qt.AlignmentFlag.AlignLeft)

            directors = directors[:5]

            for director_data in directors:
                director_card = PersonCard(director_data, is_director=True)
                directors_container.addWidget(director_card)

            directors_section.addLayout(directors_container)

            # Добавляем секцию в общий контейнер
            self.people_section_container.addLayout(directors_section)

        except Exception as e:
            print(f"Ошибка при загрузке режиссёров: {e}")

    def load_actors(self):
        """Загрузить актеров фильма"""
        try:
            actors = MovieModel.get_movie_actors(self.movie_id)

            # Если актеров нет, не создаем секцию
            if not actors:
                return

            # Создаем секцию только если есть актеры
            actors_section = QVBoxLayout()
            actors_section.setSpacing(15)

            # Заголовок
            title = QLabel("🎭 В ролях")
            title.setObjectName("SectionLabel")
            title.setStyleSheet("""
                color: #FFFFFF;
                font-size: 18px;
                font-weight: 600;
                margin-bottom: 10px;
            """)
            actors_section.addWidget(title)

            # Прокручиваемая область для актеров
            scroll = QScrollArea()
            scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
            scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
            scroll.setFixedHeight(300)  # Увеличили для новых карточек
            scroll.setStyleSheet("""
                QScrollArea {
                    background-color: transparent;
                    border: none;
                }
                QScrollBar:horizontal {
                    background: #1C1E22;
                    height: 12px;
                    margin: 0px;
                    border-radius: 6px;
                }
                QScrollBar::handle:horizontal {
                    background: #00A8E8;
                    border-radius: 6px;
                    min-width: 20px;
                }
                QScrollBar::handle:horizontal:hover {
                    background: #03B7F5;
                }
            """)

            scroll_widget = QWidget()
            actors_container = QHBoxLayout(scroll_widget)
            actors_container.setSpacing(20)
            actors_container.setAlignment(Qt.AlignmentFlag.AlignLeft)
            actors_container.setContentsMargins(5, 5, 5, 5)

            # Ограничиваем до 8 актеров (можно больше, т.к. есть прокрутка)
            actors = actors[:8]

            for actor_data in actors:
                actor_card = PersonCard(actor_data, is_director=False)
                actors_container.addWidget(actor_card)

            scroll.setWidget(scroll_widget)
            scroll.setWidgetResizable(True)

            actors_section.addWidget(scroll)

            # Добавляем секцию в общий контейнер
            self.people_section_container.addLayout(actors_section)

        except Exception as e:
            print(f"Ошибка при загрузке актеров: {e}")

    def on_session_selected(self, session_id, movie_title, session_time):
        """Выбор сеанса - открываем выбор мест"""
        from PyQt6.QtWidgets import QDialog

        dialog = QDialog(self)
        dialog.setWindowTitle(f"Выбор мест - {movie_title}")
        dialog.setMinimumSize(900, 700)
        dialog.setStyleSheet("background-color: #0F1115;")

        layout = QVBoxLayout(dialog)

        # Создаем виджет выбора мест
        seat_selection = SeatSelectionView(session_id, self.user_id)
        seat_selection.booking_complete.connect(lambda ticket_ids: self.on_booking_complete(ticket_ids, dialog))
        layout.addWidget(seat_selection)

        dialog.exec()

    def submit_review(self):
        """Отправить отзыв"""
        rating = 5 - self.rating_combo.currentIndex()
        comment = self.comment_input.toPlainText().strip()

        if not comment:
            QMessageBox.warning(self, "Ошибка", "Введите текст отзыва")
            return

        existing_review = ReviewModel.get_user_review(self.user_id, self.movie_id)
        if existing_review:
            QMessageBox.information(
                self,
                "Информация",
                "Вы уже оставляли отзыв для этого фильма"
            )
            return

        try:
            review_id = ReviewModel.add_review(
                self.user_id,
                self.movie_id,
                rating,
                comment
            )

            if review_id:
                ReviewModel.update_movie_rating(self.movie_id)

                QMessageBox.information(
                    self,
                    "Успех",
                    "Ваш отзыв успешно добавлен!"
                )

                self.comment_input.clear()
                self.rating_combo.setCurrentIndex(0)
                self.load_reviews()

                # Обновляем рейтинг
                movie_data = MovieModel.get_movie_by_id(self.movie_id)
                if movie_data:
                    self.rating_label.setText(f"⭐ {movie_data[5]:.1f}")
            else:
                QMessageBox.critical(self, "Ошибка", "Не удалось добавить отзыв")

        except Exception as e:
            QMessageBox.critical(
                self,
                "Ошибка",
                f"Ошибка при добавлении отзыва: {str(e)}"
            )

    def on_booking_complete(self, ticket_ids, dialog):
        """Обработчик успешного бронирования"""
        if ticket_ids:
            dialog.accept()
            QMessageBox.information(
                self,
                "Успех!",
                f"Билеты успешно забронированы!\nНомера билетов: {', '.join(map(str, ticket_ids))}"
            )

    def update_favorite_button(self):
        """Обновить вид кнопки избранного"""
        if not self.user_id:
            return

        from Models.WatchlistModel import WatchlistModel
        is_favorite = WatchlistModel.is_in_watchlist(self.user_id, self.movie_id)

        if is_favorite:
            self.favorite_btn.setText("❤️ В избранном")
            self.favorite_btn.setStyleSheet("""
                QPushButton {
                    background-color: #00A8E8;
                    color: #FFFFFF;
                    border: 2px solid #00A8E8;
                    border-radius: 8px;
                    font-weight: 600;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background-color: #E63946;
                    border-color: #E63946;
                }
            """)
            self.favorite_btn.setToolTip("Удалить из избранного")
        else:
            self.favorite_btn.setText("🤍 В избранное")
            self.favorite_btn.setStyleSheet("""
                QPushButton {
                    background-color: #2A2C32;
                    color: #FFFFFF;
                    border: 2px solid #00A8E8;
                    border-radius: 8px;
                    font-weight: 600;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background-color: #00A8E8;
                    color: #FFFFFF;
                }
            """)
            self.favorite_btn.setToolTip("Добавить в избранное")

    def toggle_favorite(self):
        try:
            from Models.WatchlistModel import WatchlistModel

            is_currently_favorite = WatchlistModel.is_in_watchlist(self.user_id, self.movie_id)

            if is_currently_favorite:
                # Удаляем из избранного
                success = WatchlistModel.remove_from_watchlist(self.user_id, self.movie_id)
                if success:
                    QMessageBox.information(self, "Успех", "Фильм удален из избранного")
            else:
                # Добавляем в избранное
                success = WatchlistModel.add_to_watchlist(self.user_id, self.movie_id)
                if success:
                    QMessageBox.information(self, "Успех", "Фильм добавлен в избранное")

            # Обновляем кнопку
            self.update_favorite_button()

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось изменить избранное: {str(e)}")