# backend/arxiv_client/client.py

import arxiv
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

class ArxivClient:
    def __init__(self):
        self.client = arxiv.Client()
        
    async def fetch_daily_submissions(self, categories: Optional[List[str]] = None, 
                                    date_range: Optional[str] = None) -> List[Dict]:
        """
        Fetch papers from arXiv with filtering options.
        Uses asyncio.to_thread to make synchronous arxiv package calls asynchronous.
        """
        query_parts = []
        
        # Add category filtering as primary constraint
        if categories:
            cat_query = " OR ".join([f"cat:{c.strip()}" for c in categories])
            query_parts.append(f"({cat_query})")
            
        # Add date range as secondary constraint
        if date_range:
            query_parts.append(f"submittedDate:{date_range}")
        else:
            # Default to last 3 days
            query_parts.append("submittedDate:[now-3d TO now]")
        
        # Build final query
        search_query = " AND ".join(query_parts)
        logger.info(f"Constructed arXiv query: {search_query}")
            
        # Create search
        search = arxiv.Search(
            query=search_query,
            max_results=50,
            sort_by=arxiv.SortCriterion.SubmittedDate,
            sort_order=arxiv.SortOrder.Descending
        )
        
        # Run search in thread pool to maintain async compatibility
        try:
            results = await asyncio.to_thread(self._execute_search, search)
            formatted_results = [self._format_result(result) for result in results]
            logger.info(f"Retrieved {len(formatted_results)} papers from arXiv")
            return formatted_results
        except Exception as e:
            logger.error(f"Error fetching papers from arXiv: {str(e)}")
            raise
    
    async def fetch_by_author(self, author: str, max_results: int = 50) -> List[Dict]:
        """Fetch papers by a specific author."""
        search = arxiv.Search(
            query=f"au:\"{author}\"",
            max_results=max_results,
            sort_by=arxiv.SortCriterion.SubmittedDate,
            sort_order=arxiv.SortOrder.Descending
        )
        try:
            results = await asyncio.to_thread(self._execute_search, search)
            formatted_results = [self._format_result(result) for result in results]
            logger.info(f"Retrieved {len(formatted_results)} papers by author {author}")
            return formatted_results
        except Exception as e:
            logger.error(f"Error fetching papers by author from arXiv: {str(e)}")
            raise
    
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