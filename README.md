# 🌐 Pulse - Social Media Review Analyzer

A comprehensive AI-powered solution for scraping and analyzing customer reviews from various review platforms. Features both a beautiful web interface and command-line tools.

## 🆕 New Features (v2.0)

### 📁 File Upload Support
- **Upload Excel/CSV files** directly instead of scraping
- Automatic column detection (Comments, Date, Rating, etc.)
- Support for up to 2,000 reviews per file
- File validation and preview before processing

### 🏷️ Taxonomy-Based Categorization
- **Upload your own taxonomy** with predefined categories
- Keyword-based matching with stemming support
- Hybrid approach: combines AI topics with your taxonomy
- Multi-domain support (Sentiment, Travel, Insurance, Telecom, etc.)

## Features

- **Dual Data Input**: Upload files OR scrape from URLs
- **Dynamic Web Scraping**: Supports Trustpilot, Glassdoor, and other platforms
- **AI-Powered Analysis**: GPT-4 sentiment analysis, topic modeling, and trend detection
- **Taxonomy Matching**: Map reviews to your predefined categories
- **Beautiful Web Interface**: Real-time progress tracking with interactive charts
- **Professional Reports**: Multi-sheet Excel reports with comprehensive insights
- **Data Quality Controls**: Spam filtering, duplicate removal, validation

## Quick Start

