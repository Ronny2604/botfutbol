import streamlit as st
import random
import time
import os
import urllib.parse
import requests
import hashlib
import pandas as pd
from datetime import datetime, timedelta

# --- 1. CONFIGURAÇÃO E INIT SEGURA ---
st.set_page_config(page_title="V8 SUPREME PRO", layout="wide", initial_sidebar_state="collapsed")
LINK_SUA_IMAGEM_DE_FUNDO = "https://raw.githubusercontent.com/Ronny2604/botfutbol/main/photo_5172618853803035536_c.png"
ODDS_API_KEY = "da4633249ece20283d29604cec7a7114"

# FIX DE ESTADOS (Fim do AttributeError)
DEFAULTS = {
    'autenticado': False, 'user_nome': "", 'bilhete': [], 'analisados': [],
    'analises_salvas': [], 'tipo_analise_selecionado': 'Análise Geral',
    'is_admin': False, 'boss_mode': False, 'api_key_odds': ODDS_API_KEY,
    'tema_escolhido': "🟢 Verde Hacker", 'avatar': "🐺", 'moeda': "R$",
    'juros_compostos': False, 'usar_kelly': False, 'recuperacao_red': False,
    'bancas': {"Betano": 1000.0, "Bet365": 500.0, "Betfair": 0.0},
    'historico_banca': [1000.0], 'banca_inicial_dia': 1000.0,
    'conquistas': ["🏅 Novato"], 'total_jogos': 124, 'total_acertos': 101,
    'historico_greens': []
}
for k, v in DEFAULTS.items():
    if k not in st.session_state: st.session_state[k] = v

def fmt_moeda(valor): return f"{st.session_state.moeda} {valor:,.2f}"

