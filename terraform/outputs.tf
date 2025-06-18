# Outputs for FOCUS Generator infrastructure

# S3 bucket outputs
output "frontend_bucket_name" {
  description = "Name of the S3 bucket for frontend hosting"
  value       = aws_s3_bucket.frontend.bucket
}

output "frontend_bucket_website_endpoint" {
  description = "Website endpoint for the frontend S3 bucket"
  value       = aws_s3_bucket_website_configuration.frontend.website_endpoint
}

output "cur_files_bucket_name" {
  description = "Name of the S3 bucket for CUR files"
  value       = aws_s3_bucket.cur_files.bucket
}

# Lambda outputs
output "lambda_function_name" {
  description = "Name of the Lambda function"
  value       = aws_lambda_function.focus_generator.function_name
}

output "lambda_function_arn" {
  description = "ARN of the Lambda function"
  value       = aws_lambda_function.focus_generator.arn
}

output "lambda_function_url" {
  description = "Lambda function URL (staging only)"
  value       = var.environment == "staging" ? aws_lambda_function_url.focus_generator[0].function_url : null
}

# API Gateway outputs
output "api_gateway_url" {
  description = "URL of the API Gateway"
  value       = "https://${aws_api_gateway_rest_api.focus_generator.id}.execute-api.${var.aws_region}.amazonaws.com/${aws_api_gateway_stage.focus_generator.stage_name}"
}

output "api_gateway_rest_api_id" {
  description = "ID of the API Gateway REST API"
  value       = aws_api_gateway_rest_api.focus_generator.id
}

output "api_gateway_stage_name" {
  description = "Name of the API Gateway stage"
  value       = aws_api_gateway_stage.focus_generator.stage_name
}

output "api_custom_domain_name" {
  description = "Custom domain name for API Gateway"
  value       = var.domain_name != "" && var.certificate_arn != "" ? aws_api_gateway_domain_name.focus_generator[0].domain_name : null
}

# CloudFront outputs
output "cloudfront_distribution_id" {
  description = "ID of the CloudFront distribution"
  value       = var.enable_cloudfront ? aws_cloudfront_distribution.frontend[0].id : null
}

output "cloudfront_domain_name" {
  description = "Domain name of the CloudFront distribution"
  value       = var.enable_cloudfront ? aws_cloudfront_distribution.frontend[0].domain_name : null
}

output "cloudfront_zone_id" {
  description = "Zone ID of the CloudFront distribution"
  value       = var.enable_cloudfront ? aws_cloudfront_distribution.frontend[0].hosted_zone_id : null
}

# Application URLs
output "frontend_url" {
  description = "URL of the frontend application"
  value = var.domain_name != "" ? "https://${var.domain_name}" : (
    var.enable_cloudfront ? 
    "https://${aws_cloudfront_distribution.frontend[0].domain_name}" : 
    "https://${aws_s3_bucket_website_configuration.frontend.website_endpoint}"
  )
}

output "api_url" {
  description = "URL of the API"
  value = var.domain_name != "" && var.certificate_arn != "" ? 
    "https://api.${var.domain_name}" : 
    "https://${aws_api_gateway_rest_api.focus_generator.id}.execute-api.${var.aws_region}.amazonaws.com/${aws_api_gateway_stage.focus_generator.stage_name}"
}

# Monitoring outputs
output "cloudwatch_dashboard_url" {
  description = "URL of the CloudWatch dashboard"
  value = var.enable_detailed_monitoring ? 
    "https://${var.aws_region}.console.aws.amazon.com/cloudwatch/home?region=${var.aws_region}#dashboards:name=${aws_cloudwatch_dashboard.focus_generator[0].dashboard_name}" : 
    null
}

output "sns_topic_arn" {
  description = "ARN of the SNS topic for alerts"
  value       = var.billing_alerts_email != "" ? aws_sns_topic.alerts[0].arn : null
}

# Security outputs
output "lambda_role_arn" {
  description = "ARN of the Lambda execution role"
  value       = aws_iam_role.lambda_role.arn
}

# Environment variables for CI/CD
output "environment_variables" {
  description = "Environment variables for deployment"
  value = {
    STAGING_FRONTEND_BUCKET     = var.environment == "staging" ? aws_s3_bucket.frontend.bucket : null
    STAGING_S3_BUCKET          = var.environment == "staging" ? aws_s3_bucket.cur_files.bucket : null
    STAGING_LAMBDA_FUNCTION_NAME = var.environment == "staging" ? aws_lambda_function.focus_generator.function_name : null
    STAGING_API_URL            = var.environment == "staging" ? "https://${aws_api_gateway_rest_api.focus_generator.id}.execute-api.${var.aws_region}.amazonaws.com/${aws_api_gateway_stage.focus_generator.stage_name}" : null
    STAGING_FRONTEND_URL       = var.environment == "staging" ? (var.enable_cloudfront ? "https://${aws_cloudfront_distribution.frontend[0].domain_name}" : "https://${aws_s3_bucket_website_configuration.frontend.website_endpoint}") : null
    STAGING_CORS_ORIGINS       = var.environment == "staging" ? join(",", var.cors_origins) : null
    STAGING_CLOUDFRONT_DISTRIBUTION_ID = var.environment == "staging" && var.enable_cloudfront ? aws_cloudfront_distribution.frontend[0].id : null
    
    PRODUCTION_FRONTEND_BUCKET     = var.environment == "production" ? aws_s3_bucket.frontend.bucket : null
    PRODUCTION_S3_BUCKET          = var.environment == "production" ? aws_s3_bucket.cur_files.bucket : null
    PRODUCTION_LAMBDA_FUNCTION_NAME = var.environment == "production" ? aws_lambda_function.focus_generator.function_name : null
    PRODUCTION_API_URL            = var.environment == "production" ? "https://${aws_api_gateway_rest_api.focus_generator.id}.execute-api.${var.aws_region}.amazonaws.com/${aws_api_gateway_stage.focus_generator.stage_name}" : null
    PRODUCTION_FRONTEND_URL       = var.environment == "production" ? (var.domain_name != "" ? "https://${var.domain_name}" : (var.enable_cloudfront ? "https://${aws_cloudfront_distribution.frontend[0].domain_name}" : "https://${aws_s3_bucket_website_configuration.frontend.website_endpoint}")) : null
    PRODUCTION_CORS_ORIGINS       = var.environment == "production" ? join(",", var.cors_origins) : null
    PRODUCTION_CLOUDFRONT_DISTRIBUTION_ID = var.environment == "production" && var.enable_cloudfront ? aws_cloudfront_distribution.frontend[0].id : null
  }
  sensitive = false
}

# Deployment summary
output "deployment_summary" {
  description = "Summary of deployed resources"
  value = {
    environment     = var.environment
    region          = var.aws_region
    frontend_bucket = aws_s3_bucket.frontend.bucket
    storage_bucket  = aws_s3_bucket.cur_files.bucket
    lambda_function = aws_lambda_function.focus_generator.function_name
    api_gateway_id  = aws_api_gateway_rest_api.focus_generator.id
    cloudfront_enabled = var.enable_cloudfront
    custom_domain   = var.domain_name != "" ? var.domain_name : "Not configured"
    monitoring_enabled = var.enable_detailed_monitoring
    alerts_email    = var.billing_alerts_email != "" ? var.billing_alerts_email : "Not configured"
  }
}