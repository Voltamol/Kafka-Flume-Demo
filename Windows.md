# Windows Version: Integrated Kafka → Flume → HDFS Demo Guide

## Overview
This guide explains the complete data pipeline demonstration: **Kafka → Microservices → Flume → HDFS** on **Windows**. The demo shows how real-time order processing works with automatic data archival.

## Architecture Diagram
*(Same as original - architecture doesn't change)*

## Components Explained
*(Same as original - components don't change)*

## Prerequisites

### 1. **Kafka** (Must be running)
```cmd
:: Check if Kafka is running (if using Docker)
docker ps | findstr "kafka"

:: If using native Windows Kafka, check services
sc query | findstr "kafka"
```

### 2. **HDFS** (Must be running)
```cmd
:: Start HDFS (if using Hadoop for Windows)
start-dfs.cmd

:: Or check if Hadoop services are running
jps | findstr "NameNode"
jps | findstr "DataNode"
```

### 3. **Python Environment**
```cmd
:: Activate virtual environment
kafka-demo-env\Scripts\activate

:: Verify Kafka library is installed
python -c "from kafka import KafkaProducer; print('✅ Ready')"
```

### 4. **Flume Configuration**
- ✅ `flume-kafka-hdfs.conf` exists
- ✅ `flume-config-override/flume-env.sh` exists (sets Java memory)

## Running the Demo

### Option 1: Integrated Demo (Recommended)

**Single Command Prompt Approach:**
```cmd
cd C:\Users\voltamol\Documents\GitHub\Kafka-Flume-Demo
kafka-demo-env\Scripts\activate
python integrated_demo.py
```

**What Happens:**
1. Flume agent starts automatically
2. All microservices start in background threads
3. You'll see output from all components in one terminal
4. Orders are generated automatically
5. Everything processes in real-time

### Option 2: Interactive Demo
```cmd
cd C:\Users\voltamol\Documents\GitHub\Kafka-Flume-Demo
kafka-demo-env\Scripts\activate
python kafka-demo.py
```

**Choose Option 3** (Full Demo) when prompted.

### What You'll See
*(Same output as original)*

## Multi-Command Prompt Setup (Optional)

For a more impressive presentation, you can monitor different aspects:

### Command Prompt 1: Main Demo
```cmd
python integrated_demo.py
```

### Command Prompt 2: HDFS Monitoring
```cmd
:: Create a batch file hdfs_watch.bat with:
:: @echo off
:: :loop
:: hdfs dfs -ls /archive/orders/%date:~10,4%-%date:~4,2%-%date:~7,2% 2>nul
:: timeout /t 2 >nul
:: goto loop

:: Then run:
hdfs_watch.bat
```

### Command Prompt 3: Kafka Monitoring
```cmd
:: If using Docker
docker exec -it kafka /opt/kafka/bin/kafka-console-consumer.sh --topic orders --bootstrap-server localhost:9092 --from-beginning

:: If using native Windows Kafka
.\kafka\bin\windows\kafka-console-consumer.bat --topic orders --bootstrap-server localhost:9092 --from-beginning
```

## Verification

### 1. Check Flume is Running
```cmd
tasklist | findstr "flume"
:: Should show Flume process
```

### 2. Check Kafka Topics
```cmd
:: If using Docker
docker exec kafka /opt/kafka/bin/kafka-topics.sh --list --bootstrap-server localhost:9092

:: If using native Windows Kafka
.\kafka\bin\windows\kafka-topics.bat --list --bootstrap-server localhost:9092
:: Should show: orders, inventory, notifications
```

### 3. Check HDFS Files
```cmd
:: List archived files (using current date)
for /f "tokens=2-4 delims=/ " %a in ('date /t') do set currentdate=%c-%a-%b
hdfs dfs -ls /archive/orders/%currentdate%

:: View sample data
hdfs dfs -cat /archive/orders/%currentdate%/*.json | head -5
```

### 4. Check Flume Consumer Group
```cmd
:: If using Docker
docker exec kafka /opt/kafka/bin/kafka-consumer-groups.sh --bootstrap-server localhost:9092 --group flume-archiver --describe

:: If using native Windows Kafka
.\kafka\bin\windows\kafka-consumer-groups.bat --bootstrap-server localhost:9092 --group flume-archiver --describe
:: Should show LAG = 0 (all messages consumed)
```

## Windows-Specific Troubleshooting

### Issue: "Connection refused" errors

**Solution:**
- Check Kafka: `docker ps | findstr "kafka"` or check Windows Services
- Check HDFS: `jps | findstr "NameNode"`
- Start missing services

### Issue: Flume shows no activity

**Possible Causes:**
1. **No new messages**: Flume already consumed existing messages. Generate new orders.
2. **HDFS not running**: Flume can't write. Start HDFS with `start-dfs.cmd`
3. **Kafka topic empty**: Check with Kafka console consumer

### Issue: NameNode won't start

**Solution:**
```cmd
:: Format NameNode (WARNING: This deletes existing HDFS data)
hdfs namenode -format -force

:: Then start HDFS
start-dfs.cmd
```

### Issue: "ModuleNotFoundError: No module named 'kafka'"

**Solution:**
```cmd
:: Make sure virtual environment is activated
kafka-demo-env\Scripts\activate

:: Verify
python -c "from kafka import KafkaProducer"
```

### Issue: Python script permission errors

**Solution:**
```cmd
:: Run as Administrator if needed, or check file permissions
```

### Issue: Path-related errors

**Solution:**
- Use Windows-style paths with backslashes
- Check that all file paths in configurations are correct for Windows

## Windows Batch Files for Common Tasks

### hdfs_watch.bat (for continuous HDFS monitoring)
```batch
@echo off
:loop
for /f "tokens=2-4 delims=/ " %%a in ('date /t') do set currentdate=%%c-%%a-%%b
echo Checking HDFS directory: /archive/orders/%currentdate%
hdfs dfs -ls /archive/orders/%currentdate% 2>nul
timeout /t 2 >nul
goto loop
```

### start_services.bat (to start all required services)
```batch
@echo off
echo Starting HDFS...
start-dfs.cmd
timeout /t 5

echo Checking services...
jps | findstr "NameNode"
jps | findstr "DataNode"

echo Ready to run demo!
```

## Key Differences from Mac/Linux Version

1. **Path Separators**: Use `\` instead of `/`
2. **Command Syntax**: Use Windows commands (`findstr` instead of `grep`, `tasklist` instead of `ps aux`)
3. **Virtual Environment**: Use `Scripts\activate` instead of `bin/activate`
4. **File Monitoring**: Use batch scripts instead of `watch` command
5. **Date Formatting**: Use Windows date commands instead of `date +%Y-%m-%d`

## Environment Variables Setup

Make sure these environment variables are set in Windows:
```cmd
:: Add to System Environment Variables
JAVA_HOME=C:\Program Files\Java\jdk1.8.0_xxx
HADOOP_HOME=C:\hadoop
FLUME_HOME=C:\apache-flume
PATH=%PATH%;%JAVA_HOME%\bin;%HADOOP_HOME%\bin;%FLUME_HOME%\bin
```

## Summary

This Windows version provides:
1. ✅ **Same functionality** as Mac/Linux version
2. ✅ **Windows-specific commands** and paths
3. ✅ **Batch scripts** for common tasks
4. ✅ **Troubleshooting guidance** for Windows-specific issues
5. ✅ **Complete pipeline** in one command

**Everything runs automatically on Windows** - just start the demo and watch the magic happen! 🎉

## Additional Windows Tips

- Run Command Prompt as Administrator if you encounter permission issues
- Use Windows Task Manager to monitor Java processes
- Check Windows Event Viewer for system-level errors
- Ensure your Windows firewall allows connections between services
- Consider using Windows Subsystem for Linux (WSL) if you prefer Linux commands