import json
import os
from pathlib import Path
from typing import Dict, List, Any, Optional

class FileStorage:
    """Simple file-based storage for user profiles and paper data"""
    
    def __init__(self, data_dir: str = "./data"):
        """Initialize storage with the data directory path"""
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        # Create subdirectories
        self.profiles_dir = self.data_dir / "profiles"
        self.profiles_dir.mkdir(exist_ok=True)
        
        self.papers_dir = self.data_dir / "papers"
        self.papers_dir.mkdir(exist_ok=True)
    
    def save_profile(self, user_id: str, profile_data: Dict[str, Any]) -> bool:
        """Save user profile data to a JSON file"""
        try:
            profile_path = self.profiles_dir / f"{user_id}.json"
            with open(profile_path, "w") as f:
                json.dump(profile_data, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving profile: {e}")
            return False
    
    def get_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve user profile data from storage"""
        profile_path = self.profiles_dir / f"{user_id}.json"
        
        if not profile_path.exists():
            return None
            
        try:
            with open(profile_path, "r") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error reading profile: {e}")
            return None
    
    def list_profiles(self) -> List[str]:
        """List all profile IDs"""
        profiles = []
        for file in self.profiles_dir.glob("*.json"):
            profiles.append(file.stem)
        return profiles
    
    def save_paper_cache(self, cache_id: str, papers: List[Dict[str, Any]]) -> bool:
        """Cache paper data to avoid repeated API calls"""
        try:
            cache_path = self.papers_dir / f"{cache_id}.json"
            with open(cache_path, "w") as f:
                json.dump({
                    "timestamp": os.path.getmtime(cache_path) if cache_path.exists() else None,
                    "papers": papers
                }, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving paper cache: {e}")
            return False
    
    def get_paper_cache(self, cache_id: str, max_age_hours: int = 24) -> Optional[List[Dict[str, Any]]]:
        """Retrieve cached paper data if not too old"""
        cache_path = self.papers_dir / f"{cache_id}.json"
        
        if not cache_path.exists():
            return None
            
        try:
            # Check if cache is too old
            cache_time = os.path.getmtime(cache_path)
            current_time = os.time()
            
            # Convert hours to seconds for comparison
            if (current_time - cache_time) > (max_age_hours * 3600):
                return None  # Cache too old
                
            with open(cache_path, "r") as f:
                cache_data = json.load(f)
                return cache_data.get("papers", [])
        except Exception as e:
            print(f"Error reading paper cache: {e}")
            return None
