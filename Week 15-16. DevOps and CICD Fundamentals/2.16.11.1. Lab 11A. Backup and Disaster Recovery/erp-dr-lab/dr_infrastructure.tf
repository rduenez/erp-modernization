provider "aws" {
  region = "us-east-1"
}

# Generate a random string for a unique bucket name
resource "random_string" "suffix" {
  length  = 6
  special = false
  upper   = false
}

# ==========================================
# 1. USER-UPLOADED FILES (Object Storage)
# ==========================================
resource "aws_s3_bucket" "erp_uploads" {
  bucket = "erp-invoices-dr-${random_string.suffix.result}"
}

# Enable Versioning: Overwriting a file saves the old one as a hidden version
resource "aws_s3_bucket_versioning" "erp_uploads_versioning" {
  bucket = aws_s3_bucket.erp_uploads.id
  versioning_configuration {
    status = "Enabled"
  }
}

# Lifecycle Rules: 30 days Hot, 1 Year Cold
resource "aws_s3_bucket_lifecycle_configuration" "erp_uploads_lifecycle" {
  bucket = aws_s3_bucket.erp_uploads.id

  rule {
    id     = "archive-and-delete"
    status = "Enabled"

    # Move to cheap Cold Storage (Glacier) after 30 days
    transition {
      days          = 30
      storage_class = "GLACIER"
    }

    # Permanently delete after 1 year to comply with data minimization laws
    expiration {
      days = 365
    }
  }
}

# ==========================================
# 2. DATABASE BACKUPS (RDS)
# ==========================================
resource "aws_db_instance" "erp_database" {
  identifier           = "erp-prod-db"
  engine               = "postgres"
  engine_version       = "18.3"
  instance_class       = "db.t3.micro"
  allocated_storage    = 20
  username             = "dbadmin"
  password             = "SuperSecretDRPassword!" # Should be in Secrets Manager
  
  # DISASTER RECOVERY CONFIGURATION:
  # AWS automatically takes daily full backups and retains them for 30 days.
  # Furthermore, AWS saves the Transaction Logs every 5 minutes.
  backup_retention_period = 30 
  backup_window           = "03:00-04:00" # Run daily full backup at 3 AM
  
  skip_final_snapshot     = true # Set to true only for lab cleanup
}

output "bucket_name" {
  value = aws_s3_bucket.erp_uploads.bucket
}

