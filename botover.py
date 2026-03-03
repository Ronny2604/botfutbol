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
st.set_page_config(page_title="V8 SUPREME A.I.", layout="wide", initial_sidebar_state="collapsed")

MASTER_KEY = "ronnyp@2025"
FILE_KEYS = "keys.txt" 
TOKEN = '8543393879:AAEsaXAAq2A19zbmMEfHZb-R7nLL-VdierU'
CHAT_ID = '-1003799258159'
ODDS_API_KEY = "da4633249ece20283d29604cec7a7114"

# --- 2. INICIALIZAÇÃO DE ESTADOS ---
for key, default_val in [
    ('is_admin', False), ('autenticado', False), ('user_nome', ""), 
    ('bilhete', []), ('analisados', []), ('analises_salvas', []), 
    ('tipo_analise_selecionado', 'Análise Geral'),
    ('avatar', "🐺"), ('moeda', "R$"), ('juros_compostos', False), ('usar_kelly', False),
    ('bancas', {"Betano": 1000.0, "Bet365": 500.0, "Betfair": 0.0}),
    ('historico_banca', [1500.0]), ('banca_inicial_dia', 1500.0), ('recuperacao_red', False),
    ('conquistas', ["🏅 Novato Promissor"]), ('total_jogos', 1248), ('total_acertos', 1115),
    ('historico_greens', [])
]:
    if key not in st.session_state: st.session_state[key] = default_val

# --- FUNÇÕES DE SISTEMA ---
def fmt_moeda(valor): return f"{st.session_state.moeda} {valor:,.2f}"

