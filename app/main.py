from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Request


from contextlib import asynccontextmanager

# from minio import Minio
import asyncio

import threading
import json
import pika

from dotenv import load_dotenv
from datetime import timedelta

import uuid
import httpx
import os

from app.schemas import Url_request, WorkflowRequest
# from app.utils import get_resolution

from app.schemas import VideoCreate, VideoReturn
from app.models import Video

from functools import wraps

from app.database import get_session

from sqlalchemy import insert, select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi import Depends


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Код выполнится при старте приложения
    thread = threading.Thread(target=start_consumer, daemon=True)
    thread.start()
    yield
    # Код выполнится при остановке приложения (опционально)
    print("Приложение завершает работу")

app = FastAPI(lifespan=lifespan)

# загрузка переменных окружения
load_dotenv("./.env")  
# MINIO_USER = os.environ.get("MINIO_USER")
# MINIO_PASSWORD = os.environ.get("MINIO_PASSWORD")
# MINIO_PORT = os.environ.get("MINIO_PORT")
# TOKEN = os.environ.get("TOKEN")

RABBITMQ_HOST = "localhost"
RABBITMQ_QUEUE = "db_upload"  # очередь, из которой читаем

# настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Разрешённые домены (или ["*"] для всех)
    allow_credentials=True,  # Разрешить куки и заголовки авторизации
    allow_methods=["*"],  # Разрешить все методы (GET, POST, PUT, DELETE и т. д.)
    allow_headers=["*"],  # Разрешить все заголовки
)

# клиент минио
# client = Minio(
#     MINIO_PORT,
#     access_key=MINIO_USER,
#     secret_key=MINIO_PASSWORD,
#     secure=False
# )


@app.post("/read_queue", status_code=200)
async def get_result():
    # data = await request.json()
    # print(f"Processed video with id: {data}")
    return {"status": "ok"}

# получение нотификаций о загрузке видео с минио
# @app.post("/webhook")
# async def handle_webhook(request: Request):
#     data = await request.json()
#     print(f"Event received: {data}")

#     namespace = "argo"
#     # token = open("app/fastapi-token.txt").read()
#     token = open("/var/run/secrets/kubernetes.io/serviceaccount/token").read()
#     # filename = "BigBuckBunny_640x360.m4v"
#     filename = data["Key"].split("/")[1]
#     video_id = str(uuid.uuid4())[:8]
#     preset = get_resolution(filename)
    
#     print(f"filename: {filename}\nuuid: {video_id}\npreset: {preset}")

#     workflow_manifest = {
#         "apiVersion": "argoproj.io/v1alpha1",
#         "kind": "Workflow",
#         "metadata": {
#             "generateName": "video-processing-",
#             "namespace": "argo"
#         },
#         "spec": {
#             "workflowTemplateRef": {
#                 "name": "video-processing"
#             },
#             "arguments": {
#                 "parameters": [
#                     {"name": "video_path", "value": filename},
#                     {"name": "uuid", "value": video_id},
#                     {"name": "preset", "value": preset}
#                 ]
#             }
#         }
#     }
#     if preset:
#         async with httpx.AsyncClient(
#             # verify="/home/andrew/.minikube/ca.crt"
#             verify="/var/run/secrets/kubernetes.io/serviceaccount/ca.crt"
#         ) as client:
#             response = await client.post(
#                 # f"https://192.168.49.2:8443/apis/argoproj.io/v1alpha1/namespaces/{namespace}/workflows",
#                 f"https://kubernetes.default.svc/apis/argoproj.io/v1alpha1/namespaces/{namespace}/workflows",
#                 headers={
#                     "Authorization": f"Bearer {token}",
#                     "Content-Type": "application/json"
#                 },
#                 json=workflow_manifest
#             )
        
#         if response.status_code != 201:
#             raise HTTPException(status_code=response.status_code, detail=response.text)
        
#         return response.json()
#     else:
#         raise HTTPException(status_code=404, detail="Разрешение не определено")

@app.post("/result", status_code=200)
async def get_result(request: Request):
    data = await request.json()
    print(f"Processed video with id: {data}")
    return {"status": "ok"}

# обработка сообщения с rabbitmq
def process_message(ch, method, properties, body):
    try:
        print(body.decode()) # string
        # message = json.loads(body)
        # print(f"Получено сообщение: {message}")
        # Запись в БД
        # ...

        ch.basic_ack(delivery_tag=method.delivery_tag) # подтверждение обработки
    except Exception as e:
        print(f"Ошибка обработки сообщения: {e}")

# запуск консюмера в отдельном потоке
def start_consumer():
    connection = pika.BlockingConnection(pika.ConnectionParameters(RABBITMQ_HOST))
    channel = connection.channel()

    # Объявляем очередь (на случай, если её ещё нет)
    channel.queue_declare(queue=RABBITMQ_QUEUE, durable=True)

    # Настраиваем потребителя
    channel.basic_consume(
        queue=RABBITMQ_QUEUE,
        on_message_callback=process_message,
        auto_ack=False,  # отключаем автоматическое подтверждение
    )

    print("Ожидание сообщений...")
    channel.start_consuming()


def check_result(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        result = await func(*args, **kwargs)
        if not result:
            raise HTTPException(404, 'Not found')
        return result
    return wrapper

@app.post("/video-add", response_model=VideoReturn, status_code=status.HTTP_201_CREATED)
@check_result
async def add_product(data: VideoCreate, session: AsyncSession = Depends(get_session)):
    
   # Создаем объект Video
    video = Video(
        title=data.title,
        video_url=data.video_url,
    )
    
    # Добавляем в сессию
    session.add(video)
    
    # Фиксируем изменения
    await session.commit()
    
    # Обновляем объект (чтобы получить сгенерированный ID)
    await session.refresh(video)
    print(video)

    return VideoReturn(
        id=video.id,
        title=video.title,
        video_url=video.video_url,
        views=video.views,
        likes=video.likes,
        dislikes=video.dislikes
)