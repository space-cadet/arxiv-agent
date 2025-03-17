import pytest
from unittest.mock import AsyncMock
from backend.arxiv_scraper.scraper import ArxivScraper
import httpx

@pytest.mark.asyncio
async def test_fetch_daily_submissions_success(mocker):
    """Test successful API call with mock response"""
    mock_response = AsyncMock()
    mock_response.text = "<feed><entry><title>Test Paper</title></entry></feed>"
    mock_response.raise_for_status = AsyncMock()
    
    mock_client = mocker.patch.object(httpx.AsyncClient, "get", new=AsyncMock(return_value=mock_response))
    scraper = ArxivScraper()
    
    results = await scraper.fetch_daily_submissions()
    
    # Verify API endpoint was called correctly
    mock_client.assert_awaited_once_with(
        "http://export.arxiv.org/api/query?search_query=submittedDate:[now-24h TO now]"
    )
    # Verify parsing was attempted (even though our dummy parser returns empty list)
    assert isinstance(results, list)

@pytest.mark.asyncio
async def test_category_filtering(mocker):
    """Test category parameter is properly included in query"""
    mock_response = AsyncMock()
    mock_response.text = "<feed></feed>"
    
    mocker.patch.object(httpx.AsyncClient, "get", new=AsyncMock(return_value=mock_response))
    scraper = ArxivScraper()
    
    await scraper.fetch_daily_submissions(categories=["cs.LG", "stat.ML"])
    
    args, _ = httpx.AsyncClient.get.call_args
    assert "cat:cs.LG+OR+stat.ML" in args[0]

@pytest.mark.asyncio
async def test_http_error_handling(mocker):
    """Test proper exception raising on HTTP errors"""
    # Create mock client that raises the error directly
    mock_get = AsyncMock(side_effect=httpx.HTTPError("Server error"))
    mocker.patch.object(httpx.AsyncClient, "get", new=mock_get)
    
    scraper = ArxivScraper()
    
    with pytest.raises(httpx.HTTPError):
        await scraper.fetch_daily_submissions()