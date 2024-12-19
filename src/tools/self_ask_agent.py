from langchain.agents import (AgentExecutor, Tool, create_self_ask_with_search_agent)
from langchain import hub
from langchain_google_genai import GoogleGenerativeAI
from langchain_community.utilities import SerpAPIWrapper
import os

def search_utility():
    SERPAPI_API_KEY = os.getenv('SERPAPI_API_KEY')
    return SerpAPIWrapper(serpapi_api_key=SERPAPI_API_KEY)

search_team_information = Tool(
    name='search_team_information',
    func=search_utility().run,
    description='Useful for when you need to search for information about a specific team or player',
)

def get_self_ask_agent() -> AgentExecutor:
    """
    Get the self ask agent
    """
    llm = GoogleGenerativeAI(model="gemini-pro", temperature=0.2)
    intermediate_search_tool = Tool(
        name='Intermediate Answer',
        func=search_utility().run,
        description='Search'
    )
    prompt = hub.pull("hwchase17/self-ask-with-search")
    return AgentExecutor(
        agent=create_self_ask_with_search_agent(llm, [intermediate_search_tool], prompt),
        tools = [intermediate_search_tool],
        handle_parsing_errors=True,
        verbose=True
    )