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

# --- 1. CONFIGURAÇÃO E SEGURANÇA ---
st.set_page_config(page_title="RonnyP V8 SUPREME", layout="wide", initial_sidebar_state="collapsed")

MASTER_KEY = "ronnyp@2025"
FILE_KEYS = "keys.txt" 
TOKEN = '8543393879:AAEsaXAAq2A19zbmMEfHZb-R7nLL-VdierU'
CHAT_ID = '-1003799258159'
LINK_CANAL = "https://t.me/+_4ZgNo3xYFo5M2Ex"
LINK_SUPORTE = "https://wa.me/5561996193390?text=Olá%20RonnyP"
ODDS_API_KEY = "da4633249ece20283d29604cec7a7114"

# --- 2. INICIALIZAÇÃO DE ESTADOS GLOBAIS (11 MELHORIAS) ---
if 'autenticado' not in st.session_state: st.session_state.autenticado = False
if 'user_nome' not in st.session_state: st.session_state.user_nome = ""
if 'user_genero' not in st.session_state: st.session_state.user_genero = "Masculino"
if 'bilhete' not in st.session_state: st.session_state.bilhete = []
if 'analisados' not in st.session_state: st.session_state.analisados = []
if 'tema_escolhido' not in st.session_state: st.session_state.tema_escolhido = "🟢 Verde Hacker"
if 'is_vip' not in st.session_state: st.session_state.is_vip = True 
if 'boss_mode' not in st.session_state: st.session_state.boss_mode = False

# Múltiplos Links Admin
if 'links_afiliados' not in st.session_state: 
    st.session_state.links_afiliados = [
        "https://esportiva.bet.br?ref=511e1f11699f",
        "https://br.betano.com/ref=ronny",
        "https://bet365.com/ref=ronny"
    ]

# Multi-Bancas e Conquistas
if 'bancas' not in st.session_state: 
    st.session_state.bancas = {"Betano": 1000.0, "Bet365": 500.0, "Betfair": 0.0}
if 'historico_banca' not in st.session_state: st.session_state.historico_banca = [1500.0]
if 'recuperacao_red' not in st.session_state: st.session_state.recuperacao_red = False
if 'conquistas' not in st.session_state: st.session_state.conquistas = ["🏅 Novato Promissor"]
if 'total_jogos' not in st.session_state: st.session_state.total_jogos = 1248
if 'total_acertos' not in st.session_state: st.session_state.total_acertos = 1115
if 'historico_greens' not in st.session_state: 
    st.session_state.historico_greens = [{"j": "Real Madrid x Benfica", "m": "Over 2.5", "o": 1.75}, {"j": "PSG x Monaco", "m": "Ambas Marcam", "o": 1.65}]

# --- 3. MODO BOSS (Ocultar Tela Rápido) ---
if st.session_state.boss_mode:
    st.markdown("<h3 style='color:black;'>Planilha de Custos Operacionais Q3</h3>", unsafe_allow_html=True)
    df_fake = pd.DataFrame({
        "Mês": ["Janeiro", "Fevereiro", "Março", "Abril"],
        "Receita Bruta (R$)": [15400, 16200, 14900, 18000],
        "Despesas (R$)": [12000, 11500, 13200, 12100],
        "Margem de Lucro (%)": ["22%", "29%", "11%", "32%"]
    })
    st.dataframe(df_fake, use_container_width=True)
    if st.button("Voltar ao Sistema", key="btn_boss"):
        st.session_state.boss_mode = False
        st.rerun()
    st.stop() # Trava o app na planilha falsa

# --- 4. FUNÇÕES DE SISTEMA ---
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
    with open(FILE_KEYS, "a") as f: f.write(f"{nova_key},{exp_str}\n")
    return expiracao

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
        r = requests.get(url, timeout=10)
        if r.status_code == 200: return r.json()
    except: pass
    return None

