# РАБОТА С ПАРОЛЯМИ И КОДАМИ

from passlib.context import CryptContext     #для хеширования паролей
import random     #генерация кодов
import string      #работа с наборами символов

password_context = CryptContext(schemes = ["bcrypt"], deprecated = "auto")

#превращаем пароль в хеш
def get_password_hash(password: str) ->str:
    return password_context.hash(password)  

#функция провнрки пароля
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_context.verify(plain_password, hashed_password)

#функция генерации кода
def generate_code (length: int = 5) ->str:
    code = ''.join(random.choices(string.digits, k = length))
    return code
