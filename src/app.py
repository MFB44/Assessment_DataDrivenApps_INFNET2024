from soccer_stats.competitions import get_competitions, get_matches
from soccer_stats.matches import get_lineups, get_player_stats
from langchain.memory import ConversationBufferMemory
from langchain_community.chat_message_histories import StreamlitChatMessageHistory
from langchain.schema import AIMessage, HumanMessage
# from langchain_community.callbacks.streamlit import StreamlitCallbackHandler
# from tools.soccer import get_sport_specialist_comments_about_match as comments_about_a_match
from tools import load_tools
from agent import load_agent
import streamlit as st
import json
import matplotlib.pyplot as plt
import os

LANGCHAIN_TRACING_V2=True
LANGCHAIN_ENDPOINT="https://api.smith.langchain.com"
LANGCHAIN_API_KEY=os.getenv("LANGCHAIN_API_KEY")
LANGCHAIN_PROJECT="pr-extraneous-prosecutor-7"

st.set_page_config(page_title="Soccer Match Details",
                   page_icon="⚽️")

msgs = StreamlitChatMessageHistory()

# Create memory for the conversation
if "memory" not in st.session_state:
    st.session_state["memory"] = ConversationBufferMemory(messages=msgs, memory_key="chat_history", return_messages=True)
def memorize_message():
    user_input = st.session_state["user_input"]
    st.session_state["memory"].chat_memory.add_message(HumanMessage(content=user_input))

# Load the competitions and agents
def load_competitions():
    return json.loads(get_competitions())
def load_matches(competition_id, season_id):
    return  json.loads(get_matches(competition_id, season_id))

# Create a sidebar to select Competition, Season and Match
st.sidebar.title("Apita o árbitro!")
selected_competition = None
selected_season = None
selected_match = None
match_id = None
match_details = None
specialist_comments = None

st.sidebar.header("Selecione uma competição, temporada e jogo")
competitions = load_competitions()
competition_names = sorted(set([comp['competition_name'] for comp in competitions]))
selected_competition = st.sidebar.selectbox("Choose Competition", competition_names)

if selected_competition:
    seasons = set(comp['season_name'] for comp in competitions if comp['competition_name'] == selected_competition)
    selected_season = st.sidebar.selectbox("Choose Season", sorted(seasons))

if selected_season:
    competition_id = next((comp['competition_id'] for comp in competitions if comp['competition_name'] == selected_competition),
        None
    )
    season_id = next((comp['season_id'] for comp in competitions if comp['season_name'] == selected_season and comp['competition_name'] == selected_competition),
        None
    )

    matches = load_matches(competition_id, season_id)
    match_names = sorted([f"{match['home_team']} vs {match['away_team']}" for match in matches])

    if selected_match:=st.sidebar.selectbox("Choose Match", match_names):
        match_details = next((match for match in matches if f"{match['home_team']} vs {match['away_team']}" == selected_match),
            None
        ) 
        match_id = match_details['match_id']

narration_style = st.sidebar.radio("Escolha o estilo de narração para nosso comentarista especialista", ["Formal", "Humorístico", "Técnico"])

t1, t2 = st.tabs(["Início", "Chat"])

