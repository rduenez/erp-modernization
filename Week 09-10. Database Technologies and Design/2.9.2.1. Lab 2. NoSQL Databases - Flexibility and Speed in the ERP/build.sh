# Start MongoDB (Document Store)
podman run --name erp-mongo -p 27017:27017 -d mongo:6

# Start Redis (Key-Value Store)
podman run --name erp-redis -p 6379:6379 -d redis:7-alpine

