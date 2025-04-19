from minio import Minio
from datetime import timedelta
import ffmpeg
import requests

client = Minio(
    "localhost:9000",
    access_key="minioadmin",
    secret_key="minioadmin",
    secure=False,
    region="us-east-1",
)

RESOLUTION_SETS = {
    "4K": {
        "high": ["4K", "2K", "1080p"],
        "low": ["720p", "480p", "360p", "240p", "144p"]
    },
    "2K": {
        "high": ["2K", "1080p", "720p"],
        "low": ["480p", "360p", "240p", "144p"]
    },
    "1080p": {
        "high": ["1080p", "720p"],
        "low": ["480p", "360p", "240p", "144p"]
    },
    "720p": {
        "single": ["720p", "480p", "360p", "240p", "144p"]
    }
}

def get_resolution_with_min_download(s3_path):
    data = client.get_object("videos", s3_path, length=1024*1024)
    with open("/tmp/partial.mp4", "wb") as f:
        for chunk in data.stream(32*1024):
            f.write(chunk)
    
    height = ffmpeg.probe("/tmp/partial.mp4", select_streams="v:0", show_entries="stream=height")["streams"][0]["height"]
    print(height)
    return height

async def process_video(video_uri: str):
    # Получаем разрешение (как ранее)
    height = get_resolution_with_min_download(video_uri)
    
    # Определяем наборы для обработки
    if height >= 2160:
        resolution_set = "4K"
    elif height >= 1440:
        resolution_set = "2K"
    elif height >= 1080:
        resolution_set = "1080p"
    else:
        resolution_set = "720p"
    
    config = RESOLUTION_SETS[resolution_set]
    
    # Отправляем ивенты
    if "single" in config:
        requests.post("http://argo-events/trigger", json={
            "video_uri": video_uri,
            "resolutions": config["single"],
            "node_type": "any"
        })
    else:
        requests.post("http://argo-events/trigger", json={
            "video_uri": video_uri,
            "resolutions": config["high"],
            "node_type": "high"
        })
        requests.post("http://argo-events/trigger", json={
            "video_uri": video_uri,
            "resolutions": config["low"],
            "node_type": "low"
        })
    return {"status": "processing_started"}

print(get_resolution_with_min_download('123.mp4'))
# url = client.presigned_put_object(
#     "videos",
#     "123.mp4",
#     expires=timedelta(hours=1)
# )
# print(url)
