import strawberry
from flask import Flask
from strawberry.flask.views import GraphQLView
from typing import List, Optional

# 1. Define the strongly-typed schema (The Nouns)
@strawberry.type
class Order:
    order_number: str
    total: float
    date: str
    shipping_address: str  # We will NOT ask for this in our query!

@strawberry.type
class Customer:
    id: int
    name: str
    email: str
    credit_limit: float    # We will NOT ask for this in our query!
    orders: List[Order]


# Mock Database
db_orders = [
    Order(order_number="ORD-991", total=4500.00, date="2026-04-20", shipping_address="123 Reforma, CDMX"),
    Order(order_number="ORD-992", total=150.50, date="2026-04-28", shipping_address="123 Reforma, CDMX")
]

db_customers = [
    Customer(id=123, name="Tech Solutions Mexico", email="contacto@techmx.com", credit_limit=50000.00, orders=db_orders),
    Customer(id=456, name="Industrias del Bajío", email="ventas@industriasbajio.mx", credit_limit=100000.00, orders=[])
]

# 2. Define the Query (The Verbs/Entrypoints)
@strawberry.type
class Query:
    @strawberry.field
    def customer(self, id: int) -> Optional[Customer]:
        # In a real app, this would be an SQLAlchemy database query
        for c in db_customers:
            if c.id == id:
                return c
        return None


# 3. Create the Schema and attach it to Flask
schema = strawberry.Schema(query=Query)

app = Flask(__name__)

# GraphQL uses a SINGLE endpoint for everything, usually /graphql
app.add_url_rule(
    "/graphql",
    view_func=GraphQLView.as_view("graphql_view", schema=schema)
)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5004)

