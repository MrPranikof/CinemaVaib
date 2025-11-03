from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableView, QSizePolicy, QMessageBox, QSpacerItem,
    QGroupBox, QComboBox, QSpinBox, QProgressBar, QFileDialog,
    QScrollArea  # Добавляем QScrollArea
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from core.database import datagrid_model
from Models.ReportsModel import ReportsModel
import os


class ReportGenerationThread(QThread):
    """Поток для генерации отчетов"""
    finished = pyqtSignal(str, str)  # filepath, report_name
    error = pyqtSignal(str)

    def __init__(self, report_type, days=30):
        super().__init__()
        self.report_type = report_type
        self.days = days

    def run(self):
        try:
            if self.report_type == "sales":
                filepath = ReportsModel.export_daily_sales_report(self.days)
                report_name = "Отчет по продажам"
            elif self.report_type == "movies":
                filepath = ReportsModel.export_movies_popularity_report()
                report_name = "Отчет по популярности фильмов"
            elif self.report_type == "halls":
                filepath = ReportsModel.export_halls_utilization_report(self.days)
                report_name = "Отчет по загрузке залов"
            elif self.report_type == "users":
                filepath = ReportsModel.export_users_activity_report(self.days)
                report_name = "Отчет по активности пользователей"
            elif self.report_type == "financial":
                filepath = ReportsModel.export_financial_summary_report(self.days)
                report_name = "Финансовый отчет"
            else:
                self.error.emit("Неизвестный тип отчета")
                return

            if filepath:
                self.finished.emit(filepath, report_name)
            else:
                self.error.emit("Ошибка создания отчета")

        except Exception as e:
            self.error.emit(str(e))