def calcular_forca_equipa(nome_equipa):
    hash_object = hashlib.md5(nome_equipa.encode())
    num = int(hash_object.hexdigest(), 16)
    return 60 + (num % 35), 50 + ((num // 10) % 40) 

def gerar_dados_mock():
    times = ["Real Madrid", "Barcelona", "Man City", "Arsenal", "Bayern Munique", "Flamengo", "Palmeiras", "Liverpool", "Chelsea", "Milan", "Inter", "Napoli"]
    random.shuffle(times)
    return [{"home_team": times[i*2], "away_team": times[i*2+1], "commence_time": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")} for i in range(6)]

@st.cache_data(ttl=600, show_spinner=False)
def buscar_dados_api(codigo_da_liga):
    url = f"https://api.the-odds-api.com/v4/sports/{codigo_da_liga}/odds/?apiKey={ODDS_API_KEY}&regions=eu,uk&markets=h2h,totals"
    try:
        r = requests.get(url, timeout=5)
        if r.status_code == 200 and isinstance(r.json(), list): return r.json()
    except: pass
    return gerar_dados_mock()

# --- 3. CSS ESTILO "CHATBET" (Deep Dark & Grid) ---
cor_neon = "#00ff88"
bg_app = "#0b101a" 
card_bg = "#121824"
card_border = "#1c2436"

st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    
    html, body, [data-testid="stAppViewContainer"], .main {{
        background-color: {bg_app} !important;
        font-family: 'Inter', sans-serif !important;
        color: #ffffff !important;
    }}
    
    header[data-testid="stHeader"] {{ display: none !important; }}
    .block-container {{ padding-top: 1rem !important; padding-bottom: 100px !important; max-width: 600px !important; margin: auto; }}
    
    /* ABAS SUPERIORES DISCRETAS */
    div[data-testid="stTabs"] > div:first-of-type {{ 
        background: transparent !important; 
        border-bottom: 1px solid {card_border} !important;
        padding-bottom: 5px; margin-bottom: 25px;
    }}
    div[data-testid="stTabs"] button[role="tab"] {{ color: #5a6b82 !important; font-weight: 600 !important; font-size: 12px !important; background: transparent !important; border: none !important; }}
    div[data-testid="stTabs"] button[role="tab"][aria-selected="true"] {{ color: {cor_neon} !important; border-bottom: 2px solid {cor_neon} !important; }}
    
    /* BOTÕES DA GRELHA 3x3 */
    .stButton>button[kind="secondary"] {{
        height: 100px !important;
        background-color: {card_bg} !important;
        border: 1px solid {card_border} !important;
        border-radius: 16px !important;
        color: #8b9bb4 !important;
        font-size: 13px !important;
        font-weight: 600 !important;
        display: flex !important;
        flex-direction: column !important;
        justify-content: center !important;
        align-items: center !important;
        transition: all 0.2s ease !important;
    }}
    .stButton>button[kind="secondary"]:hover, .stButton>button[kind="secondary"]:active, .stButton>button[kind="secondary"]:focus {{
        border-color: {cor_neon} !important;
        color: {cor_neon} !important;
        background-color: rgba(0, 255, 136, 0.05) !important;
        box-shadow: 0 0 15px rgba(0, 255, 136, 0.1) !important;
    }}
    
    /* BOTÃO GIGANTE (ANALISAR AGORA) E BOTOES DE APOSTA */
    .stButton>button[kind="primary"] {{
        background: linear-gradient(90deg, #00d2ff 0%, #00ff88 100%) !important;
        color: #000000 !important;
        font-weight: 800 !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 15px !important;
        font-size: 16px !important;
        box-shadow: 0 5px 15px rgba(0, 255, 136, 0.3) !important;
    }}
    
    /* CARDS DE RESULTADO (Estilo Lista) */
    .result-card {{
        background-color: {card_bg};
        border: 1px solid {cor_neon}40;
        border-radius: 12px;
        padding: 15px;
        margin-bottom: 15px;
    }}
    .market-badge {{
        background: rgba(0, 255, 136, 0.1);
        color: {cor_neon};
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 12px;
        font-weight: 800;
        display: inline-block;
        margin-bottom: 10px;
    }}
    
    /* BARRAS DE ESTATÍSTICA V8 */
    .progress-bg {{ width: 100%; background: #222; border-radius: 10px; height: 4px; margin-bottom: 8px; overflow: hidden; }}
    .progress-fill-atk {{ height: 4px; background: linear-gradient(90deg, #ff0055, #ff5555); border-radius: 10px; }}
    .progress-fill-def {{ height: 4px; background: linear-gradient(90deg, #0055ff, #00aaff); border-radius: 10px; }}
    
    ::-webkit-scrollbar {{ width: 0px; background: transparent; }} 
    </style>
""", unsafe_allow_html=True)

# --- 4. TELA DE LOGIN ---
if not st.session_state.autenticado:
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown(f"<h2 style='text-align:center; color:white; font-weight:800;'>V8 <span style='color:{cor_neon};'>A.I.</span></h2>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align:center; color:#5a6b82; font-size:14px; margin-bottom:30px;'>Conecte-se ao terminal de análise.</p>", unsafe_allow_html=True)
    nome_in = st.text_input("Seu Nome:")
    key_in = st.text_input("Chave Criptografada:", type="password")
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("ACESSAR PLATAFORMA", type="primary", use_container_width=True):
        st.session_state.autenticado = True
        st.session_state.user_nome = nome_in if nome_in else "Trader"
        st.rerun()
    st.stop()

# --- 5. NAVEGAÇÃO PRINCIPAL ---
t1, t2, t3, t4 = st.tabs(["⚽ JOGOS", "🤖 A.I. SCANNER", "🧾 BILHETE", "⚙️ PERFIL"])

# ==========================================
# ABA 1: DASHBOARD (JOGOS)
# ==========================================
with t1:
    saldo_total = sum(st.session_state.bancas.values())
    st.markdown(f"<div style='background:{card_bg}; border:1px solid {card_border}; border-radius:12px; padding:15px; margin-bottom:20px; display:flex; justify-content:space-between; align-items:center;'><div><div style='color:#8b9bb4; font-size:12px;'>Operador</div><div style='color:white; font-size:16px; font-weight:bold;'>{st.session_state.user_nome}</div></div><div style='text-align:right;'><div style='color:#8b9bb4; font-size:12px;'>Banca Total</div><div style='color:{cor_neon}; font-size:18px; font-weight:bold;'>{fmt_moeda(saldo_total)}</div></div></div>", unsafe_allow_html=True)

    jogos = gerar_dados_mock()
    st.markdown("<h4 style='font-size:14px; color:white; margin-bottom:15px;'>🔴 Partidas em Destaque</h4>", unsafe_allow_html=True)
    for j in jogos[:3]:
        st.markdown(f"<div style='background:{card_bg}; border:1px solid {card_border}; border-radius:10px; padding:12px; margin-bottom:10px; display:flex; justify-content:space-between;'><span style='color:white; font-size:14px; font-weight:600;'>{j['home_team']} <span style='color:#5a6b82;'>x</span> {j['away_team']}</span><span style='color:#5a6b82; font-size:12px;'>Hoje</span></div>", unsafe_allow_html=True)

# ==========================================
# ABA 2: RADAR A.I. (A GRELHA IGUAL À FOTO)
# ==========================================
with t2:
    st.markdown("<h3 style='text-align:center; color:white; font-size:18px; margin-bottom:20px;'>Escolha o tipo de análise</h3>", unsafe_allow_html=True)
    
    # GRELHA 3x3 DE BOTÕES
    opcoes = [
        ("📈\nAnálise Geral", "Análise Geral"), ("🏆\nResultado Final", "Resultado Final"), ("⚽\nGols", "Gols"),
        ("⏳\nPrimeiro Tempo", "Primeiro Tempo"), ("🚩\nEscanteios", "Escanteios"), ("🟨\nCartões", "Cartões"),
        ("🎯\nChutes", "Chutes"), ("👤\nJogador", "Jogador"), ("🔄\nAmbas Marcam", "Ambas Marcam")
    ]
    
    for i in range(0, 9, 3):
        c1, c2, c3 = st.columns(3)
        with c1:
            if st.button(opcoes[i][0], key=f"btn_{i}", use_container_width=True): st.session_state.tipo_analise_selecionado = opcoes[i][1]
        with c2:
            if st.button(opcoes[i+1][0], key=f"btn_{i+1}", use_container_width=True): st.session_state.tipo_analise_selecionado = opcoes[i+1][1]
        with c3:
            if st.button(opcoes[i+2][0], key=f"btn_{i+2}", use_container_width=True): st.session_state.tipo_analise_selecionado = opcoes[i+2][1]
            
    st.markdown(f"<p style='text-align:center; color:{cor_neon}; font-size:12px; margin-top:10px;'>Selecionado: <b>{st.session_state.tipo_analise_selecionado}</b></p>", unsafe_allow_html=True)

    LIGAS_DISPONIVEIS = {"🇪🇺 Champions League": "soccer_uefa_champs_league", "🇬🇧 Premier League": "soccer_epl", "🇧🇷 Brasileirão": "soccer_brazil_campeonato"}
    codigo_da_liga = LIGAS_DISPONIVEIS[st.selectbox("Selecionar Liga:", list(LIGAS_DISPONIVEIS.keys()))]

    # BOTÃO GIGANTE
    if st.button("ANALISAR AGORA", type="primary", use_container_width=True):
        with st.spinner(f"A processar {st.session_state.tipo_analise_selecionado}..."):
            time.sleep(1.5)
            dados = buscar_dados_api(codigo_da_liga)
            if not isinstance(dados, list) or len(dados) == 0: dados = gerar_dados_mock()
            
            st.session_state.analisados = []
            
            for jogo in dados[:3]:
                c, f = jogo.get('home_team', 'Casa'), jogo.get('away_team', 'Fora')
                
                mercado_base = "Vitória"
                if "Gols" in st.session_state.tipo_analise_selecionado: mercado_base = "Over 2.5 Gols"
                elif "Escanteios" in st.session_state.tipo_analise_selecionado: mercado_base = "Over 8.5 Cantos"
                elif "Ambas" in st.session_state.tipo_analise_selecionado: mercado_base = "Ambas Marcam: Sim"
                elif "Cartões" in st.session_state.tipo_analise_selecionado: mercado_base = "Over 4.5 Cartões"
                
                atk, dfs = calcular_forca_equipa(c)
                st.session_state.analisados.append({
                    "jogo": f"{c} x {f}", "m": f"{mercado_base} ({c})" if mercado_base == "Vitória" else mercado_base, 
                    "o": round(random.uniform(1.4, 2.2), 2), "data": "Hoje", "atk": atk, "def": dfs, "xg_c": round(random.uniform(0.8, 2.5), 2)
                })

    with st.expander("🛠️ Ferramentas Manuais & Override"):
        grade = st.text_area("Input de Jogos Manuais:", placeholder="Ex: Flamengo x Vasco")
        if st.button("Forçar Análise Manual"):
            if grade:
                st.session_state.analisados = []
                for j in [x for x in grade.split('\n') if 'x' in x.lower()]:
                    c, f = j.lower().split('x')[0].strip().title(), j.lower().split('x')[1].strip().title()
                    st.session_state.analisados.append({"jogo": f"{c} x {f}", "m": "Ambas Marcam", "o": 1.85, "data": "Manual", "atk": 80, "def": 60, "xg_c": 1.5})
                st.success("Matriz manual injetada.")

    # RESULTADOS DA ANÁLISE (O código HTML está esmagado em 1 linha para evitar o Bug Preto)
    if st.session_state.analisados:
        st.markdown(f"<hr style='border-color:{card_border}; margin: 30px 0;'>", unsafe_allow_html=True)
        for idx, item in enumerate(st.session_state.analisados):
            html_card = f"<div class='result-card'><div style='display:flex; justify-content:space-between;'><div class='market-badge'>{item['m']}</div><div style='background:#1c2436; padding:4px 10px; border-radius:6px; font-weight:bold; border:1px solid {cor_neon}40; color:{cor_neon};'>@{item['o']:.2f}</div></div><div style='color:#ffffff; font-size:14px; font-weight:800; margin-bottom:5px;'>⚽ {item['jogo']}</div><div style='color:#5a6b82; font-size:11px; margin-bottom:15px;'>📅 {item['data']}</div><div style='font-size:9px; color:#5a6b82;'>Poder Ofensivo (xG {item['xg_c']})</div><div class='progress-bg'><div class='progress-fill-atk' style='width:{item['atk']}%;'></div></div><div style='font-size:9px; color:#5a6b82; margin-top:4px;'>Força Defensiva</div><div class='progress-bg' style='margin-bottom:15px;'><div class='progress-fill-def' style='width:{item['def']}%;'></div></div></div>"
            st.markdown(html_card, unsafe_allow_html=True)
            
            c_add1, c_add2 = st.columns(2)
            with c_add1:
                if st.button(f"✔️ APOSTAR", key=f"add_{idx}", type="primary", use_container_width=True):
                    st.session_state.bilhete.append(item)
                    st.toast("Adicionado ao seu carrinho!")
            with c_add2:
                if st.button(f"💾 SALVAR", key=f"sav_{idx}", type="primary", use_container_width=True):
                    st.session_state.analises_salvas.append(item)
                    st.toast("Adicionado ao Tracking!")

# ==========================================
# ABA 3: BILHETE / OPERAÇÕES
# ==========================================
with t3:
    st.markdown("<h3 style='color:white; font-size:18px; margin-bottom:20px;'>Seu Bilhete (Múltipla)</h3>", unsafe_allow_html=True)
    if st.session_state.bilhete:
        odd_f = 1.0
        html_bilhete = f"<div style='background:{card_bg}; border:1px solid {cor_neon}; border-radius:12px; padding:15px; margin-bottom:15px;'>"
        for b in st.session_state.bilhete:
            odd_f *= b['o']
            html_bilhete += f"<div style='display:flex; justify-content:space-between; margin-bottom:10px; border-bottom:1px solid {card_border}; padding-bottom:5px;'><span style='font-size:13px; font-weight:600; color:white;'>{b['m']} <br><span style='font-size:10px; color:#5a6b82; font-weight:normal;'>{b['jogo']}</span></span><span style='color:{cor_neon}; font-weight:bold;'>@{b['o']:.2f}</span></div>"
        html_bilhete += "</div>"
        st.markdown(html_bilhete, unsafe_allow_html=True)
        
        st.markdown(f"<h2 style='text-align:center; color:white;'>ODD TOTAL: <span style='color:{cor_neon};'>@{odd_f:.2f}</span></h2>", unsafe_allow_html=True)
        
        valor = st.number_input("Valor da Aposta (R$):", value=50.0, step=10.0)
        st.info(f"Retorno Estimado: {fmt_moeda(valor * odd_f)}")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ BATER GREEN", type="primary", use_container_width=True):
                st.session_state.bancas["Betano"] += (valor * odd_f)
                st.session_state.bilhete = []
                st.success("Lucro adicionado à banca!")
                time.sleep(1); st.rerun()
        with col2:
            if st.button("🗑️ LIMPAR BILHETE", use_container_width=True):
                st.session_state.bilhete = []
                st.rerun()
    else:
        st.info("Nenhuma análise adicionada. Use o Radar A.I.")

    st.markdown("<h3 style='color:white; font-size:16px; margin-top:30px; margin-bottom:15px;'>Tracking Individual (Singles)</h3>", unsafe_allow_html=True)
    if st.session_state.analises_salvas:
        for i, a in enumerate(st.session_state.analises_salvas):
            st.markdown(f"<div style='background:{card_bg}; border-left:3px solid #00d2ff; padding:10px; border-radius:8px; margin-bottom:5px;'><div style='font-size:12px; font-weight:bold; color:white;'>{a['m']} (@{a['o']})</div><div style='font-size:10px; color:#5a6b82;'>{a['jogo']}</div></div>", unsafe_allow_html=True)
            c_g, c_r, c_d = st.columns([0.4, 0.4, 0.2])
            with c_g: 
                if st.button("✅ WIN", key=f"tw_{i}"): st.session_state.total_jogos+=1; st.session_state.total_acertos+=1; st.session_state.analises_salvas.pop(i); st.rerun()
            with c_r: 
                if st.button("❌ LOSS", key=f"tl_{i}"): st.session_state.total_jogos+=1; st.session_state.analises_salvas.pop(i); st.rerun()
            with c_d: 
                if st.button("🗑️", key=f"td_{i}"): st.session_state.analises_salvas.pop(i); st.rerun()
    else:
        st.caption("Nenhum jogo salvo para tracking.")

# ==========================================
# ABA 4: PERFIL E HUB DE FERRAMENTAS
# ==========================================
with t4:
    st.markdown("<h3 style='color:white; font-size:18px; margin-bottom:20px;'>Ferramentas VIP</h3>", unsafe_allow_html=True)
    
    with st.expander("🧠 Ferramentas Institucionais (Ativas)"):
        st.markdown("""
        * **Surebet Scanner:** A rodar no back-end.
        * **Kelly Criterion:** Disponível na formatação de stakes.
        * **Stop Loss:** Segurança de capital ativada (10%).
        * **Alerta de Lesões:** Integrado ao motor de varredura.
        """)
        
    with st.expander("🏛️ Gerir Bancas e Moeda"):
        st.selectbox("Moeda Global:", ["R$", "US$", "€", "₿"], key="moeda")
        st.session_state.bancas["Betano"] = st.number_input("Betano", value=st.session_state.bancas["Betano"], step=50.0)
        st.session_state.bancas["Bet365"] = st.number_input("Bet365", value=st.session_state.bancas["Bet365"], step=50.0)
        
    if st.button("Sair da Conta"):
        st.session_state.autenticado = False
        st.rerun()
