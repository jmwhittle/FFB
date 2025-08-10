"""
Sleeper API client for fetching fantasy football data.
"""

import os
import time
from typing import Dict, List, Optional, Any
import requests
from dotenv import load_dotenv

load_dotenv()


class SleeperClient:
    """Client for interacting with the Sleeper Fantasy Football API."""
    
    def __init__(self):
        self.base_url = os.getenv("SLEEPER_API_BASE_URL", "https://api.sleeper.app/v1")
        self.rate_limit = int(os.getenv("SLEEPER_RATE_LIMIT", "60"))  # per minute
        self.last_request_time = 0
        
    def _rate_limit_check(self):
        """Ensure we don't exceed rate limits."""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        min_interval = 60 / self.rate_limit  # seconds between requests
        
        if time_since_last < min_interval:
            sleep_time = min_interval - time_since_last
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def _make_request(self, endpoint: str) -> Optional[Dict]:
        """Make a request to the Sleeper API."""
        self._rate_limit_check()
        
        url = f"{self.base_url}/{endpoint}"
        
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error making request to {url}: {e}")
            return None
    
    def get_user(self, username: str) -> Optional[Dict]:
        """Get user information by username."""
        return self._make_request(f"user/{username}")
    
    def get_user_leagues(self, user_id: str, sport: str = "nfl", season: str = "2024") -> Optional[List[Dict]]:
        """Get leagues for a user."""
        return self._make_request(f"user/{user_id}/leagues/{sport}/{season}")
    
    def get_league(self, league_id: str) -> Optional[Dict]:
        """Get league information."""
        return self._make_request(f"league/{league_id}")
    
    def get_league_users(self, league_id: str) -> Optional[List[Dict]]:
        """Get users in a league."""
        return self._make_request(f"league/{league_id}/users")
    
    def get_league_rosters(self, league_id: str) -> Optional[List[Dict]]:
        """Get rosters in a league."""
        return self._make_request(f"league/{league_id}/rosters")
    
    def get_league_matchups(self, league_id: str, week: int) -> Optional[List[Dict]]:
        """Get matchups for a specific week."""
        return self._make_request(f"league/{league_id}/matchups/{week}")
    
    def get_nfl_players(self) -> Optional[Dict]:
        """Get all NFL players."""
        return self._make_request("players/nfl")
    
    def get_nfl_state(self) -> Optional[Dict]:
        """Get current NFL season state."""
        return self._make_request("state/nfl")
    
    def get_league_transactions(self, league_id: str, round_num: int) -> Optional[List[Dict]]:
        """Get transactions for a league round."""
        return self._make_request(f"league/{league_id}/transactions/{round_num}")
    
    def get_trending_players(self, sport: str = "nfl", add_drop: str = "add", 
                           hours: int = 24, limit: int = 25) -> Optional[List[Dict]]:
        """Get trending players."""
        return self._make_request(f"players/{sport}/trending/{add_drop}?lookback_hours={hours}&limit={limit}")


# Example usage and testing functions
def test_sleeper_client():
    """Test the Sleeper client with some basic calls."""
    client = SleeperClient()
    
    # Test getting NFL state
    print("Testing NFL state...")
    nfl_state = client.get_nfl_state()
    if nfl_state:
        print(f"Current NFL season: {nfl_state.get('season')}, Week: {nfl_state.get('week')}")
    
    # Test getting trending players
    print("\nTesting trending players...")
    trending = client.get_trending_players(limit=5)
    if trending:
        print(f"Found {len(trending)} trending players")
        for player in trending[:3]:
            print(f"- {player.get('player_id')}: {player.get('count')} adds")


if __name__ == "__main__":
    test_sleeper_client()
