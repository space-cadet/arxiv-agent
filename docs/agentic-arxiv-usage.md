# Using the Agentic ArXiv Module

This guide explains how to use the ArXiv client from the `@agentic/arxiv` package.

## Installation

You can install the package using your preferred package manager:

```bash
# Using npm
npm install @agentic/arxiv

# Using yarn
yarn add @agentic/arxiv

# Using pnpm
pnpm add @agentic/arxiv
```

## Basic Usage

The ArXivClient is designed to be simple to use and doesn't require any API key for authentication:

```typescript
import { ArXivClient } from '@agentic/arxiv'

// Create a client instance (no API key needed)
const arxiv = new ArXivClient()

// Search for papers
const results = await arxiv.search({
  query: 'machine learning',
  maxResults: 10
})
```

## Search Parameters

The search method accepts parameters like:
- `query`: Your search query string
- `maxResults`: Maximum number of results to return

## Search Query Examples

The ArXiv API supports various search operators and fields:

| Field | Prefix | Description |
|-------|---------|------------|
| Title | ti: | Search paper titles |
| Author | au: | Search author names |
| Abstract | abs: | Search abstracts |
| Category | cat: | Search subject categories |

Example queries:
```typescript
// Search by title
const titleResults = await arxiv.search({
  query: 'ti:"machine learning"',
  maxResults: 10
})

// Search by author
const authorResults = await arxiv.search({
  query: 'au:hinton',
  maxResults: 10
})

// Combined search
const combinedResults = await arxiv.search({
  query: 'ti:"neural networks" AND cat:cs.AI',
  maxResults: 10
})
```

## Best Practices

1. Use reasonable page sizes with `maxResults`
2. Cache results when possible
3. Be mindful of rate limits
4. Use specific search fields for better results

## Response Format

The search results include detailed paper information:
- Title
- Authors (with affiliations when available)
- Abstract
- Categories
- Published/Updated dates
- DOI (when available)
- Links (abstract, PDF, etc.)
- Comments
- Journal references

## Error Handling

The client includes built-in error handling for common issues:
- Invalid queries
- Network errors
- Rate limiting
- Malformed responses

## Additional Resources

For more information about the underlying ArXiv API, refer to:
- [ArXiv API User Manual](https://info.arxiv.org/help/api/user-manual.html)
- [ArXiv API Terms of Use](https://info.arxiv.org/help/api/tou.html)