from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

# Generate a simulated SAT Private Key (FIEL / CSD)
private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)

# Save the private key to a file (In reality, this is heavily password protected)
with open("mock_fiel.key", "wb") as key_file:
    key_file.write(private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    ))
print("Mock SAT Private Key (mock_fiel.key) generated successfully.")
