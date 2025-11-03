from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableView, QSizePolicy, QMessageBox, QSpacerItem,
    QGroupBox, QComboBox, QDateEdit, QFormLayout
)
from PyQt6.QtCore import Qt, QDate
from core.database import datagrid_model
from Models.LogModel import LogModel


class AdminPanelLogsView(QWidget):
    def __init__(self, user_id, go_back=None):
        super().__init__()
        self.user_id = user_id
        self.go_back = go_back

        self.setup_ui()
        self.load_logs()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        # Заголовок
        header = QHBoxLayout()
        title = QLabel("📊 Журнал событий")
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

        # Фильтры - ИСПРАВЛЕНИЕ: передаем layout в метод
        filter_group = self.create_filters_section()
        layout.addWidget(filter_group)  # Добавляем группу фильтров в layout

        # Таблица логов
        self.logs_view = QTableView()
        self.logs_view.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self.logs_view.setAlternatingRowColors(True)
        self.logs_view.setSortingEnabled(True)
        layout.addWidget(self.logs_view, stretch=1)

        # Кнопки управления
        btns = QHBoxLayout()
        btns.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Policy.Expanding))

        self.btn_refresh = QPushButton("🔄 Обновить")
        self.btn_refresh.clicked.connect(self.load_logs)
        btns.addWidget(self.btn_refresh)

        self.btn_cleanup = QPushButton("🗑️ Очистить старые логи")
        self.btn_cleanup.setObjectName("LogoutButton")
        self.btn_cleanup.clicked.connect(self.cleanup_old_logs)
        btns.addWidget(self.btn_cleanup)

        btns.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Policy.Expanding))
        layout.addLayout(btns)

    def create_filters_section(self):
        """Создать секцию фильтров и вернуть готовый виджет"""
        filter_group = QGroupBox("Фильтры")
        layout = QHBoxLayout(filter_group)

        # Фильтр по типу действия
        layout.addWidget(QLabel("Тип действия:"))
        self.action_filter = QComboBox()
        self.action_filter.addItem("Все действия", "all")
        self.action_filter.addItem("Вход/выход", "USER_")
        self.action_filter.addItem("Покупки билетов", "TICKET_")
        self.action_filter.addItem("Действия с фильмами", "MOVIE_")
        self.action_filter.addItem("Отзывы", "REVIEW_")
        self.action_filter.addItem("Ошибки", "ERROR_")
        self.action_filter.currentIndexChanged.connect(self.apply_filters)
        layout.addWidget(self.action_filter)

        # Фильтр по количеству записей
        layout.addWidget(QLabel("Показать:"))
        self.limit_filter = QComboBox()
        self.limit_filter.addItem("50 записей", 50)
        self.limit_filter.addItem("100 записей", 100)
        self.limit_filter.addItem("200 записей", 200)
        self.limit_filter.addItem("500 записей", 500)
        self.limit_filter.setCurrentIndex(1)
        self.limit_filter.currentIndexChanged.connect(self.apply_filters)
        layout.addWidget(self.limit_filter)

        layout.addStretch()

        return filter_group  # Возвращаем готовый виджет

    def load_logs(self):
        """Загрузить логи"""
        try:
            limit = self.limit_filter.currentData()

            # Создаем модель для таблицы (без параметра для LIMIT)
            sql = f"""
                SELECT 
                    al.log_id as "ID",
                    COALESCE(u.login, 'Система') as "Пользователь",
                    al.actor_role as "Роль",
                    al.action_type as "Тип действия",
                    al.entity_id as "ID сущности",
                    al.description as "Описание",
                    TO_CHAR(al.timestamp, 'DD.MM.YYYY HH24:MI:SS') as "Время"
                FROM activity_log al
                LEFT JOIN users u ON al.user_id = u.user_id
                ORDER BY al.timestamp DESC
                LIMIT {limit}
            """

            self.model = datagrid_model(sql)
            self.logs_view.setModel(self.model)

        except Exception as e:
            print(f"Ошибка при загрузке логов: {e}")
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить логи: {str(e)}")

    def apply_filters(self):
        """Применить фильтры"""
        try:
            limit = self.limit_filter.currentData()
            action_filter = self.action_filter.currentData()

            # Базовый SQL
            sql = f"""
                SELECT 
                    al.log_id as "ID",
                    COALESCE(u.login, 'Система') as "Пользователь",
                    al.actor_role as "Роль",
                    al.action_type as "Тип действия",
                    al.entity_id as "ID сущности",
                    al.description as "Описание",
                    TO_CHAR(al.timestamp, 'DD.MM.YYYY HH24:MI:SS') as "Время"
                FROM activity_log al
                LEFT JOIN users u ON al.user_id = u.user_id
                WHERE 1=1
            """

            # Применяем фильтр по типу действия
            if action_filter != "all":
                sql += f" AND al.action_type LIKE '{action_filter}%'"

            sql += f" ORDER BY al.timestamp DESC LIMIT {limit}"

            self.model = datagrid_model(sql)
            self.logs_view.setModel(self.model)

        except Exception as e:
            print(f"Ошибка при применении фильтров: {e}")
            QMessageBox.critical(self, "Ошибка", f"Ошибка при применении фильтров: {str(e)}")

    def cleanup_old_logs(self):
        """Очистить старые логи"""
        confirm = QMessageBox.question(
            self,
            "Очистка логов",
            "Удалить логи старше 90 дней?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if confirm == QMessageBox.StandardButton.Yes:
            try:
                LogModel.cleanup_old_logs(90)
                QMessageBox.information(self, "Успех", "Старые логи очищены")
                self.load_logs()
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось очистить логи: {str(e)}")