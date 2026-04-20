from flask import Flask, jsonify

app = Flask(__name__)

# Simulated ERP Inventory Database
inventory = {
    "item_101": {"name": "Industrial Widget", "stock": 450},
    "item_102": {"name": "Copper Wiring (m)", "stock": 1200}
}

@app.route('/api/inventory')
def get_inventory():
    return jsonify(inventory)

if __name__ == '__main__':
    # Running on port 8080
    app.run(host='0.0.0.0', port=8080)