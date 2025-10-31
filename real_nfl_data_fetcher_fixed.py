import pandas as pd
from datetime import datetime

class RealNFLDataFetcher:
    """
    Fetches real-time NFL game data, such as weekly schedules.
    This class scrapes Pro-Football-Reference.com to get upcoming game matchups.
    """

    def __init__(self):
        """
        Initializes the RealNFLDataFetcher.
        """
        self.current_year = datetime.now().year

    def get_weekly_schedule(self, week_num=None, year=None):
        """
        Fetches the NFL schedule for a specific week.

        Args:
            week_num (int, optional): The week number to fetch. If None, it will
                                      attempt to find the current week. Defaults to None.
            year (int, optional): The year of the season. Defaults to the current year.

        Returns:
            list: A list of dictionaries, where each dictionary represents a game
                  with 'home_team' and 'away_team' keys. Returns an empty list on failure.
        """
        if year is None:
            year = self.current_year
        
        try:
            url = f'https://www.pro-football-reference.com/years/{year}/games.htm'
            tables = pd.read_html(url)
            schedule_df = tables[0]

            # Data cleaning
            schedule_df = schedule_df[schedule_df['Week'] != 'Week'] # Drop header rows repeated in data
            schedule_df.rename(columns={
                'Unnamed: 5': 'winner',
                'Unnamed: 7': 'loser'
            }, inplace=True)

            # For upcoming games, winner/loser columns are used for team names
            schedule_df['home_team'] = schedule_df.apply(
                lambda row: row['loser'] if row['Unnamed: 6'] == '@' else row['winner'], 
                axis=1
            )
            schedule_df['away_team'] = schedule_df.apply(
                lambda row: row['winner'] if row['Unnamed: 6'] == '@' else row['loser'], 
                axis=1
            )

            # Filter for games that haven't been played yet (where score columns are NaN)
            upcoming_games = schedule_df[schedule_df['PtsW'].isna()]

            # If a specific week is requested, filter for that
            if week_num:
                 upcoming_games = upcoming_games[upcoming_games['Week'] == str(week_num)]
            
            # If no week is specified, get the next upcoming week
            else:
                next_week = upcoming_games['Week'].iloc[0]
                upcoming_games = upcoming_games[upcoming_games['Week'] == next_week]


            matchups = []
            for _, row in upcoming_games.iterrows():
                matchups.append({
                    "home_team": row['home_team'],
                    "away_team": row['away_team']
                })
            
            return matchups

        except Exception as e:
            print(f"Error fetching real NFL schedule data: {e}")
            return []

if __name__ == '__main__':
    fetcher = RealNFLDataFetcher()
    
    # Example: Get the schedule for the next upcoming week
    print("Fetching next week's schedule...")
    schedule = fetcher.get_weekly_schedule()
    if schedule:
        for game in schedule:
            print(f"{game['away_team']} at {game['home_team']}")
    else:
        print("Could not fetch schedule.")

    # Example: Get the schedule for a specific week (e.g., week 1)
    print("\nFetching schedule for Week 1...")
    schedule_week_1 = fetcher.get_weekly_schedule(week_num=1)
    if schedule_week_1:
        for game in schedule_week_1:
            print(f"{game['away_team']} at {game['home_team']}")
    else:
        print("Could not fetch schedule for Week 1.")


