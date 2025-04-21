FROM python:3.9-slim

WORKDIR /app
COPY . .

RUN pip install -r "requirements.txt"
RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
