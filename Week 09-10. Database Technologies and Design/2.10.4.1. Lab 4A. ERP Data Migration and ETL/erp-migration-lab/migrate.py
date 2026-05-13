import pandas as pd
from sqlalchemy import create_engine
import logging
import sys

# Set up logging for error handling
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def run_migration():
    logging.info("Starting Data Migration Process...")

    # 1. EXTRACTION
    try:
        df = pd.read_csv('legacy_customers.csv')
        logging.info(f"Extracted {len(df)} records from legacy system.")
    except Exception as e:
        logging.error(f"Failed to read CSV: {e}")
        sys.exit(1)

    # 2. TRANSFORMATION
    # Rule A: Inactive Data Cleanup
    df = df[df['account_status'] != 'Inactive']
    
    # Rule B: Validation (Drop records missing critical fields like address)
    original_count = len(df)
    df = df.dropna(subset=['raw_address'])
    if len(df) < original_count:
        logging.warning(f"Dropped {original_count - len(df)} orphaned/incomplete records missing addresses.")

    # Rule C: Duplicate merging (Keep the first occurrence based on company_name)
    df = df.drop_duplicates(subset=['company_name'], keep='first')

    # Rule D: Currency Conversions (Standardizing to MXN. Assuming 1 USD = 20 MXN for this lab)
    def convert_to_mxn(row):
        if row['currency'] == 'USD':
            return row['credit_limit'] * 20
        return row['credit_limit']
    
    df['credit_limit_mxn'] = df.apply(convert_to_mxn, axis=1)

    # Rule E: Address format standardization (Split by semicolon, uppercase the state/city)
    df[['street', 'region']] = df['raw_address'].str.split(';', expand=True)
    df['region'] = df['region'].str.strip().str.upper()

    # Select and rename columns to map to the new database schema
    final_df = df[['company_name', 'street', 'region', 'credit_limit_mxn']]
    final_df.columns = ['name', 'street_address', 'region', 'credit_limit']

    logging.info(f"Transformation complete. {len(final_df)} records ready for loading.")

    # 3. LOADING (with Roll-back capability via SQL transactions)
    engine = create_engine('postgresql://postgres:supersecret@target-erp-db:5432/postgres')
    
    try:
        # if_exists='append' ensures we add to the table. 
        #We use a transaction so it all succeeds or all fails.
        with engine.begin() as connection:
            final_df.to_sql('new_customers', con=connection, index=False, if_exists='replace')
        logging.info("Migration Successful! Data loaded into Target ERP.")
    except Exception as e:
        # If anything fails during the write, SQLAlchemy automatically rolls back the transaction
        logging.error(f"Database load failed. Transaction rolled back. Error: {e}")

if __name__ == "__main__":
    run_migration()
