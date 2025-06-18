# Production Deployment Guide

This guide provides comprehensive instructions for deploying the FOCUS Generator to production environments.

## 🏗️ **Architecture Overview**

The FOCUS Generator consists of two main components:
- **Backend**: FastAPI application that generates FOCUS-compliant CUR data
- **Frontend**: React application that provides the user interface

## 🚀 **Deployment Options**

### **Option 1: AWS Lambda + S3 (Recommended)**

This is the current architecture designed for serverless deployment.

#### **Backend Deployment (AWS Lambda)**

1. **Package the Lambda Function**
   ```bash
   cd backend
   pip install -r requirements.txt -t ./
   zip -r focus-generator-lambda.zip . -x "*.pyc" "__pycache__/*"
   ```

2. **Create Lambda Function**
   ```bash
   aws lambda create-function \
     --function-name focus-generator \
     --runtime python3.9 \
     --role arn:aws:iam::YOUR-ACCOUNT:role/lambda-execution-role \
     --handler main.handler \
     --zip-file fileb://focus-generator-lambda.zip \
     --timeout 300 \
     --memory-size 1024
   ```

3. **Configure Environment Variables**
   ```bash
   aws lambda update-function-configuration \
     --function-name focus-generator \
     --environment Variables='{
       "ENVIRONMENT":"production",
       "S3_BUCKET_NAME":"your-focus-generator-bucket",
       "CORS_ORIGINS":"https://your-domain.com",
       "FRONTEND_URL":"https://your-domain.com",
       "S3_PUBLIC_READ":"false"
     }'
   ```

4. **Create API Gateway**
   ```bash
   aws apigateway create-rest-api --name focus-generator-api
   # Configure resources and methods as needed
   ```

#### **Frontend Deployment (S3 + CloudFront)**

1. **Build the React Application**
   ```bash
   cd frontend
   npm install
   npm run build
   ```

2. **Create S3 Bucket for Hosting**
   ```bash
   aws s3 mb s3://your-focus-generator-frontend
   aws s3 website s3://your-focus-generator-frontend \
     --index-document index.html \
     --error-document index.html
   ```

3. **Deploy Frontend**
   ```bash
   aws s3 sync build/ s3://your-focus-generator-frontend
   ```

4. **Configure CloudFront Distribution**
   ```bash
   aws cloudfront create-distribution \
     --distribution-config file://cloudfront-config.json
   ```

### **Option 2: Docker Containers**

#### **Backend Dockerfile**
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY backend/requirements.txt .
RUN pip install -r requirements.txt

COPY backend/ .
EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### **Frontend Dockerfile**
```dockerfile
FROM node:18-alpine as build

WORKDIR /app
COPY frontend/package*.json ./
RUN npm ci

COPY frontend/ .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/build /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

#### **Docker Compose for Development**
```yaml
version: '3.8'
services:
  backend:
    build: 
      context: .
      dockerfile: backend/Dockerfile
    ports:
      - "8000:8000"
    environment:
      - ENVIRONMENT=development
      - S3_BUCKET_NAME=dev-focus-bucket
      - CORS_ORIGINS=http://localhost:3000
      
  frontend:
    build:
      context: .
      dockerfile: frontend/Dockerfile
    ports:
      - "80:80"
    depends_on:
      - backend
```

### **Option 3: Traditional Server Deployment**

#### **Backend (Ubuntu/CentOS Server)**

1. **Install Dependencies**
   ```bash
   sudo apt update
   sudo apt install python3 python3-pip nginx certbot
   pip3 install -r requirements.txt
   ```

2. **Configure Systemd Service**
   ```ini
   # /etc/systemd/system/focus-generator.service
   [Unit]
   Description=FOCUS Generator API
   After=network.target

   [Service]
   User=www-data
   Group=www-data
   WorkingDirectory=/var/www/focus-generator/backend
   Environment="PATH=/var/www/focus-generator/venv/bin"
   ExecStart=/var/www/focus-generator/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
   Restart=always

   [Install]
   WantedBy=multi-user.target
   ```

3. **Configure Nginx**
   ```nginx
   # /etc/nginx/sites-available/focus-generator
   server {
       listen 80;
       server_name your-api-domain.com;
       
       location / {
           proxy_pass http://127.0.0.1:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

## ⚙️ **Environment Configuration**

### **Backend Environment Variables**

Create `.env` file in the backend directory:

```bash
# Production Configuration
ENVIRONMENT=production

# AWS S3 Configuration
S3_BUCKET_NAME=your-production-bucket
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_DEFAULT_REGION=us-east-1
S3_PUBLIC_READ=false

# CORS Configuration
CORS_ORIGINS=https://your-domain.com,https://www.your-domain.com
FRONTEND_URL=https://your-domain.com

# Optional: Custom AWS endpoint for testing
# AWS_ENDPOINT_URL=http://localhost:4566
```

### **Frontend Environment Variables**

Create `.env.production` file in the frontend directory:

```bash
# Production API URL
REACT_APP_API_URL=https://your-api-domain.com

# Production Environment
REACT_APP_ENVIRONMENT=production
```

## 🛡️ **Security Configuration**

### **1. AWS IAM Policies**

#### **Lambda Execution Role Policy**
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "logs:CreateLogGroup",
                "logs:CreateLogStream",
                "logs:PutLogEvents"
            ],
            "Resource": "arn:aws:logs:*:*:*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "s3:GetObject",
                "s3:PutObject",
                "s3:DeleteObject"
            ],
            "Resource": "arn:aws:s3:::your-focus-generator-bucket/*"
        }
    ]
}
```

### **2. S3 Bucket Policies**

#### **Backend Bucket Policy (Private)**
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "DenyPublicRead",
            "Effect": "Deny",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::your-focus-generator-bucket/*",
            "Condition": {
                "StringNotEquals": {
                    "aws:PrincipalServiceName": "lambda.amazonaws.com"
                }
            }
        }
    ]
}
```

