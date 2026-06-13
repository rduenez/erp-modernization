from flask import Flask, request, jsonify
import pickle
import base64
import json
import os

app = Flask(__name__)

# Mock Database for IDOR testing
payslips_db = {
    "1001": {"owner": "alice", "salary": "$120,000", "bonus": "$15,000"},
    "1002": {"owner": "bob", "salary": "$45,000", "bonus": "$500"}
}

# ==========================================
#  VULNERABLE ENDPOINTS
# ==========================================
@app.route('/api/vulnerable/import-prefs', methods=['POST'])
def vulnerable_import():
    """VULNERABILITY 1: Insecure Deserialization"""
    try:
        data = request.get_json()
        b64_payload = data.get('payload')       
        # The app blindly decodes and unpickles (deserializes) user-provided data.
        # This allows arbitrary code execution during the object reconstruction phase!
        raw_bytes = base64.b64decode(b64_payload)
        user_prefs = pickle.loads(raw_bytes) 
        return jsonify({"message": "Preferences imported successfully", "prefs": str(user_prefs)}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/vulnerable/payslip/<doc_id>', methods=['GET'])
def vulnerable_payslip(doc_id):
    """VULNERABILITY 2: Insecure Direct Object Reference (IDOR) / Broken Access Control"""
    # We check who is logged in...
    logged_in_user = request.headers.get('X-User-Id')
    
    # ...but we NEVER verify if the logged-in user actually owns the requested doc_id!
    document = payslips_db.get(doc_id)
    
    if document:
        return jsonify({"payslip": document}), 200
    return jsonify({"error": "Not found"}), 404


# ==========================================
#  SECURE ENDPOINTS
# ==========================================
@app.route('/api/secure/import-prefs', methods=['POST'])
def secure_import():
    """FIX 1: Use Safe Data Formats (JSON) instead of Native Serialization"""
    try:
        data = request.get_json()
        # We strictly parse JSON. JSON cannot execute code; it is purely data.
        user_prefs = json.loads(data.get('payload'))
        
        return jsonify({"message": "Preferences imported securely", "prefs": user_prefs}), 200
    except Exception as e:
        return jsonify({"error": "Invalid format"}), 400


@app.route('/api/secure/payslip/<doc_id>', methods=['GET'])
def secure_payslip(doc_id):
    """FIX 2: Implement Strict Access Control Checks"""
    logged_in_user = request.headers.get('X-User-Id')
    document = payslips_db.get(doc_id)
    
    if not document:
        return jsonify({"error": "Not found"}), 404
        
    # AUTHORIZATION CHECK: Does the logged-in user own this specific resource?
    if document['owner'] != logged_in_user:
        return jsonify({"error": "Forbidden: You do not have permission to view this document."}), 403
        
    return jsonify({"payslip": document}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5050)
