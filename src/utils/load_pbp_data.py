#!/usr/bin/env python3
"""
Load NFL Play-by-Play Data to PostgreSQL
Loads detailed play-by-play data from nfl_data_py into the database
"""

import os
import sys
from pathlib import Path
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

def create_pbp_table(engine):
    """Create the play-by-play table if it doesn't exist"""
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS nfl_play_by_play (
        id BIGSERIAL PRIMARY KEY,
        
        -- Game identification
        play_id FLOAT,
        game_id VARCHAR(20) NOT NULL,
        old_game_id VARCHAR(20),
        home_team VARCHAR(3),
        away_team VARCHAR(3),
        season_type VARCHAR(10),
        week INTEGER,
        season INTEGER NOT NULL,
        game_date TIMESTAMP,
        
        -- Game context
        qtr INTEGER,
        down INTEGER,
        ydstogo INTEGER,
        yardline_100 INTEGER,
        quarter_seconds_remaining INTEGER,
        half_seconds_remaining INTEGER,
        game_seconds_remaining INTEGER,
        game_half VARCHAR(10),
        quarter_end INTEGER,
        drive INTEGER,
        sp INTEGER,
        
        -- Team possession
        posteam VARCHAR(3),
        posteam_type VARCHAR(10),
        defteam VARCHAR(3),
        side_of_field VARCHAR(3),
        goal_to_go INTEGER,
        time VARCHAR(10),
        yrdln VARCHAR(10),
        play_description TEXT,
        play_type VARCHAR(20),
        
        -- Play details
        yards_gained INTEGER,
        shotgun INTEGER,
        no_huddle INTEGER,
        qb_dropback INTEGER,
        qb_kneel INTEGER,
        qb_spike INTEGER,
        qb_scramble INTEGER,
        
        -- Passing details
        pass_length VARCHAR(10),
        pass_location VARCHAR(10),
        air_yards INTEGER,
        yards_after_catch INTEGER,
        pass_attempt INTEGER,
        complete_pass INTEGER,
        incomplete_pass INTEGER,
        pass_touchdown INTEGER,
        passing_yards INTEGER,
        interception INTEGER,
        
        -- Rushing details
        run_location VARCHAR(10),
        run_gap VARCHAR(10),
        rush_attempt INTEGER,
        rush_touchdown INTEGER,
        rushing_yards INTEGER,
        
        -- Kicking
        field_goal_result VARCHAR(20),
        kick_distance INTEGER,
        extra_point_result VARCHAR(20),
        two_point_conv_result VARCHAR(20),
        field_goal_attempt INTEGER,
        kickoff_attempt INTEGER,
        punt_attempt INTEGER,
        extra_point_attempt INTEGER,
        two_point_attempt INTEGER,
        
        -- Scoring
        touchdown INTEGER,
        return_touchdown INTEGER,
        safety INTEGER,
        home_score INTEGER,
        away_score INTEGER,
        total_home_score INTEGER,
        total_away_score INTEGER,
        
        -- Player involvement
        passer_player_id VARCHAR(20),
        passer_player_name VARCHAR(100),
        receiver_player_id VARCHAR(20),
        receiver_player_name VARCHAR(100),
        receiving_yards INTEGER,
        rusher_player_id VARCHAR(20),
        rusher_player_name VARCHAR(100),
        lateral_receiver_player_id VARCHAR(20),
        lateral_receiver_player_name VARCHAR(100),
        lateral_receiving_yards INTEGER,
        lateral_rusher_player_id VARCHAR(20),
        lateral_rusher_player_name VARCHAR(100),
        lateral_rushing_yards INTEGER,
        
        -- Turnovers
        fumble INTEGER,
        fumble_lost INTEGER,
        fumble_out_of_bounds INTEGER,
        
        -- Penalties
        penalty INTEGER,
        tackled_for_loss INTEGER,
        
        -- Advanced metrics
        epa FLOAT,
        wpa FLOAT,
        wp FLOAT,
        def_wp FLOAT,
        home_wp FLOAT,
        away_wp FLOAT,
        cpoe FLOAT,
        success INTEGER,
        air_epa FLOAT,
        yac_epa FLOAT,
        comp_air_epa FLOAT,
        comp_yac_epa FLOAT,
        total_home_epa FLOAT,
        total_away_epa FLOAT,
        qb_epa FLOAT,
        xyac_epa FLOAT,
        xyac_mean_yardage FLOAT,
        xyac_median_yardage FLOAT,
        xyac_success INTEGER,
        xyac_fd INTEGER,
        xpass FLOAT,
        pass_oe FLOAT,
        
        -- Timestamps
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    
    -- Create indexes
    CREATE INDEX IF NOT EXISTS idx_pbp_game_id ON nfl_play_by_play(game_id);
    CREATE INDEX IF NOT EXISTS idx_pbp_season_week ON nfl_play_by_play(season, week);
    CREATE INDEX IF NOT EXISTS idx_pbp_game_play ON nfl_play_by_play(game_id, play_id);
    CREATE INDEX IF NOT EXISTS idx_pbp_player_pass ON nfl_play_by_play(passer_player_id, season);
    CREATE INDEX IF NOT EXISTS idx_pbp_player_rush ON nfl_play_by_play(rusher_player_id, season);
    CREATE INDEX IF NOT EXISTS idx_pbp_player_rec ON nfl_play_by_play(receiver_player_id, season);
    CREATE INDEX IF NOT EXISTS idx_pbp_team_season ON nfl_play_by_play(posteam, season);
    CREATE INDEX IF NOT EXISTS idx_pbp_play_type ON nfl_play_by_play(play_type);
    """
    
    with engine.connect() as conn:
        conn.execute(text(create_table_sql))
        conn.commit()
    print("✅ Play-by-play table created successfully")

def load_pbp_data(engine, years, chunk_size=10000):
    """Load play-by-play data for specified years"""
    
    print(f"🏈 Loading play-by-play data for years: {years}")
    
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
    
    for year in years:
        print(f"\n📅 Loading {year} play-by-play data...")
        
        # Check if data already exists for this year
        with engine.connect() as conn:
            existing_count = conn.execute(text(
                "SELECT COUNT(*) FROM nfl_play_by_play WHERE season = :year"
            ), {"year": year}).scalar()
            
            if existing_count > 0:
                print(f"⚠️ {existing_count} records already exist for {year}. Skipping...")
                continue
        
        try:
            # Load data from nfl_data_py (disable cache to ensure fresh data)
            pbp_data = nfl.import_pbp_data([year], cache=False)
            
            if pbp_data.empty:
                print(f"❌ No data found for {year}")
                continue
            
            # Filter to columns that exist in our schema
            available_columns = [col for col in columns_to_keep if col in pbp_data.columns]
            pbp_filtered = pbp_data[available_columns].copy()
            
            # Rename 'desc' to 'play_description' to avoid PostgreSQL reserved word conflict
            if 'desc' in pbp_filtered.columns:
                pbp_filtered = pbp_filtered.rename(columns={'desc': 'play_description'})
            
            # Add timestamps
            pbp_filtered['created_at'] = datetime.utcnow()
            pbp_filtered['updated_at'] = datetime.utcnow()
            
            print(f"📊 Processing {len(pbp_filtered)} plays with {len(available_columns)} columns")
            
            # Load in chunks to avoid memory issues
            total_rows = len(pbp_filtered)
            for i in range(0, total_rows, chunk_size):
                chunk = pbp_filtered.iloc[i:i+chunk_size]
                chunk.to_sql('nfl_play_by_play', engine, if_exists='append', index=False, method='multi')
                print(f"  ✅ Loaded chunk {i//chunk_size + 1}: {len(chunk)} rows")
            
            print(f"🎉 Successfully loaded {total_rows} plays for {year}")
            
        except Exception as e:
            print(f"❌ Error loading {year}: {e}")
            continue

def main():
    """Main function to load play-by-play data"""
    print("🏈 NFL Play-by-Play Data Loader")
    print("=" * 50)
    
    # Get years to load (default to recent years)
    years_to_load = list(range(2020, 2025))  # 2020-2024
    
    print(f"Years to load: {years_to_load}")
    
    try:
        engine = get_db_connection()
        
        # Create table
        create_pbp_table(engine)
        
        # Load data
        load_pbp_data(engine, years_to_load)
        
        # Final stats
        with engine.connect() as conn:
            total_plays = conn.execute(text("SELECT COUNT(*) FROM nfl_play_by_play")).scalar()
            seasons = conn.execute(text(
                "SELECT COUNT(DISTINCT season) FROM nfl_play_by_play"
            )).scalar()
            
        print(f"\n🎊 Load Complete!")
        print(f"Total plays in database: {total_plays:,}")
        print(f"Seasons covered: {seasons}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
