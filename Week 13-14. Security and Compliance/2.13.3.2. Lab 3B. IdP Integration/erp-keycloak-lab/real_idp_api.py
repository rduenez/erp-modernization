from flask import Flask, request, jsonify
from functools import wraps
import jwt
from jwt import PyJWKClient

app = Flask(__name__)

# The endpoint where Keycloak publishes its public cryptographic keys
# Notice we use the Podman container name 'erp-keycloak'
JWKS_URL = "http://erp-keycloak:8080/realms/erp-realm/protocol/openid-connect/certs"

# PyJWKClient automatically fetches and caches the public keys from Keycloak
jwks_client = PyJWKClient(JWKS_URL)

def require_auth():
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            auth_header = request.headers.get('Authorization')
            if not auth_header or not auth_header.startswith("Bearer "):
                return jsonify({"error": "Missing token"}), 401
                
            token = auth_header.split(" ")[1]
            
            try:
                # 1. Fetch the correct public key to verify this specific token
                signing_key = jwks_client.get_signing_key_from_jwt(token)

                # 2. Cryptographically verify the token
                # NOTE: For local Podman testing, verify_aud and verify_iss are False 
                # because the token issuer might say 'localhost' while python sees 'erp-keycloak'
                decoded_claims = jwt.decode(
                    token,
                    signing_key.key,
                    algorithms=["RS256"],
                    options={"verify_aud": False, "verify_iss": False}
                )
                
            except jwt.ExpiredSignatureError:
                return jsonify({"error": "Token expired"}), 401
            except jwt.InvalidTokenError as e:
                return jsonify({"error": f"Invalid token: {e}"}), 401
                
            # 3. Extract the custom claims injected by Keycloak
            user_role = decoded_claims.get('custom:role')
            user_location = decoded_claims.get('custom:location')
            username = decoded_claims.get('preferred_username')
            
            return f(username, user_role, user_location, *args, **kwargs)
        return wrapped
    return decorator


@app.route('/api/inventory', methods=['GET'])
@require_auth()
def get_inventory(username, role, location):
    # RBAC & ABAC Business Logic
    if role != "WarehouseManager":
        return jsonify({"error": "Forbidden: Requires WarehouseManager role"}), 403
        
    return jsonify({
        "message": f"Welcome {username}. Access granted.",
        "data": f"Here is the highly confidential inventory data for the {location} facility."
    }), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5027)

