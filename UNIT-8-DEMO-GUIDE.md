# Integrated Kafka → Flume → HDFS Demo Guide

## Overview

This guide explains the complete data pipeline demonstration: **Kafka → Microservices → Flume → HDFS**. The demo shows how real-time order processing works with automatic data archival.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    E-COMMERCE ORDER SYSTEM                      │
└─────────────────────────────────────────────────────────────────┘

┌──────────────┐
│  Producer    │  Generates orders
│  (Terminal 1)│  ──→ Sends to Kafka topic: 'orders'
└──────┬───────┘
       │
       ▼
┌─────────────────────────────────────────────────────────────────┐
│                        APACHE KAFKA                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                       │
│  │ orders   │  │inventory │  │notifications                     │
│  │  topic   │  │  topic   │  │   topic  │                       │
│  └──────────┘  └──────────┘  └──────────┘                       │
└──────────┬──────────┬──────────┬────────────────────────────────┘
           │          │          │
           │          │          │
    ┌──────┴──────┐   │   ┌──────┴──────┐
    │             │   │   │             │
    ▼             ▼   ▼   ▼             ▼
┌─────────┐  ┌─────────┐  ┌─────────┐   ┌─────────┐
│Warehouse│  │Inventory│  │Notification │  Flume  │
│ Service │  │ Service │  │  Service│   │  Agent  │
│(Thread) │  │(Thread) │  │ (Thread)│   │(Thread) │
└─────────┘  └─────────┘  └─────────┘   └────┬────┘
                                             │
                                             ▼
                                     ┌──────────────┐
                                     │     HDFS     │
                                     │  /archive/   │
                                     │   orders/    │
                                     └──────────────┘
```

## Components Explained

### 1. **Order Producer** (Terminal 1)
- **What it does**: Generates simulated e-commerce orders
- **Sends to**: Kafka topic `orders`
- **Data format**: JSON with order details (order_id, customer, product, quantity, price, total, timestamp)

### 2. **Apache Kafka** (Message Broker)
- **Role**: Central message queue/bus
- **Topics**:
  - `orders`: Raw order data
  - `inventory`: Inventory updates
  - `notifications`: Customer notifications
- **Why**: Decouples services, enables real-time streaming

### 3. **Microservices** (Background Threads)
All run automatically when you start the demo:

#### **Warehouse Service**
- **Consumes**: `orders` topic
- **Does**: Processes orders, ships items
- **Produces**: 
  - Updates to `inventory` topic
  - Notifications to `notifications` topic

#### **Inventory Service**
- **Consumes**: `inventory` topic
- **Does**: Tracks stock levels in real-time
- **Shows**: Stock updates as orders are processed

#### **Notification Service**
- **Consumes**: `notifications` topic
- **Does**: Sends email notifications to customers
- **Shows**: Notification confirmations

### 4. **Flume Agent** (Background Process)
- **Consumes**: `orders` topic from Kafka
- **Does**: Archives all order data to HDFS
- **Why**: Long-term storage for analytics, compliance, backup
- **Output**: JSON files in HDFS at `/archive/orders/YYYY-MM-DD/`

### 5. **HDFS** (Hadoop Distributed File System)
- **Role**: Distributed storage for archived data
- **Location**: `/archive/orders/YYYY-MM-DD/orders-archive*.json`
- **Why**: Scalable, distributed storage for big data analytics

## Data Flow

### Step-by-Step Process

1. **Order Generation** (Terminal 1)
   ```
   Producer creates order → Sends to Kafka 'orders' topic
   ```

2. **Parallel Processing** (Automatic)
   ```
   Kafka 'orders' topic
       ├─→ Warehouse Service (processes & ships)
       │       ├─→ Publishes to 'inventory' topic
       │       └─→ Publishes to 'notifications' topic
       │
       ├─→ Inventory Service (consumes 'inventory' topic)
       │       └─→ Updates stock levels
       │
       ├─→ Notification Service (consumes 'notifications' topic)
       │       └─→ Sends customer emails
       │
       └─→ Flume Agent (consumes 'orders' topic)
               └─→ Archives to HDFS
   ```

3. **Archival** (Automatic)
   ```
   Flume reads order → Writes to HDFS → File created in /archive/orders/
   ```

## Prerequisites

### 1. **Kafka** (Must be running)
```bash
# Check if Kafka is running
docker ps | grep kafka

# If not running, start it (example - adjust for your setup)
docker start kafka
```

### 2. **HDFS** (Must be running)
```bash
# Start HDFS
start-dfs.sh

# Verify
jps | grep -E "(NameNode|DataNode)"
# Should show: NameNode and DataNode processes
```

### 3. **Python Environment**
```bash
# Activate virtual environment
source kafka-demo-env/bin/activate

# Verify Kafka library is installed
python3 -c "from kafka import KafkaProducer; print('✅ Ready')"
```

### 4. **Flume Configuration**
- ✅ `flume-kafka-hdfs.conf` exists
- ✅ `flume-config-override/flume-env.sh` exists (sets Java memory)

## Running the Demo

### Option 1: Integrated Demo (Recommended)

**Single Terminal Approach:**
```bash
cd /Users/voltamol/Documents/GitHub/Kafka-Flume-Demo
source kafka-demo-env/bin/activate
python3 integrated_demo.py
```

**What Happens:**
1. Flume agent starts automatically
2. All microservices start in background threads
3. You'll see output from all components in one terminal
4. Orders are generated automatically
5. Everything processes in real-time

### Option 2: Interactive Demo

```bash
cd /Users/voltamol/Documents/GitHub/Kafka-Flume-Demo
source kafka-demo-env/bin/activate
python3 kafka-demo.py
```

**Choose Option 3** (Full Demo) when prompted.

### What You'll See

```
======================================================================
🚀 INTEGRATED KAFKA DEMO: STARTING ALL MICROSERVICES
======================================================================

