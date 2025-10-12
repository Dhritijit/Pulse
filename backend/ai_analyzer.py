"""
AI-powered analysis module using OpenAI
Handles sentiment analysis, topic modeling, and trend detection
NOW WITH HIERARCHICAL TOPIC CLASSIFICATION (Level 1 → Level 2)
"""

from openai import OpenAI
import pandas as pd
import numpy as np
import logging
import json
import time
from datetime import datetime, timedelta
from collections import Counter, defaultdict
from sklearn.cluster import KMeans
from sklearn.metrics.pairwise import cosine_similarity
from textblob import TextBlob
import re
import config

class AIAnalyzer:
    def __init__(self):
        self.setup_logging()
        self.setup_openai()
        self.sentiment_cache = {}
        self.topic_cache = {}
        
    def setup_logging(self):
        """Setup logging configuration"""
        self.logger = logging.getLogger(__name__)
        
    def setup_openai(self):
        """Initialize OpenAI client"""
        if not config.OPENAI_API_KEY:
            raise ValueError("OpenAI API key not found. Please set OPENAI_API_KEY in your .env file")
        
        self.client = OpenAI(api_key=config.OPENAI_API_KEY)
        self.logger.info("OpenAI client initialized")
        
    def analyze_sentiment_batch(self, reviews, batch_size=20):
        """Analyze sentiment for multiple reviews using GPT-4"""
        self.logger.info(f"Starting sentiment analysis for {len(reviews)} reviews")
        
        results = []
        total_batches = (len(reviews) + batch_size - 1) // batch_size
        
        for i in range(0, len(reviews), batch_size):
            batch = reviews[i:i + batch_size]
            batch_num = (i // batch_size) + 1
            
            self.logger.info(f"Processing sentiment batch {batch_num}/{total_batches}")
            
            try:
                batch_results = self._process_sentiment_batch(batch)
                results.extend(batch_results)
                
                # Rate limiting
                time.sleep(1)
                
            except Exception as e:
                self.logger.error(f"Error processing sentiment batch {batch_num}: {e}")
                # Fallback to TextBlob for this batch
                fallback_results = self._fallback_sentiment_analysis(batch)
                results.extend(fallback_results)
                
        return results
        
    def _process_sentiment_batch(self, reviews):
        """Process a batch of reviews for sentiment analysis"""
        # Prepare reviews for GPT-4
        review_texts = []
        for i, review in enumerate(reviews):
            text = review.get('text', '')[:500]  # Limit text length
            review_texts.append(f"Review {i+1}: {text}")
            
        prompt = self._create_sentiment_prompt(review_texts)
        
        try:
            response = self.client.chat.completions.create(
                model=config.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "You are an expert sentiment analyzer. Analyze customer reviews and provide detailed sentiment analysis."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=2000
            )
            
            result_text = response.choices[0].message.content
            return self._parse_sentiment_response(result_text, reviews)
            
        except Exception as e:
            self.logger.error(f"OpenAI API error in sentiment analysis: {e}")
            raise
            
    def _create_sentiment_prompt(self, review_texts):
        """Create prompt for sentiment analysis"""
        reviews_text = "\n".join(review_texts)
        
        prompt = f"""
        Analyze the sentiment of each review below. For each review, provide:
        1. Sentiment: positive, negative, or neutral
        2. Confidence score: 0-100 (how confident you are)
        3. Key emotions: list of emotions detected
        4. Key themes: main topics/themes mentioned
        
        Please respond in JSON format like this:
        {{
            "results": [
                {{
                    "review_number": 1,
                    "sentiment": "positive",
                    "confidence": 85,
                    "emotions": ["satisfaction", "happiness"],
                    "themes": ["customer service", "product quality"]
                }}
            ]
        }}
        
        Reviews to analyze:
        {reviews_text}
        """
        
        return prompt
        
    def _parse_sentiment_response(self, response_text, reviews):
        """Parse GPT-4 sentiment analysis response"""
        try:
            # Clean response text
            response_text = response_text.strip()
            if response_text.startswith('```json'):
                response_text = response_text[7:-3]
            elif response_text.startswith('```'):
                response_text = response_text[3:-3]
                
            data = json.loads(response_text)
            results = []
            
            for i, result in enumerate(data.get('results', [])):
                if i < len(reviews):
                    analysis = {
                        'sentiment': result.get('sentiment', 'neutral'),
                        'confidence': result.get('confidence', 50) / 100.0,
                        'emotions': result.get('emotions', []),
                        'themes': result.get('themes', []),
                        'analysis_method': 'gpt4'
                    }
                    results.append(analysis)
                    
            return results
            
        except Exception as e:
            self.logger.error(f"Error parsing sentiment response: {e}")
            return self._fallback_sentiment_analysis(reviews)
            
    def _fallback_sentiment_analysis(self, reviews):
        """Fallback sentiment analysis using TextBlob"""
        results = []
        
        for review in reviews:
            text = review.get('text', '')
            blob = TextBlob(text)
            
            # Convert polarity to sentiment categories
            polarity = blob.sentiment.polarity
            if polarity > 0.1:
                sentiment = 'positive'
            elif polarity < -0.1:
                sentiment = 'negative'
            else:
                sentiment = 'neutral'
                
            analysis = {
                'sentiment': sentiment,
                'confidence': abs(polarity),
                'emotions': [],
                'themes': [],
                'analysis_method': 'textblob'
            }
            results.append(analysis)
            
        return results
        
    def extract_topics(self, reviews):
        """
        Extract topics using GPT-4 with HIERARCHICAL STRUCTURE (Level 1 → Level 2)
        NEW: Creates proper taxonomy tree with Level 1 and Level 2 categories
        """
        self.logger.info(f"Starting hierarchical topic modeling for {len(reviews)} reviews")
        
        # Sample reviews for topic extraction if too many
        if len(reviews) > 100:
            sampled_reviews = np.random.choice(reviews, 100, replace=False)
        else:
            sampled_reviews = reviews
            
        try:
            # Step 1: Let LLM create hierarchical topic structure
            hierarchical_topics = self._create_hierarchical_topics(sampled_reviews)
            self.logger.info(f"LLM created {len(hierarchical_topics)} Level 1 topics with Level 2 subcategories")
            
            # Step 2: Assign topics to all reviews
            topic_assignments = self._assign_hierarchical_topics(reviews, hierarchical_topics)
            
            return hierarchical_topics, topic_assignments
            
        except Exception as e:
            self.logger.error(f"Error in hierarchical topic modeling: {e}")
            # Fallback: Try simpler approach
            return self._fallback_hierarchical_extraction(reviews)
    
    def _create_hierarchical_topics(self, reviews):
        """
        NEW METHOD: Ask LLM to create hierarchical Level 1 → Level 2 topic structure
        """
        # Sample reviews for analysis
        sample_size = min(30, len(reviews))
        sample_reviews = np.random.choice(reviews, sample_size, replace=False)
        
        review_texts = [r.get('text', '')[:400] for r in sample_reviews]
        combined_text = "\n---\n".join(review_texts)
        
        prompt = f"""
        Analyze these customer reviews and create a HIERARCHICAL topic taxonomy with 2 levels:
        
        LEVEL 1: Broad categories (3-5 main themes)
        LEVEL 2: Specific sub-topics under each Level 1 category (2-4 per Level 1)
        
        Requirements:
        - Level 1 names should be clear, broad categories (e.g., "Billing Issues", "Customer Service", "Product Quality")
        - Level 2 names should be specific issues under each Level 1 (e.g., under "Billing Issues": "High Charges", "Incorrect Bill")
        - Every topic must have a descriptive name (NO "Topic 1", "Topic 2", etc.)
        - Each Level 2 topic must belong to exactly one Level 1 parent
        
        Respond with ONLY a JSON object in this EXACT format:
        {{
            "level1_topics": [
                {{
                    "id": "L1_1",
                    "name": "Billing Issues",
                    "description": "Problems related to billing and charges",
                    "level2_topics": [
                        {{"id": "L2_1_1", "name": "High Charges", "description": "Complaints about high bills"}},
                        {{"id": "L2_1_2", "name": "Incorrect Bill", "description": "Billing errors and discrepancies"}}
                    ]
                }},
                {{
                    "id": "L1_2",
                    "name": "Customer Service",
                    "description": "Customer support and service quality",
                    "level2_topics": [
                        {{"id": "L2_2_1", "name": "Poor Response Time", "description": "Slow customer service"}},
                        {{"id": "L2_2_2", "name": "Unhelpful Staff", "description": "Staff not resolving issues"}}
                    ]
                }}
            ]
        }}
        
        Reviews:
        {combined_text}
        """
        
        try:
            response = self.client.chat.completions.create(
                model=config.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "You are an expert at creating hierarchical taxonomies from customer feedback. Always provide descriptive, meaningful category names."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=1500
            )
            
            result_text = response.choices[0].message.content
            result = json.loads(result_text.strip().replace('```json', '').replace('```', ''))
            
            hierarchical_topics = result.get('level1_topics', [])
            
            # Validate that we have proper structure
            if not hierarchical_topics or len(hierarchical_topics) == 0:
                raise ValueError("No topics generated")
            
            # Ensure each Level 1 has Level 2 topics
            for level1 in hierarchical_topics:
                if 'level2_topics' not in level1 or not level1['level2_topics']:
                    # If no Level 2, create a generic one
                    level1['level2_topics'] = [{
                        'id': f"{level1['id']}_1",
                        'name': f"{level1['name']} - General",
                        'description': f"General issues related to {level1['name']}"
                    }]
            
            self.logger.info(f"✅ Created {len(hierarchical_topics)} Level 1 topics")
            for topic in hierarchical_topics:
                self.logger.info(f"  - {topic['name']}: {len(topic['level2_topics'])} Level 2 topics")
            
            return hierarchical_topics
            
        except Exception as e:
            self.logger.error(f"Error creating hierarchical topics: {e}")
            # Return a basic structure
            return self._create_basic_hierarchy()
    
    def _create_basic_hierarchy(self):
        """Create a basic 2-level hierarchy as fallback"""
        return [
            {
                'id': 'L1_1',
                'name': 'General Feedback',
                'description': 'General customer feedback',
                'level2_topics': [
                    {'id': 'L2_1_1', 'name': 'Product Feedback', 'description': 'Comments about products'},
                    {'id': 'L2_1_2', 'name': 'Service Feedback', 'description': 'Comments about service'}
                ]
            },
            {
                'id': 'L1_2',
                'name': 'Issues and Complaints',
                'description': 'Problems and complaints',
                'level2_topics': [
                    {'id': 'L2_2_1', 'name': 'Technical Issues', 'description': 'Technical problems'},
                    {'id': 'L2_2_2', 'name': 'Service Issues', 'description': 'Service-related problems'}
                ]
            }
        ]
    
    def _assign_hierarchical_topics(self, reviews, hierarchical_topics):
        """
        Assign each review to a Level 1 and Level 2 topic
        """
        topic_assignments = []
        
        # Create a flat list of all Level 2 topics with their Level 1 parent
        all_topics = []
        for level1 in hierarchical_topics:
            for level2 in level1['level2_topics']:
                all_topics.append({
                    'level1_id': level1['id'],
                    'level1_name': level1['name'],
                    'level2_id': level2['id'],
                    'level2_name': level2['name'],
                    'combined_desc': f"{level1['name']}: {level2['name']} - {level2['description']}"
                })
        
        # Process reviews in batches
        batch_size = 20
        for i in range(0, len(reviews), batch_size):
            batch = reviews[i:i + batch_size]
            
            try:
                batch_assignments = self._assign_topics_batch(batch, all_topics)
                topic_assignments.extend(batch_assignments)
                time.sleep(0.5)  # Rate limiting
            except Exception as e:
                self.logger.error(f"Error assigning topics to batch: {e}")
                # Fallback: assign randomly
                for _ in batch:
                    random_topic = np.random.choice(all_topics)
                    topic_assignments.append({
                        'level1_id': random_topic['level1_id'],
                        'level1_name': random_topic['level1_name'],
                        'level2_id': random_topic['level2_id'],
                        'level2_name': random_topic['level2_name'],
                        'confidence': 0.5
                    })
        
        return topic_assignments
    
    def _assign_topics_batch(self, reviews, all_topics):
        """Assign topics to a batch of reviews using LLM"""
        review_texts = []
        for i, review in enumerate(reviews):
            text = review.get('text', '')[:300]
            review_texts.append(f"Review {i+1}: {text}")
        
        reviews_combined = "\n".join(review_texts)
        
        topics_desc = "\n".join([f"{i+1}. {t['combined_desc']}" for i, t in enumerate(all_topics)])
        
        prompt = f"""
        Assign each review to the MOST APPROPRIATE topic from the list below.
        
        Available Topics:
        {topics_desc}
        
        Reviews:
        {reviews_combined}
        
        Respond with ONLY a JSON array:
        [
            {{"review_number": 1, "topic_number": 3}},
            {{"review_number": 2, "topic_number": 1}}
        ]
        
        Topic number must be from 1 to {len(all_topics)}.
        """
        
        try:
            response = self.client.chat.completions.create(
                model=config.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "You are an expert at categorizing customer feedback into predefined topics."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=500
            )
            
            result_text = response.choices[0].message.content.strip()
            result_text = result_text.replace('```json', '').replace('```', '').strip()
            assignments = json.loads(result_text)
            
            batch_results = []
            for assignment in assignments:
                topic_idx = assignment.get('topic_number', 1) - 1
                topic_idx = max(0, min(topic_idx, len(all_topics) - 1))  # Bounds check
                
                selected_topic = all_topics[topic_idx]
                batch_results.append({
                    'level1_id': selected_topic['level1_id'],
                    'level1_name': selected_topic['level1_name'],
                    'level2_id': selected_topic['level2_id'],
                    'level2_name': selected_topic['level2_name'],
                    'confidence': 0.85
                })
            
            return batch_results
            
        except Exception as e:
            self.logger.error(f"Error in batch topic assignment: {e}")
            raise
    
    def _fallback_hierarchical_extraction(self, reviews):
        """Fallback if hierarchical extraction fails"""
        self.logger.warning("Using fallback hierarchical extraction")
        
        hierarchical_topics = self._create_basic_hierarchy()
        
        # Random assignment
        topic_assignments = []
        all_topics = []
        for level1 in hierarchical_topics:
            for level2 in level1['level2_topics']:
                all_topics.append({
                    'level1_id': level1['id'],
                    'level1_name': level1['name'],
                    'level2_id': level2['id'],
                    'level2_name': level2['name']
                })
        
        for _ in reviews:
            random_topic = np.random.choice(all_topics)
            topic_assignments.append({
                'level1_id': random_topic['level1_id'],
                'level1_name': random_topic['level1_name'],
                'level2_id': random_topic['level2_id'],
                'level2_name': random_topic['level2_name'],
                'confidence': 0.5
            })
        
        return hierarchical_topics, topic_assignments
        
    def analyze_trends(self, reviews):
        """Analyze sentiment and topic trends over time"""
        self.logger.info("Analyzing trends over time")
        
        # Convert reviews to DataFrame for easier analysis
        df = pd.DataFrame(reviews)
        
        # Parse dates
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        df = df.dropna(subset=['date'])
        
        if len(df) < config.MIN_REVIEWS_FOR_TREND:
            self.logger.warning(f"Not enough reviews for trend analysis: {len(df)}")
            return {}
            
        # Sort by date
        df = df.sort_values('date')
        
        trends = {}
        
        # Sentiment trends
        trends['sentiment_trends'] = self._analyze_sentiment_trends(df)
        
        # Volume trends
        trends['volume_trends'] = self._analyze_volume_trends(df)
        
        # Rating trends (if available)
        if 'rating' in df.columns:
            trends['rating_trends'] = self._analyze_rating_trends(df)
            
        return trends
        
    def _analyze_sentiment_trends(self, df):
        """Analyze sentiment trends over time"""
        sentiment_trends = {}
        
        for period in config.TREND_PERIODS:
            if period == 'daily':
                grouped = df.groupby(df['date'].dt.date)
            elif period == 'weekly':
                grouped = df.groupby(df['date'].dt.to_period('W'))
            elif period == 'monthly':
                grouped = df.groupby(df['date'].dt.to_period('M'))
                
            trend_data = []
            for period_key, group in grouped:
                sentiment_counts = group['sentiment'].value_counts()
                total = len(group)
                
                period_data = {
                    'period': str(period_key),
                    'total_reviews': total,
                    'positive_pct': sentiment_counts.get('positive', 0) / total * 100,
                    'negative_pct': sentiment_counts.get('negative', 0) / total * 100,
                    'neutral_pct': sentiment_counts.get('neutral', 0) / total * 100
                }
                trend_data.append(period_data)
                
            sentiment_trends[period] = trend_data
            
        return sentiment_trends
        
    def _analyze_volume_trends(self, df):
        """Analyze review volume trends"""
        volume_trends = {}
        
        for period in config.TREND_PERIODS:
            if period == 'daily':
                grouped = df.groupby(df['date'].dt.date).size()
            elif period == 'weekly':
                grouped = df.groupby(df['date'].dt.to_period('W')).size()
            elif period == 'monthly':
                grouped = df.groupby(df['date'].dt.to_period('M')).size()
                
            trend_data = [
                {'period': str(period_key), 'review_count': count}
                for period_key, count in grouped.items()
            ]
            
            volume_trends[period] = trend_data
            
        return volume_trends
        
    def _analyze_rating_trends(self, df):
        """Analyze rating trends over time"""
        df['rating'] = pd.to_numeric(df['rating'], errors='coerce')
        df_ratings = df.dropna(subset=['rating'])
        
        rating_trends = {}
        
        for period in config.TREND_PERIODS:
            if period == 'daily':
                grouped = df_ratings.groupby(df_ratings['date'].dt.date)['rating']
            elif period == 'weekly':
                grouped = df_ratings.groupby(df_ratings['date'].dt.to_period('W'))['rating']
            elif period == 'monthly':
                grouped = df_ratings.groupby(df_ratings['date'].dt.to_period('M'))['rating']
                
            trend_data = []
            for period_key, ratings in grouped:
                period_data = {
                    'period': str(period_key),
                    'avg_rating': ratings.mean(),
                    'median_rating': ratings.median(),
                    'rating_count': len(ratings)
                }
                trend_data.append(period_data)
                
            rating_trends[period] = trend_data
            
        return rating_trends
        
    def generate_insights(self, sentiment_results, topics, trends):
        """Generate AI-powered insights using GPT-4"""
        self.logger.info("Generating AI insights")
        
        # Prepare summary data
        sentiment_summary = {
            'positive': sum(1 for r in sentiment_results if r['sentiment'] == 'positive'),
            'negative': sum(1 for r in sentiment_results if r['sentiment'] == 'negative'),
            'neutral': sum(1 for r in sentiment_results if r['sentiment'] == 'neutral'),
            'total': len(sentiment_results)
        }
        
        # Format hierarchical topics for prompt
        topic_summary = []
        for level1 in topics:
            topic_summary.append(f"**{level1['name']}**: {level1['description']}")
            for level2 in level1.get('level2_topics', []):
                topic_summary.append(f"  - {level2['name']}: {level2['description']}")
        
        topics_text = "\n".join(topic_summary)
        
        prompt = f"""
        Based on the customer review analysis below, provide strategic insights and recommendations.
        
        Sentiment Summary:
        - Total Reviews: {sentiment_summary['total']}
        - Positive: {sentiment_summary['positive']} ({sentiment_summary['positive']/sentiment_summary['total']*100:.1f}%)
        - Negative: {sentiment_summary['negative']} ({sentiment_summary['negative']/sentiment_summary['total']*100:.1f}%)
        - Neutral: {sentiment_summary['neutral']} ({sentiment_summary['neutral']/sentiment_summary['total']*100:.1f}%)
        
        Topic Hierarchy:
        {topics_text}
        
        Please provide:
        1. Overall sentiment assessment
        2. Key areas of concern (based on negative sentiment and topics)
        3. Strengths to leverage (based on positive sentiment and topics)
        4. Actionable recommendations
        5. Priority areas for improvement
        
        Format your response as structured insights that can be included in an executive summary.
        """
        
        try:
            response = self.client.chat.completions.create(
                model=config.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "You are a business analyst expert at interpreting customer feedback data and providing strategic insights."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=1500
            )
            
            insights = response.choices[0].message.content
            return insights
            
        except Exception as e:
            self.logger.error(f"Error generating insights: {e}")
            return "AI insights generation failed. Please review the data manually."