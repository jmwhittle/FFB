#!/usr/bin/env python3
"""
Monitor Play-by-Play Data Loading Progress
Check the current status of historical data loading
"""

import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import time

# Load environment variables
load_dotenv()

def monitor_progress():
    """Monitor the progress of play-by-play data loading"""
    print("🏈 Play-by-Play Loading Progress Monitor")
    print("=" * 50)
    
    try:
        database_url = os.getenv('DATABASE_URL')
        engine = create_engine(database_url)
        
        target_years = list(range(1999, 2025))  # 1999-2024
        
        while True:
            with engine.connect() as conn:
                # Get current status
                current_stats = conn.execute(text("""
                    SELECT 
                        COUNT(*) as total_plays,
                        COUNT(DISTINCT season) as seasons_loaded,
                        COUNT(DISTINCT game_id) as games,
                        MIN(season) as first_season,
                        MAX(season) as last_season,
                        MAX(created_at) as last_update
                    FROM nfl_play_by_play
                """)).fetchone()
                
                # Get years loaded
                years_loaded = conn.execute(text("""
                    SELECT season, COUNT(*) as plays
                    FROM nfl_play_by_play 
                    GROUP BY season 
                    ORDER BY season
                """)).fetchall()
                
                years_set = {year.season for year in years_loaded}
                missing_years = [year for year in target_years if year not in years_set]
                
                # Clear screen and show progress
                print("\033[2J\033[H")  # Clear screen
                print("🏈 NFL Play-by-Play Loading Progress")
                print("=" * 50)
                print(f"📊 Total Plays: {current_stats.total_plays:,}")
                print(f"📅 Seasons Loaded: {current_stats.seasons_loaded}/26")
                print(f"🏈 Games: {current_stats.games:,}")
                print(f"📈 Range: {current_stats.first_season}-{current_stats.last_season}")
                print(f"🕒 Last Update: {current_stats.last_update}")
                
                progress_pct = (current_stats.seasons_loaded / 26) * 100
                progress_bar = "█" * int(progress_pct // 4) + "░" * (25 - int(progress_pct // 4))
                print(f"\n📊 Progress: [{progress_bar}] {progress_pct:.1f}%")
                
                if missing_years:
                    print(f"\n⏳ Still loading: {missing_years[:10]}")
                    if len(missing_years) > 10:
                        print(f"    ... and {len(missing_years) - 10} more years")
                else:
                    print(f"\n✅ All years loaded!")
                    break
                
                print(f"\n🔄 Refreshing in 30 seconds... (Ctrl+C to exit)")
                time.sleep(30)
                
    except KeyboardInterrupt:
        print(f"\n👋 Monitoring stopped by user")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    monitor_progress()
