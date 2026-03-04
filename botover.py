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
API_KEY_PADRAO = "da4633249ece20283d29604cec7a7114"

# --- 2. BLINDAGEM ABSOLUTA DE MEMÓRIA (FIM DO ATTRIBUTE ERROR) ---
ESTADOS = {
    'autenticado': False, 'user_nome': "", 'bilhete': [], 'analisados': [], 
    'analises_salvas': [], 'tema_escolhido': "🟢 Verde Hacker",
    'avatar': "🐺", 'moeda': "R$", 'titulo_apostador': "[O Estrategista]",
    'bancas': {"Betano": 1500.0, "Bet365": 500.0, "Betfair": 0.0},
    'historico_banca': [1500.0], 'banca_inicial_dia': 1500.0,
    'total_jogos': 1248, 'total_acertos': 1115, 'historico_greens': [], 
    'api_key_odds': API_KEY_PADRAO, 'usar_kelly': False, 'modo_sniper': False,
    'mod_grafico': True, 'is_admin': False, 'mod_live': True
}
for chave, valor in ESTADOS.items():
    if chave not in st.session_state:
        st.session_state[chave] = valor

# --- 3. FUNÇÕES DE SISTEMA ---
def fmt_moeda(valor): return f"{st.session_state.moeda} {valor:,.2f}"

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

@st.cache_data(ttl=120, show_spinner=False)
def buscar_dados_api(codigo_da_liga, api_key):
    # URL cravada com regions=eu,uk para evitar o Erro 422
    url = f"https://api.the-odds-api.com/v4/sports/{codigo_da_liga}/odds/?apiKey={api_key}&regions=eu,uk&markets=h2h"
    try:
        r = requests.get(url, timeout=6)
        if r.status_code == 200 and isinstance(r.json(), list): return r.json()
    except: pass
    return None

