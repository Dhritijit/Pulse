"""
Taxonomy-based topic categorization with keyword matching and stemming
Maps reviews to predefined categories using keyword matching
"""

import pandas as pd
import numpy as np
import logging
import re
from collections import defaultdict
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize
import nltk

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)

class TaxonomyMatcher:
    def __init__(self, taxonomy_file_path=None):
        self.setup_logging()
        self.stemmer = PorterStemmer()
        self.taxonomies = {}
        self.stemmed_keywords = {}
        
        if taxonomy_file_path:
            self.load_taxonomies(taxonomy_file_path)
    
    def setup_logging(self):
        """Setup logging configuration"""
        self.logger = logging.getLogger(__name__)
    
    def load_taxonomies(self, file_path):
        """Load taxonomies from Excel file"""
        self.logger.info(f"Loading taxonomies from: {file_path}")
        
        try:
            # Read all sheets from the Excel file
            excel_file = pd.ExcelFile(file_path)
            
            for sheet_name in excel_file.sheet_names:
                if sheet_name == 'Overview':
                    continue
                
                df = pd.read_excel(file_path, sheet_name=sheet_name)
                
                # Process each taxonomy in the sheet
                for idx, row in df.iterrows():
                    if pd.isna(row.get('Taxonomy Name')):
                        continue
                    
                    high_level = str(row.get('High Level Category', '')).strip()
                    taxonomy_name = str(row.get('Taxonomy Name', '')).strip()
                    intent = str(row.get('Taxonomy Intent', '')).strip()
                    phrases = str(row.get('Phrases', '')).strip()
                    
                    if not taxonomy_name or not phrases:
                        continue
                    
                    # Parse phrases (comma-separated)
                    keywords = [kw.strip().lower() for kw in phrases.split(',') if kw.strip()]
                    
                    # Create taxonomy key
                    taxonomy_key = f"{sheet_name}_{taxonomy_name}"
                    
                    self.taxonomies[taxonomy_key] = {
                        'domain': sheet_name,
                        'high_level_category': high_level,
                        'name': taxonomy_name,
                        'intent': intent,
                        'keywords': keywords,
                        'original_phrases': phrases
                    }
                    
                    # Store stemmed versions of keywords for better matching
                    stemmed = [self.stem_phrase(kw) for kw in keywords]
                    self.stemmed_keywords[taxonomy_key] = stemmed
            
            self.logger.info(f"Loaded {len(self.taxonomies)} taxonomies from {len(excel_file.sheet_names)} sheets")
            return True
            
        except Exception as e:
            self.logger.error(f"Error loading taxonomies: {e}")
            return False
    
    def stem_phrase(self, phrase):
        """Stem a phrase (words in phrase)"""
        try:
            words = word_tokenize(phrase.lower())
            stemmed = ' '.join([self.stemmer.stem(word) for word in words])
            return stemmed
        except Exception as e:
            self.logger.error(f"Error stemming phrase '{phrase}': {e}")
            return phrase.lower()
    
    def match_review_to_taxonomies(self, review_text, top_n=3, threshold=0.1):
        """
        Match a review to taxonomies based on keyword presence
        Returns top N matching categories with scores
        """
        if not review_text or not self.taxonomies:
            return []
        
        review_text_lower = review_text.lower()
        review_stemmed = self.stem_phrase(review_text)
        
        scores = {}
        
        for taxonomy_key, taxonomy_data in self.taxonomies.items():
            score = 0
            matched_keywords = []
            
            # Check original keywords (exact/substring match)
            for keyword in taxonomy_data['keywords']:
                if keyword in review_text_lower:
                    score += 1
                    matched_keywords.append(keyword)
            
            # Check stemmed keywords for fuzzy matching
            for stemmed_kw in self.stemmed_keywords[taxonomy_key]:
                if stemmed_kw in review_stemmed and stemmed_kw not in matched_keywords:
                    score += 0.5  # Lower weight for stemmed matches
            
            if score > 0:
                scores[taxonomy_key] = {
                    'score': score,
                    'taxonomy': taxonomy_data,
                    'matched_keywords': matched_keywords
                }
        
        # Sort by score and return top N
        sorted_matches = sorted(scores.items(), key=lambda x: x[1]['score'], reverse=True)
        
        # Filter by threshold
        min_score = threshold * 10  # Adjust based on keyword count
        
        results = []
        for taxonomy_key, data in sorted_matches[:top_n]:
            if data['score'] >= min_score:
                results.append({
                    'taxonomy_key': taxonomy_key,
                    'domain': data['taxonomy']['domain'],
                    'category': data['taxonomy']['name'],
                    'high_level_category': data['taxonomy']['high_level_category'],
                    'score': data['score'],
                    'matched_keywords': data['matched_keywords'],
                    'confidence': min(data['score'] / 10, 1.0)  # Normalize to 0-1
                })
        
        return results
    
    def categorize_reviews_batch(self, reviews, top_n=3):
        """Categorize multiple reviews"""
        self.logger.info(f"Categorizing {len(reviews)} reviews using taxonomies")
        
        results = []
        for review in reviews:
            review_text = review.get('text', '')
            matches = self.match_review_to_taxonomies(review_text, top_n=top_n)
            results.append(matches)
        
        return results
    
    def get_taxonomy_statistics(self, categorization_results):
        """Get statistics about taxonomy matches"""
        stats = {
            'total_reviews': len(categorization_results),
            'reviews_with_matches': 0,
            'reviews_without_matches': 0,
            'taxonomy_counts': defaultdict(int),
            'domain_counts': defaultdict(int),
            'avg_matches_per_review': 0
        }
        
        total_matches = 0
        
        for matches in categorization_results:
            if matches:
                stats['reviews_with_matches'] += 1
                total_matches += len(matches)
                
                for match in matches:
                    stats['taxonomy_counts'][match['category']] += 1
                    stats['domain_counts'][match['domain']] += 1
            else:
                stats['reviews_without_matches'] += 1
        
        if stats['reviews_with_matches'] > 0:
            stats['avg_matches_per_review'] = total_matches / stats['reviews_with_matches']
        
        return stats
    
    def get_available_taxonomies(self):
        """Return list of all available taxonomies"""
        taxonomy_list = []
        
        for key, data in self.taxonomies.items():
            taxonomy_list.append({
                'key': key,
                'domain': data['domain'],
                'name': data['name'],
                'high_level': data['high_level_category'],
                'keyword_count': len(data['keywords'])
            })
        
        return taxonomy_list