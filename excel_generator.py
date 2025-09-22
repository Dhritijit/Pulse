"""
Excel output generator for social media review analysis
Creates structured Excel reports with multiple sheets and visualizations
"""

import pandas as pd
import numpy as np
import logging
from datetime import datetime
import xlsxwriter
from collections import Counter
import matplotlib.pyplot as plt
import seaborn as sns
import io
import base64
import config

class ExcelGenerator:
    def __init__(self):
        self.setup_logging()
        
    def setup_logging(self):
        """Setup logging configuration"""
        self.logger = logging.getLogger(__name__)
        
    def generate_report(self, reviews, sentiment_results, topics, topic_assignments, trends, insights):
        """Generate comprehensive Excel report"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = config.EXCEL_FILENAME_TEMPLATE.format(timestamp=timestamp)
        
        self.logger.info(f"Generating Excel report: {filename}")
        
        try:
            # Create Excel writer with xlsxwriter engine for advanced formatting
            with pd.ExcelWriter(filename, engine='xlsxwriter') as writer:
                workbook = writer.book
                
                # Define formats
                formats = self._create_formats(workbook)
                
                # Generate each sheet
                self._create_raw_data_sheet(reviews, sentiment_results, topic_assignments, writer, formats)
                self._create_sentiment_analysis_sheet(sentiment_results, writer, formats)
                self._create_topic_analysis_sheet(topics, topic_assignments, writer, formats)
                self._create_trend_analysis_sheet(trends, writer, formats)
                self._create_executive_summary_sheet(reviews, sentiment_results, topics, trends, insights, writer, formats)
                
                self.logger.info(f"Excel report generated successfully: {filename}")
                return filename
                
        except Exception as e:
            self.logger.error(f"Error generating Excel report: {e}")
            raise
            
    def _create_formats(self, workbook):
        """Create Excel formatting styles"""
        formats = {}
        
        # Header format
        formats['header'] = workbook.add_format({
            'bold': True,
            'font_color': 'white',
            'bg_color': '#4472C4',
            'border': 1,
            'align': 'center',
            'valign': 'vcenter'
        })
        
        # Data format
        formats['data'] = workbook.add_format({
            'border': 1,
            'align': 'left',
            'valign': 'top',
            'text_wrap': True
        })
        
        # Number format
        formats['number'] = workbook.add_format({
            'border': 1,
            'align': 'center',
            'num_format': '0.00'
        })
        
        # Percentage format
        formats['percentage'] = workbook.add_format({
            'border': 1,
            'align': 'center',
            'num_format': '0.0%'
        })
        
        # Title format
        formats['title'] = workbook.add_format({
            'bold': True,
            'font_size': 16,
            'font_color': '#4472C4'
        })
        
        # Positive sentiment
        formats['positive'] = workbook.add_format({
            'border': 1,
            'bg_color': '#C6EFCE',
            'font_color': '#006100'
        })
        
        # Negative sentiment
        formats['negative'] = workbook.add_format({
            'border': 1,
            'bg_color': '#FFC7CE',
            'font_color': '#9C0006'
        })
        
        # Neutral sentiment
        formats['neutral'] = workbook.add_format({
            'border': 1,
            'bg_color': '#FFEB9C',
            'font_color': '#9C6500'
        })
        
        return formats
        
    def _create_raw_data_sheet(self, reviews, sentiment_results, topic_assignments, writer, formats):
        """Create raw data sheet with all review information"""
        self.logger.info("Creating raw data sheet")
        
        # Combine all data
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
                'Topic_ID': topic.get('topic_id', ''),
                'Topic_Name': topic.get('topic_name', ''),
                'Topic_Confidence': topic.get('confidence', ''),
                'Analysis_Method': sentiment.get('analysis_method', '')
            }
            data.append(row)
            
        df = pd.DataFrame(data)
        
        # Write to Excel
        sheet_name = config.EXCEL_SHEETS['raw_data']
        df.to_excel(writer, sheet_name=sheet_name, index=False)
        
        # Format the sheet
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
            'Topic_Name': 20
        }
        
        for col_name, width in column_widths.items():
            if col_name in df.columns:
                col_idx = df.columns.get_loc(col_name)
                worksheet.set_column(col_idx, col_idx, width)
                
        # Apply conditional formatting for sentiment
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
                
        # Create pie chart for sentiment distribution
        self._create_sentiment_chart(worksheet, sentiment_counts, total_reviews)
        
    def _create_sentiment_chart(self, worksheet, sentiment_counts, total_reviews):
        """Create pie chart for sentiment distribution"""
        try:
            chart = worksheet._workbook.add_chart({'type': 'pie'})
            
            # Prepare data for chart
            categories = list(sentiment_counts.keys())
            values = list(sentiment_counts.values())
            
            # Add data to chart
            chart.add_series({
                'categories': categories,
                'values': values,
                'name': 'Sentiment Distribution',
                'data_labels': {'percentage': True}
            })
            
            chart.set_title({'name': 'Sentiment Distribution'})
            chart.set_style(10)
            
            # Insert chart
            worksheet.insert_chart('E3', chart, {'x_scale': 1.5, 'y_scale': 1.5})
            
        except Exception as e:
            self.logger.error(f"Error creating sentiment chart: {e}")
            
    def _create_topic_analysis_sheet(self, topics, topic_assignments, writer, formats):
        """Create topic analysis sheet"""
        self.logger.info("Creating topic analysis sheet")
        
        sheet_name = config.EXCEL_SHEETS['topic_modeling']
        workbook = writer.book
        worksheet = workbook.add_worksheet(sheet_name)
        
        # Title
        worksheet.write(0, 0, "Topic Analysis", formats['title'])
        
        # Topic summary table
        row = 3
        worksheet.write(row, 0, "Topic Name", formats['header'])
        worksheet.write(row, 1, "Description", formats['header'])
        worksheet.write(row, 2, "Keywords", formats['header'])
        worksheet.write(row, 3, "Review Count", formats['header'])
        worksheet.write(row, 4, "Sentiment Tendency", formats['header'])
        
        row += 1
        for topic_id, topic in topics.items():
            worksheet.write(row, 0, topic.get('topic_name', ''), formats['data'])
            worksheet.write(row, 1, topic.get('description', ''), formats['data'])
            worksheet.write(row, 2, ', '.join(topic.get('keywords', [])), formats['data'])
            worksheet.write(row, 3, topic.get('review_count', 0), formats['number'])
            worksheet.write(row, 4, topic.get('sentiment_tendency', ''), formats['data'])
            row += 1
            
        # Topic distribution
        topic_counts = Counter([ta.get('topic_name', 'Unknown') for ta in topic_assignments])
        
        row += 2
        worksheet.write(row, 0, "Topic Distribution", formats['header'])
        worksheet.write(row, 1, "Review Count", formats['header'])
        worksheet.write(row, 2, "Percentage", formats['header'])
        
        row += 1
        total_assignments = len(topic_assignments)
        for topic_name, count in topic_counts.most_common():
            percentage = count / total_assignments if total_assignments > 0 else 0
            worksheet.write(row, 0, topic_name, formats['data'])
            worksheet.write(row, 1, count, formats['number'])
            worksheet.write(row, 2, percentage, formats['percentage'])
            row += 1
            
        # Set column widths
        worksheet.set_column(0, 0, 25)  # Topic Name
        worksheet.set_column(1, 1, 50)  # Description
        worksheet.set_column(2, 2, 30)  # Keywords
        
    def _create_trend_analysis_sheet(self, trends, writer, formats):
        """Create trend analysis sheet"""
        self.logger.info("Creating trend analysis sheet")
        
        sheet_name = config.EXCEL_SHEETS['trend_analysis']
        
        if not trends:
            # Create empty sheet with message
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
        with pd.ExcelWriter(writer.path, engine='openpyxl', mode='a') as trend_writer:
            row_offset = 0
            
            for trend_name, df in trend_data.items():
                df.to_excel(trend_writer, sheet_name=sheet_name, 
                           startrow=row_offset, index=False)
                row_offset += len(df) + 3
                
    def _create_executive_summary_sheet(self, reviews, sentiment_results, topics, trends, insights, writer, formats):
        """Create executive summary sheet"""
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
            ("Number of Topics Identified", len(topics))
        ]
        
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
            
        # Top topics
        row += 1
        worksheet.write(row, 0, "Main Topics", formats['header'])
        row += 1
        
        for topic_id, topic in list(topics.items())[:5]:  # Top 5 topics
            worksheet.write(row, 0, topic.get('topic_name', ''), formats['data'])
            worksheet.write(row, 1, topic.get('description', ''), formats['data'])
            row += 1
            
        # AI Insights
        if insights:
            row += 2
            worksheet.write(row, 0, "AI-Generated Insights", formats['header'])
            row += 1
            
            # Split insights into lines and write each line
            insight_lines = insights.split('\n')
            for line in insight_lines:
                if line.strip():
                    worksheet.write(row, 0, line.strip(), formats['data'])
                    row += 1
                    
        # Set column widths
        worksheet.set_column(0, 0, 30)
        worksheet.set_column(1, 1, 60)
        
        # Merge cells for insights section if needed
        if insights:
            insight_start_row = row - len([l for l in insight_lines if l.strip()])
            worksheet.merge_range(f'A{insight_start_row}:B{row-1}', insights, formats['data'])
            
    def create_summary_statistics(self, reviews, sentiment_results, topics, topic_assignments):
        """Create summary statistics for the analysis"""
        stats = {
            'total_reviews': len(reviews),
            'sentiment_distribution': {},
            'topic_distribution': {},
            'source_distribution': {},
            'date_range': {},
            'confidence_stats': {}
        }
        
        # Sentiment distribution
        sentiment_counts = Counter([r.get('sentiment', 'unknown') for r in sentiment_results])
        total = len(sentiment_results)
        for sentiment, count in sentiment_counts.items():
            stats['sentiment_distribution'][sentiment] = {
                'count': count,
                'percentage': count / total * 100 if total > 0 else 0
            }
            
        # Topic distribution
        topic_counts = Counter([ta.get('topic_name', 'Unknown') for ta in topic_assignments])
        total_topics = len(topic_assignments)
        for topic, count in topic_counts.items():
            stats['topic_distribution'][topic] = {
                'count': count,
                'percentage': count / total_topics * 100 if total_topics > 0 else 0
            }
            
        # Source distribution
        source_counts = Counter([r.get('source_domain', 'unknown') for r in reviews])
        for source, count in source_counts.items():
            stats['source_distribution'][source] = count
            
        # Date range
        dates = [r.get('date') for r in reviews if r.get('date')]
        if dates:
            try:
                parsed_dates = pd.to_datetime(dates, errors='coerce').dropna()
                if len(parsed_dates) > 0:
                    stats['date_range'] = {
                        'earliest': parsed_dates.min().strftime('%Y-%m-%d'),
                        'latest': parsed_dates.max().strftime('%Y-%m-%d'),
                        'span_days': (parsed_dates.max() - parsed_dates.min()).days
                    }
            except Exception as e:
                self.logger.error(f"Error processing dates: {e}")
                
        # Confidence statistics
        confidences = [r.get('confidence', 0) for r in sentiment_results if r.get('confidence')]
        if confidences:
            stats['confidence_stats'] = {
                'mean': np.mean(confidences),
                'median': np.median(confidences),
                'std': np.std(confidences),
                'min': np.min(confidences),
                'max': np.max(confidences)
            }
            
        return stats