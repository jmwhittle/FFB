"""
Data synchronization service for fetching and storing Sleeper data.
"""

from datetime import datetime
from typing import Dict, List, Optional
from sqlalchemy.orm import Session
from config.database import get_db
from api.sleeper_client import SleeperClient
from src.models import User, League, Player, Roster, RosterEntry, Matchup, PlayerStats, Transaction


class DataSyncService:
    """Service for synchronizing data between Sleeper API and local database."""
    
    def __init__(self):
        self.client = SleeperClient()
    
    def sync_nfl_players(self, db: Session) -> int:
        """Sync all NFL players from Sleeper API."""
        print("Syncing NFL players...")
        
        players_data = self.client.get_nfl_players()
        if not players_data:
            print("Failed to fetch NFL players")
            return 0
        
        count = 0
        for player_id, player_info in players_data.items():
            try:
                # Check if player exists
                existing_player = db.query(Player).filter_by(id=player_id).first()
                
                if existing_player:
                    # Update existing player
                    for key, value in player_info.items():
                        if hasattr(existing_player, key):
                            setattr(existing_player, key, value)
                    existing_player.updated_at = datetime.utcnow()
                else:
                    # Create new player
                    player = Player(
                        id=player_id,
                        player_id=player_info.get('player_id'),
                        first_name=player_info.get('first_name'),
                        last_name=player_info.get('last_name'),
                        full_name=player_info.get('full_name'),
                        position=player_info.get('position'),
                        team=player_info.get('team'),
                        college=player_info.get('college'),
                        height=player_info.get('height'),
                        weight=player_info.get('weight'),
                        age=player_info.get('age'),
                        years_exp=player_info.get('years_exp'),
                        active=player_info.get('active', True),
                        injury_status=player_info.get('injury_status'),
                        fantasy_data_id=player_info.get('fantasy_data_id'),
                        rotowire_id=player_info.get('rotowire_id'),
                        rotoworld_id=player_info.get('rotoworld_id')
                    )
                    db.add(player)
                
                count += 1
                
                if count % 100 == 0:
                    print(f"Processed {count} players...")
                    db.commit()
                    
            except Exception as e:
                print(f"Error processing player {player_id}: {e}")
                continue
        
        db.commit()
        print(f"Synced {count} NFL players")
        return count
    
    def sync_user_leagues(self, username: str, db: Session) -> List[str]:
        """Sync leagues for a specific user."""
        print(f"Syncing leagues for user: {username}")
        
        # Get user info
        user_data = self.client.get_user(username)
        if not user_data:
            print(f"User {username} not found")
            return []
        
        user_id = user_data['user_id']
        
        # Sync user
        existing_user = db.query(User).filter_by(id=user_id).first()
        if not existing_user:
            user = User(
                id=user_id,
                username=user_data.get('username'),
                display_name=user_data.get('display_name'),
                avatar=user_data.get('avatar')
            )
            db.add(user)
            db.commit()
        
        # Get user's leagues
        leagues_data = self.client.get_user_leagues(user_id)
        if not leagues_data:
            print("No leagues found for user")
            return []
        
        league_ids = []
        for league_data in leagues_data:
            try:
                league_id = league_data['league_id']
                league_ids.append(league_id)
                
                # Check if league exists
                existing_league = db.query(League).filter_by(id=league_id).first()
                
                if not existing_league:
                    league = League(
                        id=league_id,
                        name=league_data.get('name'),
                        season=league_data.get('season'),
                        sport=league_data.get('sport', 'nfl'),
                        status=league_data.get('status'),
                        season_type=league_data.get('season_type'),
                        total_rosters=league_data.get('total_rosters'),
                        scoring_settings=league_data.get('scoring_settings'),
                        roster_positions=league_data.get('roster_positions'),
                        settings=league_data.get('settings')
                    )
                    db.add(league)
                
            except Exception as e:
                print(f"Error processing league {league_data.get('league_id')}: {e}")
                continue
        
        db.commit()
        print(f"Synced {len(league_ids)} leagues")
        return league_ids
    
    def sync_league_rosters(self, league_id: str, db: Session) -> int:
        """Sync rosters for a specific league."""
        print(f"Syncing rosters for league: {league_id}")
        
        rosters_data = self.client.get_league_rosters(league_id)
        if not rosters_data:
            print("No rosters found for league")
            return 0
        
        count = 0
        for roster_data in rosters_data:
            try:
                # Check if roster exists
                existing_roster = db.query(Roster).filter_by(
                    league_id=league_id,
                    roster_id=roster_data['roster_id']
                ).first()
                
                if not existing_roster:
                    roster = Roster(
                        roster_id=roster_data['roster_id'],
                        league_id=league_id,
                        owner_id=roster_data.get('owner_id'),
                        co_owners=roster_data.get('co_owners'),
                        wins=roster_data.get('settings', {}).get('wins', 0),
                        losses=roster_data.get('settings', {}).get('losses', 0),
                        ties=roster_data.get('settings', {}).get('ties', 0),
                        waiver_position=roster_data.get('settings', {}).get('waiver_position'),
                        waiver_budget_used=roster_data.get('settings', {}).get('waiver_budget_used', 0),
                        total_moves=roster_data.get('settings', {}).get('total_moves', 0),
                        settings=roster_data.get('settings')
                    )
                    db.add(roster)
                    count += 1
                
            except Exception as e:
                print(f"Error processing roster {roster_data.get('roster_id')}: {e}")
                continue
        
        db.commit()
        print(f"Synced {count} rosters")
        return count
    
    def sync_league_matchups(self, league_id: str, week: int, db: Session) -> int:
        """Sync matchups for a specific league and week."""
        print(f"Syncing matchups for league: {league_id}, week: {week}")
        
        matchups_data = self.client.get_league_matchups(league_id, week)
        if not matchups_data:
            print("No matchups found")
            return 0
        
        count = 0
        for matchup_data in matchups_data:
            try:
                # Check if matchup exists
                existing_matchup = db.query(Matchup).filter_by(
                    league_id=league_id,
                    roster_id=matchup_data['roster_id'],
                    week=week
                ).first()
                
                if not existing_matchup:
                    matchup = Matchup(
                        matchup_id=matchup_data.get('matchup_id'),
                        league_id=league_id,
                        roster_id=matchup_data['roster_id'],
                        week=week,
                        points=matchup_data.get('points'),
                        starters=matchup_data.get('starters'),
                        starters_points=matchup_data.get('starters_points'),
                        players=matchup_data.get('players'),
                        players_points=matchup_data.get('players_points'),
                        custom_points=matchup_data.get('custom_points')
                    )
                    db.add(matchup)
                    count += 1
                
            except Exception as e:
                print(f"Error processing matchup: {e}")
                continue
        
        db.commit()
        print(f"Synced {count} matchups")
        return count
    
    def full_sync(self, username: str) -> Dict[str, int]:
        """Perform a full data sync for a user."""
        print("Starting full data sync...")
        
        results = {
            'players': 0,
            'leagues': 0,
            'rosters': 0,
            'matchups': 0
        }
        
        db = next(get_db())
        
        try:
            # Sync NFL players (this might take a while)
            results['players'] = self.sync_nfl_players(db)
            
            # Sync user's leagues
            league_ids = self.sync_user_leagues(username, db)
            results['leagues'] = len(league_ids)
            
            # Sync rosters for each league
            total_rosters = 0
            total_matchups = 0
            
            for league_id in league_ids:
                rosters = self.sync_league_rosters(league_id, db)
                total_rosters += rosters
                
                # Sync current week matchups
                nfl_state = self.client.get_nfl_state()
                if nfl_state and nfl_state.get('week'):
                    current_week = nfl_state['week']
                    matchups = self.sync_league_matchups(league_id, current_week, db)
                    total_matchups += matchups
            
            results['rosters'] = total_rosters
            results['matchups'] = total_matchups
            
            print("Full sync completed!")
            print(f"Results: {results}")
            
        except Exception as e:
            print(f"Error during full sync: {e}")
            db.rollback()
        finally:
            db.close()
        
        return results


# CLI helper function
def run_sync(username: str):
    """CLI helper to run data sync."""
    service = DataSyncService()
    return service.full_sync(username)


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        username = sys.argv[1]
        run_sync(username)
    else:
        print("Usage: python -m src.services.data_sync <sleeper_username>")
