from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncAttrs, AsyncSession
from sqlalchemy.orm import DeclarativeBase, declared_attr

from app.config import DATABASE_URL

engine = create_async_engine(DATABASE_URL)

async_session_maker = async_sessionmaker(engine, expire_on_commit=False)


async def get_session():
    async with async_session_maker() as session:
        yield session


class Base(DeclarativeBase):
    __abstract__ = True # Указание, что это не модель и не надо создавать таблицу

    @declared_attr.directive # Указание, что это не обычный метод
    def __tablename__(cls) -> str: # задает названия таблиц моделей в виде имени модели в нижнем регистре
        return f"{cls.__name__.lower()}s"