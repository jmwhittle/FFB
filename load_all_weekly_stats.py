"""
Load the full 10 years of weekly stats data.
"""

from src.utils.load_weekly_stats import load_weekly_stats, get_weekly_stats_summary

def load_all_years():
    """Load weekly stats for the last 10 years."""
    print("Loading weekly stats for the last 10 years...")
    print("This may take 10-15 minutes...")
    
    try:
        # Load last 10 years (2015-2024)
        # Note: This will take some time as it downloads ~50-60k records
        load_weekly_stats(force_reload=False)  # Only load missing years
        
        print("\nGetting final summary...")
        total, season_counts = get_weekly_stats_summary()
        
        print(f"\nAll data loading complete!")
        print(f"Total records: {total}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Ask user for confirmation
    response = input("This will download ~50,000 records over 10 years. Continue? (y/n): ")
    if response.lower() == 'y':
        load_all_years()
    else:
        print("Cancelled.")
