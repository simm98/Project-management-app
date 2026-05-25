resource "aws_s3_bucket" "b" {
  bucket         = "tf-s3-bucket"
  acl            = "private"

  versioning {
    enabled = true
  }

  tags = {
    Name = "AWS S3 bucket"
    Environment = "Dev"
  }
}

resource "aws_iam_role" "backend_role" {
  name = "app-backend-role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Action    = "sts:AssumeRole",
      Effect    = "Allow",
      Principal = {
        Service = "ec2.amazonaws.com"
      }
    }]
  })
}

resource "aws_iam_policy" "s3_policy" {
  name        = "app-s3-policy"
  description = "Permite acceso al bucket S3 desde el backend"
  policy      = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Action   = ["s3:PutObject", "s3:GetObject", "s3:DeleteObject"],
        Effect   = "Allow",
        Resource = "${aws_s3_bucket.app_bucket.arn}/*"
      }
    ]
  })
}