import pytest
from backend.arxiv_scraper.scraper import ArxivScraper
import logging

logger = logging.getLogger(__name__)

@pytest.mark.integration
@pytest.mark.asyncio
async def test_real_arxiv_api():
    """Integration test with real Arxiv API"""
    logger.info("Starting real API test")
    scraper = ArxivScraper()
    
    try:
        results = await scraper.fetch_daily_submissions(categories=["cs.AI"])
        logger.info(f"Retrieved {len(results)} papers from ArXiv API")
        # Verify we got actual content
        assert len(results) > 0, "No papers retrieved from ArXiv API"
        first_paper = results[0]
        assert hasattr(first_paper, 'title'), "Paper object missing title attribute"
        assert first_paper.title, "Paper title is empty"
        logger.debug(f"First paper details: {first_paper}")
    except Exception as e:
        logger.error(f"API call failed: {str(e)}")
        raise

@pytest.mark.integration
@pytest.mark.asyncio
async def test_real_category_filtering():
    """Test category filtering with real API"""
    scraper = ArxivScraper()
    results = await scraper.fetch_daily_submissions(categories=["cs.LG"])
    
    # Basic validation of response
    assert isinstance(results, list)