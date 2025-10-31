from core.database import query, image_to_binary


class ActorModel:
    @staticmethod
    def get_all_actors():
        """Получить всех актёров"""
        sql = """
            SELECT actor_id, fullname, photo, created_at, updated_at
            FROM actor
            ORDER BY fullname
        """
        rows = query(sql)
        return rows if rows else []

    @staticmethod
    def get_actor_by_id(actor_id):
        """Получить актёра по ID"""
        sql = """
            SELECT actor_id, fullname, photo, created_at, updated_at
            FROM actor
            WHERE actor_id = %s
        """
        rows = query(sql, [actor_id])
        return rows[0] if rows else None

    @staticmethod
    def create_actor(fullname, photo_path):
        """Создать нового актёра"""
        sql = """
            INSERT INTO actor (fullname, photo)
            VALUES (%s, %s)
            RETURNING actor_id
        """
        photo_binary = image_to_binary(photo_path)
        result = query(sql, [fullname, photo_binary])
        return result[0][0] if result else None

    @staticmethod
    def update_actor(actor_id, fullname, photo_path=None):
        """Обновить данные актёра"""
        if photo_path:
            photo_binary = image_to_binary(photo_path)
            sql = """
                UPDATE actor
                SET fullname = %s, photo = %s, updated_at = CURRENT_TIMESTAMP
                WHERE actor_id = %s
            """
            query(sql, [fullname, photo_binary, actor_id])
        else:
            sql = """
                UPDATE actor
                SET fullname = %s, updated_at = CURRENT_TIMESTAMP
                WHERE actor_id = %s
            """
            query(sql, [fullname, actor_id])
        return True

    @staticmethod
    def delete_actor(actor_id):
        """Удалить актёра"""
        sql = "DELETE FROM actor WHERE actor_id = %s"
        query(sql, [actor_id])
        return True

    @staticmethod
    def search_actors(search_text):
        """Поиск актёров по имени"""
        sql = """
            SELECT actor_id, fullname, photo, created_at, updated_at
            FROM actor
            WHERE fullname ILIKE %s
            ORDER BY fullname
        """
        pattern = f"%{search_text}%"
        rows = query(sql, [pattern])
        return rows if rows else []

    @staticmethod
    def get_actor_movies(actor_id):
        """Получить фильмы актёра"""
        sql = """
            SELECT m.movie_id, m.title, ma.role
            FROM movies m
            JOIN movie_actor ma ON m.movie_id = ma.movie_id
            WHERE ma.actor_id = %s
            ORDER BY m.title
        """
        rows = query(sql, [actor_id])
        return rows if rows else []