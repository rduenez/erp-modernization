from flask import Flask, request, jsonify
from ldap3 import Server, Connection, ALL

app = Flask(__name__)

# LDAP Server Configuration
LDAP_SERVER_URI = 'ldap://corp-ldap:389'
BASE_DN = 'ou=employees,dc=erp,dc=com'

@app.route('/auth/login', methods=['POST'])
def ldap_login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"error": "Username and password required"}), 400

    # In LDAP, you log in using a Distinguished Name (DN)
    # We construct the DN based on the username provided
    user_dn = f"uid={username},{BASE_DN}"
    
    print(f"[AUTH] Attempting LDAP bind for: {user_dn}")

    try:
        # Define the server
        server = Server(LDAP_SERVER_URI, get_info=ALL)
        
        # Attempt to bind (authenticate) to the server with the user's credentials
        # auto_bind=True immediately attempts the connection and throws an error if it fails
        conn = Connection(server, user=user_dn, password=password, auto_bind=True)
        
        # If we reach here, the bind was successful!
        print("[AUTH] LDAP Bind Successful.")

        # We can also query LDAP for the user's full name now that we are authenticated
        conn.search(user_dn, '(objectclass=person)', attributes=['cn', 'sn'])
        full_name = conn.entries[0].cn.value if conn.entries else username
        
        # Close the LDAP connection
        conn.unbind()
        
        # Return a success token to the user (in reality, you would issue a JWT here)
        return jsonify({
            "message": "Authentication successful via Corporate Directory",
            "employee_name": full_name,
            "token": "simulated_success_token_123"
        }), 200

    except Exception as e:
        print(f"[AUTH] Server Error: {e}")
        return jsonify({"error": "Could not connect to directory server"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5022)


