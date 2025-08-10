"""
Utility script to populate NFL seasonal stats data.
"""

import pandas as pd
import nfl_data_py as nfl
from datetime import datetime
from sqlalchemy.orm import sessionmaker
from sqlalchemy import and_, func
from config.database import get_engine
from src.models import NFLSeasonalStats, NFLWeeklyStats
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create session factory
def get_session():
    engine = get_engine()
    Session = sessionmaker(bind=engine)
    return Session()


def load_seasonal_stats(seasons=None, force_reload=False, use_api=True):
    """
    Load NFL seasonal stats for specified seasons.
    
    Args:
        seasons: List of seasons to load (default: last 10 years)
        force_reload: If True, delete existing data and reload
        use_api: If True, use nfl_data_py API. If False, calculate from weekly data in DB
    """
    if seasons is None:
        current_year = datetime.now().year
        seasons = list(range(current_year - 9, current_year + 1))  # Last 10 years
    
    logger.info(f"Loading seasonal stats for seasons: {seasons}")
    
    session = get_session()
    
    try:
        # Check if we should force reload
        if force_reload:
            logger.info("Force reload requested - deleting existing data")
            session.query(NFLSeasonalStats).filter(
                NFLSeasonalStats.season.in_(seasons)
            ).delete(synchronize_session=False)
            session.commit()
        
        for season in seasons:
            logger.info(f"Processing season {season}")
            
            # Check if data already exists for this season
            existing_count = session.query(NFLSeasonalStats).filter(
                NFLSeasonalStats.season == season
            ).count()
            
            if existing_count > 0 and not force_reload:
                logger.info(f"Season {season} already loaded ({existing_count} records), skipping")
                continue
            
            try:
                if use_api:
                    # Load seasonal data from nfl_data_py API
                    seasonal_data = load_from_api(season)
                else:
                    # Calculate seasonal data from weekly data in database
                    seasonal_data = calculate_from_weekly_data(session, season)
                
                if seasonal_data.empty:
                    logger.warning(f"No seasonal data found for season {season}")
                    continue
                
                logger.info(f"Processing {len(seasonal_data)} seasonal records for {season}")
                
                # Convert to database records
                records = convert_to_db_records(seasonal_data, season)
                
                # Bulk insert records
                if records:
                    logger.info(f"Inserting {len(records)} seasonal records for season {season}")
                    session.bulk_save_objects(records)
                    session.commit()
                    logger.info(f"Successfully inserted season {season} seasonal data")
                
            except Exception as e:
                logger.error(f"Error processing season {season}: {e}")
                session.rollback()
                continue
        
        logger.info("Seasonal stats loading completed")
        
    except Exception as e:
        logger.error(f"Error in load_seasonal_stats: {e}")
        session.rollback()
        raise
    finally:
        session.close()


def load_from_api(season):
    """Load seasonal data from nfl_data_py API."""
    logger.info(f"Downloading seasonal data from API for {season}")
    return nfl.import_seasonal_data([season])


