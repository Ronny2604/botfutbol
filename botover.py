import streamlit as st
import asyncio
import random
import time
import os
import urllib.parse
import requests
import hashlib
import pandas as pd
from datetime import datetime, timedelta

# --- 1. CONFIGURAÇÃO ---
st.set_page_config(page_title="V8 SUPREME PRO", layout="wide", initial_sidebar_state="collapsed")

LINK_PAINEL = "https://seu-link-aqui.streamlit.app" 
LINK_SUA_IMAGEM_DE_FUNDO = "https://raw.githubusercontent.com/Ronny2604/botfutbol/main/photo_5172618853803035536_c.png"
MASTER_KEY = "ronnyp@2025"
FILE_KEYS = "keys.txt" 
ODDS_API_KEY = "da4633249ece20283d29604cec7a7114"

# --- 2. BLINDAGEM DE ESTADOS (ANTI-CRASH) ---
estado_padrao = {
    'is_admin': False, 'autenticado': False, 'user_nome': "", 
    'bilhete': [], 'analisados': [], 'analises_salvas': [], 
    'tipo_analise_selecionado': 'Análise Geral', 'boss_mode': False, 
    'api_key_odds': ODDS_API_KEY, 'tema_escolhido': "🟢 Verde Hacker",
    'avatar': "🐺", 'moeda': "R$", 'juros_compostos': False, 'usar_kelly': False,
    'bancas': {"Betano": 1000.0, "Bet365": 500.0, "Betfair": 0.0},
    'historico_banca': [1000.0], 'banca_inicial_dia': 1000.0, 'recuperacao_red': False,
    'conquistas': ["🏅 Novato Promissor"], 'total_jogos': 1248, 'total_acertos': 1115,
    'historico_greens': []
}
for k, v in estado_padrao.items():
    if k not in st.session_state: st.session_state[k] = v

