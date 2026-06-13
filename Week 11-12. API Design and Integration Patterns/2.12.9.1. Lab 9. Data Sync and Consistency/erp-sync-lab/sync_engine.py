import time

# Simulated State of Both Systems at 11:59 PM
# Notice the data has diverged throughout the day!
erp_database = {
    "SRV-IND-01": {
        "price": 1050.00,       # Updated in ERP recently
        "description": "Base Server", 
        "updated_at": 1714500000 # Older timestamp
    }
}

ecommerce_database = {
    "ECOMM-998877": {
        "price": 999.00,        # Someone put it on sale in Shopify!
        "description": "High-Performance Industrial Server (2026 Model)", # Updated in Shopify recently
        "updated_at": 1714505000 # Newer timestamp
    }
}

data_map = {"ECOMM-998877": "SRV-IND-01"}
def run_synchronization():

    print("=== STARTING MASTER DATA SYNCHRONIZATION ===\n") 

    for ecomm_id, erp_sku in data_map.items():

        erp_record = erp_database[erp_sku]
        ecomm_record = ecommerce_database[ecomm_id]
        print(f"Syncing {erp_sku} <--> {ecomm_id}") 

        # --- RULE 1: MASTER DATA SOURCE (Authoritative System) ---
        # Business Rule: The ERP is the absolute source of truth for Financials (Prices).
        # We don't care if the Shopify price is newer; the ERP always overwrites it.

        if ecomm_record["price"] != erp_record["price"]:
            print(f" -> Master Data Override: ERP Price (${erp_record['price']}) overwrites E-commerce Price (${ecomm_record['price']})")
            ecomm_record["price"] = erp_record["price"]

        # --- RULE 2: CONFLICT RESOLUTION (Last Write Wins) ---
        # Business Rule: For Marketing data (Descriptions), both systems can edit. 
        # We resolve conflicts by looking at the timestamp (Last Write Wins).

        if ecomm_record["description"] != erp_record["description"]:
            if ecomm_record["updated_at"] > erp_record["updated_at"]:
                print(f" -> Conflict Resolved (LWW): E-commerce Description is newer. Updating ERP.")
                erp_record["description"] = ecomm_record["description"]
            else:
                print(f" -> Conflict Resolved (LWW): ERP Description is newer. Updating E-commerce.")
                ecomm_record["description"] = erp_record["description"]
   
        print("\n--- SYNC COMPLETE. FINAL STATE: ---")
        print(f"ERP Record:   Price=${erp_record['price']}, Desc: {erp_record['description']}")
        print(f"Ecomm Record: Price=${ecomm_record['price']}, Desc: {ecomm_record['description']}\n")

if __name__ == '__main__':
    run_synchronization()
