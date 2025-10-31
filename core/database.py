import psycopg2

def query(sql, params=None):
    try:
        with psycopg2.connect("dbname=cinemavaib_db host=localhost port=5432 user=postgres") as conn:
            with conn.cursor() as cur:
                cur.execute(sql, params)
                if cur.description is not None:
                    return cur.fetchall()
                else:
                    conn.commit()
                    return None
    except Exception as e:
        print(f"Ошибка: {e}")

from PyQt6.QtGui import QStandardItem, QStandardItemModel

def datagrid_model(sql, params=None):
    rows, headers = [], []
    try:
        result = query(sql, params)
        if result is None or len(result) == 0:
            return QStandardItemModel()  # Пуста таблица

        rows_preview = query(sql + " LIMIT 0", params)
        if rows_preview is not None:
            import psycopg2
            with psycopg2.connect("dbname=cinemavaib_db host=localhost port=5432 user=postgres") as conn:
                with conn.cursor() as cur:
                    cur.execute(sql + " LIMIT 0", params)
                    headers = [desc[0] for desc in cur.description]
    except Exception as e:
        print(f"Ошибка datagrid_model(): {e}")
        return QStandardItemModel()

    if not headers and len(result) > 0:
        headers = [f"col_{i}" for i in range(len(result[0]))]

    model = QStandardItemModel()
    model.setColumnCount(len(headers))
    model.setHorizontalHeaderLabels(headers)

    for row in result:
        item_row = [QStandardItem(str(value)) for value in row]
        model.appendRow(item_row)
    return model

def image_to_binary(image):
    return psycopg2.Binary(open(image, "rb").read())

def get_image_from_db(movie_id):
    result = query("SELECT movie_image FROM movies WHERE movie_id = %s", (movie_id,))
    if result and len(result) > 0 and result[0][0] is not None:
        return bytes(result[0][0])
    return None