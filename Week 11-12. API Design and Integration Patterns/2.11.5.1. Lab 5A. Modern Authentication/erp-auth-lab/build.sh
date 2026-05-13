mkdir erp-auth-lab
cd erp-auth-lab

# Build the container image
podman build -t auth-tools .

# Run the container and execute the secure_api.py script
podman run --name erp-auth-api -v .:/app -p 5006:5006 --rm -d auth-tools python secure_api.py
