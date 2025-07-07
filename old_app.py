import streamlit as st
import pandas as pd
import spacy
from spacy.lang.de import German
import json
import os
from typing import Dict, List, Set, Tuple, Optional
import logging
from datetime import datetime
import requests
from collections import defaultdict
import re
import base64
from io import BytesIO
import anthropic
import google.generativeai as genai

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="German Language Analyzer",
    page_icon="🇩🇪",
    layout="wide"
)

# Initialize session state
if 'processed_text' not in st.session_state:
    st.session_state.processed_text = None
if 'analysis_results' not in st.session_state:
    st.session_state.analysis_results = None
if 'files_loaded' not in st.session_state:
    st.session_state.files_loaded = False
if 'analyzer' not in st.session_state:
    st.session_state.analyzer = None

class GermanLanguageAnalyzer:
    """Main class for analyzing German texts based on CEFR levels"""
    
    def __init__(self):
        self.word_levels = {}
        self.stopwords = set()
        self.core_words = set()  # Will be populated with common German core words
        self.nlp = None
        self.initialize_spacy()
        
    def initialize_spacy(self):
        """Initialize spaCy with German language model"""
        try:
            # Try to load the full German model
            self.nlp = spacy.load("de_core_news_sm")
        except OSError:
            # If not available, create a basic German language object
            logger.warning("Full German model not found. Using basic tokenizer.")
            self.nlp = German()
            
    def load_stopwords(self, filepath: str):
        """Load German stopwords from file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith(';'):
                        self.stopwords.add(line.lower())
            logger.info(f"Loaded {len(self.stopwords)} stopwords")
        except Exception as e:
            logger.error(f"Error loading stopwords: {e}")
            
    def load_word_lists(self, file_mapping: Dict[str, str]):
        """Load word lists for different CEFR levels"""
        for level, filepath in file_mapping.items():
            try:
                df = pd.read_csv(filepath)
                
                # Handle different column names
                lemma_col = 'Lemma' if 'Lemma' in df.columns else 'lemma'
                
                if lemma_col in df.columns:
                    for lemma in df[lemma_col]:
                        if pd.notna(lemma) and isinstance(lemma, str):
                            lemma_lower = lemma.lower()
                            if lemma_lower not in self.word_levels:
                                self.word_levels[lemma_lower] = level
                            
                logger.info(f"Loaded {len(df)} words for level {level}")
            except Exception as e:
                logger.error(f"Error loading {level} word list: {e}")
                
    def initialize_core_words(self):
        """Initialize a set of German core words that should be excluded from analysis"""
        # Basic pronouns, articles, prepositions, conjunctions
        self.core_words.update({
            # Articles
            'der', 'die', 'das', 'den', 'dem', 'des', 'ein', 'eine', 'einen', 'einem', 'einer', 'eines',
            # Personal pronouns
            'ich', 'du', 'er', 'sie', 'es', 'wir', 'ihr', 'sie',
            'mich', 'dich', 'ihn', 'sie', 'es', 'uns', 'euch', 'sie',
            'mir', 'dir', 'ihm', 'ihr', 'ihm', 'uns', 'euch', 'ihnen',
            # Possessive pronouns
            'mein', 'dein', 'sein', 'ihr', 'unser', 'euer',
            'meine', 'deine', 'seine', 'ihre', 'unsere', 'eure',
            # Common prepositions
            'in', 'an', 'auf', 'unter', 'über', 'vor', 'hinter', 'neben', 'zwischen',
            'mit', 'ohne', 'für', 'gegen', 'durch', 'um', 'aus', 'bei', 'nach', 'von', 'zu',
            # Common conjunctions
            'und', 'oder', 'aber', 'denn', 'sondern', 'sowie', 'als', 'wie', 'wenn', 'weil', 'dass',
            # Question words
            'was', 'wer', 'wo', 'wann', 'warum', 'wie', 'welche', 'welcher', 'welches',
            # Common adverbs
            'nicht', 'sehr', 'auch', 'noch', 'schon', 'nur', 'hier', 'da', 'dort',
            # Numbers 1-20
            'eins', 'zwei', 'drei', 'vier', 'fünf', 'sechs', 'sieben', 'acht', 'neun', 'zehn',
            'elf', 'zwölf', 'dreizehn', 'vierzehn', 'fünfzehn', 'sechzehn', 'siebzehn', 
            'achtzehn', 'neunzehn', 'zwanzig'
        })
        
    def get_word_level(self, lemma: str) -> Optional[str]:
        """Get the CEFR level of a word"""
        lemma_lower = lemma.lower()
        return self.word_levels.get(lemma_lower)
    
    def is_above_level(self, word_level: str, target_level: str) -> bool:
        """Check if a word's level is above the target level"""
        level_order = {'A1': 1, 'A2': 2, 'B1': 3, 'B2': 4, 'C1': 5}
        
        if word_level not in level_order or target_level not in level_order:
            return False
            
        return level_order[word_level] > level_order[target_level]
    
    def analyze_text(self, text: str, target_level: str) -> Dict:
        """Analyze text and find words above the target level"""
        doc = self.nlp(text)
        
        words_above_level = defaultdict(list)
        all_words = []
        skipped_entities = set()
        
        for token in doc:
            # Skip punctuation and spaces
            if token.is_punct or token.is_space:
                continue
                
            # Get lemma or use the token text
            lemma = token.lemma_ if token.lemma_ != "-PRON-" else token.text
            lemma_lower = lemma.lower()
            
            # Skip named entities
            if token.ent_type_:
                skipped_entities.add(token.text)
                continue
                
            # Skip stopwords and core words
            if lemma_lower in self.stopwords or lemma_lower in self.core_words:
                continue
                
            all_words.append((token.text, lemma))
            
            # Check word level
            word_level = self.get_word_level(lemma)
            if word_level and self.is_above_level(word_level, target_level):
                words_above_level[word_level].append({
                    'original': token.text,
                    'lemma': lemma,
                    'pos': token.pos_,
                    'index': token.i
                })
                
        return {
            'words_above_level': dict(words_above_level),
            'all_words': all_words,
            'skipped_entities': list(skipped_entities),
            'total_words': len(all_words),
            'doc': doc
        }