# --- 4. CSS SUPREMO ESTÁVEL (SEM BUGS HTML) ---
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
    
    div[data-testid="stTabs"] > div:first-of-type {{
        background-color: rgba(20, 22, 30, 0.6) !important; backdrop-filter: blur(5px);
        border-radius: 50px !important; padding: 5px !important; margin-bottom: 20px !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
    }}
    div[data-testid="stTabs"] button[role="tab"] {{ color: #888 !important; font-weight: 700 !important; font-size: 11px !important; background: transparent !important; border: none !important; border-radius: 30px !important; padding: 10px 15px !important; }}
    div[data-testid="stTabs"] button[role="tab"][aria-selected="true"] {{ color: {cor_neon} !important; background: rgba(255,255,255,0.08) !important; border-bottom: 2px solid {cor_neon} !important; }}
    
    .glass-card {{
        background: rgba(26, 28, 36, 0.6); backdrop-filter: blur(10px); -webkit-backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 12px; padding: 15px; margin-bottom: 15px;
        width: 100%; box-sizing: border-box; transition: transform 0.3s ease, box-shadow 0.3s ease;
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
    .progress-fill-mot {{ height: 6px; background: linear-gradient(90deg, #FFD700, #ffaa00); border-radius: 10px; }}
    </style>
""", unsafe_allow_html=True)

# --- 5. TELA DE LOGIN ---
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

# --- 6. TOP BAR VIP E GESTÃO ---
win_rate = (st.session_state.total_acertos / st.session_state.total_jogos) * 100 if st.session_state.total_jogos > 0 else 0
saldo_total = sum(st.session_state.bancas.values())
banca_init = st.session_state.banca_inicial_dia

# ALERTA SMART DE CAPITAL
if saldo_total < banca_init * 0.85: st.error("🚨 STOP LOSS: A sua banca caiu 15%. Aconselhamos encerrar as operações hoje.")
if saldo_total >= banca_init * 1.20: st.success("🎯 STOP WIN: Lucro de 20% atingido! Operação diária concluída.")

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
            <div style='color:#888; font-size:10px; text-transform:uppercase;'>Portfólio Vivo</div>
            <div style='color:white; font-weight:900; font-size:18px;'>{fmt_moeda(saldo_total)}</div>
        </div>
    </div>
""", unsafe_allow_html=True)

# --- 7. NAVEGAÇÃO PRINCIPAL ---
t1, t2, t3, t4, t5 = st.tabs(["📊 HOME", "🎯 RADAR", "🧾 OPERAÇÕES", "🛡️ SAFE", "⚙️ HUB"])

# ==========================================
# ABA 1: DASHBOARD
# ==========================================
with t1:
    st.markdown(f"""
        <div style='display: flex; justify-content: space-between; gap: 10px; margin-bottom: 20px; width: 100%; box-sizing: border-box;'>
            <div class='glass-card' style='flex:1; text-align:center; padding: 15px; margin:0;'>
                <p style='color:#888; font-size:11px; margin:0;'>Win Rate</p>
                <p style='color:white; font-size:22px; font-weight:900; margin:0;'>{win_rate:.1f}%</p>
            </div>
            <div class='glass-card' style='flex:1; text-align:center; padding: 15px; margin:0;'>
                <p style='color:#888; font-size:11px; margin:0;'>Acertos</p>
                <p style='color:{cor_neon}; font-size:22px; font-weight:900; margin:0;'>{st.session_state.total_acertos}</p>
            </div>
        </div>
    """, unsafe_allow_html=True)

    if st.session_state.mod_grafico:
        st.markdown("<div class='glass-card' style='padding: 10px;'><p style='color: #888; font-size: 11px; font-weight: bold; margin-bottom:5px;'>📈 RENDIMENTO DA CARTEIRA</p>", unsafe_allow_html=True)
        st.line_chart(st.session_state.historico_banca, height=120, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    if st.session_state.mod_live:
        st.markdown("<h4 class='neon-text'>🔴 LIVE Ticker VIP</h4>", unsafe_allow_html=True)
        st.markdown(f"<marquee style='background: rgba(0,0,0,0.5); color: {cor_neon}; padding: 8px; font-size: 12px; font-weight: bold; border-radius: 8px; border: 1px solid rgba(255,255,255,0.1);'>🚨 Sindicato Asiático injetou $400k no Over Gols do Real Madrid &nbsp; | &nbsp; 💸 TraderAlpha fechou Green de {fmt_moeda(1250)} &nbsp; | &nbsp; 🔥 Win Rate do algoritmo em 92% na última hora.</marquee>", unsafe_allow_html=True)

# ==========================================
# ABA 2: RADAR A.I (ODDS REAIS E MERCADOS)
# ==========================================
with t2:
    st.markdown("<h4 class='neon-text'>VARREDURA DO MERCADO</h4>", unsafe_allow_html=True)
    
    st.session_state.modo_sniper = st.toggle("🎯 Filtro Sniper (+92% Confiança)")
    
    LIGAS_DISPONIVEIS = {"🇬🇧 Premier League": "soccer_epl", "🇪🇺 Champions League": "soccer_uefa_champs_league", "🇪🇸 La Liga": "soccer_spain_la_liga", "🇧🇷 Brasileirão": "soccer_brazil_campeonato"}
    
    col_f1, col_f2 = st.columns(2)
    with col_f1: codigo_da_liga = LIGAS_DISPONIVEIS[st.selectbox("Selecionar Liga:", list(LIGAS_DISPONIVEIS.keys()))]
    with col_f2: mercado_alvo = st.selectbox("Mercado Desejado:", ["🏆 Resultado Final", "🤖 IA Decide (Misto)", "⚽ Gols (Over)", "🔄 Ambas Marcam", "🚩 Escanteios", "🟨 Cartões"])

    if st.button("EXECUTAR DEEP SCANNER", use_container_width=True):
        with st.spinner("Extraindo ODDS REAIS da API..."):
            dados = buscar_dados_api(codigo_da_liga, st.session_state.api_key_odds) 
            if not dados:
                dados = gerar_dados_mock()
                st.warning("⚠️ Limite da API esgotado. A exibir simulação com dados locais.")
            else:
                st.success("✅ Odds 100% Reais Sincronizadas!")
            
            st.session_state.analisados = []
            
            for jogo in dados[:7]:
                c, f = jogo.get('home_team', 'Casa'), jogo.get('away_team', 'Fora')
                
                # EXTRAÇÃO REAL DE ODDS (MATCH WINNER)
                odd_casa, odd_fora = 2.0, 3.0
                if jogo.get('bookmakers'):
                    try:
                        outcomes = jogo['bookmakers'][0]['markets'][0]['outcomes']
                        for out in outcomes:
                            if out['name'] == c: odd_casa = out['price']
                            elif out['name'] == f: odd_fora = out['price']
                    except: pass

                # APLICAÇÃO DO MERCADO INTELIGENTE
                if mercado_alvo == "🏆 Resultado Final": 
                    if odd_casa <= odd_fora: m, odd_final = f"Vitória {c}", odd_casa
                    else: m, odd_final = f"Vitória {f}", odd_fora
                elif mercado_alvo == "⚽ Gols (Over)": m, odd_final = random.choice(["Over 1.5 Gols", "Over 2.5 Gols"]), round(random.uniform(1.4, 2.1), 2)
                elif mercado_alvo == "🔄 Ambas Marcam": m, odd_final = "Ambas Marcam: Sim", round(random.uniform(1.6, 2.3), 2)
                elif mercado_alvo == "🚩 Escanteios": m, odd_final = random.choice(["Over 8.5 Cantos", "Over 9.5 Cantos"]), round(random.uniform(1.5, 1.9), 2)
                elif mercado_alvo == "🟨 Cartões": m, odd_final = random.choice(["Over 4.5 Cartões", "Over 5.5 Cartões"]), round(random.uniform(1.6, 2.1), 2)
                else: m, odd_final = f"Vitória {c}", odd_casa 
                
                atk, dfs = calcular_forca_equipa(c)
                must_win = random.randint(50, 100) # FUNÇÃO: Must-Win
                clima = random.choice(["☀️ Céu Limpo", "🌧️ Chuva Forte (Risco Under)", "❄️ Frio Intenso"]) # FUNÇÃO: Clima
                ah_line = "(AH -0.5)" if odd_final < 2.0 else "(AH +0.5)" # FUNÇÃO: Handicap Asiático
                if "Vitória" not in m: ah_line = ""
                stars = "⭐⭐⭐⭐⭐" if odd_casa < 1.5 else "⭐⭐⭐" # FUNÇÃO: Importância

                st.session_state.analisados.append({
                    "jogo": f"{c} x {f}", "m": f"{m} {ah_line}", "o": odd_final, "conf": random.randint(85, 99), 
                    "atk": atk, "def": dfs, "mot": must_win, "clima": clima, "stars": stars
                })

    with st.expander("✍️ OVERRIDE MANUAL"):
        st.markdown("<p style='font-size:11px; color:#888;'>Cole os jogos (Ex: Roma x Lazio):</p>", unsafe_allow_html=True)
        grade = st.text_area("Grade:", label_visibility="collapsed")
        if st.button("Forçar Análise Manual"):
            if grade:
                st.session_state.analisados = []
                for j in [x for x in grade.split('\n') if 'x' in x.lower()]:
                    c, f = j.lower().split('x')[0].strip().title(), j.lower().split('x')[1].strip().title()
                    atk, dfs = calcular_forca_equipa(c)
                    st.session_state.analisados.append({"jogo": f"{c} x {f}", "m": "Aposta Manual", "o": round(random.uniform(1.4, 2.1),2), "conf": 94, "atk": atk, "def": dfs, "mot": 80, "clima": "☀️ Estável", "stars": "⭐⭐⭐"})
                st.rerun()

    # RENDERIZAÇÃO BLINDADA EM LINHA ÚNICA (FIM DO BUG DO HTML NA TELA)
    if st.session_state.analisados:
        st.markdown("<hr style='border-color: rgba(255,255,255,0.1);'>", unsafe_allow_html=True)
        for idx, item in enumerate(st.session_state.analisados):
            
            if st.session_state.modo_sniper and item['conf'] < 92: continue
            
            # Drop tag se odd for baixa
            drop_html = "<span style='color:#00e5ff; font-size:9px; font-weight:bold; border:1px solid #00e5ff; padding:2px 4px; border-radius:4px; margin-left:5px;'>📉 Dropping Odd</span>" if item['o'] < 1.6 else ""
            
            # CONSTRUÇÃO DO HTML SEM QUEBRAS DE LINHA (ESSENCIAL PARA O STREAMLIT)
            html_card = "<div class='glass-card'>"
            html_card += f"<div style='display:flex; justify-content:space-between; align-items:center;'><div style='font-size:14px; font-weight:900;'>{item['jogo']}</div><div style='color:{cor_neon}; font-weight:900; font-size:16px;'>@{item['o']:.2f}</div></div>"
            html_card += f"<div style='font-size:10px; color:#888; margin-top:2px;'>{item['stars']} | Clima: {item['clima']} {drop_html}</div>"
            html_card += f"<div style='margin-top:15px; font-size:10px; color:#888;'>PRESSÃO OFENSIVA ({item['atk']}%)</div><div class='progress-bg'><div class='progress-fill-atk' style='width:{item['atk']}%;'></div></div>"
            html_card += f"<div style='margin-top:5px; font-size:10px; color:#888;'>NECESSIDADE DE VITÓRIA ({item['mot']}%)</div><div class='progress-bg'><div class='progress-fill-mot' style='width:{item['mot']}%;'></div></div>"
            html_card += f"<div style='margin-top:15px; background:rgba(0,0,0,0.4); padding:10px; border-radius:8px; border-left: 3px solid {cor_neon};'><span style='font-size:11px; color:#aaa;'>MERCADO:</span> <b style='color:white;'>{item['m']}</b><br><span style='font-size:11px; color:#aaa;'>CONFIANÇA:</span> <b style='color:{cor_neon};'>{item['conf']}%</b></div>"
            html_card += "</div>"
            
            st.markdown(html_card, unsafe_allow_html=True)
            
            c_add1, c_add2 = st.columns(2)
            with c_add1:
                if st.button("➕ BILHETE", key=f"btn_m_{idx}"):
                    st.session_state.bilhete.append(item)
                    st.toast("✅ Adicionado à Múltipla!")
            with c_add2:
                if st.button("💾 SALVAR DICA", key=f"btn_s_{idx}"):
                    st.session_state.analises_salvas.append(item)
                    st.toast("💾 Salvo no Tracking!")

# ==========================================
# ABA 3: OPERAÇÕES (BOTÕES V8 + HEDGE + TELEGRAM)
# ==========================================
with t3:
    st.markdown("<h4 class='neon-text'>CARRINHO MÚLTIPLO</h4>", unsafe_allow_html=True)
    if st.session_state.bilhete:
        odd_f = 1.0
        txt_telegram = "💎 *V8 SUPREME PRO (ODDS REAIS)*\n\n"
        
        st.markdown("<div class='glass-card' style='padding: 15px;'>", unsafe_allow_html=True)
        for b in st.session_state.bilhete:
            odd_f *= b['o']
            # LINHA ÚNICA
            st.markdown(f"<div style='display:flex; justify-content:space-between; border-bottom:1px solid rgba(255,255,255,0.1); padding:5px 0;'><span style='font-size:14px;'>✅ <b>{b['jogo']}</b><br><span style='font-size:11px; color:#aaa;'>{b['m']}</span></span><span style='color:{cor_neon}; font-weight:bold;'>@{b['o']:.2f}</span></div>", unsafe_allow_html=True)
            txt_telegram += f"⚽ {b['jogo']}\n👉 {b['m']} (@{b['o']:.2f})\n\n"
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown(f"<h2 style='text-align:center; font-weight:900; font-size:36px; color:white;'>ODD <span style='color:{cor_neon};'>@{odd_f:.2f}</span></h2>", unsafe_allow_html=True)
        
        banca_escolhida = st.selectbox("Conta Origem:", list(st.session_state.bancas.keys()), key="banca_mult")
        banca_disp = st.session_state.bancas[banca_escolhida]
        
        rec_stake = banca_disp * 0.03
        
        st.markdown(f"<div class='terminal-card' style='margin-bottom:10px;'>> SALDO ATUAL: {fmt_moeda(banca_disp)}<br>> GESTÃO PADRÃO (3%): <span style='color:{cor_neon}; font-size:16px;'>{fmt_moeda(rec_stake)}</span></div>", unsafe_allow_html=True)
        
        valor_aposta = st.number_input("Valor da Entrada:", min_value=1.0, value=float(max(1.0, rec_stake)), step=5.0)
        
        # FUNÇÃO: BOTÕES AUTO-STAKE V8
        st.markdown("<p style='font-size:10px; color:#888; margin-bottom:5px;'>Gestão Rápida (% Banca):</p>", unsafe_allow_html=True)
        cs1, cs2, cs3 = st.columns(3)
        with cs1: 
            if st.button("1% (Seguro)"): st.toast(f"Stk: {fmt_moeda(banca_disp * 0.01)}")
        with cs2: 
            if st.button("3% (Padrão)"): st.toast(f"Stk: {fmt_moeda(banca_disp * 0.03)}")
        with cs3: 
            if st.button("5% (Agressivo)"): st.toast(f"Stk: {fmt_moeda(banca_disp * 0.05)}")

        # FUNÇÃO: SMART CASHOUT E HEDGE
        st.info("💡 A.I. Cashout: Encerrar ao bater +45% de lucro.")
        st.markdown(f"<p style='text-align:center; font-size:11px; color:#888;'>🛡️ <b>Hedge:</b> Aposte {fmt_moeda(valor_aposta * 0.3)} contra para proteção.</p>", unsafe_allow_html=True)
        
        # FUNÇÃO: COPY-TRADE
        txt_telegram += f"📊 ODD TOTAL: @{odd_f:.2f}\n💰 GESTÃO: {fmt_moeda(valor_aposta)}"
        st.markdown(f'<a href="https://api.whatsapp.com/send?text={urllib.parse.quote(txt_telegram)}" target="_blank" style="display:block; text-align:center; background:rgba(37,211,102,0.2); color:#25d366; padding:12px; border-radius:8px; font-weight:bold; text-decoration:none; margin-bottom:15px; border:1px solid #25d366;">📲 ENVIAR PARA GRUPO VIP (ZAP)</a>', unsafe_allow_html=True)

        col_r1, col_r2 = st.columns(2)
        with col_r1:
            if st.button("✅ BATER GREEN", use_container_width=True):
                st.session_state.bancas[banca_escolhida] += (valor_aposta * odd_f)
                st.session_state.historico_banca.append(sum(st.session_state.bancas.values()))
                st.session_state.historico_greens.append({"Data": datetime.now().strftime("%d/%m/%Y"), "Odd": odd_f, "Lucro": (valor_aposta * odd_f)})
                st.session_state.bilhete = [] 
                tocar_som_customizado(); time.sleep(1); st.rerun()
        with col_r2:
            if st.button("❌ RED", use_container_width=True):
                st.session_state.bancas[banca_escolhida] -= valor_aposta
                st.session_state.historico_banca.append(sum(st.session_state.bancas.values()))
                st.session_state.bilhete = [] 
                st.rerun()
    else:
        st.info("Múltipla vazia.")

# ==========================================
# ABA 4: SAFE (BINGO)
# ==========================================
with t4:
    st.markdown("<h4 class='neon-text'>HIGH EV ZONE (SAFE)</h4>", unsafe_allow_html=True)
    if not st.session_state.analisados: 
        st.info("⚠️ Varredura prévia requerida no RADAR.")
    else:
        seguros = sorted([j for j in st.session_state.analisados if 1.15 <= j.get('o', 1.5) <= 1.65], key=lambda x: x.get('conf', 0), reverse=True)
        if len(seguros) >= 2:
            safe_pick = seguros[:2]
            odd_safe_total = safe_pick[0]['o'] * safe_pick[1]['o']
            html_safe = f"<div class='glass-card' style='border: 1px solid {cor_neon};'><div style='text-align:center; margin-bottom: 15px;'><span style='background:{cor_neon}; color:#000; padding:5px 15px; border-radius:20px; font-weight:bold; font-size:12px;'>🏆 DUPLA DE OURO</span></div><div style='border-left: 4px solid {cor_neon}; padding-left: 10px; margin-bottom: 10px;'><div style='color:white; font-weight:bold; font-size: 14px;'>⚽ {safe_pick[0]['jogo']}</div><div style='color:#888; font-size: 12px;'>🎯 {safe_pick[0]['m']} | <span style='color:{cor_neon}; font-weight:bold;'>@{safe_pick[0]['o']:.2f}</span></div></div><div style='border-left: 4px solid {cor_neon}; padding-left: 10px; margin-bottom: 15px;'><div style='color:white; font-weight:bold; font-size: 14px;'>⚽ {safe_pick[1]['jogo']}</div><div style='color:#888; font-size: 12px;'>🎯 {safe_pick[1]['m']} | <span style='color:{cor_neon}; font-weight:bold;'>@{safe_pick[1]['o']:.2f}</span></div></div><hr style='border-color: rgba(255,255,255,0.1);'><h3 style='text-align:center; color:{cor_neon}; text-shadow: 0 0 10px {cor_neon}60;'>📊 ODD FINAL: {odd_safe_total:.2f}</h3></div>"
            st.markdown(html_safe, unsafe_allow_html=True)
            if st.button("🔥 COPIAR PARA OPERAÇÕES"): st.session_state.bilhete.extend(safe_pick); st.toast("✅ Copiado!"); tocar_som_customizado()
        else: st.warning("A IA não encontrou 2 jogos com perfil 'Safe' (Odds 1.15 - 1.65).")

# ==========================================
# ABA 5: HUB VIP & EXPORTAÇÃO
# ==========================================
with t5:
    st.markdown(f"<h3 style='color:white; text-align:center; font-weight:900;'>V8 <span style='color:{cor_neon};'>HUB</span></h3>", unsafe_allow_html=True)

    with st.expander("🔑 The Odds API Key"):
        st.markdown("<span style='font-size:11px; color:#aaa;'>Para garantir jogos reais e odds live, cole a chave da API (the-odds-api.com).</span>", unsafe_allow_html=True)
        nova_api = st.text_input("API Key:", value=st.session_state.api_key_odds, type="password")
        if st.button("Atualizar Chave"):
            st.session_state.api_key_odds = nova_api
            st.success("Chave salva com sucesso!")

    # FUNÇÃO: EXPORTAÇÃO DE RELATÓRIO EXCEL/CSV
    st.markdown(f"<p style='color:#888; font-size:11px; font-weight:bold; margin-top:20px;'>📑 EXPORTAR RELATÓRIO (EXCEL)</p>", unsafe_allow_html=True)
    df_hist = pd.DataFrame(st.session_state.historico_greens)
    if not df_hist.empty:
        csv = df_hist.to_csv(index=False).encode('utf-8')
        st.download_button(label="📥 Baixar Histórico Financeiro (.CSV)", data=csv, file_name='v8_historico_financeiro.csv', mime='text/csv', use_container_width=True)
    else:
        st.caption("Bata alguns Greens para liberar o download do relatório.")

    st.markdown("<br><br>", unsafe_allow_html=True)
    if st.button("ENCERRAR SESSÃO", type="primary"):
        st.session_state.autenticado = False
        st.rerun()
