# Monitoring and alerting for FOCUS Generator

# SNS topic for alerts
resource "aws_sns_topic" "alerts" {
  count = var.billing_alerts_email != "" ? 1 : 0
  name  = "${local.name_prefix}-alerts"

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-alerts"
  })
}

# SNS topic subscription for email alerts
resource "aws_sns_topic_subscription" "email_alerts" {
  count     = var.billing_alerts_email != "" ? 1 : 0
  topic_arn = aws_sns_topic.alerts[0].arn
  protocol  = "email"
  endpoint  = var.billing_alerts_email
}

# CloudWatch dashboard
resource "aws_cloudwatch_dashboard" "focus_generator" {
  count          = var.enable_detailed_monitoring ? 1 : 0
  dashboard_name = "${local.name_prefix}-dashboard"

  dashboard_body = jsonencode({
    widgets = [
      {
        type   = "metric"
        x      = 0
        y      = 0
        width  = 12
        height = 6

        properties = {
          metrics = [
            ["AWS/Lambda", "Duration", "FunctionName", aws_lambda_function.focus_generator.function_name],
            [".", "Errors", ".", "."],
            [".", "Invocations", ".", "."]
          ]
          view    = "timeSeries"
          stacked = false
          region  = var.aws_region
          title   = "Lambda Metrics"
          period  = 300
        }
      },
      {
        type   = "metric"
        x      = 0
        y      = 6
        width  = 12
        height = 6

        properties = {
          metrics = [
            ["AWS/ApiGateway", "Count", "ApiName", aws_api_gateway_rest_api.focus_generator.name, "Stage", aws_api_gateway_stage.focus_generator.stage_name],
            [".", "Latency", ".", ".", ".", "."],
            [".", "4XXError", ".", ".", ".", "."],
            [".", "5XXError", ".", ".", ".", "."]
          ]
          view    = "timeSeries"
          stacked = false
          region  = var.aws_region
          title   = "API Gateway Metrics"
          period  = 300
        }
      },
      {
        type   = "metric"
        x      = 0
        y      = 12
        width  = 12
        height = 6

        properties = {
          metrics = var.enable_cloudfront ? [
            ["AWS/CloudFront", "Requests", "DistributionId", aws_cloudfront_distribution.frontend[0].id],
            [".", "BytesDownloaded", ".", "."],
            [".", "4xxErrorRate", ".", "."],
            [".", "5xxErrorRate", ".", "."]
          ] : []
          view    = "timeSeries"
          stacked = false
          region  = "us-east-1" # CloudFront metrics are always in us-east-1
          title   = "CloudFront Metrics"
          period  = 300
        }
      },
      {
        type   = "log"
        x      = 12
        y      = 0
        width  = 12
        height = 18

        properties = {
          query   = "SOURCE '${aws_cloudwatch_log_group.lambda_logs.name}'\n| fields @timestamp, @message\n| sort @timestamp desc\n| limit 100"
          region  = var.aws_region
          title   = "Recent Lambda Logs"
          view    = "table"
        }
      }
    ]
  })
}

# Billing alarm
resource "aws_cloudwatch_metric_alarm" "billing" {
  count = var.billing_alerts_email != "" ? 1 : 0
  
  alarm_name          = "${local.name_prefix}-billing-alarm"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "1"
  metric_name         = "EstimatedCharges"
  namespace           = "AWS/Billing"
  period              = "86400" # 24 hours
  statistic           = "Maximum"
  threshold           = var.monthly_cost_threshold
  alarm_description   = "This metric monitors monthly estimated charges"
  alarm_actions       = [aws_sns_topic.alerts[0].arn]

  dimensions = {
    Currency = "USD"
  }

  tags = local.common_tags
}