class TranslationService:
    """Service for translating German words to various languages using AI"""
    
    def __init__(self, ai_service: str = None, ai_model: str = "Claude"):
        self.ai_service = ai_service
        self.ai_model = ai_model
        self.translation_cache = {}
        
    def translate_word(self, word: str, target_lang: str) -> str:
        """Translate a German word to the target language using AI"""
        # Check cache first
        cache_key = f"{word}_{target_lang}_{self.ai_model}"
        if cache_key in self.translation_cache:
            return self.translation_cache[cache_key]
        
        # If no AI service available, return mock translation
        if not self.ai_service or self.ai_model == "None":
            return f"{word} ({target_lang[:2].upper()})"
        
        try:
            if self.ai_model == "Claude" and self.ai_service.claude_client:
                translation = self._translate_with_claude(word, target_lang)
            elif self.ai_model == "Gemini" and self.ai_service.gemini_model:
                translation = self._translate_with_gemini(word, target_lang)
            else:
                translation = f"{word} ({target_lang[:2].upper()})"
            
            # Cache the translation
            self.translation_cache[cache_key] = translation
            return translation
            
        except Exception as e:
            logger.error(f"Translation error: {e}")
            return f"{word} (error)"
    
    def _translate_with_claude(self, word: str, target_lang: str) -> str:
        """Use Claude for translation"""
        try:
            prompt = f"""Translate the German word "{word}" to {target_lang}.
            Provide ONLY the translation, no explanations or additional text.
            If the word has multiple meanings, provide the most common one.
            
            German word: {word}
            {target_lang} translation:"""
            
            response = self.ai_service.claude_client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=50,
                messages=[{"role": "user", "content": prompt}]
            )
            
            translation = response.content[0].text.strip()
            return translation if translation else f"{word} ({target_lang[:2].upper()})"
            
        except Exception as e:
            logger.error(f"Claude translation error: {e}")
            return f"{word} (error)"
    
    def _translate_with_gemini(self, word: str, target_lang: str) -> str:
        """Use Gemini for translation"""
        try:
            prompt = f"""Translate the German word "{word}" to {target_lang}.
            Provide ONLY the translation, no explanations or additional text.
            If the word has multiple meanings, provide the most common one.
            
            German word: {word}
            {target_lang} translation:"""
            
            response = self.ai_service.gemini_model.generate_content(prompt)
            translation = response.text.strip()
            return translation if translation else f"{word} ({target_lang[:2].upper()})"
            
        except Exception as e:
            logger.error(f"Gemini translation error: {e}")
            return f"{word} (error)"
    
    def translate_batch(self, words: List[str], target_lang: str) -> Dict[str, str]:
        """Translate multiple words efficiently"""
        translations = {}
        
        # For batch translation with AI, we can optimize by sending multiple words at once
        if self.ai_service and self.ai_model != "None" and len(words) > 5:
            # Batch translate for efficiency
            uncached_words = [w for w in words if f"{w}_{target_lang}_{self.ai_model}" not in self.translation_cache]
            
            if uncached_words:
                batch_translations = self._batch_translate_with_ai(uncached_words, target_lang)
                translations.update(batch_translations)
        
        # Translate remaining words individually (or all if batch not used)
        for word in words:
            if word not in translations:
                translations[word] = self.translate_word(word, target_lang)
        
        return translations
    
    def _batch_translate_with_ai(self, words: List[str], target_lang: str) -> Dict[str, str]:
        """Batch translate multiple words with AI for efficiency"""
        try:
            words_str = ', '.join([f'"{w}"' for w in words])
            
            if self.ai_model == "Claude" and self.ai_service.claude_client:
                prompt = f"""Translate these German words to {target_lang}.
                Format your response as a simple list with one translation per line, 
                in the same order as the input words.
                
                German words: {words_str}
                
                Provide ONLY the translations, one per line:"""
                
                response = self.ai_service.claude_client.messages.create(
                    model="claude-3-sonnet-20240229",
                    max_tokens=500,
                    messages=[{"role": "user", "content": prompt}]
                )
                
                translations_text = response.content[0].text.strip()
                
            elif self.ai_model == "Gemini" and self.ai_service.gemini_model:
                prompt = f"""Translate these German words to {target_lang}.
                Format your response as a simple list with one translation per line, 
                in the same order as the input words.
                
                German words: {words_str}
                
                Provide ONLY the translations, one per line:"""
                
                response = self.ai_service.gemini_model.generate_content(prompt)
                translations_text = response.text.strip()
            else:
                return {}
            
            # Parse the response
            translation_lines = translations_text.split('\n')
            translations = {}
            
            for i, word in enumerate(words):
                if i < len(translation_lines):
                    translation = translation_lines[i].strip()
                    if translation:
                        translations[word] = translation
                        # Cache it
                        cache_key = f"{word}_{target_lang}_{self.ai_model}"
                        self.translation_cache[cache_key] = translation
                
            return translations
            
        except Exception as e:
            logger.error(f"Batch translation error: {e}")
            return {}

