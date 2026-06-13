mkdir erp-middleware-lab
cd erp-middleware-lab
podman network create middleware-network

# Start RabbitMQ broker
podman run -d --name rabbit-broker --network middleware-network -p 5672:5672 -p 15672:15672 rabbitmq:3-management

# Create a Dockerfile for the middleware tools
podman build -t middleware-tools .

# Run the worker and ERP API in separate containers
podman run --rm -v .:/app --network middleware-network middleware-tools python worker.py

# In another terminal, run the ERP API
podman run --rm -v .:/app --network middleware-network middleware-tools python erp_api.py
