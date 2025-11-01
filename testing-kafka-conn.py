from kafka import KafkaProducer
try:
    producer = KafkaProducer(
        bootstrap_servers='localhost:9092',
        request_timeout_ms=5000
    )
    print('✅ Python → Kafka connection SUCCESS!')
    producer.close()
except Exception as e:
    print(f'❌ Connection failed: {e}')