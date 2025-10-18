from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QCursor
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QStackedWidget
from ViewModels.MainViewModel import MainViewModel
from Views.ProfileView import ProfileView


class MainView(QWidget):
    def __init__(self):
        super().__init__()
        self.vm = MainViewModel()

        # Header
        self.header = QWidget()
        self.header.setObjectName("HeaderBar")

        h_header = QHBoxLayout(self.header)
        h_header.setContentsMargins(20,10,20,10)
        h_header.setSpacing(15)

        self.logo_label = QLabel()
        pix = QPixmap("images/headerLogo.png")
        pix = pix.scaledToHeight(38, Qt.TransformationMode.SmoothTransformation)
        self.logo_label.setPixmap(pix)
        self.logo_label.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.logo_label.setObjectName("HeaderLogo")
        self.logo_label.mousePressEvent = self.show_main_page

        self.btn_profile = QPushButton("👨‍💼\nПрофиль")
        self.btn_profile.setObjectName("HeaderButton")
        self.btn_profile.clicked.connect(self.show_profile_page)

        self.adminBtn = QPushButton(self)
        self.adminBtn.setText("Админ-панель")
        self.adminBtn.setVisible(False)

        h_header.addWidget(self.logo_label)
        h_header.addStretch()
        h_header.addWidget(self.btn_profile)
        h_header.addWidget(self.adminBtn)

        # Content
        self.stack = QStackedWidget()
        self.stack.setObjectName("ContentArea")

        # Main
        self.page_main = QWidget()
        v_main = QVBoxLayout(self.page_main)
        v_main.setAlignment(Qt.AlignmentFlag.AlignCenter)
        v_main.addWidget(QLabel("Главный контент 🍿"))

        self.page_profile = ProfileView("TEST", self.show_main_page)

        self.page_admin = QWidget()
        v_admin = QVBoxLayout(self.page_admin)
        v_admin.addWidget(QLabel("⚙️ Админ-панель (заготовка)"))

        self.stack.addWidget(self.page_main)
        self.stack.addWidget(self.page_profile)
        self.stack.addWidget(self.page_admin)
        # Footer
        self.footer = QWidget()
        self.footer.setObjectName("FooterBar")

        h_footer = QHBoxLayout(self.footer)
        h_footer.setContentsMargins(20, 8, 20, 8)
        h_footer.setSpacing(10)

        self.footer_text = QLabel("© 2025 CinemaVaib — Все права защищены, v0.1.1")
        self.footer_text.setObjectName("FooterText")
        h_footer.addStretch()
        h_footer.addWidget(self.footer_text)
        h_footer.addStretch()

        # Основной layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        main_layout.addWidget(self.header)
        main_layout.addWidget(self.stack, stretch=1)   # тянется
        main_layout.addWidget(self.footer)

    def set_user(self, login):
        self.current_login = login
        self.adminBtn.setVisible(self.vm.get_role_id(login) == 2)

        if isinstance(self.page_profile, ProfileView):
            self.page_profile.set_user(login)

    def show_main_page(self, event=None):
        self.stack.setCurrentWidget(self.page_main)

    def show_profile_page(self):
        self.stack.setCurrentWidget(self.page_profile)

    def show_admin_page(self):
        if self.adminBtn.isVisible():
            self.stack.setCurrentWidget(self.page_admin)