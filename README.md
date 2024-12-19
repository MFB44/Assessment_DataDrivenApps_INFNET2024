# Assessment Disciplina Data Driven Apps - INFNET Ciência de Dados 2024

## Descrição e Objetivo
Este projeto visa mostrar informações sobre partidas de futebol, detalhes sobre os jogadores e eventos da partida.
Para isso foi utilizado principalmente streamlit, mas também rotas em FastAPI.

## Instruções de configuração de ambiente
- Instale as bibliotecas necessárias incluídas no arquivo requirements.txt com o código: 'pip install -r requirements.txt'.
- Crie um arquivo '.env' para suas chaves de API necessárias.
- Chave de API Gemini: Visite "https://ai.google.dev/gemini-api/docs/api-key?hl=pt-br", crie sua chave e insira no arquivo '.env' com a chave "GEMINI_API_KEY".
- Chave de API Serp: Visite "https://serpapi.com", crie sua chave e insira no arquivo '.env' com a chave "SERPAPI_API_KEY".

## Exemplos
- FastAPI : 
- Insira um "match_id" e receba um resumo da partida.
- Streamlit:
- Escolha uma competição, temporada e partida, e então selecione jogadores de cada time para compará-los.
