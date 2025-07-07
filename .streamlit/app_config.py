# .streamlit/app_config.py
"""
Centralized configuration management for the German Language Analyzer
This module handles all app configuration including secrets, paths, and settings
"""

import streamlit as st
import os
from pathlib import Path
from typing import Dict, Any, Optional
import json
import logging

logger = logging.getLogger(__name__)


class AppConfig:
    """Centralized configuration for the German Language Analyzer"""
    
    def __init__(self):
        self._config = self._load_configuration()
        
    def _load_configuration(self) -> Dict[str, Any]:
        """Load configuration from various sources with precedence"""
        config = {}
        
        # 1. Load defaults
        config.update(self._get_defaults())
        
        # 2. Load from config file if exists
        config_file = Path(".streamlit/app_config.json")
        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    config.update(json.load(f))
            except Exception as e:
                logger.error(f"Error loading config file: {e}")
        
        # 3. Load from Streamlit secrets
        config.update(self._load_from_secrets())
        
        # 4. Override with environment variables
        config.update(self._load_from_env())
        
        return config
    
    def _get_defaults(self) -> Dict[str, Any]:
        """Get default configuration values"""
        return {
            # API Keys
            'claude_api_key': None,
            'gemini_api_key': None,
            
            # Deployment
            'environment': 'development',
            'debug_mode': False,
            
            # Paths
            'vocab_directory': './',
            'stopwords_file': 'german_stopwords_plain.txt',
            'cache_directory': '.streamlit/cache',
            
            # Features
            'enable_ai_translation': True,
            'enable_batch_processing': True,
            'enable_cache': True,
            'max_cache_size': 1000,
            
            # Limits
            'max_text_length': 50000,
            'max_words_per_analysis': 10000,
            'max_batch_files': 100,
            'session_timeout': 3600,
            
            # UI Settings
            'default_target_level': 'B1',
            'default_translation_language': 'English',
            'show_advanced_options': False,
            
            # Performance
            'batch_translation_threshold': 5,  # Min words for batch translation
            'cache_ttl': 3600,  # Cache time-to-live in seconds
            
            # Model settings
            'spacy_model': 'de_core_news_sm',
            'claude_model': 'claude-3-sonnet-20240229',
            'preferred_ai_model': 'Claude',  # Default AI preference
        }
    
    def _load_from_secrets(self) -> Dict[str, Any]:
        """Load configuration from Streamlit secrets"""
        config = {}
        
        try:
            # API Keys
            if "api_keys" in st.secrets:
                config['claude_api_key'] = st.secrets.api_keys.get("claude_api_key")
                config['gemini_api_key'] = st.secrets.api_keys.get("gemini_api_key")
            
            # Deployment settings
            if "deployment" in st.secrets:
                for key, value in st.secrets.deployment.items():
                    config[key] = value
            
            # File paths
            if "file_paths" in st.secrets:
                for key, value in st.secrets.file_paths.items():
                    config[key] = value
            
            # Features
            if "features" in st.secrets:
                for key, value in st.secrets.features.items():
                    config[key] = value
            
            # Limits
            if "limits" in st.secrets:
                for key, value in st.secrets.limits.items():
                    config[key] = value
                    
        except Exception as e:
            logger.debug(f"Secrets not available: {e}")
            
        return config
    
    def _load_from_env(self) -> Dict[str, Any]:
        """Load configuration from environment variables"""
        config = {}
        
        # API Keys
        if os.getenv('CLAUDE_API_KEY'):
            config['claude_api_key'] = os.getenv('CLAUDE_API_KEY')
        if os.getenv('GEMINI_API_KEY'):
            config['gemini_api_key'] = os.getenv('GEMINI_API_KEY')
        
        # Environment
        if os.getenv('DEPLOYMENT_ENV'):
            config['environment'] = os.getenv('DEPLOYMENT_ENV')
        if os.getenv('DEBUG_MODE'):
            config['debug_mode'] = os.getenv('DEBUG_MODE').lower() == 'true'
        
        # Paths
        if os.getenv('VOCAB_DIRECTORY'):
            config['vocab_directory'] = os.getenv('VOCAB_DIRECTORY')
        
        return config
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        return self._config.get(key, default)
    
    def get_api_keys(self) -> Dict[str, Optional[str]]:
        """Get all API keys"""
        return {
            'claude': self.get('claude_api_key'),
            'gemini': self.get('gemini_api_key')
        }
    
    def get_available_ai_models(self) -> list:
        """Get list of available AI models based on configured API keys"""
        models = []
        if self.get('claude_api_key'):
            models.append('Claude')
        if self.get('gemini_api_key'):
            models.append('Gemini')
        return models
    
    def is_production(self) -> bool:
        """Check if running in production environment"""
        return self.get('environment') == 'production'
    
    def is_debug(self) -> bool:
        """Check if debug mode is enabled"""
        return self.get('debug_mode', False)
    
    def get_file_paths(self) -> Dict[str, Path]:
        """Get all file paths as Path objects"""
        return {
            'vocab_directory': Path(self.get('vocab_directory', './')),
            'stopwords_file': Path(self.get('stopwords_file', 'german_stopwords_plain.txt')),
            'cache_directory': Path(self.get('cache_directory', '.streamlit/cache'))
        }
    
    def get_vocab_files(self) -> Dict[str, Path]:
        """Get paths to vocabulary files"""
        vocab_dir = Path(self.get('vocab_directory', './'))
        return {
            'A1': vocab_dir / 'A1.csv',
            'A2': vocab_dir / 'A2.csv',
            'B1': vocab_dir / 'B1.csv',
            'B2': vocab_dir / 'B2.csv',
            'C1': vocab_dir / 'C1_withduplicates.csv'
        }
    
    def validate_configuration(self) -> Dict[str, bool]:
        """Validate current configuration"""
        validation = {
            'has_ai_keys': bool(self.get('claude_api_key') or self.get('gemini_api_key')),
            'vocab_files_exist': all(f.exists() for f in self.get_vocab_files().values()),
            'stopwords_exist': Path(self.get('stopwords_file', '')).exists(),
            'valid_environment': self.get('environment') in ['development', 'staging', 'production'],
            'cache_dir_writable': self._check_cache_directory()
        }
        
        validation['is_valid'] = all(validation.values())
        return validation
    
    def _check_cache_directory(self) -> bool:
        """Check if cache directory is writable"""
        try:
            cache_dir = Path(self.get('cache_directory', '.streamlit/cache'))
            cache_dir.mkdir(parents=True, exist_ok=True)
            test_file = cache_dir / '.test'
            test_file.touch()
            test_file.unlink()
            return True
        except:
            return False
    
    def display_status(self):
        """Display configuration status in Streamlit"""
        st.sidebar.markdown("### ⚙️ Configuration")
        
        # Environment
        env = self.get('environment', 'unknown')
        env_emoji = {'development': '🔧', 'staging': '🧪', 'production': '🚀'}.get(env, '❓')
        st.sidebar.info(f"{env_emoji} **Environment**: {env}")
        
        # AI Services
        ai_models = self.get_available_ai_models()
        if ai_models:
            st.sidebar.success(f"✅ AI: {', '.join(ai_models)}")
        else:
            st.sidebar.warning("⚠️ No AI services configured")
        
        # Debug mode
        if self.is_debug():
            st.sidebar.warning("🐛 Debug mode enabled")
        
        # Validation
        validation = self.validate_configuration()
        if not validation['vocab_files_exist']:
            st.sidebar.error("❌ Missing vocabulary files")
        
        # Cache status
        if self.get('enable_cache', True):
            cache_size = self.get('max_cache_size', 1000)
            st.sidebar.info(f"💾 Cache: ON (max {cache_size})")


# Singleton instance
_config_instance = None

def get_config() -> AppConfig:
    """Get the singleton configuration instance"""
    global _config_instance
    if _config_instance is None:
        _config_instance = AppConfig()
    return _config_instance


# Convenience functions
def get_api_keys() -> Dict[str, Optional[str]]:
    """Get API keys from configuration"""
    return get_config().get_api_keys()


def is_production() -> bool:
    """Check if running in production"""
    return get_config().is_production()


def is_debug() -> bool:
    """Check if debug mode is enabled"""
    return get_config().is_debug()


# Example usage
if __name__ == "__main__":
    # Test configuration loading
    config = get_config()
    
    print("Current Configuration:")
    print(f"Environment: {config.get('environment')}")
    print(f"Debug Mode: {config.is_debug()}")
    print(f"Available AI Models: {config.get_available_ai_models()}")
    print(f"Validation: {config.validate_configuration()}")
