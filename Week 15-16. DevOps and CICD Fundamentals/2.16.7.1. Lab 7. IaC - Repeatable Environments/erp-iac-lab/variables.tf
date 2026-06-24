variable "environment" {
  description = "The deployment environment (e.g., dev, prod)"
  type        = string
}


variable "db_instance_class" {
  description = "The size of the database"
  type        = string
}


variable "web_server_count" {
  description = "Number of web servers to run"
  type        = number
}


variable "web_server_size" {
  description = "EC2 instance size for the web servers"
  type        = string
}
