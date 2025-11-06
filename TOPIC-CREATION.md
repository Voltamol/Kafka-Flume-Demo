```bash
# 1. Start Hadoop
start-dfs.sh
jps  # Verify NameNode and DataNode

# Namenode problems?

# Format the namenode - this will recreate the directory structure
hdfs namenode -format

# Start HDFS
start-dfs.sh

# Verify it's running
jps

To prevent this in the future:

Consider changing your HDFS storage location from /tmp to a persistent location. Edit $HADOOP_HOME/etc/hadoop/core-site.xml and hdfs-site.xml to use a path like /Users/voltamol/hadoop_data instead of /tmp/hadoop-voltamol.

# 2. Start Kafka
docker start kafka
docker ps | grep kafka

# 3. Create demo directory in HDFS
hdfs dfs -mkdir -p /demo/weblogs
hdfs dfs -ls /demo

# 4. Test everything
echo "Ready for demo!"
```

```
Customer Places Order
    ↓
  Kafka (orders topic)
    ↓
├─→ Warehouse Service (ships order)
├─→ Notification Service (sends email)
└─→ Inventory Service (updates stock)
```

```bash
# Show creating topics
docker exec -it kafka /opt/kafka/bin/kafka-topics.sh \
  --create --topic orders \
  --bootstrap-server localhost:9092 \
  --partitions 3

docker exec -it kafka /opt/kafka/bin/kafka-topics.sh \
  --create --topic notifications \
  --bootstrap-server localhost:9092

docker exec -it kafka /opt/kafka/bin/kafka-topics.sh \
  --create --topic inventory \
  --bootstrap-server localhost:9092

# List topics
docker exec -it kafka /opt/kafka/bin/kafka-topics.sh \
  --list \
  --bootstrap-server localhost:9092
  ```

>"First, we create topics - these are like channels where events are published. We have separate topics for orders, notifications, and inventory updates."

>"Now we start our microservices. Each service listens to Kafka topics. Notice they're independent - if one crashes, the others keep working. This is the beauty of event-driven architecture."

>"Now watch what happens when customers place orders. Each order goes to Kafka, and all services process it independently and in real-time."

## Multi-Terminal Setup (Optional)

For a more impressive presentation, you can monitor different aspects:

### Terminal 1: Main Demo
```bash
python3 kafka-demo.py
```

### Terminal 2: HDFS Monitoring
```bash
watch -n 2 'hdfs dfs -ls /archive/orders/$(date +%Y-%m-%d) 2>/dev/null'
```

### Terminal 3: Kafka Monitoring
```bash
docker exec -it kafka /opt/kafka/bin/kafka-console-consumer.sh \
  --topic orders --bootstrap-server localhost:9092 --from-beginning
```

# Reading the json files stored in HDFS

```bash
hdfs dfs -cat /archive/orders/2025-11-01/orders-archive.1761997651647.json
```

## Method 2: Read all files from today (formatted)
```bash
# Pretty print with jq (if installed)
hdfs dfs -cat '/archive/orders/2025-11-01/*.json' | jq .

# Or just view raw
hdfs dfs -cat '/archive/orders/2025-11-01/*.json' | head -20
```

## Method 3: Download to local filesystem, then read
```bash
# Copy all files to local
hdfs dfs -get /archive/orders/2025-11-01/*.json ~/Downloads/

# Then read locally
cat ~/Downloads/orders-archive*.json | jq .
```

```bash
# Find orders by customer
hdfs dfs -cat '/archive/orders/2025-11-01/*.json' | grep '"customer": "Alice"'

# Find orders by product
hdfs dfs -cat '/archive/orders/2025-11-01/*.json' | grep '"product": "Laptop"'

# Count total orders
hdfs dfs -cat '/archive/orders/2025-11-01/*.json' | grep -c "order_id"
```
