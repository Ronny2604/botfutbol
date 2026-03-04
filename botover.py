import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import hashlib
import random

st.set_page_config(layout="wide")

st.title("Análise Esportiva Avançada")
st.markdown("""
    <style>
    .stProgress > div > div > div > div {
        background-color: #00ff88;
    }
    </style>""", unsafe_allow_html=True)

# --- 1. CONFIGURAÇÕES E FUNÇÕES DE DADOS ---

API_KEY_PADRAO = "da4633249ece20283d29604cec7a7114"

LIGAS_DISPONIVEIS = {
    "🇧🇷 Brasileirão Série A": "soccer_brazil_campeonato",
    "🇬🇧 Premier League": "soccer_epl",
    "🇪🇸 La Liga": "soccer_spain_la_liga",
    "🇮🇹 Serie A": "soccer_italy_serie_a",
    "🇪🇺 Champions League": "soccer_uefa_champs_league"
}

MERCADOS_DISPONIVEIS = {
    "🏆 Resultado Final (1X2)": "h2h",
    "⚽ Total de Gols (Mais/Menos)": "totals",
}

@st.cache_data(ttl=600) # Cache de 10 minutos
def carregar_partidas_da_api(api_key, sport_key, region="br", markets="h2h,totals"):
    """Busca partidas da API The Odds, agora com múltiplos mercados."""
    url = f"https://api.the-odds-api.com/v4/sports/{sport_key}/odds/?apiKey={api_key}&regions={region}&markets={markets}"
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Erro ao conectar na API de Odds: {e}")
        return []

def extrair_dados_partida(partida):
    """Processa a estrutura de dados de uma partida para extrair odds dos mercados."""
    dados = {
        "id": partida['id'],
        "data": datetime.fromisoformat(partida['commence_time'].replace('Z', '')).strftime('%d/%m %H:%M'),
        "partida_nome": f"{partida['home_team']} vs {partida['away_team']}",
        "time_casa": partida['home_team'],
        "time_fora": partida['away_team'],
        "odds_1x2": {},
        "odds_gols": {}
    }
    
    for bookmaker in partida.get('bookmakers', []):
        for market in bookmaker.get('markets', []):
            # Extrai odds do Resultado Final
            if market['key'] == 'h2h':
                for outcome in market['outcomes']:
                    if outcome['name'] == partida['home_team']:
                        dados['odds_1x2']['casa'] = outcome['price']
                    elif outcome['name'] == partida['away_team']:
                        dados['odds_1x2']['fora'] = outcome['price']
                    elif 'draw' in outcome['name'].lower():
                        dados['odds_1x2']['empate'] = outcome['price']
                
            # Extrai odds de Gols (Over/Under 2.5)
            elif market['key'] == 'totals':
                for outcome in market['outcomes']:
                    if outcome['point'] == 2.5: # Foco na linha de 2.5 gols
                        if outcome['name'].lower() == 'over':
                            dados['odds_gols']['mais_2.5'] = outcome['price']
                        elif outcome['name'].lower() == 'under':
                            dados['odds_gols']['menos_2.5'] = outcome['price']
    return dados

# --- 2. INTERFACE PRINCIPAL ---

st.sidebar.header("⚙️ Controles de Análise")
api_key = st.sidebar.text_input("Sua Chave The Odds API", API_KEY_PADRAO, type="password")
liga_selecionada_nome = st.sidebar.selectbox("Selecione a Liga", list(LIGAS_DISPONIVEIS.keys()))
mercado_selecionado_nome = st.sidebar.selectbox("Selecione o Mercado para Análise", list(MERCADOS_DISPONIVEIS.keys()))

liga_selecionada_key = LIGAS_DISPONIVEIS[liga_selecionada_nome]
mercado_selecionado_key = MERCADOS_DISPONIVEIS[mercado_selecionado_nome]

partidas_raw = carregar_partidas_da_api(api_key, liga_selecionada_key)

