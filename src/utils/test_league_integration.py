"""
Test Sleeper API integration with your specific league.
"""

import sys
import os
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

import requests
from dotenv import load_dotenv
import sys
import os
# Add the project root to path so we can import from api directory
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)
from api.sleeper_client import SleeperClient
import json

# Load environment variables
load_dotenv()

def test_league_data():
    """Test retrieving data for your specific league."""
    
    # Get league ID from environment
    league_id = os.getenv('SLEEPER_LEAGUE_ID')
    league_url = os.getenv('SLEEPER_LEAGUE_URL')
    
    print(f"🏈 Testing Sleeper League Data Retrieval")
    print(f"League ID: {league_id}")
    print(f"League URL: {league_url}")
    print("=" * 50)
    
    if not league_id:
        print("❌ SLEEPER_LEAGUE_ID not found in environment variables!")
        return False
    
    try:
        # Initialize Sleeper client
        client = SleeperClient()
        
        # Test 1: Get League Information
        print("\n📋 Test 1: League Information")
        league_info = client.get_league(league_id)
        
        if league_info:
            print(f"✅ League Name: {league_info.get('name', 'Unknown')}")
            print(f"✅ Season: {league_info.get('season', 'Unknown')}")
            print(f"✅ Sport: {league_info.get('sport', 'Unknown')}")
            print(f"✅ Status: {league_info.get('status', 'Unknown')}")
            print(f"✅ Total Rosters: {league_info.get('total_rosters', 'Unknown')}")
            print(f"✅ Scoring Type: {league_info.get('scoring_settings', {}).keys()}")
        else:
            print("❌ Failed to retrieve league information")
            return False
        
        # Test 2: Get Rosters
        print("\n👥 Test 2: League Rosters")
        rosters = client.get_league_rosters(league_id)
        
        if rosters:
            print(f"✅ Found {len(rosters)} rosters in the league")
            for i, roster in enumerate(rosters[:3]):  # Show first 3 rosters
                owner_id = roster.get('owner_id', 'Unknown')
                players = roster.get('players', [])
                print(f"  Roster {i+1}: Owner {owner_id}, {len(players)} players")
        else:
            print("❌ Failed to retrieve rosters")
        
        # Test 3: Get Users
        print("\n🔍 Test 3: League Users")
        users = client.get_league_users(league_id)
        
        if users:
            print(f"✅ Found {len(users)} users in the league")
            for user in users[:3]:  # Show first 3 users
                username = user.get('username', 'Unknown')
                display_name = user.get('display_name', 'Unknown')
                print(f"  User: {username} ({display_name})")
        else:
            print("❌ Failed to retrieve users")
        
        # Test 4: Get Current Week Matchups (if season is active)
        print("\n⚔️ Test 4: Current Matchups")
        try:
            # Try to get week 1 matchups
            matchups = client.get_league_matchups(league_id, 1)
            
            if matchups:
                print(f"✅ Found {len(matchups)} matchups for week 1")
                for matchup in matchups[:2]:  # Show first 2 matchups
                    matchup_id = matchup.get('matchup_id', 'Unknown')
                    points = matchup.get('points', 0)
                    roster_id = matchup.get('roster_id', 'Unknown')
                    print(f"  Matchup {matchup_id}: Roster {roster_id}, {points} points")
            else:
                print("❌ No matchups found (may be offseason)")
        except Exception as e:
            print(f"⚠️ Matchups not available: {e}")
        
        print(f"\n🎉 League data retrieval test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing league data: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_direct_api():
    """Test direct API call to verify league ID is correct."""
    league_id = os.getenv('SLEEPER_LEAGUE_ID')
    api_base = os.getenv('SLEEPER_API_BASE_URL')
    
    print(f"\n🔧 Direct API Test")
    print(f"Making direct API call to: {api_base}/league/{league_id}")
    
    try:
        response = requests.get(f"{api_base}/league/{league_id}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Direct API call successful!")
            print(f"League Name: {data.get('name', 'Unknown')}")
            print(f"Season: {data.get('season', 'Unknown')}")
            return True
        else:
            print(f"❌ Direct API call failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Direct API error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting Sleeper League Integration Test")
    
    # Test direct API first
    if test_direct_api():
        # Then test through our client
        test_league_data()
    else:
        print("❌ Direct API test failed, check your league ID")
