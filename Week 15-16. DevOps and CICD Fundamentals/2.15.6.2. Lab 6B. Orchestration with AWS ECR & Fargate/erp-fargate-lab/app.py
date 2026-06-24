from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/api/fargate-status', methods=['GET'])
def status():
    return jsonify({
        "orchestrator": "AWS Fargate",
        "message": "Running serverless! No EC2 instances to manage here."
    }), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
