#!/usr/bin/env python3
"""
Helper script to read and analyze orders archived in HDFS
"""

import subprocess
import json
import sys
from datetime import datetime

def read_hdfs_orders(date=None):
    """Read orders from HDFS and parse JSON"""
    if date is None:
        date = datetime.now().strftime('%Y-%m-%d')
    
    hdfs_path = f'/archive/orders/{date}/*.json'
    
    try:
        # Read from HDFS
        result = subprocess.run(
            ['hdfs', 'dfs', '-cat', hdfs_path],
            capture_output=True,
            text=True,
            check=True
        )
        
        orders = []
        for line in result.stdout.strip().split('\n'):
            if line.strip():
                try:
                    order = json.loads(line)
                    orders.append(order)
                except json.JSONDecodeError:
                    continue
        
        return orders
    except subprocess.CalledProcessError as e:
        print(f"Error reading from HDFS: {e}", file=sys.stderr)
        return []

def print_summary(orders):
    """Print a summary of orders"""
    if not orders:
        print("No orders found.")
        return
    
    print(f"\n📊 ORDER SUMMARY")
    print("=" * 70)
    print(f"Total Orders: {len(orders)}")
    print(f"\nBy Customer:")
    customers = {}
    for order in orders:
        customer = order.get('customer', 'Unknown')
        customers[customer] = customers.get(customer, 0) + 1
    for customer, count in sorted(customers.items(), key=lambda x: -x[1]):
        print(f"  {customer}: {count} orders")
    
    print(f"\nBy Product:")
    products = {}
    for order in orders:
        product = order.get('product', 'Unknown')
        products[product] = products.get(product, 0) + 1
    for product, count in sorted(products.items(), key=lambda x: -x[1]):
        print(f"  {product}: {count} orders")
    
    total_revenue = sum(order.get('total', 0) for order in orders)
    print(f"\n💰 Total Revenue: ${total_revenue:,.2f}")
    print("=" * 70)

def print_orders(orders, limit=10):
    """Print individual orders"""
    print(f"\n📋 RECENT ORDERS (showing {min(limit, len(orders))} of {len(orders)})")
    print("=" * 70)
    
    for order in orders[-limit:]:
        print(f"Order ID: {order.get('order_id')}")
        print(f"  Customer: {order.get('customer')}")
        print(f"  Product: {order.get('product')} x {order.get('quantity')}")
        print(f"  Total: ${order.get('total', 0):.2f}")
        print(f"  Timestamp: {order.get('timestamp')}")
        print()

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Read orders from HDFS')
    parser.add_argument('--date', help='Date in YYYY-MM-DD format (default: today)')
    parser.add_argument('--summary', action='store_true', help='Show summary only')
    parser.add_argument('--limit', type=int, default=10, help='Limit number of orders to display')
    parser.add_argument('--all', action='store_true', help='Show all orders')
    
    args = parser.parse_args()
    
    orders = read_hdfs_orders(args.date)
    
    if args.summary:
        print_summary(orders)
    elif args.all:
        limit = len(orders)
        print_orders(orders, limit)
        print_summary(orders)
    else:
        print_orders(orders, args.limit)
        print_summary(orders)

