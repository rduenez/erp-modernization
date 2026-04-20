from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

# Base classes for our two different database schemas
LegacyBase = declarative_base()
NewBase = declarative_base()

# ==========================================
# 1. ORM MAPPING: LEGACY SYSTEM
# ==========================================
class LegacyUser(LegacyBase):
    __tablename__ = 'legacy_users'
    id = Column(Integer, primary_key=True)
    full_name = Column(String)
    raw_address = Column(String)
    is_active = Column(Integer)  # 1 for active, 0 for inactive


# ==========================================
# 2. ORM MAPPING: NEW ERP SYSTEM (Normalized)
# ==========================================
class Customer(NewBase):
    __tablename__ = 'customers'
    id = Column(Integer, primary_key=True)
    first_name = Column(String)
    last_name = Column(String)
    status = Column(String)
    
    # Establish the One-to-Many relationship in Python
    addresses = relationship("Address", back_populates="customer")

class Address(NewBase):
    __tablename__ = 'addresses'
    id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey('customers.id'))
    street = Column(String)
    city = Column(String)
    
    # Link back to the parent Customer object
    customer = relationship("Customer", back_populates="addresses")

# ==========================================
# 3. MIGRATION LOGIC
# ==========================================
def run_migration():
    # Connect to both databases using the container names
    legacy_engine = create_engine('postgresql://postgres:supersecret@legacy-db:5432/postgres')
    new_engine = create_engine('postgresql://postgres:supersecret@new-erp-db:5432/postgres')

    # Create the tables in the new database based on our Python classes
    NewBase.metadata.create_all(new_engine)

    # Open sessions (connections) to both databases
    LegacySession = sessionmaker(bind=legacy_engine)
    NewSession = sessionmaker(bind=new_engine)
    
    source_session = LegacySession()
    target_session = NewSession()

    logging.info("Extracting data from Legacy DB...")
    # EXTRACTION: Query the database to get a list of Python 'LegacyUser' objects
    legacy_records = source_session.query(LegacyUser).all()
    
    migrated_count = 0

    logging.info("Transforming and Loading into Target DB...")
    for old_user in legacy_records:
        # Rule 1: Skip inactive users (Data Cleanup)
        if old_user.is_active == 0:
            logging.info(f"Skipping inactive user: {old_user.full_name}")
            continue
        
        # Rule 2: Split full_name into first and last
        name_parts = old_user.full_name.split(' ', 1)
        first = name_parts[0]
        last = name_parts[1] if len(name_parts) > 1 else ""

        # Rule 3: Map 1/0 to 'Active'/'Inactive'
        status_string = 'Active' if old_user.is_active == 1 else 'Inactive'

        # Rule 4: Split raw_address into street and city
        address_parts = old_user.raw_address.split(';')
        street = address_parts[0].strip()
        city = address_parts[1].strip() if len(address_parts) > 1 else "Unknown"

        # TRANSFORMATION -> LOADING: Instantiate the New Objects
        # Notice how we link them together purely in Python using the 'addresses' list!
        new_customer = Customer(
            first_name=first, 
            last_name=last, 
            status=status_string
        )
        
        new_address = Address(
            street=street, 
            city=city, 
            customer=new_customer # ORM automatically handles the Foreign Key injection!
        )
        
        # Add the object to the target session (it automatically adds the linked Address too)
        target_session.add(new_customer)
        migrated_count += 1
        
    # Commit the transaction to save all new objects to the New ERP DB
    try:
        target_session.commit()
    except Exception as e:
        target_session.rollback()
        logging.error(f"Migration failed: {e}")
        logging.info(f"Migration complete! Successfully migrated {migrated_count} active records.")
    finally:
        source_session.close()
        target_session.close()

if __name__ == "__main__":
    run_migration()




