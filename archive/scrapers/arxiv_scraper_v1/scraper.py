import httpx
import logging
from backoff import expo, on_exception

logger = logging.getLogger(__name__)

class ArxivScraper:
    def __init__(self, base_url="http://export.arxiv.org/api/query"):
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=30)
    
    @on_exception(expo, httpx.RequestError, max_tries=3)
    async def fetch_daily_submissions(self, categories=None, date_range=None):
        """
        Fetch papers from arXiv API with filtering options.
        
        Args:
            categories (list): List of arXiv categories (e.g. ['cs.LG', 'stat.ML'])
            date_range (str): Custom date range in arXiv format (e.g. '[2023-01-01 TO 2023-01-31]')
            
        Returns:
            list: List of paper dictionaries
        """
        # Default to last 3 days instead of 24h to get more results
        if date_range:
            query = f"?search_query=submittedDate:{date_range}"
        else:
            query = "?search_query=submittedDate:[now-3d TO now]"
            
        # Add category filtering if provided - ensure proper formatting
        if categories and len(categories) > 0:
            # Join categories with 'OR' operator for arXiv API
            cat_query = "+OR+".join([f"cat:{c}" for c in categories])
            query += f"+AND+({cat_query})"
        
        logger.info(f"Querying arXiv API: {self.base_url}{query}")
        response = await self.client.get(f"{self.base_url}{query}")
        response.raise_for_status()
        
        # Add sorting and increase results
        query += "&sortBy=submittedDate&sortOrder=descending&max_results=50"
        
        logger.info(f"Got response from arXiv API with status: {response.status_code}")
        results = self._parse_results(response.text)
        logger.info(f"Parsed {len(results)} papers from arXiv API response")
        return results
    
    @on_exception(expo, httpx.RequestError, max_tries=3)
    async def fetch_by_author(self, author, max_results=50):
        """
        Fetch papers by a specific author.
        
        Args:
            author (str): Author name
            max_results (int): Maximum number of results to return
            
        Returns:
            list: List of paper dictionaries
        """
        query = f"?search_query=au:{author.replace(' ', '+')}&max_results={max_results}"
        logger.debug(f"Querying arXiv API for author {author}")
        response = await self.client.get(f"{self.base_url}{query}")
        response.raise_for_status()
        return self._parse_results(response.text)
    
    def _parse_results(self, xml_data):
        """
        Parse arXiv API XML response into a list of paper dictionaries.
        
        Args:
            xml_data (str): XML response from arXiv API
            
        Returns:
            list: List of dictionaries containing paper data
        """
        import xml.etree.ElementTree as ET
        
        # Define namespace for parsing
        ns = {'atom': 'http://www.w3.org/2005/Atom',
              'arxiv': 'http://arxiv.org/schemas/atom'}
        
        try:
            root = ET.fromstring(xml_data)
            papers = []
            
            # Get all entries (papers)
            for entry in root.findall('.//atom:entry', ns):
                # Extract paper details with error handling
                try:
                    # Get title
                    title_elem = entry.find('./atom:title', ns)
                    title = title_elem.text.strip() if title_elem is not None else "Unknown Title"
                    
                    # Get authors
                    authors = []
                    for author in entry.findall('./atom:author/atom:name', ns):
                        if author.text:
                            authors.append(author.text)
                    
                    # Get summary/abstract
                    summary_elem = entry.find('./atom:summary', ns)
                    summary = summary_elem.text.strip() if summary_elem is not None else ""
                    
                    # Get dates
                    published_elem = entry.find('./atom:published', ns)
                    published = published_elem.text if published_elem is not None else None
                    
                    updated_elem = entry.find('./atom:updated', ns)
                    updated = updated_elem.text if updated_elem is not None else None
                    
                    # Get ID and convert to URL
                    id_elem = entry.find('./atom:id', ns)
                    paper_id = id_elem.text if id_elem is not None else None
                    
                    # Get PDF link - typically the first link with title="pdf"
                    pdf_url = None
                    for link in entry.findall('./atom:link', ns):
                        if link.get('title') == 'pdf':
                            pdf_url = link.get('href')
                            break
                    
                    # Get categories
                    categories = []
                    for category in entry.findall('./arxiv:primary_category', ns):
                        cat = category.get('term')
                        if cat:
                            categories.append(cat)
                    
                    # Create paper dictionary
                    paper = {
                        'title': title,
                        'authors': authors,
                        'summary': summary,
                        'published': published,
                        'updated': updated,
                        'id': paper_id,
                        'pdf_url': pdf_url,
                        'categories': categories
                    }
                    
                    papers.append(paper)
                except Exception as e:
                    logger.error(f"Error parsing paper entry: {e}")
                    continue
                
            return papers
            
        except ET.ParseError as e:
            logger.error(f"XML parsing error: {e}")
            return []
        
    async def close(self):
        """Close the HTTP client session"""
        await self.client.aclose()