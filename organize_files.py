#!/usr/bin/env python3
"""
organize_files.py - Help organize vocabulary files into the expected structure
"""

import os
import shutil
from pathlib import Path

def organize_files():
    """Organize vocabulary files into the expected directory structure"""
    print("📁 German Language Analyzer - File Organization Helper")
    print("=" * 50)
    
    # Create vocabulary directory if it doesn't exist
    vocab_dir = Path("vocabulary")
    if not vocab_dir.exists():
        vocab_dir.mkdir()
        print("✅ Created vocabulary/ directory")
    else:
        print("ℹ️  vocabulary/ directory already exists")
    
    # Map of expected files and possible locations
    vocabulary_files = {
        'A1.csv': ['A1.csv', './A1.csv', '../A1.csv'],
        'A2.csv': ['A2.csv', './A2.csv', '../A2.csv'],
        'B1.csv': ['B1.csv', './B1.csv', '../B1.csv'],
        'B2.csv': ['B2.csv', './B2.csv', '../B2.csv'],
        'C1_withduplicates.csv': ['C1_withduplicates.csv', './C1_withduplicates.csv', 
                                  '../C1_withduplicates.csv', 'C1.csv', './C1.csv']
    }
    
    moved_files = []
    already_in_place = []
    not_found = []
    
    # Check and move vocabulary files
    print("\n📋 Organizing vocabulary files...")
    for target_name, possible_paths in vocabulary_files.items():
        target_path = vocab_dir / target_name
        
        if target_path.exists():
            already_in_place.append(target_name)
            continue
            
        # Look for the file in possible locations
        found = False
        for possible_path in possible_paths:
            source = Path(possible_path)
            if source.exists() and source.is_file():
                # Ask before moving
                response = input(f"Found {source}. Move to vocabulary/{target_name}? (y/n): ")
                if response.lower() == 'y':
                    shutil.copy2(source, target_path)
                    moved_files.append((str(source), str(target_path)))
                    print(f"  ✅ Moved {source} → vocabulary/{target_name}")
                    found = True
                    break
                else:
                    print(f"  ⏭️  Skipped {source}")
                    found = True
                    break
        
        if not found:
            not_found.append(target_name)
    
    # Check for stopwords file
    print("\n📄 Checking stopwords file...")
    stopwords_target = Path("german_stopwords_plain.txt")
    if not stopwords_target.exists():
        # Look in common locations
        possible_stopwords = [
            'german_stopwords_plain.txt',
            './german_stopwords_plain.txt',
            '../german_stopwords_plain.txt',
            'stopwords.txt',
            'german_stopwords.txt'
        ]
        
        for possible_path in possible_stopwords:
            source = Path(possible_path)
            if source.exists() and source != stopwords_target:
                response = input(f"Found {source}. Use as stopwords file? (y/n): ")
                if response.lower() == 'y':
                    shutil.copy2(source, stopwords_target)
                    print(f"  ✅ Copied {source} → {stopwords_target}")
                    break
    else:
        print("  ✅ german_stopwords_plain.txt already in place")
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Summary:")
    
    if already_in_place:
        print(f"\n✅ Already in place ({len(already_in_place)} files):")
        for f in already_in_place:
            print(f"  • vocabulary/{f}")
    
    if moved_files:
        print(f"\n✅ Moved ({len(moved_files)} files):")
        for source, target in moved_files:
            print(f"  • {source} → {target}")
    
    if not_found:
        print(f"\n❌ Not found ({len(not_found)} files):")
        for f in not_found:
            print(f"  • {f}")
        print("\nYou'll need to add these files manually to the vocabulary/ directory")
    
    # Final check
    print("\n" + "=" * 50)
    print("Running verification...")
    os.system("python verify_setup.py")

if __name__ == "__main__":
    organize_files()
