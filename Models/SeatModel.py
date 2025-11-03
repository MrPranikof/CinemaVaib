from core.database import query

class SeatModel:
    @staticmethod
    def create_seat(hall_id, row_number, seat_number, seat_extra_price=0):
        """Создать место в зале"""
        sql = """
            INSERT INTO seat (hall_id, row_number, seat_number, seat_extra_price)
            VALUES (%s, %s, %s, %s)
            RETURNING seat_id
        """
        result = query(sql, [hall_id, row_number, seat_number, seat_extra_price])
        return result[0][0] if result else None

    @staticmethod
    def create_multiple_seats(hall_id, rows_config):
        created_seats = []
        try:
            for config in rows_config:
                row = config['row']
                seats_count = config['seats']
                price = config.get('price', 0)

                for seat in range(1, seats_count + 1):
                    seat_id = SeatModel.create_seat(hall_id, row, seat, price)
                    if seat_id:
                        created_seats.append(seat_id)
            return created_seats
        except Exception as e:
            print(f"Ошибка при создании мест: {e}")
            return created_seats

    @staticmethod
    def update_seat(seat_id, row_number, seat_number, seat_extra_price):
        """Обновить место"""
        sql = """
            UPDATE seat 
            SET row_number = %s, seat_number = %s, seat_extra_price = %s,
                updated_at = CURRENT_TIMESTAMP
            WHERE seat_id = %s
        """
        query(sql, [row_number, seat_number, seat_extra_price, seat_id])
        return True

    @staticmethod
    def delete_seat(seat_id):
        """Удалить место"""
        sql = "DELETE FROM seat WHERE seat_id = %s"
        query(sql, [seat_id])
        return True

    @staticmethod
    def delete_hall_seats(hall_id):
        """Удалить все места в зале"""
        sql = "DELETE FROM seat WHERE hall_id = %s"
        query(sql, [hall_id])
        return True

    @staticmethod
    def update_row_prices(hall_id, row_prices):
        """
        Обновить цены для всех мест в указанных рядах
        row_prices: словарь {номер_ряда: цена}
        """
        for row_number, price in row_prices.items():
            sql = """
                UPDATE seat 
                SET seat_extra_price = %s, updated_at = CURRENT_TIMESTAMP
                WHERE hall_id = %s AND row_number = %s
            """
            query(sql, [price, hall_id, row_number])
        return True

    @staticmethod
    def get_seats_by_hall(hall_id):
        """Получить все места в зале с группировкой по рядам"""
        sql = """
            SELECT row_number, seat_number, seat_extra_price, seat_id
            FROM seat 
            WHERE hall_id = %s 
            ORDER BY row_number, seat_number
        """
        return query(sql, [hall_id]) or []

    @staticmethod
    def get_rows_summary(hall_id):
        """Получить сводку по рядам (для управления ценами)"""
        sql = """
            SELECT row_number, 
                   COUNT(*) as seats_count,
                   MIN(seat_extra_price) as min_price,
                   MAX(seat_extra_price) as max_price
            FROM seat 
            WHERE hall_id = %s 
            GROUP BY row_number
            ORDER BY row_number
        """
        return query(sql, [hall_id]) or []
