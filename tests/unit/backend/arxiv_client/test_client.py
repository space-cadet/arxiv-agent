import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime
from backend.arxiv_client.client import ArxivClient
import arxiv

@pytest.mark.asyncio
async def test_fetch_daily_submissions_success(mocker):
    """Test successful API call with mock response"""
    # Create mock result
    mock_result = MagicMock()
    mock_result.title = "Test Paper"
    mock_result.authors = ["John Doe"]
    mock_result.summary = "Test summary"
    mock_result.published = datetime.now()
    mock_result.updated = datetime.now()
    mock_result.entry_id = "test_id"
    mock_result.pdf_url = "http://test.pdf"
    mock_result.categories = ["cs.AI"]
    
    # Mock the arxiv client's results method
    mock_results = mocker.patch.object(arxiv.Client, "results", return_value=[mock_result])
    
    client = ArxivClient()
    results = await client.fetch_daily_submissions(categories=["cs.AI"])
    
    assert len(results) == 1
    paper = results[0]
    assert paper["title"] == "Test Paper"
    assert paper["authors"] == ["John Doe"]
    assert paper["categories"] == ["cs.AI"]

@pytest.mark.asyncio
async def test_category_filtering(mocker):
    """Test category parameter is properly included in query"""
    mock_result = MagicMock()
    mocker.patch.object(arxiv.Client, "results", return_value=[mock_result])
    
    client = ArxivClient()
    await client.fetch_daily_submissions(categories=["cs.LG", "stat.ML"])
    
    # Verify the search query contains the categories
    args, _ = arxiv.Search.call_args
    assert "cat:cs.LG OR cat:stat.ML" in args[0]["query"]

@pytest.mark.asyncio
async def test_date_range_filtering(mocker):
    """Test date range parameter is properly included in query"""
    mock_result = MagicMock()
    mocker.patch.object(arxiv.Client, "results", return_value=[mock_result])
    
    client = ArxivClient()
    await client.fetch_daily_submissions(date_range="2023-01-01 TO 2023-01-31")
    
    args, _ = arxiv.Search.call_args
    assert "submittedDate:2023-01-01 TO 2023-01-31" in args[0]["query"]

@pytest.mark.asyncio
async def test_author_search(mocker):
    """Test fetching papers by author"""
    mock_result = MagicMock()
    mock_result.title = "Author Paper"
    mocker.patch.object(arxiv.Client, "results", return_value=[mock_result])
    
    client = ArxivClient()
    results = await client.fetch_by_author("John Doe")
    
    args, _ = arxiv.Search.call_args
    assert 'au:"John Doe"' in args[0]["query"]
    assert len(results) == 1
    assert results[0]["title"] == "Author Paper"

@pytest.mark.asyncio
async def test_multiple_criteria_query(mocker):
    """Test query with multiple criteria"""
    mock_result = MagicMock()
    mocker.patch.object(arxiv.Client, "results", return_value=[mock_result])
    
    client = ArxivClient()
    await client.fetch_daily_submissions(
        categories=["cs.AI", "stat.ML"],
        date_range="2023-01-01 TO 2023-01-31"
    )
    
    args, _ = arxiv.Search.call_args
    query = args[0]["query"]
    assert "submittedDate:2023-01-01 TO 2023-01-31" in query
    assert "cat:cs.AI OR cat:stat.ML" in query