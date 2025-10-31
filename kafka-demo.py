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
# MAIN DEMO SCRIPT
# ============================================================================

def run_demo():
    print("\n" + "=" * 70)
    print("🎯 KAFKA REAL-TIME ORDER PROCESSING DEMO")
    print("=" * 70)
    print("\nThis demo shows how Kafka enables real-time event streaming")
    print("in an e-commerce platform with multiple microservices.\n")
    
    print("Choose a demo mode:")
    print("1. Producer Only (Generate orders)")
    print("2. Consumer Only (Process orders)")
    print("3. Full Demo (All services running)")
    
    choice = input("\nEnter choice (1-3): ").strip()
    
    if choice == "1":
        # Just produce orders
        producer = OrderProducer()
        producer.start_producing(num_orders=5, delay=2)
    
    elif choice == "2":
        # Run all consumers (for presentation, run in separate terminals)
        print("\n⚠️  For best presentation effect, run these in separate terminals:")
        print("   Terminal 1: python demo.py (choose option 2, select warehouse)")
        print("   Terminal 2: python demo.py (choose option 2, select notification)")
        print("   Terminal 3: python demo.py (choose option 2, select inventory)")
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

if __name__ == '__main__':
    run_demo()