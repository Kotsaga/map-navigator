# ОСНОВНАЯ ПРОГРАММА - СОЗДАЕТ API-СЕРВЕР

from fastapi import FastAPI, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware   
from database import get_bd_connected, create_user, get_user_by_email, save_email_code, verify_email_code
from psycopg2.extras import RealDictCursor  
from auth import verify_password, generate_code
from email_utils import send_2fa_code   

# Создаём приложение 
app = FastAPI(title="Навигатор")

# Контроль запросов
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Главная страница API
@app.get("/")    #функция, обрабатывающая запросы
def read_root():
    return {"Навигатор подключен!"}

# Получить список всех городов
@app.get("/cities")
def get_cities():
    conn = get_bd_connected()
    if not conn:
        raise HTTPException(status_code=500, detail="Ошибка подключения к БД")
    
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)    #получаем словарь
        cur.execute("SELECT id, name, description, latitude, longitude FROM cities ORDER BY name;")
        cities = cur.fetchall()   #получаем всё
        cur.close()
        return cities
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()  #закрываем соединение

# Получить информацию о конкретном городе по ID
@app.get("/cities/{city_id}")
def get_city(city_id: int):
    conn = get_bd_connected()
    if not conn:
        raise HTTPException(status_code=500, detail="Ошибка подключения к БД")
    
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)  #получаем словарь
        cur.execute("SELECT id, name, description, latitude, longitude FROM cities WHERE id = %s;", (city_id,))
        city = cur.fetchone()   #получаем информацию по одному городу
        cur.close()
        
        if city is None:
            raise HTTPException(status_code=404, detail="Город не найден")
        
        return city
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()


@app.post("/register")
def register(email: str = Form(...), password: str = Form(...)):
    existing_user = get_user_by_email(email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email уже зарегистрирован")

    user_id = create_user(email, password)
    if not user_id:
        raise HTTPException(status_code=500, detail="Ошибка создания пользователя")

    return {"message": "Пользователь успешно зарегистрирован", "user_id": user_id}

@app.post("/login")
async def login(email: str = Form(...), password: str = Form(...)):
    """
    Первый шаг входа: проверяем email/пароль и отправляем код на почту
    """
    # Ищем пользователя
    user = get_user_by_email(email)
    if not user:
        raise HTTPException(status_code=401, detail="Неверный email или пароль")
    
    # Проверяем пароль
    if not verify_password(password, user['hashed_password']):
        raise HTTPException(status_code=401, detail="Неверный email или пароль")
    
    # Генерируем код
    code = generate_code()
    print(f"Код для {email}: {code}")  
    
    # Сохраняем код в БД
    save_email_code(user['id'], code)
    
    # Отправляем код на почту
    try:
        await send_2fa_code(email, code)
    except Exception as e:
        print(f"Ошибка отправки email: {e}")
        # В разработке продолжаем, даже если почта не отправилась
    
    return {
        "message": "Код подтверждения отправлен на email",
        "user_id": user['id'],
        "debug_code": code  # Убрать в продакшене!
    }


@app.post("/verify-code")
def verify_code(user_id: int = Form(...), code: str = Form(...)):
    """
    Второй шаг входа: проверяем код и возвращаем данные пользователя
    """
    # Проверяем код
    if not verify_email_code(user_id, code):
        raise HTTPException(status_code=401, detail="Неверный или просроченный код")
    
    # Получаем данные пользователя
    conn = get_bd_connected()
    if not conn:
        raise HTTPException(status_code=500, detail="Ошибка подключения к БД")
    
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT id, email FROM users WHERE id = %s", (user_id,))
        user = cur.fetchone()
        
        return {
            "message": "Вход выполнен успешно",
            "user": user
        }
    finally:
        conn.close()


@app.get("/profile/{user_id}")
def get_profile(user_id: int):
    """
    Получение профиля пользователя (простой защищённый маршрут)
    """
    conn = get_bd_connected()
    if not conn:
        raise HTTPException(status_code=500, detail="Ошибка подключения к БД")
    
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT id, email FROM users WHERE id = %s", (user_id,))
        user = cur.fetchone()
        
        if not user:
            raise HTTPException(status_code=404, detail="Пользователь не найден")
        
        return user
    finally:
        conn.close()


# Для запуска: uvicorn main:app --reload
if __name__ == "__main__":
    import uvicorn    #подключаем сервер uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)