# Quick Guide: arXiv API Usage

## Base URL
```
http://export.arxiv.org/api/query
```

## Core Query Parameters
- `search_query`: Main search query string
- `id_list`: Comma-separated list of arXiv IDs
- `start`: Starting index (0-based) for pagination
- `max_results`: Number of results to return (max 30000, in slices of 2000)
- `sortBy`: Options - "relevance", "lastUpdatedDate", "submittedDate"
- `sortOrder`: "ascending" or "descending"

## Search Fields
| Field | Prefix | Description |
|-------|---------|------------|
| Title | ti: | Search paper titles |
| Author | au: | Search author names |
| Abstract | abs: | Search abstracts |
| Comment | co: | Search comments |
| Journal Ref | jr: | Search journal references |
| Category | cat: | Search subject categories |
| Report No | rn: | Search report numbers |
| All Fields | all: | Search all fields |

## Search Operators
- AND: Combine terms (both must match)
- OR: Either term can match  
- ANDNOT: Exclude matches
- Grouping: Use parentheses (%28 %29)
- Phrases: Use quotes (%22phrase here%22)

## Examples

1. Basic keyword search:
```
http://export.arxiv.org/api/query?search_query=quantum+computing
```

2. Author search with date filter:
```
http://export.arxiv.org/api/query?search_query=au:einstein+AND+submittedDate:[20200101+TO+20201231]
```

3. Complex search:
```
http://export.arxiv.org/api/query?search_query=ti:"machine learning"+AND+cat:cs.AI+ANDNOT+au:smith
```

4. Search with pagination:
```
http://export.arxiv.org/api/query?search_query=neural+networks&start=0&max_results=10
```

## Best Practices

1. Rate Limiting
   - Include 3-second delays between requests
   - Use reasonable page sizes (max 2000 per request)
   - Cache results when possible

2. Error Handling
   - Check for HTTP status codes
   - Parse response for error messages in Atom feed
   - Verify query syntax before sending

3. Version Handling
   - Latest version: Use base ID (e.g., 2104.12345)
   - Specific version: Append version number (e.g., 2104.12345v2)

## Response Format
The API returns Atom feeds containing:

### Feed-level metadata:
- Title (with query info)
- Total results count
- Start index
- Results per page

### For each paper:
- Title
- Authors (with affiliations when available)
- Abstract
- Categories (including primary)
- Published/Updated dates
- DOI (when available)
- Links (abstract, PDF, etc.)
- Comments
- Journal references

## Common Response Fields
```xml
<entry>
  <id>http://arxiv.org/abs/paper-id</id>
  <updated>2023-01-01T12:00:00Z</updated>
  <published>2023-01-01T12:00:00Z</published>
  <title>Paper Title</title>
  <summary>Abstract text</summary>
  <author>
    <name>Author Name</name>
    <arxiv:affiliation>Institution</arxiv:affiliation>
  </author>
  <arxiv:primary_category term="category"/>
  <link title="pdf" href="http://arxiv.org/pdf/paper-id"/>
</entry>
```

## Common Mistakes to Avoid
1. Not URL-encoding search terms and spaces
2. Exceeding max_results limits
3. Making requests too quickly
4. Not handling multiple author affiliations
5. Assuming all fields are always present
