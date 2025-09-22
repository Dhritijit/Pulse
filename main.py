"""
Main orchestrator for Social Media Review Analyzer
Coordinates scraping, analysis, and report generation
"""

import os
import sys
import logging
import traceback
from datetime import datetime
from urllib.parse import urlparse
import config
from scraper import ReviewScraper
from ai_analyzer import AIAnalyzer
from excel_generator import ExcelGenerator

class SocialMediaAnalyzer:
    def __init__(self):
        self.setup_logging()
        self.scraper = ReviewScraper()
        self.analyzer = AIAnalyzer()
        self.excel_generator = ExcelGenerator()
        
    def setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            level=getattr(logging, config.LOG_LEVEL),
            format=config.LOG_FORMAT,
            handlers=[
                logging.FileHandler(f'analyzer_{datetime.now().strftime("%Y%m%d")}.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def validate_url(self, url):
        """Validate if URL is properly formatted"""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception:
            return False
            
    def validate_prerequisites(self):
        """Check if all prerequisites are met"""
        issues = []
        
        # Check OpenAI API key
        if not config.OPENAI_API_KEY:
            issues.append("OpenAI API key not found. Please set OPENAI_API_KEY in your .env file")
            
        # Check if .env file exists
        if not os.path.exists('.env'):
            issues.append(".env file not found. Please create one with your OpenAI API key")
            
        return issues
        
    def get_user_input(self):
        """Get URLs and configuration from user"""
        print("=" * 60)
        print("Social Media Review Analyzer")
        print("=" * 60)
        print()
        
        # Check prerequisites
        issues = self.validate_prerequisites()
        if issues:
            print("⚠️  Setup Issues Found:")
            for issue in issues:
                print(f"   - {issue}")
            print()
            print("Please fix these issues before continuing.")
            return None
            
        urls = []
        
        print("Enter review site URLs (one per line)")
        print("Supported sites: Trustpilot, Glassdoor, Google Reviews, Yelp, etc.")
        print("Press Enter twice when done, or type 'quit' to exit")
        print()
        
        while True:
            url = input("URL: ").strip()
            
            if url.lower() == 'quit':
                print("Exiting...")
                return None
                
            if not url:
                if urls:
                    break
                else:
                    print("Please enter at least one URL.")
                    continue
                    
            if self.validate_url(url):
                urls.append(url)
                print(f"✓ Added: {url}")
            else:
                print(f"✗ Invalid URL format: {url}")
                
        if not urls:
            print("No valid URLs provided.")
            return None
            
        # Get additional parameters
        print()
        max_reviews = input(f"Maximum reviews per site (default: {config.MAX_REVIEWS_PER_SITE}): ").strip()
        if max_reviews:
            try:
                config.MAX_REVIEWS_PER_SITE = int(max_reviews)
            except ValueError:
                print("Invalid number, using default")
                
        config_data = {
            'urls': urls,
            'max_reviews': config.MAX_REVIEWS_PER_SITE,
            'timestamp': datetime.now().isoformat()
        }
        
        return config_data
        
    def display_progress(self, step, total_steps, description):
        """Display progress information"""
        progress = f"[{step}/{total_steps}]"
        print(f"\n{progress} {description}")
        print("-" * 50)
        
    def scrape_all_reviews(self, urls):
        """Scrape reviews from all provided URLs"""
        all_reviews = []
        
        for i, url in enumerate(urls):
            self.display_progress(i + 1, len(urls), f"Scraping reviews from {url}")
            
            try:
                reviews = self.scraper.scrape_reviews(url)
                if reviews:
                    cleaned_reviews = self.scraper.clean_reviews(reviews)
                    all_reviews.extend(cleaned_reviews)
                    print(f"✓ Scraped {len(cleaned_reviews)} reviews from {url}")
                else:
                    print(f"⚠️ No reviews found at {url}")
                    
            except Exception as e:
                self.logger.error(f"Error scraping {url}: {e}")
                print(f"✗ Failed to scrape {url}: {str(e)}")
                
        return all_reviews
        
    def analyze_reviews(self, reviews):
        """Perform comprehensive analysis on reviews"""
        analysis_results = {}
        
        try:
            # Sentiment Analysis
            self.display_progress(1, 4, "Analyzing sentiment with AI")
            sentiment_results = self.analyzer.analyze_sentiment_batch(reviews)
            analysis_results['sentiment'] = sentiment_results
            print(f"✓ Completed sentiment analysis for {len(sentiment_results)} reviews")
            
            # Topic Modeling
            self.display_progress(2, 4, "Extracting topics and themes")
            topics, topic_assignments = self.analyzer.extract_topics(reviews)
            analysis_results['topics'] = topics
            analysis_results['topic_assignments'] = topic_assignments
            print(f"✓ Identified {len(topics)} main topics")
            
            # Trend Analysis
            self.display_progress(3, 4, "Analyzing trends over time")
            # Add sentiment to reviews for trend analysis
            reviews_with_sentiment = []
            for i, review in enumerate(reviews):
                review_copy = review.copy()
                if i < len(sentiment_results):
                    review_copy['sentiment'] = sentiment_results[i]['sentiment']
                reviews_with_sentiment.append(review_copy)
                
            trends = self.analyzer.analyze_trends(reviews_with_sentiment)
            analysis_results['trends'] = trends
            print("✓ Completed trend analysis")
            
            # Generate Insights
            self.display_progress(4, 4, "Generating AI insights")
            insights = self.analyzer.generate_insights(
                sentiment_results, topics, trends
            )
            analysis_results['insights'] = insights
            print("✓ Generated strategic insights")
            
        except Exception as e:
            self.logger.error(f"Error during analysis: {e}")
            print(f"✗ Analysis error: {str(e)}")
            raise
            
        return analysis_results
        
    def generate_report(self, reviews, analysis_results):
        """Generate Excel report"""
        self.display_progress(1, 1, "Generating Excel report")
        
        try:
            filename = self.excel_generator.generate_report(
                reviews=reviews,
                sentiment_results=analysis_results['sentiment'],
                topics=analysis_results['topics'],
                topic_assignments=analysis_results['topic_assignments'],
                trends=analysis_results['trends'],
                insights=analysis_results['insights']
            )
            
            print(f"✓ Excel report generated: {filename}")
            return filename
            
        except Exception as e:
            self.logger.error(f"Error generating report: {e}")
            print(f"✗ Report generation error: {str(e)}")
            raise
            
    def print_summary(self, reviews, analysis_results, filename):
        """Print analysis summary"""
        print("\n" + "=" * 60)
        print("ANALYSIS SUMMARY")
        print("=" * 60)
        
        # Basic stats
        total_reviews = len(reviews)
        sentiment_results = analysis_results['sentiment']
        topics = analysis_results['topics']
        
        print(f"Total Reviews Analyzed: {total_reviews}")
        
        # Sentiment breakdown
        from collections import Counter
        sentiment_counts = Counter([r.get('sentiment', 'unknown') for r in sentiment_results])
        
        print("\nSentiment Distribution:")
        for sentiment, count in sentiment_counts.items():
            percentage = count / total_reviews * 100 if total_reviews > 0 else 0
            print(f"  {sentiment.title()}: {count} ({percentage:.1f}%)")
            
        # Top topics
        print(f"\nMain Topics Identified: {len(topics)}")
        for i, (topic_id, topic) in enumerate(list(topics.items())[:3]):
            print(f"  {i+1}. {topic.get('topic_name', 'Unknown')}")
            
        # Sources
        source_counts = Counter([r.get('source_domain', 'unknown') for r in reviews])
        print(f"\nData Sources: {len(source_counts)}")
        for source, count in source_counts.most_common(3):
            print(f"  {source}: {count} reviews")
            
        print(f"\n📊 Full report saved as: {filename}")
        print(f"📝 Log file: analyzer_{datetime.now().strftime('%Y%m%d')}.log")
        
    def run(self):
        """Main execution method"""
        try:
            # Get user input
            config_data = self.get_user_input()
            if not config_data:
                return
                
            self.logger.info(f"Starting analysis with config: {config_data}")
            
            # Scrape reviews
            print("\n🔍 SCRAPING PHASE")
            print("=" * 30)
            reviews = self.scrape_all_reviews(config_data['urls'])
            
            if not reviews:
                print("❌ No reviews found. Please check your URLs and try again.")
                return
                
            print(f"\n✅ Scraping completed. Total reviews: {len(reviews)}")
            
            # Analyze reviews
            print("\n🤖 ANALYSIS PHASE")
            print("=" * 30)
            analysis_results = self.analyze_reviews(reviews)
            
            print("\n✅ Analysis completed.")
            
            # Generate report
            print("\n📊 REPORT GENERATION")
            print("=" * 30)
            filename = self.generate_report(reviews, analysis_results)
            
            # Print summary
            self.print_summary(reviews, analysis_results, filename)
            
            print("\n🎉 Analysis completed successfully!")
            
        except KeyboardInterrupt:
            print("\n\n❌ Analysis interrupted by user.")
            self.logger.info("Analysis interrupted by user")
            
        except Exception as e:
            print(f"\n❌ An error occurred: {str(e)}")
            self.logger.error(f"Fatal error: {e}")
            self.logger.error(traceback.format_exc())
            
def main():
    """Entry point for the application"""
    # Check Python version
    if sys.version_info < (3, 7):
        print("❌ Python 3.7 or higher is required.")
        sys.exit(1)
        
    # Create analyzer and run
    analyzer = SocialMediaAnalyzer()
    analyzer.run()
    
if __name__ == "__main__":
    main()