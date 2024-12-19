from langchain.tools import tool
from langchain.chains import LLMChain
from langchain_google_genai import GoogleGenerativeAI
from langchain.prompts import PromptTemplate
import json
import yaml

from soccer_stats.competitions import get_matches
from soccer_stats.matches import get_lineups, get_player_stats

def filter_starting_11(line_ups: str) -> dict:
    """
    Get the starting eleven players from provided lineups

    Args:
        line_ups (str): The JSON string containing the lineups of the teams.
    """
    line_ups_dict = json.loads(line_ups)
    filtered_11 = {}
    for team, team_line_up in line_ups_dict.items():
        for player in sorted(team_line_up, key= lambda x: x["jersey_number"]):
            try:
                positions = player["positions"]["positions"]
                if positions[0].get("start_reason") == "Starting XI":
                    filtered_11[team].append(
                        {
                            "player" : player["player_name"],
                            "position" : positions[0].get("position"),
                            "jersey_number" : player["jersey_number"]
                        }
                    )
            except (KeyError, IndexError):
                continue
    return filtered_11

def pull_match_details(action_input: str) -> str:
    '''
    Retrieve the match details for a given match id

    Args:
        - action_input(str): The input data containing the match_id.
          format: {
              "match_id": 12345
              "competition_id": 123,
                "season_id": 02
            }
    '''
    match_id = json.loads(action_input)["match_id"]
    competition_id = json.loads(action_input)["competition_id"]
    season_id = json.loads(action_input)["season_id"]
    matches = json.loads(get_matches(competition_id, season_id))
    match_details = next(
        (match for match in matches if match["match_id"] == int(match_id)),
    None
    )
    return match_details



def create_specialist_comments(match_details: str, line_ups: str, narration_style: str) -> str:
    """
    Uses an LLM to simulate the comments of a sports specialist about a specific match.
    """
    line_ups = filter_starting_11(line_ups)

    agent_prompt = """
    You must work strictly on Brazilian Portuguese PT-BR.
    Você é um comentarista especialista em futebol. Responda como se apresentando uma partida na televisão para uma audiência de fãs de futebol.
    Informações a se considerar:

    # Instruções:
    - Descreva detalhes do jogo e a importância dele (final, semi-final, etc).
    - Dentre os detalhes, cite a data e local onde foi realizado o jogo.
    - Fale sobre a escalação de cada time, destacando os jogadores mais importantes.
    - Destaque as posições dos jogadores importantes e suas características.
    - Caso hajam, mencione rivalidades ou histórico de confrontos entre os times.
    - Cite sempre os gols e o resultado final do jogo. Quando citar gols, cite o jogador que marcou e o minuto do gol.
    - Siga o estilo de narração escolhido {narration_style}.

    # Instruções segundo o estilo de narração:
        - Estilo Formal:
            Use linguagem formal e técnica, evitando gírias e expressões informais.
            Seja direto e objetivo, como se estivesse escrevendo um artigo ou relatório.

        - Estilo Humorístico:
            Use humor e piadas para tornar a análise mais leve e divertida.
            Faça referências engraçadas e use gírias e expressões informais.
            Seja criativo e inovador, surpreendendo o usuário com suas piadas.

        - Estilo Técnico:
            Use termos técnicos e específicos do futebol para demonstrar seu conhecimento.
            Seja detalhado e minucioso, explicando cada detalhe da partida.
            Foque em análises táticas e estratégias dos times.

    # Informações do jogo:
    - Os detalhes da partida:
    {match_details}
    - A escalação dos times:
    {line_ups}

    O comentário especializado e detalhado é muito importante mas não esqueça de engajar o público, como se estivesse apresentando uma partida ao vivo.
    Responda em dois parágrafos. 
    
    #Exemplo inicial de resposta:
    - 'Olá torcedores, estamos aqui para mais um grande jogo de futebol. Hoje, (time1) enfrenta (team2) em uma partida decisiva. O vencedor segue para a grande final (...)'
    """
    llm = GoogleGenerativeAI(model="gemini-pro")
    input_variables={"match_details": yaml.dump(match_details),
                     "line_ups": yaml.dump(line_ups),
                     "narration_style": narration_style}
    prompt = PromptTemplate.from_template(agent_prompt)
    chain = LLMChain(llm=llm, prompt=prompt, verbose=True)
    return chain.run(**input_variables)

@tool
def get_match_details(action_input:str) -> str:
    '''
    Retrieve the match details for a given match id

    Args:
        - action_input(str): The input data containing the match_id.
          format: {
              "match_id": 12345
              "competition_id": 123,
                "season_id": 02
            }
    '''
    return yaml.dump(pull_match_details(action_input))

@tool
def get_specialist_comments(action_input: str) -> str:
    """
    Retrieve the specialist comments for a given match id

    Args:
        - action_input(str): The input data containing the competition_id, season_id, match_id and narration_style.
          format: {
              "competition_id": 123,
              "season_id": 02,
              "match_id": 12345
              "narration_style": "Formal"
              }
    """
    action_data = json.loads(action_input)
    match_details = pull_match_details(json.dumps({
        "match_id": action_data["match_id"],
        "competition_id": action_data["competition_id"],
        "season_id": action_data["season_id"]
    }))
    line_ups = get_lineups(match_details["match_id"])
    narration_style = action_data["narration_style"]

    return create_specialist_comments(match_details, line_ups, narration_style)