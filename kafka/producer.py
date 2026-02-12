import json
import time
import random
from datetime import datetime
from kafka import KafkaProducer

# With this script: events are printed in the producer terminal,
# Spark console aggregations updating, Parquet files written every minute

# Kafka configuration
KAFKA_BOOTSTRAP_SERVERS = "kafka:9092" # Find the Kafka cluster
TOPIC_NAME = "orders"

producer = KafkaProducer(
    bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
    value_serializer=lambda v: json.dumps(v).encode("utf-8") # 
)
# Kafka only sends bytes. This lambda function automatically converts Python dictionaries into JSON strings 
# and then into UTF-8 bytes before sending.

users = ["u1", "u2", "u3", "u4", "u5"]

print("Starting Kafka producer... Press CTRL+C to stop.")

try:
    while True:
        event = {
            "user_id": random.choice(users),
            "amount": round(random.uniform(10, 500), 2),
            "timestamp": datetime.utcnow().isoformat()
        }

        producer.send(TOPIC_NAME, value=event)
        print(f"Sent event: {event}")
        # This is asynchronous. It puts the message into an internal buffer to be sent in the background, 
        # allowing the script to keep running without waiting for a response from the server.

        time.sleep(2) # Every 2 sec

except KeyboardInterrupt:
    print("Stopping producer...")

finally:
    # Ensure all messages currently in buffer are actually sent to Kafka before the script exits.
    producer.flush()
    # Close the connection to the brokers and release resources.
    producer.close()
