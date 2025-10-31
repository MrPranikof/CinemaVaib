from core.database import query, image_to_binary


class DirectorModel:
    @staticmethod
    def get_all_directors():
        """Получить всех режиссёров"""
        sql = """
            SELECT director_id, fullname, photo, created_at, updated_at
            FROM director
            ORDER BY fullname
        """
        rows = query(sql)
        return rows if rows else []

    @staticmethod
    def get_director_by_id(director_id):
        """Получить режиссёра по ID"""
        sql = """
            SELECT director_id, fullname, photo, created_at, updated_at
            FROM director
            WHERE director_id = %s
        """
        rows = query(sql, [director_id])
        return rows[0] if rows else None

    @staticmethod
    def create_director(fullname, photo_path):
        """Создать нового режиссёра"""
        sql = """
            INSERT INTO director (fullname, photo)
            VALUES (%s, %s)
            RETURNING director_id
        """
        photo_binary = image_to_binary(photo_path)
        result = query(sql, [fullname, photo_binary])
        return result[0][0] if result else None

    @staticmethod
    def update_director(director_id, fullname, photo_path=None):
        """Обновить данные режиссёра"""
        if photo_path:
            photo_binary = image_to_binary(photo_path)
            sql = """
                UPDATE director
                SET fullname = %s, photo = %s, updated_at = CURRENT_TIMESTAMP
                WHERE director_id = %s
            """
            query(sql, [fullname, photo_binary, director_id])
        else:
            sql = """
                UPDATE director
                SET fullname = %s, updated_at = CURRENT_TIMESTAMP
                WHERE director_id = %s
            """
            query(sql, [fullname, director_id])
        return True

    @staticmethod
    def delete_director(director_id):
        """Удалить режиссёра"""
        sql = "DELETE FROM director WHERE director_id = %s"
        query(sql, [director_id])
        return True

    @staticmethod
    def search_directors(search_text):
        """Поиск режиссёров по имени"""
        sql = """
            SELECT director_id, fullname, photo, created_at, updated_at
            FROM director
            WHERE fullname ILIKE %s
            ORDER BY fullname
        """
        pattern = f"%{search_text}%"
        rows = query(sql, [pattern])
        return rows if rows else []

    @staticmethod
    def get_director_movies(director_id):
        """Получить фильмы режиссёра"""
        sql = """
            SELECT m.movie_id, m.title
            FROM movies m
            JOIN movie_director md ON m.movie_id = md.movie_id
            WHERE md.director_id = %s
            ORDER BY m.title
        """
        rows = query(sql, [director_id])
        return rows if rows else []