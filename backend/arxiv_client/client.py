# backend/arxiv_client/client.py

import arxiv
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Optional

class ArxivClient:
    def __init__(self):
        self.client = arxiv.Client()
        
    async def fetch_daily_submissions(self, categories: Optional[List[str]] = None, 
                                    date_range: Optional[str] = None) -> List[Dict]:
        """
        Fetch papers from arXiv with filtering options.
        Uses asyncio.to_thread to make synchronous arxiv package calls asynchronous.
        """
        # Convert date range to arxiv search format
        if date_range:
            search_query = f"submittedDate:{date_range}"
        else:
            # Default to last 3 days
            search_query = "submittedDate:[now-3d TO now]"
            
        # Add category filtering
        if categories:
            cat_query = " OR ".join([f"cat:{c}" for c in categories])
            search_query = f"{search_query} AND ({cat_query})"
            
        # Create search
        search = arxiv.Search(
            query=search_query,
            max_results=50,
            sort_by=arxiv.SortCriterion.SubmittedDate,
            sort_order=arxiv.SortOrder.Descending
        )
        
        # Run search in thread pool to maintain async compatibility
        results = await asyncio.to_thread(self._execute_search, search)
        return [self._format_result(result) for result in results]
    
    async def fetch_by_author(self, author: str, max_results: int = 50) -> List[Dict]:
        """Fetch papers by a specific author."""
        search = arxiv.Search(
            query=f"au:\"{author}\"",
            max_results=max_results
        )
        results = await asyncio.to_thread(self._execute_search, search)
        return [self._format_result(result) for result in results]
    
    def _execute_search(self, search: arxiv.Search) -> List[arxiv.Result]:
        """Execute search using arxiv client."""
        return list(self.client.results(search))
    
    def _format_result(self, result: arxiv.Result) -> Dict:
        """Format arxiv Result object to match existing API response structure."""
        return {
            'title': result.title,
            'authors': [str(author) for author in result.authors],
            'summary': result.summary,
            'published': result.published.isoformat(),
            'updated': result.updated.isoformat() if result.updated else None,
            'id': result.entry_id,
            'pdf_url': result.pdf_url,
            'categories': result.categories
        }