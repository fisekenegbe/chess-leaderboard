import requests
import time
import json
from datetime import datetime, timezone

# 1. Configuration
CLUB_URL_ID = "uniben-chess-enthusiasts"
headers = {
    "User-Agent": "ClubLeaderboard/1.0 (contact: fisekenegbe@gmail.com)"
}

def get_club_leaderboard():
    print(f"Fetching roster for club: {CLUB_URL_ID}...")
    
    # 2. Get the Club Roster with Debugging
    members_url = f"https://api.chess.com/pub/club/{CLUB_URL_ID}/members"
    response = requests.get(members_url, headers=headers)
    
    print(f"API Status Code: {response.status_code}")
    
    try:
        members_data = response.json()
        if response.status_code != 200:
            print(f"Error from Chess.com: {members_data}")
            return
    except Exception as e:
        print(f"Failed to read JSON. Raw text: {response.text}")
        members_data = {}

    all_members = (
        members_data.get("weekly", []) + 
        members_data.get("monthly", []) + 
        members_data.get("all_time", [])
    )

    if not all_members:
        print("Warning: No members found in the API response.")
        return

    players = []

    # 3. Fetch data for each player 
    for member in all_members: 
        username = member["username"]
        print(f"Extracting data for {username}...")
        
        stats_url = f"https://api.chess.com/pub/player/{username}/stats"
        profile_url = f"https://api.chess.com/pub/player/{username}"
        
        try:
            # Fetch Stats (Elo)
            stats_data = requests.get(stats_url, headers=headers).json()
            rapid_elo = 0
            if "chess_rapid" in stats_data and "last" in stats_data["chess_rapid"]:
                rapid_elo = stats_data["chess_rapid"]["last"]["rating"]
                
            time.sleep(0.3) # Critical throttle to avoid IP ban
            
            # Fetch Profile (Avatar)
            profile_data = requests.get(profile_url, headers=headers).json()
            avatar = profile_data.get("avatar", "https://www.chess.com/bundles/web/images/user-image.svg")
            
            time.sleep(0.3) # Critical throttle
            
            # Only add the player if they have actually played Rapid chess
            if rapid_elo > 0:
                players.append({
                    "username": username,
                    "rapid_elo": rapid_elo,
                    "avatar": avatar
                })
                
        except Exception as e:
            print(f"Failed to extract {username}: {e}")

    # 4. Sort the list from highest Elo to lowest
    players.sort(key=lambda x: x["rapid_elo"], reverse=True)

    # 5. Package the data for the JavaScript UI
    output_data = {
        "timestamp": datetime.now(timezone.utc).strftime("%I:%M %p UTC"),
        "players": players
    }

    # 6. Save directly to leaderboard.json
    with open("leaderboard.json", "w") as outfile:
        json.dump(output_data, outfile, indent=4)
        
    print(f"Success: leaderboard.json has been generated with {len(players)} players.")

if __name__ == "__main__":
    get_club_leaderboard()
