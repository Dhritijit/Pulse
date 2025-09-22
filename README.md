# 🌊 Pulse - AI-Powered Social Media Review Analyzer

> Transform customer feedback into actionable insights with AI-powered analysis

[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/streamlit-1.28.1-FF4B4B.svg)](https://streamlit.io)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4-412991.svg)](https://openai.com)

## 🚀 What is Pulse?

Pulse is an **AI-powered review analysis tool** that helps businesses understand their customers better by:

- 🌐 **Scraping reviews** from multiple platforms (Trustpilot, Glassdoor, Google Reviews, etc.)
- 🤖 **AI analysis** using GPT-4 for sentiment and topic modeling
- 📊 **Beautiful reports** with insights and recommendations
- 🎨 **Easy-to-use** web interface and command-line tools

## ✨ Key Features

### 📱 **Two Ways to Use Pulse**
1. **Web Interface** - Beautiful, user-friendly dashboard
2. **Command Line** - For advanced users and automation

### 🎯 **What Pulse Analyzes**
- ✅ **Sentiment**: Positive, negative, neutral classification
- ✅ **Topics**: What customers talk about most
- ✅ **Trends**: Changes over time
- ✅ **Insights**: AI-generated recommendations

### 🌐 **Supported Review Sites**
- Trustpilot
- Glassdoor  
- Google Reviews
- Yelp
- Indeed
- Ambitionbox
- And many more...

## 🛠️ Installation & Setup

### **Prerequisites**
- Python 3.7 or higher
- OpenAI API key ([Get one here](https://platform.openai.com/api-keys))
- Internet connection

### **Quick Setup**

1. **Download or clone this project**
2. **Open command prompt** in the project folder
3. **Create virtual environment**:
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```
4. **Install requirements**:
   ```bash
   pip install -r requirements.txt
   ```
5. **Setup your API key**:
   - Copy `.env.template` to `.env`
   - Edit `.env` and add your OpenAI API key
6. **Run Pulse**:
   ```bash
   python run.py
   ```

## 🎮 How to Use

### **Easy Way - Web Interface**
1. Run: `python run.py`
2. Choose option 1
3. Open browser to `http://localhost:8501`
4. Enter review URLs and click "Start Analysis"
5. View results and download reports!

### **Advanced Way - Command Line**
1. Run: `python run.py`
2. Choose option 2
3. Follow prompts to enter URLs
4. Wait for analysis to complete
5. Get Excel report with insights!

## 📊 What You Get

### **Excel Reports Include**:
- 📋 Raw review data
- 😊 Sentiment analysis breakdown
- 🏷️ Topic modeling results
- 📈 Trend analysis over time
- 💡 AI-generated insights and recommendations

### **Web Dashboard Shows**:
- Real-time progress tracking
- Interactive charts and graphs
- Key metrics and statistics
- Downloadable reports

## ⚙️ Configuration

### **Environment Variables (.env)**
```env
# Required: Your OpenAI API key
OPENAI_API_KEY=your_api_key_here

# Optional: Customize these settings
MAX_REVIEWS_PER_SITE=1000
DEFAULT_DELAY=2
```

### **Advanced Settings**
Edit `config.py` to customize:
- Scraping delays and timeouts
- AI analysis parameters
- Output formats

## 🆘 Troubleshooting

### **Common Issues**

**❌ "No reviews found"**
- Check if URLs are correct and accessible
- Make sure URLs point to review pages, not search results

**❌ "OpenAI API error"**
- Verify your API key in `.env` file
- Check if you have OpenAI credits available

**❌ "Module not found"**
- Make sure virtual environment is activated
- Run `pip install -r requirements.txt` again

**❌ "Slow processing"**
- This is normal for large datasets
- Be patient, especially with 500+ reviews

### **Need Help?**
1. Check the logs in the `logs/` folder
2. Run `python run.py` and choose option 3 for help
3. Create an issue on GitHub

## 🔒 Privacy & Ethics

Pulse respects website terms and user privacy:
- ✅ Only scrapes publicly available reviews
- ✅ Implements rate limiting to be respectful
- ✅ No personal data storage beyond public reviews
- ✅ Follows robots.txt guidelines

## 📈 Roadmap

**Coming Soon**:
- 🔄 Real-time monitoring
- 📧 Email reports
- 🌍 Multi-language support
- 📱 Mobile interface
- 🔌 API endpoints

## 🤝 Contributing

We welcome contributions! Feel free to:
- 🐛 Report bugs
- 💡 Suggest features  
- 🔧 Submit improvements
- 📖 Improve documentation

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

## 🙏 Credits

Built with:
- **OpenAI GPT-4** - For intelligent analysis
- **Streamlit** - For beautiful web interface
- **Python** - For everything else
- **Love and Coffee** ☕ - For late night coding

---

**Made with ❤️ for better customer insights**

*Pulse - Understand your customers like never before*