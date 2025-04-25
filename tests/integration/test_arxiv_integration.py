import pytest
from backend.arxiv_client.client import ArxivClient
import logging

logger = logging.getLogger(__name__)

@pytest.mark.integration
@pytest.mark.asyncio
async def test_real_arxiv_api():
    """Integration test with real Arxiv API"""
    logger.info("Starting real API test")
    client = ArxivClient()
    
    try:
        results = await client.fetch_daily_submissions(categories=["cs.AI"])
        logger.info(f"Retrieved {len(results)} papers from ArXiv API")
        # Verify we got actual content
        assert len(results) > 0, "No papers retrieved from ArXiv API"
        first_paper = results[0]
        assert 'title' in first_paper, "Paper object missing title"
        assert first_paper['title'], "Paper title is empty"
        logger.debug(f"First paper details: {first_paper}")
    except Exception as e:
        logger.error(f"API call failed: {str(e)}")
        raise

@pytest.mark.integration
@pytest.mark.asyncio
async def test_real_category_filtering():
    """Test category filtering with real API"""
    client = ArxivClient()
    results = await client.fetch_daily_submissions(categories=["cs.LG"])
    
    # Basic validation of response
    assert isinstance(results, list)
    if len(results) > 0:
        # If we got results, verify they're in the correct category
        first_paper = results[0]
        assert 'cs.LG' in first_paper['categories']

@pytest.mark.integration
@pytest.mark.asyncio
async def test_real_author_search():
    """Test author search with real API"""
    client = ArxivClient()
    # Using a well-known author who likely has papers
    results = await client.fetch_by_author("Geoffrey Hinton")
    
    assert isinstance(results, list)
    assert len(results) > 0, "No papers found for test author"