# FOCUS Generator Deployment Guide

This guide provides comprehensive instructions for deploying the enhanced FOCUS Generator application in various environments.

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Environment Setup](#environment-setup)
3. [Configuration](#configuration)
4. [Deployment Options](#deployment-options)
5. [Production Considerations](#production-considerations)
6. [Monitoring and Maintenance](#monitoring-and-maintenance)
7. [Troubleshooting](#troubleshooting)

## Prerequisites

### System Requirements
- Python 3.8+
- Node.js 14+
- Redis (for rate limiting and caching)
- Git

### Optional Requirements
- AWS Account (for S3 file storage)
- Docker (for containerized deployment)
- nginx (for reverse proxy)

## Environment Setup

### 1. Clone and Setup Repository
```bash
git clone <your-repository-url>
cd FOCUS-generator
```

### 2. Backend Setup
```bash
cd FOCUS-generator/backend
pip install -r requirements.txt  # Create this file with your dependencies
```

### 3. Frontend Setup
```bash
cd FOCUS-generator/frontend
npm install
npm run build
```

### 4. Environment Configuration
```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your specific settings
nano .env
```

## Configuration

### Environment Variables

Create a `.env` file in the project root with the following variables:

```bash
# Environment
ENVIRONMENT=production
DEBUG=false

# Server
API_HOST=0.0.0.0
API_PORT=8000

# CORS
CORS_ORIGINS=https://your-frontend-domain.com
CORS_ALLOW_CREDENTIALS=true
FRONTEND_URL=https://your-frontend-domain.com

# AWS (Optional)
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
S3_BUCKET_NAME=your-bucket-name
S3_PUBLIC_READ=false

# Redis
REDIS_URL=redis://localhost:6379
REDIS_MAX_CONNECTIONS=20

# Rate Limiting
RATE_LIMIT_PER_MINUTE=100
RATE_LIMIT_PER_HOUR=1000
RATE_LIMIT_PER_DAY=10000

# Security
SECRET_KEY=your-super-secret-key-change-this
CSRF_SECRET_KEY=your-csrf-secret-key

# Performance
ENABLE_COMPRESSION=true
ENABLE_CACHING=true
CACHE_TTL=3600

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json
LOG_FILE=/var/log/focus-generator.log
```

### Security Configuration

1. **Generate secure keys**:
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

2. **Set proper file permissions**:
```bash
chmod 600 .env
```

3. **Configure CORS properly** for production:
```bash
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

## Deployment Options

### Option 1: Local Development
```bash
# Start Redis
redis-server

# Start backend
cd FOCUS-generator/backend
python3 main.py

# Start frontend (development)
cd FOCUS-generator/frontend
npm start
```

### Option 2: Production with systemd

#### Backend Service
Create `/etc/systemd/system/focus-generator.service`:
```ini
[Unit]
Description=FOCUS Generator Backend
After=network.target

[Service]
Type=simple
User=focus-generator
Group=focus-generator
WorkingDirectory=/opt/focus-generator/FOCUS-generator/backend
Environment=PATH=/opt/focus-generator/venv/bin
ExecStart=/opt/focus-generator/venv/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

#### Frontend with nginx
Create `/etc/nginx/sites-available/focus-generator`:
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    # Frontend static files
    location / {
        root /opt/focus-generator/FOCUS-generator/frontend/build;
        try_files $uri $uri/ /index.html;
    }
    
    # API proxy
    location /api/ {
        proxy_pass http://localhost:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

#### Enable and start services
```bash
sudo systemctl enable focus-generator
sudo systemctl start focus-generator
sudo systemctl enable nginx
sudo systemctl start nginx
```

### Option 3: Docker Deployment

#### Dockerfile for Backend
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY FOCUS-generator/backend/requirements.txt .
RUN pip install -r requirements.txt

COPY FOCUS-generator/backend/ .
CMD ["python", "main.py"]
```

#### Dockerfile for Frontend
```dockerfile
FROM node:14-alpine as builder
WORKDIR /app
COPY FOCUS-generator/frontend/package*.json ./
RUN npm ci --only=production
COPY FOCUS-generator/frontend/ .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/build /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
```

#### docker-compose.yml
```yaml
version: '3.8'
services:
  backend:
    build: 
      context: .
      dockerfile: Dockerfile.backend
    ports:
      - "8000:8000"
    environment:
      - REDIS_URL=redis://redis:6379
    depends_on:
      - redis
    volumes:
      - ./logs:/var/log
      
  frontend:
    build:
      context: .
      dockerfile: Dockerfile.frontend
    ports:
      - "80:80"
    depends_on:
      - backend
      
  redis:
    image: redis:alpine
    ports:
      - "6379:6379"
```

### Option 4: AWS Lambda Deployment

The application includes Lambda support via `lambda_handler.py`:

1. **Package the application**:
```bash
cd FOCUS-generator/backend
pip install -r requirements.txt -t .
zip -r lambda-package.zip .
```

2. **Deploy using AWS SAM or Terraform**:
```yaml
# template.yaml
AWSTemplateFormatVersion: '2010-09-09'
Transform: AWS::Serverless-2016-10-31

Resources:
  FocusGeneratorFunction:
    Type: AWS::Serverless::Function
    Properties:
      CodeUri: FOCUS-generator/backend/
      Handler: lambda_handler.lambda_handler
      Runtime: python3.9
      Environment:
        Variables:
          ENVIRONMENT: production
          S3_BUCKET_NAME: !Ref S3Bucket
      Events:
        Api:
          Type: Api
          Properties:
            Path: /{proxy+}
            Method: ANY
```

## Production Considerations

### Performance Optimization
1. **Enable compression** in your configuration
2. **Use Redis caching** for frequently accessed data
3. **Configure proper rate limiting** based on your traffic
4. **Enable CDN** for static assets

### Security Best Practices
1. **Use HTTPS** in production
2. **Set secure CORS origins**
3. **Use strong secret keys**
4. **Enable CSRF protection**
5. **Implement proper logging** and monitoring
6. **Keep dependencies updated**

### Scaling Considerations
1. **Use multiple workers** for the backend
2. **Implement load balancing** for high traffic
3. **Use Redis Cluster** for large-scale caching
4. **Consider database optimization** for large datasets

## Monitoring and Maintenance

### Health Checks
The application includes health check endpoints:
- Backend: `GET /health`
- Frontend: Static file serving

### Logging
Configure structured logging with:
```bash
LOG_LEVEL=INFO
LOG_FORMAT=json
LOG_FILE=/var/log/focus-generator.log
```

### Monitoring Metrics
Key metrics to monitor:
- Request rate and response times
- Error rates
- Memory and CPU usage
- Redis connection pool usage
- File generation completion rates

### Log Rotation
Configure log rotation to prevent disk space issues:
```bash
# /etc/logrotate.d/focus-generator
/var/log/focus-generator.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    create 0644 focus-generator focus-generator
}
```

## Troubleshooting

### Common Issues

#### Import Errors
If you encounter import errors, run the import fix script:
```bash
python3 fix_imports.py
```

#### Redis Connection Issues
Check Redis connectivity:
```bash
redis-cli ping
```

#### Permission Errors
Ensure proper file permissions:
```bash
chown -R focus-generator:focus-generator /opt/focus-generator
chmod -R 755 /opt/focus-generator
```

### Testing Deployment
Use the integration test script to verify deployment:
```bash
python3 integration_test.py
```

### Performance Issues
1. Check Redis memory usage
2. Monitor file generation times
3. Review application logs for bottlenecks
4. Consider increasing worker processes

### Error Debugging
1. Check application logs: `tail -f /var/log/focus-generator.log`
2. Verify environment variables are set correctly
3. Test Redis connectivity
4. Check disk space for temporary files

## Backup and Recovery

### Database Backup
If using a database, implement regular backups:
```bash
# Example for PostgreSQL
pg_dump focus_generator > backup_$(date +%Y%m%d_%H%M%S).sql
```

### Configuration Backup
Regularly backup your configuration:
```bash
cp .env .env.backup.$(date +%Y%m%d)
```

### Redis Backup
Configure Redis persistence:
```bash
# In redis.conf
save 900 1
save 300 10
save 60 10000
```

## Support

For issues and questions:
1. Check the [troubleshooting section](#troubleshooting)
2. Review application logs
3. Run the integration test script
4. Check the GitHub issues page

## Security Updates

Keep the application secure:
1. Regularly update dependencies
2. Monitor security advisories
3. Review and rotate secret keys
4. Update the application to latest version

---

This deployment guide provides a comprehensive overview of deploying the FOCUS Generator application. Choose the deployment option that best fits your infrastructure and requirements.