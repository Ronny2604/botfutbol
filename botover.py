import streamlit as st
import random
import time
import urllib.parse
import requests
import hashlib
import pandas as pd
from datetime import datetime, timedelta

# --- 1. CONFIGURAÇÃO BASE ---
st.set_page_config(page_title="V8 SUPREME PRO", layout="wide", initial_sidebar_state="collapsed")
LINK_IMG_FUNDO = "https://raw.githubusercontent.com/Ronny2604/botfutbol/main/photo_5172618853803035536_c.png"
API_KEY_PADRAO = "da4633249ece20283d29604cec7a7114"

# --- 2. INICIALIZAÇÃO FORÇA BRUTA (O FIM DO ATTRIBUTE ERROR) ---
if 'autenticado' not in st.session_state: st.session_state.autenticado = False
if 'user_nome' not in st.session_state: st.session_state.user_nome = ""
if 'bilhete' not in st.session_state: st.session_state.bilhete = []
if 'analisados' not in st.session_state: st.session_state.analisados = []
if 'analises_salvas' not in st.session_state: st.session_state.analises_salvas = []
if 'tipo_analise_selecionado' not in st.session_state: st.session_state.tipo_analise_selecionado = 'Análise Geral'
if 'api_key_odds' not in st.session_state: st.session_state.api_key_odds = API_KEY_PADRAO
if 'tema_escolhido' not in st.session_state: st.session_state.tema_escolhido = "🟢 Verde Hacker"
if 'avatar' not in st.session_state: st.session_state.avatar = "🐺"
if 'moeda' not in st.session_state: st.session_state.moeda = "R$"
if 'juros_compostos' not in st.session_state: st.session_state.juros_compostos = False
if 'usar_kelly' not in st.session_state: st.session_state.usar_kelly = False
if 'bancas' not in st.session_state: st.session_state.bancas = {"Betano": 1000.0, "Bet365": 500.0, "Betfair": 0.0}
if 'historico_banca' not in st.session_state: st.session_state.historico_banca = [1000.0]
if 'banca_inicial_dia' not in st.session_state: st.session_state.banca_inicial_dia = 1000.0
if 'total_jogos' not in st.session_state: st.session_state.total_jogos = 124
if 'total_acertos' not in st.session_state: st.session_state.total_acertos = 101
if 'historico_greens' not in st.session_state: st.session_state.historico_greens = []
if 'status_api' not in st.session_state: st.session_state.status_api = "AGUARDANDO"
if 'titulo_apostador' not in st.session_state: st.session_state.titulo_apostador = "O Estrategista"

# --- FUNÇÕES ---
def fmt_moeda(valor): return f"{st.session_state.moeda} {valor:,.2f}"

