from core.database import query


class HallModel:
    @staticmethod
    def get_all_halls():
        """Получить все залы"""
        sql = """
            SELECT hall_id, hall_number, hall_name, hall_type, 
                   hall_extra_price, created_at, updated_at
            FROM hall
            ORDER BY hall_number
        """
        return query(sql) or []

    @staticmethod
    def get_hall_by_id(hall_id):
        """Получить зал по ID"""
        sql = """
            SELECT hall_id, hall_number, hall_name, hall_type, 
                   hall_extra_price, created_at, updated_at
            FROM hall
            WHERE hall_id = %s
        """
        result = query(sql, [hall_id])
        return result[0] if result else None

    @staticmethod
    def create_hall(hall_number, hall_name, hall_type, hall_extra_price=0):
        """Создать новый зал с валидацией"""
        # Проверка на дубликат
        if HallModel.is_hall_duplicate(hall_number, hall_name, hall_type):
            raise ValueError("Зал с таким номером, названием и типом уже существует")

        sql = """
            INSERT INTO hall (hall_number, hall_name, hall_type, hall_extra_price)
            VALUES (%s, %s, %s, %s)
            RETURNING hall_id
        """
        result = query(sql, [hall_number, hall_name, hall_type, hall_extra_price])
        return result[0][0] if result else None

    @staticmethod
    def update_hall(hall_id, hall_number, hall_name, hall_type, hall_extra_price):
        """Обновить зал с валидацией"""
        # Проверка на дубликат (исключая текущий зал)
        if HallModel.is_hall_duplicate(hall_number, hall_name, hall_type, hall_id):
            raise ValueError("Зал с таким номером, названием и типом уже существует")

        sql = """
            UPDATE hall 
            SET hall_number = %s, hall_name = %s, hall_type = %s, 
                hall_extra_price = %s, updated_at = CURRENT_TIMESTAMP
            WHERE hall_id = %s
        """
        query(sql, [hall_number, hall_name, hall_type, hall_extra_price, hall_id])
        return True

    @staticmethod
    def delete_hall(hall_id):
        """Удалить зал"""
        sql = "DELETE FROM hall WHERE hall_id = %s"
        query(sql, [hall_id])
        return True

    @staticmethod
    def is_hall_duplicate(hall_number, hall_name, hall_type, exclude_hall_id=None):
        """Проверить дубликат зала"""
        if exclude_hall_id:
            sql = """
                SELECT COUNT(*) 
                FROM hall 
                WHERE (hall_number = %s OR (hall_name = %s AND hall_type = %s))
                AND hall_id != %s
            """
            result = query(sql, [hall_number, hall_name, hall_type, exclude_hall_id])
        else:
            sql = """
                SELECT COUNT(*) 
                FROM hall 
                WHERE hall_number = %s OR (hall_name = %s AND hall_type = %s)
            """
            result = query(sql, [hall_number, hall_name, hall_type])

        return result[0][0] > 0 if result else False

    @staticmethod
    def get_hall_types():
        """Получить доступные типы залов"""
        return ['Standard', 'VIP', 'IMAX', '4DX', 'Premium', 'Luxury']

    @staticmethod
    def get_hall_names():
        """Получить стандартные названия залов"""
        return ['Основной зал', 'Малый зал', 'VIP зал', 'IMAX зал', '4DX зал', 'Премиум зал']