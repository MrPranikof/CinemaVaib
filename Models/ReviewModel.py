from Models.LogModel import LogModel
from core.database import query

class ReviewModel:
    @staticmethod
    def get_movie_reviews(movie_id):
        """Получить отзывы для фильма"""
        sql = """
            SELECT r.review_id, u.login, r.rating, r.comment, r.created_at
            FROM review r
            JOIN users u ON r.user_id = u.user_id
            WHERE r.movie_id = %s
            ORDER BY r.created_at DESC
        """
        return query(sql, [movie_id]) or []

    @staticmethod
    def add_review(user_id, movie_id, rating, comment):
        """Добавить отзыв"""
        sql = """
            INSERT INTO review (user_id, movie_id, rating, comment)
            VALUES (%s, %s, %s, %s)
            RETURNING review_id
        """
        result = query(sql, [user_id, movie_id, rating, comment])

        if result:
            review_id = result[0][0]
            LogModel.log_review_action(user_id, "REVIEW_ADD", review_id, movie_id, rating)
            return review_id
        return None

    @staticmethod
    def get_user_review(user_id, movie_id):
        """Получить отзыв пользователя для фильма"""
        sql = """
            SELECT review_id, rating, comment
            FROM review
            WHERE user_id = %s AND movie_id = %s
        """
        result = query(sql, [user_id, movie_id])
        return result[0] if result else None

    @staticmethod
    def update_movie_rating(movie_id):
        """Обновить рейтинг фильма на основе отзывов"""
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