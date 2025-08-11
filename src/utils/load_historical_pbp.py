#!/usr/bin/env python3
"""
Load Historical NFL Play-by-Play Data (1999-2023)
Loads comprehensive historical play-by-play data to complement existing 2024 data
"""

import os
import sys
from datetime import datetime
import pandas as pd
import nfl_data_py as nfl
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import time

# Load environment variables
load_dotenv()

def get_db_connection():
    """Get database connection"""
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        raise ValueError("DATABASE_URL not found in environment variables")
    return create_engine(database_url)

def load_historical_pbp_data(engine, start_year=1999, end_year=2023, chunk_size=5000):
    """Load historical play-by-play data for specified year range"""
    
    print(f"🏈 Loading Historical Play-by-Play Data ({start_year}-{end_year})")
    print("=" * 60)
    
    # Define the columns we want to keep (matching our database schema)
    columns_to_keep = [
        'play_id', 'game_id', 'old_game_id', 'home_team', 'away_team', 'season_type', 
        'week', 'season', 'game_date', 'qtr', 'down', 'ydstogo', 'yardline_100',
        'quarter_seconds_remaining', 'half_seconds_remaining', 'game_seconds_remaining',
        'game_half', 'quarter_end', 'drive', 'sp', 'posteam', 'posteam_type', 'defteam',
        'side_of_field', 'goal_to_go', 'time', 'yrdln', 'desc', 'play_type',
        'yards_gained', 'shotgun', 'no_huddle', 'qb_dropback', 'qb_kneel', 'qb_spike',
        'qb_scramble', 'pass_length', 'pass_location', 'air_yards', 'yards_after_catch',
        'pass_attempt', 'complete_pass', 'incomplete_pass', 'pass_touchdown',
        'passing_yards', 'interception', 'run_location', 'run_gap', 'rush_attempt',
        'rush_touchdown', 'rushing_yards', 'field_goal_result', 'kick_distance',
        'extra_point_result', 'two_point_conv_result', 'field_goal_attempt',
        'kickoff_attempt', 'punt_attempt', 'extra_point_attempt', 'two_point_attempt',
        'touchdown', 'return_touchdown', 'safety', 'home_score', 'away_score',
        'total_home_score', 'total_away_score', 'passer_player_id', 'passer_player_name',
        'receiver_player_id', 'receiver_player_name', 'receiving_yards', 'rusher_player_id',
        'rusher_player_name', 'lateral_receiver_player_id', 'lateral_receiver_player_name',
        'lateral_receiving_yards', 'lateral_rusher_player_id', 'lateral_rusher_player_name',
        'lateral_rushing_yards', 'fumble', 'fumble_lost', 'fumble_out_of_bounds',
        'penalty', 'tackled_for_loss', 'epa', 'wpa', 'wp', 'def_wp', 'home_wp',
        'away_wp', 'cpoe', 'success', 'air_epa', 'yac_epa', 'comp_air_epa',
        'comp_yac_epa', 'total_home_epa', 'total_away_epa', 'qb_epa', 'xyac_epa',
        'xyac_mean_yardage', 'xyac_median_yardage', 'xyac_success', 'xyac_fd',
        'xpass', 'pass_oe'
    ]
    
    years_to_load = list(range(start_year, end_year + 1))
    
    # Check what years already exist
    with engine.connect() as conn:
        existing_years = conn.execute(text(
            "SELECT DISTINCT season FROM nfl_play_by_play ORDER BY season"
        )).fetchall()
        existing_years_set = {year[0] for year in existing_years}
    
    years_needed = [year for year in years_to_load if year not in existing_years_set]
    
    print(f"📊 Years already loaded: {sorted(existing_years_set)}")
    print(f"📅 Years to load: {years_needed}")
    print(f"🎯 Total years to process: {len(years_needed)}")
    
    if not years_needed:
        print("✅ All years already loaded!")
        return
    
    # Load data in chunks of years to manage memory
    year_chunks = [years_needed[i:i+3] for i in range(0, len(years_needed), 3)]
    
    total_plays_loaded = 0
    
    for chunk_idx, year_chunk in enumerate(year_chunks, 1):
        print(f"\n📦 Processing chunk {chunk_idx}/{len(year_chunks)}: {year_chunk}")
        
        try:
            start_time = time.time()
            
            # Load data for multiple years at once (more efficient)
            print(f"🔄 Fetching data from nfl_data_py API...")
            pbp_data = nfl.import_pbp_data(year_chunk, cache=False)
            
            if pbp_data.empty:
                print(f"❌ No data found for {year_chunk}")
                continue
            
            fetch_time = time.time() - start_time
            print(f"⏱️ Data fetched in {fetch_time:.1f} seconds")
            print(f"📊 Retrieved {len(pbp_data)} plays with {len(pbp_data.columns)} columns")
            
            # Filter to columns that exist in our schema
            available_columns = [col for col in columns_to_keep if col in pbp_data.columns]
            pbp_filtered = pbp_data[available_columns].copy()
            
            # Rename 'desc' to 'play_description' to avoid PostgreSQL reserved word conflict
            if 'desc' in pbp_filtered.columns:
                pbp_filtered = pbp_filtered.rename(columns={'desc': 'play_description'})
            
            # Add timestamps
            pbp_filtered['created_at'] = datetime.utcnow()
            pbp_filtered['updated_at'] = datetime.utcnow()
            
            print(f"📝 Loading {len(pbp_filtered)} plays to database...")
            
            # Load in chunks to avoid memory issues
            total_rows = len(pbp_filtered)
            chunks_loaded = 0
            
            for i in range(0, total_rows, chunk_size):
                chunk = pbp_filtered.iloc[i:i+chunk_size]
                chunk.to_sql('nfl_play_by_play', engine, if_exists='append', index=False, method='multi')
                chunks_loaded += 1
                
                if chunks_loaded % 5 == 0 or i + chunk_size >= total_rows:
                    progress = min(i + chunk_size, total_rows)
                    print(f"    ✅ Loaded {progress:,}/{total_rows:,} plays ({progress/total_rows*100:.1f}%)")
            
            total_plays_loaded += total_rows
            process_time = time.time() - start_time
            
            print(f"🎉 Chunk complete: {total_rows:,} plays in {process_time:.1f} seconds")
            print(f"📈 Running total: {total_plays_loaded:,} plays loaded")
            
            # Clear memory
            del pbp_data, pbp_filtered
            
        except Exception as e:
            print(f"❌ Error processing {year_chunk}: {e}")
            continue
    
    return total_plays_loaded

