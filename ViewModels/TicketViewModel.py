from PyQt6.QtCore import QObject, pyqtSignal
from Models.TicketPDFModel import TicketPDFModel
import os


class TicketViewModel(QObject):
    pdf_generated = pyqtSignal(str, str)
    pdf_generation_failed = pyqtSignal(str)

    def generate_ticket_pdf(self, ticket_id, user_id):
        """Сгенерировать PDF билета"""
        try:
            filepath = TicketPDFModel.generate_ticket_pdf(ticket_id, user_id)
            filename = os.path.basename(filepath)
            self.pdf_generated.emit(filepath, filename)
        except Exception as e:
            self.pdf_generation_failed.emit(str(e))

    def generate_multiple_tickets_pdf(self, ticket_ids, user_id):
        """Сгенерировать PDF с несколькими билетами"""
        try:
            filepath = TicketPDFModel.generate_multiple_tickets_pdf(ticket_ids, user_id)
            filename = os.path.basename(filepath)
            self.pdf_generated.emit(filepath, filename)
        except Exception as e:
            self.pdf_generation_failed.emit(str(e))