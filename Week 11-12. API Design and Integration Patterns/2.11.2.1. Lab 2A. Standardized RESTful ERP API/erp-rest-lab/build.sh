mkdir erp-rest-lab
cd erp-rest-lab

# Start the persistent database
podman run --name openapi-db --network openapi-network -e POSTGRES_PASSWORD=supersecret -p 5441:5432 -d postgres:15

# Run API in a container
podman run --name erp-openapi-api --network openapi-network -v .:/app -p 5003:5003 --rm -d openapi-api-app python db_api.py


curl -X POST -t "http://localhost:5003/api/v1/products" -H "accept: application/json" -H "Content-Type: application/json" -d "{ \"name\": \"Enterprise Server\", \"price\": 4500}"