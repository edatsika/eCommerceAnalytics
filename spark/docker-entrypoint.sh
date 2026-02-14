#!/bin/bash
set -e

# Paths to jars downloaded in Dockerfile
KAFKA_PACKAGES="org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0"

if [ "$SPARK_MODE" = "master" ]; then
    echo "Starting Spark Master..."
    /opt/spark/sbin/start-master.sh
    # Keep alive and show logs
    tail -f /opt/spark/logs/*.out

elif [ "$SPARK_MODE" = "worker" ]; then
    echo "Starting Spark Worker connecting to $SPARK_MASTER..."
    /opt/spark/sbin/start-worker.sh "$SPARK_MASTER"
    # Keep alive and show logs
    tail -f /opt/spark/logs/*.out

elif [ "$SPARK_MODE" = "submit" ]; then
    echo "Submitting Spark-Kafka Streaming Job to $SPARK_MASTER..."
    
    # Use --conf to define checkpointing externally
    spark-submit \
        --master "$SPARK_MASTER" \
        --packages "$KAFKA_PACKAGES" \
        --conf "spark.sql.streaming.checkpointLocation=/opt/spark/data/checkpoints" \
        /opt/spark/app/ecommerce_tracking.py

else
    echo "Running custom command: $@"
    exec "$@"
fi
