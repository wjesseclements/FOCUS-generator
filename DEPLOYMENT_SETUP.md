# Deployment Setup Instructions

## Required AWS IAM Role Creation

The deployment pipeline requires a Lambda execution role that the GitHub Actions user doesn't have permissions to create automatically. Please create this role manually using the AWS CLI or AWS Console.

### Option 1: AWS CLI Commands

Run these commands using an AWS CLI session with IAM permissions:

```bash
# Create trust policy file
cat > trust-policy.json << 'EOF'
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF

# Create the role
aws iam create-role \
  --role-name lambda-execution-role \
  --assume-role-policy-document file://trust-policy.json \
  --description "Execution role for FOCUS Generator Lambda function"

# Attach basic Lambda execution policy
aws iam attach-role-policy \
  --role-name lambda-execution-role \
  --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole

# Attach S3 access policy for file operations
aws iam attach-role-policy \
  --role-name lambda-execution-role \
  --policy-arn arn:aws:iam::aws:policy/AmazonS3FullAccess

# Clean up
rm trust-policy.json
```

### Option 2: AWS Console

1. Go to AWS IAM Console → Roles → Create Role
2. Select "Lambda" as the use case
3. Name the role: `lambda-execution-role`
4. Attach these policies:
   - `AWSLambdaBasicExecutionRole`
   - `AmazonS3FullAccess`
5. Create the role

## Current Deployment Status

The deployment is failing because the Lambda execution role doesn't exist. Once you create the role using the steps above, the deployment should succeed.

## Error Details

```
An error occurred (AccessDenied) when calling the CreateRole operation: 
User: arn:aws:iam::***:user/github-actions is not authorized to perform: iam:CreateRole
```

The GitHub Actions user needs the `lambda-execution-role` to exist before the deployment can proceed.

## Next Steps

1. Create the `lambda-execution-role` using the instructions above
2. Re-run the deployment workflow
3. The Lambda function should deploy successfully and pass health checks