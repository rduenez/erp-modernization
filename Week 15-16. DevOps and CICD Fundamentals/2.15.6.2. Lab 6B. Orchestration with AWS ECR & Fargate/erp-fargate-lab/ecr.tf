provider "aws" {
  region = "us-east-1"
}

# Create a private Elastic Container Registry
resource "aws_ecr_repository" "erp_repo" {
  name                 = "erp-fargate-api"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true # Automatically scans your Python image for CVEs!
  }
}

output "repository_url" {
  value = aws_ecr_repository.erp_repo.repository_url
}