if partidas_raw:
    st.markdown(f"## ⚽ Partidas - {liga_selecionada_nome}")
    
    dados_processados = [extrair_dados_partida(p) for p in partidas_raw]
    df_partidas = pd.DataFrame(dados_processados)

    # Exibe a tabela de jogos com as odds principais
    tabela_display = []
    for _, row in df_partidas.iterrows():
        tabela_display.append({
            "Data": row['data'],
            "Partida": row['partida_nome'],
            "Odd Casa": row['odds_1x2'].get('casa', '-'),
            "Odd Empate": row['odds_1x2'].get('empate', '-'),
            "Odd Fora": row['odds_1x2'].get('fora', '-'),
            "Mais 2.5": row['odds_gols'].get('mais_2.5', '-'),
            "Menos 2.5": row['odds_gols'].get('menos_2.5', '-')
        })
    st.dataframe(pd.DataFrame(tabela_display), use_container_width=True, hide_index=True)

    st.markdown("---")
    st.markdown(f"## 📊 Análise Detalhada - {mercado_selecionado_nome}")

    partida_selecionada_nome = st.selectbox("Selecione uma partida para analisar:", options=df_partidas['partida_nome'])

    if partida_selecionada_nome:
        partida_details = df_partidas[df_partidas['partida_nome'] == partida_selecionada_nome].iloc[0]
        odds_1x2 = partida_details['odds_1x2']
        odds_gols = partida_details['odds_gols']

        # --- ANÁLISE PARA O MERCADO SELECIONADO ---

        if mercado_selecionado_key == 'h2h' and odds_1x2:
            st.subheader(f"Análise de Resultado: {partida_details['partida_nome']}")
            
            try:
                # Converte probabilidades implícitas em "força"
                prob_casa = 1 / odds_1x2.get('casa', 100)
                prob_fora = 1 / odds_1x2.get('fora', 100)
                
                # Normaliza para criar uma barra de "Favoritismo"
                total_prob = prob_casa + prob_fora
                favoritismo_casa = prob_casa / total_prob
                
                st.progress(favoritismo_casa, text=f"Favoritismo: {partida_details['time_casa']} ({favoritismo_casa:.0%}) vs {partida_details['time_fora']} ({1-favoritismo_casa:.0%})")

                col1, col2, col3 = st.columns(3)
                col1.metric("Vitória Casa", odds_1x2.get('casa', 'N/A'))
                col2.metric("Empate", odds_1x2.get('empate', 'N/A'))
                col3.metric("Vitória Fora", odds_1x2.get('fora', 'N/A'))

                # Sugestão baseada em valor (comparando odds com favoritismo)
                sugestao = "Equilíbrio. Analisar outros fatores."
                if favoritismo_casa > 0.65 and odds_1x2.get('casa', 100) < 2.0:
                    sugestao = f"O favoritismo do {partida_details['time_casa']} é forte e refletido nas odds."
                elif favoritismo_casa > 0.55 and odds_1x2.get('casa', 100) > 2.2:
                    sugestao = f"Odd de valor para o {partida_details['time_casa']}. O mercado pode estar subestimando-o."
                
                st.success(f"**Sugestão 1X2:** {sugestao}")

            except (TypeError, ZeroDivisionError):
                st.warning("Não foi possível calcular a análise de resultado devido a dados de odds ausentes.")


        elif mercado_selecionado_key == 'totals' and odds_gols:
            st.subheader(f"Análise de Gols: {partida_details['partida_nome']}")

            try:
                # Converte odds de gols em probabilidade
                prob_mais_2_5 = 1 / odds_gols.get('mais_2.5', 100)
                prob_menos_2_5 = 1 / odds_gols.get('menos_2.5', 100)
                
                total_prob_gols = prob_mais_2_5 + prob_menos_2_5
                tendencia_over = prob_mais_2_5 / total_prob_gols

                st.progress(tendencia_over, text=f"Tendência para 'Mais de 2.5 Gols' ({tendencia_over:.0%})")
                
                col1, col2 = st.columns(2)
                col1.metric("Mais de 2.5 Gols", odds_gols.get('mais_2.5', 'N/A'))
                col2.metric("Menos de 2.5 Gols", odds_gols.get('menos_2.5', 'N/A'))

                # Sugestão baseada na tendência
                sugestao = "Mercado de gols equilibrado."
                if tendencia_over > 0.6:
                    sugestao = f"Forte tendência para um jogo com mais de 2.5 gols."
                elif tendencia_over < 0.4:
                    sugestao = f"Forte tendência para um jogo com menos de 2.5 gols."

                st.info(f"**Sugestão de Gols:** {sugestao}")

            except (TypeError, ZeroDivisionError):
                 st.warning("Não foi possível calcular a análise de gols devido a dados de odds ausentes.")
        
        else:
            st.warning(f"Os dados para o mercado '{mercado_selecionado_nome}' não estão disponíveis para esta partida.")

else:
    st.warning("Nenhuma partida encontrada para a liga selecionada. Verifique sua chave de API ou a disponibilidade de jogos.")

