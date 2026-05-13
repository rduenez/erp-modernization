mkdir erp-integration-lab
cd erp-integration-lab
podman network create integration-network


# Create a Dockerfile for the integration tools
podman build -t integration-tools .

# Run the external services container
podman run --name external-services -v .:/app --network integration-network -p 5010:5010 --rm -d integration-tools python external_apis.py

# Run the ERP orchestrator container
podman run --rm -v .:/app --network integration-network integration-tools python erp_orchestrator.py
