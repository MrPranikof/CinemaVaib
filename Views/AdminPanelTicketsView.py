from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableView, QSizePolicy, QMessageBox, QSpacerItem,
    QGroupBox, QDateEdit, QHeaderView, QTabWidget, QComboBox,
    QScrollArea
)
from PyQt6.QtCore import Qt, QDate
from core.database import datagrid_model
from Models.TicketModel import TicketModel


class AdminPanelTicketsView(QWidget):
    def __init__(self, user_id, go_back=None):
        super().__init__()

        self.user_id = user_id
        self.go_back = go_back

        self.stats_label = None
        self.revenue_label = None
        self.model = None

        self.setup_ui()
        self.load_tickets()

    def setup_ui(self):
        """Настройка интерфейса"""
        # Главный layout для всего виджета
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        scroll = QScrollArea()
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        # Контейнер для содержимого
        content_widget = QWidget()
        layout = QVBoxLayout(content_widget)
        layout.setContentsMargins(20,20,20,20)
        layout.setSpacing(25)

        # Заголовок
        header = QHBoxLayout()
        title = QLabel("🎫 Управление билетами")
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

        # Вкладки
        self.tabs = QTabWidget()
        self.tabs.setMinimumHeight(500)

        # Вкладка всех билетов
        self.create_all_tickets_tab()
        # Вкладка статистики
        self.create_stats_tab()

        layout.addWidget(self.tabs, stretch=1)

        scroll.setWidget(content_widget)
        main_layout.addWidget(scroll)

    def create_stats_section(self, parent_layout):
        """Создать секцию статистики"""
        stats_group = QGroupBox("📊 Статистика продаж")
        stats_layout = QHBoxLayout(stats_group)

        self.stats_label = QLabel()
        stats_layout.addWidget(self.stats_label)

        stats_layout.addStretch()

        btn_refresh = QPushButton("🔄 Обновить")
        btn_refresh.clicked.connect(self.update_stats)
        stats_layout.addWidget(btn_refresh)

        parent_layout.addWidget(stats_group)
        self.update_stats()

    def create_all_tickets_tab(self):
        """Вкладка со всеми билетами"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(20)

        # Фильтры
        self.create_filters_section(layout)

        # Таблица билетов
        self.tickets_view = QTableView()
        self.tickets_view.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self.tickets_view.setSelectionMode(QTableView.SelectionMode.SingleSelection)
        self.tickets_view.setAlternatingRowColors(True)
        self.tickets_view.setSortingEnabled(True)
        self.tickets_view.setMinimumHeight(400)
        layout.addWidget(self.tickets_view, stretch=1)

        # Кнопки управления
        btns = QHBoxLayout()
        btns.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Policy.Expanding))

        self.btn_view_details = QPushButton("👁️ Детали")
        self.btn_view_details.clicked.connect(self.view_ticket_details)
        btns.addWidget(self.btn_view_details)

        self.btn_cancel_ticket = QPushButton("❌ Отменить билет")
        self.btn_cancel_ticket.setObjectName("LogoutButton")
        self.btn_cancel_ticket.clicked.connect(self.cancel_ticket)
        btns.addWidget(self.btn_cancel_ticket)

        self.btn_refresh = QPushButton("🔄 Обновить")
        self.btn_refresh.clicked.connect(self.load_tickets)
        btns.addWidget(self.btn_refresh)

        btns.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Policy.Expanding))
        layout.addLayout(btns)

        self.tabs.addTab(tab, "🎫 Все билеты")

    def create_filters_section(self, parent_layout):
        """Создать секцию фильтров"""
        filter_group = QGroupBox("Фильтры")
        filter_layout = QHBoxLayout(filter_group)

        # Фильтр по периоду
        filter_layout.addWidget(QLabel("Период:"))
        self.date_from = QDateEdit()
        self.date_from.setDate(QDate.currentDate().addDays(-30))
        self.date_from.setCalendarPopup(True)
        self.date_from.setDisplayFormat("dd.MM.yyyy")
        self.date_from.setFixedWidth(120)
        filter_layout.addWidget(self.date_from)

        filter_layout.addWidget(QLabel("–"))

        self.date_to = QDateEdit()
        self.date_to.setDate(QDate.currentDate())
        self.date_to.setCalendarPopup(True)
        self.date_to.setDisplayFormat("dd.MM.yyyy")
        self.date_to.setFixedWidth(120)
        filter_layout.addWidget(self.date_to)

        # Фильтр по статусу
        filter_layout.addWidget(QLabel("Статус:"))
        self.status_filter_combo = QComboBox()
        self.status_filter_combo.addItem("Все", "all")
        self.status_filter_combo.addItem("Активные", "active")
        self.status_filter_combo.addItem("Использованные", "used")
        filter_layout.addWidget(self.status_filter_combo)

        # Кнопка применения фильтра
        btn_apply = QPushButton("Применить")
        btn_apply.clicked.connect(self.apply_filters)
        filter_layout.addWidget(btn_apply)

        # Кнопка сброса фильтров
        btn_reset = QPushButton("Сбросить")
        btn_reset.clicked.connect(self.reset_filters)
        filter_layout.addWidget(btn_reset)

        filter_layout.addStretch()
        parent_layout.addWidget(filter_group)

    def create_stats_tab(self):
        """Вкладка со статистикой продаж"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(20)

        # Заголовок
        header = QLabel("📈 Ежедневная выручка (последние 30 дней)")
        header.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(header)

        # Таблица выручки
        self.revenue_label = QLabel()
        self.revenue_label.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.revenue_label.setWordWrap(True)
        layout.addWidget(self.revenue_label, stretch=1)

        # Загружаем данные о выручке
        self.load_revenue_data()

        self.tabs.addTab(tab, "📊 Аналитика")

    def load_revenue_data(self):
        """Загрузить данные о выручке"""
        try:
            daily_revenue = TicketModel.get_daily_revenue(30)
            if daily_revenue:
                revenue_text = """
                <table style='width: 100%; border-collapse: collapse;'>
                    <tr style='background-color: #2A2C32;'>
                        <th style='padding: 10px; text-align: left; border: 1px solid #3A3C42;'>Дата</th>
                        <th style='padding: 10px; text-align: center; border: 1px solid #3A3C42;'>Билетов</th>
                        <th style='padding: 10px; text-align: right; border: 1px solid #3A3C42;'>Выручка</th>
                    </tr>
                """

                for i, (date, tickets, revenue) in enumerate(daily_revenue[:30]):
                    bg_color = "#1C1E22" if i % 2 == 0 else "#23252A"
                    revenue_val = int(float(revenue)) if revenue else 0
                    revenue_text += f"""
                    <tr style='background-color: {bg_color};'>
                        <td style='padding: 8px; border: 1px solid #3A3C42;'>{date}</td>
                        <td style='padding: 8px; text-align: center; border: 1px solid #3A3C42;'>{tickets}</td>
                        <td style='padding: 8px; text-align: right; border: 1px solid #3A3C42; color: #55C78C; font-weight: bold;'>{revenue_val:,} руб.</td>
                    </tr>
                    """

                revenue_text += "</table>"
                self.revenue_label.setText(revenue_text)
            else:
                self.revenue_label.setText(
                    "<p style='color: #999; text-align: center; padding: 40px;'>Нет данных о выручке</p>")
        except Exception as e:
            print(f"Ошибка загрузки ежедневной выручки: {e}")
            self.revenue_label.setText(f"<p style='color: #FF6B6B;'>Ошибка загрузки данных: {str(e)}</p>")

    def load_tickets(self):
        """Загрузить все билеты"""
        try:
            sql = """
                SELECT 
                    t.ticket_id as "ID",
                    m.title as "Фильм", 
                    u.login as "Пользователь",
                    h.hall_name as "Зал",
                    TO_CHAR(s.session_time, 'DD.MM.YYYY HH24:MI') as "Время сеанса", 
                    st.row_number as "Ряд", 
                    st.seat_number as "Место",
                    t.final_price as "Цена",
                    TO_CHAR(t.purchase_date, 'DD.MM.YYYY HH24:MI') as "Дата покупки",
                    CASE 
                        WHEN s.session_time > NOW() THEN 'Активный'
                        ELSE 'Использован'
                    END as "Статус"
                FROM ticket t
                JOIN session s ON t.session_id = s.session_id
                JOIN movies m ON s.movie_id = m.movie_id
                JOIN users u ON t.user_id = u.user_id
                JOIN hall h ON s.hall_id = h.hall_id
                JOIN seat st ON t.seat_id = st.seat_id
                ORDER BY t.purchase_date DESC
            """

            self.model = datagrid_model(sql)
            self.tickets_view.setModel(self.model)

            # Настройка заголовков
            header = self.tickets_view.horizontalHeader()
            header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
            header.setStretchLastSection(True)

            self.update_stats()

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить билеты: {str(e)}")

    def update_stats(self):
        """Обновить статистику"""
        try:
            stats = TicketModel.get_tickets_stats()
            if stats:
                total_tickets, total_revenue, avg_price, unique_customers, unique_movies = stats
                total_tickets = total_tickets or 0
                total_revenue = total_revenue or 0
                avg_price = avg_price or 0
                unique_customers = unique_customers or 0
                unique_movies = unique_movies or 0
            else:
                total_tickets = total_revenue = avg_price = unique_customers = unique_movies = 0

            stats_text = (
                f"🎫 Билетов продано: <b>{total_tickets}</b> | "
                f"💰 Общая выручка: <b>{int(float(total_revenue)):,} руб.</b> | "
                f"📈 Средний чек: <b>{int(float(avg_price)):,} руб.</b> | "
                f"👥 Уникальных клиентов: <b>{unique_customers}</b>"
            )

            self.stats_label.setText(stats_text)
        except Exception as e:
            print(f"Ошибка при обновлении статистики: {e}")
            self.stats_label.setText("<span style='color: #FF6B6B;'>Ошибка загрузки статистики</span>")

    def get_selected_ticket(self):
        """Получить выбранный билет"""
        selection = self.tickets_view.selectionModel().selectedRows()
        if not selection:
            return None

        row = selection[0].row()
        model = self.tickets_view.model()

        ticket_id = model.data(model.index(row, 0))
        movie_title = model.data(model.index(row, 1))
        user_login = model.data(model.index(row, 2))
        hall_name = model.data(model.index(row, 3))
        session_time = model.data(model.index(row, 4))

        return {
            'ticket_id': ticket_id,
            'movie_title': movie_title,
            'user_login': user_login,
            'hall_name': hall_name,
            'session_time': session_time
        }

    def view_ticket_details(self):
        """Просмотреть детали билета"""
        ticket = self.get_selected_ticket()
        if not ticket:
            QMessageBox.warning(self, "Внимание", "Выберите билет из таблицы")
            return

        QMessageBox.information(
            self,
            f"Детали билета #{ticket['ticket_id']}",
            f"<b>🎫 Номер билета:</b> {ticket['ticket_id']}<br>"
            f"<b>🎬 Фильм:</b> {ticket['movie_title']}<br>"
            f"<b>👤 Пользователь:</b> {ticket['user_login']}<br>"
            f"<b>🏛️ Зал:</b> {ticket['hall_name']}<br>"
            f"<b>🕐 Время сеанса:</b> {ticket['session_time']}"
        )

    def cancel_ticket(self):
        """Отменить выбранный билет"""
        ticket = self.get_selected_ticket()
        if not ticket:
            QMessageBox.warning(self, "Внимание", "Выберите билет из таблицы")
            return

        confirm = QMessageBox.question(
            self,
            "Подтверждение отмены",
            f"Отменить билет №<b>{ticket['ticket_id']}</b>?<br><br>"
            f"Фильм: {ticket['movie_title']}<br>"
            f"Пользователь: {ticket['user_login']}<br><br>"
            f"⚠️ <b>Это действие невозможно отменить!</b>",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if confirm == QMessageBox.StandardButton.Yes:
            try:
                success = TicketModel.cancel_ticket_admin(ticket['ticket_id'], self.user_id)
                if success:
                    QMessageBox.information(self, "Успех", "Билет успешно отменен")
                    self.load_tickets()
                else:
                    QMessageBox.critical(self, "Ошибка", "Не удалось отменить билет")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Ошибка при отмене билета: {str(e)}")

    def apply_filters(self):
        """Применить фильтры"""
        try:
            date_from = self.date_from.date().toString("yyyy-MM-dd")
            date_to = self.date_to.date().toString("yyyy-MM-dd")
            status = self.status_filter_combo.currentData()

            # Базовый SQL запрос
            sql = f"""
                SELECT 
                    t.ticket_id as "ID",
                    m.title as "Фильм", 
                    u.login as "Пользователь",
                    h.hall_name as "Зал",
                    TO_CHAR(s.session_time, 'DD.MM.YYYY HH24:MI') as "Время сеанса", 
                    st.row_number as "Ряд", 
                    st.seat_number as "Место",
                    t.final_price as "Цена",
                    TO_CHAR(t.purchase_date, 'DD.MM.YYYY HH24:MI') as "Дата покупки",
                    CASE 
                        WHEN s.session_time > NOW() THEN 'Активный'
                        ELSE 'Использован'
                    END as "Статус"
                FROM ticket t
                JOIN session s ON t.session_id = s.session_id
                JOIN movies m ON s.movie_id = m.movie_id
                JOIN users u ON t.user_id = u.user_id
                JOIN hall h ON s.hall_id = h.hall_id
                JOIN seat st ON t.seat_id = st.seat_id
                WHERE DATE(t.purchase_date) BETWEEN '{date_from}' AND '{date_to}'
            """

            # Добавляем фильтр по статусу
            if status == "active":
                sql += " AND s.session_time > NOW()"
            elif status == "used":
                sql += " AND s.session_time <= NOW()"

            sql += " ORDER BY t.purchase_date DESC"

            self.model = datagrid_model(sql)
            self.tickets_view.setModel(self.model)

            header = self.tickets_view.horizontalHeader()
            header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
            header.setStretchLastSection(True)

            # Показываем количество найденных билетов
            row_count = self.model.rowCount()
            QMessageBox.information(
                self,
                "Фильтр применен",
                f"Найдено билетов: {row_count}"
            )

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось применить фильтр: {str(e)}")

    def reset_filters(self):
        """Сбросить фильтры"""
        self.date_from.setDate(QDate.currentDate().addDays(-30))
        self.date_to.setDate(QDate.currentDate())
        self.status_filter_combo.setCurrentIndex(0)
        self.load_tickets()