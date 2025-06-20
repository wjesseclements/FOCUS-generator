# Local Testing Guide for FOCUS Generator

This guide will help you test the FOCUS Generator locally before deploying to AWS.

## 🏠 **Local Testing Overview**

We'll test:
1. **Backend API** - Lambda function locally
2. **Frontend Application** - React app with local API
3. **Test Suites** - All automated tests
4. **CI Pipeline** - GitHub Actions (via pull request)

## 🚀 **Step 1: Test Backend Locally**

### **1.1 Set Up Python Environment**

```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r ../requirements.txt

# Install additional testing dependencies
pip install pytest pytest-cov black flake8 bandit safety
```

### **1.2 Run Backend Tests**

```bash
# Run all backend tests
pytest -v

# Run tests with coverage
pytest --cov=. --cov-report=html --cov-report=term-missing

# Run specific test files
pytest test_generators.py -v
pytest test_main.py -v
pytest test_curGen.py -v
```

**Expected output:**
```
=============================== test session starts ===============================
collected 50+ items

test_generators.py::TestChargeGenerator::test_supported_columns PASSED
test_generators.py::TestChargeGenerator::test_charge_category_generation PASSED
...
=============================== 50+ passed in 2.34s ===============================
```

### **1.3 Test Code Quality**

```bash
# Format code with Black
black backend/ --diff  # See what would change
black backend/         # Apply formatting

# Lint code with Flake8
flake8 backend/ --max-line-length=100

# Security scan with Bandit
bandit -r backend/

# Check dependencies for vulnerabilities
safety check
```

### **1.4 Start Backend Server Locally**

```bash
# Start the FastAPI server (with new improvements)
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload

# Server will start at: http://localhost:8000
# You'll see structured JSON logs in the terminal
```

### **1.5 Test Backend API Endpoints**

Open a new terminal and test the API:

```bash
# Test health endpoint
curl http://localhost:8000/health

# Test root endpoint
curl http://localhost:8000/

# Test FOCUS generation
curl -X POST http://localhost:8000/generate-cur \
  -H "Content-Type: application/json" \
  -d '{
    "profile": "Greenfield",
    "distribution": "Evenly Distributed",
    "row_count": 5
  }'
```

**Expected responses:**
- Health: `{"status": "healthy"}`
- Root: API information JSON
- Generate: JSON with `message` and download URL

### **1.6 Test New Rate Limiting & Logging Features**

```bash
# Test rate limiting headers (check response headers)
curl -v http://localhost:8000/health

# You should see rate limit headers like:
# X-RateLimit-Limit-Minute: 10
# X-RateLimit-Limit-Hour: 100
# X-RateLimit-Remaining-Minute: 9
# X-RateLimit-Remaining-Hour: 99

# Test rate limiting by making multiple requests quickly
for i in {1..12}; do
  echo "Request $i:"
  curl -s -w "Status: %{http_code}\n" http://localhost:8000/generate-cur \
    -H "Content-Type: application/json" \
    -d '{"profile": "Greenfield", "distribution": "Evenly Distributed", "row_count": 5}'
  sleep 1
done

# After 10 requests, you should see HTTP 429 (Too Many Requests)
```

**Check Structured Logs:**
Look at your terminal running the backend - you'll see JSON formatted logs like:
```json
{
  "timestamp": "2025-06-19T20:23:55.424955",
  "level": "INFO", 
  "logger": "backend.main",
  "message": "Starting FOCUS data generation",
  "row_count": 5,
  "profile": "Greenfield"
}
```

## 🎨 **Step 2: Test Frontend Locally**

### **2.1 Set Up Frontend Environment**

```bash
cd frontend

# Install dependencies
npm install

# Verify all dependencies installed correctly
npm ls
```

### **2.2 Run Frontend Tests**

```bash
# Run all frontend tests
npm test -- --watchAll=false

# Run tests with coverage
npm test -- --coverage --watchAll=false

# Run tests in watch mode (for development)
npm test
```

**Expected output:**
```
PASS src/App.test.js
  App Component
    ✓ renders FOCUS CUR Generator title
    ✓ renders profile and distribution selection buttons
    ✓ updates row count when user types
    ... (14 tests total)

Test Suites: 1 passed, 1 total
Tests:       14 passed, 14 total
```

### **2.3 Start Frontend Development Server**

```bash
# Start React development server
npm start

# Application will open at: http://localhost:3000
```

### **2.4 Test Frontend with Local Backend**

With both servers running:

1. **Open browser** to `http://localhost:3000`
2. **Select a profile** (e.g., "Greenfield")
3. **Select a distribution** (e.g., "Evenly Distributed")
4. **Set row count** (e.g., 10)
5. **Click "Generate CUR"**
6. **Verify download** works

## 🔧 **Step 3: Test Integration Locally**

### **3.1 Full Stack Integration Test**

With both backend and frontend running:

```bash
# Test the complete flow with different combinations
curl -X POST http://localhost:8000/generate-cur \
  -H "Content-Type: application/json" \
  -d '{
    "profile": "Enterprise",
    "distribution": "ML-Focused",
    "row_count": 20
  }'

curl -X POST http://localhost:8000/generate-cur \
  -H "Content-Type: application/json" \
  -d '{
    "profile": "Large Business",
    "distribution": "Data-Intensive",
    "row_count": 15
  }'
```

