# ПРОВЕРКА АВТОРИЗАЦИИ ПОЛЬЗОВАТЕЛЕЙ

import psycopg2
import sys
import io
from datetime import datetime

# Настраиваем вывод консоли на UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("ПРОСМОТР БАЗЫ ДАННЫХ")
print("=" * 60)

# Подключаемся к базе
conn = psycopg2.connect(
    dbname="map_navigator",
    user="postgres",
    password="27011983",
    host="localhost",
    port="5432"
)
cursor = conn.cursor()

# ========== ПРОВЕРЯЕМ ТАБЛИЦУ ПОЛЬЗОВАТЕЛЕЙ ==========
print("\n👥 ТАБЛИЦА USERS:")
print("-" * 40)

cursor.execute("SELECT * FROM users;")
users = cursor.fetchall()

if users:
    print(f"Всего пользователей: {len(users)}\n")
    for user in users:
        print(f"┌─────────────────────────────────")
        print(f"│ ID:        {user[0]}")
        print(f"│ Email:     {user[1]}")
        print(f"│ Хеш пароля: {user[2][:30]}...")  # показываем только начало хеша
        print(f"└─────────────────────────────────")
else:
    print("Пользователей пока нет")

# ========== ПРОВЕРЯЕМ ТАБЛИЦУ КОДОВ ==========
print("\n\nТАБЛИЦА EMAIL_CODES:")
print("-" * 40)

cursor.execute("""
    SELECT ec.*, u.email 
    FROM email_codes ec
    LEFT JOIN users u ON ec.user_id = u.id
    ORDER BY ec.expires_at DESC;
""")
codes = cursor.fetchall()

if codes:
    print(f"Всего кодов: {len(codes)}\n")
    for code in codes:
        # Определяем статус кода
        now = datetime.now()
        is_expired = code[3] < now  # code[3] - это time
        
        status = "Действителен" if not code[4] and not is_expired else "❌ "
        if code[4]:
            status += "Использован"
        elif is_expired:
            status += "Просрочен"
        
        print(f"┌─────────────────────────────────")
        print(f"│ ID:          {code[0]}")
        print(f"│ Пользователь: {code[5]} (ID: {code[1]})")
        print(f"│ Код:         {code[2]}")
        print(f"│ Действителен до: {code[3]}")
        print(f"│ Статус:      {status}")
        print(f"└─────────────────────────────────")
else:
    print("Кодов пока нет")
    print("(войдите в аккаунт, чтобы получить код)")

# ========== ПОКАЗЫВАЕМ СВЯЗИ ==========
print("\n\nСВЯЗИ МЕЖДУ ТАБЛИЦАМИ:")
print("-" * 40)

cursor.execute("""
    SELECT 
        u.id,
        u.email,
        COUNT(ec.id) as code_count,
        MAX(ec.expires_at) as last_code_time
    FROM users u
    LEFT JOIN email_codes ec ON u.id = ec.user_id
    GROUP BY u.id, u.email;
""")
relations = cursor.fetchall()

if relations:
    for rel in relations:
        print(f"Пользователь {rel[1]} (ID: {rel[0]})")
        print(f"   ├─ Всего кодов: {rel[2]}")
        if rel[3]:
            print(f"   └─ Последний код отправлен: {rel[3]}")
        else:
            print(f"   └─ Кодов не было")
else:
    print("Нет данных для отображения связей")

cursor.close()
conn.close()

print("\n" + "=" * 60)
print("Проверка завершена!")
