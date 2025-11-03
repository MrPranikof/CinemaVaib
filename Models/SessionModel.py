from core.database import query

class SessionModel:
    @staticmethod
    def get_sessions_by_movie(movie_id):
        """Получить сеансы для конкретного фильма"""
        sql = """
            SELECT s.session_id, m.title, m.movie_image, h.hall_name, 
                   s.session_time, m.base_price + h.hall_extra_price as price
            FROM session s
            JOIN movies m ON s.movie_id = m.movie_id
            JOIN hall h ON s.hall_id = h.hall_id
            WHERE m.movie_id = %s AND s.session_time > CURRENT_TIMESTAMP
            ORDER BY s.session_time
        """
        return query(sql, [movie_id]) or []

    @staticmethod
    def create_session(movie_id, hall_id, session_time):
        """Создать сеанс"""
        sql = """
            INSERT INTO session (movie_id, hall_id, session_time)
            VALUES (%s, %s, %s)
            RETURNING session_id
        """
        result = query(sql, [movie_id, hall_id, session_time])
        return result[0][0] if result else None

    @staticmethod
    def update_session(session_id, movie_id, hall_id, session_time):
        """Обновить сеанс"""
        sql = """
            UPDATE session 
            SET movie_id = %s, hall_id = %s, session_time = %s,
                updated_at = CURRENT_TIMESTAMP
            WHERE session_id = %s
        """
        query(sql, [movie_id, hall_id, session_time, session_id])
        return True

    @staticmethod
    def delete_session(session_id):
        """Удалить сеанс"""
        sql = "DELETE FROM session WHERE session_id = %s"
        query(sql, [session_id])
        return True

    @staticmethod
    def get_all_sessions():
        """Получить все сеансы"""
        sql = """
            SELECT s.session_id, m.title, h.hall_name, s.session_time,
                   m.base_price + h.hall_extra_price as price,
                   s.created_at
            FROM session s
            JOIN movies m ON s.movie_id = m.movie_id
            JOIN hall h ON s.hall_id = h.hall_id
            ORDER BY s.session_time DESC
        """
        return query(sql) or []