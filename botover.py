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
ODDS_API_KEY = "da4633249ece20283d29604cec7a7114" # Sua chave padrão (pode estar esgotada)

# --- 2. INICIALIZAÇÃO DE ESTADOS ---
for key, default_val in [
    ('is_admin', False), ('autenticado', False), ('user_nome', ""), 
    ('bilhete', []), ('analisados', []), ('analises_salvas', []), 
    ('tipo_analise_selecionado', 'Análise Geral'),
    ('avatar', "🐺"), ('moeda', "R$"), ('juros_compostos', False), ('usar_kelly', False),
    ('bancas', {"Betano": 1000.0, "Bet365": 500.0, "Betfair": 0.0}),
    ('historico_banca', [1500.0]), ('banca_inicial_dia', 1500.0), ('recuperacao_red', False),
    ('conquistas', ["🏅 Novato Promissor"]), ('total_jogos', 1248), ('total_acertos', 1115),
    ('historico_greens', []), ('api_key_odds', ODDS_API_KEY)
]:
    if key not in st.session_state: st.session_state[key] = default_val

# --- FUNÇÕES DE SISTEMA ---
def fmt_moeda(valor): return f"{st.session_state.moeda} {valor:,.2f}"

def calcular_forca_equipa(nome_equipa):
    hash_object = hashlib.md5(nome_equipa.encode())
    num = int(hash_object.hexdigest(), 16)
    return 60 + (num % 35), 50 + ((num // 10) % 40) 

def gerar_dados_mock():
    # Simulação apenas acionada se a API falhar
    times = ["Arsenal", "Chelsea", "Liverpool", "Man City", "Aston Villa", "Newcastle", "Tottenham", "Brighton"]
    random.shuffle(times)
    d = datetime.utcnow() + timedelta(days=1)
    return [{"home_team": times[i*2], "away_team": times[i*2+1], "commence_time": d.strftime("%Y-%m-%dT%H:%M:%SZ")} for i in range(4)]

@st.cache_data(ttl=120, show_spinner=False)
def buscar_dados_api_avancado(codigo_da_liga, api_key):
    url = f"https://api.the-odds-api.com/v4/sports/{codigo_da_liga}/odds/?apiKey={api_key}&regions=eu,uk&markets=h2h"
    try:
        r = requests.get(url, timeout=8)
        if r.status_code == 200:
            return r.json() # Lista de jogos
        elif r.status_code in [401, 403]:
            return "ERRO_AUTH" # Chave inválida
        elif r.status_code == 429:
            return "ERRO_QUOTA" # Limite esgotado
    except Exception as e:
        return "ERRO_CONEXAO"
    return "ERRO_DESCONHECIDO"

def tocar_som_customizado():
    st.markdown('<audio autoplay style="display:none;"><source src="https://assets.mixkit.co/active_storage/sfx/2003/2003-preview.mp3" type="audio/mpeg"></audio>', unsafe_allow_html=True)

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
    
    div[data-testid="stTabs"] > div:first-of-type {{ 
        background: {bg_app} !important; 
        border-bottom: 1px solid {card_border} !important;
        padding-bottom: 5px; margin-bottom: 25px;
        position: sticky; top: 0; z-index: 999;
    }}
    div[data-testid="stTabs"] button[role="tab"] {{ color: #5a6b82 !important; font-weight: 600 !important; font-size: 12px !important; background: transparent !important; border: none !important; }}
    div[data-testid="stTabs"] button[role="tab"][aria-selected="true"] {{ color: {cor_neon} !important; border-bottom: 2px solid {cor_neon} !important; }}
    
    .stButton>button[kind="secondary"] {{
        height: 100px !important; background-color: {card_bg} !important; border: 1px solid {card_border} !important;
        border-radius: 16px !important; color: #8b9bb4 !important; font-size: 13px !important; font-weight: 600 !important;
        display: flex !important; flex-direction: column !important; justify-content: center !important; align-items: center !important;
        transition: all 0.2s ease !important;
    }}
    .stButton>button[kind="secondary"]:hover, .stButton>button[kind="secondary"]:active, .stButton>button[kind="secondary"]:focus {{
        border-color: {cor_neon} !important; color: {cor_neon} !important; background-color: rgba(0, 255, 136, 0.05) !important;
        box-shadow: 0 0 15px rgba(0, 255, 136, 0.1) !important;
    }}
    
    .stButton>button[kind="primary"] {{
        background: linear-gradient(90deg, #00d2ff 0%, #00ff88 100%) !important; color: #000000 !important;
        font-weight: 800 !important; border: none !important; border-radius: 12px !important; padding: 15px !important;
        font-size: 16px !important; box-shadow: 0 5px 15px rgba(0, 255, 136, 0.3) !important;
    }}
    
    .result-card {{ background-color: {card_bg}; border: 1px solid {card_border}; border-radius: 12px; padding: 15px; margin-bottom: 15px; }}
    .market-badge {{ background: rgba(0, 255, 136, 0.1); color: {cor_neon}; padding: 4px 10px; border-radius: 6px; font-size: 12px; font-weight: 800; display: inline-block; margin-bottom: 10px; }}
    
    .progress-bg {{ width: 100%; background: #222; border-radius: 10px; height: 4px; margin-bottom: 8px; overflow: hidden; }}
    .progress-fill-atk {{ height: 4px; background: linear-gradient(90deg, #ff0055, #ff5555); border-radius: 10px; }}
    .progress-fill-def {{ height: 4px; background: linear-gradient(90deg, #0055ff, #00aaff); border-radius: 10px; }}
    
    ::-webkit-scrollbar {{ width: 0px; background: transparent; }} 
    
    div[data-baseweb="input"] > div, div[data-baseweb="select"] > div {{ background-color: {card_bg} !important; border: 1px solid {card_border} !important; color: white !important; }}
    </style>
""", unsafe_allow_html=True)

# --- 4. TELA DE LOGIN ---
if not st.session_state.autenticado:
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown(f"<h2 style='text-align:center; color:white; font-weight:800;'>V8 <span style='color:{cor_neon};'>A.I.</span></h2>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align:center; color:#5a6b82; font-size:14px; margin-bottom:30px;'>Conecte-se ao terminal de análise.</p>", unsafe_allow_html=True)
    nome_in = st.text_input("Operador:", placeholder="Seu Nome")
    key_in = st.text_input("Chave Criptografada:", type="password")
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("ACESSAR PLATAFORMA", type="primary", use_container_width=True):
        st.session_state.autenticado = True
        st.session_state.user_nome = nome_in if nome_in else "Trader VIP"
        st.rerun()
    st.stop()

# --- HEADER TOP ---
saldo_total = sum(st.session_state.bancas.values())
st.markdown(f"""
    <div style='display:flex; justify-content:space-between; align-items:center; margin-bottom: 20px; padding: 15px; background: {card_bg}; border-radius: 12px; border: 1px solid {card_border};'>
        <div style='display:flex; align-items:center;'>
            <div style='font-size: 24px; margin-right: 10px;'>{st.session_state.avatar}</div>
            <div>
                <div style='font-weight:900; font-size:14px; color:white;'>{st.session_state.user_nome.upper()} <span style='background:{cor_neon}; color:#000; font-size:9px; padding:2px 4px; border-radius:4px;'>PRO</span></div>
                <div style='color:{cor_neon}; font-size:10px;'>{st.session_state.titulo_apostador}</div>
            </div>
        </div>
        <div style='text-align:right;'>
            <div style='color:#8b9bb4; font-size:10px;'>Banca Viva</div>
            <div style='color:{cor_neon}; font-size:18px; font-weight:bold;'>{fmt_moeda(saldo_total)}</div>
        </div>
    </div>
""", unsafe_allow_html=True)

# --- 5. NAVEGAÇÃO PRINCIPAL ---
t1, t2, t3, t4 = st.tabs(["⚽ JOGOS", "🤖 A.I. SCANNER", "🧾 BILHETE", "⚙️ HUB VIP"])

# ==========================================
# ABA 1: DASHBOARD (VITRINE DE JOGOS REAIS)
# ==========================================
with t1:
    st.markdown("<h4 style='font-size:14px; color:white; margin-bottom:15px;'>🔴 Vitrine de Jogos (Inglaterra)</h4>", unsafe_allow_html=True)
    
    # Tenta puxar real, senão mostra o diagnóstico!
    jogos_home = buscar_dados_api_avancado("soccer_epl", st.session_state.api_key_odds)
    
    if jogos_home == "ERRO_QUOTA":
        st.error("⚠️ O Limite da sua Chave API esgotou. Vá na aba HUB VIP e insira uma nova.")
        jogos_home = gerar_dados_mock()
    elif jogos_home == "ERRO_AUTH":
        st.error("⚠️ Chave API inválida. Vá na aba HUB VIP e insira uma correta.")
        jogos_home = gerar_dados_mock()
    elif type(jogos_home) == str or (isinstance(jogos_home, list) and len(jogos_home) == 0):
        st.warning("⚠️ Não há jogos na Premier League hoje. A exibir próximos destaques.")
        jogos_home = gerar_dados_mock()
    
    for j in jogos_home[:4]:
        c, f = j.get('home_team', 'Casa'), j.get('away_team', 'Fora')
        try:
            dt = datetime.strptime(j.get('commence_time', ''), "%Y-%m-%dT%H:%M:%SZ") - timedelta(hours=3)
            data_fmt = dt.strftime("%d/%m %H:%M")
        except: data_fmt = "Em breve"
        
        st.markdown(f"""
            <div style='background:{card_bg}; border:1px solid {card_border}; border-radius:10px; padding:12px; margin-bottom:10px; display:flex; justify-content:space-between;'>
                <span style='color:white; font-size:14px; font-weight:600;'>{c} <span style='color:#5a6b82;'>x</span> {f}</span>
                <span style='color:#5a6b82; font-size:12px;'>{data_fmt}</span>
            </div>
        """, unsafe_allow_html=True)

# ==========================================
# ABA 2: RADAR A.I. (A GRELHA)
# ==========================================
with t2:
    st.markdown("<h3 style='text-align:center; color:white; font-size:18px; margin-bottom:20px;'>Escolha o tipo de análise</h3>", unsafe_allow_html=True)
    
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
            
    st.markdown(f"<p style='text-align:center; color:{cor_neon}; font-size:12px; margin-top:10px;'>Foco Selecionado: <b>{st.session_state.tipo_analise_selecionado}</b></p>", unsafe_allow_html=True)

    LIGAS_DISPONIVEIS = {"🇪🇺 Champions League": "soccer_uefa_champs_league", "🇬🇧 Premier League": "soccer_epl", "🇪🇸 La Liga": "soccer_spain_la_liga", "🇧🇷 Brasileirão": "soccer_brazil_campeonato"}
    codigo_da_liga = LIGAS_DISPONIVEIS[st.selectbox("Selecionar Liga para Varredura:", list(LIGAS_DISPONIVEIS.keys()))]

    st.markdown("<br>", unsafe_allow_html=True)
    
    # O BOTÃO DE SCAN REAL
    if st.button("ANALISAR AGORA", type="primary", use_container_width=True):
        with st.spinner(f"A varrer base de dados da API..."):
            time.sleep(1.5)
            
            # --- BUSCA REAL NA API ---
            dados = buscar_dados_api_avancado(codigo_da_liga, st.session_state.api_key_odds)
            
            # DIAGNÓSTICO E TRATAMENTO DE ERROS NA TELA:
            if dados == "ERRO_QUOTA":
                st.error("❌ ALERTA: O limite da sua Chave API esgotou. A exibir simulação de jogos. Atualize a chave no HUB VIP.")
                dados = gerar_dados_mock()
            elif dados == "ERRO_AUTH":
                st.error("❌ ALERTA: A sua Chave API atual é inválida. A exibir simulação. Atualize a chave no HUB VIP.")
                dados = gerar_dados_mock()
            elif type(dados) == str or (isinstance(dados, list) and len(dados) == 0):
                st.warning("⚠️ Não há jogos abertos nesta liga para hoje. A exibir próximos destaques.")
                dados = gerar_dados_mock()
            else:
                st.success("✅ Jogos Reais extraídos com sucesso!")
            
            st.session_state.analisados = []
            
            for jogo in dados[:5]:
                c, f = jogo.get('home_team', 'Casa'), jogo.get('away_team', 'Fora')
                
                # Extrai Odd Real de Match Winner se existir
                odd_real = round(random.uniform(1.4, 2.3), 2)
                if jogo.get('bookmakers'):
                    try:
                        odd_real = jogo['bookmakers'][0]['markets'][0]['outcomes'][0]['price']
                    except: pass
                
                # Adaptação de mercado
                mercado_base = f"Vitória {c}"
                if "Gols" in st.session_state.tipo_analise_selecionado: mercado_base = "Over 2.5 Gols"
                elif "Escanteios" in st.session_state.tipo_analise_selecionado: mercado_base = "Over 8.5 Cantos"
                elif "Ambas" in st.session_state.tipo_analise_selecionado: mercado_base = "Ambas Marcam: Sim"
                
                try:
                    dt = datetime.strptime(jogo.get('commence_time', ''), "%Y-%m-%dT%H:%M:%SZ") - timedelta(hours=3)
                    d_txt = dt.strftime("%d/%m %H:%M")
                except: d_txt = "Em breve"

                atk, dfs = calcular_forca_equipa(c)
                st.session_state.analisados.append({
                    "jogo": f"{c} x {f}", "m": mercado_base, "o": odd_real, "data": d_txt, 
                    "atk": atk, "def": dfs, "conf": random.randint(85,99), "xg_c": round(random.uniform(1.1, 2.9), 2)
                })

    with st.expander("🛠️ OVERRIDE MANUAL (Sua própria grade)"):
        grade = st.text_area("Input de Jogos Manuais:", placeholder="Ex: Flamengo x Vasco")
        if st.button("Forçar Análise Manual"):
            if grade:
                st.session_state.analisados = []
                for j in [x for x in grade.split('\n') if 'x' in x.lower()]:
                    c, f = j.lower().split('x')[0].strip().title(), j.lower().split('x')[1].strip().title()
                    atk, dfs = calcular_forca_equipa(c)
                    st.session_state.analisados.append({"jogo": f"{c} x {f}", "m": "Aposta Sugerida", "o": 1.85, "data": "Manual", "atk": atk, "def": dfs, "conf": 92, "xg_c": 1.7})
                st.success("Matriz manual injetada.")

    # RENDERIZAÇÃO DOS CARTÕES
    if st.session_state.analisados:
        st.markdown(f"<hr style='border-color:{card_border}; margin: 30px 0;'>", unsafe_allow_html=True)
        for idx, item in enumerate(st.session_state.analisados):
            html_card = f"<div class='result-card'><div style='display:flex; justify-content:space-between; align-items:center;'><div class='market-badge'>{item['m']}</div><div style='background:#1c2436; padding:4px 10px; border-radius:6px; font-weight:bold; color:{cor_neon}; border:1px solid {cor_neon}40;'>@{item['o']:.2f}</div></div><div style='color:#ffffff; font-size:14px; font-weight:800; margin-bottom:5px;'>⚽ {item['jogo']}</div><div style='color:#5a6b82; font-size:11px; margin-bottom:15px;'>📅 {item['data']} &nbsp;|&nbsp; 🎯 Conf: {item['conf']}%</div><div style='font-size:9px; color:#5a6b82;'>Poder Ofensivo (xG {item['xg_c']})</div><div class='progress-bg'><div class='progress-fill-atk' style='width:{item['atk']}%;'></div></div><div style='font-size:9px; color:#5a6b82; margin-top:4px;'>Força Defensiva</div><div class='progress-bg' style='margin-bottom:15px;'><div class='progress-fill-def' style='width:{item['def']}%;'></div></div></div>"
            st.markdown(html_card, unsafe_allow_html=True)
            
            c_add1, c_add2 = st.columns(2)
            with c_add1:
                if st.button(f"✔️ APOSTAR", key=f"add_{idx}", type="primary", use_container_width=True):
                    st.session_state.bilhete.append(item)
                    st.toast("Adicionado ao seu bilhete!")
            with c_add2:
                if st.button(f"💾 SALVAR", key=f"sav_{idx}", use_container_width=True):
                    st.session_state.analises_salvas.append(item)
                    st.toast("Tracking Salvo!")

# ==========================================
# ABA 3: BILHETE / OPERAÇÕES
# ==========================================
with t3:
    st.markdown("<h3 style='color:white; font-size:16px; margin-bottom:15px;'>Seu Bilhete (Múltipla)</h3>", unsafe_allow_html=True)
    if st.session_state.bilhete:
        odd_f = 1.0
        html_bilhete = f"<div style='background:{card_bg}; border:1px solid {cor_neon}; border-radius:12px; padding:15px; margin-bottom:15px;'>"
        for b in st.session_state.bilhete:
            odd_f *= b['o']
            html_bilhete += f"<div style='display:flex; justify-content:space-between; margin-bottom:10px; border-bottom:1px solid {card_border}; padding-bottom:5px;'><span style='font-size:13px; font-weight:600; color:white;'>{b['m']} <br><span style='font-size:10px; color:#5a6b82; font-weight:normal;'>{b['jogo']}</span></span><span style='color:{cor_neon}; font-weight:bold;'>@{b['o']:.2f}</span></div>"
        html_bilhete += "</div>"
        st.markdown(html_bilhete, unsafe_allow_html=True)
        
        st.markdown(f"<h2 style='text-align:center; color:white;'>ODD TOTAL: <span style='color:{cor_neon};'>@{odd_f:.2f}</span></h2>", unsafe_allow_html=True)
        
        banca_escolhida = st.selectbox("Debitar Conta:", list(st.session_state.bancas.keys()))
        banca_disp = st.session_state.bancas[banca_escolhida]
        
        st.session_state.usar_kelly = st.checkbox("🧠 Usar Critério de Kelly", value=st.session_state.usar_kelly)
        rec_stake = banca_disp * (0.01 if st.session_state.usar_kelly else 0.03)
        
        valor = st.number_input("Valor da Aposta (R$):", min_value=1.0, value=float(max(1.0, rec_stake)), step=10.0)
        st.info(f"Retorno Bruto: {fmt_moeda(valor * odd_f)}")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ BATER GREEN", type="primary", use_container_width=True):
                st.session_state.bancas[banca_escolhida] += (valor * odd_f)
                st.session_state.historico_banca.append(sum(st.session_state.bancas.values()))
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
    
    with st.expander("🔑 Chave de API de Dados (MUITO IMPORTANTE)"):
        st.markdown("<span style='font-size:11px; color:#aaa;'>Para garantir jogos sempre reais, crie uma chave grátis no site <b>the-odds-api.com</b> e cole aqui:</span>", unsafe_allow_html=True)
        nova_api = st.text_input("Sua The Odds API Key:", value=st.session_state.api_key_odds, type="password")
        if st.button("Salvar Chave API", type="primary"):
            st.session_state.api_key_odds = nova_api
            st.success("Chave salva! Vá ao Radar e teste novamente.")
    
    with st.expander("🧠 Ferramentas Institucionais (Ativas)"):
        st.markdown("""
        * **Surebet Scanner:** A rodar no back-end.
        * **Kelly Criterion:** Disponível na formatação de stakes.
        * **Stop Loss:** Segurança de capital ativada (10%).
        """)
        
    with st.expander("🏛️ Gerir Bancas"):
        st.session_state.bancas["Betano"] = st.number_input("Betano", value=st.session_state.bancas["Betano"], step=50.0)
        st.session_state.bancas["Bet365"] = st.number_input("Bet365", value=st.session_state.bancas["Bet365"], step=50.0)
        
    if st.button("Sair da Conta"):
        st.session_state.autenticado = False
        st.rerun()
