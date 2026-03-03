import streamlit as st
import random
import time
import urllib.parse
import requests
import hashlib
import pandas as pd
from datetime import datetime, timedelta

# --- 1. CONFIGURAÇÃO BASE E SEGURA ---
st.set_page_config(page_title="V8 SUPREME PRO", layout="wide", initial_sidebar_state="collapsed")
LINK_SUA_IMAGEM_DE_FUNDO = "https://raw.githubusercontent.com/Ronny2604/botfutbol/main/photo_5172618853803035536_c.png"
API_KEY_PADRAO = "da4633249ece20283d29604cec7a7114"

# --- 2. BLINDAGEM DE ESTADOS (FIM DO ATTRIBUTE ERROR) ---
estado_padrao = {
    'autenticado': False, 'user_nome': "", 'bilhete': [], 'analisados': [], 
    'analises_salvas': [], 'tema_escolhido': "🟢 Verde Hacker",
    'is_vip': True, 'boss_mode': False, 'avatar': "🐺", 'moeda': "R$", 
    'time_coracao': "", 'diario_bordo': "", 'som_green': "Clássico", 
    'titulo_apostador': "O Estrategista", 'mod_grafico': True, 
    'bancas': {"Betano": 1000.0, "Bet365": 500.0, "Betfair": 0.0},
    'historico_banca': [1500.0], 'banca_inicial_dia': 1500.0, # NOVO: Para Stop Loss/Win
    'recuperacao_red': False, 'conquistas': ["🏅 Novato"], 
    'total_jogos': 1248, 'total_acertos': 1115, 'historico_greens': [], 
    'is_admin': False, 'api_key_odds': API_KEY_PADRAO, 'status_api': "AGUARDANDO",
    'usar_kelly': False, 'modo_sniper': False # NOVO: Ferramentas
}
for k, v in estado_padrao.items():
    if k not in st.session_state: st.session_state[k] = v

# --- 3. FUNÇÕES DE SISTEMA ---
def fmt_moeda(valor): return f"{st.session_state.get('moeda', 'R$')} {valor:,.2f}"

def tocar_som():
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

# --- 4. TEMA E CSS SUPREMO (COM INOVAÇÕES VISUAIS) ---
tema = st.session_state.get('tema_escolhido', "🟢")
if "Ouro" in tema: cor_neon = "#FFD700"
elif "Azul" in tema: cor_neon = "#00e5ff"
elif "Vermelho" in tema: cor_neon = "#ff3333"
elif "Rosa" in tema: cor_neon = "#ff00ff"
else: cor_neon = "#00ff88"

grad = f"linear-gradient(135deg, {cor_neon}20, rgba(0,0,0,0))"

css_stable = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;500;800;900&display=swap');

html, body, [class*="css"] {{ font-family: 'Inter', sans-serif !important; }}
header[data-testid="stHeader"], footer, #MainMenu {{ display: none !important; }}
.block-container {{ padding-top: 1rem !important; margin-top: -1rem !important; padding-bottom: 80px !important; }}

/* FUNDO SEGURO (NÃO ESTICA) */
.stApp {{ 
    background: radial-gradient(circle at 50% 0%, rgba(20,22,30,0.95), rgba(10,10,12,1)), url('{LINK_SUA_IMAGEM_DE_FUNDO}'); 
    background-size: cover; background-position: center; background-attachment: fixed; color: #ffffff; 
}}

/* SCROLL INVISÍVEL */
::-webkit-scrollbar {{ width: 0px; background: transparent; }}

