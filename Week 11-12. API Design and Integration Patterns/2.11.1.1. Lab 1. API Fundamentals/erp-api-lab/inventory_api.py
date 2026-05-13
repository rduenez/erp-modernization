from flask import Flask, request, jsonify

app = Flask(__name__)

# Mock Database
inventory = {
    "WIDGET-01": {"name": "Industrial Widget", "stock": 50}
}

@app.route('/api/internal/inventory/deduct', methods=['POST'])
def deduct_inventory():
    data = request.get_json()
    sku = data.get('sku')
    quantity = data.get('quantity')
    
    if sku not in inventory:
        return jsonify({"error": "Product not found"}), 404
        
    if inventory[sku]['stock'] < quantity:
        return jsonify({"error": "Insufficient stock"}), 400
        
    # Deduct the stock
    inventory[sku]['stock'] -= quantity


    return jsonify({
        "message": "Stock updated successfully",
        "remaining_stock": inventory[sku]['stock']
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)

