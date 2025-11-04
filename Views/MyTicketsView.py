import os
from datetime import datetime

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QAction, QCursor
from PyQt6.QtWidgets import (QDialog, QFileDialog, QFrame, QHeaderView,
                             QHBoxLayout, QLabel, QMenu, QMessageBox,
                             QProgressBar, QPushButton, QScrollArea,
                             QTableWidget, QTableWidgetItem, QVBoxLayout,
                             QWidget)

from Models.TicketModel import TicketModel
from ViewModels.TicketViewModel import TicketViewModel


class MyTicketsView(QWidget):
    def __init__(self, user_id, go_back=None):
        super().__init__()
        self.user_id = user_id
        self.go_back = go_back
        self._is_loaded = False
        self.vm = TicketViewModel()

        self.setup_ui()
        QTimer.singleShot(100, self.load_tickets)

        self.vm.pdf_generated.connect(self.on_pdf_generated)
        self.vm.pdf_generation_failed.connect(self.on_pdf_generation_failed)

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        title = QLabel("🎟️ Мои билеты")
        title.setObjectName("TitleLabel")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        self.loading_label = QLabel("⏳ Загрузка билетов...")
        self.loading_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.loading_label.setStyleSheet("color: #AAAAAA; font-size: 16px;")
        layout.addWidget(self.loading_label)

        self.pdf_progress = QProgressBar()
        self.pdf_progress.setVisible(False)
        self.pdf_progress.setRange(0, 0)
        layout.addWidget(self.pdf_progress)

        self.tickets_table = QTableWidget()
        self.tickets_table.setColumnCount(8)
        self.tickets_table.setHorizontalHeaderLabels([
            "Фильм", "Зал", "Время", "Место", "Стоимость", "Статус", "Действия", "PDF"
        ])

        header = self.tickets_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Fixed)

        self.tickets_table.setColumnWidth(0, 300)
        self.tickets_table.setColumnWidth(1, 150)
        self.tickets_table.setColumnWidth(2, 140)
        self.tickets_table.setColumnWidth(3, 120)
        self.tickets_table.setColumnWidth(4, 90)
        self.tickets_table.setColumnWidth(5, 150)
        self.tickets_table.setColumnWidth(6, 150)
        self.tickets_table.setColumnWidth(7, 150)

        self.tickets_table.verticalHeader().setDefaultSectionSize(50)
        self.tickets_table.verticalHeader().setVisible(False)
        self.tickets_table.setAlternatingRowColors(True)
        self.tickets_table.setVisible(False)
        self.tickets_table.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.tickets_table.setSelectionMode(QTableWidget.SelectionMode.NoSelection)

        self.tickets_table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tickets_table.customContextMenuRequested.connect(self.show_context_menu)

        scroll_area = QScrollArea()
        scroll_area.setWidget(self.tickets_table)
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)

        layout.addWidget(scroll_area, stretch=1)

        self.btn_bulk_pdf = QPushButton("📥 Скачать все билеты PDF")
        self.btn_bulk_pdf.setFixedHeight(40)
        self.btn_bulk_pdf.clicked.connect(self.download_all_tickets_pdf)
        self.btn_bulk_pdf.setVisible(False)
        layout.addWidget(self.btn_bulk_pdf)

        if self.go_back:
            btn_back = QPushButton("⬅ Назад")
            btn_back.setObjectName("BackButton")
            btn_back.clicked.connect(self.go_back)
            layout.addWidget(btn_back)

    def show_context_menu(self, position):
        row = self.tickets_table.rowAt(position.y())
        if row < 0:
            return

        ticket_id_item = self.tickets_table.item(row, 0)
        if not ticket_id_item:
            return

        ticket_id = ticket_id_item.data(Qt.ItemDataRole.UserRole)
        if not ticket_id:
            return

        menu = QMenu(self)

        download_action = QAction("📥 Скачать PDF билета", self)
        download_action.triggered.connect(lambda: self.download_ticket_pdf(ticket_id))
        menu.addAction(download_action)

        details_action = QAction("👁️ Просмотреть детали", self)
        details_action.triggered.connect(lambda: self.view_ticket_details(ticket_id))
        menu.addAction(details_action)

        menu.exec(QCursor.pos())

    def load_tickets(self):
        try:
            if self._is_loaded:
                return

            tickets = TicketModel.get_user_tickets(self.user_id)

            if not tickets:
                self.loading_label.setText("🎫 У вас пока нет билетов")
                return

            self.tickets_table.setRowCount(len(tickets))

            for row, ticket in enumerate(tickets):
                ticket_id, movie_title, hall_name, session_time, seat_row, seat_number, price, *_ = ticket

                can_cancel = self.can_cancel_ticket(session_time)
                status_text, status_color = self.get_ticket_status(session_time, can_cancel)

                film_item = QTableWidgetItem(str(movie_title))
                film_item.setData(Qt.ItemDataRole.UserRole, ticket_id)
                self.tickets_table.setItem(row, 0, film_item)

                self.tickets_table.setItem(row, 1, QTableWidgetItem(str(hall_name)))
                self.tickets_table.setItem(row, 2, QTableWidgetItem(session_time.strftime('%d.%m.%Y %H:%M')))
                self.tickets_table.setItem(row, 3, QTableWidgetItem(f"Ряд {seat_row}, Место {seat_number}"))
                self.tickets_table.setItem(row, 4, QTableWidgetItem(f"{float(price):.0f} руб."))

                status_item = QTableWidgetItem(status_text)
                if status_color == "green":
                    status_item.setForeground(Qt.GlobalColor.green)
                elif status_color == "red":
                    status_item.setForeground(Qt.GlobalColor.red)
                elif status_color == "orange":
                    status_item.setForeground(Qt.GlobalColor.yellow)
                self.tickets_table.setItem(row, 5, status_item)

                actions_widget = QWidget()
                actions_layout = QHBoxLayout(actions_widget)
                actions_layout.setContentsMargins(0, 0, 0, 0)
                actions_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

                if can_cancel:
                    cancel_btn = QPushButton("Отменить")
                    cancel_btn.setStyleSheet("background-color: #E63946; border-radius: 5px;")
                    cancel_btn.clicked.connect(lambda checked, tid=ticket_id: self.cancel_ticket(tid))
                    actions_layout.addWidget(cancel_btn)
                else:
                    cancel_label = QLabel("Нельзя вернуть")
                    cancel_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    cancel_label.setStyleSheet("color: #888;")
                    actions_layout.addWidget(cancel_label)
                self.tickets_table.setCellWidget(row, 6, actions_widget)

                pdf_widget = QWidget()
                pdf_layout = QHBoxLayout(pdf_widget)
                pdf_layout.setContentsMargins(0, 0, 0, 0)
                pdf_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
                pdf_btn = QPushButton("Скачать билет")
                pdf_btn.clicked.connect(lambda checked, tid=ticket_id: self.download_ticket_pdf(tid))
                pdf_layout.addWidget(pdf_btn)
                self.tickets_table.setCellWidget(row, 7, pdf_widget)

                for col in range(6):
                    item = self.tickets_table.item(row, col)
                    if item:
                        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)

            self.loading_label.setVisible(False)
            self.tickets_table.setVisible(True)
            self.btn_bulk_pdf.setVisible(len(tickets) > 0)
            self._is_loaded = True

        except Exception as e:
            print(f"Ошибка при загрузке билетов: {e}")
            self.loading_label.setText("❌ Ошибка загрузки билетов")

    def download_ticket_pdf(self, ticket_id):
        try:
            self.pdf_progress.setVisible(True)
            self.vm.generate_ticket_pdf(ticket_id, self.user_id)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось начать генерацию PDF: {str(e)}")
            self.pdf_progress.setVisible(False)

    def download_all_tickets_pdf(self):
        try:
            tickets = TicketModel.get_user_tickets(self.user_id)
            if not tickets:
                QMessageBox.information(self, "Информация", "У вас нет билетов для скачивания")
                return

            ticket_ids = [ticket[0] for ticket in tickets]
            self.pdf_progress.setVisible(True)
            self.vm.generate_multiple_tickets_pdf(ticket_ids, self.user_id)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось начать генерацию PDF: {str(e)}")
            self.pdf_progress.setVisible(False)

    def on_pdf_generated(self, filepath, filename):
        self.pdf_progress.setVisible(False)
        try:
            reply = QMessageBox.question(
                self,
                "PDF готов",
                f"Файл '{filename}' успешно сгенерирован!\n\nХотите открыть файл или сохранить в другое место?",
                QMessageBox.StandardButton.Open | QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Cancel
            )
            if reply == QMessageBox.StandardButton.Open:
                os.startfile(os.path.normpath(filepath))
            elif reply == QMessageBox.StandardButton.Save:
                new_path, _ = QFileDialog.getSaveFileName(self, "Сохранить PDF", filename, "PDF Files (*.pdf)")
                if new_path:
                    import shutil
                    shutil.copy2(filepath, new_path)
                    QMessageBox.information(self, "Успех", f"Файл сохранен: {new_path}")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось обработать PDF файл: {str(e)}")

    def on_pdf_generation_failed(self, error_message):
        self.pdf_progress.setVisible(False)
        QMessageBox.critical(self, "Ошибка", f"Не удалось сгенерировать PDF:\n{error_message}")

    def view_ticket_details(self, ticket_id):
        ticket_data = None
        for i in range(self.tickets_table.rowCount()):
            if self.tickets_table.item(i, 0).data(Qt.ItemDataRole.UserRole) == ticket_id:
                ticket_data = {
                    "id": ticket_id,
                    "film": self.tickets_table.item(i, 0).text(),
                    "hall": self.tickets_table.item(i, 1).text(),
                    "time": self.tickets_table.item(i, 2).text(),
                    "seat": self.tickets_table.item(i, 3).text(),
                    "price": self.tickets_table.item(i, 4).text(),
                }
                break

        if not ticket_data:
            QMessageBox.warning(self, "Ошибка", "Информация о билете не найдена в таблице")
            return

        QMessageBox.information(
            self,
            f"Детали билета #{ticket_data['id']}",
            f"<b>🎬 Фильм:</b> {ticket_data['film']}<br>"
            f"<b>🏛️ Зал:</b> {ticket_data['hall']}<br>"
            f"<b>🕐 Время сеанса:</b> {ticket_data['time']}<br>"
            f"<b>💺 Место:</b> {ticket_data['seat']}<br>"
            f"<b>💰 Стоимость:</b> {ticket_data['price']}"
        )

    def can_cancel_ticket(self, session_time):
        return (session_time - datetime.now()).total_seconds() > 3600

    def get_ticket_status(self, session_time, can_cancel):
        if session_time < datetime.now():
            return "Сеанс прошел", "red"
        elif can_cancel:
            return "Активен", "green"
        else:
            return "Скоро начнется", "orange"

    def cancel_ticket(self, ticket_id):
        """Отменить билет"""
        try:
            ticket_info = TicketModel.get_ticket_by_id(ticket_id)
            if not ticket_info:
                QMessageBox.critical(self, "Ошибка", "Билет не найден")
                return

            confirm = QMessageBox.question(
                self,
                "Отмена брони",
                f"Вы уверены, что хотите отменить бронь?\n\n"
                f"🎬 {ticket_info[1]}\n"
                f"🏛️ {ticket_info[2]}\n"
                f"💰 {float(ticket_info[7]):.0f} руб.\n\n"
                f"Средства будут возвращены в течение 24 часов.\n"
                f"⚠️ Это действие необратимо!",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )

            if confirm == QMessageBox.StandardButton.Yes:
                if TicketModel.cancel_ticket(ticket_id, self.user_id):
                    QMessageBox.information(
                        self,
                        "Успех",
                        "Бронь отменена!\n\nСредства будут возвращены в течение 24 часов."
                    )

                    self._is_loaded = False
                    self.tickets_table.setVisible(False)
                    self.btn_bulk_pdf.setVisible(False)
                    self.loading_label.setText("⏳ Обновление...")
                    self.loading_label.setVisible(True)
                    QTimer.singleShot(100, self.load_tickets)
                else:
                    QMessageBox.critical(self, "Ошибка", "Не удалось отменить бронь")

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при отмене: {str(e)}")