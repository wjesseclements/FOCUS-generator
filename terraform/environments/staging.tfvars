# Staging environment configuration for FOCUS Generator

environment = "staging"
aws_region  = "us-east-1"

# Domain configuration (optional)
domain_name     = ""  # Set to your staging domain if you have one
certificate_arn = ""  # Set to your ACM certificate ARN if using custom domain

# Lambda configuration
lambda_timeout = 300
lambda_memory  = 1024

# S3 configuration
enable_s3_versioning = true
s3_lifecycle_enabled = true
s3_lifecycle_days    = 7  # Shorter retention for staging

# CloudFront configuration
enable_cloudfront     = true
cloudfront_price_class = "PriceClass_100"  # Cost-effective for staging

# API Gateway configuration
api_throttle_rate_limit  = 500   # Lower limits for staging
api_throttle_burst_limit = 1000

# Monitoring configuration
enable_detailed_monitoring = true
log_retention_days        = 7  # Shorter retention for staging

# Security configuration
cors_origins = [
  "http://localhost:3000",      # Local development
  "https://staging.yourdomain.com",  # Replace with your staging domain
  "https://*.amazonaws.com"     # CloudFront and S3 domains
]

enable_waf = false  # Disable WAF for staging to reduce costs

# Cost management
billing_alerts_email    = "your-email@example.com"  # Replace with your email
monthly_cost_threshold  = 50  # Lower threshold for staging