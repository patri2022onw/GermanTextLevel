#!/usr/bin/env python3
"""
Command-line interface for German Language Analyzer
Supports batch processing of multiple files
"""

import argparse
import os
import sys
import json
from pathlib import Path
import pandas as pd
from typing import List, Dict, Optional
import logging
from datetime import datetime

# Import the main analyzer components
# Note: Ensure the main app components are in a module structure
try:
    from german_analyzer import GermanLanguageAnalyzer, create_leveled_text, create_word_lists, AIService, TranslationService
except ImportError:
    print("Error: Could not import analyzer components. Ensure the main app is properly structured.")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class BatchProcessor:
    """Batch processor for German text analysis"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.analyzer = GermanLanguageAnalyzer()
        self.ai_service = AIService()
        self.config = self.load_config(config_path) if config_path else {}
        self.setup_ai_services()
        
    def load_config(self, config_path: str) -> Dict:
        """Load configuration from JSON file"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            return {}
    
    def setup_ai_services(self):
        """Setup AI services from config or environment"""
        # Try to get API keys from config or environment
        claude_key = self.config.get('ai_services', {}).get('claude', {}).get('api_key') or os.getenv('CLAUDE_API_KEY')
        gemini_key = self.config.get('ai_services', {}).get('gemini', {}).get('api_key') or os.getenv('GEMINI_API_KEY')
        
        if claude_key:
            if self.ai_service.initialize_claude(claude_key):
                logger.info("Claude API initialized for batch processing")
        
        if gemini_key:
            if self.ai_service.initialize_gemini(gemini_key):
                logger.info("Gemini API initialized for batch processing")
            
    def setup_analyzer(self, word_lists_dir: str = "vocabulary", stopwords_path: str = "german_stopwords_plain.txt"):
        """Setup the analyzer with word lists and stopwords"""
        # Initialize core words
        self.analyzer.initialize_core_words()
        
        # Load stopwords
        if os.path.exists(stopwords_path):
            self.analyzer.load_stopwords(stopwords_path)
            logger.info(f"Loaded stopwords from {stopwords_path}")
        else:
            logger.warning(f"Stopwords file not found: {stopwords_path}")
            
        # Load word lists from vocabulary directory
        file_mapping = {
            'A1': os.path.join(word_lists_dir, 'A1.csv'),
            'A2': os.path.join(word_lists_dir, 'A2.csv'),
            'B1': os.path.join(word_lists_dir, 'B1.csv'),
            'B2': os.path.join(word_lists_dir, 'B2.csv'),
            'C1': os.path.join(word_lists_dir, 'C1_withduplicates.csv')
        }
        
        # Filter existing files
        existing_files = {level: path for level, path in file_mapping.items() 
                         if os.path.exists(path)}
        
        if existing_files:
            self.analyzer.load_word_lists(existing_files)
            logger.info(f"Loaded {len(self.analyzer.word_levels)} unique words")
        else:
            logger.error("No word list files found!")
            
    def process_file(self, input_path: str, output_dir: str, 
                    target_level: str, mode: str = 'leveling',
                    target_language: str = 'English',
                    ai_model: str = 'None') -> bool:
        """Process a single file"""
        try:
            # Read input file
            with open(input_path, 'r', encoding='utf-8') as f:
                text = f.read()
                
            logger.info(f"Processing {input_path} (mode: {mode}, level: {target_level}, AI: {ai_model})")
            
            # Analyze text
            analysis_results = self.analyzer.analyze_text(text, target_level)
            
            # Generate output based on mode
            if mode == 'leveling':
                # Use AI if available and requested
                if ai_model != 'None' and (
                    (ai_model == 'Claude' and self.ai_service.claude_client) or
                    (ai_model == 'Gemini' and self.ai_service.gemini_model)
                ):
                    output_text = create_leveled_text(self.analyzer, text, target_level, 
                                                    self.ai_service, ai_model)
                else:
                    output_text = create_leveled_text(self.analyzer, text, target_level)
                    
                output_filename = f"{Path(input_path).stem}_leveled_{target_level}.txt"
                output_path = os.path.join(output_dir, output_filename)
                
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(output_text)
                    
            else:  # labeling mode
                # Use AI for translations if available
                ai_to_use = self.ai_service if ai_model != 'None' else None
                word_df = create_word_lists(self.analyzer, analysis_results, target_language,
                                          ai_to_use, ai_model)
                output_filename = f"{Path(input_path).stem}_words_{target_level}_{target_language}.csv"
                output_path = os.path.join(output_dir, output_filename)
                
                word_df.to_csv(output_path, index=False)
                
            logger.info(f"Output saved to {output_path}")
            
            # Save analysis report
            report_filename = f"{Path(input_path).stem}_report_{target_level}.json"
            report_path = os.path.join(output_dir, report_filename)
            
            report = {
                'input_file': input_path,
                'target_level': target_level,
                'mode': mode,
                'ai_model': ai_model,
                'timestamp': datetime.now().isoformat(),
                'statistics': {
                    'total_words': analysis_results['total_words'],
                    'words_above_level': sum(len(words) for words in 
                                           analysis_results['words_above_level'].values()),
                    'skipped_entities': len(analysis_results['skipped_entities'])
                },
                'words_by_level': {level: len(words) for level, words in 
                                 analysis_results['words_above_level'].items()}
            }
            
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
                
            return True
            
        except Exception as e:
            logger.error(f"Error processing {input_path}: {e}")
            return False
            
    def process_directory(self, input_dir: str, output_dir: str,
                         target_level: str, mode: str = 'leveling',
                         target_language: str = 'English',
                         pattern: str = '*.txt',
                         ai_model: str = 'None') -> Dict[str, bool]:
        """Process all matching files in a directory"""
        results = {}
        
        # Find all matching files
        input_path = Path(input_dir)
        files = list(input_path.glob(pattern))
        
        if not files:
            logger.warning(f"No files matching pattern '{pattern}' found in {input_dir}")
            return results
            
        logger.info(f"Found {len(files)} files to process")
        
        # Process each file
        for file_path in files:
            success = self.process_file(
                str(file_path), output_dir, target_level, 
                mode, target_language, ai_model
            )
            results[str(file_path)] = success
            
        # Generate summary report
        summary_path = os.path.join(output_dir, 'batch_summary.json')
        summary = {
            'timestamp': datetime.now().isoformat(),
            'input_directory': input_dir,
            'pattern': pattern,
            'target_level': target_level,
            'mode': mode,
            'ai_model': ai_model,
            'total_files': len(files),
            'successful': sum(1 for success in results.values() if success),
            'failed': sum(1 for success in results.values() if not success),
            'results': results
        }
        
        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
            
        return results

