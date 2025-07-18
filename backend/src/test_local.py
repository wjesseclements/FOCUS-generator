#!/usr/bin/env python3
"""
Local testing script for FOCUS Generator.
This bypasses S3 and saves files locally for testing.
"""

import os
import sys
import tempfile
from datetime import datetime

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from curGen import generate_focus_data
from validate_cur import validate_focus_df

def test_focus_generation(profile="Greenfield", distribution="Evenly Distributed", row_count=5):
    """Test FOCUS data generation locally."""
    print(f"🧪 Testing FOCUS Generation")
    print(f"   Profile: {profile}")
    print(f"   Distribution: {distribution}")
    print(f"   Row Count: {row_count}")
    print()
    
    try:
        # Generate FOCUS data
        print("📊 Generating FOCUS data...")
        df = generate_focus_data(
            profile=profile,
            distribution=distribution,
            row_count=row_count
        )
        
        print(f"✅ Generated {len(df)} rows")
        print(f"   Columns: {len(df.columns)}")
        print()
        
        # Validate the data
        print("🔍 Validating FOCUS compliance...")
        validate_focus_df(df)
        print("✅ FOCUS validation passed")
        print()
        
        # Save to temporary file
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
        df.to_csv(temp_file.name, index=False)
        print(f"💾 Saved to: {temp_file.name}")
        
        # Show sample data
        print("📋 Sample data (first 3 rows):")
        print(df.head(3).to_string())
        print()
        
        # Show column summary
        print("📈 Column Summary:")
        for col in df.columns:
            non_null = df[col].notna().sum()
            print(f"   {col}: {non_null}/{len(df)} non-null values")
        
        return temp_file.name
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_all_combinations():
    """Test all profile and distribution combinations."""
    profiles = ["Greenfield", "Large Business", "Enterprise"]
    distributions = ["Evenly Distributed", "ML-Focused", "Data-Intensive", "Media-Intensive"]
    
    print("🚀 Testing all profile/distribution combinations...")
    print()
    
    results = []
    for profile in profiles:
        for distribution in distributions:
            print(f"Testing: {profile} + {distribution}")
            result = test_focus_generation(profile, distribution, 3)
            results.append((profile, distribution, result is not None))
            print("-" * 50)
    
    # Summary
    print("📊 Test Results Summary:")
    passed = sum(1 for _, _, success in results if success)
    total = len(results)
    print(f"   Passed: {passed}/{total}")
    
    for profile, distribution, success in results:
        status = "✅" if success else "❌"
        print(f"   {status} {profile} + {distribution}")

if __name__ == "__main__":
    print("🏠 FOCUS Generator Local Testing")
    print("=" * 40)
    print()
    
    if len(sys.argv) > 1 and sys.argv[1] == "all":
        test_all_combinations()
    else:
        # Test single combination
        test_focus_generation()