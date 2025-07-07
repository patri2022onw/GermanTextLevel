#!/usr/bin/env python3
"""
fix_dependencies.py - Resolve dependency conflicts for German Language Analyzer
"""

import subprocess
import sys
import os

def run_command(cmd, check=True):
    """Run a command and return the result"""
    print(f"Running: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if check and result.returncode != 0:
        print(f"Error: {result.stderr}")
        return False
    print(result.stdout)
    return True

def main():
    print("🔧 German Language Analyzer - Dependency Fix Tool")
    print("=" * 50)
    
    # Step 1: Create a clean virtual environment
    print("\n1. Creating clean virtual environment...")
    if os.path.exists("venv"):
        response = input("Virtual environment already exists. Recreate it? (y/n): ")
        if response.lower() == 'y':
            if sys.platform == "win32":
                run_command("rmdir /s /q venv", check=False)
            else:
                run_command("rm -rf venv", check=False)
            run_command(f"{sys.executable} -m venv venv")
        else:
            print("Using existing virtual environment.")
    else:
        run_command(f"{sys.executable} -m venv venv")
    
    # Step 2: Activate instructions
    print("\n2. Activate the virtual environment:")
    if sys.platform == "win32":
        print("   Run: venv\\Scripts\\activate")
        activate_cmd = "venv\\Scripts\\python.exe"
    else:
        print("   Run: source venv/bin/activate")
        activate_cmd = "venv/bin/python"
    
    print("\n3. Installing packages in correct order...")
    
    # Use the virtual environment's pip
    pip_cmd = f"{activate_cmd} -m pip"
    
    # Upgrade pip first
    print("\n📦 Upgrading pip...")
    run_command(f"{pip_cmd} install --upgrade pip")
    
    # Install numpy and scipy first (core dependencies)
    print("\n📦 Installing numpy and scipy...")
    run_command(f"{pip_cmd} install numpy==1.24.3 scipy==1.10.1")
    
    # Install pandas
    print("\n📦 Installing pandas...")
    run_command(f"{pip_cmd} install pandas==2.0.3")
    
    # Install Streamlit
    print("\n📦 Installing Streamlit...")
    run_command(f"{pip_cmd} install streamlit==1.28.1")
    
    # Install spaCy
    print("\n📦 Installing spaCy...")
    run_command(f"{pip_cmd} install spacy==3.6.1")
    
    # Install AI libraries
    print("\n📦 Installing AI libraries...")
    run_command(f"{pip_cmd} install anthropic==0.7.7 google-generativeai==0.3.2")
    
    # Install remaining dependencies
    print("\n📦 Installing remaining dependencies...")
    run_command(f"{pip_cmd} install requests==2.31.0")
    
    # Download spaCy model
    print("\n📦 Downloading German language model...")
    run_command(f"{activate_cmd} -m spacy download de_core_news_sm")
    
    # Verify installation
    print("\n✅ Verifying installation...")
    test_code = """
import streamlit
import pandas
import numpy
import scipy
import spacy
import anthropic
import google.generativeai
print(f"numpy version: {numpy.__version__}")
print(f"scipy version: {scipy.__version__}")
print(f"pandas version: {pandas.__version__}")
print(f"streamlit version: {streamlit.__version__}")
print(f"spacy version: {spacy.__version__}")
print("All packages imported successfully!")
"""
    
    with open("test_imports.py", "w") as f:
        f.write(test_code)
    
    if run_command(f"{activate_cmd} test_imports.py"):
        print("\n✅ All dependencies installed successfully!")
        os.remove("test_imports.py")
    else:
        print("\n❌ Some imports failed. Check the error messages above.")
        
    print("\n📋 Next steps:")
    print("1. Activate your virtual environment:")
    if sys.platform == "win32":
        print("   venv\\Scripts\\activate")
    else:
        print("   source venv/bin/activate")
    print("2. Run the app:")
    print("   streamlit run app.py")
    print("\nIf you still encounter issues, try using requirements-fixed.txt:")
    print("   pip install -r requirements-fixed.txt")

if __name__ == "__main__":
    main()
