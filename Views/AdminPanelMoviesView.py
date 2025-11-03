from PyQt6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QPushButton, QHBoxLayout,
    QTableView, QSizePolicy, QMessageBox, QSpacerItem, QDialog,
    QLineEdit, QFormLayout, QDialogButtonBox, QFileDialog, QTextEdit,
    QDoubleSpinBox, QListWidget, QComboBox, QTabWidget, QTableWidget,
    QTableWidgetItem, QHeaderView, QAbstractItemView, QListWidgetItem, QScrollArea
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap

from Models.LogModel import LogModel
from core.database import datagrid_model, query, image_to_binary
from Models.MovieModel import MovieModel


class AdminPanelMoviesView(QWidget):
    def __init__(self, go_back=None, user_id=None):
        super().__init__()
        self.go_back = go_back
        self.user_id = user_id

        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 30, 40, 30)
        layout.setSpacing(25)

        # Заголовок
        header = QHBoxLayout()
        title = QLabel("🎥 Управление фильмами")
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

        # Поиск
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Поиск фильмов...")
        self.search_input.textChanged.connect(self.on_search)
        layout.addWidget(self.search_input)

        # Таблица
        self.refresh_table()

        self.view = QTableView()
        self.view.setModel(self.model)
        self.view.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self.view.setSelectionMode(QTableView.SelectionMode.SingleSelection)
        self.view.setAlternatingRowColors(True)

        layout.addWidget(self.view, stretch=1)

        # Кнопки
        btns = QHBoxLayout()
        btns.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Policy.Expanding))

        self.btn_add = QPushButton("➕ Добавить фильм")
        self.btn_add.clicked.connect(self.add_movie)
        btns.addWidget(self.btn_add)

        self.btn_edit = QPushButton("✏️ Редактировать")
        self.btn_edit.clicked.connect(self.edit_movie)
        btns.addWidget(self.btn_edit)

        self.btn_delete = QPushButton("🗑 Удалить")
        self.btn_delete.setObjectName("LogoutButton")
        self.btn_delete.clicked.connect(self.delete_movie)
        btns.addWidget(self.btn_delete)

        self.btn_refresh = QPushButton("🔄 Обновить")
        self.btn_refresh.clicked.connect(self.refresh_table)
        btns.addWidget(self.btn_refresh)

        btns.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Policy.Expanding))
        layout.addLayout(btns)

    def refresh_table(self):
        self.model = datagrid_model(
            "SELECT movie_id, title, base_price, rating, created_at FROM movies ORDER BY created_at DESC"
        )

        if hasattr(self, 'view'):
            self.view.setModel(self.model)

        for row in range(self.model.rowCount()):
            for col in range(self.model.columnCount()):
                item = self.model.item(row, col)
                if item:
                    item.setEditable(False)

    def on_search(self, text):
        if len(text.strip()) >= 2:
            self.model = datagrid_model(
                "SELECT movie_id, title, base_price, rating, created_at FROM movies WHERE title ILIKE %s ORDER BY created_at DESC",
                (f"%{text.strip()}%",)
            )
            self.view.setModel(self.model)
        elif len(text.strip()) == 0:
            self.refresh_table()

    def get_selected_movie(self):
        selection = self.view.selectionModel().selectedRows()
        if not selection:
            return None

        row = selection[0].row()
        return {
            'movie_id': self.model.item(row, 0).text(),
            'title': self.model.item(row, 1).text()
        }

    def add_movie(self):
        """Добавить фильм"""
        dialog = MovieDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            try:
                title = dialog.title_input.text().strip()
                description = dialog.description_input.toPlainText().strip()
                price = dialog.price_input.value()
                photo_path = dialog.photo_path

                if not title or not description:
                    QMessageBox.warning(self, "Ошибка", "Заполните название и описание")
                    return

                if not photo_path:
                    QMessageBox.warning(self, "Ошибка", "Выберите постер фильма")
                    return

                # Создаём фильм
                photo_binary = image_to_binary(photo_path)
                sql = """
                    INSERT INTO movies (title, description, movie_image, base_price, rating)
                    VALUES (%s, %s, %s, %s, 0.0)
                    RETURNING movie_id
                """
                result = query(sql, (title, description, photo_binary, price))
                movie_id = result[0][0]

                LogModel.log_movie_action(
                    self.user_id,
                    "MOVIE_ADD",
                    movie_id,
                    title,
                    is_admin=True
                )

                # Добавляем жанры
                for genre_id in dialog.get_selected_genres():
                    query("INSERT INTO movie_genre (movie_id, genre_id) VALUES (%s, %s)",
                          (movie_id, genre_id))

                # Добавляем режиссёров
                for director_id in dialog.get_selected_directors():
                    query("INSERT INTO movie_director (movie_id, director_id) VALUES (%s, %s)",
                          (movie_id, director_id))

                # Добавляем актёров с ролями
                for actor_data in dialog.get_actors_with_roles():
                    query("INSERT INTO movie_actor (movie_id, actor_id, role) VALUES (%s, %s, %s)",
                          (movie_id, actor_data['actor_id'], actor_data['role']))

                QMessageBox.information(self, "Успех", f"Фильм '{title}' добавлен")
                self.refresh_table()
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось добавить фильм:\n{e}")

    def edit_movie(self):
        """Редактировать фильм"""
        movie = self.get_selected_movie()
        if not movie:
            QMessageBox.warning(self, "Внимание", "Выберите фильм")
            return

        dialog = MovieDialog(self, movie['movie_id'])

        if dialog.exec() == QDialog.DialogCode.Accepted:
            try:
                title = dialog.title_input.text().strip()
                description = dialog.description_input.toPlainText().strip()
                price = dialog.price_input.value()
                photo_path = dialog.photo_path

                if not title or not description:
                    QMessageBox.warning(self, "Ошибка", "Заполните название и описание")
                    return

                # Обновляем основную информацию
                if photo_path:
                    photo_binary = image_to_binary(photo_path)
                    sql = """
                        UPDATE movies 
                        SET title = %s, description = %s, movie_image = %s, 
                            base_price = %s, updated_at = CURRENT_TIMESTAMP
                        WHERE movie_id = %s
                    """
                    query(sql, (title, description, photo_binary, price, movie['movie_id']))
                else:
                    sql = """
                        UPDATE movies 
                        SET title = %s, description = %s, base_price = %s, 
                            updated_at = CURRENT_TIMESTAMP
                        WHERE movie_id = %s
                    """
                    query(sql, (title, description, price, movie['movie_id']))

                # Обновляем жанры
                query("DELETE FROM movie_genre WHERE movie_id = %s", (movie['movie_id'],))
                for genre_id in dialog.get_selected_genres():
                    query("INSERT INTO movie_genre (movie_id, genre_id) VALUES (%s, %s)",
                          (movie['movie_id'], genre_id))

                # Обновляем режиссёров
                query("DELETE FROM movie_director WHERE movie_id = %s", (movie['movie_id'],))
                for director_id in dialog.get_selected_directors():
                    query("INSERT INTO movie_director (movie_id, director_id) VALUES (%s, %s)",
                          (movie['movie_id'], director_id))

                # Обновляем актёров
                query("DELETE FROM movie_actor WHERE movie_id = %s", (movie['movie_id'],))
                for actor_data in dialog.get_actors_with_roles():
                    query("INSERT INTO movie_actor (movie_id, actor_id, role) VALUES (%s, %s, %s)",
                          (movie['movie_id'], actor_data['actor_id'], actor_data['role']))

                QMessageBox.information(self, "Успех", "Фильм обновлён")
                self.refresh_table()
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", str(e))

    def delete_movie(self):
        """Удалить фильм"""
        movie = self.get_selected_movie()
        if not movie:
            return

        confirm = QMessageBox.question(
            self, "Подтверждение",
            f"Удалить фильм '<b>{movie['title']}</b>'?<br><br>⚠️ <b>Это действие необратимо!</b>",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if confirm == QMessageBox.StandardButton.Yes:
            try:
                # Логируем перед удалением
                LogModel.log_movie_action(
                    self.user_id,
                    "MOVIE_DELETE",
                    movie['movie_id'],
                    movie['title'],
                    is_admin=True
                )

                query("DELETE FROM movies WHERE movie_id = %s", (movie['movie_id'],))
                QMessageBox.information(self, "Успех", "Фильм удалён")
                self.refresh_table()

            except Exception as e:
                LogModel.log_error(self.user_id, "MOVIE_DELETE", str(e), movie['movie_id'])
                QMessageBox.critical(self, "Ошибка", str(e))


class MovieDialog(QDialog):
    def __init__(self, parent=None, movie_id=None):
        super().__init__(parent)
        self.photo_path = None
        self.movie_id = movie_id
        self.setWindowTitle("Редактирование фильма" if movie_id else "Добавление фильма")
        self.resize(900, 650)

        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(15, 15, 15, 15)

        # Заголовок
        title_label = QLabel("Редактирование фильма" if movie_id else "Добавление нового фильма")
        title_label.setObjectName("TitleLabel")
        main_layout.addWidget(title_label)

        # Создаём вкладки с прокруткой
        self.tabs = QTabWidget()

        # Вкладка 1: Основная информация
        self.tab_basic = self.create_basic_tab()
        self.tabs.addTab(self.tab_basic, "📋 Основная информация")

        # Вкладка 2: Жанры
        self.tab_genres = self.create_genres_tab()
        self.tabs.addTab(self.tab_genres, "🎭 Жанры")

        # Вкладка 3: Режиссёры
        self.tab_directors = self.create_directors_tab()
        self.tabs.addTab(self.tab_directors, "🎬 Режиссёры")

        # Вкладка 4: Актёры
        self.tab_actors = self.create_actors_tab()
        self.tabs.addTab(self.tab_actors, "🎭 Актёры")

        main_layout.addWidget(self.tabs)

        # Кнопки
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        main_layout.addWidget(buttons)

        # Если редактирование - загружаем данные
        if movie_id:
            self.load_movie_data()

    def create_basic_tab(self):
        """Вкладка с основной информацией"""
        # Контейнер для прокрутки
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        widget = QWidget()
        layout = QFormLayout(widget)
        layout.setSpacing(15)
        layout.setContentsMargins(10, 10, 10, 10)

        # Название
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Введите название фильма")
        layout.addRow("Название:", self.title_input)

        # Описание
        self.description_input = QTextEdit()
        self.description_input.setMinimumHeight(100)
        self.description_input.setMaximumHeight(150)
        self.description_input.setPlaceholderText("Введите описание фильма")
        layout.addRow("Описание:", self.description_input)

        # Цена
        self.price_input = QDoubleSpinBox()
        self.price_input.setRange(0, 10000)
        self.price_input.setValue(300)
        self.price_input.setSuffix(" ₽")
        layout.addRow("Базовая цена:", self.price_input)

        # Постер
        photo_layout = QHBoxLayout()
        self.photo_label = QLabel("Постер не выбран")
        self.btn_choose_photo = QPushButton("📁 Выбрать постер")
        self.btn_choose_photo.clicked.connect(self.choose_photo)
        photo_layout.addWidget(self.photo_label, stretch=1)
        photo_layout.addWidget(self.btn_choose_photo)
        layout.addRow("Постер:", photo_layout)

        # Превью постера
        self.photo_preview = QLabel()
        self.photo_preview.setFixedSize(200, 280)
        self.photo_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.photo_preview.setStyleSheet("""
            QLabel {
                border: 2px dashed #35383D;
                border-radius: 8px;
                background-color: #1C1E22;
                color: #666;
            }
        """)
        self.photo_preview.setText("Превью постера")
        layout.addRow("Превью:", self.photo_preview)

        scroll.setWidget(widget)
        return scroll

    def create_genres_tab(self):
        """Вкладка с жанрами"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)

        info = QLabel("Выберите один или несколько жанров для фильма:")
        info.setStyleSheet("color: #AAAAAA; font-size: 13px;")
        layout.addWidget(info)

        self.genre_list = QListWidget()
        self.genre_list.setSelectionMode(QListWidget.SelectionMode.MultiSelection)

        try:
            genres = query("SELECT genre_id, name FROM genres ORDER BY name")
            if genres:
                for genre_id, genre_name in genres:
                    item = QListWidgetItem(genre_name)
                    item.setData(Qt.ItemDataRole.UserRole, genre_id)
                    self.genre_list.addItem(item)
        except Exception as e:
            print(f"Ошибка загрузки жанров: {e}")

        layout.addWidget(self.genre_list)

        return widget

    def create_directors_tab(self):
        """Вкладка с режиссёрами"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)

        info = QLabel("Выберите режиссёра (режиссёров) фильма:")
        info.setStyleSheet("color: #AAAAAA; font-size: 13px;")
        layout.addWidget(info)

        self.director_list = QListWidget()
        self.director_list.setSelectionMode(QListWidget.SelectionMode.MultiSelection)

        try:
            directors = query("SELECT director_id, fullname FROM director ORDER BY fullname")
            if directors:
                for director_id, fullname in directors:
                    item = QListWidgetItem(fullname)
                    item.setData(Qt.ItemDataRole.UserRole, director_id)
                    self.director_list.addItem(item)
        except Exception as e:
            print(f"Ошибка загрузки режиссёров: {e}")

        layout.addWidget(self.director_list)

        return widget

    def create_actors_tab(self):
        """Вкладка с актёрами"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)

        info = QLabel("Добавьте актёров и их роли в фильме:")
        info.setStyleSheet("color: #AAAAAA; font-size: 13px;")
        layout.addWidget(info)

        # Таблица актёров с ролями
        self.actors_table = QTableWidget()
        self.actors_table.setColumnCount(3)
        self.actors_table.setHorizontalHeaderLabels(["Актёр", "Роль в фильме", "Действие"])

        # Автоматическое растягивание колонок
        header = self.actors_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)

        # Автоподгон высоты строк
        self.actors_table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)

        self.actors_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.actors_table.setAlternatingRowColors(True)

        layout.addWidget(self.actors_table)

        # Кнопка добавления актёра
        btn_add_actor = QPushButton("➕ Добавить актёра")
        btn_add_actor.clicked.connect(self.add_actor_row)
        layout.addWidget(btn_add_actor)

        return widget

    def add_actor_row(self):
        """Добавить строку для выбора актёра"""
        row = self.actors_table.rowCount()
        self.actors_table.insertRow(row)

        # ComboBox с актёрами
        actor_combo = QComboBox()
        try:
            actors = query("SELECT actor_id, fullname FROM actor ORDER BY fullname")
            if actors:
                for actor_id, fullname in actors:
                    actor_combo.addItem(fullname, actor_id)
        except Exception as e:
            print(f"Ошибка загрузки актёров: {e}")

        self.actors_table.setCellWidget(row, 0, actor_combo)

        # Поле для роли
        role_input = QLineEdit()
        role_input.setPlaceholderText("Роль персонажа...")
        self.actors_table.setCellWidget(row, 1, role_input)

        # Кнопка удаления с ТЕКСТОМ
        btn_remove = QPushButton("Удалить")
        btn_remove.setFixedSize(90, 35)
        btn_remove.setObjectName("LogoutButton")
        btn_remove.clicked.connect(lambda: self.remove_actor_row(row))
        self.actors_table.setCellWidget(row, 2, btn_remove)

        # Обновляем размеры
        self.actors_table.resizeRowsToContents()

    def remove_actor_row(self, row):
        """Удалить строку актёра"""
        # Находим правильную строку по виджету кнопки
        sender_btn = self.sender()
        for r in range(self.actors_table.rowCount()):
            if self.actors_table.cellWidget(r, 2) == sender_btn:
                self.actors_table.removeRow(r)
                break

        # Обновляем размеры после удаления
        self.actors_table.resizeRowsToContents()

    def choose_photo(self):
        """Выбрать постер"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Выберите постер", "",
            "Images (*.png *.jpg *.jpeg *.bmp)"
        )
        if file_path:
            self.photo_path = file_path
            self.photo_label.setText(file_path.split('/')[-1])
            self.photo_label.setStyleSheet("color: #00A8E8; font-weight: 600;")

            pixmap = QPixmap(file_path)
            if not pixmap.isNull():
                scaled_pixmap = pixmap.scaled(
                    200, 280,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
                self.photo_preview.setPixmap(scaled_pixmap)


            self.photo_preview.setStyleSheet("""
                QLabel {
                    border: 2px solid #00A8E8;
                    border-radius: 8px;
                    background-color: #16181C;
                }
            """)

    def get_selected_genres(self):
        """Получить ID выбранных жанров"""
        selected = []
        for item in self.genre_list.selectedItems():
            genre_id = item.data(Qt.ItemDataRole.UserRole)
            if genre_id is not None:
                selected.append(genre_id)
        return selected

    def get_selected_directors(self):
        """Получить ID выбранных режиссёров"""
        selected = []
        for item in self.director_list.selectedItems():
            director_id = item.data(Qt.ItemDataRole.UserRole)
            if director_id is not None:
                selected.append(director_id)
        return selected

    def get_actors_with_roles(self):
        """Получить список актёров с ролями"""
        actors = []
        for row in range(self.actors_table.rowCount()):
            actor_combo = self.actors_table.cellWidget(row, 0)
            role_input = self.actors_table.cellWidget(row, 1)

            if actor_combo and role_input:
                actor_id = actor_combo.currentData()
                role = role_input.text().strip()
                if actor_id is not None:
                    actors.append({'actor_id': actor_id, 'role': role})

        return actors

    def load_movie_data(self):
        """Загрузить данные фильма для редактирования"""
        if not self.movie_id:
            return

        try:
            # Основная информация
            movie_data = query(
                "SELECT title, description, base_price FROM movies WHERE movie_id = %s",
                (self.movie_id,)
            )
            if movie_data:
                self.title_input.setText(movie_data[0][0])
                self.description_input.setPlainText(movie_data[0][1])
                self.price_input.setValue(movie_data[0][2])

            # Загрузить жанры
            genre_ids = query(
                "SELECT genre_id FROM movie_genre WHERE movie_id = %s",
                (self.movie_id,)
            )
            selected_genres = [g[0] for g in genre_ids] if genre_ids else []

            for i in range(self.genre_list.count()):
                item = self.genre_list.item(i)
                if item and item.data(Qt.ItemDataRole.UserRole) in selected_genres:
                    item.setSelected(True)

            # Загрузить режиссёров
            director_ids = query(
                "SELECT director_id FROM movie_director WHERE movie_id = %s",
                (self.movie_id,)
            )
            selected_directors = [d[0] for d in director_ids] if director_ids else []

            for i in range(self.director_list.count()):
                item = self.director_list.item(i)
                if item and item.data(Qt.ItemDataRole.UserRole) in selected_directors:
                    item.setSelected(True)

            # Загрузить актёров
            actors_data = query(
                "SELECT actor_id, role FROM movie_actor WHERE movie_id = %s",
                (self.movie_id,)
            )

            if actors_data:
                for actor_id, role in actors_data:
                    self.add_actor_row()
                    row = self.actors_table.rowCount() - 1

                    actor_combo = self.actors_table.cellWidget(row, 0)
                    role_input = self.actors_table.cellWidget(row, 1)

                    if actor_combo:
                        for i in range(actor_combo.count()):
                            if actor_combo.itemData(i) == actor_id:
                                actor_combo.setCurrentIndex(i)
                                break

                    if role and role_input:
                        role_input.setText(role)
        except Exception as e:
            print(f"Ошибка загрузки данных фильма: {e}")
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить данные фильма:\n{e}")

    def check_duplicate_actors(self):
        """Проверить наличие дубликатов актёров"""
        actor_ids = []
        duplicates = []

        for row in range(self.actors_table.rowCount()):
            actor_combo = self.actors_table.cellWidget(row, 0)
            if actor_combo:
                actor_id = actor_combo.currentData()
                actor_name = actor_combo.currentText()

                if actor_id in actor_ids:
                    duplicates.append(actor_name)
                else:
                    actor_ids.append(actor_id)

        return duplicates

    def accept(self):
        """Валидация перед сохранением"""
        # Проверка на дубликаты актёров
        duplicates = self.check_duplicate_actors()
        if duplicates:
            QMessageBox.warning(
                self,
                "⚠️ Дубликаты актёров",
                f"Следующие актёры добавлены несколько раз:\n\n"
                f"• {chr(10).join(set(duplicates))}\n\n"
                f"Один актёр не может играть несколько ролей в одном фильме.\n"
                f"Удалите дубликаты перед сохранением."
            )
            return  # Не закрываем диалог

        # Если всё ок - вызываем стандартный accept
        super().accept()