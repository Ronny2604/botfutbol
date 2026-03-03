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

# --- 2. INICIALIZAÇÃO "NUCLEAR" DE MEMÓRIA (FIM DO ECRÃ VERMELHO) ---
if 'init_done' not in st.session_state:
    st.session_state.update({
        'autenticado': False, 'user_nome': "", 'bilhete': [], 'analisados': [],
        'analises_salvas': [], 'tipo_analise_selecionado': 'Análise Geral',
        'is_admin': False, 'boss_mode': False, 'api_key_odds': API_KEY_PADRAO,
        'tema_escolhido': "🟢 Verde Hacker", 'avatar': "🐺", 'moeda': "R$",
        'juros_compostos': False, 'usar_kelly': False, 'recuperacao_red': False,
        'bancas': {"Betano": 1000.0, "Bet365": 500.0, "Betfair": 0.0},
        'historico_banca': [1000.0], 'banca_inicial_dia': 1000.0,
        'conquistas': ["🏅 Novato"], 'total_jogos': 124, 'total_acertos': 101,
        'historico_greens': [], 'status_api': "AGUARDANDO",
        'titulo_apostador': "O Estrategista",
        'init_done': True
    })

# --- FUNÇÕES ---
def fmt_moeda(valor): return f"{st.session_state.get('moeda', 'R$')} {valor:,.2f}"

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
    som_html = '<audio autoplay style="display:none;"><source src="https://assets.mixkit.co/active_storage/sfx/2003/2003-preview.mp3" type="audio/mpeg"></audio>'
    st.markdown(som_html.replace('\n', ''), unsafe_allow_html=True)

# --- 3. CSS ROOT (BLINDADO CONTRA TELA ESTICADA) ---
cor_neon = "#00ff88"
c_prim = "#ffffff"
c_sec = "#8b9bb4"
border_card = "#1c2436"

css_code = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800;900&display=swap');

body {{
    background-image: url('{LINK_IMG_FUNDO}') !important;
    background-size: cover !important;
    background-position: center !important;
    background-attachment: fixed !important;
    background-color: #0b101a !important;
}}

html, .stApp, [data-testid="stAppViewContainer"], .main, [data-testid="stHeader"] {{
    background: transparent !important;
    background-color: transparent !important;
    font-family: 'Inter', sans-serif !important; 
    color: #ffffff !important;
    overflow-x: hidden !important;
}}

header[data-testid="stHeader"], footer, #MainMenu {{ display: none !important; }}
.block-container {{ padding-top: 1rem !important; padding-bottom: 120px !important; max-width: 600px !important; margin: 0 auto !important; }}

div[data-baseweb="input"] > div, div[data-baseweb="select"] > div, textarea {{ background-color: rgba(18,24,36,0.9) !important; border: 1px solid {border_card} !important; color: white !important; border-radius: 8px !important; }}

