# Views/AdminPanelView.py - упрощенная версия
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QGridLayout, QLabel
from PyQt6.QtCore import Qt

class AdminPanelView(QWidget):
    def __init__(self, go_back=None, go_to_users=None, go_to_actors=None,
                 go_to_directors=None, go_to_movies=None, go_to_genres=None,
                 go_to_halls=None, go_to_sessions=None, go_to_tickets = None, go_to_logs=None, go_to_reviews=None, go_to_reports=None):
        super().__init__()

        self.go_back = go_back
        self.go_to_users = go_to_users
        self.go_to_actors = go_to_actors
        self.go_to_directors = go_to_directors
        self.go_to_movies = go_to_movies
        self.go_to_genres = go_to_genres
        self.go_to_halls = go_to_halls
        self.go_to_sessions = go_to_sessions
        self.go_to_tickets = go_to_tickets
        self.go_to_logs = go_to_logs
        self.go_to_reviews = go_to_reviews
        self.go_to_reports = go_to_reports

        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(25)

        # Заголовок
        title = QLabel("🛠 Панель администратора")
        title.setObjectName("TitleLabel")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Сетка кнопок 3 колонки для лучшего размещения
        grid_layout = QGridLayout()
        grid_layout.setSpacing(15)
        grid_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Первый ряд
        self.btn_users = QPushButton("👥 Пользователи")
        self.btn_users.setFixedSize(200, 45)
        self.btn_users.clicked.connect(self.open_users_view)
        grid_layout.addWidget(self.btn_users, 0, 0)

        self.btn_movies = QPushButton("🎥 Фильмы")
        self.btn_movies.setFixedSize(200, 45)
        self.btn_movies.clicked.connect(self.open_movies_view)
        grid_layout.addWidget(self.btn_movies, 0, 1)

        self.btn_sessions = QPushButton("🎫 Сеансы")
        self.btn_sessions.setFixedSize(200, 45)
        self.btn_sessions.clicked.connect(self.open_sessions_view)
        grid_layout.addWidget(self.btn_sessions, 0, 2)

        # Второй ряд
        self.btn_halls = QPushButton("🎭 Залы")
        self.btn_halls.setFixedSize(200, 45)
        self.btn_halls.clicked.connect(self.open_halls_view)
        grid_layout.addWidget(self.btn_halls, 1, 0)

        self.btn_tickets = QPushButton("🎫 Билеты")
        self.btn_tickets.setFixedSize(200, 45)
        self.btn_tickets.clicked.connect(self.open_tickets_view)
        grid_layout.addWidget(self.btn_tickets, 1, 1)

        self.btn_reviews = QPushButton("💬 Отзывы")  # Новая кнопка
        self.btn_reviews.setFixedSize(200, 45)
        self.btn_reviews.clicked.connect(self.open_reviews_view)
        grid_layout.addWidget(self.btn_reviews, 1, 2)

        # Третий ряд
        self.btn_actors = QPushButton("🎭 Актёры")
        self.btn_actors.setFixedSize(200, 45)
        self.btn_actors.clicked.connect(self.open_actors_view)
        grid_layout.addWidget(self.btn_actors, 2, 0)

        self.btn_directors = QPushButton("🎬 Режиссёры")
        self.btn_directors.setFixedSize(200, 45)
        self.btn_directors.clicked.connect(self.open_directors_view)
        grid_layout.addWidget(self.btn_directors, 2, 1)

        self.btn_genres = QPushButton("🎭 Жанры")
        self.btn_genres.setFixedSize(200, 45)
        self.btn_genres.clicked.connect(self.open_genres_view)
        grid_layout.addWidget(self.btn_genres, 2, 2)

        # Четвертый ряд
        self.btn_logs = QPushButton("📊 Журнал событий")
        self.btn_logs.setFixedSize(200, 45)
        self.btn_logs.clicked.connect(self.open_logs_view)
        grid_layout.addWidget(self.btn_logs, 3, 1)

        self.btn_reports = QPushButton("📊 Отчеты")
        self.btn_reports.setFixedSize(200, 45)
        self.btn_reports.clicked.connect(self.open_reports_view)
        grid_layout.addWidget(self.btn_reports, 3, 2)  # Ряд 3, колонка 2

        layout.addLayout(grid_layout)

        layout.addLayout(grid_layout)

        # Кнопка назад по центру
        self.btn_back = QPushButton("⬅ Назад в главное меню")
        self.btn_back.setFixedSize(300, 45)
        self.btn_back.setObjectName("BackButton")
        if self.go_back:
            self.btn_back.clicked.connect(self.go_back)
        layout.addWidget(self.btn_back, alignment=Qt.AlignmentFlag.AlignCenter)

    def open_users_view(self):
        if self.go_to_users:
            self.go_to_users()

    def open_actors_view(self):
        if self.go_to_actors:
            self.go_to_actors()

    def open_directors_view(self):
        if self.go_to_directors:
            self.go_to_directors()

    def open_movies_view(self):
        if self.go_to_movies:
            self.go_to_movies()

    def open_genres_view(self):
        if self.go_to_genres:
            self.go_to_genres()

    def open_halls_view(self):
        if self.go_to_halls:
            self.go_to_halls()

    def open_sessions_view(self):
        if self.go_to_sessions:
            self.go_to_sessions()

    def open_tickets_view(self):
        if self.go_to_tickets:
            self.go_to_tickets()

    def open_logs_view(self):
        if self.go_to_logs:
            self.go_to_logs()

    def open_reviews_view(self):
        if self.go_to_reviews:
            self.go_to_reviews()

    def open_reports_view(self):
        if self.go_to_reports:
            self.go_to_reports()