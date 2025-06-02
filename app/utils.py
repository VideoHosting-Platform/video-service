import aio_pika
import asyncio
import json

from app.config import settings
from app.models import Video
from app.database import async_session_maker  

RABBITMQ_HOST = settings.RABBITMQ_HOST
RABBITMQ_QUEUE = settings.RABBITMQ_QUEUE


async def process_message(message: aio_pika.IncomingMessage):
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
        print("Invalid JSON format")
        await message.nack(requeue=False)
    except KeyError as e:
        print(f"Missing required field: {e}")
        await message.nack(requeue=False)
    except Exception as e:
        print(f"Processing failed: {e}")
        await message.nack(requeue=True)  # повторная попытка для временных ошибок

async def start_consumer():
    connection = await aio_pika.connect_robust(
        f"amqp://{RABBITMQ_HOST}/"
    )
    
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

