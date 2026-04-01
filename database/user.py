# СОЗДАНИЕ ТАБЛИЦЫ ПОЛЬЗОВАТЕЛЕЙ И КОДОВ 2FA

import psycopg2
import sys
import io

# Настраиваем вывод консоли на UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


# Подключаемся к базе
conn = psycopg2.connect(
    dbname="map_navigator",
    user="postgres",
    password="27011983",
    host="localhost",
    port="5432"
)
cursor = conn.cursor()

cursor.execute("DROP TABLE IF EXISTS email_codes;")
cursor.execute("DROP TABLE IF EXISTS users;")

# Создаём таблицу пользователей
cursor.execute("""
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(100) UNIQUE NOT NULL,
    HASHED_password VARCHAR(200) NOT NULL
);
""")


# Создаём таблицу кодов для 2FA
cursor.execute("""
CREATE TABLE email_codes (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    code VARCHAR(5) NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    is_used BOOLEAN DEFAULT FALSE
);
""")

# Создаём таблицу избранных маршрутов
cursor.execute("""
CREATE TABLE favorite_routes (
    id SERIAL PRIMARY KEY,                                 
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,   
    from_city_id INTEGER REFERENCES cities(id) ON DELETE CASCADE,  
    to_city_id INTEGER REFERENCES cities(id) ON DELETE CASCADE,   
    route_name VARCHAR(100),     
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,     
    UNIQUE(user_id, from_city_id, to_city_id)    
);
""")

conn.commit()

cursor.close()
conn.close()
