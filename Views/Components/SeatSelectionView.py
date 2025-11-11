from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QGridLayout, QFrame, QMessageBox,
                             QScrollArea)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from Models.TicketModel import TicketModel


class SeatWidget(QFrame):
    seat_clicked = pyqtSignal(int, int, float)  # seat_id, seat_number, price

    def __init__(self, seat_data, is_available=True, parent=None):
        super().__init__(parent)
        self.seat_id = seat_data[0]
        self.row = seat_data[1]
        self.number = seat_data[2]
        self.price = float(seat_data[3]) if seat_data[3] else 0.0
        self.is_available = is_available
        self.is_selected = False

        self.setup_ui()

    def setup_ui(self):
        self.setFixedSize(50, 50)
        if self.is_available:
            self.setCursor(Qt.CursorShape.PointingHandCursor)
        else:
            self.setCursor(Qt.CursorShape.ForbiddenCursor)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(2, 2, 2, 2)

        self.seat_label = QLabel(str(self.number))
        self.seat_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.seat_label.setStyleSheet("""
            background-color: transparent;
            color: #FFFFFF;
            font-weight: 600;
            font-size: 12px;
        """)
        layout.addWidget(self.seat_label)

        self.update_style()

    def update_style(self):
        if not self.is_available:
            # Занятое место
            self.setStyleSheet("""
                QFrame {
                    background-color: #E63946;
                    border: 2px solid #B71C1C;
                    border-radius: 8px;
                }
            """)
        elif self.is_selected:
            # Выбранное место
            self.setStyleSheet("""
                QFrame {
                    background-color: #55C78C;
                    border: 2px solid #2E7D32;
                    border-radius: 8px;
                }
            """)
        else:
            # Свободное место
            self.setStyleSheet("""
                QFrame {
                    background-color: #00A8E8;
                    border: 2px solid #0077B6;
                    border-radius: 8px;
                }
                QFrame:hover {
                    background-color: #03B7F5;
                    border: 2px solid #00A8E8;
                }
            """)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self.is_available:
            QTimer.singleShot(0, lambda: self.handle_click())
        super().mousePressEvent(event)

    def handle_click(self):
        """Обработка клика на место"""
        self.is_selected = not self.is_selected
        self.update_style()
        self.seat_clicked.emit(self.seat_id, self.number, self.price)

    def set_selected(self, selected):
        """Установить состояние выбора извне"""
        if self.is_available:
            self.is_selected = selected
            self.update_style()


