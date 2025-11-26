from datetime import datetime, timedelta
from typing import List
import httpx

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel


app = FastAPI()

# Mount static files (CSS, JS, images)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Configure templates directory
templates = Jinja2Templates(directory="templates")


class Match(BaseModel):
    id: int
    team1: str
    team2: str
    match_format: str
    start_time: str
    venue: str
    status: str
    score_summary: str
    man_of_match: str = "-"
    man_of_series: str = "-"
    best_batsman: str = "-"
    best_bowler: str = "-"
    series_name: str = "-"
    match_number: str = "-"
    toss_winner: str = "-"
    toss_decision: str = "-"
    umpires: str = "-"
    match_referee: str = "-"
    match_url: str = "-"
    scorecard_url: str = "-"
    detailed_score: dict = {}  # Full scorecard data


# Fetch real cricket match data from cricapi.com (free tier)
# You can get a free API key from: https://www.cricapi.com/
# For now, this uses a demo approach. Replace with your actual API key.
CRICKET_API_KEY = "48e8c9c5-77c8-45f7-bda6-f5555f4c9dc2"  # Replace with actual key from cricapi.com
# Note: CricAPI v1 endpoint - make sure the URL is correct
CRICKET_API_URL = "https://api.cricapi.com/v1/currentMatches"


