import pika
import time
import json

def process_heavy_report(ch, method, properties, body):
    data = json.loads(body)
    print(f"\n[WORKER] Received request to generate report for: {data['month']} {data['year']}")
    print(f"[WORKER] Generating PDF... this will take some time...")
    
    # Simulate a heavy, time-consuming process
    time.sleep(5) 
    
    print(f"[WORKER] -> PDF Report for {data['month']} {data['year']} completed and emailed to user!")
    
    # Acknowledge the message so RabbitMQ removes it from the queue
    ch.basic_ack(delivery_tag=method.delivery_tag)

def start_worker():
    # Connect to RabbitMQ container
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbit-broker'))
    channel = connection.channel()

    # Ensure the queue exists
    channel.queue_declare(queue='financial_reports', durable=True)

    # Tell RabbitMQ to send messages to our processing function
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue='financial_reports', on_message_callback=process_heavy_report)

    print('[WORKER] Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()

if __name__ == '__main__':
    print('[WORKER] MAIN')
    start_worker()