### **3.2 Test Error Handling**

```bash
# Test invalid profile
curl -X POST http://localhost:8000/generate-cur \
  -H "Content-Type: application/json" \
  -d '{
    "profile": "InvalidProfile",
    "distribution": "Evenly Distributed",
    "row_count": 5
  }'

# Test invalid row count
curl -X POST http://localhost:8000/generate-cur \
  -H "Content-Type: application/json" \
  -d '{
    "profile": "Greenfield",
    "distribution": "Evenly Distributed",
    "row_count": -1
  }'
```

### **3.3 Test FOCUS Validation**

```bash
# Generate a file and validate it
curl -X POST http://localhost:8000/generate-cur \
  -H "Content-Type: application/json" \
  -d '{
    "profile": "Greenfield",
    "distribution": "Evenly Distributed",
    "row_count": 10
  }' | jq '.url' | xargs curl -o test_output.csv

# Check the CSV file
head -5 test_output.csv
wc -l test_output.csv  # Should show 11 lines (header + 10 data rows)
```

## 🧪 **Step 4: Test CI Pipeline (GitHub Actions)**

### **4.1 Create a Test Branch**

```bash
# Create a new branch for testing
git checkout -b test-local-changes

# Make a small change to trigger CI
echo "# Local Testing Complete - $(date)" >> LOCAL_TEST_RESULTS.md

# Commit and push
git add .
git commit -m "test: Verify CI pipeline with local testing results"
git push origin test-local-changes
```

### **4.2 Create Pull Request**

1. Go to GitHub repository
2. Create pull request from `test-local-changes` to `feature/complete-generator-architecture`
3. Watch the CI pipeline run:
   - ✅ Backend tests
   - ✅ Frontend tests
   - ✅ Security scanning
   - ✅ Integration tests
   - ✅ Quality gate

### **4.3 Verify CI Results**

The CI pipeline should:
- Run all tests successfully
- Pass security scans
- Complete integration tests
- Show green checkmarks

## 📊 **Step 5: Performance Testing**

### **5.1 Load Testing (Optional)**

```bash
# Install ab (Apache Bench) if not available
# macOS: brew install httpd
# Ubuntu: sudo apt-get install apache2-utils

# Test API performance
ab -n 100 -c 10 http://localhost:8000/health

# Test FOCUS generation performance
ab -n 10 -c 2 -p post_data.json -T application/json http://localhost:8000/generate-cur
```

Create `post_data.json`:
```json
{
  "profile": "Greenfield",
  "distribution": "Evenly Distributed",
  "row_count": 5
}
```

### **5.2 Memory and CPU Testing**

```bash
# Monitor backend performance
# Start backend with profiling
pip install memory-profiler
python -m memory_profiler main.py

# Or use htop/top to monitor resources while testing
htop
```

## ✅ **Local Testing Checklist**

### **Backend Tests:**
- [ ] All Python tests pass (50+ tests)
- [ ] Code formatting passes (Black)
- [ ] Linting passes (Flake8)
- [ ] Security scan passes (Bandit)
- [ ] Dependencies are secure (Safety)
- [ ] API endpoints respond correctly
- [ ] FOCUS generation works for all profiles

### **Frontend Tests:**
- [ ] All React tests pass (14 tests)
- [ ] Components render correctly
- [ ] User interactions work
- [ ] API integration works
- [ ] Error handling works
- [ ] Form validation works

### **Integration Tests:**
- [ ] Frontend connects to backend
- [ ] File generation and download works
- [ ] Error messages display correctly
- [ ] All profile/distribution combinations work
- [ ] Generated files are valid CSV
- [ ] FOCUS compliance validation passes

### **CI Pipeline Tests:**
- [ ] Pull request triggers CI
- [ ] All CI jobs pass
- [ ] Security scans complete
- [ ] Quality gates pass

## 🐛 **Common Local Testing Issues**

### **Issue 1: Backend won't start**
```bash
# Check Python version
python --version  # Should be 3.9+

# Check dependencies
pip list | grep fastapi
pip list | grep uvicorn

# Try installing individually
pip install fastapi uvicorn
```

### **Issue 2: Frontend tests fail**
```bash
# Clear npm cache
npm cache clean --force

# Delete node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

### **Issue 3: CORS errors**
```bash
# Update backend CORS settings in main.py
# Make sure localhost:3000 is in allowed origins
```

### **Issue 4: File generation fails**
```bash
# Check backend logs for errors
# Verify all generators are working
python -c "from generator_factory import get_generator_factory; print('Factory works!')"
```

## 🎯 **Success Criteria**

✅ **Local testing is successful when:**
- All backend tests pass
- All frontend tests pass  
- API endpoints respond correctly
- Frontend can generate and download files
- CI pipeline passes on pull request
- No security vulnerabilities found
- Performance is acceptable

## 🚀 **Ready for Deployment**

Once all local tests pass, you can proceed with confidence to:
1. Deploy staging environment
2. Configure GitHub variables
3. Test staging deployment
4. Deploy to production

The local testing ensures everything works before spending time on AWS infrastructure!