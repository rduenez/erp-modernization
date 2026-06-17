# 1. Define the Cloud Provider
provider "aws" {
  region = "us-east-1"
}

# Generate a random string to ensure a globally unique bucket name
resource "random_string" "suffix" {
  length  = 6
  special = false
  upper   = false
}

# 2. Define the Infrastructure (The Bucket)
resource "aws_s3_bucket" "promo_site" {
  bucket = "devops-promo-site-${random_string.suffix.result}"
}

# 3. Configure the Bucket for Static Web Hosting
resource "aws_s3_bucket_website_configuration" "promo_site_config" {
  bucket = aws_s3_bucket.promo_site.id

  index_document {
    suffix = "index.html"
  }
}

# 4. Upload the Developer's Code automatically
resource "aws_s3_object" "index_upload" {
  bucket       = aws_s3_bucket.promo_site.id
  key          = "index.html"
  source       = "index.html"
  content_type = "text/html"
}

# 5. Output the final URL (Feedback Loop)
output "website_endpoint" {
  value       = aws_s3_bucket_website_configuration.promo_site_config.website_endpoint
  description = "The public URL of the deployed application."
}

