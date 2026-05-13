from flask import Flask, request, jsonify
from flasgger import Swagger
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import declarative_base, sessionmaker

app = Flask(__name__)
# Initialize the OpenAPI Swagger UI
swagger = Swagger(app)

# Database Setup
engine = create_engine('postgresql://postgres:supersecret@openapi-db:5432/postgres')
Base = declarative_base()
Session = sessionmaker(bind=engine)

class Product(Base):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    price = Column(Float, nullable=False)

# Create the table if it doesn't exist
Base.metadata.create_all(engine)

@app.route('/api/v1/products', methods=['GET'])
def get_products():
    """
    Retrieve a list of all products
    ---
    tags:
      - Products
    responses:
      200:
        description: A list of products returned successfully
    """
    db = Session()
    products = db.query(Product).all()
    result = [{"id": p.id, "name": p.name, "price": p.price} for p in products]
    db.close()
    
    return jsonify(result), 200

@app.route('/api/v1/products', methods=['POST'])
def create_product():
    """
    Create a new product in the ERP
    ---
    tags:
      - Products
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - name
            - price
          properties:
            name:
              type: string
              example: "Enterprise Server"
            price:
              type: number
              example: 4500.00
    responses:
      201:
        description: Product successfully created
      400:
        description: Bad Request (Missing parameters)
    """

    data = request.get_json()
    
    if not data or 'name' not in data or 'price' not in data:
        return jsonify({"error": "Bad Request: Missing name or price"}), 400
        
    db = Session()
    new_product = Product(name=data['name'], price=data['price'])
    db.add(new_product)
    db.commit()
    
    response = {"id": new_product.id, "name": new_product.name, "price": new_product.price}
    db.close()
    
    return jsonify(response), 201


if __name__ == '__main__':
    # Running on all interfaces so Podman can expose it
    app.run(host='0.0.0.0', port=5003)

