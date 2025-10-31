#!/usr/bin/env python3
"""
Flume Demo: Web Server Log Generator
Simulates a web server generating access logs for Flume to collect
"""

import random
import time
from datetime import datetime
import os

class WebLogGenerator:
    def __init__(self, log_file="/tmp/demo-webserver.log"):
        self.log_file = log_file
        
        self.ips = [
            "192.168.1.10", "192.168.1.25", "192.168.1.50",
            "10.0.0.15", "10.0.0.32", "172.16.0.8"
        ]
        
        self.methods = ["GET", "POST", "PUT", "DELETE"]
        
        self.urls = [
            "/", "/home", "/products", "/cart", "/checkout",
            "/api/users", "/api/products", "/api/orders",
            "/login", "/logout", "/profile", "/search"
        ]
        
        self.status_codes = [200, 200, 200, 200, 201, 304, 400, 404, 500]
        
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X)",
            "Mozilla/5.0 (Linux; Android 10) AppleWebKit/537.36"
        ]
    
    def generate_log_entry(self):
        """Generate a single Apache-style log entry"""
        ip = random.choice(self.ips)
        timestamp = datetime.now().strftime("%d/%b/%Y:%H:%M:%S +0000")
        method = random.choice(self.methods)
        url = random.choice(self.urls)
        status = random.choice(self.status_codes)
        size = random.randint(100, 50000)
        user_agent = random.choice(self.user_agents)
        
        # Apache Combined Log Format
        log = f'{ip} - - [{timestamp}] "{method} {url} HTTP/1.1" {status} {size} "-" "{user_agent}"'
        return log
    
    def start_generating(self, num_logs=100, delay=0.5):
        """Generate web server logs continuously"""
        print("=" * 80)
        print("🌐 WEB SERVER LOG GENERATOR")
        print("=" * 80)
        print(f"Writing logs to: {self.log_file}")
        print(f"Generating {num_logs} log entries...\n")
        
        # Create/clear log file
        with open(self.log_file, 'w') as f:
            f.write("")
        
        for i in range(num_logs):
            log_entry = self.generate_log_entry()
            
            # Append to log file
            with open(self.log_file, 'a') as f:
                f.write(log_entry + '\n')
            
            # Display
            print(f"[{i+1:3d}] {log_entry}")
            
            time.sleep(delay)
        
        print(f"\n✅ Generated {num_logs} log entries!")
        print(f"📁 Log file: {self.log_file}")
        print("=" * 80)

def main():
    print("\n" + "=" * 80)
    print("🎯 FLUME DEMO: WEB SERVER LOG COLLECTION")
    print("=" * 80)
    print("\nThis simulates a web server generating access logs.")
    print("Flume will automatically collect these logs and send them to HDFS.\n")
    
    print("Choose mode:")
    print("1. Generate 20 logs slowly (for presentation)")
    print("2. Generate 100 logs quickly (show volume)")
    print("3. Continuous generation (run until stopped)")
    
    choice = input("\nEnter choice (1-3): ").strip()
    
    generator = WebLogGenerator()
    
    if choice == "1":
        generator.start_generating(num_logs=20, delay=1.5)
    elif choice == "2":
        generator.start_generating(num_logs=100, delay=0.2)
    elif choice == "3":
        print("\n🔄 Generating logs continuously... (Press Ctrl+C to stop)\n")
        try:
            while True:
                generator.start_generating(num_logs=10, delay=1)
                time.sleep(2)
        except KeyboardInterrupt:
            print("\n\n⏹️  Stopped generating logs")

if __name__ == '__main__':
    main()