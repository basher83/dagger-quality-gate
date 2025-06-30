resource "aws_instance" "example" {
instance_type = "t2.micro"
  ami = "ami-12345678"

    tags = {
Name = "Example Instance"
  Environment = "test"
    }
}

variable "region" {
  default = "us-east-1"
description = "AWS region"
}