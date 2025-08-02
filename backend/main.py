import threading

from infrastructure.messaging import run_consumer

# initalize classes from infrastructure and services here

@app.on_event("startup")
def start_kafka_consumer():
    thread = threading.Thread(target=run_consumer, daemon=True)
    thread.start()
