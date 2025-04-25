import { ArXivClient } from '@agentic/arxiv';

async function testArxivClient() {
    // Create a client instance with base URL
    const client = new ArXivClient({
        apiBaseUrl: 'http://export.arxiv.org/api'
    });

    try {
        // Test basic search
        console.log('Testing basic search...');
        const searchResults = await client.search({
            searchQuery: 'machine learning',
            maxResults: 5,
            start: 0
        });
        console.log('Search results:', searchResults);

        // Test search with multiple criteria
        console.log('\nTesting search with category...');
        const categoryResults = await client.search({
            searchQuery: 'ti:"neural networks" AND cat:cs.AI',
            maxResults: 3,
            start: 0
        });
        console.log('Category search results:', categoryResults);

        // Test author search
        console.log('\nTesting author search...');
        const authorResults = await client.search({
            searchQuery: 'au:hinton',
            maxResults: 3,
            start: 0
        });
        console.log('Author search results:', authorResults);

    } catch (error) {
        console.error('Error occurred:', error);
    }
}

// Run the test
testArxivClient().catch(console.error);