#### **Frontend Bucket Policy (Public Read)**
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "PublicReadGetObject",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::your-focus-generator-frontend/*"
        }
    ]
}
```

### **3. CORS Configuration**

Ensure CORS is properly configured in production:

```python
# backend/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,  # Only specific domains
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
```

## 📋 **Production Checklist**

### **Pre-Deployment**
- [ ] All tests passing (`npm test` and backend tests)
- [ ] Environment variables configured for production
- [ ] Remove all hardcoded development URLs
- [ ] Configure proper CORS origins
- [ ] Set up SSL certificates
- [ ] Configure monitoring and logging

### **Backend Checklist**
- [ ] `ENVIRONMENT=production` set
- [ ] S3 bucket configured with proper permissions
- [ ] `S3_PUBLIC_READ=false` for security
- [ ] CORS origins set to production domains only
- [ ] AWS credentials configured (preferably IAM roles)
- [ ] Lambda timeout increased to 300 seconds
- [ ] Memory allocation sufficient (1024MB recommended)

### **Frontend Checklist**
- [ ] `REACT_APP_API_URL` points to production API
- [ ] `REACT_APP_ENVIRONMENT=production`
- [ ] Build optimized (`npm run build`)
- [ ] Static assets served via CDN
- [ ] Gzip compression enabled
- [ ] Cache headers configured

### **Security Checklist**
- [ ] No secrets in source code
- [ ] API rate limiting implemented
- [ ] HTTPS enforced
- [ ] Security headers configured
- [ ] Input validation on all endpoints
- [ ] CORS configured for specific origins only

## 📊 **Monitoring and Logging**

### **CloudWatch Metrics (AWS)**
- Lambda function duration and errors
- API Gateway request counts and latency
- S3 storage usage

### **Application Logs**
```python
# Enhanced logging configuration
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

### **Health Checks**
The application includes health check endpoints:
- Backend: `GET /health`
- Frontend: Service worker status

## 🔄 **CI/CD Pipeline**

### **GitHub Actions Example**
```yaml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  deploy-backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Deploy to Lambda
        run: |
          # Package and deploy backend
          cd backend
          pip install -r requirements.txt -t ./
          zip -r ../function.zip .
          aws lambda update-function-code \
            --function-name focus-generator \
            --zip-file fileb://../function.zip

  deploy-frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Build and Deploy Frontend
        run: |
          cd frontend
          npm ci
          npm run build
          aws s3 sync build/ s3://your-focus-generator-frontend
          aws cloudfront create-invalidation \
            --distribution-id YOUR-DISTRIBUTION-ID \
            --paths "/*"
```

## 🚨 **Troubleshooting**

### **Common Issues**

#### **Lambda Timeout**
- Increase timeout to 300 seconds
- Optimize code for faster execution
- Consider pagination for large datasets

#### **CORS Errors**
- Verify CORS_ORIGINS environment variable
- Check API Gateway CORS configuration
- Ensure preflight requests are handled

#### **S3 Access Denied**
- Verify IAM permissions
- Check bucket policies
- Ensure AWS credentials are correct

#### **Frontend Build Errors**
- Check Node.js version compatibility
- Clear npm cache: `npm cache clean --force`
- Delete node_modules and reinstall

## 📈 **Performance Optimization**

### **Backend Optimizations**
- Enable Lambda provisioned concurrency for consistent performance
- Use connection pooling for database connections
- Implement caching for frequently requested data

### **Frontend Optimizations**
- Enable gzip compression
- Configure browser caching headers
- Use CloudFront for global content delivery
- Implement code splitting for large applications

## 📞 **Support and Maintenance**

### **Monitoring Alerts**
Set up alerts for:
- Lambda function errors
- API Gateway 5xx errors
- High response times
- S3 storage limits

### **Backup Strategy**
- Regular S3 bucket backups
- Version control for all configurations
- Database backups if applicable

### **Update Procedures**
1. Test all changes in staging environment
2. Deploy during low-traffic periods
3. Monitor for errors post-deployment
4. Have rollback plan ready

This production deployment guide ensures a secure, scalable, and maintainable FOCUS Generator deployment.