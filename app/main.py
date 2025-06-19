from fastapi import FastAPI, HTTPException, status, Depends, Response
from fastapi.middleware.cors import CORSMiddleware

from contextlib import asynccontextmanager
from functools import wraps
from sqlalchemy import delete, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
import asyncio

from app.schemas import VideoCreate, VideoReturn
from app.models import Video
from app.database import get_session
from app.utils import start_consumer

import logging
from typing import List


# Настройка базового логера
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

# логгер для main.py
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    
    logger.info("Consumer starting...")
    consumer_task = asyncio.create_task(start_consumer())
    yield
    logger.info("Consumer stopping...")
    consumer_task.cancel()
    try:
        await consumer_task
    except asyncio.CancelledError:
        logger.info("Consumer canceled")
    except Exception as e:
        logger.error(f"Error while stopping consumer: {e}")

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
async def add_video(data: VideoCreate, session: AsyncSession = Depends(get_session)): 
    # проверка, что видео с таким video_id еще нет
    result = await session.execute(select(Video).where(Video.video_id==data.video_id))
    if result.scalar_one_or_none() is not None:
        raise HTTPException(
            status_code=400,
            detail=f"Incorrect input data"
        )

    video = Video(title=data.title, video_url=data.video_url, video_id=data.video_id)
    session.add(video)
    await session.commit()
    await session.refresh(video) # обновляем объект (чтобы получить сгенерированный ID)

    return video.to_return_model()

@app.get("/video/{video_id}", response_model=VideoReturn, status_code=status.HTTP_200_OK)
async def get_video(video_id: str, session: AsyncSession = Depends(get_session)): 
    result = await session.execute(select(Video).where(Video.video_id==video_id))
    video = result.scalar_one_or_none()
    if not video:
        raise HTTPException(404, "No video with this id")

    return video.to_return_model()

@app.get("/video", response_model=List[VideoReturn], status_code=status.HTTP_200_OK)
async def get_all_videos(session: AsyncSession = Depends(get_session)): 
    # Получаем все видео из базы
    result = await session.execute(select(Video))
    videos = result.scalars().all()
    
    if not videos:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No videos found")
    
    # Преобразуем каждое видео в формат VideoReturn
    return [video.to_return_model() for video in videos]

@app.delete("/video/{video_id}", status_code=status.HTTP_200_OK)
async def delete_video(video_id: str, session: AsyncSession = Depends(get_session)): 
    try:
        result = await session.execute(select(Video).where(Video.video_id == video_id))
        video = result.scalar_one_or_none()
        
        if not video:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No Video with this id"
            )

        await session.execute(delete(Video).where(Video.video_id == video_id).returning(Video.video_id))
        await session.commit()
        
        return {"status": "ok"}
        
    except HTTPException:
        raise
    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting video: {str(e)}"
        )

@app.put("/video/{video_id}", response_model=VideoReturn, status_code=status.HTTP_200_OK)
async def update_video(video_id: str, update_data: VideoCreate, session: AsyncSession = Depends(get_session)):
    try:
        result = await session.execute(select(Video).where(Video.video_id == video_id))
        video = result.scalar_one_or_none()
        
        if not video:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No video with this id"
            )

        update_values = {k: v for k, v in update_data.dict().items() if v is not None}
        
        if not update_values:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No data provided for update"
            )

        await session.execute(update(Video).where(Video.video_id == video_id).values(**update_values))
        await session.commit()

        await session.refresh(video) 
        
        return video.to_return_model()
         
    except HTTPException:
        raise
    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating video: {str(e)}"
        )