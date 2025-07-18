# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Common Development Commands

### Backend Development
```bash
# Activate virtual environment (from project root)
cd FOCUS-generator
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install backend dependencies
pip install -r requirements.txt

# Run backend server (from backend directory)
cd backend
python main.py  # Starts FastAPI server on http://localhost:8000

# Run backend tests
pytest -v  # Run all tests
pytest test_validate_cur.py -v  # Run specific test file
pytest -k "test_generator" -v  # Run tests matching pattern

# Lint Python code
flake8 backend/  # Check for style issues
```

### Frontend Development
```bash
# Install frontend dependencies (from frontend directory)
cd FOCUS-generator/frontend
npm install

# Run frontend development server
npm start  # Starts React app on http://localhost:3000

# Build for production
npm run build  # Creates optimized build in frontend/build/

# Run frontend tests
npm test  # Run in watch mode
npm test -- --coverage  # Generate coverage report
npm test -- --watchAll=false  # Run once and exit
```

### Infrastructure Deployment
```bash
# Deploy with Terraform (from terraform directory)
cd FOCUS-generator/terraform
terraform init
terraform plan -var-file=environments/staging.tfvars
terraform apply -var-file=environments/production.tfvars
```

## High-Level Architecture

### System Overview
The FOCUS Generator is a full-stack application for generating synthetic FOCUS-compliant Cost and Usage Reports (CURs) for cloud billing data. It consists of:

1. **FastAPI Backend (Python)**: Handles data generation logic with 50 specialized column generators, each implementing the FOCUS specification requirements for their respective columns.

2. **React Frontend**: Provides an intuitive UI for configuring generation parameters, with real-time visualization of generated data characteristics.

3. **AWS Infrastructure**: Serverless deployment using Lambda functions, API Gateway, S3 storage, and CloudFront CDN.

### Key Architectural Patterns

#### Generator Factory Pattern
The backend uses a factory pattern (`ColumnGeneratorFactory`) to manage 50+ specialized generators. Each generator inherits from `ColumnGenerator` base class and implements column-specific logic:

- **Context-Aware Generation**: Generators receive a `GenerationContext` object containing all parameters and previously generated columns, enabling cross-column relationships.
- **Multi-Cloud Support**: Generators adapt output based on selected cloud provider (AWS, Azure, GCP).
- **Profile-Based Generation**: Different user profiles (Startup, Enterprise, Data-Heavy, ML/AI) influence cost distributions and service selections.

#### API Structure
- `/api/generate-cur`: Single-file CUR generation
- `/api/generate-multi-month`: Multi-month trend generation with configurable growth patterns
- `/api/download/{file_id}`: Secure file download with expiration

#### Frontend State Management
- Custom hooks (`useFocusGenerator`) manage API interactions
- Context providers handle theme and global state
- Component-based architecture with clear separation of concerns

### Critical Files and Their Roles

**Backend Core Files:**
- `backend/column_generators.py`: All 50 specialized column generators
- `backend/curGen.py`: Main generation orchestration logic
- `backend/validate_cur.py`: FOCUS compliance validation
- `backend/generator_factory.py`: Factory pattern implementation
- `backend/lambda_handler.py`: AWS Lambda integration

**Frontend Key Components:**
- `frontend/src/hooks/useFocusGenerator.js`: Core API integration hook
- `frontend/src/components/sections/`: Main UI sections
- `frontend/src/App.js`: Application root and routing

**Infrastructure:**
- `terraform/lambda.tf`: Lambda function configuration
- `terraform/api_gateway.tf`: REST API setup
- `terraform/cloudfront.tf`: CDN distribution

### Data Flow
1. User configures parameters in React UI
2. Frontend sends POST request to FastAPI backend
3. Backend validates input and creates GenerationContext
4. ColumnGeneratorFactory creates appropriate generators
5. Generators produce FOCUS-compliant data with cross-column relationships
6. Data is validated and saved as CSV
7. File URL returned to frontend for download

### Testing Strategy
- **Unit Tests**: Each generator has dedicated tests validating output format and relationships
- **Integration Tests**: End-to-end generation and validation tests
- **FOCUS Compliance Tests**: Automated validation against FOCUS specification rules