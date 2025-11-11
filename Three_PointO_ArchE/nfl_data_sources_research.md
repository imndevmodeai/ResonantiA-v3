# NFL Data Sources Research & Implementation Guide
## WHERE, WHEN, WHY, WHAT, and HOW

---

## 1. PLAYER/COACH MOVEMENT DATA

### WHERE to Get It:

**Primary Sources:**
1. **NFL.com Official Transaction Log**
   - URL: `https://www.nfl.com/transactions/`
   - Endpoint: `/transactions/{year}/{month}`
   - Format: HTML (requires scraping)
   - Updates: Real-time (within minutes of official announcement)

2. **SportsDataIO API** (Paid)
   - Base URL: `https://api.sportsdata.io/v3/nfl`
   - Endpoints:
     - `/transactions/{season}` - All transactions
     - `/players/{playerid}` - Player details
     - `/teams/{team}` - Team rosters
   - Pricing: $50-200/month depending on tier
   - Free Tier: Limited (500 requests/day)
   - Updates: Real-time

3. **Pro Football Reference** (Free, Scraping)
   - URL: `https://www.pro-football-reference.com/`
   - Pages:
     - `/players/{last}/{first}.htm` - Player career history
     - `/teams/{team}/{year}_roster.htm` - Team rosters by year
     - `/coaches/` - Coaching staff history
   - Format: HTML (requires BeautifulSoup)
   - Updates: Daily

4. **ESPN API** (Limited Free Access)
   - Base URL: `https://site.api.espn.com/apis/site/v2/sports/football/nfl/`
   - Endpoints:
     - `/teams/{teamid}/roster` - Team rosters
     - `/transactions` - Recent transactions
   - Free Tier: 1000 requests/day
   - Updates: Near real-time

5. **NFL Team Websites** (Scraping)
   - Each team has official roster pages
   - Example: `https://www.{team}.com/team/players-roster/`
   - Format: HTML
   - Updates: Real-time

### WHEN to Gather:

**Update Frequency:**
- **Real-time**: During trade deadline (October), free agency (March), draft (April)
- **Daily**: During regular season (check for practice squad changes, waiver claims)
- **Weekly**: During off-season (coaching staff changes, player signings)
- **Historical**: Build database going back 5+ years for insider connections

**Optimal Times:**
- **Morning (6-9 AM EST)**: Official NFL announcements
- **Afternoon (2-5 PM EST)**: Team practice reports, roster updates
- **Evening (7-10 PM EST)**: Social media activity, insider reports

### WHY It Matters:

**Insider Knowledge Value:**
- **Backup QBs**: Know play calls, hand signals, audible system (1-2 point edge)
- **Coaches**: Know entire system, tendencies, game planning (3-5 point edge)
- **Practice Squad Players**: Know route concepts, timing (0.5-1 point edge)
- **Cut Players**: Limited knowledge but may know personnel packages (0.5 point edge)

**Impact on Predictions:**
- System familiarity can shift scoring by 2-5 points
- Insider knowledge affects play-calling predictions
- Coaching connections reveal strategic advantages

### WHAT Data to Collect:

**Player Movement:**
```json
{
  "player_name": "John Doe",
  "position": "QB",
  "from_team": "Team A",
  "to_team": "Team B",
  "transaction_date": "2025-10-28",
  "transaction_type": "trade|waiver|free_agent|practice_squad",
  "years_with_team": 3,
  "role": "starter|backup|practice_squad|cut",
  "current_status": "active|inactive|coach"
}
```

**Coaching Staff:**
```json
{
  "coach_name": "Jane Smith",
  "position": "Offensive Coordinator",
  "from_team": "Team A",
  "to_team": "Team B",
  "start_date": "2025-03-15",
  "end_date": "2025-11-09",
  "years_with_team": 2,
  "knowledge_level": "critical|high|medium|low"
}
```

### HOW to Implement:

**1. Web Scraping (NFL.com Transactions)**
```python
import requests
from bs4 import BeautifulSoup
from datetime import datetime

def scrape_nfl_transactions(year: int, month: int) -> List[Dict]:
    """Scrape NFL.com transaction log"""
    url = f"https://www.nfl.com/transactions/{year}/{month:02d}"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    transactions = []
    # Parse transaction table
    for row in soup.find_all('tr', class_='transaction-row'):
        # Extract player name, teams, date, type
        # Store in database
        pass
    
    return transactions
```

