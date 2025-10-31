import pandas as pd
import random

class NFLTeamDatabase:
    """
    A database of NFL teams and their associated statistics, fetched from a live web source.
    This class scrapes data from Pro-Football-Reference.com to provide up-to-date
    team statistics for use in predictions.
    """

    def __init__(self, year=2023):
        """
        Initializes the NFLTeamDatabase by scraping data for the specified year.

        Args:
            year (int): The NFL season year to fetch data for.
        """
        self.year = year
        self.teams = self._fetch_team_stats()

    def _fetch_team_stats(self):
        """
        Fetches NFL team stats from Pro-Football-Reference.com using pandas.
        It retrieves standings, offense, and defense stats and synthesizes them
        into a unified dictionary.

        Returns:
            dict: A dictionary of teams with their synthesized statistics.
                  Returns an empty dict if fetching fails.
        """
        teams_data = {}
        try:
            url = f'https://www.pro-football-reference.com/years/{self.year}/'
            tables = pd.read_html(url)
            
            # First two tables are AFC and NFC standings
            afc_standings = tables[0]
            nfc_standings = tables[1]
            
            # The fifth table is typically Team Stats
            team_stats = tables[4]

            # Clean up the standings tables
            afc_standings.rename(columns={'Tm': 'Team'}, inplace=True)
            nfc_standings.rename(columns={'Tm': 'Team'}, inplace=True)
            standings = pd.concat([afc_standings, nfc_standings])
            standings['Team'] = standings['Team'].apply(lambda x: x.split('*')[0].split('+')[0].strip())


            # Clean up the team stats table
            team_stats.columns = ['_'.join(col).strip() for col in team_stats.columns.values]
            team_stats.rename(columns={'Team_': 'Team'}, inplace=True)

            # Merge standings and stats
            full_stats = pd.merge(standings, team_stats, on='Team')

            # Normalize stats to create ratings
            pf_max = full_stats['PF'].astype(float).max()
            pa_max = full_stats['PA'].astype(float).max()
            
            for _, row in full_stats.iterrows():
                team_name = row['Team']
                
                # Normalize Points For and Points Against to a 0-100 scale
                offense_rating = (row['PF'] / pf_max) * 100
                # Invert defense rating so higher is better
                defense_rating = (1 - (row['PA'] / pa_max)) * 100

                teams_data[team_name] = {
                    "offense": round(offense_rating, 2),
                    "defense": round(defense_rating, 2),
                    "special_teams": random.randint(75, 95), # Placeholder for now
                    "wins": int(row['W']),
                    "losses": int(row['L']),
                }
            
            return teams_data

        except Exception as e:
            print(f"Error fetching real NFL data: {e}")
            print("Falling back to an empty database.")
            return {}

    def get_team_stats(self, team_name):
        """
        Retrieves the statistics for a given team.

        Args:
            team_name (str): The name of the team.

        Returns:
            dict: A dictionary of team statistics, or None if the team is not found.
        """
        return self.teams.get(team_name)

    def get_all_teams(self):
        """
        Retrieves a list of all team names in the database.

        Returns:
            list: A list of all team names.
        """
        return list(self.teams.keys())

    def get_random_matchup(self):
        """
        Selects two different random teams for a matchup.

        Returns:
            tuple: A tuple containing the names of the two random teams.
        """
        if not self.teams:
            return None, None
        team1, team2 = random.sample(list(self.teams.keys()), 2)
        return team1, team2
