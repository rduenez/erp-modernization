import xmltodict
import json
import asyncio
import aiohttp

# Pointing to the Node-RED iPaaS container on our network
IPAAS_WEBHOOK_URL = "http://local-ipaas:1880/api/legacy-orders"

async def send_order_to_ipaas(session, order_id, json_payload):
    """Send a single order to iPaaS asynchronously."""
    try:
        async with session.post(IPAAS_WEBHOOK_URL, json=json_payload) as response:
            await response.json()
            print(f"[ESB] Order {order_id} sent successfully.")
    except Exception as e:
        print(f"Failed to reach iPaaS for Order {order_id}: {e}")

async def process_legacy_file():
    print("--- [ESB] Starting Protocol Translation ---")
    
    # 1. Read the legacy XML file
    with open('export.xml', 'r') as file:
        xml_data = file.read()
        
    # 2. Translate XML to a Python Dictionary
    parsed_data = xmltodict.parse(xml_data)
    orders = parsed_data['ERP_Export']['Order']
    
    # 3. Transform and Route to iPaaS
    async with aiohttp.ClientSession() as session:
        tasks = []
        for order in orders:
            # Construct a modern JSON payload
            json_payload = {
                "order_id": order['OrderID'],
                "customer_name": order['Customer'],
                "amount": float(order['TotalValue'])
            }
            
            print(f"[ESB] Translated Order {json_payload['order_id']}. Sending to iPaaS...")
            
            # Create async task for each order
            task = send_order_to_ipaas(session, json_payload['order_id'], json_payload)
            tasks.append(task)
        
        # Wait for all tasks to complete concurrently
        await asyncio.gather(*tasks)
    
    print(f"[ESB] All orders processed.")

if __name__ == '__main__':
    asyncio.run(process_legacy_file())
