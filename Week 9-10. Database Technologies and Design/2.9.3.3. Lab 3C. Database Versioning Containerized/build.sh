mkdir erp-container-migrations
cd erp-container-migrations

# Create a custom network so containers can resolve each other by name
podman network create erp-network

podman run --name erp-db-server --network erp-network -e POSTGRES_PASSWORD=supersecret -p 5434:5432 -d postgres:15
podman build -t erp-migration-tools .
