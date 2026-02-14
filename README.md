# Real-Time eCommerce Analytics Pipeline

A demo end-to-end data engineering pipeline designed to process e-commerce order streams in real-time. 
This project implements a simple architecture that provides both a **Hot Path** (Real-time monitoring via InfluxDB & Grafana) and a **Cold Path** (Batch analytics via Parquet Data Lake).

## 📐 Architecture & Data Flow
1. **Ingestion:** A Python producer simulates realistic order events (JSON) and publishes them to the Kafka topic `orders`.
2. **Processing:** Apache Spark (Structured Streaming) consumes the stream, applying **1-minute Tumbling Windows** and **Watermarking** (2 min) for late data management.
3. **Hot Path (Monitoring):** Aggregated metrics are pushed to **InfluxDB** for visualization in **Grafana**.
4. **Cold Path (Storage):** Raw events are persisted in **Parquet format** (columnar storage) for downstream batch processing and historical analysis.

## 🧰 Tech Stack
- **Apache Kafka** (Broker & KRaft mode)
- **Apache Spark 3.5** (Structured Streaming engine)
- **InfluxDB 2.7** (Time-series Database)
- **Grafana** (Observability & Dashboards)
- **Docker & Docker Compose** (Infrastructure orchestration)

## 📦 Key Engineering Features
- **Fault Tolerance:** Checkpointing enabled to ensure recovery from the last processed offset in case of failure
- **Late Data Handling:** Implemented Watermarking to handle out-of-order events
- **Automated Orchestration:** Custom entrypoints ensure the Spark job is submitted only when Kafka and InfluxDB are fully healthy
- **Resource Management:** Optimized Docker resource limits for local development


🚀 **How to run**

Deploy the stack:

```
docker-compose up --build -d
```

🔍 **Monitoring the pipeline**

Spark Console (Live Aggregations):
```
docker logs -f spark-submit-job
```
    
Kafka Producer Logs:
```
docker logs -f kafka-producer
```
    
Grafana Dashboard:
```
Go to http://localhost:3000 (admin/admin)
```
    
InfluxDB UI:
```
Go to http://localhost:8086 (admin/password123)
```

Run the Spark streaming job

```
docker exec -it spark-master-kafka-demo \
  /opt/spark/bin/spark-submit \
  --master spark://spark-master-kafka-demo:7077 \
  /opt/spark/app/ecommerce_tracking.py
```
or with specific arguments:

```
docker exec -it spark-master-kafka-demo \
  /opt/spark/bin/spark-submit \
  --master spark://spark-master-kafka-demo:7077 \
  --executor-memory 512m \
  --total-executor-cores 2 \
  --conf "spark.executor.instances=2" \
  --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0 /opt/spark/app/ecommerce_tracking.py
```
You should see real-time aggregations printed to the console, leave it running.

```
-------------------------------------------
Batch: 3
-------------------------------------------
| window.start       | window.end         | total_revenue |
| 2026-02-09 14:12:00| 2026-02-09 14:13:00| 845.67        |
```

📦 Features

    - Fault Tolerance: Utilization of Checkpointing for immediate recovery from failures
    - Late Data Handling: Watermarking ensures that "late" events do not compromise the integrity of current windows
    - Automated Submission: The Spark job is automatically submitted once Kafka is ready


📊 **Batch Analytics (Cold Storage)**

Processed events are written as Parquet files:

```
/opt/spark/data/refined_orders/
```

Read the data in batch mode

```
docker exec -it spark-master-kafka-demo \
/opt/spark/bin/pyspark \
--master spark://spark-master-kafka-demo:7077

```

```
df = spark.read.parquet("/opt/spark/data/refined_orders")
df.groupBy("user_id").sum("amount").show(truncate=False)
```

To stop and clean up:
```
docker-compose down
```

---

### Example plot

<img width="1314" height="750" alt="image" src="https://github.com/user-attachments/assets/93866c94-778e-4d32-84fd-af2ccb907e6e" />


