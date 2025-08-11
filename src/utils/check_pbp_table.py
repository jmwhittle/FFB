#!/usr/bin/env python3
"""
Check Play-by-Play Table Status
Verify the table exists and show statistics
"""

import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def main():
    """Check play-by-play table status"""
    print("🏈 Play-by-Play Table Status")
    print("=" * 40)
    
    try:
        database_url = os.getenv('DATABASE_URL')
        engine = create_engine(database_url)
        
        with engine.connect() as conn:
            # Check if table exists
            table_exists = conn.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'nfl_play_by_play'
                );
            """)).scalar()
            
            if not table_exists:
                print("❌ nfl_play_by_play table does not exist")
                return
            
            print("✅ nfl_play_by_play table exists")
            
            # Get table statistics
            stats = conn.execute(text("""
                SELECT 
                    COUNT(*) as total_plays,
                    COUNT(DISTINCT season) as seasons,
                    COUNT(DISTINCT game_id) as games,
                    COUNT(DISTINCT week) as weeks,
                    MIN(season) as first_season,
                    MAX(season) as last_season
                FROM nfl_play_by_play
            """)).fetchone()
            
            print(f"\n📊 Table Statistics:")
            print(f"  - Total plays: {stats.total_plays:,}")
            print(f"  - Seasons: {stats.seasons} ({stats.first_season}-{stats.last_season})")
            print(f"  - Games: {stats.games:,}")
            print(f"  - Weeks: {stats.weeks}")
            
            # Show play type breakdown
            play_types = conn.execute(text("""
                SELECT play_type, COUNT(*) as count
                FROM nfl_play_by_play 
                WHERE play_type IS NOT NULL
                GROUP BY play_type 
                ORDER BY count DESC 
                LIMIT 8
            """)).fetchall()
            
            print(f"\n🎯 Play Types:")
            for play in play_types:
                print(f"  - {play.play_type}: {play.count:,} plays")
            
            # Show recent data
            recent = conn.execute(text("""
                SELECT season, COUNT(*) as plays
                FROM nfl_play_by_play 
                GROUP BY season 
                ORDER BY season DESC
            """)).fetchall()
            
            print(f"\n📅 Data by Season:")
            for season_data in recent:
                print(f"  - {season_data.season}: {season_data.plays:,} plays")
                
            print(f"\n✅ Play-by-play table is ready for analysis!")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
