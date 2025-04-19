#!/bin/bash

# Запрос названия образа у пользователя
read -p "Введите название образа (например, video-processor): " image_name
read -p "Введите версию образа (например, 1.0): " image_version

# Полное имя образа (например, video-processor:1.0)
full_image="${image_name}:${image_version}"

# 1. Переключение на Docker Minikube
echo -e "\n\033[1mШаг 1: Настройка Minikube Docker\033[0m"
eval $(minikube docker-env)
if [ $? -ne 0 ]; then
    echo "❌ Ошибка: Minikube не запущен или Docker не настроен."
    exit 1
fi
echo "✅ Успешно: Minikube Docker настроен."

# 2. Сборка образа
echo -e "\n\033[1mШаг 2: Сборка Docker-образа\033[0m"
docker build -t "$full_image" .
if [ $? -ne 0 ]; then
    echo "❌ Ошибка: Не удалось собрать образ."
    exit 1
fi
echo "✅ Успешно: Образ $full_image собран."

# 3. Тегирование образа для локального реестра
echo -e "\n\033[1mШаг 3: Тегирование образа\033[0m"
local_image="localhost:5000/$full_image"
docker tag "$full_image" "$local_image"
if [ $? -ne 0 ]; then
    echo "❌ Ошибка: Не удалось добавить тег."
    exit 1
fi
echo "✅ Успешно: Образ тегирован как $local_image."

# 4. Загрузка образа в локальный реестр Minikube
echo -e "\n\033[1mШаг 4: Загрузка в локальный реестр\033[0m"
docker push "$local_image"
if [ $? -ne 0 ]; then
    echo "❌ Ошибка: Не удалось загрузить образ в реестр."
    echo "Проверьте, запущен ли локальный реестр: kubectl get pods -n kube-system | grep registry"
    exit 1
fi
echo "✅ Успешно: Образ $local_image загружен в реестр."

# Итог
echo -e "\n\033[1mГотово!\033[0m"
echo "Образ доступен в Minikube как: $local_image"