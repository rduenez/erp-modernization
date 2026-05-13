from sqlalchemy import Column, Integer, String, DECIMAL
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Order(Base):
    __tablename__ = 'orders'

    order_id = Column(Integer, primary_key=True)
    order_number = Column(String(50), unique=True, nullable=False)
    total_amount = Column(DECIMAL(12, 2), default=0.00)
    
    # NEW FEATURE: The marketing team requested this column
    discount_code = Column(String(20), nullable=True)
