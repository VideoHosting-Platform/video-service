# Конфигурация
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secrets.yaml

# БД
kubectl apply -f k8s/db/pvc.yaml
kubectl apply -f k8s/db/service.yaml
kubectl apply -f k8s/db/deployment.yaml

# Ждем пока БД запустится
kubectl wait --for=condition=ready pod -l app=video-db --timeout=90s

# Видео-сервис
kubectl apply -f k8s/video-service/service.yaml
kubectl apply -f k8s/video-service/deployment.yaml