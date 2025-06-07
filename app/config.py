from pydantic_settings import BaseSettings    
import os
# from dotenv import load_dotenv

class Settings(BaseSettings):
    DB_NAME: str 
    DB_USER: str
    DB_PASS: str
    DB_HOST: str
    DB_PORT: int
    RABBITMQ_USER: str
    RABBITMQ_PASSWORD: str
    RABBITMQ_HOST: str
    RABBITMQ_PORT: str
    RABBITMQ_QUEUE: str 

# для работы без кубера. Должен быть .env файл
# load_dotenv(".env")

settings = Settings()
DATABASE_URL = f'postgresql+asyncpg://{settings.DB_USER}:{settings.DB_PASS}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}'
