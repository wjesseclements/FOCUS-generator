# S3 buckets for FOCUS Generator

# S3 bucket for frontend hosting
resource "aws_s3_bucket" "frontend" {
  bucket = "${local.name_prefix}-frontend"
  
  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-frontend"
    Type = "Frontend"
  })
}

# S3 bucket for generated CUR files
resource "aws_s3_bucket" "cur_files" {
  bucket = "${local.name_prefix}-cur-files"
  
  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-cur-files"
    Type = "Storage"
  })
}

# Frontend bucket configuration
resource "aws_s3_bucket_versioning" "frontend" {
  bucket = aws_s3_bucket.frontend.id
  versioning_configuration {
    status = var.enable_s3_versioning ? "Enabled" : "Disabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "frontend" {
  bucket = aws_s3_bucket.frontend.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "frontend" {
  bucket = aws_s3_bucket.frontend.id

  # Frontend needs to be publicly readable
  block_public_acls       = false
  block_public_policy     = false
  ignore_public_acls      = false
  restrict_public_buckets = false
}

resource "aws_s3_bucket_website_configuration" "frontend" {
  bucket = aws_s3_bucket.frontend.id

  index_document {
    suffix = "index.html"
  }

  error_document {
    key = "index.html"
  }
}

resource "aws_s3_bucket_policy" "frontend" {
  bucket = aws_s3_bucket.frontend.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid       = "PublicReadGetObject"
        Effect    = "Allow"
        Principal = "*"
        Action    = "s3:GetObject"
        Resource  = "${aws_s3_bucket.frontend.arn}/*"
      }
    ]
  })

  depends_on = [aws_s3_bucket_public_access_block.frontend]
}

# CUR files bucket configuration (private)
resource "aws_s3_bucket_versioning" "cur_files" {
  bucket = aws_s3_bucket.cur_files.id
  versioning_configuration {
    status = var.enable_s3_versioning ? "Enabled" : "Disabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "cur_files" {
  bucket = aws_s3_bucket.cur_files.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "cur_files" {
  bucket = aws_s3_bucket.cur_files.id

  # CUR files bucket should be private
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# Lifecycle configuration for CUR files
resource "aws_s3_bucket_lifecycle_configuration" "cur_files" {
  count  = var.s3_lifecycle_enabled ? 1 : 0
  bucket = aws_s3_bucket.cur_files.id

  rule {
    id     = "cleanup_old_files"
    status = "Enabled"

    expiration {
      days = var.s3_lifecycle_days
    }

    noncurrent_version_expiration {
      noncurrent_days = 7
    }

    abort_incomplete_multipart_upload {
      days_after_initiation = 1
    }
  }
}

# CORS configuration for CUR files bucket
resource "aws_s3_bucket_cors_configuration" "cur_files" {
  bucket = aws_s3_bucket.cur_files.id

  cors_rule {
    allowed_headers = ["*"]
    allowed_methods = ["GET", "HEAD"]
    allowed_origins = var.cors_origins
    expose_headers  = ["ETag"]
    max_age_seconds = 3000
  }
}