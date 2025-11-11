#!/usr/bin/env python3
"""
NFL Transaction Scraper
Scrapes NFL.com transaction log for player/coach movements
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime
from typing import List, Dict
import logging
import time

logger = logging.getLogger(__name__)

def scrape_nfl_transactions(year: int, month: int) -> List[Dict]:
    """
    Scrape NFL.com transaction log
    
    NFL.com uses different URLs for different transaction types:
    - /transactions/league/trades/{year}/{month}
    - /transactions/league/signings/{year}/{month}
    - /transactions/league/waivers/{year}/{month}
    - /transactions/league/reserve-list/{year}/{month}
    - /transactions/league/terminations/{year}/{month}
    
    Args:
        year: Year to scrape
        month: Month to scrape (1-12)
    
    Returns:
        List of transaction dictionaries
    """
    transactions = []
    
    # NFL.com has separate pages for different transaction types
    transaction_types = [
        ('trades', 'trade'),
        ('signings', 'free_agent'),
        ('waivers', 'waiver'),
        ('reserve-list', 'reserve'),
        ('terminations', 'release'),
        ('other', 'other')
    ]
    
    base_url = "https://www.nfl.com"
    
    for url_suffix, trans_type in transaction_types:
        url = f"{base_url}/transactions/league/{url_suffix}/{year}/{month:02d}"
        
        try:
            logger.debug(f"Scraping {url_suffix} from {url}")
            response = requests.get(url, timeout=10, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            
            if response.status_code == 404:
                logger.debug(f"Page not found: {url} (may not have transactions this month)")
                continue
            
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # NFL.com uses tables with <tr> rows containing transaction data
            # Structure: <tr> with <td> containing date, player link, team info
            tables = soup.find_all('table')
            
            for table in tables:
                rows = table.find_all('tr')
                
                for row in rows:
                    try:
                        # Skip header rows
                        if row.find('th'):
                            continue
                        
                        cells = row.find_all('td')
                        if len(cells) < 2:
                            continue
                        
                        # Extract date (usually first or second cell)
                        date_str = None
                        player_name = None
                        player_link = None
                        team_info = []
                        
                        for i, cell in enumerate(cells):
                            text = cell.get_text(strip=True)
                            
                            # Look for date pattern (MM/DD or similar)
                            if not date_str and ('/' in text and len(text) <= 10):
                                date_str = text
                            
                            # Look for player link
                            player_link_elem = cell.find('a', class_=lambda x: x and 'nfl-o-cta' in str(x))
                            if player_link_elem:
                                player_name = player_link_elem.get_text(strip=True)
                                player_link = player_link_elem.get('href', '')
                            
                            # Look for team names in text
                            team_names = [
                                'Lions', 'Commanders', 'Chiefs', 'Ravens', 'Eagles', 'Packers',
                                'Cowboys', 'Steelers', 'Patriots', 'Bills', 'Dolphins', 'Jets',
                                'Browns', 'Bengals', 'Texans', 'Colts', 'Jaguars', 'Titans',
                                'Broncos', 'Raiders', 'Chargers', 'Cardinals', 'Rams', '49ers',
                                'Seahawks', 'Bears', 'Vikings', 'Falcons', 'Panthers', 'Saints',
                                'Buccaneers', 'Giants'
                            ]
                            for team_name in team_names:
                                if team_name in text and team_name not in team_info:
                                    team_info.append(team_name)
                        
                        # If we found a player, create transaction
                        if player_name:
                            # Determine teams involved
                            from_team = team_info[0] if len(team_info) > 0 else None
                            to_team = team_info[1] if len(team_info) > 1 else (team_info[0] if trans_type == 'free_agent' else None)
                            
                            # For trades, both teams should be present
                            if trans_type == 'trade' and len(team_info) >= 2:
                                from_team = team_info[0]
                                to_team = team_info[1]
                            elif trans_type in ['free_agent', 'signings']:
                                to_team = team_info[0] if team_info else None
                            elif trans_type in ['release', 'waiver', 'terminations']:
                                from_team = team_info[0] if team_info else None
                            
                            transaction = {
                                'player_name': player_name,
                                'type': trans_type,
                                'date': date_str or f"{year}-{month:02d}-01",
                                'from_team': from_team,
                                'to_team': to_team,
                                'source_url': url,
                                'position': None  # Would need to extract from player page or other source
                            }
                            
                            # Try to extract position from player link or surrounding text
                            if player_link and '/players/' in player_link:
                                # Position might be in URL or we'd need to fetch player page
                                pass
                            
                            transactions.append(transaction)
                            
                    except Exception as e:
                        logger.debug(f"Error parsing row: {e}")
                        continue
            
            logger.info(f"Scraped {len([t for t in transactions if t.get('source_url') == url])} {url_suffix} transactions")
            
        except requests.RequestException as e:
            logger.debug(f"Failed to scrape {url_suffix}: {e}")
            continue
        except Exception as e:
            logger.debug(f"Unexpected error scraping {url_suffix}: {e}")
            continue
    
    logger.info(f"Total scraped {len(transactions)} transactions from NFL.com")
    return transactions


def _parse_transaction_text(text: str, team: str, default_type: str = None) -> Dict:
    """
    Parse transaction text to extract structured data
    
    Examples:
        "Signed QB John Doe"
        "Traded WR Jane Smith to Team B"
        "Released RB Chris Johnson"
        "Placed on practice squad: WR Mike Williams"
    """
    transaction = {}
    
    # Determine transaction type
    text_lower = text.lower()
    
    if 'traded' in text_lower or 'trade' in text_lower:
        transaction['type'] = 'trade'
        # Extract "to Team B"
        if ' to ' in text_lower:
            parts = text.split(' to ', 1)
            transaction['to_team'] = parts[-1].strip().split()[0] if parts else team
            transaction['from_team'] = team
            # Extract player name and position
            player_part = parts[0].replace('Traded', '').replace('trade', '').strip()
            transaction.update(_extract_player_info(player_part))
        else:
            # Trade without explicit "to" - might be in different format
            transaction['from_team'] = team
            transaction.update(_extract_player_info(text))
    elif 'signed' in text_lower or 'sign' in text_lower:
        transaction['type'] = 'free_agent'
        transaction['to_team'] = team
        player_part = text.replace('Signed', '').replace('sign', '').strip()
        transaction.update(_extract_player_info(player_part))
    elif 'released' in text_lower or 'release' in text_lower:
        transaction['type'] = 'release'
        transaction['from_team'] = team
        player_part = text.replace('Released', '').replace('release', '').strip()
        transaction.update(_extract_player_info(player_part))
    elif 'waived' in text_lower or 'waiver' in text_lower:
        transaction['type'] = 'waiver'
        transaction['from_team'] = team
        player_part = text.replace('Waived', '').replace('waiver', '').strip()
        transaction.update(_extract_player_info(player_part))
    elif 'practice squad' in text_lower or 'practice' in text_lower:
        transaction['type'] = 'practice_squad'
        transaction['to_team'] = team
        transaction['role'] = 'practice_squad'
        player_part = text.replace('Placed on practice squad:', '').replace('practice', '').strip()
        transaction.update(_extract_player_info(player_part))
    elif default_type:
        transaction['type'] = default_type
        transaction['to_team'] = team if default_type in ['free_agent', 'practice_squad'] else None
        transaction['from_team'] = team if default_type in ['release', 'waiver', 'trade'] else None
        transaction.update(_extract_player_info(text))
    else:
        # Try to extract any player info even if type is unclear
        transaction['type'] = 'other'
        transaction['team'] = team
        transaction.update(_extract_player_info(text))
        if not transaction.get('player_name'):
            return None  # No player found, skip
    
    return transaction


def _extract_player_info(text: str) -> Dict:
    """Extract player name and position from text"""
    # Example: "QB John Doe" or "WR Jane Smith"
    parts = text.strip().split(' ', 1)
    
    if len(parts) == 2:
        position = parts[0].upper()
        player_name = parts[1].strip()
        
        # Determine role
        role = 'player'
        if position == 'QB':
            role = 'backup_qb'  # Would need to check if starter or backup
        
        return {
            'player_name': player_name,
            'position': position,
            'role': role
        }
    
    return {'player_name': text.strip()}


if __name__ == "__main__":
    # Test scraper
    today = datetime.now()
    transactions = scrape_nfl_transactions(today.year, today.month)
    print(f"Found {len(transactions)} transactions")
    for trans in transactions[:5]:  # Print first 5
        print(json.dumps(trans, indent=2))

