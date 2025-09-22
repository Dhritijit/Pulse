"""
Beautiful Streamlit Web Interface for Social Media Review Analyzer
Professional UI for analyzing customer reviews with AI
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import time
import os
import logging
from datetime import datetime
from collections import Counter
import json
import base64

# Configure page
st.set_page_config(
    page_title="Social Media Review Analyzer",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Import our modules
try:
    from scraper import ReviewScraper
    from ai_analyzer import AIAnalyzer
    from excel_generator import ExcelGenerator
    import config
except ImportError as e:
    st.error(f"⚠️ Import Error: {e}")
    st.stop()

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .subtitle {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 3rem;
    }
    .metric-card {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
    }
    .success-box {
        background: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .warning-box {
        background: #fff3cd;
        border: 1px solid #ffeaa7;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .error-box {
        background: #f8d7da;
        border: 1px solid #f5c6cb;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .stProgress .st-bo {
        background-color: #667eea;
    }
</style>
""", unsafe_allow_html=True)

class StreamlitAnalyzer:
    def __init__(self):
        self.scraper = None
        self.analyzer = None
        self.excel_generator = None
        
    def initialize_components(self):
        """Initialize analyzer components with error handling"""
        try:
            self.scraper = ReviewScraper()
            self.analyzer = AIAnalyzer()
            self.excel_generator = ExcelGenerator()
            return True
        except Exception as e:
            st.error(f"❌ Initialization Error: {str(e)}")
            return False
            
    def validate_url(self, url):
        """Validate URL format"""
        from urllib.parse import urlparse
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except:
            return False
            
    def process_urls(self, urls):
        """Process and validate URLs"""
        valid_urls = []
        invalid_urls = []
        
        for url in urls:
            url = url.strip()
            if url and self.validate_url(url):
                valid_urls.append(url)
            elif url:
                invalid_urls.append(url)
                
        return valid_urls, invalid_urls
        
    def run_analysis(self, urls, max_reviews, progress_bar, status_text):
        """Run the complete analysis pipeline"""
        results = {
            'reviews': [],
            'sentiment_results': [],
            'topics': {},
            'topic_assignments': [],
            'trends': {},
            'insights': '',
            'filename': ''
        }
        
        try:
            # Phase 1: Scraping
            status_text.text("🔍 Phase 1: Scraping reviews...")
            progress_bar.progress(10)
            
            all_reviews = []
            for i, url in enumerate(urls):
                status_text.text(f"🔍 Scraping {i+1}/{len(urls)}: {url[:50]}...")
                reviews = self.scraper.scrape_reviews(url, max_pages=5)
                if reviews:
                    cleaned_reviews = self.scraper.clean_reviews(reviews)
                    all_reviews.extend(cleaned_reviews[:max_reviews])
                    
                progress = 10 + (i + 1) * 20 // len(urls)
                progress_bar.progress(progress)
                
            if not all_reviews:
                st.error("❌ No reviews found. Please check your URLs.")
                return None
                
            results['reviews'] = all_reviews
            st.success(f"✅ Scraped {len(all_reviews)} reviews successfully!")
            
            # Phase 2: Sentiment Analysis
            progress_bar.progress(35)
            status_text.text("🤖 Phase 2: Analyzing sentiment with AI...")
            
            sentiment_results = self.analyzer.analyze_sentiment_batch(all_reviews)
            results['sentiment_results'] = sentiment_results
            
            progress_bar.progress(55)
            st.success(f"✅ Sentiment analysis complete!")
            
            # Phase 3: Topic Modeling
            status_text.text("📊 Phase 3: Extracting topics and themes...")
            
            topics, topic_assignments = self.analyzer.extract_topics(all_reviews)
            results['topics'] = topics
            results['topic_assignments'] = topic_assignments
            
            progress_bar.progress(75)
            st.success(f"✅ Identified {len(topics)} main topics!")
            
            # Phase 4: Trend Analysis
            status_text.text("📈 Phase 4: Analyzing trends...")
            
            # Add sentiment to reviews for trend analysis
            reviews_with_sentiment = []
            for i, review in enumerate(all_reviews):
                review_copy = review.copy()
                if i < len(sentiment_results):
                    review_copy['sentiment'] = sentiment_results[i]['sentiment']
                reviews_with_sentiment.append(review_copy)
                
            trends = self.analyzer.analyze_trends(reviews_with_sentiment)
            results['trends'] = trends
            
            progress_bar.progress(85)
            
            # Phase 5: Generate Insights
            status_text.text("💡 Phase 5: Generating AI insights...")
            
            insights = self.analyzer.generate_insights(sentiment_results, topics, trends)
            results['insights'] = insights
            
            progress_bar.progress(95)
            
            # Phase 6: Generate Excel Report
            status_text.text("📄 Phase 6: Creating Excel report...")
            
            filename = self.excel_generator.generate_report(
                reviews=all_reviews,
                sentiment_results=sentiment_results,
                topics=topics,
                topic_assignments=topic_assignments,
                trends=trends,
                insights=insights
            )
            results['filename'] = filename
            
            progress_bar.progress(100)
            status_text.text("✅ Analysis complete!")
            
            return results
            
        except Exception as e:
            st.error(f"❌ Analysis failed: {str(e)}")
            return None

