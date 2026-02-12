FROM apache/spark:3.5.5

USER root

# Install Python dependencies
RUN pip install --no-cache-dir pyspark kafka-python
RUN apt-get update && apt-get install -y rsync && rm -rf /var/lib/apt/lists/*


WORKDIR /app
COPY app /app

# Entrypoint
COPY docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh
ENTRYPOINT ["docker-entrypoint.sh"]
