# International Cricket Statistics - Live & Recent Matches

A web application that displays live and recent international cricket match statistics using real-time data from CricAPI.

## Features

- Shows matches from the last 24 hours (Test, ODI, T20I)
- Real-time scores and match status
- Auto-refreshes every 2 minutes
- Clean, responsive UI

## Setup Instructions

### 1. Install Dependencies

```bash
python -m venv .venv
.\.venv\Scripts\activate   # Windows
pip install fastapi uvicorn jinja2 httpx
```

### 2. Get a Free Cricket API Key

To display **real cricket data**, you need a free API key:

1. Visit: **https://www.cricapi.com/**
2. Click "Sign Up" or "Get API Key"
3. Create a free account
4. Copy your API key from the dashboard

### 3. Configure API Key

Open `main.py` and replace this line:

```python
CRICKET_API_KEY = "your_api_key_here"
```

With your actual API key:

```python
CRICKET_API_KEY = "abc123xyz456"  # Your real key
```

### 4. Run the App

```bash
uvicorn main:app --reload
```

Then open: **http://127.0.0.1:8000/**

## Alternative: Use Mock Data for Testing

If you don't want to use a real API yet, you can temporarily use mock data by commenting out the API call and returning sample matches.

## API Endpoints

- `GET /` - Main web page
- `GET /api/todays-matches` - JSON list of matches from last 24 hours
- `GET /api/last-24h-matches` - Same as above (alias)

## Tech Stack

- **Backend**: FastAPI (Python)
- **Frontend**: HTML, CSS, Vanilla JavaScript
- **Data Source**: CricAPI (https://www.cricapi.com/)
- **HTTP Client**: httpx

## Project Structure

```
.
├── main.py                 # FastAPI backend
├── templates/
│   └── todays_matches.html # Frontend HTML
├── static/
│   └── style.css          # Styling
└── README.md              # This file
```

## Notes

- Free tier API has rate limits (usually 100 requests/day)
- The app caches nothing currently, so each page load = 1 API call
- For production, add caching (Redis) to reduce API calls

## Future Enhancements

- Add player statistics
- Add team rankings
- Add historical data and trends
- Add filters by format/team
- Add live score updates (WebSocket)
