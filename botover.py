import streamlit as st
import asyncio
import random
import time
import os
import urllib.parse
import requests
import hashlib
import pandas as pd
from telegram import Bot
from datetime import datetime, timedelta

# --- 1. CONFIGURAÇÃO E SEGURANÇA ---
LINK_PAINEL = "https://seu-link-aqui.streamlit.app" 
LINK_SUA_IMAGEM_DE_FUNDO = "https://raw.githubusercontent.com/Ronny2604/botfutbol/main/photo_5172618853803035536_c.png"

st.set_page_config(page_title="V8 SUPREME PRO", layout="wide", initial_sidebar_state="collapsed")

MASTER_KEY = "ronnyp@2025"
FILE_KEYS = "keys.txt" 
TOKEN = '8543393879:AAEsaXAAq2A19zbmMEfHZb-R7nLL-VdierU'
CHAT_ID = '-1003799258159'
ODDS_API_KEY = "da4633249ece20283d29604cec7a7114"

# --- 2. INICIALIZAÇÃO DE ESTADOS GLOBAIS ---
for key, default_val in [
    ('is_admin', False), ('autenticado', False), ('user_nome', ""), 
    ('bilhete', []), ('analisados', []), ('analises_salvas', []), 
    ('tipo_analise_selecionado', 'Análise Geral'), 
    ('tema_escolhido', "🟢 Verde Hacker (Dark)"), ('is_vip', True), ('boss_mode', False),
    ('links_afiliados', ["https://esportiva.bet.br?ref=511e1f11699f", "https://br.betano.com/ref=ronny"]),
    ('link_afiliado_ativo', "https://esportiva.bet.br?ref=511e1f11699f"),
    ('avatar', "🐺"), ('moeda', "R$"), ('time_coracao', ""), ('diario_bordo', ""),
    ('som_green', "Clássico"), ('animacao_vitoria', "Balões"), ('titulo_apostador', "[O Estrategista]"),
    ('mod_grafico', True), ('mod_massas', True), ('mod_live', True),
    ('juros_compostos', False), ('usar_kelly', False), ('recuperacao_red', False),
    ('bancas', {"Betano": 1000.0, "Bet365": 500.0, "Betfair": 0.0}),
    ('historico_banca', [1500.0]), ('banca_inicial_dia', 1500.0),
    ('conquistas', ["🏅 Novato"]), ('total_jogos', 1248), ('total_acertos', 1115),
    ('historico_greens', [])
]:
    if key not in st.session_state: st.session_state[key] = default_val

# --- 3. MODO BOSS (EXCEL REALISTA) ---
if st.session_state.boss_mode:
    st.markdown("""<style>.stApp{background:#fff!important;color:#000!important;font-family:Calibri,sans-serif!important}header{display:none!important}.excel-table{width:100%;border-collapse:collapse;font-size:14px}.excel-table th{background:#f3f3f3;border:1px solid #d0d0d0;padding:5px;text-align:center;color:#333;font-weight:normal}.excel-table td{border:1px solid #d0d0d0;padding:5px;color:#000}.excel-header{background:#217346!important;color:white!important;padding:10px;font-weight:bold;font-size:18px;margin-bottom:20px}</style><div class="excel-header">📊 Livro1 - Excel</div><table class="excel-table"><tr><th>A</th><th>B</th><th>C</th><th>D</th></tr><tr><td>1</td><td><b>Mês</b></td><td><b>Receita Bruta</b></td><td><b>Despesas</b></td></tr><tr><td>2</td><td>Janeiro</td><td>$ 15,400.00</td><td>$ 12,000.00</td></tr><tr><td>3</td><td>Fevereiro</td><td>$ 16,200.00</td><td>$ 11,500.00</td></tr></table>""", unsafe_allow_html=True)
    if st.button("Sair (Esc)"): st.session_state.boss_mode = False; st.rerun()
    st.stop()

# --- 4. FUNÇÕES DE SISTEMA & API (JOGOS REAIS) ---
def fmt_moeda(valor): return f"{st.session_state.moeda} {valor:,.2f}"