class AIService:
    """Service for AI-powered text analysis and simplification"""
    
    def __init__(self):
        self.claude_client = None
        self.gemini_model = None
        
    def initialize_claude(self, api_key: str):
        """Initialize Claude API client"""
        try:
            self.claude_client = anthropic.Anthropic(api_key=api_key)
            return True
        except Exception as e:
            logger.error(f"Error initializing Claude: {e}")
            return False
            
    def initialize_gemini(self, api_key: str):
        """Initialize Gemini API client"""
        try:
            genai.configure(api_key=api_key)
            self.gemini_model = genai.GenerativeModel('gemini-pro')
            return True
        except Exception as e:
            logger.error(f"Error initializing Gemini: {e}")
            return False
            
    def simplify_text_claude(self, text: str, target_level: str, words_to_replace: List[str]) -> str:
        """Use Claude to simplify text"""
        if not self.claude_client:
            return text
            
        try:
            prompt = f"""Please simplify the following German text to {target_level} level. 
            Replace these words that are above {target_level} level: {', '.join(words_to_replace)}
            Keep the meaning as close as possible to the original.
            
            Original text: {text}
            
            Simplified text:"""
            
            response = self.claude_client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=1000,
                messages=[{"role": "user", "content": prompt}]
            )
            
            return response.content[0].text
        except Exception as e:
            logger.error(f"Error using Claude: {e}")
            return text
            
    def simplify_text_gemini(self, text: str, target_level: str, words_to_replace: List[str]) -> str:
        """Use Gemini to simplify text"""
        if not self.gemini_model:
            return text
            
        try:
            prompt = f"""Please simplify the following German text to {target_level} level. 
            Replace these words that are above {target_level} level: {', '.join(words_to_replace)}
            Keep the meaning as close as possible to the original.
            
            Original text: {text}
            
            Simplified text:"""
            
            response = self.gemini_model.generate_content(prompt)
            return response.text
        except Exception as e:
            logger.error(f"Error using Gemini: {e}")
            return text

