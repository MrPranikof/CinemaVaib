from PyQt6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QPushButton, QHBoxLayout,
    QTableView, QSizePolicy, QMessageBox, QSpacerItem, QDialog,
    QLineEdit, QFormLayout, QDialogButtonBox, QComboBox, QDateTimeEdit,
    QGroupBox
)
from PyQt6.QtCore import Qt, QDateTime
from core.database import datagrid_model
from Models.SessionModel import SessionModel
from Models.MovieModel import MovieModel
from Models.HallModel import HallModel


class AdminPanelSessionsView(QWidget):
    def __init__(self, go_back=None):
        super().__init__()
        self.go_back = go_back
        self.setup_ui()
        self.refresh_sessions_table()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 30, 40, 30)
        layout.setSpacing(25)

        # Заголовок
        header = QHBoxLayout()
        title = QLabel("🎬 Управление сеансами")
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

        # Фильтры
        self.create_filters_section(layout)

        # Таблица сеансов
        self.sessions_view = QTableView()
        self.sessions_view.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self.sessions_view.setSelectionMode(QTableView.SelectionMode.SingleSelection)
        self.sessions_view.setAlternatingRowColors(True)
        self.sessions_view.setSortingEnabled(True)
        layout.addWidget(self.sessions_view, stretch=1)

        # Кнопки управления
        btns = QHBoxLayout()
        btns.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Policy.Expanding))

        self.btn_add_session = QPushButton("➕ Добавить сеанс")
        self.btn_add_session.clicked.connect(self.add_session)
        btns.addWidget(self.btn_add_session)

        self.btn_edit_session = QPushButton("✏️ Редактировать")
        self.btn_edit_session.clicked.connect(self.edit_session)
        btns.addWidget(self.btn_edit_session)

        self.btn_delete_session = QPushButton("🗑 Удалить")
        self.btn_delete_session.setObjectName("LogoutButton")
        self.btn_delete_session.clicked.connect(self.delete_session)
        btns.addWidget(self.btn_delete_session)

        self.btn_refresh = QPushButton("🔄 Обновить")
        self.btn_refresh.clicked.connect(self.refresh_sessions_table)
        btns.addWidget(self.btn_refresh)

        btns.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Policy.Expanding))
        layout.addLayout(btns)

    def create_filters_section(self, parent_layout):
        """Создать секцию фильтров"""
        filter_group = QGroupBox("Фильтры")
        filter_layout = QHBoxLayout(filter_group)

        # Фильтр по фильму
        filter_layout.addWidget(QLabel("Фильм:"))
        self.movie_filter_combo = QComboBox()
        self.movie_filter_combo.addItem("Все фильмы", 0)

        movies = MovieModel.get_all_movies()
        for movie in movies:
            self.movie_filter_combo.addItem(movie[1], movie[0])  # title, movie_id

        self.movie_filter_combo.currentIndexChanged.connect(self.apply_filters)
        filter_layout.addWidget(self.movie_filter_combo)

        # Фильтр по залу
        filter_layout.addWidget(QLabel("Зал:"))
        self.hall_filter_combo = QComboBox()
        self.hall_filter_combo.addItem("Все залы", 0)

        halls = HallModel.get_all_halls()
        for hall in halls:
            self.hall_filter_combo.addItem(f"{hall[1]} - {hall[2]}", hall[0])  # number - name

        self.hall_filter_combo.currentIndexChanged.connect(self.apply_filters)
        filter_layout.addWidget(self.hall_filter_combo)

        filter_layout.addStretch()
        parent_layout.addWidget(filter_group)

    def refresh_sessions_table(self):
        """Обновить таблицу сеансов"""
        self.sessions_model = datagrid_model(
            "SELECT s.session_id, m.title, h.hall_name, "
            "s.session_time, m.base_price + h.hall_extra_price as price, "
            "s.created_at "
            "FROM session s "
            "JOIN movies m ON s.movie_id = m.movie_id "
            "JOIN hall h ON s.hall_id = h.hall_id "
            "ORDER BY s.session_time DESC"
        )
        self.sessions_view.setModel(self.sessions_model)

    def apply_filters(self):
        """Применить фильтры"""
        movie_id = self.movie_filter_combo.currentData()
        hall_id = self.hall_filter_combo.currentData()

        where_conditions = []
        params = []

        if movie_id and movie_id != 0:
            where_conditions.append("s.movie_id = %s")
            params.append(movie_id)

        if hall_id and hall_id != 0:
            where_conditions.append("s.hall_id = %s")
            params.append(hall_id)

        sql = f"""
            SELECT s.session_id, m.title, h.hall_name, 
                   s.session_time, m.base_price + h.hall_extra_price as price,
                   s.created_at 
            FROM session s
            JOIN movies m ON s.movie_id = m.movie_id
            JOIN hall h ON s.hall_id = h.hall_id
        """

        if where_conditions:
            sql += " WHERE " + " AND ".join(where_conditions)

        sql += " ORDER BY s.session_time DESC"

        self.sessions_model = datagrid_model(sql, params)
        self.sessions_view.setModel(self.sessions_model)

    def get_selected_session(self):
        """Получить выбранный сеанс"""
        selection = self.sessions_view.selectionModel().selectedRows()
        if not selection:
            return None

        row = selection[0].row()
        return {
            'session_id': self.sessions_model.item(row, 0).text(),
            'movie_title': self.sessions_model.item(row, 1).text(),
            'hall_name': self.sessions_model.item(row, 2).text()
        }

    def add_session(self):
        """Добавить сеанс"""
        dialog = SessionDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            try:
                session_id = SessionModel.create_session(
                    dialog.movie_combo.currentData(),
                    dialog.hall_combo.currentData(),
                    dialog.datetime_input.dateTime().toPyDateTime()
                )
                if session_id:
                    QMessageBox.information(self, "Успех", "Сеанс успешно добавлен")
                    self.refresh_sessions_table()
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось добавить сеанс: {str(e)}")

    def edit_session(self):
        """Редактировать сеанс"""
        session = self.get_selected_session()
        if not session:
            QMessageBox.warning(self, "Внимание", "Выберите сеанс из таблицы")
            return

        session_data = SessionModel.get_session_by_id(session['session_id'])
        if not session_data:
            QMessageBox.warning(self, "Ошибка", "Сеанс не найден")
            return

        dialog = SessionDialog(self, session_data)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            try:
                SessionModel.update_session(
                    session['session_id'],
                    dialog.movie_combo.currentData(),
                    dialog.hall_combo.currentData(),
                    dialog.datetime_input.dateTime().toPyDateTime()
                )
                QMessageBox.information(self, "Успех", "Сеанс успешно обновлен")
                self.refresh_sessions_table()
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось обновить сеанс: {str(e)}")

    def delete_session(self):
        """Удалить сеанс"""
        session = self.get_selected_session()
        if not session:
            QMessageBox.warning(self, "Внимание", "Выберите сеанс из таблицы")
            return

        confirm = QMessageBox.question(
            self, "Подтверждение",
            f"Удалить сеанс '<b>{session['movie_title']}</b>'?<br>"
            f"Зал: {session['hall_name']}<br><br>"
            f"⚠️ <b>Будут удалены все связанные билеты!</b>",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if confirm == QMessageBox.StandardButton.Yes:
            try:
                SessionModel.delete_session(session['session_id'])
                QMessageBox.information(self, "Успех", "Сеанс удален")
                self.refresh_sessions_table()
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось удалить сеанс: {str(e)}")


class SessionDialog(QDialog):
    def __init__(self, parent=None, session_data=None):
        super().__init__(parent)
        self.setWindowTitle("Добавление сеанса" if not session_data else "Редактирование сеанса")
        self.setFixedWidth(500)

        layout = QFormLayout(self)
        layout.setSpacing(15)

        # Выбор фильма
        self.movie_combo = QComboBox()
        movies = MovieModel.get_all_movies()
        for movie in movies:
            self.movie_combo.addItem(movie[1], movie[0])  # title, movie_id
        layout.addRow("Фильм:", self.movie_combo)

        # Выбор зала
        self.hall_combo = QComboBox()
        halls = HallModel.get_all_halls()
        for hall in halls:
            self.hall_combo.addItem(f"{hall[1]} - {hall[2]} ({hall[3]})", hall[0])
        layout.addRow("Зал:", self.hall_combo)

        # Дата и время
        self.datetime_input = QDateTimeEdit()
        self.datetime_input.setDateTime(QDateTime.currentDateTime().addDays(1))
        self.datetime_input.setCalendarPopup(True)
        self.datetime_input.setDisplayFormat("dd.MM.yyyy HH:mm")
        layout.addRow("Дата и время:", self.datetime_input)

        # Заполняем данные если редактирование
        if session_data:
            # Устанавливаем фильм
            for i in range(self.movie_combo.count()):
                if self.movie_combo.itemData(i) == session_data[1]:  # movie_id
                    self.movie_combo.setCurrentIndex(i)
                    break

            # Устанавливаем зал
            for i in range(self.hall_combo.count()):
                if self.hall_combo.itemData(i) == session_data[5]:  # hall_id
                    self.hall_combo.setCurrentIndex(i)
                    break

            # Устанавливаем дату и время
            session_dt = QDateTime.fromString(
                session_data[8].strftime("%Y-%m-%d %H:%M:%S"),
                "yyyy-MM-dd HH:mm:ss"
            )
            self.datetime_input.setDateTime(session_dt)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)