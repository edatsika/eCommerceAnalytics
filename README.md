# E-commerce-order-processing-demo

This project demonstrates a real-time data processing pipeline using Apache Kafka and Apache Spark Structured Streaming, fully containerized with Docker Compose.
Streaming e-commerce order events are produced to Kafka, processed in real time by Spark, aggregated using event-time windows, and persisted to Parquet for downstream analytics.

📐 **Architecture**

Kafka Producer --> Kafka Topic (orders) --> Spark Structured Streaming --> Parquet Sink (file-based data lake)

🧰 **Tech Stack**

Apache Kafka – real-time event ingestion

Apache Spark (Structured Streaming) – stream processing & aggregation

PySpark – Spark application code

Docker & Docker Compose – containerized infrastructure

Parquet – columnar storage format

📦 **Features**

- Real-time ingestion from Kafka

- Event-time windowed aggregations (1-minute tumbling windows)

- Watermarking for late data handling

- Fault-tolerant processing using Spark checkpoints

- Dual sinks:

  Console output for monitoring

  Parquet files for batch analytics

🚀 **How to Run**

1️⃣ Start all services

```
docker compose up -d
```

2️⃣ Produce sample Kafka events

```
docker exec -it kafka \
  python /producer.py
```

3️⃣ Run the Spark streaming job

```
docker exec -it spark-master-kafka-demo \
  /opt/spark/bin/spark-submit \
  --master spark://spark-master-kafka-demo:7077 \
  /opt/spark/app/ecommerce_tracking.py
```

You should see real-time aggregations printed to the console.

📊 **Output Data**

Processed events are written as Parquet files:

```
/opt/spark/data/refined_orders/
```

Read the data in batch mode

```
docker exec -it spark-master-kafka-demo \
  /opt/spark/bin/pyspark
```

```
df = spark.read.parquet("/opt/spark/data/refined_orders")
df.show(truncate=False)
```
🧠**What this simple project demonstrates**

- End-to-end streaming pipeline design

- Spark Structured Streaming semantics

- Kafka offset management & fault tolerance

- Dockerized data infrastructure

- Transition from streaming to batch analytics

🧹 **Notes**

- Checkpoint and data directories are not committed to GitHub.

- This project is intended for local development and learning purposes.

📌 **Possible improvements**

- Add schema evolution handling

- Write aggregated output to a database

- Add monitoring with Spark UI & Kafka metrics

- Deploy to cloud storage (S3 / GCS / Azure Blob)

