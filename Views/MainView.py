from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QCursor
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout
from ViewModels.MainViewModel import MainViewModel

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
        self.logo_label.mousePressEvent = self.go_home

        self.btn_profile = QPushButton("👨‍💼\nПрофиль")
        self.btn_profile.setObjectName("HeaderButton")

        self.adminBtn = QPushButton(self)
        self.adminBtn.setText("Админ-панель")
        self.adminBtn.setVisible(False)

        h_header.addWidget(self.logo_label)
        h_header.addStretch()
        h_header.addWidget(self.btn_profile)
        h_header.addWidget(self.adminBtn)

        # Content
        self.content = QWidget()
        self.content.setObjectName("ContentArea")

        v_content = QVBoxLayout(self.content)
        v_content.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.content_label = QLabel("Главный контент 🍿")
        self.content_label.setObjectName("MainLabel")
        v_content.addWidget(self.content_label)

        # Footer
        self.footer = QWidget()
        self.footer.setObjectName("FooterBar")

        h_footer = QHBoxLayout(self.footer)
        h_footer.setContentsMargins(20, 8, 20, 8)
        h_footer.setSpacing(10)

        self.footer_text = QLabel("© 2025 CinemaVaib — Все права защищены, v0.1.0")
        self.footer_text.setObjectName("FooterText")
        h_footer.addStretch()
        h_footer.addWidget(self.footer_text)
        h_footer.addStretch()

        # Основной layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        main_layout.addWidget(self.header)
        main_layout.addWidget(self.content, stretch=1)   # тянется
        main_layout.addWidget(self.footer)

    def set_user(self, login):
        if self.vm.get_role_id(login) == 2:
            self.adminBtn.setVisible(True)
        else:
            self.adminBtn.setVisible(False)

    def go_home(self, event):
        print("Переход на главную страницу")