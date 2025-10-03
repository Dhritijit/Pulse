"""
File processor for uploaded review files (Excel/CSV)
Handles parsing and validation of user-uploaded review data
"""

import pandas as pd
import numpy as np
import logging
from datetime import datetime
import re

class FileProcessor:
    def __init__(self):
        self.setup_logging()
        self.max_reviews = 2000
    
    def setup_logging(self):
        """Setup logging configuration"""
        self.logger = logging.getLogger(__name__)
    
    def process_uploaded_file(self, file_path, max_reviews=2000):
        """
        Process uploaded Excel or CSV file
        Returns list of review dictionaries
        """
        self.logger.info(f"Processing uploaded file: {file_path}")
        self.max_reviews = max_reviews
        
        try:
            # Determine file type and read
            if file_path.endswith('.csv'):
                df = pd.read_csv(file_path, encoding='utf-8-sig')
            elif file_path.endswith(('.xlsx', '.xls')):
                df = pd.read_excel(file_path)
            else:
                raise ValueError(f"Unsupported file format. Please upload .csv, .xlsx, or .xls file")
            
            self.logger.info(f"File loaded. Shape: {df.shape}")
            self.logger.info(f"Columns: {df.columns.tolist()}")
            
            # Detect and map columns
            column_mapping = self.detect_columns(df)
            
            if not column_mapping['text_column']:
                raise ValueError("Could not detect review text column. Please ensure your file has a 'Comments' or 'Review' column")
            
            # Extract reviews
            reviews = self.extract_reviews(df, column_mapping)
            
            # Limit to max reviews
            if len(reviews) > self.max_reviews:
                self.logger.warning(f"File contains {len(reviews)} reviews. Limiting to {self.max_reviews}")
                reviews = reviews[:self.max_reviews]
            
            self.logger.info(f"Successfully processed {len(reviews)} reviews from file")
            return reviews
            
        except Exception as e:
            self.logger.error(f"Error processing file: {e}")
            raise
    
    def detect_columns(self, df):
        """
        Intelligently detect which columns contain review text, dates, ratings, etc.
        """
        column_mapping = {
            'text_column': None,
            'date_column': None,
            'rating_column': None,
            'source_column': None
        }
        
        columns_lower = {col.lower(): col for col in df.columns}
        
        # Detect text/comment column
        text_patterns = ['comment', 'review', 'text', 'feedback', 'description', 'message', 'content']
        for pattern in text_patterns:
            for col_lower, col_original in columns_lower.items():
                if pattern in col_lower:
                    column_mapping['text_column'] = col_original
                    break
            if column_mapping['text_column']:
                break
        
        # If still not found, use first column with long text
        if not column_mapping['text_column']:
            for col in df.columns:
                if df[col].dtype == 'object':
                    avg_length = df[col].astype(str).str.len().mean()
                    if avg_length > 50:  # Likely review text
                        column_mapping['text_column'] = col
                        break
        
        # Detect date column
        date_patterns = ['date', 'time', 'created', 'posted', 'timestamp']
        for pattern in date_patterns:
            for col_lower, col_original in columns_lower.items():
                if pattern in col_lower:
                    column_mapping['date_column'] = col_original
                    break
            if column_mapping['date_column']:
                break
        
        # Detect rating column
        rating_patterns = ['rating', 'score', 'star', 'rate']
        for pattern in rating_patterns:
            for col_lower, col_original in columns_lower.items():
                if pattern in col_lower:
                    column_mapping['rating_column'] = col_original
                    break
            if column_mapping['rating_column']:
                break
        
        # Detect source column
        source_patterns = ['source', 'platform', 'site', 'channel', 'origin']
        for pattern in source_patterns:
            for col_lower, col_original in columns_lower.items():
                if pattern in col_lower:
                    column_mapping['source_column'] = col_original
                    break
            if column_mapping['source_column']:
                break
        
        self.logger.info(f"Column mapping detected: {column_mapping}")
        return column_mapping
    
    def extract_reviews(self, df, column_mapping):
        """Extract reviews from DataFrame based on column mapping"""
        reviews = []
        
        text_col = column_mapping['text_column']
        date_col = column_mapping['date_column']
        rating_col = column_mapping['rating_column']
        source_col = column_mapping['source_column']
        
        for idx, row in df.iterrows():
            # Extract text
            text = str(row[text_col]) if pd.notna(row[text_col]) else ''
            
            # Skip empty reviews
            if not text or text.lower() in ['nan', 'none', '']:
                continue
            
            # Skip very short reviews (likely not real reviews)
            if len(text.strip()) < 10:
                continue
            
            review = {
                'text': text.strip(),
                'rating': None,
                'date': None,
                'source_domain': 'uploaded_file',
                'source_url': 'uploaded_file',
                'reviewer': '',
                'scraped_at': datetime.now().isoformat()
            }
            
            # Extract date if available
            if date_col and pd.notna(row[date_col]):
                try:
                    date_value = pd.to_datetime(row[date_col])
                    review['date'] = date_value.strftime('%Y-%m-%d')
                except:
                    review['date'] = str(row[date_col])
            
            # Extract rating if available
            if rating_col and pd.notna(row[rating_col]):
                try:
                    rating = float(row[rating_col])
                    review['rating'] = rating
                except:
                    # Try to extract number from string
                    rating_str = str(row[rating_col])
                    numbers = re.findall(r'\d+\.?\d*', rating_str)
                    if numbers:
                        review['rating'] = float(numbers[0])
            
            # Extract source if available
            if source_col and pd.notna(row[source_col]):
                review['source_domain'] = str(row[source_col])
            
            reviews.append(review)
        
        return reviews
    
    def validate_file(self, file_path):
        """
        Validate uploaded file before processing
        Returns (is_valid, error_message)
        """
        try:
            # Check file size (max 50MB)
            import os
            file_size = os.path.getsize(file_path)
            if file_size > 50 * 1024 * 1024:  # 50MB
                return False, "File size exceeds 50MB limit"
            
            # Try to read file
            if file_path.endswith('.csv'):
                df = pd.read_csv(file_path, nrows=5)
            elif file_path.endswith(('.xlsx', '.xls')):
                df = pd.read_excel(file_path, nrows=5)
            else:
                return False, "Invalid file format. Please upload .csv or .xlsx file"
            
            # Check if file has any data
            if df.empty:
                return False, "File is empty"
            
            # Check if there's at least one text column
            text_columns = []
            for col in df.columns:
                if df[col].dtype == 'object':
                    avg_length = df[col].astype(str).str.len().mean()
                    if avg_length > 20:
                        text_columns.append(col)
            
            if not text_columns:
                return False, "No text columns detected. Please ensure your file contains review text"
            
            return True, "File is valid"
            
        except Exception as e:
            return False, f"Error validating file: {str(e)}"
    
    def get_file_preview(self, file_path, num_rows=5):
        """Get preview of uploaded file"""
        try:
            if file_path.endswith('.csv'):
                df = pd.read_csv(file_path, nrows=num_rows)
            else:
                df = pd.read_excel(file_path, nrows=num_rows)
            
            return df.to_dict('records'), df.columns.tolist()
        except Exception as e:
            self.logger.error(f"Error getting file preview: {e}")
            return [], []