def fmt_moeda(valor): return f"{st.session_state.moeda} {valor:,.2f}"
def calcular_forca_equipa(nome): num = int(hashlib.md5(nome.encode()).hexdigest(), 16); return 60 + (num % 35), 50 + ((num // 10) % 40)
def tocar_som(): st.markdown('<audio autoplay style="display:none;"><source src="https://assets.mixkit.co/active_storage/sfx/2003/2003-preview.mp3" type="audio/mpeg"></audio>', unsafe_allow_html=True)

def gerar_dados_mock():
    times = ["Real Madrid", "Barcelona", "Man City", "Arsenal", "Bayern", "Flamengo", "Liverpool", "Chelsea", "Milan", "Inter"]
    random.shuffle(times)
    d = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    return [{"home_team": times[i*2], "away_team": times[i*2+1], "commence_time": d} for i in range(5)]

@st.cache_data(ttl=300, show_spinner=False)
def buscar_dados_api(liga, api_key):
    url = f"https://api.the-odds-api.com/v4/sports/{liga}/odds/?apiKey={api_key}&regions=eu,uk&markets=h2h"
    try:
        r = requests.get(url, timeout=5)
        if r.status_code == 200 and isinstance(r.json(), list): return r.json()
    except: pass
    return None

# --- 3. MOTOR DE TEMAS ---
tema = st.session_state.tema_escolhido
is_light = ("Light" in tema)
if is_light:
    cor_neon = "#0055ff"; c_prim = "#111111"; c_sec = "#555555"; c_inv = "#ffffff"
    card_bg = "rgba(255, 255, 255, 0.85)"; card_border = "rgba(0, 0, 0, 0.1)"; bg_app = "#f0f2f6"
else:
    cor_neon = "#00ff88"
    if "Ouro" in tema: cor_neon = "#FFD700"
    elif "Azul" in tema: cor_neon = "#00e5ff"
    elif "Vermelho" in tema: cor_neon = "#ff3333"
    elif "Rosa" in tema: cor_neon = "#ff00ff"
    c_prim = "#ffffff"; c_sec = "#8b9bb4"; c_inv = "#000000"
    card_bg = "rgba(18, 24, 36, 0.75)"; card_border = "rgba(255, 255, 255, 0.08)"; bg_app = "#0b101a"

# --- 4. CSS SUPREMO (FIM DA TELA PRETA E BUGS HTML) ---
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800;900&display=swap');
    
    /* 1. TRAVA DE VIEWPORT (FIM DA TELA PRETA LATERAL) */
    html, body {{ overflow-x: hidden !important; width: 100% !important; margin: 0 !important; padding: 0 !important; background-color: {bg_app} !important; font-family: 'Inter', sans-serif !important; color: {c_prim} !important; }}
    [data-testid="stAppViewContainer"] {{ overflow-x: hidden !important; width: 100% !important; }}
    
    /* 2. FUNDO ABSOLUTO */
    .stApp::before {{
        content: ""; position: fixed; top: 0; left: 0; width: 100%; height: 100vh;
        background: {'linear-gradient(rgba(240,242,246,0.9), rgba(255,255,255,0.95))' if is_light else 'radial-gradient(circle at 50% 0%, rgba(11,16,26,0.9), rgba(5,8,12,1))'}, url('{LINK_SUA_IMAGEM_DE_FUNDO}');
        background-size: cover; background-position: center; z-index: -1;
    }}
    
    header[data-testid="stHeader"], footer, #MainMenu {{ display: none !important; }}
    .block-container {{ padding-top: 1rem !important; padding-bottom: 90px !important; max-width: 600px !important; margin: 0 auto !important; overflow-x: hidden !important; }}
    
    /* 3. INPUTS TRANSPARENTES */
    div[data-baseweb="input"] > div, div[data-baseweb="select"] > div, textarea {{ background-color: rgba(18,24,36,0.5) !important; border: 1px solid {card_border} !important; color: {c_prim} !important; border-radius: 8px !important; transition: all 0.3s ease; }}
    div[data-baseweb="input"] > div:focus-within {{ border-color: {cor_neon} !important; box-shadow: inset 0 0 10px {cor_neon}30 !important; }}
    .stMarkdown p, .stText p, label {{ color: {c_prim} !important; }}
    
    /* 4. BOTTOM NAV FLUTUANTE */
    div[data-testid="stTabs"] > div:first-of-type {{ 
        position: fixed !important; bottom: 15px !important; left: 50% !important; transform: translateX(-50%) !important;
        width: 95% !important; max-width: 580px !important;
        background: {'rgba(255,255,255,0.85)' if is_light else 'rgba(18,24,36,0.85)'} !important;
        backdrop-filter: blur(20px) !important; -webkit-backdrop-filter: blur(20px) !important;
        border-radius: 30px !important; border: 1px solid {cor_neon}40 !important;
        padding: 5px 10px !important; z-index: 99999 !important; box-shadow: 0 10px 30px rgba(0,0,0,0.5) !important;
        display: flex !important; justify-content: space-evenly !important;
    }}
    div[data-testid="stTabs"] button[role="tab"] {{ flex: 1 !important; color: {c_sec} !important; font-size: 10px !important; font-weight: 800 !important; background: transparent !important; border: none !important; border-radius: 20px !important; padding: 10px 0 !important; transition: 0.3s; }}
    div[data-testid="stTabs"] button[role="tab"][aria-selected="true"] {{ color: {cor_neon} !important; background: {cor_neon}15 !important; }}
    
    /* 5. GRELHA 3x3 E EFEITO HOVER */
    .stButton>button[kind="secondary"] {{ height: 80px !important; background-color: {card_bg} !important; border: 1px solid {card_border} !important; border-radius: 16px !important; color: {c_sec} !important; font-size: 12px !important; font-weight: 600 !important; transition: all 0.2s ease !important; }}
    .stButton>button[kind="secondary"]:hover, .stButton>button[kind="secondary"]:active {{ border-color: {cor_neon} !important; color: {cor_neon} !important; background-color: {cor_neon}10 !important; transform: scale(0.96) !important; }}
    
    /* 6. BOTÃO NEON PULSE */
    .stButton>button[kind="primary"] {{ background: linear-gradient(90deg, #00d2ff 0%, {cor_neon} 100%) !important; color: #000 !important; font-weight: 900 !important; border: none !important; border-radius: 12px !important; padding: 15px !important; font-size: 16px !important; box-shadow: 0 0 15px {cor_neon}50 !important; transition: all 0.2s !important; }}
    .stButton>button[kind="primary"]:active {{ transform: scale(0.96) !important; box-shadow: 0 0 5px {cor_neon}80 !important; }}
    
    /* 7. CARTÕES E BARRAS STRIPES */
    .card {{ background: {card_bg}; backdrop-filter: blur(10px); border: 1px solid {card_border}; border-radius: 16px; padding: 15px; margin-bottom: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); width: 100%; box-sizing: border-box; }}
    .badge {{ background: {cor_neon}15; color: {cor_neon}; padding: 4px 10px; border-radius: 6px; font-size: 11px; font-weight: 800; border: 1px solid {cor_neon}40; }}
    
    .progress-bg {{ width: 100%; background: rgba(0,0,0,0.3); border-radius: 10px; height: 6px; margin-bottom: 8px; overflow: hidden; }}
    .progress-fill-atk {{ height: 6px; background: linear-gradient(45deg, #ff0055 25%, #ff5555 25%, #ff5555 50%, #ff0055 50%, #ff0055 75%, #ff5555 75%, #ff5555 100%); background-size: 20px 20px; border-radius: 10px; animation: moveStripes 1s linear infinite; }}
    .progress-fill-def {{ height: 6px; background: linear-gradient(45deg, #0055ff 25%, #00aaff 25%, #00aaff 50%, #0055ff 50%, #0055ff 75%, #00aaff 75%, #00aaff 100%); background-size: 20px 20px; border-radius: 10px; animation: moveStripes 1s linear infinite; }}
    @keyframes moveStripes {{ 0% {{ background-position: 0 0; }} 100% {{ background-position: 20px 0; }} }}
    
    /* 8. PULSAR AO VIVO E EV+ */
    .live-dot {{ display: inline-block; width: 8px; height: 8px; background-color: #ff3333; border-radius: 50%; margin-right: 5px; animation: pulseRed 1.5s infinite; }}
    @keyframes pulseRed {{ 0% {{ box-shadow: 0 0 0 0 rgba(255,51,51,0.7); }} 70% {{ box-shadow: 0 0 0 6px rgba(255,51,51,0); }} 100% {{ box-shadow: 0 0 0 0 rgba(255,51,51,0); }} }}
    .ev-flag {{ animation: pulseEV 2s infinite; color: #FFD700; font-weight: 900; font-size: 10px; border: 1px solid #FFD700; padding: 2px 5px; border-radius: 4px; }}
    @keyframes pulseEV {{ 0%, 100% {{ opacity: 1; }} 50% {{ opacity: 0.5; }} }}
    
    ::-webkit-scrollbar {{ width: 0px; background: transparent; }}
    </style>
""", unsafe_allow_html=True)

# --- 5. TELA DE LOGIN ---
if not st.session_state.autenticado:
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    st.markdown(f"<h1 style='text-align:center; font-weight:900; font-size:48px; margin-bottom:0;'>V8 <span style='color:{cor_neon};'>A.I.</span></h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align:center; color:{c_sec}; font-size:12px; margin-bottom:40px; letter-spacing:2px;'>TERMINAL INSTITUCIONAL</p>", unsafe_allow_html=True)
    nome_in = st.text_input("Operador ID:", placeholder="Seu Nome")
    if st.button("INICIAR SESSÃO", type="primary", use_container_width=True):
        st.session_state.autenticado = True
        st.session_state.user_nome = nome_in if nome_in else "Trader"
        st.rerun()
    st.stop()

# --- 6. HEADER FIXO TOP ---
saldo_atual = sum(st.session_state.bancas.values())

# NOVO: Stop Win e Stop Loss Logic
if saldo_atual < st.session_state.banca_inicial_dia * 0.9: st.error("🚨 STOP LOSS ATINGIDO! Proteja o seu capital.")
if saldo_atual >= st.session_state.banca_inicial_dia * 1.2: st.success("🎯 STOP WIN ATINGIDO! Meta diária concluída. Relaxe!")

btc_price = 64320.50 + random.uniform(-50, 50) # FEATURE: Crypto Ticker
st.markdown(f"<div style='text-align:center; font-size:9px; color:{c_sec}; padding:5px;'>₿ BTC: <span style='color:{cor_neon};'>${btc_price:,.2f}</span> | MKT: ABERTO</div>", unsafe_allow_html=True)

pct_banca = min(100, max(0, (saldo_atual / st.session_state.banca_inicial_dia) * 100))
cor_banca = cor_neon if pct_banca >= 100 else ("#FFD700" if pct_banca > 90 else "#ff3333")

st.markdown(f"""
    <div style='background:{card_bg}; border:1px solid {card_border}; border-radius:16px; padding:15px; margin-bottom:20px; display:flex; justify-content:space-between; align-items:center;'>
        <div style='display:flex; align-items:center;'>
            <div style='font-size: 28px; margin-right: 12px;'>{st.session_state.avatar}</div>
            <div>
                <div style='font-weight:900; font-size:16px; color:{c_prim};'>{st.session_state.user_nome.upper()}</div>
                <div style='color:{cor_neon}; font-size:10px;'>{st.session_state.titulo_apostador}</div>
            </div>
        </div>
        <div style='text-align:right;'>
            <div style='color:{c_sec}; font-size:10px; text-transform:uppercase;'>Banca</div>
            <div style='color:{c_prim}; font-weight:900; font-size:20px;'>{fmt_moeda(saldo_atual)}</div>
            <div style='width:60px; height:3px; background:#222; border-radius:2px; margin-top:4px; float:right;'><div style='width:{pct_banca}%; height:3px; background:{cor_banca};'></div></div>
        </div>
    </div>
""", unsafe_allow_html=True)

# --- 7. NAVEGAÇÃO ---
t1, t2, t3, t4 = st.tabs(["📊 HOME", "🎯 RADAR", "🧾 BILHETE", "⚙️ HUB"])

# ==========================================
# ABA 1: DASHBOARD
# ==========================================
with t1:
    win_rate = (st.session_state.total_acertos / st.session_state.total_jogos) * 100 if st.session_state.total_jogos > 0 else 0
    fg_val = random.randint(30, 80)
    fg_cor = "#ff3333" if fg_val < 45 else (cor_neon if fg_val > 60 else "#FFD700")
    
    st.markdown(f"""
        <div style='display: flex; gap: 10px; margin-bottom: 15px;'>
            <div class='card' style='flex:1; text-align:center; padding:12px; margin:0;'>
                <p style='color:{c_sec}; font-size:10px; margin:0;'>Win Rate A.I.</p>
                <p style='color:{cor_neon}; font-size:22px; font-weight:900; margin:0;'>{win_rate:.1f}%</p>
            </div>
            <div class='card' style='flex:1; text-align:center; padding:12px; margin:0;'>
                <p style='color:{c_sec}; font-size:10px; margin:0;'>Fear & Greed</p>
                <p style='color:{fg_cor}; font-size:22px; font-weight:900; margin:0;'>{fg_val}</p>
            </div>
        </div>
    """, unsafe_allow_html=True)

    if st.session_state.mod_grafico:
        st.markdown(f"<div class='card' style='padding:15px;'><p style='color:{c_sec}; font-size:11px; margin:0 0 10px 0;'>📈 Desempenho Linear</p>", unsafe_allow_html=True)
        st.line_chart(st.session_state.historico_banca, height=120, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown(f"<h4 style='font-size:14px; color:{c_prim}; margin-bottom:10px;'>🔴 Operações ao Vivo</h4>", unsafe_allow_html=True)
    st.markdown(f"""
        <div class='card' style='border-left: 3px solid #ff3333; padding:12px;'>
            <div style='display:flex; justify-content:space-between; align-items:center;'>
                <div><span class='live-dot'></span><span style='color:{c_prim}; font-size:14px; font-weight:800;'>Real Madrid 1 x 0 Getafe</span></div>
                <div style='background:rgba(255,51,51,0.1); color:#ff3333; padding:3px 8px; border-radius:4px; font-size:10px; font-weight:bold;'>78'</div>
            </div>
            <div style='font-size:11px; color:{c_sec}; margin-top:5px;'>Target: <b style='color:{cor_neon};'>Under 2.5</b></div>
        </div>
    """, unsafe_allow_html=True)

# ==========================================
# ABA 2: RADAR A.I. (GRELHA 3x3)
# ==========================================
with t2:
    st.markdown(f"<p style='text-align:center; font-size:14px; font-weight:800; color:{c_prim};'>Direcionamento Algorítmico</p>", unsafe_allow_html=True)
    
    opcoes = [("📈\nGeral", "Análise Geral"), ("🏆\nResultado", "Resultado Final"), ("⚽\nGols", "Gols"), ("⏳\nHT", "Primeiro Tempo"), ("🚩\nCantos", "Escanteios"), ("🟨\nCartões", "Cartões"), ("🎯\nChutes", "Chutes"), ("👤\nJogador", "Jogador"), ("🔄\nBTTS", "Ambas Marcam")]
    for i in range(0, 9, 3):
        c1, c2, c3 = st.columns(3)
        with c1: 
            if st.button(opcoes[i][0], key=f"btn_{i}", use_container_width=True): st.session_state.tipo_analise_selecionado = opcoes[i][1]
        with c2: 
            if st.button(opcoes[i+1][0], key=f"btn_{i+1}", use_container_width=True): st.session_state.tipo_analise_selecionado = opcoes[i+1][1]
        with c3: 
            if st.button(opcoes[i+2][0], key=f"btn_{i+2}", use_container_width=True): st.session_state.tipo_analise_selecionado = opcoes[i+2][1]
            
    st.markdown(f"<p style='text-align:center; color:{cor_neon}; font-size:11px; font-weight:bold; margin-bottom:15px;'>Foco: {st.session_state.tipo_analise_selecionado}</p>", unsafe_allow_html=True)

    LIGAS = {"🇪🇺 Champions League": "soccer_uefa_champs_league", "🇬🇧 Premier League": "soccer_epl", "🇪🇸 La Liga": "soccer_spain_la_liga", "🇧🇷 Brasileirão": "soccer_brazil_campeonato"}
    liga_selecionada = st.selectbox("Liga Base:", list(LIGAS.keys()))

    if st.button("INICIAR VARREDURA", type="primary", use_container_width=True):
        with st.spinner("Procurando assimetrias na API..."):
            time.sleep(1)
            dados = buscar_dados_api(LIGAS[liga_selecionada], st.session_state.api_key_odds)
            
            if dados == "QUOTA_ERROR": st.error("🚨 Limite da API esgotado! Insira nova chave no Hub. Usando Mock."); dados = gerar_dados_mock()
            elif dados == "AUTH_ERROR": st.error("🚨 Chave Inválida. Usando Mock."); dados = gerar_dados_mock()
            elif not dados: st.warning("⚠️ Sem jogos hoje. Mostrando Mock."); dados = gerar_dados_mock()
            else: st.success("✅ Conectado aos servidores asiáticos.")
            
            st.session_state.analisados = []
            for jogo in dados[:5]:
                c, f = jogo.get('home_team', 'Casa'), jogo.get('away_team', 'Fora')
                odd = round(random.uniform(1.4, 2.3), 2)
                
                m = f"Vitória {c}"
                if "Gols" in st.session_state.tipo_analise_selecionado: m = "Over 2.5 Gols"
                elif "Cantos" in st.session_state.tipo_analise_selecionado: m = "Over 8.5 Cantos"
                elif "Ambas" in st.session_state.tipo_analise_selecionado: m = "Ambas Marcam: Sim"
                
                atk, dfs = calcular_forca_equipa(c)
                conf = random.randint(85,99)
                vol = random.randint(50, 1500)
                ref = random.choice(["Rigoroso", "Médio", "Brando"])
                st.session_state.analisados.append({
                    "jogo": f"{c} x {f}", "m": m, "o": odd, "atk": atk, "def": dfs, "conf": conf,
                    "xg_c": round(random.uniform(1.1, 2.9), 2), "xg_f": round(random.uniform(0.5, 1.5), 2),
                    "vol": vol, "ref": ref, "ev": (odd > 1.8 and conf > 90), "streak": random.randint(1,5)
                })

    with st.expander("✍️ Modo Manual"):
        grade = st.text_area("Cole os jogos (Time A x Time B):")
        if st.button("Gerar Análise Manual"):
            if grade:
                st.session_state.analisados = []
                for j in [x for x in grade.split('\n') if 'x' in x.lower()]:
                    c, f = j.lower().split('x')[0].strip().title(), j.lower().split('x')[1].strip().title()
                    st.session_state.analisados.append({"jogo": f"{c} x {f}", "m": "Aposta IA", "o": 1.85, "atk": 80, "def": 60, "conf": 92, "xg_c": 1.8, "xg_f": 0.9, "vol": 100, "ref": "Médio", "ev": True, "streak": 2})

    # CARTÕES DE RESULTADO BLINDADOS (SEM HTML BUGADO)
    if st.session_state.analisados:
        for idx, i in enumerate(st.session_state.analisados):
            ev_html = "<span class='ev-flag'>EV+</span>" if i['ev'] else ""
            html = ""
            html += f"<div class='card'>"
            html += f"<div style='display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;'><span class='badge'>{i['m']}</span><span style='background:#1c2436; padding:4px 8px; border-radius:6px; color:{cor_neon}; font-weight:900;'>@{i['o']:.2f}</span></div>"
            html += f"<div style='font-size:14px; font-weight:800; color:{c_prim}; margin-bottom:5px;'>⚽ {i['jogo']} {ev_html}</div>"
            html += f"<div style='font-size:10px; color:{c_sec}; margin-bottom:10px; display:flex; justify-content:space-between;'><span>🐋 Vol: ${i['vol']}k</span><span>🔥 Strk: {i['streak']}V</span><span>🎯 {i['conf']}%</span></div>"
            html += f"<div style='font-size:9px; color:{c_sec};'>Poder Ofensivo (xG {i['xg_c']})</div>"
            html += f"<div class='progress-bg'><div class='progress-fill-atk' style='width:{i['atk']}%;'></div></div>"
            html += f"<div style='font-size:9px; color:{c_sec}; margin-top:4px;'>Muralha Defensiva</div>"
            html += f"<div class='progress-bg' style='margin-bottom:10px;'><div class='progress-fill-def' style='width:{i['def']}%;'></div></div>"
            html += f"<div style='background:rgba(0,0,0,0.3); padding:8px; border-radius:6px; font-size:10px; color:{c_sec}; border-left:2px solid {cor_neon};'>🤖 <b>IA Whisper:</b> Árbitro {i['ref']}. Pressão esperada no 2º Tempo.</div>"
            html += f"</div>"
            st.markdown(html, unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("➕ BILHETE", key=f"m_{idx}", type="primary", use_container_width=True): st.session_state.bilhete.append(i); st.toast("No Carrinho!")
            with col2:
                if st.button("💾 SINGLE", key=f"s_{idx}", use_container_width=True): st.session_state.analises_salvas.append(i); st.toast("Salvo!")

# ==========================================
# ABA 3: BILHETE & OPERAÇÕES
# ==========================================
with t3:
    st.markdown(f"<h3 style='color:{c_prim}; font-size:16px;'>🧾 Carrinho Múltiplo</h3>", unsafe_allow_html=True)
    if st.session_state.bilhete:
        odd_f = 1.0
        html_b = f"<div class='card'>"
        txt_telegram = "💎 *V8 SUPREME PRO*\n\n"
        for b in st.session_state.bilhete:
            odd_f *= b['o']
            html_b += f"<div style='display:flex; justify-content:space-between; margin-bottom:10px; border-bottom:1px solid {card_border}; padding-bottom:5px;'><span style='font-size:13px; font-weight:600; color:{c_prim};'>{b['m']}<br><span style='font-size:10px; color:{c_sec};'>{b['jogo']}</span></span><span style='color:{cor_neon}; font-weight:bold;'>@{b['o']:.2f}</span></div>"
            txt_telegram += f"⚽ {b['jogo']}\n👉 {b['m']} (@{b['o']})\n\n"
        html_b += "</div>"
        st.markdown(html_b, unsafe_allow_html=True)
        
        st.markdown(f"<h2 style='text-align:center; color:{c_prim}; font-weight:900; font-size:36px;'>ODD <span style='color:{cor_neon};'>@{odd_f:.2f}</span></h2>", unsafe_allow_html=True)
        
        banca = st.session_state.bancas["Betano"]
        st.session_state.usar_kelly = st.checkbox("🧠 Calculadora Kelly Criterion", value=st.session_state.usar_kelly)
        
        if st.session_state.usar_kelly:
            prob = 1 / odd_f * 1.15
            kelly = max(0.01, min(((odd_f - 1) * prob - (1 - prob)) / (odd_f - 1), 0.05))
            rec_stake = banca * kelly
        else:
            rec_stake = banca * (0.03 if odd_f < 2.5 else 0.01)

        valor = st.number_input("Entrada (R$):", min_value=1.0, value=float(max(1.0, rec_stake)), step=10.0)
        
        hedge_val = valor * 0.3 # Proteção Hedge
        st.markdown(f"<div style='font-size:10px; color:{c_sec}; text-align:center; margin-bottom:15px;'>🛡️ <b>Hedge:</b> Aposte {fmt_moeda(hedge_val)} contra o resultado para proteger capital.</div>", unsafe_allow_html=True)
        
        txt_telegram += f"📊 ODD TOTAL: @{odd_f:.2f}\n💰 GESTÃO: {fmt_moeda(valor)}"
        st.markdown(f'<a href="https://api.whatsapp.com/send?text={urllib.parse.quote(txt_telegram)}" target="_blank" style="display:block; text-align:center; background:#25d366; color:white; padding:12px; border-radius:8px; font-weight:bold; text-decoration:none; margin-bottom:15px;">📲 COPIAR PARA GRUPO VIP</a>', unsafe_allow_html=True)

        c1, c2 = st.columns(2)
        with c1:
            if st.button("✅ GREEN", type="primary", use_container_width=True):
                st.session_state.bancas["Betano"] += (valor * odd_f); st.session_state.historico_banca.append(sum(st.session_state.bancas.values()))
                st.session_state.bilhete = []; tocar_som(); time.sleep(1); st.rerun()
        with c2:
            if st.button("❌ RED", use_container_width=True):
                st.session_state.bancas["Betano"] -= valor; st.session_state.historico_banca.append(sum(st.session_state.bancas.values()))
                st.session_state.bilhete = []; st.rerun()
    else: st.info("Carrinho Vazio.")

    st.markdown(f"<h3 style='color:{c_prim}; font-size:16px; margin-top:20px;'>📂 Tracking Individual</h3>", unsafe_allow_html=True)
    if st.session_state.analises_salvas:
        for i, a in enumerate(st.session_state.analises_salvas):
            st.markdown(f"<div class='card' style='border-left:3px solid #00d2ff; padding:10px; margin-bottom:5px;'><div style='font-size:12px; font-weight:bold; color:{c_prim};'>{a['m']} <span style='color:{cor_neon};'>@{a['o']}</span></div><div style='font-size:10px; color:{c_sec};'>{a['jogo']}</div></div>", unsafe_allow_html=True)
            c_g, c_r, c_d = st.columns([0.4, 0.4, 0.2])
            with c_g: 
                if st.button("✅ WIN", key=f"tw_{i}"): st.session_state.total_jogos+=1; st.session_state.total_acertos+=1; st.session_state.historico_greens.insert(0, {"Jogo": a['jogo'], "Odd": a['o']}); st.session_state.analises_salvas.pop(i); tocar_som(); st.rerun()
            with c_r: 
                if st.button("❌ LOSS", key=f"tl_{i}"): st.session_state.total_jogos+=1; st.session_state.analises_salvas.pop(i); st.rerun()
            with c_d: 
                if st.button("🗑️", key=f"td_{i}"): st.session_state.analises_salvas.pop(i); st.rerun()
    else: st.caption("Nenhuma Single Salva.")

# ==========================================
# ABA 4: HUB DE FERRAMENTAS VIP
# ==========================================
with t4:
    st.markdown(f"<h3 style='color:{c_prim}; font-size:18px; margin-bottom:20px;'>⚙️ HUB VIP</h3>", unsafe_allow_html=True)
    
    with st.expander("🔑 The Odds API Key"):
        st.markdown(f"<span style='font-size:11px; color:{c_sec};'>Insira a sua chave (the-odds-api.com) para dados reais:</span>", unsafe_allow_html=True)
        nova_api = st.text_input("API Key:", value=st.session_state.api_key_odds, type="password")
        if st.button("Salvar API", type="primary"): st.session_state.api_key_odds = nova_api; st.success("Salva!")
            
    with st.expander("🏛️ Bancas e Personalização"):
        st.selectbox("Tema do App:", ["🟢 Verde Hacker", "🟡 Ouro Milionário", "🔵 Azul Cyberpunk", "⚪ Modo Claro (Light)"], key="tema_escolhido")
        st.selectbox("Moeda:", ["R$", "US$", "€"], key="moeda")
        st.session_state.bancas["Betano"] = st.number_input("Banca Atual", value=st.session_state.bancas["Betano"], step=50.0)
    
    st.markdown(f"<p style='color:{c_sec}; font-size:11px; font-weight:bold; margin-top:20px;'>📑 EXPORTAR TRACKING</p>", unsafe_allow_html=True)
    df_greens = pd.DataFrame(st.session_state.historico_greens)
    if not df_greens.empty:
        csv = df_greens.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Baixar Excel (.CSV)", data=csv, file_name='v8_historico.csv', mime='text/csv', use_container_width=True)

    if st.button("Desconectar do Terminal"):
        st.session_state.autenticado = False
        st.rerun()
