# FOCUS Generator

A comprehensive synthetic data generator for creating FOCUS-compliant Cost and Usage Reports (CURs) to build and test cloud cost dashboards across AWS, Azure, and Google Cloud Platform.

## 🎯 Purpose

The FOCUS Generator helps organizations:
- **Test cost analysis dashboards** without using real sensitive billing data
- **Generate realistic multi-cloud cost scenarios** for development and testing
- **Validate FOCUS compliance** in cost management tools
- **Create demo datasets** for presentations and training
- **Benchmark cost analysis tools** with consistent test data

## 🏗️ Architecture Overview

### System Components

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   React UI      │────▶│  FastAPI Backend │────▶│  S3 Storage     │
│   (Frontend)    │     │  (Python)        │     │  (Generated CSVs)│
└─────────────────┘     └─────────────────┘     └─────────────────┘
        │                        │                        │
        ▼                        ▼                        ▼
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  CloudFront CDN │     │  Lambda Function │     │  API Gateway    │
│  (Production)   │     │  (Serverless)    │     │  (REST API)     │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

### Key Technologies

- **Backend**: Python 3.x, FastAPI, Pandas, Boto3
- **Frontend**: React 18, Tailwind CSS, Framer Motion
- **Infrastructure**: AWS Lambda, API Gateway, S3, CloudFront
- **IaC**: Terraform for infrastructure management
- **Testing**: Pytest (backend), Jest (frontend)

## 🚀 Features

### Data Generation Capabilities

1. **100% FOCUS Column Coverage**
   - All 50 FOCUS specification columns supported
   - Specialized generators for each column type
   - Cross-column relationship validation

2. **Multi-Cloud Support**
   - AWS (Amazon Web Services)
   - Microsoft Azure
   - Google Cloud Platform
   - Provider-specific naming conventions and services

3. **Customization Options**
   - **Profiles**: Startup, Enterprise, Data-Heavy, ML/AI
   - **Distributions**: Balanced, Compute-Heavy, Storage-Heavy, Network-Heavy
   - **Row Count**: 100 to 100,000+ rows
   - **Time Periods**: Single month or multi-month trends

4. **Trend Simulation**
   - Linear growth patterns
   - Seasonal variations
   - Spike scenarios
   - Custom trend parameters

### Technical Features

- **FOCUS Validation**: Built-in validation ensures 100% compliance
- **Rate Limiting**: API protection against abuse
- **CORS Support**: Secure cross-origin requests
- **Error Handling**: Comprehensive error messages
- **Logging**: Structured logging for debugging

## 📁 Project Structure

```
FOCUS-generator/
├── backend/                    # Python FastAPI backend
│   ├── column_generators.py    # Specialized column generators
│   ├── curGen.py              # Main generation logic
│   ├── validate_cur.py        # FOCUS validation
│   ├── main.py                # FastAPI application
│   ├── lambda_handler.py      # AWS Lambda handler
│   └── models.py              # Pydantic models
├── frontend/                   # React frontend
│   ├── src/
│   │   ├── components/        # UI components
│   │   ├── hooks/            # Custom React hooks
│   │   └── contexts/         # React contexts
│   └── public/               # Static assets
├── terraform/                 # Infrastructure as Code
│   ├── main.tf               # Main configuration
│   ├── lambda.tf             # Lambda functions
│   └── cloudfront.tf         # CDN configuration
└── files/                    # Generated CSV storage

```

## 🛠️ Installation & Setup

### Prerequisites

- Python 3.8+
- Node.js 16+
- npm or yarn
- AWS CLI (for deployment)
- Terraform (for infrastructure)

### Backend Setup

```bash
# Navigate to backend directory
cd FOCUS-generator/backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r ../requirements.txt

# Run backend server
python main.py
```

The backend will start on `http://localhost:8000`

### Frontend Setup

```bash
# Navigate to frontend directory
cd FOCUS-generator/frontend

# Install dependencies
npm install

# Start development server
npm start
```

The frontend will start on `http://localhost:3000`

## 🎮 Usage

### Web Interface

1. **Select Profile**: Choose from Startup, Enterprise, Data-Heavy, or ML/AI
2. **Choose Distribution**: Pick service usage distribution pattern
3. **Set Row Count**: Specify number of records to generate
4. **Select Providers**: Choose one or more cloud providers
5. **Configure Trends** (optional): Set up multi-month patterns
6. **Generate**: Click generate to create your FOCUS CUR

### API Usage

```bash
# Generate basic CUR
curl -X POST http://localhost:8000/api/generate-cur \
  -H "Content-Type: application/json" \
  -d '{
    "profile": "startup",
    "distribution": "balanced",
    "row_count": 1000,
    "providers": ["aws"]
  }'

# Generate with trends
curl -X POST http://localhost:8000/api/generate-multi-month \
  -H "Content-Type: application/json" \
  -d '{
    "profile": "enterprise",
    "distribution": "compute_heavy",
    "row_count": 5000,
    "providers": ["aws", "azure"],
    "trend_options": {
      "month_count": 6,
      "scenario": "linear",
      "parameters": {"growth_rate": 0.1}
    }
  }'
```

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest -v
```

### Frontend Tests
```bash
cd frontend
npm test
```

### Validation Tests
```bash
# Test FOCUS compliance
python backend/test_validate_cur.py

# Test generators
python backend/test_generators.py
```

## 📊 Data Quality

### FOCUS Compliance
- All mandatory fields populated
- Conditional field logic implemented
- Cross-column validation rules enforced
- Proper null handling for optional fields

### Realistic Data Patterns
- Industry-standard service names
- Realistic cost distributions
- Proper regional distribution
- Meaningful resource relationships
- Valid timestamp sequences

## 🚀 Deployment

### Local Development
Both frontend and backend can run locally for development and testing.

### Production Deployment
```bash
cd terraform
terraform init
terraform plan -var-file=environments/production.tfvars
terraform apply -var-file=environments/production.tfvars
```

### Environment Variables
Create a `.env` file in the backend directory:
```
ENVIRONMENT=development
DEBUG=True
CORS_ORIGINS=http://localhost:3000
API_KEY=your-api-key-here
```

## 🔒 Security Features

- Rate limiting on API endpoints
- CORS configuration for secure requests
- Input validation on all parameters
- No sensitive data in generated output
- Secure file handling for downloads

## 📈 Performance

- Generates 10,000 rows in ~2 seconds
- Supports up to 100,000 rows per request
- Efficient memory usage with streaming
- Optimized column generators

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License.

## 🆘 Troubleshooting

### Common Issues

1. **Backend won't start**: Check Python version and dependencies
2. **Frontend build errors**: Clear node_modules and reinstall
3. **CORS errors**: Verify CORS_ORIGINS in .env file
4. **Generation timeout**: Reduce row count or use batching

### Getting Help

- Check the documentation in `/docs`
- Review test files for usage examples
- Submit issues on GitHub
- Contact the development team

## 🎯 Roadmap

- [ ] Additional cloud providers (Oracle, IBM)
- [ ] Custom column definitions
- [ ] Export to multiple formats (Parquet, JSON)
- [ ] Advanced anomaly injection
- [ ] Cost optimization recommendations

---

Built with ❤️ for the FinOps community