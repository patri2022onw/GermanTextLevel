# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a German Language Analyzer web application built with Streamlit that analyzes German texts based on CEFR levels (A1-C1). The application provides two main modes:
- **Leveling**: Simplifies texts by removing/replacing difficult words
- **Labeling**: Generates vocabulary lists with translations

## Development Commands

### Setup and Environment
```bash
# Run quick setup (Linux/Mac)
./quickstart.sh

# Manual setup
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows

pip install -r requirements.txt
python -m spacy download de_core_news_sm
```

### Running the Application
```bash
# Main web application
streamlit run app.py

# CLI batch processor
python cli_batch_processor.py -i text.txt -o output/ -l B1

# Check file setup
python check_files.py

# Verify imports and dependencies
python test_imports.py
```

### Testing and Verification
```bash
# No formal test suite - use these verification scripts:
python verify_setup.py
python test_imports.py
```

## Core Architecture

### Main Components

1. **GermanLanguageAnalyzer** (`app.py:35-224`): Core class that handles:
   - CEFR level vocabulary loading from CSV files
   - spaCy-based text processing with German NLP model
   - Word level analysis and filtering
   - Named entity recognition to exclude proper nouns

2. **AIService** (`app.py:225-298`): AI integration layer supporting:
   - Claude (Anthropic) API for text simplification
   - Gemini (Google) API for text simplification
   - Context-aware German text processing

3. **TranslationService** (`translation_service.py`): Handles translations using:
   - AI-powered translations (Claude/Gemini)
   - Batch processing for efficiency
   - Caching for performance optimization

4. **CLI Processor** (`cli_batch_processor.py`): Command-line interface for:
   - Batch processing of multiple text files
   - Automated workflow integration
   - Headless operation without web interface

### Data Dependencies

The application requires specific vocabulary files in the root directory:
- `A1.csv`, `A2.csv`, `B1.csv`, `B2.csv`, `C1_withduplicates.csv`
- `german_stopwords_plain.txt`

Each CSV file must contain at least a `Lemma` column for word lookups.

### Configuration

- **Streamlit config**: `.streamlit/config.toml` with custom theme, performance settings, and German text processing parameters
- **API credentials**: `.streamlit/secrets.toml` (use template from quickstart.sh)
- **Logging**: Configured in each module, outputs to `logs/` directory

## Key Implementation Details

### Text Processing Pipeline
1. Load vocabulary files into word_levels dictionary
2. Process text with spaCy's German model (`de_core_news_sm`)
3. Extract lemmas and filter by CEFR level
4. Apply named entity recognition to exclude proper nouns
5. Generate results based on selected mode (leveling/labeling)

### AI Integration
- Both Claude and Gemini APIs are supported for text simplification
- Translation service uses the same AI models (no separate translation API needed)
- Caching is implemented to optimize API usage and costs

### Performance Considerations
- Text length limit: 50,000 characters (configurable in config.toml)
- Caching enabled for vocabulary lookups and translations
- Batch processing available for large-scale operations

## File Structure
```
app.py                    # Main Streamlit application
translation_service.py    # AI translation service
cli_batch_processor.py    # CLI batch processor
quickstart.sh            # Setup script
vocabulary/              # CEFR vocabulary CSV files
.streamlit/              # Streamlit configuration
logs/                    # Application logs
output/                  # CLI output directory
```

## API Requirements

To use AI features, add API keys to `.streamlit/secrets.toml`:
```toml
[api_keys]
claude_api_key = "your-claude-api-key"
gemini_api_key = "your-gemini-api-key"
```

## Known Dependencies

- spaCy German model: `de_core_news_sm` (downloaded via setup script)
- Python 3.8+ (optimized for Python 3.12)
- Streamlit 1.28+
- pandas for CSV processing
- anthropic and google-generativeai for AI services