def create_leveled_text(analyzer: GermanLanguageAnalyzer, text: str, target_level: str, 
                       ai_service: Optional[AIService] = None, ai_model: str = None) -> str:
    """Create a simplified version of the text without words above the target level"""
    analysis = analyzer.analyze_text(text, target_level)
    
    # Get all words above level
    words_to_replace = []
    for level_words in analysis['words_above_level'].values():
        words_to_replace.extend([w['lemma'] for w in level_words])
    
    if ai_service and ai_model and words_to_replace:
        # Use AI to simplify
        if ai_model == "Claude":
            return ai_service.simplify_text_claude(text, target_level, words_to_replace)
        elif ai_model == "Gemini":
            return ai_service.simplify_text_gemini(text, target_level, words_to_replace)
    
    # Fallback: Simple removal of difficult words
    doc = analysis['doc']
    tokens = []
    
    for token in doc:
        lemma = token.lemma_ if token.lemma_ != "-PRON-" else token.text
        word_level = analyzer.get_word_level(lemma)
        
        if word_level and analyzer.is_above_level(word_level, target_level):
            # Skip the word or replace with placeholder
            tokens.append("[...]")
        else:
            tokens.append(token.text)
            
    # Reconstruct text with proper spacing
    result = ""
    for i, token in enumerate(tokens):
        if i > 0 and not token in ".,;:!?" and tokens[i-1] != "[...]":
            result += " "
        result += token
        
    return result

def create_word_lists(analyzer: GermanLanguageAnalyzer, analysis_results: Dict, 
                     target_language: str, ai_service: Optional[AIService] = None,
                     ai_model: str = "None") -> pd.DataFrame:
    """Create word lists with translations for words above the target level"""
    translation_service = TranslationService(ai_service, ai_model)
    
    # Collect all words that need translation
    all_words_to_translate = []
    word_info_map = {}
    
    for level, words in analysis_results['words_above_level'].items():
        for word_info in words:
            lemma = word_info['lemma']
            all_words_to_translate.append(lemma)
            if lemma not in word_info_map:
                word_info_map[lemma] = []
            word_info_map[lemma].append((word_info, level))
    
    # Batch translate all words at once for efficiency
    if all_words_to_translate:
        translations = translation_service.translate_batch(all_words_to_translate, target_language)
    else:
        translations = {}
    
    # Build the word data
    word_data = []
    for level, words in analysis_results['words_above_level'].items():
        for word_info in words:
            lemma = word_info['lemma']
            translation = translations.get(lemma, translation_service.translate_word(lemma, target_language))
            
            word_data.append({
                'German Word': word_info['original'],
                'Lemma': lemma,
                'Part of Speech': word_info['pos'],
                'Level': level,
                'Translation': translation
            })
            
    return pd.DataFrame(word_data)

def create_download_link(data: str, filename: str, link_text: str) -> str:
    """Create a download link for the results"""
    b64 = base64.b64encode(data.encode()).decode()
    return f'<a href="data:file/txt;base64,{b64}" download="{filename}">{link_text}</a>'

