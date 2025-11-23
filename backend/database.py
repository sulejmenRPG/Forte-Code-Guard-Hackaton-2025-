"""
Database configuration and models
"""

from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import logging

from backend.config import settings

logger = logging.getLogger(__name__)

Base = declarative_base()


class CodeReviewDB(Base):
    """Database model for code reviews"""
    __tablename__ = "code_reviews"
    
    id = Column(Integer, primary_key=True, index=True)
    merge_request_id = Column(Integer, index=True)
    project_id = Column(Integer)
    project_name = Column(String)
    author = Column(String)
    team = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    analysis_time = Column(Integer)  # seconds
    score = Column(Float)
    critical_issues = Column(Integer)
    medium_issues = Column(Integer)
    low_issues = Column(Integer)
    status = Column(String)  # pending, approved, rejected
    senior_time_saved = Column(Integer)  # minutes
    summary = Column(Text, nullable=True)


# Database engine
engine = None
SessionLocal = None


def init_db():
    """Initialize database"""
    global engine, SessionLocal
    
    try:
        db_url = settings.DATABASE_URL
        
        # If no DATABASE_URL, use SQLite as fallback
        if not db_url or db_url == "":
            logger.warning("⚠️ No DATABASE_URL found, using SQLite fallback")
            db_url = "sqlite:///./code_review.db"
        
        engine = create_engine(db_url)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        
        # Create tables
        Base.metadata.create_all(bind=engine)
        logger.info(f"✅ Database initialized: {db_url.split('@')[0] if '@' in db_url else 'SQLite'}")
        
    except Exception as e:
        logger.warning(f"⚠️ Database init failed: {str(e)}")
        logger.warning("Continuing without database...")


def close_db():
    """Close database connection"""
    if engine:
        engine.dispose()
        logger.info("Database connection closed")


def get_db():
    """Get database session"""
    if SessionLocal:
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()


def save_review(mr_data: dict, analysis_result: dict):
    """Save code review to database"""
    if not SessionLocal:
        logger.warning("Database not initialized, skipping save")
        return
    
    db = SessionLocal()
    try:
        # Calculate realistic time saved based on code complexity
        critical = analysis_result.get('critical_count', 0)
        medium = analysis_result.get('medium_count', 0)
        low = analysis_result.get('low_count', 0)
        lines_changed = analysis_result.get('lines_changed', 0)
        
        # Realistic calculation based on lines + issues:
        # 1. Base time from lines changed:
        #    - 1-50 lines: 5-10 min
        #    - 51-200 lines: 10-30 min
        #    - 201-500 lines: 30-60 min
        #    - 500+ lines: 60-90 min
        if lines_changed <= 50:
            base_time = 5 + (lines_changed * 0.1)  # ~0.1 min per line
        elif lines_changed <= 200:
            base_time = 10 + ((lines_changed - 50) * 0.13)
        elif lines_changed <= 500:
            base_time = 30 + ((lines_changed - 200) * 0.1)
        else:
            base_time = 60 + min((lines_changed - 500) * 0.06, 30)
        
        # 2. Add time for issues found:
        #    - Critical: 20 min (hard to spot manually)
        #    - Medium: 10 min
        #    - Low: 3 min
        issue_time = (critical * 20) + (medium * 10) + (low * 3)
        
        # 3. Total time
        estimated_time = int(base_time + issue_time)
        
        # 4. Apply reasonable limits
        estimated_time = min(estimated_time, 120)  # Cap at 2 hours
        estimated_time = max(estimated_time, 5)    # Minimum 5 min
        
        review = CodeReviewDB(
            merge_request_id=mr_data.get('iid'),
            project_id=mr_data.get('project_id'),
            project_name=mr_data.get('source_project', {}).get('name', 'Unknown'),
            author=mr_data.get('author', {}).get('username', 'Unknown'),
            team=None,  # Can be extracted from project metadata
            analysis_time=30,  # Placeholder, можно засечь реальное время
            score=analysis_result.get('score', 0),
            critical_issues=critical,
            medium_issues=medium,
            low_issues=low,
            status='needs_review' if analysis_result.get('score', 0) < 7 else 'approved',
            senior_time_saved=estimated_time,
            summary=analysis_result.get('summary', '')
        )
        
        db.add(review)
        db.commit()
        logger.info(f"✅ Review saved to DB: MR #{mr_data.get('iid')}")
        
    except Exception as e:
        logger.error(f"❌ Failed to save review: {str(e)}")
        db.rollback()
    finally:
        db.close()


def clear_all_reviews():
    """Clear all reviews from database"""
    if not SessionLocal:
        logger.warning("Database not initialized")
        return 0
    
    db = SessionLocal()
    try:
        count = db.query(CodeReviewDB).count()
        db.query(CodeReviewDB).delete()
        db.commit()
        logger.info(f"🗑️ Cleared {count} reviews from database")
        return count
    except Exception as e:
        logger.error(f"❌ Failed to clear reviews: {str(e)}")
        db.rollback()
        return 0
    finally:
        db.close()


def get_stats():
    """Get statistics from database"""
    if not SessionLocal:
        return None
    
    db = SessionLocal()
    try:
        from sqlalchemy import func
        
        total_reviews = db.query(func.count(CodeReviewDB.id)).scalar()
        avg_score = db.query(func.avg(CodeReviewDB.score)).scalar() or 0
        total_time_saved = db.query(func.sum(CodeReviewDB.senior_time_saved)).scalar() or 0
        total_issues = db.query(
            func.sum(CodeReviewDB.critical_issues + 
                    CodeReviewDB.medium_issues + 
                    CodeReviewDB.low_issues)
        ).scalar() or 0
        
        return {
            "total_mrs": total_reviews,
            "total_comments": int(total_issues),
            "time_saved_hours": round(total_time_saved / 60, 1),
            "avg_score": round(avg_score, 1)
        }
        
    except Exception as e:
        logger.error(f"Error getting stats: {str(e)}")
        return None
    finally:
        db.close()


def get_recent_reviews(limit: int = 10):
    """Get recent reviews from database"""
    if not SessionLocal:
        return []
    
    db = SessionLocal()
    try:
        reviews = db.query(CodeReviewDB).order_by(
            CodeReviewDB.created_at.desc()
        ).limit(limit).all()
        
        result = []
        for review in reviews:
            result.append({
                "mr_id": review.merge_request_id,
                "project_name": review.project_name,
                "author": review.author,
                "score": review.score,
                "status": review.status,
                "created_at": review.created_at.isoformat() if review.created_at else None,
                "time_saved": review.senior_time_saved,
                "total_issues": review.critical_issues + review.medium_issues + review.low_issues,
                "critical_issues": review.critical_issues
            })
        
        return result
        
    except Exception as e:
        logger.error(f"Error getting recent reviews: {str(e)}")
        return []
    finally:
        db.close()
