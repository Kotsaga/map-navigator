# РАБОТА С БД

import psycopg2      #библиотека для работы с бд
from datetime import datetime, timedelta
from psycopg2.extras import RealDictCursor

def get_bd_connected():
    """Подключение к БД"""
    try:
        conn = psycopg2.connect(
            dbname = "map_navigator",   #название бд
            user = "postgres",        #по умолчанию
            password = "27011983",
            host = "localhost",       #по умолчанию
            port = "5432",
            client_encoding='UTF8'
        )

        print("Подключение установлено!") 
        return conn
    except Exception as e:
        print ("Ошибка подключения к БД")
        return None

def create_user(email, password):
    from auth import get_password_hash
    hashed = get_password_hash(password)

    conn = get_bd_connected()
    if not conn:
        return None

    try:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO users (email, hashed_password) VALUES (%s, %s) RETURNING id",
            (email, hashed)
        )
        user_id = cur.fetchone()[0]
        conn.commit()
        return user_id
    except Exception as e:
        print(f"Ошибка создания пользователя: {e}")
        conn.rollback()
        return None
    finally:
        conn.close()

def get_user_by_email(email):
    conn = get_bd_connected()
    if not conn:
        return None
    
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT * FROM users WHERE email = %s", (email,))
        return cur.fetchone()
    finally:
        conn.close()

def save_email_code(user_id, code):
    conn = get_bd_connected()
    if not conn:
        return False
    
    try:
        cur = conn.cursor()
        expires_at = datetime.now() + timedelta(minutes=5)
        cur.execute(
            "INSERT INTO email_codes (user_id, code, expires_at) VALUES (%s, %s, %s)",
            (user_id, code, expires_at)
        )
        conn.commit()
        return True
    except Exception as e:
        print(f"Ошибка сохранения кода: {e}")
        return False
    finally:
        conn.close()

def verify_email_code(user_id, code):
    conn = get_bd_connected()
    if not conn:
        return False
    
    try:
        cur = conn.cursor()
        # Ищем активный код
        cur.execute("""
            SELECT id FROM email_codes 
            WHERE user_id = %s 
            AND code = %s 
            AND expires_at > NOW() 
            AND is_used = FALSE
            ORDER BY expires_at DESC 
            LIMIT 1
        """, (user_id, code))
        
        result = cur.fetchone()
        
        if result:
            # Помечаем код как использованный
            cur.execute("UPDATE email_codes SET is_used = TRUE WHERE id = %s", (result[0],))
            conn.commit()
            return True
        
        return False
    except Exception as e:
        print(f"Ошибка проверки кода: {e}")
        return False
    finally:
        conn.close()

def save_favorite_route(user_id, from_city_id, to_city_id, route_name=None):
    """Сохраняет избранный маршрут"""
    conn = get_bd_connected()
    if not conn:
        return False
    
    try:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO favorite_routes (user_id, from_city_id, to_city_id, route_name)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (user_id, from_city_id, to_city_id) DO NOTHING
        """, (user_id, from_city_id, to_city_id, route_name))
        conn.commit()
        return True
    except Exception as e:
        print(f"Ошибка сохранения маршрута: {e}")
        return False
    finally:
        conn.close()

def get_user_favorite_routes(user_id):
    """Получить все избранные маршруты пользователя"""
    conn = get_bd_connected()
    if not conn:
        return []
    
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("""
            SELECT fr.id, fr.from_city_id, fr.to_city_id, fr.route_name, fr.created_at,
                   c1.name as from_city_name, c2.name as to_city_name,
                   c1.latitude as from_lat, c1.longitude as from_lon,
                   c2.latitude as to_lat, c2.longitude as to_lon
            FROM favorite_routes fr
            JOIN cities c1 ON fr.from_city_id = c1.id
            JOIN cities c2 ON fr.to_city_id = c2.id
            WHERE fr.user_id = %s
            ORDER BY fr.created_at DESC
        """, (user_id,))
        return cur.fetchall()
    finally:
        conn.close()

def delete_favorite_route(user_id, route_id):
    """Удалить избранный маршрут"""
    conn = get_bd_connected()
    if not conn:
        return False
    
    try:
        cur = conn.cursor()
        cur.execute("""
            DELETE FROM favorite_routes 
            WHERE id = %s AND user_id = %s
        """, (route_id, user_id))
        conn.commit()
        return cur.rowcount > 0
    except Exception as e:
        print(f"Ошибка удаления маршрута: {e}")
        return False
    finally:
        conn.close()


if __name__ == "__main__":
    conn = get_bd_connected()
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM cities")
        result = cursor.fetchall()
        print("Города в базе данных:")
        for city in result:
            print(f"  - {city[1]}")  #   название города
        cursor.close()
        conn.close()
    else:
        print("Не удалось подключиться к БД")
