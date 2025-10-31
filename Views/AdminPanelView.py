from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton
from PyQt6.QtCore import Qt


class AdminPanelView(QWidget):
    def __init__(self, go_back=None, go_to_users=None, go_to_actors=None,
                 go_to_directors=None, go_to_movies=None, go_to_genres=None):
        super().__init__()

        self.go_back = go_back
        self.go_to_users = go_to_users
        self.go_to_actors = go_to_actors
        self.go_to_directors = go_to_directors
        self.go_to_movies = go_to_movies
        self.go_to_genres = go_to_genres

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(25)

        # Кнопки управления
        self.btn_users = QPushButton("👥 Пользователи")
        self.btn_users.setFixedSize(220, 45)
        self.btn_users.clicked.connect(self.open_users_view)

        self.btn_movies = QPushButton("🎥 Фильмы")
        self.btn_movies.setFixedSize(220, 45)
        self.btn_movies.clicked.connect(self.open_movies_view)

        self.btn_actors = QPushButton("🎭 Актёры")
        self.btn_actors.setFixedSize(220, 45)
        self.btn_actors.clicked.connect(self.open_actors_view)

        self.btn_directors = QPushButton("🎬 Режиссёры")
        self.btn_directors.setFixedSize(220, 45)
        self.btn_directors.clicked.connect(self.open_directors_view)

        self.btn_genres = QPushButton("🎭 Жанры")
        self.btn_genres.setFixedSize(220, 45)
        self.btn_genres.clicked.connect(self.open_genres_view)

        self.btn_back = QPushButton("⬅ Назад")
        self.btn_back.setFixedSize(220, 45)
        self.btn_back.setObjectName("BackButton")
        if self.go_back:
            self.btn_back.clicked.connect(self.go_back)

        layout.addWidget(self.btn_users, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.btn_movies, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.btn_actors, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.btn_directors, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.btn_genres, alignment=Qt.AlignmentFlag.AlignCenter)
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