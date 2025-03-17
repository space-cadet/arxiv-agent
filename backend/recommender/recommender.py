class PaperRecommender:
    def __init__(self):
        self.embedding_model = "all-mpnet-base-v2"  # Sentence-BERT model
        self.ranking_factors = {
            "relevance": 0.7,
            "recency": 0.2,
            "author_reputation": 0.1
        }
    
    def rank_papers(self, papers, user_vector):
        """Hybrid ranking algorithm"""
        # Combines semantic similarity and collaborative signals