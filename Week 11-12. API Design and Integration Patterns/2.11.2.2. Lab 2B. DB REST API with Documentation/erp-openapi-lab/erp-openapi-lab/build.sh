mkdir erp-openapi-lab
cd erp-openapi-lab
podman network create openapi-network

# Start the persistent database
podman run --name openapi-db --network openapi-network -e POSTGRES_PASSWORD=supersecret -p 5441:5432 -d postgres:15

# Build the API application container
podman build -t openapi-api-app .