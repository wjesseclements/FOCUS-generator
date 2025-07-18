# GitHub Actions Deployment Setup Guide

## Overview
This guide ensures your GitHub Actions workflows will successfully deploy the enhanced FOCUS Generator application when changes are merged.

## ✅ Workflow Files Created

### 1. CI Pipeline (`.github/workflows/ci.yml`)
- **Triggers**: On all pushes and pull requests
- **Features**:
  - Backend tests with Redis service container
  - Frontend build and tests
  - Security scanning with bandit and trufflehog
  - Import fixing for our relative imports
  - Integration testing
  - Type checking with mypy
  - Linting with flake8

### 2. Deploy Pipeline (`.github/workflows/deploy.yaml`)
- **Triggers**: On push to main branch or manual dispatch
- **Features**:
  - Frontend deployment to S3
  - Backend deployment to AWS Lambda
  - Pandas layer creation for Lambda
  - Environment variable configuration
  - CloudFront cache invalidation (if configured)
  - Post-deployment validation

## 🔐 Required GitHub Secrets

Configure these secrets in your GitHub repository (Settings → Secrets and variables → Actions):

### Essential Secrets
1. **AWS_ACCESS_KEY_ID**: AWS IAM user access key
2. **AWS_SECRET_ACCESS_KEY**: AWS IAM user secret key
3. **SECRET_KEY**: Application secret key (generate with: `python3 -c "import secrets; print(secrets.token_urlsafe(32))"`)
4. **CSRF_SECRET_KEY**: CSRF protection key (generate same way as SECRET_KEY)
5. **REDIS_URL**: Redis connection URL (e.g., `redis://your-redis-host:6379`)
6. **PRODUCTION_API_URL**: Your Lambda function URL (will be available after first deployment)

### Optional Secrets
7. **CLOUDFRONT_DISTRIBUTION_ID**: If using CloudFront CDN

## 🛠️ Pre-Deployment Checklist

### AWS Resources Setup
Ensure these AWS resources exist:

1. **S3 Bucket**: `cur-gen-bucket` (or update in deploy.yaml)
   ```bash
   aws s3 mb s3://cur-gen-bucket
   aws s3api put-bucket-website --bucket cur-gen-bucket --website-configuration file://website-config.json
   ```

2. **Lambda Function**: `focus-generator-api`
   ```bash
   aws lambda create-function \
     --function-name focus-generator-api \
     --runtime python3.11 \
     --role arn:aws:iam::YOUR_ACCOUNT:role/lambda-execution-role \
     --handler lambda_handler.lambda_handler \
     --zip-file fileb://initial-function.zip
   ```

3. **IAM Role**: Lambda execution role with permissions for:
   - S3 access (if using S3 for file storage)
   - CloudWatch Logs
   - Lambda layer usage

### Local Testing
Before pushing:

1. **Run validation script**:
   ```bash
   python3 validate_workflows.py
   ```

2. **Test imports**:
   ```bash
   python3 fix_imports.py
   python3 integration_test.py
   ```

3. **Check requirements**:
   ```bash
   pip install -r requirements.txt
   cd FOCUS-generator/frontend && npm install
   ```

## 🚀 Deployment Process

### Initial Deployment
1. **Configure GitHub Secrets** (see above)
2. **Create AWS resources** (S3 bucket, Lambda function)
3. **Push to main branch**:
   ```bash
   git add .
   git commit -m "feat: Add enhanced FOCUS Generator with CI/CD"
   git push origin main
   ```

### Monitoring Deployment
1. Go to GitHub Actions tab in your repository
2. Watch the "Deploy FOCUS Generator" workflow
3. Check for any errors in the logs
4. Verify deployment:
   - Frontend: `https://cur-gen-bucket.s3-website-us-east-1.amazonaws.com`
   - Backend: Check Lambda function URL in AWS Console

## 🔧 Troubleshooting

### Common Issues

1. **Import Errors in Lambda**:
   - The `fix_imports.py` script runs automatically
   - Ensure all backend files use relative imports

2. **Lambda Package Too Large**:
   - Pandas and heavy dependencies are in a separate layer
   - Only lightweight dependencies are in the main package

3. **CORS Issues**:
   - Lambda function URL CORS is configured in deploy workflow
   - Frontend should use the PRODUCTION_API_URL secret

4. **Missing Dependencies**:
   - Check `requirements.txt` includes all packages
   - Lambda uses a subset defined in the workflow

### Workflow Customization

#### Change AWS Region
Update in `.github/workflows/deploy.yaml`:
```yaml
env:
  AWS_REGION: your-region  # Default: us-east-1
```

#### Change Resource Names
Update these environment variables:
```yaml
env:
  LAMBDA_FUNCTION_NAME: your-function-name
  S3_BUCKET_NAME: your-bucket-name
  PANDAS_LAYER_NAME: your-layer-name
```

#### Add More Environment Variables
In the Lambda configuration step:
```yaml
--environment Variables="{
  YOUR_NEW_VAR=${{ secrets.YOUR_NEW_SECRET }},
  ...
}"
```

## 📊 Post-Deployment Validation

After successful deployment:

1. **Test Health Endpoint**:
   ```bash
   curl https://your-lambda-url/health
   ```

2. **Check CloudWatch Logs**:
   - Go to AWS CloudWatch
   - Find `/aws/lambda/focus-generator-api` log group
   - Check for any errors

3. **Test File Generation**:
   - Access frontend URL
   - Generate a test FOCUS file
   - Verify download works

4. **Monitor Performance**:
   - Check Lambda metrics
   - Monitor Redis connections
   - Review error rates

## 🔄 Continuous Deployment

The workflows are configured for continuous deployment:

1. **Feature Branches**: 
   - Push to any branch triggers CI tests
   - No deployment occurs

2. **Main Branch**:
   - Push to main triggers both CI and deployment
   - Automatic deployment to production

3. **Manual Deployment**:
   - Use "workflow_dispatch" in GitHub Actions
   - Allows deployment without code changes

## 📝 Maintenance

### Updating Dependencies
1. Update `requirements.txt`
2. Test locally
3. Push changes - workflows will handle the rest

### Updating Lambda Configuration
1. Modify environment variables in deploy.yaml
2. Adjust memory/timeout if needed
3. Push changes

### Rotating Secrets
1. Generate new secrets locally
2. Update in GitHub Secrets
3. Trigger a new deployment

## 🎯 Success Criteria

Your deployment is successful when:

- ✅ All GitHub Actions workflows pass
- ✅ Frontend loads without errors
- ✅ Backend health check returns 200
- ✅ File generation works end-to-end
- ✅ No errors in CloudWatch logs
- ✅ Performance metrics are acceptable

## 📞 Support

If you encounter issues:

1. Check workflow logs in GitHub Actions
2. Review CloudWatch logs for Lambda
3. Verify all secrets are correctly set
4. Ensure AWS resources have proper permissions
5. Run local validation scripts

---

**Ready to Deploy!** 🚀

Once you've completed the setup above, your enhanced FOCUS Generator will automatically deploy whenever you push to the main branch.