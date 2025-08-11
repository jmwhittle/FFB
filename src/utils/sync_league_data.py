"""
Sync your Sleeper league data to the database.
"""

import sys
import os
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from dotenv import load_dotenv
from api.sleeper_client import SleeperClient
from config.database import get_session_local
from src.models import League, User, Roster, RosterEntry
from datetime import datetime

# Load environment variables
load_dotenv()

def sync_league_data():
    """Sync your Sleeper league data to the database."""
    
    league_id = os.getenv('SLEEPER_LEAGUE_ID')
    if not league_id:
        print("❌ SLEEPER_LEAGUE_ID not found in environment variables!")
        return False
    
    print(f"🔄 Syncing Sleeper League Data")
    print(f"League ID: {league_id}")
    print("=" * 50)
    
    # Initialize client and database session
    client = SleeperClient()
    SessionLocal = get_session_local()
    session = SessionLocal()
    
    try:
        # 1. Sync League Information
        print("\n📋 Step 1: Syncing League Information")
        league_data = client.get_league(league_id)
        
        if not league_data:
            print("❌ Failed to retrieve league data")
            return False
        
        # Check if league already exists
        existing_league = session.query(League).filter(League.id == league_id).first()
        
        if existing_league:
            print(f"✅ League already exists, updating: {league_data.get('name')}")
            # Update existing league
            existing_league.name = league_data.get('name', '')
            existing_league.season = league_data.get('season', '2025')
            existing_league.status = league_data.get('status', '')
            existing_league.total_rosters = league_data.get('total_rosters', 0)
            existing_league.scoring_settings = league_data.get('scoring_settings', {})
            existing_league.roster_positions = league_data.get('roster_positions', [])
            existing_league.settings = league_data.get('settings', {})
            existing_league.updated_at = datetime.utcnow()
        else:
            print(f"✅ Creating new league: {league_data.get('name')}")
            # Create new league
            league = League(
                id=league_id,
                name=league_data.get('name', ''),
                season=league_data.get('season', '2025'),
                sport=league_data.get('sport', 'nfl'),
                status=league_data.get('status', ''),
                season_type=league_data.get('season_type', 'regular'),
                total_rosters=league_data.get('total_rosters', 0),
                scoring_settings=league_data.get('scoring_settings', {}),
                roster_positions=league_data.get('roster_positions', []),
                settings=league_data.get('settings', {})
            )
            session.add(league)
        
        # 2. Sync Users
        print("\n👥 Step 2: Syncing League Users")
        users_data = client.get_league_users(league_id)
        
        if users_data:
            print(f"✅ Found {len(users_data)} users")
            
            for user_data in users_data:
                user_id = user_data.get('user_id')
                username = user_data.get('username', '') or user_id  # Use user_id if username is empty
                display_name = user_data.get('display_name', '')
                
                if not user_id:
                    continue
                
                # Check if user exists
                existing_user = session.query(User).filter(User.id == user_id).first()
                
                if existing_user:
                    # Update existing user
                    existing_user.username = username
                    existing_user.display_name = display_name
                    existing_user.avatar = user_data.get('avatar', '')
                    existing_user.updated_at = datetime.utcnow()
                else:
                    # Create new user
                    user = User(
                        id=user_id,
                        username=username,
                        display_name=display_name,
                        avatar=user_data.get('avatar', '')
                    )
                    session.add(user)
                
                print(f"  ✅ User: {display_name} ({username})")
        
        # 3. Sync Rosters
        print("\n🏈 Step 3: Syncing League Rosters")
        rosters_data = client.get_league_rosters(league_id)
        
        if rosters_data:
            print(f"✅ Found {len(rosters_data)} rosters")
            
            for roster_data in rosters_data:
                roster_id = roster_data.get('roster_id')
                owner_id = roster_data.get('owner_id')
                
                if not roster_id:
                    continue
                
                # Check if roster exists
                existing_roster = session.query(Roster).filter(
                    Roster.roster_id == roster_id,
                    Roster.league_id == league_id
                ).first()
                
                if existing_roster:
                    # Update existing roster
                    existing_roster.owner_id = owner_id
                    existing_roster.roster_id = roster_id
                    existing_roster.settings = roster_data.get('settings', {})
                    existing_roster.metadata = roster_data.get('metadata', {})
                    existing_roster.updated_at = datetime.utcnow()
                else:
                    # Create new roster
                    roster = Roster(
                        roster_id=roster_id,
                        league_id=league_id,
                        owner_id=owner_id,
                        settings=roster_data.get('settings', {}),
                        metadata=roster_data.get('metadata', {})
                    )
                    session.add(roster)
                
                players = roster_data.get('players', [])
                print(f"  ✅ Roster {roster_id}: Owner {owner_id}, {len(players)} players")
        
        # Commit all changes
        session.commit()
        print(f"\n🎉 League sync completed successfully!")
        
        # Show summary
        print(f"\n📊 Database Summary:")
        league_count = session.query(League).filter(League.id == league_id).count()
        user_count = session.query(User).count()
        roster_count = session.query(Roster).filter(Roster.league_id == league_id).count()
        
        print(f"  Leagues: {league_count}")
        print(f"  Users: {user_count}")
        print(f"  Rosters: {roster_count}")
        
        return True
        
    except Exception as e:
        session.rollback()
        print(f"❌ Error syncing league data: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        session.close()

def show_league_summary():
    """Show a summary of your league data in the database."""
    
    league_id = os.getenv('SLEEPER_LEAGUE_ID')
    SessionLocal = get_session_local()
    session = SessionLocal()
    
    try:
        print(f"\n📋 Your League Summary")
        print("=" * 30)
        
        # Get league info
        league = session.query(League).filter(League.id == league_id).first()
        if league:
            print(f"League: {league.name}")
            print(f"Season: {league.season}")
            print(f"Status: {league.status}")
            print(f"Rosters: {league.total_rosters}")
        
        # Get users in this league via rosters
        rosters = session.query(Roster).filter(Roster.league_id == league_id).all()
        owner_ids = [r.owner_id for r in rosters if r.owner_id]
        
        users = session.query(User).filter(User.id.in_(owner_ids)).all()
        
        print(f"\nUsers ({len(users)}):")
        for user in users:
            print(f"  - {user.display_name} ({user.username})")
        
        print(f"\nRosters ({len(rosters)}):")
        for roster in rosters:
            owner = session.query(User).filter(User.id == roster.owner_id).first()
            owner_name = owner.display_name if owner else "Unknown"
            print(f"  - Roster {roster.id}: {owner_name}")
        
    except Exception as e:
        print(f"❌ Error showing summary: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    print("🏈 Sleeper League Database Sync")
    print("=" * 40)
    
    if sync_league_data():
        show_league_summary()
        
        print(f"\n🎯 Next Steps:")
        print(f"1. Your league is now in the database!")
        print(f"2. Run this script periodically to sync updates")
        print(f"3. Use the database for advanced analytics")
        print(f"4. Build reports and dashboards from your league data")
