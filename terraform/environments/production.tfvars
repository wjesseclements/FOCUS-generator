# Production environment configuration for FOCUS Generator

environment = "production"
aws_region  = "us-east-1"

# Domain configuration
domain_name     = "yourdomain.com"  # Replace with your production domain
certificate_arn = ""  # Replace with your ACM certificate ARN

# Lambda configuration
lambda_timeout = 300
lambda_memory  = 1024

# S3 configuration
enable_s3_versioning = true
s3_lifecycle_enabled = true
s3_lifecycle_days    = 30  # Longer retention for production

# CloudFront configuration
enable_cloudfront     = true
cloudfront_price_class = "PriceClass_200"  # Better performance for production

# API Gateway configuration
api_throttle_rate_limit  = 1000
api_throttle_burst_limit = 2000

# Monitoring configuration
enable_detailed_monitoring = true
log_retention_days        = 30  # Longer retention for production

# Security configuration
cors_origins = [
  "https://yourdomain.com",      # Replace with your production domain
  "https://www.yourdomain.com"   # Replace with your production domain
]

enable_waf = false  # Enable if you need additional protection

# Cost management
billing_alerts_email    = "alerts@yourdomain.com"  # Replace with your alerts email
monthly_cost_threshold  = 200  # Higher threshold for production