async def get_last_24h_matches() -> List[Match]:
    """
    Fetch all international cricket matches (Test, ODI, T20I).
    Includes in-progress, completed, and upcoming matches.
    Falls back to empty list if API fails.
    """
    matches = []
    
    try:
        # Fetch current matches from cricket API
        print(f"Fetching from: {CRICKET_API_URL}")
        print(f"Using API Key: {CRICKET_API_KEY[:10]}...")
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                CRICKET_API_URL,
                params={"apikey": CRICKET_API_KEY}
            )
            
            print(f"Response Status: {response.status_code}")
            
            if response.status_code != 200:
                print(f"API Error: {response.status_code}")
                print(f"Response Text: {response.text}")
                return matches
            
            data = response.json()
            print(f"API Response Keys: {data.keys()}")
            
            # Check for API errors
            if "error" in data or "statusCode" in data:
                print(f"API Error Response: {data}")
                return matches
            
            if not data.get("data"):
                print(f"No data returned from API. Full response: {data}")
                return matches
            
            print(f"Found {len(data.get('data', []))} matches from API")
            
            now = datetime.utcnow()
            
            # Process each match from the API
            for idx, match_data in enumerate(data.get("data", [])):
                # Only include international matches (Test, ODI, T20I)
                match_type = match_data.get("matchType", "").lower()
                if match_type not in ["test", "odi", "t20", "t20i"]:
                    continue
                
                # FILTER: Show ONLY International Cricket (Men's & Women's)
                # Exclude ALL domestic leagues
                
                # Get match details for filtering
                match_name = match_data.get("name", "").lower()
                series_name = match_data.get("series", "").lower()
                teams = match_data.get("teams", [])
                team1_lower = teams[0].lower() if len(teams) > 0 else ""
                team2_lower = teams[1].lower() if len(teams) > 1 else ""
                
                # Skip ALL domestic leagues
                domestic_keywords = [
                    "ipl", "bbl", "psl", "cpl", "bpl", "lpl", "msl", "t10", "wpl",
                    "premier league", "super league", "bash", "vitality",
                    "hundred", "county", "shield", "trophy", "ranji",
                    "duleep", "vijay hazare", "syed mushtaq", "plunket",
                    "hurricanes", "sixers", "thunder", "scorchers", "renegades",
                    "strikers", "stars", "heat", "royals", "knights", "capitals",
                    "kings", "titans", "giants", "riders", "warriors"
                ]
                
                # Australian state teams
                australian_states = [
                    "south australia", "western australia", "new south wales", 
                    "queensland", "victoria", "tasmania", "act meteor", "cricket australia xi"
                ]
                
                # Indian state/regional teams
                indian_states = [
                    "mumbai", "delhi", "karnataka", "tamil nadu", "bengal",
                    "punjab", "maharashtra", "gujarat", "rajasthan", "haryana",
                    "uttar pradesh", "madhya pradesh", "kerala", "hyderabad",
                    "baroda", "saurashtra", "vidarbha", "andhra", "jharkhand"
                ]
                
                # Other regional/state teams
                other_regional = [
                    "northern districts", "central districts", "auckland", "canterbury",
                    "wellington", "otago", "dolphins", "lions", "titans", "warriors",
                    "cobras", "knights", "cape cobras", "easterns", "northerns"
                ]
                
                # Combine all state/regional team names
                state_teams = australian_states + indian_states + other_regional
                
                # Check if either team is a state/regional team
                is_state_match = any(state in team1_lower or state in team2_lower 
                                    for state in state_teams)
                
                # Check for domestic league keywords
                is_domestic = any(keyword in match_name or keyword in series_name 
                                 for keyword in domestic_keywords)
                
                # Skip if domestic or state match
                if is_domestic or is_state_match:
                    continue
                
                # Parse match start time
                date_str = match_data.get("dateTimeGMT", "")
                try:
                    match_time = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S")
                except:
                    match_time = now
                
                # Extract team names
                teams = match_data.get("teams", [])
                team1 = teams[0] if len(teams) > 0 else "Team 1"
                team2 = teams[1] if len(teams) > 1 else "Team 2"
                
                # Determine status
                status = match_data.get("status", "Scheduled")
                if "won" in status.lower():
                    match_status = "Completed"
                elif match_data.get("matchStarted", False):
                    match_status = "In Progress"
                else:
                    match_status = "Scheduled"
                
                # Get score summary and detailed score
                score = match_data.get("score", [])
                detailed_score = {}
                
                if score:
                    score_summary = " | ".join([f"{s.get('inning', '')}: {s.get('r', 0)}/{s.get('w', 0)} ({s.get('o', 0)} ov)" for s in score])
                    # Store detailed score for expandable view
                    detailed_score = {
                        "innings": score,
                        "scorecard": match_data.get("scorecard", []),
                        "teamInfo": match_data.get("teamInfo", [])
                    }
                else:
                    score_summary = status if status else "-"
                
                # Extract player awards/stats (try multiple field names)
                # Different APIs use different field names
                man_of_match = (
                    match_data.get("manOfTheMatch") or 
                    match_data.get("mom") or 
                    match_data.get("playerOfTheMatch") or 
                    "-"
                )
                
                man_of_series = (
                    match_data.get("manOfTheSeries") or 
                    match_data.get("mos") or 
                    match_data.get("playerOfTheSeries") or 
                    "-"
                )
                
                # Try to extract best batsman and bowler from match data
                best_batsman = "-"
                best_bowler = "-"
                
                # Check multiple possible locations for player stats
                if "players" in match_data:
                    players = match_data.get("players", {})
                    best_batsman = (
                        players.get("bestBatsman") or 
                        players.get("topBatsman") or 
                        "-"
                    )
                    best_bowler = (
                        players.get("bestBowler") or 
                        players.get("topBowler") or 
                        "-"
                    )
                
                # Alternative: Check score data for top performers
                if best_batsman == "-" or best_bowler == "-":
                    score_data = match_data.get("score", [])
                    if score_data and isinstance(score_data, list):
                        for innings in score_data:
                            if isinstance(innings, dict):
                                if best_batsman == "-" and "topBatsman" in innings:
                                    best_batsman = innings.get("topBatsman", "-")
                                if best_bowler == "-" and "topBowler" in innings:
                                    best_bowler = innings.get("topBowler", "-")
                
                # Extract additional interesting information
                series_name = match_data.get("series", "-")
                match_number = match_data.get("matchNumber", "-")
                
                # Toss information
                toss_winner = match_data.get("tossWinner", "-")
                toss_choice = match_data.get("tossChoice", "-")
                toss_decision = f"{toss_choice}" if toss_choice != "-" else "-"
                
                # Officials
                umpires_list = match_data.get("umpires", [])
                umpires = ", ".join(umpires_list) if umpires_list else "-"
                match_referee = match_data.get("referee", "-")
                
                # Extract match URLs for scorecard
                # Try multiple possible field names from API
                match_id = match_data.get("id", "")
                match_url = (
                    match_data.get("matchUrl") or 
                    match_data.get("url") or 
                    match_data.get("link") or
                    ""
                )
                scorecard_url = (
                    match_data.get("scorecardUrl") or 
                    match_data.get("scorecard") or
                    ""
                )
                
                # If API provides match ID, try to construct ESPN Cricinfo URL
                if not scorecard_url and match_id:
                    # ESPN Cricinfo URL format: /series/[series-id]/[match-name]-[match-id]/full-scorecard
                    # Since we don't have series ID, use the match ID in a generic format
                    scorecard_url = f"https://www.espncricinfo.com/series/0/scorecard/{match_id}"
                
                # If still no URL, construct based on match name
                if not scorecard_url:
                    # Create a clean match identifier
                    team1_slug = team1.lower().replace(" ", "-")
                    team2_slug = team2.lower().replace(" ", "-")
                    date_slug = match_time.strftime("%Y-%m-%d")
                    format_slug = match_type.lower()
                    
                    # Use Cricbuzz as alternative (more reliable URL structure)
                    scorecard_url = f"https://www.cricbuzz.com/cricket-scores/{team1_slug}-vs-{team2_slug}-{format_slug}-{date_slug}"
                
                # Use scorecard URL for match URL if not provided
                if not match_url:
                    match_url = scorecard_url
                
                matches.append(Match(
                    id=idx + 1,
                    team1=team1,
                    team2=team2,
                    match_format=match_type.upper(),
                    start_time=match_time.strftime("%Y-%m-%d %H:%M UTC"),
                    venue=match_data.get("venue", "TBD"),
                    status=match_status,
                    score_summary=score_summary,
                    man_of_match=man_of_match,
                    man_of_series=man_of_series,
                    best_batsman=best_batsman,
                    best_bowler=best_bowler,
                    series_name=series_name,
                    match_number=str(match_number) if match_number != "-" else "-",
                    toss_winner=toss_winner,
                    toss_decision=toss_decision,
                    umpires=umpires,
                    match_referee=match_referee,
                    match_url=match_url,
                    scorecard_url=scorecard_url,
                    detailed_score=detailed_score
                ))
                
    except Exception as e:
        print(f"Error fetching cricket data: {e}")
    
    return matches


