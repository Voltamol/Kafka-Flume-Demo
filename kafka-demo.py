#!/usr/bin/env python3
"""
Kafka Demo: Real-time E-commerce Order Processing
Perfect for presentations - shows Kafka's power in action!
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

# ============================================================================
# PART 1: ORDER PRODUCER (Simulates customers placing orders)
# ============================================================================

class OrderProducer:
    def __init__(self):
        self.producer = KafkaProducer(
            bootstrap_servers='localhost:9092',
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
        
        self.products = [
            {"name": "Laptop", "price": 999.99},
            {"name": "Headphones", "price": 79.99},
            {"name": "Keyboard", "price": 49.99},
            {"name": "Mouse", "price": 29.99},
            {"name": "Monitor", "price": 299.99},
            {"name": "Webcam", "price": 89.99}
        ]
        
        self.customers = ["Alice", "Bob", "Charlie", "Diana", "Eve"]
    
    def generate_order(self):
        """Generate a random order"""
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
    
    def start_producing(self, num_orders=10, delay=2):
        """Produce orders to Kafka"""
        print("=" * 70)
        print("🛒 E-COMMERCE ORDER PRODUCER")
        print("=" * 70)
        print(f"Generating {num_orders} orders...\n")
        
        for i in range(num_orders):
            order = self.generate_order()
            
            # Send to Kafka
            self.producer.send('orders', value=order)
            self.producer.flush()
            
            # Display
            print(f"✅ Order #{i+1} Placed:")
            print(f"   Order ID: {order['order_id']}")
            print(f"   Customer: {order['customer']}")
            print(f"   Product:  {order['product']} x {order['quantity']}")
            print(f"   Total:    ${order['total']}")
            print(f"   → Sent to Kafka topic: 'orders'\n")
            
            time.sleep(delay)
        
        print("✨ All orders sent to Kafka!\n")
        self.producer.close()

# ============================================================================
# PART 2: WAREHOUSE SERVICE (Processes orders)
# ============================================================================

class WarehouseService:
    def __init__(self):
        self.consumer = KafkaConsumer(
            'orders',
            bootstrap_servers='localhost:9092',
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            group_id='warehouse-service',
            auto_offset_reset='earliest'
        )
        
        self.producer = KafkaProducer(
            bootstrap_servers='localhost:9092',
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
    
    def process_orders(self):
        print("=" * 70)
        print("📦 WAREHOUSE SERVICE")
        print("=" * 70)
        print("Listening for orders...\n")
        
        for message in self.consumer:
            order = message.value
            
            print(f"📦 Processing Order: {order['order_id']}")
            print(f"   Picking {order['quantity']} x {order['product']}...")
            
            # Simulate processing time
            time.sleep(1)
            
            # Update inventory
            inventory_update = {
                "product": order['product'],
                "quantity_sold": order['quantity'],
                "timestamp": datetime.now().isoformat()
            }
            self.producer.send('inventory', value=inventory_update)
            
            # Send notification
            notification = {
                "order_id": order['order_id'],
                "customer": order['customer'],
                "message": f"Your order for {order['product']} has been shipped!",
                "timestamp": datetime.now().isoformat()
            }
            self.producer.send('notifications', value=notification)
            
            print(f"   ✅ Order shipped!")
            print(f"   → Inventory updated")
            print(f"   → Notification sent\n")

# ============================================================================
# PART 3: NOTIFICATION SERVICE (Sends alerts to customers)
# ============================================================================

class NotificationService:
    def __init__(self):
        self.consumer = KafkaConsumer(
            'notifications',
            bootstrap_servers='localhost:9092',
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            group_id='notification-service',
            auto_offset_reset='earliest'
        )
    
    def send_notifications(self):
        print("=" * 70)
        print("📧 NOTIFICATION SERVICE")
        print("=" * 70)
        print("Listening for notifications...\n")
        
        for message in self.consumer:
            notification = message.value
            
            print(f"📧 Sending Email to {notification['customer']}:")
            print(f"   Order: {notification['order_id']}")
            print(f"   Message: {notification['message']}")
            print(f"   ✅ Email sent!\n")

# ============================================================================
# PART 4: INVENTORY SERVICE (Tracks stock levels)
# ============================================================================

class InventoryService:
    def __init__(self):
        self.consumer = KafkaConsumer(
            'inventory',
            bootstrap_servers='localhost:9092',
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            group_id='inventory-service',
            auto_offset_reset='earliest'
        )
        
        self.stock = {
            "Laptop": 50,
            "Headphones": 100,
            "Keyboard": 75,
            "Mouse": 120,
            "Monitor": 30,
            "Webcam": 45
        }
    
    def track_inventory(self):
        print("=" * 70)
        print("📊 INVENTORY SERVICE")
        print("=" * 70)
        print("Tracking stock levels...\n")
        print("Current Stock:")
        for product, qty in self.stock.items():
            print(f"   {product}: {qty} units")
        print()
        
        for message in self.consumer:
            update = message.value
            product = update['product']
            quantity_sold = update['quantity_sold']
            
            # Update stock
            if product in self.stock:
                self.stock[product] -= quantity_sold
                
                print(f"📊 Inventory Update:")
                print(f"   Product: {product}")
                print(f"   Sold: {quantity_sold} units")
                print(f"   Remaining: {self.stock[product]} units")
                
                # Low stock alert
                if self.stock[product] < 20:
                    print(f"   ⚠️  LOW STOCK ALERT!")
                
                print()

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
# MAIN DEMO SCRIPT
# ============================================================================

def run_demo():
    # Register signal handlers for cleanup
    def signal_handler(sig, frame):
        stop_flume_agent()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    print("\n" + "=" * 70)
    print("🎯 KAFKA REAL-TIME ORDER PROCESSING DEMO")
    print("=" * 70)
    print("\nThis demo shows how Kafka enables real-time event streaming")
    print("in an e-commerce platform with multiple microservices.\n")
    
    print("Choose a demo mode:")
    print("1. Producer Only (Generate orders)")
    print("2. Consumer Only (Process orders)")
    print("3. Full Demo (All services running + Flume)")
    
    choice = input("\nEnter choice (1-3): ").strip()
    
    # Start Flume for options 1 and 3 (where orders are produced)
    flume_started = False
    if choice in ["1", "3"]:
        flume_started = start_flume_agent()
        if flume_started:
            time.sleep(2)  # Give Flume time to initialize
        else:
            print("\n⚠️  Continuing without Flume. You can start it manually if needed.")
            time.sleep(1)
    
    try:
        if choice == "1":
            # Just produce orders
            producer = OrderProducer()
            producer.start_producing(num_orders=5, delay=2)
        
        elif choice == "2":
            # Run all consumers (for presentation, run in separate terminals)
            print("\n⚠️  For best presentation effect, run these in separate terminals:")
            print("   Terminal 1: python kafka-demo.py (choose option 2, select warehouse)")
            print("   Terminal 2: python kafka-demo.py (choose option 2, select notification)")
            print("   Terminal 3: python kafka-demo.py (choose option 2, select inventory)")
            print()
            
            print("Select service to run:")
            print("1. Warehouse Service")
            print("2. Notification Service")
            print("3. Inventory Service")
            
            service = input("\nEnter choice (1-3): ").strip()
            
            if service == "1":
                warehouse = WarehouseService()
                warehouse.process_orders()
            elif service == "2":
                notifier = NotificationService()
                notifier.send_notifications()
            elif service == "3":
                inventory = InventoryService()
                inventory.track_inventory()
        
        elif choice == "3":
            # Full demo with threading
            print("\n🚀 Starting all services...\n")
            time.sleep(2)
            
            # Start consumers in background threads
            warehouse = WarehouseService()
            notifier = NotificationService()
            inventory = InventoryService()
            
            Thread(target=warehouse.process_orders, daemon=True).start()
            Thread(target=notifier.send_notifications, daemon=True).start()
            Thread(target=inventory.track_inventory, daemon=True).start()
            
            time.sleep(3)
            
            # Start producing orders
            producer = OrderProducer()
            producer.start_producing(num_orders=5, delay=3)
            
            # Keep running for a bit to see all processing
            print("\n⏳ Processing orders... (wait 10 seconds)\n")
            time.sleep(10)
            
            print("\n✨ Demo completed!")
            print("=" * 70)
    finally:
        # Clean up Flume if it was started
        if flume_started:
            stop_flume_agent()

if __name__ == '__main__':
    run_demo()