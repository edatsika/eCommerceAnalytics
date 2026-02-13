# eCcommerce order processing demo

A production-grade, end-to-end data engineering pipeline designed to process e-commerce order streams in real-time. 
This project implements a **Lambda-style architecture**, providing both a **Hot Path** (Real-time monitoring via InfluxDB & Grafana) and a **Cold Path** (Batch analytics via Parquet Data Lake).

## 📐 Architecture & Data Flow
1. **Ingestion:** A Python producer simulates realistic order events (JSON) and publishes them to the Kafka topic `orders`.
2. **Processing:** Apache Spark (Structured Streaming) consumes the stream, applying **1-minute Tumbling Windows** and **Watermarking** (2 min) for late data management.
3. **Hot Path (Monitoring):** Aggregated metrics are pushed to **InfluxDB** for sub-second visualization in **Grafana**.
4. **Cold Path (Storage):** Raw events are persisted in **Parquet format** (columnar storage) for downstream batch processing and historical analysis.

## 🧰 Tech Stack
- **Apache Kafka** (Broker & KRaft mode)
- **Apache Spark 3.5** (Structured Streaming engine)
- **InfluxDB 2.7** (Time-series Database)
- **Grafana** (Observability & Dashboards)
- **Docker & Docker Compose** (Infrastructure orchestration)

## 📦 Key Engineering Features
- **Fault Tolerance:** Checkpointing enabled to ensure recovery from the last processed offset in case of failure
- **Late Data Handling:** Implemented Watermarking to handle out-of-order events and prevent memory leaks
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

    - Fault Tolerance: Χρήση Checkpointing για άμεση ανάκαμψη από αστοχία.
    - Late Data Handling: Το Watermarking διασφαλίζει ότι τα "αργοπορημένα" events δεν θα αλλοιώσουν τα τρέχοντα windows.
    - Automated Submission: Το Spark job υποβάλλεται αυτόματα μόλις ο Kafka είναι ready.


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

### Check demo video