def calculate_from_weekly_data(session, season):
    """Calculate seasonal totals from weekly data in database."""
    logger.info(f"Calculating seasonal data from weekly database records for {season}")
    
    # Query weekly data and aggregate by player
    query = session.query(
        NFLWeeklyStats.player_id,
        NFLWeeklyStats.player_name,
        NFLWeeklyStats.player_display_name,
        NFLWeeklyStats.position,
        NFLWeeklyStats.position_group,
        func.max(NFLWeeklyStats.team).label('team'),  # Most recent team
        func.count(NFLWeeklyStats.week).label('games_played'),
        
        # Passing totals
        func.sum(NFLWeeklyStats.completions).label('completions'),
        func.sum(NFLWeeklyStats.attempts).label('attempts'),
        func.sum(NFLWeeklyStats.passing_yards).label('passing_yards'),
        func.sum(NFLWeeklyStats.passing_tds).label('passing_tds'),
        func.sum(NFLWeeklyStats.interceptions).label('interceptions'),
        func.sum(NFLWeeklyStats.sacks).label('sacks'),
        func.sum(NFLWeeklyStats.sack_yards).label('sack_yards'),
        func.sum(NFLWeeklyStats.passing_air_yards).label('passing_air_yards'),
        func.sum(NFLWeeklyStats.passing_yards_after_catch).label('passing_yards_after_catch'),
        func.sum(NFLWeeklyStats.passing_first_downs).label('passing_first_downs'),
        func.sum(NFLWeeklyStats.passing_epa).label('passing_epa'),
        func.sum(NFLWeeklyStats.passing_2pt_conversions).label('passing_2pt_conversions'),
        
        # Rushing totals
        func.sum(NFLWeeklyStats.carries).label('carries'),
        func.sum(NFLWeeklyStats.rushing_yards).label('rushing_yards'),
        func.sum(NFLWeeklyStats.rushing_tds).label('rushing_tds'),
        func.sum(NFLWeeklyStats.rushing_fumbles).label('rushing_fumbles'),
        func.sum(NFLWeeklyStats.rushing_fumbles_lost).label('rushing_fumbles_lost'),
        func.sum(NFLWeeklyStats.rushing_first_downs).label('rushing_first_downs'),
        func.sum(NFLWeeklyStats.rushing_epa).label('rushing_epa'),
        func.sum(NFLWeeklyStats.rushing_2pt_conversions).label('rushing_2pt_conversions'),
        
        # Receiving totals
        func.sum(NFLWeeklyStats.targets).label('targets'),
        func.sum(NFLWeeklyStats.receptions).label('receptions'),
        func.sum(NFLWeeklyStats.receiving_yards).label('receiving_yards'),
        func.sum(NFLWeeklyStats.receiving_tds).label('receiving_tds'),
        func.sum(NFLWeeklyStats.receiving_fumbles).label('receiving_fumbles'),
        func.sum(NFLWeeklyStats.receiving_fumbles_lost).label('receiving_fumbles_lost'),
        func.sum(NFLWeeklyStats.receiving_air_yards).label('receiving_air_yards'),
        func.sum(NFLWeeklyStats.receiving_yards_after_catch).label('receiving_yards_after_catch'),
        func.sum(NFLWeeklyStats.receiving_first_downs).label('receiving_first_downs'),
        func.sum(NFLWeeklyStats.receiving_epa).label('receiving_epa'),
        func.sum(NFLWeeklyStats.receiving_2pt_conversions).label('receiving_2pt_conversions'),
        
        # Special teams and fantasy
        func.sum(NFLWeeklyStats.special_teams_tds).label('special_teams_tds'),
        func.sum(NFLWeeklyStats.fantasy_points).label('fantasy_points'),
        func.sum(NFLWeeklyStats.fantasy_points_ppr).label('fantasy_points_ppr'),
        
        # Advanced metrics (averages)
        func.avg(NFLWeeklyStats.target_share).label('target_share'),
        func.avg(NFLWeeklyStats.air_yards_share).label('air_yards_share'),
        func.avg(NFLWeeklyStats.wopr).label('wopr')
    ).filter(
        NFLWeeklyStats.season == season
    ).group_by(
        NFLWeeklyStats.player_id,
        NFLWeeklyStats.player_name,
        NFLWeeklyStats.player_display_name,
        NFLWeeklyStats.position,
        NFLWeeklyStats.position_group
    ).all()
    
    # Convert to DataFrame
    df = pd.DataFrame([{
        'player_id': row.player_id,
        'player_name': row.player_name,
        'player_display_name': row.player_display_name,
        'position': row.position,
        'position_group': row.position_group,
        'team': row.team,
        'games_played': row.games_played,
        'completions': row.completions or 0,
        'attempts': row.attempts or 0,
        'passing_yards': row.passing_yards or 0,
        'passing_tds': row.passing_tds or 0,
        'interceptions': row.interceptions or 0,
        'sacks': row.sacks or 0,
        'sack_yards': row.sack_yards or 0,
        'passing_air_yards': row.passing_air_yards or 0,
        'passing_yards_after_catch': row.passing_yards_after_catch or 0,
        'passing_first_downs': row.passing_first_downs or 0,
        'passing_epa': row.passing_epa or 0,
        'passing_2pt_conversions': row.passing_2pt_conversions or 0,
        'carries': row.carries or 0,
        'rushing_yards': row.rushing_yards or 0,
        'rushing_tds': row.rushing_tds or 0,
        'rushing_fumbles': row.rushing_fumbles or 0,
        'rushing_fumbles_lost': row.rushing_fumbles_lost or 0,
        'rushing_first_downs': row.rushing_first_downs or 0,
        'rushing_epa': row.rushing_epa or 0,
        'rushing_2pt_conversions': row.rushing_2pt_conversions or 0,
        'targets': row.targets or 0,
        'receptions': row.receptions or 0,
        'receiving_yards': row.receiving_yards or 0,
        'receiving_tds': row.receiving_tds or 0,
        'receiving_fumbles': row.receiving_fumbles or 0,
        'receiving_fumbles_lost': row.receiving_fumbles_lost or 0,
        'receiving_air_yards': row.receiving_air_yards or 0,
        'receiving_yards_after_catch': row.receiving_yards_after_catch or 0,
        'receiving_first_downs': row.receiving_first_downs or 0,
        'receiving_epa': row.receiving_epa or 0,
        'receiving_2pt_conversions': row.receiving_2pt_conversions or 0,
        'special_teams_tds': row.special_teams_tds or 0,
        'fantasy_points': row.fantasy_points or 0,
        'fantasy_points_ppr': row.fantasy_points_ppr or 0,
        'target_share': row.target_share,
        'air_yards_share': row.air_yards_share,
        'wopr': row.wopr
    } for row in query])
    
    return df


