"""
Configuration file for Social Media Review Analyzer
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# OpenAI Configuration
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')  # Set this in your .env file
OPENAI_MODEL = "gpt-4"
OPENAI_EMBEDDING_MODEL = "text-embedding-ada-002"

# Scraping Configuration
MAX_REVIEWS_PER_SITE = 5000  # Maximum reviews to scrape per URL
DEFAULT_DELAY = 2  # Change to: 1
RANDOM_DELAY_RANGE = (0.5, 1.5)  # Change to: (0.5, 1.5)
MAX_RETRIES = 3
REQUEST_TIMEOUT = 30

# User Agent Configuration
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0'
]

# Site-specific selectors for common review sites
SITE_SELECTORS = {
    'ambitionbox.com': {
    'review_container': '.review-card, .review-item, [class*="review"]',
    'review_text': '.review-text, .review-content, [class*="review-text"]',
    'rating': '.rating, [class*="rating"], [class*="star"]',
    'reviewer': '.reviewer-name, .review-author, [class*="author"]',
    'date': '.review-date, [class*="date"]',
    'pagination': '.next-page, .pagination-next, [href*="page"]'
    },    
    'trustpilot.com': {
        'review_container': 'article[data-service-review-card-paper]',
        'review_text': 'div[data-service-review-text-typography="true"]',
        'rating': 'div[data-service-review-rating] img',
        'reviewer': 'span[data-consumer-name-typography="true"]',
        'date': 'time',
        'pagination': 'a[data-pagination-button-next-label]'
    },
    'glassdoor.com': {
        'review_container': 'li[data-test="employer-review"]',
        'review_text': '[data-test="reviewBodyText"]',
        'rating': '[data-test="rating"]',
        'reviewer': '[data-test="employee-review-reviewer"]',
        'date': '[data-test="review-date"]',
        'pagination': '[data-test="pagination-next"]'
    },
    'google.com': {
        'review_container': 'div[data-review-id]',
        'review_text': 'span[data-expandable-text]',
        'rating': 'span[aria-label*="star"]',
        'reviewer': 'div[data-value="Name"]',
        'date': 'span[class*="date"]',
        'pagination': 'button[aria-label="Next page"]'
    },
    'yelp.com': {
        'review_container': 'div[data-testid*="review"]',
        'review_text': 'p[data-testid="review-text"]',
        'rating': 'div[aria-label*="star rating"]',
        'reviewer': 'span[data-testid="review-author"]',
        'date': 'span[data-testid="review-date"]',
        'pagination': 'a[aria-label="Next"]'
    },
    'glassdoor.co.in': {
    'review_container': '[data-test="employer-review"], .review, .employerReview',
    'review_text': '[data-test="reviewBodyText"], .review-details, .reviewBodyText',
    'rating': '[data-test="rating"], .ratingNumber, [class*="rating"]',
    'reviewer': '[data-test="employee-review-reviewer"], .reviewer, .authorName',
    'date': '[data-test="review-date"], .review-date, [class*="date"]',
    'pagination': '[data-test="pagination-next"], .next, [aria-label="Next"]'
    },
}
# Analysis Configuration
SENTIMENT_CATEGORIES = ['positive', 'negative', 'neutral']
MIN_REVIEW_LENGTH = 5  # Minimum characters for a valid review
MAX_REVIEW_LENGTH = 5000  # Maximum characters to process

# Excel Output Configuration
EXCEL_FILENAME_TEMPLATE = "social_media_analysis_{timestamp}.xlsx"
EXCEL_SHEETS = {
    'raw_data': 'Raw Reviews',
    'sentiment_analysis': 'Sentiment Analysis',
    'topic_modeling': 'Topic Analysis',
    'trend_analysis': 'Trend Analysis',
    'summary': 'Executive Summary'
}

# Logging Configuration
LOG_LEVEL = 'INFO'
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

# Data Cleaning Configuration
SPAM_KEYWORDS = [
    'spam', 'fake', 'bot', 'advertisement', 'promo', 'discount code',
    'click here', 'visit our website', 'buy now', 'limited time'
]

STOP_WORDS_CUSTOM = [
    'review', 'company', 'service', 'product', 'customer', 'experience'
]

# Topic Modeling Configuration
NUM_TOPICS = 5  # Number of topics to extract
MIN_TOPIC_WORDS = 10  # Minimum words per topic

# Trend Analysis Configuration
TREND_PERIODS = ['daily', 'weekly', 'monthly']
MIN_REVIEWS_FOR_TREND = 10  # Minimum reviews needed for trend analysis