### Prerequisites
- Python 3.7+
- OpenAI API key ([Get one here](https://platform.openai.com/api-keys))
- Chrome browser (for URL scraping)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/YOUR_USERNAME/social-media-review-analyzer.git
cd social-media-review-analyzer
```

2. **Create virtual environment**
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Setup environment**
```bash
# Copy template
cp .env.template .env

# Edit .env and add your OpenAI API key
# OPENAI_API_KEY=sk-your-api-key-here
```

5. **Run the application**
```bash
# Web interface (recommended)
streamlit run app.py

# Command line
python main.py

# Or use the launcher
python run.py
```

## 📊 Usage Guide

### Option 1: Upload Review File

1. Launch the web interface: `streamlit run app.py`
2. Choose "Upload File (Excel/CSV)" option
3. Upload your file with review data
4. (Optional) Upload taxonomy file for categorization
5. Click "Start Analysis"
6. Download your comprehensive Excel report

**File Requirements:**
- Formats: `.xlsx`, `.xls`, or `.csv`
- Required column: Review text (auto-detected from columns like "Comments", "Review", "Text", "Feedback")
- Optional columns: Date, Rating, Source
- Maximum: 2,000 reviews per file
- Maximum size: 50 MB

**Example File Structure:**
```csv
Date,Comments,Rating,Source
2024-01-15,"Great service, very helpful",5,Google Reviews
2024-01-16,"Poor experience, long wait times",2,Trustpilot
```

### Option 2: Scrape from URLs

1. Launch the web interface: `streamlit run app.py`
2. Choose "Scrape from URLs" option
3. Paste review site URLs (one per line)
4. Configure settings in sidebar
5. Click "Start Analysis"
6. Download your comprehensive Excel report

**Supported Sites:**
- Trustpilot
- Glassdoor
- Google Reviews
- Yelp
- Most other review sites (automatic detection)

### 🏷️ Using Taxonomy Categorization

1. **Prepare your taxonomy file** (Excel format):
   - Create sheets for different domains (e.g., "Sentiment_Emotions", "Travel", "Insurance")
   - Include columns: `High Level Category`, `Taxonomy Name`, `Taxonomy Intent`, `Phrases`
   - Add comma-separated keywords in the `Phrases` column

**Example Taxonomy Structure:**
```
Sheet: Sentiment_Emotions
┌──────────────────┬───────────────┬─────────────────────────┬──────────────────────────┐
│ High Level Cat.  │ Taxonomy Name │ Taxonomy Intent         │ Phrases                  │
├──────────────────┼───────────────┼─────────────────────────┼──────────────────────────┤
│ High Level       │ Happy         │ Happy customer emotion  │ happy, delighted, love,  │
│                  │               │                         │ excellent, amazing, glad │
├──────────────────┼───────────────┼─────────────────────────┼──────────────────────────┤
│ High Level       │ Angry         │ Angry customer emotion  │ angry, disgusted, hate,  │
│                  │               │                         │ frustrated, appalled     │
└──────────────────┴───────────────┴─────────────────────────┴──────────────────────────┘
```

2. **Upload in the interface**:
   - Go to sidebar → "Taxonomy Configuration"
   - Upload your taxonomy Excel file
   - Check "Use Taxonomy Matching"
   - Run analysis

3. **Results include**:
   - Top 3 matching categories per review
   - Match scores and confidence levels
   - Category distribution charts
   - Taxonomy analysis sheet in Excel report

## 📦 Project Structure

```
social-media-analyzer/
├── app.py                      # Streamlit web interface (UPDATED)
├── scraper.py                  # Web scraping module
├── ai_analyzer.py              # AI analysis module
├── file_processor.py           # File upload handler (NEW)
├── taxonomy_matcher.py         # Taxonomy matching (NEW)
├── excel_generator.py          # Report generation (UPDATED)
├── config.py                   # Configuration
├── main.py                     # CLI interface
├── run.py                      # Easy launcher
├── requirements.txt            # Dependencies (UPDATED)
├── .env.template               # Environment template
└── README.md                   # This file
```

## 🔧 Configuration

Edit `config.py` or `.env` file to customize:

- **OpenAI Settings**: Model, API key, embedding model
- **Scraping Limits**: Max reviews per site, delays, retries
- **Analysis Parameters**: Number of topics, sentiment categories
- **File Limits**: Max file size, max reviews per upload

## 📊 Output Report

The Excel report includes:

1. **Raw Reviews** - All review data with sentiment and taxonomy matches
2. **Sentiment Analysis** - Distribution, confidence, emotions
3. **Topic Analysis** - AI-discovered topics with keywords
4. **Taxonomy Analysis** - Category matches and statistics (if enabled)
5. **Trend Analysis** - Changes over time
6. **Executive Summary** - Key metrics and AI insights

## 🎯 How It Works

### File Upload Flow
```
1. User uploads Excel/CSV file
2. System detects columns automatically
3. Validates and extracts reviews
4. Runs AI sentiment analysis
5. Discovers topics with AI
6. Matches to taxonomy (if enabled)
7. Generates comprehensive report
```

### Taxonomy Matching Process
```
1. Load taxonomy with keywords
2. Stem keywords for better matching
3. For each review:
   - Check exact keyword matches
   - Check stemmed keyword matches
   - Score and rank categories
4. Return top N matches with confidence
5. Combine with AI-discovered topics
```

## 💡 Tips for Best Results

### File Upload
- Use clear column names (e.g., "Comments" not "Col1")
- Include dates for trend analysis
- Clean data beforehand (remove empty rows)
- UTF-8 encoding for special characters

### Taxonomy
- Use comprehensive keyword lists
- Include variations and synonyms
- Organize by domain/category
- Test with small datasets first

### URL Scraping
- Use direct review page URLs
- Start with 100-500 reviews for testing
- Check site's robots.txt
- Respect rate limits

## 🐛 Troubleshooting

### Common Issues

**"No text columns detected"**
- Solution: Rename your column to "Comments", "Review", or "Text"

**"Taxonomy file upload failed"**
- Solution: Ensure Excel file has correct structure (see example above)

**"Analysis failed: OpenAI API error"**
- Solution: Check API key, check credits, check internet connection

**"No reviews found" (URL scraping)**
- Solution: Verify URL is correct, check if site blocks scrapers

**"File too large"**
- Solution: Split into multiple files or filter to top reviews

## 📝 Example Use Cases

1. **Product Reviews Analysis**
   - Upload Amazon/Shopify reviews
   - Identify pain points and strengths
   - Track sentiment over time

2. **Employee Feedback**
   - Upload Glassdoor reviews
   - Categorize by department
   - Identify improvement areas

3. **Customer Support**
   - Upload support tickets/feedback
   - Match to predefined issue categories
   - Prioritize by sentiment

4. **Competitive Analysis**
   - Scrape competitor reviews
   - Compare sentiment trends
   - Identify market gaps

## 🔐 Privacy & Security

- Review data processed locally
- OpenAI API used only for analysis
- No data stored on external servers
- API keys stored in local `.env` file

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create feature branch
3. Commit changes
4. Push to branch
5. Open pull request

## 📄 License

MIT License - see LICENSE file for details

## 🆘 Support

- **Issues**: [GitHub Issues](https://github.com/YOUR_USERNAME/social-media-review-analyzer/issues)
- **Documentation**: See `/docs` folder
- **Email**: your.email@example.com

## 🎉 Acknowledgments

- OpenAI for GPT-4 API
- Streamlit for the web framework
- NLTK for text processing
- All open-source contributors

## 🗺️ Roadmap

- [ ] Real-time monitoring and alerts
- [ ] Multi-language support
- [ ] Custom AI model fine-tuning
- [ ] API for integrations
- [ ] Scheduled automated scraping
- [ ] Advanced visualization dashboard
- [ ] Export to PowerPoint
- [ ] Slack/Teams integrations

---

**Version 2.0** | Made with ❤️ for better customer insights