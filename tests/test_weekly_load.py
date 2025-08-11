"""
Test loading a small amount of weekly stats data.
"""

from src.utils.load_weekly_stats import load_weekly_stats, get_weekly_stats_summary

def test_load_single_season():
    """Test loading data for a single season."""
    print("Testing weekly stats loading with 2024 season...")
    
    try:
        # Load just 2024 data
        load_weekly_stats(seasons=[2024], force_reload=True)
        
        print("\nGetting summary...")
        total, season_counts = get_weekly_stats_summary()
        
        print(f"\nLoading complete!")
        print(f"Total records: {total}")
        for season, count in season_counts.items():
            print(f"Season {season}: {count} records")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_load_single_season()
