from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableView, QSizePolicy, QMessageBox, QSpacerItem,
    QGroupBox, QComboBox, QLineEdit, QTextEdit, QDialog,
    QDialogButtonBox, QFormLayout, QSpinBox
)
from PyQt6.QtCore import Qt
from core.database import datagrid_model
from Models.ReviewAdminModel import ReviewAdminModel
from Models.LogModel import LogModel


class AdminPanelReviewsView(QWidget):
    def __init__(self, user_id, go_back=None):
        super().__init__()
        self.user_id = user_id
        self.go_back = go_back

        self.setup_ui()
        self.load_reviews()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        # Заголовок
        header = QHBoxLayout()
        title = QLabel("💬 Управление отзывами")
        title.setObjectName("TitleLabel")
        header.addWidget(title)
        header.addStretch()

        self.btn_back = QPushButton("⬅ Назад")
        self.btn_back.setObjectName("BackButton")
        self.btn_back.setFixedWidth(150)
        if self.go_back:
            self.btn_back.clicked.connect(self.go_back)
        header.addWidget(self.btn_back)

        layout.addLayout(header)

        # Статистика
        self.create_stats_section(layout)

        # Поиск
        self.create_search_section(layout)

        # Таблица отзывов
        self.reviews_view = QTableView()
        self.reviews_view.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self.reviews_view.setSelectionMode(QTableView.SelectionMode.SingleSelection)
        self.reviews_view.setAlternatingRowColors(True)
        self.reviews_view.setSortingEnabled(True)
        layout.addWidget(self.reviews_view, stretch=1)

        # Кнопки управления
        btns = QHBoxLayout()
        btns.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Policy.Expanding))

        self.btn_view_details = QPushButton("👁️ Просмотреть")
        self.btn_view_details.clicked.connect(self.view_review_details)
        btns.addWidget(self.btn_view_details)

        self.btn_delete = QPushButton("🗑 Удалить")
        self.btn_delete.setObjectName("LogoutButton")
        self.btn_delete.clicked.connect(self.delete_review)
        btns.addWidget(self.btn_delete)

        self.btn_refresh = QPushButton("🔄 Обновить")
        self.btn_refresh.clicked.connect(self.load_reviews)
        btns.addWidget(self.btn_refresh)

        btns.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Policy.Expanding))
        layout.addLayout(btns)

    def create_stats_section(self, parent_layout):
        """Создать секцию статистики"""
        stats_group = QGroupBox("📊 Статистика отзывов")
        stats_layout = QHBoxLayout(stats_group)

        self.stats_label = QLabel()
        stats_layout.addWidget(self.stats_label)

        stats_layout.addStretch()
        parent_layout.addWidget(stats_group)
        self.update_stats()

    def create_search_section(self, parent_layout):
        """Создать секцию поиска"""
        search_group = QGroupBox("🔍 Поиск отзывов")
        search_layout = QHBoxLayout(search_group)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Поиск по комментарию или названию фильма...")
        self.search_input.textChanged.connect(self.on_search)
        search_layout.addWidget(self.search_input)

        search_layout.addStretch()
        parent_layout.addWidget(search_group)

    def load_reviews(self):
        """Загрузить отзывы"""
        try:
            sql = """
                SELECT 
                    r.review_id as "ID",
                    u.login as "Пользователь",
                    m.title as "Фильм",
                    r.rating as "Оценка",
                    LEFT(r.comment, 50) || CASE WHEN LENGTH(r.comment) > 50 THEN '...' ELSE '' END as "Комментарий",
                    TO_CHAR(r.created_at, 'DD.MM.YYYY HH24:MI') as "Дата"
                FROM review r
                JOIN users u ON r.user_id = u.user_id
                JOIN movies m ON r.movie_id = m.movie_id
                ORDER BY r.created_at DESC
                LIMIT 100
            """

            self.model = datagrid_model(sql)
            self.reviews_view.setModel(self.model)
            self.update_stats()

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить отзывы: {str(e)}")

    def update_stats(self):
        """Обновить статистику"""
        try:
            stats = ReviewAdminModel.get_reviews_stats()
            if stats:
                total_reviews, avg_rating, unique_users, unique_movies = stats
                stats_text = (
                    f"📊 Всего отзывов: <b>{total_reviews}</b> | "
                    f"⭐ Средняя оценка: <b>{avg_rating:.1f}</b> | "
                    f"👥 Уникальных пользователей: <b>{unique_users}</b> | "
                    f"🎬 Фильмов с отзывами: <b>{unique_movies}</b>"
                )
            else:
                stats_text = "📊 Нет данных для отображения"

            self.stats_label.setText(stats_text)
        except Exception as e:
            self.stats_label.setText("📊 Ошибка загрузки статистики")

    def on_search(self, text):
        """Обработка поиска"""
        try:
            search_text = text.strip()

            if len(search_text) >= 2:
                # Используем прямой SQL запрос для поиска
                sql = f"""
                    SELECT 
                        r.review_id as "ID",
                        u.login as "Пользователь",
                        m.title as "Фильм",
                        r.rating as "Оценка",
                        LEFT(r.comment, 50) || CASE WHEN LENGTH(r.comment) > 50 THEN '...' ELSE '' END as "Комментарий",
                        TO_CHAR(r.created_at, 'DD.MM.YYYY HH24:MI') as "Дата"
                    FROM review r
                    JOIN users u ON r.user_id = u.user_id
                    JOIN movies m ON r.movie_id = m.movie_id
                    WHERE r.comment ILIKE '%{search_text}%' OR m.title ILIKE '%{search_text}%'
                    ORDER BY r.created_at DESC
                    LIMIT 100
                """

                self.model = datagrid_model(sql)
                self.reviews_view.setModel(self.model)

            elif len(search_text) == 0:
                self.load_reviews()

        except Exception as e:
            print(f"Ошибка поиска: {e}")
            QMessageBox.critical(self, "Ошибка", f"Ошибка при поиске: {str(e)}")

    def get_selected_review(self):
        """Получить выбранный отзыв"""
        selection = self.reviews_view.selectionModel().selectedRows()
        if not selection:
            return None

        row = selection[0].row()
        model = self.reviews_view.model()

        review_id = model.data(model.index(row, 0))
        user_login = model.data(model.index(row, 1))
        movie_title = model.data(model.index(row, 2))
        rating = model.data(model.index(row, 3))
        comment = model.data(model.index(row, 4))

        return {
            'review_id': review_id,
            'user_login': user_login,
            'movie_title': movie_title,
            'rating': rating,
            'comment': comment
        }

    def view_review_details(self):
        """Просмотреть детали отзыва"""
        review = self.get_selected_review()
        if not review:
            QMessageBox.warning(self, "Внимание", "Выберите отзыв из таблицы")
            return

        dialog = ReviewDetailsDialog(self, review)
        dialog.exec()

    def delete_review(self):
        """Удалить отзыв"""
        review = self.get_selected_review()
        if not review:
            QMessageBox.warning(self, "Внимание", "Выберите отзыв из таблицы")
            return

        confirm = QMessageBox.question(
            self,
            "Подтверждение удаления",
            f"Удалить отзыв пользователя '<b>{review['user_login']}</b>'?\n\n"
            f"Фильм: {review['movie_title']}\n"
            f"Оценка: {review['rating']}⭐\n\n"
            f"⚠️ <b>Это действие необратимо!</b>",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if confirm == QMessageBox.StandardButton.Yes:
            try:
                # Получаем полную информацию об отзыве перед удалением
                full_review = ReviewAdminModel.get_review_by_id(review['review_id'])
                if full_review:
                    movie_id = full_review[3]  # movie_id

                    # Удаляем отзыв
                    ReviewAdminModel.delete_review(review['review_id'])

                    # Обновляем рейтинг фильма
                    ReviewAdminModel.update_review_rating(movie_id)

                    # Логируем действие
                    LogModel.log_admin_action(
                        self.user_id,
                        "REVIEW_DELETE",
                        "Review",
                        review['review_id'],
                        f"Удален отзыв пользователя {review['user_login']} для фильма '{review['movie_title']}'"
                    )

                    QMessageBox.information(self, "Успех", "Отзыв успешно удален")
                    self.load_reviews()
                else:
                    QMessageBox.critical(self, "Ошибка", "Отзыв не найден")

            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось удалить отзыв: {str(e)}")


class ReviewDetailsDialog(QDialog):
    """Диалог просмотра деталей отзыва"""

    def __init__(self, parent=None, review_data=None):
        super().__init__(parent)
        self.review_data = review_data
        self.setWindowTitle("Детали отзыва")
        self.setFixedWidth(600)
        self.setMinimumHeight(400)

        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        # Заголовок
        title = QLabel("📝 Детали отзыва")
        title.setObjectName("TitleLabel")
        layout.addWidget(title)

        # Информация об отзыве
        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        # Пользователь
        user_label = QLabel(review_data['user_login'])
        user_label.setStyleSheet("font-weight: 600; color: #00A8E8;")
        form.addRow("👤 Пользователь:", user_label)

        # Фильм
        movie_label = QLabel(review_data['movie_title'])
        movie_label.setStyleSheet("font-weight: 600;")
        form.addRow("🎬 Фильм:", movie_label)

        # Оценка
        rating_label = QLabel("★" * int(review_data['rating']) + "☆" * (5 - int(review_data['rating'])))
        rating_label.setStyleSheet("color: #FFD700; font-size: 16px; font-weight: 600;")
        form.addRow("⭐ Оценка:", rating_label)

        layout.addLayout(form)

        # Комментарий
        comment_label = QLabel("💬 Комментарий:")
        comment_label.setObjectName("SectionLabel")
        layout.addWidget(comment_label)

        comment_text = QTextEdit()
        comment_text.setPlainText(review_data['comment'])
        comment_text.setReadOnly(True)
        comment_text.setStyleSheet("""
            QTextEdit {
                background-color: #1C1E22;
                border: 1px solid #2A2C32;
                border-radius: 5px;
                padding: 10px;
                color: #EAEAEA;
            }
        """)
        layout.addWidget(comment_text, stretch=1)

        # Кнопки
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)