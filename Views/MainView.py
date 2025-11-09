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

        self.user_data = UserModel.get_user_data(user_id)

        if not self.user_data:
            QMessageBox.critical(self, "Ошибка", "Пользователь не найден в базе данных")
            if go_login:
                go_login()
            return

        # Header
        self.header = QWidget(self)
        self.header.setObjectName("HeaderBar")

        h_header = QHBoxLayout(self.header)
        h_header.setContentsMargins(20, 10, 20, 10)
        h_header.setSpacing(15)

        self.logo_label = QLabel(self.header)
        pix = QPixmap("images/headerLogo.png")
        pix = pix.scaledToHeight(38, Qt.TransformationMode.SmoothTransformation)
        self.logo_label.setPixmap(pix)
        self.logo_label.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.logo_label.setObjectName("HeaderLogo")
        self.logo_label.mousePressEvent = self.show_main_page

        self.btn_watchlist = QPushButton("❤️\nИзбранное", parent=self.header)
        self.btn_watchlist.setObjectName("HeaderButton")
        self.btn_watchlist.clicked.connect(self.show_watchlist_page)

        self.btn_tickets = QPushButton("🎟️\nМои билеты", parent=self.header)
        self.btn_tickets.setObjectName("HeaderButton")
        self.btn_tickets.clicked.connect(self.show_my_tickets)

        self.btn_profile = QPushButton("👨‍💼\nПрофиль", parent=self.header)
        self.btn_profile.setObjectName("HeaderButton")
        self.btn_profile.clicked.connect(self.show_profile_page)

        self.adminBtn = QPushButton("🛠\nАдмин-панель", parent=self.header)
        self.adminBtn.setObjectName("HeaderButton")
        self.adminBtn.setVisible(self.user_data['role_id'] == 2)
        self.adminBtn.clicked.connect(self.show_admin_page)

        h_header.addWidget(self.logo_label)
        h_header.addStretch()
        h_header.addWidget(self.btn_watchlist)
        h_header.addWidget(self.btn_tickets)
        h_header.addWidget(self.btn_profile)
        h_header.addWidget(self.adminBtn)

        # Content area
        self.stack = QStackedWidget(self)
        self.stack.setObjectName("ContentArea")

        self.page_main = None
        self.page_profile = None
        self.page_admin_panel = None
        self.page_admin_panel_users = None
        self.page_admin_panel_actors = None
        self.page_admin_panel_directors = None
        self.page_admin_panel_movies = None
        self.page_admin_panel_genres = None
        self.page_admin_panel_halls = None
        self.page_admin_panel_sessions = None
        self.page_movie_detail = None
        self.page_admin_panel_tickets = None
        self.page_admin_panel_logs = None

        # Footer
        self.footer = QWidget(self)
        self.footer.setObjectName("FooterBar")

        h_footer = QHBoxLayout(self.footer)
        h_footer.setContentsMargins(20, 8, 20, 8)
        h_footer.setSpacing(10)

        self.footer_text = QLabel("© 2025 CinemaVaib — Все права защищены, v1.2.0")
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

        self.show_main_page()

    def _create_main_page(self):
        from Views.Components.MovieGridView import MovieGridView

        # Получаем СВЕЖИЕ данные пользователя из БД
        fresh_data = UserModel.get_user_data(self.user_id)

        if not fresh_data:
            page = QWidget(self)
            layout = QVBoxLayout(page)
            layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            error_label = QLabel("⚠️ Ошибка загрузки данных пользователя")
            error_label.setObjectName("ErrorLabel")
            layout.addWidget(error_label)
            return page

        page = QWidget(self)
        main_layout = QVBoxLayout(page)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.movie_grid = MovieGridView()
        self.movie_grid.movie_clicked.connect(self.show_movie_detail)
        main_layout.addWidget(self.movie_grid)

        return page

    def show_main_page(self, event=None):
        try:
            if self.page_main is not None:
                self.stack.removeWidget(self.page_main)
                self.page_main.deleteLater()

            self.user_data = UserModel.get_user_data(self.user_id)

            if not self.user_data:
                QMessageBox.critical(self, "Ошибка", "Пользователь был удален из базы данных")
                if self.go_login:
                    self.go_login()
                return

            self.adminBtn.setVisible(self.user_data['role_id'] == 2)

            self.page_main = self._create_main_page()
            self.stack.addWidget(self.page_main)
            self.stack.setCurrentWidget(self.page_main)

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить главную страницу: {str(e)}")

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
            go_to_genres = self.show_panel_genres,
            go_to_halls = self.show_panel_halls,
            go_to_sessions = self.show_panel_sessions,
            go_to_tickets = self.show_panel_tickets,
            go_to_logs = self.show_panel_logs,
            go_to_reviews=self.show_panel_reviews,
            go_to_reports=self.show_panel_reports
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

    def show_movie_detail(self, movie_id):
        """Показать детальную страницу фильма"""
        if self.page_movie_detail is not None:
            self.stack.removeWidget(self.page_movie_detail)
            self.page_movie_detail.deleteLater()

        from Views.MovieDetailView import MovieDetailView
        self.page_movie_detail = MovieDetailView(movie_id, self.user_id)
        self.page_movie_detail.go_back.connect(self.show_main_page)
        self.page_movie_detail.show_seat_selection.connect(self.show_seat_selection)

        self.stack.addWidget(self.page_movie_detail)
        self.stack.setCurrentWidget(self.page_movie_detail)

    def show_seat_selection(self, session_id, movie_title, session_time):
        """Показать выбор мест (заглушка)"""
        QMessageBox.information(
            self,
            "Выбор мест",
            f"🎫 Бронирование билетов\n\n"
            f"Фильм: {movie_title}\n"
            f"Сеанс: {session_time}\n"
            f"ID сеанса: {session_id}\n\n"
            f"Функционал выбора мест будет реализован в следующем этапе"
        )

    def show_panel_halls(self):
        """Показать управление залами"""
        from Views.AdminPanelHallsView import AdminPanelHallsView

        if self.page_admin_panel_halls is not None:
            self.stack.removeWidget(self.page_admin_panel_halls)
            self.page_admin_panel_halls.deleteLater()

        self.page_admin_panel_halls = AdminPanelHallsView(go_back=self.show_admin_page)
        self.stack.addWidget(self.page_admin_panel_halls)
        self.stack.setCurrentWidget(self.page_admin_panel_halls)

    def show_panel_sessions(self):
        """Показать управление сеансами"""
        from Views.AdminPanelSessionsView import AdminPanelSessionsView

        if self.page_admin_panel_sessions is not None:
            self.stack.removeWidget(self.page_admin_panel_sessions)
            self.page_admin_panel_sessions.deleteLater()

        self.page_admin_panel_sessions = AdminPanelSessionsView(go_back=self.show_admin_page)
        self.stack.addWidget(self.page_admin_panel_sessions)
        self.stack.setCurrentWidget(self.page_admin_panel_sessions)

    def show_watchlist_page(self):
        """Показать страницу избранного"""
        # Обновляем данные перед переходом
        self.user_data = UserModel.get_user_data(self.user_id)

        if not self.user_data:
            QMessageBox.critical(self, "Ошибка", "Пользователь был удален из базы данных")
            if self.go_login:
                self.go_login()
            return

        # Пересоздаем страницу избранного для свежих данных
        if hasattr(self, 'page_watchlist') and self.page_watchlist is not None:
            try:
                self.stack.removeWidget(self.page_watchlist)
                self.page_watchlist.deleteLater()
            except:
                pass

        from Views.WatchlistView import WatchlistView
        self.page_watchlist = WatchlistView(
            user_id=self.user_id,
            go_back=self.show_main_page
        )
        self.page_watchlist.movie_clicked.connect(self.show_movie_detail)

        self.stack.addWidget(self.page_watchlist)
        self.stack.setCurrentWidget(self.page_watchlist)

    def show_my_tickets(self):
        """Показать мои билеты"""
        try:
            from Views.MyTicketsView import MyTicketsView

            if hasattr(self, 'page_my_tickets') and self.page_my_tickets is not None:
                try:
                    self.stack.removeWidget(self.page_my_tickets)
                    self.page_my_tickets.deleteLater()
                    self.page_my_tickets = None
                except Exception as e:
                    print(f"Ошибка при удалении старого виджета билетов: {e}")

            # Создаем новый виджет
            self.page_my_tickets = MyTicketsView(self.user_id, go_back=self.show_main_page)
            self.stack.addWidget(self.page_my_tickets)
            self.stack.setCurrentWidget(self.page_my_tickets)

        except Exception as e:
            print(f"Ошибка при создании виджета билетов: {e}")
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить билеты: {str(e)}")

    def show_panel_tickets(self):
        """Показать управление билетами"""
        try:
            if hasattr(self, 'page_admin_panel_tickets'):
                if self.page_admin_panel_tickets is not None:
                    try:
                        self.stack.removeWidget(self.page_admin_panel_tickets)
                        self.page_admin_panel_tickets.deleteLater()
                        self.page_admin_panel_tickets = None
                    except:
                        pass

            from Views.AdminPanelTicketsView import AdminPanelTicketsView

            self.page_admin_panel_tickets = AdminPanelTicketsView(
                user_id=self.user_id,
                go_back=self.show_admin_page
            )
            self.stack.addWidget(self.page_admin_panel_tickets)
            self.stack.setCurrentWidget(self.page_admin_panel_tickets)

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось открыть управление билетами: {str(e)}")

    def show_panel_logs(self):
        from Views.AdminPanelLogsView import AdminPanelLogsView

        if self.page_admin_panel_logs is not None:
            self.stack.removeWidget(self.page_admin_panel_logs)
            self.page_admin_panel_logs.deleteLater()

        self.page_admin_panel_logs = AdminPanelLogsView(
            user_id=self.user_id,
            go_back=self.show_admin_page
        )
        self.stack.addWidget(self.page_admin_panel_logs)
        self.stack.setCurrentWidget(self.page_admin_panel_logs)

    def show_panel_reviews(self):
        """Показать управление отзывами"""
        from Views.AdminPanelReviewsView import AdminPanelReviewsView

        if hasattr(self, 'page_admin_panel_reviews') and self.page_admin_panel_reviews is not None:
            self.stack.removeWidget(self.page_admin_panel_reviews)
            self.page_admin_panel_reviews.deleteLater()

        self.page_admin_panel_reviews = AdminPanelReviewsView(
            user_id=self.user_id,
            go_back=self.show_admin_page
        )
        self.stack.addWidget(self.page_admin_panel_reviews)
        self.stack.setCurrentWidget(self.page_admin_panel_reviews)

    def show_panel_reports(self):
        from Views.AdminPanelReportsView import AdminPanelReportsView

        if hasattr(self, 'page_admin_panel_reports') and self.page_admin_panel_reports is not None:
            self.stack.removeWidget(self.page_admin_panel_reports)
            self.page_admin_panel_reports.deleteLater()

        self.page_admin_panel_reports = AdminPanelReportsView(
            user_id=self.user_id,
            go_back=self.show_admin_page
        )
        self.stack.addWidget(self.page_admin_panel_reports)
        self.stack.setCurrentWidget(self.page_admin_panel_reports)