📥 STARTING FLUME AGENT
======================================================================
[FLUME] Info: Sourcing environment configuration script...
[FLUME] ✅ Flume agent started and ready!

All services are running in background threads...
Flume agent is reading 'orders' topic and archiving to HDFS.

======================================================================
🛒 E-COMMERCE PRODUCER: Generating 5 orders...
======================================================================
✅ Order #1 Placed: ORD-1234 (Laptop x 2)
   [Warehouse] Processing: ORD-1234 - Shipping...
   [Inventory] Updated: Laptop - Remaining: 48
   [Notifier] Sending Email to Alice for ORD-1234
[FLUME] Info: Event consumed from Kafka
[FLUME] Info: Successfully wrote to HDFS

✅ Order #2 Placed: ORD-5678 (Keyboard x 1)
... (more orders)

✨ Demo completed! Check HDFS for archived data.
```

## Multi-Terminal Setup (Optional)

For a more impressive presentation, you can monitor different aspects:

### Terminal 1: Main Demo
```bash
python3 integrated_demo.py
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

## Verification

### 1. Check Flume is Running
```bash
ps aux | grep -i "[f]lume.*agent"
# Should show Flume process
```

### 2. Check Kafka Topics
```bash
docker exec kafka /opt/kafka/bin/kafka-topics.sh \
  --list --bootstrap-server localhost:9092
# Should show: orders, inventory, notifications
```

### 3. Check HDFS Files
```bash
# List archived files
hdfs dfs -ls /archive/orders/$(date +%Y-%m-%d)

# View sample data
hdfs dfs -cat /archive/orders/$(date +%Y-%m-%d)/*.json | head -5
```

### 4. Check Flume Consumer Group
```bash
docker exec kafka /opt/kafka/bin/kafka-consumer-groups.sh \
  --bootstrap-server localhost:9092 \
  --group flume-archiver --describe
# Should show LAG = 0 (all messages consumed)
```

## Understanding the Output

### Flume Output Prefixes

- `[FLUME]` - Normal Flume log messages
- `[FLUME] ❌ ERROR:` - Errors (HDFS connection issues, etc.)
- `[FLUME] ⚠️  WARN:` - Warnings (Java compatibility, etc.)
- `[FLUME] ✅ INFO:` - Success messages (consumed, written, etc.)

### Service Output

- `✅ Order #X Placed:` - Order generated
- `📦 Processing Order:` - Warehouse processing
- `📊 Inventory Update:` - Stock level changes
- `📧 Email Notification:` - Customer notification sent

## Troubleshooting

### Issue: "Connection refused" errors

**Solution:**
- Check Kafka: `docker ps | grep kafka`
- Check HDFS: `jps | grep NameNode`
- Start missing services

### Issue: Flume shows no activity

**Possible Causes:**
1. **No new messages**: Flume already consumed existing messages. Generate new orders.
2. **HDFS not running**: Flume can't write. Start HDFS with `start-dfs.sh`
3. **Kafka topic empty**: Check with `docker exec kafka /opt/kafka/bin/kafka-console-consumer.sh --topic orders --bootstrap-server localhost:9092 --max-messages 1`

### Issue: NameNode won't start

**Solution:**
```bash
# Format NameNode (WARNING: This deletes existing HDFS data)
hdfs namenode -format -force

# Then start HDFS
start-dfs.sh
```

### Issue: "ModuleNotFoundError: No module named 'kafka'"

**Solution:**
```bash
# Make sure virtual environment is activated
source kafka-demo-env/bin/activate

# Verify
python3 -c "from kafka import KafkaProducer"
```

## Key Concepts

### Why Kafka?
- **Decoupling**: Services don't need to know about each other
- **Scalability**: Handle high message volumes
- **Reliability**: Messages are persisted
- **Real-time**: Low latency processing

### Why Flume?
- **Reliability**: Built for data ingestion
- **Integration**: Easy Kafka → HDFS connector
- **Buffering**: Handles backpressure gracefully
- **Production-ready**: Used in enterprise systems

### Why HDFS?
- **Scalability**: Distributed storage for large datasets
- **Analytics**: Compatible with Spark, Hive, etc.
- **Durability**: Replicated across nodes
- **Cost-effective**: Store large amounts of data

## Data Flow Summary

```
Order Created
    ↓
Kafka 'orders' topic
    ↓
    ├─→ Warehouse Service → 'inventory' topic → Inventory Service
    ├─→ Warehouse Service → 'notifications' topic → Notification Service
    └─→ Flume Agent → HDFS Archive
```

## Next Steps

### Analyze Archived Data
```bash
# Use the helper script
python3 read_hdfs_orders.py --summary

# Or query directly
hdfs dfs -cat /archive/orders/*/*.json | python3 -m json.tool
```

### Extend the Demo
- Add more microservices
- Add more Kafka topics
- Add Flume agents for other topics (inventory, notifications)
- Add analytics with Spark or Hive

## Summary

This integrated demo shows:
1. ✅ **Real-time processing** with Kafka
2. ✅ **Microservices architecture** with independent services
3. ✅ **Data archival** with Flume → HDFS
4. ✅ **Complete pipeline** in one command
5. ✅ **Production-like** setup

**Everything runs automatically** - just start the demo and watch the magic happen! 🎉