**2. API Integration (SportsDataIO)**
```python
import requests

def get_sportsdata_transactions(api_key: str, season: str) -> List[Dict]:
    """Fetch transactions from SportsDataIO API"""
    url = f"https://api.sportsdata.io/v3/nfl/transactions/{season}"
    headers = {"Ocp-Apim-Subscription-Key": api_key}
    response = requests.get(url, headers=headers)
    return response.json()
```

**3. Database Structure**
```sql
CREATE TABLE player_movements (
    id SERIAL PRIMARY KEY,
    player_name VARCHAR(100),
    position VARCHAR(10),
    from_team VARCHAR(50),
    to_team VARCHAR(50),
    transaction_date DATE,
    transaction_type VARCHAR(20),
    years_with_team INTEGER,
    role VARCHAR(20),
    current_status VARCHAR(20),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE coaching_staff (
    id SERIAL PRIMARY KEY,
    coach_name VARCHAR(100),
    position VARCHAR(50),
    from_team VARCHAR(50),
    to_team VARCHAR(50),
    start_date DATE,
    end_date DATE,
    years_with_team INTEGER,
    knowledge_level VARCHAR(20),
    created_at TIMESTAMP DEFAULT NOW()
);
```

---

## 2. BETTING LINE INTELLIGENCE

### WHERE to Get It:

**Primary Sources:**
1. **The Odds API** (Paid)
   - Base URL: `https://api.the-odds-api.com/v4/`
   - Endpoints:
     - `/sports/americanfootball_nfl/odds/` - Current lines
     - `/sports/americanfootball_nfl/odds-history/` - Historical lines
   - Pricing: $10-50/month (500-10,000 requests/month)
   - Free Tier: 500 requests/month
   - Updates: Real-time (every 5-10 minutes)

2. **Sportsbook APIs** (Various)
   - **DraftKings API**: Requires partnership
   - **FanDuel API**: Requires partnership
   - **BetMGM API**: Requires partnership
   - **Caesars API**: Requires partnership
   - Note: Most require commercial agreements

3. **Action Network** (Paid)
   - URL: `https://www.actionnetwork.com/`
   - Provides: Public betting percentages, sharp money indicators
   - Pricing: $10-30/month
   - Updates: Real-time

4. **Vegas Insider** (Free, Scraping)
   - URL: `https://www.vegasinsider.com/nfl/odds/las-vegas/`
   - Format: HTML
   - Updates: Every 15-30 minutes
   - Provides: Line movements, public percentages (estimated)

5. **Pregame.com** (Free, Scraping)
   - URL: `https://www.pregame.com/`
   - Provides: Line movements, public betting data
   - Format: HTML
   - Updates: Real-time

### WHEN to Gather:

**Update Frequency:**
- **Real-time**: During game week (lines change constantly)
- **Every 5-10 minutes**: During peak betting hours (Friday-Sunday)
- **Hourly**: During off-peak hours
- **Historical**: Track line movements over time

**Optimal Times:**
- **Sunday Morning (9-11 AM EST)**: Final line movements before games
- **Friday-Saturday**: Line movements, public money percentages
- **Monday-Thursday**: Initial lines posted, early sharp money

### WHY It Matters:

**Line Shading Analysis:**
- **Public Money**: 60-70% typically bets on favorite
- **Popular Teams**: Cowboys, Packers, Steelers get 1-1.5 point shading
- **Travel Factor**: Road teams get 2-3 extra points
- **Sharp Money**: Professional bettors fade public (creates value)

**Edge Opportunities:**
- **Fade Public**: When 70%+ on favorite, bet underdog (2-3 point value)
- **Follow Sharp**: When sharp money heavy, follow (1-2 point value)
- **Line Shopping**: Find best line across books (0.5-1 point value)

### WHAT Data to Collect:

**Betting Line Data:**
```json
{
  "game_id": "2025-11-09-DET-WAS",
  "team1": "Detroit Lions",
  "team2": "Washington Commanders",
  "public_line": 3.5,
  "sharp_line": 2.0,
  "line_shading": 1.5,
  "public_money_pct": 0.68,
  "sharp_money_pct": 0.32,
  "travel_factor": 0.0,
  "popularity_factor": 0.5,
  "real_matchup_line": 2.0,
  "edge_opportunity": "fade_public",
  "timestamp": "2025-11-09T10:00:00Z"
}
```

### HOW to Implement:

