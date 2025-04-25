from fastapi.testclient import TestClient
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.main import app

client = TestClient(app)

def test_author_search():
    response = client.post("/papers/by-author", json={"author_id": "Bengio"})
    assert response.status_code == 200
    data = response.json()
    assert data["success"] == True
    assert len(data["papers"]) > 0
    assert "title" in data["papers"][0]

def test_daily_papers():
    response = client.post("/papers/daily", json={"categories": ["cs.AI"]})
    assert response.status_code == 200
    data = response.json()
    assert data["success"] == True
    assert len(data["papers"]) > 0
    assert "title" in data["papers"][0]