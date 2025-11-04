#!/bin/bash
cd /Users/voltamol/Documents/GitHub/Kafka-Flume-Demo
flume-ng agent --conf-file flume-kafka-hdfs.conf --name agent --conf flume-config-override -Dflume.root.logger=INFO,console
