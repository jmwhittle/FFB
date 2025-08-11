"""
Comprehensive test for Sleeper league ID resolution and data retrieval.
"""

import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_multiple_formats(league_identifier):
    """Test league identifier in multiple formats."""
    
    print(f"🔍 Testing league identifier: {league_identifier}")
    print("=" * 50)
    
    # Format 1: Direct league ID
    print("\n📋 Test 1: Direct League ID")
    api_url_1 = f"https://api.sleeper.app/v1/league/{league_identifier}"
    try:
        response = requests.get(api_url_1)
        print(f"URL: {api_url_1}")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ SUCCESS! League found:")
            print(f"   Name: {data.get('name', 'Unknown')}")
            print(f"   Season: {data.get('season', 'Unknown')}")
            print(f"   Status: {data.get('status', 'Unknown')}")
            print(f"   Total Rosters: {data.get('total_rosters', 'Unknown')}")
            return league_identifier, data
        else:
            print(f"❌ Failed: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Format 2: Try as user ID (sometimes league identifiers are user-based)
    print("\n👤 Test 2: User-based lookup")
    api_url_2 = f"https://api.sleeper.app/v1/user/{league_identifier}"
    try:
        response = requests.get(api_url_2)
        print(f"URL: {api_url_2}")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            user_data = response.json()
            print(f"✅ User found: {user_data.get('display_name', 'Unknown')}")
            
            # Try to get leagues for this user
            user_id = user_data.get('user_id')
            if user_id:
                leagues_url = f"https://api.sleeper.app/v1/user/{user_id}/leagues/nfl/2024"
                leagues_response = requests.get(leagues_url)
                
                if leagues_response.status_code == 200:
                    leagues = leagues_response.json()
                    print(f"✅ Found {len(leagues)} leagues for user:")
                    
                    for i, league in enumerate(leagues):
                        league_id = league.get('league_id')
                        league_name = league.get('name', 'Unknown')
                        print(f"   League {i+1}: {league_name} (ID: {league_id})")
                    
                    return leagues[0].get('league_id') if leagues else None, leagues[0] if leagues else None
                    
        else:
            print(f"❌ Failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Format 3: Try different API endpoints
    print("\n🔄 Test 3: Alternative endpoints")
    alternative_endpoints = [
        f"https://api.sleeper.app/v1/league/{league_identifier}/users",
        f"https://api.sleeper.app/v1/league/{league_identifier}/rosters",
    ]
    
    for endpoint in alternative_endpoints:
        try:
            response = requests.get(endpoint)
            print(f"URL: {endpoint}")
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                print(f"✅ Endpoint responds! Data length: {len(response.text)}")
                return league_identifier, response.json()
            else:
                print(f"❌ Failed: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    return None, None

def get_sample_league_data():
    """Get a sample public league for testing our integration."""
    
    print("\n🧪 Testing with sample public league")
    print("=" * 40)
    
    # Use a known working league ID for testing
    sample_league_id = "784462448978907136"  # A public league
    
    try:
        response = requests.get(f"https://api.sleeper.app/v1/league/{sample_league_id}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Sample league test successful!")
            print(f"   Name: {data.get('name', 'Unknown')}")
            print(f"   Season: {data.get('season', 'Unknown')}")
            
            # Test getting rosters
            rosters_response = requests.get(f"https://api.sleeper.app/v1/league/{sample_league_id}/rosters")
            if rosters_response.status_code == 200:
                rosters = rosters_response.json()
                print(f"   Rosters: {len(rosters)} found")
                
            # Test getting users  
            users_response = requests.get(f"https://api.sleeper.app/v1/league/{sample_league_id}/users")
            if users_response.status_code == 200:
                users = users_response.json()
                print(f"   Users: {len(users)} found")
                
            print(f"\n💡 Our Sleeper integration is working correctly!")
            print(f"   Issue is likely with the league identifier format")
            
            return True
            
    except Exception as e:
        print(f"❌ Sample test failed: {e}")
        return False

def suggest_solutions():
    """Provide solutions for finding the correct league ID."""
    
    print("\n🎯 Solutions to Find Your League ID:")
    print("=" * 45)
    
    print("\n📱 Method 1: Use Sleeper App")
    print("1. Open Sleeper app on your phone")
    print("2. Go to your league")
    print("3. Tap 'League Settings' or 'Settings'")
    print("4. Look for 'League ID' or 'Share League'")
    print("5. The League ID should be a long number like: 784462448978907136")
    
    print("\n🌐 Method 2: Browser Method")
    print("1. Open https://sleeper.com/i/zE1z32J65M3oo in your browser")
    print("2. Join/view the league (should redirect to actual league page)")
    print("3. Look at the URL after redirect:")
    print("   - Should be like: https://sleeper.app/leagues/[LEAGUE_ID]")
    print("   - Copy the number after /leagues/")
    
    print("\n🔧 Method 3: API Discovery")
    print("1. If you know your Sleeper username, we can find your leagues")
    print("2. Provide your Sleeper username and we'll search for your leagues")
    
    print("\n📞 Method 4: Ask Commissioner")
    print("1. Ask your league commissioner for the numeric League ID")
    print("2. It should be a 15-18 digit number")

if __name__ == "__main__":
    print("🏈 Sleeper League Resolution Test")
    print("=" * 40)
    
    # Get the league identifier from environment
    league_id = os.getenv('SLEEPER_LEAGUE_ID', 'zE1z32J65M3oo')
    
    # Test the identifier
    working_id, league_data = test_multiple_formats(league_id)
    
    if working_id and league_data:
        print(f"\n🎉 SUCCESS! Your league ID is: {working_id}")
        print(f"💡 Update your .env file with: SLEEPER_LEAGUE_ID={working_id}")
    else:
        print(f"\n❌ Could not resolve league identifier: {league_id}")
        
        # Test our integration with a known working league
        if get_sample_league_data():
            suggest_solutions()
        else:
            print("❌ Basic Sleeper API integration failed")
    
    print(f"\n📝 Next Steps:")
    print(f"1. Find your correct numeric League ID")
    print(f"2. Update SLEEPER_LEAGUE_ID in your .env file")
    print(f"3. Run the league integration test again")
