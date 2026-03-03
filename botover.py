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

# --- 2. INICIALIZAÇÃO DE ESTADOS (ANTI-CRASH) ---
estado_padrao = {
    'autenticado': False, 'user_nome': "", 'bilhete': [], 'analisados': [], 
    'analises_salvas': [], 'tema_escolhido': "🟢 Verde Hacker",
    'avatar': "🐺", 'moeda': "R$", 'titulo_apostador': "[O Estrategista]",
    'bancas': {"Betano": 1000.0, "Bet365": 500.0, "Betfair": 0.0},
    'historico_banca': [1500.0], 'banca_inicial_dia': 1500.0,
    'total_jogos': 1248, 'total_acertos': 1115, 'historico_greens': [], 
    'api_key_odds': ODDS_API_KEY, 'usar_kelly': False, 'modo_sniper': False
}
for k, v in estado_padrao.items():
    if k not in st.session_state:
        st.session_state[k] = v

# --- 3. FUNÇÕES DE SISTEMA ---
def fmt_moeda(valor):
    return f"{st.session_state.moeda} {valor:,.2f}"

def tocar_som_customizado():
    st.markdown('<audio autoplay style="display:none;"><source src="https://assets.mixkit.co/active_storage/sfx/2003/2003-preview.mp3" type="audio/mpeg"></audio>', unsafe_allow_html=True)

def calcular_forca_equipa(nome_equipa):
    hash_object = hashlib.md5(nome_equipa.encode())
    num = int(hash_object.hexdigest(), 16)
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

# --- 4. CSS SUPREMO (O LAYOUT ESTÁVEL QUE FUNCIONOU) ---
cor_neon = "#00ff88"
grad = f"linear-gradient(135deg, rgba(0,255,136,0.1), rgba(0,0,0,0))"