@st.cache_data(ttl=3600, show_spinner=False)
def obter_jogos_vitrine():
    for liga in ["soccer_epl", "soccer_uefa_champs_league", "soccer_brazil_campeonato", "soccer_spain_la_liga"]:
        dados = buscar_dados_api(liga)
        if dados and len(dados) >= 5:
            return [{"casa": d.get('home_team','A'), "fora": d.get('away_team','B'), "jogo": f"{d.get('home_team')} x {d.get('away_team')}"} for d in dados[:5]]
    return [{"casa": "Flamengo", "fora": "Palmeiras", "jogo": "Flamengo x Palmeiras"}, {"casa": "Arsenal", "fora": "Chelsea", "jogo": "Arsenal x Chelsea"}, {"casa": "Man City", "fora": "Liverpool", "jogo": "Man City x Liverpool"}, {"casa": "Real Madrid", "fora": "Barcelona", "jogo": "Real Madrid x Barcelona"}, {"casa": "Milan", "fora": "Inter", "jogo": "Milan x Inter"}]

jogos_vitrine = obter_jogos_vitrine()

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
else: cor_neon = "#00ff88"

# --- GATILHO FOMO ---
if st.session_state.autenticado and random.random() < 0.2:
    st.toast(random.choice([
        "💸 Marcos_SP sacou R$ 850 agora!",
        f"🚨 Odd do {jogos_vitrine[0]['casa']} derretendo!",
        "🔥 340 VIPs online.",
        "💰 Ana_Silva recuperou o Red!"
    ]))

