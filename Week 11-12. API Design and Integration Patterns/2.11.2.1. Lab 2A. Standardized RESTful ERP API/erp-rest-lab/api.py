from flask import Flask, request, jsonify

app = Flask(__name__)

# Mock Database
products_db = [
    {"id": 1, "name": "Laptop", "price": 1200},
    {"id": 2, "name": "Mouse", "price": 25},
    {"id": 3, "name": "Keyboard", "price": 75},
    {"id": 4, "name": "Monitor", "price": 300},
    {"id": 5, "name": "Desk", "price": 450}
]

# --- VERSION 1 API ---

# 1. READ ALL (With Pagination & Filtering)
@app.route('/api/v1/products', methods=['GET'])
def get_products():
    # Stateless interaction: Every request must provide its own pagination context
    page = int(request.args.get('page', 1))
    page_size = int(request.args.get('pageSize', 2))
    
    start = (page - 1) * page_size
    end = start + page_size
    
    paginated_data = products_db[start:end]
    
    # 200 OK is default, returning JSON and metadata
    return jsonify({
        "data": paginated_data,
        "page": page,
        "pageSize": page_size,
        "totalRecords": len(products_db)
    }), 200

# 2. READ ONE (Path Parameter)
@app.route('/api/v1/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    product = next((p for p in products_db if p["id"] == product_id), None)
    
    if product:
        return jsonify(product), 200 # 200 OK
    else:
        return jsonify({"error": "Product not found"}), 404 # 404 Not Found


# 3. CREATE (Validating input)
@app.route('/api/v1/products', methods=['POST'])
def create_product():
    data = request.get_json()
    
    # Validation
    if not data or not 'name' in data or not 'price' in data:
        return jsonify({"error": "Bad Request: Missing name or price"}), 400 # 400 Bad Request
        
    new_product = {
        "id": len(products_db) + 1,
        "name": data['name'],
        "price": data['price']
    }
    products_db.append(new_product)
    
    return jsonify(new_product), 201 # 201 Created


# 4. UPDATE (Full Replacement)
@app.route('/api/v1/products/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    product = next((p for p in products_db if p["id"] == product_id), None)
    
    if not product:
        return jsonify({"error": "Product not found"}), 404
        
    data = request.get_json()
    product['name'] = data.get('name', product['name'])
    product['price'] = data.get('price', product['price'])
    
    return jsonify(product), 200


# 5. DELETE
@app.route('/api/v1/products/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    global products_db
    initial_length = len(products_db)
    products_db = [p for p in products_db if p["id"] != product_id]
    
    if len(products_db) < initial_length:
        # Some REST APIs return 204 No Content on delete, or a 200 with a message
        return jsonify({"message": "Product deleted"}), 200 
    else:
        return jsonify({"error": "Product not found"}), 404

# --- VERSION 2 API (Breaking Change Example) ---
# Scenario: In V2, we change "price" to "price_usd" and require a "category" field.
@app.route('/api/v2/products', methods=['POST'])
def create_product_v2():
    data = request.get_json()
    if not data or not 'name' in data or not 'price_usd' in data or not 'category' in data:
        return jsonify({"error": "Bad Request: Missing name, price_usd, or category"}), 400
    
    return jsonify({"message": "V2 Product Created"}), 201

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)
