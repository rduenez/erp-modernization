provider "aws" {
  region = "us-east-1"
}

# 1. Create the Secure Vault inside AWS
resource "aws_secretsmanager_secret" "erp_prod_secrets" {
  name        = "erp/production/config"
  description = "Production credentials and API keys for the ERP application"
}

# 2. Populate the Vault with the Production Values
resource "aws_secretsmanager_secret_version" "erp_prod_secrets_values" {
  secret_id     = aws_secretsmanager_secret.erp_prod_secrets.id
  secret_string = jsonencode({
    DB_CONNECTION   = "postgresql://admin:ProdSuperSecret99!@erp-prod-db.aws.internal:5432/erp_prod"
    PAYMENT_API_KEY = "sk_live_9876543210productionkey"
    SAT_API_KEY     = "sat_live_key_auth_001"
    ENABLE_NEW_UI   = "false" # Keep features disabled in prod until marketing is ready
  })
}

output "secret_arn" {
  value = aws_secretsmanager_secret.erp_prod_secrets.arn
}
