#!/usr/bin/env python3
"""
Integrated Kafka Demo: Order Processing with Archival
Shows Producer, Microservices, and background data Archival by Flume
"""

from kafka import KafkaProducer, KafkaConsumer
import json
import time
import random
from datetime import datetime
from threading import Thread
import subprocess
import os
import sys
import signal

# --- Producer Class (Same as before) ---
class OrderProducer:
    def __init__(self):
        # Uses the 'orders' topic
        self.producer = KafkaProducer(
            bootstrap_servers='localhost:9092',
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
        self.products = [
            {"name": "Laptop", "price": 999.99},
            {"name": "Headphones", "price": 79.99},
            {"name": "Keyboard", "price": 49.99}
        ]
        self.customers = ["Alice", "Bob", "Charlie"]
    
    def generate_order(self):
        product = random.choice(self.products)
        customer = random.choice(self.customers)
        quantity = random.randint(1, 3)
        
        order = {
            "order_id": f"ORD-{random.randint(1000, 9999)}",
            "customer": customer,
            "product": product["name"],
            "quantity": quantity,
            "price": product["price"],
            "total": round(product["price"] * quantity, 2),
            "timestamp": datetime.now().isoformat(),
            "status": "pending"
        }
        return order
    
    def start_producing(self, num_orders=5, delay=3):
        print("=" * 70)
        print(f"🛒 E-COMMERCE PRODUCER: Generating {num_orders} orders...")
        print("=" * 70)
        
        for i in range(num_orders):
            order = self.generate_order()
            self.producer.send('orders', value=order)
            self.producer.flush()
            
            print(f"✅ Order #{i+1} Placed: {order['order_id']} ({order['product']} x {order['quantity']})")
            time.sleep(delay)
        
        print("\n✨ Order generation finished.")
        self.producer.close()

# --- Warehouse Service (Same as before) ---
class WarehouseService:
    def __init__(self):
        self.consumer = KafkaConsumer('orders', bootstrap_servers='localhost:9092', 
                                      value_deserializer=lambda m: json.loads(m.decode('utf-8')),
                                      group_id='warehouse-service', auto_offset_reset='earliest')
        self.producer = KafkaProducer(bootstrap_servers='localhost:9092',
                                      value_serializer=lambda v: json.dumps(v).encode('utf-8'))
    
    def process_orders(self):
        print("📦 WAREHOUSE SERVICE: Listening...")
        for message in self.consumer:
            order = message.value
            print(f"   [Warehouse] Processing: {order['order_id']} - Shipping...")
            time.sleep(1) # Simulate work
            
            # Send events to downstream topics
            self.producer.send('inventory', value={"product": order['product'], "quantity_sold": order['quantity']})
            self.producer.send('notifications', value={"order_id": order['order_id'], "customer": order['customer'], "message": "Shipped!"})
            print(f"   [Warehouse] ✅ Shipped and events fired.")

# --- Notification Service (Same as before) ---
class NotificationService:
    def __init__(self):
        self.consumer = KafkaConsumer('notifications', bootstrap_servers='localhost:9092',
                                      value_deserializer=lambda m: json.loads(m.decode('utf-8')),
                                      group_id='notification-service', auto_offset_reset='earliest')
    
    def send_notifications(self):
        print("📧 NOTIFICATION SERVICE: Listening...")
        for message in self.consumer:
            notification = message.value
            print(f"   [Notifier] Sending Email to {notification['customer']} for {notification['order_id']}")

# --- Inventory Service (Same as before) ---
class InventoryService:
    def __init__(self):
        self.consumer = KafkaConsumer('inventory', bootstrap_servers='localhost:9092',
                                      value_deserializer=lambda m: json.loads(m.decode('utf-8')),
                                      group_id='inventory-service', auto_offset_reset='earliest')
        self.stock = {"Laptop": 50, "Headphones": 100, "Keyboard": 75}
    
    def track_inventory(self):
        print("📊 INVENTORY SERVICE: Listening...")
        for message in self.consumer:
            update = message.value
            product = update['product']
            quantity_sold = update['quantity_sold']
            
            if product in self.stock:
                self.stock[product] -= quantity_sold
                print(f"   [Inventory] Updated: {product} - Remaining: {self.stock[product]}")

# ============================================================================
# FLUME MANAGEMENT
# ============================================================================

flume_process = None

def start_flume_agent():
    """Start Flume agent and stream its output in real-time"""
    global flume_process
    
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    flume_config = os.path.join(script_dir, 'flume-kafka-hdfs.conf')
    
    print("\n" + "=" * 70)
    print("📥 STARTING FLUME AGENT")
    print("=" * 70)
    print(f"Config: {flume_config}")
    print("Reading from Kafka topic 'orders' and archiving to HDFS...")
    print("\n⚠️  NOTE: Make sure HDFS is running (start-dfs.sh) for archival to work!")
    print("=" * 70 + "\n")
    
    try:
        # Set up environment with Java options for Flume
        env = os.environ.copy()
        # Note: flume-env.sh already sets JAVA_OPTS, so we don't duplicate it here
        # If flume-env.sh doesn't exist, set it as fallback
        flume_env_file = os.path.join(script_dir, 'flume-config-override', 'flume-env.sh')
        if not os.path.exists(flume_env_file):
            env['JAVA_OPTS'] = '-Xmx512m -Xms256m'
        
        # Point to flume-env.sh directory - Flume needs --conf to read flume-env.sh
        flume_env_dir = os.path.join(script_dir, 'flume-config-override')
        
        # Build Flume command
        flume_cmd = ['flume-ng', 'agent', '--conf-file', flume_config, '--name', 'agent']
        
        # Add --conf if directory exists (this tells Flume where to find flume-env.sh)
        if os.path.exists(flume_env_dir):
            flume_cmd.extend(['--conf', flume_env_dir])
            env['FLUME_CONF_DIR'] = flume_env_dir
        
        # Start Flume agent as subprocess with unbuffered output
        flume_process = subprocess.Popen(
            flume_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1,  # Line buffered
            env=env
        )
        
        def stream_output():
            """Stream Flume output to terminal"""
            try:
                for line in iter(flume_process.stdout.readline, ''):
                    if line:
                        line_lower = line.lower().rstrip()
                        # Highlight important messages
                        if any(keyword in line_lower for keyword in ['error', 'exception', 'failed', 'connection refused']):
                            print(f"[FLUME] ❌ ERROR: {line.rstrip()}")
                        elif any(keyword in line_lower for keyword in ['warn', 'warning']):
                            print(f"[FLUME] ⚠️  WARN: {line.rstrip()}")
                        elif any(keyword in line_lower for keyword in ['started', 'success', 'consumed', 'written']):
                            print(f"[FLUME] ✅ INFO: {line.rstrip()}")
                        else:
                            print(f"[FLUME] {line.rstrip()}")
                        sys.stdout.flush()
            except Exception as e:
                print(f"[FLUME] Error reading output: {e}")
        
        # Start output streaming in background thread
        output_thread = Thread(target=stream_output, daemon=True)
        output_thread.start()
        
        # Give Flume time to start
        time.sleep(3)
        
        # Check if process is still running (if not, it may have crashed)
        if flume_process.poll() is not None:
            print("\n⚠️  WARNING: Flume process exited unexpectedly!")
            print("Check your Flume installation and configuration.")
            return False
        
        print("\n✅ Flume agent started and ready!\n")
        return True
        
    except FileNotFoundError:
        print("\n❌ ERROR: 'flume-ng' command not found!")
        print("Please ensure Flume is installed and 'flume-ng' is in your PATH.")
        return False
    except Exception as e:
        print(f"\n❌ ERROR starting Flume: {e}")
        return False

def stop_flume_agent():
    """Stop Flume agent gracefully"""
    global flume_process
    if flume_process:
        print("\n📥 Stopping Flume agent...")
        try:
            flume_process.terminate()
            flume_process.wait(timeout=5)
            print("✅ Flume agent stopped.")
        except subprocess.TimeoutExpired:
            print("⚠️  Flume didn't stop gracefully, forcing termination...")
            flume_process.kill()
            flume_process.wait()
        except Exception as e:
            print(f"⚠️  Error stopping Flume: {e}")

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def run_integrated_demo():
    # Register signal handlers for cleanup
    def signal_handler(sig, frame):
        stop_flume_agent()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    print("\n" + "=" * 70)
    print("🚀 INTEGRATED KAFKA DEMO: STARTING ALL MICROSERVICES")
    print("=" * 70)
    
    # 0. Start Flume agent first
    if not start_flume_agent():
        print("\n⚠️  Continuing without Flume. You can start it manually if needed.")
        time.sleep(2)
    else:
        time.sleep(2)  # Give Flume a moment to fully initialize
    
    print("All services are running in background threads...")
    print("Flume agent is reading 'orders' topic and archiving to HDFS.\n")
    
    try:
        # 1. Start all Consumers in background threads (daemon=True means they close when the main script ends)
        Thread(target=WarehouseService().process_orders, daemon=True).start()
        Thread(target=NotificationService().send_notifications, daemon=True).start()
        Thread(target=InventoryService().track_inventory, daemon=True).start()
        
        time.sleep(2) # Give threads time to start up
        
        # 2. Start the Producer (runs in the main thread)
        producer = OrderProducer()
        producer.start_producing(num_orders=5, delay=3)
        
        print("\n⏳ Allowing 10 seconds for all downstream processing (and Flume archival) to complete...")
        time.sleep(10)
        
        print("\n✨ Demo completed! Check HDFS for archived data.")
        print("=" * 70)
    finally:
        # Clean up Flume
        stop_flume_agent()

if __name__ == '__main__':
    run_integrated_demo()