from PyQt6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QPushButton, QHBoxLayout,
    QTableView, QSizePolicy, QMessageBox, QSpacerItem, QDialog,
    QLineEdit, QFormLayout, QDialogButtonBox, QSpinBox, QDoubleSpinBox,
    QTabWidget, QGridLayout, QGroupBox, QComboBox, QTableWidgetItem, QTableWidget
)
from PyQt6.QtCore import Qt
from core.database import datagrid_model
from Models.HallModel import HallModel
from Models.SeatModel import SeatModel


class AdminPanelHallsView(QWidget):
    def __init__(self, go_back=None):
        super().__init__()
        self.go_back = go_back
        self.setup_ui()
        self.refresh_halls_table()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 30, 40, 30)
        layout.setSpacing(25)

        # Заголовок
        header = QHBoxLayout()
        title = QLabel("🎭 Управление залами")
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

        # Вкладки
        self.tabs = QTabWidget()

        # Вкладка залов
        self.create_halls_tab()
        # Вкладка управления местами
        self.create_seats_tab()

        layout.addWidget(self.tabs, stretch=1)

    def create_halls_tab(self):
        """Вкладка управления залами"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(20)

        # Таблица залов
        self.halls_view = QTableView()
        self.halls_view.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self.halls_view.setSelectionMode(QTableView.SelectionMode.SingleSelection)
        self.halls_view.setAlternatingRowColors(True)
        layout.addWidget(self.halls_view, stretch=1)

        # Кнопки управления
        btns = QHBoxLayout()
        btns.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Policy.Expanding))

        self.btn_add_hall = QPushButton("➕ Добавить зал")
        self.btn_add_hall.clicked.connect(self.add_hall)
        btns.addWidget(self.btn_add_hall)

        self.btn_edit_hall = QPushButton("✏️ Редактировать")
        self.btn_edit_hall.clicked.connect(self.edit_hall)
        btns.addWidget(self.btn_edit_hall)

        self.btn_delete_hall = QPushButton("🗑 Удалить")
        self.btn_delete_hall.setObjectName("LogoutButton")
        self.btn_delete_hall.clicked.connect(self.delete_hall)
        btns.addWidget(self.btn_delete_hall)

        self.btn_refresh = QPushButton("🔄 Обновить")
        self.btn_refresh.clicked.connect(self.refresh_halls_table)
        btns.addWidget(self.btn_refresh)

        btns.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Policy.Expanding))
        layout.addLayout(btns)

        self.tabs.addTab(tab, "Залы")

    def create_seats_tab(self):
        """Вкладка управления местами"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(20)

        # Выбор зала
        hall_group = QGroupBox("Выбор зала")
        hall_layout = QHBoxLayout(hall_group)

        hall_layout.addWidget(QLabel("Зал:"))
        self.hall_combo = QComboBox()
        self.hall_combo.currentIndexChanged.connect(self.on_hall_selected)
        hall_layout.addWidget(self.hall_combo)

        hall_layout.addStretch()
        layout.addWidget(hall_group)

        # Информация о зале
        self.hall_info = QLabel("Выберите зал для управления местами")
        self.hall_info.setStyleSheet("color: #666; font-style: italic;")
        layout.addWidget(self.hall_info)

        # Таблица мест
        self.seats_view = QTableView()
        self.seats_view.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self.seats_view.setAlternatingRowColors(True)
        layout.addWidget(self.seats_view, stretch=1)

        # Кнопки управления местами
        seats_btns = QHBoxLayout()
        seats_btns.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Policy.Expanding))

        self.btn_add_seats = QPushButton("🎫 Добавить места")
        self.btn_add_seats.clicked.connect(self.add_seats_bulk)
        seats_btns.addWidget(self.btn_add_seats)

        # НОВАЯ КНОПКА - управление ценами по рядам
        self.btn_manage_prices = QPushButton("💰 Управление ценами")
        self.btn_manage_prices.clicked.connect(self.manage_row_prices)
        seats_btns.addWidget(self.btn_manage_prices)

        self.btn_clear_seats = QPushButton("🗑 Очистить места")
        self.btn_clear_seats.setObjectName("LogoutButton")
        self.btn_clear_seats.clicked.connect(self.clear_seats)
        seats_btns.addWidget(self.btn_clear_seats)

        seats_btns.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Policy.Expanding))
        layout.addLayout(seats_btns)

        self.tabs.addTab(tab, "Места")

    def refresh_halls_table(self):
        """Обновить таблицу залов"""
        self.halls_model = datagrid_model(
            "SELECT hall_id, hall_number, hall_name, hall_type, "
            "hall_extra_price, created_at FROM hall ORDER BY hall_number"
        )
        self.halls_view.setModel(self.halls_model)

        # Обновить комбобокс залов
        self.hall_combo.clear()
        halls = HallModel.get_all_halls()
        for hall in halls:
            self.hall_combo.addItem(f"{hall[1]} - {hall[2]}", hall[0])

    def on_hall_selected(self):
        """Обработчик выбора зала"""
        hall_id = self.hall_combo.currentData()
        if hall_id:
            hall = HallModel.get_hall_by_id(hall_id)
            if hall:
                self.hall_info.setText(
                    f"Зал: {hall[2]} (№{hall[1]}, {hall[3]}) - "
                    f"Доплата: {hall[4]} руб."
                )
                self.refresh_seats_table(hall_id)

    def refresh_seats_table(self, hall_id):
        """Обновить таблицу мест с информацией о ценах"""
        self.seats_model = datagrid_model(
            "SELECT seat_id, row_number, seat_number, seat_extra_price, "
            "created_at FROM seat WHERE hall_id = %s ORDER BY row_number, seat_number",
            [hall_id]
        )
        self.seats_view.setModel(self.seats_model)

        # Обновляем информацию о зале
        hall = HallModel.get_hall_by_id(hall_id)
        if hall:
            seats_count = len(SeatModel.get_seats_by_hall(hall_id))
            rows_summary = SeatModel.get_rows_summary(hall_id)

            info_text = f"Зал: {hall[2]} (№{hall[1]}, {hall[3]}) - "
            info_text += f"Мест: {seats_count} - "
            info_text += f"Рядов: {len(rows_summary)}"

            self.hall_info.setText(info_text)
            self.hall_info.setStyleSheet("color: #00A8E8; font-weight: 600;")

    def get_selected_hall(self):
        """Получить выбранный зал"""
        selection = self.halls_view.selectionModel().selectedRows()
        if not selection:
            return None

        row = selection[0].row()
        return {
            'hall_id': self.halls_model.item(row, 0).text(),
            'hall_number': self.halls_model.item(row, 1).text(),
            'hall_name': self.halls_model.item(row, 2).text()
        }

    def add_hall(self):
        """Добавить зал"""
        dialog = HallDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            try:
                # Получаем данные из нового диалога
                hall_data = dialog.get_hall_data()
                hall_id = HallModel.create_hall(
                    hall_data['number'],
                    hall_data['name'],
                    hall_data['type'],
                    hall_data['extra_price']
                )
                if hall_id:
                    QMessageBox.information(self, "Успех", "Зал успешно добавлен")
                    self.refresh_halls_table()
            except ValueError as e:
                QMessageBox.warning(self, "Ошибка валидации", str(e))
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось добавить зал: {str(e)}")

    def edit_hall(self):
        """Редактировать зал"""
        hall = self.get_selected_hall()
        if not hall:
            QMessageBox.warning(self, "Внимание", "Выберите зал из таблицы")
            return

        hall_data = HallModel.get_hall_by_id(hall['hall_id'])
        dialog = HallDialog(self, hall_data)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            try:
                # Получаем данные из нового диалога
                hall_data = dialog.get_hall_data()
                HallModel.update_hall(
                    hall['hall_id'],
                    hall_data['number'],
                    hall_data['name'],
                    hall_data['type'],
                    hall_data['extra_price']
                )
                QMessageBox.information(self, "Успех", "Зал успешно обновлен")
                self.refresh_halls_table()
            except ValueError as e:
                QMessageBox.warning(self, "Ошибка валидации", str(e))
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось обновить зал: {str(e)}")

    def delete_hall(self):
        """Удалить зал"""
        hall = self.get_selected_hall()
        if not hall:
            QMessageBox.warning(self, "Внимание", "Выберите зал из таблицы")
            return

        confirm = QMessageBox.question(
            self, "Подтверждение",
            f"Удалить зал '<b>{hall['hall_name']}</b>' (№{hall['hall_number']})?<br><br>"
            f"⚠️ <b>Будут удалены все связанные сеансы и места!</b>",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if confirm == QMessageBox.StandardButton.Yes:
            try:
                HallModel.delete_hall(hall['hall_id'])
                QMessageBox.information(self, "Успех", "Зал удален")
                self.refresh_halls_table()
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось удалить зал: {str(e)}")

    def add_seats_bulk(self):
        """Добавить места с настройкой цен по рядам"""
        hall_id = self.hall_combo.currentData()
        if not hall_id:
            QMessageBox.warning(self, "Внимание", "Выберите зал")
            return

        dialog = BulkSeatsDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            try:
                rows_config = dialog.get_rows_config()
                created_count = SeatModel.create_multiple_seats(hall_id, rows_config)

                QMessageBox.information(
                    self, "Успех",
                    f"Добавлено {len(created_count)} мест\n"
                    f"Рядов: {len(rows_config)}\n"
                    f"Настройка цен применена"
                )
                self.refresh_seats_table(hall_id)
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось добавить места: {str(e)}")

    def clear_seats(self):
        """Очистить все места в зале"""
        hall_id = self.hall_combo.currentData()
        if not hall_id:
            QMessageBox.warning(self, "Внимание", "Выберите зал")
            return

        hall = HallModel.get_hall_by_id(hall_id)
        confirm = QMessageBox.question(
            self, "Подтверждение",
            f"Очистить все места в зале '<b>{hall[2]}</b>'?<br><br>"
            f"⚠️ <b>Это действие необратимо!</b>",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if confirm == QMessageBox.StandardButton.Yes:
            try:
                SeatModel.delete_hall_seats(hall_id)
                QMessageBox.information(self, "Успех", "Места очищены")
                self.refresh_seats_table(hall_id)
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось очистить места: {str(e)}")

    def manage_row_prices(self):
        """Управление ценами по рядам"""
        hall_id = self.hall_combo.currentData()
        if not hall_id:
            QMessageBox.warning(self, "Внимание", "Выберите зал")
            return

        # Получаем текущие ряды
        rows_summary = SeatModel.get_rows_summary(hall_id)
        if not rows_summary:
            QMessageBox.information(self, "Информация", "В зале нет мест для настройки цен")
            return

        dialog = QDialog(self)
        dialog.setWindowTitle("Управление ценами по рядам")
        dialog.setFixedWidth(500)

        layout = QVBoxLayout(dialog)

        # Таблица цен
        table = QTableWidget()
        table.setColumnCount(2)
        table.setHorizontalHeaderLabels(["Номер ряда", "Цена за место (руб.)"])
        table.setRowCount(len(rows_summary))

        for i, (row_number, seats_count, min_price, max_price) in enumerate(rows_summary):
            # Номер ряда
            row_item = QTableWidgetItem(str(row_number))
            row_item.setFlags(row_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            table.setItem(i, 0, row_item)

            # Цена (используем максимальную цену если есть различия)
            price_item = QTableWidgetItem(str(max_price))
            table.setItem(i, 1, price_item)

        layout.addWidget(table)

        # Кнопки
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(lambda: self.apply_row_prices(hall_id, table, dialog))
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)

        dialog.exec()

    def apply_row_prices(self, hall_id, table, dialog):
        """Применить новые цены для рядов"""
        try:
            row_prices = {}
            for row in range(table.rowCount()):
                row_number = int(table.item(row, 0).text())
                price = float(table.item(row, 1).text())
                row_prices[row_number] = price

            SeatModel.update_row_prices(hall_id, row_prices)
            QMessageBox.information(self, "Успех", "Цены успешно обновлены")
            self.refresh_seats_table(hall_id)
            dialog.accept()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось обновить цены: {str(e)}")


# Диалоги
class HallDialog(QDialog):
    def __init__(self, parent=None, hall_data=None):
        super().__init__(parent)
        self.setWindowTitle("Добавление зала" if not hall_data else "Редактирование зала")
        self.setFixedWidth(450)

        layout = QFormLayout(self)
        layout.setSpacing(15)

        # Номер зала
        self.number_input = QSpinBox()
        self.number_input.setRange(1, 100)
        self.number_input.setValue(1)
        layout.addRow("Номер зала*:", self.number_input)

        # Название зала - комбобокс с возможностью ввода
        self.name_combo = QComboBox()
        self.name_combo.setEditable(True)
        hall_names = HallModel.get_hall_names()
        for name in hall_names:
            self.name_combo.addItem(name)
        self.name_combo.setCurrentText("")
        layout.addRow("Название зала*:", self.name_combo)

        # Тип зала - комбобокс
        self.type_combo = QComboBox()
        hall_types = HallModel.get_hall_types()
        for hall_type in hall_types:
            self.type_combo.addItem(hall_type)
        layout.addRow("Тип зала*:", self.type_combo)

        # Доплата за зал
        self.extra_price_input = QDoubleSpinBox()
        self.extra_price_input.setRange(0, 1000)
        self.extra_price_input.setSuffix(" руб.")
        self.extra_price_input.setValue(0)
        self.extra_price_input.setSingleStep(50)
        layout.addRow("Доплата за зал:", self.extra_price_input)

        # Заполняем данные если редактирование
        if hall_data:
            self.number_input.setValue(hall_data[1])
            self.name_combo.setCurrentText(hall_data[2])
            self.type_combo.setCurrentText(hall_data[3])
            self.extra_price_input.setValue(float(hall_data[4]))

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.validate_and_accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

    def validate_and_accept(self):
        """Валидация перед принятием"""
        hall_name = self.name_combo.currentText().strip()
        hall_type = self.type_combo.currentText().strip()

        # Проверка на пустые поля
        if not hall_name:
            QMessageBox.warning(self, "Ошибка", "Введите название зала")
            return

        if not hall_type:
            QMessageBox.warning(self, "Ошибка", "Выберите тип зала")
            return

        # Проверка на специальные символы в названии
        if any(char in hall_name for char in ['\\', '/', ':', '*', '?', '"', '<', '>', '|']):
            QMessageBox.warning(self, "Ошибка", "Название зала содержит недопустимые символы")
            return

        self.accept()

    def get_hall_data(self):
        """Получить данные формы"""
        return {
            'number': self.number_input.value(),
            'name': self.name_combo.currentText().strip(),
            'type': self.type_combo.currentText().strip(),
            'extra_price': self.extra_price_input.value()
        }


class BulkSeatsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Добавление мест с настройкой цен по рядам")
        self.setFixedWidth(600)
        self.setMinimumHeight(400)

        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        # Информация
        info_label = QLabel(
            "Настройте ряды мест. Для каждого ряда укажите количество мест и дополнительную цену.\n"
            "Например: VIP ряды могут стоить дороже."
        )
        info_label.setWordWrap(True)
        info_label.setStyleSheet("color: #AAAAAA; font-size: 13px;")
        layout.addWidget(info_label)

        # Таблица настройки рядов
        self.rows_table = QTableWidget()
        self.rows_table.setColumnCount(3)
        self.rows_table.setHorizontalHeaderLabels(["Номер ряда", "Количество мест", "Доп. цена (руб.)"])
        self.rows_table.horizontalHeader().setStretchLastSection(True)

        # Устанавливаем начальные данные (5 рядов по 10 мест)
        self.rows_table.setRowCount(5)
        for row in range(5):
            # Номер ряда
            row_item = QTableWidgetItem(str(row + 1))
            row_item.setFlags(row_item.flags() & ~Qt.ItemFlag.ItemIsEditable)  # Не редактируемый
            self.rows_table.setItem(row, 0, row_item)

            # Количество мест
            seats_item = QTableWidgetItem("10")
            self.rows_table.setItem(row, 1, seats_item)

            # Цена
            price_item = QTableWidgetItem("0")
            self.rows_table.setItem(row, 2, price_item)

        layout.addWidget(self.rows_table)

        # Кнопки управления таблицей
        table_buttons = QHBoxLayout()

        btn_add_row = QPushButton("➕ Добавить ряд")
        btn_add_row.clicked.connect(self.add_row)
        table_buttons.addWidget(btn_add_row)

        btn_remove_row = QPushButton("➖ Удалить ряд")
        btn_remove_row.clicked.connect(self.remove_row)
        table_buttons.addWidget(btn_remove_row)

        table_buttons.addStretch()
        layout.addLayout(table_buttons)

        # Кнопки диалога
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.validate_and_accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def add_row(self):
        """Добавить новый ряд"""
        row_count = self.rows_table.rowCount()
        self.rows_table.insertRow(row_count)

        # Номер ряда (автоматически)
        row_item = QTableWidgetItem(str(row_count + 1))
        row_item.setFlags(row_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        self.rows_table.setItem(row_count, 0, row_item)

        # Количество мест (по умолчанию 10)
        seats_item = QTableWidgetItem("10")
        self.rows_table.setItem(row_count, 1, seats_item)

        # Цена (по умолчанию 0)
        price_item = QTableWidgetItem("0")
        self.rows_table.setItem(row_count, 2, price_item)

    def remove_row(self):
        """Удалить последний ряд"""
        row_count = self.rows_table.rowCount()
        if row_count > 1:  # Минимум 1 ряд
            self.rows_table.removeRow(row_count - 1)

    def validate_and_accept(self):
        """Валидация данных"""
        for row in range(self.rows_table.rowCount()):
            seats_text = self.rows_table.item(row, 1).text()
            price_text = self.rows_table.item(row, 2).text()

            # Проверка количества мест
            try:
                seats = int(seats_text)
                if seats <= 0 or seats > 50:
                    QMessageBox.warning(self, "Ошибка", f"Количество мест в ряду {row + 1} должно быть от 1 до 50")
                    return
            except ValueError:
                QMessageBox.warning(self, "Ошибка", f"Некорректное количество мест в ряду {row + 1}")
                return

            # Проверка цены
            try:
                price = float(price_text)
                if price < 0 or price > 1000:
                    QMessageBox.warning(self, "Ошибка", f"Цена в ряду {row + 1} должна быть от 0 до 1000")
                    return
            except ValueError:
                QMessageBox.warning(self, "Ошибка", f"Некорректная цена в ряду {row + 1}")
                return

        self.accept()

    def get_rows_config(self):
        """Получить конфигурацию рядов"""
        config = []
        for row in range(self.rows_table.rowCount()):
            row_number = int(self.rows_table.item(row, 0).text())
            seats_count = int(self.rows_table.item(row, 1).text())
            price = float(self.rows_table.item(row, 2).text())

            config.append({
                'row': row_number,
                'seats': seats_count,
                'price': price
            })
        return config