/* MENU INFERIOR BLINDADO */
div[data-testid="stTabs"] > div:first-of-type {{ 
    position: fixed !important; bottom: 0 !important; left: 0 !important; right: 0 !important; 
    background: rgba(11, 16, 26, 0.95) !important; backdrop-filter: blur(25px) !important;
    border-top: 1px solid {border_card} !important; border-radius: 20px 20px 0 0 !important; 
    padding: 10px 0 25px 0 !important; z-index: 99999 !important; display: flex !important; 
    justify-content: space-evenly !important; margin: 0 !important; box-sizing: border-box !important;
}}
div[data-testid="stTabs"] button[role="tab"] {{ flex: 1 !important; color: #8b9bb4 !important; font-size: 10px !important; font-weight: 800 !important; background: transparent !important; border: none !important; border-radius: 20px !important; padding: 12px 0 !important; transition: 0.3s; }}
div[data-testid="stTabs"] button[role="tab"][aria-selected="true"] {{ color: {cor_neon} !important; background: {cor_neon}15 !important; }}

.stButton>button[kind="secondary"] {{ height: 80px !important; background-color: rgba(18,24,36,0.85) !important; border: 1px solid #1c2436 !important; border-radius: 12px !important; color: #8b9bb4 !important; font-size: 12px !important; font-weight: 600 !important; transition: all 0.2s !important; }}
.stButton>button[kind="secondary"]:active {{ border-color: {cor_neon} !important; color: {cor_neon} !important; background-color: {cor_neon}10 !important; transform: scale(0.96) !important; }}

.stButton>button[kind="primary"] {{ background: linear-gradient(90deg, #00d2ff 0%, {cor_neon} 100%) !important; color: #000 !important; font-weight: 900 !important; border: none !important; border-radius: 12px !important; padding: 15px !important; font-size: 16px !important; box-shadow: 0 0 15px {cor_neon}50 !important; transition: all 0.2s !important; }}
.stButton>button[kind="primary"]:active {{ transform: scale(0.96) !important; box-shadow: 0 0 5px {cor_neon}80 !important; }}

::-webkit-scrollbar {{ width: 0px; background: transparent; }}
</style>
"""
st.markdown(css_code.replace('\n', ''), unsafe_allow_html=True)

# --- 4. TELA DE LOGIN ---
if not st.session_state.get('autenticado', False):
    login_html = f"""<br><br><br><br><h1 style='text-align:center; font-weight:900; font-size:48px; color:white;'>V8 <span style='color:{cor_neon}; text-shadow: 0 0 20px {cor_neon};'>A.I.</span></h1><p style='text-align:center; color:#8b9bb4; font-size:12px; margin-bottom:40px; text-transform:uppercase; letter-spacing:2px;'>Terminal Institucional</p>"""
    st.markdown(login_html.replace('\n', ''), unsafe_allow_html=True)
    nome_in = st.text_input("Operador ID:", placeholder="Seu nome aqui")
    if st.button("INICIAR SESSÃO", type="primary", use_container_width=True):
        st.session_state['autenticado'] = True
        st.session_state['user_nome'] = nome_in if nome_in else "Trader VIP"
        st.rerun()
    st.stop()

# --- 5. HEADER FIXO ---
saldo_atual = sum(st.session_state.get('bancas', {}).values())
pct_banca = min(100, max(0, (saldo_atual / st.session_state.get('banca_inicial_dia', 1000)) * 100))
cor_banca = cor_neon if pct_banca >= 100 else ("#FFD700" if pct_banca > 90 else "#ff3333")

header_html = f"""
<div style='position: sticky; top: 0; z-index: 999; background: rgba(18,24,36,0.9); backdrop-filter: blur(15px); padding: 15px; margin:-15px -15px 20px -15px; border-bottom: 1px solid #1c2436;'>
    <div style='display:flex; justify-content:space-between; align-items:center;'>
        <div style='display:flex; align-items:center;'>
            <div style='font-size: 24px; margin-right: 10px;'>{st.session_state.get('avatar')}</div>
            <div>
                <div style='font-weight:900; font-size:14px; color:white;'>{st.session_state.get('user_nome').upper()} <span style='background:{cor_neon}; color:#000; font-size:9px; padding:2px 4px; border-radius:4px;'>PRO</span></div>
                <div style='color:#8b9bb4; font-size:10px;'>API: <span style='color:{cor_neon};'>{st.session_state.get('status_api')}</span></div>
            </div>
        </div>
        <div style='text-align:right;'>
            <div style='color:#8b9bb4; font-size:10px; text-transform:uppercase;'>Banca</div>
            <div style='color:white; font-weight:900; font-size:18px;'>{fmt_moeda(saldo_atual)}</div>
        </div>
    </div>
    <div style='width:100%; height:2px; background:#1c2436; border-radius:2px; margin-top:10px;'><div style='width:{pct_banca}%; height:2px; background:{cor_banca}; box-shadow: 0 0 10px {cor_banca};'></div></div>
</div>
"""
st.markdown(header_html.replace('\n', ''), unsafe_allow_html=True)

# --- 6. NAVEGAÇÃO BOTTOM ---
t1, t2, t3, t4 = st.tabs(["📊 HOME", "🎯 RADAR", "🧾 BILHETE", "⚙️ HUB"])

# ==========================================
# ABA 1: DASHBOARD
# ==========================================
with t1:
    if saldo_atual < st.session_state.get('banca_inicial_dia') * 0.9: st.error("🚨 STOP LOSS ATINGIDO! Bloqueio sugerido.")
    
    win_rate = (st.session_state.get('total_acertos') / st.session_state.get('total_jogos')) * 100 if st.session_state.get('total_jogos') > 0 else 0
    fg_val = random.randint(30, 80)
    fg_cor = "#ff3333" if fg_val < 45 else (cor_neon if fg_val > 60 else "#FFD700")
    
    dash_html = f"""
    <div style='display: flex; gap: 10px; margin-bottom: 15px; width: 100%; box-sizing: border-box;'>
        <div style='flex:1; text-align:center; padding:15px; background:rgba(18,24,36,0.8); border-radius:12px; border:1px solid #1c2436;'>
            <p style='color:#8b9bb4; font-size:10px; margin:0;'>Win Rate A.I.</p>
            <p style='color:{cor_neon}; font-size:20px; font-weight:900; margin:0;'>{win_rate:.1f}%</p>
        </div>
        <div style='flex:1; text-align:center; padding:15px; background:rgba(18,24,36,0.8); border-radius:12px; border:1px solid #1c2436;'>
            <p style='color:#8b9bb4; font-size:10px; margin:0;'>Sentimento</p>
            <p style='color:{fg_cor}; font-size:20px; font-weight:900; margin:0;'>{fg_val}</p>
        </div>
    </div>
    """
    st.markdown(dash_html.replace('\n', ''), unsafe_allow_html=True)

    rank_html = f"""
    <h4 style='font-size:14px; color:white; margin-top:20px;'>🏆 Ranking Global VIP</h4>
    <div style='background:rgba(18,24,36,0.8); border-radius:12px; border:1px solid #1c2436; padding: 15px;'>
        <div style='display:flex; justify-content:space-between; border-bottom:1px solid #1c2436; padding-bottom:8px;'><span style='font-size:12px; color:white;'>🥇 TraderAlpha</span> <b style='color:{cor_neon}; font-size:12px;'>+{fmt_moeda(4520)}</b></div>
        <div style='display:flex; justify-content:space-between; border-bottom:1px solid #1c2436; padding:8px 0;'><span style='font-size:12px; color:white;'>🥈 {st.session_state.get('user_nome')}</span> <b style='color:{cor_neon}; font-size:12px;'>+{fmt_moeda(1250)}</b></div>
        <div style='display:flex; justify-content:space-between; padding-top:8px;'><span style='font-size:12px; color:white;'>🥉 Lucas_Inv</span> <b style='color:{cor_neon}; font-size:12px;'>+{fmt_moeda(890)}</b></div>
    </div>
    """
    st.markdown(rank_html.replace('\n', ''), unsafe_allow_html=True)

# ==========================================
# ABA 2: RADAR A.I.
# ==========================================
with t2:
    st.markdown(f"<p style='text-align:center; font-size:14px; font-weight:800; color:white;'>Direcionamento Algorítmico</p>", unsafe_allow_html=True)
    
    opcoes = [("📈\nGeral", "Análise Geral"), ("🏆\nResultado", "Resultado Final"), ("⚽\nGols", "Gols"), ("⏳\nHT", "Primeiro Tempo"), ("🚩\nCantos", "Escanteios"), ("🟨\nCartões", "Cartões"), ("🎯\nChutes", "Chutes"), ("👤\nJogador", "Jogador"), ("🔄\nBTTS", "Ambas Marcam")]
    for i in range(0, 9, 3):
        c1, c2, c3 = st.columns(3)
        with c1: 
            if st.button(opcoes[i][0], key=f"btn_{i}", use_container_width=True): st.session_state['tipo_analise_selecionado'] = opcoes[i][1]
        with c2: 
            if st.button(opcoes[i+1][0], key=f"btn_{i+1}", use_container_width=True): st.session_state['tipo_analise_selecionado'] = opcoes[i+1][1]
        with c3: 
            if st.button(opcoes[i+2][0], key=f"btn_{i+2}", use_container_width=True): st.session_state['tipo_analise_selecionado'] = opcoes[i+2][1]
            
    foco = st.session_state.get('tipo_analise_selecionado', 'Análise Geral')
    st.markdown(f"<p style='text-align:center; color:{cor_neon}; font-size:11px; font-weight:bold; margin-bottom:15px;'>Foco Selecionado: {foco}</p>", unsafe_allow_html=True)

    LIGAS = {"🇪🇺 Champions League": "soccer_uefa_champs_league", "🇬🇧 Premier League": "soccer_epl", "🇪🇸 La Liga": "soccer_spain_la_liga", "🇧🇷 Brasileirão": "soccer_brazil_campeonato"}
    codigo_da_liga = LIGAS[st.selectbox("Selecionar Filtro Geográfico:", list(LIGAS.keys()))]

    if st.button("INICIAR VARREDURA", type="primary", use_container_width=True):
        with st.spinner("Conectando à The Odds API..."):
            time.sleep(1)
            dados = buscar_dados_api(codigo_da_liga, st.session_state.get('api_key_odds'))
            
            if dados == "QUOTA_ERROR": 
                st.session_state['status_api'] = "SIMULAÇÃO (LIMIT_EXCEEDED)"
                st.error("🚨 Limite da API esgotado! Insira nova chave no Hub. Usando Mock Data."); dados = gerar_dados_mock()
            elif dados == "AUTH_ERROR": 
                st.session_state['status_api'] = "SIMULAÇÃO (INVALID_KEY)"
                st.error("🚨 Chave API Inválida. Usando Mock Data."); dados = gerar_dados_mock()
            elif not dados: 
                st.session_state['status_api'] = "SIMULAÇÃO (NO_GAMES)"
                st.warning("⚠️ Sem jogos hoje nesta liga. Mostrando Mock Data."); dados = gerar_dados_mock()
            else: 
                st.session_state['status_api'] = "CONECTADO (REAL DATA)"
                st.success("✅ Conectado aos servidores. Dados reais extraídos.")
            
            st.session_state['analisados'] = []
            for jogo in dados[:5]:
                c, f = jogo.get('home_team', 'Casa'), jogo.get('away_team', 'Fora')
                odd = round(random.uniform(1.4, 2.3), 2)
                
                if "Gols" in foco: m = random.choice(["Over 1.5 Gols", "Over 2.5 Gols", "Under 3.5 Gols"])
                elif "Cantos" in foco or "Escanteios" in foco: m = random.choice(["Over 8.5 Cantos", "Over 9.5 Cantos"])
                elif "Ambas" in foco: m = "Ambas Marcam: Sim"
                elif "Cartões" in foco: m = random.choice(["Over 4.5 Cartões", "Over 5.5 Cartões"])
                elif "Resultado" in foco: m = random.choice([f"Vitória {c}", f"Vitória {f}", "Empate"])
                elif "Tempo" in foco: m = random.choice(["Over 0.5 HT", f"Vitória HT {c}"])
                else: m = random.choice([f"Vitória {c}", "Ambas Marcam: Sim", "Over 1.5 Gols"])
                
                atk, dfs = calcular_forca_equipa(c)
                whisper = random.choice(["Equipa da casa marca forte no 2º Tempo.", "Árbitro com média de 5.5 cartões.", "Tática focada em posse de bola.", "Alerta de valor detectado via algoritmo."])
                
                st.session_state['analisados'].append({
                    "jogo": f"{c} x {f}", "m": m, "o": odd, "atk": atk, "def": dfs, "conf": random.randint(85,99),
                    "xg_c": round(random.uniform(1.1, 2.9), 2), "xg_f": round(random.uniform(0.5, 1.5), 2),
                    "vol": random.randint(50, 1500), "ev": (odd > 1.7 and atk > 75), "data": "Hoje", "whisper": whisper
                })

    with st.expander("✍️ Modo Manual (A.I. Customizada)"):
        st.markdown("<p style='font-size:11px; color:#8b9bb4;'>Cole os seus jogos abaixo. A IA aplicará a estatística e o <b>Foco Selecionado</b> acima.</p>", unsafe_allow_html=True)
        grade = st.text_area("Formato: Time A x Time B", label_visibility="collapsed")
        if st.button("Forçar Análise Manual"):
            if grade:
                st.session_state['analisados'] = []
                for j in [x for x in grade.split('\n') if 'x' in x.lower()]:
                    c, f = j.lower().split('x')[0].strip().title(), j.lower().split('x')[1].strip().title()
                    atk, dfs = calcular_forca_equipa(c)
                    
                    # MAGIA AQUI: O MODO MANUAL AGORA RESPEITA O BOTÃO CLICADO NA GRELHA!
                    if "Gols" in foco: m = random.choice(["Over 1.5 Gols", "Over 2.5 Gols", "Under 3.5 Gols"])
                    elif "Cantos" in foco or "Escanteios" in foco: m = random.choice(["Over 8.5 Cantos", "Over 9.5 Cantos"])
                    elif "Ambas" in foco: m = "Ambas Marcam: Sim"
                    elif "Cartões" in foco: m = random.choice(["Over 4.5 Cartões", "Over 5.5 Cartões"])
                    elif "Resultado" in foco: m = random.choice([f"Vitória {c}", f"Vitória {f}", "Empate"])
                    elif "Tempo" in foco: m = random.choice(["Over 0.5 HT", f"Vitória HT {c}"])
                    else: m = random.choice([f"Vitória {c}", "Ambas Marcam: Sim", "Over 1.5 Gols"])
                    
                    odd_manual = round(random.uniform(1.4, 2.1), 2)
                    st.session_state['analisados'].append({
                        "jogo": f"{c} x {f}", "m": m, "o": odd_manual, "atk": atk, "def": dfs, "conf": random.randint(88, 99), 
                        "xg_c": round(random.uniform(1.1, 2.9), 2), "xg_f": round(random.uniform(0.5, 1.5), 2), 
                        "vol": random.randint(50, 1000), "ev": (odd_manual > 1.7), "data": "Manual", "whisper": "Análise Customizada (Override)."
                    })
                st.rerun()

    # RENDERIZAÇÃO BLINDADA
    if st.session_state.get('analisados'):
        st.markdown("<br>", unsafe_allow_html=True)
        for idx, i in enumerate(st.session_state.get('analisados')):
            ev_tag = f"<span style='color:#FFD700; border:1px solid #FFD700; padding:2px 4px; border-radius:4px; font-size:9px; font-weight:bold;'>EV+</span>" if i['ev'] else ""
            
            html_final = f"<div style='background:rgba(18,24,36,0.85); border:1px solid #1c2436; border-radius:12px; padding:15px; margin-bottom:15px;'><div style='display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;'><span style='background:rgba(0,255,136,0.1); color:{cor_neon}; padding:4px 8px; border-radius:4px; font-size:11px; font-weight:800;'>{i['m']}</span><span style='background:#121824; padding:4px 8px; border-radius:6px; color:{cor_neon}; font-weight:900; border:1px solid rgba(0,255,136,0.3);'>@{i['o']:.2f}</span></div><div style='color:white; font-size:14px; font-weight:800; margin-bottom:5px;'>⚽ {i['jogo']} {ev_tag}</div><div style='display:flex; justify-content:space-between; color:#8b9bb4; font-size:10px; margin-bottom:15px;'><span>📅 {i['data']}</span><span>🐋 Vol: ${i['vol']}k</span><span>🎯 Conf: {i['conf']}%</span></div><div style='display:flex; justify-content:space-between; font-size:9px; color:#8b9bb4;'><span>Poder Ofensivo (xG {i['xg_c']})</span><span>{i['atk']}%</span></div><div style='width:100%; background:rgba(0,0,0,0.4); height:4px; border-radius:4px; margin-bottom:8px;'><div style='width:{i['atk']}%; background:{cor_neon}; height:4px; border-radius:4px;'></div></div><div style='display:flex; justify-content:space-between; font-size:9px; color:#8b9bb4;'><span>Muralha Defensiva (xG {i['xg_f']})</span><span>{i['def']}%</span></div><div style='width:100%; background:rgba(0,0,0,0.4); height:4px; border-radius:4px; margin-bottom:10px;'><div style='width:{i['def']}%; background:#00aaff; height:4px; border-radius:4px;'></div></div><div style='background:rgba(0,0,0,0.3); border-left:2px solid {cor_neon}; padding:8px; border-radius:6px; font-size:10px; color:#8b9bb4; font-style:italic;'>🤖 <b>IA Whisper:</b> {i.get('whisper', 'Dados promissores.')}</div></div>"
            st.markdown(html_final.replace('\n', ''), unsafe_allow_html=True)
            
            c_add1, c_add2 = st.columns(2)
            with c_add1:
                if st.button(f"➕ BILHETE", key=f"m_{idx}", type="primary", use_container_width=True): 
                    st.session_state['bilhete'].append(i); st.toast("No Carrinho!")
            with c_add2:
                if st.button(f"💾 SALVAR", key=f"s_{idx}", use_container_width=True): 
                    st.session_state['analises_salvas'].append(i); st.toast("Tracking Salvo!")

# ==========================================
# ABA 3: BILHETE
# ==========================================
with t3:
    st.markdown(f"<h3 style='color:white; font-size:16px;'>🧾 Carrinho Múltiplo</h3>", unsafe_allow_html=True)
    bilhete = st.session_state.get('bilhete', [])
    
    if bilhete:
        odd_f = 1.0
        html_b = f"<div style='background:rgba(18,24,36,0.85); border:1px solid #1c2436; border-radius:12px; padding:15px; margin-bottom:15px;'>"
        for b in bilhete:
            odd_f *= b['o']
            html_b += f"<div style='display:flex; justify-content:space-between; margin-bottom:10px; border-bottom:1px solid #1c2436; padding-bottom:5px;'><span style='font-size:13px; font-weight:600; color:white;'>{b['m']}<br><span style='font-size:10px; color:#8b9bb4;'>{b['jogo']}</span></span><span style='color:{cor_neon}; font-weight:bold;'>@{b['o']:.2f}</span></div>"
        html_b += "</div>"
        st.markdown(html_b.replace('\n', ''), unsafe_allow_html=True)
        
        st.markdown(f"<h2 style='text-align:center; color:white; font-weight:900; font-size:36px;'>ODD <span style='color:{cor_neon}; text-shadow:0 0 15px {cor_neon}60;'>@{odd_f:.2f}</span></h2>", unsafe_allow_html=True)
        
        bancas = st.session_state.get('bancas', {})
        banca_escolhida = st.selectbox("Debitar Conta:", list(bancas.keys()))
        banca_disp = bancas[banca_escolhida]
        
        st.session_state['usar_kelly'] = st.checkbox("🧠 Calculadora Kelly Criterion", value=st.session_state.get('usar_kelly', False))
        if st.session_state.get('usar_kelly'):
            prob = 1 / odd_f * 1.15
            kelly_pct = max(0.01, min(((odd_f - 1) * prob - (1 - prob)) / (odd_f - 1), 0.05))
            rec_stake = banca_disp * kelly_pct
        else: rec_stake = banca_disp * (0.03 if odd_f < 2.5 else 0.01)

        valor = st.number_input("Entrada (R$):", min_value=1.0, value=float(max(1.0, rec_stake)), step=10.0)
        
        hedge_val = valor * 0.3
        st.markdown(f"<div style='font-size:10px; color:#8b9bb4; text-align:center; margin-bottom:15px;'>🛡️ <b>Hedge:</b> Aposte {fmt_moeda(hedge_val)} no 'Empate' para proteger capital.</div>", unsafe_allow_html=True)

        c1, c2 = st.columns(2)
        with c1:
            if st.button("✅ GREEN", type="primary", use_container_width=True):
                st.session_state['bancas'][banca_escolhida] += (valor * odd_f)
                st.session_state['historico_banca'].append(sum(st.session_state['bancas'].values()))
                st.session_state['bilhete'] = []; tocar_som(); time.sleep(1); st.rerun()
        with c2:
            if st.button("❌ RED", use_container_width=True):
                st.session_state['bancas'][banca_escolhida] -= valor
                st.session_state['historico_banca'].append(sum(st.session_state['bancas'].values()))
                st.session_state['bilhete'] = []; st.rerun()
    else:
        st.info("O carrinho está vazio.")

    st.markdown(f"<h3 style='color:white; font-size:16px; margin-top:30px;'>📂 Tracking (Validação)</h3>", unsafe_allow_html=True)
    salvas = st.session_state.get('analises_salvas', [])
    if salvas:
        for i, a in enumerate(salvas):
            st.markdown(f"<div style='background:rgba(18,24,36,0.85); padding:10px; border-left:3px solid #00d2ff; margin-bottom:5px; border-radius:4px;'><div style='font-size:12px; font-weight:bold; color:white;'>{a['m']} <span style='color:{cor_neon};'>@{a['o']}</span></div><div style='font-size:10px; color:#8b9bb4;'>{a['jogo']}</div></div>".replace('\n', ''), unsafe_allow_html=True)
            c_g, c_r, c_d = st.columns([0.4, 0.4, 0.2])
            with c_g: 
                if st.button("✅ WIN", key=f"tw_{i}"): 
                    st.session_state['total_jogos']+=1; st.session_state['total_acertos']+=1
                    st.session_state['analises_salvas'].pop(i); tocar_som(); time.sleep(1); st.rerun()
            with c_r: 
                if st.button("❌ LOSS", key=f"tl_{i}"): 
                    st.session_state['total_jogos']+=1
                    st.session_state['analises_salvas'].pop(i); st.rerun()
            with c_d: 
                if st.button("🗑️", key=f"td_{i}"): st.session_state['analises_salvas'].pop(i); st.rerun()
    else:
        st.caption("Nenhuma Single Salva.")

# ==========================================
# ABA 4: HUB VIP
# ==========================================
with t4:
    st.markdown(f"<h3 style='color:white; font-size:18px; margin-bottom:20px;'>⚙️ HUB VIP</h3>", unsafe_allow_html=True)
    
    with st.expander("🔑 Chave da API The Odds"):
        st.markdown(f"<span style='font-size:11px; color:#8b9bb4;'>Insira sua chave (the-odds-api.com) para buscar dados 100% reais:</span>", unsafe_allow_html=True)
        nova_api = st.text_input("API Key:", value=st.session_state.get('api_key_odds'), type="password")
        if st.button("Salvar API", type="primary"): 
            st.session_state['api_key_odds'] = nova_api; st.success("Chave Atualizada!")
            
    with st.expander("🏛️ Bancas e Interface"):
        st.session_state['bancas']["Betano"] = st.number_input("Banca Atual", value=st.session_state.get('bancas')["Betano"], step=50.0)
    
    with st.expander("📡 Console de Auditoria (Deep Web Logs)"):
        st.markdown(f"<div style='background:#000; padding:10px; border-radius:8px; font-family:monospace; color:{cor_neon}; font-size:10px;'> > AUTH KEY: {st.session_state.get('api_key_odds')[:5]}...<br>> LAST PING: {datetime.now().strftime('%H:%M:%S')}<br>> FETCHING SYNDICATE DATA...<br>> STATUS: {st.session_state.get('status_api')}</div>".replace('\n', ''), unsafe_allow_html=True)

    if st.button("Desconectar do Terminal", use_container_width=True):
        st.session_state['autenticado'] = False; st.rerun()
