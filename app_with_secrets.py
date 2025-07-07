# app_with_secrets.py
# Example showing how to integrate Streamlit secrets for API keys

import streamlit as st
import os

def get_api_keys():
    """Get API keys from Streamlit secrets or environment variables"""
    
    # Try to get from Streamlit secrets first
    try:
        claude_key = st.secrets.get("api_keys", {}).get("claude_api_key", "")
        gemini_key = st.secrets.get("api_keys", {}).get("gemini_api_key", "")
        
        return {
            'claude': claude_key,
            'gemini': gemini_key
        }
    except:
        # Fallback to environment variables
        return {
            'claude': os.getenv('CLAUDE_API_KEY', ''),
            'gemini': os.getenv('GEMINI_API_KEY', '')
        }

def initialize_services_with_secrets(ai_service, api_keys):
    """Initialize AI services with pre-configured API keys"""
    
    # Initialize Claude if key is available
    if api_keys['claude']:
        if ai_service.initialize_claude(api_keys['claude']):
            st.sidebar.success("✅ Claude API auto-initialized")
        else:
            st.sidebar.error("❌ Failed to initialize Claude API")
    
    # Initialize Gemini if key is available
    if api_keys['gemini']:
        if ai_service.initialize_gemini(api_keys['gemini']):
            st.sidebar.success("✅ Gemini API auto-initialized")
        else:
            st.sidebar.error("❌ Failed to initialize Gemini API")
    
    return ai_service

# Modified sidebar section for the main app
def render_sidebar_with_secrets(ai_service):
    """Render sidebar with support for pre-configured secrets"""
    
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # Get pre-configured API keys
        api_keys = get_api_keys()
        
        # API Keys section
        st.subheader("🔑 API Keys")
        
        # Show status of pre-configured keys
        if any(api_keys.values()):
            st.info("🔐 Some API keys are pre-configured")
            
            # Initialize services with pre-configured keys
            ai_service = initialize_services_with_secrets(ai_service, api_keys)
        
        # Allow manual input to override
        with st.expander("Manual API Key Input (Optional)"):
            manual_claude_key = st.text_input(
                "Claude API Key", 
                type="password",
                help="Override pre-configured key",
                value="" if not api_keys['claude'] else "••••••••"
            )
            
            manual_gemini_key = st.text_input(
                "Gemini API Key", 
                type="password",
                help="Override pre-configured key",
                value="" if not api_keys['gemini'] else "••••••••"
            )
            
            # Only initialize if new keys are provided
            if manual_claude_key and manual_claude_key != "••••••••":
                if ai_service.initialize_claude(manual_claude_key):
                    st.success("✅ Claude API initialized with manual key")
                else:
                    st.error("❌ Failed to initialize Claude API")
            
            if manual_gemini_key and manual_gemini_key != "••••••••":
                if ai_service.initialize_gemini(manual_gemini_key):
                    st.success("✅ Gemini API initialized with manual key")
                else:
                    st.error("❌ Failed to initialize Gemini API")
        
        # Rest of sidebar content...
        
# Example secrets.toml file for Streamlit Cloud:
"""
# .streamlit/secrets.toml

[api_keys]
claude_api_key = "sk-ant-..."
gemini_api_key = "AIza..."

[deployment]
environment = "production"
debug_mode = false

[file_paths]
vocab_directory = "vocabulary/"
stopwords_file = "german_stopwords_plain.txt"
"""