"""
Example of how to use Streamlit secrets in your application
This file shows best practices for accessing secrets safely
"""

import streamlit as st
import os
from typing import Optional, Dict, Any


def get_api_keys() -> Dict[str, Optional[str]]:
    """
    Safely retrieve API keys from Streamlit secrets or environment variables
    
    Returns:
        Dictionary with API keys (may be None if not configured)
    """
    api_keys = {
        'claude': None,
        'gemini': None
    }
    
    # Method 1: Try Streamlit secrets first (for Streamlit Cloud)
    try:
        if "api_keys" in st.secrets:
            api_keys['claude'] = st.secrets.api_keys.get("claude_api_key", None)
            api_keys['gemini'] = st.secrets.api_keys.get("gemini_api_key", None)
    except Exception as e:
        # Secrets not available (local development without secrets.toml)
        pass
    
    # Method 2: Fall back to environment variables
    if not api_keys['claude']:
        api_keys['claude'] = os.getenv('CLAUDE_API_KEY')
    if not api_keys['gemini']:
        api_keys['gemini'] = os.getenv('GEMINI_API_KEY')
    
    return api_keys


def get_deployment_config() -> Dict[str, Any]:
    """
    Get deployment configuration settings
    
    Returns:
        Dictionary with deployment settings
    """
    default_config = {
        'environment': 'development',
        'debug_mode': False,
        'enable_cache': True,
        'max_cache_size': 1000
    }
    
    # Try to get from secrets
    try:
        if "deployment" in st.secrets:
            default_config.update(st.secrets.deployment.to_dict())
        if "features" in st.secrets:
            default_config.update(st.secrets.features.to_dict())
    except:
        pass
    
    # Override with environment variables if they exist
    if os.getenv('DEPLOYMENT_ENV'):
        default_config['environment'] = os.getenv('DEPLOYMENT_ENV')
    
    return default_config


def get_file_paths() -> Dict[str, str]:
    """
    Get file paths configuration
    
    Returns:
        Dictionary with file paths
    """
    paths = {
        'vocab_directory': './',
        'stopwords_file': 'german_stopwords_plain.txt',
        'cache_directory': '.streamlit/cache'
    }
    
    # Try to get from secrets
    try:
        if "file_paths" in st.secrets:
            paths.update(st.secrets.file_paths.to_dict())
    except:
        pass
    
    return paths


def validate_api_keys(api_keys: Dict[str, Optional[str]]) -> Dict[str, bool]:
    """
    Validate which API keys are configured
    
    Args:
        api_keys: Dictionary of API keys
        
    Returns:
        Dictionary indicating which services are available
    """
    return {
        'claude_available': bool(api_keys.get('claude')),
        'gemini_available': bool(api_keys.get('gemini')),
        'any_ai_available': bool(api_keys.get('claude') or api_keys.get('gemini'))
    }


def display_configuration_status():
    """
    Display current configuration status in Streamlit sidebar
    """
    with st.sidebar:
        st.header("⚙️ Configuration Status")
        
        # Get configurations
        api_keys = get_api_keys()
        deployment = get_deployment_config()
        availability = validate_api_keys(api_keys)
        
        # Display environment
        env_color = {
            'development': '🟡',
            'staging': '🟠',
            'production': '🟢'
        }.get(deployment['environment'], '⚪')
        
        st.write(f"{env_color} Environment: **{deployment['environment']}**")
        
        # Display API status
        st.write("**AI Services:**")
        if availability['claude_available']:
            st.write("✅ Claude API configured")
        else:
            st.write("❌ Claude API not configured")
            
        if availability['gemini_available']:
            st.write("✅ Gemini API configured")
        else:
            st.write("❌ Gemini API not configured")
        
        # Display feature flags
        if deployment.get('debug_mode'):
            st.warning("🐛 Debug mode is enabled")
        
        # Cache status
        if deployment.get('enable_cache', True):
            st.write(f"💾 Cache enabled (max {deployment.get('max_cache_size', 1000)} items)")
        else:
            st.write("💾 Cache disabled")


# Example usage in main app
def main():
    """Example main function showing secrets usage"""
    st.title("Streamlit Secrets Example")
    
    # Display configuration status
    display_configuration_status()
    
    # Get API keys safely
    api_keys = get_api_keys()
    
    # Check if any AI service is available
    availability = validate_api_keys(api_keys)
    
    if availability['any_ai_available']:
        st.success("✅ AI services are configured and ready!")
        
        # Initialize AI service with available key
        if availability['claude_available']:
            st.write("Using Claude for AI services")
            # Initialize Claude with api_keys['claude']
        elif availability['gemini_available']:
            st.write("Using Gemini for AI services")
            # Initialize Gemini with api_keys['gemini']
    else:
        st.warning("⚠️ No AI services configured. Please add API keys.")
        st.info("""
        **To add API keys:**
        1. For local development: Create `.streamlit/secrets.toml`
        2. For Streamlit Cloud: Add in App Settings → Secrets
        3. Or set environment variables: `CLAUDE_API_KEY` or `GEMINI_API_KEY`
        """)
    
    # Example of using file paths
    paths = get_file_paths()
    st.write("**File Paths:**")
    st.json(paths)


if __name__ == "__main__":
    # This example can be run standalone to test secrets configuration
    main()