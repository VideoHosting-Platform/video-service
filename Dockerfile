# As build - временные файлы остаются на этапе сборки и не попадают в образ 
FROM python:3.12-alpine AS build

# Создаем не-root пользователя
# Chown меняет владельца и группу директории /app на пользователя appuser
RUN addgroup -S -g 1001 appgroup && \
    adduser -S -u 1001 -G appgroup appuser && \
    mkdir /app && \
    chown appuser:appgroup /app

WORKDIR /app

# Копирует файлы с сразу правильными правами
# Переключение пользователя
COPY --chown=appuser:appgroup . .

USER appuser 

# Создаем виртуальное окружение
# --no-cache отключает сохранение кэша pip
# --user устанавливает зависимости в другую папку, где нет лишнего
RUN python -m venv /home/appuser/venv && \
    . /home/appuser/venv/bin/activate && \
    pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir --no-warn-script-location -r requirements.txt

# Финальный образ
FROM python:3.12-alpine

# Повторно создаем такого же пользователя
RUN addgroup -S -g 1001 appgroup && \
    adduser -S -u 1001 -G appgroup appuser && \
    mkdir /app && \
    chown appuser:appgroup /app

WORKDIR /app

# Копируем зависимости из build
COPY --from=build --chown=appuser:appgroup /home/appuser/venv /home/appuser/venv
COPY --chown=appuser:appgroup . .

ENV PATH="/home/appuser/venv/bin:$PATH" \
    PYTHONPATH=/app

USER appuser

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]