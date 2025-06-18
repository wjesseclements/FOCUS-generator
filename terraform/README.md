# FOCUS Generator Terraform Infrastructure

This directory contains the Infrastructure as Code (IaC) for the FOCUS Generator using Terraform.

## 🏗️ **Architecture Overview**

The infrastructure includes:
- **S3 Buckets**: Frontend hosting and CUR file storage
- **Lambda Function**: Backend API with pandas layer
- **API Gateway**: RESTful API with throttling and monitoring
- **CloudFront**: Global CDN for frontend (optional)
- **CloudWatch**: Comprehensive monitoring and alerting
- **IAM**: Least-privilege security roles and policies

## 📋 **Prerequisites**

1. **AWS CLI configured** with appropriate permissions
2. **Terraform >= 1.0** installed
3. **AWS account** with billing enabled for cost monitoring
4. **Domain name and SSL certificate** (optional, for custom domains)

### Required AWS Permissions

Your AWS user/role needs these permissions:
- S3: Full access for bucket management
- Lambda: Full access for function deployment
- API Gateway: Full access for API management
- CloudFront: Full access for CDN management
- IAM: Role and policy management
- CloudWatch: Monitoring and alerting
- SNS: Topic management for alerts

## 🚀 **Quick Start**

### 1. Clone and Setup

```bash
cd terraform
cp environments/staging.tfvars.example environments/staging.tfvars
cp environments/production.tfvars.example environments/production.tfvars
```

### 2. Configure Environment Variables

Edit the `.tfvars` files with your specific values:

**staging.tfvars:**
```hcl
# Update these values
billing_alerts_email = "your-email@example.com"
cors_origins = ["http://localhost:3000", "https://your-staging-domain.com"]
```

**production.tfvars:**
```hcl
# Update these values
domain_name = "your-domain.com"
certificate_arn = "arn:aws:acm:us-east-1:123456789012:certificate/abcd1234-..."
billing_alerts_email = "alerts@your-domain.com"
cors_origins = ["https://your-domain.com"]
```

### 3. Initialize Terraform

```bash
# Initialize with remote state (recommended)
terraform init

# Or initialize with local state for testing
terraform init
```

### 4. Deploy Staging Environment

```bash
# Plan the deployment
terraform plan -var-file="environments/staging.tfvars"

# Apply the changes
terraform apply -var-file="environments/staging.tfvars"
```

### 5. Deploy Production Environment

```bash
# Create a new workspace for production
terraform workspace new production

# Plan the deployment
terraform plan -var-file="environments/production.tfvars"

# Apply the changes
terraform apply -var-file="environments/production.tfvars"
```

## 📁 **File Structure**

```
terraform/
├── main.tf              # Main configuration and providers
├── variables.tf         # Input variables
├── outputs.tf           # Output values
├── s3.tf               # S3 buckets configuration
├── lambda.tf           # Lambda function and IAM
├── api_gateway.tf      # API Gateway configuration
├── cloudfront.tf       # CloudFront distribution
├── monitoring.tf       # CloudWatch and alerting
├── environments/       # Environment-specific configurations
│   ├── staging.tfvars
│   └── production.tfvars
└── README.md          # This file
```

## ⚙️ **Configuration Options**

### Core Settings

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `environment` | Environment name (staging/production) | - | ✅ |
| `aws_region` | AWS region for resources | `us-east-1` | ✅ |
| `domain_name` | Custom domain for frontend | `""` | ❌ |
| `certificate_arn` | SSL certificate ARN | `""` | ❌ |

### Lambda Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `lambda_timeout` | Function timeout in seconds | `300` |
| `lambda_memory` | Memory allocation in MB | `1024` |
| `lambda_runtime` | Python runtime version | `python3.11` |

### Storage Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `enable_s3_versioning` | Enable S3 versioning | `true` |
| `s3_lifecycle_days` | Days before object deletion | `30` |

### Monitoring Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `enable_detailed_monitoring` | Enable CloudWatch detailed monitoring | `true` |
| `log_retention_days` | CloudWatch log retention | `14` |
| `billing_alerts_email` | Email for cost alerts | `""` |
| `monthly_cost_threshold` | Cost threshold for alerts (USD) | `100` |

## 🔐 **Security Features**

### S3 Security
- **Frontend bucket**: Public read for web hosting
- **CUR files bucket**: Private with IAM-only access
- **Encryption**: AES-256 server-side encryption
- **Versioning**: Enabled for data protection

### Lambda Security
- **IAM roles**: Least-privilege access
- **Environment variables**: Secure configuration
- **VPC**: Optional VPC deployment

