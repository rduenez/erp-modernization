mkdir erp-gateway-lab
cd erp-gateway-lab
podman network create gateway-network

# Create a Dockerfile for the legacy backend API
podman build -t legacy-backend .

# Run the legacy backend API container
podman run --name erp-legacy-api --network gateway-network -v .:/app --rm -d legacy-backend python legacy_api.py

# Create a Dockerfile for the Kong API Gateway
podman run -d --name kong-gateway --network gateway-network -e "KONG_DATABASE=off" -e "KONG_DECLARATIVE_CONFIG=/kong.yml" -e "KONG_PROXY_ACCESS_LOG=/dev/stdout" -e "KONG_PROXY_ERROR_LOG=/dev/stderr" -v ./kong.yml:/kong.yml -p 8000:8000 kong:3.6

curl -s http://localhost:5011/inventory

curl -i http://localhost:8000/api/v1/inventory

curl -i http://localhost:8000/api/v1/inventory \
     -H "x-api-key: hacker_key_123"

curl -s -X GET http://localhost:8000/api/v1/inventory \
     -H "x-api-key: kong_super_secret_key_2026"
