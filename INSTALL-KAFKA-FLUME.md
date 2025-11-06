# Installing Apache Kafka and Apache Flume

This guide explains quick installation steps for Apache Kafka and Apache Flume on macOS and Linux. It covers common methods (Homebrew for macOS, tarball/manual install for Linux/macOS), basic configuration, and how to verify both services are working.

> Tested concepts: Kafka (broker), Flume agent (source -> channel -> sink). This guide assumes a single-machine/dev setup.

---

## Prerequisites

- Java 8+ (OpenJDK 8/11/17+). Verify with:

  zsh: java -version

- Sufficient disk space and networking between components.

- Optional on macOS: Homebrew installed (https://brew.sh)

---

## Install Apache Kafka

Two common methods are shown: Homebrew (macOS) and manual tarball (macOS/Linux).

### A. macOS — Homebrew (quick)

1. Update Homebrew and install:

   zsh: brew update && brew install kafka

2. Start Kafka (Homebrew may install and run Zookeeper/ Kafka as services):

   zsh: brew services start zookeeper

   zsh: brew services start kafka

3. Verify broker is running by listing topics (default broker: localhost:9092):

   zsh: kafka-topics --bootstrap-server localhost:9092 --list

Notes: Homebrew package names can change; if `kafka` is not available search `brew search kafka`.

### B. Manual tarball (macOS / Linux)

1. Download Kafka (choose a recent stable release) from https://kafka.apache.org/downloads. Example (replace version):

   zsh: curl -O https://downloads.apache.org/kafka/3.5.0/kafka_2.13-3.5.0.tgz

2. Extract and move into a preferred location:

   zsh: tar -xzf kafka_2.13-3.5.0.tgz

   zsh: mv kafka_2.13-3.5.0 /usr/local/kafka

3. (Optional) Use Zookeeper (legacy) or KRaft (newer Kafka without Zookeeper).

- Start Zookeeper (if using legacy mode):

  zsh: /usr/local/kafka/bin/zookeeper-server-start.sh -daemon /usr/local/kafka/config/zookeeper.properties

- Start Kafka broker (legacy with Zookeeper):

  zsh: /usr/local/kafka/bin/kafka-server-start.sh -daemon /usr/local/kafka/config/server.properties

- For KRaft mode, follow Kafka release notes and configure `kafka/server.properties` for controller quorum and node id.

4. Verify:

   zsh: /usr/local/kafka/bin/kafka-topics.sh --bootstrap-server localhost:9092 --list

5. Create a test topic and send/consume messages:

   zsh: /usr/local/kafka/bin/kafka-topics.sh --create --topic test --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1

   zsh: /usr/local/kafka/bin/kafka-console-producer.sh --topic test --bootstrap-server localhost:9092

   zsh: /usr/local/kafka/bin/kafka-console-consumer.sh --topic test --bootstrap-server localhost:9092 --from-beginning

---

## Install Apache Flume

Apache Flume is typically installed from a binary tarball.

### A. Download and extract

1. Get a Flume release from https://flume.apache.org or the Apache mirrors. Example:

   zsh: curl -O https://downloads.apache.org/flume/1.9.0/apache-flume-1.9.0-bin.tar.gz

2. Extract and move:

   zsh: tar -xzf apache-flume-1.9.0-bin.tar.gz

   zsh: mv apache-flume-1.9.0-bin /usr/local/flume

3. Set FLUME_HOME (optional, add to ~/.zshrc):

   export FLUME_HOME=/usr/local/flume

   export PATH="$FLUME_HOME/bin:$PATH"

### B. Configure a Flume agent

Flume agents run with a config file describing sources, channels and sinks. Example minimal `agent.conf` for reading a file and sending to Kafka:

agent.sources = r1
agent.channels = c1
agent.sinks = k1

agent.sources.r1.type = spooldir
agent.sources.r1.spoolDir = /path/to/spooldir

agent.channels.c1.type = memory
agent.channels.c1.capacity = 10000

agent.sinks.k1.type = org.apache.flume.sink.kafka.KafkaSink
agent.sinks.k1.topic = orders
agent.sinks.k1.brokerList = localhost:9092

agent.sources.r1.channels = c1
agent.sinks.k1.channel = c1

Adjust plugin / sink class names depending on Flume version and connectors installed.

### C. Start a Flume agent

   zsh: $FLUME_HOME/bin/flume-ng agent -n agent -c conf -f /path/to/agent.conf -Dflume.root.logger=INFO,console

This starts the agent named in the config (here `agent`).

---

## Windows Installation

### Prerequisites

- Java 8+ (OpenJDK or Oracle JDK). Verify with:

  cmd: java -version

- Download and install 7-Zip or WinRAR for extracting tar.gz files.
- Ensure environment variables (JAVA_HOME, PATH) are set correctly.

### Install Apache Kafka on Windows

1. Download Kafka from https://kafka.apache.org/downloads (choose a recent release, e.g. kafka_2.13-3.5.0.tgz).
2. Extract the archive using 7-Zip or WinRAR:
   - Right-click the .tgz file > Extract Here (twice, for .tgz then .tar)
   - Move the extracted folder to a preferred location (e.g. C:\kafka)
3. Open Command Prompt and navigate to the Kafka directory:

   cmd: cd C:\kafka

4. Start Zookeeper (legacy mode):

   cmd: bin\windows\zookeeper-server-start.bat config\zookeeper.properties

5. In a new Command Prompt, start Kafka broker:

   cmd: bin\windows\kafka-server-start.bat config\server.properties

6. Verify broker is running:

   cmd: bin\windows\kafka-topics.bat --bootstrap-server localhost:9092 --list

7. Create a topic and test producer/consumer:

   cmd: bin\windows\kafka-topics.bat --create --topic test --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1
   cmd: bin\windows\kafka-console-producer.bat --topic test --bootstrap-server localhost:9092
   cmd: bin\windows\kafka-console-consumer.bat --topic test --bootstrap-server localhost:9092 --from-beginning

### Install Apache Flume on Windows

1. Download Flume from https://flume.apache.org (e.g. apache-flume-1.9.0-bin.tar.gz).
2. Extract using 7-Zip or WinRAR:
   - Right-click the .tar.gz file > Extract Here (twice)
   - Move the folder to a preferred location (e.g. C:\flume)
3. Flume is not officially supported on Windows, but can run with Cygwin or Windows Subsystem for Linux (WSL). For native Windows, use WSL:
   - Install WSL (https://docs.microsoft.com/en-us/windows/wsl/install)
   - Copy Flume files to your WSL home directory
   - Run Flume commands in the WSL terminal as on Linux/macOS

#### Example Flume agent start (in WSL):

   $FLUME_HOME/bin/flume-ng agent -n agent -c conf -f /path/to/agent.conf -Dflume.root.logger=INFO,console

### Notes

- For production, Linux is recommended for Flume. On Windows, use WSL for best compatibility.
- Ensure ports 9092 (Kafka) and 2181 (Zookeeper) are open in Windows Firewall.
- Use separate Command Prompt windows for each service.

---

## Verifying integration (Flume -> Kafka)

1. Ensure Kafka topic exists (`orders` in example).
2. Start a consumer to watch the topic:

   zsh: /usr/local/kafka/bin/kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic orders --from-beginning

3. Place a test file into Flume spoolDir (or send data to configured source). Flume should read and publish messages to Kafka.

---

## Troubleshooting

- Java: ensure JAVA_HOME points to a supported JDK.
- Ports: Kafka default 9092, Zookeeper 2181 — ensure not blocked by firewall.
- Logs: Kafka logs in `logs/` (broker), Flume logs to console or log files under FLUME_HOME.
- Connector classes: Kafka sink class names changed across Flume versions — consult Flume docs.

---

## Useful links

- Kafka downloads and docs: https://kafka.apache.org
- Flume downloads and docs: https://flume.apache.org
- Homebrew: https://brew.sh

---

If you want, I can add sample systemd service files, a macOS launchd plist, or a packaged Docker Compose example to run Kafka + Zookeeper + Flume quickly. Specify which one and it will be added.
