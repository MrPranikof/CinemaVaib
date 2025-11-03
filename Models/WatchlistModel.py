from core.database import query


class WatchlistModel:
    @staticmethod
    def get_user_watchlist(user_id):
        """Получить избранные фильмы пользователя"""
        sql = """
            SELECT w.watchlist_id, m.movie_id, m.title, m.description, 
                   m.movie_image, m.base_price, m.rating, w.status, w.created_at
            FROM watchlist w
            JOIN movies m ON w.movie_id = m.movie_id
            WHERE w.user_id = %s
            ORDER BY w.created_at DESC
        """
        return query(sql, [user_id]) or []

    @staticmethod
    def add_to_watchlist(user_id, movie_id, status='Planned'):
        """Добавить фильм в избранное"""
        # Проверяем, нет ли уже этого фильма в избранном
        check_sql = "SELECT watchlist_id FROM watchlist WHERE user_id = %s AND movie_id = %s"
        existing = query(check_sql, [user_id, movie_id])

        if existing:
            return False  # Уже в избранном

        sql = """
            INSERT INTO watchlist (user_id, movie_id, status)
            VALUES (%s, %s, %s)
            RETURNING watchlist_id
        """
        result = query(sql, [user_id, movie_id, status])
        return result[0][0] if result else None

    @staticmethod
    def remove_from_watchlist(user_id, movie_id):
        """Удалить фильм из избранного"""
        sql = "DELETE FROM watchlist WHERE user_id = %s AND movie_id = %s"
        query(sql, [user_id, movie_id])
        return True

    @staticmethod
    def is_in_watchlist(user_id, movie_id):
        """Проверить, есть ли фильм в избранном"""
        sql = "SELECT watchlist_id FROM watchlist WHERE user_id = %s AND movie_id = %s"
        result = query(sql, [user_id, movie_id])
        return bool(result)

    @staticmethod
    def update_watchlist_status(watchlist_id, status):
        """Обновить статус фильма в избранном"""
        sql = """
            UPDATE watchlist 
            SET status = %s, updated_at = CURRENT_TIMESTAMP
            WHERE watchlist_id = %s
        """
        query(sql, [status, watchlist_id])
        return True

    @staticmethod
    def get_watchlist_stats(user_id):
        """Получить статистику по избранному"""
        sql = """
            SELECT 
                COUNT(*) as total,
                COUNT(CASE WHEN status = 'Watched' THEN 1 END) as watched,
                COUNT(CASE WHEN status = 'Planned' THEN 1 END) as planned,
                COUNT(CASE WHEN status = 'Watching' THEN 1 END) as watching
            FROM watchlist 
            WHERE user_id = %s
        """
        result = query(sql, [user_id])
        return result[0] if result else (0, 0, 0, 0)