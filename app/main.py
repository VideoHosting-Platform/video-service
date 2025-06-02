from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.middleware.cors import CORSMiddleware

from contextlib import asynccontextmanager
from functools import wraps
from sqlalchemy.ext.asyncio import AsyncSession
import asyncio

from app.schemas import VideoCreate, VideoReturn
from app.models import Video
from app.database import get_session
from app.utils import start_consumer


@asynccontextmanager
async def lifespan(app: FastAPI): # создание асинхронной таски при старте
    consumer_task = asyncio.create_task(start_consumer())
    yield
    consumer_task.cancel() # при завершении приложения
    try:
        await consumer_task
    except asyncio.CancelledError:
        pass
    print("Exiting app...")

app = FastAPI(lifespan=lifespan)


app = FastAPI(lifespan=lifespan)

app.add_middleware( # настройка CORS в middleware
    CORSMiddleware,
    allow_origins=["*"],  # Разрешённые домены (или ["*"] для всех)
    allow_credentials=True,  # Разрешить куки и заголовки авторизации
    allow_methods=["*"],  # Разрешить все методы (GET, POST, PUT, DELETE и т. д.)
    allow_headers=["*"],  # Разрешить все заголовки
)


def check_result(func): # декоратор возвращает ошибку 404 в случае неудачи
    @wraps(func)
    async def wrapper(*args, **kwargs):
        result = await func(*args, **kwargs)
        if not result:
            raise HTTPException(404, 'Not found')
        return result
    return wrapper

@app.post("/video", response_model=VideoReturn, status_code=status.HTTP_201_CREATED)
@check_result
async def add_product(data: VideoCreate, session: AsyncSession = Depends(get_session)): 
    video = Video(title=data.title, video_url=data.video_url)
    session.add(video)
    await session.commit()
    await session.refresh(video) # обновляем объект (чтобы получить сгенерированный ID)

    return VideoReturn(
        id=video.id,
        title=video.title,
        video_url=video.video_url,
        views=video.views,
        likes=video.likes,
        dislikes=video.dislikes
    )

