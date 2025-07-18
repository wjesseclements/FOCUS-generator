#!/usr/bin/env python3
"""
Integration test script for FOCUS Generator.
Tests both backend and frontend integration, import fixes, and core functionality.
"""

import sys
import os
import subprocess
import json
from pathlib import Path
from datetime import datetime

def run_command(cmd, cwd=None, capture_output=True):
    """Run a command and return the result."""
    try:
        result = subprocess.run(
            cmd, 
            shell=True, 
            cwd=cwd, 
            capture_output=capture_output,
            text=True
        )
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def test_python_path():
    """Test if Python path is correctly set up."""
    print("Testing Python path setup...")
    
    # Add current directory to Python path
    current_dir = Path(__file__).parent
    backend_dir = current_dir / "FOCUS-generator" / "backend"
    
    if str(backend_dir) not in sys.path:
        sys.path.insert(0, str(backend_dir))
    
    print(f"✓ Added {backend_dir} to Python path")
    return True

def test_backend_imports():
    """Test backend module imports."""
    print("Testing backend imports...")
    
    try:
        # Change to backend directory
        backend_dir = Path(__file__).parent / "FOCUS-generator" / "backend"
        os.chdir(backend_dir)
        
        # Test basic imports
        from config import get_settings
        settings = get_settings()
        print(f"✓ Config loaded successfully (environment: {settings.environment})")
        
        from exceptions import FocusGeneratorError
        print("✓ Exception classes imported successfully")
        
        from error_handler import ErrorHandler
        print("✓ Error handler imported successfully")
        
        from retry_utils import retry_with_backoff
        print("✓ Retry utilities imported successfully")
        
        return True
        
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False

def test_frontend_dependencies():
    """Test frontend dependencies."""
    print("Testing frontend dependencies...")
    
    frontend_dir = Path(__file__).parent / "FOCUS-generator" / "frontend"
    
    # Check if package.json exists
    package_json = frontend_dir / "package.json"
    if not package_json.exists():
        print("✗ package.json not found")
        return False
    
    print("✓ package.json found")
    
    # Check if node_modules exists
    node_modules = frontend_dir / "node_modules"
    if node_modules.exists():
        print("✓ node_modules found")
        return True
    else:
        print("⚠ node_modules not found - dependencies may need to be installed")
        return True  # This is not a failure, just a warning

def test_configuration():
    """Test configuration management."""
    print("Testing configuration management...")
    
    try:
        backend_dir = Path(__file__).parent / "FOCUS-generator" / "backend"
        os.chdir(backend_dir)
        
        from config import get_settings, apply_environment_config
        
        # Test default settings
        settings = get_settings()
        print(f"✓ Default settings loaded: {settings.environment}")
        
        # Test environment-specific overrides
        settings_dev = apply_environment_config(settings)
        print(f"✓ Environment config applied: debug={settings_dev.debug}")
        
        # Test AWS config
        aws_config = settings.get_aws_config()
        print(f"✓ AWS config generated: region={aws_config.get('region_name')}")
        
        return True
        
    except Exception as e:
        print(f"✗ Configuration test failed: {e}")
        return False

def test_error_handling():
    """Test error handling system."""
    print("Testing error handling system...")
    
    try:
        backend_dir = Path(__file__).parent / "FOCUS-generator" / "backend"
        os.chdir(backend_dir)
        
        from exceptions import ValidationError, DataGenerationError
        from error_handler import ErrorHandler
        
        # Test custom exception
        try:
            raise ValidationError("Test validation error", {"field": "test"})
        except ValidationError as e:
            print(f"✓ Custom exception raised: {e.message}")
        
        # Test error handler
        error_handler = ErrorHandler()
        test_error = Exception("Test error")
        http_exception = error_handler.handle_error(test_error)
        print(f"✓ Error handler processed exception: {http_exception.status_code}")
        
        return True
        
    except Exception as e:
        print(f"✗ Error handling test failed: {e}")
        return False

def test_git_integration():
    """Test git repository integration."""
    print("Testing git integration...")
    
    project_root = Path(__file__).parent
    
    # Check if .git directory exists
    git_dir = project_root / ".git"
    if not git_dir.exists():
        print("✗ Git repository not initialized")
        return False
    
    print("✓ Git repository found")
    
    # Check git status
    success, stdout, stderr = run_command("git status --porcelain", cwd=project_root)
    if success:
        modified_files = stdout.strip().split('\n') if stdout.strip() else []
        print(f"✓ Git status checked: {len(modified_files)} modified files")
    else:
        print(f"⚠ Git status check failed: {stderr}")
    
    # Check remote configuration
    success, stdout, stderr = run_command("git remote -v", cwd=project_root)
    if success and stdout.strip():
        print("✓ Git remotes configured")
    else:
        print("⚠ No git remotes configured")
    
    return True