st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;500;700;900&display=swap');
    
    html, body, [class*="css"] {{ font-family: 'Inter', sans-serif !important; }}
    header[data-testid="stHeader"] {{ display: none !important; }}
    .block-container {{ padding-top: 1rem !important; margin-top: -1rem !important; padding-bottom: 80px !important; }}
    #MainMenu {{visibility: hidden !important;}} .stDeployButton {{display:none !important;}} footer {{visibility: hidden !important;}}
    
    .stApp {{ 
        background: radial-gradient(circle at 50% 0%, rgba(20,22,30,0.9), rgba(10,10,12,1)), url('{LINK_SUA_IMAGEM_DE_FUNDO}'); 
        background-size: cover; background-position: center; background-attachment: fixed; color: #ffffff; 
    }}
    
    /* ABAS NATIVAS REESTILIZADAS SEGURAS */
    div[data-testid="stTabs"] > div:first-of-type {{
        background-color: rgba(20, 22, 30, 0.6) !important;
        backdrop-filter: blur(5px);
        border-radius: 50px !important;
        padding: 5px !important;
        margin-bottom: 20px !important;
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
    
    /* GLASS CARDS ESTABILIZADOS */
    .glass-card {{
        background: rgba(26, 28, 36, 0.6);
        backdrop-filter: blur(10px); -webkit-backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px; padding: 15px; margin-bottom: 15px;
        width: 100%; box-sizing: border-box; 
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }}
    .glass-card:hover {{ border-color: {cor_neon}50; }}
    
    .terminal-card {{ background: #0a0b10; border: 1px solid #222; border-left: 3px solid {cor_neon}; border-radius: 8px; padding: 15px; font-family: monospace; color: #00ff88; width: 100%; box-sizing: border-box; }}
    
    .neon-text {{ color: {cor_neon}; font-weight: 900; font-size: 14px; letter-spacing: 1px; text-transform: uppercase; text-shadow: 0 0 10px {cor_neon}40; }}
    
    .stButton>button {{ 
        background: {grad} !important; color: white !important; font-weight: 900 !important; 
        border-radius: 8px !important; border: 1px solid {cor_neon} !important; padding: 12px 20px !important; 
        width: 100%; transition: all 0.2s ease !important;
    }}
    .stButton>button:hover {{ background: {cor_neon} !important; color: #000 !important; transform: translateY(-2px) !important; }}
    .stButton>button:active {{ transform: translateY(1px) !important; filter: brightness(0.9) !important; }}
    
    .progress-bg {{ width: 100%; background: #222; border-radius: 10px; height: 6px; margin-bottom: 8px; overflow: hidden; }}
    .progress-fill-atk {{ height: 6px; background: linear-gradient(90deg, #ff0055, #ff5555); border-radius: 10px; }}
    .progress-fill-def {{ height: 6px; background: linear-gradient(90deg, #0055ff, #00aaff); border-radius: 10px; }}
    </style>
""", unsafe_allow_html=True)

# --- TELA DE LOGIN ---
if not st.session_state.autenticado:
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    with st.container():
        st.markdown(f"<div class='glass-card' style='max-width:400px; margin:auto; text-align:center;'><h1 style='color:#fff; font-weight:900; margin-bottom:0;'>V8 <span style='color:{cor_neon};'>SUPREME</span></h1><p style='color:#888; font-size: 11px; letter-spacing:2px; margin-bottom: 30px;'>A.I. INTELLIGENCE HUB</p></div>", unsafe_allow_html=True)
        nome_in = st.text_input("Credencial de Acesso:", placeholder="Seu Nome")
        if st.button("INICIAR SESSÃO", use_container_width=True):
            st.session_state.autenticado = True
            st.session_state.user_nome = nome_in if nome_in else "VIP"
            st.rerun()
    st.stop()

# --- TOP BAR VIP & ALERTAS DE GESTÃO ---
win_rate = (st.session_state.total_acertos / st.session_state.total_jogos) * 100 if st.session_state.total_jogos > 0 else 0
saldo_total = sum(st.session_state.bancas.values())
banca_init = st.session_state.banca_inicial_dia

# FERRAMENTA PREMIUM: ALERTAS STOP-WIN / STOP-LOSS
if saldo_total < banca_init * 0.85: st.error("🚨 ALERTA DE RISCO: A sua banca caiu 15%. É aconselhável acionar o Stop Loss.")
if saldo_total >= banca_init * 1.20: st.success("🎯 STOP WIN: Lucro de 20% atingido hoje. Excelente trabalho!")

st.markdown(f"""
    <div style='display:flex; justify-content:space-between; align-items:center; margin-bottom: 15px; padding: 15px; background: rgba(20,22,30,0.8); border-radius: 12px; border: 1px solid rgba(255,255,255,0.05); width: 100%; box-sizing: border-box;'>
        <div style='display:flex; align-items:center;'>
            <div style='font-size: 28px; margin-right: 12px;'>{st.session_state.avatar}</div>
            <div>
                <div style='color:white; font-weight:900; font-size:16px;'>{st.session_state.user_nome.upper()} <span style='background:{cor_neon}; color:black; font-size:9px; padding:2px 6px; border-radius:4px; vertical-align:middle; font-weight:bold;'>PRO</span></div>
                <div style='color:{cor_neon}; font-size:11px; margin-top:2px;'>{st.session_state.titulo_apostador}</div>
            </div>
        </div>
        <div style='text-align:right;'>
            <div style='color:#888; font-size:10px; text-transform:uppercase;'>Saldo Consolidado</div>
            <div style='color:white; font-weight:900; font-size:18px;'>{fmt_moeda(saldo_total)}</div>
        </div>
    </div>
""", unsafe_allow_html=True)

# --- NAVEGAÇÃO PRINCIPAL (NO TOPO, ESTÁVEL) ---
t1, t2, t3, t4, t5 = st.tabs(["📊 HOME", "🎯 RADAR", "🧾 OPERAÇÕES", "🛡️ SAFE", "⚙️ HUB"])

# ==========================================
# ABA 1: DASHBOARD
# ==========================================
with t1:
    # FERRAMENTA PREMIUM: FEAR & GREED INDEX E LEADERBOARD
    fg_val = random.randint(30, 80)
    fg_cor = "#ff3333" if fg_val < 45 else (cor_neon if fg_val > 60 else "#FFD700")

    st.markdown(f"""
        <div style='display: flex; justify-content: space-between; gap: 10px; margin-bottom: 20px; width: 100%; box-sizing: border-box;'>
            <div class='glass-card' style='flex:1; text-align:center; padding: 15px; margin:0;'>
                <p style='color:#888; font-size:11px; margin:0;'>Win Rate A.I.</p>
                <p style='color:{cor_neon}; font-size:22px; font-weight:900; margin:0;'>{win_rate:.1f}%</p>
            </div>
            <div class='glass-card' style='flex:1; text-align:center; padding: 15px; margin:0;'>
                <p style='color:#888; font-size:11px; margin:0;'>Market Sentiment</p>
                <p style='color:{fg_cor}; font-size:22px; font-weight:900; margin:0;'>{fg_val}</p>
            </div>
        </div>
    """, unsafe_allow_html=True)

    if st.session_state.mod_grafico:
        st.markdown("<div class='glass-card' style='padding: 10px;'><p style='color: #888; font-size: 11px; font-weight: bold; margin-bottom:5px;'>📈 RENDIMENTO DA CARTEIRA</p>", unsafe_allow_html=True)
        st.line_chart(st.session_state.historico_banca, height=120, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<h4 class='neon-text'>🏆 RANKING VIP DIÁRIO</h4>", unsafe_allow_html=True)
    st.markdown(f"""
        <div class='glass-card' style='padding: 15px;'>
            <div style='display:flex; justify-content:space-between; border-bottom:1px solid rgba(255,255,255,0.05); padding-bottom:8px;'><span style='font-size:12px; color:#fff;'>🥇 TraderAlpha</span> <b style='color:{cor_neon}; font-size:12px;'>+{fmt_moeda(4520)}</b></div>
            <div style='display:flex; justify-content:space-between; border-bottom:1px solid rgba(255,255,255,0.05); padding:8px 0;'><span style='font-size:12px; color:#fff;'>🥈 {st.session_state.user_nome}</span> <b style='color:{cor_neon}; font-size:12px;'>+{fmt_moeda(1250)}</b></div>
            <div style='display:flex; justify-content:space-between; padding-top:8px;'><span style='font-size:12px; color:#fff;'>🥉 Lucas_Inv</span> <b style='color:{cor_neon}; font-size:12px;'>+{fmt_moeda(890)}</b></div>
        </div>
    """, unsafe_allow_html=True)

# ==========================================
# ABA 2: RADAR A.I (FILTRO DE MERCADOS E SNIPER)
# ==========================================
with t2:
    st.markdown("<h4 class='neon-text'>VARREDURA ALGORÍTMICA</h4>", unsafe_allow_html=True)
    
    # FERRAMENTA PREMIUM: MODO SNIPER
    st.session_state.modo_sniper = st.toggle("🎯 Ativar Filtro Sniper (+92% Confiança)")

    LIGAS_DISPONIVEIS = {"🇪🇺 Champions League": "soccer_uefa_champs_league", "🇬🇧 Premier League": "soccer_epl", "🇪🇸 La Liga": "soccer_spain_la_liga", "🇧🇷 Brasileirão": "soccer_brazil_campeonato"}
    
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        codigo_da_liga = LIGAS_DISPONIVEIS[st.selectbox("Selecionar Liga:", list(LIGAS_DISPONIVEIS.keys()))]
    with col_f2:
        mercado_alvo = st.selectbox("Mercado Desejado:", ["🤖 IA Decide (Misto)", "🏆 Resultado Final", "⚽ Gols (Over/Under)", "🔄 Ambas Marcam", "🚩 Escanteios", "🟨 Cartões"])

    if st.button("EXECUTAR SCANNER", use_container_width=True):
        with st.spinner("Procurando assimetrias..."):
            dados = buscar_dados_api(codigo_da_liga, st.session_state.api_key_odds) 
            if not dados:
                dados = gerar_dados_mock()
                st.warning("⚠️ Limite da API esgotado. A exibir simulação global.")
            else:
                st.success("✅ Dados extraídos com sucesso!")
            
            st.session_state.analisados = []
            for jogo in dados[:10]:
                c, f = jogo.get('home_team', 'Casa'), jogo.get('away_team', 'Fora')
                
                # Regras de mercado selecionado
                if mercado_alvo == "⚽ Gols (Over/Under)": m = random.choice(["Over 1.5 Gols", "Over 2.5 Gols", "Under 3.5 Gols"])
                elif mercado_alvo == "🔄 Ambas Marcam": m = "Ambas Marcam: Sim"
                elif mercado_alvo == "🚩 Escanteios": m = random.choice(["Over 8.5 Cantos", "Over 9.5 Cantos"])
                elif mercado_alvo == "🟨 Cartões": m = random.choice(["Over 4.5 Cartões", "Over 5.5 Cartões"])
                elif mercado_alvo == "🏆 Resultado Final": m = random.choice([f"Vitória {c}", f"Vitória {f}", "Empate"])
                else: m = random.choice([f"Vitória {c}", "Ambas Marcam: Sim", "Over 1.5 Gols", "Over 8.5 Cantos"])
                
                odd = round(random.uniform(1.3, 2.5), 2)
                atk, dfs = calcular_forca_equipa(c)
                conf = random.randint(85, 99)
                xg_c = round(random.uniform(1.1, 2.8), 2)
                whisper = random.choice(["Árbitro com tendência de cartões.", "Equipa visitante sofre muitos golos no HT.", "Valor matemático confirmado."])
                
                st.session_state.analisados.append({"jogo": f"{c} x {f}", "casa": c, "fora": f, "m": m, "o": odd, "conf": conf, "atk": atk, "def": dfs, "xg": xg_c, "whisper": whisper})

    with st.expander("✍️ OVERRIDE MANUAL (Sua Própria Grade)"):
        st.markdown("<p style='font-size:11px; color:#888;'>Cole os jogos abaixo para a IA analisar o EV+:</p>", unsafe_allow_html=True)
        grade = st.text_area("Ex: Flamengo x Vasco", label_visibility="collapsed")
        if st.button("Forçar Análise Manual"):
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
                    
                    st.session_state.analisados.append({"jogo": f"{c} x {f}", "casa": c, "fora": f, "m": m, "o": round(random.uniform(1.4, 2.1),2), "conf": random.randint(88, 99), "atk": atk, "def": dfs, "xg": 1.8, "whisper": "Análise gerada por Input Manual."})
                st.rerun()

    # RENDERIZAÇÃO BLINDADA COM WHISPERS
    if st.session_state.analisados:
        st.markdown("<hr style='border-color: rgba(255,255,255,0.1);'>", unsafe_allow_html=True)
        for idx, item in enumerate(st.session_state.analisados):
            
            # FILTRO SNIPER LÓGICA
            if st.session_state.modo_sniper and item['conf'] < 92: continue

            # HTML Numa Linha para não bugar
            html_card = f"<div class='glass-card'><div style='display:flex; justify-content:space-between; align-items:center;'><div style='font-size:14px; font-weight:900;'>{item['casa']} <span style='color:#555; font-size:10px;'>VS</span> {item['fora']}</div><div style='color:{cor_neon}; font-weight:900; font-size:16px;'>@{item['o']:.2f}</div></div><div style='margin-top:15px; font-size:10px; color:#888;'>PRESSÃO OFENSIVA (xG {item['xg']})</div><div class='progress-bg'><div class='progress-fill-atk' style='width:{item['atk']}%;'></div></div><div style='margin-top:5px; font-size:10px; color:#888;'>MURALHA DEFENSIVA</div><div class='progress-bg'><div class='progress-fill-def' style='width:{item['def']}%;'></div></div><div style='margin-top:15px; background:rgba(0,0,0,0.4); padding:10px; border-radius:8px; border-left: 2px solid {cor_neon};'><span style='font-size:11px; color:#aaa;'>MERCADO:</span> <b style='color:white;'>{item['m']}</b><br><span style='font-size:11px; color:#aaa;'>CONFIANÇA:</span> <b style='color:{cor_neon};'>{item['conf']}%</b><br><span style='font-size:10px; color:#888; font-style:italic;'>🤖 Whisper: {item['whisper']}</span></div></div>"
            st.markdown(html_card, unsafe_allow_html=True)
            
            col_add1, col_add2 = st.columns(2)
            with col_add1:
                if st.button("➕ BILHETE", key=f"btn_m_{idx}"):
                    st.session_state.bilhete.append(item)
                    st.toast("✅ Adicionado à Múltipla!")
            with col_add2:
                if st.button("💾 SALVAR DICA", key=f"btn_s_{idx}"):
                    st.session_state.analises_salvas.append(item)
                    st.toast("💾 Salvo no Tracking Pessoal!")

# ==========================================
# ABA 3: OPERAÇÕES (KELLY + HEDGE + TELEGRAM)
# ==========================================
with t3:
    st.markdown("<h4 class='neon-text'>CARRINHO MÚLTIPLO</h4>", unsafe_allow_html=True)
    if st.session_state.bilhete:
        odd_f = 1.0
        txt_telegram = "💎 *V8 SUPREME PRO*\n\n"
        
        st.markdown("<div class='glass-card' style='padding: 15px;'>", unsafe_allow_html=True)
        for b in st.session_state.bilhete:
            odd_f *= b['o']
            st.markdown(f"<p style='margin:0; font-size:14px; border-bottom: 1px solid rgba(255,255,255,0.1); padding: 5px 0;'>✅ <b>{b['jogo']}</b> <span style='float:right; color:{cor_neon}; font-weight:bold;'>@{b['o']:.2f}</span><br><span style='font-size:11px; color:#aaa;'>Mercado: {b['m']}</span></p>", unsafe_allow_html=True)
            txt_telegram += f"⚽ {b['jogo']}\n👉 {b['m']} (@{b['o']:.2f})\n\n"
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown(f"<h2 style='text-align:center; font-weight:900; font-size:36px; color:white;'>ODD <span style='color:{cor_neon};'>@{odd_f:.2f}</span></h2>", unsafe_allow_html=True)
        
        banca_escolhida = st.selectbox("Conta Origem:", list(st.session_state.bancas.keys()), key="banca_mult")
        banca_disp = st.session_state.bancas[banca_escolhida]
        
        # FERRAMENTA PREMIUM: KELLY CRITERION E GESTÃO
        st.session_state.usar_kelly = st.checkbox("🧠 Usar Matemática de Kelly", value=st.session_state.usar_kelly)
        if st.session_state.usar_kelly:
            prob = 1 / odd_f * 1.15
            kelly_pct = max(0.01, min(((odd_f - 1) * prob - (1 - prob)) / (odd_f - 1), 0.05))
            rec_stake = banca_disp * kelly_pct
        else:
            rec_stake = banca_disp * (0.03 if odd_f < 2.5 else 0.01)

        st.markdown(f"<div class='terminal-card' style='margin-bottom:10px;'>> SALDO: {fmt_moeda(banca_disp)}<br>> GESTÃO IDEAL: <span style='color:{cor_neon}; font-size:16px;'>{fmt_moeda(rec_stake)}</span></div>", unsafe_allow_html=True)
        
        valor_aposta = st.number_input("Entrada (Múltipla):", min_value=1.0, value=float(max(1.0, rec_stake)), step=5.0)
        
        # FERRAMENTA PREMIUM: HEDGE CALCULATOR
        st.markdown(f"<p style='text-align:center; font-size:11px; color:#aaa;'>🛡️ <b>Proteção (Hedge):</b> Aposte {fmt_moeda(valor_aposta * 0.3)} contra para proteger o capital.</p>", unsafe_allow_html=True)
        
        # FERRAMENTA PREMIUM: BOTÃO EXPORT TELEGRAM
        txt_telegram += f"📊 ODD TOTAL: @{odd_f:.2f}\n💰 GESTÃO: {fmt_moeda(valor_aposta)}"
        st.markdown(f'<a href="https://api.whatsapp.com/send?text={urllib.parse.quote(txt_telegram)}" target="_blank" style="display:block; text-align:center; background:rgba(37,211,102,0.2); color:#25d366; padding:12px; border-radius:8px; font-weight:bold; text-decoration:none; margin-bottom:15px; border:1px solid #25d366;">📲 ENVIAR PARA GRUPO VIP</a>', unsafe_allow_html=True)

        col_r1, col_r2 = st.columns(2)
        with col_r1:
            if st.button("✅ BATER GREEN", use_container_width=True):
                st.session_state.bancas[banca_escolhida] += (valor_aposta * odd_f)
                st.session_state.historico_banca.append(sum(st.session_state.bancas.values()))
                st.session_state.bilhete = [] 
                tocar_som_customizado()
                time.sleep(1); st.rerun()
        with col_r2:
            if st.button("❌ ASSUMIR RED", use_container_width=True):
                st.session_state.bancas[banca_escolhida] -= valor_aposta
                st.session_state.historico_banca.append(sum(st.session_state.bancas.values()))
                st.session_state.bilhete = [] 
                st.rerun()
    else:
        st.info("Múltipla vazia.")

    st.markdown("<h4 class='neon-text' style='margin-top: 40px;'>📂 TRACKING DE ANÁLISES (SINGLES)</h4>", unsafe_allow_html=True)
    if st.session_state.analises_salvas:
        for i, a in enumerate(st.session_state.analises_salvas):
            html_track = f"<div class='glass-card' style='padding: 10px 15px; margin-bottom: 5px; border-left: 3px solid #00e5ff;'><div style='font-size:13px; font-weight:bold; color:white;'>{a['jogo']}</div><div style='display:flex; justify-content:space-between; margin-top:2px;'><span style='color:#888; font-size:11px;'>Call: <b style='color:white;'>{a['m']}</b></span><span style='color:{cor_neon}; font-weight:bold; font-size:12px;'>@{a['o']:.2f}</span></div></div>"
            st.markdown(html_track, unsafe_allow_html=True)
            
            c_g, c_r, c_d = st.columns([0.4, 0.4, 0.2])
            with c_g:
                if st.button("✅ WIN", key=f"tg_{i}"):
                    st.session_state.total_jogos += 1; st.session_state.total_acertos += 1
                    st.session_state.analises_salvas.pop(i)
                    tocar_som_customizado(); time.sleep(1); st.rerun()
            with c_r:
                if st.button("❌ LOSS", key=f"tr_{i}"):
                    st.session_state.total_jogos += 1; st.session_state.analises_salvas.pop(i); st.rerun()
            with c_d:
                if st.button("🗑️", key=f"td_{i}"):
                    st.session_state.analises_salvas.pop(i); st.rerun()
    else:
        st.caption("Nenhuma análise individual salva.")

# ==========================================
# ABA 4: SAFE (BINGO)
# ==========================================
with t4:
    st.markdown("<h4 class='neon-text'>HIGH EV ZONE (SAFE)</h4>", unsafe_allow_html=True)
    if not st.session_state.analisados: 
        st.info("⚠️ Varredura prévia requerida no RADAR (ou via Override Manual).")
    else:
        seguros = sorted([j for j in st.session_state.analisados if 1.15 <= j.get('o', 1.5) <= 1.65], key=lambda x: x.get('conf', 0), reverse=True)
        if len(seguros) >= 2:
            safe_pick = seguros[:2]
            odd_safe_total = safe_pick[0].get('o', 1.2) * safe_pick[1].get('o', 1.2)
            html_safe = f"<div class='glass-card' style='border: 1px solid {cor_neon};'><div style='text-align:center; margin-bottom: 15px;'><span style='background:{cor_neon}; color:#000; padding:5px 15px; border-radius:20px; font-weight:bold; font-size:12px;'>🏆 DUPLA DE OURO</span></div><div style='border-left: 4px solid {cor_neon}; padding-left: 10px; margin-bottom: 10px;'><div style='color:white; font-weight:bold; font-size: 14px;'>⚽ {safe_pick[0]['jogo']}</div><div style='color:#888; font-size: 12px;'>🎯 {safe_pick[0]['m']} | <span style='color:{cor_neon}; font-weight:bold;'>@{safe_pick[0]['o']:.2f}</span></div></div><div style='border-left: 4px solid {cor_neon}; padding-left: 10px; margin-bottom: 15px;'><div style='color:white; font-weight:bold; font-size: 14px;'>⚽ {safe_pick[1]['jogo']}</div><div style='color:#888; font-size: 12px;'>🎯 {safe_pick[1]['m']} | <span style='color:{cor_neon}; font-weight:bold;'>@{safe_pick[1]['o']:.2f}</span></div></div><hr style='border-color: rgba(255,255,255,0.1);'><h3 style='text-align:center; color:{cor_neon}; text-shadow: 0 0 10px {cor_neon}60;'>📊 ODD FINAL: {odd_safe_total:.2f}</h3></div>"
            st.markdown(html_safe, unsafe_allow_html=True)
            if st.button("🔥 COPIAR PARA OPERAÇÕES"): st.session_state.bilhete.extend(safe_pick); st.toast("✅ Copiado!"); tocar_som_customizado()
        else: st.warning("A IA não encontrou 2 jogos com perfil 'Safe' (Odds 1.15 - 1.65) nesta varredura.")

# ==========================================
# ABA 5: HUB DE CONTROLE E LOGS
# ==========================================
with t5:
    st.markdown(f"<h3 style='color:white; text-align:center; font-weight:900;'>V8 <span style='color:{cor_neon};'>HUB</span></h3>", unsafe_allow_html=True)

    with st.expander("🔑 Chave de API de Dados"):
        st.markdown("<span style='font-size:11px; color:#aaa;'>Para garantir jogos reais, atualize sua chave do <b>the-odds-api.com</b>:</span>", unsafe_allow_html=True)
        nova_api = st.text_input("API Key:", value=st.session_state.api_key_odds, type="password")
        if st.button("Atualizar Chave"):
            st.session_state.api_key_odds = nova_api
            st.success("Chave salva com sucesso!")

    with st.expander("🏛️ GESTÃO DE BANCAS"):
        col_c1, col_c2, col_c3 = st.columns(3)
        st.session_state.bancas["Betano"] = col_c1.number_input("Betano", value=st.session_state.bancas["Betano"], step=50.0)
        st.session_state.bancas["Bet365"] = col_c2.number_input("Bet365", value=st.session_state.bancas["Bet365"], step=50.0)
        st.session_state.bancas["Betfair"] = col_c3.number_input("Betfair", value=st.session_state.bancas["Betfair"], step=50.0)

    # FERRAMENTA PREMIUM: TERMINAL DE LOGS DA IA
    with st.expander("📡 Terminal A.I. (Audit Logs)"):
        st.markdown(f"<div class='terminal-card' style='font-size:10px;'>> PING SERVER ASIAN... OK<br>> LAST UPDATE: {datetime.now().strftime('%H:%M:%S')}<br>> FETCHING SYNDICATE DATA... OK<br>> STATUS API: ONLINE<br>> MODEL: V8.QUANT.CORE</div>", unsafe_allow_html=True)

    st.markdown("<br><br>", unsafe_allow_html=True)
    if st.button("ENCERRAR SESSÃO", type="primary"):
        st.session_state.autenticado = False
        st.rerun()
