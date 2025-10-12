"""
Excel output generator - UPDATED for hierarchical Level 1 → Level 2 topics
"""

import pandas as pd
import numpy as np
import logging
from datetime import datetime
import xlsxwriter
from collections import Counter
import config

class ExcelGenerator:
    def __init__(self):
        self.setup_logging()
        
    def setup_logging(self):
        """Setup logging configuration"""
        self.logger = logging.getLogger(__name__)
        
    def generate_report(self, reviews, sentiment_results, topics, topic_assignments, 
                       trends, insights, taxonomy_matches=None):
        """Generate comprehensive Excel report with hierarchical topics"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = config.EXCEL_FILENAME_TEMPLATE.format(timestamp=timestamp)
        
        self.logger.info(f"Generating Excel report: {filename}")
        
        try:
            with pd.ExcelWriter(filename, engine='xlsxwriter') as writer:
                workbook = writer.book
                formats = self._create_formats(workbook)
                
                # Generate sheets
                self._create_raw_data_sheet(reviews, sentiment_results, topic_assignments, 
                                          taxonomy_matches, writer, formats)
                self._create_sentiment_analysis_sheet(sentiment_results, writer, formats)
                self._create_topic_analysis_sheet(topics, topic_assignments, writer, formats)
                
                # Add taxonomy sheet if data available
                if taxonomy_matches:
                    self._create_taxonomy_analysis_sheet(taxonomy_matches, writer, formats)
                
                self._create_trend_analysis_sheet(trends, writer, formats)
                self._create_executive_summary_sheet(reviews, sentiment_results, topics, 
                                                    trends, insights, taxonomy_matches, writer, formats)
                
                self.logger.info(f"Excel report generated successfully: {filename}")
                return filename
                
        except Exception as e:
            self.logger.error(f"Error generating Excel report: {e}")
            raise
    
    def _create_formats(self, workbook):
        """Create Excel formatting styles"""
        formats = {}
        
        formats['header'] = workbook.add_format({
            'bold': True,
            'font_color': 'white',
            'bg_color': '#4472C4',
            'border': 1,
            'align': 'center',
            'valign': 'vcenter'
        })
        
        formats['data'] = workbook.add_format({
            'border': 1,
            'align': 'left',
            'valign': 'top',
            'text_wrap': True
        })
        
        formats['number'] = workbook.add_format({
            'border': 1,
            'align': 'center',
            'num_format': '0.00'
        })
        
        formats['percentage'] = workbook.add_format({
            'border': 1,
            'align': 'center',
            'num_format': '0.0%'
        })
        
        formats['title'] = workbook.add_format({
            'bold': True,
            'font_size': 16,
            'font_color': '#4472C4'
        })
        
        formats['positive'] = workbook.add_format({
            'border': 1,
            'bg_color': '#C6EFCE',
            'font_color': '#006100'
        })
        
        formats['negative'] = workbook.add_format({
            'border': 1,
            'bg_color': '#FFC7CE',
            'font_color': '#9C0006'
        })
        
        formats['neutral'] = workbook.add_format({
            'border': 1,
            'bg_color': '#FFEB9C',
            'font_color': '#9C6500'
        })
        
        return formats
    
    def _create_raw_data_sheet(self, reviews, sentiment_results, topic_assignments, 
                              taxonomy_matches, writer, formats):
        """Create raw data sheet with all review information including taxonomy"""
        self.logger.info("Creating raw data sheet")
        
        data = []
        for i, review in enumerate(reviews):
            sentiment = sentiment_results[i] if i < len(sentiment_results) else {}
            topic = topic_assignments[i] if i < len(topic_assignments) else {}
            
            row = {
                'Review_ID': i + 1,
                'Source_URL': review.get('source_url', ''),
                'Source_Domain': review.get('source_domain', ''),
                'Review_Text': review.get('text', ''),
                'Rating': review.get('rating', ''),
                'Reviewer': review.get('reviewer', ''),
                'Date': review.get('date', ''),
                'Scraped_At': review.get('scraped_at', ''),
                'Sentiment': sentiment.get('sentiment', ''),
                'Sentiment_Confidence': sentiment.get('confidence', ''),
                'Emotions': ', '.join(sentiment.get('emotions', [])),
                'Themes': ', '.join(sentiment.get('themes', [])),
                'Level1_Topic': topic.get('level1_name', ''),
                'Level2_Topic': topic.get('level2_name', ''),
                'Topic_Confidence': topic.get('confidence', ''),
                'Analysis_Method': sentiment.get('analysis_method', '')
            }
            
            # Add taxonomy matches if available
            if taxonomy_matches and i < len(taxonomy_matches):
                matches = taxonomy_matches[i]
                if matches:
                    row['Taxonomy_Category_1'] = matches[0].get('category', '')
                    row['Taxonomy_Score_1'] = matches[0].get('score', '')
                    row['Taxonomy_Domain_1'] = matches[0].get('domain', '')
                    
                    if len(matches) > 1:
                        row['Taxonomy_Category_2'] = matches[1].get('category', '')
                        row['Taxonomy_Score_2'] = matches[1].get('score', '')
                    
                    if len(matches) > 2:
                        row['Taxonomy_Category_3'] = matches[2].get('category', '')
                        row['Taxonomy_Score_3'] = matches[2].get('score', '')
            
            data.append(row)
        
        df = pd.DataFrame(data)
        
        sheet_name = config.EXCEL_SHEETS['raw_data']
        df.to_excel(writer, sheet_name=sheet_name, index=False)
        
        worksheet = writer.sheets[sheet_name]
        
        # Apply header formatting
        for col_num, value in enumerate(df.columns):
            worksheet.write(0, col_num, value, formats['header'])
        
        # Set column widths
        column_widths = {
            'Review_Text': 50,
            'Source_URL': 30,
            'Reviewer': 20,
            'Emotions': 25,
            'Themes': 25,
            'Level1_Topic': 20,
            'Level2_Topic': 20,
            'Taxonomy_Category_1': 25,
            'Taxonomy_Category_2': 25,
            'Taxonomy_Category_3': 25
        }
        
        for col_name, width in column_widths.items():
            if col_name in df.columns:
                col_idx = df.columns.get_loc(col_name)
                worksheet.set_column(col_idx, col_idx, width)
        
        # Apply conditional formatting for sentiment
        if 'Sentiment' in df.columns:
            sentiment_col = df.columns.get_loc('Sentiment')
            last_row = len(df)
            
            worksheet.conditional_format(1, sentiment_col, last_row, sentiment_col, {
                'type': 'text',
                'criteria': 'containing',
                'value': 'positive',
                'format': formats['positive']
            })
            
            worksheet.conditional_format(1, sentiment_col, last_row, sentiment_col, {
                'type': 'text',
                'criteria': 'containing',
                'value': 'negative',
                'format': formats['negative']
            })
            
            worksheet.conditional_format(1, sentiment_col, last_row, sentiment_col, {
                'type': 'text',
                'criteria': 'containing',
                'value': 'neutral',
                'format': formats['neutral']
            })
    
    def _create_sentiment_analysis_sheet(self, sentiment_results, writer, formats):
        """Create sentiment analysis summary sheet"""
        self.logger.info("Creating sentiment analysis sheet")
        
        sheet_name = config.EXCEL_SHEETS['sentiment_analysis']
        workbook = writer.book
        worksheet = workbook.add_worksheet(sheet_name)
        
        # Title
        worksheet.write(0, 0, "Sentiment Analysis Summary", formats['title'])
        
        # Overall sentiment distribution
        sentiment_counts = Counter([r.get('sentiment', 'unknown') for r in sentiment_results])
        total_reviews = len(sentiment_results)
        
        # Sentiment summary table
        row = 3
        worksheet.write(row, 0, "Sentiment Distribution", formats['header'])
        worksheet.write(row, 1, "Count", formats['header'])
        worksheet.write(row, 2, "Percentage", formats['header'])
        
        row += 1
        for sentiment, count in sentiment_counts.items():
            percentage = count / total_reviews if total_reviews > 0 else 0
            worksheet.write(row, 0, sentiment.title(), formats['data'])
            worksheet.write(row, 1, count, formats['number'])
            worksheet.write(row, 2, percentage, formats['percentage'])
            row += 1
        
        # Confidence analysis
        row += 2
        worksheet.write(row, 0, "Confidence Analysis", formats['header'])
        row += 1
        
        confidences = [r.get('confidence', 0) for r in sentiment_results if r.get('confidence')]
        if confidences:
            avg_confidence = np.mean(confidences)
            median_confidence = np.median(confidences)
            
            worksheet.write(row, 0, "Average Confidence", formats['data'])
            worksheet.write(row, 1, avg_confidence, formats['percentage'])
            row += 1
            
            worksheet.write(row, 0, "Median Confidence", formats['data'])
            worksheet.write(row, 1, median_confidence, formats['percentage'])
            row += 1
        
        # Emotion analysis
        all_emotions = []
        for result in sentiment_results:
            all_emotions.extend(result.get('emotions', []))
        
        if all_emotions:
            emotion_counts = Counter(all_emotions)
            
            row += 2
            worksheet.write(row, 0, "Top Emotions Detected", formats['header'])
            worksheet.write(row, 1, "Frequency", formats['header'])
            row += 1
            
            for emotion, count in emotion_counts.most_common(10):
                worksheet.write(row, 0, emotion.title(), formats['data'])
                worksheet.write(row, 1, count, formats['number'])
                row += 1
    
    def _create_topic_analysis_sheet(self, topics, topic_assignments, writer, formats):
        """Create hierarchical topic analysis sheet (Level 1 → Level 2)"""
        self.logger.info("Creating hierarchical topic analysis sheet")
        
        sheet_name = config.EXCEL_SHEETS['topic_modeling']
        workbook = writer.book
        worksheet = workbook.add_worksheet(sheet_name)
        
        # Title
        worksheet.write(0, 0, "Hierarchical Topic Analysis (Level 1 → Level 2)", formats['title'])
        
        # FIXED: Iterate over list of topics, not .items()
        row = 3
        worksheet.write(row, 0, "Level 1 Topic", formats['header'])
        worksheet.write(row, 1, "Description", formats['header'])
        worksheet.write(row, 2, "Level 2 Topics", formats['header'])
        
        row += 1
        
        # Display hierarchical structure
        for level1_topic in topics:
            worksheet.write(row, 0, level1_topic.get('name', ''), formats['data'])
            worksheet.write(row, 1, level1_topic.get('description', ''), formats['data'])
            
            # Get Level 2 topics
            level2_topics = level1_topic.get('level2_topics', [])
            level2_names = [l2.get('name', '') for l2 in level2_topics]
            worksheet.write(row, 2, ', '.join(level2_names), formats['data'])
            row += 1
        
        # Topic assignment distribution
        row += 2
        worksheet.write(row, 0, "Level 1 Topic Distribution", formats['header'])
        worksheet.write(row, 1, "Review Count", formats['header'])
        worksheet.write(row, 2, "Percentage", formats['header'])
        
        row += 1
        
        # Count Level 1 topics
        level1_counts = Counter([ta.get('level1_name', 'Unknown') for ta in topic_assignments])
        total_assignments = len(topic_assignments)
        
        for topic_name, count in level1_counts.most_common():
            percentage = count / total_assignments if total_assignments > 0 else 0
            worksheet.write(row, 0, topic_name, formats['data'])
            worksheet.write(row, 1, count, formats['number'])
            worksheet.write(row, 2, percentage, formats['percentage'])
            row += 1
        
        # Level 2 distribution
        row += 2
        worksheet.write(row, 0, "Level 2 Topic Distribution", formats['header'])
        worksheet.write(row, 1, "Review Count", formats['header'])
        worksheet.write(row, 2, "Percentage", formats['header'])
        
        row += 1
        
        # Count Level 2 topics
        level2_counts = Counter([ta.get('level2_name', 'Unknown') for ta in topic_assignments])
        
        for topic_name, count in level2_counts.most_common(20):  # Top 20
            percentage = count / total_assignments if total_assignments > 0 else 0
            worksheet.write(row, 0, topic_name, formats['data'])
            worksheet.write(row, 1, count, formats['number'])
            worksheet.write(row, 2, percentage, formats['percentage'])
            row += 1
        
        # Set column widths
        worksheet.set_column(0, 0, 30)
        worksheet.set_column(1, 1, 50)
        worksheet.set_column(2, 2, 40)
    
    def _create_taxonomy_analysis_sheet(self, taxonomy_matches, writer, formats):
        """Create dedicated sheet for taxonomy analysis"""
        self.logger.info("Creating taxonomy analysis sheet")
        
        sheet_name = 'Taxonomy Analysis'
        workbook = writer.book
        worksheet = workbook.add_worksheet(sheet_name)
        
        # Title
        worksheet.write(0, 0, "Taxonomy Category Analysis", formats['title'])
        
        # Calculate statistics
        category_counts = Counter()
        domain_counts = Counter()
        total_matches = 0
        reviews_with_matches = 0
        
        for matches in taxonomy_matches:
            if matches:
                reviews_with_matches += 1
                total_matches += len(matches)
                for match in matches:
                    category_counts[match['category']] += 1
                    domain_counts[match['domain']] += 1
        
        # Summary statistics
        row = 3
        worksheet.write(row, 0, "Summary Statistics", formats['header'])
        worksheet.write(row, 1, "Value", formats['header'])
        row += 1
        
        worksheet.write(row, 0, "Total Reviews", formats['data'])
        worksheet.write(row, 1, len(taxonomy_matches), formats['number'])
        row += 1
        
        worksheet.write(row, 0, "Reviews with Matches", formats['data'])
        worksheet.write(row, 1, reviews_with_matches, formats['number'])
        row += 1
        
        worksheet.write(row, 0, "Match Rate", formats['data'])
        match_rate = reviews_with_matches / len(taxonomy_matches) if len(taxonomy_matches) > 0 else 0
        worksheet.write(row, 1, match_rate, formats['percentage'])
        row += 1
        
        worksheet.write(row, 0, "Total Matches", formats['data'])
        worksheet.write(row, 1, total_matches, formats['number'])
        row += 1
        
        worksheet.write(row, 0, "Avg Matches per Review", formats['data'])
        avg_matches = total_matches / reviews_with_matches if reviews_with_matches > 0 else 0
        worksheet.write(row, 1, avg_matches, formats['number'])
        row += 1
        
        # Category distribution
        row += 2
        worksheet.write(row, 0, "Category Distribution", formats['header'])
        worksheet.write(row, 1, "Count", formats['header'])
        worksheet.write(row, 2, "Percentage", formats['header'])
        row += 1
        
        for category, count in category_counts.most_common():
            percentage = count / len(taxonomy_matches) if len(taxonomy_matches) > 0 else 0
            worksheet.write(row, 0, category, formats['data'])
            worksheet.write(row, 1, count, formats['number'])
            worksheet.write(row, 2, percentage, formats['percentage'])
            row += 1
        
        # Domain distribution
        row += 2
        worksheet.write(row, 0, "Domain Distribution", formats['header'])
        worksheet.write(row, 1, "Count", formats['header'])
        worksheet.write(row, 2, "Percentage", formats['header'])
        row += 1
        
        for domain, count in domain_counts.most_common():
            percentage = count / len(taxonomy_matches) if len(taxonomy_matches) > 0 else 0
            worksheet.write(row, 0, domain, formats['data'])
            worksheet.write(row, 1, count, formats['number'])
            worksheet.write(row, 2, percentage, formats['percentage'])
            row += 1
        
        # Set column widths
        worksheet.set_column(0, 0, 30)
        worksheet.set_column(1, 1, 15)
        worksheet.set_column(2, 2, 15)
    
    def _create_trend_analysis_sheet(self, trends, writer, formats):
        """Create trend analysis sheet"""
        self.logger.info("Creating trend analysis sheet")
        
        sheet_name = config.EXCEL_SHEETS['trend_analysis']
        
        if not trends:
            workbook = writer.book
            worksheet = workbook.add_worksheet(sheet_name)
            worksheet.write(0, 0, "Trend Analysis", formats['title'])
            worksheet.write(2, 0, "No trend data available - insufficient date information", formats['data'])
            return
        
        # Create DataFrames for different trend types
        trend_data = {}
        
        if 'sentiment_trends' in trends:
            for period, data in trends['sentiment_trends'].items():
                if data:
                    df = pd.DataFrame(data)
                    trend_data[f'sentiment_{period}'] = df
        
        if 'volume_trends' in trends:
            for period, data in trends['volume_trends'].items():
                if data:
                    df = pd.DataFrame(data)
                    trend_data[f'volume_{period}'] = df
        
        if 'rating_trends' in trends:
            for period, data in trends['rating_trends'].items():
                if data:
                    df = pd.DataFrame(data)
                    trend_data[f'rating_{period}'] = df
        
        # Write trend data to sheet
        workbook = writer.book
        worksheet = workbook.add_worksheet(sheet_name)
        
        worksheet.write(0, 0, "Trend Analysis", formats['title'])
        
        row = 3
        for trend_name, df in trend_data.items():
            # Write trend name
            worksheet.write(row, 0, trend_name.replace('_', ' ').title(), formats['header'])
            row += 2
            
            # Write headers
            for col_idx, col_name in enumerate(df.columns):
                worksheet.write(row, col_idx, col_name, formats['header'])
            row += 1
            
            # Write data
            for _, data_row in df.iterrows():
                for col_idx, value in enumerate(data_row):
                    worksheet.write(row, col_idx, value, formats['data'])
                row += 1
            
            row += 2
    
    def _create_executive_summary_sheet(self, reviews, sentiment_results, topics, 
                                       trends, insights, taxonomy_matches, writer, formats):
        """Create executive summary sheet with hierarchical topics"""
        self.logger.info("Creating executive summary sheet")
        
        sheet_name = config.EXCEL_SHEETS['summary']
        workbook = writer.book
        worksheet = workbook.add_worksheet(sheet_name)
        
        # Title
        worksheet.write(0, 0, "Executive Summary", formats['title'])
        worksheet.write(1, 0, f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}", formats['data'])
        
        row = 3
        
        # Key metrics
        worksheet.write(row, 0, "Key Metrics", formats['header'])
        row += 1
        
        total_reviews = len(reviews)
        sentiment_counts = Counter([r.get('sentiment', 'unknown') for r in sentiment_results])
        
        metrics = [
            ("Total Reviews Analyzed", total_reviews),
            ("Positive Reviews", sentiment_counts.get('positive', 0)),
            ("Negative Reviews", sentiment_counts.get('negative', 0)),
            ("Neutral Reviews", sentiment_counts.get('neutral', 0)),
            ("Positive Percentage", f"{sentiment_counts.get('positive', 0)/total_reviews*100:.1f}%" if total_reviews > 0 else "0%"),
            ("Negative Percentage", f"{sentiment_counts.get('negative', 0)/total_reviews*100:.1f}%" if total_reviews > 0 else "0%"),
            ("Number of Level 1 Topics", len(topics))
        ]
        
        # Add taxonomy metrics if available
        if taxonomy_matches:
            reviews_with_taxonomy = sum(1 for matches in taxonomy_matches if matches)
            metrics.append(("Reviews with Taxonomy Matches", reviews_with_taxonomy))
            metrics.append(("Taxonomy Match Rate", f"{reviews_with_taxonomy/total_reviews*100:.1f}%" if total_reviews > 0 else "0%"))
        
        for metric, value in metrics:
            worksheet.write(row, 0, metric, formats['data'])
            worksheet.write(row, 1, value, formats['data'])
            row += 1
        
        # Source breakdown
        row += 1
        worksheet.write(row, 0, "Source Breakdown", formats['header'])
        row += 1
        
        source_counts = Counter([r.get('source_domain', 'unknown') for r in reviews])
        for source, count in source_counts.most_common():
            worksheet.write(row, 0, source, formats['data'])
            worksheet.write(row, 1, count, formats['data'])
            row += 1
        
        # FIXED: Main Level 1 topics - iterate over list
        row += 1
        worksheet.write(row, 0, "Main Level 1 Topics", formats['header'])
        row += 1
        
        for level1_topic in topics[:5]:  # Top 5 Level 1 topics
            worksheet.write(row, 0, level1_topic.get('name', ''), formats['data'])
            worksheet.write(row, 1, level1_topic.get('description', ''), formats['data'])
            row += 1
        
        # Top taxonomy categories (if available)
        if taxonomy_matches:
            row += 1
            worksheet.write(row, 0, "Top Taxonomy Categories", formats['header'])
            row += 1
            
            category_counts = Counter()
            for matches in taxonomy_matches:
                for match in matches:
                    category_counts[match['category']] += 1
            
            for category, count in category_counts.most_common(5):
                worksheet.write(row, 0, category, formats['data'])
                worksheet.write(row, 1, count, formats['data'])
                row += 1
        
        # AI Insights
        if insights:
            row += 2
            worksheet.write(row, 0, "AI-Generated Insights", formats['header'])
            row += 1
            
            # Split insights into lines
            insight_lines = insights.split('\n')
            for line in insight_lines:
                if line.strip():
                    worksheet.write(row, 0, line.strip(), formats['data'])
                    row += 1
        
        # Set column widths
        worksheet.set_column(0, 0, 35)
        worksheet.set_column(1, 1, 60)