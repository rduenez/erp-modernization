from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/api/public/status', methods=['GET'])
def status():
    return jsonify({"status": "ERP is online and operational."}), 200

@app.route('/api/admin/dashboard', methods=['GET'])
def admin():
    return jsonify({"data": "Top Secret Financials"}), 200

if __name__ == '__main__':
    # Listen on port 5060 internally
    app.run(host='0.0.0.0', port=5060)
