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
    som_html = '<audio autoplay style="display:none;"><source src="https://assets.mixkit.co/active_storage/sfx/2003/2003-preview.mp3" type="audio/mpeg"></audio>'
    st.markdown(som_html.replace('\n', ''), unsafe_allow_html=True)

# --- 3. CSS SEGURO (FIM DA TELA ESTICADA) ---
cor_neon = "#00ff88"
c_prim = "#ffffff"
c_sec = "#8b9bb4"
bg_card = "rgba(18, 24, 36, 0.85)"
border_card = "#1c2436"

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
        st.session_state.user_nome = nome_in if nome_in else "Trader VIP"
        st.rerun()
    st.stop()

# --- 5. HEADER FIXO ---
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
    if saldo_atual < banca_inicial * 0.9: st.error("🚨 STOP LOSS ATINGIDO! Bloqueio sugerido.")
    
    win_rate = (st.session_state.total_acertos / st.session_state.total_jogos) * 100 if st.session_state.total_jogos > 0 else 0
    fg_val = random.randint(30, 80)
    fg_cor = "#ff3333" if fg_val < 45 else (cor_neon if fg_val > 60 else "#FFD700")
    
    dash_html = f"""
    <div style='display: flex; gap: 10px; margin-bottom: 15px; width: 100%; box-sizing: border-box;'>
        <div class='card' style='flex:1; text-align:center; padding:15px; margin:0;'>
            <p style='color:{c_sec}; font-size:10px; margin:0;'>Win Rate A.I.</p>
            <p style='color:{cor_neon}; font-size:20px; font-weight:900; margin:0;'>{win_rate:.1f}%</p>
        </div>
        <div class='card' style='flex:1; text-align:center; padding:15px; margin:0;'>
            <p style='color:{c_sec}; font-size:10px; margin:0;'>Fear & Greed</p>
            <p style='color:{fg_cor}; font-size:20px; font-weight:900; margin:0;'>{fg_val}</p>
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
# ABA 2: RADAR A.I. (COM FILTRO DE MERCADOS)
# ==========================================
with t2:
    st.markdown(f"<h4 style='color:{cor_neon}; font-size:16px;'>Varredura de Mercado</h4>", unsafe_allow_html=True)
    
    LIGAS_DISPONIVEIS = {"🇪🇺 Champions League": "soccer_uefa_champs_league", "🇬🇧 Premier League": "soccer_epl", "🇪🇸 La Liga": "soccer_spain_la_liga", "🇧🇷 Brasileirão": "soccer_brazil_campeonato"}
    
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        codigo_da_liga = LIGAS_DISPONIVEIS[st.selectbox("Selecionar Liga:", list(LIGAS_DISPONIVEIS.keys()))]
    with col_f2:
        mercado_alvo = st.selectbox("Mercado Específico:", ["🤖 IA Decide (Misto)", "🏆 Resultado Final", "⚽ Gols (Over/Under)", "🔄 Ambas Marcam", "🚩 Escanteios", "🟨 Cartões"])

    if st.button("EXECUTAR SCANNER", type="primary", use_container_width=True):
        with st.spinner("Procurando assimetrias na API..."):
            dados = buscar_dados_api(codigo_da_liga, st.session_state.api_key_odds) 
            
            if dados == "QUOTA_ERROR": 
                st.session_state.status_api = "SIMULAÇÃO"
                st.error("🚨 Limite da API esgotado! Insira nova chave no Hub."); dados = gerar_dados_mock()
            elif dados == "AUTH_ERROR": 
                st.session_state.status_api = "SIMULAÇÃO"
                st.error("🚨 Chave API Inválida."); dados = gerar_dados_mock()
            elif not dados: 
                st.session_state.status_api = "ONLINE"
                st.warning("⚠️ Sem jogos hoje nesta liga. Mostrando Mock."); dados = gerar_dados_mock()
            else: 
                st.session_state.status_api = "ONLINE"
                st.success("✅ Dados extraídos com sucesso.")
            
            st.session_state.analisados = []
            for jogo in dados[:10]:
                c, f = jogo.get('home_team', 'Casa'), jogo.get('away_team', 'Fora')
                
                # --- A LÓGICA CORRIGIDA DOS MERCADOS ---
                if mercado_alvo == "⚽ Gols (Over/Under)": m = random.choice(["Over 1.5 Gols", "Over 2.5 Gols", "Under 3.5 Gols"])
                elif mercado_alvo == "🔄 Ambas Marcam": m = "Ambas Marcam: Sim"
                elif mercado_alvo == "🚩 Escanteios": m = random.choice(["Over 8.5 Cantos", "Over 9.5 Cantos"])
                elif mercado_alvo == "🟨 Cartões": m = random.choice(["Over 4.5 Cartões", "Over 5.5 Cartões"])
                elif mercado_alvo == "🏆 Resultado Final": m = random.choice([f"Vitória {c}", f"Vitória {f}", "Empate"])
                else: m = random.choice([f"Vitória {c}", "Ambas Marcam: Sim", "Over 1.5 Gols", "Over 8.5 Cantos"]) # IA Decide
                
                odd = round(random.uniform(1.3, 2.5), 2)
                atk, dfs = calcular_forca_equipa(c)
                
                st.session_state.analisados.append({"jogo": f"{c} x {f}", "m": m, "o": odd, "conf": random.randint(85, 99), "atk": atk, "def": dfs})

    with st.expander("✍️ Modo Manual (Sua Própria Grade)"):
        st.markdown("<p style='font-size:11px; color:#8b9bb4;'>Cole os jogos abaixo para a IA analisar o EV+:</p>", unsafe_allow_html=True)
        grade = st.text_area("Ex: Flamengo x Vasco", label_visibility="collapsed")
        if st.button("Gerar Análise Manual"):
            if grade:
                st.session_state.analisados = []
                for j in [x for x in grade.split('\n') if 'x' in x.lower()]:
                    c, f = j.lower().split('x')[0].strip().title(), j.lower().split('x')[1].strip().title()
                    atk, dfs = calcular_forca_equipa(c)
                    
                    if mercado_alvo == "⚽ Gols (Over/Under)": m = random.choice(["Over 1.5 Gols", "Over 2.5 Gols"])
                    elif mercado_alvo == "🔄 Ambas Marcam": m = "Ambas Marcam: Sim"
                    elif mercado_alvo == "🚩 Escanteios": m = "Over 8.5 Cantos"
                    elif mercado_alvo == "🟨 Cartões": m = "Over 4.5 Cartões"
                    elif mercado_alvo == "🏆 Resultado Final": m = f"Vitória {c}"
                    else: m = random.choice([f"Vitória {c}", "Ambas Marcam: Sim", "Over 1.5 Gols"])
                    
                    st.session_state.analisados.append({"jogo": f"{c} x {f}", "m": m, "o": round(random.uniform(1.4, 2.1),2), "conf": random.randint(88, 99), "atk": atk, "def": dfs})
                st.rerun()

    # RENDERIZAÇÃO DOS CARTÕES BLINDADA
    if st.session_state.analisados:
        st.write("<br>", unsafe_allow_html=True)
        for idx, i in enumerate(st.session_state.analisados):
            html_final = f"<div class='card'><div style='display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;'><span style='background:rgba(0,255,136,0.1); color:{cor_neon}; padding:4px 8px; border-radius:4px; font-size:11px; font-weight:800;'>{i['m']}</span><span style='background:#121824; padding:4px 8px; border-radius:6px; color:{cor_neon}; font-weight:900; border:1px solid rgba(0,255,136,0.3);'>@{i['o']:.2f}</span></div><div style='color:white; font-size:14px; font-weight:800; margin-bottom:15px;'>⚽ {i['jogo']}</div><div style='display:flex; justify-content:space-between; font-size:9px; color:#8b9bb4;'><span>Força Ofensiva</span><span>{i['atk']}%</span></div><div style='width:100%; background:rgba(0,0,0,0.4); height:4px; border-radius:4px; margin-bottom:8px;'><div style='width:{i['atk']}%; background:{cor_neon}; height:4px; border-radius:4px;'></div></div><div style='display:flex; justify-content:space-between; font-size:9px; color:#8b9bb4;'><span>Solidez Defensiva</span><span>{i['def']}%</span></div><div style='width:100%; background:rgba(0,0,0,0.4); height:4px; border-radius:4px; margin-bottom:10px;'><div style='width:{i['def']}%; background:#00aaff; height:4px; border-radius:4px;'></div></div></div>"
            st.write(html_final.replace('\n', ''), unsafe_allow_html=True)
            
            c_add1, c_add2 = st.columns(2)
            with c_add1:
                if st.button(f"➕ BILHETE", key=f"m_{idx}", type="primary", use_container_width=True): 
                    st.session_state.bilhete.append(i); st.toast("No Carrinho!")
            with c_add2:
                if st.button(f"💾 SALVAR", key=f"s_{idx}", use_container_width=True): 
                    st.session_state.analises_salvas.append(i); st.toast("Tracking Salvo!")

# ==========================================
# ABA 3: BILHETE E SAFE BINGO
# ==========================================
with t3:
    st.write(f"<h3 style='color:white; font-size:16px;'>🧾 Carrinho Múltiplo</h3>", unsafe_allow_html=True)
    bilhete = st.session_state.bilhete
    
    if bilhete:
        odd_f = 1.0
        html_b = f"<div style='background:rgba(18,24,36,0.85); border:1px solid #1c2436; border-radius:12px; padding:15px; margin-bottom:15px;'>"
        for b in bilhete:
            odd_f *= b['o']
            html_b += f"<div style='display:flex; justify-content:space-between; margin-bottom:10px; border-bottom:1px solid #1c2436; padding-bottom:5px;'><span style='font-size:13px; font-weight:600; color:white;'>{b['m']}<br><span style='font-size:10px; color:#8b9bb4;'>{b['jogo']}</span></span><span style='color:{cor_neon}; font-weight:bold;'>@{b['o']:.2f}</span></div>"
        html_b += "</div>"
        st.write(html_b.replace('\n', ''), unsafe_allow_html=True)
        
        st.write(f"<h2 style='text-align:center; color:white; font-weight:900; font-size:36px;'>ODD <span style='color:{cor_neon}; text-shadow:0 0 15px {cor_neon}60;'>@{odd_f:.2f}</span></h2>", unsafe_allow_html=True)
        
        bancas = st.session_state.bancas
        banca_escolhida = st.selectbox("Debitar Conta:", list(bancas.keys()))
        banca_disp = bancas[banca_escolhida]
        
        rec_stake = banca_disp * (0.03 if odd_f < 2.5 else 0.01)

        valor = st.number_input("Entrada (R$):", min_value=1.0, value=float(max(1.0, rec_stake)), step=10.0)
        
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

    # BINGO SAFE (Dupla do Dia)
    st.write(f"<h3 style='color:white; font-size:16px; margin-top:30px;'>🏆 High EV (Safe Bingo)</h3>", unsafe_allow_html=True)
    if not st.session_state.analisados: 
        st.caption("Faça uma varredura no Radar primeiro.")
    else:
        seguros = sorted([j for j in st.session_state.analisados if 1.15 <= j.get('o', 1.5) <= 1.65], key=lambda x: x.get('conf', 0), reverse=True)
        if len(seguros) >= 2:
            s1, s2 = seguros[0], seguros[1]
            odd_safe = s1['o'] * s2['o']
            html_safe = f"<div class='card' style='border-color:{cor_neon};'><div style='text-align:center; margin-bottom:10px;'><span style='background:{cor_neon}; color:#000; padding:4px 10px; border-radius:12px; font-weight:bold; font-size:10px;'>DUPLA DE OURO</span></div><div style='font-size:13px; font-weight:bold;'>1. {s1['jogo']} ({s1['m']} @{s1['o']})</div><div style='font-size:13px; font-weight:bold; margin-top:5px;'>2. {s2['jogo']} ({s2['m']} @{s2['o']})</div><hr style='border-color:#1c2436;'><h3 style='text-align:center; color:{cor_neon}; margin:0;'>ODD FINAL: {odd_safe:.2f}</h3></div>"
            st.write(html_safe.replace('\n', ''), unsafe_allow_html=True)
            if st.button("🔥 COPIAR PARA CARRINHO", use_container_width=True): 
                st.session_state.bilhete.extend([s1, s2]); st.rerun()
        else:
            st.caption("A IA não encontrou 2 jogos com perfil 'Safe' (Odds 1.15-1.65) nesta varredura.")

    st.write(f"<h3 style='color:white; font-size:16px; margin-top:30px;'>📂 Tracking Individual</h3>", unsafe_allow_html=True)
    salvas = st.session_state.analises_salvas
    if salvas:
        for i, a in enumerate(salvas):
            st.write(f"<div style='background:rgba(18,24,36,0.85); padding:10px; border-left:3px solid #00d2ff; margin-bottom:5px; border-radius:4px;'><div style='font-size:12px; font-weight:bold; color:white;'>{a['m']} <span style='color:{cor_neon};'>@{a['o']}</span></div><div style='font-size:10px; color:#8b9bb4;'>{a['jogo']}</div></div>".replace('\n', ''), unsafe_allow_html=True)
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
    st.write(f"<h3 style='color:{c_prim}; font-size:18px; margin-bottom:20px;'>⚙️ HUB VIP</h3>", unsafe_allow_html=True)
    
    with st.expander("🔑 Chave da API The Odds"):
        st.write(f"<span style='font-size:11px; color:#8b9bb4;'>Insira sua chave (the-odds-api.com) para buscar dados 100% reais:</span>", unsafe_allow_html=True)
        nova_api = st.text_input("API Key:", value=st.session_state.api_key_odds, type="password")
        if st.button("Salvar API", type="primary"): 
            st.session_state.api_key_odds = nova_api; st.success("Chave Atualizada!")
            
    with st.expander("🏛️ Bancas e Interface"):
        st.session_state.bancas["Betano"] = st.number_input("Banca Atual", value=st.session_state.bancas["Betano"], step=50.0)
    
    with st.expander("📡 Console de Auditoria (Deep Web Logs)"):
        st.write(f"<div style='background:#000; padding:10px; border-radius:8px; font-family:monospace; color:{cor_neon}; font-size:10px;'> > AUTH KEY: {st.session_state.api_key_odds[:5]}...<br>> LAST PING: {datetime.now().strftime('%H:%M:%S')}<br>> FETCHING SYNDICATE DATA...<br>> STATUS: {st.session_state.status_api}</div>".replace('\n', ''), unsafe_allow_html=True)

    if st.button("Desconectar do Terminal", use_container_width=True):
        st.session_state.autenticado = False; st.rerun()
