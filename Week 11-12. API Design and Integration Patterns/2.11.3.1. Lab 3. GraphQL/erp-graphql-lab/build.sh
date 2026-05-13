mkdir erp-graphql-lab
cd erp-graphql-lab

# Build the GraphQL API container
podman build -t graphql-api-app .

podman run --name erp-graphql-api -v .:/app -p 5004:5004 --rm -d graphql-api-app python graphql_api.py

curl -s -X POST "http://localhost:5005/webhook/order-ready" \
     -H "Content-Type: application/json" \
     -H "X-ERP-Signature: sha256=fake_hacker_signature" \
     -d '{"order_id": "FREE-STUFF", "shipping_address": "Hacker House"}'
