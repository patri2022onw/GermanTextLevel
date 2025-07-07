#!/bin/bash
# quickstart.sh - Quick setup script for German Language Analyzer

echo "🇩🇪 German Language Analyzer - Quick Start Setup"
echo "=============================================="

# Check Python version
echo -e "\n📍 Checking Python version..."
python_version=$(python3 --version 2>&1)
if [[ $? -eq 0 ]]; then
    echo "✅ Found: $python_version"
else
    echo "❌ Python 3 not found. Please install Python 3.8 or higher."
    exit 1
fi

# Create virtual environment
echo -e "\n📍 Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "ℹ️  Virtual environment already exists"
fi

# Activate virtual environment
echo -e "\n📍 Activating virtual environment..."
source venv/bin/activate || . venv/Scripts/activate
echo "✅ Virtual environment activated"

# Install requirements
echo -e "\n📍 Installing requirements..."
pip install --upgrade pip
pip install -r requirements.txt
echo "✅ Requirements installed"

# Download spaCy model
echo -e "\n📍 Downloading German language model..."
python -m spacy download de_core_news_sm
echo "✅ Language model downloaded"

# Create directories if needed
echo -e "\n📍 Setting up project structure..."
mkdir -p .streamlit
mkdir -p logs
mkdir -p output
echo "✅ Directories created"

# Check for vocabulary files
echo -e "\n📍 Checking vocabulary files..."
python check_files.py

# Create example secrets file if it doesn't exist
if [ ! -f ".streamlit/secrets.toml" ]; then
    echo -e "\n📍 Creating example secrets file..."
    cat > .streamlit/secrets.toml << 'EOF'
# Example secrets file - Add your actual API keys here
[api_keys]
# claude_api_key = "your-claude-api-key"
# gemini_api_key = "your-gemini-api-key"
# deepl_api_key = "your-deepl-api-key"

[deployment]
environment = "development"
EOF
    echo "✅ Created .streamlit/secrets.toml (add your API keys)"
fi

# Final instructions
echo -e "\n✨ Setup complete!"
echo -e "\n📋 Next steps:"
echo "1. Add your vocabulary files (A1.csv, A2.csv, etc.) to the project root"
echo "2. Add your API keys to .streamlit/secrets.toml (optional)"
echo "3. Run the app with: streamlit run app.py"
echo -e "\n💡 For deployment on Streamlit Cloud:"
echo "   - Push all files to GitHub"
echo "   - Deploy at share.streamlit.io"
echo "   - Configure secrets in the Streamlit Cloud dashboard"