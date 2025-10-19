from core.database import query
from core.utils import hash_password, verify_password

class UserModel:
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
        sql = "INSERT INTO users (login, email, password_hash) VALUES (%s, %s, %s);"
        query(sql, [login, email, hash_password(password)])
        return True

    @staticmethod
    def check_password(login: str, password: str) -> bool:
        user = UserModel.find_by_login(login)
        if user is None:
            return False
        stored_hash = user[2]
        return verify_password(stored_hash, password)

    @staticmethod
    def last_login(login: str):
        user = UserModel.find_by_login(login)
        if user is None:
            return False

        sql = "UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE login = %s;"
        query(sql, [login])
        return True

    @staticmethod
    def get_user_role_id(login: str):
        sql = "SELECT role_id FROM users WHERE login = %s;"
        rows = query(sql, [login])
        return rows[0][0] if rows else None

    @staticmethod
    def update_password(login: str, old_password: str, new_password: str) -> bool:
        user = UserModel.find_by_login(login)
        if user is None:
            return False

        stored_hash = user[2]

        if not verify_password(stored_hash, old_password):
            return False

        new_hash = hash_password(new_password)
        sql = """
            UPDATE users
            SET password_hash = %s,
                updated_at = CURRENT_TIMESTAMP
            WHERE login = %s;
        """
        query(sql, [new_hash, login])
        return True