@app.get("/api/last-24h-matches", response_model=List[Match])
async def api_last_24h_matches():
    """Return a list of matches from the last 24 hours as JSON."""
    return await get_last_24h_matches()


# Keep old endpoint for backward compatibility
@app.get("/api/todays-matches", response_model=List[Match])
async def api_todays_matches():
    """Return a list of matches from the last 24 hours as JSON (alias)."""
    return await get_last_24h_matches()


@app.get("/last-24h-matches", response_class=HTMLResponse)
async def last_24h_matches_page(request: Request):
    """Render the HTML page that shows matches from the last 24 hours."""
    return templates.TemplateResponse(
        "todays_matches.html",
        {"request": request},
    )


# Keep old route for backward compatibility
@app.get("/todays-matches", response_class=HTMLResponse)
async def todays_matches_page(request: Request):
    """Render the HTML page that shows matches from the last 24 hours (alias)."""
    return templates.TemplateResponse(
        "todays_matches.html",
        {"request": request},
    )


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Redirect root to the last 24 hours matches page for convenience."""
    return templates.TemplateResponse(
        "todays_matches.html",
        {"request": request},
    )


@app.get("/api/debug/raw")
async def debug_raw_api():
    """Debug endpoint to see raw API response."""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                CRICKET_API_URL,
                params={"apikey": CRICKET_API_KEY, "offset": 0}
            )
            return response.json()
    except Exception as e:
        return {"error": str(e)}
