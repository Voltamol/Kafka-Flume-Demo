#!/usr/bin/env python3
"""
Inventory Service - Standalone script for multi-terminal demo
Run this in Terminal 4
"""

from kafka import KafkaConsumer
import json
import sys

def main():
    print("=" * 70)
    print("📊 INVENTORY SERVICE")
    print("=" * 70)
    print("Listening for inventory updates from Kafka topic 'inventory'...")
    print("Will track stock levels in real-time")
    print("=" * 70 + "\n")
    
    # Initial stock levels
    stock = {
        "Laptop": 50,
        "Headphones": 100,
        "Keyboard": 75,
        "Mouse": 120,
        "Monitor": 30,
        "Webcam": 45
    }
    
    print("📦 Current Stock Levels:")
    for product, qty in stock.items():
        print(f"   {product}: {qty} units")
    print()
    
    try:
        consumer = KafkaConsumer(
            'inventory',
            bootstrap_servers='localhost:9092',
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            group_id='inventory-service',
            auto_offset_reset='earliest'
        )
        
        print("✅ Connected to Kafka. Waiting for inventory updates...\n")
        
        for message in consumer:
            update = message.value
            product = update['product']
            quantity_sold = update['quantity_sold']
            order_id = update.get('order_id', 'N/A')
            
            # Update stock
            if product in stock:
                old_stock = stock[product]
                stock[product] -= quantity_sold
                
                print(f"📊 Inventory Update:")
                print(f"   Order: {order_id}")
                print(f"   Product: {product}")
                print(f"   Sold: {quantity_sold} units")
                print(f"   Previous Stock: {old_stock} units")
                print(f"   New Stock: {stock[product]} units")
                
                # Low stock alert
                if stock[product] < 20:
                    print(f"   ⚠️  LOW STOCK ALERT! Only {stock[product]} units remaining!")
                else:
                    print(f"   ✅ Stock level OK")
            else:
                print(f"⚠️  Unknown product: {product}")
            
            print()
            
    except KeyboardInterrupt:
        print("\n\n⏹️  Inventory service stopped.")
        print("\n📦 Final Stock Levels:")
        for product, qty in stock.items():
            print(f"   {product}: {qty} units")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()

