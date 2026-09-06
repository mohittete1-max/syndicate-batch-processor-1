import json
import os
import pandas as pd

def parse_cricsheet_json(file_path):
    """
    Parses a single Cricsheet JSON match file (supports T20, ODI, Test) 
    and flattens it into a ball-by-ball Pandas DataFrame.
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    info = data.get('info', {})
    match_type = info.get('match_type', 'unknown')
    venue = info.get('venue', 'unknown')
    dates = info.get('dates', [None])
    match_date = dates[0] if dates else None
    teams = info.get('teams', [])
    gender = info.get('gender', 'male')
    
    toss_winner = info.get('toss', {}).get('winner')
    toss_decision = info.get('toss', {}).get('decision')
    
    rows = []
    innings_list = data.get('innings', [])
    
    for inning_idx, inning in enumerate(innings_list):
        batting_team = inning.get('team')
        bowling_team = [t for t in teams if t != batting_team]
        bowling_team = bowling_team[0] if bowling_team else 'unknown'
        
        overs = inning.get('overs', [])
        for over in overs:
            over_num = over.get('net_over', over.get('over', 0))
            phase = _get_match_phase(match_type, over_num)
            
            deliveries = over.get('deliveries', [])
            for ball_idx, delivery in enumerate(deliveries):
                batter = delivery.get('batter')
                bowler = delivery.get('bowler')
                non_striker = delivery.get('non_striker')
                
                runs_dict = delivery.get('runs', {})
                runs_batter = runs_dict.get('batter', 0)
                runs_extras = runs_dict.get('extras', 0)
                runs_total = runs_dict.get('total', 0)
                
                wickets = delivery.get('wickets', [])
                is_wicket = 1 if wickets else 0
                player_dismissed = wickets[0].get('player_out') if is_wicket else None
                wicket_kind = wickets[0].get('kind') if is_wicket else None
                
                rows.append({
                    'match_date': match_date,
                    'match_type': match_type,
                    'gender': gender,
                    'venue': venue,
                    'batting_team': batting_team,
                    'bowling_team': bowling_team,
                    'inning': inning_idx + 1,
                    'over': over_num,
                    'ball': ball_idx + 1,
                    'phase': phase,
                    'batter': batter,
                    'bowler': bowler,
                    'runs_batter': runs_batter,
                    'runs_extras': runs_extras,
                    'runs_total': runs_total,
                    'is_wicket': is_wicket,
                    'player_dismissed': player_dismissed,
                    'wicket_kind': wicket_kind,
                    'toss_winner': toss_winner,
                    'toss_decision': toss_decision
                })
                
    return pd.DataFrame(rows)

def _get_match_phase(match_type, over_num):
    """Classifies the phase of the game based on format rules."""
    mt = match_type.lower()
    if mt == 't20':
        if over_num < 6:
            return 'powerplay'
        elif over_num < 16:
            return 'middle'
        else:
            return 'death'
    elif mt == 'odi':
        if over_num < 10:
            return 'powerplay_1'
        elif over_num < 40:
            return 'middle'
        else:
            return 'death'
    else:
        return 'extended_play'
