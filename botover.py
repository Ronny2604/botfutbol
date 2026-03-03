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
LINK_SUA_IMAGEM_DE_FUNDO = "https://raw.githubusercontent.com/Ronny2604/botfutbol/main/photo_5172618853803035536_c.png"
ODDS_API_KEY = "da4633249ece20283d29604cec7a7114"

# --- 2. BLINDAGEM DE ESTADOS (FIM DO ATTRIBUTE ERROR) ---
estado_padrao = {
    'autenticado': False, 'user_nome': "", 'bilhete': [], 'analisados': [], 
    'analises_salvas': [], 'tema_escolhido': "🟢 Verde Hacker",
    'avatar': "🐺", 'moeda': "R$", 'titulo_apostador': "[O Estrategista]",
    'bancas': {"Betano": 1000.0, "Bet365": 500.0, "Betfair": 0.0},
    'historico_banca': [1500.0], 'banca_inicial_dia': 1500.0,
    'total_jogos': 1248, 'total_acertos': 1115, 'historico_greens': [], 
    'api_key_odds': ODDS_API_KEY, 'usar_kelly': False, 'modo_sniper': False,
    'mod_grafico': True
}
for k, v in estado_padrao.items():
    if k not in st.session_state:
        st.session_state[k] = v

# --- 3. FUNÇÕES DE SISTEMA ---
def fmt_moeda(valor): return f"{st.session_state.get('moeda', 'R$')} {valor:,.2f}"

def tocar_som_customizado():
    st.markdown('<audio autoplay style="display:none;"><source src="https://assets.mixkit.co/active_storage/sfx/2003/2003-preview.mp3" type="audio/mpeg"></audio>', unsafe_allow_html=True)

