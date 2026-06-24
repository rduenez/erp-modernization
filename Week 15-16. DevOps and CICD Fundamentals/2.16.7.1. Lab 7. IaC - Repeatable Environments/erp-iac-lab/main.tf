provider "aws" {
  region = "us-east-1"
}

# 1. Network: Fetch the default VPC to keep the lab simple
data "aws_vpc" "default" { default = true }
data "aws_subnets" "default" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.default.id]
  }
}

# 2. Database: PostgreSQL RDS
resource "aws_db_instance" "erp_database" {
  identifier           = "erp-db-${var.environment}"
  engine               = "postgres"
  engine_version       = "15.4"
  instance_class       = var.db_instance_class
  allocated_storage    = 20
  username             = "erp_admin"
  password             = "SuperSecretPassword123!" # In real life, use AWS Secrets Manager
  skip_final_snapshot  = true
}

# 3. Load Balancer: Distributes traffic to our web servers
resource "aws_lb" "erp_alb" {
  name               = "erp-alb-${var.environment}"
  internal           = false
  load_balancer_type = "application"
  subnets            = data.aws_subnets.default.ids
}

# 4. Web Servers: Auto Scaling Group
resource "aws_launch_template" "erp_web" {
  name_prefix   = "erp-web-${var.environment}"
  image_id      = "ami-0c7217cdde317cfec" # Standard Ubuntu AMI
  instance_type = var.web_server_size
  
  # A simple script to start our Python API container on boot
  user_data = base64encode(<<-EOF
              #!/bin/bash
              apt-get update -y && apt-get install podman -y
              podman run -d -p 80:5000 yourusername/erp-api:latest
              EOF
  )
}

# 5. Auto Scaling Group: Ensures we have the desired number of web servers
resource "aws_autoscaling_group" "erp_asg" {
  name                = "erp-asg-${var.environment}"
  vpc_zone_identifier = data.aws_subnets.default.ids
  desired_capacity    = var.web_server_count
  max_size            = var.web_server_count * 2
  min_size            = var.web_server_count

  launch_template {
    id      = aws_launch_template.erp_web.id
    version = "$Latest"
  }
}
