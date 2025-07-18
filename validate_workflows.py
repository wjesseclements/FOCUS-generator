#!/usr/bin/env python3
"""
Validate GitHub Actions workflows for deployment readiness.
"""

import os
import json
import yaml
from pathlib import Path
from typing import Dict, List, Tuple

def check_file_exists(file_path: str) -> Tuple[bool, str]:
    """Check if a required file exists."""
    path = Path(file_path)
    if path.exists():
        return True, f"✅ {file_path} exists"
    else:
        return False, f"❌ {file_path} is missing"

def check_workflow_files() -> List[Tuple[bool, str]]:
    """Check if workflow files exist and are valid."""
    results = []
    
    workflow_dir = Path(".github/workflows")
    if not workflow_dir.exists():
        results.append((False, "❌ .github/workflows directory is missing"))
        return results
    
    results.append((True, "✅ .github/workflows directory exists"))
    
    # Check for CI workflow
    ci_file = workflow_dir / "ci.yml"
    if ci_file.exists():
        try:
            with open(ci_file, 'r') as f:
                yaml.safe_load(f)
            results.append((True, "✅ ci.yml exists and is valid YAML"))
        except yaml.YAMLError as e:
            results.append((False, f"❌ ci.yml has invalid YAML: {e}"))
    else:
        results.append((False, "❌ ci.yml is missing"))
    
    # Check for deploy workflow
    deploy_file = workflow_dir / "deploy.yaml"
    if deploy_file.exists():
        try:
            with open(deploy_file, 'r') as f:
                yaml.safe_load(f)
            results.append((True, "✅ deploy.yaml exists and is valid YAML"))
        except yaml.YAMLError as e:
            results.append((False, f"❌ deploy.yaml has invalid YAML: {e}"))
    else:
        results.append((False, "❌ deploy.yaml is missing"))
    
    return results

def check_required_files() -> List[Tuple[bool, str]]:
    """Check for required files for deployment."""
    required_files = [
        "backend/requirements.txt",
        "backend/src/main.py",
        "backend/src/lambda_handler.py",
        "frontend/package.json",
        "frontend/src/App.js",
        ".flake8",
        ".gitignore",
        ".env.example"
    ]
    
    results = []
    for file_path in required_files:
        results.append(check_file_exists(file_path))
    
    return results

def check_dependencies() -> List[Tuple[bool, str]]:
    """Check if dependencies are properly configured."""
    results = []
    
    # Check requirements.txt
    if Path("backend/requirements.txt").exists():
        with open("backend/requirements.txt", 'r') as f:
            content = f.read()
            required_packages = ["fastapi", "pandas", "boto3", "mangum", "redis", "pydantic"]
            missing = []
            for package in required_packages:
                if package not in content:
                    missing.append(package)
            
            if missing:
                results.append((False, f"❌ Missing required packages in requirements.txt: {', '.join(missing)}"))
            else:
                results.append((True, "✅ All required packages found in requirements.txt"))
    else:
        results.append((False, "❌ backend/requirements.txt is missing"))
    
    # Check package.json
    package_json_path = Path("frontend/package.json")
    if package_json_path.exists():
        with open(package_json_path, 'r') as f:
            package_data = json.load(f)
            if "scripts" in package_data:
                required_scripts = ["start", "build", "test"]
                missing_scripts = [s for s in required_scripts if s not in package_data["scripts"]]
                if missing_scripts:
                    results.append((False, f"❌ Missing scripts in package.json: {', '.join(missing_scripts)}"))
                else:
                    results.append((True, "✅ All required scripts found in package.json"))
            else:
                results.append((False, "❌ No scripts section in package.json"))
    else:
        results.append((False, "❌ package.json is missing"))
    
    return results

def check_secrets_needed() -> List[str]:
    """List the GitHub secrets needed for deployment."""
    return [
        "AWS_ACCESS_KEY_ID",
        "AWS_SECRET_ACCESS_KEY",
        "PRODUCTION_API_URL",
        "REDIS_URL",
        "SECRET_KEY",
        "CSRF_SECRET_KEY",
        "CLOUDFRONT_DISTRIBUTION_ID (optional)"
    ]

def generate_report() -> None:
    """Generate a comprehensive validation report."""
    print("=" * 60)
    print("GitHub Actions Workflow Validation Report")
    print("=" * 60)
    print()
    
    all_checks_passed = True
    
    # Check workflow files
    print("Workflow Files:")
    workflow_results = check_workflow_files()
    for passed, message in workflow_results:
        print(f"  {message}")
        if not passed:
            all_checks_passed = False
    print()
    
    # Check required files
    print("Required Files:")
    file_results = check_required_files()
    for passed, message in file_results:
        print(f"  {message}")
        if not passed:
            all_checks_passed = False
    print()
    
    # Check dependencies
    print("Dependencies:")
    dep_results = check_dependencies()
    for passed, message in dep_results:
        print(f"  {message}")
        if not passed:
            all_checks_passed = False
    print()
    
    # List required secrets
    print("Required GitHub Secrets:")
    for secret in check_secrets_needed():
        print(f"  - {secret}")
    print()
    
    # Final verdict
    print("=" * 60)
    if all_checks_passed:
        print("✅ All checks passed! Workflows are ready for deployment.")
        print()
        print("Next steps:")
        print("1. Ensure all GitHub secrets are configured in your repository")
        print("2. Update AWS resource names in deploy.yaml if needed")
        print("3. Commit and push changes to trigger workflows")
        print("4. Monitor workflow runs in GitHub Actions tab")
    else:
        print("❌ Some checks failed. Please fix the issues above before deployment.")
        print()
        print("Common fixes:")
        print("1. Run 'pip freeze > requirements.txt' to generate requirements")
        print("2. Ensure all backend files use relative imports")
        print("3. Check that frontend/package.json has all required scripts")
        print("4. Verify all files are in the correct locations")
    print("=" * 60)

if __name__ == "__main__":
    # Try to import yaml, install if not available
    try:
        import yaml
    except ImportError:
        print("Installing PyYAML for workflow validation...")
        os.system("pip install pyyaml")
        import yaml
    
    generate_report()