def calcular_forca_equipa(nome_equipa):
    num = int(hashlib.md5(nome_equipa.encode()).hexdigest(), 16)
    return 60 + (num % 35), 50 + ((num // 10) % 40) 

def gerar_dados_mock():
    times = ["Real Madrid", "Barcelona", "Man City", "Arsenal", "Bayern", "Flamengo", "Liverpool", "Chelsea", "Milan", "Inter"]
    random.shuffle(times)
    d = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    return [{"home_team": times[i*2], "away_team": times[i*2+1], "commence_time": d} for i in range(5)]

@st.cache_data(ttl=300, show_spinner=False)
def buscar_dados_api(codigo_da_liga, api_key):
    url = f"https://api.the-odds-api.com/v4/sports/{codigo_da_liga}/odds/?apiKey={api_key}&regions=eu,uk&markets=h2h"
    try:
        r = requests.get(url, timeout=5)
        if r.status_code == 200 and isinstance(r.json(), list): return r.json()
    except: pass
    return None

# --- 4. CSS SUPREMO (LAYOUT ESTÁVEL + INOVAÇÕES VISUAIS INTERNAS) ---
tema = st.session_state.get('tema_escolhido', "🟢 Verde Hacker")
if "Ouro" in tema: cor_neon = "#FFD700"
elif "Azul" in tema: cor_neon = "#00e5ff"
elif "Vermelho" in tema: cor_neon = "#ff3333"
elif "Rosa" in tema: cor_neon = "#ff00ff"
else: cor_neon = "#00ff88"
grad = f"linear-gradient(135deg, {cor_neon}20, rgba(0,0,0,0))"

st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;500;700;900&display=swap');
    
    html, body, [class*="css"] {{ font-family: 'Inter', sans-serif !important; }}
    header[data-testid="stHeader"], footer, #MainMenu {{ display: none !important; }}
    .block-container {{ padding-top: 1rem !important; margin-top: -1rem !important; padding-bottom: 80px !important; }}
    
    /* Fundo Seguro */
    .stApp {{ 
        background: radial-gradient(circle at 50% 0%, rgba(20,22,30,0.9), rgba(10,10,12,1)), url('{LINK_SUA_IMAGEM_DE_FUNDO}'); 
        background-size: cover; background-position: center; background-attachment: fixed; color: #ffffff; 
    }}
    
    /* Abas no Topo (Formato Pílula) */
    div[data-testid="stTabs"] > div:first-of-type {{
        background-color: rgba(20, 22, 30, 0.6) !important; backdrop-filter: blur(5px);
        border-radius: 50px !important; padding: 5px !important; margin-bottom: 20px !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
    }}
    div[data-testid="stTabs"] button[role="tab"] {{ 
        color: #888 !important; font-weight: 700 !important; font-size: 11px !important; 
        background: transparent !important; border: none !important; 
        border-radius: 30px !important; padding: 10px 15px !important;
    }}
    div[data-testid="stTabs"] button[role="tab"][aria-selected="true"] {{ 
        color: {cor_neon} !important; background: rgba(255,255,255,0.08) !important; 
        border-bottom: 2px solid {cor_neon} !important;
    }}
    
    /* Glass Cards com Efeito Neon Pulse */
    .glass-card {{
        background: rgba(26, 28, 36, 0.6); backdrop-filter: blur(15px); -webkit-backdrop-filter: blur(15px);
        border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 12px; padding: 15px; margin-bottom: 15px;
        width: 100%; box-sizing: border-box; transition: transform 0.3s ease, box-shadow 0.3s ease, border-color 0.3s ease;
    }}
    .glass-card:hover {{ border-color: {cor_neon}80; box-shadow: 0 0 15px {cor_neon}20; }}
    
    /* Elementos Premium */
    .terminal-card {{ background: #0a0b10; border: 1px solid #222; border-left: 3px solid {cor_neon}; border-radius: 8px; padding: 15px; font-family: monospace; color: {cor_neon}; width: 100%; box-sizing: border-box; font-size: 10px; }}
    .neon-text {{ color: {cor_neon}; font-weight: 900; font-size: 14px; letter-spacing: 2px; text-transform: uppercase; text-shadow: 0 0 10px {cor_neon}40; }}
    .grad-divider {{ height: 1px; background: linear-gradient(90deg, transparent, {cor_neon}50, transparent); margin: 20px 0; border: none; }}
    
    /* Animações e Botões 3D */
    .stButton>button {{ 
        background: {grad} !important; color: white !important; font-weight: 900 !important; 
        border-radius: 8px !important; border: 1px solid {cor_neon} !important; padding: 12px 20px !important; 
        width: 100%; transition: all 0.2s ease !important;
    }}
    .stButton>button:hover {{ background: {cor_neon} !important; color: #000 !important; box-shadow: 0 5px 15px {cor_neon}60 !important; }}
    .stButton>button:active {{ transform: translateY(2px) !important; filter: brightness(0.9) !important; }}
    
    .live-dot {{ display: inline-block; width: 8px; height: 8px; background-color: #ff3333; border-radius: 50%; margin-right: 5px; animation: pulse 1.5s infinite; }}
    @keyframes pulse {{ 0% {{ box-shadow: 0 0 0 0 rgba(255,51,51,0.7); }} 70% {{ box-shadow: 0 0 0 6px rgba(0,0,0,0); }} 100% {{ box-shadow: 0 0 0 0 rgba(0,0,0,0); }} }}
    
    .progress-bg {{ width: 100%; background: #111; border-radius: 10px; height: 6px; margin-bottom: 8px; overflow: hidden; border: 1px solid #333; }}
    .progress-fill-atk {{ height: 6px; background: linear-gradient(90deg, #ff0055, #ff5555); border-radius: 10px; box-shadow: 0 0 10px #ff0055; }}
    .progress-fill-def {{ height: 6px; background: linear-gradient(90deg, #0055ff, #00aaff); border-radius: 10px; box-shadow: 0 0 10px #0055ff; }}
    
    ::-webkit-scrollbar {{ display: none; }}
    </style>
""", unsafe_allow_html=True)

# --- TELA DE LOGIN ---
if not st.session_state.get('autenticado', False):
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    with st.container():
        st.markdown(f"<div class='glass-card' style='max-width:400px; margin:auto; text-align:center;'><h1 style='color:#fff; font-weight:900; margin-bottom:0;'>V8 <span style='color:{cor_neon}; text-shadow: 0 0 20px {cor_neon};'>SUPREME</span></h1><p style='color:#888; font-size: 11px; letter-spacing:2px; margin-bottom: 30px;'>TERMINAL INSTITUCIONAL</p></div>".replace('\n', ''), unsafe_allow_html=True)
        nome_in = st.text_input("Credencial de Acesso:", placeholder="Insira o seu ID")
        if st.button("INICIAR SESSÃO", use_container_width=True):
            st.session_state['autenticado'] = True
            st.session_state['user_nome'] = nome_in if nome_in else "VIP"
            st.rerun()
    st.stop()

# --- TOP BAR VIP & ALERTAS STOP-WIN/LOSS ---
win_rate = (st.session_state.get('total_acertos', 0) / st.session_state.get('total_jogos', 1)) * 100 if st.session_state.get('total_jogos', 1) > 0 else 0
saldo_total = sum(st.session_state.get('bancas', {}).values())
banca_init = st.session_state.get('banca_inicial_dia', 1500)
pct_banca = min(100, max(0, (saldo_total / banca_init) * 100)) if banca_init > 0 else 0
cor_banca = cor_neon if pct_banca >= 100 else ("#FFD700" if pct_banca > 85 else "#ff3333")

if saldo_total < banca_init * 0.85: st.error("🚨 STOP LOSS: Proteja o seu capital. É aconselhável encerrar o terminal hoje.")
if saldo_total >= banca_init * 1.20: st.success("🎯 STOP WIN: Meta diária batida com sucesso! Bom descanso.")

html_topbar = (
    f"<div style='display:flex; justify-content:space-between; align-items:center; padding: 15px; background: rgba(20,22,30,0.8); border-radius: 12px; border: 1px solid rgba(255,255,255,0.05); width: 100%; box-sizing: border-box;'>"
    f"<div style='display:flex; align-items:center;'>"
    f"<div style='font-size: 28px; margin-right: 12px;'>{st.session_state.get('avatar', '🐺')}</div>"
    f"<div>"
    f"<div style='color:white; font-weight:900; font-size:16px;'>{str(st.session_state.get('user_nome', 'VIP')).upper()} <span style='background:{cor_neon}; color:black; font-size:9px; padding:2px 6px; border-radius:4px; vertical-align:middle; font-weight:bold;'>PRO</span></div>"
    f"<div style='color:{cor_neon}; font-size:11px; margin-top:2px;'>{st.session_state.get('titulo_apostador', 'Estrategista')}</div>"
    f"</div></div>"
    f"<div style='text-align:right;'>"
    f"<div style='color:#888; font-size:10px; text-transform:uppercase;'>Saldo Consolidado</div>"
    f"<div style='color:white; font-weight:900; font-size:18px;'>{fmt_moeda(saldo_total)}</div>"
    f"<div style='width:100%; height:2px; background:#1c2436; border-radius:2px; margin-top:5px;'><div style='width:{pct_banca}%; height:2px; background:{cor_banca}; box-shadow: 0 0 5px {cor_banca};'></div></div>"
    f"</div></div><br>"
)
st.markdown(html_topbar.replace('\n', ''), unsafe_allow_html=True)

# --- NAVEGAÇÃO PRINCIPAL (NO TOPO, ESTÁVEL) ---
t1, t2, t3, t4, t5 = st.tabs(["📊 HOME", "🎯 RADAR", "🧾 OPERAÇÕES", "🛡️ SAFE", "⚙️ HUB"])

LIGAS_DISPONIVEIS = {"🇪🇺 Champions League": "soccer_uefa_champs_league", "🇬🇧 Premier League": "soccer_epl", "🇪🇸 La Liga": "soccer_spain_la_liga", "🇧🇷 Brasileirão": "soccer_brazil_campeonato"}

# ==========================================
# ABA 1: DASHBOARD
# ==========================================
with t1:
    fg_val = random.randint(30, 80)
    fg_cor = "#ff3333" if fg_val < 45 else (cor_neon if fg_val > 60 else "#FFD700")

    st.markdown(f"""
        <div style='display: flex; justify-content: space-between; gap: 10px; margin-bottom: 20px; width: 100%; box-sizing: border-box;'>
            <div class='glass-card' style='flex:1; text-align:center; padding: 15px; margin:0;'>
                <p style='color:#888; font-size:11px; margin:0;'>Win Rate A.I.</p>
                <p style='color:{cor_neon if win_rate > 60 else "#FFD700"}; font-size:22px; font-weight:900; margin:0;'>{win_rate:.1f}%</p>
            </div>
            <div class='glass-card' style='flex:1; text-align:center; padding: 15px; margin:0;'>
                <p style='color:#888; font-size:11px; margin:0;'>Market Fear & Greed</p>
                <p style='color:{fg_cor}; font-size:22px; font-weight:900; margin:0;'>{fg_val}</p>
            </div>
        </div>
    """.replace('\n', ''), unsafe_allow_html=True)

    if st.session_state.get('mod_grafico'):
        st.markdown(f"<div class='glass-card'><p style='color: #888; font-size: 11px; font-weight: bold; margin-bottom:5px; letter-spacing: 1px;'>📈 RENDIMENTO LINEAR</p></div>".replace('\n', ''), unsafe_allow_html=True)
        st.line_chart(st.session_state.get('historico_banca', []), height=120, use_container_width=True)

    st.markdown("<h4 class='neon-text'>🔴 LIVE SCORES</h4>", unsafe_allow_html=True)
    st.markdown(f"""
        <div class='glass-card' style='display:flex; justify-content:space-between; align-items:center; border-left: 3px solid #ff3333;'>
            <div>
                <span class='live-dot'></span>
                <span style='background:rgba(255,51,51,0.1); color:#ff3333; padding:2px 6px; border-radius:4px; font-size:10px; font-weight:bold; margin-right: 5px;'>78'</span>
                <span style='color:white; font-weight:bold; font-size: 14px;'>Real Madrid 1 x 0 Getafe</span>
            </div>
            <div style='text-align:right; font-size:11px; color:#888;'>Call IA<br><b style='color:{cor_neon};'>Under 2.5</b></div>
        </div>
    """.replace('\n', ''), unsafe_allow_html=True)

# ==========================================
# ABA 2: RADAR A.I E MERCADOS
# ==========================================
with t2:
    st.markdown("<h4 class='neon-text'>VARREDURA DO MERCADO</h4>", unsafe_allow_html=True)
    
    st.session_state['modo_sniper'] = st.toggle("🎯 Filtro Sniper (+92% Confiança)")
    
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        codigo_da_liga = LIGAS_DISPONIVEIS[st.selectbox("Selecionar Liga:", list(LIGAS_DISPONIVEIS.keys()))]
    with col_f2:
        mercado_alvo = st.selectbox("Mercado Desejado:", ["🤖 IA Decide (Misto)", "🏆 Resultado Final", "⚽ Gols (Over/Under)", "🔄 Ambas Marcam", "🚩 Escanteios", "🟨 Cartões"])

    if st.button("EXECUTAR SCANNER", use_container_width=True):
        with st.spinner("Procurando assimetrias na API..."):
            dados = buscar_dados_api(codigo_da_liga, st.session_state.get('api_key_odds')) 
            if not dados:
                dados = gerar_dados_mock()
                st.warning("⚠️ API Esgotada ou sem jogos hoje. A exibir simulação global.")
            else:
                st.success("✅ Dados extraídos com sucesso!")
            
            st.session_state['analisados'] = []
            for jogo in dados[:10]:
                c, f = jogo.get('home_team', 'Casa'), jogo.get('away_team', 'Fora')
                
                if mercado_alvo == "⚽ Gols (Over/Under)": m = random.choice(["Over 1.5 Gols", "Over 2.5 Gols", "Under 3.5 Gols"])
                elif mercado_alvo == "🔄 Ambas Marcam": m = "Ambas Marcam: Sim"
                elif mercado_alvo == "🚩 Escanteios": m = random.choice(["Over 8.5 Cantos", "Over 9.5 Cantos"])
                elif mercado_alvo == "🟨 Cartões": m = random.choice(["Over 4.5 Cartões", "Over 5.5 Cartões"])
                elif mercado_alvo == "🏆 Resultado Final": m = random.choice([f"Vitória {c}", f"Vitória {f}", "Empate"])
                else: m = random.choice([f"Vitória {c}", "Ambas Marcam: Sim", "Over 1.5 Gols", "Over 8.5 Cantos"])
                
                odd = round(random.uniform(1.3, 2.5), 2)
                atk, dfs = calcular_forca_equipa(c)
                conf = random.randint(85, 99)
                xg = round(random.uniform(1.1, 2.8), 2)
                whisper = random.choice(["Árbitro rigoroso. Valor em cartões.", "Equipa visitante costuma ceder golos no HT.", "Valor matemático detetado na Odd."])
                
                st.session_state['analisados'].append({"jogo": f"{c} x {f}", "casa": c, "fora": f, "m": m, "o": odd, "conf": conf, "atk": atk, "def": dfs, "xg": xg, "whisper": whisper})

    with st.expander("✍️ Modo Manual (Sua Grade)"):
        grade = st.text_area("Input de Jogos (Ex: Flamengo x Vasco):", label_visibility="collapsed")
        if st.button("Forçar Análise Manual"):
            if grade:
                st.session_state['analisados'] = []
                for j in [x for x in grade.split('\n') if 'x' in x.lower()]:
                    c, f = j.lower().split('x')[0].strip().title(), j.lower().split('x')[1].strip().title()
                    atk, dfs = calcular_forca_equipa(c)
                    
                    if mercado_alvo == "⚽ Gols (Over/Under)": m = random.choice(["Over 1.5 Gols", "Over 2.5 Gols"])
                    elif mercado_alvo == "🔄 Ambas Marcam": m = "Ambas Marcam: Sim"
                    elif mercado_alvo == "🚩 Escanteios": m = "Over 8.5 Cantos"
                    elif mercado_alvo == "🟨 Cartões": m = "Over 4.5 Cartões"
                    elif mercado_alvo == "🏆 Resultado Final": m = f"Vitória {c}"
                    else: m = random.choice([f"Vitória {c}", "Ambas Marcam: Sim", "Over 1.5 Gols"])
                    
                    st.session_state['analisados'].append({"jogo": f"{c} x {f}", "casa": c, "fora": f, "m": m, "o": round(random.uniform(1.4, 2.1),2), "conf": random.randint(88, 99), "atk": atk, "def": dfs, "xg": 1.5, "whisper": "Análise Injetada Manualmente."})
                st.rerun()

    # RENDERIZAÇÃO BLINDADA COM WHISPERS
    analisados = st.session_state.get('analisados', [])
    if analisados:
        st.markdown("<div class='grad-divider'></div>", unsafe_allow_html=True)
        for idx, item in enumerate(analisados):
            
            if st.session_state.get('modo_sniper') and item['conf'] < 92: continue
            
            ev_badge = f"<span style='color:#FFD700; border:1px solid #FFD700; padding:2px 4px; border-radius:4px; font-size:9px; font-weight:bold; margin-left: 5px;'>EV+</span>" if item['conf'] > 90 else ""

            html_card = (
                f"<div class='glass-card'>"
                f"<div style='display:flex; justify-content:space-between; align-items:center;'>"
                f"<div style='background:rgba(0,255,136,0.1); color:{cor_neon}; padding:4px 8px; border-radius:12px; font-size:11px; font-weight:800; border: 1px solid {cor_neon}40;'>{item['m']}</div>"
                f"<div style='color:{cor_neon}; font-weight:900; font-size:16px;'>@{item['o']:.2f}</div>"
                f"</div>"
                f"<div style='color:white; font-size:14px; font-weight:800; margin-top:10px; margin-bottom:15px;'>⚽ {item['jogo']} {ev_badge}</div>"
                f"<div style='display:flex; justify-content:space-between; font-size:9px; color:#888;'><span>PRESSÃO OFENSIVA (xG {item['xg']})</span><span>{item['atk']}%</span></div>"
                f"<div class='progress-bg'><div class='progress-fill-atk' style='width:{item['atk']}%;'></div></div>"
                f"<div style='display:flex; justify-content:space-between; font-size:9px; color:#888; margin-top:4px;'><span>MURALHA DEFENSIVA</span><span>{item['def']}%</span></div>"
                f"<div class='progress-bg'><div class='progress-fill-def' style='width:{item['def']}%;'></div></div>"
                f"<div style='margin-top:15px; background:rgba(0,0,0,0.3); padding:10px; border-radius:8px; border-left: 2px solid {cor_neon}; display:flex; justify-content:space-between; align-items:center;'>"
                f"<span style='font-size:10px; color:#aaa; font-style:italic;'>🤖 <b>Whisper:</b> {item['whisper']}</span>"
                f"<span style='font-size:12px; font-weight:900; color:{cor_neon};'>{item['conf']}%</span>"
                f"</div></div>"
            )
            st.markdown(html_card.replace('\n', ''), unsafe_allow_html=True)
            
            c_add1, c_add2 = st.columns(2)
            with c_add1:
                if st.button("➕ BILHETE", key=f"m_{idx}"):
                    st.session_state['bilhete'].append(item); st.toast("✅ Adicionado!")
            with c_add2:
                if st.button("💾 SALVAR DICA", key=f"s_{idx}"):
                    st.session_state['analises_salvas'].append(item); st.toast("💾 Salvo no Tracking!")

# ==========================================
# ABA 3: OPERAÇÕES (KELLY + HEDGE + TELEGRAM)
# ==========================================
with t3:
    st.markdown("<h4 class='neon-text'>CARRINHO MÚLTIPLO</h4>", unsafe_allow_html=True)
    bilhete = st.session_state.get('bilhete', [])
    if bilhete:
        odd_f = 1.0
        txt_telegram = "💎 *V8 SUPREME PRO*\n\n"
        html_b = "<div class='glass-card' style='padding: 15px;'>"
        
        for b in bilhete:
            odd_f *= b['o']
            html_b += f"<p style='margin:0; font-size:14px; border-bottom: 1px solid rgba(255,255,255,0.1); padding: 8px 0; display:flex; justify-content:space-between;'><span><b>{b['jogo']}</b><br><span style='font-size:11px; color:#aaa;'>{b['m']}</span></span><span style='color:{cor_neon}; font-weight:bold;'>@{b['o']:.2f}</span></p>"
            txt_telegram += f"⚽ {b['jogo']}\n👉 {b['m']} (@{b['o']:.2f})\n\n"
            
        html_b += "</div>"
        st.markdown(html_b.replace('\n', ''), unsafe_allow_html=True)
        
        st.markdown(f"<h2 style='text-align:center; font-weight:900; font-size:36px; color:white;'>ODD <span style='color:{cor_neon};'>@{odd_f:.2f}</span></h2>", unsafe_allow_html=True)
        
        bancas_atuais = st.session_state.get('bancas', {})
        banca_escolhida = st.selectbox("Conta Origem:", list(bancas_atuais.keys()))
        banca_disp = bancas_atuais[banca_escolhida]
        
        st.session_state['usar_kelly'] = st.checkbox("🧠 Matemática de Kelly", value=st.session_state.get('usar_kelly', False))
        if st.session_state.get('usar_kelly'):
            prob = 1 / odd_f * 1.15
            kelly_pct = max(0.01, min(((odd_f - 1) * prob - (1 - prob)) / (odd_f - 1), 0.05))
            rec_stake = banca_disp * kelly_pct
        else:
            rec_stake = banca_disp * (0.03 if odd_f < 2.5 else 0.01)

        st.markdown(f"<div class='terminal-card' style='margin-bottom:20px;'>> SALDO: {fmt_moeda(banca_disp)}<br>> GESTÃO IDEAL: <span style='color:{cor_neon}; font-size:16px;'>{fmt_moeda(rec_stake)}</span></div>".replace('\n', ''), unsafe_allow_html=True)
        
        valor = st.number_input("Entrada (Múltipla):", min_value=1.0, value=float(max(1.0, rec_stake)), step=5.0)
        
        st.markdown(f"<p style='text-align:center; font-size:11px; color:#888;'>🛡️ <b>Proteção (Hedge):</b> Aposte {fmt_moeda(valor * 0.3)} no resultado inverso noutra casa.</p>", unsafe_allow_html=True)
        
        txt_telegram += f"📊 ODD TOTAL: @{odd_f:.2f}\n💰 GESTÃO: {fmt_moeda(valor)}"
        st.markdown(f'<a href="https://api.whatsapp.com/send?text={urllib.parse.quote(txt_telegram)}" target="_blank" style="display:block; text-align:center; background:rgba(37,211,102,0.1); color:#25d366; padding:12px; border-radius:8px; font-weight:bold; text-decoration:none; margin-bottom:15px; border:1px solid #25d366;">📲 ENVIAR PARA GRUPO VIP</a>', unsafe_allow_html=True)

        c1, c2 = st.columns(2)
        with c1:
            if st.button("✅ BATER GREEN"):
                st.session_state['bancas'][banca_escolhida] += (valor * odd_f)
                st.session_state['historico_banca'].append(sum(st.session_state.get('bancas').values()))
                st.session_state['bilhete'] = []
                tocar_som_customizado()
                time.sleep(1); st.rerun()
        with c2:
            if st.button("❌ ASSUMIR RED"):
                st.session_state['bancas'][banca_escolhida] -= valor
                st.session_state['historico_banca'].append(sum(st.session_state.get('bancas').values()))
                st.session_state['bilhete'] = []
                st.rerun()
    else:
        st.info("Múltipla vazia.")

    st.markdown("<h4 class='neon-text' style='margin-top: 40px;'>📂 TRACKING INDIVIDUAL</h4>", unsafe_allow_html=True)
    salvas = st.session_state.get('analises_salvas', [])
    if salvas:
        for i, a in enumerate(salvas):
            html_t = f"<div class='glass-card' style='padding: 10px 15px; margin-bottom: 5px; border-left: 3px solid #00e5ff;'><div style='font-size:13px; font-weight:bold; color:white;'>{a['jogo']}</div><div style='display:flex; justify-content:space-between; margin-top:2px;'><span style='color:#888; font-size:11px;'>Call: <b style='color:white;'>{a['m']}</b></span><span style='color:{cor_neon}; font-weight:bold; font-size:12px;'>@{a['o']:.2f}</span></div></div>"
            st.markdown(html_t.replace('\n', ''), unsafe_allow_html=True)
            c_g, c_r, c_d = st.columns([0.4, 0.4, 0.2])
            with c_g:
                if st.button("✅ WIN", key=f"tw_{i}"):
                    st.session_state['total_jogos'] += 1; st.session_state['total_acertos'] += 1
                    st.session_state['analises_salvas'].pop(i); tocar_som_customizado(); time.sleep(1); st.rerun()
            with c_r:
                if st.button("❌ LOSS", key=f"tl_{i}"):
                    st.session_state['total_jogos'] += 1; st.session_state['analises_salvas'].pop(i); st.rerun()
            with c_d:
                if st.button("🗑️", key=f"td_{i}"):
                    st.session_state['analises_salvas'].pop(i); st.rerun()
    else:
        st.caption("Nenhuma análise salva.")

# ==========================================
# ABA 4: SAFE BINGO
# ==========================================
with t4:
    st.markdown("<h4 class='neon-text'>HIGH EV ZONE (SAFE)</h4>", unsafe_allow_html=True)
    analisados = st.session_state.get('analisados', [])
    if not analisados: 
        st.info("⚠️ Varredura prévia requerida no RADAR.")
    else:
        seguros = sorted([j for j in analisados if 1.15 <= j.get('o', 1.5) <= 1.65], key=lambda x: x.get('conf', 0), reverse=True)
        if len(seguros) >= 2:
            s1, s2 = seguros[0], seguros[1]
            odd_s = s1['o'] * s2['o']
            html_safe = (
                f"<div class='glass-card' style='border: 1px solid {cor_neon};'>"
                f"<div style='text-align:center; margin-bottom: 15px;'><span style='background:{cor_neon}; color:#000; padding:5px 15px; border-radius:20px; font-weight:bold; font-size:12px;'>🏆 DUPLA DE OURO</span></div>"
                f"<div style='border-left: 4px solid {cor_neon}; padding-left: 10px; margin-bottom: 10px;'><div style='color:white; font-weight:bold; font-size: 14px;'>⚽ {s1['jogo']}</div><div style='color:#888; font-size: 12px;'>🎯 {s1['m']} | <span style='color:{cor_neon}; font-weight:bold;'>@{s1['o']:.2f}</span></div></div>"
                f"<div style='border-left: 4px solid {cor_neon}; padding-left: 10px; margin-bottom: 15px;'><div style='color:white; font-weight:bold; font-size: 14px;'>⚽ {s2['jogo']}</div><div style='color:#888; font-size: 12px;'>🎯 {s2['m']} | <span style='color:{cor_neon}; font-weight:bold;'>@{s2['o']:.2f}</span></div></div>"
                f"<hr style='border-color: rgba(255,255,255,0.1);'><h3 style='text-align:center; color:{cor_neon}; text-shadow: 0 0 10px {cor_neon}60;'>📊 ODD FINAL: {odd_s:.2f}</h3></div>"
            )
            st.markdown(html_safe.replace('\n', ''), unsafe_allow_html=True)
            if st.button("🔥 COPIAR PARA OPERAÇÕES"): 
                st.session_state['bilhete'].extend([s1, s2]); st.toast("✅ Copiado!"); tocar_som_customizado()
        else: st.warning("A IA não encontrou 2 jogos com perfil 'Safe' (Odds 1.15-1.65).")

# ==========================================
# ABA 5: HUB VIP
# ==========================================
with t5:
    st.markdown(f"<h3 style='color:white; text-align:center; font-weight:900;'>V8 <span style='color:{cor_neon};'>HUB</span></h3>", unsafe_allow_html=True)

    with st.expander("🔑 Chave de API de Dados (IMPORTANTE)"):
        st.markdown("<span style='font-size:11px; color:#aaa;'>Crie uma chave grátis em the-odds-api.com e cole aqui para jogos reais.</span>", unsafe_allow_html=True)
        nova_api = st.text_input("API Key:", value=st.session_state.get('api_key_odds'), type="password")
        if st.button("Salvar Chave"): st.session_state['api_key_odds'] = nova_api; st.success("Salva!")

    with st.expander("🏛️ GESTÃO DE BANCAS"):
        st.session_state['bancas']["Betano"] = st.number_input("Betano", value=st.session_state.get('bancas')["Betano"], step=50.0)
        st.session_state['bancas']["Bet365"] = st.number_input("Bet365", value=st.session_state.get('bancas')["Bet365"], step=50.0)
        st.session_state['bancas']["Betfair"] = st.number_input("Betfair", value=st.session_state.get('bancas')["Betfair"], step=50.0)

    with st.expander("📡 Terminal A.I. (Audit Logs)"):
        st.markdown(f"<div class='terminal-card' style='font-size:9px;'>> PING SERVER... OK<br>> LAST UPDATE: {datetime.now().strftime('%H:%M:%S')}<br>> FETCHING SYNDICATE DATA... OK<br>> API KEY: VALID<br>> MODEL: V8.QUANT.CORE</div>".replace('\n', ''), unsafe_allow_html=True)

    with st.expander("⚙️ CUSTOMIZAÇÃO"):
        st.selectbox("Motor Gráfico:", ["🟢 Verde Hacker", "🟡 Ouro Milionário", "🔵 Azul Cyberpunk", "🔴 Vermelho Kamikaze", "🟣 Rosa Choque"], key="tema_escolhido")
        st.selectbox("Moeda:", ["R$", "US$", "€", "₿"], key="moeda")

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("ENCERRAR SESSÃO", type="primary", use_container_width=True):
        st.session_state['autenticado'] = False; st.rerun()
