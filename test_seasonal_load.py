"""
Test loading seasonal stats data for 2024.
"""

from src.utils.load_seasonal_stats import load_seasonal_stats, get_seasonal_stats_summary

def test_load_single_season():
    """Test loading seasonal data for 2024 season."""
    print("Testing seasonal stats loading with 2024 season...")
    
    try:
        # Load just 2024 data from API
        load_seasonal_stats(seasons=[2024], force_reload=True, use_api=True)
        
        print("\nGetting summary...")
        total, season_counts = get_seasonal_stats_summary()
        
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