**1. The Odds API Integration**
```python
import requests

def get_betting_lines(api_key: str, sport: str = "americanfootball_nfl") -> List[Dict]:
    """Fetch current betting lines"""
    url = f"https://api.the-odds-api.com/v4/sports/{sport}/odds"
    params = {
        "apiKey": api_key,
        "regions": "us",
        "markets": "spreads",
        "oddsFormat": "american"
    }
    response = requests.get(url, params=params)
    return response.json()
```

**2. Vegas Insider Scraping**
```python
from bs4 import BeautifulSoup

def scrape_vegas_insider_lines() -> List[Dict]:
    """Scrape betting lines from Vegas Insider"""
    url = "https://www.vegasinsider.com/nfl/odds/las-vegas/"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    lines = []
    # Parse line table
    for row in soup.find_all('tr', class_='odds-row'):
        # Extract team names, spreads, public percentages
        pass
    
    return lines
```

**3. Line Shading Calculation**
```python
def calculate_line_shading(public_line: float, favorite: str, 
                          venue: str, team_popularity: Dict[str, float]) -> Dict:
    """Calculate line shading factors"""
    travel_factor = 2.5 if venue != "home" else 0.0
    popularity_shading = team_popularity.get(favorite, 0.0)
    
    sharp_line = public_line - travel_factor - popularity_shading
    
    return {
        "public_line": public_line,
        "sharp_line": sharp_line,
        "line_shading": travel_factor + popularity_shading,
        "travel_factor": travel_factor,
        "popularity_factor": popularity_shading
    }
```

---

## 3. PRACTICE SQUAD & WAIVER WIRE

### WHERE to Get It:

**Primary Sources:**
1. **NFL.com Transaction Log** (Free, Scraping)
   - URL: `https://www.nfl.com/transactions/`
   - Filter: "Practice Squad" transactions
   - Updates: Real-time

2. **Team Websites** (Scraping)
   - Each team lists practice squad rosters
   - Example: `https://www.{team}.com/team/players-roster/practice-squad/`
   - Updates: Daily

3. **NFL.com Official Practice Squad List** (Free, Scraping)
   - URL: `https://www.nfl.com/players/practice-squad/`
   - Updates: Daily

4. **SportsDataIO API** (Paid)
   - Endpoint: `/teams/{team}/practice-squad`
   - Updates: Real-time

### WHEN to Gather:

**Update Frequency:**
- **Daily**: Practice squad changes happen frequently
- **Weekly**: During season (Tuesday-Wednesday most active)
- **Real-time**: During waiver wire periods

### WHY It Matters:

**Practice Squad Knowledge:**
- Players know route concepts, timing, system familiarity
- Can provide insights to new team (0.5-1 point edge)
- Often overlooked by public but valuable for insider intel

### WHAT Data to Collect:

```json
{
  "player_name": "John Doe",
  "position": "WR",
  "team": "Team A",
  "previous_teams": ["Team B", "Team C"],
  "years_on_practice_squad": 2,
  "current_status": "active|cut|signed_to_active",
  "knowledge_level": "medium"
}
```

---

## 4. INJURY REPORTS & SOCIAL MEDIA

### WHERE to Get It:

**Primary Sources:**
1. **NFL.com Official Injury Report** (Free, Scraping)
   - URL: `https://www.nfl.com/injuries/`
   - Updates: Daily (Wednesday-Saturday during season)

2. **ESPN Injury Tracker** (Free, Scraping)
   - URL: `https://www.espn.com/nfl/injuries`
   - Updates: Real-time

3. **Twitter/X API** (Paid)
   - Base URL: `https://api.twitter.com/2/`
   - Endpoints:
     - `/tweets/search/recent` - Search tweets
     - `/users/by/username/{username}` - User info
   - Pricing: $100-5000/month (Basic to Enterprise)
   - Free Tier: 1,500 tweets/month (very limited)

4. **Reddit API** (Free)
   - Base URL: `https://www.reddit.com/api/`
   - Endpoints:
     - `/r/{subreddit}/new.json` - New posts
     - `/r/{subreddit}/comments/{post_id}.json` - Comments
   - Free Tier: 60 requests/minute
   - Updates: Real-time

5. **Team Beat Reporters** (Scraping Twitter)
   - Each team has beat reporters who tweet practice updates
   - Example: Search "@{team}Beat" on Twitter
   - Updates: Real-time

### WHEN to Gather:

