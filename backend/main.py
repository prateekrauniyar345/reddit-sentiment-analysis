"""
FastAPI Backend for Reddit Sentiment Analysis
Improved async processing for handling 1000+ posts
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import asyncio
import aiohttp
import os
from datetime import datetime, timedelta
import json
import sqlite3
from contextlib import asynccontextmanager
import uvicorn
from concurrent.futures import ThreadPoolExecutor
import pandas as pd
import numpy as np
from collections import Counter
import re
from textblob import TextBlob
import logging

# Import our custom modules
from reddit_service import RedditService
from sentiment_service import SentimentService
from analytics_service import AnalyticsService
from database import DatabaseManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global services
reddit_service = None
sentiment_service = None
analytics_service = None
db_manager = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize services on startup"""
    global reddit_service, sentiment_service, analytics_service, db_manager
    
    # Initialize database
    db_manager = DatabaseManager()
    await db_manager.initialize()
    
    # Initialize services
    reddit_service = RedditService()
    sentiment_service = SentimentService()
    analytics_service = AnalyticsService()
    
    logger.info("Services initialized successfully")
    yield
    
    # Cleanup on shutdown
    await db_manager.close()
    logger.info("Services cleaned up")

app = FastAPI(
    title="Reddit Sentiment Analysis API",
    description="Advanced Reddit sentiment analysis with async processing",
    version="2.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class AnalysisRequest(BaseModel):
    query: str
    limit: int = 100
    subreddits: Optional[List[str]] = None
    time_filter: Optional[str] = "week"  # all, day, week, month, year
    sort_type: Optional[str] = "relevance"  # relevance, hot, top, new

class AnalysisStatus(BaseModel):
    task_id: str
    status: str  # pending, processing, completed, failed
    progress: int  # 0-100
    message: str

class Comment(BaseModel):
    id: str
    author: str
    body: str
    score: int
    created_utc: float
    sentiment_score: float
    sentiment_label: str

class Post(BaseModel):
    id: str
    title: str
    selftext: str
    author: str
    subreddit: str
    score: int
    upvote_ratio: float
    num_comments: int
    created_utc: float
    url: str
    is_video: bool
    over_18: bool
    comments: List[Comment]
    overall_sentiment: float
    sentiment_label: str
    engagement_score: float

class AnalysisResult(BaseModel):
    task_id: str
    query: str
    total_posts: int
    total_comments: int
    analysis_duration: float
    created_at: datetime
    posts: List[Post]
    analytics: Dict[str, Any]

# In-memory task storage (in production, use Redis)
active_tasks: Dict[str, Dict] = {}

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "Reddit Sentiment Analysis API", "version": "2.0.0"}

@app.post("/analyze", response_model=Dict[str, str])
async def start_analysis(request: AnalysisRequest, background_tasks: BackgroundTasks):
    """Start Reddit sentiment analysis"""
    import uuid
    task_id = str(uuid.uuid4())
    
    # Store task info
    active_tasks[task_id] = {
        "status": "pending",
        "progress": 0,
        "message": "Analysis queued",
        "created_at": datetime.utcnow(),
        "request": request.dict()
    }
    
    # Start background analysis
    background_tasks.add_task(perform_analysis, task_id, request)
    
    return {"task_id": task_id, "message": "Analysis started"}

@app.get("/status/{task_id}", response_model=AnalysisStatus)
async def get_analysis_status(task_id: str):
    """Get analysis status"""
    if task_id not in active_tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task = active_tasks[task_id]
    return AnalysisStatus(
        task_id=task_id,
        status=task["status"],
        progress=task["progress"],
        message=task["message"]
    )

@app.get("/result/{task_id}")
async def get_analysis_result(task_id: str):
    """Get analysis result"""
    if task_id not in active_tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task = active_tasks[task_id]
    if task["status"] != "completed":
        raise HTTPException(status_code=400, detail="Analysis not completed")
    
    # Get result from database
    result = await db_manager.get_analysis_result(task_id)
    if not result:
        raise HTTPException(status_code=404, detail="Result not found")
    
    return result

@app.get("/history")
async def get_analysis_history(limit: int = 10):
    """Get analysis history"""
    history = await db_manager.get_analysis_history(limit)
    return {"history": history}

@app.delete("/result/{task_id}")
async def delete_analysis_result(task_id: str):
    """Delete analysis result"""
    await db_manager.delete_analysis_result(task_id)
    if task_id in active_tasks:
        del active_tasks[task_id]
    return {"message": "Result deleted successfully"}

async def perform_analysis(task_id: str, request: AnalysisRequest):
    """Perform the actual analysis in background"""
    try:
        # Update status
        active_tasks[task_id]["status"] = "processing"
        active_tasks[task_id]["message"] = "Fetching Reddit data..."
        active_tasks[task_id]["progress"] = 10
        
        start_time = datetime.utcnow()
        
        # Fetch Reddit data with improved async processing
        posts_data = await reddit_service.fetch_posts_async(
            query=request.query,
            limit=request.limit,
            subreddits=request.subreddits,
            time_filter=request.time_filter,
            sort_type=request.sort_type,
            progress_callback=lambda p: update_progress(task_id, p, "Fetching posts...")
        )
        
        # Update progress
        active_tasks[task_id]["progress"] = 40
        active_tasks[task_id]["message"] = "Analyzing sentiment..."
        
        # Perform sentiment analysis in batches
        analyzed_posts = await sentiment_service.analyze_posts_batch(
            posts_data,
            progress_callback=lambda p: update_progress(task_id, 40 + p//2, "Analyzing sentiment...")
        )
        
        # Update progress
        active_tasks[task_id]["progress"] = 80
        active_tasks[task_id]["message"] = "Generating analytics..."
        
        # Generate advanced analytics
        analytics = await analytics_service.generate_analytics(analyzed_posts)
        
        # Calculate analysis duration
        end_time = datetime.utcnow()
        duration = (end_time - start_time).total_seconds()
        
        # Create result object
        result = AnalysisResult(
            task_id=task_id,
            query=request.query,
            total_posts=len(analyzed_posts),
            total_comments=sum(len(post.comments) for post in analyzed_posts),
            analysis_duration=duration,
            created_at=start_time,
            posts=analyzed_posts,
            analytics=analytics
        )
        
        # Save to database
        await db_manager.save_analysis_result(result)
        
        # Update final status
        active_tasks[task_id]["status"] = "completed"
        active_tasks[task_id]["progress"] = 100
        active_tasks[task_id]["message"] = "Analysis completed successfully"
        
        logger.info(f"Analysis {task_id} completed in {duration:.2f} seconds")
        
    except Exception as e:
        logger.error(f"Analysis {task_id} failed: {str(e)}")
        active_tasks[task_id]["status"] = "failed"
        active_tasks[task_id]["message"] = f"Analysis failed: {str(e)}"

def update_progress(task_id: str, progress: int, message: str):
    """Update task progress"""
    if task_id in active_tasks:
        active_tasks[task_id]["progress"] = min(progress, 100)
        active_tasks[task_id]["message"] = message

@app.get("/analytics/summary/{task_id}")
async def get_analytics_summary(task_id: str):
    """Get analytics summary for a completed analysis"""
    result = await db_manager.get_analysis_result(task_id)
    if not result:
        raise HTTPException(status_code=404, detail="Result not found")
    
    return result["analytics"]

@app.get("/analytics/trends")
async def get_sentiment_trends(days: int = 30):
    """Get sentiment trends over time"""
    trends = await db_manager.get_sentiment_trends(days)
    return {"trends": trends}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )