# translation_service.py
"""
AI-Powered Translation Service for German Language Analyzer
Uses Claude or Gemini for high-quality, context-aware translations
"""

import logging
from typing import Dict, List, Optional, Tuple
from abc import ABC, abstractmethod
import time
import json

logger = logging.getLogger(__name__)


class TranslationProvider(ABC):
    """Abstract base class for translation providers"""
    
    @abstractmethod
    def translate(self, text: str, source_lang: str, target_lang: str) -> str:
        """Translate text from source language to target language"""
        pass
    
    @abstractmethod
    def translate_batch(self, texts: List[str], source_lang: str, target_lang: str) -> Dict[str, str]:
        """Translate multiple texts efficiently"""
        pass


class ClaudeTranslationProvider(TranslationProvider):
    """Translation provider using Claude AI"""
    
    def __init__(self, claude_client):
        self.client = claude_client
        self.model = "claude-3-sonnet-20240229"
        
    def translate(self, text: str, source_lang: str = 'German', target_lang: str = 'English') -> str:
        """Translate a single word or phrase using Claude"""
        try:
            prompt = f"""Translate the {source_lang} word or phrase "{text}" to {target_lang}.
            Provide ONLY the translation, no explanations or additional text.
            If the word has multiple meanings, provide the most common one used in educational contexts.
            
            {source_lang}: {text}
            {target_lang}:"""
            
            response = self.client.messages.create(
                model=self.model,
                max_tokens=50,
                messages=[{"role": "user", "content": prompt}]
            )
            
            translation = response.content[0].text.strip()
            return translation if translation else text
            
        except Exception as e:
            logger.error(f"Claude translation error: {e}")
            return text
    
    def translate_batch(self, texts: List[str], source_lang: str = 'German', 
                       target_lang: str = 'English') -> Dict[str, str]:
        """Translate multiple texts efficiently using Claude"""
        if not texts:
            return {}
            
        try:
            # Format texts for batch translation
            texts_formatted = '\n'.join([f'{i+1}. "{text}"' for i, text in enumerate(texts)])
            
            prompt = f"""Translate these {source_lang} words to {target_lang}.
            Format your response as a numbered list with ONLY the translations, 
            one per line, in the same order as the input.
            
            {source_lang} words:
            {texts_formatted}
            
            Provide ONLY the {target_lang} translations (numbered):"""
            
            response = self.client.messages.create(
                model=self.model,
                max_tokens=500,
                messages=[{"role": "user", "content": prompt}]
            )
            
            # Parse response
            translations_text = response.content[0].text.strip()
            translation_lines = translations_text.split('\n')
            
            translations = {}
            for i, text in enumerate(texts):
                # Try to extract translation from numbered list
                for line in translation_lines:
                    if line.strip().startswith(f"{i+1}."):
                        # Remove number and clean up
                        translation = line.split('.', 1)[1].strip().strip('"')
                        translations[text] = translation
                        break
                else:
                    # Fallback if parsing fails
                    translations[text] = text
                    
            return translations
            
        except Exception as e:
            logger.error(f"Claude batch translation error: {e}")
            return {text: text for text in texts}


