"""
FastAPI Backend for Pulse.ai - Social Media Review Analyzer
Provides REST API and WebSocket for real-time analysis
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

# Import existing modules
from scraper import ReviewScraper
from ai_analyzer import AIAnalyzer
from excel_generator import ExcelGenerator
import config

# Initialize FastAPI app
app = FastAPI(
    title="Pulse.ai API",
    description="AI-Powered Social Media Review Analysis API",
    version="1.0.0"
)

# CORS middleware - allow React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # React dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global storage for jobs (in production, use Redis/Database)
jobs: Dict[str, Dict[str, Any]] = {}
websocket_connections: Dict[str, WebSocket] = {}

# Pydantic models
class AnalysisRequest(BaseModel):
    urls: List[HttpUrl]
    max_reviews: int = 500
    num_topics: int = 5

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
        "id": job_id,
        "type": job_type,
        "status": "pending",
        "progress": 0,
        "message": "Job created",
        "results": None,
        "error": None,
        "created_at": datetime.now().isoformat()
    }
    return job_id

async def send_progress(job_id: str, progress: int, message: str):
    """Send progress update via WebSocket"""
    if job_id in jobs:
        jobs[job_id]["progress"] = progress
        jobs[job_id]["message"] = message
        
        # Send to WebSocket if connected
        if job_id in websocket_connections:
            try:
                await websocket_connections[job_id].send_json({
                    "progress": progress,
                    "message": message,
                    "status": jobs[job_id]["status"]
                })
            except:
                pass

def run_analysis_sync(job_id: str, urls: List[str], max_reviews: int):
    """Run analysis synchronously (for background task)"""
    try:
        # Update job status
        jobs[job_id]["status"] = "running"
        
        # Initialize components
        scraper = ReviewScraper()
        analyzer = AIAnalyzer()
        excel_generator = ExcelGenerator()
        
        # Phase 1: Scraping
        asyncio.run(send_progress(job_id, 10, "Starting review scraping..."))
        all_reviews = []
        
        for i, url in enumerate(urls):
            asyncio.run(send_progress(
                job_id, 
                10 + (i + 1) * 20 // len(urls),
                f"Scraping reviews from {url[:50]}..."
            ))
            
            reviews = scraper.scrape_reviews(str(url), max_pages=5)
            if reviews:
                cleaned_reviews = scraper.clean_reviews(reviews)
                all_reviews.extend(cleaned_reviews[:max_reviews])
        
        if not all_reviews:
            raise Exception("No reviews found")
        
        # Phase 2: Sentiment Analysis
        asyncio.run(send_progress(job_id, 35, "Analyzing sentiment with AI..."))
        sentiment_results = analyzer.analyze_sentiment_batch(all_reviews)
        
        # Phase 3: Topic Modeling
        asyncio.run(send_progress(job_id, 55, "Extracting topics and themes..."))
        topics, topic_assignments = analyzer.extract_topics(all_reviews)
        
        # Phase 4: Trend Analysis
        asyncio.run(send_progress(job_id, 75, "Analyzing trends..."))
        reviews_with_sentiment = []
        for i, review in enumerate(all_reviews):
            review_copy = review.copy()
            if i < len(sentiment_results):
                review_copy['sentiment'] = sentiment_results[i]['sentiment']
            reviews_with_sentiment.append(review_copy)
        
        trends = analyzer.analyze_trends(reviews_with_sentiment)
        
        # Phase 5: Generate Insights
        asyncio.run(send_progress(job_id, 85, "Generating AI insights..."))
        insights = analyzer.generate_insights(sentiment_results, topics, trends)
        
        # Phase 6: Generate Excel Report
        asyncio.run(send_progress(job_id, 95, "Creating Excel report..."))
        filename = excel_generator.generate_report(
            reviews=all_reviews,
            sentiment_results=sentiment_results,
            topics=topics,
            topic_assignments=topic_assignments,
            trends=trends,
            insights=insights
        )
        
        # Store results
        jobs[job_id]["status"] = "completed"
        jobs[job_id]["progress"] = 100
        jobs[job_id]["message"] = "Analysis completed successfully!"
        jobs[job_id]["results"] = {
            "reviews": all_reviews,
            "sentiment_results": sentiment_results,
            "topics": topics,
            "topic_assignments": topic_assignments,
            "trends": trends,
            "insights": insights,
            "filename": filename,
            "total_reviews": len(all_reviews)
        }
        
        asyncio.run(send_progress(job_id, 100, "Analysis complete!"))
        
    except Exception as e:
        jobs[job_id]["status"] = "failed"
        jobs[job_id]["error"] = str(e)
        jobs[job_id]["message"] = f"Analysis failed: {str(e)}"
        asyncio.run(send_progress(job_id, 0, f"Error: {str(e)}"))

# API Endpoints

@app.get("/", response_model=HealthCheck)
async def root():
    """Health check endpoint"""
    return {
        "status": "online",
        "openai_configured": bool(config.OPENAI_API_KEY),
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/analyze/urls")
async def analyze_urls(request: AnalysisRequest, background_tasks: BackgroundTasks):
    """Start URL-based analysis"""
    
    # Validate OpenAI key
    if not config.OPENAI_API_KEY or config.OPENAI_API_KEY == "your_openai_api_key_here":
        raise HTTPException(status_code=400, detail="OpenAI API key not configured")
    
    # Create job
    job_id = create_job("url_analysis")
    
    # Convert Pydantic URLs to strings
    urls = [str(url) for url in request.urls]
    
    # Run analysis in background
    background_tasks.add_task(run_analysis_sync, job_id, urls, request.max_reviews)
    
    return {"job_id": job_id, "message": "Analysis started"}

@app.post("/api/analyze/upload")
async def analyze_upload(file: UploadFile = File(...), background_tasks: BackgroundTasks = None):
    """Start file-based analysis"""
    
    # Validate file type
    if not file.filename.endswith(('.csv', '.xlsx', '.xls')):
        raise HTTPException(status_code=400, detail="Invalid file type. Only CSV and Excel files are supported.")
    
    # Validate OpenAI key
    if not config.OPENAI_API_KEY or config.OPENAI_API_KEY == "your_openai_api_key_here":
        raise HTTPException(status_code=400, detail="OpenAI API key not configured")
    
    # Save uploaded file
    upload_dir = Path("uploads")
    upload_dir.mkdir(exist_ok=True)
    
    file_path = upload_dir / f"{uuid.uuid4()}_{file.filename}"
    
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)
    
    # Create job
    job_id = create_job("file_analysis")
    
    # TODO: Implement file-based analysis
    # For now, return job ID
    jobs[job_id]["status"] = "completed"
    jobs[job_id]["message"] = "File uploaded successfully (analysis not yet implemented)"
    jobs[job_id]["progress"] = 100
    
    return {"job_id": job_id, "message": "File uploaded and analysis started"}

@app.get("/api/jobs/{job_id}", response_model=JobStatus)
async def get_job_status(job_id: str):
    """Get job status and results"""
    
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return jobs[job_id]

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
    
    try:
        while True:
            # Keep connection alive
            data = await websocket.receive_text()
            
            # If job is completed or failed, close connection
            if job_id in jobs and jobs[job_id]["status"] in ["completed", "failed", "cancelled"]:
                await websocket.send_json({
                    "status": jobs[job_id]["status"],
                    "progress": jobs[job_id]["progress"],
                    "message": jobs[job_id]["message"]
                })
                break
                
    except WebSocketDisconnect:
        pass
    finally:
        if job_id in websocket_connections:
            del websocket_connections[job_id]

@app.get("/api/config")
async def get_config():
    """Get current configuration"""
    return {
        "max_reviews_per_site": config.MAX_REVIEWS_PER_SITE,
        "openai_model": config.OPENAI_MODEL,
        "num_topics": config.NUM_TOPICS,
        "supported_sites": list(config.SITE_SELECTORS.keys())
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)