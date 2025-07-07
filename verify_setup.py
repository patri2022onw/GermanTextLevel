#!/usr/bin/env python3
"""
verify_setup.py - Quick verification that the project is set up correctly
"""

import os
import sys
from pathlib import Path
import pandas as pd

def check_setup():
    """Verify the project setup"""
    print("🔍 German Language Analyzer - Setup Verification")
    print("=" * 50)
    
    # Check current directory
    current_dir = Path.cwd()
    print(f"\n📍 Current directory: {current_dir}")
    
    issues = []
    
    # Check vocabulary directory
    print("\n📁 Checking vocabulary directory...")
    vocab_dir = Path("vocabulary")
    if vocab_dir.exists() and vocab_dir.is_dir():
        print("✅ vocabulary/ directory exists")
        
        # Check individual vocabulary files
        expected_files = {
            'A1.csv': 'A1',
            'A2.csv': 'A2', 
            'B1.csv': 'B1',
            'B2.csv': 'B2',
            'C1_withduplicates.csv': 'C1'
        }
        
        for filename, level in expected_files.items():
            filepath = vocab_dir / filename
            if filepath.exists():
                try:
                    df = pd.read_csv(filepath)
                    print(f"  ✅ {filename:<25} ({len(df)} words)")
                except Exception as e:
                    print(f"  ❌ {filename:<25} (error reading: {e})")
                    issues.append(f"Cannot read {filename}")
            else:
                print(f"  ❌ {filename:<25} (missing)")
                issues.append(f"Missing {filename}")
    else:
        print("❌ vocabulary/ directory not found")
        issues.append("vocabulary/ directory missing")
    
    # Check stopwords file
    print("\n📄 Checking stopwords file...")
    stopwords_file = Path("german_stopwords_plain.txt")
    if stopwords_file.exists():
        with open(stopwords_file, 'r', encoding='utf-8') as f:
            lines = [line.strip() for line in f if line.strip() and not line.startswith(';')]
        print(f"✅ german_stopwords_plain.txt exists ({len(lines)} stopwords)")
    else:
        print("❌ german_stopwords_plain.txt not found")
        issues.append("german_stopwords_plain.txt missing")
    
    # Check Python files
    print("\n🐍 Checking Python files...")
    python_files = ['app.py', 'translation_service.py', 'check_files.py']
    for pyfile in python_files:
        if Path(pyfile).exists():
            print(f"  ✅ {pyfile}")
        else:
            print(f"  ❌ {pyfile} (missing)")
            issues.append(f"{pyfile} missing")
    
    # Check requirements
    print("\n📦 Checking requirements...")
    if Path("requirements.txt").exists():
        print("✅ requirements.txt exists")
    else:
        print("❌ requirements.txt not found")
        issues.append("requirements.txt missing")
        
    if Path("requirements-python312.txt").exists():
        print("✅ requirements-python312.txt exists (for Python 3.12+)")
    
    # Check .streamlit directory
    print("\n⚙️ Checking Streamlit configuration...")
    streamlit_dir = Path(".streamlit")
    if streamlit_dir.exists():
        print("✅ .streamlit/ directory exists")
        
        if (streamlit_dir / "config.toml").exists():
            print("  ✅ config.toml exists")
        else:
            print("  ❌ config.toml missing")
            issues.append(".streamlit/config.toml missing")
            
        if (streamlit_dir / "secrets.toml").exists():
            print("  ✅ secrets.toml exists")
        elif (streamlit_dir / "secrets.toml.template").exists():
            print("  ⚠️  secrets.toml.template exists (copy to secrets.toml and add API keys)")
        else:
            print("  ❌ No secrets configuration found")
    else:
        print("❌ .streamlit/ directory not found")
        issues.append(".streamlit/ directory missing")
    
    # Summary
    print("\n" + "=" * 50)
    if not issues:
        print("✅ All files are in place! Ready to run:")
        print("\n  streamlit run app.py")
        print("\nOptional: Add API keys to .streamlit/secrets.toml for AI features")
        return True
    else:
        print(f"❌ Found {len(issues)} issue(s):\n")
        for issue in issues:
            print(f"  • {issue}")
        print("\nPlease fix these issues before running the app.")
        return False

if __name__ == "__main__":
    success = check_setup()
    sys.exit(0 if success else 1)
