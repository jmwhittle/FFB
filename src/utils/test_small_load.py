"""
Test loading a small subset of historical data to validate the approach.
"""

import sys
import os
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

import nfl_data_py as nfl
from sqlalchemy import text
from src.models import NFLWeeklyStats
from config.database import get_session_local
import pandas as pd

def test_small_load():
    """Test loading just 2022-2023 data."""
    SessionLocal = get_session_local()
    session = SessionLocal()
    
    try:
        print("Testing small data load (2022-2023)...")
        
        # Load just 2 years of data
        years = [2022, 2023]
        weekly_data = nfl.import_weekly_data(years=years)
        
        print(f"Retrieved {len(weekly_data)} records for {years}")
        print(f"Columns: {list(weekly_data.columns)}")
        
        # Clean data
        weekly_data = weekly_data.fillna(0)
        
        # Check for any missing columns in our model vs API data
        api_columns = set(weekly_data.columns)
        
        # Get model columns (excluding timestamps)
        model_columns = set([
            'player_id', 'season', 'week', 'player_name', 'player_display_name',
            'position', 'position_group', 'recent_team', 'headshot_url',
            'opponent_team', 'season_type', 'completions', 'attempts',
            'passing_yards', 'passing_tds', 'interceptions', 'sacks',
            'sack_yards', 'sack_fumbles', 'sack_fumbles_lost',
            'passing_air_yards', 'passing_yards_after_catch',
            'passing_first_downs', 'passing_epa', 'passing_2pt_conversions',
            'carries', 'rushing_yards', 'rushing_tds', 'rushing_fumbles',
            'rushing_fumbles_lost', 'rushing_first_downs', 'rushing_epa',
            'rushing_2pt_conversions', 'targets', 'receptions',
            'receiving_yards', 'receiving_tds', 'receiving_fumbles',
            'receiving_fumbles_lost', 'receiving_air_yards',
            'receiving_yards_after_catch', 'receiving_first_downs',
            'receiving_epa', 'receiving_2pt_conversions', 'special_teams_tds',
            'fantasy_points', 'fantasy_points_ppr', 'target_share',
            'air_yards_share', 'wopr', 'pacr', 'racr', 'dakota'
        ])
        
        missing_in_model = api_columns - model_columns
        missing_in_api = model_columns - api_columns
        
        print(f"\nColumns in API but not in model: {missing_in_model}")
        print(f"Columns in model but not in API: {missing_in_api}")
        
        # Test inserting one record
        first_record = weekly_data.iloc[0].to_dict()
        
        # Remove any extra columns
        filtered_record = {k: v for k, v in first_record.items() if k in model_columns}
        
        print(f"\nTesting insert of one record...")
        print(f"Record data: {filtered_record}")
        
        stats_obj = NFLWeeklyStats(**filtered_record)
        session.add(stats_obj)
        session.commit()
        
        print("✅ Test insert successful!")
        
    except Exception as e:
        session.rollback()
        print(f"❌ Error in test: {e}")
        import traceback
        traceback.print_exc()
    finally:
        session.close()

if __name__ == "__main__":
    test_small_load()
