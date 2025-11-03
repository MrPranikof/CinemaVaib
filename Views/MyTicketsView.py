from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QFrame, QScrollArea, QMessageBox,
                             QTableWidget, QTableWidgetItem, QHeaderView)
from PyQt6.QtCore import Qt
from Models.TicketModel import TicketModel
from datetime import datetime


class MyTicketsView(QWidget):
    def __init__(self, user_id, go_back=None):
        super().__init__()
        self.user_id = user_id
        self.go_back = go_back
        self._is_loaded = False

        self.setup_ui()
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(100, self.load_tickets)

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        # Заголовок
        title = QLabel("🎟️ Мои билеты")
        title.setObjectName("TitleLabel")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Сообщение о загрузке
        self.loading_label = QLabel("⏳ Загрузка билетов...")
        self.loading_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.loading_label.setStyleSheet("color: #AAAAAA; font-size: 16px;")
        layout.addWidget(self.loading_label)

        # Таблица билетов
        self.tickets_table = QTableWidget()
        self.tickets_table.setColumnCount(7)
        self.tickets_table.setHorizontalHeaderLabels([
            "Фильм", "Зал", "Время", "Место", "Стоимость", "Статус", "Действия"
        ])

        # Настройка таблицы
        header = self.tickets_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)  # Фильм - растягивается
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)  # Зал - фиксированный
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)  # Время - фиксированный
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)  # Место - фиксированный
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)  # Стоимость - фиксированный
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Fixed)  # Статус - фиксированный
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.Stretch)

        self.tickets_table.setColumnWidth(0, 200)
        self.tickets_table.setColumnWidth(1, 120)
        self.tickets_table.setColumnWidth(2, 150)
        self.tickets_table.setColumnWidth(3, 120)
        self.tickets_table.setColumnWidth(4, 100)
        self.tickets_table.setColumnWidth(5, 125)
        self.tickets_table.setColumnWidth(6, 100)

        self.tickets_table.verticalHeader().setDefaultSectionSize(50)
        self.tickets_table.verticalHeader().setVisible(False)
        self.tickets_table.setAlternatingRowColors(True)
        self.tickets_table.setVisible(False)

        self.tickets_table.setStyleSheet("""
            QTableWidget {
                background-color: #1C1E22;
                border: 1px solid #2A2C32;
                border-radius: 8px;
                gridline-color: #2A2C32;
            }
            QTableWidget::item {
                padding: 8px;
                border: none;
                color: #EAEAEA;
            }
            QTableWidget::item:selected {
                background-color: #00A8E8;
                color: #FFFFFF;
            }
            QHeaderView::section {
                background-color: #25272B;
                color: #EAEAEA;
                font-weight: bold;
                padding: 10px;
                border: none;
                border-right: 1px solid #2A2C32;
            }
        """)

        layout.addWidget(self.tickets_table, stretch=1)

        # Кнопка назад
        if self.go_back:
            btn_back = QPushButton("⬅ Назад")
            btn_back.setObjectName("BackButton")
            btn_back.clicked.connect(self.go_back)
            layout.addWidget(btn_back)

    def load_tickets(self):
        """Загрузить билеты пользователя с проверкой возможности отмены"""
        try:
            if self._is_loaded:
                return

            tickets = TicketModel.get_user_tickets(self.user_id)

            if not tickets:
                self.loading_label.setText("🎫 У вас пока нет билетов")
                return

            self.tickets_table.setRowCount(len(tickets))

            for row, ticket in enumerate(tickets):
                # ticket структура:
                # [0]ticket_id, [1]title, [2]hall_name, [3]session_time,
                # [4]row_number, [5]seat_number, [6]final_price, [7]purchase_date, [8]final_price_discount

                # Проверяем, можно ли отменить билет
                session_time = ticket[3]
                can_cancel = self.can_cancel_ticket(session_time)
                status_text, status_color = self.get_ticket_status(session_time)

                # Заполняем данные
                self.tickets_table.setItem(row, 0, QTableWidgetItem(str(ticket[1])))  # Фильм
                self.tickets_table.setItem(row, 1, QTableWidgetItem(str(ticket[2])))  # Зал
                self.tickets_table.setItem(row, 2, QTableWidgetItem(session_time.strftime('%d.%m.%Y %H:%M')))  # Время
                self.tickets_table.setItem(row, 3, QTableWidgetItem(f"Ряд {ticket[4]}, Место {ticket[5]}"))  # Место
                self.tickets_table.setItem(row, 4, QTableWidgetItem(f"{float(ticket[6]):.0f} руб."))  # Стоимость

                # Статус
                status_item = QTableWidgetItem(status_text)
                status_item.setForeground(Qt.GlobalColor.green if can_cancel else Qt.GlobalColor.red)
                self.tickets_table.setItem(row, 5, status_item)

                # Кнопка отмены
                if can_cancel:
                    cancel_btn = QPushButton("Отменить")
                    cancel_btn.setFixedSize(150, 35)
                    cancel_btn.setStyleSheet("""
                        QPushButton {
                            background-color: #E63946;
                            color: white;
                            border: none;
                            border-radius: 5px;
                            font-weight: bold;
                            padding: 5px;
                        }
                        QPushButton:hover {
                            background-color: #C1121F;
                        }
                    """)
                    cancel_btn.clicked.connect(lambda checked, tid=ticket[0]: self.cancel_ticket(tid))
                    self.tickets_table.setCellWidget(row, 6, cancel_btn)
                else:
                    # Если отмена невозможна - показываем неактивную кнопку
                    cancel_btn = QPushButton("Нельзя вернуть")
                    cancel_btn.setFixedSize(150, 35)
                    cancel_btn.setEnabled(False)
                    cancel_btn.setStyleSheet("""
                        QPushButton {
                            background-color: #666666;
                            color: #AAAAAA;
                            border: none;
                            border-radius: 5px;
                            font-weight: bold;
                            padding: 5px;
                        }
                    """)
                    self.tickets_table.setCellWidget(row, 6, cancel_btn)

                # Устанавливаем выравнивание для всех ячеек
                for col in range(6):  # Для всех столбцов кроме последнего (там кнопка)
                    item = self.tickets_table.item(row, col)
                    if item:
                        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)

            # Показываем таблицу после загрузки
            self.loading_label.setVisible(False)
            self.tickets_table.setVisible(True)
            self._is_loaded = True

        except Exception as e:
            print(f"Ошибка при загрузке билетов: {e}")
            self.loading_label.setText("❌ Ошибка загрузки билетов")

    def can_cancel_ticket(self, session_time):
        """Проверить, можно ли отменить билет"""
        try:
            current_time = datetime.now()

            # Билет можно отменить только ДО начала сеанса
            # И если до сеанса осталось больше 1 часа
            time_difference = session_time - current_time
            return time_difference.total_seconds() > 3600  # 1 час в секундах

        except Exception as e:
            print(f"Ошибка при проверке возможности отмены: {e}")
            return False

    def get_ticket_status(self, session_time):
        """Получить текст и цвет статуса билета"""
        try:
            current_time = datetime.now()

            if session_time < current_time:
                return "Сеанс прошел", "red"
            elif self.can_cancel_ticket(session_time):
                return "Активен", "green"
            else:
                return "Нельзя вернуть", "orange"

        except Exception as e:
            print(f"Ошибка при определении статуса: {e}")
            return "⚫ Неизвестно", "gray"

    def cancel_ticket(self, ticket_id):
        """Отменить билет с дополнительными проверками"""
        try:
            # Дополнительная проверка перед отменой
            ticket_info = TicketModel.get_ticket_by_id(ticket_id)
            if not ticket_info:
                QMessageBox.critical(self, "Ошибка", "Билет не найден")
                return

            session_time = ticket_info[3]  # session_time из get_ticket_by_id

            if not self.can_cancel_ticket(session_time):
                QMessageBox.warning(
                    self,
                    "Невозможно отменить",
                    "Этот билет нельзя вернуть:\n"
                    "- Сеанс уже начался или скоро начнется\n"
                    "- Возврат возможен только за 1 час до начала сеанса"
                )
                return

            confirm = QMessageBox.question(
                self,
                "Отмена брони",
                "Вы уверены, что хотите отменить бронь?\n"
                f"Средства будут возвращены на ваш счет.\n\n"
                f"⚠️ Это действие необратимо!",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )

            if confirm == QMessageBox.StandardButton.Yes:
                success = TicketModel.cancel_ticket(ticket_id)
                if success:
                    QMessageBox.information(
                        self,
                        "Успех",
                        "Бронь отменена!\n"
                        f"Средства будут возвращены в течение 24 часов."
                    )
                    # Сбрасываем флаг и перезагружаем
                    self._is_loaded = False
                    self.tickets_table.setVisible(False)
                    self.loading_label.setVisible(True)
                    self.loading_label.setText("⏳ Обновление списка...")
                    from PyQt6.QtCore import QTimer
                    QTimer.singleShot(500, self.load_tickets)
                else:
                    QMessageBox.critical(self, "Ошибка", "Не удалось отменить бронь")

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при отмене брони: {str(e)}")

    def __del__(self):
        try:
            self._is_loaded = False
        except:
            pass