from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, window, sum as _sum
from pyspark.sql.types import StructType, StringType, DoubleType, TimestampType
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
import os
import logging

# Setup professional logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SparkStreamingApp")

# InfluxDB Config (από το docker-compose)
INFLUX_URL = "http://influxdb:8086"
INFLUX_TOKEN = "my-super-secret-token"
INFLUX_ORG = "my-org"
INFLUX_BUCKET = "ecommerce_metrics"

# Runs for each micro-batch
# Sends aggregated data to InfluxDB
def write_to_influx(batch_df, batch_id):

    if batch_df.count() == 0:
        return

    client = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG)
    write_api = client.write_api(write_options=SYNCHRONOUS)
    
    try:
        for row in batch_df.collect():
            # Create point for Grafana
            point = Point("revenue_stats") \
                .tag("window_start", str(row['window']['start'])) \
                .field("total_revenue", float(row['total_revenue']))
            
            write_api.write(bucket=INFLUX_BUCKET, record=point)
        logger.info(f" Batch {batch_id}: Sent {batch_df.count()} points to InfluxDB")
    except Exception as e:
        logger.error(f" Error writing to InfluxDB: {e}")
    finally:
        client.close()

def run_pipeline():
    spark = SparkSession.builder \
        .appName("RealTimeEcomAnalytics") \
        .getOrCreate()

    # Schema definition
    schema = StructType() \
        .add("user_id", StringType()) \
        .add("amount", DoubleType()) \
        .add("timestamp", TimestampType())

    # 1. Read from Kafka
    raw_df = spark.readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", "kafka:9092") \
        .option("subscribe", "orders") \
        .option("startingOffsets", "earliest") \
        .load()

    # 2. Parse JSON & Clean
    parsed_df = raw_df.select(
        from_json(col("value").cast("string"), schema).alias("data")
    ).select("data.*").filter(col("user_id").isNotNull())

    # 3. Transformations: 1-min Windows with 2-min Watermark
    windowed_revenue = parsed_df \
        .withWatermark("timestamp", "2 minutes") \
        .groupBy(window(col("timestamp"), "1 minute")) \
        .agg(_sum("amount").alias("total_revenue"))

    # --- SINKS ---

    # Sink A: Storage (Parquet) - Raw Data Data Lake
    query_storage = parsed_df.writeStream \
        .trigger(processingTime='1 minute') \
        .format("parquet") \
        .option("path", "/opt/spark/data/refined_orders") \
        .option("checkpointLocation", "/opt/spark/data/checkpoints/raw_data") \
        .outputMode("append") \
        .start()

    # Sink B: InfluxDB & Console - Real-time Monitoring
    # Use foreachBatch to send aggregates to InfluxDB
    query_monitoring = windowed_revenue.writeStream \
        .foreachBatch(write_to_influx) \
        .outputMode("update") \
        .start()

    # Sink C: Console (Optional for debugging)
    query_console = windowed_revenue.writeStream \
        .outputMode("update") \
        .format("console") \
        .option("truncate", "false") \
        .start()

    spark.streams.awaitAnyTermination()

if __name__ == "__main__":
    run_pipeline()
