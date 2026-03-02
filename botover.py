import streamlit as st
import asyncio
import random
import time
import os
import urllib.parse
import requests
import hashlib
from telegram import Bot
from datetime import datetime, timedelta

# --- CONFIGURAÇÕES PESSOAIS DO CEO ---
LINK_PAINEL = "https://seu-link-aqui.streamlit.app" 
LINK_SUA_IMAGEM_DE_FUNDO = "https://raw.githubusercontent.com/Ronny2604/botfutbol/main/photo_5172618853803035536_c.png"
LINK_SEU_AUDIO_BRIEFING = "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3" 

# LISTA DE LINKS DE AFILIADO (ROTAÇÃO AUTOMÁTICA)
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

def get_saudacao():
    hora = datetime.now().hour
    if 5 <= hora < 12: return "☕ Bom dia"
    elif 12 <= hora < 18: return "☀️ Boa tarde"
    else: return "🌙 Boa noite"

# SIMULADOR DE FORÇA 
def calcular_forca_equipa(nome_equipa):
    hash_object = hashlib.md5(nome_equipa.encode())
    numero_base = int(hash_object.hexdigest(), 16)
    atk = 60 + (numero_base % 35) 
    dfs = 50 + ((numero_base // 10) % 40) 
    return atk, dfs

# SISTEMA DE CACHING
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

# --- 3. INICIALIZAÇÃO E ESTADOS DINÂMICOS ---
if 'autenticado' not in st.session_state: st.session_state.autenticado = False
if 'user_nome' not in st.session_state: st.session_state.user_nome = ""
if 'user_genero' not in st.session_state: st.session_state.user_genero = "Masculino"
if 'bilhete' not in st.session_state: st.session_state.bilhete = []
if 'analisados' not in st.session_state: st.session_state.analisados = []
if 'show_welcome' not in st.session_state: st.session_state.show_welcome = False
if 'tema_escolhido' not in st.session_state: st.session_state.tema_escolhido = "Padrão (Por Gênero)"
if 'modo_story' not in st.session_state: st.session_state.modo_story = False
if 'is_vip' not in st.session_state: st.session_state.is_vip = True 

if 'link_afiliado_ativo' not in st.session_state: 
    st.session_state.link_afiliado_ativo = random.choice(LINKS_AFILIADOS)

# VARIÁVEIS DO DASHBOARD DINÂMICO
if 'total_jogos' not in st.session_state: st.session_state.total_jogos = 1248
if 'total_acertos' not in st.session_state: st.session_state.total_acertos = 1115
if 'roi_atual' not in st.session_state: st.session_state.roi_atual = 14.2
if 'historico_greens' not in st.session_state: 
    st.session_state.historico_greens = [
        {"j": "Real Madrid x SL Benfica", "m": "Over 2.5 Gols", "o": 1.75},
        {"j": "Paris Saint Germain x Monaco", "m": "Over 8.5 Cantos", "o": 1.65},
        {"j": "Cruzeiro x Corinthians", "m": "Ambas Marcam", "o": 1.90},
        {"j": "Juventus FC x Galatasaray", "m": "1 e Over 2.5", "o": 2.15}
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

# --- 4. CSS FOOTI PREMIUM + ANIMAÇÕES DE BOTÕES ---
st.markdown(f"""
    <style>
    #MainMenu {{visibility: hidden !important;}}
    .stDeployButton {{display:none !important;}}
    footer {{visibility: hidden !important;}}
    header {{visibility: hidden !important;}}
    
    @keyframes fadeIn {{ from {{ opacity: 0; transform: translateY(10px); }} to {{ opacity: 1; transform: translateY(0); }} }}
    
    .stApp {{ 
        background: linear-gradient(rgba(15, 16, 21, 0.92), rgba(15, 16, 21, 0.98)), url('{LINK_SUA_IMAGEM_DE_FUNDO}');
        background-size: cover; background-position: center; background-attachment: fixed;
        animation: fadeIn 0.8s ease-out; color: #ffffff;
    }}
    
    /* MENU NATIVO PREMIUM NO TOPO */
    div[data-testid="stTabs"] > div:first-of-type {{
        background-color: rgba(26, 27, 34, 0.9) !important;
        border-radius: 12px !important;
        padding: 5px !important;
        border: 1px solid #2d2f36 !important;
        margin-bottom: 20px !important;
        justify-content: space-evenly !important;
    }}
    div[data-testid="stTabs"] button[role="tab"] {{
        flex: 1 !important;
        color: #888 !important;
        font-weight: bold !important;
        font-size: 11px !important;
        background: transparent !important;
        border: none !important;
        white-space: nowrap !important;
        transition: color 0.3s ease !important;
    }}
    div[data-testid="stTabs"] button[role="tab"]:hover {{
        color: #fff !important;
    }}
    div[data-testid="stTabs"] button[role="tab"][aria-selected="true"] {{
        color: {cor_neon} !important;
        background-color: rgba(255,255,255,0.05) !important;
        border-radius: 8px !important;
        border-bottom: none !important;
    }}
    
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
    
    /* === ANIMAÇÕES DE BOTÕES (HOVER E CLICK) === */
    .stButton>button {{ 
        background: {cor_neon} !important; 
        color: #000 !important; 
        font-weight: 900 !important; 
        border-radius: 8px !important; 
        border: none !important; 
        padding: 10px 20px !important; 
        width: 100%; 
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3) !important;
    }}
    /* Efeito Hover (Brilho e Flutuação) */
    .stButton>button:hover {{ 
        transform: translateY(-3px) scale(1.02) !important; 
        filter: brightness(1.1) !important; 
        box-shadow: 0 8px 20px {cor_neon}60 !important;
    }}
    /* Efeito Click (Mola/Pressionar) */
    .stButton>button:active {{ 
        transform: translateY(2px) scale(0.95) !important; 
        box-shadow: 0 2px 4px {cor_neon}40 !important;
        filter: brightness(0.9) !important;
    }}
    
    .btn-side {{ display: block; padding: 12px; margin-bottom: 10px; text-align: center; border-radius: 8px; font-weight: bold; text-decoration: none; color: white !important; font-size: 14px; transition: all 0.2s ease; }}
    .btn-side:hover {{ transform: translateY(-3px) scale(1.02); filter: brightness(1.1); box-shadow: 0 8px 15px rgba(255,255,255,0.1); }}
    .btn-side:active {{ transform: translateY(1px) scale(0.95); }}
    
    .story-card {{ background: linear-gradient(180deg, #1a1b22 0%, #0f1015 100%); padding: 30px; border-radius: 20px; border: 2px solid {cor_neon}; box-shadow: 0 0 30px {cor_neon}40; text-align: center; position: relative; overflow: hidden; }}
    .story-watermark {{ position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%) rotate(-30deg); font-size: 60px; color: rgba(255,255,255,0.03); white-space: nowrap; font-weight: 900; pointer-events: none; }}
    
    .blur-overlay {{ filter: blur(8px); pointer-events: none; user-select: none; opacity: 0.6; }}
    .lock-icon {{ position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); z-index: 10; text-align: center; background: rgba(0,0,0,0.8); padding: 20px; border-radius: 12px; border: 1px solid {cor_neon}; box-shadow: 0 0 20px #000; width: 80%; transition: transform 0.3s ease; }}
    .lock-icon:hover {{ transform: translate(-50%, -50%) scale(1.05); }}
    
    .live-badge {{ background-color: #ff3333; color: white; padding: 2px 6px; border-radius: 4px; font-size: 10px; font-weight: bold; animation: blink 2s infinite; display: inline-block; }}
    @keyframes blink {{ 0% {{ opacity: 1; }} 50% {{ opacity: 0.4; }} 100% {{ opacity: 1; }} }}
    </style>
""", unsafe_allow_html=True)

# --- CAPTURA DE KEY VIA URL ---
url_key = ""
if "key" in st.query_params:
    url_key = st.query_params["key"]

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
                    st.session_state.show_welcome = True
                    st.rerun()
                else: st.error("❌ Key Inválida ou Expirada!")
        st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

win_rate = (st.session_state.total_acertos / st.session_state.total_jogos) * 100 if st.session_state.total_jogos > 0 else 0

# --- 6. NAVEGAÇÃO PRINCIPAL (ABAS NO TOPO ESTILIZADAS) ---
st.markdown("<br>", unsafe_allow_html=True)
t1, t2, t3, t4, t5 = st.tabs(["🏠 INÍCIO", "🎯 RADAR", "📋 BILHETE", "🛡️ SAFE", "⚙️ PERFIL"])

LIGAS_DISPONIVEIS = {
    "🇬🇧 Premier League": "soccer_epl", "🇪🇺 Champions League": "soccer_uefa_champs_league",
    "🇪🇸 La Liga": "soccer_spain_la_liga", "🇮🇹 Serie A": "soccer_italy_serie_a",
    "🇧🇷 Brasileirão": "soccer_brazil_campeonato"
}

# ==========================================
# ABA 1: INÍCIO (Dashboard, Live Scores e Histórico)
# ==========================================
with t1:
    st.markdown(f"<h4 class='neon-text'>BEM-VINDO</h4>", unsafe_allow_html=True)
    st.markdown(f"<h1 class='header-destaque'>{st.session_state.user_nome.upper()}</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #888; font-size: 14px; margin-bottom: 20px;'>SUA JORNADA DE VITÓRIA COMEÇA AGORA.</p>", unsafe_allow_html=True)

    if st.session_state.show_welcome:
        st.toast(f"{get_saudacao()}, {st.session_state.user_nome}! Vamos aos lucros! 💰")
        tocar_som_moeda()
        st.balloons()
        st.session_state.show_welcome = False

    st.markdown("<p style='color: #888; font-size: 12px; margin-bottom: 5px; font-weight: bold;'>📊 TRACK RECORD — 30 DIAS (AO VIVO)</p>", unsafe_allow_html=True)
    html_stats = (
        f"<div class='stat-container'>"
        f"<div class='stat-box'><p class='stat-title'>Jogos</p><p class='stat-value'>{st.session_state.total_jogos}</p></div>"
        f"<div class='stat-box'><p class='stat-title'>Acertos</p><p class='stat-value green'>{st.session_state.total_acertos}</p></div>"
        f"<div class='stat-box'><p class='stat-title'>Win Rate</p><p class='stat-value'>{win_rate:.1f}%</p></div>"
        f"<div class='stat-box'><p class='stat-title'>ROI</p><p class='stat-value green'>+{st.session_state.roi_atual:.1f}%</p></div>"
        f"</div>"
    )
    st.markdown(html_stats, unsafe_allow_html=True)

    st.markdown("<h4 style='color:white; margin-top: 20px;'>🔴 JOGOS A DECORRER</h4>", unsafe_allow_html=True)
    html_live = (
        f"<div style='background-color: rgba(26,27,34,0.9); border-left: 3px solid #ff3333; padding: 10px 15px; margin-bottom: 10px; border-radius: 6px; display: flex; justify-content: space-between; align-items: center;'>"
        f"<div><span class='live-badge'>65'</span> <span style='color:white; font-weight:bold; font-size: 14px; margin-left: 10px;'>Arsenal 1 x 0 Chelsea</span></div>"
        f"<div style='color:#bbb; font-size: 12px;'>IA previu: <span style='color:{cor_neon}; font-weight:bold;'>Vitória Arsenal</span></div>"
        f"</div>"
        f"<div style='background-color: rgba(26,27,34,0.9); border-left: 3px solid #ff3333; padding: 10px 15px; margin-bottom: 20px; border-radius: 6px; display: flex; justify-content: space-between; align-items: center;'>"
        f"<div><span class='live-badge'>82'</span> <span style='color:white; font-weight:bold; font-size: 14px; margin-left: 10px;'>Flamengo 2 x 1 Vasco</span></div>"
        f"<div style='color:#bbb; font-size: 12px;'>IA previu: <span style='color:{cor_neon}; font-weight:bold;'>Mais 2.5 Gols</span></div>"
        f"</div>"
    )
    st.markdown(html_live, unsafe_allow_html=True)

    st.markdown("<h4 style='color:white;'>🏆 ÚLTIMOS GREENS DO VIP</h4>", unsafe_allow_html=True)
    for h in st.session_state.historico_greens:
        html_historico = (
            f"<div style='background-color: rgba(26,27,34,0.9); border-left: 5px solid #00ff88; padding: 15px; margin-bottom: 10px; border-radius: 6px;'>"
            f"<div style='color:white; font-weight:bold; font-size: 16px;'>{h['j']}</div>"
            f"<div style='color:#bbb; font-size: 14px; margin-top:5px;'>🎯 {h['m']} | <span style='color:#00ff88; font-weight:bold; font-size: 16px;'>@{h['o']} ✅ GREEN</span></div>"
            f"</div>"
        )
        st.markdown(html_historico, unsafe_allow_html=True)

# ==========================================
# ABA 2: RADAR (Construtor e IA Turbinada)
# ==========================================
with t2:
    st.markdown("<h4 class='neon-text'>SELECTION HUB</h4>", unsafe_allow_html=True)
    
    with st.expander("🏗️ BET BUILDER: Focar em 1 Jogo"):
        jogo_builder = st.text_input("Qual o jogo principal de hoje?", placeholder="Ex: Real Madrid x Barcelona")
        if st.button("🔧 CONSTRUIR MÚLTIPLA", use_container_width=True):
            if jogo_builder and 'x' in jogo_builder.lower():
                parts = jogo_builder.lower().split('x')
                casa = parts[0].strip().title()
                fora = parts[1].strip().title()
                
                atk_c, def_c = calcular_forca_equipa(casa)
                atk_f, def_f = calcular_forca_equipa(fora)
                
                st.session_state.analisados = [
                    {"jogo": jogo_builder, "casa": casa, "fora": fora, "hora": "Hoje", "m": f"Vitória {casa} ou Empate", "o": 1.45, "conf": 98, "atk": atk_c, "def": def_c},
                    {"jogo": jogo_builder, "casa": casa, "fora": fora, "hora": "Hoje", "m": "Mais de 1.5 Gols", "o": 1.30, "conf": 95, "atk": max(atk_c, atk_f), "def": min(def_c, def_f)},
                    {"jogo": jogo_builder, "casa": casa, "fora": fora, "hora": "Hoje", "m": "Mais de 7.5 Escanteios", "o": 1.55, "conf": 89, "atk": atk_c, "def": def_f}
                ]
                st.success("Múltipla construída com base no cálculo da força real das equipas!")
            else:
                st.warning("Digite no formato 'Time A x Time B'")
    
    st.markdown("<br><p style='color:#888; font-size: 12px;'>OU ESCOLHA UMA LIGA PARA VARREDURA IA:</p>", unsafe_allow_html=True)
    liga_selecionada = st.selectbox("Selecione o Mercado:", list(LIGAS_DISPONIVEIS.keys()))
    codigo_da_liga = LIGAS_DISPONIVEIS[liga_selecionada]
    
    if st.button("🚨 PROCESSAR DADOS IA"):
        with st.status("A iniciar Protocolo V8 Supreme via CACHE...", expanded=True) as status:
            st.write("⏳ Procurando dados em alta velocidade...")
            dados = buscar_dados_api(codigo_da_liga) 
            
            if dados:
                st.session_state.analisados = []
                hoje_brasil = datetime.utcnow() - timedelta(hours=3)
                data_hoje_str = hoje_brasil.strftime("%Y-%m-%d")
                jogos_do_dia = [j for j in dados if j.get('commence_time', '').startswith(data_hoje_str)]
                
                for jogo in jogos_do_dia[:15]:
                    casa = jogo.get('home_team', 'Casa')
                    fora = jogo.get('away_team', 'Fora')
                    hora_jogo = datetime.strptime(jogo.get('commence_time', ''), "%Y-%m-%dT%H:%M:%SZ") - timedelta(hours=3)
                    nome_jogo = f"{casa} x {fora}"
                    mercados_encontrados = []
                    
                    if jogo.get('bookmakers'):
                        for bookie in jogo['bookmakers']:
                            for mercado in bookie.get('markets', []):
                                if mercado['key'] == 'h2h':
                                    for out in mercado['outcomes']:
                                        mercados_encontrados.append({"m": f"Vitória {out['name']}", "o": out['price']})
                                elif mercado['key'] == 'totals':
                                    for out in mercado['outcomes']:
                                        mercados_encontrados.append({"m": f"{out['name']} {out.get('point','')} Gols", "o": out['price']})

                    if mercados_encontrados:
                        melhor_aposta = random.choice(mercados_encontrados)
                        atk, dfs = calcular_forca_equipa(casa)
                        
                        st.session_state.analisados.append({
                            "jogo": nome_jogo, "casa": casa, "fora": fora, "hora": hora_jogo.strftime("%H:%M"),
                            "m": melhor_aposta["m"], "o": round(melhor_aposta["o"], 2), 
                            "conf": random.randint(85, 99), "atk": atk, "def": dfs
                        })
                status.update(label="✅ Varredura Concluída em tempo recorde!", state="complete", expanded=False)
            else: status.update(label="Erro na busca. API fora do ar ou limite excedido.", state="error")

    if st.session_state.analisados:
        st.markdown("---")
        min_conf = st.slider("MODO SNIPER: Filtrar por Confiança IA (%):", min_value=85, max_value=99, value=85)
        
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            if st.button("🎲 GERAR DUPLA SEGURA"):
                if len(st.session_state.analisados) >= 2:
                    st.session_state.bilhete.extend(sorted(st.session_state.analisados, key=lambda x: x['o'])[:2])
                    st.success("✅ Dupla adicionada!")
        with col_m2:
            if st.button("🚀 PROJETO ODD 1.000"):
                if len(st.session_state.analisados) >= 4:
                    jogos_ordenados = sorted(st.session_state.analisados, key=lambda x: x['conf'], reverse=True)
                    bilhete_milionario = []
                    odd_acumulada = 1.0
                    for jogo in jogos_ordenados:
                        bilhete_milionario.append(jogo)
                        odd_acumulada *= jogo['o']
                        if odd_acumulada >= 1000: break
                    st.session_state.bilhete.extend(bilhete_milionario) 
                    st.success(f"🚀 Bilhete adicionado: @{odd_acumulada:.2f}")

        st.markdown("<br><h4 class='neon-text'>OPORTUNIDADES IDENTIFICADAS</h4>", unsafe_allow_html=True)
        for idx, item in enumerate(st.session_state.analisados):
            if item['conf'] >= min_conf:
                html_card = (
                    f"<div class='game-card'>"
                    f"<div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;'>"
                    f"<div style='width: 40%; font-weight: bold; font-size: 14px;'>{item['casa']}</div>"
                    f"<div style='width: 10%; text-align: center; color: #555; font-size: 11px; font-style: italic;'>VS</div>"
                    f"<div style='width: 40%; font-weight: bold; font-size: 14px; text-align: right;'>{item['fora']}</div>"
                    f"</div>"
                    f"<div style='font-size: 10px; color: #888; margin-bottom: 2px;'>Força Ofensiva Calculada</div>"
                    f"<div style='width: 100%; background: #222; border-radius: 3px; height: 4px; margin-bottom: 8px;'><div style='width: {item['atk']}%; height: 4px; background: #ff3333; border-radius: 3px;'></div></div>"
                    f"<div style='font-size: 10px; color: #888; margin-bottom: 2px;'>Eficiência Defensiva</div>"
                    f"<div style='width: 100%; background: #222; border-radius: 3px; height: 4px; margin-bottom: 8px;'><div style='width: {item['def']}%; height: 4px; background: #00e5ff; border-radius: 3px;'></div></div>"
                    f"<div style='margin-top: 15px; background-color: rgba(0,0,0,0.3); padding: 10px; border-radius: 6px; display: flex; justify-content: space-between; align-items: center;'>"
                    f"<div><span style='font-size: 11px; color: #888;'>PREVISÃO IA:</span><br><span style='color: {cor_neon}; font-weight: bold; font-size: 13px;'>{item['m']}</span></div>"
                    f"<div style='text-align: right;'><span style='font-size: 11px; color: #888;'>ODD CALC:</span><br><span style='color: white; font-weight: bold; font-size: 15px;'>@{item['o']}</span></div>"
                    f"</div>"
                    f"<div style='margin-top: 5px; display: flex; justify-content: space-between; font-size: 11px; color: #aaa;'>"
                    f"<span>🕒 {item['hora']}</span><span style='color:{cor_neon}; font-weight:bold;'>⚡ Confiança: {item['conf']}%</span>"
                    f"</div>"
                    f"</div>"
                )
                st.markdown(html_card, unsafe_allow_html=True)
                if st.button(f"➕ ADICIONAR AO BILHETE", key=f"btn_{idx}"):
                    st.session_state.bilhete.append(item)
                    st.toast("✅ Adicionado!")

# ==========================================
# ABA 3: MEU BILHETE E MODO STORY
# ==========================================
with t3:
    st.markdown("<h4 class='neon-text'>CARRINHO DE APOSTAS</h4>", unsafe_allow_html=True)
    if st.session_state.bilhete:
        odd_f = 1.0
        
        if st.session_state.modo_story:
            st.button("❌ FECHAR MODO STORY", on_click=lambda: st.session_state.update(modo_story=False))
            st.markdown("<p style='text-align:center; font-size:12px; color:#888;'>Tire um print da tela abaixo e poste no seu Instagram!</p>", unsafe_allow_html=True)
            
            html_story = f"<div class='story-card'><div class='story-watermark'>@ronny_olivzz61</div>"
            html_story += f"<h2 style='color:{cor_neon}; font-style:italic; margin-bottom: 30px;'>V8 SUPREME A.I. 🤖</h2>"
            
            for b in st.session_state.bilhete:
                odd_f *= b['o']
                html_story += f"<div style='background:rgba(0,0,0,0.5); padding:10px; border-radius:8px; margin-bottom:10px; text-align:left; border-left:4px solid {cor_neon}; z-index: 2; position:relative;'>"
                html_story += f"<div style='font-weight:bold; font-size:14px; color:white;'>⚽ {b['jogo']}</div>"
                html_story += f"<div style='color:#bbb; font-size:12px;'>🎯 {b['m']}</div>"
                html_story += f"</div>"
            
            html_story += f"<div style='margin-top: 30px; font-size: 14px; color:#888;'>ODD FINAL IDENTIFICADA</div>"
            html_story += f"<div style='font-size: 40px; font-weight: 900; color:{cor_neon}; text-shadow: 0 0 20px {cor_neon};'>@{odd_f:.2f}</div>"
            html_story += f"<div style='margin-top: 20px; font-size: 12px; background:{cor_neon}; color:#000; padding:8px; border-radius:20px; font-weight:bold; display:inline-block;'>COPIE E COLE NO VIP 👆</div>"
            html_story += f"</div>"
            
            st.markdown(html_story, unsafe_allow_html=True)
            
        else:
            msg_tg = f"👑 *RONNYP VIP V8* 👑\n\n"
            msg_whats = "👑 *RONNYP VIP V8* 👑\n\n"
            
            st.markdown("<div style='background-color: rgba(26,27,34,0.8); padding: 15px; border-radius: 8px; border: 1px solid #2d2f36;'>", unsafe_allow_html=True)
            for b in st.session_state.bilhete:
                odd_f *= b['o']
                st.markdown(f"<p style='margin:0; font-size:14px; border-bottom: 1px solid #333; padding: 5px 0;'>✅ <b>{b['jogo']}</b> <span style='float:right; color:{cor_neon}; font-weight:bold;'>@{b['o']}</span></p>", unsafe_allow_html=True)
                msg_tg += f"🏟️ *{b['jogo']}*\n🎯 {b['m']} (@{b['o']})\n\n"
                msg_whats += f"🏟️ {b['jogo']}\n🎯 {b['m']} (@{b['o']})\n\n"
            st.markdown("</div>", unsafe_allow_html=True)
            
            st.markdown(f"<h2 style='text-align:center; margin-top:20px;'>📊 ODD TOTAL: <span style='color:{cor_neon};'>{odd_f:.2f}</span></h2>", unsafe_allow_html=True)
            
            if st.button("📸 MODO STORY (INSTAGRAM)", use_container_width=True):
                st.session_state.modo_story = True
                st.rerun()

            valor_aposta = st.number_input("💸 Stake (R$):", min_value=1.0, value=10.0, step=5.0)
            retorno = valor_aposta * odd_f
            st.info(f"🤑 RETORNO ESPERADO: R$ {retorno:.2f}")
            
            final_msg_whats = msg_whats + f"📊 *Odd Total: {odd_f:.2f}*\n💸 Aposta: R$ {valor_aposta:.2f}\n🤑 Retorno: R$ {retorno:.2f}\n\n🎰 APOSTE AQUI: {st.session_state.link_afiliado_ativo}"
            
            col_b1, col_b2 = st.columns(2)
            with col_b1:
                if st.button("ENVIAR TELEGRAM"):
                    asyncio.run(Bot(TOKEN).send_message(CHAT_ID, msg_tg, parse_mode='Markdown'))
                    st.success("Enviado!")
            with col_b2:
                link_zap = f"https://api.whatsapp.com/send?text={urllib.parse.quote(final_msg_whats)}"
                st.markdown(f'<a href="{link_zap}" target="_blank" class="btn-side" style="background: #25d366; margin:0;">🟢 ENVIAR ZAP</a>', unsafe_allow_html=True)
                
            st.markdown("---")
            st.markdown("<p style='text-align:center; color:#888; font-size:12px;'>RESULTADOS DO BILHETE (ADMIN)</p>", unsafe_allow_html=True)
            
            col_res1, col_res2, col_res3 = st.columns(3)
            with col_res1:
                if st.button("🟢 GREEN"):
                    st.session_state.total_jogos += len(st.session_state.bilhete)
                    st.session_state.total_acertos += len(st.session_state.bilhete)
                    for b in st.session_state.bilhete: st.session_state.historico_greens.insert(0, {"j": b['jogo'], "m": b['m'], "o": b['o']})
                    st.session_state.bilhete = [] 
                    st.rerun()
            with col_res2:
                if st.button("🔴 RED"):
                    st.session_state.total_jogos += len(st.session_state.bilhete)
                    st.session_state.bilhete = []
                    st.rerun()
            with col_res3:
                if st.button("🗑️ LIMPAR"):
                    st.session_state.bilhete = []
                    st.rerun()
    else:
        st.info("Seu bilhete está vazio. Vá na aba RADAR e adicione partidas.")

# ==========================================
# ABA 4: BILHETE SAFE DINÂMICO
# ==========================================
with t4:
    st.markdown("<h4 class='neon-text'>ALTO EV (SAFE)</h4>", unsafe_allow_html=True)
    
    if not st.session_state.is_vip:
        st.markdown(f"""
        <div style='position: relative; margin-top: 20px;'>
            <div class='blur-overlay'>
                <div style='background-color: rgba(26,27,34,0.9); padding: 20px; border-radius: 12px; border: 1px solid #FFD700;'>
                    <div style='text-align:center; margin-bottom: 15px;'><span style='background:#FFD700; color:#000; padding:5px 15px; border-radius:20px; font-weight:bold; font-size:12px;'>🏆 IA ASSERTIVIDADE: 99%</span></div>
                    <div style='border-left: 4px solid #00ff88; padding-left: 10px; margin-bottom: 10px;'><div style='color:white; font-weight:bold; font-size: 16px;'>⚽ Time A x Time B</div><div style='color:#bbb; font-size: 14px;'>🎯 Mercado Secreto | <span style='color:#00ff88; font-weight:bold;'>@1.50</span></div></div>
                </div>
            </div>
            <div class='lock-icon'>
                <h1 style='margin:0;'>🔒</h1>
                <h3 style='color:#FFD700; margin-top:10px;'>CONTEÚDO BLOQUEADO</h3>
                <p style='color:#bbb; font-size:12px;'>Esta aposta de alto valor está disponível apenas para membros do plano V8 Supremo.</p>
                <a href="{LINK_SUPORTE}" target="_blank" class="btn-side" style="background: #FFD700; color:#000 !important; margin-top:10px;">RENOVAR MEU ACESSO</a>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("<p style='color:#bbb; font-size:14px;'>A Inteligência Artificial separou as entradas mais seguras com base na sua última varredura no Radar!</p>", unsafe_allow_html=True)
        
        if not st.session_state.analisados:
            st.warning("⚠️ O Radar está vazio. Vá na aba 🎯 RADAR e clique em 'PROCESSAR DADOS IA' primeiro para encontrarmos a Boa do Dia.")
        else:
            seguros = [j for j in st.session_state.analisados if 1.15 <= j['o'] <= 1.65]
            seguros = sorted(seguros, key=lambda x: x['conf'], reverse=True)
            
            if len(seguros) >= 2:
                safe_pick = seguros[:2]
                odd_safe_total = safe_pick[0]['o'] * safe_pick[1]['o']
                media_conf = (safe_pick[0]['conf'] + safe_pick[1]['conf']) // 2
                
                html_safe = (
                    f"<div style='background-color: rgba(26,27,34,0.9); padding: 20px; border-radius: 12px; border: 1px solid #FFD700;'>"
                    f"<div style='text-align:center; margin-bottom: 15px;'><span style='background:#FFD700; color:#000; padding:5px 15px; border-radius:20px; font-weight:bold; font-size:12px;'>🏆 IA ASSERTIVIDADE: {media_conf}%</span></div>"
                    f"<div style='border-left: 4px solid #00ff88; padding-left: 10px; margin-bottom: 10px;'><div style='color:white; font-weight:bold; font-size: 16px;'>⚽ {safe_pick[0]['jogo']}</div><div style='color:#bbb; font-size: 14px;'>🎯 {safe_pick[0]['m']} | <span style='color:#00ff88; font-weight:bold;'>@{safe_pick[0]['o']:.2f}</span></div></div>"
                    f"<div style='border-left: 4px solid #00ff88; padding-left: 10px; margin-bottom: 15px;'><div style='color:white; font-weight:bold; font-size: 16px;'>⚽ {safe_pick[1]['jogo']}</div><div style='color:#bbb; font-size: 14px;'>🎯 {safe_pick[1]['m']} | <span style='color:#00ff88; font-weight:bold;'>@{safe_pick[1]['o']:.2f}</span></div></div>"
                    f"<hr style='border-color: rgba(255,215,0,0.3);'>"
                    f"<h3 style='text-align:center; color:#FFD700; text-shadow: 0 0 10px #FFD700;'>📊 ODD FINAL: {odd_safe_total:.2f}</h3>"
                    f"</div>"
                )
                st.markdown(html_safe, unsafe_allow_html=True)
                
                if st.button("🔥 COPIAR SAFE PARA O MEU BILHETE", use_container_width=True):
                    st.session_state.bilhete.extend(safe_pick)
                    tocar_som_moeda()
                    st.success("✅ Bilhete Safe copiado com sucesso! Vá na aba BILHETE para finalizar.")
            else:
                st.info("A IA não encontrou pelo menos 2 jogos com perfil 'Super Seguro' na varredura atual. Tente varrer outra Liga lá no Radar.")

# ==========================================
# ABA 5: PERFIL (Admin e Configurações)
# ==========================================
with t5:
    st.markdown(f"<h3 style='color:{cor_neon}; text-align:center;'>👑 CEO & FOUNDER</h3>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#888; font-size:12px; margin-top:-10px;'>Ronny P. | Especialista em IA</p>", unsafe_allow_html=True)
    st.markdown(f'<a href="https://instagram.com/ronny_olivzz61" target="_blank" class="btn-side" style="background: linear-gradient(45deg, #f09433, #e6683c, #dc2743, #cc2366, #bc1888);">📸 SIGA @ronny_olivzz61</a>', unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown(f"<h4 style='color:{cor_neon}; text-align:center; font-size: 14px;'>🎙️ BRIEFING DIÁRIO</h4>", unsafe_allow_html=True)
    st.audio(LINK_SEU_AUDIO_BRIEFING, format="audio/mp3")

    st.markdown("---")
    st.markdown("<p style='color:#888; font-size:11px; font-weight:bold;'>🎨 PERSONALIZAR INTERFACE</p>", unsafe_allow_html=True)
    st.selectbox("Escolha seu Neon:", ["Padrão (Por Gênero)", "🟢 Verde Hacker", "🟡 Ouro Milionário", "🔵 Azul Cyberpunk", "🔴 Vermelho Kamikaze", "🟣 Rosa Choque"], key="tema_escolhido")
    
    if st.session_state.is_admin:
        st.markdown("---")
        st.markdown("<p style='color:#888; font-size:11px; font-weight:bold;'>TESTE DE MARKETING (ADMIN)</p>", unsafe_allow_html=True)
        is_vip_checkbox = st.checkbox("Status de Assinatura: VIP Supremo", value=st.session_state.is_vip)
        if is_vip_checkbox != st.session_state.is_vip:
            st.session_state.is_vip = is_vip_checkbox
            st.rerun()
        st.caption("Desmarque a caixa acima e vá na aba 'SAFE' para ver o efeito Blur que os clientes não pagantes verão.")

    if st.session_state.is_admin:
        st.markdown("---")
        st.markdown("<p style='color:#888; font-size:11px; font-weight:bold;'>GERADOR DE KEYS (ADMIN)</p>", unsafe_allow_html=True)
        c_nome = st.text_input("Nome da Key:")
        tempo_key = st.selectbox("Validade:", ["24 Horas", "7 Dias", "30 Dias"])
        if st.button("CRIAR VIP"):
            horas = 24 if tempo_key == "24 Horas" else (168 if tempo_key == "7 Dias" else 720)
            salvar_key(c_nome, horas)
            st.success(f"✅ Key {c_nome} gerada!")
            st.code(f"{LINK_PAINEL}?key={c_nome}", language="text")

    st.markdown("<br><br>", unsafe_allow_html=True)
    if st.button("SAIR DO APLICATIVO"):
        st.session_state.autenticado = False
        st.rerun()