def main():
    parser = argparse.ArgumentParser(
        description='German Language Analyzer - Batch Processing Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process a single file (uses default vocabulary/ directory)
  python batch_processor.py -i text.txt -o output/ -l B1
  
  # Process all txt files in a directory
  python batch_processor.py -i texts/ -o output/ -l A2 --batch
  
  # Generate word lists with AI translations
  python batch_processor.py -i text.txt -o output/ -l B2 -m labeling -t French --ai claude
  
  # Use custom word lists directory (if not using default)
  python batch_processor.py -i text.txt -o output/ -l B1 -w custom_vocab/
        """
    )
    
    # Input/Output arguments
    parser.add_argument('-i', '--input', required=True,
                       help='Input file or directory path')
    parser.add_argument('-o', '--output', required=True,
                       help='Output directory path')
    
    # Analysis settings
    parser.add_argument('-l', '--level', required=True,
                       choices=['A1', 'A2', 'B1', 'B2', 'C1'],
                       help='Target CEFR level')
    parser.add_argument('-m', '--mode', default='leveling',
                       choices=['leveling', 'labeling'],
                       help='Analysis mode (default: leveling)')
    parser.add_argument('-t', '--target-language', default='English',
                       choices=['English', 'French', 'Spanish', 'Italian', 'Polish', 'Russian'],
                       help='Target language for translations (default: English)')
    
    # AI settings
    parser.add_argument('--ai', dest='ai_model', default='None',
                       choices=['None', 'Claude', 'Gemini'],
                       help='AI model to use for translations and simplification (default: None)')
    
    # Batch processing
    parser.add_argument('--batch', action='store_true',
                       help='Process all files in input directory')
    parser.add_argument('--pattern', default='*.txt',
                       help='File pattern for batch processing (default: *.txt)')
    
    # Configuration
    parser.add_argument('-w', '--word-lists', default='vocabulary',
                       help='Directory containing word list CSV files (default: vocabulary)')
    parser.add_argument('-s', '--stopwords', default='german_stopwords_plain.txt',
                       help='Path to stopwords file (default: german_stopwords_plain.txt)')
    parser.add_argument('-c', '--config', help='Path to configuration JSON file')
    
    # Logging
    parser.add_argument('-v', '--verbose', action='store_true',
                       help='Enable verbose logging')
    
    args = parser.parse_args()
    
    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Create output directory
    os.makedirs(args.output, exist_ok=True)
    
    # Initialize processor
    processor = BatchProcessor(args.config)
    
    # Setup analyzer
    logger.info("Setting up analyzer...")
    processor.setup_analyzer(args.word_lists, args.stopwords)
    
    # Process files
    if args.batch:
        if not os.path.isdir(args.input):
            logger.error("Batch mode requires input to be a directory")
            sys.exit(1)
            
        results = processor.process_directory(
            args.input, args.output, args.level,
            args.mode, args.target_language, args.pattern, args.ai_model
        )
        
        # Print summary
        successful = sum(1 for success in results.values() if success)
        failed = sum(1 for success in results.values() if not success)
        
        print(f"\nBatch processing complete:")
        print(f"  Total files: {len(results)}")
        print(f"  Successful: {successful}")
        print(f"  Failed: {failed}")
        print(f"  Output directory: {args.output}")
        if args.ai_model != 'None':
            print(f"  AI model used: {args.ai_model}")
        
    else:
        if not os.path.isfile(args.input):
            logger.error(f"Input file not found: {args.input}")
            sys.exit(1)
            
        success = processor.process_file(
            args.input, args.output, args.level,
            args.mode, args.target_language, args.ai_model
        )
        
        if success:
            print(f"\nProcessing complete. Output saved to: {args.output}")
            if args.ai_model != 'None':
                print(f"AI model used: {args.ai_model}")
        else:
            print("\nProcessing failed. Check logs for details.")
            sys.exit(1)

if __name__ == "__main__":
    main()
