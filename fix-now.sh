#!/bin/bash
# fix_now.sh - Immediate fix for your current error

echo "🚀 Immediate Fix for Python 3.12"
echo "================================"

# Exit on any error
set -e

# Step 1: Clean everything
echo "Step 1: Cleaning old environment..."
deactivate 2>/dev/null || true
rm -rf venv

# Step 2: Create new environment
echo "Step 2: Creating fresh environment..."
python3 -m venv venv

# Step 3: Activate and upgrade pip
echo "Step 3: Activating and upgrading pip..."
source venv/bin/activate
python -m pip install --upgrade pip setuptools wheel

# Step 4: Install compatible packages
echo "Step 4: Installing Python 3.12 compatible packages..."
pip install numpy==1.26.2
pip install scipy==1.11.4  
pip install pandas==2.1.3
pip install streamlit==1.28.1
pip install spacy==3.7.2
pip install anthropic google-generativeai requests

# Step 5: Download spaCy model
echo "Step 5: Downloading German language model..."
python -m spacy download de_core_news_sm

# Step 6: Verify
echo "Step 6: Verifying installation..."
python -c "
import numpy, scipy, pandas, streamlit, spacy
print('✅ numpy', numpy.__version__)
print('✅ scipy', scipy.__version__)
print('✅ pandas', pandas.__version__)
print('✅ streamlit', streamlit.__version__)
print('✅ spacy', spacy.__version__)
print('\n🎉 All packages installed successfully!')
"

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Make sure you're in the virtual environment:"
echo "   source venv/bin/activate"
echo ""
echo "2. Run the app:"
echo "   streamlit run app.py"
echo ""
echo "3. Add your vocabulary files and API keys"