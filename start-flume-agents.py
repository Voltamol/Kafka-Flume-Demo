#!/usr/bin/env python3
"""
Start All Flume Agents - For multi-terminal demo
This script can start all three Flume agents separately
"""

import subprocess
import os
import sys
import time
import signal

flume_processes = {}

def start_flume_agent(name, config_file):
    """Start a Flume agent and return the process"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(script_dir, config_file)
    flume_env_dir = os.path.join(script_dir, 'flume-config-override')
    
    env = os.environ.copy()
    env['JAVA_OPTS'] = '-Xmx512m -Xms256m'
    
    flume_cmd = ['flume-ng', 'agent', '--conf-file', config_path, '--name', 'agent']
    
    if os.path.exists(flume_env_dir):
        flume_cmd.extend(['--conf', flume_env_dir])
        env['FLUME_CONF_DIR'] = flume_env_dir
    
    print(f"Starting Flume agent: {name}")
    print(f"  Config: {config_path}\n")
    
    try:
        process = subprocess.Popen(
            flume_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1,
            env=env
        )
        return process
    except Exception as e:
        print(f"❌ Error starting {name}: {e}")
        return None

def main():
    print("=" * 70)
    print("🚀 FLUME AGENTS MANAGER")
    print("=" * 70)
    print("This script helps you start Flume agents in separate terminals")
    print("=" * 70 + "\n")
    
    print("Available Flume agents:")
    print("1. Orders Archiver (flume-kafka-hdfs.conf)")
    print("2. Inventory Archiver (flume-kafka-inventory.conf)")
    print("3. Notifications Archiver (flume-kafka-notifications.conf)")
    print("4. Start all agents")
    print("5. Exit")
    
    choice = input("\nSelect agent to start (1-5): ").strip()
    
    agents = {
        '1': ('Orders Archiver', 'flume-kafka-hdfs.conf'),
        '2': ('Inventory Archiver', 'flume-kafka-inventory.conf'),
        '3': ('Notifications Archiver', 'flume-kafka-notifications.conf'),
    }
    
    if choice == '4':
        print("\n⚠️  Starting all agents...")
        print("Note: For best results, run each agent in a separate terminal\n")
        
        for key, (name, config) in agents.items():
            print(f"\n{'='*70}")
            print(f"To start {name}, run this command in a separate terminal:")
            print(f"{'='*70}")
            script_dir = os.path.dirname(os.path.abspath(__file__))
            config_path = os.path.join(script_dir, config)
            flume_env_dir = os.path.join(script_dir, 'flume-config-override')
            
            cmd = f"flume-ng agent --conf-file {config_path} --name agent"
            if os.path.exists(flume_env_dir):
                cmd += f" --conf {flume_env_dir}"
            cmd += f" -Dflume.root.logger=INFO,console"
            
            print(f"\n{cmd}\n")
        
        print("=" * 70)
        print("Or run each manually:")
        print("=" * 70)
        for key, (name, config) in agents.items():
            print(f"Terminal for {name}:")
            print(f"  cd {os.path.dirname(os.path.abspath(__file__))}")
            print(f"  flume-ng agent --conf-file {config} --name agent --conf flume-config-override")
            print()
    
    elif choice in agents:
        name, config = agents[choice]
        process = start_flume_agent(name, config)
        
        if process:
            print(f"✅ {name} started (PID: {process.pid})")
            print("Press Ctrl+C to stop\n")
            
            def signal_handler(sig, frame):
                print(f"\n\n⏹️  Stopping {name}...")
                process.terminate()
                try:
                    process.wait(timeout=5)
                    print(f"✅ {name} stopped.")
                except subprocess.TimeoutExpired:
                    process.kill()
                    print(f"⚠️  Force stopped {name}.")
                sys.exit(0)
            
            signal.signal(signal.SIGINT, signal_handler)
            signal.signal(signal.SIGTERM, signal_handler)
            
            # Stream output
            try:
                for line in iter(process.stdout.readline, ''):
                    if line:
                        print(f"[FLUME-{name}] {line.rstrip()}")
                        sys.stdout.flush()
            except Exception as e:
                print(f"Error: {e}")
    
    elif choice == '5':
        sys.exit(0)
    else:
        print("Invalid choice.")
        sys.exit(1)

if __name__ == '__main__':
    main()

