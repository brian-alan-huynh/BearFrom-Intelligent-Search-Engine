import os
import json

from confluent_kafka import Producer, Consumer
from dotenv import load_dotenv

from ..config import S3_CLIENT, BUCKET_NAME

load_dotenv()
env = os.getenv

kafka_producer = Producer({
    "bootstrap.servers": env("KAFKA_BOOTSTRAP_SERVERS"),
    "queue.buffering.max.messages": 100000,
    "queue.buffering.max.ms": 500,
    "compression.type": "lz4",
    "security.protocol": "SASL_SSL",
    "sasl.mechanisms": "PLAIN",
    "sasl.username": env("KAFKA_API_KEY"),
    "sasl.password": env("KAFKA_API_SECRET")
})

kafka_consumer = Consumer({
    "bootstrap.servers": env("KAFKA_BOOTSTRAP_SERVERS"),
    "group.id": "msg-queue-for-external-services",
    "auto.offset.reset": "earliest",
    "enable.auto.commit": True,
    "auto.commit.interval.ms": 1000,
    "security.protocol": "SASL_SSL",
    "sasl.mechanisms": "PLAIN",
    "sasl.username": env("KAFKA_API_KEY"),
    "sasl.password": env("KAFKA_API_SECRET")
})

kafka_consumer.subscribe([
    "s3.upload_pfp",
    "s3.delete_pfp",
])

BATCH_SIZE = 10
RATE_LIMIT = 0.1

while True:
    records = kafka_consumer.poll(timeout=2.0)
    
    if not records:
        records.sleep(2.0)
        continue
    
    msg = json.loads(records.value().decode("utf-8"))
    operation = msg["operation"]
    
    match operation:
        case "upload_pfp":
            s3_key = msg["s3_key"]
            file_content = bytes.fromhex(msg["file_content"])
            content_type = msg["content_type"]
            
            S3_CLIENT.put_object(
                Bucket=BUCKET_NAME,
                Key=s3_key,
                Body=file_content,
                ContentType=content_type,
                ACL='public-read'
            )

        case "delete_pfp":
            s3_key = msg["s3_key"]
            
            S3_CLIENT.delete_object(
                Bucket=BUCKET_NAME,
                Key=s3_key
            )