**Update Frequency:**
- **Real-time**: Social media monitoring (continuous)
- **Daily**: Official injury reports (Wednesday-Saturday)
- **Hourly**: Practice reports (during practice hours)

**Optimal Times:**
- **Morning (7-9 AM EST)**: Practice reports, injury updates
- **Afternoon (2-5 PM EST)**: Practice observations, social media activity
- **Evening (7-10 PM EST)**: Insider reports, fan observations

### WHY It Matters:

**Hidden Information:**
- **Social Media**: Players tweet about injuries before official reports
- **Practice Reports**: Beat writers observe limitations not in official reports
- **Forums**: Fans share practice observations from open practices
- **Personal Issues**: Social media reveals relationship problems, family issues

**Impact:**
- Can reveal injuries 1-2 days before official reports
- Practice limitations affect game predictions
- Personal issues affect player performance (1-2 point impact)

### WHAT Data to Collect:

**Injury Data:**
```json
{
  "player_name": "John Doe",
  "team": "Team A",
  "injury": "Ankle",
  "status": "Questionable|Doubtful|Out",
  "practice_status": "Full|Limited|Did Not Participate",
  "source": "Official|Social Media|Practice Report",
  "confidence": 0.9,
  "impact": "high|moderate|low"
}
```

**Social Media Mentions:**
```json
{
  "platform": "Twitter",
  "author": "@beat_reporter",
  "content": "Player X was limited in practice today",
  "timestamp": "2025-11-09T14:30:00Z",
  "relevance": "high|medium|low",
  "verified": true
}
```

### HOW to Implement:

**1. Twitter/X API**
```python
import tweepy

def search_twitter_injuries(api_key: str, team: str) -> List[Dict]:
    """Search Twitter for injury mentions"""
    client = tweepy.Client(bearer_token=api_key)
    
    query = f"{team} injury OR {team} practice -is:retweet"
    tweets = client.search_recent_tweets(
        query=query,
        max_results=100,
        tweet_fields=['created_at', 'author_id']
    )
    
    return tweets.data
```

**2. Reddit API**
```python
import praw

def get_reddit_practice_reports(subreddit: str = "nfl") -> List[Dict]:
    """Get practice reports from Reddit"""
    reddit = praw.Reddit(
        client_id="your_client_id",
        client_secret="your_client_secret",
        user_agent="NFL Intelligence Bot"
    )
    
    posts = []
    for submission in reddit.subreddit(subreddit).new(limit=100):
        if "practice" in submission.title.lower():
            posts.append({
                "title": submission.title,
                "content": submission.selftext,
                "author": str(submission.author),
                "created": submission.created_utc
            })
    
    return posts
```

**3. NFL.com Injury Report Scraping**
```python
def scrape_nfl_injury_report(week: int) -> List[Dict]:
    """Scrape official NFL injury report"""
    url = f"https://www.nfl.com/injuries/week/{week}"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    injuries = []
    # Parse injury table
    for team_section in soup.find_all('div', class_='team-injuries'):
        team_name = team_section.find('h3').text
        for row in team_section.find_all('tr'):
            # Extract player, injury, status
            pass
    
    return injuries
```

---

## 5. ADVANCED METRICS (EPA, DVOA, Next Gen Stats)

### WHERE to Get It:

**Primary Sources:**
1. **Football Outsiders** (DVOA) (Paid)
   - URL: `https://www.footballoutsiders.com/`
   - Provides: DVOA, DAVE, VOA metrics
   - Pricing: $35/year (subscription)
   - Updates: Weekly

2. **Next Gen Stats** (NFL.com) (Free, Scraping)
   - URL: `https://www.nfl.com/next-gen-stats/`
   - Provides: Time to Throw, Air Yards, Completion Probability
   - Format: HTML/JSON
   - Updates: Weekly

3. **Pro Football Reference** (Free, Scraping)
   - URL: `https://www.pro-football-reference.com/`
   - Provides: Advanced stats, EPA calculations
   - Format: HTML
   - Updates: Daily

4. **nflfastR** (R Package, Free)
   - Provides: Play-by-play data, EPA calculations
   - Can be accessed via Python (rpy2) or converted to CSV
   - Updates: Weekly

### WHEN to Gather:

**Update Frequency:**
- **Weekly**: After each game week
- **Daily**: During season (stats update after games)
- **Historical**: Build database going back 5+ years

### WHY It Matters:

