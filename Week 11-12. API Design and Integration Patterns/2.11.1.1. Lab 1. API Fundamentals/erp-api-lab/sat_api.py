from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/api/v1/calculate-tax', methods=['POST'])
def calculate_tax():
    # The "Contract": We expect a JSON payload with a 'subtotal'
    data = request.get_json()
    
    if not data or 'subtotal' not in data:
        return jsonify({"error": "Bad Request. 'subtotal' is required"}), 400
        
    subtotal = float(data['subtotal'])
    iva = subtotal * 0.16  # 16% tax in Mexico
    total = subtotal + iva
        
    # We return the official tax calculation and a mock digital stamp
    return jsonify({
        "status": "success",
        "subtotal": subtotal,
        "iva_calculated": iva,
        "total_official": total,
        "sat_digital_stamp": "SAT-XYZ-987654321"
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

