from fastapi import APIRouter

router = APIRouter()

from langchain.chains import LLMChain
from langchain_google_genai import GoogleGenerativeAI
from langchain.prompts import PromptTemplate
import yaml

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from soccer_stats.matches import get_events, get_player_stats

def events_summary(match_events):
    """
    Uses an LLM to summarize the events of a match
    """
    pre_prompt = """
    You are an AI assistant tasked with summarizing the events of a soccer match.
    You must always make the summary as clear and friendly as possible.
    Be clear and concise in your summary.

    You must use the current match events:
    {match_events}

    Answer example:
    "Team A won agains Team B, with a score of 2-1. The goals were from Player A and Player B."
    """
    llm = GoogleGenerativeAI(model="gemini-1.5-flash")
    input_variables={"match_events": yaml.dump(match_events)}
    prompt = PromptTemplate.from_template(pre_prompt)
    chain = LLMChain(llm=llm, prompt=prompt, verbose=True)
    return chain.run(**input_variables)

@router.get("/match_summary/{match_id}")
def match_summary(match_id: int):
    match_events = get_events(match_id)
    return events_summary(match_events)

@router.get("/player_stats/{match_id}/{player_name}")
def player_stats(match_id: int, player_name: str):
    return get_player_stats(match_id, player_name)

# def match_summary2(match_id: int):
#     match_events = get_events(match_id)
#     return events_summary(match_events)

# print(match_summary2(3942819))

def player_stats(match_id: int, player_name: str):
    return get_player_stats(match_id, player_name)

print(player_stats(303299, "Filip Kostić"))