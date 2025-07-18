# FOCUS Generator - Enhanced Edition

[![CI](https://github.com/wjesseclements/FOCUS-generator/actions/workflows/ci.yml/badge.svg)](https://github.com/wjesseclements/FOCUS-generator/actions/workflows/ci.yml)
[![Deploy](https://github.com/wjesseclements/FOCUS-generator/actions/workflows/deploy.yaml/badge.svg)](https://github.com/wjesseclements/FOCUS-generator/actions/workflows/deploy.yaml)

> Generate synthetic FOCUS-compliant Cost and Usage Reports (CURs) for building and testing cloud cost dashboards with enterprise-grade reliability and security.

## 🚀 What's New in Enhanced Edition

This enhanced version includes significant improvements for production readiness, security, and performance:

### 🔒 **Security & Reliability**
- **Comprehensive Input Validation** - Pydantic models with security mixins and input sanitization
- **CSRF Protection** - Token-based CSRF protection middleware for production security
- **Advanced Rate Limiting** - Redis-based sliding window rate limiting with per-minute/hour/day limits
- **Robust Error Handling** - Domain-specific exception hierarchy with correlation IDs and structured logging

### ⚡ **Performance & Scalability**
- **Streaming CSV Generation** - Memory-efficient streaming for large datasets (100K+ rows)
- **Request/Response Compression** - GZip compression for improved network performance
- **React Optimization** - Component memoization and optimized re-rendering
- **Retry Logic** - Exponential backoff with circuit breaker patterns for external services

### 🛠 **Developer Experience**
- **Comprehensive Type Hints** - Full TypeScript-style annotations throughout backend
- **Enhanced Error Boundaries** - Graceful error handling in React components
- **Centralized Configuration** - Unified config management across environments
- **Detailed Logging** - Structured logging with correlation IDs for debugging

## 📋 Table of Contents

- [Features](#features)
- [Quick Start](#quick-start)
- [Architecture](#architecture)
- [API Documentation](#api-documentation)
- [Configuration](#configuration)
- [Development](#development)
- [Deployment](#deployment)
- [Contributing](#contributing)

## ✨ Features

### Core Functionality
- **FOCUS v1.1 Compliant** - Generate synthetic data following FinOps Open Cost and Usage Specification
- **Multi-Cloud Support** - AWS, Azure, and Google Cloud Provider data generation
- **Multiple Profiles** - Greenfield, Large Business, and Enterprise cost patterns
- **Trend Simulation** - Linear, seasonal, step-change, and anomaly patterns
- **Multi-Month Generation** - Generate historical data with realistic trends

### Data Generation Options
- **Distribution Patterns**: Evenly Distributed, ML-Focused, Data-Intensive, Media-Intensive
- **Configurable Scale**: From 1 to 100,000 rows per dataset
- **File Formats**: CSV and compressed CSV (gzip)
- **Packaging**: Individual files or ZIP archives for multi-cloud/multi-month data

### Production Features
- **High Availability** - Built for AWS Lambda with auto-scaling
- **Security First** - CSRF protection, input validation, rate limiting
- **Monitoring Ready** - Structured logging, error correlation, health checks
- **Performance Optimized** - Streaming generation, compression, caching

## 🚦 Quick Start

### Prerequisites
- Python 3.9+
- Node.js 16+
- Redis (for production rate limiting)
- AWS CLI (for deployment)

### Local Development

```bash
# Clone the repository
git clone https://github.com/wjesseclements/FOCUS-generator.git
cd FOCUS-generator

# Backend setup
cd FOCUS-generator/backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Frontend setup
cd ../frontend
npm install

# Start development servers
# Terminal 1 - Backend
cd backend
python main.py

# Terminal 2 - Frontend
cd frontend
npm start
```

### Docker Development

```bash
# Build and run with Docker Compose
docker-compose up --build

# Access the application
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Quick Test

```bash
# Generate sample data via API
curl -X POST "http://localhost:8000/generate-cur" \
  -H "Content-Type: application/json" \
  -d '{
    "profile": "Greenfield",
    "distribution": "Evenly Distributed",
    "row_count": 100,
    "providers": ["aws"]
  }'
```

## 🏗 Architecture

### System Overview
```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   React     │    │   FastAPI   │    │   AWS S3    │
│  Frontend   │───▶│   Backend   │───▶│  Storage    │
│             │    │             │    │             │
└─────────────┘    └─────────────┘    └─────────────┘
                           │
                   ┌─────────────┐
                   │    Redis    │
                   │Rate Limiting│
                   └─────────────┘
```

### Key Components

#### Backend (`/backend`)
- **FastAPI Application** - High-performance async API framework
- **Data Generation Engine** - FOCUS-compliant synthetic data creation
- **Multi-File Generator** - Multi-cloud and multi-month data orchestration
- **Streaming Engine** - Memory-efficient large dataset generation
- **Security Layer** - Input validation, CSRF protection, rate limiting

#### Frontend (`/frontend`)
- **React Application** - Modern SPA with TypeScript support
- **Component Library** - Reusable UI components with error boundaries
- **State Management** - Context-based state with optimized re-rendering
- **Theme System** - Dark/light mode with consistent design tokens

#### Infrastructure (`/terraform`)
- **AWS Lambda** - Serverless compute for scalable data generation
- **CloudFront** - Global CDN for frontend distribution
- **S3 Storage** - Generated file storage with presigned URLs
- **API Gateway** - Managed API endpoint with throttling

## 📡 API Documentation

### Core Endpoints

#### `POST /generate-cur`
Generate FOCUS-compliant CUR data with comprehensive options.

```json
{
  "profile": "Greenfield|Large Business|Enterprise",
  "distribution": "Evenly Distributed|ML-Focused|Data-Intensive|Media-Intensive",
  "row_count": 1000,
  "providers": ["aws", "azure", "gcp"],
  "multi_month": false,
  "trend_options": {
    "monthCount": 6,
    "scenario": "linear|seasonal|stepChange|anomaly",
    "parameters": {
      "growthRate": 10,
      "peakMultiplier": 2.5
    }
  }
}
```

#### `POST /generate-cur-stream`
Stream large datasets efficiently (10K+ rows).

```json
{
  "profile": "Enterprise",
  "distribution": "Data-Intensive", 
  "row_count": 50000,
  "providers": ["aws"]
}
```

#### Response Format
```json
{
  "message": "FOCUS data generated successfully!",
  "downloadUrl": "https://presigned-s3-url...",
  "fileSize": "2 files",
  "generationTime": "2-3 seconds",
  "summary": {
    "totalRows": 2000,
    "providers": ["aws", "azure"],
    "dateRange": "2025-01 to 2025-06"
  }
}
```

### Error Handling
All API errors include correlation IDs for debugging:

```json
{
  "error": true,
  "error_id": "a1b2c3d4",
  "message": "Validation failed for column 'BilledCost'",
  "type": "ValidationError",
  "details": {
    "column": "BilledCost",
    "constraint": "must_be_positive"
  }
}
```

## ⚙️ Configuration

### Environment Variables

#### Backend Configuration
```bash
# API Settings
API_HOST=0.0.0.0
API_PORT=8000
ENVIRONMENT=development|production
DEBUG=true

# Security
SECRET_KEY=your-secret-key
CSRF_SECRET_KEY=your-csrf-secret
CORS_ORIGINS=http://localhost:3000

# Storage
S3_BUCKET_NAME=your-bucket-name
S3_PUBLIC_READ=false

# Rate Limiting
REDIS_URL=redis://localhost:6379
RATE_LIMIT_PER_MINUTE=10
RATE_LIMIT_PER_HOUR=100
RATE_LIMIT_PER_DAY=1000

# Generation Limits
MAX_FILE_SIZE_MB=100
MAX_GENERATION_TIMEOUT=300
```

#### Frontend Configuration
```bash
# API Endpoint
REACT_APP_API_URL=http://localhost:8000

# Feature Flags
REACT_APP_ENABLE_STREAMING=true
REACT_APP_ENABLE_TRENDS=true
```

### Production Configuration

For production deployments, ensure:
- Redis cluster for rate limiting
- S3 bucket with proper IAM policies
- CloudWatch logging enabled
- Secrets stored in AWS Secrets Manager

## 🔧 Development

### Project Structure
```
FOCUS-generator/
├── backend/                 # FastAPI backend
│   ├── exceptions.py       # Custom exception hierarchy
│   ├── error_handler.py    # Centralized error handling
│   ├── retry_utils.py      # Retry logic and circuit breakers
│   ├── validation.py       # Input validation and sanitization
│   ├── models.py          # Pydantic data models
│   ├── main.py           # FastAPI application
│   └── ...
├── frontend/               # React frontend
│   ├── src/
│   │   ├── components/   # Reusable UI components
│   │   ├── hooks/       # Custom React hooks
│   │   ├── contexts/    # React context providers
│   │   └── ...
├── terraform/             # Infrastructure as Code
├── .github/workflows/    # CI/CD pipelines
└── requirements.txt     # Python dependencies
```

### Development Workflow

1. **Feature Development**
   ```bash
   git checkout -b feature/your-feature-name
   # Make changes
   git commit -m "feat: add your feature"
   git push origin feature/your-feature-name
   ```

2. **Testing**
   ```bash
   # Backend tests
   cd backend
   pytest

   # Frontend tests
   cd frontend
   npm test

   # Integration tests
   npm run test:integration
   ```

3. **Code Quality**
   ```bash
   # Python formatting
   black backend/
   isort backend/

   # JavaScript formatting
   cd frontend && npm run format

   # Type checking
   mypy backend/
   cd frontend && npm run type-check
   ```

### Adding New Features

#### Backend
1. Create custom exceptions in `exceptions.py`
2. Add validation in `models.py` 
3. Implement business logic with error handling
4. Add comprehensive tests
5. Update API documentation

#### Frontend
1. Create components with error boundaries
2. Add memoization for performance
3. Implement proper loading states
4. Add comprehensive error handling
5. Update component documentation

## 🚀 Deployment

### AWS Lambda Deployment

```bash
# Build and deploy with Terraform
cd terraform
terraform init
terraform plan -var-file="environments/production.tfvars"
terraform apply
```

### Docker Deployment

```bash
# Build production image
docker build -t focus-generator .

# Run with environment variables
docker run -p 8000:8000 \
  -e ENVIRONMENT=production \
  -e REDIS_URL=redis://your-redis:6379 \
  focus-generator
```

### Manual Deployment

```bash
# Install dependencies
pip install -r requirements.txt
cd frontend && npm install && npm run build

# Start production server
gunicorn backend.main:app --host 0.0.0.0 --port 8000
```

## 🔍 Monitoring and Observability

### Health Checks
- `GET /health` - Application health status
- `GET /metrics` - Prometheus metrics (when enabled)

### Logging
All logs include correlation IDs and structured data:
```json
{
  "timestamp": "2025-01-20T10:30:00Z",
  "level": "INFO",
  "message": "Generate CUR request",
  "correlation_id": "a1b2c3d4",
  "context": {
    "profile": "Enterprise",
    "row_count": 10000,
    "providers": ["aws"]
  }
}
```

### Error Tracking
- Structured error responses with correlation IDs
- Centralized error logging with context
- Rate limit monitoring and alerting

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Setup
1. Fork the repository
2. Create a feature branch
3. Make your changes with tests
4. Submit a pull request

### Code Standards
- Python: Black formatting, type hints, docstrings
- JavaScript: Prettier formatting, JSDoc comments
- All code must pass CI checks
- Test coverage > 80%

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Original project by [wjesseclements](https://github.com/wjesseclements)
- FOCUS specification by [FinOps Foundation](https://www.finops.org/)
- Built with [FastAPI](https://fastapi.tiangolo.com/) and [React](https://reactjs.org/)

## 📞 Support

- 📚 [Documentation](https://github.com/wjesseclements/FOCUS-generator/wiki)
- 🐛 [Issue Tracker](https://github.com/wjesseclements/FOCUS-generator/issues)
- 💬 [Discussions](https://github.com/wjesseclements/FOCUS-generator/discussions)

---

**Made with ❤️ for the FinOps community**