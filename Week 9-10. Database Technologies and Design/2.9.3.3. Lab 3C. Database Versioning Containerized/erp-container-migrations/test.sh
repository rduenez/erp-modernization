podman run --name erp-db --network erp-network -e POSTGRES_PASSWORD=supersecret -p 5434:5432 -d postgres:15
podman run --rm -v .:/app --network erp-network erp-migration-tools alembic revision --autogenerate -m "conciliate"

