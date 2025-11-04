# Multi-Terminal Demo Setup Guide

This guide shows you how to run the Kafka → Flume → HDFS demo with each service in its own terminal for better visibility.

## Prerequisites

1. **Kafka must be running**
   ```bash
   # Check if Kafka is running
   docker ps | grep kafka
   ```

2. **HDFS must be running**
   ```bash
   start-dfs.sh
   # Verify:
   hdfs dfsadmin -report
   ```

3. **Activate your Python virtual environment**
   ```bash
   source kafka-demo-env/bin/activate
   ```

## Terminal Setup

Open **6 separate terminals** in this directory (`Kafka-Flume-Demo/`):

### Terminal 1: Order Producer
```bash
cd /Users/voltamol/Documents/GitHub/Kafka-Flume-Demo
source kafka-demo-env/bin/activate
python3 producer-only.py
```
**What you'll see:** Orders being generated and sent to Kafka

### Terminal 2: Warehouse Service
```bash
cd /Users/voltamol/Documents/GitHub/Kafka-Flume-Demo
source kafka-demo-env/bin/activate
python3 warehouse-service.py
```
**What you'll see:** Orders being processed, shipped, and published to inventory/notifications topics

### Terminal 3: Notification Service
```bash
cd /Users/voltamol/Documents/GitHub/Kafka-Flume-Demo
source kafka-demo-env/bin/activate
python3 notification-service.py
```
**What you'll see:** Email notifications being sent to customers

### Terminal 4: Inventory Service
```bash
cd /Users/voltamol/Documents/GitHub/Kafka-Flume-Demo
source kafka-demo-env/bin/activate
python3 inventory-service.py
```
**What you'll see:** Stock levels being updated in real-time

### Terminal 5: Flume - Orders Archiver
```bash
cd /Users/voltamol/Documents/GitHub/Kafka-Flume-Demo
flume-ng agent --conf-file flume-kafka-hdfs.conf --name agent --conf flume-config-override -Dflume.root.logger=INFO,console
```
**What you'll see:** Orders being consumed from Kafka and archived to HDFS

### Terminal 6: Flume - Inventory Archiver (Optional)
```bash
cd /Users/voltamol/Documents/GitHub/Kafka-Flume-Demo
flume-ng agent --conf-file flume-kafka-inventory.conf --name agent --conf flume-config-override -Dflume.root.logger=INFO,console
```
**What you'll see:** Inventory updates being archived to HDFS

### Terminal 7: Flume - Notifications Archiver (Optional)
```bash
cd /Users/voltamol/Documents/GitHub/Kafka-Flume-Demo
flume-ng agent --conf-file flume-kafka-notifications.conf --name agent --conf flume-config-override -Dflume.root.logger=INFO,console
```
**What you'll see:** Notifications being archived to HDFS

## Startup Order

1. **First, start HDFS** (if not running)
2. **Start all Python services** (Terminals 1-4)
3. **Start Flume agents** (Terminals 5-7)
4. **In Terminal 1**, run the producer and generate orders

## What You'll See

### Terminal 1 (Producer):
```
🛒 E-COMMERCE ORDER PRODUCER
✅ Order #1 Placed:
   Order ID: ORD-1234
   Customer: Alice
   Product: Laptop x 2
   → Sent to Kafka topic: 'orders'
```

### Terminal 2 (Warehouse):
```
📦 WAREHOUSE SERVICE
📦 Processing Order: ORD-1234
   → Picking items from warehouse...
   ✅ Order shipped!
   → Published to 'inventory' topic
   → Published to 'notifications' topic
```

### Terminal 3 (Notifications):
```
📧 NOTIFICATION SERVICE
📧 Email Notification:
   To: Alice
   Order: ORD-1234
   → Email sent! ✅
```

### Terminal 4 (Inventory):
```
📊 INVENTORY SERVICE
📊 Inventory Update:
   Product: Laptop
   Sold: 2 units
   New Stock: 48 units
   ✅ Stock level OK
```

### Terminal 5 (Flume - Orders):
```
[FLUME] Info: Kafka Source STARTED
[FLUME] Info: Event Drain Successful for 1 events
[FLUME] Info: HDFS Sink wrote 1 events
```

## Troubleshooting

### "ModuleNotFoundError: No module named 'kafka'"
**Solution:** Make sure you activated the virtual environment:
```bash
source kafka-demo-env/bin/activate
```

### "Connection refused" errors
**Solution:** Check that Kafka and HDFS are running:
```bash
# Check Kafka
docker ps | grep kafka

# Check HDFS
jps | grep -E "(NameNode|DataNode)"
```

### Services not seeing messages
**Solution:** 
1. Make sure all services are connected to the same Kafka broker (`localhost:9092`)
2. Check that topics exist:
   ```bash
   docker exec -it kafka /opt/kafka/bin/kafka-topics.sh --list --bootstrap-server localhost:9092
   ```

### Flume not showing output
**Solution:** Make sure you're using the `-Dflume.root.logger=INFO,console` flag to see logs

## Verification

After running the demo, verify data in HDFS:

```bash
# Check orders archived
hdfs dfs -ls /archive/orders/$(date +%Y-%m-%d)

# Check inventory archived
hdfs dfs -ls /archive/inventory/$(date +%Y-%m-%d)

# Check notifications archived
hdfs dfs -ls /archive/notifications/$(date +%Y-%m-%d)

# View sample data
hdfs dfs -cat /archive/orders/$(date +%Y-%m-%d)/*.json | head -5
```

## Quick Start Script

Alternatively, use the helper script:
```bash
python3 start-flume-agents.py
```
This will show you the exact commands to run in each terminal.

