Here's the Windows version of your commands:

## Windows Setup Commands

### 1. Start Hadoop (Windows)

```cmd
REM 1. Start Hadoop
start-dfs.cmd
jps

REM If NameNode problems occur:
REM Format the namenode
hdfs namenode -format

REM Start HDFS
start-dfs.cmd

REM Verify it's running
jps
```

**Note for persistent storage on Windows:**
Edit `%HADOOP_HOME%\etc\hadoop\core-site.xml` and `hdfs-site.xml` to use a path like `C:\hadoop_data` instead of `C:\tmp\hadoop-username`.

---

### 2. Start Kafka (Docker on Windows)

```cmd
REM Start Kafka container
docker start kafka
docker ps | findstr kafka
```

---

### 3. Create Demo Directory in HDFS

```cmd
REM Create demo directory
hdfs dfs -mkdir -p /demo/weblogs
hdfs dfs -ls /demo

REM Test everything
echo Ready for demo!
```

---

### 4. Create Kafka Topics (Windows)

```cmd
REM Create orders topic
docker exec -it kafka /opt/kafka/bin/kafka-topics.sh --create --topic orders --bootstrap-server localhost:9092 --partitions 3

REM Create notifications topic
docker exec -it kafka /opt/kafka/bin/kafka-topics.sh --create --topic notifications --bootstrap-server localhost:9092

REM Create inventory topic
docker exec -it kafka /opt/kafka/bin/kafka-topics.sh --create --topic inventory --bootstrap-server localhost:9092

REM List all topics
docker exec -it kafka /opt/kafka/bin/kafka-topics.sh --list --bootstrap-server localhost:9092
```

---

## Multi-Terminal Setup (Windows PowerShell/CMD)

### Terminal 1: Main Demo
```powershell
python integrated_demo.py
```

### Terminal 2: HDFS Monitoring (PowerShell)
```powershell
# Windows doesn't have 'watch', so use a loop
while($true) {
    Clear-Host
    $date = Get-Date -Format "yyyy-MM-dd"
    hdfs dfs -ls "/archive/orders/$date" 2>$null
    Start-Sleep -Seconds 2
}
```

**Or in CMD:**
```cmd
:loop
cls
hdfs dfs -ls /archive/orders/2025-11-01 2>nul
timeout /t 2 /nobreak >nul
goto loop
```

### Terminal 3: Kafka Monitoring
```cmd
docker exec -it kafka /opt/kafka/bin/kafka-console-consumer.sh --topic orders --bootstrap-server localhost:9092 --from-beginning
```

---

## Reading JSON Files from HDFS (Windows)

### Method 1: Read specific file
```cmd
hdfs dfs -cat /archive/orders/2025-11-01/orders-archive.1761997651647.json
```

### Method 2: Read all files from today
```cmd
REM Raw view (no jq on Windows by default)
hdfs dfs -cat "/archive/orders/2025-11-01/*.json" | more

REM If you have jq installed (via Chocolatey: choco install jq)
hdfs dfs -cat "/archive/orders/2025-11-01/*.json" | jq .

REM View first 20 lines
hdfs dfs -cat "/archive/orders/2025-11-01/*.json" | findstr /N "^" | findstr "^[1-9]:"
```

### Method 3: Download to local filesystem
```cmd
REM Copy to Downloads folder
hdfs dfs -get /archive/orders/2025-11-01/*.json %USERPROFILE%\Downloads\

REM Then read locally
type %USERPROFILE%\Downloads\orders-archive*.json

REM With jq (if installed)
type %USERPROFILE%\Downloads\orders-archive*.json | jq .
```

---

## Searching/Filtering Orders (Windows)

```cmd
REM Find orders by customer (use findstr instead of grep)
hdfs dfs -cat "/archive/orders/2025-11-01/*.json" | findstr "\"customer\": \"Alice\""

REM Find orders by product
hdfs dfs -cat "/archive/orders/2025-11-01/*.json" | findstr "\"product\": \"Laptop\""

REM Count total orders (PowerShell is better for this)
```

**PowerShell version for counting:**
```powershell
(hdfs dfs -cat "/archive/orders/2025-11-01/*.json" | Select-String "order_id").Count
```

---

## Key Windows Differences:

| Linux/Mac | Windows Equivalent |
|-----------|-------------------|
| `start-dfs.sh` | `start-dfs.cmd` |
| `stop-dfs.sh` | `stop-dfs.cmd` |
| `grep` | `findstr` |
| `watch` | PowerShell loop or `:loop` in CMD |
| `~/Downloads` | `%USERPROFILE%\Downloads` |
| `2>/dev/null` | `2>nul` |
| `\|` (pipe) | `\|` (same) |

---

## Installing Missing Tools on Windows:

If you need Linux-like commands on Windows:

### Option 1: Use PowerShell (recommended)
Most commands work better in PowerShell than CMD.

### Option 2: Install Git Bash
Comes with Git for Windows and provides bash shell.

### Option 3: Install Chocolatey package manager
```powershell
# Install jq for JSON parsing
choco install jq

# Install grep-like tools
choco install gnuwin32-grep
```

### Option 4: Use WSL (Windows Subsystem for Linux)
Run actual Linux commands on Windows:
```powershell
wsl
# Now you can use bash commands
```

Would you like me to help you set up any specific part of this on Windows, or create a complete Windows batch script for your demo?