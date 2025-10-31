# Models/GenreModel.py
from core.database import query


class GenreModel:
    @staticmethod
    def get_all_genres():
        """Получить все жанры"""
        sql = "SELECT genre_id, name, created_at, updated_at FROM genres ORDER BY name"
        rows = query(sql)
        return rows if rows else []

    @staticmethod
    def get_genre_by_id(genre_id):
        """Получить жанр по ID"""
        sql = "SELECT genre_id, name FROM genres WHERE genre_id = %s"
        rows = query(sql, [genre_id])
        return rows[0] if rows else None

    @staticmethod
    def create_genre(name):
        """Создать новый жанр"""
        sql = "INSERT INTO genres (name) VALUES (%s) RETURNING genre_id"
        result = query(sql, [name])
        return result[0][0] if result else None

    @staticmethod
    def update_genre(genre_id, name):
        """Обновить жанр"""
        sql = "UPDATE genres SET name = %s, updated_at = CURRENT_TIMESTAMP WHERE genre_id = %s"
        query(sql, [name, genre_id])
        return True

    @staticmethod
    def delete_genre(genre_id):
        """Удалить жанр"""
        sql = "DELETE FROM genres WHERE genre_id = %s"
        query(sql, [genre_id])
        return True

    @staticmethod
    def search_genres(search_text):
        """Поиск жанров"""
        sql = "SELECT genre_id, name, created_at, updated_at FROM genres WHERE name ILIKE %s ORDER BY name"
        pattern = f"%{search_text}%"
        rows = query(sql, [pattern])
        return rows if rows else []