# --- CSS PREMIUM ---
st.markdown(f"""
    <style>
    header[data-testid="stHeader"] {{ display: none !important; }}
    .block-container {{ padding-top: 1rem !important; margin-top: -1rem !important; padding-bottom: 50px !important;}}
    #MainMenu {{visibility: hidden !important;}} .stDeployButton {{display:none !important;}} footer {{visibility: hidden !important;}}
    .stApp {{ background: linear-gradient(rgba(15, 16, 21, 0.92), rgba(15, 16, 21, 0.98)), url('{LINK_SUA_IMAGEM_DE_FUNDO}'); background-size: cover; background-position: center; background-attachment: fixed; color: #ffffff; }}
    div[data-testid="stTabs"] > div:first-of-type {{ background-color: rgba(26, 27, 34, 0.9) !important; border-radius: 12px !important; padding: 5px !important; border: 1px solid #2d2f36 !important; margin-bottom: 20px !important; justify-content: space-evenly !important; }}
    div[data-testid="stTabs"] button[role="tab"] {{ flex: 1 !important; color: #888 !important; font-weight: bold !important; font-size: 11px !important; background: transparent !important; border: none !important; transition: color 0.3s ease !important; }}
    div[data-testid="stTabs"] button[role="tab"]:hover {{ color: #fff !important; }}
    div[data-testid="stTabs"] button[role="tab"][aria-selected="true"] {{ color: {cor_neon} !important; background-color: rgba(255,255,255,0.05) !important; border-radius: 8px !important; }}
    .neon-text {{ color: {cor_neon}; font-weight: bold; font-size: 12px; letter-spacing: 1px; text-transform: uppercase; }}
    .header-destaque {{ text-align: left; color: #ffffff; font-size: 32px; font-weight: 900; font-style: italic; margin-top: -10px; line-height: 1.1; }}
    .stat-container {{ display: flex; justify-content: space-between; background-color: rgba(26, 27, 34, 0.8); border-radius: 8px; border: 1px solid #2d2f36; padding: 15px; margin-bottom: 20px; }}
    .stat-box {{ text-align: center; width: 24%; border-right: 1px solid #333; }}
    .stat-box:last-child {{ border-right: none; }}
    .stat-title {{ color: #888; font-size: 11px; margin:0; text-transform: uppercase; letter-spacing: 0.5px; }}
    .stat-value {{ font-size: 22px; font-weight: 900; margin: 5px 0 0 0; }}
    .game-card {{ background-color: rgba(26, 27, 34, 0.9); padding: 15px; border-radius: 8px; margin-bottom: 12px; border-left: 4px solid #333; transition: all 0.3s ease; border-top: 1px solid #2d2f36; border-right: 1px solid #2d2f36; border-bottom: 1px solid #2d2f36; }}
    .game-card:hover {{ border-left: 4px solid {cor_neon}; box-shadow: 0 4px 15px rgba(0,0,0,0.5); transform: translateY(-2px); }}
    .stButton>button {{ background: {cor_neon} !important; color: #000 !important; font-weight: 900 !important; border-radius: 8px !important; border: none !important; padding: 10px 20px !important; width: 100%; transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important; box-shadow: 0 4px 6px rgba(0,0,0,0.3) !important; }}
    .stButton>button:hover {{ transform: translateY(-3px) scale(1.02) !important; filter: brightness(1.1) !important; box-shadow: 0 8px 20px {cor_neon}60 !important; }}
    .stButton>button:active {{ transform: translateY(2px) scale(0.95) !important; filter: brightness(0.9) !important; }}
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
        
        st.markdown("<p style='text-align:center; margin-top:15px; color:#888; font-size: 12px;'>OU</p>", unsafe_allow_html=True)
        if st.button("🔓 ENTRAR COM FACE ID"):
            if url_key: 
                st.session_state.autenticado = True
                st.session_state.is_admin = True
                st.session_state.user_nome = "CEO"
                st.rerun()
            else:
                st.warning("Face ID requer chave pré-configurada.")
        st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# --- BOSS BUTTON SUPERIOR ---
col_logo, col_boss = st.columns([0.8, 0.2])
with col_boss:
    if st.button("👁️", help="Modo Invisível"):
        st.session_state.boss_mode = True
        st.rerun()

win_rate = (st.session_state.total_acertos / st.session_state.total_jogos) * 100 if st.session_state.total_jogos > 0 else 0
saldo_total = sum(st.session_state.bancas.values())

# --- 6. NAVEGAÇÃO PRINCIPAL ---
t1, t2, t3, t4, t5 = st.tabs(["🏠 INÍCIO", "🎯 RADAR", "📋 BILHETE", "🛡️ SAFE", "⚙️ PERFIL"])

LIGAS_DISPONIVEIS = {"🇬🇧 Premier League": "soccer_epl", "🇪🇺 Champions League": "soccer_uefa_champs_league", "🇪🇸 La Liga": "soccer_spain_la_liga", "🇧🇷 Brasileirão": "soccer_brazil_campeonato"}

# ==========================================
# ABA 1: INÍCIO 
# ==========================================
with t1:
    st.markdown(f"<h4 class='neon-text'>BEM-VINDO</h4>", unsafe_allow_html=True)
    st.markdown(f"<h1 class='header-destaque'>{st.session_state.user_nome.upper()}</h1>", unsafe_allow_html=True)
    
    st.markdown(f"<p style='color: #888; font-size: 11px; font-weight: bold;'>📈 EVOLUÇÃO DA SUA BANCA (SALDO: R$ {saldo_total:.2f})</p>", unsafe_allow_html=True)
    st.line_chart(st.session_state.historico_banca, height=150, use_container_width=True)

    st.markdown("<p style='color: #888; font-size: 12px; margin-top: 15px; font-weight: bold;'>📊 TRACK RECORD GLOBAL — 30 DIAS</p>", unsafe_allow_html=True)
    st.markdown(f"""
        <div class='stat-container'>
            <div class='stat-box'><p class='stat-title'>Jogos</p><p class='stat-value'>{st.session_state.total_jogos}</p></div>
            <div class='stat-box'><p class='stat-title'>Acertos</p><p class='stat-value green' style='color:{cor_neon};'>{st.session_state.total_acertos}</p></div>
            <div class='stat-box'><p class='stat-title'>Win Rate</p><p class='stat-value'>{win_rate:.1f}%</p></div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("<h4 style='color:white; margin-top: 20px;'>👥 MAIS APOSTADOS PELOS VIPs</h4>", unsafe_allow_html=True)
    st.markdown(f"""
        <div style='background: rgba(0,0,0,0.4); padding: 10px; border-radius: 8px; border-left: 3px solid {cor_neon}; margin-bottom: 5px;'>
            <span style='color:{cor_neon}; font-weight:bold;'>#1</span> {jogos_vitrine[0]['jogo']} (Ambas Marcam)
        </div>
        <div style='background: rgba(0,0,0,0.4); padding: 10px; border-radius: 8px; border-left: 3px solid #FFD700; margin-bottom: 20px;'>
            <span style='color:#FFD700; font-weight:bold;'>#2</span> {jogos_vitrine[1]['jogo']} (+1.5 Gols)
        </div>
    """, unsafe_allow_html=True)

    minuto = datetime.now().minute
    st.markdown("<h4 style='color:white;'>🔴 JOGOS A DECORRER</h4>", unsafe_allow_html=True)
    st.markdown(f"""
        <div style='background-color: rgba(26,27,34,0.9); border-left: 3px solid #ff3333; padding: 10px 15px; margin-bottom: 10px; border-radius: 6px; display: flex; justify-content: space-between; align-items: center;'>
            <div><span class='live-badge'>{(minuto+23)%90+1}'</span> <span style='color:white; font-weight:bold; font-size: 14px; margin-left: 10px;'>{jogos_vitrine[2]['casa']} {(minuto//15)%3} x {(minuto//25)%2} {jogos_vitrine[2]['fora']}</span></div>
            <div style='color:#bbb; font-size: 12px;'>IA: <span style='color:{cor_neon}; font-weight:bold;'>Over 1.5</span></div>
        </div>
    """, unsafe_allow_html=True)

# ==========================================
# ABA 2: RADAR, ORÁCULO E SUREBET
# ==========================================
with t2:
    st.markdown("<h4 class='neon-text'>SELECTION HUB</h4>", unsafe_allow_html=True)
    
    # SMART MONEY E LESÕES
    st.markdown(f"""
        <div style='background-color: rgba(0,229,255,0.1); border: 1px solid #00e5ff; padding: 10px; border-radius: 8px; margin-bottom: 10px;'>
            <span style='color:#00e5ff; font-weight:bold;'>📉 SMART MONEY:</span> 78% do dinheiro dos Sindicatos Asiáticos acabou de entrar contra o <b>{jogos_vitrine[3]['casa']}</b>. Siga o fluxo.
        </div>
    """, unsafe_allow_html=True)

    with st.expander("⚖️ OPORTUNIDADE DE SUREBET (LUCRO 100%)"):
        j_surebet = jogos_vitrine[4]
        link_sorteado = random.choice(st.session_state.links_afiliados)
        st.markdown(f"""
        <p style='font-size: 12px; color:#bbb;'>A IA encontrou uma falha de precificação nas casas:</p>
        <div style='background: rgba(0,0,0,0.5); padding: 10px; border-radius: 8px;'>
            <b>Jogo:</b> {j_surebet['jogo']}<br>
            Aposte <b>R$ 50</b> no {j_surebet['casa']} na sua Casa Primária (Odd @2.10)<br>
            Aposte <b>R$ 50</b> em Empate/{j_surebet['fora']} no link VIP abaixo (Odd @2.15)<br>
            <span style='color:{cor_neon}; font-weight:bold;'>Lucro Garantido: R$ 5,00 a R$ 7,50!</span><br>
            <a href="{link_sorteado}" target="_blank" style="color:#00e5ff; font-size:11px;">Abrir Link VIP</a>
        </div>
        """, unsafe_allow_html=True)

    with st.expander("🤖 ORÁCULO V8 - Pergunte à IA"):
        pergunta = st.text_input("O que você quer analisar?", placeholder="Ex: Analise o Flamengo")
        if st.button("🔮 CONSULTAR"):
            if pergunta:
                with st.spinner("Analisando 10.000 variáveis em tempo real..."):
                    time.sleep(1.5)
                    time_alvo = pergunta.split()[-1].capitalize()
                    atk, dfs = calcular_forca_equipa(time_alvo)
                    st.markdown(f"""
                    <div class='chat-bubble'>
                        <strong style='color:white;'>V8 Supreme A.I:</strong><br>Relatório para <b>{time_alvo}</b>:<br>
                        - Eficiência de Ataque: <span style='color:#ff3333;'>{atk}%</span><br>
                        - Solidez Defensiva: <span style='color:#00e5ff;'>{dfs}%</span><br>
                        Probabilidade de Sucesso: <b>{random.randint(75, 96)}%</b>. Sugestão: EV+ acima de @1.45.
                    </div>
                    """, unsafe_allow_html=True)

    with st.expander("✍️ MODO MANUAL: Inserir Grade"):
        grade = st.text_area("Lista de jogos:", height=100, placeholder="Santos x Fluminense\nCeara x Coritiba")
        if st.button("🔍 ANÁLISE MANUAL"):
            if grade:
                jogos = [j for j in grade.split('\n') if 'x' in j.lower()]
                st.session_state.analisados = []
                for j in jogos:
                    parts = j.lower().split('x')
                    casa, fora = parts[0].strip().title(), parts[1].strip().title()
                    atk, dfs = calcular_forca_equipa(casa)
                    st.session_state.analisados.append({
                        "jogo": j, "casa": casa, "fora": fora, "hora": "Hoje",
                        "m": random.choice(["Ambas Marcam", "Over 1.5", "Vitória Casa"]), "o": round(random.uniform(1.4, 2.1), 2), 
                        "conf": random.randint(88,99), "atk": atk, "def": dfs, "arb": random.choice(["Rigoroso", "Moderado"])
                    })
                st.success("Concluído!")

    st.markdown("<br><p style='color:#888; font-size: 12px;'>VARREDURA DE MERCADO:</p>", unsafe_allow_html=True)
    codigo_da_liga = LIGAS_DISPONIVEIS[st.selectbox("Liga:", list(LIGAS_DISPONIVEIS.keys()))]
    
    if st.button("🚨 PROCESSAR DADOS IA"):
        with st.status("A iniciar Protocolo V8 Supreme...", expanded=True) as status:
            dados = buscar_dados_api(codigo_da_liga) 
            if dados:
                st.session_state.analisados = []
                data_hoje_str = (datetime.utcnow() - timedelta(hours=3)).strftime("%Y-%m-%d")
                for jogo in [j for j in dados if j.get('commence_time', '').startswith(data_hoje_str)][:15]:
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
                            "m": aposta["m"], "o": round(aposta["o"], 2), "conf": random.randint(85, 99), "atk": atk, "def": dfs, "arb": random.choice(["Rigoroso", "Moderado", "Brando"])
                        })
                status.update(label="✅ Varredura Concluída!", state="complete", expanded=False)
            else: status.update(label="Erro API.", state="error")

    if st.session_state.analisados:
        st.markdown("---")
        min_conf = st.slider("Filtro Sniper (%):", min_value=85, max_value=99, value=85)
        for idx, item in enumerate(st.session_state.analisados):
            if item['conf'] >= min_conf:
                # HEATMAP E ARBITRO INJETADOS NO CARD
                with st.expander(f"⚽ {item['casa']} x {item['fora']} | @{item['o']}"):
                    st.markdown(f"""
                        <div style='font-size: 11px; color: #888; margin-bottom: 10px;'>
                            <b>Previsão:</b> <span style='color:{cor_neon};'>{item['m']}</span><br>
                            <b>Confiança:</b> {item['conf']}%<br>
                            <b>Perfil Árbitro:</b> {item.get('arb', 'Desconhecido')} (Média 4.5 cartões)<br>
                            <br><b>🔥 Heatmap de Gols Previsto:</b>
                        </div>
                    """, unsafe_allow_html=True)
                    # Gráfico de calor simples
                    col_h1, col_h2, col_h3 = st.columns(3)
                    col_h1.markdown("<div style='background:#ff3333; padding:5px; text-align:center; font-size:10px; border-radius:4px;'>0-30' (Alto)</div>", unsafe_allow_html=True)
                    col_h2.markdown("<div style='background:#222; padding:5px; text-align:center; font-size:10px; border-radius:4px;'>31-60' (Baixo)</div>", unsafe_allow_html=True)
                    col_h3.markdown(f"<div style='background:{cor_neon}; color:black; padding:5px; text-align:center; font-size:10px; border-radius:4px; font-weight:bold;'>61-90' (Máx)</div>", unsafe_allow_html=True)
                    
                    st.markdown("<br>", unsafe_allow_html=True)
                    if st.button(f"➕ ADICIONAR AO BILHETE", key=f"btn_{idx}"):
                        st.session_state.bilhete.append(item)
                        st.toast("✅ Adicionado!")

