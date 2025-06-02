import pika

from app.config import settings

RABBITMQ_HOST = settings.RABBITMQ_HOST
RABBITMQ_QUEUE = settings.RABBITMQ_QUEUE  # очередь, из которой читаем


def process_message(ch, method, properties, body): 
    try:
        print("Received message:", body.decode()) # string
        # message = json.loads(body)
        # print(f"Получено сообщение: {message}")
        # Запись в БД
        # ...

        ch.basic_ack(delivery_tag=method.delivery_tag) # подтверждение обработки
    except Exception as e:
        print(f"Message processing error: {e}")

def start_consumer():
    connection = pika.BlockingConnection(pika.ConnectionParameters(RABBITMQ_HOST))
    channel = connection.channel()

    # создание очереди, если её нет
    channel.queue_declare(queue=RABBITMQ_QUEUE, durable=True)
 
    channel.basic_consume(
        queue=RABBITMQ_QUEUE,
        on_message_callback=process_message,
        auto_ack=False,  # отключаем автоматическое подтверждение
    )

    print("Waiting for messages...")
    channel.start_consuming()


