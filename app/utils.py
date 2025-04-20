from minio import Minio
import ffmpeg

from dotenv import load_dotenv
import os


# загрузка переменных окружения
load_dotenv("./.env.dev")  
MINIO_USER = os.environ.get("MINIO_USER")
MINIO_PASSWORD = os.environ.get("MINIO_PASSWORD")
MINIO_PORT = os.environ.get("MINIO_PORT")


client = Minio(
    MINIO_PORT,
    access_key=MINIO_USER,
    secret_key=MINIO_PASSWORD,
    secure=False
)

def get_resolution(filename: str):
    data = client.get_object("videos", filename, length=1024*1024)
    with open("/tmp/partial.mp4", "wb") as f:
        for chunk in data.stream(32*1024):
            f.write(chunk)
    
    height = ffmpeg.probe("/tmp/partial.mp4", select_streams="v:0", show_entries="stream=height")["streams"][0]["height"]

    if height >= 4320:
        return "4k"
    elif height >= 2160:
        return "2k"
    elif height >= 1080:
        return "1080p"
    elif height >= 720:
        return "720p"
    elif height >= 480:
        return "480p"
    elif height >= 360:
        return "360p"
    elif height >= 240:
        return "240p"
    elif height >= 144:
        return "144p"
    return None