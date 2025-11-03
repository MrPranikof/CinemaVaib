from Models.LogModel import LogModel
from core.database import query

class TicketModel:
    @staticmethod
    def create_ticket(session_id, user_id, seat_id, discount_percent=0):
        """Создать билет"""
        sql = """
            INSERT INTO ticket (session_id, user_id, seat_id, percent_discount)
            VALUES (%s, %s, %s, %s)
            RETURNING ticket_id
        """
        result = query(sql, [session_id, user_id, seat_id, discount_percent])

        if result:
            ticket_id = result[0][0]
            # Логируем покупку
            LogModel.log_ticket_purchase(user_id, ticket_id, session_id, 1)
            return ticket_id
        return None

    @staticmethod
    def get_user_tickets(user_id):
        """Получить билеты пользователя"""
        sql = """
            SELECT t.ticket_id, m.title, h.hall_name, s.session_time,
                   st.row_number, st.seat_number, t.final_price,
                   t.purchase_date, t.final_price_discount
            FROM ticket t
            JOIN session s ON t.session_id = s.session_id
            JOIN movies m ON s.movie_id = m.movie_id
            JOIN hall h ON s.hall_id = h.hall_id
            JOIN seat st ON t.seat_id = st.seat_id
            WHERE t.user_id = %s
            ORDER BY s.session_time DESC
        """
        return query(sql, [user_id]) or []

    @staticmethod
    def get_available_seats(session_id):
        """Получить доступные места для сеанса"""
        try:
            sql = """
                SELECT s.seat_id, s.row_number, s.seat_number, s.seat_extra_price,
                       h.hall_name, h.hall_type
                FROM seat s
                JOIN hall h ON s.hall_id = h.hall_id
                JOIN session se ON se.hall_id = h.hall_id
                WHERE se.session_id = %s 
                AND s.seat_id NOT IN (
                    SELECT seat_id FROM ticket WHERE session_id = %s
                )
                ORDER BY s.row_number, s.seat_number
            """
            result = query(sql, [session_id, session_id]) or []

            return result
        except Exception as e:
            print(f"Ошибка в get_available_seats: {e}")
            return []

    @staticmethod
    def get_occupied_seats(session_id):
        """Получить занятые места для сеанса"""
        sql = """
            SELECT s.seat_id, s.row_number, s.seat_number
            FROM seat s
            JOIN ticket t ON s.seat_id = t.seat_id
            WHERE t.session_id = %s
            ORDER BY s.row_number, s.seat_number
        """
        return query(sql, [session_id]) or []

    @staticmethod
    def is_seat_available(session_id, seat_id):
        """Проверить доступность места"""
        sql = """
            SELECT COUNT(*) 
            FROM ticket 
            WHERE session_id = %s AND seat_id = %s
        """
        result = query(sql, [session_id, seat_id])
        return result[0][0] == 0 if result else True

    @staticmethod
    def get_ticket_by_id(ticket_id):
        """Получить билет по ID - ИСПРАВЛЕННАЯ ВЕРСИЯ"""
        try:
            sql = """
                SELECT 
                    t.ticket_id, 
                    m.title, 
                    h.hall_name, 
                    s.session_time,
                    st.row_number, 
                    st.seat_number, 
                    t.final_price,
                    t.final_price_discount, 
                    t.purchase_date,
                    m.movie_image, 
                    s.session_id, 
                    m.movie_id,
                    t.user_id  -- ДОБАВЛЕНО: user_id для логирования
                FROM ticket t
                JOIN session s ON t.session_id = s.session_id
                JOIN movies m ON s.movie_id = m.movie_id
                JOIN hall h ON s.hall_id = h.hall_id
                JOIN seat st ON t.seat_id = st.seat_id
                WHERE t.ticket_id = %s
            """
            result = query(sql, [ticket_id])
            if result:
                return result[0]
            else:
                return None
        except Exception as e:
            print(f"Ошибка при поиске билета #{ticket_id}: {e}")
            return None

    @staticmethod
    def cancel_ticket(ticket_id, user_id=None):
        try:
            # Если user_id не передан, получаем из БД
            if user_id is None:
                ticket_info = query("SELECT user_id FROM ticket WHERE ticket_id = %s", [ticket_id])
                if not ticket_info:
                    return False
                user_id = ticket_info[0][0]

            # Удаляем билет
            sql = "DELETE FROM ticket WHERE ticket_id = %s RETURNING ticket_id"
            result = query(sql, [ticket_id])

            if result:
                LogModel.log_ticket_cancel(user_id, ticket_id)
                return True
            else:
                print(f"Не удалось удалить билет #{ticket_id}")
                return False

        except Exception as e:
            print(f"Ошибка при отмене билета #{ticket_id}: {e}")
            import traceback
            traceback.print_exc()
            return False

    @staticmethod
    def get_session_info(session_id):
        """Получить информацию о сеансе"""
        sql = """
            SELECT s.session_id, m.title, m.base_price, h.hall_name, 
                   h.hall_extra_price, s.session_time, m.movie_image,
                   h.hall_id
            FROM session s
            JOIN movies m ON s.movie_id = m.movie_id
            JOIN hall h ON s.hall_id = h.hall_id
            WHERE s.session_id = %s
        """
        result = query(sql, [session_id])
        return result[0] if result else None

    @staticmethod
    def get_all_seats_for_hall(hall_id):
        """Получить все места для указанного зала"""
        sql = """
            SELECT s.seat_id, s.row_number, s.seat_number, s.seat_extra_price
            FROM seat s
            WHERE s.hall_id = %s
            ORDER BY s.row_number, s.seat_number
        """
        return query(sql, [hall_id]) or []

    @staticmethod
    def get_all_tickets(limit=None, offset=0):
        """Получить все билеты с информацией - ОБНОВЛЕННАЯ ВЕРСИЯ"""
        sql = """
            SELECT 
                t.ticket_id,
                m.title as movie_title,
                u.login as user_login,
                h.hall_name,
                s.session_time,
                st.row_number,
                st.seat_number,
                t.final_price,
                t.purchase_date
            FROM ticket t
            JOIN session s ON t.session_id = s.session_id
            JOIN movies m ON s.movie_id = m.movie_id
            JOIN users u ON t.user_id = u.user_id
            JOIN hall h ON s.hall_id = h.hall_id
            JOIN seat st ON t.seat_id = st.seat_id
            ORDER BY t.purchase_date DESC
        """
        if limit:
            sql += f" LIMIT {limit} OFFSET {offset}"

        return query(sql) or []

    @staticmethod
    def get_tickets_by_session(session_id):
        """Получить все билеты для конкретного сеанса"""
        sql = """
            SELECT 
                t.ticket_id,
                u.login as user_login,
                st.row_number,
                st.seat_number,
                t.final_price,
                t.purchase_date
            FROM ticket t
            JOIN users u ON t.user_id = u.user_id
            JOIN seat st ON t.seat_id = st.seat_id
            WHERE t.session_id = %s
            ORDER BY st.row_number, st.seat_number
        """
        return query(sql, [session_id]) or []

    @staticmethod
    def get_tickets_stats():
        """Получить статистику по билетам"""
        sql = """
            SELECT 
                COUNT(*) as total_tickets,
                SUM(t.final_price) as total_revenue,
                AVG(t.final_price) as avg_ticket_price,
                COUNT(DISTINCT t.user_id) as unique_customers,
                COUNT(DISTINCT s.movie_id) as unique_movies
            FROM ticket t
            JOIN session s ON t.session_id = s.session_id
        """
        result = query(sql)
        return result[0] if result else (0, 0, 0, 0, 0)

    @staticmethod
    def get_daily_revenue(days=30):
        """Получить ежедневную выручку за последние N дней"""
        sql = f"""
            SELECT 
                DATE(t.purchase_date) as date,
                COUNT(*) as tickets_sold,
                SUM(t.final_price) as daily_revenue
            FROM ticket t
            WHERE t.purchase_date >= CURRENT_DATE - INTERVAL '{days} days'
            GROUP BY DATE(t.purchase_date)
            ORDER BY date DESC
        """
        return query(sql) or []

    @staticmethod
    def cancel_ticket_admin(ticket_id, admin_id):
        """Отмена билета администратором с логированием - ИСПРАВЛЕННАЯ ВЕРСИЯ"""
        try:
            print(f"🔄 Админ #{admin_id} отменяет билет #{ticket_id}")

            ticket_info = query("""
                SELECT t.user_id, t.session_id, t.seat_id, t.final_price
                FROM ticket t WHERE ticket_id = %s
            """, [ticket_id])

            if not ticket_info:
                print(f"❌ Билет #{ticket_id} не найден для админ-отмены")
                return False

            user_id, session_id, seat_id, price = ticket_info[0]

            sql = "DELETE FROM ticket WHERE ticket_id = %s RETURNING ticket_id"
            result = query(sql, [ticket_id])

            if result is not None:
                print(f"✅ Админ успешно отменил билет #{ticket_id}")

                LogModel.log_ticket_cancel(user_id, ticket_id, is_admin=True)
                # Дополнительное логирование для админа
                LogModel.log_admin_action(
                    admin_id,
                    "TICKET_CANCEL",
                    "Ticket",
                    ticket_id,
                    f"Отмена билета #{ticket_id}. Возврат: {price} руб."
                )
                return True
            else:
                print(f"❌ Ошибка при админ-отмене билета #{ticket_id}")
                return False

        except Exception as e:
            print(f"💥 Критическая ошибка при админ-отмене: {e}")
            LogModel.log_error(admin_id, "TICKET_CANCEL_ADMIN", str(e), ticket_id)
            return False