def create_download_link(filename):
    """Create download link for Excel file"""
    try:
        with open(filename, 'rb') as f:
            data = f.read()
        b64 = base64.b64encode(data).decode()
        href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="{filename}">📥 Download Excel Report</a>'
        return href
    except Exception as e:
        return f"❌ Error creating download link: {e}"

def display_sentiment_chart(sentiment_results):
    """Display sentiment analysis chart"""
    sentiment_counts = Counter([r.get('sentiment', 'unknown') for r in sentiment_results])
    
    # Create pie chart
    fig = px.pie(
        values=list(sentiment_counts.values()),
        names=list(sentiment_counts.keys()),
        title="Sentiment Distribution",
        color_discrete_map={
            'positive': '#28a745',
            'negative': '#dc3545',
            'neutral': '#ffc107'
        }
    )
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)

def display_topic_chart(topics, topic_assignments):
    """Display topic analysis chart"""
    topic_counts = Counter([ta.get('topic_name', 'Unknown') for ta in topic_assignments])
    
    # Create bar chart
    fig = px.bar(
        x=list(topic_counts.keys()),
        y=list(topic_counts.values()),
        title="Topic Distribution",
        labels={'x': 'Topics', 'y': 'Number of Reviews'}
    )
    fig.update_layout(height=400, xaxis_tickangle=-45)
    st.plotly_chart(fig, use_container_width=True)

def display_metrics(results):
    """Display key metrics"""
    reviews = results['reviews']
    sentiment_results = results['sentiment_results']
    topics = results['topics']
    
    # Calculate metrics
    total_reviews = len(reviews)
    sentiment_counts = Counter([r.get('sentiment', 'unknown') for r in sentiment_results])
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Reviews", total_reviews)
        
    with col2:
        positive_pct = sentiment_counts.get('positive', 0) / total_reviews * 100 if total_reviews > 0 else 0
        st.metric("Positive %", f"{positive_pct:.1f}%")
        
    with col3:
        negative_pct = sentiment_counts.get('negative', 0) / total_reviews * 100 if total_reviews > 0 else 0
        st.metric("Negative %", f"{negative_pct:.1f}%")
        
    with col4:
        st.metric("Topics Found", len(topics))

