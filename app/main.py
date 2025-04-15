from typing import Union

from fastapi import FastAPI
from fastapi import Request
from fastapi.middleware.cors import CORSMiddleware

from minio import Minio
from datetime import timedelta

from minio import Minio
from datetime import timedelta

from dotenv import load_dotenv
import os
from typing import Dict, Any
from pydantic import BaseModel

app = FastAPI()

load_dotenv("./.env.dev")  
MINIO_USER = os.environ.get('MINIO_USER')
MINIO_PASSWORD = os.environ.get('MINIO_PASSWORD')

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Разрешённые домены (или ["*"] для всех)
    allow_credentials=True,  # Разрешить куки и заголовки авторизации
    allow_methods=["*"],  # Разрешить все методы (GET, POST, PUT, DELETE и т. д.)
    allow_headers=["*"],  # Разрешить все заголовки
)

client = Minio(
    "localhost:9000",
    access_key=MINIO_USER,
    secret_key=MINIO_PASSWORD,
    secure=False
    )

class Url_request(BaseModel):
    fileName: str
    fileType: str

@app.get("/")
async def read_root():
    return {"Hello": "Ifbest"}

@app.post("/generate-presigned-url")
async def generate_presigned_url(url: Url_request):
    url = client.presigned_put_object(
        "videos",
        url.fileName,
        expires=timedelta(hours=1)
    )
    return {"presigned_url":url}

@app.post("/webhook")
async def handle_webhook(request: Request):
    data = await request.json()
    print(f"Event received: {data}")

    url = client.presigned_get_object(
    "videos",  # Имя бакета
    data["Key"].split("/")[1],  # Имя файла
    expires=timedelta(hours=1)
    )
    print("заггрузка", url)
    return {"status": "ok"}

# Порядок команд для настройки нотификации в minio
# 1) Зарегистрировать вебхук в миинио:  mc admin config set local notify_webhook:service endpoint="http://172.17.0.1:8000/webhook"
# 2) Перезапустить сервер: mc admin service restart local
# 3) Сделать вебхук пунктом назначения при создании объектов в бакете videos(put почему-то): mc event add local/videos arn:minio:sqs::service:webhook --event put
# 4)