"""
Utility functions for the Fantasy Football Database project.
"""

import json
from datetime import datetime
from typing import Dict, List, Any, Optional
import pandas as pd


def format_player_name(first_name: Optional[str], last_name: Optional[str]) -> str:
    """Format player name consistently."""
    if not first_name and not last_name:
        return "Unknown Player"
    if not first_name:
        return last_name or "Unknown"
    if not last_name:
        return first_name
    return f"{first_name} {last_name}"


def calculate_fantasy_points(stats: Dict[str, Any], scoring_settings: Dict[str, float] = None) -> float:
    """Calculate fantasy points based on player stats and league scoring settings."""
    if not scoring_settings:
        # Default PPR scoring
        scoring_settings = {
            'pass_yd': 0.04,
            'pass_td': 4.0,
            'pass_int': -2.0,
            'rush_yd': 0.1,
            'rush_td': 6.0,
            'rec': 1.0,  # PPR
            'rec_yd': 0.1,
            'rec_td': 6.0,
            'fgm': 3.0,
            'xpm': 1.0,
            'def_td': 6.0,
            'def_int': 2.0,
            'def_fum_rec': 2.0,
            'def_sack': 1.0,
            'def_safety': 2.0
        }
    
    points = 0.0
    
    for stat, value in stats.items():
        if stat in scoring_settings and value is not None:
            points += float(value) * scoring_settings[stat]
    
    return round(points, 2)


def get_current_nfl_week() -> int:
    """Get the current NFL week (simplified logic)."""
    # This is a simplified version - in production you'd want to use the Sleeper API
    # or a more sophisticated date calculation
    now = datetime.now()
    
    # NFL season typically starts first Thursday of September
    # This is a rough approximation
    if now.month >= 9 or now.month <= 1:
        # During season
        if now.month == 9:
            return min(4, max(1, (now.day - 5) // 7 + 1))
        elif now.month >= 10:
            return min(18, (now.month - 9) * 4 + (now.day // 7) + 1)
        else:  # January - playoffs
            return 18 + (now.day // 7)
    else:
        return 1  # Off-season default


def validate_sleeper_data(data: Dict[str, Any], required_fields: List[str]) -> bool:
    """Validate that Sleeper API data contains required fields."""
    if not data:
        return False
    
    for field in required_fields:
        if field not in data:
            return False
    
    return True


def clean_json_data(data: Any) -> Any:
    """Clean JSON data for database storage."""
    if isinstance(data, dict):
        return {k: clean_json_data(v) for k, v in data.items() if v is not None}
    elif isinstance(data, list):
        return [clean_json_data(item) for item in data if item is not None]
    elif isinstance(data, (int, float, str, bool)):
        return data
    else:
        return str(data) if data is not None else None


def safe_int_convert(value: Any) -> Optional[int]:
    """Safely convert value to integer."""
    if value is None:
        return None
    try:
        return int(float(value))
    except (ValueError, TypeError):
        return None


def safe_float_convert(value: Any) -> Optional[float]:
    """Safely convert value to float."""
    if value is None:
        return None
    try:
        return float(value)
    except (ValueError, TypeError):
        return None


def chunk_list(lst: List[Any], chunk_size: int) -> List[List[Any]]:
    """Split a list into chunks of specified size."""
    for i in range(0, len(lst), chunk_size):
        yield lst[i:i + chunk_size]


def get_position_display_order() -> Dict[str, int]:
    """Get standard position display order for fantasy football."""
    return {
        'QB': 1,
        'RB': 2,
        'WR': 3,
        'TE': 4,
        'K': 5,
        'DEF': 6,
        'DST': 6,  # Alternative name for defense
        'FLEX': 7,
        'BN': 8,
        'IR': 9
    }


def format_currency(amount: float) -> str:
    """Format amount as currency string."""
    return f"${amount:,.2f}"


def get_week_range(week: int, season: str = "2024") -> tuple:
    """Get date range for a specific NFL week."""
    # This is a simplified version - you'd want more accurate date calculations
    # based on the actual NFL schedule
    
    import datetime
    
    # Approximate start of 2024 NFL season (first Thursday in September)
    season_start = datetime.date(2024, 9, 5)  # Adjust based on actual season
    
    # Each week is 7 days
    week_start = season_start + datetime.timedelta(weeks=week-1)
    week_end = week_start + datetime.timedelta(days=6)
    
    return week_start, week_end


def create_summary_stats(df: pd.DataFrame, group_by: str, metrics: List[str]) -> pd.DataFrame:
    """Create summary statistics for a DataFrame."""
    if df.empty:
        return pd.DataFrame()
    
    summary_funcs = {
        'count': 'count',
        'mean': 'mean',
        'median': 'median',
        'std': 'std',
        'min': 'min',
        'max': 'max',
        'sum': 'sum'
    }
    
    result = df.groupby(group_by)[metrics].agg(list(summary_funcs.keys())).round(2)
    return result


# Export commonly used functions
__all__ = [
    'format_player_name',
    'calculate_fantasy_points',
    'get_current_nfl_week',
    'validate_sleeper_data',
    'clean_json_data',
    'safe_int_convert',
    'safe_float_convert',
    'chunk_list',
    'get_position_display_order',
    'format_currency',
    'get_week_range',
    'create_summary_stats'
]