class AdminPanelReportsView(QWidget):
    def __init__(self, user_id, go_back=None):
        super().__init__()
        self.user_id = user_id
        self.go_back = go_back
        self.current_report_thread = None

        self.setup_ui()

    def setup_ui(self):
        # Главный layout для всего виджета
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Создаем область прокрутки
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        # Контейнер для содержимого
        content_widget = QWidget()
        layout = QVBoxLayout(content_widget)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        # Заголовок
        header = QHBoxLayout()
        title = QLabel("📊 Система отчетов")
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

        # Выбор периода
        self.create_period_section(layout)

        # Виды отчетов
        self.create_reports_section(layout)

        # Прогресс бар
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        # Статус
        self.status_label = QLabel("Выберите отчет для генерации")
        self.status_label.setStyleSheet("""
            QLabel {
                color: #00A8E8;
                font-size: 12px;
                padding: 8px;
                background-color: #1C1E22;
                border-radius: 5px;
                border-left: 3px solid #00A8E8;
            }
        """)
        layout.addWidget(self.status_label)

        layout.addStretch()

        # Устанавливаем контейнер в область прокрутки
        scroll_area.setWidget(content_widget)

        # Добавляем область прокрутки в главный layout
        main_layout.addWidget(scroll_area)

        # Сохраняем ссылку на content_widget для update_realtime_stats
        self.content_widget = content_widget

    def create_period_section(self, parent_layout):
        """Создать секцию выбора периода"""
        period_group = QGroupBox("📅 Период отчетов")
        period_group.setMinimumHeight(80)  # Минимальная высота
        period_layout = QHBoxLayout(period_group)

        period_layout.addWidget(QLabel("Период:"))

        self.days_spinbox = QSpinBox()
        self.days_spinbox.setRange(1, 365)
        self.days_spinbox.setValue(30)
        self.days_spinbox.setSuffix(" дней")
        self.days_spinbox.setFixedWidth(100)
        period_layout.addWidget(self.days_spinbox)

        period_layout.addStretch()
        parent_layout.addWidget(period_group)

    def create_reports_section(self, parent_layout):
        """Создать секцию с видами отчетов"""
        reports_group = QGroupBox("📈 Доступные отчеты")
        reports_group.setMinimumHeight(350)  # Увеличиваем минимальную высоту для всех кнопок
        reports_layout = QVBoxLayout(reports_group)
        reports_layout.setSpacing(10)  # Добавляем отступы между кнопками

        # Отчет по продажам
        sales_btn = QPushButton("💰 Ежедневные продажи")
        sales_btn.setFixedHeight(50)
        sales_btn.clicked.connect(lambda: self.generate_report("sales"))
        reports_layout.addWidget(sales_btn)

        # Отчет по фильмам
        movies_btn = QPushButton("🎬 Популярность фильмов")
        movies_btn.setFixedHeight(50)
        movies_btn.clicked.connect(lambda: self.generate_report("movies"))
        reports_layout.addWidget(movies_btn)

        # Отчет по залам
        halls_btn = QPushButton("🎭 Загрузка залов")
        halls_btn.setFixedHeight(50)
        halls_btn.clicked.connect(lambda: self.generate_report("halls"))
        reports_layout.addWidget(halls_btn)

        # Отчет по пользователям
        users_btn = QPushButton("👥 Активность пользователей")
        users_btn.setFixedHeight(50)
        users_btn.clicked.connect(lambda: self.generate_report("users"))
        reports_layout.addWidget(users_btn)

        # Финансовый отчет
        financial_btn = QPushButton("💵 Финансовый отчет")
        financial_btn.setFixedHeight(50)
        financial_btn.clicked.connect(lambda: self.generate_report("financial"))
        reports_layout.addWidget(financial_btn)

        parent_layout.addWidget(reports_group)

    def generate_report(self, report_type):
        """Генерация отчета"""
        if self.current_report_thread and self.current_report_thread.isRunning():
            QMessageBox.warning(self, "Внимание", "Дождитесь завершения текущей генерации отчета")
            return

        days = self.days_spinbox.value()

        # Показываем прогресс
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Бесконечный прогресс
        self.status_label.setText("🔄 Генерация отчета...")
        self.status_label.setStyleSheet("""
            QLabel {
                color: #FFA726;
                font-size: 12px;
                padding: 8px;
                background-color: #1C1E22;
                border-radius: 5px;
                border-left: 3px solid #FFA726;
            }
        """)

        # Запускаем в отдельном потоке
        self.current_report_thread = ReportGenerationThread(report_type, days)
        self.current_report_thread.finished.connect(self.on_report_generated)
        self.current_report_thread.error.connect(self.on_report_error)
        self.current_report_thread.start()

    def on_report_generated(self, filepath, report_name):
        """Обработчик успешной генерации отчета"""
        self.progress_bar.setVisible(False)

        # Показываем успешный статус
        self.status_label.setText(f"✅ Отчет '{report_name}' успешно сгенерирован")
        self.status_label.setStyleSheet("""
            QLabel {
                color: #55C78C;
                font-size: 12px;
                padding: 8px;
                background-color: #1C1E22;
                border-radius: 5px;
                border-left: 3px solid #55C78C;
            }
        """)

        # Предлагаем открыть или сохранить файл
        reply = QMessageBox.question(
            self,
            "Отчет готов",
            f"Отчет '{report_name}' успешно сгенерирован!\n\n"
            f"Хотите открыть файл или сохранить в другое место?",
            QMessageBox.StandardButton.Open |
            QMessageBox.StandardButton.Save |
            QMessageBox.StandardButton.Cancel
        )

        if reply == QMessageBox.StandardButton.Open:
            # Открываем файл
            os.startfile(filepath)  # Windows
        elif reply == QMessageBox.StandardButton.Save:
            # Предлагаем сохранить в другое место
            new_path, _ = QFileDialog.getSaveFileName(
                self,
                "Сохранить отчет",
                os.path.basename(filepath),
                "Excel Files (*.xlsx)"
            )
            if new_path:
                import shutil
                shutil.copy2(filepath, new_path)
                QMessageBox.information(self, "Успех", f"Отчет сохранен: {new_path}")

    def on_report_error(self, error_message):
        """Обработчик ошибки генерации отчета"""
        self.progress_bar.setVisible(False)

        self.status_label.setText(f"❌ Ошибка: {error_message}")
        self.status_label.setStyleSheet("""
            QLabel {
                color: #E63946;
                font-size: 12px;
                padding: 8px;
                background-color: #1C1E22;
                border-radius: 5px;
                border-left: 3px solid #E63946;
            }
        """)

        QMessageBox.critical(self, "Ошибка", f"Не удалось сгенерировать отчет:\n{error_message}")

    def closeEvent(self, event):
        """Обработчик закрытия окна"""
        if self.current_report_thread and self.current_report_thread.isRunning():
            self.current_report_thread.terminate()
            self.current_report_thread.wait()
        event.accept()

    def update_realtime_stats(self):
        """Обновить статистику в реальном времени"""
        try:
            stats = ReportsModel.get_realtime_stats()
            if stats:
                active_movies, upcoming_sessions, today_tickets, today_revenue, active_users = stats

                stats_text = (
                    f"🎬 Активных фильмов: <b>{active_movies}</b> | "
                    f"📅 Ближайших сеансов: <b>{upcoming_sessions}</b> | "
                    f"🎫 Билетов сегодня: <b>{today_tickets}</b> | "
                    f"💰 Выручка сегодня: <b>{today_revenue:,.0f} руб.</b> | "
                    f"👥 Активных пользователей: <b>{active_users}</b>"
                )

                # Создаем или обновляем виджет статистики
                if hasattr(self, 'realtime_stats_label'):
                    self.realtime_stats_label.setText(stats_text)
                else:
                    self.realtime_stats_label = QLabel(stats_text)
                    self.realtime_stats_label.setStyleSheet("""
                        QLabel {
                            color: #00A8E8;
                            font-size: 12px;
                            padding: 10px;
                            background-color: #1C1E22;
                            border-radius: 5px;
                            border: 1px solid #2A2C32;
                        }
                    """)
                    # Вставляем после заголовка
                    self.content_widget.layout().insertWidget(1, self.realtime_stats_label)

        except Exception as e:
            print(f"Ошибка обновления статистики: {e}")

    def showEvent(self, event):
        """Обработчик показа виджета"""
        super().showEvent(event)
        self.update_realtime_stats()