class GeminiTranslationProvider(TranslationProvider):
    """Translation provider using Gemini AI"""
    
    def __init__(self, gemini_model):
        self.model = gemini_model
        
    def translate(self, text: str, source_lang: str = 'German', target_lang: str = 'English') -> str:
        """Translate a single word or phrase using Gemini"""
        try:
            prompt = f"""Translate the {source_lang} word or phrase "{text}" to {target_lang}.
            Provide ONLY the translation, no explanations or additional text.
            If the word has multiple meanings, provide the most common one used in educational contexts.
            
            {source_lang}: {text}
            {target_lang}:"""
            
            response = self.model.generate_content(prompt)
            translation = response.text.strip()
            return translation if translation else text
            
        except Exception as e:
            logger.error(f"Gemini translation error: {e}")
            return text
    
    def translate_batch(self, texts: List[str], source_lang: str = 'German', 
                       target_lang: str = 'English') -> Dict[str, str]:
        """Translate multiple texts efficiently using Gemini"""
        if not texts:
            return {}
            
        try:
            # Format texts for batch translation
            texts_formatted = '\n'.join([f'{i+1}. "{text}"' for i, text in enumerate(texts)])
            
            prompt = f"""Translate these {source_lang} words to {target_lang}.
            Format your response as a numbered list with ONLY the translations, 
            one per line, in the same order as the input.
            
            {source_lang} words:
            {texts_formatted}
            
            Provide ONLY the {target_lang} translations (numbered):"""
            
            response = self.model.generate_content(prompt)
            
            # Parse response
            translations_text = response.text.strip()
            translation_lines = translations_text.split('\n')
            
            translations = {}
            for i, text in enumerate(texts):
                # Try to extract translation from numbered list
                for line in translation_lines:
                    if line.strip().startswith(f"{i+1}."):
                        # Remove number and clean up
                        translation = line.split('.', 1)[1].strip().strip('"')
                        translations[text] = translation
                        break
                else:
                    # Fallback if parsing fails
                    translations[text] = text
                    
            return translations
            
        except Exception as e:
            logger.error(f"Gemini batch translation error: {e}")
            return {text: text for text in texts}


class MockTranslationProvider(TranslationProvider):
    """Mock translation provider for testing and fallback"""
    
    def __init__(self):
        # Common German-English translations for testing
        self.translations = {
            'haus': 'house',
            'buch': 'book',
            'wasser': 'water',
            'arbeiten': 'work',
            'entwickeln': 'develop',
            'gesellschaft': 'society',
            'unwiderruflich': 'irrevocable',
            'paradigma': 'paradigm',
            'erkenntnis': 'insight',
            'bewältigen': 'cope with'
        }
        
    def translate(self, text: str, source_lang: str = 'German', target_lang: str = 'English') -> str:
        """Mock translation - returns formatted text or known translation"""
        text_lower = text.lower()
        
        # Check if we have a known translation
        if text_lower in self.translations and target_lang == 'English':
            return self.translations[text_lower]
            
        # Return formatted mock translation
        lang_code = {
            'English': 'EN',
            'French': 'FR',
            'Spanish': 'ES',
            'Italian': 'IT',
            'Polish': 'PL',
            'Russian': 'RU'
        }.get(target_lang, 'XX')
        
        return f"{text} ({lang_code})"
    
    def translate_batch(self, texts: List[str], source_lang: str = 'German', 
                       target_lang: str = 'English') -> Dict[str, str]:
        """Mock batch translation"""
        return {text: self.translate(text, source_lang, target_lang) for text in texts}


