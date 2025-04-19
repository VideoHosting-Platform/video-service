from typing import Union

from fastapi import FastAPI, HTTPException
from fastapi import Request
from fastapi.middleware.cors import CORSMiddleware

from minio import Minio
import httpx
from datetime import timedelta

from dotenv import load_dotenv
import os
from typing import Dict, Any
from pydantic import BaseModel

from kubernetes import client as kube_client, config 

app = FastAPI()

# Конфигурация
ARGO_EVENTS_WEBHOOK_URL = "http://argo-events-event-source-svc.argo-events.svc.cluster.local:12000/video-processing"

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
    "minio.minio.svc.cluster.local:9000",
    access_key=MINIO_USER,
    secret_key=MINIO_PASSWORD,
    secure=False
)


class Url_request(BaseModel):
    fileName: str # input.mp4
    fileType: str # video/mp4

class WorkflowRequest(BaseModel):
    name: str
    # другие параметры вашего workflow


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
    # print(f"video_path: {data["Key"]}")

    # video_path = data["Key"]
    # uuid = str(get_uuid())
    # preset = str(get_preset())


    # try:
    #     async with httpx.AsyncClient() as client:
    #         response = await client.post(
    #             ARGO_EVENTS_WEBHOOK_URL,
    #             json={
    #                 "video_path": video_path,
    #                 "uuid": uuid,
    #                 "preset": preset,
    #                 "skip_processing": "False" # Обработка видео, а не тест
    #             },
    #             timeout=30.0
    #         )
    #         response.raise_for_status()
    #         return {"status": "success", "message": "Video processing started"}
    # except httpx.HTTPStatusError as e:
    #     raise HTTPException(status_code=e.response.status_code, detail=str(e))
    # except Exception as e:
    #     raise HTTPException(status_code=500, detail=str(e))

    # url = client.presigned_get_object(
    # "videos",  # Имя бакета
    # data["Key"].split("/")[1],  # Имя файла
    # expires=timedelta(hours=1)
    # )
    # print("загрузка", url)
    return {"status": "ok"}

@app.post("/post-processing") # поменять
async def post_process():
    return {"status": "ok"}

# DB
# uuid pk
# filename
# is_processed


# 

import httpx
import os

verif = "MIIDBjCCAe6gAwIBAgIBATANBgkqhkiG9w0BAQsFADAVMRMwEQYDVQQDEwptaW5pa3ViZUNBMB4XDTI1MDQxMTIwNTAyNFoXDTM1MDQxMDIwNTAyNFowFTETMBEGA1UEAxMKbWluaWt1YmVDQTCCASIwDQYJKoZIhvcNAQEBBQADggEPADCCAQoCggEBALMvNhVrpL3bddthkHY19Zgq0OU/WPRT663gEuglPgKZ1RaAFA4ZTnYYjpvLlw3mSvlNs7RVAP90YGT88OpSBUu9bREl9UdPfXFmz/xk5zH8q9oCk0av/UWLFt07jFIH5pUFARGq+vaGt84Jdg8kgM7vj9/4nu4Zzn8n8NkoWRqWaWSh/BndTmU5N74sNpmoslv8BfbrTNkPi+nbSS/pyUcuojHfX6YRh4sBGLpvUNbZMC0yHX7Cn3y5vGNHR5O1VOfsYnAvFrKI3/tRPXX9zgAEerJC9vQIe/mMZdhCid4n/1iSsYkjpSB+aRC6QFX98w+p3FomNH3V8KB/+FCll/kCAwEAAaNhMF8wDgYDVR0PAQH/BAQDAgKkMB0GA1UdJQQWMBQGCCsGAQUFBwMCBggrBgEFBQcDATAPBgNVHRMBAf8EBTADAQH/MB0GA1UdDgQWBBTOMRKGDUQENfW49u7yo5ZfHvespTANBgkqhkiG9w0BAQsFAAOCAQEAp/PRgz+3RC15ysU9at3aJGWOtl/kvyCR22c+0YwIrWbeu5L8X4q0No4nPFlfhLhB3CgzQdMIN/lrKcZn6Kj7K4DyO3BdcxCNuzTdvYlBPl/fSzvCy+ytvtdz6XtJH+AAg2mQMc8LuQwyOy1KlrmICokPEcr3KFuQRIGTNnPpucvEwc3aPvyZESb6QNQV7jyvEJHllTjYOdUr8RqVp3dmeUZ2ksI9Ntq2DiwJwgRzcGffop6tUMmtvT00xC3Lhn95Wr4E8n5ZDaAbqg6Znjn6WUIXcg7lkK8qk4ZxO0jIMPBfsNuhOoLDV1esbJa595Y+GHbMuRH9ARvr1HDt88D0OQ=="

