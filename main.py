"""
Main application entry point for Fantasy Football Database.
"""

import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from config.database import setup_database, get_db
from api.sleeper_client import SleeperClient
from src.services.data_sync import DataSyncService


def main():
    """Main application function."""
    print("Fantasy Football Database")
    print("=" * 30)
    
    # Initialize database
    print("1. Setting up database...")
    try:
        setup_database()
        print("✓ Database setup complete")
    except Exception as e:
        print(f"✗ Database setup failed: {e}")
        return
    
    # Test Sleeper API connection
    print("\n2. Testing Sleeper API connection...")
    try:
        client = SleeperClient()
        nfl_state = client.get_nfl_state()
        if nfl_state:
            print(f"✓ Connected to Sleeper API")
            print(f"  Current NFL Season: {nfl_state.get('season')}")
            print(f"  Current Week: {nfl_state.get('week')}")
            print(f"  Season Type: {nfl_state.get('season_type')}")
        else:
            print("✗ Failed to connect to Sleeper API")
    except Exception as e:
        print(f"✗ Sleeper API test failed: {e}")
    
    print("\n3. System ready!")
    print("Next steps:")
    print("- Configure your .env file with database credentials")
    print("- Run data sync to populate initial data")
    print("- Explore notebooks/ for data analysis examples")


if __name__ == "__main__":
    main()
