#!/usr/bin/env python3
"""
check_files.py - Verify all required files are present for deployment
"""

import os
import sys
import pandas as pd
from pathlib import Path

# Define required files with updated paths
REQUIRED_FILES = {
    'vocabulary': {
        'vocabulary/A1.csv': {'min_rows': 500, 'required_columns': ['Lemma']},
        'vocabulary/A2.csv': {'min_rows': 400, 'required_columns': ['Lemma']},
        'vocabulary/B1.csv': {'min_rows': 1000, 'required_columns': ['Lemma']},
        'vocabulary/B2.csv': {'min_rows': 1500, 'required_columns': ['lemma']},  # Note lowercase
        'vocabulary/C1_withduplicates.csv': {'min_rows': 2000, 'required_columns': ['Lemma']}
    },
    'stopwords': {
        'german_stopwords_plain.txt': {'min_lines': 100}
    },
    'application': {
        'app.py': {},
        'requirements.txt': {},
        'translation_service.py': {}
    }
}

def check_file_exists(filepath):
    """Check if a file exists"""
    return os.path.exists(filepath)

def check_csv_file(filepath, requirements):
    """Check if a CSV file meets requirements"""
    try:
        df = pd.read_csv(filepath)
        
        # Check minimum rows
        if 'min_rows' in requirements:
            if len(df) < requirements['min_rows']:
                return False, f"Only {len(df)} rows, need at least {requirements['min_rows']}"
        
        # Check required columns
        if 'required_columns' in requirements:
            missing_cols = []
            for col in requirements['required_columns']:
                if col not in df.columns:
                    missing_cols.append(col)
            
            if missing_cols:
                return False, f"Missing columns: {', '.join(missing_cols)}"
        
        return True, f"✓ {len(df)} rows"
        
    except Exception as e:
        return False, f"Error reading CSV: {str(e)}"

def check_text_file(filepath, requirements):
    """Check if a text file meets requirements"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Count non-empty, non-comment lines
        content_lines = [line for line in lines 
                        if line.strip() and not line.strip().startswith(';')]
        
        if 'min_lines' in requirements:
            if len(content_lines) < requirements['min_lines']:
                return False, f"Only {len(content_lines)} lines, need at least {requirements['min_lines']}"
        
        return True, f"✓ {len(content_lines)} lines"
        
    except Exception as e:
        return False, f"Error reading file: {str(e)}"

def main():
    """Check all required files"""
    print("🔍 German Language Analyzer - File Checker")
    print("=" * 50)
    
    all_good = True
    
    # Check each category
    for category, files in REQUIRED_FILES.items():
        print(f"\n📁 {category.upper()}")
        print("-" * 30)
        
        for filename, requirements in files.items():
            if not check_file_exists(filename):
                print(f"❌ {filename:<30} - NOT FOUND")
                all_good = False
                continue
            
            # Check file contents based on type
            if filename.endswith('.csv'):
                success, message = check_csv_file(filename, requirements)
            elif filename.endswith('.txt') and requirements:
                success, message = check_text_file(filename, requirements)
            else:
                success, message = True, "✓ Exists"
            
            if success:
                print(f"✅ {filename:<30} - {message}")
            else:
                print(f"❌ {filename:<30} - {message}")
                all_good = False
    
    # Summary
    print("\n" + "=" * 50)
    if all_good:
        print("✅ All files present and valid! Ready for deployment.")
        
        # Additional deployment tips
        print("\n📋 Next steps:")
        print("1. Commit all files to your Git repository")
        print("2. Push to GitHub")
        print("3. Deploy on Streamlit Cloud")
        print("4. Configure secrets if using API keys")
        
        return 0
    else:
        print("❌ Some files are missing or invalid.")
        print("\n💡 Tips:")
        print("- Ensure all CSV files have the correct column names")
        print("- Check that file names match exactly (case-sensitive)")
        print("- Verify stopwords file is plain text with one word per line")
        
        return 1

if __name__ == "__main__":
    sys.exit(main())