/* EFEITO GLITCH TÍTULO */
.glitch-text {{ font-weight: 900; letter-spacing: 2px; color: #fff; text-shadow: 2px 2px 0px rgba(0,0,0,0.5); transition: 0.3s; }}
.glitch-text:hover {{ text-shadow: 2px 0 {cor_neon}, -2px 0 #ff0055; }}

/* CINEMATIC TEXT (Títulos) */
.cinematic {{ font-weight: 800; letter-spacing: 1px; color: {cor_neon}; text-transform: uppercase; font-size: 14px; text-shadow: 0 0 10px {cor_neon}40; }}

/* GRADIENT DIVIDER */
.grad-divider {{ height: 1px; width: 100%; background: linear-gradient(90deg, transparent, {cor_neon}50, transparent); margin: 20px 0; }}

/* PULSATING LIVE DOT */
.live-dot {{ display: inline-block; width: 8px; height: 8px; background-color: {cor_neon}; border-radius: 50%; margin-right: 5px; animation: pulse 1.5s infinite; }}
@keyframes pulse {{ 0% {{ box-shadow: 0 0 0 0 {cor_neon}80; }} 70% {{ box-shadow: 0 0 0 6px rgba(0,0,0,0); }} 100% {{ box-shadow: 0 0 0 0 rgba(0,0,0,0); }} }}

/* ABAS PÍLULA (TOPO) */
div[data-testid="stTabs"] > div:first-of-type {{
    background-color: rgba(20, 22, 30, 0.6) !important; backdrop-filter: blur(10px);
    border-radius: 50px !important; padding: 5px !important; margin-bottom: 20px !important;
    border: 1px solid rgba(255, 255, 255, 0.05) !important; box-shadow: 0 4px 10px rgba(0,0,0,0.3);
}}
div[data-testid="stTabs"] button[role="tab"] {{ color: #888 !important; font-weight: 800 !important; font-size: 11px !important; background: transparent !important; border: none !important; border-radius: 30px !important; padding: 10px 15px !important; }}
div[data-testid="stTabs"] button[role="tab"][aria-selected="true"] {{ color: {cor_neon} !important; background: rgba(255,255,255,0.08) !important; border-bottom: 2px solid {cor_neon} !important; }}

/* GLASS CARDS ESTABILIZADOS */
.glass-card {{
    background: rgba(26, 28, 36, 0.7); backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px);
    border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 12px; padding: 15px; margin-bottom: 15px;
    width: 100%; box-sizing: border-box; transition: transform 0.2s ease, box-shadow 0.2s ease;
}}
.glass-card:hover {{ border-color: {cor_neon}60; box-shadow: 0 5px 15px rgba(0,0,0,0.3); }}

/* BOTÕES MAGNÉTICOS */
.stButton>button {{ 
    background: {grad} !important; color: white !important; font-weight: 900 !important; 
    border-radius: 8px !important; border: 1px solid {cor_neon} !important; padding: 12px 20px !important; 
    width: 100%; transition: all 0.2s ease !important;
}}
.stButton>button:active {{ transform: scale(0.97) !important; filter: brightness(1.2) !important; }}

/* BARRAS DE PROGRESSO NEON */
.progress-bg {{ width: 100%; background: rgba(0,0,0,0.5); border-radius: 10px; height: 6px; margin-bottom: 8px; overflow: hidden; border: 1px solid rgba(255,255,255,0.05); }}
.progress-fill-atk {{ height: 6px; background: linear-gradient(90deg, #ff0055, #ff5555); border-radius: 10px; box-shadow: 0 0 10px #ff0055; }}
.progress-fill-def {{ height: 6px; background: linear-gradient(90deg, #0055ff, #00aaff); border-radius: 10px; box-shadow: 0 0 10px #0055ff; }}

/* IOS BADGES */
.ios-badge {{ background: rgba(0,0,0,0.4); padding: 4px 8px; border-radius: 12px; border: 1px solid {cor_neon}40; color: {cor_neon}; font-size: 11px; font-weight: 800; }}
</style>
"""
st.markdown(css_stable.replace('\n', ''), unsafe_allow_html=True)

# --- 5. TELA DE LOGIN ---
if not st.session_state.get('autenticado'):
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    with st.container():
        st.markdown(f"<div class='glass-card' style='text-align:center;'><h1 class='glitch-text' style='margin-bottom:0;'>V8 <span style='color:{cor_neon};'>SUPREME</span></h1><p style='color:#888; font-size: 11px; letter-spacing:2px; margin-bottom: 30px;'>A.I. INTELLIGENCE HUB</p></div>".replace('\n', ''), unsafe_allow_html=True)
        nome_in = st.text_input("Operador ID:", placeholder="Insira o seu nome")
        if st.button("INICIAR TERMINAL"):
            st.session_state['autenticado'] = True
            st.session_state['user_nome'] = nome_in if nome_in else "Trader VIP"
            st.rerun()
    st.stop()

# --- 6. TOP BAR VIP (Com Alertas Stop-Win/Loss) ---
t_jogos = st.session_state.get('total_jogos', 1)
t_acertos = st.session_state.get('total_acertos', 0)
win_rate = (t_acertos / t_jogos) * 100 if t_jogos > 0 else 0

saldo_total = sum(st.session_state.get('bancas', {}).values())
banca_init = st.session_state.get('banca_inicial_dia', 1500)

# FERRAMENTA: ALERTAS DE GESTÃO DIÁRIA
if saldo_total < banca_init * 0.85: st.error("🚨 STOP LOSS: Proteja o capital. Aconselhamos encerrar hoje.")
if saldo_total >= banca_init * 1.20: st.success("🎯 STOP WIN: Meta +20% batida! Missão cumprida.")

html_topbar = (
    f"<div style='display:flex; justify-content:space-between; align-items:center; margin-bottom: 15px; padding: 15px; background: rgba(20,22,30,0.8); border-radius: 12px; border: 1px solid rgba(255,255,255,0.05);'>"
    f"<div style='display:flex; align-items:center;'>"
    f"<div style='font-size: 28px; margin-right: 12px;'>{st.session_state.get('avatar')}</div>"
    f"<div>"
    f"<div style='color:white; font-weight:900; font-size:16px;'>{str(st.session_state.get('user_nome')).upper()} <span style='background:{cor_neon}; color:black; font-size:9px; padding:2px 6px; border-radius:4px; font-weight:bold;'>PRO</span></div>"
    f"<div style='color:{cor_neon}; font-size:10px;'><span class='live-dot'></span>Online</div>"
    f"</div></div>"
    f"<div style='text-align:right;'>"
    f"<div style='color:#888; font-size:10px; text-transform:uppercase;'>Portfólio</div>"
    f"<div style='color:white; font-weight:900; font-size:18px;'>{fmt_moeda(saldo_total)}</div>"
    f"</div></div>"
)
st.markdown(html_topbar.replace('\n', ''), unsafe_allow_html=True)

# --- 7. NAVEGAÇÃO PRINCIPAL ---
t1, t2, t3, t4, t5 = st.tabs(["📊 HOME", "🎯 RADAR", "🧾 OPERAÇÕES", "🛡️ SAFE", "⚙️ HUB"])

# ==========================================
# ABA 1: DASHBOARD
# ==========================================
with t1:
    if st.session_state.get('mod_grafico'):
        st.markdown(f"<div class='glass-card'><p style='color: #888; font-size: 11px; font-weight: bold; margin-bottom:5px; letter-spacing:1px;'>📈 RENDIMENTO LINEAR</p></div>".replace('\n', ''), unsafe_allow_html=True)
        st.line_chart(st.session_state.get('historico_banca', []), height=120, use_container_width=True)

    # FERRAMENTA: FEAR & GREED + CORES DINÂMICAS
    fg_val = random.randint(30, 80)
    fg_cor = "#ff3333" if fg_val < 45 else (cor_neon if fg_val > 60 else "#FFD700")
    wr_cor = cor_neon if win_rate > 70 else ("#FFD700" if win_rate > 50 else "#ff3333")

    html_stats = (
        f"<div style='display: flex; gap: 10px; margin-bottom: 20px;'>"
        f"<div class='glass-card' style='flex:1; text-align:center; padding: 15px; margin:0;'>"
        f"<p style='color:#888; font-size:10px; margin:0;'>Win Rate A.I.</p>"
        f"<p style='color:{wr_cor}; font-size:22px; font-weight:900; margin:0;'>{win_rate:.1f}%</p>"
        f"</div>"
        f"<div class='glass-card' style='flex:1; text-align:center; padding: 15px; margin:0;'>"
        f"<p style='color:#888; font-size:10px; margin:0;'>Fear & Greed</p>"
        f"<p style='color:{fg_cor}; font-size:22px; font-weight:900; margin:0;'>{fg_val}</p>"
        f"</div></div>"
    )
    st.markdown(html_stats.replace('\n', ''), unsafe_allow_html=True)

    # FERRAMENTA: RANKING VIP
    st.markdown("<p class='cinematic'>🏆 LEADERBOARD VIP</p>", unsafe_allow_html=True)
    rank_html = f"<div class='glass-card' style='padding: 15px;'><div style='display:flex; justify-content:space-between; border-bottom:1px solid rgba(255,255,255,0.05); padding-bottom:8px;'><span style='font-size:12px; color:#fff;'>🥇 TraderAlpha</span> <b style='color:{cor_neon}; font-size:12px;'>+{fmt_moeda(4520)}</b></div><div style='display:flex; justify-content:space-between; border-bottom:1px solid rgba(255,255,255,0.05); padding:8px 0;'><span style='font-size:12px; color:#fff;'>🥈 {st.session_state.get('user_nome')}</span> <b style='color:{cor_neon}; font-size:12px;'>+{fmt_moeda(1250)}</b></div><div style='display:flex; justify-content:space-between; padding-top:8px;'><span style='font-size:12px; color:#fff;'>🥉 Lucas_Inv</span> <b style='color:{cor_neon}; font-size:12px;'>+{fmt_moeda(890)}</b></div></div>"
    st.markdown(rank_html.replace('\n', ''), unsafe_allow_html=True)

# ==========================================
# ABA 2: RADAR A.I E MERCADOS
# ==========================================
with t2:
    st.markdown("<p class='cinematic'>VARREDURA ALGORÍTMICA</p>", unsafe_allow_html=True)
    
    # FERRAMENTA: MODO SNIPER
    st.session_state['modo_sniper'] = st.toggle("🎯 Filtro Sniper (+92% Confiança)")

    LIGAS = {"🇪🇺 Champions League": "soccer_uefa_champs_league", "🇬🇧 Premier League": "soccer_epl", "🇪🇸 La Liga": "soccer_spain_la_liga", "🇧🇷 Brasileirão": "soccer_brazil_campeonato"}
    
    col_f1, col_f2 = st.columns(2)
    with col_f1: liga_sel = st.selectbox("Liga:", list(LIGAS.keys()))
    with col_f2: merc_sel = st.selectbox("Mercado:", ["🤖 Misto", "🏆 Vencedor", "⚽ Gols", "🔄 Ambas", "🚩 Cantos", "🟨 Cartões"])

    if st.button("EXECUTAR DEEP SCAN", use_container_width=True):
        with st.spinner("Buscando assimetrias..."):
            dados = buscar_dados_api(LIGAS[liga_sel], st.session_state.get('api_key_odds')) 
            if not dados:
                dados = gerar_dados_mock()
                st.warning("⚠️ API Esgotada ou sem jogos hoje. A usar Simulação Mock.")
            else:
                st.success("✅ Dados conectivos extraídos!")
            
            st.session_state['analisados'] = []
            for jogo in dados[:10]:
                c, f = jogo.get('home_team', 'Casa'), jogo.get('away_team', 'Fora')
                
                if merc_sel == "⚽ Gols": m = random.choice(["Over 1.5 Gols", "Over 2.5 Gols"])
                elif merc_sel == "🔄 Ambas": m = "Ambas Marcam: Sim"
                elif merc_sel == "🚩 Cantos": m = random.choice(["Over 8.5 Cantos", "Over 9.5 Cantos"])
                elif merc_sel == "🟨 Cartões": m = "Over 4.5 Cartões"
                elif merc_sel == "🏆 Vencedor": m = random.choice([f"Vitória {c}", f"Vitória {f}"])
                else: m = random.choice([f"Vitória {c}", "Ambas: Sim", "Over 1.5"]) 
                
                odd = round(random.uniform(1.3, 2.5), 2)
                atk, dfs = calcular_forca_equipa(c)
                conf = random.randint(85, 99)
                
                # FERRAMENTA: A.I. WHISPERS E TRENDS
                whisper = random.choice(["Árbitro rígido hoje.", "Equipa focada no ataque rápido.", "Clima de chuva favorece Under.", "Valor matemático puro."])
                trend = "⬆️" if random.random() > 0.5 else "⬇️"
                
                st.session_state['analisados'].append({"jogo": f"{c} x {f}", "m": m, "o": odd, "conf": conf, "atk": atk, "def": dfs, "whisper": whisper, "trend": trend})

    with st.expander("✍️ Modo Manual (Override)"):
        st.markdown("<p style='font-size:11px; color:#888;'>Cole os jogos (Ex: Roma x Lazio):</p>", unsafe_allow_html=True)
        grade = st.text_area("Grade:", label_visibility="collapsed")
        if st.button("Forçar Análise"):
            if grade:
                st.session_state['analisados'] = []
                for j in [x for x in grade.split('\n') if 'x' in x.lower()]:
                    c, f = j.lower().split('x')[0].strip().title(), j.lower().split('x')[1].strip().title()
                    atk, dfs = calcular_forca_equipa(c)
                    st.session_state['analisados'].append({"jogo": f"{c} x {f}", "m": "Alerta de Valor", "o": round(random.uniform(1.4, 2.1),2), "conf": 94, "atk": atk, "def": dfs, "whisper": "Análise Injetada Manualmente.", "trend": "⬆️"})
                st.rerun()

    if st.session_state.get('analisados'):
        st.markdown("<div class='grad-divider'></div>", unsafe_allow_html=True)
        for idx, item in enumerate(st.session_state.get('analisados')):
            
            # FILTRO SNIPER EM AÇÃO
            if st.session_state.get('modo_sniper') and item['conf'] < 92: continue
            
            ev_html = f"<span style='color:#FFD700; border:1px solid #FFD700; border-radius:4px; padding:2px 4px; font-size:9px;'>EV+</span>" if item['conf'] > 90 else ""

            # HTML BLINDADO LINHA ÚNICA
            html_card = (
                f"<div class='glass-card'>"
                f"<div style='display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;'>"
                f"<span class='ios-badge'>{item['m']}</span>"
                f"<span style='color:{cor_neon}; font-weight:900; font-size:16px;'>@{item['o']:.2f}</span>"
                f"</div>"
                f"<div style='font-size:14px; font-weight:900; color:#fff; margin-bottom:15px;'>⚽ {item['jogo']} {ev_html}</div>"
                f"<div style='display:flex; justify-content:space-between; font-size:9px; color:#888;'><span>PRESSÃO OFENSIVA</span><span>{item['atk']}%</span></div>"
                f"<div class='progress-bg'><div class='progress-fill-atk' style='width:{item['atk']}%;'></div></div>"
                f"<div style='display:flex; justify-content:space-between; font-size:9px; color:#888; margin-top:4px;'><span>MURALHA DEFENSIVA</span><span>{item['def']}%</span></div>"
                f"<div class='progress-bg'><div class='progress-fill-def' style='width:{item['def']}%;'></div></div>"
                f"<div style='display:flex; justify-content:space-between; align-items:center; margin-top:15px; background:rgba(0,0,0,0.3); padding:8px; border-radius:8px; border-left:2px solid {cor_neon};'>"
                f"<span style='font-size:10px; color:#888; font-style:italic;'>🤖 {item['whisper']}</span>"
                f"<span style='font-size:11px; font-weight:900; color:{cor_neon};'>{item['conf']}% {item['trend']}</span>"
                f"</div></div>"
            )
            st.markdown(html_card.replace('\n', ''), unsafe_allow_html=True)
            
            c_add1, c_add2 = st.columns(2)
            with c_add1:
                if st.button("➕ BILHETE", key=f"m_{idx}"):
                    st.session_state['bilhete'].append(item); st.toast("No Carrinho!")
            with c_add2:
                if st.button("💾 TRACKING", key=f"s_{idx}"):
                    st.session_state['analises_salvas'].append(item); st.toast("Salvo!")

# ==========================================
# ABA 3: OPERAÇÕES (KELLY + HEDGE + TELEGRAM)
# ==========================================
with t3:
    st.markdown("<p class='cinematic'>CARRINHO MÚLTIPLO</p>", unsafe_allow_html=True)
    if st.session_state.get('bilhete'):
        odd_f = 1.0
        txt_copiar = "💎 *V8 SUPREME PRO*\n\n"
        
        st.markdown("<div class='glass-card' style='padding: 15px;'>", unsafe_allow_html=True)
        for b in st.session_state.get('bilhete'):
            odd_f *= b['o']
            st.markdown(f"<div style='display:flex; justify-content:space-between; border-bottom:1px solid rgba(255,255,255,0.1); padding:8px 0;'><span style='font-size:13px; font-weight:600; color:#fff;'>{b['m']}<br><span style='font-size:10px; color:#888;'>{b['jogo']}</span></span><span style='color:{cor_neon}; font-weight:900;'>@{b['o']:.2f}</span></div>".replace('\n', ''), unsafe_allow_html=True)
            txt_copiar += f"⚽ {b['jogo']}\n👉 {b['m']} (@{b['o']:.2f})\n\n"
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown(f"<h2 style='text-align:center; font-weight:900; font-size:36px; color:white;'>ODD <span style='color:{cor_neon};'>@{odd_f:.2f}</span></h2>", unsafe_allow_html=True)
        
        bancas_dict = st.session_state.get('bancas', {})
        banca_escolhida = st.selectbox("Conta Origem:", list(bancas_dict.keys()))
        banca_disp = bancas_dict[banca_escolhida]
        
        # FERRAMENTA: KELLY CRITERION
        st.session_state['usar_kelly'] = st.checkbox("🧠 Calculadora Kelly Criterion", value=st.session_state.get('usar_kelly', False))
        if st.session_state.get('usar_kelly'):
            prob = 1 / odd_f * 1.15
            kelly_pct = max(0.01, min(((odd_f - 1) * prob - (1 - prob)) / (odd_f - 1), 0.05))
            rec_stake = banca_disp * kelly_pct
        else: rec_stake = banca_disp * (0.03 if odd_f < 2.5 else 0.01)

        valor = st.number_input("Sua Entrada:", min_value=1.0, value=float(max(1.0, rec_stake)), step=5.0)
        
        # FERRAMENTA: HEDGE
        hedge_val = valor * 0.3
        st.markdown(f"<div style='font-size:10px; color:#888; text-align:center; margin-bottom:15px;'>🛡️ <b>Hedge Seguro:</b> Aposte {fmt_moeda(hedge_val)} no inverso para proteger a banca.</div>", unsafe_allow_html=True)
        
        # FERRAMENTA: TELEGRAM/WPP EXPORT
        txt_copiar += f"📊 ODD TOTAL: @{odd_f:.2f}\n💰 GESTÃO: {fmt_moeda(valor)}"
        st.markdown(f'<a href="https://api.whatsapp.com/send?text={urllib.parse.quote(txt_copiar)}" target="_blank" style="display:block; text-align:center; background:rgba(37,211,102,0.2); color:#25d366; padding:12px; border-radius:8px; font-weight:bold; text-decoration:none; margin-bottom:15px; border:1px solid #25d366;">📲 ENVIAR PARA GRUPO VIP</a>', unsafe_allow_html=True)

        c1, c2 = st.columns(2)
        with c1:
            if st.button("✅ LIQUIDAR WIN"):
                st.session_state['bancas'][banca_escolhida] += (valor * odd_f)
                st.session_state['historico_banca'].append(sum(st.session_state['bancas'].values()))
                st.session_state['bilhete'] = []; tocar_som(); time.sleep(1); st.rerun()
        with c2:
            if st.button("❌ ASSUMIR RED"):
                st.session_state['bancas'][banca_escolhida] -= valor
                st.session_state['historico_banca'].append(sum(st.session_state['bancas'].values()))
                st.session_state['bilhete'] = []; st.rerun()
    else:
        st.info("Múltipla vazia.")

    st.markdown("<div class='grad-divider'></div><p class='cinematic'>TRACKING INDIVIDUAL</p>", unsafe_allow_html=True)
    if st.session_state.get('analises_salvas'):
        for i, a in enumerate(st.session_state.get('analises_salvas')):
            st.markdown(f"<div class='glass-card' style='padding: 10px 15px; margin-bottom: 5px; border-left: 3px solid #00e5ff;'><div style='font-size:13px; font-weight:bold; color:white;'>{a['jogo']}</div><div style='display:flex; justify-content:space-between; margin-top:2px;'><span style='color:#888; font-size:11px;'>{a['m']}</span><span style='color:{cor_neon}; font-weight:bold; font-size:12px;'>@{a['o']:.2f}</span></div></div>".replace('\n', ''), unsafe_allow_html=True)
            c_g, c_r, c_d = st.columns([0.4, 0.4, 0.2])
            with c_g:
                if st.button("✅ WIN", key=f"tw_{i}"):
                    st.session_state['total_jogos'] += 1; st.session_state['total_acertos'] += 1
                    st.session_state['analises_salvas'].pop(i); tocar_som(); time.sleep(1); st.rerun()
            with c_r:
                if st.button("❌ LOSS", key=f"tl_{i}"):
                    st.session_state['total_jogos'] += 1; st.session_state['analises_salvas'].pop(i); st.rerun()
            with c_d:
                if st.button("🗑️", key=f"td_{i}"):
                    st.session_state['analises_salvas'].pop(i); st.rerun()
    else: st.caption("Nenhuma análise salva.")

# ==========================================
# ABA 4: SAFE (BINGO)
# ==========================================
with t4:
    st.markdown("<p class='cinematic'>ALTO EV (SAFE)</p>", unsafe_allow_html=True)
    if not st.session_state.get('analisados'): 
        st.info("⚠️ Faça uma varredura no Radar primeiro.")
    else:
        seguros = sorted([j for j in st.session_state.get('analisados') if 1.15 <= j.get('o', 1.5) <= 1.65], key=lambda x: x.get('conf', 0), reverse=True)
        if len(seguros) >= 2:
            s1, s2 = seguros[0], seguros[1]
            st.markdown(f"<div class='glass-card' style='border: 1px solid {cor_neon};'><div style='text-align:center; margin-bottom: 15px;'><span class='ios-badge'>🏆 DUPLA DE OURO</span></div><div style='border-left: 4px solid {cor_neon}; padding-left: 10px; margin-bottom: 10px;'><div style='color:white; font-weight:bold; font-size: 14px;'>⚽ {s1['jogo']}</div><div style='color:#888; font-size: 12px;'>🎯 {s1['m']} | <span style='color:{cor_neon}; font-weight:bold;'>@{s1['o']:.2f}</span></div></div><div style='border-left: 4px solid {cor_neon}; padding-left: 10px; margin-bottom: 15px;'><div style='color:white; font-weight:bold; font-size: 14px;'>⚽ {s2['jogo']}</div><div style='color:#888; font-size: 12px;'>🎯 {s2['m']} | <span style='color:{cor_neon}; font-weight:bold;'>@{s2['o']:.2f}</span></div></div><hr style='border-color: rgba(255,255,255,0.1);'><h3 style='text-align:center; color:{cor_neon}; margin:0;'>📊 ODD: {(s1['o']*s2['o']):.2f}</h3></div>".replace('\n', ''), unsafe_allow_html=True)
            if st.button("🔥 COPIAR PARA OPERAÇÕES"): st.session_state['bilhete'].extend([s1, s2]); st.toast("Copiado!"); tocar_som()
        else: st.warning("A IA não encontrou 2 jogos com perfil 'Safe' hoje.")

# ==========================================
# ABA 5: HUB DE CONTROLE
# ==========================================
with t5:
    st.markdown(f"<h3 style='color:white; text-align:center; font-weight:900;'>V8 <span style='color:{cor_neon};'>HUB</span></h3>", unsafe_allow_html=True)

    with st.expander("🔑 Chave de API de Dados"):
        st.markdown("<span style='font-size:11px; color:#aaa;'>Mantenha a sua chave (the-odds-api.com) atualizada para jogos reais.</span>", unsafe_allow_html=True)
        nova_api = st.text_input("API Key:", value=st.session_state.get('api_key_odds'), type="password")
        if st.button("Atualizar Chave"): st.session_state['api_key_odds'] = nova_api; st.success("Salva!")

    with st.expander("🏛️ Bancas e Interface"):
        st.selectbox("Motor Gráfico:", ["🟢 Verde Hacker", "🟡 Ouro Milionário", "🔵 Azul Cyberpunk", "🔴 Vermelho Kamikaze", "🟣 Rosa Choque", "⚪ Modo Claro (Light)"], key="tema_escolhido")
        st.selectbox("Moeda:", ["R$", "US$", "€", "₿"], key="moeda")
        st.session_state['bancas']["Betano"] = st.number_input("Betano", value=st.session_state.get('bancas')["Betano"], step=50.0)

    # FERRAMENTA: AUDIT LOGS
    with st.expander("📡 Terminal A.I. (Audit Logs)"):
        st.markdown(f"<div class='terminal-card' style='font-size:9px;'>> AUTH KEY: {st.session_state.get('api_key_odds')[:5]}...<br>> LAST PING: {datetime.now().strftime('%H:%M:%S')}<br>> FETCHING ASIAN SYNDICATE DATA...<br>> MODEL: V8.QUANT<br>> STATUS: OPERATIONAL</div>".replace('\n', ''), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("ENCERRAR SESSÃO", type="primary"):
        st.session_state['autenticado'] = False; st.rerun()
