# Запуск
Установить библиотеки:
```
pip install -r requirements.txt
```

Перейти в каталог ```/video-service```   
Запустить ювикорн:
```
uvicorn app.main:app --reload
```

Порядок команд для настройки нотификации в minio
 mc alias set minio http://localhost:9000 minioadmin minioadmin
 1) Зарегистрировать вебхук в миинио:  mc admin config set local notify_webhook:service endpoint="http://172.17.0.1:8000/webhook"
 2) Перезапустить сервер: mc admin service restart local
 3) Сделать вебхук пунктом назначения при создании объектов в бакете videos(put почему-то): mc event add local/videos arn:minio:sqs::service:webhook --event put

minikube service minio-console -n minio
kubectl -n argo create token fastapi-external-sa --duration=8760h > fastapi-token.txt