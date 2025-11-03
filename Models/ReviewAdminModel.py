from core.database import query


class ReviewAdminModel:

    @staticmethod
    def get_all_reviews(limit=None, offset=0):
        """Получить все отзывы с информацией о пользователях и фильмах"""
        sql = """
            SELECT 
                r.review_id,
                u.login as user_login,
                m.title as movie_title,
                r.rating,
                r.comment,
                r.created_at,
                r.updated_at
            FROM review r
            JOIN users u ON r.user_id = u.user_id
            JOIN movies m ON r.movie_id = m.movie_id
            ORDER BY r.created_at DESC
        """
        if limit:
            sql += f" LIMIT {limit} OFFSET {offset}"

        return query(sql) or []

    @staticmethod
    def get_review_by_id(review_id):
        """Получить отзыв по ID"""
        sql = """
            SELECT 
                r.review_id,
                u.user_id,
                u.login,
                m.movie_id,
                m.title,
                r.rating,
                r.comment,
                r.created_at
            FROM review r
            JOIN users u ON r.user_id = u.user_id
            JOIN movies m ON r.movie_id = m.movie_id
            WHERE r.review_id = %s
        """
        result = query(sql, [review_id])
        return result[0] if result else None

    @staticmethod
    def delete_review(review_id):
        """Удалить отзыв"""
        sql = "DELETE FROM review WHERE review_id = %s"
        query(sql, [review_id])
        return True

    @staticmethod
    def update_review_rating(movie_id):
        """Обновить рейтинг фильма после изменения отзывов"""
        sql = """
            UPDATE movies 
            SET rating = (
                SELECT COALESCE(AVG(rating), 0) 
                FROM review 
                WHERE movie_id = %s
            )
            WHERE movie_id = %s
        """
        query(sql, [movie_id, movie_id])
        return True

    @staticmethod
    def search_reviews(search_text):
        """Поиск отзывов по тексту комментария или названию фильма"""
        sql = """
            SELECT 
                r.review_id,
                u.login as user_login,
                m.title as movie_title,
                r.rating,
                r.comment,
                r.created_at
            FROM review r
            JOIN users u ON r.user_id = u.user_id
            JOIN movies m ON r.movie_id = m.movie_id
            WHERE r.comment ILIKE %s OR m.title ILIKE %s
            ORDER BY r.created_at DESC
            LIMIT 100
        """
        pattern = f"%{search_text}%"
        return query(sql, [pattern, pattern]) or []

    @staticmethod
    def get_reviews_stats():
        """Получить статистику по отзывам"""
        sql = """
            SELECT 
                COUNT(*) as total_reviews,
                AVG(rating) as avg_rating,
                COUNT(DISTINCT user_id) as unique_users,
                COUNT(DISTINCT movie_id) as unique_movies
            FROM review
        """
        result = query(sql)
        return result[0] if result else (0, 0, 0, 0)