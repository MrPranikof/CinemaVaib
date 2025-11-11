from Models.LogModel import LogModel
from core.database import query, image_to_binary


class ActorModel:
    @staticmethod
    def get_all_actors():
        """Получить всех актёров"""
        sql = """
            SELECT actor_id, name || ' ' || lastname AS fullname, photo, created_at, updated_at
            FROM actor
            ORDER BY fullname
        """
        rows = query(sql)
        return rows if rows else []

    @staticmethod
    def get_actor_by_id(actor_id):
        """Получить актёра по ID"""
        sql = """
            SELECT actor_id, name || ' ' || lastname AS fullname, photo, created_at, updated_at
            FROM actor
            WHERE actor_id = %s
        """
        rows = query(sql, [actor_id])
        return rows[0] if rows else None

    @staticmethod
    def create_actor(name, lastname, photo_path, user_id=None):
        """Создать нового актёра с логированием"""
        sql = """
            INSERT INTO actor (name, lastname, photo)
            VALUES (%s, %s, %s)
            RETURNING actor_id
        """
        photo_binary = image_to_binary(photo_path)
        result = query(sql, [name, lastname, photo_binary])

        if result:
            actor_id = result[0][0]
            LogModel.log_admin_action(
                user_id,
                "ACTOR_CREATE",
                "Actor",
                actor_id,
                f"Создан актер: {name} {lastname}"
            )
            return actor_id
        return None

    @staticmethod
    def update_actor(actor_id, name, lastname, photo_path=None, user_id=None):
        """Обновить данные актёра с логированием"""
        if photo_path:
            photo_binary = image_to_binary(photo_path)
            sql = """
                UPDATE actor
                SET name = %s, lastname = %s, photo = %s, updated_at = CURRENT_TIMESTAMP
                WHERE actor_id = %s
            """
            query(sql, [name, lastname, photo_binary, actor_id])
        else:
            sql = """
                UPDATE actor
                SET name = %s, lastname = %s, updated_at = CURRENT_TIMESTAMP
                WHERE actor_id = %s
            """
            query(sql, [name, lastname, actor_id])

        LogModel.log_admin_action(
            user_id,
            "ACTOR_UPDATE",
            "Actor",
            actor_id,
            f"Обновлен актер: {name} {lastname} (ID: {actor_id})"
        )
        return True

    @staticmethod
    def delete_actor(actor_id, user_id=None):
        # Сначала получаем данные для лога
        actor_data = ActorModel.get_actor_by_id(actor_id)
        actor_name = f"{actor_data[1]} {actor_data[2]}" if actor_data else "Unknown"

        sql = "DELETE FROM actor WHERE actor_id = %s"
        query(sql, [actor_id])

        LogModel.log_admin_action(
            user_id,
            "ACTOR_DELETE",
            "Actor",
            actor_id,
            f"Удален актер: {actor_name} (ID: {actor_id})"
        )
        return True

    @staticmethod
    def search_actors(search_text):
        """Поиск актёров по имени"""
        sql = """
            SELECT actor_id, name || ' ' || lastname AS fullname, photo, created_at, updated_at
            FROM actor
            WHERE (name || ' ' || lastname) ILIKE %s
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