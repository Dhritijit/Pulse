"""
FastAPI Backend for Pulse.ai - Social Media Review Analyzer
UPDATED: Now supports hierarchical topic classification (Level 1 → Level 2)
"""

from fastapi import FastAPI, UploadFile, File, HTTPException, WebSocket, WebSocketDisconnect, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel, HttpUrl
from typing import List, Optional, Dict, Any
import asyncio
import json
import uuid
import os
from datetime import datetime
from pathlib import Path
import logging
from collections import defaultdict, Counter

# Import existing modules
from scraper import ReviewScraper
from ai_analyzer import AIAnalyzer
from excel_generator import ExcelGenerator
import config

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Pulse.ai API",
    description="AI-Powered Social Media Review Analysis API with Hierarchical Topics",
    version="2.1.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "*"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600,
)

# Global storage
jobs: Dict[str, Dict[str, Any]] = {}
websocket_connections: Dict[str, WebSocket] = {}

# Pydantic models
class AnalysisRequest(BaseModel):
    urls: List[HttpUrl]
    max_reviews: int = 500
    batch_size: int = 20
    max_pages: int = 10

class JobStatus(BaseModel):
    job_id: str
    status: str
    progress: int
    message: str
    results: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class HealthCheck(BaseModel):
    status: str
    openai_configured: bool
    timestamp: str

# Helper functions
def create_job(job_type: str) -> str:
    """Create a new analysis job"""
    job_id = str(uuid.uuid4())
    jobs[job_id] = {
        "job_id": job_id,
        "type": job_type,
        "status": "pending",
        "progress": 0,
        "message": "Job created",
        "results": None,
        "error": None,
        "created_at": datetime.now().isoformat()
    }
    logger.info(f"✅ Created job: {job_id}")
    return job_id

async def broadcast_progress(job_id: str, progress: int, message: str, status: str = None):
    """Broadcast progress update to WebSocket and update job"""
    if job_id in jobs:
        jobs[job_id]["progress"] = progress
        jobs[job_id]["message"] = message
        if status:
            jobs[job_id]["status"] = status
        
        logger.info(f"📊 Job {job_id}: {progress}% - {message}")
        
        if job_id in websocket_connections:
            try:
                await websocket_connections[job_id].send_json({
                    "progress": progress,
                    "message": message,
                    "status": jobs[job_id]["status"]
                })
            except Exception as e:
                logger.error(f"❌ WebSocket send error for job {job_id}: {e}")