def main():
    """Main Streamlit application"""
    
    # Header
    st.markdown('<h1 class="main-header">🌐 Pulse</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">AI-Powered Customer Review Analysis & Insights</p>', unsafe_allow_html=True)
    
    # Initialize session state
    if 'analysis_results' not in st.session_state:
        st.session_state.analysis_results = None
    if 'analyzer' not in st.session_state:
        st.session_state.analyzer = StreamlitAnalyzer()
    
    # Sidebar configuration
    st.sidebar.header("⚙️ Configuration")
    
    # Check prerequisites
    st.sidebar.subheader("📋 Prerequisites Check")
    
    # Check OpenAI API key
    api_key_status = "✅ Set" if config.OPENAI_API_KEY and config.OPENAI_API_KEY != "your_openai_api_key_here" else "❌ Missing"
    st.sidebar.write(f"**OpenAI API Key:** {api_key_status}")
    
    if api_key_status == "❌ Missing":
        st.sidebar.error("Please set your OpenAI API key in the .env file")
        st.stop()
    
    # Analysis settings
    st.sidebar.subheader("🎛️ Analysis Settings")
    max_reviews = st.sidebar.slider("Max reviews per site", 50, 2000, 500, 50)
    
    # Advanced settings
    with st.sidebar.expander("🔧 Advanced Settings"):
        batch_size = st.slider("Sentiment analysis batch size", 10, 50, 20)
        num_topics = st.slider("Number of topics to extract", 3, 10, 5)
    
    # Main content area
    tab1, tab2, tab3 = st.tabs(["🔍 Analysis", "📊 Results", "📚 Help"])
    
    with tab1:
        st.header("🔗 Enter Review Site URLs")
        st.write("Paste URLs from review sites like Trustpilot, Glassdoor, Google Reviews, Yelp, etc.")
        
        # URL input
        url_input = st.text_area(
            "URLs (one per line):",
            height=150,
            placeholder="https://www.trustpilot.com/review/company-name.com\nhttps://www.glassdoor.com/Reviews/Company-Reviews-E123456.htm\nhttps://www.yelp.com/biz/restaurant-name"
        )
        
        # Process URLs
        if url_input:
            urls = [url.strip() for url in url_input.split('\n') if url.strip()]
            valid_urls, invalid_urls = st.session_state.analyzer.process_urls(urls)
            
            if valid_urls:
                st.success(f"✅ {len(valid_urls)} valid URLs found")
                with st.expander("View URLs"):
                    for i, url in enumerate(valid_urls, 1):
                        st.write(f"{i}. {url}")
                        
            if invalid_urls:
                st.warning(f"⚠️ {len(invalid_urls)} invalid URLs found")
                with st.expander("View invalid URLs"):
                    for url in invalid_urls:
                        st.write(f"❌ {url}")
        else:
            valid_urls = []
            
        # Analysis button
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🚀 Start Analysis", type="primary", use_container_width=True):
                if not valid_urls:
                    st.error("❌ Please enter at least one valid URL")
                else:
                    # Initialize components
                    if not st.session_state.analyzer.initialize_components():
                        st.stop()
                    
                    # Create progress indicators
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    # Run analysis
                    with st.spinner("Analyzing reviews..."):
                        results = st.session_state.analyzer.run_analysis(
                            valid_urls, max_reviews, progress_bar, status_text
                        )
                        
                    if results:
                        st.session_state.analysis_results = results
                        st.success("🎉 Analysis completed successfully!")
                        st.balloons()
                        
                        # Show quick preview
                        st.subheader("📊 Quick Results Preview")
                        display_metrics(results)
                        
                        # Download link
                        if results['filename']:
                            download_link = create_download_link(results['filename'])
                            st.markdown(download_link, unsafe_allow_html=True)
                            
                        st.info("👆 Switch to the 'Results' tab to see detailed analysis!")
    
    with tab2:
        if st.session_state.analysis_results:
            results = st.session_state.analysis_results
            
            st.header("📊 Analysis Results")
            
            # Key metrics
            st.subheader("📈 Key Metrics")
            display_metrics(results)
            
            # Charts
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("😊 Sentiment Analysis")
                display_sentiment_chart(results['sentiment_results'])
                
            with col2:
                st.subheader("🏷️ Topic Analysis")
                display_topic_chart(results['topics'], results['topic_assignments'])
            
            # Topics details
            st.subheader("🔍 Detailed Topic Analysis")
            for topic_id, topic in results['topics'].items():
                with st.expander(f"📌 {topic.get('topic_name', f'Topic {topic_id + 1}')}"):
                    st.write(f"**Description:** {topic.get('description', 'N/A')}")
                    st.write(f"**Keywords:** {', '.join(topic.get('keywords', []))}")
                    st.write(f"**Review Count:** {topic.get('review_count', 0)}")
                    st.write(f"**Sentiment Tendency:** {topic.get('sentiment_tendency', 'N/A')}")
            
            # AI Insights
            st.subheader("💡 AI-Generated Insights")
            if results['insights']:
                st.markdown(results['insights'])
            else:
                st.write("No insights generated.")
            
            # Sample reviews
            st.subheader("📝 Sample Reviews")
            if results['reviews']:
                sample_size = min(5, len(results['reviews']))
                for i in range(sample_size):
                    review = results['reviews'][i]
                    sentiment = results['sentiment_results'][i] if i < len(results['sentiment_results']) else {}
                    
                    with st.expander(f"Review {i+1} - {sentiment.get('sentiment', 'Unknown').title()}"):
                        st.write(f"**Text:** {review.get('text', 'N/A')[:300]}...")
                        st.write(f"**Rating:** {review.get('rating', 'N/A')}")
                        st.write(f"**Source:** {review.get('source_domain', 'N/A')}")
                        st.write(f"**Sentiment:** {sentiment.get('sentiment', 'N/A')} ({sentiment.get('confidence', 0):.2f} confidence)")
            
            # Download section
            st.subheader("📥 Download Report")
            if results['filename']:
                download_link = create_download_link(results['filename'])
                st.markdown(download_link, unsafe_allow_html=True)
                
                st.info(f"""
                📊 **Your Excel report contains:**
                - Raw reviews data with sentiment analysis
                - Detailed sentiment breakdown and metrics
                - Topic modeling with keywords and themes
                - Trend analysis over time
                - Executive summary with AI insights
                """)
        else:
            st.info("👈 Start an analysis in the 'Analysis' tab to see results here!")
    
    with tab3:
        st.header("📚 How to Use")
        
        st.subheader("🎯 Getting Started")
        st.markdown("""
        1. **Enter URLs**: Paste review site URLs in the Analysis tab
        2. **Configure Settings**: Adjust settings in the sidebar
        3. **Start Analysis**: Click the "Start Analysis" button
        4. **View Results**: Check the Results tab for insights
        5. **Download Report**: Get your Excel report with full analysis
        """)
        
        st.subheader("🌐 Supported Sites")
        st.markdown("""
        - **Trustpilot**: Company review pages
        - **Glassdoor**: Employee reviews and company ratings
        - **Google Reviews**: Business and location reviews
        - **Yelp**: Restaurant and business reviews
        - **Most other review sites**: Automatic detection
        """)
        
        st.subheader("📊 What You Get")
        st.markdown("""
        - **Sentiment Analysis**: Positive, negative, neutral classification
        - **Topic Modeling**: Key themes and topics in reviews
        - **Trend Analysis**: Changes over time
        - **AI Insights**: Strategic recommendations
        - **Professional Excel Report**: Multi-sheet analysis
        """)
        
        st.subheader("⚡ Tips for Best Results")
        st.markdown("""
        - Use direct links to review pages (not search results)
        - Start with smaller datasets (100-500 reviews) for testing
        - Make sure review pages are publicly accessible
        - Check your OpenAI API credits before large analyses
        """)
        
        st.subheader("❓ Common Issues")
        st.markdown("""
        - **No reviews found**: Check URL format and accessibility
        - **Analysis failed**: Verify OpenAI API key and credits
        - **Slow processing**: Large datasets take time (5-15 minutes for 1000+ reviews)
        """)

if __name__ == "__main__":
    main()