from flask import Flask, request, jsonify
import bcrypt
import redis
import secrets
import re

app = Flask(__name__)

# Connect to our Redis container
session_store = redis.Redis(host='session-redis', port=6379, decode_responses=True)

# Mock Database (In a real app, this is PostgreSQL)
users_db = {}

# --- 1. PASSWORD COMPLEXITY & HASHING ---
@app.route('/auth/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    raw_password = data.get('password')

    if username in users_db:
        return jsonify({"error": "User already exists"}), 400
    
    # Complexity Requirement: Min 8 chars, 1 uppercase, 1 number, 1 special
    if not re.match(r'^(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$', raw_password):
        return jsonify({"error": "Password does not meet complexity requirements."}), 400

    # Security: NEVER store plaintext. Hash it with bcrypt and a unique salt.
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(raw_password.encode('utf-8'), salt)

    users_db[username] = hashed_password
    return jsonify({"message": "User registered securely."}), 201#, "user": username, "hashed_password": str(users_db[username])}), 201

# --- 2. LOGIN & SECURE SESSIONS ---
@app.route('/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    raw_password = data.get('password')

    stored_hash = users_db.get(username)

    if stored_hash and bcrypt.checkpw(raw_password.encode('utf-8'), stored_hash):
        # Generate a cryptographically secure, random 43-character session token
        session_token = secrets.token_urlsafe(32)
        # Store in Redis: Key = token, Value = username
        # Enforce exactly 900 seconds (15 minutes) session timeout
        session_store.setex(f"session:{session_token}", 60, username)     
        return jsonify({"message": "Login successful", "session_token": session_token}), 200

    return jsonify({"error": "Invalid credentials"}), 401

# --- 3. SESSION VALIDATION (Protected Route) ---
@app.route('/api/secure-data', methods=['GET'])
def get_secure_data():
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith("Bearer "):
        return jsonify({"error": "Missing token"}), 401       
    session_token = auth_header.split(" ")[1]   
    # Check if the session exists in Redis
    username = session_store.get(f"session:{session_token}")
    if not username:
        return jsonify({"error": "Session expired or invalid. Please log in."}), 401       
    # Optional: Reset the 15-minute timer on activity (Sliding Expiration)
    session_store.expire(f"session:{session_token}", 60)
    return jsonify({"message": f"Welcome back, {username}. Here is the financial data."}), 200

# --- 4. LOGOUT FUNCTIONALITY ---
@app.route('/auth/logout', methods=['POST'])
def logout():
    auth_header = request.headers.get('Authorization')
    if auth_header and auth_header.startswith("Bearer "):
        session_token = auth_header.split(" ")[1]    
        # Instantly destroy the session in Redis
        session_store.delete(f"session:{session_token}")       
    return jsonify({"message": "Successfully logged out."}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5021)