def convert_to_db_records(df, season):
    """Convert DataFrame to NFLSeasonalStats database records."""
    records = []
    
    for _, row in df.iterrows():
        # Calculate efficiency metrics
        completion_pct = safe_divide(row.get('completions', 0), row.get('attempts', 0)) * 100
        yards_per_attempt = safe_divide(row.get('passing_yards', 0), row.get('attempts', 0))
        yards_per_completion = safe_divide(row.get('passing_yards', 0), row.get('completions', 0))
        yards_per_carry = safe_divide(row.get('rushing_yards', 0), row.get('carries', 0))
        catch_pct = safe_divide(row.get('receptions', 0), row.get('targets', 0)) * 100
        yards_per_target = safe_divide(row.get('receiving_yards', 0), row.get('targets', 0))
        yards_per_reception = safe_divide(row.get('receiving_yards', 0), row.get('receptions', 0))
        
        # Calculate fantasy points per game
        games_played = max(row.get('games_played', 1), 1)  # Avoid division by zero
        fantasy_ppg = safe_divide(row.get('fantasy_points', 0), games_played)
        fantasy_ppr_ppg = safe_divide(row.get('fantasy_points_ppr', 0), games_played)
        
        record = NFLSeasonalStats(
            player_id=str(row.get('player_id', '')),
            season=season,
            player_name=str(row.get('player_name', '')),
            player_display_name=str(row.get('player_display_name', '')),
            position=str(row.get('position', '')),
            position_group=str(row.get('position_group', '')),
            team=str(row.get('team', row.get('recent_team', ''))),
            games_played=int(row.get('games_played', 0)),
            season_type='REG',  # Default to regular season
            
            # Passing stats
            completions=safe_float(row.get('completions')),
            attempts=safe_float(row.get('attempts')),
            passing_yards=safe_float(row.get('passing_yards')),
            passing_tds=safe_float(row.get('passing_tds')),
            interceptions=safe_float(row.get('interceptions')),
            sacks=safe_float(row.get('sacks')),
            sack_yards=safe_float(row.get('sack_yards')),
            passing_air_yards=safe_float(row.get('passing_air_yards')),
            passing_yards_after_catch=safe_float(row.get('passing_yards_after_catch')),
            passing_first_downs=safe_float(row.get('passing_first_downs')),
            passing_epa=safe_float(row.get('passing_epa')),
            passing_2pt_conversions=safe_float(row.get('passing_2pt_conversions')),
            
            # Passing efficiency
            completion_percentage=completion_pct,
            yards_per_attempt=yards_per_attempt,
            yards_per_completion=yards_per_completion,
            
            # Rushing stats
            carries=safe_float(row.get('carries')),
            rushing_yards=safe_float(row.get('rushing_yards')),
            rushing_tds=safe_float(row.get('rushing_tds')),
            rushing_fumbles=safe_float(row.get('rushing_fumbles')),
            rushing_fumbles_lost=safe_float(row.get('rushing_fumbles_lost')),
            rushing_first_downs=safe_float(row.get('rushing_first_downs')),
            rushing_epa=safe_float(row.get('rushing_epa')),
            rushing_2pt_conversions=safe_float(row.get('rushing_2pt_conversions')),
            yards_per_carry=yards_per_carry,
            
            # Receiving stats
            targets=safe_float(row.get('targets')),
            receptions=safe_float(row.get('receptions')),
            receiving_yards=safe_float(row.get('receiving_yards')),
            receiving_tds=safe_float(row.get('receiving_tds')),
            receiving_fumbles=safe_float(row.get('receiving_fumbles')),
            receiving_fumbles_lost=safe_float(row.get('receiving_fumbles_lost')),
            receiving_air_yards=safe_float(row.get('receiving_air_yards')),
            receiving_yards_after_catch=safe_float(row.get('receiving_yards_after_catch')),
            receiving_first_downs=safe_float(row.get('receiving_first_downs')),
            receiving_epa=safe_float(row.get('receiving_epa')),
            receiving_2pt_conversions=safe_float(row.get('receiving_2pt_conversions')),
            
            # Receiving efficiency
            catch_percentage=catch_pct,
            yards_per_target=yards_per_target,
            yards_per_reception=yards_per_reception,
            
            # Special teams and fantasy
            special_teams_tds=safe_float(row.get('special_teams_tds')),
            fantasy_points=safe_float(row.get('fantasy_points')),
            fantasy_points_ppr=safe_float(row.get('fantasy_points_ppr')),
            
            # Advanced metrics
            target_share=safe_float(row.get('target_share')),
            air_yards_share=safe_float(row.get('air_yards_share')),
            wopr=safe_float(row.get('wopr')),
            
            # Per-game metrics
            fantasy_points_per_game=fantasy_ppg,
            fantasy_points_ppr_per_game=fantasy_ppr_ppg
        )
        records.append(record)
    
    return records


