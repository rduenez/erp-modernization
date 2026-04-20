podman run --rm -v .:/app erp-migration-tools alembic init migrations
podman run --rm -v .:/app --network erp-network erp-migration-tools alembic revision -m "add_orders_table"
podman run --rm -v .:/app --network erp-network erp-migration-tools alembic upgrade head