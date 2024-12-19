from statsbombpy import sb
import json

def get_competitions() -> str:
    """
    Gets all competitions available in the StatsBomb API
    """
    return json.dumps(sb.competitions().to_dict(orient='records'))

def get_matches(competition_id: int, season_id: int) -> str:
    """
    Gets all matches for a given competition and season
    """
    return json.dumps(sb.matches(competition_id=competition_id, season_id=season_id).to_dict(orient='records'))
