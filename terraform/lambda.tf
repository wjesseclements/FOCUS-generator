# Lambda function and related resources for FOCUS Generator

# IAM role for Lambda function
resource "aws_iam_role" "lambda_role" {
  name = "${local.name_prefix}-lambda-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-lambda-role"
  })
}

# IAM policy for Lambda function
resource "aws_iam_role_policy" "lambda_policy" {
  name = "${local.name_prefix}-lambda-policy"
  role = aws_iam_role.lambda_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject"
        ]
        Resource = "${aws_s3_bucket.cur_files.arn}/*"
      },
      {
        Effect = "Allow"
        Action = [
          "s3:ListBucket"
        ]
        Resource = aws_s3_bucket.cur_files.arn
      },
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "arn:aws:logs:${var.aws_region}:*:*"
      }
    ]
  })
}

# Attach basic Lambda execution role
resource "aws_iam_role_policy_attachment" "lambda_basic" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

# CloudWatch log group for Lambda
resource "aws_cloudwatch_log_group" "lambda_logs" {
  name              = "/aws/lambda/${local.name_prefix}-api"
  retention_in_days = var.log_retention_days

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-lambda-logs"
  })
}

# Lambda function
resource "aws_lambda_function" "focus_generator" {
  function_name    = "${local.name_prefix}-api"
  role            = aws_iam_role.lambda_role.arn
  handler         = "lambda_handler.handler"
  runtime         = var.lambda_runtime
  timeout         = var.lambda_timeout
  memory_size     = var.lambda_memory

  # This will be updated by CI/CD pipeline
  filename         = "placeholder.zip"
  source_code_hash = data.archive_file.placeholder.output_base64sha256

  environment {
    variables = {
      ENVIRONMENT         = var.environment
      S3_BUCKET_NAME     = aws_s3_bucket.cur_files.bucket
      CORS_ORIGINS       = join(",", var.cors_origins)
      FRONTEND_URL       = var.domain_name != "" ? "https://${var.domain_name}" : "https://${aws_s3_bucket.frontend.bucket}.s3-website-${var.aws_region}.amazonaws.com"
      S3_PUBLIC_READ     = "false"
    }
  }

  depends_on = [
    aws_iam_role_policy_attachment.lambda_basic,
    aws_cloudwatch_log_group.lambda_logs,
  ]

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-api"
  })
}

# Create placeholder zip file for initial deployment
data "archive_file" "placeholder" {
  type        = "zip"
  output_path = "/tmp/placeholder.zip"
  
  source {
    content  = "# Placeholder - will be replaced by CI/CD\ndef handler(event, context):\n    return {'statusCode': 200, 'body': 'Placeholder'}"
    filename = "lambda_handler.py"
  }
}

# Lambda function URL for direct invocation (optional)
resource "aws_lambda_function_url" "focus_generator" {
  count              = var.environment == "staging" ? 1 : 0
  function_name      = aws_lambda_function.focus_generator.function_name
  authorization_type = "NONE"

  cors {
    allow_credentials = false
    allow_origins     = var.cors_origins
    allow_methods     = ["GET", "POST", "OPTIONS"]
    allow_headers     = ["*"]
    expose_headers    = ["*"]
    max_age          = 86400
  }
}

# Lambda permission for API Gateway
resource "aws_lambda_permission" "api_gateway" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.focus_generator.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.focus_generator.execution_arn}/*/*"
}

# CloudWatch alarms for Lambda
resource "aws_cloudwatch_metric_alarm" "lambda_errors" {
  count = var.enable_detailed_monitoring ? 1 : 0
  
  alarm_name          = "${local.name_prefix}-lambda-errors"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "Errors"
  namespace           = "AWS/Lambda"
  period              = "300"
  statistic           = "Sum"
  threshold           = "5"
  alarm_description   = "This metric monitors lambda errors"
  alarm_actions       = var.billing_alerts_email != "" ? [aws_sns_topic.alerts[0].arn] : []

  dimensions = {
    FunctionName = aws_lambda_function.focus_generator.function_name
  }

  tags = local.common_tags
}

resource "aws_cloudwatch_metric_alarm" "lambda_duration" {
  count = var.enable_detailed_monitoring ? 1 : 0
  
  alarm_name          = "${local.name_prefix}-lambda-duration"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "Duration"
  namespace           = "AWS/Lambda"
  period              = "300"
  statistic           = "Average"
  threshold           = "30000" # 30 seconds
  alarm_description   = "This metric monitors lambda duration"
  alarm_actions       = var.billing_alerts_email != "" ? [aws_sns_topic.alerts[0].arn] : []

  dimensions = {
    FunctionName = aws_lambda_function.focus_generator.function_name
  }

  tags = local.common_tags
}