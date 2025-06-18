# API Gateway for FOCUS Generator

# API Gateway REST API
resource "aws_api_gateway_rest_api" "focus_generator" {
  name        = "${local.name_prefix}-api"
  description = "FOCUS Generator API - ${var.environment}"

  endpoint_configuration {
    types = ["REGIONAL"]
  }

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-api"
  })
}

# API Gateway deployment
resource "aws_api_gateway_deployment" "focus_generator" {
  depends_on = [
    aws_api_gateway_method.proxy,
    aws_api_gateway_integration.proxy,
    aws_api_gateway_method.cors,
    aws_api_gateway_integration.cors,
  ]

  rest_api_id = aws_api_gateway_rest_api.focus_generator.id

  triggers = {
    redeployment = sha1(jsonencode([
      aws_api_gateway_resource.proxy.id,
      aws_api_gateway_method.proxy.id,
      aws_api_gateway_integration.proxy.id,
      aws_api_gateway_method.cors.id,
      aws_api_gateway_integration.cors.id,
    ]))
  }

  lifecycle {
    create_before_destroy = true
  }
}

# API Gateway stage
resource "aws_api_gateway_stage" "focus_generator" {
  deployment_id = aws_api_gateway_deployment.focus_generator.id
  rest_api_id   = aws_api_gateway_rest_api.focus_generator.id
  stage_name    = var.environment

  # Enable logging
  access_log_destination_arn = aws_cloudwatch_log_group.api_gateway.arn
  access_log_format = jsonencode({
    requestId      = "$context.requestId"
    ip             = "$context.identity.sourceIp"
    caller         = "$context.identity.caller"
    user           = "$context.identity.user"
    requestTime    = "$context.requestTime"
    httpMethod     = "$context.httpMethod"
    resourcePath   = "$context.resourcePath"
    status         = "$context.status"
    protocol       = "$context.protocol"
    responseLength = "$context.responseLength"
    errorMessage   = "$context.error.message"
    errorType      = "$context.error.messageString"
  })

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-api-stage"
  })
}

# CloudWatch log group for API Gateway
resource "aws_cloudwatch_log_group" "api_gateway" {
  name              = "/aws/apigateway/${local.name_prefix}"
  retention_in_days = var.log_retention_days

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-api-gateway-logs"
  })
}

# API Gateway resource for proxy
resource "aws_api_gateway_resource" "proxy" {
  rest_api_id = aws_api_gateway_rest_api.focus_generator.id
  parent_id   = aws_api_gateway_rest_api.focus_generator.root_resource_id
  path_part   = "{proxy+}"
}

# API Gateway method for proxy
resource "aws_api_gateway_method" "proxy" {
  rest_api_id   = aws_api_gateway_rest_api.focus_generator.id
  resource_id   = aws_api_gateway_resource.proxy.id
  http_method   = "ANY"
  authorization = "NONE"
}

# API Gateway integration for proxy
resource "aws_api_gateway_integration" "proxy" {
  rest_api_id = aws_api_gateway_rest_api.focus_generator.id
  resource_id = aws_api_gateway_method.proxy.resource_id
  http_method = aws_api_gateway_method.proxy.http_method

  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.focus_generator.invoke_arn
}

# API Gateway method for root
resource "aws_api_gateway_method" "proxy_root" {
  rest_api_id   = aws_api_gateway_rest_api.focus_generator.id
  resource_id   = aws_api_gateway_rest_api.focus_generator.root_resource_id
  http_method   = "ANY"
  authorization = "NONE"
}

# API Gateway integration for root
resource "aws_api_gateway_integration" "proxy_root" {
  rest_api_id = aws_api_gateway_rest_api.focus_generator.id
  resource_id = aws_api_gateway_method.proxy_root.resource_id
  http_method = aws_api_gateway_method.proxy_root.http_method

  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.focus_generator.invoke_arn
}

