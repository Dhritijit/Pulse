"""
Professional BI-Style Streamlit Interface for Social Media Review Analyzer
Custom branding, hierarchical categories, and interactive dashboards
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
from collections import Counter, defaultdict
import json
import base64
import tempfile

# Configure page - MUST be first Streamlit command
st.set_page_config(
    page_title="Pulse Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Import modules
try:
    from scraper import ReviewScraper
    from ai_analyzer import AIAnalyzer
    from excel_generator import ExcelGenerator
    from file_processor import FileProcessor
    from taxonomy_matcher import TaxonomyMatcher
    import config
except ImportError as e:
    st.error(f"Import Error: {e}")
    st.stop()

# Custom CSS with brand colors
st.markdown("""
<style>
    :root {
        --sidebar-bg: #1B3C53;
        --main-bg: #234C6A;
        --card-bg: #2C5F7F;
        --text-primary: #FFFFFF;
        --text-secondary: #E0E0E0;
        --accent: #4A90E2;
        --success: #28a745;
        --warning: #ffc107;
        --danger: #dc3545;
    }
    
    [data-testid="stSidebar"] {
        background-color: #1B3C53 !important;
    }
    
    [data-testid="stSidebar"] * {
        color: #FFFFFF !important;
    }
    
    .main {
        background-color: #234C6A !important;
    }
    
    .block-container {
        background-color: #234C6A !important;
        padding-top: 2rem !important;
    }
    
    h1, h2, h3, h4, h5, h6 {
        color: #FFFFFF !important;
        font-weight: 600 !important;
    }
    
    .stAlert, .stInfo, .stSuccess, .stWarning, .stError {
        background-color: #2C5F7F !important;
        color: #FFFFFF !important;
        border-radius: 10px !important;
        border-left: 4px solid #4A90E2 !important;
    }
    
    [data-testid="stMetricValue"] {
        font-size: 2rem !important;
        color: #4A90E2 !important;
        font-weight: 700 !important;
    }
    
    [data-testid="stMetricLabel"] {
        color: #E0E0E0 !important;
        font-size: 0.9rem !important;
    }
    
    .stButton > button {
        background: linear-gradient(90deg, #4A90E2 0%, #357ABD 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.6rem 2rem !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 12px rgba(74, 144, 226, 0.4) !important;
    }
    
    .stProgress > div > div > div {
        background: linear-gradient(90deg, #4A90E2 0%, #357ABD 100%) !important;
    }
    
    [data-testid="stFileUploader"] {
        background-color: #2C5F7F !important;
        border-radius: 10px !important;
        padding: 1rem !important;
        border: 2px dashed #4A90E2 !important;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem !important;
        background-color: transparent !important;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: #2C5F7F !important;
        color: #FFFFFF !important;
        border-radius: 8px 8px 0 0 !important;
        padding: 0.8rem 2rem !important;
        font-weight: 600 !important;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(180deg, #4A90E2 0%, #2C5F7F 100%) !important;
    }
    
    .logo-container {
        text-align: center;
        padding: 1rem 0 2rem 0;
        border-bottom: 2px solid #2C5F7F;
        margin-bottom: 2rem;
    }
    
    .section-header {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        padding: 1rem;
        background: linear-gradient(90deg, #2C5F7F 0%, transparent 100%);
        border-left: 4px solid #4A90E2;
        border-radius: 4px;
        margin: 1rem 0;
    }
    
    .section-icon {
        font-size: 1.5rem;
    }
    
    .bi-card {
        background: linear-gradient(135deg, #2C5F7F 0%, #1B3C53 100%);
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        border: 1px solid #4A90E2;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    }
    
    .dataframe {
        background-color: #2C5F7F !important;
        color: #FFFFFF !important;
    }
    
    .stRadio > label {
        background-color: #2C5F7F !important;
        padding: 0.5rem 1rem !important;
        border-radius: 8px !important;
        margin: 0.2rem 0 !important;
    }
    
    .streamlit-expanderHeader {
        background-color: #2C5F7F !important;
        color: #FFFFFF !important;
        border-radius: 8px !important;
    }
</style>
""", unsafe_allow_html=True)

class StreamlitAnalyzer:
    def __init__(self):
        self.scraper = None
        self.analyzer = None
        self.excel_generator = None
        self.file_processor = None
        self.taxonomy_matcher = None
        
    def initialize_components(self, taxonomy_file=None):
        """Initialize analyzer components"""
        try:
            self.scraper = ReviewScraper()
            self.analyzer = AIAnalyzer()
            self.excel_generator = ExcelGenerator()
            self.file_processor = FileProcessor()
            
            if taxonomy_file:
                self.taxonomy_matcher = TaxonomyMatcher(taxonomy_file)
            
            return True
        except Exception as e:
            st.error(f"Initialization Error: {str(e)}")
            return False
    
    def process_uploaded_file(self, uploaded_file, max_reviews):
        """Process uploaded review file"""
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                tmp_path = tmp_file.name
            
            is_valid, message = self.file_processor.validate_file(tmp_path)
            if not is_valid:
                os.unlink(tmp_path)
                return None, message
            
            reviews = self.file_processor.process_uploaded_file(tmp_path, max_reviews)
            os.unlink(tmp_path)
            
            return reviews, f"Successfully processed {len(reviews)} reviews"
            
        except Exception as e:
            return None, f"Error processing file: {str(e)}"
    
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
    
    def create_hierarchical_topics(self, topics, topic_assignments, taxonomy_matches):
        """Create hierarchical topic structure (Level 1 -> Level 2)"""
        hierarchical = defaultdict(lambda: {'level2': defaultdict(int), 'total': 0})
        
        if taxonomy_matches:
            for matches in taxonomy_matches:
                if matches:
                    level1 = matches[0].get('high_level_category', 'Other')
                    level2 = matches[0].get('category', 'Uncategorized')
                    hierarchical[level1]['level2'][level2] += 1
                    hierarchical[level1]['total'] += 1
        
        if not hierarchical:
            for assignment in topic_assignments:
                level1 = 'AI Discovered Topics'
                level2 = assignment.get('topic_name', 'Unknown')
                hierarchical[level1]['level2'][level2] += 1
                hierarchical[level1]['total'] += 1
        
        return dict(hierarchical)
    
    def run_analysis(self, reviews, use_taxonomy, progress_bar, status_text):
        """Run complete analysis pipeline"""
        results = {
            'reviews': [],
            'sentiment_results': [],
            'topics': {},
            'topic_assignments': [],
            'taxonomy_matches': [],
            'hierarchical_topics': {},
            'trends': {},
            'insights': '',
            'filename': ''
        }
        
        try:
            results['reviews'] = reviews
            
            # Phase 1: Sentiment Analysis
            progress_bar.progress(20)
            status_text.text("Phase 1: AI Sentiment Analysis...")
            
            sentiment_results = self.analyzer.analyze_sentiment_batch(reviews)
            results['sentiment_results'] = sentiment_results
            
            progress_bar.progress(40)
            
            # Phase 2: Topic Modeling
            status_text.text("Phase 2: Topic Discovery...")
            
            topics, topic_assignments = self.analyzer.extract_topics(reviews)
            results['topics'] = topics
            results['topic_assignments'] = topic_assignments
            
            progress_bar.progress(60)
            
            # Phase 3: Taxonomy Matching
            if use_taxonomy and self.taxonomy_matcher:
                status_text.text("Phase 3: Category Matching...")
                
                taxonomy_matches = self.taxonomy_matcher.categorize_reviews_batch(reviews, top_n=3)
                results['taxonomy_matches'] = taxonomy_matches
                
                progress_bar.progress(75)
            
            # Create hierarchical structure
            results['hierarchical_topics'] = self.create_hierarchical_topics(
                topics, topic_assignments, results.get('taxonomy_matches', [])
            )
            
            # Phase 4: Trend Analysis
            status_text.text("Phase 4: Trend Analysis...")
            
            reviews_with_sentiment = []
            for i, review in enumerate(reviews):
                review_copy = review.copy()
                if i < len(sentiment_results):
                    review_copy['sentiment'] = sentiment_results[i]['sentiment']
                reviews_with_sentiment.append(review_copy)
            
            trends = self.analyzer.analyze_trends(reviews_with_sentiment)
            results['trends'] = trends
            
            progress_bar.progress(85)
            
            # Phase 5: Generate Insights
            status_text.text("Phase 5: AI Insights...")
            
            insights = self.analyzer.generate_insights(sentiment_results, topics, trends)
            results['insights'] = insights
            
            progress_bar.progress(95)
            
            # Phase 6: Generate Report
            status_text.text("Phase 6: Creating Report...")
            
            filename = self.excel_generator.generate_report(
                reviews=reviews,
                sentiment_results=sentiment_results,
                topics=topics,
                topic_assignments=topic_assignments,
                trends=trends,
                insights=insights,
                taxonomy_matches=results.get('taxonomy_matches', [])
            )
            results['filename'] = filename
            
            progress_bar.progress(100)
            status_text.text("Analysis Complete!")
            
            return results
            
        except Exception as e:
            st.error(f"Analysis failed: {str(e)}")
            return None

def load_logo():
    """Load and display logo"""
    logo_path = "logo.png"
    if os.path.exists(logo_path):
        with open(logo_path, "rb") as f:
            logo_data = base64.b64encode(f.read()).decode()
        return f'<img src="data:image/png;base64,{logo_data}" style="max-width: 180px; margin: auto; display: block;">'
    else:
        return '<h2 style="text-align: center; color: #4A90E2;">PULSE</h2>'

def create_download_link(filename):
    """Create download link for Excel file"""
    try:
        with open(filename, 'rb') as f:
            data = f.read()
        b64 = base64.b64encode(data).decode()
        href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="{filename}" style="color: #4A90E2; text-decoration: none; font-weight: 600;">Download Excel Report</a>'
        return href
    except Exception as e:
        return f"Error: {e}"

def display_hierarchical_topics(hierarchical_topics, total_reviews):
    """Display hierarchical topic drill-down with volume percentages"""
    st.markdown('<div class="section-header"><span class="section-icon">📊</span><h3>Topic Distribution - Hierarchical View</h3></div>', unsafe_allow_html=True)
    
    for level1, data in hierarchical_topics.items():
        level1_count = data['total']
        level1_pct = (level1_count / total_reviews * 100) if total_reviews > 0 else 0
        
        with st.expander(f"{level1} ({level1_count} reviews, {level1_pct:.1f}%)", expanded=True):
            level2_data = data['level2']
            
            if level2_data:
                df = pd.DataFrame([
                    {
                        'Category': cat,
                        'Count': count,
                        '% of Total': f"{(count/total_reviews*100):.1f}%",
                        '% of Parent': f"{(count/level1_count*100):.1f}%"
                    }
                    for cat, count in sorted(level2_data.items(), key=lambda x: x[1], reverse=True)
                ])
                
                st.dataframe(df, use_container_width=True, hide_index=True)
                
                fig = go.Figure()
                
                categories = list(level2_data.keys())
                values = list(level2_data.values())
                percentages = [(v/total_reviews*100) for v in values]
                
                fig.add_trace(go.Bar(
                    y=categories,
                    x=values,
                    orientation='h',
                    text=[f'{v} ({p:.1f}%)' for v, p in zip(values, percentages)],
                    textposition='outside',
                    marker=dict(
                        color=values,
                        colorscale='Blues',
                        showscale=False
                    ),
                    hovertemplate='<b>%{y}</b><br>Count: %{x}<br><extra></extra>'
                ))
                
                fig.update_layout(
                    title=f"Level 2 Categories under {level1}",
                    xaxis_title="Number of Reviews",
                    yaxis_title="",
                    height=max(300, len(categories) * 40),
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#FFFFFF'),
                    showlegend=False
                )
                
                st.plotly_chart(fig, use_container_width=True)

def display_bi_dashboard(results):
    """Display BI-style dashboard with all metrics"""
    st.markdown('<div class="section-header"><span class="section-icon">📈</span><h2>Executive Dashboard</h2></div>', unsafe_allow_html=True)
    
    total_reviews = len(results['reviews'])
    sentiment_results = results['sentiment_results']
    sentiment_counts = Counter([r.get('sentiment', 'unknown') for r in sentiment_results])
    
    # Top KPIs
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown('<div class="bi-card">', unsafe_allow_html=True)
        st.metric("Total Reviews", f"{total_reviews:,}")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        positive_pct = (sentiment_counts.get('positive', 0) / total_reviews * 100) if total_reviews > 0 else 0
        st.markdown('<div class="bi-card">', unsafe_allow_html=True)
        st.metric("Positive Sentiment", f"{positive_pct:.1f}%", 
                 delta=f"{sentiment_counts.get('positive', 0)} reviews")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        negative_pct = (sentiment_counts.get('negative', 0) / total_reviews * 100) if total_reviews > 0 else 0
        st.markdown('<div class="bi-card">', unsafe_allow_html=True)
        st.metric("Negative Sentiment", f"{negative_pct:.1f}%",
                 delta=f"{sentiment_counts.get('negative', 0)} reviews",
                 delta_color="inverse")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        st.markdown('<div class="bi-card">', unsafe_allow_html=True)
        st.metric("Categories", len(results.get('hierarchical_topics', {})))
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Sentiment Distribution Chart
    st.markdown("---")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="bi-card">', unsafe_allow_html=True)
        st.markdown("### Sentiment Analysis")
        
        fig = go.Figure(data=[go.Pie(
            labels=list(sentiment_counts.keys()),
            values=list(sentiment_counts.values()),
            hole=0.4,
            marker=dict(colors=['#28a745', '#dc3545', '#ffc107']),
            textinfo='label+percent',
            textfont=dict(size=14, color='white')
        )])
        
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#FFFFFF'),
            showlegend=True,
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="bi-card">', unsafe_allow_html=True)
        st.markdown("### Volume Distribution")
        
        if results.get('hierarchical_topics'):
            all_categories = []
            all_counts = []
            
            for level1, data in results['hierarchical_topics'].items():
                for level2, count in data['level2'].items():
                    all_categories.append(f"{level1}: {level2}")
                    all_counts.append(count)
            
            sorted_data = sorted(zip(all_categories, all_counts), key=lambda x: x[1], reverse=True)[:10]
            categories, counts = zip(*sorted_data) if sorted_data else ([], [])
            
            percentages = [(c/total_reviews*100) for c in counts]
            
            fig = go.Figure(data=[go.Bar(
                y=list(categories),
                x=list(counts),
                orientation='h',
                text=[f'{c} ({p:.1f}%)' for c, p in zip(counts, percentages)],
                textposition='outside',
                marker=dict(color='#4A90E2'),
                hovertemplate='<b>%{y}</b><br>Count: %{x}<br><extra></extra>'
            )])
            
            fig.update_layout(
                title="Top 10 Categories by Volume",
                xaxis_title="Number of Reviews",
                yaxis_title="",
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#FFFFFF'),
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Hierarchical drill-down
    st.markdown("---")
    if results.get('hierarchical_topics'):
        display_hierarchical_topics(results['hierarchical_topics'], total_reviews)

def main():
    """Main application"""
    
    # Initialize session state
    if 'analysis_results' not in st.session_state:
        st.session_state.analysis_results = None
    if 'analyzer' not in st.session_state:
        st.session_state.analyzer = StreamlitAnalyzer()
    if 'taxonomy_file_uploaded' not in st.session_state:
        st.session_state.taxonomy_file_uploaded = False
    
    # Sidebar with logo
    with st.sidebar:
        st.markdown('<div class="logo-container">', unsafe_allow_html=True)
        st.markdown(load_logo(), unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Configuration section
        st.markdown('<div class="section-header"><span class="section-icon">⚙️</span><h3>Configuration</h3></div>', unsafe_allow_html=True)
        
        # API Key status
        api_key_status = "Active" if config.OPENAI_API_KEY and config.OPENAI_API_KEY != "your_openai_api_key_here" else "Missing"
        st.info(f"**OpenAI API:** {api_key_status}")
        
        if api_key_status == "Missing":
            st.error("Configure API key in .env file")
            st.stop()
        
        # Taxonomy Configuration
        st.markdown('<div class="section-header"><span class="section-icon">🏷️</span><h3>Taxonomy</h3></div>', unsafe_allow_html=True)
        
        taxonomy_file = st.file_uploader(
            "Upload Taxonomy File",
            type=['xlsx', 'xls'],
            help="Excel file with predefined categories"
        )
        
        taxonomy_path = None
        if taxonomy_file:
            with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp_file:
                tmp_file.write(taxonomy_file.getvalue())
                taxonomy_path = tmp_file.name
            st.success("Taxonomy loaded")
            st.session_state.taxonomy_file_uploaded = True
        
        use_taxonomy = st.checkbox(
            "Enable Taxonomy Matching",
            value=st.session_state.taxonomy_file_uploaded,
            disabled=not st.session_state.taxonomy_file_uploaded
        )
        
        # Analysis Settings
        st.markdown('<div class="section-header"><span class="section-icon">🎛️</span><h3>Settings</h3></div>', unsafe_allow_html=True)
        
        max_reviews = st.slider("Max Reviews", 50, 2000, 500, 50)
        
        with st.expander("Advanced"):
            batch_size = st.slider("Batch Size", 10, 50, 20)
            num_topics = st.slider("Number of Topics", 3, 10, 5)
    
    # Main content area
    st.markdown('<h1 style="text-align: center; color: #4A90E2; margin-bottom: 2rem;">Customer Insights Analytics Platform</h1>', unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["Data Input", "Analytics Dashboard", "Documentation"])
    
    with tab1:
        st.markdown('<div class="section-header"><span class="section-icon">📥</span><h2>Data Source Selection</h2></div>', unsafe_allow_html=True)
        
        data_source = st.radio(
            "Choose your data input method:",
            ["Upload File (Excel/CSV)", "Web Scraping (URLs)"],
            horizontal=True
        )
        
        all_reviews = []
        uploaded_file = None
        valid_urls = []
        
        if data_source == "Upload File (Excel/CSV)":
            st.markdown('<div class="bi-card">', unsafe_allow_html=True)
            st.markdown("### File Upload")
            st.write("Upload Excel or CSV file containing customer reviews")
            
            uploaded_file = st.file_uploader(
                "Select File",
                type=['csv', 'xlsx', 'xls'],
                help="File should contain review text in a column named 'Comments', 'Review', or similar"
            )
            
            if uploaded_file:
                st.success(f"{uploaded_file.name} uploaded ({len(uploaded_file.getvalue())/1024/1024:.2f} MB)")
                
                if st.button("Preview Data", use_container_width=True):
                    try:
                        if uploaded_file.name.endswith('.csv'):
                            preview_df = pd.read_csv(uploaded_file, nrows=5)
                        else:
                            preview_df = pd.read_excel(uploaded_file, nrows=5)
                        
                        st.dataframe(preview_df, use_container_width=True)
                        uploaded_file.seek(0)
                    except Exception as e:
                        st.error(f"Preview error: {e}")
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        else:
            st.markdown('<div class="bi-card">', unsafe_allow_html=True)
            st.markdown("### Web Scraping")
            
            url_input = st.text_area(
                "Enter URLs (one per line):",
                height=150,
                placeholder="https://www.trustpilot.com/review/company.com"
            )
            
            if url_input:
                urls = [url.strip() for url in url_input.split('\n') if url.strip()]
                valid_urls, invalid_urls = st.session_state.analyzer.process_urls(urls)
                
                if valid_urls:
                    st.success(f"{len(valid_urls)} valid URLs")
                if invalid_urls:
                    st.warning(f"{len(invalid_urls)} invalid URLs")
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Analysis button
        st.markdown("---")
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("START ANALYSIS", type="primary", use_container_width=True):
                if data_source == "Upload File (Excel/CSV)" and not uploaded_file:
                    st.error("Please upload a file first")
                elif data_source == "Web Scraping (URLs)" and not valid_urls:
                    st.error("Please enter at least one URL")
                else:
                    if not st.session_state.analyzer.initialize_components(taxonomy_path):
                        st.stop()
                    
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    if data_source == "Upload File (Excel/CSV)":
                        status_text.text("Processing file...")
                        progress_bar.progress(10)
                        
                        reviews, message = st.session_state.analyzer.process_uploaded_file(
                            uploaded_file, max_reviews
                        )
                        
                        if not reviews:
                            st.error(f"{message}")
                            st.stop()
                        
                        all_reviews = reviews
                    
                    else:
                        status_text.text("Scraping websites...")
                        progress_bar.progress(5)
                        
                        for i, url in enumerate(valid_urls):
                            status_text.text(f"Scraping {i+1}/{len(valid_urls)}...")
                            reviews = st.session_state.analyzer.scraper.scrape_reviews(url, max_pages=5)
                            if reviews:
                                cleaned = st.session_state.analyzer.scraper.clean_reviews(reviews)
                                all_reviews.extend(cleaned[:max_reviews])
                            progress_bar.progress(5 + (i + 1) * 10 // len(valid_urls))
                    
                    if all_reviews:
                        with st.spinner("Processing..."):
                            results = st.session_state.analyzer.run_analysis(
                                all_reviews, use_taxonomy, progress_bar, status_text
                            )
                        
                        if results:
                            st.session_state.analysis_results = results
                            st.success("Analysis Complete!")
                            st.balloons()
                            
                            if results['filename']:
                                st.markdown(create_download_link(results['filename']), unsafe_allow_html=True)
    
    with tab2:
        if st.session_state.analysis_results:
            display_bi_dashboard(st.session_state.analysis_results)
        else:
            st.info("Run an analysis from the Data Input tab to view results")
    
    with tab3:
        st.markdown('<div class="section-header"><span class="section-icon">📖</span><h2>Documentation</h2></div>', unsafe_allow_html=True)
        
        st.markdown("""
        ### Getting Started
        1. Upload your taxonomy file (sidebar)
        2. Choose data source (upload file or scrape URLs)
        3. Configure analysis settings
        4. Click "Start Analysis"
        5. View results in Analytics Dashboard
        
        ### Features
        - **Hierarchical Categories**: Level 1 to Level 2 drill-down
        - **Volume Analysis**: See percentage of total reviews per category
        - **BI-Style Dashboard**: Professional analytics interface
        - **AI-Powered Insights**: Automated pattern detection
        
        ### Taxonomy Format
        Your Excel taxonomy should have:
        - **High Level Category**: Level 1 (e.g., "Billing Issues")
        - **Taxonomy Name**: Level 2 (e.g., "High Bill", "Incorrect Bill")
        - **Phrases**: Comma-separated keywords
        
        ### Tips
        - Start with 100-500 reviews for testing
        - Use descriptive Level 1 categories
        - Add multiple Level 2 sub-categories per Level 1
        - Include keyword variations in taxonomy
        """)

if __name__ == "__main__":
    main()