**Advanced Metrics Value:**
- **EPA**: Better predictor than yards/points
- **DVOA**: Adjusts for opponent strength
- **Next Gen Stats**: Reveals hidden performance factors
- **Combined**: More accurate than traditional stats

### WHAT Data to Collect:

```json
{
  "team": "Team A",
  "week": 10,
  "season": 2025,
  "epa_per_play": 0.08,
  "dvoa": 12.5,
  "time_to_throw": 2.8,
  "air_yards_per_attempt": 8.5,
  "completion_probability": 0.72
}
```

---

## IMPLEMENTATION PRIORITY

### Phase 1 (Immediate - Free Sources):
1. ✅ NFL.com transaction scraping
2. ✅ Pro Football Reference scraping
3. ✅ Reddit API for practice reports
4. ✅ Vegas Insider scraping for betting lines

### Phase 2 (Short-term - Low Cost):
1. The Odds API ($10-50/month)
2. Twitter API Basic ($100/month)
3. Football Outsiders subscription ($35/year)

### Phase 3 (Long-term - Higher Cost):
1. SportsDataIO API ($50-200/month)
2. Action Network ($10-30/month)
3. Twitter API Enterprise ($5000/month)

---

## DATABASE SCHEMA

```sql
-- Player Movements
CREATE TABLE player_movements (
    id SERIAL PRIMARY KEY,
    player_name VARCHAR(100) NOT NULL,
    position VARCHAR(10),
    from_team VARCHAR(50),
    to_team VARCHAR(50),
    transaction_date DATE,
    transaction_type VARCHAR(20),
    years_with_team INTEGER,
    role VARCHAR(20),
    current_status VARCHAR(20),
    knowledge_level VARCHAR(20),
    created_at TIMESTAMP DEFAULT NOW(),
    INDEX idx_teams (from_team, to_team),
    INDEX idx_date (transaction_date)
);

-- Coaching Staff
CREATE TABLE coaching_staff (
    id SERIAL PRIMARY KEY,
    coach_name VARCHAR(100) NOT NULL,
    position VARCHAR(50),
    from_team VARCHAR(50),
    to_team VARCHAR(50),
    start_date DATE,
    end_date DATE,
    years_with_team INTEGER,
    knowledge_level VARCHAR(20),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Betting Lines
CREATE TABLE betting_lines (
    id SERIAL PRIMARY KEY,
    game_id VARCHAR(50) NOT NULL,
    team1 VARCHAR(50),
    team2 VARCHAR(50),
    public_line FLOAT,
    sharp_line FLOAT,
    line_shading FLOAT,
    public_money_pct FLOAT,
    sharp_money_pct FLOAT,
    timestamp TIMESTAMP,
    INDEX idx_game (game_id),
    INDEX idx_timestamp (timestamp)
);

-- Injuries
CREATE TABLE injuries (
    id SERIAL PRIMARY KEY,
    player_name VARCHAR(100),
    team VARCHAR(50),
    injury VARCHAR(100),
    status VARCHAR(20),
    practice_status VARCHAR(20),
    source VARCHAR(50),
    confidence FLOAT,
    impact VARCHAR(20),
    reported_at TIMESTAMP,
    INDEX idx_team (team),
    INDEX idx_date (reported_at)
);

-- Social Media Mentions
CREATE TABLE social_media_mentions (
    id SERIAL PRIMARY KEY,
    platform VARCHAR(20),
    author VARCHAR(100),
    content TEXT,
    timestamp TIMESTAMP,
    relevance VARCHAR(20),
    verified BOOLEAN,
    INDEX idx_timestamp (timestamp)
);
```

---

## AUTOMATION SCHEDULE

**Daily Tasks:**
- 6:00 AM: Scrape NFL.com transactions
- 7:00 AM: Scrape injury reports
- 8:00 AM: Check Reddit for practice reports
- 9:00 AM: Update betting lines
- 2:00 PM: Check social media for practice updates
- 5:00 PM: Final betting line update

**Weekly Tasks:**
- Monday: Update advanced metrics (EPA, DVOA)
- Tuesday: Process waiver wire transactions
- Wednesday: Update practice squad rosters
- Thursday: Final injury report analysis
- Friday: Betting line intelligence update
- Saturday: Final game preparation
- Sunday: Real-time monitoring during games

---

This comprehensive guide provides the foundation for implementing real data gathering for the NFL insider intelligence system.