### API Gateway Security
- **Throttling**: Rate limiting to prevent abuse
- **CORS**: Configurable origins
- **WAF**: Optional Web Application Firewall

### CloudFront Security
- **HTTPS**: Enforce SSL/TLS
- **Security headers**: HSTS, X-Frame-Options, etc.
- **Origin Access Control**: Secure S3 access

## 📊 **Monitoring and Alerting**

### CloudWatch Metrics
- Lambda duration, errors, and invocations
- API Gateway latency and error rates
- CloudFront request metrics
- Custom FOCUS generation metrics

### Billing Alerts
- Monthly cost threshold monitoring
- Cost anomaly detection
- SNS email notifications

### Dashboard
- Comprehensive CloudWatch dashboard
- Real-time metrics visualization
- Log analysis and troubleshooting

## 🔄 **CI/CD Integration**

The Terraform configuration is designed to work with GitHub Actions:

### Environment Variables for CI/CD

After deployment, use these outputs in your CI/CD:

```bash
# Staging
STAGING_FRONTEND_BUCKET=$(terraform output -raw frontend_bucket_name)
STAGING_API_URL=$(terraform output -raw api_url)
STAGING_LAMBDA_FUNCTION_NAME=$(terraform output -raw lambda_function_name)

# Production
PRODUCTION_FRONTEND_BUCKET=$(terraform output -raw frontend_bucket_name)
PRODUCTION_API_URL=$(terraform output -raw api_url)
PRODUCTION_LAMBDA_FUNCTION_NAME=$(terraform output -raw lambda_function_name)
```

### GitHub Secrets Required

Add these secrets to your GitHub repository:
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`

### GitHub Variables Required

Add these variables for each environment:
- `STAGING_FRONTEND_BUCKET`
- `STAGING_S3_BUCKET`
- `STAGING_LAMBDA_FUNCTION_NAME`
- `STAGING_API_URL`
- `STAGING_FRONTEND_URL`
- `STAGING_CORS_ORIGINS`

## 💰 **Cost Optimization**

### Staging Environment
- Reduced CloudFront price class
- Shorter log retention
- Lower API Gateway limits
- Estimated cost: $20-50/month

### Production Environment
- Optimized for performance
- Enhanced monitoring
- Global CDN coverage
- Estimated cost: $50-200/month

### Cost Monitoring
- Billing alarms at configurable thresholds
- Cost anomaly detection
- Resource tagging for cost allocation

## 🛠️ **Maintenance**

### Regular Tasks
1. **Update Terraform**: Keep Terraform and providers updated
2. **Review costs**: Monitor monthly spending
3. **Security patches**: Update Lambda runtime and dependencies
4. **Log cleanup**: Manage CloudWatch log retention

### Backup Strategy
- S3 versioning for data protection
- Terraform state backup (if using remote state)
- Infrastructure documentation

## 🚨 **Troubleshooting**

### Common Issues

#### Terraform State Conflicts
```bash
# Force unlock if needed
terraform force-unlock <lock-id>

# Import existing resources if needed
terraform import aws_s3_bucket.frontend existing-bucket-name
```

#### Lambda Deployment Issues
```bash
# Check function status
aws lambda get-function --function-name $(terraform output -raw lambda_function_name)

# View logs
aws logs tail /aws/lambda/$(terraform output -raw lambda_function_name) --follow
```

#### API Gateway Issues
```bash
# Test API endpoint
curl -X GET $(terraform output -raw api_url)/health

# Check API Gateway logs
aws logs tail /aws/apigateway/$(terraform output -raw api_gateway_rest_api_id) --follow
```

#### CloudFront Issues
```bash
# Check distribution status
aws cloudfront get-distribution --id $(terraform output -raw cloudfront_distribution_id)

# Invalidate cache
aws cloudfront create-invalidation --distribution-id $(terraform output -raw cloudfront_distribution_id) --paths "/*"
```

### Support Resources
- [Terraform AWS Provider Documentation](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
- [AWS Lambda Documentation](https://docs.aws.amazon.com/lambda/)
- [AWS API Gateway Documentation](https://docs.aws.amazon.com/apigateway/)
- [Project Issues](https://github.com/wjesseclements/FOCUS-generator/issues)

## 🔄 **Updates and Versioning**

This infrastructure follows semantic versioning and is continuously updated to:
- Support new AWS features
- Improve security posture
- Optimize costs
- Enhance monitoring capabilities

For updates and changes, see the project's [CHANGELOG.md](../CHANGELOG.md).