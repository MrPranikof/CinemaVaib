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
        return None