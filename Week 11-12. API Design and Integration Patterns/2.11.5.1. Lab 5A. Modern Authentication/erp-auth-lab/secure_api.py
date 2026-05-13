from flask import Flask, request, jsonify
import jwt
import datetime
from functools import wraps

app = Flask(__name__)

# --- SECRETS & CONFIG ---
# In production, these NEVER live in the code. They come from environment variables or a Key Vault.
JWT_SECRET_KEY = "my_super_secret_jwt_signing_key_2026"
PAYMENT_API_KEY = "pk_live_89874321_erp_payment_key"

# Mock User Database
users_db = {
    "admin_user": "password123",
    "sales_rep": "sellstuff2026"
}

# --- MIDDLEWARE: JWT Validator ---
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        
        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({"error": "Missing or invalid Authorization header"}), 401
            
        token = auth_header.split(" ")[1]
        
        try:
            # Decode the token. If the signature is wrong or the token expired, this throws an error.
            decoded_payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=["HS256"])
            # Pass the decoded username to the actual route
            request.current_user = decoded_payload["username"]
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token has expired. Please log in again."}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token signature."}), 401
            
        return f(*args, **kwargs)
    return decorated


# --- 1. THE LOGIN ROUTE (Issues JWT) ---
@app.route('/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    # 1. Authenticate the user
    if username in users_db and users_db[username] == password:
        # 2. Generate the JWT (Stateless Token)
        expiration_time = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=15)
        
        payload = {
            "username": username,
            "role": "admin" if username == "admin_user" else "user",
            "exp": expiration_time # The token self-destructs in 15 minutes
        }
        
        token = jwt.encode(payload, JWT_SECRET_KEY, algorithm="HS256")
        
        return jsonify({"message": "Login successful", "token": token}), 200
        
    return jsonify({"error": "Invalid credentials"}), 401


# --- 2. PROTECTED ROUTE (Requires JWT) ---
@app.route('/api/v1/inventory', methods=['GET'])
@token_required
def get_inventory():
    # The token_required decorator verified the user.
    # Because JWTs are stateless, we didn't have to query a database to check if a session exists!
    return jsonify({
        "message": f"Welcome {request.current_user}. Access granted to inventory.",
        "data": [{"item": "Laptop", "stock": 45}]
    }), 200

# --- 3. API KEY ROUTE (Simulating Payment Processors) ---
@app.route('/api/v1/process-payment', methods=['POST'])
def process_payment():
    # Payment processors often use a static API key sent in a custom header
    api_key_header = request.headers.get('x-api-key')
    
    if not api_key_header or api_key_header != PAYMENT_API_KEY:
        return jsonify({"error": "Unauthorized. Invalid API Key."}), 401
        
    return jsonify({"status": "Payment Processed Successfully"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5006)


