"""
AI Code Review Assistant - Main Application
ForteBank Hackathon 2025
"""

from fastapi import FastAPI, Request, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
from typing import Optional

from backend.config import settings
from backend.models import WebhookPayload, HealthResponse
from backend.gitlab_client import GitLabClient
from backend.code_analyzer import CodeAnalyzer
from backend.feedback import learning_system, Feedback
from backend.database import init_db, close_db, save_review, get_stats as get_db_stats
import json
from pathlib import Path
import time
from collections import defaultdict

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Cache for preventing duplicate processing
# Format: {(project_id, mr_iid): last_processed_timestamp}
processed_mrs_cache = defaultdict(float)
DUPLICATE_THRESHOLD = 60  # seconds - don't process same MR within 60 seconds


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager for FastAPI application"""
    logger.info("🚀 Starting AI Code Review Assistant...")
    
    # Initialize database
    init_db()
    logger.info("✅ Database initialized")
    
    # Initialize GitLab client
    app.state.gitlab_client = GitLabClient()
    logger.info("✅ GitLab client initialized")
    
    # Initialize Code Analyzer
    app.state.code_analyzer = CodeAnalyzer()
    logger.info("✅ Code Analyzer initialized")
    
    logger.info(f"🎯 LLM Provider: {settings.LLM_PROVIDER}")
    logger.info(f"🌐 Server running on {settings.APP_HOST}:{settings.PORT}")
    
    yield
    
    # Cleanup
    logger.info("👋 Shutting down...")
    close_db()


# Initialize FastAPI app
app = FastAPI(
    title="AI Code Review Assistant",
    description="Automated code review system for GitLab using AI",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", response_model=HealthResponse)
async def root():
    """Root endpoint - health check"""
    return HealthResponse(
        status="healthy",
        message="AI Code Review Assistant is running",
        version="1.0.0"
    )


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        message="All systems operational",
        version="1.0.0"
    )


@app.post("/webhook/gitlab")
async def gitlab_webhook(
    request: Request,
    x_gitlab_token: Optional[str] = Header(None)
):
    """
    GitLab webhook endpoint
    Receives notifications about Merge Request events
    """
    logger.info("📨 Received GitLab webhook")
    
    # Verify webhook token
    if x_gitlab_token != settings.WEBHOOK_SECRET:
        logger.warning("❌ Invalid webhook token")
        raise HTTPException(status_code=401, detail="Invalid webhook token")
    
    # Parse payload
    try:
        payload = await request.json()
        logger.info(f"📦 Payload: {payload.get('object_kind', 'unknown')}")
        
        # Only process merge request events
        if payload.get('object_kind') != 'merge_request':
            return {"status": "ignored", "reason": "Not a merge request event"}
        
        # Get MR details
        mr_data = payload.get('object_attributes', {})
        action = mr_data.get('action')
        
        # Only process on 'open' or 'update' actions
        if action not in ['open', 'update', 'reopen']:
            return {"status": "ignored", "reason": f"Action '{action}' not processed"}
        
        project_id = payload.get('project', {}).get('id')
        mr_iid = mr_data.get('iid')
        
        # Check for duplicate processing
        mr_key = (project_id, mr_iid)
        current_time = time.time()
        last_processed = processed_mrs_cache.get(mr_key, 0)
        
        if current_time - last_processed < DUPLICATE_THRESHOLD:
            logger.info(f"⏭️ Skipping duplicate webhook for MR #{mr_iid} (processed {int(current_time - last_processed)}s ago)")
            return {"status": "skipped", "reason": "Duplicate webhook within threshold"}
        
        # Mark as processing
        processed_mrs_cache[mr_key] = current_time
        
        logger.info(f"🔍 Processing MR #{mr_iid} in project {project_id}")
        
        # Get clients from app state
        gitlab_client: GitLabClient = request.app.state.gitlab_client
        code_analyzer: CodeAnalyzer = request.app.state.code_analyzer
        
        # Fetch MR details and changes
        mr = gitlab_client.get_merge_request(project_id, mr_iid)
        changes = gitlab_client.get_mr_changes(project_id, mr_iid)
        
        if not changes:
            logger.info("ℹ️ No changes to analyze")
            return {"status": "success", "message": "No changes to analyze"}
        
        # Analyze code
        logger.info("🤖 Starting AI analysis...")
        analysis_result = await code_analyzer.analyze_changes(changes, mr_data)
        
        # Post results to GitLab
        logger.info("💬 Posting analysis results to GitLab...")
        gitlab_client.post_review_comments(
            project_id=project_id,
            mr_iid=mr_iid,
            analysis_result=analysis_result
        )
        
        # Update MR labels based on analysis
        if settings.AUTO_LABEL_MR:
            gitlab_client.update_mr_labels(
                project_id=project_id,
                mr_iid=mr_iid,
                score=analysis_result['score']
            )
        
        # Save to database
        save_review(mr_data, analysis_result)
        
        logger.info(f"✅ Analysis complete! Score: {analysis_result['score']}/10")
        
        return {
            "status": "success",
            "message": "Code review completed",
            "score": analysis_result['score'],
            "issues_found": len(analysis_result['issues'])
        }
        
    except Exception as e:
        logger.error(f"❌ Error processing webhook: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/stats")
async def get_statistics():
    """Get analysis statistics (for dashboard)"""
    try:
        # Try to get from database first
        db_stats = get_db_stats()
        if db_stats:
            return db_stats
        
        # Fallback to JSON file
        stats_file = Path("data/stats.json")
        if stats_file.exists():
            with open(stats_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        return {
            "total_mrs": 0,
            "total_comments": 0,
            "time_saved_hours": 0,
            "avg_score": 0.0
        }
    except Exception as e:
        logger.error(f"Error loading stats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/feedback")
async def add_feedback(feedback: Feedback):
    """Add feedback from senior developer"""
    try:
        learning_system.add_feedback(feedback)
        return {"status": "success", "message": "Feedback recorded"}
    except Exception as e:
        logger.error(f"Error adding feedback: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/feedback/stats")
async def get_feedback_stats():
    """Get feedback statistics"""
    try:
        return learning_system.get_feedback_stats()
    except Exception as e:
        logger.error(f"Error getting feedback stats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/learning/patterns")
async def get_learning_patterns():
    """Get learned patterns"""
    try:
        return learning_system.get_learning_patterns()
    except Exception as e:
        logger.error(f"Error getting learning patterns: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.APP_HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
