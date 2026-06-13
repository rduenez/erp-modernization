import boto3
import json
import logging
from botocore.exceptions import ClientError
from sqlalchemy import create_engine, text

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(message)s')

def get_secret():
    secret_name = "erp/prod/db-credentials"
    # Specify the region where you created the secret (change if necessary)
    region_name = "us-east-1" 

    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    try:
        logging.info(f"Calling AWS Secrets Manager to fetch: {secret_name}")
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        # Handle exceptions if AWS denies access or the secret doesn't exist
        logging.error(f"Failed to retrieve secret: {e}")
        raise e

    # Decrypts secret using the associated KMS key and returns the JSON string
    secret = get_secret_value_response['SecretString']
    return json.loads(secret)

def connect_to_database():

    # 1. Fetch the credentials dynamically
    credentials = get_secret()
    
    username = credentials['username']
    password = credentials['password']
    host = credentials['host']
    port = credentials['port']
    dbname = credentials['dbname']

    logging.info("Secret successfully retrieved and parsed. Building connection string (hiding password).")

    # 2. Build the SQLAlchemy connection string
    db_url = f"postgresql://{username}:{password}@{host}:{port}/{dbname}"
    
    engine = create_engine(db_url)
    
    # 3. Test the connection
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT version();"))
            db_version = result.scalar()
            logging.info("SUCCESS! Securely connected to the database.")
            logging.info(f"Database Version: {db_version}")
    except Exception as e:
        logging.error(f"Database connection failed: {e}")

if __name__ == '__main__':
    connect_to_database()