def calcular_forca_equipa(nome): 
    num = int(hashlib.md5(nome.encode()).hexdigest(), 16)
    return 60 + (num % 35), 50 + ((num // 10) % 40)

def gerar_dados_mock():
    times = ["Arsenal", "Chelsea", "Liverpool", "Man City", "Flamengo", "Palmeiras", "Real Madrid", "Barcelona"]
    random.shuffle(times)
    d = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    return [{"home_team": times[i*2], "away_team": times[i*2+1], "commence_time": d} for i in range(4)]

@st.cache_data(ttl=60, show_spinner=False)
def buscar_dados_api(liga, api_key):
    url = f"https://api.the-odds-api.com/v4/sports/{liga}/odds/?apiKey={api_key}&regions=eu,uk&markets=h2h"
    try:
        r = requests.get(url, timeout=5)
        if r.status_code == 200: return r.json()
        elif r.status_code in [401, 403]: return "AUTH_ERROR"
        elif r.status_code == 429: return "QUOTA_ERROR"
    except: return "CONN_ERROR"
    return None

def tocar_som():
    # Renderizar som sem quebras de linha
    som_html = '<audio autoplay style="display:none;"><source src="https://assets.mixkit.co/active_storage/sfx/2003/2003-preview.mp3" type="audio/mpeg"></audio>'
    st.markdown(som_html.replace('\n', ''), unsafe_allow_html=True)

# --- 3. CSS SEGURO (FIM DA TELA ESTICADA) ---
cor_neon = "#00ff88"
c_prim = "#ffffff"
c_sec = "#8b9bb4"
bg_card = "rgba(18, 24, 36, 0.85)"
border_card = "#1c2436"

# CSS injetado com replace para evitar parsing do Markdown
css_code = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800;900&display=swap');

html, body {{
    max-width: 100vw !important;
    overflow-x: hidden !important; 
    margin: 0 !important;
    padding: 0 !important;
}}

.stApp {{
    background: radial-gradient(circle at 50% 0%, rgba(11,16,26,0.9), rgba(5,8,12,1)), url('{LINK_IMG_FUNDO}') !important;
    background-size: cover !important;
    background-position: center !important;
    background-attachment: fixed !important;
    font-family: 'Inter', sans-serif !important;
    color: {c_prim} !important;
}}

header[data-testid="stHeader"], footer, #MainMenu {{ display: none !important; }}

.block-container {{ 
    padding-top: 1rem !important; 
    padding-bottom: 120px !important; 
    max-width: 600px !important; 
    margin: 0 auto !important; 
    overflow-x: hidden !important; 
}}

div[data-baseweb="input"] > div, div[data-baseweb="select"] > div, textarea {{ 
    background-color: rgba(18,24,36,0.9) !important; 
    border: 1px solid {border_card} !important; 
    color: white !important; 
    border-radius: 8px !important; 
    box-sizing: border-box !important; 
}}
.stMarkdown p, .stText p, label {{ color: {c_prim} !important; }}

/* MENU INFERIOR BLINDADO COM LEFT 0 E RIGHT 0 */
div[data-testid="stTabs"] > div:first-of-type {{ 
    position: fixed !important; 
    bottom: 0 !important; 
    left: 0 !important; 
    right: 0 !important; 
    background: rgba(11, 16, 26, 0.95) !important; 
    backdrop-filter: blur(20px) !important;
    border-top: 1px solid {border_card} !important;
    border-radius: 20px 20px 0 0 !important; 
    padding: 10px 0 25px 0 !important; 
    z-index: 99999 !important; 
    display: flex !important; 
    justify-content: space-evenly !important;
    margin: 0 !important;
    box-sizing: border-box !important;
}}
div[data-testid="stTabs"] button[role="tab"] {{ flex: 1 !important; color: {c_sec} !important; font-size: 11px !important; font-weight: 800 !important; background: transparent !important; border: none !important; padding: 10px 0 !important; transition: 0.3s; }}
div[data-testid="stTabs"] button[role="tab"][aria-selected="true"] {{ color: {cor_neon} !important; border-top: 3px solid {cor_neon} !important; background: linear-gradient(180deg, rgba(0,255,136,0.1), transparent) !important; }}

.stButton>button[kind="secondary"] {{ height: 80px !important; background-color: {bg_card} !important; border: 1px solid {border_card} !important; border-radius: 12px !important; color: {c_sec} !important; font-size: 12px !important; font-weight: 600 !important; transition: all 0.2s !important; width: 100% !important; }}
.stButton>button[kind="secondary"]:active {{ border-color: {cor_neon} !important; color: {cor_neon} !important; background-color: {cor_neon}15 !important; transform: scale(0.96) !important; }}

.stButton>button[kind="primary"] {{ background: linear-gradient(90deg, #00d2ff 0%, {cor_neon} 100%) !important; color: #000 !important; font-weight: 900 !important; border: none !important; border-radius: 12px !important; padding: 15px !important; font-size: 16px !important; box-shadow: 0 0 15px {cor_neon}50 !important; transition: all 0.2s !important; width: 100% !important; }}
.stButton>button[kind="primary"]:active {{ transform: scale(0.96) !important; box-shadow: 0 0 5px {cor_neon}80 !important; }}

.card {{ background: {bg_card}; border: 1px solid {border_card}; border-radius: 12px; padding: 15px; margin-bottom: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.3); box-sizing: border-box !important; width: 100% !important; overflow: hidden !important; }}
.badge {{ background: rgba(0,255,136,0.1); color: {cor_neon}; padding: 4px 8px; border-radius: 4px; font-size: 11px; font-weight: 800; }}
.progress-bg {{ width: 100%; background: #0b101a; border-radius: 10px; height: 5px; margin-bottom: 8px; overflow: hidden; border: 1px solid {border_card}; }}
.progress-fill-atk {{ height: 5px; background: linear-gradient(90deg, #ff0055, #ff5555); border-radius: 10px; }}
.progress-fill-def {{ height: 5px; background: linear-gradient(90deg, #0055ff, #00aaff); border-radius: 10px; }}

::-webkit-scrollbar {{ display: none !important; }}
</style>
"""
st.markdown(css_code.replace('\n', ''), unsafe_allow_html=True)

# --- 4. TELA DE LOGIN ---
if not st.session_state.autenticado:
    login_html = f"""
    <br><br><br><br>
    <h1 style='text-align:center; font-weight:900; font-size:48px; color:{c_prim};'>V8 <span style='color:{cor_neon}; text-shadow: 0 0 20px {cor_neon};'>A.I.</span></h1>
    <p style='text-align:center; color:{c_sec}; font-size:12px; margin-bottom:40px; text-transform:uppercase; letter-spacing:2px;'>Terminal de Alta Frequência</p>
    """
    st.markdown(login_html.replace('\n', ''), unsafe_allow_html=True)
    
    nome_in = st.text_input("Operador ID:", placeholder="Insira o seu nome")
    if st.button("INICIAR SESSÃO", type="primary", use_container_width=True):
        st.session_state.autenticado = True
        st.session_state.user_nome = nome_in if nome_in else "Trader"
        st.rerun()
    st.stop()

# --- 5. HEADER SEGURO ---
saldo_atual = sum(st.session_state.bancas.values())
banca_inicial = st.session_state.banca_inicial_dia
pct_banca = min(100, max(0, (saldo_atual / banca_inicial) * 100)) if banca_inicial > 0 else 0
cor_banca = cor_neon if pct_banca >= 100 else ("#FFD700" if pct_banca > 90 else "#ff3333")

header_html = f"""
<div style='position: sticky; top: 0; z-index: 999; background: rgba(11,16,26,0.95); backdrop-filter: blur(15px); padding: 15px; border-radius: 0 0 16px 16px; border-bottom: 1px solid {border_card}; margin-bottom: 20px; width: 100%; box-sizing: border-box;'>
    <div style='display:flex; justify-content:space-between; align-items:center;'>
        <div style='display:flex; align-items:center;'>
            <div style='font-size: 24px; margin-right: 10px;'>{st.session_state.avatar}</div>
            <div>
                <div style='font-weight:900; font-size:14px; color:{c_prim};'>{st.session_state.user_nome.upper()} <span style='background:{cor_neon}; color:#000; font-size:9px; padding:2px 4px; border-radius:4px;'>PRO</span></div>
                <div style='color:{c_sec}; font-size:10px;'>API: <span style='color:{cor_neon};'>{st.session_state.status_api}</span></div>
            </div>
        </div>
        <div style='text-align:right;'>
            <div style='color:{c_sec}; font-size:10px; text-transform:uppercase;'>Banca Viva</div>
            <div style='color:{c_prim}; font-weight:900; font-size:18px;'>{fmt_moeda(saldo_atual)}</div>
        </div>
    </div>
    <div style='width:100%; height:2px; background:#1c2436; border-radius:2px; margin-top:10px;'><div style='width:{pct_banca}%; height:2px; background:{cor_banca}; box-shadow: 0 0 8px {cor_banca};'></div></div>
</div>
"""
st.markdown(header_html.replace('\n', ''), unsafe_allow_html=True)

# --- 6. NAVEGAÇÃO BOTTOM ---
t1, t2, t3, t4 = st.tabs(["📊 HOME", "🎯 RADAR", "🧾 BILHETE", "⚙️ HUB"])

# ==========================================
# ABA 1: DASHBOARD
# ==========================================
with t1:
    if saldo_atual < banca_inicial * 0.9: st.error("🚨 STOP LOSS: Banca caiu mais de 10%. Proteja o seu capital.")
    if saldo_atual >= banca_inicial * 1.2: st.success("🎯 STOP WIN: Meta diária batida. Relaxe!")
    
    t_jogos = st.session_state.total_jogos
    t_acertos = st.session_state.total_acertos
    win_rate = (t_acertos / t_jogos) * 100 if t_jogos > 0 else 0
    fg_val = random.randint(30, 80)
    fg_cor = "#ff3333" if fg_val < 45 else (cor_neon if fg_val > 60 else "#FFD700")
    
    dash_html = f"""
    <div style='display: flex; gap: 10px; margin-bottom: 15px; width: 100%; box-sizing: border-box;'>
        <div class='card' style='flex:1; text-align:center; padding:15px; margin:0;'>
            <p style='color:{c_sec}; font-size:10px; margin:0;'>Win Rate A.I.</p>
            <p style='color:{cor_neon}; font-size:22px; font-weight:900; margin:0;'>{win_rate:.1f}%</p>
        </div>
        <div class='card' style='flex:1; text-align:center; padding:15px; margin:0;'>
            <p style='color:{c_sec}; font-size:10px; margin:0;'>Fear & Greed</p>
            <p style='color:{fg_cor}; font-size:22px; font-weight:900; margin:0;'>{fg_val}</p>
        </div>
    </div>
    """
    st.markdown(dash_html.replace('\n', ''), unsafe_allow_html=True)

    rank_html = f"""
    <h4 style='font-size:14px; color:{c_prim}; margin-top:10px;'>🏆 Ranking Global VIP</h4>
    <div class='card' style='padding: 15px;'>
        <div style='display:flex; justify-content:space-between; border-bottom:1px solid {border_card}; padding-bottom:8px;'><span style='font-size:12px; color:{c_prim};'>🥇 TraderAlpha</span> <b style='color:{cor_neon}; font-size:12px;'>+{fmt_moeda(4520)}</b></div>
        <div style='display:flex; justify-content:space-between; border-bottom:1px solid {border_card}; padding:8px 0;'><span style='font-size:12px; color:{c_prim};'>🥈 {st.session_state.user_nome}</span> <b style='color:{cor_neon}; font-size:12px;'>+{fmt_moeda(1250)}</b></div>
        <div style='display:flex; justify-content:space-between; padding-top:8px;'><span style='font-size:12px; color:{c_prim};'>🥉 Lucas_Inv</span> <b style='color:{cor_neon}; font-size:12px;'>+{fmt_moeda(890)}</b></div>
    </div>
    """
    st.markdown(rank_html.replace('\n', ''), unsafe_allow_html=True)

# ==========================================
# ABA 2: RADAR A.I.
# ==========================================
with t2:
    st.markdown(f"<p style='text-align:center; font-size:14px; font-weight:800; color:{c_prim}; margin:0;'>Direcionamento Algorítmico</p>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align:center; color:{cor_neon}; font-size:11px; font-weight:bold; margin-bottom:15px;'>Foco: {st.session_state.tipo_analise_selecionado}</p>", unsafe_allow_html=True)
    
    opcoes = [("📈 Análise Geral", "Análise Geral"), ("🏆 Resultado", "Resultado Final"), ("⚽ Gols", "Gols"), ("⏳ 1º Tempo", "Primeiro Tempo"), ("🚩 Escanteios", "Escanteios"), ("🔄 Ambas Marcam", "Ambas Marcam")]
    for i in range(0, 6, 2):
        c1, c2 = st.columns(2)
        with c1: 
            if st.button(opcoes[i][0], key=f"btn_{i}", use_container_width=True): st.session_state.tipo_analise_selecionado = opcoes[i][1]; st.rerun()
        with c2: 
            if st.button(opcoes[i+1][0], key=f"btn_{i+1}", use_container_width=True): st.session_state.tipo_analise_selecionado = opcoes[i+1][1]; st.rerun()

    LIGAS = {"🇪🇺 Champions League": "soccer_uefa_champs_league", "🇬🇧 Premier League": "soccer_epl", "🇪🇸 La Liga": "soccer_spain_la_liga", "🇧🇷 Brasileirão": "soccer_brazil_campeonato"}
    codigo_da_liga = LIGAS[st.selectbox("Selecionar Filtro Geográfico:", list(LIGAS.keys()))]

    if st.button("ANALISAR AGORA", type="primary", use_container_width=True):
        with st.spinner("Conectando à The Odds API..."):
            time.sleep(1)
            dados = buscar_dados_api(codigo_da_liga, st.session_state.api_key_odds)
            
            if dados == "QUOTA_ERROR": 
                st.session_state.status_api = "OFFLINE"
                st.error("🚨 Limite da API esgotado! Insira nova chave no Hub."); dados = gerar_dados_mock()
            elif dados == "AUTH_ERROR": 
                st.session_state.status_api = "OFFLINE"
                st.error("🚨 Chave API Inválida."); dados = gerar_dados_mock()
            elif not dados: 
                st.session_state.status_api = "ONLINE"
                st.warning("⚠️ Sem jogos hoje nesta liga. Mostrando Mock."); dados = gerar_dados_mock()
            else: 
                st.session_state.status_api = "ONLINE"
                st.success("✅ Dados extraídos com sucesso.")
            
            st.session_state.analisados = []
            foco = st.session_state.tipo_analise_selecionado
            
            for jogo in dados[:5]:
                c, f = jogo.get('home_team', 'Casa'), jogo.get('away_team', 'Fora')
                odd = round(random.uniform(1.4, 2.3), 2)
                m = f"Vitória {c}"
                if "Gols" in foco: m = "Over 2.5 Gols"
                elif "Escanteios" in foco: m = "Over 8.5 Cantos"
                elif "Ambas" in foco: m = "Ambas Marcam: Sim"
                
                atk, dfs = calcular_forca_equipa(c)
                st.session_state.analisados.append({
                    "jogo": f"{c} x {f}", "m": m, "o": odd, "atk": atk, "def": dfs, "conf": random.randint(85,99),
                    "xg_c": round(random.uniform(1.1, 2.9), 2), "xg_f": round(random.uniform(0.5, 1.5), 2),
                    "vol": random.randint(50, 1500), "ev": (odd > 1.7 and atk > 75), "data": "Hoje"
                })

    with st.expander("✍️ Modo Manual (Override)"):
        grade = st.text_area("Cole os jogos (Time A x Time B):")
        if st.button("Gerar Análise Manual"):
            if grade:
                st.session_state.analisados = []
                for j in [x for x in grade.split('\n') if 'x' in x.lower()]:
                    c, f = j.lower().split('x')[0].strip().title(), j.lower().split('x')[1].strip().title()
                    st.session_state.analisados.append({"jogo": f"{c} x {f}", "m": "Aposta IA", "o": 1.85, "atk": 80, "def": 60, "conf": 92, "xg_c": 1.8, "xg_f": 0.9, "vol": 100, "ev": True, "data": "Manual"})
                st.rerun()

    if st.session_state.analisados:
        st.markdown("<br>", unsafe_allow_html=True)
        for idx, i in enumerate(st.session_state.analisados):
            ev_tag = f"<span style='color:#FFD700; border:1px solid #FFD700; padding:2px 4px; border-radius:4px; font-size:9px; font-weight:bold;'>EV+</span>" if i['ev'] else ""
            
            # HTML 100% BLINDADO (REPLACE \N)
            html_card = f"""
            <div class='card'>
                <div style='display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;'>
                    <span class='badge'>{i['m']}</span>
                    <span style='background:#121824; padding:4px 8px; border-radius:6px; color:{cor_neon}; font-weight:900; border:1px solid {cor_neon}40;'>@{i['o']:.2f}</span>
                </div>
                <div style='color:{c_prim}; font-size:14px; font-weight:800; margin-bottom:5px;'>⚽ {i['jogo']} {ev_tag}</div>
                <div style='display:flex; justify-content:space-between; color:{c_sec}; font-size:10px; margin-bottom:15px;'><span>📅 {i['data']}</span><span>🐋 Vol: ${i['vol']}k</span><span>🎯 Conf: {i['conf']}%</span></div>
                <div style='display:flex; justify-content:space-between; font-size:9px; color:{c_sec};'><span>Poder Ofensivo (xG {i['xg_c']})</span><span>{i['atk']}%</span></div>
                <div class='progress-bg'><div class='progress-fill-atk' style='width:{i['atk']}%;'></div></div>
                <div style='display:flex; justify-content:space-between; font-size:9px; color:{c_sec}; margin-top:4px;'><span>Muralha Defensiva (xG {i['xg_f']})</span><span>{i['def']}%</span></div>
                <div class='progress-bg' style='margin-bottom:15px;'><div class='progress-fill-def' style='width:{i['def']}%;'></div></div>
            </div>
            """
            st.markdown(html_card.replace('\n', ''), unsafe_allow_html=True)
            
            c_add1, c_add2 = st.columns(2)
            with c_add1:
                if st.button(f"➕ BILHETE", key=f"m_{idx}", type="primary", use_container_width=True): 
                    st.session_state.bilhete.append(i); st.toast("No Carrinho!")
            with c_add2:
                if st.button(f"💾 SALVAR", key=f"s_{idx}", use_container_width=True): 
                    st.session_state.analises_salvas.append(i); st.toast("Tracking Salvo!")

# ==========================================
# ABA 3: BILHETE
# ==========================================
with t3:
    st.markdown(f"<h3 style='color:{c_prim}; font-size:16px;'>🧾 Carrinho Múltiplo</h3>", unsafe_allow_html=True)
    if st.session_state.bilhete:
        odd_f = 1.0
        html_b = f"<div class='card'>"
        for b in st.session_state.bilhete:
            odd_f *= b['o']
            html_b += f"<div style='display:flex; justify-content:space-between; margin-bottom:10px; border-bottom:1px solid {border_card}; padding-bottom:5px;'><span style='font-size:13px; font-weight:600; color:{c_prim};'>{b['m']}<br><span style='font-size:10px; color:{c_sec};'>{b['jogo']}</span></span><span style='color:{cor_neon}; font-weight:bold;'>@{b['o']:.2f}</span></div>"
        html_b += "</div>"
        st.markdown(html_b.replace('\n', ''), unsafe_allow_html=True)
        
        st.markdown(f"<h2 style='text-align:center; color:{c_prim}; font-weight:900; font-size:36px;'>ODD <span style='color:{cor_neon}; text-shadow:0 0 15px {cor_neon}60;'>@{odd_f:.2f}</span></h2>", unsafe_allow_html=True)
        
        banca_escolhida = st.selectbox("Debitar Conta:", list(st.session_state.bancas.keys()))
        banca_disp = st.session_state.bancas[banca_escolhida]
        
        st.session_state.usar_kelly = st.checkbox("🧠 Calculadora Kelly Criterion", value=st.session_state.usar_kelly)
        if st.session_state.usar_kelly:
            prob = 1 / odd_f * 1.15
            kelly_pct = max(0.01, min(((odd_f - 1) * prob - (1 - prob)) / (odd_f - 1), 0.05))
            rec_stake = banca_disp * kelly_pct
        else: rec_stake = banca_disp * (0.03 if odd_f < 2.5 else 0.01)

        valor = st.number_input("Entrada (R$):", min_value=1.0, value=float(max(1.0, rec_stake)), step=10.0)
        st.markdown(f"<div style='font-size:10px; color:{c_sec}; text-align:center; margin-bottom:15px;'>🛡️ <b>Hedge:</b> Aposte {fmt_moeda(valor*0.3)} no 'Empate' para proteger capital.</div>", unsafe_allow_html=True)

        c1, c2 = st.columns(2)
        with c1:
            if st.button("✅ GREEN", type="primary", use_container_width=True):
                st.session_state.bancas[banca_escolhida] += (valor * odd_f)
                st.session_state.historico_banca.append(sum(st.session_state.bancas.values()))
                st.session_state.bilhete = []; tocar_som(); time.sleep(1); st.rerun()
        with c2:
            if st.button("❌ RED", use_container_width=True):
                st.session_state.bancas[banca_escolhida] -= valor
                st.session_state.historico_banca.append(sum(st.session_state.bancas.values()))
                st.session_state.bilhete = []; st.rerun()
    else:
        st.info("O carrinho está vazio.")

    st.markdown(f"<h3 style='color:{c_prim}; font-size:16px; margin-top:30px;'>📂 Tracking (Validação)</h3>", unsafe_allow_html=True)
    if st.session_state.analises_salvas:
        for i, a in enumerate(st.session_state.analises_salvas):
            st.markdown(f"<div class='card' style='border-left:3px solid #00d2ff; padding:10px; margin-bottom:5px;'><div style='font-size:12px; font-weight:bold; color:{c_prim};'>{a['m']} <span style='color:{cor_neon};'>@{a['o']}</span></div><div style='font-size:10px; color:{c_sec};'>{a['jogo']}</div></div>".replace('\n', ''), unsafe_allow_html=True)
            c_g, c_r, c_d = st.columns([0.4, 0.4, 0.2])
            with c_g: 
                if st.button("✅ WIN", key=f"tw_{i}"): 
                    st.session_state.total_jogos+=1; st.session_state.total_acertos+=1
                    st.session_state.analises_salvas.pop(i); tocar_som(); time.sleep(1); st.rerun()
            with c_r: 
                if st.button("❌ LOSS", key=f"tl_{i}"): 
                    st.session_state.total_jogos+=1
                    st.session_state.analises_salvas.pop(i); st.rerun()
            with c_d: 
                if st.button("🗑️", key=f"td_{i}"): st.session_state.analises_salvas.pop(i); st.rerun()
    else:
        st.caption("Nenhuma Single Salva.")

# ==========================================
# ABA 4: HUB VIP
# ==========================================
with t4:
    st.markdown(f"<h3 style='color:{c_prim}; font-size:18px; margin-bottom:20px;'>⚙️ HUB VIP</h3>", unsafe_allow_html=True)
    
    with st.expander("🔑 Chave da API The Odds"):
        st.markdown(f"<span style='font-size:11px; color:{c_sec};'>Insira sua chave (the-odds-api.com) para buscar dados reais:</span>", unsafe_allow_html=True)
        nova_api = st.text_input("API Key:", value=st.session_state.api_key_odds, type="password")
        if st.button("Salvar API", type="primary"): 
            st.session_state.api_key_odds = nova_api; st.success("Chave Atualizada!")
            
    with st.expander("🏛️ Bancas e Interface"):
        st.session_state.bancas["Betano"] = st.number_input("Banca Atual", value=st.session_state.bancas["Betano"], step=50.0)
    
    if st.button("Desconectar do Terminal", use_container_width=True):
        st.session_state.autenticado = False; st.rerun()
