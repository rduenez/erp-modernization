mkdir erp-cia-lab
cd erp-cia-lab
podman network create secure-net

# Run DB container
podman run --name vault-db --network secure-net -e POSTGRES_PASSWORD=SuperComplexDbPass123! -d postgres:15

podman build -t cia-api .

podman run --name vault-api  --network secure-net --restart on-failure:5 -p 5020:5020 -v .:/app --rm=false -d cia-api python secure_vault.py