def check_for_existing_files() -> Dict[str, bool]:
    """Check if vocabulary and stopword files exist in the deployment environment"""
    files_status = {
        'A1': os.path.exists('A1.csv'),
        'A2': os.path.exists('A2.csv'),
        'B1': os.path.exists('B1.csv'),
        'B2': os.path.exists('B2.csv'),
        'C1': os.path.exists('C1_withduplicates.csv'),
        'stopwords': os.path.exists('german_stopwords_plain.txt')
    }
    return files_status

def load_existing_files(analyzer: GermanLanguageAnalyzer) -> bool:
    """Try to load existing vocabulary and stopword files"""
    try:
        # Initialize core words
        analyzer.initialize_core_words()
        
        # Check and load stopwords
        if os.path.exists('german_stopwords_plain.txt'):
            analyzer.load_stopwords('german_stopwords_plain.txt')
            logger.info("Loaded existing stopwords file")
        
        # Check and load word lists
        file_mapping = {}
        for level in ['A1', 'A2', 'B1', 'B2']:
            if os.path.exists(f'{level}.csv'):
                file_mapping[level] = f'{level}.csv'
        
        # Special case for C1
        if os.path.exists('C1_withduplicates.csv'):
            file_mapping['C1'] = 'C1_withduplicates.csv'
        
        if file_mapping:
            analyzer.load_word_lists(file_mapping)
            logger.info(f"Loaded {len(analyzer.word_levels)} words from existing files")
            return True
        
        return False
        
    except Exception as e:
        logger.error(f"Error loading existing files: {e}")
        return False

