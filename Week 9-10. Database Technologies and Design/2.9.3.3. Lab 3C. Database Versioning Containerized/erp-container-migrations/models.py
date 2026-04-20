from sqlalchemy import Column, Integer, String, TIMESTAMP, text, Numeric, Text, CheckConstraint
from sqlalchemy.orm import declarative_base, Mapped, mapped_column
from typing import Optional
from datetime import datetime
from decimal import Decimal

Base = declarative_base()

class Order(Base):
    __tablename__ = "orders"
    __table_args__ = (
        CheckConstraint(
            "status IN ('Draft', 'Confirmed', 'Shipped', 'Invoiced', 'Cancelled')",
            name="orders_status_check"
        ),
        {"schema": "public"}
    )

    # order_id serial4 NOT NULL -> Primary Key with auto-increment
    order_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # order_number varchar(50) NOT NULL UNIQUE
    order_number: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    
    # customer_id int4 NOT NULL FOREIGN KEY
    # customer_id: Mapped[int] = mapped_column(
    #     Integer, ForeignKey("customers.customer_id"), nullable=False
    # )
    
    # order_date timestamp DEFAULT CURRENT_TIMESTAMP
    order_date: Mapped[Optional[datetime]] = mapped_column(
        TIMESTAMP, server_default=text("CURRENT_TIMESTAMP")
    )
    
    required_date: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP)
    
    # status varchar(20) DEFAULT 'Draft'
    status: Mapped[Optional[str]] = mapped_column(
        String(20), server_default="Draft"
    )
    
    # numeric(12, 2) mappings
    sub_total: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(12, 2), server_default="0.00"
    )
    tax_amount: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(12, 2), server_default="0.00"
    )
    total_amount: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(12, 2), server_default="0.00"
    )
    
    ship_to_address: Mapped[Optional[str]] = mapped_column(Text)
    
    created_date: Mapped[Optional[datetime]] = mapped_column(
        TIMESTAMP, server_default=text("CURRENT_TIMESTAMP")
    )
    
    created_by: Mapped[Optional[str]] = mapped_column(String(50))
    
    # The new feature requested by Marketing
    discount_code: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)