async def run_analysis_async(job_id: str, urls: List[str], max_reviews: int, batch_size: int = 20, max_pages: int = 10):
    """Run analysis asynchronously with hierarchical topic support"""
    try:
        await broadcast_progress(job_id, 1, "🚀 Initializing analysis engine...", "running")
        await asyncio.sleep(0.5)
        
        await broadcast_progress(job_id, 3, "🔧 Loading AI models and scraper...")
        scraper = ReviewScraper()
        analyzer = AIAnalyzer()
        excel_generator = ExcelGenerator()
        
        # Phase 1: Scraping (5-30%)
        await broadcast_progress(job_id, 5, f"🌐 Starting web scraping from {len(urls)} URL(s)...")
        all_reviews = []
        
        for i, url in enumerate(urls):
            progress = 5 + int((i) * 20 / len(urls))
            await broadcast_progress(job_id, progress, f"🔍 Scraping site {i+1}/{len(urls)}: {url[:50]}...")
            
            try:
                reviews = scraper.scrape_reviews(str(url), max_pages=max_pages)
                if reviews:
                    cleaned_reviews = scraper.clean_reviews(reviews)
                    all_reviews.extend(cleaned_reviews[:max_reviews // len(urls)])
                    
                    progress = 5 + int((i + 1) * 20 / len(urls))
                    await broadcast_progress(job_id, progress, f"✅ Scraped {len(cleaned_reviews)} reviews from site {i+1}")
                    logger.info(f"Scraped {len(cleaned_reviews)} reviews from {url}")
            except Exception as e:
                logger.error(f"Error scraping {url}: {e}")
                await broadcast_progress(job_id, progress, f"⚠️ Warning: Could not scrape {url[:50]}")
                continue
        
        if not all_reviews:
            raise Exception("❌ No reviews found from any URL. Please check URLs and try again.")
        
        all_reviews = all_reviews[:max_reviews]
        await broadcast_progress(job_id, 30, f"✅ Scraping complete! Collected {len(all_reviews)} reviews")
        await asyncio.sleep(0.5)
        
        # Phase 2: Sentiment Analysis (30-50%)
        await broadcast_progress(job_id, 32, "🧠 Starting AI sentiment analysis...")
        await asyncio.sleep(0.3)
        
        await broadcast_progress(job_id, 35, f"💭 Analyzing sentiment for {len(all_reviews)} reviews...")
        sentiment_results = analyzer.analyze_sentiment_batch(all_reviews, batch_size=batch_size)
        
        await broadcast_progress(job_id, 48, "✅ Sentiment analysis complete!")
        await asyncio.sleep(0.3)
        await broadcast_progress(job_id, 50, f"📊 Processed {len(sentiment_results)} sentiment scores")
        
        # Phase 3: Hierarchical Topic Modeling (50-65%)
        await broadcast_progress(job_id, 52, "🔬 Creating hierarchical topic taxonomy (Level 1 → Level 2)...")
        await asyncio.sleep(0.3)
        
        await broadcast_progress(job_id, 55, "🧩 LLM analyzing review patterns and building topic tree...")
        hierarchical_topics, topic_assignments = analyzer.extract_topics(all_reviews)
        
        num_level1 = len(hierarchical_topics)
        total_level2 = sum(len(t.get('level2_topics', [])) for t in hierarchical_topics)
        await broadcast_progress(job_id, 63, f"✅ Created {num_level1} Level 1 topics with {total_level2} Level 2 subtopics")
        await asyncio.sleep(0.3)
        await broadcast_progress(job_id, 65, "📋 Topic categorization complete")
        
        # Phase 4: Trend Analysis (65-80%)
        await broadcast_progress(job_id, 67, "📈 Analyzing trends over time...")
        await asyncio.sleep(0.3)
        
        await broadcast_progress(job_id, 70, "🔄 Combining sentiment with timeline data...")
        reviews_with_sentiment = []
        for i, review in enumerate(all_reviews):
            review_copy = review.copy()
            if i < len(sentiment_results):
                review_copy['sentiment'] = sentiment_results[i]['sentiment']
            reviews_with_sentiment.append(review_copy)
        
        await broadcast_progress(job_id, 75, "📊 Computing trend patterns...")
        trends = analyzer.analyze_trends(reviews_with_sentiment)
        
        await broadcast_progress(job_id, 80, "✅ Trend analysis complete")
        await asyncio.sleep(0.3)
        
        # Phase 5: Generate Insights (80-90%)
        await broadcast_progress(job_id, 82, "💡 Generating AI insights...")
        await asyncio.sleep(0.3)
        
        await broadcast_progress(job_id, 85, "🤖 AI analyzing patterns and generating recommendations...")
        insights = analyzer.generate_insights(sentiment_results, hierarchical_topics, trends)
        
        await broadcast_progress(job_id, 90, "✅ Strategic insights generated")
        await asyncio.sleep(0.3)
        
        # Phase 6: Calculate hierarchical quantifications (90-95%)
        await broadcast_progress(job_id, 92, "📐 Calculating topic distributions and percentages...")
        hierarchical_stats = calculate_hierarchical_stats(topic_assignments, len(all_reviews), hierarchical_topics)
        
        # Phase 7: Generate Excel Report (95-98%)
        await broadcast_progress(job_id, 95, "📊 Creating comprehensive Excel report...")
        await asyncio.sleep(0.3)
        
        await broadcast_progress(job_id, 96, "📑 Formatting charts and tables...")
        filename = excel_generator.generate_report(
            reviews=all_reviews,
            sentiment_results=sentiment_results,
            topics=hierarchical_topics,
            topic_assignments=topic_assignments,
            trends=trends,
            insights=insights
        )
        
        await broadcast_progress(job_id, 98, "✅ Excel report generated")
        await asyncio.sleep(0.3)
        
        # Store results
        await broadcast_progress(job_id, 99, "🎨 Preparing dashboard data...")
        results = {
            "reviews": all_reviews,
            "sentiment_results": sentiment_results,
            "hierarchical_topics": hierarchical_topics,
            "topic_assignments": topic_assignments,
            "hierarchical_stats": hierarchical_stats,
            "trends": trends,
            "insights": insights,
            "filename": filename,
            "total_reviews": len(all_reviews)
        }
        
        jobs[job_id]["results"] = results
        jobs[job_id]["status"] = "completed"
        await broadcast_progress(job_id, 100, "🎉 Analysis completed successfully!", "completed")
        
        logger.info(f"✅ Job {job_id} completed with {len(all_reviews)} reviews and {num_level1} Level 1 topics")
        
    except Exception as e:
        error_msg = str(e)
        logger.error(f"❌ Job {job_id} failed: {error_msg}")
        jobs[job_id]["status"] = "failed"
        jobs[job_id]["error"] = error_msg
        jobs[job_id]["message"] = f"Analysis failed: {error_msg}"
        await broadcast_progress(job_id, 0, f"❌ Error: {error_msg}", "failed")

def calculate_hierarchical_stats(topic_assignments, total_reviews, hierarchical_topics):
    """
    Calculate Level 1 and Level 2 topic statistics with proper quantification
    
    Level 1: percentage of total reviews
    Level 2: percentage of Level 1 parent reviews
    """
    # Count assignments by Level 1 and Level 2
    level1_counts = defaultdict(int)
    level2_counts = defaultdict(lambda: defaultdict(int))
    
    for assignment in topic_assignments:
        level1_id = assignment['level1_id']
        level2_id = assignment['level2_id']
        
        level1_counts[level1_id] += 1
        level2_counts[level1_id][level2_id] += 1
    
    # Build hierarchical stats
    hierarchical_stats = []
    
    for level1_topic in hierarchical_topics:
        level1_id = level1_topic['id']
        level1_name = level1_topic['name']
        level1_count = level1_counts.get(level1_id, 0)
        level1_percentage = (level1_count / total_reviews * 100) if total_reviews > 0 else 0
        
        # Calculate Level 2 stats
        level2_stats = []
        for level2_topic in level1_topic.get('level2_topics', []):
            level2_id = level2_topic['id']
            level2_name = level2_topic['name']
            level2_count = level2_counts[level1_id].get(level2_id, 0)
            
            # Level 2 percentage is relative to Level 1 parent
            level2_percentage = (level2_count / level1_count * 100) if level1_count > 0 else 0
            
            level2_stats.append({
                'id': level2_id,
                'name': level2_name,
                'count': level2_count,
                'percentage': round(level2_percentage, 1),
                'percentage_of_total': round((level2_count / total_reviews * 100) if total_reviews > 0 else 0, 1)
            })
        
        hierarchical_stats.append({
            'level1_id': level1_id,
            'level1_name': level1_name,
            'level1_count': level1_count,
            'level1_percentage': round(level1_percentage, 1),
            'level2_topics': level2_stats
        })
    
    logger.info(f"📊 Hierarchical stats calculated for {len(hierarchical_stats)} Level 1 topics")
    return hierarchical_stats

# API Endpoints

@app.get("/", response_model=HealthCheck)
async def root():
    """Health check endpoint"""
    return {
        "status": "online",
        "openai_configured": bool(config.OPENAI_API_KEY and config.OPENAI_API_KEY != "your_openai_api_key_here"),
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/analyze/urls")
async def analyze_urls(request: AnalysisRequest, background_tasks: BackgroundTasks):
    """Start URL-based analysis with hierarchical topic support"""
    
    if not config.OPENAI_API_KEY or config.OPENAI_API_KEY == "your_openai_api_key_here":
        raise HTTPException(status_code=400, detail="OpenAI API key not configured")
    
    job_id = create_job("url_analysis")
    urls = [str(url) for url in request.urls]
    
    logger.info(f"🚀 Starting hierarchical analysis for job {job_id} with {len(urls)} URLs")
    
    asyncio.create_task(run_analysis_async(
        job_id, 
        urls, 
        request.max_reviews,
        request.batch_size,
        request.max_pages
    ))
    
    return {"job_id": job_id, "message": "Analysis started"}

@app.post("/api/analyze/upload")
async def analyze_upload(file: UploadFile = File(...)):
    """Start file-based analysis"""
    
    if not file.filename.endswith(('.csv', '.xlsx', '.xls')):
        raise HTTPException(status_code=400, detail="Invalid file type. Only CSV and Excel files are supported.")
    
    if not config.OPENAI_API_KEY or config.OPENAI_API_KEY == "your_openai_api_key_here":
        raise HTTPException(status_code=400, detail="OpenAI API key not configured")
    
    upload_dir = Path("uploads")
    upload_dir.mkdir(exist_ok=True)
    
    file_path = upload_dir / f"{uuid.uuid4()}_{file.filename}"
    
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)
    
    job_id = create_job("file_analysis")
    
    jobs[job_id]["status"] = "completed"
    jobs[job_id]["message"] = "File uploaded (full analysis coming soon)"
    jobs[job_id]["progress"] = 100
    
    return {"job_id": job_id, "message": "File uploaded successfully"}

@app.get("/api/jobs/{job_id}", response_model=JobStatus)
async def get_job_status(job_id: str):
    """Get job status and results"""
    
    if job_id not in jobs:
        logger.warning(f"Job {job_id} not found")
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = jobs[job_id]
    logger.info(f"Status check for job {job_id}: {job['status']} - {job['progress']}%")
    return job

@app.get("/api/download/{filename}")
async def download_report(filename: str):
    """Download generated Excel report"""
    
    file_path = Path(filename)
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(
        path=str(file_path),
        filename=filename,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

@app.delete("/api/jobs/{job_id}")
async def cancel_job(job_id: str):
    """Cancel a running job"""
    
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    if jobs[job_id]["status"] == "running":
        jobs[job_id]["status"] = "cancelled"
        jobs[job_id]["message"] = "Job cancelled by user"
        return {"message": "Job cancelled"}
    
    return {"message": "Job already completed or failed"}

@app.websocket("/ws/{job_id}")
async def websocket_endpoint(websocket: WebSocket, job_id: str):
    """WebSocket for real-time progress updates"""
    
    await websocket.accept()
    websocket_connections[job_id] = websocket
    logger.info(f"🔌 WebSocket connected for job {job_id}")
    
    try:
        while True:
            try:
                data = await asyncio.wait_for(websocket.receive_text(), timeout=1.0)
            except asyncio.TimeoutError:
                if job_id in jobs:
                    job_status = jobs[job_id]["status"]
                    if job_status in ["completed", "failed", "cancelled"]:
                        await websocket.send_json({
                            "status": job_status,
                            "progress": jobs[job_id]["progress"],
                            "message": jobs[job_id]["message"]
                        })
                        logger.info(f"✅ Sent final WebSocket status for job {job_id}: {job_status}")
                        break
                continue
                
    except WebSocketDisconnect:
        logger.info(f"🔌 WebSocket disconnected for job {job_id}")
    except Exception as e:
        logger.error(f"❌ WebSocket error for job {job_id}: {e}")
    finally:
        if job_id in websocket_connections:
            del websocket_connections[job_id]
            logger.info(f"🔌 Cleaned up WebSocket for job {job_id}")

@app.get("/api/config")
async def get_config():
    """Get current configuration"""
    return {
        "max_reviews_per_site": config.MAX_REVIEWS_PER_SITE,
        "openai_model": config.OPENAI_MODEL,
        "supported_sites": list(config.SITE_SELECTORS.keys())
    }

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Pulse.ai Backend Server with Hierarchical Topic Support...")
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)