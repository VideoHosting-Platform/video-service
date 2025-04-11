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


class Url_request(BaseModel):
    fileName: str
    fileType: str

@app.get("/")
async def read_root():
    return {"Hello": "Ifbest"}

@app.post("/generate-presigned-url")
async def generate_presigned_url(url: Url_request):
    client = Minio(
    "localhost:9000",
    access_key=MINIO_USER,
    secret_key=MINIO_PASSWORD,
    secure=False
    )

    url = client.presigned_put_object(
        "videos",
        url.fileName,
        expires=timedelta(hours=1)
    )
    return {"presigned_url":url}