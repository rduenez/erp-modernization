podman exec -it erp-mongo mongosh

// Insert a Laptop
db.products.insertOne({
    sku: "TECH-101",
    category: "Electronics",
    name: "Developer Laptop",
    specs: { ram: "32GB", storage: "1TB SSD", cpu: "Core i9" },
    warranty_months: 36
});


// Insert a T-Shirt
db.products.insertOne({
    sku: "APP-505",
    category: "Apparel",
    name: "Company Logo Tee",
    variants: ["Small", "Medium", "Large"],
    material: "100% Cotton"
});


db.products.find().pretty()
