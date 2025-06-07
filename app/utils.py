import aio_pika
import asyncio
import json

from app.config import settings
from app.models import Video
from app.database import async_session_maker  

import logging

RABBITMQ_USER = settings.RABBITMQ_USER
RABBITMQ_PASS = settings.RABBITMQ_PASS
RABBITMQ_HOST = settings.RABBITMQ_HOST
RABBITMQ_PORT = settings.RABBITMQ_PORT
RABBITMQ_QUEUE = settings.RABBITMQ_QUEUE


async def process_message(message: aio_pika.IncomingMessage):
    print("process message")
    try:
        data = json.loads(message.body.decode())
        print(f"Received message: {data}")
        
        async with async_session_maker() as session:
            video = Video(
                title=data["video_title"],
                video_url=data["video_master_playlist_url"],
                video_id=data["video_id"]
            )
            session.add(video)
            await session.commit()
        
        await message.ack() # подтверждение, что сообщение прочитано
        print("Message processed successfully")
        
    except json.JSONDecodeError:
        print("Received message with invalid JSON format")
        await message.nack(requeue=False)
    except KeyError as e:
        print(f"Missing required field: {e}")
        await message.nack(requeue=False)
    except Exception as e:
        print(f"Processing failed: {e}")
        await message.nack(requeue=True)  # повторная попытка для временных ошибок


logger = logging.getLogger(__name__)

async def start_consumer():
    try:
        logger.info("Подключение к RabbitMQ")
        logger.info("HOST IS ", RABBITMQ_HOST, settings.RABBITMQ_HOST)
        connection = await aio_pika.connect_robust(
            f"amqp://{settings.RABBITMQ_USER}:{settings.RABBITMQ_PASS}@{settings.RABBITMQ_HOST}:{settings.RABBITMQ_PORT}/"
        )

        logger.info("Успешное подключение!")
    except Exception as e:
        logger.error(f"Ошибка: {e}", exc_info=True)
        raise
    
    async with connection:
        # канал связи для работы с очредями
        channel = await connection.channel()
        # получать только 1 сообщение за раз
        # следующее сообщение придёт после подтверждения текущего
        await channel.set_qos(prefetch_count=1)
        
        # cоздаёт очередь, если её не существует
        queue = await channel.declare_queue(
            RABBITMQ_QUEUE,
            durable=True
        )
        
        print("Consumer started. Waiting for messages...")
        await queue.consume(process_message)
        
        # бесконечный цикл ожидания
        while True:
            await asyncio.sleep(1)

