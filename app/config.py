from pydantic_settings import BaseSettings    
import os
from dotenv import load_dotenv

class Settings(BaseSettings):
    DB_NAME: str 
    DB_USER: str
    DB_PASS: str
    DB_HOST: str
    DB_PORT: int

load_dotenv(os.getenv("ENV", ".env"), override=True)
settings = Settings()
DATABASE_URL = f'postgresql+asyncpg://{settings.DB_USER}:{settings.DB_PASS}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}'

print(os.getenv("ENV"), settings.DB_NAME)