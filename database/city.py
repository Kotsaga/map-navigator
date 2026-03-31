# СОЗДАНИЕ БД И ТАБЛИТЫ ГОРОДОВ

import psycopg2
import sys
import io

# Настраиваем вывод консоли на UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Подключаемся к стандартной базе postgres
conn = psycopg2.connect(
    dbname="postgres",
    user="postgres",
    password="27011983",
    host="localhost",
    port="5432"
)
conn.autocommit = True
cursor = conn.cursor()

# Удаляем старую базу если есть
cursor.execute("DROP DATABASE IF EXISTS map_navigator;")

# Создаём новую базу с UTF8 кодировкой, используя template0
cursor.execute("""
    CREATE DATABASE map_navigator 
    ENCODING 'UTF8' 
    LC_COLLATE 'Russian_Russia.1251' 
    LC_CTYPE 'Russian_Russia.1251'
    TEMPLATE template0;
""")

cursor.close()
conn.close()

# Подключаемся к новой базе
conn = psycopg2.connect(
    dbname="map_navigator",
    user="postgres",
    password="27011983",
    host="localhost",
    port="5432"
)
cursor = conn.cursor()

# Создаём таблицу городов
cursor.execute("""
CREATE TABLE cities (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    latitude DOUBLE PRECISION NOT NULL,
    longitude DOUBLE PRECISION NOT NULL
);
""")

# Вставляем города
cities = [
    ('Москва', 'Столица России', 55.7522, 37.6156),
    ('Санкт-Петербург', 'Второй по численности населения город России', 59.9386, 30.3141),
    ('Пенза', 'Административный город Пензенской области', 53.2007, 45.0046),
    ('Тюмень', 'Один из старейших городов Сибири', 57.1522, 65.5272)
]

for city in cities:
    cursor.execute(
        "INSERT INTO cities (name, description, latitude, longitude) VALUES (%s, %s, %s, %s);",
        city
    )

conn.commit()

# Проверяем результат
cursor.execute("SELECT name, description FROM cities;")
for row in cursor.fetchall():
    print(f"  - {row[0]}: {row[1]}")

cursor.close()
conn.close()