proxy_verif = "MIIDDDCCAfSgAwIBAgIBATANBgkqhkiG9w0BAQsFADAYMRYwFAYDVQQDEw1wcm94eUNsaWVudENBMB4XDTI1MDQxMTIwNTAyNFoXDTM1MDQxMDIwNTAyNFowGDEWMBQGA1UEAxMNcHJveHlDbGllbnRDQTCCASIwDQYJKoZIhvcNAQEBBQADggEPADCCAQoCggEBAOok/pSh6A78HfenBFWWQpgqat52r5eURFe454qI/a2VVOlSzf0wTJz6DUURO9FO463IwL6iQSrDzMzctd90g65yfDgabDyRs5L/Qq42Y/82iC7PyYd+M3J29yWAxQ+8rL8nKZWp9ePIeSEpKa2+mJZh2b4UG/0T/ebJCoFP5k5l+Ea3F0KXs/i3Hy21VPYdLCIBjAI3vuAykZTKrEqGlYejTFtioCGKMZiwikQIDccgHorjU+X94fsVH3Ip9iktCe80mvGHcDAuiAp65vTcopvyzNnbJOYHqBb/8KPeg4ENe3DBIsnGVPW350pCzEXiFufrdOn/QofgnySAmTmB8psCAwEAAaNhMF8wDgYDVR0PAQH/BAQDAgKkMB0GA1UdJQQWMBQGCCsGAQUFBwMCBggrBgEFBQcDATAPBgNVHRMBAf8EBTADAQH/MB0GA1UdDgQWBBT0qyzRxT5invcTZfh251yU8GvOWDANBgkqhkiG9w0BAQsFAAOCAQEA2oEN10PZVQbtVctrxiWQ39Y7tocrr+Aehp1yezYP5TZdZbqmcmv7NPv98Up9ABKdTIY+723aaBWitu/U/Q/eEJlc1CuhPKn7/wFvzhrR0pK7MUcAW7WoxAlqbcCnPDGUK4bV8fgZSAx+woktlEMkznFUZmCoaIJdDxDa5GYvYlGRATwHj9Q+9pqh2a89bhWmF4KOWmBGC0B3++gMkaz7gHOie0HiXUDJPi1XCohWqkrYrbUbi/0mGhXEb61GFEJDYBO0EpuVc1xqOCyZtCx/6lY9XP6Vf6zHLwxxdPBbZbtAUtsqcwevyzq19i2ZVvkMRWEj+3OCTskJHA2DkweG0g=="

@app.post("/create-workflow-http")
async def create_workflow_http(request: WorkflowRequest):
    namespace = "argo"
    token = open("fastapi-token.txt").read()
    
    workflow_manifest = {
        "apiVersion": "argoproj.io/v1alpha1",
        "kind": "Workflow",
        "metadata": {
            "generateName": f"{request.name}-",
            "namespace": namespace
        },
        "spec": {
            "entrypoint": "main",
            "templates": [
                {
                    "name": "main",
                    "container": {
                        "image": "alpine:latest",
                        "command": ["echo", "Hello from Argo!"]
                    }
                }
            ]
        }
    }


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