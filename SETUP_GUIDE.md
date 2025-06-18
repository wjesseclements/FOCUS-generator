# Complete Setup Guide for FOCUS Generator CI/CD Pipeline

This guide will walk you through the final setup steps to get your CI/CD pipeline fully operational.

## 📋 **Prerequisites Checklist**

Before starting, ensure you have:
- [ ] AWS CLI installed and configured with appropriate permissions
- [ ] Terraform installed (version 1.0 or higher)
- [ ] Admin access to your GitHub repository
- [ ] A valid email address for alerts
- [ ] (Optional) A domain name and SSL certificate for production

## 🚀 **Step 1: Configure Environment Variables**

### **1.1 Configure Staging Environment**

Edit the staging configuration file:

```bash
cd terraform/environments
```

Open `staging.tfvars` and update these values:

```hcl
# ⚠️ REQUIRED: Replace with your actual email
billing_alerts_email = "your-email@example.com"

# ⚠️ REQUIRED: Update CORS origins for staging
cors_origins = [
  "http://localhost:3000",                    # Local development
  "https://your-staging-domain.com",         # Replace with your staging domain
  "https://*.amazonaws.com"                  # AWS domains (keep this)
]

# Optional: If you have a staging domain
domain_name = "staging.yourdomain.com"      # Replace or leave empty ""
certificate_arn = ""                        # Replace with ACM certificate ARN or leave empty

# Cost settings (adjust as needed)
monthly_cost_threshold = 50                 # Alert when monthly cost exceeds $50
```

### **1.2 Configure Production Environment**

Open `production.tfvars` and update these values:

```hcl
# ⚠️ REQUIRED: Replace with your production domain
domain_name = "yourdomain.com"              # Replace with your actual domain

# ⚠️ REQUIRED: Replace with your SSL certificate ARN
certificate_arn = "arn:aws:acm:us-east-1:123456789012:certificate/abcd1234-..."

# ⚠️ REQUIRED: Replace with your alerts email
billing_alerts_email = "alerts@yourdomain.com"

# ⚠️ REQUIRED: Update CORS origins for production
cors_origins = [
  "https://yourdomain.com",                  # Replace with your domain
  "https://www.yourdomain.com"               # Replace with your domain (if using www)
]

# Cost settings
monthly_cost_threshold = 200                # Alert when monthly cost exceeds $200
```

### **1.3 AWS Permissions Verification**

Verify your AWS credentials have the required permissions:

```bash
# Test basic AWS access
aws sts get-caller-identity

# Test S3 access
aws s3 ls

# Test Lambda access
aws lambda list-functions --max-items 1

# Test IAM access
aws iam list-roles --max-items 1
```

If any command fails, you need to update your AWS permissions. Contact your AWS administrator or add these policies to your user:
- `AmazonS3FullAccess`
- `AWSLambda_FullAccess`
- `AmazonAPIGatewayAdministrator`
- `CloudFrontFullAccess`
- `CloudWatchFullAccess`
- `IAMFullAccess`

## 🏗️ **Step 2: Deploy Infrastructure**

### **2.1 Initialize Terraform**

```bash
cd terraform

# Initialize Terraform (first time only)
terraform init
```

**Expected output:**
```
Initializing the backend...
Initializing provider plugins...
- Finding hashicorp/aws versions matching "~> 5.0"...
- Installing hashicorp/aws v5.x.x...

Terraform has been successfully initialized!
```

### **2.2 Deploy Staging Environment**

```bash
# Create staging workspace
terraform workspace new staging
# If workspace already exists: terraform workspace select staging

# Plan the staging deployment
terraform plan -var-file="environments/staging.tfvars"
```

**Review the plan carefully.** You should see resources like:
- 2 S3 buckets (frontend and CUR files)
- 1 Lambda function
- 1 API Gateway
- CloudWatch resources
- IAM roles and policies

```bash
# Apply the staging deployment
terraform apply -var-file="environments/staging.tfvars"
```

When prompted, type `yes` to confirm.

**⏱️ Expected time:** 5-10 minutes

### **2.3 Deploy Production Environment**

```bash
# Create production workspace
terraform workspace new production
# If workspace already exists: terraform workspace select production

# Plan the production deployment
terraform plan -var-file="environments/production.tfvars"

# Apply the production deployment
terraform apply -var-file="environments/production.tfvars"
```

### **2.4 Save Terraform Outputs**

After each deployment, save the outputs:

