from statsbombpy import sb
from copy import copy
import numpy as np
import pandas as pd
import json
import yaml

class PlayerStatsError(Exception):
    def __init__(self, message):
        super().__init__(message)
        self.message = message

def to_json(df: pd.DataFrame) -> str:
    """
    Convert the statsbombpy DataFrame to a JSON string
    """
    return json.dumps(df, indent=2)

def get_lineups(match_id: int) -> str:
    """
    Get the lineups for a given match
    """
    data = sb.lineups(match_id=match_id)
    data_final = copy(data)
    list_fields = ['cards', 'positions']
    for field in list_fields:
        for key, df in data.items():
            df[field] = df[field].apply(lambda v: {field: v})
            data_final[key] = df.to_dict(orient='records')
    return to_json(data_final)

def get_events(match_id: int) -> str:
    """
    Get the events for a given match
    """
    events = sb.events(match_id=match_id, split=True, flatten_attrs=False)
    full_events = pd.concat([v for _, v in events.items()])
    return yaml.dump([
        {k: v for k, v in event.items() if v is not np.nan} 
        for event in full_events.sort_values(by="minute").to_dict(orient='records')
    ])

def get_player_stats(match_id, player_name) -> str:
    """
    Get the statistics for a given player in a match
    """
    try:
        events = sb.events(match_id=match_id)
        if events.empty:
            raise PlayerStatsError(f"No events found for match {match_id}")
        
        player_events = events[events['player'] == player_name]
        if player_events.empty:
            raise PlayerStatsError(f"No events found for player {player_name} in match {match_id}")
        
        stats = {
            "player": player_name,
            "passes_completed": player_events[(player_events['type'] == 'Pass') & (player_events['pass_outcome'].isna())].shape[0],
            "passes_attempted": player_events[player_events['type'] == 'Pass'].shape[0],
            "shots": player_events[player_events['type'] == 'Shot'].shape[0],
            "shots_on_target": player_events[(player_events['type'] == 'Shot') & (player_events['shot_outcome'] == 'On Target')].shape[0],
            "fouls_committed": player_events[player_events['type'] == 'Foul Committed'].shape[0],
            "fouls_won": player_events[player_events['type'] == 'Foul Won'].shape[0],
            "tackles": player_events[player_events['type'] == 'Tackle'].shape[0],
            "interceptions": player_events[player_events['type'] == 'Interception'].shape[0],
            "dribbles_successful": player_events[(player_events['type'] == 'Dribble') & (player_events['dribble_outcome'] == 'Complete')].shape[0],
            "dribbles_attempted": player_events[player_events['type'] == 'Dribble'].shape[0],
        }

    except PlayerStatsError as e:
        raise PlayerStatsError(e.message)
    except Exception as e:
        raise PlayerStatsError(f"An unexpected error occurred: {str(e)}")
    
    return to_json(stats)