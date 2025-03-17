class UserProfileManager:
    def __init__(self):
        self.interest_weights = {}  # {"nlp": 0.8, "computer_vision": 0.6}
        self.history = []           # Previously saved/liked papers
    
    def calculate_interest_vector(self):
        """Convert free-form interests to weighted vector"""
        # Uses TF-IDF or sentence transformers