```bash
# For staging
terraform workspace select staging
terraform output > staging-outputs.txt

# For production  
terraform workspace select production
terraform output > production-outputs.txt
```

**Keep these files safe** - you'll need the values for GitHub configuration.

## ⚙️ **Step 3: Set Up GitHub Repository Variables**

### **3.1 Access GitHub Repository Settings**

1. Go to your GitHub repository: `https://github.com/wjesseclements/FOCUS-generator`
2. Click **Settings** tab
3. In the left sidebar, click **Secrets and variables** → **Actions**
4. Click the **Variables** tab

### **3.2 Add Staging Environment Variables**

Click **New repository variable** and add each of these:

**From your `staging-outputs.txt` file:**

| Variable Name | Value Source | Example Value |
|---------------|--------------|---------------|
| `STAGING_FRONTEND_BUCKET` | `frontend_bucket_name` | `focus-generator-staging-frontend` |
| `STAGING_S3_BUCKET` | `cur_files_bucket_name` | `focus-generator-staging-cur-files` |
| `STAGING_LAMBDA_FUNCTION_NAME` | `lambda_function_name` | `focus-generator-staging-api` |
| `STAGING_API_URL` | `api_url` | `https://abc123.execute-api.us-east-1.amazonaws.com/staging` |
| `STAGING_FRONTEND_URL` | `frontend_url` | `https://d123456.cloudfront.net` |
| `STAGING_CORS_ORIGINS` | From your tfvars | `http://localhost:3000,https://staging.yourdomain.com` |

**If you enabled CloudFront:**
| Variable Name | Value Source |
|---------------|--------------|
| `STAGING_CLOUDFRONT_DISTRIBUTION_ID` | `cloudfront_distribution_id` |

### **3.3 Add Production Environment Variables**

| Variable Name | Value Source | Example Value |
|---------------|--------------|---------------|
| `PRODUCTION_FRONTEND_BUCKET` | `frontend_bucket_name` | `focus-generator-production-frontend` |
| `PRODUCTION_S3_BUCKET` | `cur_files_bucket_name` | `focus-generator-production-cur-files` |
| `PRODUCTION_LAMBDA_FUNCTION_NAME` | `lambda_function_name` | `focus-generator-production-api` |
| `PRODUCTION_API_URL` | `api_url` | `https://xyz789.execute-api.us-east-1.amazonaws.com/production` |
| `PRODUCTION_FRONTEND_URL` | `frontend_url` | `https://yourdomain.com` |
| `PRODUCTION_CORS_ORIGINS` | From your tfvars | `https://yourdomain.com,https://www.yourdomain.com` |

**If you enabled CloudFront:**
| Variable Name | Value Source |
|---------------|--------------|
| `PRODUCTION_CLOUDFRONT_DISTRIBUTION_ID` | `cloudfront_distribution_id` |

### **3.4 Verify GitHub Secrets Exist**

In the **Secrets** tab, verify these exist (they should already be there):
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`

If they don't exist, add them with your AWS credentials.

### **3.5 Set Up GitHub Environment Protection**

1. Go to **Settings** → **Environments**
2. Click **New environment**
3. Name it `production`
4. Under **Environment protection rules**:
   - ✅ Check **Required reviewers**
   - Add yourself as a reviewer
   - ✅ Check **Wait timer** and set to `0` minutes
5. Click **Save protection rules**

This ensures production deployments require manual approval.

## 🧪 **Step 4: Test the Pipeline**

### **4.1 Test CI Pipeline**

Create a test pull request:

```bash
# Create a new branch
git checkout -b test-ci-pipeline

# Make a small change (e.g., update README)
echo "# Testing CI Pipeline" >> TEST.md
git add TEST.md
git commit -m "Test: Add test file to verify CI pipeline"

# Push the branch
git push origin test-ci-pipeline
```

1. Go to GitHub and create a pull request
2. Watch the **Actions** tab - you should see:
   - ✅ Backend tests
   - ✅ Frontend tests  
   - ✅ Security scanning
   - ✅ Integration tests
   - ✅ Quality gate

**Expected time:** 5-8 minutes

### **4.2 Test Staging Deployment**

Merge your test PR to trigger staging deployment:

1. Merge the pull request to `main` branch
2. Go to **Actions** tab
3. Watch the "Deploy to Staging" workflow
4. Verify deployment succeeds

**Expected time:** 8-12 minutes

### **4.3 Test Staging Environment**

Once staging deployment completes:

```bash
# Test the staging API health endpoint
curl https://YOUR_STAGING_API_URL/health

