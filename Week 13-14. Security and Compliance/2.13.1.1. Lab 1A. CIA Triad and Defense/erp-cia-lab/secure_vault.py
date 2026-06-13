from flask import Flask, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# In-memory mock database
payroll_db = {}


# --- AVAILABILITY: Global Error Handler ---
# If a bug occurs, we catch it here instead of letting the server crash and go offline.
@app.errorhandler(Exception)
def handle_exception(e):
    logging.error(f"Server Error: {str(e)}")
    return jsonify({"error": "An internal error occurred. Service remains available."}), 500

@app.route('/api/v1/payroll', methods=['POST'])
def add_payroll():
    data = request.get_json()

    # --- INTEGRITY: Input Validation ---
    # We ensure the data is accurate, complete, and hasn't been maliciously formed.
    if not data or 'employee_id' not in data or 'salary' not in data or 'ssn' not in data:
        return jsonify({"error": "Data Integrity Failure: Missing required fields"}), 400
        
    try:
        salary = float(data['salary'])
        if salary < 0 or salary > 1000000:
            return jsonify({"error": "Data Integrity Failure: Invalid salary range"}), 400
    except ValueError:
        return jsonify({"error": "Data Integrity Failure: Salary must be a number"}), 400

    # --- CONFIDENTIALITY: Data Masking and Hashing ---
    # We NEVER store sensitive data like Social Security Numbers in plain text.
    # We use a one-way cryptographic hash. If the database is stolen, the SSN remains hidden.
    secure_ssn_hash = generate_password_hash(data['ssn'])
    
    # Store the sanitized and secured data
    emp_id = data['employee_id']
    payroll_db[emp_id] = {
        "salary": salary,
        "ssn_hash": secure_ssn_hash
    }

    logging.info(f"Successfully stored secure record for employee {emp_id}")
    return jsonify({"message": "Record stored securely."}), 201

@app.route('/api/v1/payroll/<employee_id>', methods=['GET'])
def get_payroll(employee_id):
    record = payroll_db.get(employee_id)
    if not record:
        return jsonify({"error": "Not found"}), 404

    # --- CONFIDENTIALITY: Need-to-Know Basis ---
    # When returning the data, we DO NOT return the SSN hash. The user doesn't need it to view the salary.
    return jsonify({
        "employee_id": employee_id,
        "salary": record['salary']
    }), 200

if __name__ == '__main__':
    # Running the API on port 5020
    app.run(host='0.0.0.0', port=5020)

