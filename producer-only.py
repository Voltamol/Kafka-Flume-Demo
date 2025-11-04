#!/usr/bin/env python3
"""
Order Producer - Standalone script for multi-terminal demo
Run this in Terminal 1 (after starting services)
"""

from kafka import KafkaProducer
import json
import time
import random
import sys
from datetime import datetime

def main():
    products = [
        {"name": "Laptop", "price": 999.99},
        {"name": "Headphones", "price": 79.99},
        {"name": "Keyboard", "price": 49.99},
        {"name": "Mouse", "price": 29.99},
        {"name": "Monitor", "price": 299.99},
        {"name": "Webcam", "price": 89.99}
    ]
    
    customers = ["Alice", "Bob", "Charlie", "Diana", "Eve"]
    
    print("=" * 70)
    print("🛒 E-COMMERCE ORDER PRODUCER")
    print("=" * 70)
    print("Generating orders and sending to Kafka topic 'orders'...")
    print("=" * 70 + "\n")
    
    try:
        producer = KafkaProducer(
            bootstrap_servers='localhost:9092',
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
        
        print("✅ Connected to Kafka. Starting order generation...\n")
        
        num_orders = int(input("How many orders to generate? (default 5): ") or "5")
        delay = float(input("Delay between orders in seconds? (default 2): ") or "2")
        
        print(f"\n🚀 Generating {num_orders} orders...\n")
        
        for i in range(num_orders):
            product = random.choice(products)
            customer = random.choice(customers)
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
            
            producer.send('orders', value=order)
            producer.flush()
            
            print(f"✅ Order #{i+1} Placed:")
            print(f"   Order ID: {order['order_id']}")
            print(f"   Customer: {order['customer']}")
            print(f"   Product: {order['product']} x {order['quantity']}")
            print(f"   Total: ${order['total']}")
            print(f"   → Sent to Kafka topic: 'orders'\n")
            
            time.sleep(delay)
        
        print("✨ All orders sent to Kafka!")
        producer.close()
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Producer stopped.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()

