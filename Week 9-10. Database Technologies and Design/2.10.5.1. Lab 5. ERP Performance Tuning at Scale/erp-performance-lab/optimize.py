from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import declarative_base, relationship, sessionmaker, joinedload
import redis
import json
import time

Base = declarative_base()

class Category(Base):
    __tablename__ = 'categories'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    products = relationship("Product", back_populates="category")

class Product(Base):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True)
    category_id = Column(Integer, ForeignKey('categories.id'))
    name = Column(String)
    price = Column(Integer)
    category = relationship("Category", back_populates="products")

# Connect to Postgres and Redis on the Podman network
engine = create_engine('postgresql://postgres:supersecret@perf-db:5432/postgres')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
db = Session()

cache = redis.Redis(host='perf-redis', port=6379, decode_responses=True)

# --- SEED DATA ---
if not db.query(Category).first():
    c = Category(name="Electronics")
    db.add_all([
        Product(name="Laptop", price=1200, category=c),
        Product(name="Phone", price=800, category=c)
    ])
    db.commit()

# --- 1. THE N+1 PROBLEM vs EAGER LOADING ---
print("--- Testing N+1 vs Eager Loading ---")

# BAD: N+1 Queries (Triggers 1 query for categories, plus 1 query per category to get products)
categories_bad = db.query(Category).all()
for c in categories_bad:
    # Accessing c.products triggers a hidden database hit!
    print(f"Bad Query -> {c.name} has {len(c.products)} products")

# GOOD: Eager Loading (Triggers exactly 1 SQL query using a JOIN)
categories_good = db.query(Category).options(joinedload(Category.products)).all()
for c in categories_good:
    # Products are already in memory!
    print(f"Good Query -> {c.name} has {len(c.products)} products")

# --- 2. THE REDIS CACHING LAYER ---
print("\n--- Testing Redis Cache ---")

def get_product_price(product_id):
    cache_key = f"product:{product_id}:price"
    
    # Check Cache First
    start = time.time()
    cached_price = cache.get(cache_key)
    
    if cached_price:
        print(f"CACHE HIT: Loaded price ${cached_price} in {(time.time()-start)*1000:.4f} ms")
        return cached_price
        
    # Cache Miss: Hit the slow Database
    print("CACHE MISS: Querying PostgreSQL...")
    product = db.query(Product).filter(Product.id == product_id).first()
    
    if product:
        # Save to cache for 60 seconds
        cache.setex(cache_key, 60, product.price)
        print(f"DB HIT: Loaded price ${product.price} in {(time.time()-start)*1000:.4f} ms")
        return product.price

# First call hits DB, Second call hits Cache
get_product_price(1)
get_product_price(1)



