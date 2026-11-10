import os
import pika

credentials = pika.PlainCredentials(
    os.environ["RABBIT_USER"],
    os.environ["RABBIT_PASS"]
)
connection = pika.BlockingConnection(
    pika.ConnectionParameters(
        host="rabbitmq",
        port=5672,
        virtual_host="/",
        credentials=credentials
    )
)
channel = connection.channel()
channel.basic_publish(
    exchange="",
    routing_key="video.dlx.source.test",
    body="DLQ_TEST_MESSAGE_2026",
    properties=pika.BasicProperties(delivery_mode=2)
)
print("Test message published to video.dlx.source.test")
connection.close()