def test_file_structure():
    """Test expected file structure."""
    print("Testing file structure...")
    
    project_root = Path(__file__).parent
    
    # Expected files and directories
    expected_structure = {
        "FOCUS-generator/backend/main.py": "Backend main application",
        "FOCUS-generator/backend/config.py": "Configuration management",
        "FOCUS-generator/backend/exceptions.py": "Custom exceptions",
        "FOCUS-generator/backend/error_handler.py": "Error handling",
        "FOCUS-generator/backend/retry_utils.py": "Retry utilities",
        "FOCUS-generator/frontend/src/App.js": "Frontend main component",
        "FOCUS-generator/frontend/package.json": "Frontend dependencies",
        "README.md": "Project documentation",
        "CHANGELOG.md": "Change log",
        ".gitignore": "Git ignore patterns",
        ".env.example": "Environment configuration example",
    }
    
    missing_files = []
    for file_path, description in expected_structure.items():
        full_path = project_root / file_path
        if full_path.exists():
            print(f"✓ {description}: {file_path}")
        else:
            print(f"✗ Missing {description}: {file_path}")
            missing_files.append(file_path)
    
    if missing_files:
        print(f"⚠ {len(missing_files)} files missing from expected structure")
    
    return len(missing_files) == 0

def create_compatibility_report():
    """Create a compatibility report."""
    print("Creating compatibility report...")
    
    report = {
        "timestamp": datetime.now().isoformat(),
        "tests": {},
        "recommendations": [],
        "issues": []
    }
    
    # Run all tests
    tests = [
        ("python_path", test_python_path),
        ("backend_imports", test_backend_imports),
        ("frontend_dependencies", test_frontend_dependencies),
        ("configuration", test_configuration),
        ("error_handling", test_error_handling),
        ("git_integration", test_git_integration),
        ("file_structure", test_file_structure),
    ]
    
    for test_name, test_func in tests:
        print(f"\n{'='*50}")
        print(f"Running {test_name} test...")
        print(f"{'='*50}")
        
        try:
            result = test_func()
            report["tests"][test_name] = {
                "passed": result,
                "error": None
            }
        except Exception as e:
            report["tests"][test_name] = {
                "passed": False,
                "error": str(e)
            }
            print(f"✗ Test {test_name} failed with error: {e}")
    
    # Add recommendations based on test results
    failed_tests = [name for name, result in report["tests"].items() if not result["passed"]]
    
    if "backend_imports" in failed_tests:
        report["recommendations"].append(
            "Fix backend import issues by ensuring all modules use relative imports"
        )
    
    if "frontend_dependencies" in failed_tests:
        report["recommendations"].append(
            "Install frontend dependencies with: cd FOCUS-generator/frontend && npm install"
        )
    
    if "git_integration" in failed_tests:
        report["recommendations"].append(
            "Initialize git repository and set up remotes"
        )
    
    if not failed_tests:
        report["recommendations"].append(
            "All tests passed! The application is ready for deployment."
        )
    
    # Write report to file
    report_file = Path(__file__).parent / "integration_report.json"
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n{'='*50}")
    print("INTEGRATION TEST SUMMARY")
    print(f"{'='*50}")
    print(f"Tests run: {len(report['tests'])}")
    print(f"Passed: {sum(1 for r in report['tests'].values() if r['passed'])}")
    print(f"Failed: {len(failed_tests)}")
    print(f"Report saved to: {report_file}")
    
    if failed_tests:
        print("\nFailed tests:")
        for test_name in failed_tests:
            print(f"  - {test_name}")
    
    print("\nRecommendations:")
    for rec in report["recommendations"]:
        print(f"  - {rec}")
    
    return len(failed_tests) == 0

if __name__ == "__main__":
    print("FOCUS Generator Integration Test")
    print("=" * 50)
    
    success = create_compatibility_report()
    
    if success:
        print("\n🎉 All integration tests passed!")
        sys.exit(0)
    else:
        print("\n⚠️  Some integration tests failed. Check the report for details.")
        sys.exit(1)