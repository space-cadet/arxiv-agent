import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import asyncio
import json
import os
from pathlib import Path

from backend.arxiv_scraper.scraper import ArxivScraper

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="arXiv Agent API", 
             description="API for fetching and recommending arXiv papers")

# Add CORS middleware to allow requests from Streamlit
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development - restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create data directory for storage
DATA_DIR = Path("./data")
DATA_DIR.mkdir(exist_ok=True)
PROFILES_FILE = DATA_DIR / "user_profiles.json"

# Initialize with empty profiles if file doesn't exist
if not PROFILES_FILE.exists():
    with open(PROFILES_FILE, "w") as f:
        json.dump({}, f)

# Define data models
class AuthorQuery(BaseModel):
    author_id: str
    max_results: Optional[int] = 50

class CategoryQuery(BaseModel):
    categories: List[str]
    date_range: Optional[str] = None

class UserProfile(BaseModel):
    user_id: str
    interests: List[str] = []
    favorite_authors: List[str] = []
    saved_papers: List[str] = []

# Initialize scraper
scraper = ArxivScraper()

@app.get("/")
async def root():
    return {"status": "ok", "message": "arXiv Agent API is running"}

@app.post("/papers/by-author")
async def get_papers_by_author(query: AuthorQuery):
    """Fetch papers by a specific author"""
    try:
        papers = await scraper.fetch_by_author(query.author_id, query.max_results)
        
        # Add a placeholder for citation counts
        # In a full implementation, you would need to query a citation database or use a service
        # like Semantic Scholar API, CrossRef, or Google Scholar (with proper rate limiting)
        for paper in papers:
            paper["citation_count"] = 0  # Placeholder for future enhancement
            
            # Parse the arXiv ID for potential external API queries
            if paper.get("id"):
                try:
                    # Example: Extract arXiv ID from URL like http://arxiv.org/abs/1234.5678
                    arxiv_id = paper["id"].split("/")[-1]
                    paper["arxiv_id"] = arxiv_id
                except:
                    paper["arxiv_id"] = None
        
        return {"success": True, "papers": papers, "count": len(papers)}
    except Exception as e:
        logger.error(f"Error fetching papers by author: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/papers/daily")
async def get_daily_papers(query: CategoryQuery):
    """Fetch daily papers with optional category filtering"""
    try:
        # Debug logging to trace the issue
        logger.info(f"Received daily papers request with categories: {query.categories}")
        
        papers = await scraper.fetch_daily_submissions(
            categories=query.categories, 
            date_range=query.date_range
        )
        
        logger.info(f"Found {len(papers)} papers")
        return {"success": True, "papers": papers, "count": len(papers)}
    except Exception as e:
        logger.error(f"Error fetching daily papers: {e}", exc_info=True)
        # Return a more helpful error message instead of throwing an exception
        return {"success": False, "papers": [], "error": str(e), "count": 0}

@app.get("/profile/{user_id}")
async def get_user_profile(user_id: str):
    """Get a user profile by ID"""
    with open(PROFILES_FILE, "r") as f:
        profiles = json.load(f)
    
    if user_id not in profiles:
        return {"success": False, "message": "Profile not found"}
    
    return {"success": True, "profile": profiles[user_id]}

@app.post("/profile")
async def save_user_profile(profile: UserProfile):
    """Create or update a user profile"""
    with open(PROFILES_FILE, "r") as f:
        profiles = json.load(f)
    
    # Update profile data
    profiles[profile.user_id] = profile.dict()
    
    # Save back to file
    with open(PROFILES_FILE, "w") as f:
        json.dump(profiles, f, indent=2)
    
    return {"success": True, "message": "Profile updated successfully"}

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up resources on shutdown"""
    await scraper.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
