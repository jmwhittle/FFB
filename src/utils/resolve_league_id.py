"""
Extract the correct Sleeper league ID from the invite link.
"""

import requests
import re
from urllib.parse import urlparse

def extract_league_id_from_url(sleeper_url):
    """
    Extract league ID from various Sleeper URL formats.
    
    Sleeper URLs can be:
    - https://sleeper.com/i/zE1z32J65M3oo (invite link)
    - https://sleeper.app/leagues/123456789 (direct league)
    """
    
    print(f"🔍 Analyzing Sleeper URL: {sleeper_url}")
    
    # Check if it's an invite link
    if '/i/' in sleeper_url:
        invite_code = sleeper_url.split('/i/')[-1]
        print(f"📧 Found invite code: {invite_code}")
        
        # Unfortunately, Sleeper doesn't provide a direct API to resolve invite codes
        # We need to try different approaches
        
        print("⚠️ Invite links can't be directly resolved via API")
        print("🔧 Possible solutions:")
        print("1. Join the league and get the league ID from the URL")
        print("2. Ask the league commissioner for the league ID")
        print("3. Use browser dev tools to inspect network requests")
        
        return None
    
    # Check if it's a direct league URL
    league_id_match = re.search(r'/leagues/(\d+)', sleeper_url)
    if league_id_match:
        league_id = league_id_match.group(1)
        print(f"✅ Found league ID: {league_id}")
        return league_id
    
    # Check if the URL itself is a league ID
    if sleeper_url.isdigit():
        print(f"✅ URL appears to be a league ID: {sleeper_url}")
        return sleeper_url
    
    print("❌ Could not extract league ID from URL")
    return None

def test_league_id(league_id):
    """Test if a league ID is valid."""
    if not league_id:
        return False
        
    api_url = f"https://api.sleeper.app/v1/league/{league_id}"
    print(f"🧪 Testing league ID: {league_id}")
    print(f"API URL: {api_url}")
    
    try:
        response = requests.get(api_url)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ League found!")
            print(f"   Name: {data.get('name', 'Unknown')}")
            print(f"   Season: {data.get('season', 'Unknown')}")
            print(f"   Status: {data.get('status', 'Unknown')}")
            return True
        else:
            print(f"❌ League ID invalid: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing league ID: {e}")
        return False

def find_league_alternatives():
    """Provide alternative methods to find the league ID."""
    
    print("\n🎯 How to Find Your Sleeper League ID:")
    print("=" * 50)
    
    print("\n📱 Method 1: From the Sleeper App/Website")
    print("1. Open your league in the Sleeper app or website")
    print("2. Look at the URL in your browser:")
    print("   - Should be like: https://sleeper.app/leagues/123456789")
    print("   - The number at the end is your league ID")
    
    print("\n🌐 Method 2: Browser Developer Tools")
    print("1. Open your league page in a web browser")
    print("2. Press F12 to open developer tools")
    print("3. Go to Network tab and refresh the page")
    print("4. Look for API calls to sleeper.app containing your league data")
    
    print("\n👥 Method 3: Ask League Commissioner")
    print("1. Ask your league commissioner to:")
    print("2. Go to League Settings in the Sleeper app")
    print("3. Share the direct league URL (not invite link)")
    
    print("\n🔗 Method 4: Convert Invite Link")
    print("1. Click on your invite link to join/view the league")
    print("2. Once on the league page, copy the URL from browser")
    print("3. The URL should contain the actual league ID")

if __name__ == "__main__":
    print("🏈 Sleeper League ID Resolver")
    print("=" * 40)
    
    # Test the URL we have
    sleeper_url = "https://sleeper.com/i/zE1z32J65M3oo"
    league_id = extract_league_id_from_url(sleeper_url)
    
    if league_id:
        test_league_id(league_id)
    else:
        find_league_alternatives()
        
        # Let's also try some common patterns that might work
        print("\n🔄 Trying Alternative Approaches...")
        
        # Sometimes the invite code can be decoded
        invite_code = "zE1z32J65M3oo"
        print(f"Invite code: {invite_code}")
        
        # Try to find any pattern
        possible_ids = [
            "1126080302831382528",  # The ID you originally had
            # Add more if you have them
        ]
        
        print("\n🧪 Testing possible league IDs...")
        for pid in possible_ids:
            if test_league_id(pid):
                print(f"\n✅ Working league ID found: {pid}")
                print(f"💡 Update your .env file with: SLEEPER_LEAGUE_ID={pid}")
                break
