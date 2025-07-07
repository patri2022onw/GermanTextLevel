# .streamlit Configuration Folder

This folder contains configuration files for the German Language Analyzer Streamlit app.

## 📁 Files in this folder

### 1. **config.toml** ✅
Main configuration file for Streamlit settings:
- Theme and appearance
- Server configuration
- Performance settings
- File upload limits

### 2. **secrets.toml** 🔐
**IMPORTANT**: This file contains sensitive API keys and should NEVER be committed to version control!
- Copy `secrets.toml.template` to `secrets.toml`
- Add your actual API keys
- Ensure it's in `.gitignore`

### 3. **secrets.toml.template** 📋
Template file showing the structure for secrets.toml:
- Example API key entries
- Configuration options
- Documentation

### 4. **credentials.toml** (optional) 🔑
For Google Cloud services integration:
- Only needed if using Google Cloud APIs
- Similar security considerations as secrets.toml

## 🚀 Quick Setup

1. **For local development:**
   ```bash
   cd .streamlit
   cp secrets.toml.template secrets.toml
   # Edit secrets.toml with your API keys
   ```

2. **For Streamlit Cloud:**
   - Don't upload secrets.toml
   - Add secrets through the web interface
   - Go to: App settings → Secrets
   - Paste the contents (without comments)

## 🔐 Security Best Practices

1. **Never commit secrets to Git:**
   ```bash
   # Ensure this is in your .gitignore
   .streamlit/secrets.toml
   .streamlit/credentials.toml
   ```

2. **Use environment variables as alternative:**
   ```python
   import os
   api_key = os.getenv('CLAUDE_API_KEY', '')
   ```

3. **Rotate keys regularly**

## 📝 Configuration Options

### Theme Customization
Edit `config.toml` to change:
- Colors (primaryColor, backgroundColor, etc.)
- Fonts
- Layout options

### Performance Tuning
Adjust in `config.toml`:
- `maxUploadSize`: For larger vocabulary files
- `enableWebsocketCompression`: For better performance
- `caching`: Enable/disable caching

### Development Settings
- `runOnSave`: Auto-reload on file changes
- `showErrorDetails`: Detailed error messages
- `logger.level`: Set to "debug" for troubleshooting

## 🌐 Deployment Configurations

### Local Development
```toml
[server]
address = "localhost"
port = 8501
```

### Production (Streamlit Cloud)
```toml
[server]
address = "0.0.0.0"
headless = true
```

## 📚 Additional Resources

- [Streamlit Configuration](https://docs.streamlit.io/library/advanced-features/configuration)
- [Streamlit Secrets Management](https://docs.streamlit.io/streamlit-community-cloud/get-started/deploy-an-app/connect-to-data-sources/secrets-management)
- [Theming Documentation](https://docs.streamlit.io/library/advanced-features/theming)

---

**Remember**: Keep your secrets secret! 🤫