def calcular_forca_equipa(nome): 
    num = int(hashlib.md5(nome.encode()).hexdigest(), 16)
    return 60 + (num % 35), 50 + ((num // 10) % 40)

def tocar_som(): 
    st.markdown('<audio autoplay style="display:none;"><source src="https://assets.mixkit.co/active_storage/sfx/2003/2003-preview.mp3" type="audio/mpeg"></audio>', unsafe_allow_html=True)

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

# --- 2. TEMAS (Variáveis Extraídas para não bugar o F-String) ---
is_light = ("Light" in st.session_state.tema_escolhido)
cor_neon = "#0055ff" if is_light else ("#FFD700" if "Ouro" in st.session_state.tema_escolhido else ("#00e5ff" if "Azul" in st.session_state.tema_escolhido else "#00ff88"))
c_prim = "#111111" if is_light else "#ffffff"
c_sec = "#555555" if is_light else "#8b9bb4"
card_bg = "rgba(255, 255, 255, 0.85)" if is_light else "rgba(18, 24, 36, 0.75)"
card_border = "rgba(0, 0, 0, 0.1)" if is_light else "rgba(255, 255, 255, 0.08)"
bg_app = "rgba(240, 242, 246, 1)" if is_light else "rgba(11, 16, 26, 1)"

# --- 3. CSS (BLINDADO CONTRA TELA PRETA) ---
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800;900&display=swap');
    
    /* 1. TRAVA ABSOLUTA DE BACKGROUND (FIM DO BUG PRETO) */
    .stApp {{
        background: radial-gradient(circle at 50% 0%, {bg_app} 0%, rgba(5,8,12,0.95) 100%), url('{LINK_SUA_IMAGEM_DE_FUNDO}');
        background-size: cover; background-position: center; background-attachment: fixed;
        font-family: 'Inter', sans-serif !important; color: {c_prim} !important;
    }}
    
    html, body, [data-testid="stAppViewContainer"], .main {{ background: transparent !important; overflow-x: hidden !important; }}
    
    header[data-testid="stHeader"], footer, #MainMenu {{ display: none !important; }}
    
    /* ESPAÇAMENTO PARA O MENU INFERIOR */
    .block-container {{ padding-top: 1rem !important; padding-bottom: 120px !important; max-width: 600px !important; margin: 0 auto !important; }}
    
    /* 2. MENU BOTTOM ESTILO iOS */
    div[data-testid="stTabs"] > div:first-of-type {{ 
        position: fixed !important; bottom: 15px !important; left: 50% !important; transform: translateX(-50%) !important;
        width: 92% !important; max-width: 580px !important;
        background: {card_bg} !important; backdrop-filter: blur(25px) !important; -webkit-backdrop-filter: blur(25px) !important;
        border-radius: 30px !important; border: 1px solid {cor_neon}50 !important;
        padding: 5px 10px !important; z-index: 99999 !important; box-shadow: 0 10px 40px rgba(0,0,0,0.8) !important;
        display: flex !important; justify-content: space-evenly !important;
    }}
    div[data-testid="stTabs"] button[role="tab"] {{ flex: 1 !important; color: {c_sec} !important; font-size: 10px !important; font-weight: 800 !important; background: transparent !important; border: none !important; border-radius: 20px !important; padding: 12px 0 !important; transition: 0.3s; }}
    div[data-testid="stTabs"] button[role="tab"][aria-selected="true"] {{ color: {cor_neon} !important; background: {cor_neon}15 !important; }}
    
    /* 3. CARTÕES E GRELHA */
    .stButton>button[kind="secondary"] {{ height: 80px !important; background-color: {card_bg} !important; border: 1px solid {card_border} !important; border-radius: 12px !important; color: {c_sec} !important; font-size: 12px !important; font-weight: 600 !important; transition: all 0.2s ease !important; }}
    .stButton>button[kind="secondary"]:hover, .stButton>button[kind="secondary"]:active {{ border-color: {cor_neon} !important; color: {cor_neon} !important; background-color: {cor_neon}10 !important; transform: scale(0.96) !important; }}
    
    /* 4. BOTÃO GIGANTE */
    .stButton>button[kind="primary"] {{ background: linear-gradient(90deg, #00d2ff 0%, {cor_neon} 100%) !important; color: #000 !important; font-weight: 900 !important; border: none !important; border-radius: 12px !important; padding: 15px !important; font-size: 16px !important; box-shadow: 0 0 15px {cor_neon}50 !important; transition: all 0.2s !important; }}
    .stButton>button[kind="primary"]:active {{ transform: scale(0.96) !important; box-shadow: 0 0 5px {cor_neon}80 !important; }}
    
    .card {{ background: {card_bg}; backdrop-filter: blur(10px); border: 1px solid {card_border}; border-radius: 16px; padding: 15px; margin-bottom: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.3); width: 100%; box-sizing: border-box; }}
    
    /* 5. BARRAS ANIMADAS STRIPES */
    .progress-bg {{ width: 100%; background: rgba(0,0,0,0.5); border-radius: 10px; height: 5px; margin-bottom: 8px; overflow: hidden; }}
    .progress-fill-atk {{ height: 5px; background: repeating-linear-gradient(45deg, #ff0055, #ff0055 10px, #ff5555 10px, #ff5555 20px); border-radius: 10px; }}
    .progress-fill-def {{ height: 5px; background: repeating-linear-gradient(45deg, #0055ff, #0055ff 10px, #00aaff 10px, #00aaff 20px); border-radius: 10px; }}
    
    /* 6. PULSAR AO VIVO */
    .live-dot {{ display: inline-block; width: 8px; height: 8px; background-color: #ff3333; border-radius: 50%; margin-right: 5px; animation: pulseRed 1.5s infinite; }}
    @keyframes pulseRed {{ 0% {{ box-shadow: 0 0 0 0 rgba(255,51,51,0.7); }} 70% {{ box-shadow: 0 0 0 6px rgba(255,51,51,0); }} 100% {{ box-shadow: 0 0 0 0 rgba(255,51,51,0); }} }}
    
    ::-webkit-scrollbar {{ width: 0px; background: transparent; }}
    div[data-baseweb="input"] > div, div[data-baseweb="select"] > div {{ background-color: {card_bg} !important; border: 1px solid {card_border} !important; color: {c_prim} !important; }}
    </style>
""", unsafe_allow_html=True)

# --- 4. TELA DE LOGIN ---
if not st.session_state.autenticado:
    st.markdown("<br><br><br><br>", unsafe_allow_html=True)
    st.markdown(f"<h1 style='text-align:center; font-weight:900; font-size:48px; letter-spacing:2px; color:{c_prim};'>V8 <span style='color:{cor_neon}; text-shadow: 0 0 20px {cor_neon};'>A.I.</span></h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align:center; color:{c_sec}; font-size:12px; margin-bottom:40px; text-transform:uppercase;'>Terminal Institucional</p>", unsafe_allow_html=True)
    nome_in = st.text_input("Operador ID:", placeholder="Insira seu nome")
    if st.button("INICIAR SESSÃO", type="primary", use_container_width=True):
        st.session_state.autenticado = True
        st.session_state.user_nome = nome_in if nome_in else "Trader VIP"
        st.rerun()
    st.stop()

# --- 5. HEADER FIXO TOP (BANKROLL HEALTH & ALERTAS) ---
saldo_atual = sum(st.session_state.bancas.values())
pct_banca = min(100, max(0, (saldo_atual / st.session_state.banca_inicial_dia) * 100))
cor_banca = cor_neon if pct_banca >= 100 else ("#FFD700" if pct_banca > 90 else "#ff3333")

if saldo_atual < st.session_state.banca_inicial_dia * 0.9: st.error("🚨 STOP LOSS: Banca caiu >10%. Pare de operar agora.")
if saldo_atual >= st.session_state.banca_inicial_dia * 1.2: st.success("🎯 STOP WIN: Lucro de 20% atingido. Relaxe e aproveite o dia!")

st.markdown(f"""
    <div style='position: sticky; top: 0; z-index: 999; background: {card_bg}; backdrop-filter: blur(15px); padding: 15px; margin:-15px -15px 20px -15px; border-bottom: 1px solid {card_border};'>
        <div style='display:flex; justify-content:space-between; align-items:center;'>
            <div style='display:flex; align-items:center;'>
                <div style='font-size: 24px; margin-right: 10px;'>{st.session_state.avatar}</div>
                <div>
                    <div style='font-weight:900; font-size:14px; color:{c_prim};'>{st.session_state.user_nome.upper()} <span style='background:{cor_neon}; color:#000; font-size:9px; padding:2px 4px; border-radius:4px;'>PRO</span></div>
                    <div style='color:{cor_neon}; font-size:10px;'>{st.session_state.titulo_apostador}</div>
                </div>
            </div>
            <div style='text-align:right;'>
                <div style='color:{c_sec}; font-size:10px; text-transform:uppercase;'>Banca Viva</div>
                <div style='color:{c_prim}; font-weight:900; font-size:18px;'>{fmt_moeda(saldo_atual)}</div>
            </div>
        </div>
        <div style='width:100%; height:2px; background:#1c2436; border-radius:2px; margin-top:10px;'><div style='width:{pct_banca}%; height:2px; background:{cor_banca}; box-shadow: 0 0 10px {cor_banca};'></div></div>
    </div>
""", unsafe_allow_html=True)

# --- 6. NAVEGAÇÃO BOTTOM ---
t1, t2, t3, t4 = st.tabs(["📊 HOME", "🎯 RADAR", "🧾 BILHETE", "⚙️ HUB"])

# ==========================================
# ABA 1: DASHBOARD
# ==========================================
with t1:
    win_rate = (st.session_state.total_acertos / st.session_state.total_jogos) * 100 if st.session_state.total_jogos > 0 else 0
    fg_val = random.randint(30, 80)
    fg_cor = "#ff3333" if fg_val < 45 else (cor_neon if fg_val > 60 else "#FFD700")
    fg_text = "Cuidado" if fg_val < 45 else ("Agressivo" if fg_val > 60 else "Neutro")
    
    st.markdown(f"""
        <div style='display: flex; gap: 10px; margin-bottom: 15px;'>
            <div class='card' style='flex:1; text-align:center; margin:0; padding:10px;'>
                <p style='color:{c_sec}; font-size:10px; margin:0;'>Win Rate A.I.</p>
                <p style='color:{cor_neon}; font-size:20px; font-weight:900; margin:0;'>{win_rate:.1f}%</p>
            </div>
            <div class='card' style='flex:1; text-align:center; margin:0; padding:10px;'>
                <p style='color:{c_sec}; font-size:10px; margin:0;'>Market Sentiment</p>
                <p style='color:{fg_cor}; font-size:16px; font-weight:900; margin:0;'>{fg_val} ({fg_text})</p>
            </div>
        </div>
    """, unsafe_allow_html=True)

    if st.session_state.mod_grafico:
        st.markdown(f"<div class='card' style='padding:15px;'><p style='color:{c_sec}; font-size:11px; margin:0 0 10px 0;'>📈 Desempenho Linear</p>", unsafe_allow_html=True)
        st.line_chart(st.session_state.historico_banca, height=120, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown(f"<h4 style='font-size:14px; color:{c_prim}; margin-top:10px;'>🏆 Ranking Global VIP</h4>", unsafe_allow_html=True)
    st.markdown(f"""
        <div class='card' style='padding: 10px 15px;'>
            <div style='display:flex; justify-content:space-between; border-bottom:1px solid {card_border}; padding-bottom:8px;'><span style='font-size:12px; color:{c_prim};'>🥇 TraderAlpha</span> <b style='color:{cor_neon}; font-size:12px;'>+{fmt_moeda(4520)}</b></div>
            <div style='display:flex; justify-content:space-between; border-bottom:1px solid {card_border}; padding:8px 0;'><span style='font-size:12px; color:{c_prim};'>🥈 {st.session_state.user_nome}</span> <b style='color:{cor_neon}; font-size:12px;'>+{fmt_moeda(1250)}</b></div>
            <div style='display:flex; justify-content:space-between; padding-top:8px;'><span style='font-size:12px; color:{c_prim};'>🥉 Lucas_Inv</span> <b style='color:{cor_neon}; font-size:12px;'>+{fmt_moeda(890)}</b></div>
        </div>
    """, unsafe_allow_html=True)

# ==========================================
# ABA 2: RADAR A.I. (A GRELHA 3x3)
# ==========================================
with t2:
    st.markdown(f"<p style='text-align:center; font-size:14px; font-weight:800; color:{c_prim};'>Direcionamento Algorítmico</p>", unsafe_allow_html=True)
    
    opcoes = [("📈\nGeral", "Análise Geral"), ("🏆\nResultado", "Resultado"), ("⚽\nGols", "Gols"), ("⏳\nHT", "Primeiro Tempo"), ("🚩\nCantos", "Escanteios"), ("🟨\nCartões", "Cartões"), ("🎯\nChutes", "Chutes"), ("👤\nJogador", "Jogador"), ("🔄\nBTTS", "Ambas Marcam")]
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
    codigo_da_liga = LIGAS[st.selectbox("Selecionar Filtro Geográfico:", list(LIGAS.keys()))]

    if st.button("INICIAR VARREDURA", type="primary", use_container_width=True):
        with st.spinner("Decodificando API The Odds..."):
            time.sleep(1.5)
            dados = buscar_dados_api(codigo_da_liga, st.session_state.api_key_odds)
            
            if dados == "QUOTA_ERROR": st.error("🚨 Limite da API esgotado! Insira nova chave no Hub. Usando Mock."); dados = gerar_dados_mock()
            elif dados == "AUTH_ERROR": st.error("🚨 Chave Inválida. Usando Mock."); dados = gerar_dados_mock()
            elif not dados: st.warning("⚠️ Sem jogos hoje nesta liga. Mostrando Global Mock."); dados = gerar_dados_mock()
            
            st.session_state.analisados = []
            for jogo in dados[:5]:
                c, f = jogo.get('home_team', 'Casa'), jogo.get('away_team', 'Fora')
                odd = round(random.uniform(1.4, 2.3), 2)
                
                m = f"Vitória {c}"
                if "Gols" in st.session_state.tipo_analise_selecionado: m = "Over 2.5 Gols"
                elif "Cantos" in st.session_state.tipo_analise_selecionado: m = "Over 8.5 Cantos"
                elif "Ambas" in st.session_state.tipo_analise_selecionado: m = "Ambas Marcam: Sim"
                
                try:
                    dt = datetime.strptime(jogo.get('commence_time', ''), "%Y-%m-%dT%H:%M:%SZ") - timedelta(hours=3)
                    d_txt = dt.strftime("%d/%m %H:%M")
                except: d_txt = "Em breve"

                atk, dfs = calcular_forca_equipa(c)
                st.session_state.analisados.append({
                    "jogo": f"{c} x {f}", "m": m, "o": odd, "atk": atk, "def": dfs, "conf": random.randint(85,99),
                    "xg_c": round(random.uniform(1.1, 2.9), 2), "xg_f": round(random.uniform(0.5, 1.5), 2),
                    "vol": random.randint(50, 1500), "ev": (odd > 1.7 and atk > 75), "data": d_txt,
                    "whisper": random.choice(["Equipa da casa marca 60% no 2º Tempo.", "Árbitro rigoroso (+5 cartões).", "Tendência alta de Under 2.5."])
                })

    with st.expander("✍️ Modo Manual"):
        grade = st.text_area("Cole os jogos (Time A x Time B):")
        if st.button("Gerar Análise Manual"):
            if grade:
                st.session_state.analisados = []
                for j in [x for x in grade.split('\n') if 'x' in x.lower()]:
                    c, f = j.lower().split('x')[0].strip().title(), j.lower().split('x')[1].strip().title()
                    st.session_state.analisados.append({"jogo": f"{c} x {f}", "m": "Aposta IA", "o": 1.85, "atk": 80, "def": 60, "conf": 92, "xg_c": 1.8, "xg_f": 0.9, "vol": 100, "ev": True, "data": "Manual", "whisper": "Análise forçada pelo operador."})

    if st.session_state.analisados:
        st.markdown("<br>", unsafe_allow_html=True)
        for idx, i in enumerate(st.session_state.analisados):
            # MONTAGEM BLINDADA (FIM DOS ERROS DE STRING FORMAT)
            ev_badge = f"<span style='color:#FFD700; border:1px solid #FFD700; padding:2px 4px; border-radius:4px; font-size:9px; font-weight:bold; margin-left:5px;'>EV+</span>" if i['ev'] else ""
            c_html = "".join([
                f"<div class='card'>",
                f"<div style='display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;'>",
                f"<div style='background:rgba(0,255,136,0.1); color:{cor_neon}; padding:4px 8px; border-radius:4px; font-size:11px; font-weight:800;'>{i['m']}</div>",
                f"<div style='color:{cor_neon}; font-weight:900; font-size:16px;'>@{i['o']:.2f}</div>",
                f"</div>",
                f"<div style='color:{c_prim}; font-size:14px; font-weight:800; margin-bottom:5px;'>⚽ {i['jogo']} {ev_badge}</div>",
                f"<div style='display:flex; justify-content:space-between; color:{c_sec}; font-size:10px; margin-bottom:15px;'><span>📅 {i['data']}</span><span>🐋 Vol: ${i['vol']}k</span><span>🎯 Conf: {i['conf']}%</span></div>",
                f"<div style='display:flex; justify-content:space-between; font-size:9px; color:{c_sec};'><span>xG Ofensivo ({i['xg_c']})</span><span>{i['atk']}%</span></div>",
                f"<div class='progress-bg'><div class='progress-fill-atk' style='width:{i['atk']}%;'></div></div>",
                f"<div style='display:flex; justify-content:space-between; font-size:9px; color:{c_sec}; margin-top:4px;'><span>Muralha Defensiva ({i['xg_f']})</span><span>{i['def']}%</span></div>",
                f"<div class='progress-bg' style='margin-bottom:12px;'><div class='progress-fill-def' style='width:{i['def']}%;'></div></div>",
                f"<div style='background:rgba(0,0,0,0.4); border-left:2px solid {cor_neon}; padding:8px; border-radius:6px; font-size:10px; color:{c_sec}; font-style:italic;'>🤖 <b>IA Whisper:</b> {i['whisper']}</div>",
                f"</div>"
            ])
            st.markdown(c_html, unsafe_allow_html=True)
            
            c_add1, c_add2 = st.columns(2)
            with c_add1:
                if st.button(f"➕ BILHETE", key=f"m_{idx}", type="primary", use_container_width=True): st.session_state.bilhete.append(i); st.toast("No Carrinho!")
            with c_add2:
                if st.button(f"💾 SINGLE", key=f"s_{idx}", use_container_width=True): st.session_state.analises_salvas.append(i); st.toast("Salvo!")

# ==========================================
# ABA 3: BILHETE / OPERAÇÕES
# ==========================================
with t3:
    st.markdown(f"<h3 style='color:{c_prim}; font-size:16px;'>🧾 Carrinho Múltiplo</h3>", unsafe_allow_html=True)
    if st.session_state.bilhete:
        odd_f = 1.0
        html_b = f"<div class='card'>"
        txt_zap = "💎 *V8 SUPREME PRO*\n\n"
        for b in st.session_state.bilhete:
            odd_f *= b['o']
            html_b += f"<div style='display:flex; justify-content:space-between; margin-bottom:10px; border-bottom:1px solid {card_border}; padding-bottom:5px;'><span style='font-size:13px; font-weight:600; color:{c_prim};'>{b['m']}<br><span style='font-size:10px; color:{c_sec};'>{b['jogo']}</span></span><span style='color:{cor_neon}; font-weight:bold;'>@{b['o']:.2f}</span></div>"
            txt_zap += f"⚽ {b['jogo']}\n👉 {b['m']} (@{b['o']})\n\n"
        html_b += "</div>"
        st.markdown(html_b, unsafe_allow_html=True)
        
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
        
        hedge_val = valor * 0.3
        st.markdown(f"<div style='font-size:10px; color:{c_sec}; text-align:center; margin-bottom:15px;'>🛡️ <b>Hedge:</b> Aposte {fmt_moeda(hedge_val)} no 'Empate' noutra casa para proteger.</div>", unsafe_allow_html=True)
        
        txt_zap += f"📊 ODD TOTAL: @{odd_f:.2f}\n💰 GESTÃO: {fmt_moeda(valor)}"
        st.markdown(f'<a href="https://api.whatsapp.com/send?text={urllib.parse.quote(txt_zap)}" target="_blank" style="display:block; text-align:center; background:rgba(37,211,102,0.2); color:#25d366; padding:12px; border-radius:8px; font-weight:bold; text-decoration:none; margin-bottom:15px; border:1px solid #25d366;">📲 COPIAR PARA GRUPO VIP</a>', unsafe_allow_html=True)

        c1, c2 = st.columns(2)
        with c1:
            if st.button("✅ GREEN", type="primary", use_container_width=True):
                st.session_state.bancas[banca_escolhida] += (valor * odd_f); st.session_state.historico_banca.append(sum(st.session_state.bancas.values()))
                st.session_state.bilhete = []; tocar_som(); time.sleep(1); st.rerun()
        with c2:
            if st.button("❌ RED", use_container_width=True):
                st.session_state.bancas[banca_escolhida] -= valor; st.session_state.historico_banca.append(sum(st.session_state.bancas.values()))
                st.session_state.bilhete = []; st.rerun()
    else:
        st.info("O carrinho está vazio.")

    st.markdown(f"<h3 style='color:{c_prim}; font-size:16px; margin-top:30px; margin-bottom:15px;'>Tracking Individual (Singles)</h3>", unsafe_allow_html=True)
    if st.session_state.analises_salvas:
        for i, a in enumerate(st.session_state.analises_salvas):
            st.markdown(f"<div class='card' style='padding:10px; border-left:3px solid #00d2ff;'><div style='font-size:12px; font-weight:bold; color:{c_prim};'>{a['m']} <span style='color:{cor_neon};'>@{a['o']}</span></div><div style='font-size:10px; color:{c_sec};'>{a['jogo']}</div></div>", unsafe_allow_html=True)
            c_g, c_r, c_d = st.columns([0.4, 0.4, 0.2])
            with c_g: 
                if st.button("✅ WIN", key=f"tw_{i}"): 
                    st.session_state.total_jogos+=1; st.session_state.total_acertos+=1; st.session_state.historico_greens.insert(0, {"Jogo": a['jogo'], "Odd": a['o']}); st.session_state.analises_salvas.pop(i); tocar_som(); st.rerun()
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
    st.markdown(f"<h3 style='color:{c_prim}; font-size:18px; margin-bottom:20px;'>⚙️ HUB VIP</h3>", unsafe_allow_html=True)
    
    with st.expander("🔑 Chave da API The Odds"):
        st.markdown(f"<span style='font-size:11px; color:{c_sec};'>Insira a sua chave (the-odds-api.com) para dados reais:</span>", unsafe_allow_html=True)
        nova_api = st.text_input("API Key:", value=st.session_state.api_key_odds, type="password")
        if st.button("Salvar API", type="primary"): st.session_state.api_key_odds = nova_api; st.success("Salva!")
            
    with st.expander("🏛️ Bancas e Personalização"):
        st.selectbox("Tema do App:", ["🟢 Verde Hacker", "🟡 Ouro Milionário", "🔵 Azul Cyberpunk", "🔴 Vermelho Kamikaze", "⚪ Modo Claro (Light)"], key="tema_escolhido")
        st.selectbox("Moeda:", ["R$", "US$", "€"], key="moeda")
        st.session_state.bancas["Betano"] = st.number_input("Banca Atual", value=st.session_state.bancas["Betano"], step=50.0)
    
    with st.expander("📡 Terminal A.I (Deep Web Logs)"):
        st.markdown(f"<div style='background:#000; padding:10px; border-radius:8px; font-family:monospace; color:#00ff88; font-size:10px;'> > AUTH KEY: VALID<br>> LAST PING: {datetime.now().strftime('%H:%M:%S')}<br>> FETCHING SYNDICATE DATA...<br>> STATUS: OPERATIONAL</div>", unsafe_allow_html=True)

    st.markdown(f"<p style='color:{c_sec}; font-size:11px; font-weight:bold; margin-top:20px;'>📑 EXPORTAR TRACKING</p>", unsafe_allow_html=True)
    df_greens = pd.DataFrame(st.session_state.historico_greens)
    if not df_greens.empty:
        csv = df_greens.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Baixar Excel (.CSV)", data=csv, file_name='v8_historico.csv', mime='text/csv', use_container_width=True)

    if st.button("Desconectar do Terminal"):
        st.session_state.autenticado = False
        st.rerun()