class TranslationService:
    """Main translation service with caching and provider management"""
    
    def __init__(self, ai_service=None, ai_model: str = "None"):
        self.ai_service = ai_service
        self.ai_model = ai_model
        self.translation_cache = {}
        self.provider = None
        self._initialize_provider()
        
    def _initialize_provider(self):
        """Initialize the appropriate translation provider"""
        if self.ai_model == "Claude" and self.ai_service and hasattr(self.ai_service, 'claude_client'):
            if self.ai_service.claude_client:
                self.provider = ClaudeTranslationProvider(self.ai_service.claude_client)
                logger.info("Initialized Claude translation provider")
        elif self.ai_model == "Gemini" and self.ai_service and hasattr(self.ai_service, 'gemini_model'):
            if self.ai_service.gemini_model:
                self.provider = GeminiTranslationProvider(self.ai_service.gemini_model)
                logger.info("Initialized Gemini translation provider")
        else:
            self.provider = MockTranslationProvider()
            logger.info("Using mock translation provider")
            
    def translate_word(self, word: str, target_lang: str, source_lang: str = 'German') -> str:
        """Translate a single word with caching"""
        # Create cache key
        cache_key = f"{word}_{source_lang}_{target_lang}_{self.ai_model}"
        
        # Check cache first
        if cache_key in self.translation_cache:
            return self.translation_cache[cache_key]
            
        # Translate using provider
        translation = self.provider.translate(word, source_lang, target_lang)
        
        # Cache the result
        self.translation_cache[cache_key] = translation
        
        return translation
    
    def translate_batch(self, words: List[str], target_lang: str, 
                       source_lang: str = 'German') -> Dict[str, str]:
        """Translate multiple words efficiently with caching"""
        if not words:
            return {}
            
        # Check cache and separate cached/uncached words
        translations = {}
        uncached_words = []
        
        for word in words:
            cache_key = f"{word}_{source_lang}_{target_lang}_{self.ai_model}"
            if cache_key in self.translation_cache:
                translations[word] = self.translation_cache[cache_key]
            else:
                uncached_words.append(word)
        
        # Batch translate uncached words
        if uncached_words:
            # For efficiency, batch translate if we have many words
            if len(uncached_words) > 5 and not isinstance(self.provider, MockTranslationProvider):
                new_translations = self.provider.translate_batch(uncached_words, source_lang, target_lang)
            else:
                # Translate individually for small batches
                new_translations = {}
                for word in uncached_words:
                    new_translations[word] = self.provider.translate(word, source_lang, target_lang)
            
            # Update translations and cache
            for word, translation in new_translations.items():
                translations[word] = translation
                cache_key = f"{word}_{source_lang}_{target_lang}_{self.ai_model}"
                self.translation_cache[cache_key] = translation
                
        return translations
    
    def clear_cache(self):
        """Clear the translation cache"""
        self.translation_cache.clear()
        logger.info("Translation cache cleared")
        
    def get_cache_stats(self) -> Dict[str, int]:
        """Get cache statistics"""
        return {
            'cache_size': len(self.translation_cache),
            'unique_words': len(set(key.split('_')[0] for key in self.translation_cache)),
            'languages': len(set(key.split('_')[2] for key in self.translation_cache))
        }
    
    def export_cache(self, filepath: str):
        """Export cache to JSON file"""
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self.translation_cache, f, ensure_ascii=False, indent=2)
            logger.info(f"Cache exported to {filepath}")
        except Exception as e:
            logger.error(f"Error exporting cache: {e}")
            
    def import_cache(self, filepath: str):
        """Import cache from JSON file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                imported_cache = json.load(f)
                self.translation_cache.update(imported_cache)
            logger.info(f"Cache imported from {filepath}")
        except Exception as e:
            logger.error(f"Error importing cache: {e}")


# Convenience functions for standalone use
def create_translation_service(ai_service=None, ai_model: str = "None") -> TranslationService:
    """Create a translation service instance"""
    return TranslationService(ai_service, ai_model)


def translate_german_word(word: str, target_language: str = "English", 
                         ai_service=None, ai_model: str = "None") -> str:
    """Convenience function to translate a single German word"""
    service = TranslationService(ai_service, ai_model)
    return service.translate_word(word, target_language)


def translate_german_words(words: List[str], target_language: str = "English",
                          ai_service=None, ai_model: str = "None") -> Dict[str, str]:
    """Convenience function to translate multiple German words"""
    service = TranslationService(ai_service, ai_model)
    return service.translate_batch(words, target_language)


# Example usage
if __name__ == "__main__":
    # Example: Using mock translations
    print("=== Mock Translation Example ===")
    service = TranslationService()
    
    # Single word
    word = "Gesellschaft"
    translation = service.translate_word(word, "English")
    print(f"{word} -> {translation}")
    
    # Batch translation
    words = ["Haus", "entwickeln", "Paradigma", "unwiderruflich"]
    translations = service.translate_batch(words, "French")
    for word, trans in translations.items():
        print(f"{word} -> {trans}")
    
    # Cache stats
    print(f"\nCache stats: {service.get_cache_stats()}")
