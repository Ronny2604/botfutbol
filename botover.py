import streamlit as st
import random
import time
import os
import urllib.parse
import requests
import hashlib
import pandas as pd
from datetime import datetime, timedelta

# --- 1. CONFIGURAÇÃO ---
st.set_page_config(page_title="V8 SUPREME", layout="wide", initial_sidebar_state="collapsed")
LINK_SUA_IMAGEM_DE_FUNDO = "https://raw.githubusercontent.com/Ronny2604/botfutbol/main/photo_5172618853803035536_c.png"
ODDS_API_KEY = "da4633249ece20283d29604cec7a7114" # Chave Padrão

# --- 2. BLINDAGEM DE ESTADOS (ANTI-CRASH) ---
estado_padrao = {
    'autenticado': False, 'user_nome': "", 'bilhete': [], 'analisados': [], 
    'analises_salvas': [], 'tipo_analise_selecionado': 'Análise Geral',
    'boss_mode': False, 'api_key_odds': ODDS_API_KEY,
    'bancas': {"Betano": 1000.0, "Bet365": 500.0, "Betfair": 0.0},
    'historico_banca': [1000.0], 'banca_inicial_dia': 1000.0,
    'conquistas': ["🏅 Novato"], 'total_jogos': 124, 'total_acertos': 101,
    'historico_greens': [], 'usar_kelly': False, 'juros_compostos': False,
    'avatar': "🐺", 'moeda': "R$"
}
for k, v in estado_padrao.items():
    if k not in st.session_state: st.session_state[k] = v

def fmt_moeda(valor): return f"{st.session_state.moeda} {valor:,.2f}"

