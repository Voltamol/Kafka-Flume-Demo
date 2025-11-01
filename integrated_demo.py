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
# MAIN EXECUTION
# ============================================================================

def run_integrated_demo():
    print("\n" + "=" * 70)
    print("🚀 INTEGRATED KAFKA DEMO: STARTING ALL MICROSERVICES")
    print("=" * 70)
    print("All services are running in background threads...")
    print("The Flume agent (running in its own terminal) is also reading 'orders'.\n")
    
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
    
    print("\n✨ Demo completed! Check Flume terminal and HDFS for archived data.")
    print("=" * 70)

if __name__ == '__main__':
    run_integrated_demo()