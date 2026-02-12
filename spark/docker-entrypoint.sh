#!/bin/bash
set -e

if [ "$SPARK_MODE" = "master" ]; then
    echo "Starting Spark master..."
    /opt/spark/sbin/start-master.sh
elif [ "$SPARK_MODE" = "worker" ]; then
    echo "Starting Spark worker..."
    /opt/spark/sbin/start-worker.sh $SPARK_MASTER
else
    echo "Running custom command: $@"
    exec "$@"
fi

tail -f /dev/null
