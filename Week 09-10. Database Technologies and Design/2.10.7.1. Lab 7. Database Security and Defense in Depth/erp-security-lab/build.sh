mkdir erp-security-lab
cd erp-security-lab
podman network create sec-network

podman run --name sec-db --network sec-network -e POSTGRES_PASSWORD=superadmin -p 5440:5432 -d postgres:15

podman run --rm -v .:/app --network sec-network erp-sec-tools python vulnerable_app.py