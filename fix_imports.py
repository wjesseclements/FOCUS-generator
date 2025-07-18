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
    
    changes_made = False
    
    # Pattern 1: Fix backend.module imports to relative imports  
    pattern1 = r'from backend\.([a-zA-Z_][a-zA-Z0-9_]*) import'
    replacement1 = r'from \1 import'
    
    matches1 = re.findall(pattern1, content)
    if matches1:
        content = re.sub(pattern1, replacement1, content)
        print(f"  Fixed backend.module imports: {matches1}")
        changes_made = True
    
    # Pattern 2: Fix relative imports to work in CI (for main.py specifically)
    if file_path.name == 'main.py':
        # Convert relative imports to absolute imports that work in CI
        relative_patterns = [
            (r'from \.([a-zA-Z_][a-zA-Z0-9_]*) import', r'from \1 import'),
        ]
        
        for pattern, replacement in relative_patterns:
            matches = re.findall(pattern, content)
            if matches:
                content = re.sub(pattern, replacement, content)
                print(f"  Fixed relative imports: {matches}")
                changes_made = True
    
    # Pattern 3: Ensure proper module structure for CI environment
    # Add Python path setup if needed
    if file_path.name == 'main.py' and 'sys.path' not in content:
        # Add path setup at the top of main.py
        imports_section = content.split('\n')
        insert_index = 0
        
        # Find where to insert the path setup
        for i, line in enumerate(imports_section):
            if line.strip().startswith('import ') or line.strip().startswith('from '):
                insert_index = i
                break
        
        path_setup = """
import sys
import os
from pathlib import Path

# Add backend src directory to Python path for CI compatibility
backend_src = Path(__file__).parent
if str(backend_src) not in sys.path:
    sys.path.insert(0, str(backend_src))
"""
        
        imports_section.insert(insert_index, path_setup)
        content = '\n'.join(imports_section)
        print("  Added Python path setup for CI compatibility")
        changes_made = True
    
    if changes_made:
        # Write back to file
        with open(file_path, 'w') as f:
            f.write(content)
        
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