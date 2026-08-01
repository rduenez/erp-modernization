import boto3
import os
from flask import Flask, request, jsonify

app = Flask(__name__)
# Pass the bucket name via environment variable
BUCKET_NAME = os.environ.get("S3_BUCKET_NAME")
s3_client = boto3.client('s3')


@app.route('/api/upload-invoice', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files['file']
    filename = file.filename
    
    # Stream the file directly into AWS S3 (Never save to local container disk!)
    s3_client.upload_fileobj(file, BUCKET_NAME, filename)
    
    return jsonify({"message": f"{filename} securely stored in S3."}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
