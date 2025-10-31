from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QCursor
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QStackedWidget, QMessageBox

from Views.ProfileView import ProfileView
from Views.AdminPanelView import AdminPanelView
from Views.AdminPanelUsersView import AdminPanelUsersView
from Models.UserModel import UserModel


class MainView(QWidget):
    def __init__(self, user_id, go_login=None):
        super().__init__()
        self.user_id = user_id
        self.go_login = go_login

        # Получаем АКТУАЛЬНЫЕ данные пользователя из БД
        self.user_data = UserModel.get_user_data(user_id)

        if not self.user_data:
            QMessageBox.critical(self, "Ошибка", "Пользователь не найден в базе данных")
            if go_login:
                go_login()
            return

        # Header
        self.header = QWidget()
        self.header.setObjectName("HeaderBar")

        h_header = QHBoxLayout(self.header)
        h_header.setContentsMargins(20, 10, 20, 10)
        h_header.setSpacing(15)

        self.logo_label = QLabel()
        pix = QPixmap("images/headerLogo.png")
        pix = pix.scaledToHeight(38, Qt.TransformationMode.SmoothTransformation)
        self.logo_label.setPixmap(pix)
        self.logo_label.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.logo_label.setObjectName("HeaderLogo")
        self.logo_label.mousePressEvent = self.show_main_page

        self.btn_profile = QPushButton("👨‍💼\nПрофиль")
        self.btn_profile.setObjectName("HeaderButton")
        self.btn_profile.clicked.connect(self.show_profile_page)

        self.adminBtn = QPushButton("🛠\nАдмин-панель")
        self.adminBtn.setObjectName("HeaderButton")
        self.adminBtn.setVisible(self.user_data['role_id'] == 2)
        self.adminBtn.clicked.connect(self.show_admin_page)

        h_header.addWidget(self.logo_label)
        h_header.addStretch()
        h_header.addWidget(self.btn_profile)
        h_header.addWidget(self.adminBtn)

        # Content area
        self.stack = QStackedWidget()
        self.stack.setObjectName("ContentArea")

        # ВСЕ страницы создаются по требованию (lazy loading)
        self.page_main = None
        self.page_profile = None
        self.page_admin_panel = None
        self.page_admin_panel_users = None
        self.page_admin_panel_actors = None
        self.page_admin_panel_directors = None
        self.page_admin_panel_movies = None
        self.page_admin_panel_genres = None

        # Footer
        self.footer = QWidget()
        self.footer.setObjectName("FooterBar")

        h_footer = QHBoxLayout(self.footer)
        h_footer.setContentsMargins(20, 8, 20, 8)
        h_footer.setSpacing(10)

        self.footer_text = QLabel("© 2025 CinemaVaib — Все права защищены, v0.3.0")
        self.footer_text.setObjectName("FooterText")
        h_footer.addStretch()
        h_footer.addWidget(self.footer_text)
        h_footer.addStretch()

        # Основной layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        main_layout.addWidget(self.header)
        main_layout.addWidget(self.stack, stretch=1)
        main_layout.addWidget(self.footer)

        # Показываем главную страницу сразу после инициализации
        self.show_main_page()

    def _create_main_page(self):
        from Views.Components.MovieGridView import MovieGridView

        # Получаем СВЕЖИЕ данные пользователя из БД
        fresh_data = UserModel.get_user_data(self.user_id)

        if not fresh_data:
            # Если пользователь удален из БД
            page = QWidget()
            layout = QVBoxLayout(page)
            layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            error_label = QLabel("⚠️ Ошибка загрузки данных пользователя")
            error_label.setObjectName("ErrorLabel")
            layout.addWidget(error_label)
            return page

        page = QWidget()
        main_layout = QVBoxLayout(page)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Сетка фильмов
        self.movie_grid = MovieGridView()
        self.movie_grid.movie_clicked.connect(self.show_movie_detail)
        main_layout.addWidget(self.movie_grid)

        return page

    def show_main_page(self, event=None):
        if self.page_main is not None:
            self.stack.removeWidget(self.page_main)
            self.page_main.deleteLater()

        # Обновляем кэшированные данные пользователя
        self.user_data = UserModel.get_user_data(self.user_id)

        if not self.user_data:
            QMessageBox.critical(self, "Ошибка", "Пользователь был удален из базы данных")
            if self.go_login:
                self.go_login()
            return

        # Обновляем видимость кнопки админки (роль могла измениться)
        self.adminBtn.setVisible(self.user_data['role_id'] == 2)

        # Создаем страницу
        self.page_main = self._create_main_page()
        self.stack.addWidget(self.page_main)
        self.stack.setCurrentWidget(self.page_main)

    def show_profile_page(self):
        """Показать профиль с АКТУАЛЬНЫМИ данными из БД"""
        # Обновляем данные перед переходом
        self.user_data = UserModel.get_user_data(self.user_id)

        if not self.user_data:
            QMessageBox.critical(self, "Ошибка", "Пользователь был удален из базы данных")
            if self.go_login:
                self.go_login()
            return

        # ВСЕГДА пересоздаем страницу профиля для свежих данных
        if self.page_profile is not None:
            self.stack.removeWidget(self.page_profile)
            self.page_profile.deleteLater()

        self.page_profile = ProfileView(
            user_id=self.user_id,
            go_back=self.show_main_page,
            go_login=self.go_login
        )
        self.stack.addWidget(self.page_profile)
        self.stack.setCurrentWidget(self.page_profile)

    def show_admin_page(self):
        """Показать админ-панель"""
        self.user_data = UserModel.get_user_data(self.user_id)

        if not self.user_data or self.user_data['role_id'] != 2:
            QMessageBox.warning(self, "Доступ запрещён", "У вас нет прав администратора.")
            return

        if self.page_admin_panel is not None:
            self.stack.removeWidget(self.page_admin_panel)
            self.page_admin_panel.deleteLater()

        self.page_admin_panel = AdminPanelView(
            go_back=self.show_main_page,
            go_to_users=self.show_panel_users,
            go_to_actors=self.show_panel_actors,
            go_to_directors=self.show_panel_directors,
            go_to_movies=self.show_panel_movies,
            go_to_genres = self.show_panel_genres
        )
        self.stack.addWidget(self.page_admin_panel)
        self.stack.setCurrentWidget(self.page_admin_panel)

    def show_panel_users(self):
        """Показать управление пользователями"""
        # ВСЕГДА пересоздаем для актуальных данных из БД
        if self.page_admin_panel_users is not None:
            self.stack.removeWidget(self.page_admin_panel_users)
            self.page_admin_panel_users.deleteLater()

        self.page_admin_panel_users = AdminPanelUsersView(
            go_back=self.show_admin_page
        )
        self.stack.addWidget(self.page_admin_panel_users)
        self.stack.setCurrentWidget(self.page_admin_panel_users)

    def show_movie_detail(self, movie_id):
        QMessageBox.information(
            self,
            "Фильм",
            f"Вы выбрали фильм с ID: {movie_id}\n\nДетальная страница в разработке"
        )

    def show_panel_actors(self):
        """Показать управление актёрами"""
        from Views.AdminPanelActorsView import AdminPanelActorsView

        if self.page_admin_panel_actors is not None:
            self.stack.removeWidget(self.page_admin_panel_actors)
            self.page_admin_panel_actors.deleteLater()

        self.page_admin_panel_actors = AdminPanelActorsView(go_back=self.show_admin_page)
        self.stack.addWidget(self.page_admin_panel_actors)
        self.stack.setCurrentWidget(self.page_admin_panel_actors)

    def show_panel_directors(self):
        """Показать управление режиссёрами"""
        from Views.AdminPanelDirectorsView import AdminPanelDirectorsView

        if self.page_admin_panel_directors is not None:
            self.stack.removeWidget(self.page_admin_panel_directors)
            self.page_admin_panel_directors.deleteLater()

        self.page_admin_panel_directors = AdminPanelDirectorsView(go_back=self.show_admin_page)
        self.stack.addWidget(self.page_admin_panel_directors)
        self.stack.setCurrentWidget(self.page_admin_panel_directors)

    def show_panel_movies(self):
        """Показать управление фильмами"""
        from Views.AdminPanelMoviesView import AdminPanelMoviesView

        if self.page_admin_panel_movies is not None:
            self.stack.removeWidget(self.page_admin_panel_movies)
            self.page_admin_panel_movies.deleteLater()

        self.page_admin_panel_movies = AdminPanelMoviesView(go_back=self.show_admin_page)
        self.stack.addWidget(self.page_admin_panel_movies)
        self.stack.setCurrentWidget(self.page_admin_panel_movies)

    def show_panel_genres(self):
        """Показать управление жанрами"""
        from Views.AdminPanelGenresView import AdminPanelGenresView

        if self.page_admin_panel_genres is not None:
            self.stack.removeWidget(self.page_admin_panel_genres)
            self.page_admin_panel_genres.deleteLater()

        self.page_admin_panel_genres = AdminPanelGenresView(go_back=self.show_admin_page)
        self.stack.addWidget(self.page_admin_panel_genres)
        self.stack.setCurrentWidget(self.page_admin_panel_genres)