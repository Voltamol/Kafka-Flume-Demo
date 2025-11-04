#!/usr/bin/env python3
"""
Notification Service - Standalone script for multi-terminal demo
Run this in Terminal 3
"""

from kafka import KafkaConsumer
import json
import sys

def main():
    print("=" * 70)
    print("📧 NOTIFICATION SERVICE")
    print("=" * 70)
    print("Listening for notifications from Kafka topic 'notifications'...")
    print("Will send email notifications to customers")
    print("=" * 70 + "\n")
    
    try:
        consumer = KafkaConsumer(
            'notifications',
            bootstrap_servers='localhost:9092',
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            group_id='notification-service',
            auto_offset_reset='earliest'
        )
        
        print("✅ Connected to Kafka. Waiting for notifications...\n")
        
        for message in consumer:
            notification = message.value
            
            print(f"📧 Email Notification:")
            print(f"   To: {notification['customer']}")
            print(f"   Order: {notification['order_id']}")
            print(f"   Message: {notification['message']}")
            print(f"   → Email sent! ✅")
            print()
            
    except KeyboardInterrupt:
        print("\n\n⏹️  Notification service stopped.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()