# CORS configuration
resource "aws_api_gateway_method" "cors" {
  rest_api_id   = aws_api_gateway_rest_api.focus_generator.id
  resource_id   = aws_api_gateway_resource.proxy.id
  http_method   = "OPTIONS"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "cors" {
  rest_api_id = aws_api_gateway_rest_api.focus_generator.id
  resource_id = aws_api_gateway_resource.proxy.id
  http_method = aws_api_gateway_method.cors.http_method
  type        = "MOCK"

  request_templates = {
    "application/json" = "{\"statusCode\": 200}"
  }
}

resource "aws_api_gateway_method_response" "cors" {
  rest_api_id = aws_api_gateway_rest_api.focus_generator.id
  resource_id = aws_api_gateway_resource.proxy.id
  http_method = aws_api_gateway_method.cors.http_method
  status_code = "200"

  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers" = true
    "method.response.header.Access-Control-Allow-Methods" = true
    "method.response.header.Access-Control-Allow-Origin"  = true
  }
}

resource "aws_api_gateway_integration_response" "cors" {
  rest_api_id = aws_api_gateway_rest_api.focus_generator.id
  resource_id = aws_api_gateway_resource.proxy.id
  http_method = aws_api_gateway_method.cors.http_method
  status_code = aws_api_gateway_method_response.cors.status_code

  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers" = "'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'"
    "method.response.header.Access-Control-Allow-Methods" = "'GET,OPTIONS,POST,PUT'"
    "method.response.header.Access-Control-Allow-Origin"  = "'*'"
  }
}

# API Gateway throttling
resource "aws_api_gateway_method_settings" "focus_generator" {
  rest_api_id = aws_api_gateway_rest_api.focus_generator.id
  stage_name  = aws_api_gateway_stage.focus_generator.stage_name
  method_path = "*/*"

  settings {
    throttling_rate_limit  = var.api_throttle_rate_limit
    throttling_burst_limit = var.api_throttle_burst_limit
    logging_level          = var.enable_detailed_monitoring ? "INFO" : "ERROR"
    data_trace_enabled     = var.enable_detailed_monitoring
    metrics_enabled        = var.enable_detailed_monitoring
  }
}

# Custom domain name (optional)
resource "aws_api_gateway_domain_name" "focus_generator" {
  count           = var.domain_name != "" && var.certificate_arn != "" ? 1 : 0
  domain_name     = "api.${var.domain_name}"
  certificate_arn = var.certificate_arn

  endpoint_configuration {
    types = ["REGIONAL"]
  }

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-api-domain"
  })
}

# Base path mapping for custom domain
resource "aws_api_gateway_base_path_mapping" "focus_generator" {
  count       = var.domain_name != "" && var.certificate_arn != "" ? 1 : 0
  api_id      = aws_api_gateway_rest_api.focus_generator.id
  stage_name  = aws_api_gateway_stage.focus_generator.stage_name
  domain_name = aws_api_gateway_domain_name.focus_generator[0].domain_name
}

# CloudWatch alarms for API Gateway
resource "aws_cloudwatch_metric_alarm" "api_gateway_errors" {
  count = var.enable_detailed_monitoring ? 1 : 0
  
  alarm_name          = "${local.name_prefix}-api-gateway-errors"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "4XXError"
  namespace           = "AWS/ApiGateway"
  period              = "300"
  statistic           = "Sum"
  threshold           = "10"
  alarm_description   = "This metric monitors API Gateway 4XX errors"
  alarm_actions       = var.billing_alerts_email != "" ? [aws_sns_topic.alerts[0].arn] : []

  dimensions = {
    ApiName = aws_api_gateway_rest_api.focus_generator.name
    Stage   = aws_api_gateway_stage.focus_generator.stage_name
  }

  tags = local.common_tags
}

resource "aws_cloudwatch_metric_alarm" "api_gateway_latency" {
  count = var.enable_detailed_monitoring ? 1 : 0
  
  alarm_name          = "${local.name_prefix}-api-gateway-latency"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "Latency"
  namespace           = "AWS/ApiGateway"
  period              = "300"
  statistic           = "Average"
  threshold           = "5000" # 5 seconds
  alarm_description   = "This metric monitors API Gateway latency"
  alarm_actions       = var.billing_alerts_email != "" ? [aws_sns_topic.alerts[0].arn] : []

  dimensions = {
    ApiName = aws_api_gateway_rest_api.focus_generator.name
    Stage   = aws_api_gateway_stage.focus_generator.stage_name
  }

  tags = local.common_tags
}