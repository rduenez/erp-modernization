mkdir erp-api-lab
cd erp-api-lab
podman network create api-network

# Run external SAT API
podman run --name external-sat-api --network api-network -v .:/app -d api-base python sat_api.py

# Run internal Inventory API
podman run --name internal-inv-api --network api-network -v .:/app -d api-base python inventory_api.py

# Run script to checkout items
podman run --rm -v .:/app --network api-network api-base python checkout.py