# arXiv Agent

A simple application to fetch, browse, and manage arXiv papers based on author, category, and personal interests.

## Features

- Search for papers by author
- Browse daily arXiv submissions filtered by category
- Create and manage research profiles with interests and favorite authors
- Simple and clean interface

## Project Structure

```
arxiv-agent/
├── app.py                # Streamlit frontend
├── backend/              # Backend API and services
│   ├── arxiv_scraper/    # arXiv API interaction
│   ├── storage/          # Data storage
│   └── main.py           # FastAPI backend
├── data/                 # Local data storage
│   ├── profiles/         # User profile storage
│   └── papers/           # Paper cache storage
└── requirements.txt      # Dependencies
```

## Setup and Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd arxiv-agent
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Start the backend server:
```bash
uvicorn backend.main:app --reload --port 8000
```

4. Start the Streamlit frontend:
```bash
streamlit run app.py
```

5. Open your browser and navigate to:
```
http://localhost:8501
```

## Usage

### Author Search
- Enter an author's name or ID to find their publications
- Access search history for quick re-searches (persists between sessions)
- Sort papers by publication date, update date, or title with persistent results
- View paper details including abstract, categories, and publication date
- (Future enhancement: Citation-based sorting)

### Daily Papers
- Browse the latest submissions to arXiv
- Filter by categories of interest (customizable and persistent)
- Read abstracts and access paper links

### My Profile
- Create a personal research profile
- Save your research interests and favorite authors

## Development

This is a minimal working version. Future enhancements could include:
- Advanced recommendation system
- Paper saving and organization
- Citation management
- Collaborative features
