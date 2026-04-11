podman build -t erp-inventory-api .
podman images
podman run -d -p 8080:8080 --name inventory-service erp-inventory-api
podman run -d --name erp-database -e POSTGRES_PASSWORD=supersecret postgres:15
podman ps