class SeatSelectionView(QWidget):
    """Виджет выбора мест в зале"""
    booking_complete = pyqtSignal(list)  # список ticket_ids

    def __init__(self, session_id, user_id, parent=None):
        super().__init__(parent)
        self.session_id = session_id
        self.user_id = user_id
        self.selected_seats = {}  # словарь {seat_id: (seat_number, price)}
        self.seat_widgets = {}  # словарь {seat_id: SeatWidget}

        self.setup_ui()
        self.load_seats()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # Заголовок
        title = QLabel("🎫 Выбор мест")
        title.setObjectName("TitleLabel")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #FFFFFF;")
        layout.addWidget(title)

        # Информация о сеансе
        self.session_info = QLabel()
        self.session_info.setStyleSheet("color: #CCCCCC; font-size: 14px;")
        layout.addWidget(self.session_info)

        # Легенда
        legend_layout = QHBoxLayout()
        legend_layout.setSpacing(15)

        # Свободно
        free_legend = QHBoxLayout()
        free_color = QLabel()
        free_color.setFixedSize(20, 20)
        free_color.setStyleSheet("background-color: #00A8E8; border-radius: 4px;")
        free_label = QLabel("Свободно")
        free_label.setStyleSheet("color: #CCCCCC;")
        free_legend.addWidget(free_color)
        free_legend.addWidget(free_label)
        legend_layout.addLayout(free_legend)

        # Занято
        occupied_legend = QHBoxLayout()
        occupied_color = QLabel()
        occupied_color.setFixedSize(20, 20)
        occupied_color.setStyleSheet("background-color: #E63946; border-radius: 4px;")
        occupied_label = QLabel("Занято")
        occupied_label.setStyleSheet("color: #CCCCCC;")
        occupied_legend.addWidget(occupied_color)
        occupied_legend.addWidget(occupied_label)
        legend_layout.addLayout(occupied_legend)

        # Выбрано
        selected_legend = QHBoxLayout()
        selected_color = QLabel()
        selected_color.setFixedSize(20, 20)
        selected_color.setStyleSheet("background-color: #55C78C; border-radius: 4px;")
        selected_label = QLabel("Выбрано")
        selected_label.setStyleSheet("color: #CCCCCC;")
        selected_legend.addWidget(selected_color)
        selected_legend.addWidget(selected_label)
        legend_layout.addLayout(selected_legend)

        legend_layout.addStretch()
        layout.addLayout(legend_layout)

        # Экран зала
        screen_label = QLabel("🎬 ЭКРАН")
        screen_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        screen_label.setStyleSheet("""
            background-color: #2A2C32;
            color: #FFFFFF;
            font-weight: 700;
            font-size: 16px;
            padding: 10px;
            border-radius: 8px;
            margin: 20px 50px;
        """)
        layout.addWidget(screen_label)

        # Область прокрутки для мест
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        self.seats_container = QWidget()
        self.seats_layout = QGridLayout(self.seats_container)
        self.seats_layout.setSpacing(8)
        self.seats_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        scroll.setWidget(self.seats_container)
        layout.addWidget(scroll, stretch=1)

        # Панель выбора
        self.selection_panel = self.create_selection_panel()
        layout.addWidget(self.selection_panel)

        # Загружаем информацию о сеансе после создания UI
        QTimer.singleShot(0, self.load_session_info)

    def create_selection_panel(self):
        """Создать панель с информацией о выборе"""
        panel = QFrame()
        panel.setStyleSheet("""
            QFrame {
                background-color: #1C1E22;
                border: 2px solid #2A2C32;
                border-radius: 8px;
                padding: 15px;
            }
        """)

        layout = QHBoxLayout(panel)

        # Информация о выборе
        self.selection_info = QLabel("Выберите места")
        self.selection_info.setStyleSheet("color: #CCCCCC; font-size: 14px;")
        layout.addWidget(self.selection_info)

        layout.addStretch()

        # Кнопка бронирования
        self.book_btn = QPushButton("🛒 Забронировать")
        self.book_btn.setFixedSize(180, 40)
        self.book_btn.setEnabled(False)
        self.book_btn.clicked.connect(self.book_tickets)
        self.book_btn.setStyleSheet("""
            QPushButton {
                background-color: #00A8E8;
                color: white;
                border: none;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover:enabled {
                background-color: #0077B6;
            }
            QPushButton:disabled {
                background-color: #2A2C32;
                color: #666666;
            }
        """)
        layout.addWidget(self.book_btn)

        return panel

    def load_session_info(self):
        """Загрузить информацию о сеансе"""
        try:
            session_info = TicketModel.get_session_info(self.session_id)
            if session_info:
                # session_info[1] - title, session_info[3] - hall_name, session_info[5] - session_time
                info_text = f"🎬 {session_info[1]} | 🎭 {session_info[3]} | 🕒 {session_info[5].strftime('%d.%m.%Y %H:%M')}"
                self.session_info.setText(info_text)
        except Exception as e:
            print(f"Ошибка при загрузке информации о сеансе: {e}")

    def load_seats(self):
        """Загрузить места зала"""
        try:
            # Очищаем предыдущие виджеты
            while self.seats_layout.count():
                child = self.seats_layout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()

            self.seat_widgets.clear()
            self.selected_seats.clear()

            # Получаем информацию о сеансе
            session_info = TicketModel.get_session_info(self.session_id)
            if not session_info:
                raise Exception("Не удалось получить информацию о сеансе")

            hall_id = session_info[7]  # hall_id - последний элемент

            # Получаем все места зала
            all_seats = TicketModel.get_all_seats_for_hall(hall_id)

            # Получаем занятые места для этого сеанса
            occupied_seats = TicketModel.get_occupied_seats(self.session_id)
            occupied_ids = {seat[0] for seat in occupied_seats}

            # Группируем места по рядам
            rows = {}
            for seat in all_seats:
                row = seat[1]
                if row not in rows:
                    rows[row] = []
                rows[row].append(seat)

            # Сортируем ряды
            sorted_rows = sorted(rows.keys())

            # Создаем виджеты мест
            for row_index, row_num in enumerate(sorted_rows):
                # Метка ряда
                row_label = QLabel(f"Ряд {row_num}")
                row_label.setStyleSheet("color: #FFFFFF; font-weight: 600; margin-right: 10px;")
                self.seats_layout.addWidget(row_label, row_index, 0)

                # Места в ряду
                seats_in_row = sorted(rows[row_num], key=lambda x: x[2])
                for col_index, seat_data in enumerate(seats_in_row):
                    # Проверяем доступность места
                    is_available = seat_data[0] not in occupied_ids

                    # Создаем виджет места
                    seat_widget = SeatWidget(seat_data, is_available)

                    # Подключаем сигнал только для доступных мест
                    if is_available:
                        seat_widget.seat_clicked.connect(self.on_seat_clicked)

                    # Сохраняем виджет
                    self.seat_widgets[seat_data[0]] = seat_widget

                    self.seats_layout.addWidget(seat_widget, row_index, col_index + 1)

        except Exception as e:
            print(f"Ошибка при загрузке мест: {e}")
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить схему зала: {str(e)}")

    def on_seat_clicked(self, seat_id, seat_number, price):
        """Обработчик выбора места"""
        try:
            if seat_id in self.selected_seats:
                del self.selected_seats[seat_id]
            else:
                self.selected_seats[seat_id] = (seat_number, float(price))

            self.update_selection_info()

        except Exception as e:
            print(f"Ошибка при обработке выбора места: {e}")

    def update_selection_info(self):
        """Обновить информацию о выборе"""
        try:
            if not self.selected_seats:
                self.selection_info.setText("Выберите места")
                self.book_btn.setEnabled(False)
                return

            seats_numbers = sorted([seat[0] for seat in self.selected_seats.values()])
            seats_text = ", ".join([f"#{num}" for num in seats_numbers])

            total_price = self.calculate_total_price()

            self.selection_info.setText(
                f"Выбрано мест: {len(self.selected_seats)} ({seats_text}) | "
                f"Итого: {total_price:.0f} руб."
            )
            self.book_btn.setEnabled(True)

        except Exception as e:
            print(f"Ошибка при обновлении информации о выборе: {e}")

    def calculate_total_price(self):
        """Рассчитать общую стоимость"""
        try:
            session_info = TicketModel.get_session_info(self.session_id)
            if session_info:
                # session_info[2] - base_price, session_info[4] - hall_extra_price
                base_price = float(session_info[2]) if session_info[2] else 0.0
                hall_extra = float(session_info[4]) if session_info[4] else 0.0
            else:
                base_price = 0.0
                hall_extra = 0.0

            # Суммируем цены мест
            seats_price = sum(float(seat[1]) for seat in self.selected_seats.values())

            # Общая цена
            total = seats_price + (base_price + hall_extra) * len(self.selected_seats)
            return total

        except Exception as e:
            print(f"Ошибка при расчете цены: {e}")
            return 0.0

    def book_tickets(self):
        """Забронировать выбранные места"""
        if not self.selected_seats:
            return

        total_price = self.calculate_total_price()
        confirm = QMessageBox.question(
            self,
            "Подтверждение бронирования",
            f"Забронировать {len(self.selected_seats)} мест?\n\n"
            f"Стоимость: {total_price:.0f} руб.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if confirm == QMessageBox.StandardButton.Yes:
            try:
                successful_bookings = []
                for seat_id in self.selected_seats.keys():
                    ticket_id = TicketModel.create_ticket(self.session_id, self.user_id, seat_id)
                    if ticket_id:
                        successful_bookings.append(ticket_id)

                if successful_bookings:
                    QMessageBox.information(
                        self,
                        "Успех!",
                        f"Бронь оформлена!\n"
                        f"Забронировано мест: {len(successful_bookings)}\n"
                        f"Номера билетов: {', '.join(map(str, successful_bookings))}"
                    )
                    self.booking_complete.emit(successful_bookings)
                    # Перезагружаем места после бронирования
                    self.load_seats()
                else:
                    QMessageBox.critical(self, "Ошибка", "Не удалось забронировать места")

            except Exception as e:
                print(f"Ошибка при бронировании: {e}")
                QMessageBox.critical(self, "Ошибка", f"Ошибка при бронировании: {str(e)}")

    def refresh(self):
        """Обновить виджет при повторном открытии"""
        self.load_seats()
        self.load_session_info()