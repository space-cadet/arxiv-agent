from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import arxiv
from typing import List, Optional, Dict
from pydantic import BaseModel

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AuthorSearchRequest(BaseModel):
    author_id: str
    max_results: int = 50

class DailySearchRequest(BaseModel):
    categories: List[str] = []
    date_range: Optional[Dict] = None

@app.post("/papers/by-author")
async def get_papers_by_author(request: AuthorSearchRequest):
    # Dead simple author search
    search = arxiv.Search(
        query=f"au:{request.author_id}",
        max_results=request.max_results
    )
    papers = []
    for result in search.results():
        papers.append({
            "title": result.title,
            "authors": [author.name for author in result.authors],
            "summary": result.summary,
            "published": result.published.isoformat() + "Z",
            "updated": result.updated.isoformat() + "Z" if result.updated else None,
            "categories": result.categories,
            "id": result.entry_id,
            "pdf_url": result.pdf_url
        })
    return {"success": True, "papers": papers}

@app.post("/papers/daily")
async def get_daily_papers(request: DailySearchRequest):
    # Simple category-based search
    if not request.categories:
        query = "cat:*"  # All categories
    else:
        query = " OR ".join([f"cat:{cat}" for cat in request.categories])
        
    search = arxiv.Search(
        query=query,
        max_results=50,
        sort_by=arxiv.SortCriterion.SubmittedDate
    )
    
    papers = []
    for result in search.results():
        papers.append({
            "title": result.title,
            "authors": [author.name for author in result.authors],
            "summary": result.summary,
            "published": result.published.isoformat() + "Z",
            "updated": result.updated.isoformat() + "Z" if result.updated else None,
            "categories": result.categories,
            "id": result.entry_id,
            "pdf_url": result.pdf_url
        })
    return {"success": True, "papers": papers}

@app.get("/profile/{user_id}")
async def get_profile(user_id: str):
    # Super simple profile response
    return {"success": True, "profile": {"interests": [], "favorite_authors": []}}

@app.post("/profile")
async def save_profile(profile_data: dict):
    # Just return success for now
    return {"success": True}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)