#!/bin/bash
# .streamlit/setup.sh
# Setup script for .streamlit configuration folder

echo "🚀 Setting up .streamlit configuration folder"
echo "=========================================="

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if we're in the .streamlit directory or project root
if [[ ${PWD##*/} == ".streamlit" ]]; then
    STREAMLIT_DIR="."
elif [[ -d ".streamlit" ]]; then
    STREAMLIT_DIR=".streamlit"
else
    echo -e "${YELLOW}Creating .streamlit directory...${NC}"
    mkdir -p .streamlit
    STREAMLIT_DIR=".streamlit"
fi

cd "$STREAMLIT_DIR"

# Function to create file from template
create_from_template() {
    template_file="$1.template"
    target_file="$1"
    
    if [[ -f "$target_file" ]]; then
        echo -e "${YELLOW}⚠️  $target_file already exists. Skipping...${NC}"
    elif [[ -f "$template_file" ]]; then
        cp "$template_file" "$target_file"
        echo -e "${GREEN}✅ Created $target_file from template${NC}"
        echo -e "${YELLOW}   👉 Remember to edit $target_file with your actual values${NC}"
    else
        echo -e "${RED}❌ Template $template_file not found${NC}"
    fi
}

# 1. Check for required files
echo -e "\n${GREEN}1. Checking required files...${NC}"

if [[ ! -f "config.toml" ]]; then
    echo -e "${RED}❌ config.toml not found${NC}"
    echo "   Please ensure config.toml exists in the .streamlit directory"
else
    echo -e "${GREEN}✅ config.toml found${NC}"
fi

# 2. Create secrets.toml from template
echo -e "\n${GREEN}2. Setting up secrets...${NC}"
create_from_template "secrets.toml"

# 3. Create credentials.toml from template (optional)
echo -e "\n${GREEN}3. Setting up Google credentials (optional)...${NC}"
read -p "Do you want to set up Google Cloud credentials? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    create_from_template "credentials.toml"
else
    echo "   Skipping Google credentials setup"
fi

# 4. Create cache directory
echo -e "\n${GREEN}4. Creating cache directory...${NC}"
if [[ ! -d "cache" ]]; then
    mkdir -p cache
    echo -e "${GREEN}✅ Created cache directory${NC}"
else
    echo "   Cache directory already exists"
fi

# 5. Set proper permissions
echo -e "\n${GREEN}5. Setting file permissions...${NC}"
chmod 600 secrets.toml 2>/dev/null && echo -e "${GREEN}✅ Set secure permissions on secrets.toml${NC}"
chmod 600 credentials.toml 2>/dev/null && echo -e "${GREEN}✅ Set secure permissions on credentials.toml${NC}"

# 6. Check .gitignore
echo -e "\n${GREEN}6. Checking .gitignore...${NC}"
if [[ -f ".gitignore" ]]; then
    echo -e "${GREEN}✅ .gitignore found${NC}"
    
    # Check if secrets.toml is in .gitignore
    if grep -q "secrets.toml" .gitignore; then
        echo -e "${GREEN}✅ secrets.toml is in .gitignore${NC}"
    else
        echo -e "${RED}⚠️  secrets.toml is NOT in .gitignore - adding it${NC}"
        echo "secrets.toml" >> .gitignore
    fi
else
    echo -e "${YELLOW}⚠️  No .gitignore found in .streamlit directory${NC}"
fi

# 7. Validate TOML syntax (if python is available)
echo -e "\n${GREEN}7. Validating configuration files...${NC}"
if command -v python3 &> /dev/null; then
    python3 -c "
import toml
import sys
files = ['config.toml', 'secrets.toml']
for f in files:
    try:
        with open(f, 'r') as file:
            toml.load(file)
        print(f'✅ {f} - Valid TOML syntax')
    except FileNotFoundError:
        print(f'⚠️  {f} - Not found')
    except Exception as e:
        print(f'❌ {f} - Invalid TOML: {e}')
        sys.exit(1)
" 2>/dev/null || echo -e "${YELLOW}   Install 'toml' package for validation: pip install toml${NC}"
else
    echo "   Python not found - skipping TOML validation"
fi

# 8. Summary
echo -e "\n${GREEN}📋 Setup Summary${NC}"
echo "================"

# Check what's configured
if [[ -f "secrets.toml" ]]; then
    if grep -q "claude_api_key = \"sk-ant" secrets.toml 2>/dev/null; then
        echo -e "${YELLOW}⚠️  secrets.toml exists but contains template values${NC}"
        echo "   Edit secrets.toml and add your actual API keys"
    else
        echo -e "${GREEN}✅ secrets.toml is configured${NC}"
    fi
else
    echo -e "${RED}❌ secrets.toml not found${NC}"
fi

# Final instructions
echo -e "\n${GREEN}🎯 Next Steps:${NC}"
echo "1. Edit secrets.toml with your API keys:"
echo "   - Claude API key from https://console.anthropic.com/"
echo "   - OR Gemini API key from https://makersuite.google.com/"
echo ""
echo "2. For Streamlit Cloud deployment:"
echo "   - Don't commit secrets.toml to Git"
echo "   - Add secrets through the Streamlit Cloud web interface"
echo ""
echo "3. Test your configuration:"
echo "   cd .. && streamlit run app.py"

echo -e "\n${GREEN}✨ Setup complete!${NC}"

# Return to original directory
cd - > /dev/null