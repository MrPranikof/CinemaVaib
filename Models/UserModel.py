from core.database import query
from core.utils import hash_password, verify_password


class UserModel:
    @staticmethod
    def find_by_id(user_id: int):
        sql = "SELECT * FROM users WHERE user_id = %s;"
        rows = query(sql, [user_id])
        return rows[0] if rows else None

    @staticmethod
    def get_user_id(login: str):
        """Получить user_id по логину"""
        sql = "SELECT user_id FROM users WHERE login = %s;"
        rows = query(sql, [login])
        return rows[0][0] if rows else None

    @staticmethod
    def get_login_by_id(user_id: int):
        """Получить логин по user_id"""
        sql = "SELECT login FROM users WHERE user_id = %s;"
        rows = query(sql, [user_id])
        return rows[0][0] if rows else None

    @staticmethod
    def get_email_by_id(user_id: int):
        """Получить email по user_id"""
        sql = "SELECT email FROM users WHERE user_id = %s;"
        rows = query(sql, [user_id])
        return rows[0][0] if rows else None

    @staticmethod
    def get_user_data(user_id: int):
        """Получить ВСЕ актуальные данные пользователя по ID"""
        sql = """
            SELECT u.user_id, u.login, u.email, r.role_name, u.status, 
                   u.created_at, u.updated_at, u.last_login, r.role_id
            FROM users u
            JOIN roles r ON u.role_id = r.role_id
            WHERE u.user_id = %s
        """
        rows = query(sql, [user_id])
        if rows:
            return {
                'user_id': rows[0][0],
                'login': rows[0][1],
                'email': rows[0][2],
                'role_name': rows[0][3],
                'status': rows[0][4],
                'created_at': rows[0][5],
                'updated_at': rows[0][6],
                'last_login': rows[0][7],
                'role_id': rows[0][8]
            }
        return None

    @staticmethod
    def find_by_login(login: str):
        sql = "SELECT * FROM users WHERE login = %s;"
        rows = query(sql, [login])
        return rows[0] if rows else None

    @staticmethod
    def find_by_email(email: str):
        sql = "SELECT * FROM users WHERE email = %s;"
        rows = query(sql, [email])
        return rows[0] if rows else None

    @staticmethod
    def create_user(login: str, email: str, password: str):
        sql = "INSERT INTO users (login, email, password_hash) VALUES (%s, %s, %s) RETURNING user_id;"
        result = query(sql, [login, email, hash_password(password)])
        return result[0][0] if result else None

    @staticmethod
    def check_password(login: str, password: str) -> bool:
        user = UserModel.find_by_login(login)
        if user is None:
            return False
        stored_hash = user[2]  # password_hash
        return verify_password(stored_hash, password)

    @staticmethod
    def last_login(user_id: int):
        """Обновить время последнего входа по user_id"""
        sql = "UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE user_id = %s;"
        query(sql, [user_id])
        return True

    @staticmethod
    def update_password_by_id(user_id: int, old_password: str, new_password: str) -> bool:
        """Обновить пароль по user_id"""
        user = UserModel.find_by_id(user_id)
        if user is None:
            return False

        stored_hash = user[2]  # password_hash

        if not verify_password(stored_hash, old_password):
            return False

        new_hash = hash_password(new_password)
        sql = """
            UPDATE users
            SET password_hash = %s,
                updated_at = CURRENT_TIMESTAMP
            WHERE user_id = %s;
        """
        query(sql, [new_hash, user_id])
        return True

    @staticmethod
    def update_password(login: str, old_password: str, new_password: str) -> bool:
        """Обновить пароль по логину (для обратной совместимости)"""
        user = UserModel.find_by_login(login)
        if user is None:
            return False
        return UserModel.update_password_by_id(user[0], old_password, new_password)

    @staticmethod
    def get_user_role_id(login: str):
        sql = "SELECT role_id FROM users WHERE login = %s;"
        rows = query(sql, [login])
        return rows[0][0] if rows else None

    @staticmethod
    def get_user_role_name_by_id(user_id):
        sql = """
            SELECT r.role_name 
            FROM users u
            JOIN roles r ON u.role_id = r.role_id
            WHERE u.user_id = %s
        """
        rows = query(sql, [user_id])
        return rows[0][0] if rows else "Unknown"