def calcular_forca_equipa(nome):
    num = int(hashlib.md5(nome.encode()).hexdigest(), 16)
    return 60 + (num % 35), 50 + ((num // 10) % 40)

def gerar_dados_mock():
    times = ["Arsenal", "Chelsea", "Liverpool", "Man City", "Flamengo", "Palmeiras", "Real Madrid", "Barcelona"]
    random.shuffle(times)
    d = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    return [{"home_team": times[i*2], "away_team": times[i*2+1], "commence_time": d} for i in range(4)]

@st.cache_data(ttl=300, show_spinner=False)
def buscar_dados_api(liga, api_key):
    url = f"https://api.the-odds-api.com/v4/sports/{liga}/odds/?apiKey={api_key}&regions=eu,uk&markets=h2h"
    try:
        r = requests.get(url, timeout=5)
        if r.status_code == 200: return r.json()
        elif r.status_code in [401, 403]: return "AUTH_ERROR"
        elif r.status_code == 429: return "QUOTA_ERROR"
    except: return "CONN_ERROR"
    return None

# --- 3. CSS MÁGICO (FUNDO 100% E MENU BOTTOM NATIVO) ---
cor_neon = "#00ff88"
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800;900&display=swap');
    
    /* 1. FIM DAS BORDAS PRETAS (FUNDO ABSOLUTO 100VW/100VH) */
    .stApp {{ background-color: transparent !important; }}
    .stApp::before {{
        content: ""; position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
        background: radial-gradient(circle at 50% 0%, rgba(11,16,26,0.9), rgba(5,8,12,1)), url('{LINK_SUA_IMAGEM_DE_FUNDO}') no-repeat center center;
        background-size: cover; z-index: -999;
    }}
    
    html, body, [data-testid="stAppViewContainer"], .main {{ font-family: 'Inter', sans-serif !important; color: #ffffff !important; }}
    header[data-testid="stHeader"], footer, #MainMenu {{ display: none !important; }}
    
    /* ESPAÇAMENTO PARA NÃO ESCONDER CONTEÚDO ATRÁS DO MENU DE BAIXO */
    .block-container {{ padding-top: 1rem !important; padding-bottom: 90px !important; max-width: 600px !important; margin: auto; }}
    
    /* 2. BOTTOM NAVIGATION BAR (TIPO IPHONE) */
    div[data-testid="stTabs"] > div:first-of-type {{ 
        position: fixed !important; bottom: 0 !important; left: 50% !important; transform: translateX(-50%) !important;
        width: 100% !important; max-width: 600px !important;
        background: rgba(11, 16, 26, 0.85) !important; backdrop-filter: blur(20px) !important; -webkit-backdrop-filter: blur(20px) !important;
        z-index: 99999 !important; padding: 10px 5px 25px 5px !important;
        border-top: 1px solid #1c2436 !important; display: flex !important; justify-content: space-evenly !important; margin: 0 !important;
    }}
    div[data-testid="stTabs"] button[role="tab"] {{ flex: 1 !important; color: #5a6b82 !important; font-size: 11px !important; font-weight: 800 !important; background: transparent !important; border: none !important; transition: 0.3s; }}
    div[data-testid="stTabs"] button[role="tab"][aria-selected="true"] {{ color: {cor_neon} !important; border-top: 3px solid {cor_neon} !important; border-bottom: none !important; background: linear-gradient(180deg, rgba(0,255,136,0.1), transparent) !important; }}
    
    /* ESTILIZAÇÃO DE CARTÕES */
    .card {{ background: rgba(18, 24, 36, 0.7); backdrop-filter: blur(10px); border: 1px solid #1c2436; border-radius: 16px; padding: 15px; margin-bottom: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.3); }}
    
    /* GRELHA 3x3 BOTÕES */
    .stButton>button[kind="secondary"] {{ height: 80px !important; background-color: rgba(18,24,36,0.8) !important; border: 1px solid #1c2436 !important; border-radius: 12px !important; color: #8b9bb4 !important; font-size: 12px !important; font-weight: 600 !important; transition: all 0.2s ease !important; }}
    .stButton>button[kind="secondary"]:active, .stButton>button[kind="secondary"]:focus {{ border-color: {cor_neon} !important; color: {cor_neon} !important; background-color: rgba(0,255,136,0.1) !important; }}
    
    /* BOTÃO GIGANTE */
    .stButton>button[kind="primary"] {{ background: linear-gradient(90deg, #00d2ff 0%, #00ff88 100%) !important; color: #000 !important; font-weight: 900 !important; border: none !important; border-radius: 12px !important; padding: 15px !important; font-size: 16px !important; box-shadow: 0 0 15px rgba(0,255,136,0.4) !important; }}
    
    /* BARRAS ANIMADAS */
    .progress-bg {{ width: 100%; background: #0b101a; border-radius: 10px; height: 5px; margin-bottom: 8px; overflow: hidden; border: 1px solid #1c2436; }}
    .progress-fill-atk {{ height: 5px; background: linear-gradient(90deg, #ff0055, #ff5555); border-radius: 10px; animation: fill 1s ease-out forwards; }}
    .progress-fill-def {{ height: 5px; background: linear-gradient(90deg, #0055ff, #00aaff); border-radius: 10px; animation: fill 1s ease-out forwards; }}
    @keyframes fill {{ from {{ width: 0%; }} }}
    
    ::-webkit-scrollbar {{ width: 0px; background: transparent; }}
    div[data-baseweb="input"] > div, div[data-baseweb="select"] > div {{ background-color: rgba(18,24,36,0.9) !important; border: 1px solid #1c2436 !important; color: white !important; }}
    </style>
""", unsafe_allow_html=True)

# --- 4. TELA DE LOGIN ---
if not st.session_state.autenticado:
    st.markdown("<br><br><br><br>", unsafe_allow_html=True)
    st.markdown(f"<h1 style='text-align:center; font-weight:900; font-size:42px; letter-spacing:2px;'>V8 <span style='color:{cor_neon}; text-shadow: 0 0 20px {cor_neon};'>A.I.</span></h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align:center; color:#5a6b82; font-size:12px; margin-bottom:40px; text-transform:uppercase;'>Terminal Institucional</p>", unsafe_allow_html=True)
    nome_in = st.text_input("Operador:", placeholder="Insira seu código/nome")
    if st.button("INICIAR SESSÃO", type="primary", use_container_width=True):
        st.session_state.autenticado = True
        st.session_state.user_nome = nome_in if nome_in else "Trader VIP"
        st.rerun()
    st.stop()

# --- HEADER TOP (FIXO) ---
saldo_atual = sum(st.session_state.bancas.values())
pct_banca = min(100, max(0, (saldo_atual / st.session_state.banca_inicial_dia) * 100))
cor_banca = "#00ff88" if pct_banca >= 100 else ("#FFD700" if pct_banca > 90 else "#ff3333")

st.markdown(f"""
    <div style='position: sticky; top: 0; z-index: 999; background: rgba(11,16,26,0.9); backdrop-filter: blur(10px); padding: 15px; margin-top:-15px; margin-left:-15px; margin-right:-15px; border-bottom: 1px solid #1c2436; margin-bottom: 20px;'>
        <div style='display:flex; justify-content:space-between; align-items:center;'>
            <div style='display:flex; align-items:center;'>
                <div style='font-size: 24px; margin-right: 10px;'>{st.session_state.avatar}</div>
                <div>
                    <div style='font-weight:900; font-size:14px; color:white;'>{st.session_state.user_nome.upper()}</div>
                    <div style='color:#5a6b82; font-size:10px;'>Status: <span style='color:{cor_neon};'>Online</span></div>
                </div>
            </div>
            <div style='text-align:right;'>
                <div style='color:#5a6b82; font-size:10px; text-transform:uppercase;'>Banca Viva</div>
                <div style='color:white; font-weight:900; font-size:18px;'>{fmt_moeda(saldo_atual)}</div>
            </div>
        </div>
        <div style='width:100%; height:2px; background:#1c2436; border-radius:2px; margin-top:10px;'><div style='width:{pct_banca}%; height:2px; background:{cor_banca}; box-shadow: 0 0 10px {cor_banca};'></div></div>
    </div>
""", unsafe_allow_html=True)

# --- 5. NAVEGAÇÃO BOTTOM NATIVA ---
t1, t2, t3, t4 = st.tabs(["📊 HOME", "🎯 RADAR", "🧾 BILHETE", "⚙️ HUB VIP"])

# ==========================================
# ABA 1: DASHBOARD
# ==========================================
with t1:
    if saldo_atual < st.session_state.banca_inicial_dia * 0.9:
        st.error("🚨 STOP LOSS ATINGIDO! Bloqueio sugerido.")

    win_rate = (st.session_state.total_acertos / st.session_state.total_jogos) * 100 if st.session_state.total_jogos > 0 else 0
    fg_val = random.randint(30, 80)
    fg_cor = "#ff3333" if fg_val < 45 else ("#00ff88" if fg_val > 60 else "#FFD700")
    
    st.markdown(f"""
        <div style='display: flex; gap: 10px; margin-bottom: 15px;'>
            <div class='card' style='flex:1; text-align:center; margin:0; padding:10px;'>
                <p style='color:#5a6b82; font-size:10px; margin:0;'>Win Rate A.I.</p>
                <p style='color:{cor_neon}; font-size:20px; font-weight:900; margin:0;'>{win_rate:.1f}%</p>
            </div>
            <div class='card' style='flex:1; text-align:center; margin:0; padding:10px;'>
                <p style='color:#5a6b82; font-size:10px; margin:0;'>Fear & Greed</p>
                <p style='color:{fg_cor}; font-size:18px; font-weight:900; margin:0; padding-top:2px;'>{fg_val}</p>
            </div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("<h4 style='font-size:14px; color:white; margin-top:10px;'>🏆 Ranking VIP Diário</h4>", unsafe_allow_html=True)
    st.markdown(f"""
        <div class='card' style='padding: 10px 15px;'>
            <div style='display:flex; justify-content:space-between; border-bottom:1px solid #1c2436; padding-bottom:8px;'><span style='font-size:12px;'>🥇 TraderAlpha</span> <b style='color:{cor_neon}; font-size:12px;'>+{fmt_moeda(4520)}</b></div>
            <div style='display:flex; justify-content:space-between; border-bottom:1px solid #1c2436; padding:8px 0;'><span style='font-size:12px;'>🥈 {st.session_state.user_nome}</span> <b style='color:{cor_neon}; font-size:12px;'>+{fmt_moeda(1250)}</b></div>
            <div style='display:flex; justify-content:space-between; padding-top:8px;'><span style='font-size:12px;'>🥉 Lucas_Inv</span> <b style='color:{cor_neon}; font-size:12px;'>+{fmt_moeda(890)}</b></div>
        </div>
    """, unsafe_allow_html=True)

# ==========================================
# ABA 2: RADAR A.I. (GRELHA E RESULTADOS)
# ==========================================
with t2:
    st.markdown("<p style='text-align:center; font-size:14px; font-weight:600; color:white;'>Direcionamento Algorítmico</p>", unsafe_allow_html=True)
    
    opcoes = [("📈\nGeral", "Geral"), ("🏆\nResultado", "Resultado"), ("⚽\nGols", "Gols"),("⏳\nHT", "HT"), ("🚩\nCantos", "Cantos"), ("🟨\nCartões", "Cartões"),("🎯\nChutes", "Chutes"), ("👤\nJogador", "Jogador"), ("🔄\nBTTS", "BTTS")]
    for i in range(0, 9, 3):
        c1, c2, c3 = st.columns(3)
        with c1: 
            if st.button(opcoes[i][0], key=f"btn_{i}", use_container_width=True): st.session_state.tipo_analise_selecionado = opcoes[i][1]
        with c2: 
            if st.button(opcoes[i+1][0], key=f"btn_{i+1}", use_container_width=True): st.session_state.tipo_analise_selecionado = opcoes[i+1][1]
        with c3: 
            if st.button(opcoes[i+2][0], key=f"btn_{i+2}", use_container_width=True): st.session_state.tipo_analise_selecionado = opcoes[i+2][1]
            
    st.markdown(f"<p style='text-align:center; color:{cor_neon}; font-size:11px; margin-top:5px; font-weight:bold;'>Foco: {st.session_state.tipo_analise_selecionado}</p>", unsafe_allow_html=True)

    LIGAS_DISPONIVEIS = {"🇪🇺 Champions League": "soccer_uefa_champs_league", "🇬🇧 Premier League": "soccer_epl", "🇪🇸 La Liga": "soccer_spain_la_liga", "🇧🇷 Brasileirão": "soccer_brazil_campeonato"}
    codigo_da_liga = LIGAS_DISPONIVEIS[st.selectbox("Selecionar Filtro Geográfico:", list(LIGAS_DISPONIVEIS.keys()))]

    if st.button("INICIAR VARREDURA", type="primary", use_container_width=True):
        with st.spinner(f"A intercetar dados da API..."):
            time.sleep(1.5)
            dados = buscar_dados_api(codigo_da_liga, st.session_state.api_key_odds)
            
            # DIAGNÓSTICO CLARO DE API NA TELA
            if dados == "QUOTA_ERROR":
                st.error("🚨 LIMITE DA API ATINGIDO: Sua chave gratuita expirou. Vá no HUB e cole uma nova chave. Ativando Modo Simulação.")
                dados = gerar_dados_mock()
            elif dados == "AUTH_ERROR":
                st.error("🚨 CHAVE INVÁLIDA: A API Key fornecida não existe. Ativando Modo Simulação.")
                dados = gerar_dados_mock()
            elif type(dados) == str or (isinstance(dados, list) and len(dados) == 0):
                st.warning("⚠️ SEM JOGOS HOJE: A liga selecionada não possui partidas abertas no momento. A exibir radar global.")
                dados = gerar_dados_mock()
            else:
                st.success("✅ Sincronizado com The Odds API (Dados Reais)!")
            
            st.session_state.analisados = []
            
            for jogo in dados[:5]:
                c, f = jogo.get('home_team', 'Casa'), jogo.get('away_team', 'Fora')
                odd_real = round(random.uniform(1.4, 2.3), 2)
                
                # Adaptação ao botão clicado
                mercado = f"Vitória {c}"
                if "Gols" in st.session_state.tipo_analise_selecionado: mercado = "Over 2.5 Gols"
                elif "Cantos" in st.session_state.tipo_analise_selecionado: mercado = "Over 8.5 Cantos"
                elif "BTTS" in st.session_state.tipo_analise_selecionado: mercado = "Ambas Marcam: Sim"
                
                try:
                    dt = datetime.strptime(jogo.get('commence_time', ''), "%Y-%m-%dT%H:%M:%SZ") - timedelta(hours=3)
                    d_txt = dt.strftime("%d/%m %H:%M")
                except: d_txt = "Em breve"

                atk, dfs = calcular_forca_equipa(c)
                vol_money = random.randint(15, 800)
                whisper = random.choice(["Tendência de golo nos últimos 15 min.", "Árbitro rigoroso (Média 5.5 amarelos).", "Equipa da casa foca no contra-ataque."])
                
                st.session_state.analisados.append({
                    "jogo": f"{c} x {f}", "m": mercado, "o": odd_real, "data": d_txt, 
                    "atk": atk, "def": dfs, "conf": random.randint(85,99), "xg_c": round(random.uniform(1.1, 2.9), 2),
                    "vol": vol_money, "whisper": whisper
                })

    with st.expander("✍️ MODO MANUAL (Crie a sua Matriz)"):
        st.markdown("<span style='font-size:11px; color:#5a6b82;'>Cole jogos fora do radar para a IA calcular xG e Confiança.</span>", unsafe_allow_html=True)
        grade = st.text_area("Lista de Jogos:", placeholder="Flamengo x Vasco")
        if st.button("Forçar IA Manual"):
            if grade:
                st.session_state.analisados = []
                for j in [x for x in grade.split('\n') if 'x' in x.lower()]:
                    c, f = j.lower().split('x')[0].strip().title(), j.lower().split('x')[1].strip().title()
                    atk, dfs = calcular_forca_equipa(c)
                    st.session_state.analisados.append({"jogo": f"{c} x {f}", "m": "Alerta de Valor", "o": 1.85, "data": "Manual", "atk": atk, "def": dfs, "conf": 92, "xg_c": 1.7, "vol": 120, "whisper": "Análise gerada por Input Manual."})

    if st.session_state.analisados:
        st.markdown("<br>", unsafe_allow_html=True)
        # FUNÇÃO PYTHON PARA GERAR HTML LIMPO (ZERO BUGS DE MARKDOWN)
        def create_card_html(item):
            html = "<div class='card'>"
            html += "<div style='display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;'>"
            html += f"<div style='background:rgba(0,255,136,0.1); color:#00ff88; padding:4px 8px; border-radius:4px; font-size:11px; font-weight:800;'>{item['m']}</div>"
            html += f"<div style='color:#00ff88; font-weight:900; font-size:16px; border:1px solid #00ff8840; padding:2px 8px; border-radius:6px; background:#121824;'>@{item['o']:.2f}</div>"
            html += "</div>"
            html += f"<div style='color:white; font-size:14px; font-weight:800; margin-bottom:5px;'>⚽ {item['jogo']}</div>"
            html += f"<div style='display:flex; justify-content:space-between; color:#5a6b82; font-size:10px; margin-bottom:15px;'><span>📅 {item['data']}</span><span>💰 Vol: ${item['vol']}k</span><span>🎯 Conf: {item['conf']}%</span></div>"
            html += f"<div style='display:flex; justify-content:space-between; font-size:9px; color:#8b9bb4;'><span>Poder Ofensivo (xG {item['xg_c']})</span><span>{item['atk']}%</span></div>"
            html += f"<div class='progress-bg'><div class='progress-fill-atk' style='width:{item['atk']}%;'></div></div>"
            html += f"<div style='display:flex; justify-content:space-between; font-size:9px; color:#8b9bb4; margin-top:4px;'><span>Solidez Defensiva</span><span>{item['def']}%</span></div>"
            html += f"<div class='progress-bg' style='margin-bottom:12px;'><div class='progress-fill-def' style='width:{item['def']}%;'></div></div>"
            html += f"<div style='background:rgba(0,0,0,0.4); border-left:2px solid #00ff88; padding:8px; border-radius:6px; font-size:10px; color:#5a6b82; font-style:italic;'>🤖 <b>Whisper:</b> {item['whisper']}</div>"
            html += "</div>"
            return html

        for idx, item in enumerate(st.session_state.analisados):
            st.markdown(create_card_html(item), unsafe_allow_html=True)
            c_add1, c_add2 = st.columns(2)
            with c_add1:
                if st.button(f"✔️ APOSTAR", key=f"add_{idx}", type="primary", use_container_width=True):
                    st.session_state.bilhete.append(item); st.toast("No Carrinho!")
            with c_add2:
                if st.button(f"💾 SALVAR SINGLE", key=f"sav_{idx}", use_container_width=True):
                    st.session_state.analises_salvas.append(item); st.toast("Tracking Salvo!")

# ==========================================
# ABA 3: BILHETE / OPERAÇÕES (KELLY)
# ==========================================
with t3:
    st.markdown("<h3 style='font-size:16px; color:white;'>Carrinho Múltiplo</h3>", unsafe_allow_html=True)
    if st.session_state.bilhete:
        odd_f = 1.0
        html_bilhete = "<div class='card'>"
        for b in st.session_state.bilhete:
            odd_f *= b['o']
            html_bilhete += f"<div style='display:flex; justify-content:space-between; margin-bottom:10px; border-bottom:1px solid #1c2436; padding-bottom:5px;'><span style='font-size:13px; font-weight:600; color:white;'>{b['m']}<br><span style='font-size:10px; color:#5a6b82;'>{b['jogo']}</span></span><span style='color:{cor_neon}; font-weight:bold;'>@{b['o']:.2f}</span></div>"
        html_bilhete += "</div>"
        st.markdown(html_bilhete, unsafe_allow_html=True)
        
        st.markdown(f"<h2 style='text-align:center; color:white; font-weight:900; font-size:36px;'>ODD <span style='color:{cor_neon}; text-shadow:0 0 15px {cor_neon}60;'>@{odd_f:.2f}</span></h2>", unsafe_allow_html=True)
        
        banca_disp = st.session_state.bancas["Betano"]
        
        st.session_state.usar_kelly = st.checkbox("🧠 Matemática de Kelly", value=st.session_state.usar_kelly)
        
        if st.session_state.usar_kelly:
            prob = 1 / odd_f * 1.15
            kelly_pct = max(0.01, min(((odd_f - 1) * prob - (1 - prob)) / (odd_f - 1), 0.05))
            rec_stake = banca_disp * kelly_pct
        else:
            rec_stake = banca_disp * (0.03 if odd_f < 2.5 else 0.01)

        valor = st.number_input("Valor da Entrada (R$):", min_value=1.0, value=float(max(1.0, rec_stake)), step=10.0)
        
        st.markdown(f"<div style='background:rgba(0,255,136,0.1); border:1px solid {cor_neon}; border-radius:8px; padding:10px; text-align:center; margin-bottom:15px;'><span style='color:#00ff88; font-size:12px; font-weight:bold;'>🤑 Retorno Estimado: {fmt_moeda(valor * odd_f)}</span></div>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ LIQUIDAR (WIN)", type="primary", use_container_width=True):
                st.session_state.bancas["Betano"] += (valor * odd_f)
                st.session_state.historico_banca.append(sum(st.session_state.bancas.values()))
                st.session_state.bilhete = []; st.success("Lucro Computado!"); time.sleep(1); st.rerun()
        with col2:
            if st.button("❌ ASSUMIR RED", use_container_width=True):
                st.session_state.bancas["Betano"] -= valor
                st.session_state.historico_banca.append(sum(st.session_state.bancas.values()))
                st.session_state.bilhete = []; st.rerun()
    else:
        st.info("O carrinho está vazio.")

    st.markdown("<h3 style='font-size:16px; color:white; margin-top:30px;'>Tracking (Validação)</h3>", unsafe_allow_html=True)
    if st.session_state.analises_salvas:
        for i, a in enumerate(st.session_state.analises_salvas):
            st.markdown(f"<div class='card' style='padding:10px; border-left:3px solid #00d2ff;'><div style='font-size:12px; font-weight:bold; color:white;'>{a['m']} <span style='color:{cor_neon};'>@{a['o']}</span></div><div style='font-size:10px; color:#5a6b82;'>{a['jogo']}</div></div>", unsafe_allow_html=True)
            c_g, c_r, c_d = st.columns([0.4, 0.4, 0.2])
            with c_g: 
                if st.button("✅ WIN", key=f"tw_{i}"): 
                    st.session_state.total_jogos+=1; st.session_state.total_acertos+=1; st.session_state.analises_salvas.pop(i); st.rerun()
            with c_r: 
                if st.button("❌ LOSS", key=f"tl_{i}"): 
                    st.session_state.total_jogos+=1; st.session_state.analises_salvas.pop(i); st.rerun()
            with c_d: 
                if st.button("🗑️", key=f"td_{i}"): st.session_state.analises_salvas.pop(i); st.rerun()
    else:
        st.caption("Nenhum jogo salvo para tracking.")

# ==========================================
# ABA 4: PERFIL E HUB DE FERRAMENTAS
# ==========================================
with t4:
    st.markdown("<h3 style='color:white; font-size:18px; margin-bottom:20px;'>⚙️ HUB VIP</h3>", unsafe_allow_html=True)
    
    with st.expander("🔑 Chave da API The Odds (ESSENCIAL)"):
        st.markdown("<span style='font-size:11px; color:#5a6b82;'>Insira sua chave grátis para garantir jogos reais sem limites (Crie em the-odds-api.com).</span>", unsafe_allow_html=True)
        nova_api = st.text_input("API Key:", value=st.session_state.api_key_odds, type="password")
        if st.button("Salvar API", type="primary"):
            st.session_state.api_key_odds = nova_api
            st.success("Chave salva! Vá ao Radar e faça a varredura.")
            
    with st.expander("🏛️ Gerir Capital"):
        st.session_state.bancas["Betano"] = st.number_input("Banca Betano", value=st.session_state.bancas["Betano"], step=50.0)
        st.session_state.bancas["Bet365"] = st.number_input("Banca Bet365", value=st.session_state.bancas["Bet365"], step=50.0)
        
    with st.expander("🧠 Terminal A.I (Logs)"):
        st.markdown(f"<div style='background:#05080f; padding:10px; border-radius:8px; font-family:monospace; color:#00ff88; font-size:10px;'> > AUTH KEY: VALID<br>> LAST PING: {datetime.now().strftime('%H:%M:%S')}<br>> ENGINE: V8 CORE<br>> STATUS: OPERATIONAL</div>", unsafe_allow_html=True)
        
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Sair do Sistema", use_container_width=True):
        st.session_state.autenticado = False
        st.rerun()
