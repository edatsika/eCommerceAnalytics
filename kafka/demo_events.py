import json
import time
from datetime import datetime, timedelta
from kafka import KafkaProducer

producer = KafkaProducer(
    bootstrap_servers="kafka:9092", 
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
)

def send_massive_event(label, amount, minutes_ago=0):
    timestamp = (datetime.utcnow() - timedelta(minutes=minutes_ago))
    event = {
        "user_id": f"DEMO_BOLT_{label}",
        "amount": amount, # Should be high enough
        "timestamp": timestamp.isoformat()
    }
    producer.send("orders", value=event)
    producer.flush()
    print(f"Sent {label} event | Amount: ${amount} | Window: {timestamp.strftime('%H:%M')}")

print("--- Starting Live Demo Scenario (High Impact) ---")

# 1. NORMAL EVENT
send_massive_event("NORMAL", amount=50000.0, minutes_ago=0)
time.sleep(5)

# 2. LATE EVENT (bar earlier to check watermark)
send_massive_event("LATE_OK", amount=80000.0, minutes_ago=1)
time.sleep(5)

# 3. TOO LATE EVENT: Watermark Drop
send_massive_event("TOO_LATE", amount=100000.0, minutes_ago=5)

print("--- Demo Finished ---")
producer.close()
