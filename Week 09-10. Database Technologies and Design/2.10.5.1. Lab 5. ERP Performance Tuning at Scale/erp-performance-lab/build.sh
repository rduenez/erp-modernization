mkdir erp-performance-lab
cd erp-performance-lab
podman network create perf-network


# Primary ERP Database
podman run --name perf-db --network perf-network -e POSTGRES_PASSWORD=supersecret -p 5438:5432 -d postgres:15

# Redis Caching Layer
podman run --name perf-redis --network perf-network -p 6380:6379 -d redis:7-alpine

podman build -t erp-perf-tools .