# Main Streamlit App
def main():
    st.title("🇩🇪 German Language Analyzer")
    st.markdown("Analyze German texts based on CEFR levels (A1-C1)")
    
    # Initialize analyzer if not already done
    if st.session_state.analyzer is None:
        st.session_state.analyzer = GermanLanguageAnalyzer()
        
    analyzer = st.session_state.analyzer
    ai_service = AIService()
    
    # Check for existing files and load them automatically
    if not st.session_state.files_loaded:
        with st.spinner("Checking for vocabulary files..."):
            files_status = check_for_existing_files()
            all_files_exist = all(files_status.values())
            
            if all_files_exist:
                # All files exist, load them automatically
                if load_existing_files(analyzer):
                    st.session_state.files_loaded = True
                    st.success(f"✅ Automatically loaded vocabulary files! ({len(analyzer.word_levels)} unique words)")
                else:
                    st.error("❌ Error loading existing files. Please upload manually.")
            else:
                # Some files are missing, show which ones
                missing_files = [name for name, exists in files_status.items() if not exists]
                st.warning(f"⚠️ Missing files: {', '.join(missing_files)}. Please upload them below.")
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # API Keys section
        st.subheader("🔑 API Keys (Optional)")
        claude_api_key = st.text_input("Claude API Key", type="password", 
                                      help="Enter your Claude API key for AI-powered analysis")
        gemini_api_key = st.text_input("Gemini API Key", type="password",
                                      help="Enter your Gemini API key for AI-powered analysis")
        
        if claude_api_key:
            if ai_service.initialize_claude(claude_api_key):
                st.success("✅ Claude API initialized")
            else:
                st.error("❌ Failed to initialize Claude API")
                
        if gemini_api_key:
            if ai_service.initialize_gemini(gemini_api_key):
                st.success("✅ Gemini API initialized")
            else:
                st.error("❌ Failed to initialize Gemini API")
        
        st.divider()
        
        # Only show file upload section if files weren't loaded automatically
        if not st.session_state.files_loaded:
            st.subheader("📁 Upload Missing Word Lists")
            
            # Check which files are missing
            files_status = check_for_existing_files()
            
            uploaded_files = {}
            levels = ['A1', 'A2', 'B1', 'B2', 'C1']
            
            for level in levels:
                file_key = level if level != 'C1' else 'C1'
                if not files_status.get(file_key, False):
                    file = st.file_uploader(f"Upload {level} word list (CSV)", type=['csv'], key=f"{level}_file")
                    if file:
                        uploaded_files[level] = file
                else:
                    st.success(f"✅ {level} file already exists")
                        
            # Upload stopwords file if missing
            if not files_status.get('stopwords', False):
                stopwords_file = st.file_uploader("Upload German stopwords (TXT)", type=['txt'], key="stopwords_file")
            else:
                st.success("✅ Stopwords file already exists")
                stopwords_file = None
            
            # Load files button
            if st.button("Load Uploaded Files", disabled=st.session_state.files_loaded):
                with st.spinner("Loading word lists..."):
                    # Initialize core words
                    analyzer.initialize_core_words()
                    
                    # Load existing stopwords or uploaded one
                    if files_status.get('stopwords', False):
                        analyzer.load_stopwords('german_stopwords_plain.txt')
                    elif stopwords_file:
                        stopwords_content = stopwords_file.read().decode('utf-8')
                        # Save temporarily and load
                        with open("temp_stopwords.txt", "w", encoding='utf-8') as f:
                            f.write(stopwords_content)
                        analyzer.load_stopwords("temp_stopwords.txt")
                        os.remove("temp_stopwords.txt")
                        
                    # Load word lists (both existing and uploaded)
                    file_mapping = {}
                    
                    # First, add existing files
                    for level in ['A1', 'A2', 'B1', 'B2']:
                        if os.path.exists(f'{level}.csv'):
                            file_mapping[level] = f'{level}.csv'
                    if os.path.exists('C1_withduplicates.csv'):
                        file_mapping['C1'] = 'C1_withduplicates.csv'
                    
                    # Then, add uploaded files
                    for level, file in uploaded_files.items():
                        if file:
                            # Save temporarily and load
                            df = pd.read_csv(file)
                            temp_path = f"temp_{level}.csv"
                            df.to_csv(temp_path, index=False)
                            file_mapping[level] = temp_path
                            
                    analyzer.load_word_lists(file_mapping)
                    
                    # Clean up temp files
                    for level, path in file_mapping.items():
                        if path.startswith('temp_'):
                            os.remove(path)
                            
                    st.session_state.files_loaded = True
                    st.success(f"✅ Loaded {len(analyzer.word_levels)} unique words")
                    st.rerun()
        else:
            # Files are loaded, show status
            st.success("✅ All vocabulary files loaded")
            st.info(f"Total words in database: {len(analyzer.word_levels)}")
            
            # Option to reload files
            if st.button("🔄 Reload Files"):
                st.session_state.files_loaded = False
                st.session_state.analyzer = GermanLanguageAnalyzer()
                st.rerun()
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("📝 Input Text")
        
        # Text input options
        input_method = st.radio("Choose input method:", ["Type/Paste Text", "Upload File"])
        
        if input_method == "Type/Paste Text":
            text_input = st.text_area("Enter German text:", height=300,
                                     placeholder="Paste or type your German text here...")
        else:
            uploaded_text_file = st.file_uploader("Upload text file", type=['txt'])
            if uploaded_text_file:
                text_input = uploaded_text_file.read().decode('utf-8')
                st.text_area("Uploaded text:", text_input, height=300, disabled=True)
            else:
                text_input = ""
    
    with col2:
        st.header("🎯 Analysis Settings")
        
        # Target level selection
        target_level = st.selectbox("Select target CEFR level:", 
                                   ['A1', 'A2', 'B1', 'B2', 'C1'])
        
        # Analysis mode
        analysis_mode = st.radio("Select analysis mode:",
                                ["Leveling", "Labeling"])
        
        if analysis_mode == "Labeling":
            # Translation language selection
            target_language = st.selectbox("Select translation language:",
                                          ["English", "French", "Spanish", 
                                           "Italian", "Polish", "Russian"])
            
            # Show translation method info
            if ai_model != "None":
                st.info(f"🤖 Translations will use {ai_model}")
            else:
                st.warning("💡 Enable AI for better translations")
        else:
            target_language = None
            
        # AI model selection (only if API keys are provided)
        ai_models = ["None"]
        if claude_api_key:
            ai_models.append("Claude")
        if gemini_api_key:
            ai_models.append("Gemini")
            
        if len(ai_models) > 1:
            ai_model = st.selectbox("Select AI model for analysis:", ai_models,
                                  help="AI models improve text simplification and provide accurate translations")
        else:
            ai_model = "None"
    
    # Analyze button
    if st.button("🔍 Analyze Text", type="primary"):
        if not text_input:
            st.error("Please enter some text to analyze.")
        elif not st.session_state.files_loaded:
            st.error("Please load word lists first. Check the sidebar to upload missing files.")
        else:
            with st.spinner("Analyzing text..."):
                try:
                    # Perform analysis
                    analysis_results = analyzer.analyze_text(text_input, target_level)
                    st.session_state.analysis_results = analysis_results
                    st.session_state.processed_text = text_input
                    
                    # Display results
                    st.success("✅ Analysis complete!")
                    
                    # Statistics
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Total Words", analysis_results['total_words'])
                    with col2:
                        total_above = sum(len(words) for words in analysis_results['words_above_level'].values())
                        st.metric("Words Above Level", total_above)
                    with col3:
                        st.metric("Named Entities Skipped", len(analysis_results['skipped_entities']))
                    
                    # Show results based on mode
                    if analysis_mode == "Leveling":
                        st.header("📄 Leveled Text")
                        
                        # Create simplified text
                        if ai_model != "None":
                            leveled_text = create_leveled_text(analyzer, text_input, target_level, 
                                                              ai_service, ai_model)
                        else:
                            leveled_text = create_leveled_text(analyzer, text_input, target_level)
                            
                        st.text_area("Simplified text:", leveled_text, height=300)
                        
                        # Download button
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        filename = f"leveled_text_{target_level}_{timestamp}.txt"
                        st.download_button(
                            label="📥 Download Leveled Text",
                            data=leveled_text,
                            file_name=filename,
                            mime="text/plain"
                        )
                        
                    else:  # Labeling mode
                        st.header("📋 Word Lists")
                        
                        # Show translation progress
                        with st.spinner(f"Translating words to {target_language} using {ai_model if ai_model != 'None' else 'basic translation'}..."):
                            # Create word lists with translations
                            word_df = create_word_lists(analyzer, analysis_results, target_language,
                                                       ai_service if ai_model != "None" else None, ai_model)
                        
                        if not word_df.empty:
                            # Show translation quality info
                            if ai_model != "None":
                                st.success(f"✅ Translations completed using {ai_model}")
                            else:
                                st.info("ℹ️ Basic translations provided. Enable AI for more accurate translations.")
                            
                            # Display word lists
                            st.dataframe(word_df, use_container_width=True)
                            
                            # Group by level
                            st.subheader("Words by Level")
                            for level in sorted(word_df['Level'].unique()):
                                level_words = word_df[word_df['Level'] == level]
                                with st.expander(f"Level {level} ({len(level_words)} words)"):
                                    st.dataframe(level_words)
                            
                            # Download button
                            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                            csv_data = word_df.to_csv(index=False)
                            filename = f"word_list_{target_level}_{target_language}_{timestamp}.csv"
                            st.download_button(
                                label="📥 Download Word List (CSV)",
                                data=csv_data,
                                file_name=filename,
                                mime="text/csv"
                            )
                        else:
                            st.info("No words found above the selected level.")
                            
                except Exception as e:
                    st.error(f"An error occurred during analysis: {str(e)}")
                    logger.error(f"Analysis error: {e}", exc_info=True)
    
    # Footer
    st.divider()
    st.markdown("""
    ### 📖 Instructions
    1. **Upload word lists** for each CEFR level (A1-C1) in the sidebar
    2. **Enter or upload** your German text
    3. **Select the target level** (e.g., B1)
    4. **Choose analysis mode**:
       - **Leveling**: Creates a simplified version without words above the target level
       - **Labeling**: Creates word lists with translations for words above the target level
    5. **Click Analyze** to process the text
    6. **Download** your results
    
    ### ℹ️ Notes
    - Named entities and core German words are automatically excluded from analysis
    - For better results with Leveling mode, provide API keys for Claude or Gemini
    - Translation feature requires internet connection (currently using mock translations)
    """)

if __name__ == "__main__":
    main()
