#!/usr/bin/env python3
"""
Warehouse Service - Standalone script for multi-terminal demo
Run this in Terminal 2
"""

from kafka import KafkaConsumer, KafkaProducer
import json
import sys
import time

def main():
    print("=" * 70)
    print("📦 WAREHOUSE SERVICE")
    print("=" * 70)
    print("Listening for orders from Kafka topic 'orders'...")
    print("Will process orders and publish to 'inventory' and 'notifications' topics")
    print("=" * 70 + "\n")
    
    try:
        consumer = KafkaConsumer(
            'orders',
            bootstrap_servers='localhost:9092',
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            group_id='warehouse-service',
            auto_offset_reset='earliest'
        )
        
        producer = KafkaProducer(
            bootstrap_servers='localhost:9092',
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
        
        print("✅ Connected to Kafka. Waiting for orders...\n")
        
        for message in consumer:
            order = message.value
            print(f"📦 Processing Order: {order['order_id']}")
            print(f"   Customer: {order['customer']}")
            print(f"   Product: {order['product']} x {order['quantity']}")
            print(f"   Total: ${order['total']}")
            
            # Simulate processing
            print("   → Picking items from warehouse...")
            time.sleep(1)
            
            # Send to inventory topic
            inventory_update = {
                "product": order['product'],
                "quantity_sold": order['quantity'],
                "timestamp": order.get('timestamp', ''),
                "order_id": order['order_id']
            }
            producer.send('inventory', value=inventory_update)
            
            # Send to notifications topic
            notification = {
                "order_id": order['order_id'],
                "customer": order['customer'],
                "message": f"Your order for {order['product']} has been shipped!",
                "timestamp": order.get('timestamp', '')
            }
            producer.send('notifications', value=notification)
            
            producer.flush()
            
            print(f"   ✅ Order shipped!")
            print(f"   → Published to 'inventory' topic")
            print(f"   → Published to 'notifications' topic")
            print()
            
    except KeyboardInterrupt:
        print("\n\n⏹️  Warehouse service stopped.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()

