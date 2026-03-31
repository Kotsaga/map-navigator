# ОТПРАВКА ПИСЕМ

from fastapi_mail import FastMail, MessageSchema, ConnectionConfig

# НАСТРОЙКИ ПОЧТЫ 
conf = ConnectionConfig(
    MAIL_USERNAME="ritakotsaga06@gmail.com",  
    MAIL_PASSWORD="uwst ohjn gbyl ydio",     
    MAIL_FROM="ritakotsaga06@gmail.com",       
    MAIL_PORT=587,
    MAIL_SERVER="smtp.gmail.com",
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True
)

async def send_2fa_code(email: str, code: str):
    """Отправляет код подтверждения на почту"""
    message = MessageSchema(
        subject="Код для входа в Навигатор",
        recipients=[email],
        body=f"""
        <html>
            <body style="font-family: Arial, sans-serif;">
                <h2>Код подтверждения</h2>
                <p>Для входа введите этот код:</p>
                <h1 style="font-size: 36px; letter-spacing: 5px; background: #f0f0f0; padding: 10px; text-align: center;">
                    {code}
                </h1>
                <p>Код действителен 5 минут.</p>
                <hr>
                <p style="color: #666; font-size: 12px;">Map Navigator</p>
            </body>
        </html>
        """,
        subtype="html"
    )
    
    fm = FastMail(conf)
    await fm.send_message(message)
    return True