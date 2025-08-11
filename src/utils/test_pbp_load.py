#!/usr/bin/env python3
"""
Test NFL Play-by-Play Data Loading
Load just 2024 data to test the table and process
"""

import os
import sys
from datetime import datetime
import pandas as pd
import nfl_data_py as nfl
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_db_connection():
    """Get database connection"""
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        raise ValueError("DATABASE_URL not found in environment variables")
    return create_engine(database_url)

def test_pbp_load():
    """Test loading a small amount of play-by-play data"""
    
    print("🏈 Testing Play-by-Play Data Load")
    print("=" * 40)
    
    try:
        engine = get_db_connection()
        
        # Check if table exists
        with engine.connect() as conn:
            table_exists = conn.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'nfl_play_by_play'
                );
            """)).scalar()
            
            if not table_exists:
                print("❌ nfl_play_by_play table does not exist")
                print("Run load_pbp_data.py first to create the table")
                return
            
            print("✅ Play-by-play table exists")
        
        # Load just 2024 data as a test
        print("\n📅 Loading 2024 play-by-play data...")
        
        # Check if data already exists
        with engine.connect() as conn:
            existing_count = conn.execute(text(
                "SELECT COUNT(*) FROM nfl_play_by_play WHERE season = 2024"
            )).scalar()
            
            if existing_count > 0:
                print(f"⚠️ {existing_count} records already exist for 2024")
                return
        
        # Load just 2024 data
        pbp_data = nfl.import_pbp_data([2024], cache=False)
        
        if pbp_data.empty:
            print("❌ No data retrieved")
            return
        
        print(f"📊 Retrieved {len(pbp_data)} plays with {len(pbp_data.columns)} columns")
        
        # Key columns for our table
        key_columns = [
            'play_id', 'game_id', 'season', 'week', 'posteam', 'defteam',
            'play_type', 'yards_gained', 'desc', 'touchdown', 'epa',
            'passer_player_id', 'passer_player_name', 'rusher_player_id', 
            'rusher_player_name', 'receiver_player_id', 'receiver_player_name'
        ]
        
        # Filter to available columns
        available_columns = [col for col in key_columns if col in pbp_data.columns]
        pbp_test = pbp_data[available_columns].copy()
        
        # Rename desc column to avoid reserved word conflict
        if 'desc' in pbp_test.columns:
            pbp_test = pbp_test.rename(columns={'desc': 'play_description'})
        
        # Add timestamps
        pbp_test['created_at'] = datetime.utcnow()
        pbp_test['updated_at'] = datetime.utcnow()
        
        print(f"📝 Loading {len(pbp_test)} plays to database...")
        
        # Load test data in smaller chunks
        chunk_size = 5000
        total_loaded = 0
        
        for i in range(0, len(pbp_test), chunk_size):
            chunk = pbp_test.iloc[i:i+chunk_size]
            chunk.to_sql('nfl_play_by_play', engine, if_exists='append', index=False, method='multi')
            total_loaded += len(chunk)
            print(f"  ✅ Loaded {total_loaded}/{len(pbp_test)} plays")
        
        # Verify the load
        with engine.connect() as conn:
            final_count = conn.execute(text(
                "SELECT COUNT(*) FROM nfl_play_by_play WHERE season = 2024"
            )).scalar()
            
            sample_plays = conn.execute(text("""
                SELECT game_id, play_type, yards_gained, play_description, epa
                FROM nfl_play_by_play 
                WHERE season = 2024 AND play_type IS NOT NULL
                LIMIT 5
            """)).fetchall()
        
        print(f"\n🎉 Success! Loaded {final_count} plays for 2024")
        print(f"\nSample plays:")
        for play in sample_plays:
            print(f"  - {play.play_type}: {play.yards_gained} yards, EPA: {play.epa}")
        
        print(f"\n✅ Play-by-play table is working correctly!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_pbp_load()