def safe_float(value):
    """Safely convert value to float, returning None for invalid values."""
    if pd.isna(value) or value == '' or value is None:
        return None
    try:
        return float(value)
    except (ValueError, TypeError):
        return None


def safe_divide(numerator, denominator):
    """Safely divide two numbers, returning 0 if denominator is 0."""
    if denominator == 0 or denominator is None:
        return 0
    return numerator / denominator


def get_seasonal_stats_summary():
    """Get summary of loaded seasonal stats data."""
    session = get_session()
    
    try:
        # Get total count
        total = session.query(NFLSeasonalStats).count()
        
        # Get count by season
        season_counts = session.query(
            NFLSeasonalStats.season,
            func.count(NFLSeasonalStats.player_id).label('count')
        ).group_by(NFLSeasonalStats.season).all()
        
        logger.info(f"Total seasonal stats records: {total}")
        for season, count in season_counts:
            logger.info(f"Season {season}: {count} records")
            
        return total, dict(season_counts)
        
    except Exception as e:
        logger.error(f"Error getting summary: {e}")
        return 0, {}
    finally:
        session.close()


if __name__ == "__main__":
    # Load seasonal data from API for last 10 years
    load_seasonal_stats(use_api=True)
    
    # Print summary
    get_seasonal_stats_summary()
