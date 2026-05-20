import os
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

# Завантажуємо змінні оточення з .env файлу
load_dotenv()

# Отримуємо DATABASE_URL для Neon PostgreSQL
DATABASE_URL = os.getenv("DATABASE_URL")

# Перевіряємо чи DATABASE_URL визначена
if not DATABASE_URL:
    raise ValueError("DATABASE_URL не визначена в .env файлі")

# Створюємо engine для підключення до бази даних
# Neon потребує SSL-підключення, яке вже налаштовано в DATABASE_URL
engine = create_engine(
    DATABASE_URL,
    echo=False  # Встановіть на True для див SQL запитів у консолі
)

# Створюємо фабрику сесій SessionLocal
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Створюємо базовий клас для всіх моделей
Base = declarative_base()


# Функція-залежність для отримання сесії бази даних (для FastAPI)
def get_db() -> Generator:
    """
    Генератор, що забезпечує сесію бази даних для кожного запиту.
    Автоматично закриває сесію після використання.
    
    Yields:
        SessionLocal: Сесія для взаємодії з БД
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
