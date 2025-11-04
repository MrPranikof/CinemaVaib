import os
import tempfile
from reportlab.lib.pagesizes import A5  # Изменили A6 на A5
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib.colors import Color, black, white
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import ImageReader
from datetime import datetime
import qrcode
from io import BytesIO

# Импортируем ваши модели
from Models.LogModel import LogModel
from Models.TicketModel import TicketModel


class TicketPDFModel:

    @staticmethod
    def register_fonts():
        """Регистрация шрифтов для поддержки кириллицы"""
        try:
            if os.name == 'nt':  # Windows
                font_dir = "C:/Windows/Fonts/"
                if os.path.exists(font_dir + "arial.ttf"):
                    pdfmetrics.registerFont(TTFont('Arial', font_dir + 'arial.ttf'))
                    pdfmetrics.registerFont(TTFont('Arial-Bold', font_dir + 'arialbd.ttf'))
                    return True
                if os.path.exists(font_dir + "calibri.ttf"):
                    pdfmetrics.registerFont(TTFont('Arial', font_dir + 'calibri.ttf'))
                    pdfmetrics.registerFont(TTFont('Arial-Bold', font_dir + 'calibrib.ttf'))
                    return True
            return False
        except Exception as e:
            print(f"Ошибка при регистрации шрифтов: {e}")
            return False

    @staticmethod
    def generate_qr_code(data):
        """Генерация QR кода"""
        qr = qrcode.QRCode(
            version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=2
        )
        qr.add_data(data)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        return buffer

    @staticmethod
    def _draw_single_ticket_content(c, ticket_id, user_id, ticket_info, fonts_registered, page_info=""):
        page_width, page_height = A5

        # --- Настройки макета билета (центрируем на странице) ---
        ticket_width = 120 * mm
        left_margin = (page_width - ticket_width) / 2
        right_margin = left_margin + ticket_width

        # Настройка цветов и шрифтов
        primary_color = Color(0 / 255, 168 / 255, 232 / 255)
        accent_color = Color(31 / 255, 41 / 255, 55 / 255)
        text_color = black
        font_name = "Arial" if fonts_registered else "Helvetica"
        font_bold = "Arial-Bold" if fonts_registered else "Helvetica-Bold"

        # --- Отрисовка ---
        # Фон страницы
        c.setFillColor(Color(0.95, 0.95, 0.95))  # Слегка серый фон для контраста
        c.rect(0, 0, page_width, page_height, fill=1, stroke=0)

        # Белая подложка для самого билета
        c.setFillColor(white)
        # Рисуем тень для эффекта объема
        c.setFillColor(Color(0.8, 0.8, 0.8))
        c.rect(left_margin + 1 * mm, 15 * mm - 1 * mm, ticket_width, page_height - 30 * mm, fill=1, stroke=0)
        # Сам билет
        c.setFillColor(white)
        c.rect(left_margin, 15 * mm, ticket_width, page_height - 30 * mm, fill=1, stroke=0)

        # Шапка
        header_height = 30 * mm
        y_header_start = page_height - 15 * mm - header_height
        c.setFillColor(primary_color)
        c.rect(left_margin, y_header_start, ticket_width, header_height, fill=1, stroke=0)

        # Логотип
        c.setFillColor(white)
        logo_path = "images/headerLogo.png"
        try:
            if os.path.exists(logo_path):
                logo = ImageReader(logo_path)
                c.drawImage(logo, left_margin + 10 * mm, y_header_start + 5 * mm, width=40 * mm, height=20 * mm,
                            mask='auto', preserveAspectRatio=True)
            else:
                raise FileNotFoundError()
        except Exception:
            c.setFont(font_bold, 20)
            c.drawString(left_margin + 10 * mm, y_header_start + 10 * mm, "CINEMAVAIB")

        # Текст "ЭЛЕКТРОННЫЙ БИЛЕТ"
        c.setFont(font_bold, 9)
        c.drawRightString(right_margin - 10 * mm, y_header_start + 22 * mm, "ЭЛЕКТРОННЫЙ БИЛЕТ")

        # --- Основная информация ---
        y_position = y_header_start - 15 * mm
        content_margin = left_margin + 10 * mm

        # Фильм
        c.setFillColor(text_color)
        c.setFont(font_bold, 12)
        c.drawString(content_margin, y_position, "ФИЛЬМ:")
        c.setFont(font_name, 12)
        movie_title = str(ticket_info[1])
        c.drawString(content_margin, y_position - 7 * mm, movie_title)
        y_position -= 20 * mm

        # Зал
        c.setFont(font_bold, 11)
        c.drawString(content_margin, y_position, "ЗАЛ:")
        c.setFont(font_name, 11)
        hall_display = f"№{ticket_info[3]} - {ticket_info[2]}" if ticket_info[3] else str(ticket_info[2])
        c.drawString(content_margin + 15 * mm, y_position, hall_display)
        y_position -= 10 * mm

        # Дата и время
        c.setFont(font_bold, 11)
        c.drawString(content_margin, y_position, "ДАТА И ВРЕМЯ:")
        c.setFont(font_name, 11)
        session_time = ticket_info[4]
        time_str = session_time.strftime('%d.%m.%Y %H:%M') if not isinstance(session_time, str) else session_time
        c.drawString(content_margin + 35 * mm, y_position, time_str)
        y_position -= 10 * mm

        # Место и Стоимость в одну строку
        c.setFont(font_bold, 11)
        c.drawString(content_margin, y_position, "МЕСТО:")
        c.setFont(font_name, 11)
        c.drawString(content_margin + 20 * mm, y_position, f"Ряд {ticket_info[5]}, Место {ticket_info[6]}")

        c.setFont(font_bold, 11)
        c.drawString(content_margin + 60 * mm, y_position, "ЦЕНА:")
        c.setFont(font_name, 11)
        price = float(ticket_info[7]) if ticket_info[7] else 0.0
        c.drawString(content_margin + 75 * mm, y_position, f"{price:.0f} руб.")
        y_position -= 20 * mm

        # Номер билета
        c.setFillColor(Color(0.95, 0.95, 0.95))
        c.setStrokeColor(Color(0.85, 0.85, 0.85))
        c.rect(left_margin + 5 * mm, y_position - 7 * mm, ticket_width - 10 * mm, 12 * mm, fill=1, stroke=1)
        c.setFillColor(accent_color)
        c.setFont(font_bold, 14)
        c.drawCentredString(page_width / 2, y_position - 3 * mm, f"БИЛЕТ №{ticket_id}")

        # QR-код
        qr_size = 55 * mm
        qr_y = y_position - 15 * mm - qr_size
        qr_x = (page_width - qr_size) / 2
        try:
            qr_data = f"TICKET:{ticket_id}:USER:{user_id}:SESSION:{ticket_info[11]}"
            qr_image = ImageReader(TicketPDFModel.generate_qr_code(qr_data))
            c.drawImage(qr_image, qr_x, qr_y, width=qr_size, height=qr_size)
            c.setFillColor(text_color)
            c.setFont(font_name, 9)
            c.drawCentredString(page_width / 2, qr_y - 2 * mm, "Покажите этот QR-код на входе в кинозал")
        except Exception as e:
            print(f"Ошибка при генерации QR кода: {e}")

        # Нижний колонтитул страницы
        c.setFillColor(Color(0.5, 0.5, 0.5))
        c.setFont(font_name, 8)
        if page_info:
            c.drawCentredString(page_width / 2, 8 * mm, page_info)
        c.drawRightString(page_width - 10 * mm, 8 * mm, f"Сгенерировано: {datetime.now().strftime('%d.%m.%Y %H:%M')}")
        c.drawString(10 * mm, 8 * mm, "Приятного просмотра!")

    @staticmethod
    def generate_ticket_pdf(ticket_id, user_id):
        """Сгенерировать PDF одного билета на странице A5."""
        try:
            fonts_registered = TicketPDFModel.register_fonts()
            ticket_info = TicketModel.get_ticket_by_id(ticket_id)

            if not ticket_info: raise Exception("Билет не найден")
            if ticket_info[13] != user_id: raise Exception("Этот билет не принадлежит вам")

            temp_dir = tempfile.gettempdir()
            filename = f"ticket_{ticket_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            filepath = os.path.join(temp_dir, filename)

            c = canvas.Canvas(filepath, pagesize=A5)
            TicketPDFModel._draw_single_ticket_content(c, ticket_id, user_id, ticket_info, fonts_registered)
            c.save()

            LogModel.log_pdf_generation(user_id, ticket_id, True)
            return filepath
        except Exception as e:
            LogModel.log_pdf_generation(user_id, ticket_id, False, str(e))
            raise e

    @staticmethod
    def generate_multiple_tickets_pdf(ticket_ids, user_id):
        """Сгенерировать PDF с несколькими билетами, каждый на своей странице A5."""
        try:
            fonts_registered = TicketPDFModel.register_fonts()

            temp_dir = tempfile.gettempdir()
            filename = f"tickets_{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            filepath = os.path.join(temp_dir, filename)

            c = canvas.Canvas(filepath, pagesize=A5)

            valid_tickets = []
            for ticket_id in ticket_ids:
                ticket_info = TicketModel.get_ticket_by_id(ticket_id)
                if ticket_info and ticket_info[13] == user_id:
                    valid_tickets.append((ticket_id, ticket_info))

            if not valid_tickets:
                raise Exception("Не найдено действительных билетов для указанного пользователя.")

            total_pages = len(valid_tickets)
            for i, (ticket_id, ticket_info) in enumerate(valid_tickets):
                if i > 0: c.showPage()
                page_info = f"Страница {i + 1} из {total_pages}"
                TicketPDFModel._draw_single_ticket_content(c, ticket_id, user_id, ticket_info, fonts_registered,
                                                           page_info)

            c.save()
            LogModel.log_pdf_generation(user_id, [tid for tid, _ in valid_tickets], True)
            return filepath
        except Exception as e:
            LogModel.log_pdf_generation(user_id, ticket_ids, False, str(e))
            raise e