# Custom metric for FOCUS generation success rate
resource "aws_cloudwatch_log_metric_filter" "focus_generation_success" {
  count          = var.enable_detailed_monitoring ? 1 : 0
  name           = "${local.name_prefix}-focus-generation-success"
  log_group_name = aws_cloudwatch_log_group.lambda_logs.name
  pattern        = "[timestamp, request_id, level=\"INFO\", message=\"FOCUS generation completed successfully\"]"

  metric_transformation {
    name      = "FOCUSGenerationSuccess"
    namespace = "FOCUS/Generator"
    value     = "1"
  }
}

resource "aws_cloudwatch_log_metric_filter" "focus_generation_error" {
  count          = var.enable_detailed_monitoring ? 1 : 0
  name           = "${local.name_prefix}-focus-generation-error"
  log_group_name = aws_cloudwatch_log_group.lambda_logs.name
  pattern        = "[timestamp, request_id, level=\"ERROR\", message]"

  metric_transformation {
    name      = "FOCUSGenerationError"
    namespace = "FOCUS/Generator"
    value     = "1"
  }
}

# Alarm for FOCUS generation errors
resource "aws_cloudwatch_metric_alarm" "focus_generation_errors" {
  count = var.enable_detailed_monitoring && var.billing_alerts_email != "" ? 1 : 0
  
  alarm_name          = "${local.name_prefix}-focus-generation-errors"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "1"
  metric_name         = "FOCUSGenerationError"
  namespace           = "FOCUS/Generator"
  period              = "300"
  statistic           = "Sum"
  threshold           = "3"
  alarm_description   = "This metric monitors FOCUS generation errors"
  alarm_actions       = [aws_sns_topic.alerts[0].arn]
  treat_missing_data  = "notBreaching"

  tags = local.common_tags
}

# Cost anomaly detection
resource "aws_ce_anomaly_detector" "focus_generator" {
  count         = var.billing_alerts_email != "" ? 1 : 0
  name          = "${local.name_prefix}-cost-anomaly"
  monitor_type  = "DIMENSIONAL"

  specification = jsonencode({
    Dimension     = "SERVICE"
    MatchOptions  = ["EQUALS"]
    Values        = ["Amazon Simple Storage Service", "AWS Lambda", "Amazon API Gateway", "Amazon CloudFront"]
  })

  tags = local.common_tags
}

resource "aws_ce_anomaly_subscription" "focus_generator" {
  count     = var.billing_alerts_email != "" ? 1 : 0
  name      = "${local.name_prefix}-cost-anomaly-subscription"
  frequency = "DAILY"
  
  monitor_arn_list = [
    aws_ce_anomaly_detector.focus_generator[0].arn
  ]
  
  subscriber {
    type    = "EMAIL"
    address = var.billing_alerts_email
  }

  threshold_expression {
    and {
      dimension {
        key           = "ANOMALY_TOTAL_IMPACT_ABSOLUTE"
        values        = [tostring(var.monthly_cost_threshold / 10)] # Alert if anomaly > 10% of threshold
        match_options = ["GREATER_THAN_OR_EQUAL"]
      }
    }
  }

  tags = local.common_tags
}

# Application Insights for enhanced monitoring
resource "aws_applicationinsights_application" "focus_generator" {
  count                = var.enable_detailed_monitoring ? 1 : 0
  resource_group_name  = aws_resourcegroups_group.focus_generator[0].name
  auto_config_enabled  = true
  cwe_monitor_enabled  = true
  auto_create          = true

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-app-insights"
  })

  depends_on = [aws_resourcegroups_group.focus_generator]
}

# Resource group for Application Insights
resource "aws_resourcegroups_group" "focus_generator" {
  count = var.enable_detailed_monitoring ? 1 : 0
  name  = "${local.name_prefix}-resources"

  resource_query {
    query = jsonencode({
      ResourceTypeFilters = ["AWS::AllSupported"]
      TagFilters = [
        {
          Key    = "Project"
          Values = ["FOCUS-Generator"]
        },
        {
          Key    = "Environment"
          Values = [var.environment]
        }
      ]
    })
  }

  tags = local.common_tags
}