with t1:
    st.header("Gráficos e Estatísticas")
    with st.expander(f"Detalhes do jogo: {selected_match}"):
        st.write(f"ID do jogo: {match_id}")
        if match_details:
            st.write("Detalhes do jogo:")
            for key, value in match_details.items():
                st.write(f"{key}: {value}")
    home_team = match_details['home_team']
    away_team = match_details['away_team']
    lineups_str = get_lineups(match_id)
    lineups_dict = json.loads(lineups_str)
    ht_len = len(lineups_dict[home_team])
    at_len = len(lineups_dict[away_team])
    ht_players = [lineups_dict[home_team][i]['player_name'] for i in range(ht_len)]
    at_players = [lineups_dict[away_team][i]['player_name'] for i in range(at_len)]
    c1, c2 = st.columns(2)
    with c1:
        with st.container(border=True):
            st.write(f"Time da casa: {home_team}")
            home_player = st.selectbox("Escolha um jogador", ht_players)
            player_stats_str = get_player_stats(match_id, home_player)
            player_stats_dict = json.loads(player_stats_str)
            with st.container(border=True):
                for key, value in player_stats_dict.items():
                    st.write(f"{key.title()}: {value}")
            stats = {
                "Passes_Completed": player_stats_dict.get("passes_completed", 0),
                "Passes_Attempted": player_stats_dict.get("passes_attempted", 0),
                "Shots": player_stats_dict.get("shots", 0),
                "Shots_On_Target": player_stats_dict.get("shots_on_target", 0),
                "Fouls_Committed": player_stats_dict.get("fouls_committed", 0),
                "Fouls_Won": player_stats_dict.get("fouls_won", 0),
                "Tackles": player_stats_dict.get("tackles", 0),
                "Interceptions": player_stats_dict.get("interceptions", 0),
                "Dribbles_Successful": player_stats_dict.get("dribbles_successful", 0),
                "Dribbles_Attempted": player_stats_dict.get("dribbles_attempted", 0)
            }
            fig, ax = plt.subplots()
            ax.barh(list(stats.keys()), list(stats.values()))
            ax.set_xlabel('Quantidade')
            ax.set_title(f'Estatísticas de {home_player}')
            st.pyplot(fig)
    with c2:
        with st.container(border=True):
            st.write(f"Time visitante: {away_team}")
            away_player = st.selectbox("Escolha um jogador", at_players)
            player_stats_str = get_player_stats(match_id, away_player)
            player_stats_dict = json.loads(player_stats_str)
            with st.container(border=True):
                for key, value in player_stats_dict.items():
                    st.write(f"{key.title()}: {value}")
            stats = {
                "Passes_Completed": player_stats_dict.get("passes_completed", 0),
                "Passes_Attempted": player_stats_dict.get("passes_attempted", 0),
                "Shots": player_stats_dict.get("shots", 0),
                "Shots_On_Target": player_stats_dict.get("shots_on_target", 0),
                "Fouls_Committed": player_stats_dict.get("fouls_committed", 0),
                "Fouls_Won": player_stats_dict.get("fouls_won", 0),
                "Tackles": player_stats_dict.get("tackles", 0),
                "Interceptions": player_stats_dict.get("interceptions", 0),
                "Dribbles_Successful": player_stats_dict.get("dribbles_successful", 0),
                "Dribbles_Attempted": player_stats_dict.get("dribbles_attempted", 0)
            }
            fig, ax = plt.subplots()
            ax.barh(list(stats.keys()), list(stats.values()))
            ax.set_xlabel('Quantidade')
            ax.set_title(f'Estatísticas de {home_player}') 
            st.pyplot(fig)
with t2:
    if not match_id:
        st.title("Football Match Conversation")
        st.write("Use the sidebar to select a competition, then a match, and start a conversation.")
    else:
        st.markdown(f'<h1 class="title">{selected_match}</h1><h3 class="title">{selected_competition} - Season {selected_season}</h3>', unsafe_allow_html=True)
        with st.container(border=False):
            st.chat_input(key="user_input", on_submit=memorize_message) 

            if user_input := st.session_state.user_input:
                chat_history = st.session_state["memory"].chat_memory.messages

                for msg in chat_history:
                    if isinstance(msg, HumanMessage):
                        with st.chat_message("user"):
                            st.write(f"{msg.content}")
                    elif isinstance(msg, AIMessage):
                        with st.chat_message("assistant"):
                            st.write(f"{msg.content}")
                            
                with st.spinner("Estou pensando..."):
                    try:
                        agent = load_agent()
                        
                        tools = load_tools()
                        tool_names = [tool.name for tool in tools]
                        tool_descriptions = [tool.description for tool in tools]

                        input_data = {
                            "match_id": match_id,
                            "match_name": selected_match,
                            "input": user_input,
                            "agent_scratchpad": "",
                            "competition_id": competition_id,
                            "season_id": season_id,
                            "tool_names": tool_names,
                            "tools": tool_descriptions,
                            "narration_style": narration_style
                        }

                        response = agent.invoke(input=input_data, handle_parsing_errors=True)

                        if isinstance(response, dict) and "output" in response:
                            output = response.get("output")
                        else:
                            output = "Desculpe, não entendi. Tente novamente."

                        st.session_state["memory"].chat_memory.add_message(AIMessage(content=output))

                        with st.chat_message("assistant"):
                            st.write(output)

                    except Exception as e:
                        st.error(f"Erro na execução do agente: {str(e)}")

