mkdir erp-webhook-lab
cd erp-webhook-lab
podman network create webhook-network

podman build -t webhook-tools .

# Run the shipping API receiver
podman run --name shipping-api --network webhook-network -v .:/app -p 5005:5005 --rm -d webhook-tools python shipping_receiver.py

# Run the ERP publisher
podman run --rm -v .:/app --network webhook-network webhook-tools python erp_publisher.py
