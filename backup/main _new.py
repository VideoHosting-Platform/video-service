from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Request

from minio import Minio

from dotenv import load_dotenv
from datetime import timedelta

import uuid
import httpx
import os

from .shemas import Url_request, WorkflowRequest
from .utils import get_resolution


app = FastAPI()

# загрузка переменных окружения
load_dotenv("./.env.dev")  
MINIO_USER = os.environ.get("MINIO_USER")
MINIO_PASSWORD = os.environ.get("MINIO_PASSWORD")
MINIO_PORT = os.environ.get("MINIO_PORT")
# TOKEN = os.environ.get("TOKEN")

# настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Разрешённые домены (или ["*"] для всех)
    allow_credentials=True,  # Разрешить куки и заголовки авторизации
    allow_methods=["*"],  # Разрешить все методы (GET, POST, PUT, DELETE и т. д.)
    allow_headers=["*"],  # Разрешить все заголовки
)

# клиент минио
client = Minio(
    MINIO_PORT,
    access_key=MINIO_USER,
    secret_key=MINIO_PASSWORD,
    secure=False
)

# генерация ссылки для загруженного в минио видео 
@app.post("/generate-presigned-url")
async def generate_presigned_url(url: Url_request):
    url = client.presigned_put_object(
        "videos", # имя бакета, куда загружаются видео
        url.fileName, 
        expires=timedelta(hours=1)
    )
    return {"presigned_url":url}

# получение нотификаций о загрузке видео с минио
@app.post("/webhook")
async def handle_webhook(request: Request):
    data = await request.json()
    print(f"Event received: {data}")
    return {"status": "ok"}

# запуск воркфлоу
@app.post("/create-workflow-http")
async def create_workflow_http(request: WorkflowRequest):
    namespace = "argo"
    token = open("app/fastapi-token.txt").read()
    filename = "BigBuckBunny_640x360.m4v"
    video_id = str(uuid.uuid4())[:8]
    preset = get_resolution(filename)
    
    print(f"filename: {filename}\nuuid: {video_id}\npreset: {preset}")

    workflow_manifest = {
        "apiVersion": "argoproj.io/v1alpha1",
        "kind": "Workflow",
        "metadata": {
            "generateName": "video-processing-",
            "namespace": "argo"
        },
        "spec": {
            "workflowTemplateRef": {
                "name": "video-processing"
            },
            "arguments": {
                "parameters": [
                    {"name": "video_path", "value": filename},
                    {"name": "uuid", "value": video_id},
                    {"name": "preset", "value": preset}
                ]
            }
        }
    }
    if preset:
        async with httpx.AsyncClient(
            # verify="/var/run/secrets/kubernetes.io/serviceaccount/ca.crt"
            verify="/home/andrew/.minikube/ca.crt"
        ) as client:
            response = await client.post(
                f"https://192.168.49.2:8443/apis/argoproj.io/v1alpha1/namespaces/{namespace}/workflows",
                headers={
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json"
                },
                json=workflow_manifest
            )
        
        if response.status_code != 201:
            raise HTTPException(status_code=response.status_code, detail=response.text)
        
        return response.json()
    else:
        raise HTTPException(status_code=404, detail="Разрешение не определено")
