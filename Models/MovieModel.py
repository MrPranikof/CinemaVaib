# Models/MovieModel.py
from core.database import query


class MovieModel:
    @staticmethod
    def get_all_movies(limit=None, offset=0):
        """Получить все фильмы с ограничением - ИСПРАВЛЕННАЯ ВЕРСИЯ"""
        try:
            sql = """
                SELECT movie_id, title, description, movie_image, 
                       base_price, rating, created_at, updated_at
                FROM movies
                ORDER BY created_at DESC
            """
            if limit:
                sql += f" LIMIT {limit} OFFSET {offset}"

            rows = query(sql)
            return rows if rows else []  # Всегда возвращаем список, даже пустой

        except Exception as e:
            print(f"❌ Ошибка в get_all_movies: {e}")
            return []  # Возвращаем пустой список при ошибке

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
        """Поиск фильмов по названию - ИСПРАВЛЕННАЯ ВЕРСИЯ"""
        try:
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
        except Exception as e:
            print(f"❌ Ошибка в search_movies: {e}")
            return []




    @staticmethod
    def get_movies_by_genre(genre_id):
        """Получить фильмы по жанру - ИСПРАВЛЕННАЯ ВЕРСИЯ"""
        try:
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
        except Exception as e:
            print(f"❌ Ошибка в get_movies_by_genre: {e}")
            return []

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

    @staticmethod
    def get_movie_directors(movie_id):
        """Получить режиссёров фильма"""
        sql = """
            SELECT d.director_id, d.fullname, d.photo
            FROM director d
            JOIN movie_director md ON d.director_id = md.director_id
            WHERE md.movie_id = %s
        """
        return query(sql, [movie_id]) or []

    @staticmethod
    def get_movie_actors(movie_id):
        """Получить актёров фильма с ролями"""
        sql = """
            SELECT a.actor_id, a.fullname, a.photo, ma.role
            FROM actor a
            JOIN movie_actor ma ON a.actor_id = ma.actor_id
            WHERE ma.movie_id = %s
            ORDER BY ma.created_at
        """
        return query(sql, [movie_id]) or []