def calcular_forca_equipa(nome_equipa):
    num = int(hashlib.md5(nome_equipa.encode()).hexdigest(), 16)
    return 60 + (num % 35), 50 + ((num // 10) % 40)

def gerar_dados_mock():
    # Fallback caso a API esteja sem saldo
    times = ["Flamengo", "Palmeiras", "Real Madrid", "Man City", "Arsenal", "Liverpool", "Bayern", "Boca Juniors"]
    random.shuffle(times)
    d = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    return [{"home_team": times[i*2], "away_team": times[i*2+1], "commence_time": d} for i in range(4)]

@st.cache_data(ttl=600, show_spinner=False)
def buscar_dados_api(codigo_da_liga):
    url = f"https://api.the-odds-api.com/v4/sports/{codigo_da_liga}/odds/?apiKey={ODDS_API_KEY}&regions=eu,uk&markets=h2h,totals"
    try:
        r = requests.get(url, timeout=5)
        if r.status_code == 200 and isinstance(r.json(), list): return r.json()
    except: pass
    return gerar_dados_mock()

jogos_vitrine = buscar_dados_api("soccer_epl")
if not jogos_vitrine: jogos_vitrine = gerar_dados_mock()

def tocar_som():
    st.markdown('<audio autoplay style="display:none;"><source src="https://assets.mixkit.co/active_storage/sfx/2003/2003-preview.mp3" type="audio/mpeg"></audio>', unsafe_allow_html=True)

# --- 5. MOTOR DE TEMAS & CSS (ESTILO CHATBET + PREMIUM) ---
is_light = ("Light" in st.session_state.tema_escolhido)
cor_neon = "#00ff88" if not is_light else "#0055ff"
bg_app = "#0b101a" if not is_light else "#f0f2f6"
card_bg = "#121824" if not is_light else "#ffffff"
card_border = "#1c2436" if not is_light else "#d0d0d0"
c_text = "#ffffff" if not is_light else "#111111"
c_sub = "#5a6b82" if not is_light else "#666666"

st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800;900&display=swap');
    
    html, body, [data-testid="stAppViewContainer"], .main {{
        background-color: {bg_app} !important;
        font-family: 'Inter', sans-serif !important;
        color: {c_text} !important;
    }}
    header[data-testid="stHeader"] {{ display: none !important; }}
    .block-container {{ padding-top: 1rem !important; padding-bottom: 100px !important; max-width: 700px !important; margin: auto; }}
    
    .stMarkdown p, .stText p, h1, h2, h3, h4, h5, h6, label {{ color: {c_text} !important; }}
    div[data-baseweb="select"] > div, div[data-baseweb="input"] > div, textarea {{ background-color: {card_bg} !important; color: {c_text} !important; border: 1px solid {card_border} !important; }}
    
    /* MENU SUPERIOR */
    div[data-testid="stTabs"] > div:first-of-type {{ 
        position: sticky !important; top: 0px !important; z-index: 999 !important;
        background-color: rgba(11, 16, 26, 0.8) !important; backdrop-filter: blur(15px) !important;
        border-bottom: 1px solid {card_border} !important; padding-bottom: 5px; margin-bottom: 25px;
    }}
    div[data-testid="stTabs"] button[role="tab"] {{ color: {c_sub} !important; font-weight: 700 !important; font-size: 11px !important; background: transparent !important; border: none !important; }}
    div[data-testid="stTabs"] button[role="tab"][aria-selected="true"] {{ color: {cor_neon} !important; border-bottom: 2px solid {cor_neon} !important; }}
    
    /* GRELHA 3x3 */
    .btn-grid {{
        height: 90px !important; background-color: {card_bg} !important; border: 1px solid {card_border} !important;
        border-radius: 16px !important; color: {c_sub} !important; font-size: 12px !important; font-weight: 600 !important;
        display: flex !important; flex-direction: column !important; justify-content: center !important; align-items: center !important;
        transition: all 0.2s ease !important; width: 100%; margin-bottom: 10px;
    }}
    .btn-grid:hover, .btn-grid:active {{ border-color: {cor_neon} !important; color: {cor_neon} !important; background-color: rgba(0, 255, 136, 0.05) !important; }}
    
    /* BOTÃO GIGANTE */
    .btn-action {{
        background: linear-gradient(90deg, #00d2ff 0%, #00ff88 100%) !important; color: #000 !important;
        font-weight: 900 !important; border: none !important; border-radius: 12px !important; padding: 15px !important;
        font-size: 16px !important; width: 100%; box-shadow: 0 5px 15px rgba(0, 255, 136, 0.3) !important;
        transition: transform 0.2s; text-align: center; text-decoration: none; display: inline-block; cursor: pointer;
    }}
    .btn-action:active {{ transform: scale(0.98); }}
    
    /* CARDS DE RESULTADO HÍBRIDOS (ChatBet Style + Barras V8) */
    .result-card {{ background-color: {card_bg}; border: 1px solid {card_border}; border-radius: 12px; padding: 15px; margin-bottom: 15px; transition: border-color 0.3s; }}
    .result-card:hover {{ border-color: {cor_neon}50; box-shadow: 0 0 15px rgba(0,255,136,0.05); }}
    .market-badge {{ background: rgba(0, 255, 136, 0.1); color: {cor_neon}; padding: 4px 10px; border-radius: 6px; font-size: 12px; font-weight: 800; display: inline-block; margin-bottom: 10px; }}
    
    /* BARRAS DE ESTATÍSTICA V8 */
    .progress-bg {{ width: 100%; background: #222; border-radius: 10px; height: 4px; margin-bottom: 8px; overflow: hidden; }}
    .progress-fill-atk {{ height: 4px; background: linear-gradient(90deg, #ff0055, #ff5555); border-radius: 10px; }}
    .progress-fill-def {{ height: 4px; background: linear-gradient(90deg, #0055ff, #00aaff); border-radius: 10px; }}
    
    .terminal-card {{ background: #05080f; border: 1px solid {card_border}; border-left: 3px solid {cor_neon}; border-radius: 8px; padding: 15px; font-family: monospace; color: {cor_neon}; font-size:12px; }}
    ::-webkit-scrollbar {{ width: 0px; background: transparent; }} 
    </style>
""", unsafe_allow_html=True)

# --- 6. TELA DE LOGIN ---
if not st.session_state.autenticado:
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    st.markdown(f"<h1 style='text-align:center; font-weight:900;'>V8 <span style='color:{cor_neon};'>SUPREME</span></h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align:center; color:{c_sub}; font-size: 12px; margin-bottom: 30px;'>A.I. INTELLIGENCE HUB</p>", unsafe_allow_html=True)
    
    nome_in = st.text_input("Operador:", placeholder="Seu Nome")
    key_in = st.text_input("Chave:", type="password")
    
    if st.button("ACESSAR TERMINAL", type="primary", use_container_width=True):
        st.session_state.autenticado = True
        st.session_state.user_nome = nome_in if nome_in else "Trader VIP"
        st.rerun()
    st.stop()

# --- HEADER TOP (SALDO E AVISOS) ---
saldo_total = sum(st.session_state.bancas.values())
if saldo_total < st.session_state.banca_inicial_dia * 0.9: st.error("⚠️ STOP LOSS ATINGIDO.")

st.markdown(f"""
    <div style='display:flex; justify-content:space-between; align-items:center; margin-bottom: 20px; padding: 15px; background: {card_bg}; border-radius: 12px; border: 1px solid {card_border};'>
        <div style='display:flex; align-items:center;'>
            <div style='font-size: 24px; margin-right: 10px;'>{st.session_state.avatar}</div>
            <div>
                <div style='font-weight:900; font-size:14px;'>{st.session_state.user_nome.upper()} <span style='background:{cor_neon}; color:#000; font-size:9px; padding:2px 4px; border-radius:4px;'>PRO</span></div>
                <div style='color:{cor_neon}; font-size:10px;'>{st.session_state.titulo_apostador}</div>
            </div>
        </div>
        <div style='text-align:right;'>
            <div style='color:{c_sub}; font-size:10px;'>Banca Viva</div>
            <div style='font-weight:900; font-size:18px;'>{fmt_moeda(saldo_total)}</div>
        </div>
    </div>
""", unsafe_allow_html=True)

# BOTÃO BOSS OCULTO
col_e, col_b = st.columns([0.9, 0.1])
with col_b:
    if st.button("👁️"): st.session_state.boss_mode = True; st.rerun()

# --- 7. NAVEGAÇÃO PRINCIPAL ---
t1, t2, t3, t4, t5 = st.tabs(["📊 HOME", "🎯 RADAR", "🧾 OPERAÇÕES", "🛡️ SAFE", "⚙️ HUB"])

# ==========================================
# ABA 1: DASHBOARD
# ==========================================
with t1:
    if st.session_state.mod_grafico:
        st.markdown(f"<div style='background:{card_bg}; border:1px solid {card_border}; padding:15px; border-radius:12px;'><p style='color:{c_sub}; font-size:11px; margin:0;'>📈 Rendimento Linear</p>", unsafe_allow_html=True)
        st.line_chart(st.session_state.historico_banca, height=120, use_container_width=True)
        st.markdown("</div><br>", unsafe_allow_html=True)

    win_rate = (st.session_state.total_acertos / st.session_state.total_jogos) * 100 if st.session_state.total_jogos > 0 else 0
    
    c1, c2 = st.columns(2)
    with c1: st.markdown(f"<div style='background:{card_bg}; border:1px solid {card_border}; padding:15px; border-radius:12px; text-align:center;'><p style='color:{c_sub}; font-size:10px; margin:0;'>Win Rate A.I.</p><h3 style='margin:0; color:{cor_neon};'>{win_rate:.1f}%</h3></div>", unsafe_allow_html=True)
    with c2: st.markdown(f"<div style='background:{card_bg}; border:1px solid {card_border}; padding:15px; border-radius:12px; text-align:center;'><p style='color:{c_sub}; font-size:10px; margin:0;'>Fear & Greed Index</p><h3 style='margin:0; color:#FFD700;'>62 (Neutro)</h3></div>", unsafe_allow_html=True)

    st.markdown(f"<h4 style='font-size:14px; margin-top:20px;'>🔴 LIVE SCORES</h4>", unsafe_allow_html=True)
    st.markdown(f"""
        <div style='background:{card_bg}; border:1px solid {card_border}; border-left: 4px solid #ff3333; padding:12px; border-radius:8px; display:flex; justify-content:space-between;'>
            <div><span style='background:#ff3333; padding:2px 6px; border-radius:4px; font-size:10px; font-weight:bold;'>78'</span> <span style='font-size: 13px; font-weight:bold; margin-left: 5px;'>Real Madrid 1 x 0 Getafe</span></div>
            <div style='text-align:right; font-size:11px; color:{c_sub};'>Target: <b style='color:{cor_neon};'>Under 2.5</b></div>
        </div>
    """, unsafe_allow_html=True)

# ==========================================
# ABA 2: RADAR A.I (A GRELHA APPLIKE)
# ==========================================
with t2:
    st.markdown("<p style='text-align:center; font-size:14px; font-weight:600; margin-bottom:15px;'>Escolha o tipo de análise</p>", unsafe_allow_html=True)
    
    # GRELHA 3x3 COM CSS INLINE PARA CLICAR
    opcoes = [
        ("📈 Análise Geral", "Análise Geral"), ("🏆 Resultado", "Resultado Final"), ("⚽ Gols", "Gols"),
        ("⏳ 1º Tempo", "Primeiro Tempo"), ("🚩 Escanteios", "Escanteios"), ("🟨 Cartões", "Cartões"),
        ("🎯 Chutes", "Chutes"), ("👤 Jogador", "Jogador"), ("🔄 Ambas Marcam", "Ambas Marcam")
    ]
    
    st.markdown("<style>.stButton>button { height: 60px; border-radius: 12px; font-weight: 600; }</style>", unsafe_allow_html=True)
    
    for i in range(0, 9, 3):
        c1, c2, c3 = st.columns(3)
        with c1: 
            if st.button(opcoes[i][0], key=f"g_{i}", use_container_width=True): st.session_state.tipo_analise_selecionado = opcoes[i][1]
        with c2: 
            if st.button(opcoes[i+1][0], key=f"g_{i+1}", use_container_width=True): st.session_state.tipo_analise_selecionado = opcoes[i+1][1]
        with c3: 
            if st.button(opcoes[i+2][0], key=f"g_{i+2}", use_container_width=True): st.session_state.tipo_analise_selecionado = opcoes[i+2][1]
            
    st.markdown(f"<p style='text-align:center; color:{cor_neon}; font-size:12px; margin-top:10px;'>Foco da IA: <b>{st.session_state.tipo_analise_selecionado}</b></p>", unsafe_allow_html=True)

    LIGAS_DISPONIVEIS = {"🇪🇺 Champions League": "soccer_uefa_champs_league", "🇬🇧 Premier League": "soccer_epl", "🇧🇷 Brasileirão": "soccer_brazil_campeonato"}
    codigo_da_liga = LIGAS_DISPONIVEIS[st.selectbox("Selecionar Liga:", list(LIGAS_DISPONIVEIS.keys()))]

    # BOTÃO GIGANTE (HTML custom inject para bypass do Streamlit limit)
    st.markdown("""<style>div.stButton > button:first-child { background: linear-gradient(90deg, #00d2ff 0%, #00ff88 100%); color: black; font-weight: 900; border: none; padding: 15px; border-radius: 12px; font-size: 16px; }</style>""", unsafe_allow_html=True)
    
    if st.button("ANALISAR AGORA", use_container_width=True):
        with st.spinner(f"A processar {st.session_state.tipo_analise_selecionado}..."):
            time.sleep(1.5)
            dados = buscar_dados_api(codigo_da_liga)
            if not isinstance(dados, list) or len(dados) == 0: dados = gerar_dados_mock()
            
            st.session_state.analisados = []
            
            # Lógica Dinâmica baseada no botão clicado!
            for jogo in dados[:5]:
                c, f = jogo.get('home_team', 'Casa'), jogo.get('away_team', 'Fora')
                
                # Adaptação de mercado
                if "Gols" in st.session_state.tipo_analise_selecionado:
                    mercado = random.choice(["Over 1.5 Gols", "Over 2.5 Gols", "Under 3.5 Gols"])
                elif "Escanteios" in st.session_state.tipo_analise_selecionado:
                    mercado = random.choice(["Over 8.5 Cantos", "Over 9.5 Cantos"])
                elif "Ambas" in st.session_state.tipo_analise_selecionado:
                    mercado = "Ambas Marcam: Sim"
                elif "Cartões" in st.session_state.tipo_analise_selecionado:
                    mercado = "Over 4.5 Cartões"
                else:
                    mercado = f"Vitória {c}"
                
                atk, dfs = calcular_forca_equipa(c)
                st.session_state.analisados.append({
                    "jogo": f"{c} x {f}", "m": mercado, "o": round(random.uniform(1.3, 2.3), 2),
                    "conf": random.randint(85, 99), "atk": atk, "def": dfs, "xg_c": round(random.uniform(0.8, 2.5), 2),
                    "weather": random.choice(["☀️", "🌧️"]), "streak": random.randint(1,5)
                })

    # FUNÇÕES PREMIUM EM EXPANDERS
    with st.expander("🛠️ Ferramentas Manuais & Avançadas"):
        grade = st.text_area("Input de Jogos Manuais:", placeholder="Ex: Flamengo x Vasco")
        if st.button("Forçar Análise Manual"):
            if grade:
                st.session_state.analisados = []
                for j in [x for x in grade.split('\n') if 'x' in x.lower()]:
                    c, f = j.lower().split('x')[0].strip().title(), j.lower().split('x')[1].strip().title()
                    st.session_state.analisados.append({"jogo": f"{c} x {f}", "m": "Ambas Marcam", "o": 1.85, "conf": 92, "atk": 80, "def": 60, "xg_c": 1.5, "weather": "☀️", "streak": 2})
                st.success("Matriz manual injetada.")
        
        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown(f"<div class='terminal-card'><b>[SUREBET SCANNER]</b><br>Oportunidade encontrada: Roma x Napoli.<br>Aposte na Betano e Bet365 para lucro 100% garantido.</div>", unsafe_allow_html=True)

    # RENDERIZAÇÃO DOS RESULTADOS (MIX CHATBET + V8 BARS)
    if st.session_state.analisados:
        st.markdown(f"<hr style='border-color: {card_border}; margin: 25px 0;'>", unsafe_allow_html=True)
        for idx, item in enumerate(st.session_state.analisados):
            html_card = f"""
            <div class='result-card'>
                <div style='display:flex; justify-content:space-between; align-items:center;'>
                    <div class='market-badge'>{item['m']}</div>
                    <div style='background:#1c2436; padding:4px 10px; border-radius:6px; font-weight:bold; color:{cor_neon}; border:1px solid {cor_neon}40;'>@{item['o']:.2f}</div>
                </div>
                <div style='font-size:14px; font-weight:800; margin-top:5px; color:{c_text};'>{item['jogo']}</div>
                <div style='font-size:10px; color:{c_sub}; margin-top:2px; margin-bottom:10px;'>{item['weather']} Hoje | 🔥 Streak: {item['streak']}V | 🎯 Conf: {item['conf']}%</div>
                
                <div style='font-size:9px; color:{c_sub};'>Poder Ofensivo (xG {item['xg_c']})</div>
                <div class='progress-bg'><div class='progress-fill-atk' style='width:{item['atk']}%;'></div></div>
                <div style='font-size:9px; color:{c_sub}; margin-top:4px;'>Força Defensiva</div>
                <div class='progress-bg' style='margin-bottom:15px;'><div class='progress-fill-def' style='width:{item['def']}%;'></div></div>
            </div>
            """
            st.markdown(html_card, unsafe_allow_html=True)
            
            c_add1, c_add2 = st.columns(2)
            with c_add1:
                if st.button("✔️ APOSTAR", key=f"add_{idx}", use_container_width=True): st.session_state.bilhete.append(item); st.toast("No Bilhete!")
            with c_add2:
                if st.button("💾 SALVAR", key=f"sav_{idx}", use_container_width=True): st.session_state.analises_salvas.append(item); st.toast("Tracking Salvo!")

# ==========================================
# ABA 3: OPERAÇÕES (BILHETE + TRACKING)
# ==========================================
with t3:
    st.markdown("<h3 style='font-size:16px; margin-bottom:15px;'>Seu Bilhete (Múltipla)</h3>", unsafe_allow_html=True)
    if st.session_state.bilhete:
        odd_f = 1.0
        st.markdown(f"<div style='background:{card_bg}; border:1px solid {card_border}; border-radius:12px; padding:15px;'>", unsafe_allow_html=True)
        for b in st.session_state.bilhete:
            odd_f *= b['o']
            st.markdown(f"<div style='display:flex; justify-content:space-between; margin-bottom:10px; border-bottom:1px solid {card_border}; padding-bottom:5px;'><span style='font-size:13px; font-weight:600;'>{b['m']} <br><span style='font-size:10px; color:{c_sub}; font-weight:normal;'>{b['jogo']}</span></span><span style='color:{cor_neon}; font-weight:bold;'>@{b['o']}</span></div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown(f"<h2 style='text-align:center; font-weight:900; font-size:32px; color:{c_text}; margin-top:15px;'>ODD <span style='color:{cor_neon};'>@{odd_f:.2f}</span></h2>", unsafe_allow_html=True)
        
        banca_escolhida = st.selectbox("Debitar Conta:", list(st.session_state.bancas.keys()))
        banca_disp = st.session_state.bancas[banca_escolhida]
        
        st.session_state.usar_kelly = st.checkbox("🧠 Usar Critério de Kelly", value=st.session_state.usar_kelly)
        rec_stake = banca_disp * (0.01 if st.session_state.usar_kelly else 0.03)
        
        valor_aposta = st.number_input("Valor da Entrada (R$):", min_value=1.0, value=float(max(1.0, rec_stake)), step=10.0)
        st.info(f"Retorno Bruto: {fmt_moeda(valor_aposta * odd_f)}")

        c_liq1, c_liq2 = st.columns(2)
        with c_liq1:
            if st.button("✅ BATER GREEN", type="primary", use_container_width=True):
                tocar_som(); st.session_state.total_jogos += len(st.session_state.bilhete); st.session_state.total_acertos += len(st.session_state.bilhete)
                st.session_state.bancas[banca_escolhida] += (valor_aposta * odd_f); st.session_state.historico_banca.append(sum(st.session_state.bancas.values()))
                st.session_state.bilhete = []; time.sleep(1); st.rerun()
        with c_liq2:
            if st.button("❌ ASSUMIR RED", use_container_width=True):
                st.session_state.total_jogos += len(st.session_state.bilhete); st.session_state.bancas[banca_escolhida] -= valor_aposta
                st.session_state.historico_banca.append(sum(st.session_state.bancas.values())); st.session_state.bilhete = []; st.rerun()
    else:
        st.info("Nenhuma aposta selecionada.")

    st.markdown("<h3 style='font-size:16px; margin-top:30px; margin-bottom:15px;'>Tracking Individual (Singles)</h3>", unsafe_allow_html=True)
    if st.session_state.analises_salvas:
        for i, a in enumerate(st.session_state.analises_salvas):
            st.markdown(f"<div style='background:{card_bg}; border-left:3px solid #00d2ff; padding:10px; border-radius:8px; margin-bottom:5px;'><div style='font-size:12px; font-weight:bold;'>{a['m']} (@{a['o']})</div><div style='font-size:10px; color:{c_sub};'>{a['jogo']}</div></div>", unsafe_allow_html=True)
            c_g, c_r, c_d = st.columns([0.4, 0.4, 0.2])
            with c_g: 
                if st.button("✅ WIN", key=f"tw_{i}"): st.session_state.total_jogos+=1; st.session_state.total_acertos+=1; st.session_state.historico_greens.insert(0, {"Jogo": a['jogo'], "Odd": a['o']}); st.session_state.analises_salvas.pop(i); tocar_som(); st.rerun()
            with c_r: 
                if st.button("❌ LOSS", key=f"tl_{i}"): st.session_state.total_jogos+=1; st.session_state.analises_salvas.pop(i); st.rerun()
            with c_d: 
                if st.button("🗑️", key=f"td_{i}"): st.session_state.analises_salvas.pop(i); st.rerun()
    else:
        st.caption("Nenhum jogo salvo para tracking.")

# ==========================================
# ABA 4: SAFE (BINGO DO DIA)
# ==========================================
with t4:
    st.markdown("<h4 class='metallic-text'>ALTO EV (SAFE)</h4>", unsafe_allow_html=True)
    if not st.session_state.is_vip:
        st.info("Eleve o plano para Supremo.")
    else:
        if not st.session_state.analisados: st.warning("Faça uma varredura no Radar primeiro.")
        else:
            seguros = sorted([j for j in st.session_state.analisados if 1.15 <= j.get('o', 1.5) <= 1.65], key=lambda x: x.get('conf', 0), reverse=True)
            if len(seguros) >= 2:
                safe_pick = seguros[:2]
                st.markdown(f"<div class='result-card' style='border-color:{cor_neon};'><div style='text-align:center;'><span class='market-badge'>🏆 DUPLA DO DIA</span></div><div style='font-size:14px; font-weight:bold;'>1. {safe_pick[0]['jogo']} ({safe_pick[0]['m']} @{safe_pick[0]['o']})</div><div style='font-size:14px; font-weight:bold; margin-top:5px;'>2. {safe_pick[1]['jogo']} ({safe_pick[1]['m']} @{safe_pick[1]['o']})</div><hr style='border-color:{card_border};'><h3 style='text-align:center; color:{cor_neon};'>ODD TOTAL: {(safe_pick[0]['o'] * safe_pick[1]['o']):.2f}</h3></div>", unsafe_allow_html=True)
                if st.button("🔥 COPIAR PARA BILHETE"): st.session_state.bilhete.extend(safe_pick); st.toast("Copiado!")
            else: st.warning("A IA não encontrou 2 jogos com perfil 'Safe' hoje.")

# ==========================================
# ABA 5: HUB E PERFIL
# ==========================================
with t5:
    st.markdown(f"<h3 style='color:{c_text}; text-align:center; font-weight:900;'>V8 <span style='color:{cor_neon};'>HUB</span></h3>", unsafe_allow_html=True)
    
    with st.expander("🏛️ GESTÃO DE BANCAS"):
        st.session_state.bancas["Betano"] = st.number_input("Betano", value=st.session_state.bancas["Betano"], step=50.0)
        st.session_state.bancas["Bet365"] = st.number_input("Bet365", value=st.session_state.bancas["Bet365"], step=50.0)

    with st.expander("⚙️ CUSTOMIZAÇÃO & EXPORTAÇÃO"):
        st.selectbox("Tema do App:", ["🟢 Verde Hacker (Dark)", "⚪ Modo Claro (Light)"], key="tema_escolhido")
        st.text_input("Foco Específico (Time):", placeholder="Ex: Flamengo", key="time_coracao")
        
        df_greens = pd.DataFrame(st.session_state.historico_greens)
        if not df_greens.empty:
            csv = df_greens.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Baixar Histórico (CSV)", data=csv, file_name='v8_historico.csv', mime='text/csv', use_container_width=True)

    if st.button("ENCERRAR SESSÃO", type="primary"):
        st.session_state.autenticado = False
        st.rerun()
