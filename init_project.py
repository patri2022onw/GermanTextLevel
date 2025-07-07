#!/usr/bin/env python3
"""
init_project.py - Initialize the German Language Analyzer project
Sets up the correct directory structure and verifies all files
"""

import os
import sys
import subprocess
from pathlib import Path
import shutil

def run_command(cmd):
    """Run a command and return success status"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(result.stdout)
            return True
        else:
            print(f"Error: {result.stderr}")
            return False
    except Exception as e:
        print(f"Error running command: {e}")
        return False

def main():
    """Initialize the project"""
    print("🚀 German Language Analyzer - Project Initialization")
    print("=" * 50)
    print(f"Project directory: {Path.cwd()}")
    
    # Step 1: Create necessary directories
    print("\n📁 Step 1: Creating directory structure...")
    
    directories = ['vocabulary', '.streamlit', 'output', 'logs']
    for dir_name in directories:
        dir_path = Path(dir_name)
        if not dir_path.exists():
            dir_path.mkdir(parents=True)
            print(f"  ✅ Created {dir_name}/")
        else:
            print(f"  ℹ️  {dir_name}/ already exists")
    
    # Step 2: Check for vocabulary files
    print("\n📋 Step 2: Checking for vocabulary files...")
    
    vocab_files_needed = {
        'A1.csv': False,
        'A2.csv': False,
        'B1.csv': False,
        'B2.csv': False,
        'C1_withduplicates.csv': False
    }
    
    vocab_dir = Path('vocabulary')
    for filename in vocab_files_needed:
        if (vocab_dir / filename).exists():
            vocab_files_needed[filename] = True
            print(f"  ✅ {filename} found")
        else:
            # Check if file exists in current directory
            if Path(filename).exists():
                shutil.move(filename, vocab_dir / filename)
                vocab_files_needed[filename] = True
                print(f"  ✅ Moved {filename} to vocabulary/")
            else:
                print(f"  ❌ {filename} not found")
    
    # Step 3: Check for stopwords
    print("\n📄 Step 3: Checking for stopwords file...")
    
    stopwords_file = Path("german_stopwords_plain.txt")
    if stopwords_file.exists():
        print("  ✅ german_stopwords_plain.txt found")
    else:
        print("  ❌ german_stopwords_plain.txt not found")
    
    # Step 4: Set up Streamlit configuration
    print("\n⚙️ Step 4: Setting up Streamlit configuration...")
    
    config_file = Path(".streamlit/config.toml")
    secrets_template = Path(".streamlit/secrets.toml.template")
    secrets_file = Path(".streamlit/secrets.toml")
    
    if not config_file.exists():
        print("  ❌ config.toml not found - please add it to .streamlit/")
    else:
        print("  ✅ config.toml found")
    
    if secrets_file.exists():
        print("  ✅ secrets.toml found")
    elif secrets_template.exists():
        print("  ℹ️  secrets.toml.template found")
        response = input("  Create secrets.toml from template? (y/n): ")
        if response.lower() == 'y':
            shutil.copy(secrets_template, secrets_file)
            print("  ✅ Created secrets.toml - remember to add your API keys!")
    else:
        print("  ❌ No secrets configuration found")
    
    # Step 5: Check Python environment
    print("\n🐍 Step 5: Checking Python environment...")
    
    python_version = sys.version_info
    print(f"  Python version: {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    if python_version >= (3, 12):
        requirements_file = "requirements-python312.txt"
        print("  ℹ️  Using requirements-python312.txt for Python 3.12+")
    else:
        requirements_file = "requirements.txt"
    
    # Step 6: Offer to install dependencies
    print("\n📦 Step 6: Dependencies...")
    
    if Path(requirements_file).exists():
        response = input(f"Install dependencies from {requirements_file}? (y/n): ")
        if response.lower() == 'y':
            print("  Installing packages...")
            if run_command(f"pip install -r {requirements_file}"):
                print("  ✅ Dependencies installed")
                
                # Download spaCy model
                print("  Downloading German language model...")
                if run_command("python -m spacy download de_core_news_sm"):
                    print("  ✅ spaCy model downloaded")
            else:
                print("  ❌ Failed to install dependencies")
    else:
        print(f"  ❌ {requirements_file} not found")
    
    # Step 7: Final verification
    print("\n✅ Step 7: Final verification...")
    
    if Path("verify_setup.py").exists():
        run_command("python verify_setup.py")
    else:
        # Basic verification
        all_vocab_files = all(vocab_files_needed.values())
        has_stopwords = stopwords_file.exists()
        has_app = Path("app.py").exists()
        
        print("\n" + "=" * 50)
        print("📊 Project Status:")
        print(f"  Vocabulary files: {'✅ Complete' if all_vocab_files else '❌ Missing files'}")
        print(f"  Stopwords file: {'✅ Found' if has_stopwords else '❌ Missing'}")
        print(f"  Main app: {'✅ Found' if has_app else '❌ Missing'}")
        
        if all_vocab_files and has_stopwords and has_app:
            print("\n✅ Project is ready to run!")
            print("\nNext steps:")
            print("1. Add API keys to .streamlit/secrets.toml (optional)")
            print("2. Run: streamlit run app.py")
        else:
            print("\n❌ Project setup incomplete. Please add missing files.")
    
    print("\n" + "=" * 50)
    print("Initialization complete!")

if __name__ == "__main__":
    main()
