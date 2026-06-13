mkdir erp-session-lab
cd erp-session-lab
podman network create session-network

# Start the Redis session store
podman run --name session-redis --network session-network -p 6381:6379 -d redis:7-alpine

# Build the session tools container
podman build -t session-tools .

# Start the authentication server
podman run --name erp-auth-server --network session-network -v .:/app -p 5021:5021 --rm -d session-tools python auth_server.py


