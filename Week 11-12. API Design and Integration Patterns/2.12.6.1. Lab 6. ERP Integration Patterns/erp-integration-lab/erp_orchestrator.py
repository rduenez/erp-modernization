import requests
import base64

# External Service Endpoints (Routing to our Podman container)
EXTERNAL_HOST = "http://external-services:5010"

def fulfill_order(order_data):
    print(f"=== STARTING ORDER FULFILLMENT: {order_data['order_id']} ===\n")
    
    # ---------------------------------------------------------
    # 1. E-COMMERCE INTEGRATION: Sync Inventory
    # ---------------------------------------------------------
    print("STEP 1: Syncing E-commerce Inventory...")
    inventory_payload = {
        "sku": order_data['sku'],
        "new_stock": 49  # Assume we had 50 and sold 1
    }
    res_ecommerce = requests.post(f"{EXTERNAL_HOST}/ecommerce/inventory/sync", json=inventory_payload)
    if res_ecommerce.status_code == 200:
        print(" -> Success: Shopify stock updated.\n")


    # ---------------------------------------------------------
    # 2. SAT INVOICING INTEGRATION (CFDI 4.0)
    # ---------------------------------------------------------
    print("STEP 2: Generating XML and requesting SAT Timbrado...")
    
    # Generate a simplified XML representation for CFDI 4.0
    # In reality, this requires strict XML namespaces, XSLT chain schemas, and your CSD private key signature
    cfdi_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
    <cfdi:Comprobante Version="4.0" Total="{order_data['total']}" Moneda="MXN" TipoDeComprobante="I" Exportacion="01" MetodoPago="PUE" FormaPago="04">
        <cfdi:Emisor Rfc="EKU9003173C9" Nombre="Mi ERP SA de CV" RegimenFiscal="601"/>
        <cfdi:Receptor Rfc="{order_data['rfc']}" Nombre="{order_data['cliente']}" DomicilioFiscalReceptor="{order_data['cp']}" RegimenFiscalReceptor="601" UsoCFDI="G03"/>
        <cfdi:Conceptos>
            <cfdi:Concepto ClaveProdServ="43211503" Cantidad="1" ValorUnitario="{order_data['subtotal']}" Importe="{order_data['subtotal']}" Descripcion="Industrial Server"/>
        </cfdi:Conceptos>
    </cfdi:Comprobante>"""
    
    # PACs usually require the XML to be sent as base64 string or multipart file
    xml_base64 = base64.b64encode(cfdi_xml.encode('utf-8')).decode('utf-8')
    
    pac_payload = {"xml_base64": xml_base64}
    res_pac = requests.post(f"{EXTERNAL_HOST}/sat/pac/timbrar", json=pac_payload)
    
    
    if res_pac.status_code == 200:
        pac_data = res_pac.json()
        print(f" -> Success: CFDI Stamped! Folio Fiscal (UUID): {pac_data['uuid']}\n")

    # ---------------------------------------------------------
    # 3. SHIPPING INTEGRATION
    # ---------------------------------------------------------
    print("STEP 3: Generating Shipping Label...")
    shipping_payload = {
        "postal_code": order_data['cp'],
        "weight_kg": 15.5,
        "dimensions": "40x40x20"
    }
    res_shipping = requests.post(f"{EXTERNAL_HOST}/shipping/label", json=shipping_payload)
    
    if res_shipping.status_code == 200:
        ship_data = res_shipping.json()
        print(f" -> Success: Carrier selected: {ship_data['carrier']}")
        print(f" -> Tracking Number: {ship_data['tracking_number']}")
        print(f" -> Print Label: {ship_data['label_url']}\n")

    print("=== ORDER FULFILLMENT COMPLETE ===")


if __name__ == '__main__':
    # Simulating data arriving from an order entry screen
    order = {
        "order_id": "ORD-2026-9988",
        "sku": "SRV-IND-01",
        "cliente": "Empresa Manufacturera del Norte SA de CV",
        "rfc": "EMN900101XYZ",
        "cp": "64000", # Monterrey CP
        "subtotal": 10000.00,
        "total": 11600.00 # 16% IVA
    }
    
    fulfill_order(order)

