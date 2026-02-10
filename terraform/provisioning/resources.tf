# Generate a random suffix to ensure bucket name uniqueness
resource "random_string" "suffix" {
  length  = 6
  special = false
  upper   = false
}

# Create a new S3 bucket with a random suffix
resource "aws_s3_bucket" "trainticket_bucket" {
  bucket = lower("${var.AWS_INSTANCE_PREFIX}-trainticket-bucket-${random_string.suffix.result}")
  force_destroy = true

  tags = {
    Name = "${var.AWS_INSTANCE_PREFIX}-trainticket-bucket-${random_string.suffix.result}"
  }
}

# Configure public access block settings for the bucket
resource "aws_s3_bucket_public_access_block" "trainticket_bucket_public_access_block" {
  bucket = aws_s3_bucket.trainticket_bucket.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# Attach a bucket policy to allow read/write access
resource "aws_s3_bucket_policy" "trainticket_bucket_policy" {
  bucket = aws_s3_bucket.trainticket_bucket.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = { AWS = "arn:aws:iam::${var.AWS_ACCOUNT_ID}:role/TrainTicket_S3Access" }
        Action = [
          "s3:GetObject",
          "s3:PutObject"
        ]
        Resource = "${aws_s3_bucket.trainticket_bucket.arn}/*"
      }
    ]
  })
}

# Update IAM role policy to allow access to the S3 bucket
resource "aws_iam_role_policy" "trainticket_s3_policy" {
   role = length(data.aws_iam_role.existing_role.id) > 0 ? data.aws_iam_role.existing_role.name : aws_iam_role.TrainTicket_role[0].name

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:PutObject",
          "s3:GetObject",
        ]
        Resource = [
          "${aws_s3_bucket.trainticket_bucket.arn}",
        ]
      }
    ]
  })
}

# Check if the IAM role already exists
data "aws_iam_role" "existing_role" {
  name = "TrainTicket_S3Access"
}

# Create an IAM role to access S3 bucket
resource "aws_iam_role" "TrainTicket_role" {
  count = length(data.aws_iam_role.existing_role.id) == 0 ? 1 : 0
  name = "TrainTicket_S3Access"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Service = "ec2.amazonaws.com"
        }
        Action = "sts:AssumeRole"
      }
    ]
  })
  permissions_boundary = "arn:aws:iam::${var.AWS_ACCOUNT_ID}:policy/resource-provisioner-boundary"
}

# Check if the IAM instance profile already exists
data "aws_iam_instance_profile" "existing_instance_profile" {
  name = "TrainTicket_instance_profile"
}

# Create an IAM instance profile only if it doesn't exist
resource "aws_iam_instance_profile" "TrainTicket_instance_profile" {
  count = length(data.aws_iam_instance_profile.existing_instance_profile.id) == 0 ? 1 : 0
  name = "TrainTicket_instance_profile"
  role = length(data.aws_iam_role.existing_role.id) > 0 ? data.aws_iam_role.existing_role.name : aws_iam_role.TrainTicket_role[0].name
}

# Check if the security group already exists
data "aws_security_group" "existing_sg" {
  filter {
    name   = "group-name"
    values = ["TrainTicket_security_group"]
  }
}

# Create a security group only if it doesn't exist
resource "aws_security_group" "TrainTicket_sg" {
  count = length(data.aws_security_group.existing_sg.id) == 0 ? 1 : 0
  name        = "TrainTicket_security_group"
  description = "Security group for TrainTicket EC2 instances"

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  ingress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["172.31.0.0/16"]
  }
  ingress {
    from_port   = 8080
    to_port     = 8080
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  ingress {
    from_port   = 8848
    to_port     = 8848
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  ingress {
    from_port   = 16433
    to_port     = 16433
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  tags = {
    Name = "TrainTicket_security_group"
  }
}

# Create EC2 instances for the MicroK8s cluster (4 nodes: 1 master + 3 workers)
resource "aws_instance" "TrainTicket_node" {
  count         = 4
  ami           = "ami-084568db4383264d4"
  instance_type = "t2.xlarge"
  key_name      =  "${var.AWS_KEY_PAIR}"
  iam_instance_profile = length(data.aws_iam_instance_profile.existing_instance_profile.id) > 0 ? data.aws_iam_instance_profile.existing_instance_profile.name : aws_iam_instance_profile.TrainTicket_instance_profile[0].name
  vpc_security_group_ids = length(data.aws_security_group.existing_sg.id) > 0 ? [data.aws_security_group.existing_sg.id] : [aws_security_group.TrainTicket_sg[0].id]

  # Add root block device configuration
  root_block_device {
    volume_size = 50          # Size in GiB
    volume_type = "gp3"       # General Purpose SSD
    delete_on_termination = true # Automatically delete the volume when the instance is terminated
  }

tags = {
  Name = "${var.AWS_INSTANCE_PREFIX}-TrainTicket-${count.index == 0 ? "Master" : count.index == 1 ? "Worker1" : count.index == 2 ? "Worker2" : "Worker3"}"
  owning_team = "${var.AWS_OWNING_TEAM}"
}
  user_data = templatefile("${path.module}/user_data.sh", {
    instance_index         = count.index,
    AWS_INSTANCE_PREFIX    = var.AWS_INSTANCE_PREFIX,
    AWS_ACCOUNT_ID         = var.AWS_ACCOUNT_ID,
    NEW_RELIC_LICENSE_KEY  = var.NEW_RELIC_LICENSE_KEY,
    NEW_RELIC_API_KEY      = var.NEW_RELIC_API_KEY,
    NEW_RELIC_ACCOUNT_ID   = var.NEW_RELIC_ACCOUNT_ID,
    NEW_RELIC_REGION       = var.NEW_RELIC_REGION,
    NEW_RELIC_BROWSER_KEY  = var.NEW_RELIC_BROWSER_KEY,
    GITHUB_USERNAME        = var.GITHUB_USERNAME,
    GITHUB_PAT             = var.GITHUB_PAT,
    RANDOM_SUFFIX          = random_string.suffix.result,
    BUCKET_NAME            = "${lower(var.AWS_INSTANCE_PREFIX)}-trainticket-bucket-${random_string.suffix.result}"
  })
}
