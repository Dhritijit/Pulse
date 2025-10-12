"""
Universal Web Scraper for Review Sites
Handles multiple review platforms dynamically
Enhanced with smart pagination detection
"""

import requests
import time
import random
import logging
import re
from datetime import datetime
from urllib.parse import urlparse, urljoin, parse_qs, urlunparse, urlencode
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from fake_useragent import UserAgent
import config

class ReviewScraper:
    def __init__(self):
        self.session = requests.Session()
        self.ua = UserAgent()
        self.setup_logging()
        self.reviews = []
        
    def setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            level=getattr(logging, config.LOG_LEVEL),
            format=config.LOG_FORMAT,
            handlers=[
                logging.FileHandler('scraper.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def setup_selenium_driver(self, headless=True):
        """Setup Selenium WebDriver for JavaScript-heavy sites"""
        chrome_options = Options()
        if headless:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument(f"--user-agent={self.ua.random}")
        
        try:
            self.driver = webdriver.Chrome(
                ChromeDriverManager().install(),
                options=chrome_options
            )
            return True
        except Exception as e:
            self.logger.error(f"Failed to setup Selenium driver: {e}")
            return False
            
    def get_site_info(self, url):
        """Extract site information and determine scraping strategy"""
        parsed_url = urlparse(url)
        domain = parsed_url.netloc.lower()
        
        # Remove www. prefix
        if domain.startswith('www.'):
            domain = domain[4:]
            
        site_info = {
            'domain': domain,
            'base_url': f"{parsed_url.scheme}://{parsed_url.netloc}",
            'selectors': None,
            'requires_selenium': False
        }
        
        # Check if we have predefined selectors for this site
        for site_key, selectors in config.SITE_SELECTORS.items():
            if site_key in domain:
                site_info['selectors'] = selectors
                break
                
        # Sites that typically require JavaScript rendering
        js_heavy_sites = ['glassdoor.com', 'glassdoor.co.in', 'indeed.com', 'linkedin.com', 'ambitionbox.com']
        if any(site in domain for site in js_heavy_sites):
            site_info['requires_selenium'] = True
            
        return site_info
        
    def make_request(self, url, use_selenium=False):
        """Make HTTP request with proper headers and delays"""
        headers = {
            'User-Agent': self.ua.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9,hi;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0'
            }
                
        if use_selenium:
            try:
                self.driver.get(url)
                time.sleep(3)  # Wait for page to load
                return self.driver.page_source
            except Exception as e:
                self.logger.error(f"Selenium request failed for {url}: {e}")
                return None
        else:
            try:
                response = self.session.get(
                    url, 
                    headers=headers, 
                    timeout=config.REQUEST_TIMEOUT
                )
                response.raise_for_status()
                
                # Random delay to be respectful
                delay = random.uniform(*config.RANDOM_DELAY_RANGE)
                time.sleep(delay)
                
                return response.text
            except Exception as e:
                self.logger.error(f"Request failed for {url}: {e}")
                return None
                
    def extract_reviews_generic(self, html_content, site_info):
        """Generic review extraction using intelligent parsing"""
        soup = BeautifulSoup(html_content, 'html.parser')
        reviews = []
        
        # Try predefined selectors first
        if site_info['selectors']:
            reviews = self.extract_with_selectors(soup, site_info['selectors'])
            
        # If no reviews found with selectors, try generic approach
        if not reviews:
            reviews = self.extract_with_patterns(soup, site_info)
            
        return reviews
        
    def extract_with_selectors(self, soup, selectors):
        """Extract reviews using predefined CSS selectors"""
        reviews = []
        
        try:
            review_containers = soup.select(selectors['review_container'])
            
            for container in review_containers:
                review = self.parse_review_container(container, selectors)
                if review and self.is_valid_review(review):
                    reviews.append(review)
                    
        except Exception as e:
            self.logger.error(f"Error extracting with selectors: {e}")
            
        return reviews
        
    def parse_review_container(self, container, selectors):
        """Parse individual review container"""
        try:
            review = {
                'text': '',
                'rating': None,
                'reviewer': '',
                'date': '',
                'source': 'unknown'
            }
            
            # Extract review text
            text_elem = container.select_one(selectors.get('review_text', ''))
            if text_elem:
                review['text'] = text_elem.get_text(strip=True)
                
            # Extract rating
            rating_elem = container.select_one(selectors.get('rating', ''))
            if rating_elem:
                review['rating'] = self.extract_rating(rating_elem)
                
            # Extract reviewer name
            reviewer_elem = container.select_one(selectors.get('reviewer', ''))
            if reviewer_elem:
                review['reviewer'] = reviewer_elem.get_text(strip=True)
                
            # Extract date
            date_elem = container.select_one(selectors.get('date', ''))
            if date_elem:
                review['date'] = self.parse_date(date_elem.get_text(strip=True))
                
            return review
            
        except Exception as e:
            self.logger.error(f"Error parsing review container: {e}")
            return None
            
    def extract_with_patterns(self, soup, site_info):
        """Extract reviews using pattern recognition"""
        reviews = []
        
        # Common patterns for review identification
        review_patterns = [
            {'tag': 'div', 'class_contains': ['review', 'comment', 'feedback']},
            {'tag': 'article', 'class_contains': ['review', 'post']},
            {'tag': 'li', 'class_contains': ['review', 'item']},
        ]
        
        for pattern in review_patterns:
            elements = soup.find_all(pattern['tag'])
            for elem in elements:
                class_attr = elem.get('class', [])
                if any(keyword in ' '.join(class_attr).lower() 
                      for keyword in pattern['class_contains']):
                    review = self.parse_generic_review(elem)
                    if review and self.is_valid_review(review):
                        reviews.append(review)
                        
        return reviews
        
    def parse_generic_review(self, element):
        """Parse review using generic patterns"""
        try:
            review = {
                'text': '',
                'rating': None,
                'reviewer': '',
                'date': '',
                'source': 'generic'
            }
            
            # Extract text content
            text_elements = element.find_all(['p', 'div', 'span'], 
                                           text=True, recursive=True)
            texts = []
            for elem in text_elements:
                text = elem.get_text(strip=True)
                if len(text) > 20:  # Likely review text
                    texts.append(text)
                    
            review['text'] = ' '.join(texts[:3])  # Take first 3 meaningful texts
            
            # Try to extract rating from stars, numbers, etc.
            rating_elem = element.find(['span', 'div'], 
                                     class_=re.compile(r'star|rating|score', re.I))
            if rating_elem:
                review['rating'] = self.extract_rating(rating_elem)
                
            return review
            
        except Exception as e:
            self.logger.error(f"Error in generic review parsing: {e}")
            return None
            
    def extract_rating(self, element):
        """Extract rating from various formats"""
        try:
            # Check for star count in class names
            class_attr = ' '.join(element.get('class', []))
            star_match = re.search(r'(\d+)[-_]?star|star[-_]?(\d+)', class_attr, re.I)
            if star_match:
                return int(star_match.group(1) or star_match.group(2))
                
            # Check for aria-label with rating
            aria_label = element.get('aria-label', '')
            rating_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:out of|/|\s*star)', aria_label, re.I)
            if rating_match:
                return float(rating_match.group(1))
                
            # Check for direct text content
            text = element.get_text(strip=True)
            number_match = re.search(r'(\d+(?:\.\d+)?)', text)
            if number_match:
                rating = float(number_match.group(1))
                if 1 <= rating <= 5:  # Assuming 5-star scale
                    return rating
                    
        except Exception as e:
            self.logger.error(f"Error extracting rating: {e}")
            
        return None
        
    def parse_date(self, date_string):
        """Parse date from various formats"""
        try:
            # Common date patterns
            patterns = [
                r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
                r'(\d{4}[/-]\d{1,2}[/-]\d{1,2})',
                r'(\w+\s+\d{1,2},?\s+\d{4})',
                r'(\d{1,2}\s+\w+\s+\d{4})'
            ]
            
            for pattern in patterns:
                match = re.search(pattern, date_string)
                if match:
                    return match.group(1)
                    
        except Exception as e:
            self.logger.error(f"Error parsing date: {e}")
            
        return date_string
        
    def is_valid_review(self, review):
        """Validate if extracted data is a valid review"""
        if not review or not review.get('text'):
            return False
            
        text = review['text'].strip()
        
        # Check minimum length
        if len(text) < config.MIN_REVIEW_LENGTH:
            return False
            
        # Check for spam keywords
        text_lower = text.lower()
        spam_count = sum(1 for keyword in config.SPAM_KEYWORDS 
                        if keyword in text_lower)
        if spam_count >= 2:  # Multiple spam indicators
            return False
            
        return True
    
    # ========================================================================
    # 🆕 NEW METHODS: Smart Pagination Detection & URL Building
    # ========================================================================
    
    def detect_pagination_pattern(self, url):
        """
        Detect pagination URL pattern from the current URL
        
        Returns:
            dict: {
                'pattern_type': 'query_param' | 'path_segment' | 'none',
                'param_name': 'page' (if query_param),
                'current_page': 2 (if detected),
                'base_url': URL without page parameter
            }
        """
        try:
            parsed = urlparse(url)
            query_params = parse_qs(parsed.query)
            
            # Check for common page parameter names
            page_param_names = ['page', 'p', 'pg', 'pageNumber', 'pageNum']
            
            for param_name in page_param_names:
                if param_name in query_params:
                    current_page = int(query_params[param_name][0])
                    
                    # Build base URL without the page parameter
                    clean_params = {k: v for k, v in query_params.items() if k != param_name}
                    query_string = urlencode(clean_params, doseq=True)
                    base_url = urlunparse((
                        parsed.scheme,
                        parsed.netloc,
                        parsed.path,
                        parsed.params,
                        query_string,
                        ''
                    ))
                    
                    self.logger.info(f"✅ Detected pagination pattern: ?{param_name}={current_page}")
                    
                    return {
                        'pattern_type': 'query_param',
                        'param_name': param_name,
                        'current_page': current_page,
                        'base_url': base_url
                    }
            
            # Check for path-based pagination (e.g., /page/2/)
            path_match = re.search(r'/page[s]?/(\d+)', parsed.path, re.I)
            if path_match:
                current_page = int(path_match.group(1))
                base_path = re.sub(r'/page[s]?/\d+', '', parsed.path, flags=re.I)
                base_url = urlunparse((
                    parsed.scheme,
                    parsed.netloc,
                    base_path,
                    parsed.params,
                    parsed.query,
                    ''
                ))
                
                self.logger.info(f"✅ Detected path-based pagination: /page/{current_page}")
                
                return {
                    'pattern_type': 'path_segment',
                    'current_page': current_page,
                    'base_url': base_url
                }
            
            # No pagination detected in URL - might be page 1
            self.logger.info("ℹ️  No pagination pattern in URL - assuming page 1")
            return {
                'pattern_type': 'query_param',  # Assume query param for building
                'param_name': 'page',  # Most common
                'current_page': 1,
                'base_url': url
            }
            
        except Exception as e:
            self.logger.error(f"Error detecting pagination pattern: {e}")
            return {'pattern_type': 'none'}
    
    def build_pagination_urls(self, pattern_info, start_page, end_page):
        """
        Build pagination URLs based on detected pattern
        
        Args:
            pattern_info: dict from detect_pagination_pattern()
            start_page: int - starting page number
            end_page: int - ending page number
            
        Returns:
            list of URLs
        """
        urls = []
        
        try:
            if pattern_info['pattern_type'] == 'none':
                return urls
            
            base_url = pattern_info['base_url']
            
            if pattern_info['pattern_type'] == 'query_param':
                param_name = pattern_info['param_name']
                parsed = urlparse(base_url)
                
                for page_num in range(start_page, end_page + 1):
                    # Add page parameter to existing query string
                    query_params = parse_qs(parsed.query)
                    query_params[param_name] = [str(page_num)]
                    query_string = urlencode(query_params, doseq=True)
                    
                    page_url = urlunparse((
                        parsed.scheme,
                        parsed.netloc,
                        parsed.path,
                        parsed.params,
                        query_string,
                        ''
                    ))
                    urls.append(page_url)
                    
            elif pattern_info['pattern_type'] == 'path_segment':
                parsed = urlparse(base_url)
                
                for page_num in range(start_page, end_page + 1):
                    page_path = f"{parsed.path}/page/{page_num}"
                    page_url = urlunparse((
                        parsed.scheme,
                        parsed.netloc,
                        page_path,
                        parsed.params,
                        parsed.query,
                        ''
                    ))
                    urls.append(page_url)
            
            self.logger.info(f"🔨 Built {len(urls)} pagination URLs (pages {start_page}-{end_page})")
            
        except Exception as e:
            self.logger.error(f"Error building pagination URLs: {e}")
            
        return urls
        
    def get_pagination_urls(self, html_content, site_info, current_url):
        """
        ENHANCED: Extract pagination URLs using hybrid approach
        
        Strategy:
        1. Try to detect URL pattern and build next URL automatically
        2. If pattern detection fails, fall back to selector-based extraction
        3. Return list of next page URLs to scrape
        """
        urls = []
        
        try:
            # ============================================================
            # STRATEGY 1: Smart URL Pattern Detection & Building
            # ============================================================
            self.logger.info("🔍 Attempting smart pagination detection...")
            
            pattern_info = self.detect_pagination_pattern(current_url)
            
            if pattern_info['pattern_type'] != 'none':
                current_page = pattern_info.get('current_page', 1)
                next_page = current_page + 1
                
                # Build just the next page URL
                next_urls = self.build_pagination_urls(pattern_info, next_page, next_page)
                
                if next_urls:
                    urls.extend(next_urls)
                    self.logger.info(f"✅ Built next page URL using pattern: {next_urls[0]}")
                    return urls  # Success! Return the built URLs
            
            # ============================================================
            # STRATEGY 2: Selector-Based Extraction (Fallback)
            # ============================================================
            self.logger.info("🔄 Pattern detection didn't work, trying selector-based extraction...")
            
            if site_info['selectors'] and 'pagination' in site_info['selectors']:
                soup = BeautifulSoup(html_content, 'html.parser')
                next_links = soup.select(site_info['selectors']['pagination'])
                
                self.logger.info(f"🔎 Found {len(next_links)} elements matching pagination selector")
                
                for link in next_links:
                    href = link.get('href')
                    if href:
                        full_url = urljoin(current_url, href)
                        urls.append(full_url)
                        self.logger.info(f"✅ Extracted pagination URL from selector: {full_url}")
                
                if urls:
                    return urls  # Success with selectors!
                else:
                    self.logger.warning("⚠️  Pagination selector matched elements but no href found")
            else:
                self.logger.warning("⚠️  No pagination selector defined for this site")
            
            # ============================================================
            # STRATEGY 3: Last Resort - Try Generic Patterns
            # ============================================================
            if not urls:
                self.logger.info("🔄 Trying generic pagination patterns...")
                soup = BeautifulSoup(html_content, 'html.parser')
                
                # Try common generic selectors
                generic_selectors = [
                    'a[rel="next"]',
                    'a:contains("Next")',
                    'a:contains("next")',
                    'a[aria-label*="next" i]',
                    'button[aria-label*="next" i]'
                ]
                
                for selector in generic_selectors:
                    try:
                        next_links = soup.select(selector)
                        for link in next_links:
                            href = link.get('href')
                            if href:
                                full_url = urljoin(current_url, href)
                                urls.append(full_url)
                                self.logger.info(f"✅ Found pagination using generic pattern: {selector}")
                                return urls
                    except:
                        continue
                        
        except Exception as e:
            self.logger.error(f"❌ Error in pagination URL extraction: {e}")
            
        if not urls:
            self.logger.warning("⚠️  No pagination URLs found - this might be the last page")
            
        return urls
        
    def scrape_reviews(self, url, max_pages=10):
        """Main method to scrape reviews from a URL"""
        self.logger.info(f"Starting to scrape reviews from: {url}")
        
        site_info = self.get_site_info(url)
        self.logger.info(f"Detected site: {site_info['domain']}")
        
        # Setup Selenium if required
        if site_info['requires_selenium']:
            if not self.setup_selenium_driver():
                self.logger.error("Failed to setup Selenium driver")
                return []
                
        all_reviews = []
        urls_to_process = [url]
        processed_urls = set()
        
        try:
            for page_num in range(max_pages):
                if not urls_to_process:
                    break
                    
                current_url = urls_to_process.pop(0)
                if current_url in processed_urls:
                    continue
                    
                self.logger.info(f"Processing page {page_num + 1}: {current_url}")
                
                # Make request
                html_content = self.make_request(
                    current_url, 
                    site_info['requires_selenium']
                )
                
                if not html_content:
                    self.logger.warning(f"Failed to get content from: {current_url}")
                    continue
                    
                # Extract reviews
                reviews = self.extract_reviews_generic(html_content, site_info)
                all_reviews.extend(reviews)
                
                self.logger.info(f"Extracted {len(reviews)} reviews from page {page_num + 1}")
                
                # Check if we've reached the limit
                if len(all_reviews) >= config.MAX_REVIEWS_PER_SITE:
                    self.logger.info(f"Reached maximum review limit: {config.MAX_REVIEWS_PER_SITE}")
                    break
                    
                # Get pagination URLs using enhanced method
                next_urls = self.get_pagination_urls(html_content, site_info, current_url)
                for next_url in next_urls:
                    if next_url not in processed_urls:
                        urls_to_process.append(next_url)
                        
                processed_urls.add(current_url)
                
                # Rate limiting delay
                time.sleep(config.DEFAULT_DELAY)
                
        except KeyboardInterrupt:
            self.logger.info("Scraping interrupted by user")
        except Exception as e:
            self.logger.error(f"Error during scraping: {e}")
        finally:
            if hasattr(self, 'driver'):
                self.driver.quit()
                
        # Add metadata to reviews
        for review in all_reviews:
            review['scraped_at'] = datetime.now().isoformat()
            review['source_url'] = url
            review['source_domain'] = site_info['domain']
            
        self.logger.info(f"Scraping completed. Total reviews: {len(all_reviews)}")
        return all_reviews
        
    def clean_reviews(self, reviews):
        """Clean and deduplicate reviews"""
        self.logger.info("Cleaning and processing reviews...")
        
        cleaned_reviews = []
        seen_texts = set()
        
        for review in reviews:
            # Remove duplicates based on text similarity
            text = review.get('text', '').strip().lower()
            if not text or text in seen_texts:
                continue
                
            # Clean text
            review['text'] = re.sub(r'\s+', ' ', review['text']).strip()
            review['text'] = review['text'][:config.MAX_REVIEW_LENGTH]
            
            # Validate again after cleaning
            if self.is_valid_review(review):
                cleaned_reviews.append(review)
                seen_texts.add(text)
                
        self.logger.info(f"Cleaned reviews: {len(cleaned_reviews)} (removed {len(reviews) - len(cleaned_reviews)} duplicates/invalid)")
        return cleaned_reviews