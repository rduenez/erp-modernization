from flask import Flask, request, jsonify
from functools import wraps

app = Flask(__name__)

# --- 1. MOCK DATABASE & IDENTITIES ---
# Identity Store: Users mapped to Roles (RBAC) and Attributes (ABAC)
users_db = {
    "alice":   {"role": "PurchasingAgent", "location": "HQ"},
    "bob":     {"role": "WarehouseManager", "location": "Irapuato"},
    "charlie": {"role": "WarehouseManager", "location": "Leon"},
    "diana":   {"role": "FinanceController", "location": "HQ"}
}

# Order Database
orders_db = {}
order_counter = 1

# --- 2. RBAC DECORATOR ---
def require_role(required_role):
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):

            user_id = request.headers.get('X-User-Id')
            user = users_db.get(user_id)

            if not user:
                return jsonify({"error": "Unauthorized. User not found."}), 401
                
            # RBAC Check: Does the user's role match the requirement?
            if user['role'] != required_role:
                return jsonify({"error": f"Forbidden. Requires role: {required_role}"}), 403
                
            return f(user_id, user, *args, **kwargs)
        
        return wrapped
    return decorator

# --- 3. THE ENDPOINTS (Enforcing Business Rules) ---

@app.route('/api/orders', methods=['POST'])
@require_role('PurchasingAgent') # LEAST PRIVILEGE: Only agents can create
def create_order(user_id, user):
    global order_counter
    data = request.get_json()
    target_location = data.get('location') # e.g., 'Irapuato'
    
    order_id = f"ORD-{order_counter}"
    orders_db[order_id] = {
        "item": data.get("item"),
        "location": target_location,
        "status": "PENDING",
        "created_by": user_id, # Track for Separation of Duties
        "received_by": None
    }
    order_counter += 1
    return jsonify({"message": f"Order {order_id} created for {target_location} warehouse."}), 201


@app.route('/api/orders/<order_id>/receive', methods=['POST'])
@require_role('WarehouseManager') # RBAC Check
def receive_order(user_id, user, order_id):

    order = orders_db.get(order_id)

    if not order:
        return jsonify({"error": "Order not found"}), 404
        
    # ABAC Check: Granular location control
    # Bob (Irapuato) CANNOT receive an order destined for Charlie (Leon)
    if order['location'] != user['location']:
        return jsonify({"error": f"ABAC Violation: You can only receive orders for {user['location']}."}), 403
        
    order['status'] = "RECEIVED"
    order['received_by'] = user_id
    
    return jsonify({"message": f"Order {order_id} marked as received securely."}), 200


@app.route('/api/orders/<order_id>/pay', methods=['POST'])
@require_role('FinanceController') # RBAC Check
def pay_order(user_id, user, order_id):

    order = orders_db.get(order_id)

    if not order:
        return jsonify({"error": "Order not found"}), 404
            
    if order['status'] != "RECEIVED":
        return jsonify({"error": "Cannot pay. Order has not been received yet."}), 400
        
    # SEPARATION OF DUTIES Check: The person paying CANNOT be the person who created it.
    # (Even if Diana somehow got Purchasing Agent rights, this blocks her from paying her own invoices)
    if order['created_by'] == user_id:
        return jsonify({"error": "Separation of Duties Violation: You cannot pay for an order you created."}), 403
        
    order['status'] = "PAID"
    
    return jsonify({"message": f"Order {order_id} has been paid successfully."}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5025)



