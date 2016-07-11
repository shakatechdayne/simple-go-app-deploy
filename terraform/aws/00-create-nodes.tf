# Variables
variable "vpcId" {}
variable "subnetId" {}
variable "awsKey" {}
variable "awsSecret" {}
variable "region" {}
variable "webPort" {}
variable "appPort" {}
variable "buildPort" {}
variable "amiId" {}
variable "keyPair" {}

provider "aws" {
  region = "${var.region}"
  access_key = "${var.awsKey}"
  secret_key = "${var.awsSecret}"
}

# Security group for web balancer
resource "aws_security_group" "webSg" {
  name = "WebNode SG"
  description = "Allow web requests to Web Node"
  vpc_id = "${var.vpcId}"

  ingress {
    from_port = "${var.webPort}"
    to_port = "${var.webPort}"
    protocol = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port = 22
    to_port = 22
    protocol = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port = 0
    to_port = 0
    protocol = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
# Security group for Go App
resource "aws_security_group" "appSg" {
  name = "GoApp SG"
  description = "Allow app requests to App Servers"
  vpc_id = "${var.vpcId}"

  ingress {
    from_port = "${var.appPort}"
    to_port = "${var.appPort}"
    protocol = "tcp"
    security_groups = ["${aws_security_group.webSg.id}"]
  }

  ingress {
    from_port = 22
    to_port = 22
    protocol = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port = 0
    to_port = 0
    protocol = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# Security group for Jenkins
resource "aws_security_group" "buildSg" {
  name = "Build SG"
  description = "Allow requests to build server"
  vpc_id = "${var.vpcId}"

  ingress {
    from_port = "${var.buildPort}"
    to_port = "${var.buildPort}"
    protocol = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port = 22
    to_port = 22
    protocol = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port = 0
    to_port = 0
    protocol = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# Instance definition for the Go App
resource "aws_instance" "appIns" {
  count = "2"
  ami = "${var.amiId}"
  instance_type = "t2.micro"
  subnet_id = "${var.subnetId}"
  key_name = "${var.keyPair}"
  vpc_security_group_ids = ["${aws_security_group.appSg.id}"]
  associate_public_ip_address = true
  tags {
    Name = "goApp-${count.index}"
  }
}

# Instance definition for the Web Balancer
resource "aws_instance" "webIns" {
  count = "1"
  ami = "${var.amiId}"
  instance_type = "t2.micro"
  subnet_id = "${var.subnetId}"
  key_name = "${var.keyPair}"
  vpc_security_group_ids = ["${aws_security_group.webSg.id}"]
  associate_public_ip_address = true
  tags {
    Name = "webBalancer-${count.index}"
  }
}

# Instance definition for the Builder
resource "aws_instance" "buildIns" {
  count = "1"
  ami = "${var.amiId}"
  instance_type = "t2.micro"
  subnet_id = "${var.subnetId}"
  key_name = "${var.keyPair}"
  vpc_security_group_ids = ["${aws_security_group.buildSg.id}"]
  associate_public_ip_address = true
  tags {
    Name = "appBuilder-${count.index}"
  }
}
