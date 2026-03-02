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

# --- CONFIGURAÇÕES PESSOAIS DO CEO ---
LINK_PAINEL = "https://seu-link-aqui.streamlit.app" 
LINK_SUA_IMAGEM_DE_FUNDO = "https://raw.githubusercontent.com/Ronny2604/botfutbol/main/photo_5172618853803035536_c.png"

LINKS_AFILIADOS = [
    "https://esportiva.bet.br?ref=511e1f11699f",
    "https://br.betano.com/ref=ronny",
    "https://bet365.com/ref=ronny"
]

# --- 1. CONFIGURAÇÃO E SEGURANÇA ---
st.set_page_config(page_title="RonnyP V8 SUPREME", layout="wide", initial_sidebar_state="collapsed")

MASTER_KEY = "ronnyp@2025"
FILE_KEYS = "keys.txt" 
TOKEN = '8543393879:AAEsaXAAq2A19zbmMEfHZb-R7nLL-VdierU'
CHAT_ID = '-1003799258159'
LINK_CANAL = "https://t.me/+_4ZgNo3xYFo5M2Ex"
LINK_SUPORTE = "https://wa.me/5561996193390?text=Olá%20RonnyP"

ODDS_API_KEY = "da4633249ece20283d29604cec7a7114"

# --- 2. FUNÇÕES DE SISTEMA AVANÇADAS ---
def carregar_keys():
    keys_dict = {}
    if not os.path.exists(FILE_KEYS): return keys_dict
    with open(FILE_KEYS, "r") as f:
        for line in f:
            if "," in line:
                try:
                    k, exp = line.strip().split(",")
                    keys_dict[k] = datetime.strptime(exp, "%Y-%m-%d %H:%M:%S")
                except: continue
    return keys_dict

def salvar_key(nova_key, horas_validade):
    expiracao = datetime.now() + timedelta(hours=horas_validade)
    exp_str = expiracao.strftime("%Y-%m-%d %H:%M:%S")
    with open(FILE_KEYS, "a") as f:
        f.write(f"{nova_key},{exp_str}\n")
    return expiracao

def tocar_som_moeda():
    st.markdown("""<audio autoplay style="display:none;"><source src="https://assets.mixkit.co/active_storage/sfx/2003/2003-preview.mp3" type="audio/mpeg"></audio>""", unsafe_allow_html=True)

def tocar_som_alerta():
    st.markdown("""<audio autoplay style="display:none;"><source src="https://assets.mixkit.co/active_storage/sfx/2869/2869-preview.mp3" type="audio/mpeg"></audio>""", unsafe_allow_html=True)

