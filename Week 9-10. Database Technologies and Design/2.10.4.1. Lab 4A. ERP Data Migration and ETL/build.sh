mkdir erp-migration-lab
cd erp-migration-lab
podman network create migration-network

podman run --name target-erp-db --network migration-network -e POSTGRES_PASSWORD=supersecret -p 5435:5432 -d postgres:15
