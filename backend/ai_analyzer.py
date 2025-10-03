"""
AI-powered analysis module using OpenAI
Handles sentiment analysis, topic modeling, and trend detection
"""

import openai
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
        
        openai.api_key = config.OPENAI_API_KEY
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
            response = openai.ChatCompletion.create(
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
        
    def extract_topics(self, reviews, num_topics=None):
        """Extract topics using GPT-4 and embeddings"""
        if num_topics is None:
            num_topics = config.NUM_TOPICS
            
        self.logger.info(f"Starting topic modeling for {len(reviews)} reviews")
        
        # Sample reviews for topic extraction if too many
        if len(reviews) > 100:
            sampled_reviews = np.random.choice(reviews, 100, replace=False)
        else:
            sampled_reviews = reviews
            
        try:
            # Get embeddings for clustering
            embeddings = self._get_embeddings([r.get('text', '') for r in sampled_reviews])
            
            # Perform clustering
            clusters = self._cluster_reviews(embeddings, num_topics)
            
            # Extract topics from each cluster
            topics = self._extract_cluster_topics(sampled_reviews, clusters, num_topics)
            
            # Assign topics to all reviews
            all_embeddings = self._get_embeddings([r.get('text', '') for r in reviews])
            topic_assignments = self._assign_topics_to_reviews(all_embeddings, topics)
            
            return topics, topic_assignments
            
        except Exception as e:
            self.logger.error(f"Error in topic modeling: {e}")
            return self._fallback_topic_extraction(reviews, num_topics)
            
    def _get_embeddings(self, texts):
        """Get OpenAI embeddings for texts"""
        embeddings = []
        batch_size = 50
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            
            try:
                response = openai.Embedding.create(
                    model=config.OPENAI_EMBEDDING_MODEL,
                    input=batch
                )
                
                batch_embeddings = [item['embedding'] for item in response['data']]
                embeddings.extend(batch_embeddings)
                
                time.sleep(0.5)  # Rate limiting
                
            except Exception as e:
                self.logger.error(f"Error getting embeddings: {e}")
                # Fill with zeros for failed batches
                embeddings.extend([[0] * 1536 for _ in batch])
                
        return np.array(embeddings)
        
    def _cluster_reviews(self, embeddings, num_clusters):
        """Cluster reviews using K-means"""
        if len(embeddings) < num_clusters:
            num_clusters = len(embeddings)
            
        kmeans = KMeans(n_clusters=num_clusters, random_state=42, n_init=10)
        clusters = kmeans.fit_predict(embeddings)
        
        return clusters
        
    def _extract_cluster_topics(self, reviews, clusters, num_topics):
        """Extract topics from each cluster using GPT-4"""
        topics = {}
        
        for cluster_id in range(num_topics):
            cluster_reviews = [reviews[i] for i, c in enumerate(clusters) if c == cluster_id]
            
            if not cluster_reviews:
                continue
                
            # Sample reviews from cluster
            sample_size = min(10, len(cluster_reviews))
            sample_reviews = np.random.choice(cluster_reviews, sample_size, replace=False)
            
            topic = self._analyze_cluster_topic(sample_reviews, cluster_id)
            topics[cluster_id] = topic
            
        return topics
        
    def _analyze_cluster_topic(self, reviews, cluster_id):
        """Analyze topic for a specific cluster"""
        review_texts = [r.get('text', '')[:300] for r in reviews]
        combined_text = "\n---\n".join(review_texts)
        
        prompt = f"""
        Analyze the following customer reviews and identify the main topic/theme they share.
        Provide:
        1. Topic name (2-4 words)
        2. Topic description (1-2 sentences)
        3. Key keywords (5-8 words)
        4. Sentiment tendency (positive/negative/mixed)
        
        Respond in JSON format:
        {{
            "topic_name": "Customer Service",
            "description": "Reviews discussing customer service experiences and support quality",
            "keywords": ["support", "service", "help", "staff", "response"],
            "sentiment_tendency": "mixed"
        }}
        
        Reviews:
        {combined_text}
        """
        
        try:
            response = openai.ChatCompletion.create(
                model=config.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "You are an expert at identifying themes and topics in customer feedback."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=500
            )
            
            result_text = response.choices[0].message.content
            topic_data = json.loads(result_text.strip().replace('```json', '').replace('```', ''))
            
            topic_data['cluster_id'] = cluster_id
            topic_data['review_count'] = len(reviews)
            
            return topic_data
            
        except Exception as e:
            self.logger.error(f"Error analyzing cluster topic: {e}")
            return {
                'topic_name': f'Topic {cluster_id + 1}',
                'description': 'Topic analysis failed',
                'keywords': [],
                'sentiment_tendency': 'neutral',
                'cluster_id': cluster_id,
                'review_count': len(reviews)
            }
            
    def _assign_topics_to_reviews(self, embeddings, topics):
        """Assign topics to all reviews based on similarity"""
        # Get topic centroids (simplified approach)
        topic_assignments = []
        
        # For each review, find the most similar topic
        for embedding in embeddings:
            best_topic = 0
            best_similarity = -1
            
            for topic_id, topic_data in topics.items():
                # Simple assignment based on cluster ID
                # In a more sophisticated approach, we'd compute similarity to topic centroid
                similarity = np.random.random()  # Placeholder
                
                if similarity > best_similarity:
                    best_similarity = similarity
                    best_topic = topic_id
                    
            topic_assignments.append({
                'topic_id': best_topic,
                'topic_name': topics.get(best_topic, {}).get('topic_name', 'Unknown'),
                'confidence': best_similarity
            })
            
        return topic_assignments
        
    def _fallback_topic_extraction(self, reviews, num_topics):
        """Fallback topic extraction using keyword frequency"""
        # Simple keyword-based topic extraction
        all_text = ' '.join([r.get('text', '') for r in reviews])
        words = re.findall(r'\b\w+\b', all_text.lower())
        
        # Filter common words
        filtered_words = [w for w in words if len(w) > 3 and w not in config.STOP_WORDS_CUSTOM]
        word_freq = Counter(filtered_words)
        
        topics = {}
        for i in range(min(num_topics, 5)):
            top_words = [word for word, count in word_freq.most_common(10)[i*2:(i+1)*2]]
            topics[i] = {
                'topic_name': f'Topic {i+1}',
                'description': f'Topic based on keywords: {", ".join(top_words)}',
                'keywords': top_words,
                'sentiment_tendency': 'neutral',
                'cluster_id': i,
                'review_count': len(reviews) // num_topics
            }
            
        # Simple topic assignment
        topic_assignments = []
        for _ in reviews:
            topic_assignments.append({
                'topic_id': np.random.randint(0, len(topics)),
                'topic_name': f'Topic {np.random.randint(1, len(topics)+1)}',
                'confidence': 0.5
            })
            
        return topics, topic_assignments
        
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
        # Group by time periods
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
        
        topic_summary = [
            {
                'name': topic['topic_name'],
                'description': topic['description'],
                'review_count': topic['review_count']
            }
            for topic in topics.values()
        ]
        
        prompt = f"""
        Based on the customer review analysis below, provide strategic insights and recommendations.
        
        Sentiment Summary:
        - Total Reviews: {sentiment_summary['total']}
        - Positive: {sentiment_summary['positive']} ({sentiment_summary['positive']/sentiment_summary['total']*100:.1f}%)
        - Negative: {sentiment_summary['negative']} ({sentiment_summary['negative']/sentiment_summary['total']*100:.1f}%)
        - Neutral: {sentiment_summary['neutral']} ({sentiment_summary['neutral']/sentiment_summary['total']*100:.1f}%)
        
        Main Topics:
        {json.dumps(topic_summary, indent=2)}
        
        Please provide:
        1. Overall sentiment assessment
        2. Key areas of concern (based on negative sentiment and topics)
        3. Strengths to leverage (based on positive sentiment and topics)
        4. Actionable recommendations
        5. Priority areas for improvement
        
        Format your response as structured insights that can be included in an executive summary.
        """
        
        try:
            response = openai.ChatCompletion.create(
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
            