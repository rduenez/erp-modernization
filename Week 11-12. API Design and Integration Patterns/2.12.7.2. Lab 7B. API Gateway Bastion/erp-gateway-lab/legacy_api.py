from flask import Flask, jsonify

app = Flask(__name__)

# A completely unprotected route!
@app.route('/api/v1/inventory', methods=['GET'])
def get_inventory():
    print("BACKEND HIT: Returning inventory data...")
    return jsonify({
        "status": "success",
        "data": [
            {"sku": "WIDGET-A", "stock": 500},
            {"sku": "SERVER-X", "stock": 12}
        ]
    }), 200

if __name__ == '__main__':
    # Running on port 5011
    app.run(host='0.0.0.0', port=5011)

