import pika
import json
import sys

def request_report(month, year):
    # Connect to RabbitMQ
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbit-broker'))
    channel = connection.channel()

    # Ensure the queue exists (in case the API starts before the worker)
    channel.queue_declare(queue='financial_reports', durable=True)

    # The data we want the worker to process
    job_data = {
        "month": month,
        "year": year,
        "requested_by": "admin_user"
    }

    # Drop the message into the queue
    channel.basic_publish(
        exchange='',
        routing_key='financial_reports',
        body=json.dumps(job_data),
        properties=pika.BasicProperties(
            delivery_mode=2,  # Make message persistent (survives RabbitMQ restarts)
        )
    )
    
    print(f"[ERP API] Fast Response: Report request for {month} {year} accepted. You will receive an email when it is ready.")
    connection.close()

if __name__ == '__main__':
    # Simulate a user clicking "Generate Report" 3 times in a row
    request_report("January", 2026)
    request_report("February", 2026)
    request_report("March", 2026)

