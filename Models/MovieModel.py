# Models/MovieModel.py
from core.database import query


class MovieModel:
    @staticmethod
    def get_all_movies(limit=None, offset=0):
        """Получить все фильмы с ограничением"""
        sql = """
            SELECT movie_id, title, description, movie_image, 
                   base_price, rating, created_at, updated_at
            FROM movies
            ORDER BY created_at DESC
        """
        if limit:
            sql += f" LIMIT {limit} OFFSET {offset}"

        rows = query(sql)
        return rows if rows else []

    @staticmethod
    def get_movie_by_id(movie_id):
        """Получить фильм по ID"""
        sql = """
            SELECT movie_id, title, description, movie_image, 
                   base_price, rating, created_at, updated_at
            FROM movies
            WHERE movie_id = %s
        """
        rows = query(sql, [movie_id])
        return rows[0] if rows else None

    @staticmethod
    def search_movies(search_text):
        """Поиск фильмов по названию"""
        sql = """
            SELECT movie_id, title, description, movie_image, 
                   base_price, rating, created_at, updated_at
            FROM movies
            WHERE title ILIKE %s OR description ILIKE %s
            ORDER BY rating DESC, created_at DESC
        """
        pattern = f"%{search_text}%"
        rows = query(sql, [pattern, pattern])
        return rows if rows else []

    @staticmethod
    def get_movies_by_genre(genre_id):
        """Получить фильмы по жанру"""
        sql = """
            SELECT m.movie_id, m.title, m.description, m.movie_image, 
                   m.base_price, m.rating, m.created_at, m.updated_at
            FROM movies m
            JOIN movie_genre mg ON m.movie_id = mg.movie_id
            WHERE mg.genre_id = %s
            ORDER BY m.rating DESC
        """
        rows = query(sql, [genre_id])
        return rows if rows else []

    @staticmethod
    def get_movie_genres(movie_id):
        """Получить жанры фильма"""
        sql = """
            SELECT g.genre_id, g.name
            FROM genres g
            JOIN movie_genre mg ON g.genre_id = mg.genre_id
            WHERE mg.movie_id = %s
        """
        rows = query(sql, [movie_id])
        return rows if rows else []

    @staticmethod
    def get_all_genres():
        """Получить все жанры"""
        sql = "SELECT genre_id, name FROM genres ORDER BY name"
        rows = query(sql)
        return rows if rows else []