from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, window, sum as _sum
from pyspark.sql.types import StructType, StringType, DoubleType, TimestampType

# Kafka topic "orders" receive events like this:
# {"user_id":"u1","amount":29.99,"timestamp":"2026-02-06T19:10:00"}

spark = SparkSession.builder \
    .appName("RealTimeEcomAnalytics") \
    .getOrCreate()

# Construct a StructType by adding new elements to it, to define the schema.
schema = StructType() \
    .add("user_id", StringType()) \
    .add("amount", DoubleType()) \
    .add("timestamp", TimestampType())

# Read continuously from topic = orders
# Kafka messages are raw bytes  so Spark converts them into structured rows.
raw_df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "kafka:9092") \
    .option("subscribe", "orders") \
    .load()

# Kafka raw data to DataFrame with given schema
parsed_df = raw_df.selectExpr("CAST(value AS STRING)") \
    .select(from_json(col("value"), schema).alias("data")) \
    .select("data.*")\
    .filter(col("data").isNotNull())

# Time-Window Aggregation in streaming data --> Spark Structured Streaming
# Calc sales per minute !!!

# Watermark: lets Spark handle late data, e.g., wait for data with timestamp up to 2 min older
# than max observed timestamp, after 2 minutes, window is deleted.

# Tumbling windows, no overlap like in Sliding windows
# For each 1 min windows, sum amount, result is DataFrame with window, i.e.,
# a struct with start and end times, and total_revenue.
windowed_revenue = parsed_df \
    .withWatermark("timestamp", "2 minutes") \
    .groupBy(window(col("timestamp"), "1 minute")) \
    .agg(_sum("amount").alias("total_revenue"))

# Without Watermarking, Spark should keep in memory (State) all windows forever, 
# in case an old record arrives later. Allow late events up to 2 min.

# Sinks

# Without "start", Spark doesn't execute anything.

# Sink A: Console for monitoring, writes sums per minute
query1 = windowed_revenue.writeStream \
    .outputMode("complete") \
    .format("console") \
    .start()
# use complete because of groupBy: each time show whole table with aggregated data, testing only

# Sink B: Storage (Parquet files), writes raw data as they come
query2 = parsed_df.writeStream \
    .trigger(processingTime='1 minute') \
    .format("parquet") \
    .option("path", "/opt/spark/data/refined_orders") \
    .option("checkpointLocation", "/opt/spark/data/checkpoints") \
    .start()
# Per 1 minute, Spark processes whatever comes from Kafka, otherwise
# it writes as fast as it can.
# Checkpoint to restart from offset where it previously stopped.

query1.awaitTermination()
query2.awaitTermination()
