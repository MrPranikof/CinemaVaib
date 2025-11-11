from Models.UserModel import UserModel
from core.database import query

class LogModel:
    @staticmethod
    def log_action(user_id, actor_role, action_type, entity_id, description,
                   action_result="SUCCESS", error_message=None):
        try:
            sql = """
                INSERT INTO activity_log 
                (user_id, actor_role, action_type, entity_id, description, created_at)
                VALUES (%s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
                RETURNING log_id
            """

            result = query(sql, [user_id, actor_role, action_type, entity_id, description])
            return result[0][0] if result else None

        except Exception as e:
            print(f"Ошибка при логировании: {e}")
            return None

    @staticmethod
    def log_user_login(user_id, login_success=True, error_msg=None, user_role=None):
        """Логирование входа пользователя"""
        action_type = "USER_LOGIN"

        # Определяем роль актора
        if user_role:
            actor_role = user_role  # "Admin" или "User"
        elif login_success:
            # Если роль не передана, но вход успешен - получаем роль из БД
            actor_role = UserModel.get_user_role_name_by_id(user_id)
        else:
            actor_role = "User"  # Для неудачных попыток

        result = "SUCCESS" if login_success else "FAILED"

        if login_success:
            desc = f"Вход пользователя ID: {user_id} (Роль: {actor_role})"
        else:
            desc = f"Неудачная попытка входа: {error_msg}"

        return LogModel.log_action(
            user_id if login_success else None,
            actor_role,
            action_type,
            user_id if login_success else None,
            desc,
            result,
            error_msg
        )

    @staticmethod
    def log_user_logout(user_id):
        """Логирование выхода пользователя"""
        return LogModel.log_action(
            user_id,
            "User",
            "USER_LOGOUT",
            user_id,
            f"Выход пользователя ID: {user_id}"
        )

    @staticmethod
    def log_user_register(user_id, login):
        """Логирование регистрации пользователя"""
        return LogModel.log_action(
            user_id,
            "System",
            "USER_REGISTER",
            user_id,
            f"Регистрация нового пользователя: {login} (ID: {user_id})"
        )

    @staticmethod
    def log_password_change(user_id, success=True, error_msg=None):
        """Логирование смены пароля"""
        action_type = "PASSWORD_CHANGE"
        result = "SUCCESS" if success else "FAILED"
        desc = f"Смена пароля пользователя ID: {user_id}" if success else f"Ошибка смены пароля: {error_msg}"

        return LogModel.log_action(
            user_id,
            "User",
            action_type,
            user_id,
            desc,
            result,
            error_msg
        )

    @staticmethod
    def log_ticket_purchase(user_id, ticket_id, session_id, seats_count):
        """Логирование покупки билета"""
        return LogModel.log_action(
            user_id,
            "User",
            "TICKET_PURCHASE",
            ticket_id,
            f"Покупка билета #{ticket_id} на сеанс #{session_id} ({seats_count} мест)"
        )

    @staticmethod
    def log_ticket_cancel(user_id, ticket_id, is_admin=False):
        """Логирование отмены билета"""
        actor = "Admin" if is_admin else "User"
        return LogModel.log_action(
            user_id,
            actor,
            "TICKET_CANCEL",
            ticket_id,
            f"Отмена билета #{ticket_id}"
        )

    @staticmethod
    def log_movie_action(user_id, action_type, movie_id, movie_title, is_admin=False):
        """Логирование действий с фильмами"""
        actor = "Admin" if is_admin else "User"
        actions = {
            "MOVIE_ADD": f"Добавлен фильм: {movie_title} (ID: {movie_id})",
            "MOVIE_EDIT": f"Изменен фильм: {movie_title} (ID: {movie_id})",
            "MOVIE_DELETE": f"Удален фильм: {movie_title} (ID: {movie_id})",
            "MOVIE_VIEW": f"Просмотр фильма: {movie_title} (ID: {movie_id})"
        }

        description = actions.get(action_type, f"Действие с фильмом: {movie_title}")

        return LogModel.log_action(
            user_id,
            actor,
            action_type,
            movie_id,
            description
        )

    @staticmethod
    def log_review_action(user_id, action_type, review_id, movie_id, rating=None):
        """Логирование действий с отзывами"""
        actions = {
            "REVIEW_ADD": f"Добавлен отзыв к фильму ID: {movie_id} с оценкой {rating}",
            "REVIEW_EDIT": f"Изменен отзыв #{review_id} для фильма ID: {movie_id}",
            "REVIEW_DELETE": f"Удален отзыв #{review_id} для фильма ID: {movie_id}"
        }

        description = actions.get(action_type, f"Действие с отзывом #{review_id}")

        return LogModel.log_action(
            user_id,
            "User",
            action_type,
            review_id,
            description
        )

    @staticmethod
    def log_admin_action(admin_id, action_type, entity_type, entity_id, description):
        """Логирование действий администратора"""
        return LogModel.log_action(
            admin_id,
            "Admin",
            action_type,
            entity_id,
            f"[{entity_type}] {description}"
        )

    @staticmethod
    def log_error(user_id, action_type, error_msg, entity_id=None):
        """Логирование ошибок"""
        return LogModel.log_action(
            user_id,
            "System",
            f"ERROR_{action_type}",
            entity_id,
            f"Ошибка: {error_msg}",
            "FAILED",
            error_msg
        )

    @staticmethod
    def get_recent_logs(limit=100, user_id=None, action_type=None):
        """Получить последние записи лога"""
        sql = """
            SELECT al.log_id, al.user_id, u.login, al.actor_role, al.action_type, 
                   al.entity_id, al.description, al.created_at
            FROM activity_log al
            LEFT JOIN users u ON al.user_id = u.user_id
            WHERE 1=1
        """
        params = []

        if user_id:
            sql += " AND al.user_id = %s"
            params.append(user_id)

        if action_type:
            sql += " AND al.action_type = %s"
            params.append(action_type)

        sql += " ORDER BY al.created_at DESC LIMIT %s"
        params.append(limit)

        return query(sql, params) or []

    @staticmethod
    def cleanup_old_logs(days_to_keep=90):
        """Очистка старых логов"""
        sql = "DELETE FROM activity_log WHERE created_at < CURRENT_DATE - INTERVAL '%s days'"
        query(sql, [days_to_keep])
        return True

    @staticmethod
    def log_pdf_generation(user_id, ticket_ids, success=True, error_msg=None):
        action_type = "PDF_GENERATION"
        result = "SUCCESS" if success else "FAILED"

        if isinstance(ticket_ids, list):
            tickets_text = f"{len(ticket_ids)} билетов"
        else:
            tickets_text = f"билета #{ticket_ids}"

        description = f"Генерация PDF для {tickets_text}"

        if not success:
            description += f" - Ошибка: {error_msg}"

        return LogModel.log_action(
            user_id,
            "User",
            action_type,
            ticket_ids[0] if isinstance(ticket_ids, list) and ticket_ids else ticket_ids,
            description,
            result,
            error_msg
        )