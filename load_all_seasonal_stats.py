"""
Load seasonal stats for the last 10 years.
"""

from src.utils.load_seasonal_stats import load_seasonal_stats, get_seasonal_stats_summary

def load_all_seasonal_years():
    """Load seasonal stats for the last 10 years."""
    print("Loading seasonal stats for the last 10 years...")
    print("This should take 3-5 minutes...")
    
    try:
        # Load last 10 years from API (much faster than weekly data)
        load_seasonal_stats(force_reload=False, use_api=True)
        
        print("\nGetting final summary...")
        total, season_counts = get_seasonal_stats_summary()
        
        print(f"\nAll seasonal data loading complete!")
        print(f"Total records: {total}")
        for season, count in sorted(season_counts.items()):
            print(f"Season {season}: {count} records")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Ask user for confirmation
    response = input("This will download ~6,000 seasonal records over 10 years. Continue? (y/n): ")
    if response.lower() == 'y':
        load_all_seasonal_years()
    else:
        print("Cancelled.")
