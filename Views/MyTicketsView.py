import os
from datetime import datetime

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import (QFileDialog, QFrame, QHeaderView,
                             QHBoxLayout, QLabel, QMessageBox,
                             QProgressBar, QPushButton, QScrollArea,
                             QTableWidget, QTableWidgetItem, QVBoxLayout,
                             QWidget, QAbstractItemView)

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

        self.selection_hint_label = QLabel("💡 Совет: Удерживайте Ctrl или Shift для выбора нескольких билетов.")
        self.selection_hint_label.setStyleSheet("color: #888888; font-size: 11pt;")
        self.selection_hint_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.selection_hint_label.setVisible(False)
        layout.addWidget(self.selection_hint_label)

        self.tickets_table = QTableWidget()
        self.tickets_table.setColumnCount(6)
        self.tickets_table.setHorizontalHeaderLabels([
            "Фильм", "Зал", "Время", "Место", "Стоимость", "Статус"
        ])

        header = self.tickets_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Interactive)
        self.tickets_table.setColumnWidth(0, 350)

        self.tickets_table.verticalHeader().setDefaultSectionSize(50)
        self.tickets_table.verticalHeader().setVisible(False)
        self.tickets_table.setAlternatingRowColors(True)
        self.tickets_table.setVisible(False)
        self.tickets_table.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        self.tickets_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tickets_table.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.tickets_table.itemSelectionChanged.connect(self.update_action_buttons_state)

        scroll_area = QScrollArea()
        scroll_area.setWidget(self.tickets_table)
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        layout.addWidget(scroll_area, stretch=1)

        self.actions_widget = QWidget()
        actions_layout = QHBoxLayout(self.actions_widget)
        actions_layout.setContentsMargins(0, 0, 0, 0)
        actions_layout.setSpacing(10)

        self.btn_cancel_selected = QPushButton("❌ Отменить выбранный")
        self.btn_cancel_selected.setFixedHeight(40)
        self.btn_cancel_selected.clicked.connect(self.cancel_selected_ticket)

        self.btn_download_selected_pdf = QPushButton("📥 Скачать PDF")
        self.btn_download_selected_pdf.setFixedHeight(40)
        self.btn_download_selected_pdf.setToolTip("Выберите один билет в таблице, чтобы скачать его.")
        self.btn_download_selected_pdf.clicked.connect(self.download_selected_ticket_pdf)

        self.btn_download_multiple_pdf = QPushButton("📦 Скачать выбранные PDF")
        self.btn_download_multiple_pdf.setFixedHeight(40)
        self.btn_download_multiple_pdf.setToolTip(
            "Выберите один или несколько билетов (удерживая Ctrl или Shift) для скачивания."
        )
        self.btn_download_multiple_pdf.clicked.connect(self.download_selected_tickets_pdf)

        actions_layout.addWidget(self.btn_cancel_selected)
        actions_layout.addWidget(self.btn_download_selected_pdf)
        actions_layout.addWidget(self.btn_download_multiple_pdf)
        actions_layout.addStretch()

        self.actions_widget.setVisible(False)
        layout.addWidget(self.actions_widget)

        if self.go_back:
            btn_back = QPushButton("⬅ Назад")
            btn_back.setObjectName("BackButton")
            btn_back.clicked.connect(self.go_back)
            layout.addWidget(btn_back)

    def load_tickets(self):
        try:
            if self._is_loaded:
                self.tickets_table.setRowCount(0)

            tickets = TicketModel.get_user_tickets(self.user_id)

            if not tickets:
                self.loading_label.setText("🎫 У вас пока нет билетов")
                self.loading_label.setVisible(True)
                self.tickets_table.setVisible(False)
                self.actions_widget.setVisible(False)
                self.selection_hint_label.setVisible(False)
                return

            self.tickets_table.setRowCount(len(tickets))

            for row, ticket in enumerate(tickets):
                ticket_id, movie_title, hall_name, session_time, seat_row, seat_number, price, *_ = ticket

                can_cancel = self.can_cancel_ticket(session_time)
                status_text, status_color = self.get_ticket_status(session_time, can_cancel)

                film_item = QTableWidgetItem(str(movie_title))
                film_item.setData(Qt.ItemDataRole.UserRole, {'id': ticket_id, 'can_cancel': can_cancel})
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

                for col in range(6):
                    item = self.tickets_table.item(row, col)
                    if item:
                        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)

            self.loading_label.setVisible(False)
            self.tickets_table.setVisible(True)
            self.actions_widget.setVisible(True)
            self.selection_hint_label.setVisible(True)
            self.update_action_buttons_state()
            self._is_loaded = True

        except Exception as e:
            print(f"Ошибка при загрузке билетов: {e}")
            self.loading_label.setText("❌ Ошибка загрузки билетов")
            self.loading_label.setVisible(True)

    def update_action_buttons_state(self):
        selected_rows = self.get_selected_ticket_ids(get_data=True)
        count = len(selected_rows)

        can_cancel_selected = False
        if count == 1:
            can_cancel_selected = selected_rows[0]['can_cancel']

        self.btn_cancel_selected.setEnabled(count == 1 and can_cancel_selected)
        self.btn_download_selected_pdf.setEnabled(count == 1)
        self.btn_download_multiple_pdf.setEnabled(count > 0)

    def get_selected_ticket_ids(self, get_data=False):
        selected_ids = []
        selected_rows = self.tickets_table.selectionModel().selectedRows()

        for index in selected_rows:
            item_data = self.tickets_table.item(index.row(), 0).data(Qt.ItemDataRole.UserRole)
            if get_data:
                selected_ids.append(item_data)
            else:
                selected_ids.append(item_data['id'])
        return selected_ids

    def download_selected_ticket_pdf(self):
        selected_ids = self.get_selected_ticket_ids()
        if len(selected_ids) != 1:
            QMessageBox.warning(self, "Внимание", "Пожалуйста, выберите ровно один билет для скачивания.")
            return

        ticket_id = selected_ids[0]
        try:
            self.pdf_progress.setVisible(True)
            self.vm.generate_ticket_pdf(ticket_id, self.user_id)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось начать генерацию PDF: {str(e)}")
            self.pdf_progress.setVisible(False)

    def download_selected_tickets_pdf(self):
        ticket_ids = self.get_selected_ticket_ids()
        if not ticket_ids:
            QMessageBox.warning(self, "Внимание", "Пожалуйста, выберите один или несколько билетов для скачивания.")
            return

        try:
            self.pdf_progress.setVisible(True)
            if len(ticket_ids) == 1:
                self.vm.generate_ticket_pdf(ticket_ids[0], self.user_id)
            else:
                self.vm.generate_multiple_tickets_pdf(ticket_ids, self.user_id)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось начать генерацию PDF: {str(e)}")
            self.pdf_progress.setVisible(False)

    def cancel_selected_ticket(self):
        selected_ids = self.get_selected_ticket_ids()
        if len(selected_ids) != 1:
            QMessageBox.warning(self, "Внимание", "Пожалуйста, выберите ровно один билет для отмены.")
            return
        self.cancel_ticket(selected_ids[0])

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
                    self.loading_label.setText("⏳ Обновление списка...")
                    self.loading_label.setVisible(True)
                    self.tickets_table.setVisible(False)
                    self.actions_widget.setVisible(False)
                    self.selection_hint_label.setVisible(False)
                    QTimer.singleShot(100, self.load_tickets)
                else:
                    QMessageBox.critical(self, "Ошибка", "Не удалось отменить бронь")

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при отмене: {str(e)}")