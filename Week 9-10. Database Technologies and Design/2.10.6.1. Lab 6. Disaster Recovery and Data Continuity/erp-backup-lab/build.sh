mkdir erp-backup-lab
cd erp-backup-lab

podman run --name prod-db -e POSTGRES_PASSWORD=supersecret -p 5439:5432 -d postgres:15

# Dump entire database to a file
podman exec -t prod-db pg_dump -U postgres -c postgres > prod_full_backup.sql

# Restore the database from the backup file
cat prod_full_backup.sql | podman exec -i prod-db psql -U postgres -d postgres

