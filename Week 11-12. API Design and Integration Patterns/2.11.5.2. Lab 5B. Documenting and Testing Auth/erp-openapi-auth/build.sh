mkdir erp-openapi-auth
cd erp-openapi-auth

# Create a Dockerfile with the necessary tools for testing and documenting the API
podman build -t openapi-auth-tools .

# Run the container to test and document the API
podman run --name erp-openapi-auth-api -v .:/app -p 5007:5007 --rm -d openapi-auth-tools python secure_openapi.py
