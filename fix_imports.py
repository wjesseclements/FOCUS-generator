#!/usr/bin/env python3
"""
Script to fix import issues in the FOCUS Generator backend.
Converts absolute imports to relative imports for local modules.
"""

import os
import re
from pathlib import Path

def fix_imports_in_file(file_path):
    """Fix imports in a single file."""
    print(f"Fixing imports in {file_path}")
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Pattern to match backend imports
    pattern = r'from backend\.([a-zA-Z_][a-zA-Z0-9_]*) import'
    replacement = r'from \1 import'
    
    # Replace imports
    new_content = re.sub(pattern, replacement, content)
    
    # Count replacements
    matches = re.findall(pattern, content)
    if matches:
        print(f"  Fixed {len(matches)} imports: {matches}")
        
        # Write back to file
        with open(file_path, 'w') as f:
            f.write(new_content)
        
        return True
    else:
        print("  No imports to fix")
        return False

def fix_all_imports():
    """Fix imports in all Python files in the backend directory."""
    backend_dir = Path(__file__).parent / "backend" / "src"
    
    if not backend_dir.exists():
        print(f"Backend directory not found: {backend_dir}")
        return
    
    python_files = list(backend_dir.glob("*.py"))
    fixed_files = []
    
    for file_path in python_files:
        if file_path.name.startswith("test_"):
            continue  # Skip test files for now
        
        if fix_imports_in_file(file_path):
            fixed_files.append(file_path.name)
    
    print(f"\nFixed imports in {len(fixed_files)} files:")
    for file_name in fixed_files:
        print(f"  - {file_name}")

if __name__ == "__main__":
    print("FOCUS Generator Import Fix")
    print("=" * 30)
    fix_all_imports()
    print("\nDone!")