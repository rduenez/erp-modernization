# ==========================================
# 1. MULTI-REGION PROVIDERS
# ==========================================
provider "aws" {
  alias  = "primary"
  region = "us-east-1" # Virginia
}

provider "aws" {
  alias  = "dr_region"
  region = "us-west-2" # Oregon
}

# ==========================================
# 2. ENCRYPTED SECRETS (Geographic Redundancy)
# ==========================================
resource "aws_secretsmanager_secret" "erp_config" {
  provider    = aws.primary
  name        = "erp/production/config"
  description = "Encrypted application configuration"

  # Automatically replicate this encrypted secret to the DR region!
  replica {
    region = "us-west-2"
  }
}

# ==========================================
# 3. DATABASE BACKUP STRATEGY
# ==========================================
resource "aws_db_instance" "primary_db" {
  provider             = aws.primary
  identifier           = "erp-primary-db"
  engine               = "postgres"
  engine_version       = "18.3"
  instance_class       = "db.t3.micro"
  allocated_storage    = 20
  username             = "admin"
  password             = "DummyPass123!" 
  
  # RPO STRATEGY: 
  # Daily full backups + Transaction logs every 5 minutes.
  # Retained for 30 days hot storage.
  backup_retention_period = 30
  backup_window           = "03:00-04:00"
  skip_final_snapshot     = true
}

# GEOGRAPHIC REDUNDANCY: Replicate Backups to Oregon
# This ensures that if Virginia is physically destroyed, the backups safely exist on the West Coast.
resource "aws_db_instance_automated_backups_replication" "dr_db_replica" {
  provider               = aws.dr_region
  source_db_instance_arn = aws_db_instance.primary_db.arn
  retention_period       = 30
}
