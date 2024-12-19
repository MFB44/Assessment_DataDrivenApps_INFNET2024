from typing import List, Dict
from langchain_core.tools import Tool
from langchain_community.utilities import SerpAPIWrapper
from .self_ask_agent import get_self_ask_agent, search_team_information
from .soccer import get_specialist_comments, get_match_details

def load_tools(tool_names: List[str] = []) -> Dict[str, Tool]:
    """
    Load tools
    """
    TOOLS = [
        search_team_information,
        get_match_details,
        get_specialist_comments,
        Tool.from_function(name='Self-ask agent',
                           func=get_self_ask_agent().invoke,
                           description="A tool to answer complicated questions. Useful for when you need to answer questions, get competitions events, team details, etc. Input should be a question."),
    ]
    if tool_names == []:
        return TOOLS
    return {t.name: t for t in TOOLS if t.name in tool_names}