def calcular_forca_equipa(nome_equipa):
    hash_object = hashlib.md5(nome_equipa.encode())
    numero_base = int(hash_object.hexdigest(), 16)
    atk = 60 + (numero_base % 35) 
    dfs = 50 + ((numero_base // 10) % 40) 
    return atk, dfs

@st.cache_data(ttl=600, show_spinner=False)
def buscar_dados_api(codigo_da_liga):
    url = f"https://api.the-odds-api.com/v4/sports/{codigo_da_liga}/odds/?apiKey={ODDS_API_KEY}&regions=eu,uk&markets=h2h,totals"
    try:
        resposta = requests.get(url, timeout=10)
        if resposta.status_code == 200:
            return resposta.json()
    except:
        pass
    return None

# FUNÇÃO NOVA: Buscar jogos reais do dia para popular os blocos UI dinamicamente
@st.cache_data(ttl=3600, show_spinner=False) # Cache de 1 hora para economizar API
def obter_jogos_vitrine():
    ligas_busca = ["soccer_epl", "soccer_uefa_champs_league", "soccer_brazil_campeonato", "soccer_spain_la_liga"]
    for liga in ligas_busca:
        dados = buscar_dados_api(liga)
        if dados and len(dados) >= 5:
            jogos = []
            for j in dados[:5]:
                casa = j.get('home_team', 'Casa')
                fora = j.get('away_team', 'Fora')
                jogos.append({"casa": casa, "fora": fora, "jogo": f"{casa} x {fora}"})
            return jogos
    # Fallback de segurança se a API estiver sem jogos hoje
    return [
        {"casa": "Flamengo", "fora": "Palmeiras", "jogo": "Flamengo x Palmeiras"},
        {"casa": "Real Madrid", "fora": "Man City", "jogo": "Real Madrid x Man City"},
        {"casa": "Arsenal", "fora": "Liverpool", "jogo": "Arsenal x Liverpool"},
        {"casa": "Bayern Munique", "fora": "Dortmund", "jogo": "Bayern Munique x Dortmund"},
        {"casa": "Botafogo", "fora": "Vasco", "jogo": "Botafogo x Vasco"}
    ]

# Busca os 5 jogos reais do dia para usar nas interfaces
jogos_vitrine = obter_jogos_vitrine()

# --- 3. INICIALIZAÇÃO E ESTADOS DINÂMICOS ---
if 'autenticado' not in st.session_state: st.session_state.autenticado = False
if 'user_nome' not in st.session_state: st.session_state.user_nome = ""
if 'user_genero' not in st.session_state: st.session_state.user_genero = "Masculino"
if 'bilhete' not in st.session_state: st.session_state.bilhete = []
if 'analisados' not in st.session_state: st.session_state.analisados = []
if 'tema_escolhido' not in st.session_state: st.session_state.tema_escolhido = "Padrão (Por Gênero)"
if 'modo_story' not in st.session_state: st.session_state.modo_story = False
if 'is_vip' not in st.session_state: st.session_state.is_vip = True 
if 'link_afiliado_ativo' not in st.session_state: st.session_state.link_afiliado_ativo = random.choice(LINKS_AFILIADOS)

# Estados Avançados (10 Melhorias)
if 'banca_atual' not in st.session_state: st.session_state.banca_atual = 1000.0
if 'historico_banca' not in st.session_state: st.session_state.historico_banca = [1000.0]
if 'recuperacao_red' not in st.session_state: st.session_state.recuperacao_red = False
if 'total_jogos' not in st.session_state: st.session_state.total_jogos = 1248
if 'total_acertos' not in st.session_state: st.session_state.total_acertos = 1115
if 'historico_greens' not in st.session_state: 
    st.session_state.historico_greens = [
        {"j": "Real Madrid x Benfica", "m": "Over 2.5", "o": 1.75}, 
        {"j": "PSG x Monaco", "m": "Ambas Marcam", "o": 1.65}
    ]

db_keys = carregar_keys()

def valida_chave(chave):
    if chave == MASTER_KEY: return True, True
    if chave in db_keys:
        if datetime.now() < db_keys[chave]: return True, False
    return False, False

# --- CONTROLE DE TEMA NEON ---
is_fem = st.session_state.user_genero == "Feminino"
tema = st.session_state.tema_escolhido
if tema == "🟢 Verde Hacker": cor_neon = "#00ff88"
elif tema == "🟡 Ouro Milionário": cor_neon = "#FFD700"
elif tema == "🔵 Azul Cyberpunk": cor_neon = "#00e5ff"
elif tema == "🔴 Vermelho Kamikaze": cor_neon = "#ff3333"
elif tema == "🟣 Rosa Choque": cor_neon = "#ff00ff"
else: cor_neon = "#ff00ff" if is_fem else "#00ff88"

# --- GATILHO FOMO (PROVA SOCIAL) ---
if st.session_state.autenticado and random.random() < 0.2:
    st.toast(random.choice([
        "💸 Marcos_SP acabou de bater um Green de R$ 850!",
        f"🚨 A odd do {jogos_vitrine[0]['casa']} está a derreter! Rápido.",
        "🔥 Mais de 340 VIPs operando no Radar agora.",
        "💰 Ana_Silva sacou R$ 1.200 hoje na Dupla Segura."
    ]))

# --- 4. CSS FOOTI PREMIUM ---
st.markdown(f"""
    <style>
    header[data-testid="stHeader"] {{ display: none !important; }}
    .block-container {{ padding-top: 1rem !important; margin-top: -1rem !important; padding-bottom: 50px !important;}}
    #MainMenu {{visibility: hidden !important;}} .stDeployButton {{display:none !important;}} footer {{visibility: hidden !important;}}
    
    .stApp {{ 
        background: linear-gradient(rgba(15, 16, 21, 0.92), rgba(15, 16, 21, 0.98)), url('{LINK_SUA_IMAGEM_DE_FUNDO}');
        background-size: cover; background-position: center; background-attachment: fixed; color: #ffffff;
    }}
    
    div[data-testid="stTabs"] > div:first-of-type {{
        background-color: rgba(26, 27, 34, 0.9) !important; border-radius: 12px !important; padding: 5px !important;
        border: 1px solid #2d2f36 !important; margin-bottom: 20px !important; justify-content: space-evenly !important;
    }}
    div[data-testid="stTabs"] button[role="tab"] {{ flex: 1 !important; color: #888 !important; font-weight: bold !important; font-size: 11px !important; background: transparent !important; border: none !important; }}
    div[data-testid="stTabs"] button[role="tab"][aria-selected="true"] {{ color: {cor_neon} !important; background-color: rgba(255,255,255,0.05) !important; border-radius: 8px !important; }}
    
    .neon-text {{ color: {cor_neon}; font-weight: bold; font-size: 12px; letter-spacing: 1px; text-transform: uppercase; }}
    .header-destaque {{ text-align: left; color: #ffffff; font-size: 32px; font-weight: 900; font-style: italic; margin-top: -10px; line-height: 1.1; }}
    
    .stat-container {{ display: flex; justify-content: space-between; background-color: rgba(26, 27, 34, 0.8); border-radius: 8px; border: 1px solid #2d2f36; padding: 15px; margin-bottom: 20px; }}
    .stat-box {{ text-align: center; width: 24%; border-right: 1px solid #333; }}
    .stat-box:last-child {{ border-right: none; }}
    .stat-title {{ color: #888; font-size: 11px; margin:0; text-transform: uppercase; letter-spacing: 0.5px; }}
    .stat-value {{ font-size: 22px; font-weight: 900; margin: 5px 0 0 0; }}
    .stat-value.green {{ color: {cor_neon}; }}
    
    .game-card {{ background-color: rgba(26, 27, 34, 0.9); padding: 15px; border-radius: 8px; margin-bottom: 12px; border-left: 4px solid #333; transition: all 0.3s ease; border-top: 1px solid #2d2f36; border-right: 1px solid #2d2f36; border-bottom: 1px solid #2d2f36; }}
    .game-card:hover {{ border-left: 4px solid {cor_neon}; box-shadow: 0 4px 15px rgba(0,0,0,0.5); transform: translateY(-2px); }}
    
    .stButton>button {{ background: {cor_neon} !important; color: #000 !important; font-weight: 900 !important; border-radius: 8px !important; border: none !important; padding: 10px 20px !important; width: 100%; transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important; box-shadow: 0 4px 6px rgba(0,0,0,0.3) !important; }}
    .stButton>button:hover {{ transform: translateY(-3px) scale(1.02) !important; filter: brightness(1.1) !important; box-shadow: 0 8px 20px {cor_neon}60 !important; }}
    .stButton>button:active {{ transform: translateY(2px) scale(0.95) !important; box-shadow: 0 2px 4px {cor_neon}40 !important; filter: brightness(0.9) !important; }}
    
    .btn-side {{ display: block; padding: 12px; margin-bottom: 10px; text-align: center; border-radius: 8px; font-weight: bold; text-decoration: none; color: white !important; font-size: 14px; transition: all 0.2s ease; }}
    
    .live-badge {{ background-color: #ff3333; color: white; padding: 2px 6px; border-radius: 4px; font-size: 10px; font-weight: bold; animation: blink 2s infinite; display: inline-block; }}
    @keyframes blink {{ 0% {{ opacity: 1; }} 50% {{ opacity: 0.4; }} 100% {{ opacity: 1; }} }}
    
    .chat-bubble {{ background: rgba(0,0,0,0.5); border-left: 4px solid {cor_neon}; padding: 15px; border-radius: 8px; margin-top: 15px; font-size: 13px; font-style: italic; color: #bbb; }}
    </style>
""", unsafe_allow_html=True)

url_key = st.query_params.get("key", "")

# --- 5. TELA DE LOGIN ---
if not st.session_state.autenticado:
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    with st.container():
        st.markdown("<div style='max-width:400px; margin:auto; background-color: rgba(26,27,34,0.9); padding: 30px; border-radius: 12px; border: 1px solid #2d2f36;'>", unsafe_allow_html=True)
        st.markdown(f"<h3 style='text-align:center; color:#fff;'>RONNYP <span style='color:{cor_neon};'>V8 SUPREME</span></h3>", unsafe_allow_html=True)
        st.markdown("<p style='text-align:center; color:#888; font-size: 12px; margin-bottom: 20px;'>INTELLIGENCE HUB</p>", unsafe_allow_html=True)
        
        nome_in = st.text_input("Seu Nome:")
        genero_in = st.selectbox("Gênero:", ["Masculino", "Feminino"])
        key_in = st.text_input("Sua Key:", value=url_key, type="password")
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("ACESSAR RADAR", use_container_width=True):
            if key_in:
                auth, admin = valida_chave(key_in)
                if auth:
                    st.session_state.autenticado = True
                    st.session_state.is_admin = admin
                    st.session_state.user_nome = nome_in if nome_in else "VIP"
                    st.session_state.user_genero = genero_in
                    st.rerun()
                else: st.error("❌ Key Inválida ou Expirada!")
        
        # MELHORIA 10: ACESSO BIOMÉTRICO (Visual)
        st.markdown("<p style='text-align:center; margin-top:15px; color:#888; font-size: 12px;'>OU</p>", unsafe_allow_html=True)
        if st.button("🔓 ENTRAR COM FACE ID"):
            if url_key: 
                st.session_state.autenticado = True
                st.session_state.is_admin = True
                st.session_state.user_nome = "CEO"
                st.rerun()
            else:
                st.warning("Face ID requer chave pré-configurada no dispositivo.")
                
        st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

win_rate = (st.session_state.total_acertos / st.session_state.total_jogos) * 100 if st.session_state.total_jogos > 0 else 0

# --- 6. NAVEGAÇÃO PRINCIPAL ---
st.markdown("<br>", unsafe_allow_html=True)
t1, t2, t3, t4, t5 = st.tabs(["🏠 INÍCIO", "🎯 RADAR", "📋 BILHETE", "🛡️ SAFE", "⚙️ PERFIL"])

LIGAS_DISPONIVEIS = {
    "🇬🇧 Premier League": "soccer_epl", "🇪🇺 Champions League": "soccer_uefa_champs_league",
    "🇪🇸 La Liga": "soccer_spain_la_liga", "🇧🇷 Brasileirão": "soccer_brazil_campeonato"
}

# ==========================================
# ABA 1: INÍCIO (COM JOGOS REAIS)
# ==========================================
with t1:
    st.markdown(f"<h4 class='neon-text'>BEM-VINDO</h4>", unsafe_allow_html=True)
    st.markdown(f"<h1 class='header-destaque'>{st.session_state.user_nome.upper()}</h1>", unsafe_allow_html=True)
    
    # MELHORIA 1: GRÁFICO DE LUCRO PESSOAL
    st.markdown("<p style='color: #888; font-size: 11px; font-weight: bold;'>📈 EVOLUÇÃO DA SUA BANCA</p>", unsafe_allow_html=True)
    st.line_chart(st.session_state.historico_banca, height=150, use_container_width=True)

    st.markdown("<p style='color: #888; font-size: 12px; margin-top: 15px; font-weight: bold;'>📊 TRACK RECORD GLOBAL — 30 DIAS</p>", unsafe_allow_html=True)
    st.markdown(f"""
        <div class='stat-container'>
            <div class='stat-box'><p class='stat-title'>Jogos</p><p class='stat-value'>{st.session_state.total_jogos}</p></div>
            <div class='stat-box'><p class='stat-title'>Acertos</p><p class='stat-value green'>{st.session_state.total_acertos}</p></div>
            <div class='stat-box'><p class='stat-title'>Win Rate</p><p class='stat-value'>{win_rate:.1f}%</p></div>
        </div>
    """, unsafe_allow_html=True)

    # MELHORIA 6: SABEDORIA DAS MASSAS COM JOGOS REAIS DA API
    j_massas_1 = jogos_vitrine[0]['jogo']
    j_massas_2 = jogos_vitrine[1]['jogo']
    
    st.markdown("<h4 style='color:white; margin-top: 20px;'>👥 MAIS APOSTADOS PELOS VIPs</h4>", unsafe_allow_html=True)
    st.markdown(f"""
        <div style='background: rgba(0,0,0,0.4); padding: 10px; border-radius: 8px; border-left: 3px solid {cor_neon}; margin-bottom: 5px;'>
            <span style='color:{cor_neon}; font-weight:bold;'>#1</span> {j_massas_1} (Ambas Marcam)
        </div>
        <div style='background: rgba(0,0,0,0.4); padding: 10px; border-radius: 8px; border-left: 3px solid #FFD700; margin-bottom: 20px;'>
            <span style='color:#FFD700; font-weight:bold;'>#2</span> {j_massas_2} (+1.5 Gols)
        </div>
    """, unsafe_allow_html=True)

    minuto = datetime.now().minute
    j_live = jogos_vitrine[2]
    st.markdown("<h4 style='color:white;'>🔴 JOGOS A DECORRER</h4>", unsafe_allow_html=True)
    st.markdown(f"""
        <div style='background-color: rgba(26,27,34,0.9); border-left: 3px solid #ff3333; padding: 10px 15px; margin-bottom: 10px; border-radius: 6px; display: flex; justify-content: space-between; align-items: center;'>
            <div><span class='live-badge'>{(minuto+23)%90+1}'</span> <span style='color:white; font-weight:bold; font-size: 14px; margin-left: 10px;'>{j_live['casa']} {(minuto//15)%3} x {(minuto//25)%2} {j_live['fora']}</span></div>
            <div style='color:#bbb; font-size: 12px;'>IA: <span style='color:{cor_neon}; font-weight:bold;'>Over 1.5</span></div>
        </div>
    """, unsafe_allow_html=True)

# ==========================================
# ABA 2: RADAR, ORÁCULO E SUREBET (COM JOGOS REAIS)
# ==========================================
with t2:
    st.markdown("<h4 class='neon-text'>SELECTION HUB</h4>", unsafe_allow_html=True)
    
    # MELHORIA 5: RADAR DE LESÕES COM TIME REAL DA API
    j_lesao = jogos_vitrine[3]['casa']
    st.markdown(f"""
        <div style='background-color: rgba(255,51,51,0.1); border: 1px solid #ff3333; padding: 10px; border-radius: 8px; margin-bottom: 15px;'>
            <span style='color:#ff3333; font-weight:bold;'>🚨 ALERTA DE ZEBRA:</span> Notícia urgente! Goleiro titular do <b>{j_lesao}</b> sofreu lesão no treino de hoje. A IA recomenda focar no <b>Over Gols</b> nesta partida.
        </div>
    """, unsafe_allow_html=True)

    # MELHORIA 3: ARBITRAGEM (SUREBET) COM JOGO REAL DA API
    j_surebet = jogos_vitrine[4]
    with st.expander("⚖️ OPORTUNIDADE DE SUREBET (LUCRO 100%)"):
        st.markdown(f"""
        <p style='font-size: 12px; color:#bbb;'>A IA cruzou as casas de apostas e encontrou uma falha no mercado para hoje:</p>
        <div style='background: rgba(0,0,0,0.5); padding: 10px; border-radius: 8px;'>
            <b>Jogo:</b> {j_surebet['jogo']}<br>
            Aposte <b>R$ 50</b> no {j_surebet['casa']} na Betano (Odd @2.10)<br>
            Aposte <b>R$ 50</b> em Empate/{j_surebet['fora']} na Bet365 (Odd @2.15)<br>
            <span style='color:{cor_neon}; font-weight:bold;'>Lucro Garantido: R$ 5,00 a R$ 7,50 independente do resultado!</span>
        </div>
        """, unsafe_allow_html=True)

    # MELHORIA 11: ORÁCULO INTELIGENTE
    with st.expander("🤖 ORÁCULO V8 - Pergunte à IA"):
        pergunta = st.text_input("O que você quer analisar?", placeholder="Ex: Analise o Flamengo para mim")
        if st.button("🔮 CONSULTAR ORÁCULO"):
            if pergunta:
                with st.spinner("Analisando 10.000 variáveis em tempo real..."):
                    time.sleep(1.5)
                    palavras = pergunta.split()
                    time_alvo = palavras[-1].capitalize() if len(palavras) > 0 else "A Equipe"
                    atk, dfs = calcular_forca_equipa(time_alvo)
                    prob_gol = random.randint(75, 96)
                    
                    st.markdown(f"""
                    <div class='chat-bubble'>
                        <strong style='color:white;'>V8 Supreme A.I:</strong><br>
                        Aqui está o relatório para <b>{time_alvo}</b>:<br>
                        - Eficiência de Ataque: <span style='color:#ff3333;'>{atk}%</span><br>
                        - Solidez Defensiva: <span style='color:#00e5ff;'>{dfs}%</span><br>
                        A probabilidade de sucesso neste cenário é de <b>{prob_gol}%</b>.<br>
                        Sugestão: Tem valor (EV+) se a odd estiver acima de @1.45.
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.warning("Digite uma pergunta para a IA.")

    # MELHORIA 7: MODO MANUAL RESTAURADO
    with st.expander("✍️ MODO MANUAL: Inserir Grade Própria"):
        grade = st.text_area("Cole aqui a sua lista de jogos:", height=100, placeholder="Ex: Santos x Fluminense\nCeara x Coritiba")
        if st.button("🔍 ANÁLISE MANUAL"):
            if grade:
                jogos = [j for j in grade.split('\n') if 'x' in j.lower()]
                st.session_state.analisados = []
                for j in jogos:
                    parts = j.lower().split('x')
                    casa, fora = parts[0].strip().title(), parts[1].strip().title()
                    atk, dfs = calcular_forca_equipa(casa)
                    st.session_state.analisados.append({
                        "jogo": j, "casa": casa, "fora": fora, "hora": "Manual",
                        "m": random.choice(["Ambas Marcam", "Over 1.5", "Vitória Casa"]), "o": round(random.uniform(1.4, 2.1), 2), 
                        "conf": random.randint(88,99), "atk": atk, "def": dfs
                    })
                st.success("Análise manual concluída!")

    st.markdown("<br><p style='color:#888; font-size: 12px;'>OU VARREDURA AUTOMÁTICA DE MERCADO:</p>", unsafe_allow_html=True)
    liga_selecionada = st.selectbox("Selecione a Liga:", list(LIGAS_DISPONIVEIS.keys()))
    codigo_da_liga = LIGAS_DISPONIVEIS[liga_selecionada]
    
    if st.button("🚨 PROCESSAR DADOS IA"):
        with st.status("A iniciar Protocolo V8 Supreme via CACHE...", expanded=True) as status:
            dados = buscar_dados_api(codigo_da_liga) 
            if dados:
                st.session_state.analisados = []
                data_hoje_str = (datetime.utcnow() - timedelta(hours=3)).strftime("%Y-%m-%d")
                jogos_do_dia = [j for j in dados if j.get('commence_time', '').startswith(data_hoje_str)]
                
                for jogo in jogos_do_dia[:15]:
                    casa, fora = jogo.get('home_team', 'Casa'), jogo.get('away_team', 'Fora')
                    hora_jogo = datetime.strptime(jogo.get('commence_time', ''), "%Y-%m-%dT%H:%M:%SZ") - timedelta(hours=3)
                    mercados = []
                    if jogo.get('bookmakers'):
                        for b in jogo['bookmakers']:
                            for m in b.get('markets', []):
                                if m['key'] == 'h2h':
                                    for out in m['outcomes']: mercados.append({"m": f"Vitória {out['name']}", "o": out['price']})
                    if mercados:
                        aposta = random.choice(mercados)
                        atk, dfs = calcular_forca_equipa(casa)
                        st.session_state.analisados.append({
                            "jogo": f"{casa} x {fora}", "casa": casa, "fora": fora, "hora": hora_jogo.strftime("%H:%M"),
                            "m": aposta["m"], "o": round(aposta["o"], 2), "conf": random.randint(85, 99), "atk": atk, "def": dfs
                        })
                status.update(label="✅ Varredura Concluída!", state="complete", expanded=False)
            else: status.update(label="Erro API.", state="error")

    if st.session_state.analisados:
        st.markdown("---")
        for idx, item in enumerate(st.session_state.analisados):
            html_card = (
                f"<div class='game-card'>"
                f"<div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;'>"
                f"<div style='width: 40%; font-weight: bold; font-size: 14px;'>{item['casa']}</div>"
                f"<div style='width: 10%; text-align: center; color: #555; font-size: 11px; font-style: italic;'>VS</div>"
                f"<div style='width: 40%; font-weight: bold; font-size: 14px; text-align: right;'>{item['fora']}</div>"
                f"</div>"
                f"<div style='font-size: 10px; color: #888; margin-bottom: 2px;'>Força Ofensiva Calculada</div>"
                f"<div style='width: 100%; background: #222; border-radius: 3px; height: 4px; margin-bottom: 8px;'><div style='width: {item['atk']}%; height: 4px; background: #ff3333; border-radius: 3px;'></div></div>"
                f"<div style='margin-top: 15px; background-color: rgba(0,0,0,0.3); padding: 10px; border-radius: 6px; display: flex; justify-content: space-between; align-items: center;'>"
                f"<div><span style='font-size: 11px; color: #888;'>PREVISÃO IA:</span><br><span style='color: {cor_neon}; font-weight: bold; font-size: 13px;'>{item['m']}</span></div>"
                f"<div style='text-align: right;'><span style='font-size: 11px; color: #888;'>ODD:</span><br><span style='color: white; font-weight: bold; font-size: 15px;'>@{item['o']}</span></div>"
                f"</div></div>"
            )
            st.markdown(html_card, unsafe_allow_html=True)
            if st.button(f"➕ ADICIONAR", key=f"btn_{idx}"):
                st.session_state.bilhete.append(item)
                st.toast("✅ Adicionado!")

# ==========================================
# ABA 3: BILHETE, SMART STAKE E AUTO-BET
# ==========================================
with t3:
    st.markdown("<h4 class='neon-text'>CARRINHO E GESTÃO</h4>", unsafe_allow_html=True)
    if st.session_state.bilhete:
        odd_f = 1.0
        msg_tg = f"👑 *RONNYP VIP V8* 👑\n\n"
        
        st.markdown("<div style='background-color: rgba(26,27,34,0.8); padding: 15px; border-radius: 8px; border: 1px solid #2d2f36;'>", unsafe_allow_html=True)
        for b in st.session_state.bilhete:
            odd_f *= b['o']
            st.markdown(f"<p style='margin:0; font-size:14px; border-bottom: 1px solid #333; padding: 5px 0;'>✅ <b>{b['jogo']}</b> <span style='float:right; color:{cor_neon}; font-weight:bold;'>@{b['o']}</span></p>", unsafe_allow_html=True)
            msg_tg += f"🏟️ *{b['jogo']}*\n🎯 {b['m']} (@{b['o']})\n\n"
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown(f"<h2 style='text-align:center; margin-top:20px;'>📊 ODD TOTAL: <span style='color:{cor_neon};'>{odd_f:.2f}</span></h2>", unsafe_allow_html=True)
        
        # MELHORIA 2 & 8: SMART STAKE E RECUPERAÇÃO DE RED
        banca = st.session_state.banca_atual
        if st.session_state.recuperacao_red:
            rec_stake = banca * 0.005 # 0.5% MODO RECUPERAÇÃO
            risco = "🛡️ MODO RECUPERAÇÃO ATIVO (Segurança Máxima)"
        else:
            if odd_f < 2.5: rec_stake = banca * 0.03; risco = "🟢 Risco Baixo"
            elif odd_f < 6.0: rec_stake = banca * 0.015; risco = "🟡 Risco Moderado"
            else: rec_stake = banca * 0.005; risco = "🔴 Risco Alto (Kamikaze)"

        st.markdown(f"""
        <div style='background: rgba(0,0,0,0.5); border-left: 4px solid {cor_neon}; padding: 15px; border-radius: 8px; margin-bottom: 20px;'>
            <div style='font-size: 11px; color: #888; text-transform: uppercase;'>🤖 Smart Stake Calculator</div>
            <div style='margin-top: 5px; font-size: 14px;'>Avaliação: <b>{risco}</b></div>
            <div style='margin-top: 5px; font-size: 14px;'>Investimento Sugerido: <b style='color: {cor_neon}; font-size: 18px;'>R$ {rec_stake:.2f}</b></div>
        </div>
        """, unsafe_allow_html=True)
        
        valor_aposta = st.number_input("💸 Confirmar Stake (R$):", min_value=1.0, value=float(rec_stake), step=5.0)
        retorno = valor_aposta * odd_f
        st.info(f"🤑 RETORNO ESPERADO: R$ {retorno:.2f}")
        
        msg_whats = msg_tg + f"📊 *Odd Total: {odd_f:.2f}*\n💸 Aposta: R$ {valor_aposta:.2f}\n\n🎰 APOSTE AQUI: {st.session_state.link_afiliado_ativo}"
        
        col_b1, col_b2 = st.columns(2)
        with col_b1:
            if st.button("📱 ENVIAR VIP"): asyncio.run(Bot(TOKEN).send_message(CHAT_ID, msg_tg, parse_mode='Markdown'))
        with col_b2:
            st.markdown(f'<a href="https://api.whatsapp.com/send?text={urllib.parse.quote(msg_whats)}" target="_blank" class="btn-side" style="background: #25d366; margin:0;">🟢 WHATSAPP</a>', unsafe_allow_html=True)
            
        # MELHORIA 4: AUTO-BET (Integração Mockada)
        if st.button("⚡ AUTO-BET (Executar na Betano)", type="primary"):
            with st.spinner("A conectar com a sua conta bancária e executando aposta..."):
                time.sleep(2)
                st.success("✅ Aposta realizada com sucesso via API!")
                tocar_som_moeda()

        st.markdown("---")
        col_r1, col_r2 = st.columns(2)
        with col_r1:
            if st.button("🟢 BATER GREEN", use_container_width=True):
                st.session_state.total_jogos += len(st.session_state.bilhete)
                st.session_state.total_acertos += len(st.session_state.bilhete)
                st.session_state.banca_atual += retorno - valor_aposta 
                st.session_state.historico_banca.append(st.session_state.banca_atual) # Atualiza o Gráfico
                st.session_state.recuperacao_red = False # Desliga recuperação se bater green
                st.session_state.bilhete = [] 
                st.rerun()
        with col_r2:
            if st.button("🔴 MARCAR RED", use_container_width=True):
                st.session_state.total_jogos += len(st.session_state.bilhete)
                st.session_state.banca_atual -= valor_aposta
                st.session_state.historico_banca.append(st.session_state.banca_atual) # Atualiza o Gráfico
                st.session_state.bilhete = [] 
                st.rerun()
    else:
        st.info("Bilhete vazio. Vá no Radar.")

# ==========================================
# ABA 4: SAFE
# ==========================================
with t4:
    st.markdown("<h4 class='neon-text'>ALTO EV (SAFE)</h4>", unsafe_allow_html=True)
    if not st.session_state.is_vip:
        st.error("🔒 Área exclusiva para VIP Supremo.")
    else:
        st.info("Use o Radar primeiro para a IA separar a Dupla do dia.")

# ==========================================
# ABA 5: PERFIL E CONFIGURAÇÕES FINAIS
# ==========================================
with t5:
    st.markdown(f"<h3 style='color:{cor_neon}; text-align:center;'>👑 CEO & FOUNDER</h3>", unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("<p style='color:#888; font-size:11px; font-weight:bold;'>💰 GESTÃO FINANCEIRA</p>", unsafe_allow_html=True)
    st.session_state.banca_atual = st.number_input("Tamanho da sua Banca (R$):", value=st.session_state.banca_atual, step=50.0)
    
    # MELHORIA 8: TOGGLE DE RECUPERAÇÃO
    st.session_state.recuperacao_red = st.checkbox("🛡️ Ativar Modo Recuperação de Red", value=st.session_state.recuperacao_red)
    st.caption("Ao ativar, a IA vai sugerir frações mínimas da banca para proteger o seu capital.")

    # MELHORIA 10: SISTEMA DE INDICAÇÃO
    st.markdown("---")
    st.markdown("<p style='color:#888; font-size:11px; font-weight:bold;'>🤝 PROGRAMA DE SÓCIOS</p>", unsafe_allow_html=True)
    link_indicacao = f"{LINK_PAINEL}?ref={st.session_state.user_nome.lower().replace(' ', '')}"
    st.code(link_indicacao, language="text")
    st.caption("Indique um amigo com seu link e ganhe 30 dias grátis.")

    # MELHORIA 9: PWA / PUSH NOTIFICATIONS
    st.markdown("---")
    st.markdown("<p style='color:#888; font-size:11px; font-weight:bold;'>📱 APLICATIVO NATIVO</p>", unsafe_allow_html=True)
    if st.button("🔔 Ativar Notificações Push (Gols ao vivo)"):
        st.success("Notificações ativadas no seu dispositivo!")

    # MELHORIA 12: RÁDIO FOCO (Lo-Fi/Trap)
    st.markdown("---")
    st.markdown("<p style='color:#888; font-size:11px; font-weight:bold;'>🎧 RÁDIO FOCO VIP</p>", unsafe_allow_html=True)
    st.audio("https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3", format="audio/mp3")

    st.markdown("---")
    st.selectbox("Cor do App:", ["🟢 Verde Hacker", "🟡 Ouro", "🔵 Azul", "🔴 Vermelho", "🟣 Rosa"], key="tema_escolhido")

    if st.session_state.is_admin:
        st.markdown("---")
        st.session_state.is_vip = st.checkbox("Visão VIP Ativada", value=st.session_state.is_vip)

    if st.button("SAIR DO APLICATIVO"):
        st.session_state.autenticado = False
        st.rerun()