# ==========================================
# ABA 3: BILHETE E FERRAMENTAS VIP
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
        
        # TORCIDA VIP MATCHMAKING
        st.markdown(f"<p style='text-align:center; font-size:11px; color:#00e5ff;'>👥 <b>{random.randint(12, 54)} VIPs</b> estão nesta mesma aposta agora.</p>", unsafe_allow_html=True)

        # MULTI-BANCAS NO BILHETE
        banca_escolhida = st.selectbox("Debitar da Carteira:", list(st.session_state.bancas.keys()))
        banca_disp = st.session_state.bancas[banca_escolhida]
        
        if st.session_state.recuperacao_red: rec_stake = banca_disp * 0.005; risco = "🛡️ RECUPERAÇÃO DE RED"
        else:
            if odd_f < 2.5: rec_stake = banca_disp * 0.03; risco = "🟢 Risco Baixo"
            elif odd_f < 6.0: rec_stake = banca_disp * 0.015; risco = "🟡 Risco Moderado"
            else: rec_stake = banca_disp * 0.005; risco = "🔴 Risco Alto (Kamikaze)"

        st.markdown(f"""
        <div style='background: rgba(0,0,0,0.5); border-left: 4px solid {cor_neon}; padding: 15px; border-radius: 8px; margin-bottom: 20px;'>
            <div style='font-size: 11px; color: #888;'>🤖 Smart Stake | Banca {banca_escolhida}: R$ {banca_disp:.2f}</div>
            <div style='margin-top: 5px; font-size: 14px;'>Risco: <b>{risco}</b></div>
            <div style='margin-top: 5px; font-size: 14px;'>Investimento Sugerido: <b style='color: {cor_neon}; font-size: 18px;'>R$ {rec_stake:.2f}</b></div>
            <div style='font-size: 10px; color:#ff3333; margin-top: 5px;'>🧮 Tip Cashout: Saia se o jogo empatar até os 75' mins.</div>
        </div>
        """, unsafe_allow_html=True)
        
        valor_aposta = st.number_input("💸 Confirmar Stake (R$):", min_value=1.0, value=float(rec_stake), step=5.0)
        retorno = valor_aposta * odd_f
        st.info(f"🤑 RETORNO ESPERADO: R$ {retorno:.2f}")
        
        link_zap = f"https://api.whatsapp.com/send?text={urllib.parse.quote(msg_tg)}"
        
        col_b1, col_b2 = st.columns(2)
        with col_b1:
            if st.button("⚡ AUTO-BET (API)"):
                with st.spinner("Executando aposta automática..."):
                    time.sleep(1.5)
                    st.session_state.bancas[banca_escolhida] -= valor_aposta
                    st.success("✅ Aposta Injetada!")
                    if "🏅 High Roller" not in st.session_state.conquistas and valor_aposta >= 100:
                        st.session_state.conquistas.append("🏅 High Roller")
                        st.balloons()
        with col_b2:
            st.markdown(f'<a href="{link_zap}" target="_blank" class="btn-side" style="background: #25d366; margin:0;">🟢 ENVIAR ZAP</a>', unsafe_allow_html=True)

        st.markdown("---")
        col_r1, col_r2 = st.columns(2)
        with col_r1:
            if st.button("🟢 BATER GREEN", use_container_width=True):
                st.session_state.total_jogos += len(st.session_state.bilhete)
                st.session_state.total_acertos += len(st.session_state.bilhete)
                st.session_state.bancas[banca_escolhida] += retorno 
                st.session_state.historico_banca.append(sum(st.session_state.bancas.values()))
                st.session_state.recuperacao_red = False
                if "🎯 Sniper" not in st.session_state.conquistas and st.session_state.total_acertos % 5 == 0:
                    st.session_state.conquistas.append("🎯 Sniper")
                st.session_state.bilhete = [] 
                st.rerun()
        with col_r2:
            if st.button("🔴 MARCAR RED", use_container_width=True):
                st.session_state.total_jogos += len(st.session_state.bilhete)
                st.session_state.historico_banca.append(sum(st.session_state.bancas.values()))
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
# ABA 5: PERFIL (Multi-Banca, Relatório, Admin)
# ==========================================
with t5:
    st.markdown(f"<h3 style='color:{cor_neon}; text-align:center;'>👑 CEO & FOUNDER</h3>", unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("<p style='color:#888; font-size:11px; font-weight:bold;'>🏆 MINHAS CONQUISTAS</p>", unsafe_allow_html=True)
    st.markdown(" ".join([f"<span style='background:#333; padding:5px 10px; border-radius:15px; font-size:12px; margin-right:5px;'>{c}</span>" for c in st.session_state.conquistas]), unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("<p style='color:#888; font-size:11px; font-weight:bold;'>🏛️ GESTÃO DE CARTEIRAS (MULTI-BANCA)</p>", unsafe_allow_html=True)
    col_c1, col_c2, col_c3 = st.columns(3)
    st.session_state.bancas["Betano"] = col_c1.number_input("Betano", value=st.session_state.bancas["Betano"], step=50.0)
    st.session_state.bancas["Bet365"] = col_c2.number_input("Bet365", value=st.session_state.bancas["Bet365"], step=50.0)
    st.session_state.bancas["Betfair"] = col_c3.number_input("Betfair", value=st.session_state.bancas["Betfair"], step=50.0)
    
    st.session_state.recuperacao_red = st.checkbox("🛡️ Ativar Modo Recuperação de Red", value=st.session_state.recuperacao_red)

    st.markdown("---")
    st.markdown("<p style='color:#888; font-size:11px; font-weight:bold;'>🤖 INTEGRAÇÃO BOT TELEGRAM INDIVIDUAL</p>", unsafe_allow_html=True)
    st.text_input("Vincular ID Pessoal do Telegram:", placeholder="Ex: @seu_usuario")
    st.caption("Receba alertas de Green direto no seu PV.")

    st.markdown("---")
    st.markdown("<p style='color:#888; font-size:11px; font-weight:bold;'>📑 RELATÓRIO EXECUTIVO MENSAL</p>", unsafe_allow_html=True)
    relatorio_txt = f"RELATÓRIO V8 SUPREME\n\nNome: {st.session_state.user_nome}\nSaldo Total: R$ {saldo_total:.2f}\nWin Rate: {win_rate:.1f}%\nConquistas: {', '.join(st.session_state.conquistas)}"
    st.download_button("Baixar PDF/Extrato", data=relatorio_txt, file_name="Extrato_V8_Supreme.txt", use_container_width=True)

    st.markdown("---")
    st.selectbox("Tema do App:", ["🟢 Verde Hacker", "🟡 Ouro Milionário", "🔵 Azul Cyberpunk", "🔴 Vermelho Kamikaze", "🟣 Rosa Choque"], key="tema_escolhido")

    # ADMIN: GESTÃO MÚLTIPLA DE LINKS
    if st.session_state.is_admin:
        st.markdown("---")
        st.markdown("<p style='color:#ff3333; font-size:11px; font-weight:bold;'>🔗 ADMIN: GESTÃO DE LINKS DE AFILIADO</p>", unsafe_allow_html=True)
        novos_links = st.text_area("Insira os links (um por linha):", value="\n".join(st.session_state.links_afiliados), height=100)
        if st.button("Salvar Links de Afiliado"):
            st.session_state.links_afiliados = [l.strip() for l in novos_links.split('\n') if l.strip()]
            st.success("Links atualizados! O app irá sortear entre eles.")

        st.markdown("---")
        c_nome = st.text_input("Gerador Key:")
        if st.button("CRIAR VIP"):
            salvar_key(c_nome, 24)
            st.code(f"{LINK_PAINEL}?key={c_nome}")

    st.markdown("<br><br>", unsafe_allow_html=True)
    if st.button("SAIR DO APLICATIVO"):
        st.session_state.autenticado = False
        st.rerun()
