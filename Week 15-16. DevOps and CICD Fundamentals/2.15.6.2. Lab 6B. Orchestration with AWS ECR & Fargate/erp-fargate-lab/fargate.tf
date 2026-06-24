# 1. Get Default VPC and Subnet data to avoid complex network coding
data "aws_vpc" "default" { default = true }
data "aws_subnets" "default" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.default.id]
  }
}
# 2. Create the ECS Cluster
resource "aws_ecs_cluster" "erp_cluster" {
  name = "erp-production-cluster"
}
# 3. IAM Role for Fargate to pull the image from ECR
resource "aws_iam_role" "ecs_execution_role" {
  name = "ecs_execution_role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = { Service = "ecs-tasks.amazonaws.com" }
    }]
  })
}

resource "aws_iam_role_policy_attachment" "ecs_execution_role_policy" {
  role       = aws_iam_role.ecs_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

# 4. Define the Fargate Task (The "Pod" equivalent)
resource "aws_ecs_task_definition" "erp_task" {
  family                   = "erp-fargate-task"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "256" # 0.25 vCPU
  memory                   = "512" # 512 MB RAM
  execution_role_arn       = aws_iam_role.ecs_execution_role.arn

  container_definitions = jsonencode([{
    name      = "erp-api-container"
    image     = aws_ecr_repository.erp_repo.repository_url # Pulls from your private repo!
    essential = true
    portMappings = [{
      containerPort = 80
      hostPort      = 80
    }]
  }])
}

# 5. Run the Service on Fargate
resource "aws_ecs_service" "erp_service" {
  name            = "erp-fargate-service"
  cluster         = aws_ecs_cluster.erp_cluster.id
  task_definition = aws_ecs_task_definition.erp_task.arn
  launch_type     = "FARGATE"
  desired_count   = 1 # Number of containers to keep alive

  network_configuration {
    subnets          = data.aws_subnets.default.ids
    assign_public_ip = true
  }
}
