import httpx
from backoff import expo, on_exception

class ArxivScraper:
    def __init__(self, base_url="http://export.arxiv.org/api/query"):
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=30)
    
    @on_exception(expo, httpx.RequestError, max_tries=3)
    async def fetch_daily_submissions(self, categories=None):
        query = "?search_query=submittedDate:[now-24h TO now]"
        if categories:
            query += f"+AND+cat:{'+OR+'.join(categories)}"
        
        response = await self.client.get(f"{self.base_url}{query}")
        response.raise_for_status()
        return self._parse_results(response.text)
    
    def _parse_results(self, xml_data):
        # Implementation for parsing Arxiv XML
        # Returns list of paper dictionaries
        return []