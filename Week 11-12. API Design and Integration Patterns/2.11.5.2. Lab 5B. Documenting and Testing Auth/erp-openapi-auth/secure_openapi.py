from flask import Flask, request, jsonify
from flasgger import Swagger
import jwt
import datetime
from functools import wraps

app = Flask(__name__)

# --- SWAGGER SECURITY CONFIGURATION ---
swagger_template = {
    "swagger": "2.0",
    "info": {
        "title": "ERP Secure API",
        "description": "API demonstrating JWT and API Key Auth via OpenAPI",
        "version": "1.0.0"
    },
    "securityDefinitions": {
        "BearerAuth": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",
            "description": "Enter your JWT in the format: Bearer <token>"
        },
        "ApiKeyAuth": {
            "type": "apiKey",
            "name": "x-api-key",
            "in": "header",
            "description": "Static API Key for payment processors"
        }
    }
}

swagger = Swagger(app, template=swagger_template)

# --- SECRETS & MOCK DB ---
JWT_SECRET_KEY = "my_super_secret_jwt_signing_key_2026"
PAYMENT_API_KEY = "pk_live_89874321_erp_payment_key"
users_db = {"sales_rep": "sellstuff2026"}

# --- MIDDLEWARE: JWT Validator ---
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({"error": "Missing or invalid Authorization header"}), 401
            
        token = auth_header.split(" ")[1]
        try:
            decoded_payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=["HS256"])
            request.current_user = decoded_payload["username"]
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
            return jsonify({"error": "Invalid or expired token"}), 401
            
        return f(*args, **kwargs)
    return decorated

# --- ROUTES ---

@app.route('/auth/login', methods=['POST'])
def login():
    """
    Login to receive a JWT
    ---
    tags:
      - Authentication
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            username:
              type: string
              example: "sales_rep"
            password:
              type: string
              example: "sellstuff2026"
    responses:
      200:
        description: Successful login
    """
    data = request.get_json()
    if data and data.get('username') in users_db and users_db[data.get('username')] == data.get('password'):
        exp = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=15)
        token = jwt.encode({"username": data.get('username'), "exp": exp}, JWT_SECRET_KEY, algorithm="HS256")
        return jsonify({"token": token}), 200
    return jsonify({"error": "Invalid credentials"}), 401


@app.route('/api/v1/inventory', methods=['GET'])
@token_required
def get_inventory():
    """
    Get current inventory (Requires JWT)
    ---
    tags:
      - Protected ERP Data
    security:
      - BearerAuth: []
    responses:
      200:
        description: Inventory data accessed successfully
      401:
        description: Unauthorized
    """
    return jsonify({
        "message": f"Welcome {request.current_user}.",
        "data": [{"item": "Laptop", "stock": 45}]
    }), 200


@app.route('/api/v1/process-payment', methods=['POST'])
def process_payment():
    """
    Process a payment (Requires Static API Key)
    ---
    tags:
      - Protected ERP Data
    security:
      - ApiKeyAuth: []
    responses:
      200:
        description: Payment Processed
      401:
        description: Invalid API Key
    """
    api_key = request.headers.get('x-api-key')
    if not api_key or api_key != PAYMENT_API_KEY:
        return jsonify({"error": "Unauthorized"}), 401
    return jsonify({"status": "Payment Processed Successfully"}), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5007)