# Test FOCUS generation
curl -X POST https://YOUR_STAGING_API_URL/generate-cur \
  -H "Content-Type: application/json" \
  -d '{
    "profile": "Greenfield",
    "distribution": "Evenly Distributed",
    "row_count": 5
  }'
```

Replace `YOUR_STAGING_API_URL` with the actual URL from your GitHub variables.

**Expected response:** JSON with `message` and `url` fields.

### **4.4 Test Production Deployment (Optional)**

1. Go to **Actions** tab
2. Click **Deploy to Production**
3. Click **Run workflow**
4. In the confirmation field, type: `DEPLOY`
5. Click **Run workflow**
6. The workflow will wait for manual approval
7. Click **Review deployments** and approve

**Expected time:** 10-15 minutes

### **4.5 Test Frontend Applications**

Visit your frontend URLs:
- **Staging**: Check your `STAGING_FRONTEND_URL`
- **Production**: Check your `PRODUCTION_FRONTEND_URL`

You should see the FOCUS Generator interface.

## 🔍 **Troubleshooting Common Issues**

### **Issue 1: Terraform Deployment Fails**

**Error:** `AccessDenied` or permission errors

**Solution:**
```bash
# Check your AWS credentials
aws sts get-caller-identity

# Verify you're in the right region
aws configure get region

# Check if you have the required permissions
aws iam get-user
```

### **Issue 2: GitHub Actions Fail**

**Error:** `AWS credentials not found`

**Solution:**
1. Go to GitHub **Settings** → **Secrets**
2. Verify `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` exist
3. Update them if necessary

### **Issue 3: Lambda Function Doesn't Deploy**

**Error:** Lambda update fails in CI/CD

**Solution:**
```bash
# Check if Lambda function exists
aws lambda get-function --function-name YOUR_FUNCTION_NAME

# Check CloudWatch logs
aws logs tail /aws/lambda/YOUR_FUNCTION_NAME --follow
```

### **Issue 4: Domain/SSL Certificate Issues**

**Error:** Certificate validation fails

**Solution:**
1. Verify your certificate is in `us-east-1` region (required for CloudFront)
2. Ensure certificate status is "Issued"
3. Check domain name matches exactly

### **Issue 5: CORS Errors in Frontend**

**Error:** `Access to fetch at 'API_URL' from origin 'FRONTEND_URL' has been blocked by CORS policy`

**Solution:**
1. Check your `cors_origins` in Terraform variables
2. Ensure frontend URL is included
3. Redeploy with correct CORS settings

## 📞 **Getting Help**

### **Immediate Help**
- **CloudWatch Logs**: Check AWS CloudWatch for detailed error logs
- **GitHub Actions Logs**: Click on failed workflow steps for details
- **Terraform Logs**: Run `terraform plan` to see what will change

### **Reference Documentation**
- [Terraform AWS Provider](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [AWS Lambda Documentation](https://docs.aws.amazon.com/lambda/)

### **Support Channels**
- **GitHub Issues**: [Create an issue](https://github.com/wjesseclements/FOCUS-generator/issues)
- **AWS Support**: For infrastructure-specific problems
- **Community Forums**: Stack Overflow with tags `terraform`, `aws-lambda`, `github-actions`

## ✅ **Verification Checklist**

After completing all steps, verify:

- [ ] Terraform deployed successfully for both environments
- [ ] All GitHub repository variables are set correctly
- [ ] CI pipeline passes on pull requests
- [ ] Staging deployment works automatically
- [ ] Production deployment requires manual approval
- [ ] Both frontend applications are accessible
- [ ] API endpoints respond correctly
- [ ] CloudWatch monitoring is active
- [ ] Cost alerts are configured

## 🎉 **Success!**

Once all steps are complete, you'll have:

✅ **Automated CI/CD pipeline** with comprehensive testing  
✅ **Staging environment** that auto-deploys on main branch  
✅ **Production environment** with manual approval gates  
✅ **Infrastructure as Code** with Terraform  
✅ **Comprehensive monitoring** and cost alerts  
✅ **Security scanning** on every pull request  

Your FOCUS Generator is now running with **enterprise-grade CI/CD capabilities**!

---

## 🔄 **Next Steps After Setup**

1. **Monitor costs** via AWS Billing Dashboard
2. **Review security scans** in GitHub Security tab
3. **Set up additional environments** (e.g., development)
4. **Configure custom domain** if not done initially
5. **Enable advanced monitoring** features as needed

**Estimated total setup time:** 1-2 hours (depending on experience level)