def show_final_stats(engine):
    """Show final database statistics"""
    with engine.connect() as conn:
        # Overall stats
        stats = conn.execute(text("""
            SELECT 
                COUNT(*) as total_plays,
                COUNT(DISTINCT season) as seasons,
                COUNT(DISTINCT game_id) as games,
                MIN(season) as first_season,
                MAX(season) as last_season
            FROM nfl_play_by_play
        """)).fetchone()
        
        # By decade
        decade_stats = conn.execute(text("""
            SELECT 
                CASE 
                    WHEN season < 2000 THEN '1990s'
                    WHEN season < 2010 THEN '2000s'
                    WHEN season < 2020 THEN '2010s'
                    ELSE '2020s'
                END as decade,
                COUNT(*) as plays,
                COUNT(DISTINCT season) as seasons
            FROM nfl_play_by_play 
            GROUP BY 
                CASE 
                    WHEN season < 2000 THEN '1990s'
                    WHEN season < 2010 THEN '2000s'
                    WHEN season < 2020 THEN '2010s'
                    ELSE '2020s'
                END
            ORDER BY decade
        """)).fetchall()
        
        print(f"\n🎊 Final Database Statistics:")
        print(f"=" * 50)
        print(f"📊 Total plays: {stats.total_plays:,}")
        print(f"📅 Seasons: {stats.seasons} ({stats.first_season}-{stats.last_season})")
        print(f"🏈 Games: {stats.games:,}")
        
        print(f"\n📈 Data by Decade:")
        for decade in decade_stats:
            print(f"  - {decade.decade}: {decade.plays:,} plays ({decade.seasons} seasons)")

def main():
    """Main function to load historical play-by-play data"""
    print("🏈 NFL Historical Play-by-Play Data Loader")
    print("=" * 60)
    print("Loading comprehensive play-by-play data from 1999-2023")
    print("This will create the most complete NFL play database possible!")
    print("=" * 60)
    
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
                return 1
        
        start_time = time.time()
        
        # Load historical data
        total_loaded = load_historical_pbp_data(engine, start_year=1999, end_year=2023)
        
        # Show final statistics
        show_final_stats(engine)
        
        total_time = time.time() - start_time
        
        print(f"\n🎉 Historical Load Complete!")
        print(f"⏱️ Total time: {total_time/60:.1f} minutes")
        print(f"📊 Total plays loaded: {total_loaded:,}")
        print(f"🚀 Your database now contains 26 years of NFL play-by-play data!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
