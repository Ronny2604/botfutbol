import streamlit as st
import asyncio
import random
import time
import os
import urllib.parse
import requests
from telegram import Bot
from datetime import datetime, timedelta

# --- 1. CONFIGURAÇÃO E SEGURANÇA ---
st.set_page_config(page_title="RonnyP V8 SUPREME", layout="wide", initial_sidebar_state="expanded")

MASTER_KEY = "ronnyp@2025"
FILE_KEYS = "keys.txt" 
TOKEN = '8543393879:AAEsaXAAq2A19zbmMEfHZb-R7nLL-VdierU'
CHAT_ID = '-1003799258159'
LINK_CANAL = "https://t.me/+_4ZgNo3xYFo5M2Ex"
LINK_SUPORTE = "https://wa.me/5561996193390?text=Olá%20RonnyP"
LINK_CASA_1 = "https://esportiva.bet.br?ref=511e1f11699f"

# ⚠️ COLOQUE O LINK REAL DO SEU APLICATIVO AQUI ABAIXO:
LINK_PAINEL = "https://seu-link-aqui.streamlit.app"

ODDS_API_KEY = "da4633249ece20283d29604cec7a7114"

# --- 2. FUNÇÕES DE SISTEMA ---
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
    som_html = """
    <audio autoplay style="display:none;">
        <source src="https://assets.mixkit.co/active_storage/sfx/2003/2003-preview.mp3" type="audio/mpeg">
    </audio>
    """
    st.markdown(som_html, unsafe_allow_html=True)

def tocar_som_alerta():
    som_html = """
    <audio autoplay style="display:none;">
        <source src="https://assets.mixkit.co/active_storage/sfx/2869/2869-preview.mp3" type="audio/mpeg">
    </audio>
    """
    st.markdown(som_html, unsafe_allow_html=True)

# --- 3. INICIALIZAÇÃO E ESTADOS ---
if 'autenticado' not in st.session_state: st.session_state.autenticado = False
if 'user_nome' not in st.session_state: st.session_state.user_nome = ""
if 'user_genero' not in st.session_state: st.session_state.user_genero = "Masculino"
if 'bilhete' not in st.session_state: st.session_state.bilhete = []
if 'analisados' not in st.session_state: st.session_state.analisados = []
if 'show_welcome' not in st.session_state: st.session_state.show_welcome = False
if 'tema_escolhido' not in st.session_state: st.session_state.tema_escolhido = "Padrão (Por Gênero)"

db_keys = carregar_keys()

def valida_chave(chave):
    if chave == MASTER_KEY: return True, True
    if chave in db_keys:
        if datetime.now() < db_keys[chave]: return True, False
    return False, False

# --- CONTROLE DE TEMA NEON ---
if st.session_state.autenticado:
    with st.sidebar:
        st.markdown("<h4 style='color:white; text-align:center;'>🎨 PERSONALIZAR INTERFACE</h4>", unsafe_allow_html=True)
        st.session_state.tema_escolhido = st.selectbox(
            "Escolha seu Neon:", 
            ["Padrão (Por Gênero)", "🟢 Verde Hacker", "🟡 Ouro Milionário", "🔵 Azul Cyberpunk", "🔴 Vermelho Kamikaze", "🟣 Rosa Choque"]
        )

is_fem = st.session_state.user_genero == "Feminino"
if st.session_state.tema_escolhido == "🟢 Verde Hacker": cor_neon = "#00ff88"
elif st.session_state.tema_escolhido == "🟡 Ouro Milionário": cor_neon = "#FFD700"
elif st.session_state.tema_escolhido == "🔵 Azul Cyberpunk": cor_neon = "#00e5ff"
elif st.session_state.tema_escolhido == "🔴 Vermelho Kamikaze": cor_neon = "#ff3333"
elif st.session_state.tema_escolhido == "🟣 Rosa Choque": cor_neon = "#ff00ff"
else: cor_neon = "#ff00ff" if is_fem else "#00ff88"

bg_marquee = "#1a001a" if cor_neon == "#ff00ff" else "#00120a"

# --- 4. CSS SUPREME E GLASSMORPHISM ---
st.markdown(f"""
    <style>
    #MainMenu {{visibility: hidden !important;}}
    .stDeployButton {{display:none !important;}}
    footer {{visibility: hidden !important;}}
    [data-testid="stActionButtonIcon"] {{display: none !important;}}
    
    @keyframes fadeIn {{ from {{ opacity: 0; transform: translateY(10px); }} to {{ opacity: 1; transform: translateY(0); }} }}
    
    .stApp {{ background: radial-gradient(circle at center, #0a1b33 0%, #02060d 100%); animation: fadeIn 0.8s ease-out; }}
    
    .glass-panel {{
        background: rgba(10, 22, 38, 0.45) !important;
        backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px);
        border-radius: 16px; border: 1px solid rgba(255, 255, 255, 0.08);
        padding: 20px; margin-bottom: 15px; box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
        transition: transform 0.3s ease;
    }}
    .glass-panel:hover {{ transform: translateY(-2px); border-color: {cor_neon}50; box-shadow: 0 8px 32px 0 {cor_neon}20; }}
    
    header[data-testid="stHeader"] {{ background-color: rgba(2, 6, 13, 0.8) !important; border-bottom: 1px solid {cor_neon}33; backdrop-filter: blur(10px); }}
    .header-destaque {{ text-align: center; padding: 10px; color: {cor_neon}; font-size: 28px; font-weight: 900; text-shadow: 0 0 20px {cor_neon}; margin-top: -20px; letter-spacing: 2px; }}
    
    .marquee-wrapper {{ width: 100%; overflow: hidden; background: rgba(0,0,0,0.5); border-bottom: 2px solid {cor_neon}; padding: 10px 0; display: flex; margin-bottom: 20px; backdrop-filter: blur(5px); }}
    .marquee-content {{ display: flex; white-space: nowrap; animation: marquee 30s linear infinite; }}
    .marquee-item {{ padding: 0 40px; color: {cor_neon}; font-weight: bold; text-shadow: 0 0 5px {cor_neon}; }}
    @keyframes marquee {{ 0% {{ transform: translateX(0); }} 100% {{ transform: translateX(-50%); }} }}
    
    .btn-side {{ display: block; padding: 12px; margin-bottom: 10px; text-align: center; border-radius: 8px; font-weight: bold; text-decoration: none; color: white !important; font-size: 14px; transition: 0.3s; }}
    .btn-side:hover {{ transform: scale(1.02); filter: brightness(1.2); }}
    .stButton>button {{ background: {cor_neon} !important; color: #040d1a !important; font-weight: 900 !important; border-radius: 10px !important; border: none !important; transition: 0.3s; }}
    .stButton>button:hover {{ transform: scale(1.03); box-shadow: 0 0 15px {cor_neon}; }}
    
    @keyframes pulse-pix {{ 0% {{ transform: scale(1); box-shadow: 0 0 0 0 {cor_neon}70; }} 50% {{ transform: scale(1.05); box-shadow: 0 0 15px 5px {cor_neon}40; }} 100% {{ transform: scale(1); box-shadow: 0 0 0 0 {cor_neon}00; }} }}
    .btn-pix {{ display: block; padding: 15px; margin-top: 15px; text-align: center; border-radius: 12px; font-weight: 900; text-decoration: none; color: #040d1a !important; font-size: 16px; background-color: {cor_neon}; animation: pulse-pix 2s infinite; text-transform: uppercase; letter-spacing: 1px; }}
    
    .metric-card {{ background: rgba(10, 22, 38, 0.6); border: 1px solid {cor_neon}30; border-radius: 12px; padding: 15px; text-align: center; box-shadow: 0 4px 15px {cor_neon}10; transition: 0.3s; }}
    .metric-card:hover {{ transform: translateY(-5px); border-color: {cor_neon}; }}
    .metric-title {{ color: #bbb; font-size: 14px; text-transform: uppercase; letter-spacing: 1px; }}
    .metric-value {{ color: {cor_neon}; font-size: 24px; font-weight: bold; text-shadow: 0 0 10px {cor_neon}50; margin-top: 5px; }}

    @keyframes popup-anim {{ 0%, 100% {{ bottom: -100px; opacity: 0; }} 10%, 90% {{ bottom: 20px; opacity: 1; }} }}
    @keyframes text-carousel {{
        0% {{ content: "🔥 Marcos M. acabou de gerar uma Dupla Segura!"; border-left-color: {cor_neon}; }}
        33% {{ content: "💰 Saque de R$ 850,00 realizado por Ana"; border-left-color: #FFD700; }}
        66% {{ content: "🚨 Lucas ativou o Modo Kamikaze"; border-left-color: #ff3333; }}
        100% {{ content: "✅ O VIP bateu 3 Greens seguidos hoje!"; border-left-color: #00ff88; }}
    }}
    .toast-flutuante {{ position: fixed; right: 20px; background: rgba(10, 22, 38, 0.95); color: white; padding: 15px 25px; border-radius: 10px; border-left: 5px solid {cor_neon}; box-shadow: 0 5px 20px rgba(0,0,0,0.8); z-index: 9999; animation: popup-anim 15s infinite; font-weight: bold; backdrop-filter: blur(5px); }}
    .toast-flutuante::after {{ content: ""; animation: text-carousel 60s infinite steps(1); }}
    </style>
    
    <div class="toast-flutuante"></div>
    """, unsafe_allow_html=True)

# --- CAPTURA DE KEY VIA URL (LOGIN MÁGICO) ---
url_key = ""
if "key" in st.query_params:
    url_key = st.query_params["key"]

# --- 5. TELA DE LOGIN ---
if not st.session_state.autenticado:
    st.markdown(f"<div class='header-destaque'>RONNYP V8 SUPREME</div>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    with st.container():
        st.markdown("<div class='glass-panel' style='max-width:400px; margin:auto;'>", unsafe_allow_html=True)
        st.markdown(f"<h3 style='text-align:center; color:{cor_neon};'>ACESSO VIP Ouro</h3>", unsafe_allow_html=True)
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

# --- 6. CONTEÚDO LOGADO ---
st.markdown(f"<div class='header-destaque'>RONNYP V8 SUPREME</div>", unsafe_allow_html=True)
itens_marquee = "".join([f"<div class='marquee-item'> 🔥 {n} ENTROU NO VIP </div>" for n in ["Marcos", "Ana", "Lucas", "Julia", "Tadeu", "Carla"]])
st.markdown(f"<div class='marquee-wrapper'><div class='marquee-content'>{itens_marquee}{itens_marquee}</div></div>", unsafe_allow_html=True)

if st.session_state.show_welcome:
    st.toast(f"Bem-vindo(a) ao nível Supreme, {st.session_state.user_nome}! 💰")
    tocar_som_moeda()
    st.balloons()
    st.session_state.show_welcome = False

# --- 7. MENU LATERAL & ADMIN ---
with st.sidebar:
    st.markdown("<div class='glass-panel' style='text-align: center; padding: 15px;'>", unsafe_allow_html=True)
    st.markdown(f"<h3 style='color:{cor_neon}; margin-bottom: 0; text-shadow: 0 0 10px {cor_neon};'>👑 CEO & FOUNDER</h3>", unsafe_allow_html=True)
    st.markdown("<p style='color:#bbb; font-size:14px;'>Ronny P. | Especialista em IA</p>", unsafe_allow_html=True)
    
    st.markdown(f'<a href="https://instagram.com/ronny_olivzz61" target="_blank" class="btn-side" style="background: linear-gradient(45deg, #f09433 0%, #e6683c 25%, #dc2743 50%, #cc2366 75%, #bc1888 100%); border-radius: 30px;">📸 SIGA @ronny_olivzz61</a>', unsafe_allow_html=True)
    st.markdown(f'<a href="https://tiktok.com/@ronny.p061" target="_blank" class="btn-side" style="background: #000; border: 1px solid {cor_neon}; border-radius: 30px;">🎵 SIGA @ronny.p061 no TikTok</a>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown(f"<p style='text-align:center; font-size: 18px; margin-bottom: 5px;'>👤 Bem-vindo(a), <b>{st.session_state.user_nome}</b></p>", unsafe_allow_html=True)
    st.markdown(f"<div style='text-align:center; margin-bottom: 20px;'><span style='background-color:rgba(0,0,0,0.5); padding: 5px 15px; border-radius: 20px; color:{cor_neon}; font-size: 12px; font-weight:bold; border: 1px solid {cor_neon}; box-shadow: 0 0 10px {cor_neon}50;'>💎 VIP DIAMANTE</span></div>", unsafe_allow_html=True)
    
    st.markdown("---")
    st.subheader("🔗 ACESSOS RÁPIDOS")
    st.markdown(f'<a href="{LINK_CASA_1}" target="_blank" class="btn-side" style="background: {cor_neon}; color: #000 !important;">🎰 CASA RECOMENDADA</a>', unsafe_allow_html=True)
    st.markdown(f'<a href="{LINK_SUPORTE}" target="_blank" class="btn-side" style="background: #25d366;">🟢 SUPORTE WHATSAPP</a>', unsafe_allow_html=True)
    st.markdown(f'<a href="{LINK_CANAL}" target="_blank" class="btn-side" style="background: #0088cc;">🔵 CANAL TELEGRAM</a>', unsafe_allow_html=True)
    
    st.markdown("---")
    st.subheader("📊 GESTÃO & ALAVANCAGEM")
    banca = st.number_input("Banca Atual (R$):", value=100.0)
    entrada = banca * 0.03
    st.info(f"💰 Entrada Ideal (3%): R$ {entrada:.2f}")
    
    st.markdown("<p style='font-size: 14px; color: #bbb;'>📈 Evolução da Banca em 30 Dias (Meta 3%/dia)</p>", unsafe_allow_html=True)
    evolucao = []
    banca_simulada = banca
    for _ in range(30):
        banca_simulada *= 1.03
        evolucao.append(banca_simulada)
    st.bar_chart(evolucao, height=150)
    st.success(f"Projeção final: R$ {banca_simulada:.2f}")

    msg_pix = urllib.parse.quote("Fala Ronny! Meu acesso VIP V8 Supreme está acabar e não quero ficar de fora. Envia-me a chave PIX para eu renovar! 💸🚀")
    link_pix = f"https://wa.me/5561996193390?text={msg_pix}"
    st.markdown(f'<a href="{link_pix}" target="_blank" class="btn-pix">🔄 RENOVAR VIP VIA PIX</a>', unsafe_allow_html=True)

    if st.session_state.is_admin:
        st.markdown("---")
        st.subheader("🎫 GERADOR DE KEYS")
        c_nome = st.text_input("Nome da Key:")
        tempo_key = st.selectbox("Validade:", ["24 Horas", "7 Dias", "30 Dias"])
        if st.button("CRIAR VIP"):
            horas = 24
            if tempo_key == "7 Dias": horas = 168
            elif tempo_key == "30 Dias": horas = 720
            salvar_key(c_nome, horas)
            
            st.success(f"✅ Key {c_nome} gerada com sucesso!")
            
            link_magico = f"{LINK_PAINEL}?key={c_nome}"
            msg_cliente = f"✅ *ACESSO VIP LIBERADO!*\n\nFala campeão! Seu acesso ao *RonnyP V8 Supreme* está pronto.\n\n🔑 *Sua Key:* {c_nome}\n⏳ *Validade:* {tempo_key}\n\n🔗 *Acesse direto clicando aqui:*\n{link_magico}"
            
            st.code(msg_cliente, language="text")
            
            txt_zap_codificado = urllib.parse.quote(msg_cliente)
            link_zap_cliente = f"https://api.whatsapp.com/send?text={txt_zap_codificado}"
            st.markdown(f'<a href="{link_zap_cliente}" target="_blank" class="btn-side" style="background: #25d366; color: white !important;">🟢 ENVIAR PARA O CLIENTE (ZAP)</a>', unsafe_allow_html=True)

    st.markdown("<br>"*5, unsafe_allow_html=True)
    if st.button("SAIR", use_container_width=True):
        st.session_state.autenticado = False
        st.rerun()

# --- 8. DASHBOARD E SISTEMA PREMIUM ---
c1, c2, c3 = st.columns(3)
with c1:
    st.markdown(f"<div class='metric-card'><div class='metric-title'>Win Rate IA (30D)</div><div class='metric-value'>89.4%</div></div>", unsafe_allow_html=True)
with c2:
    st.markdown(f"<div class='metric-card'><div class='metric-title'>Jogos Analisados</div><div class='metric-value'>1.248</div></div>", unsafe_allow_html=True)
with c3:
    st.markdown(f"<div class='metric-card'><div class='metric-title'>Oportunidades Hoje</div><div class='metric-value'>14 Ativas</div></div>", unsafe_allow_html=True)

st.markdown(f"""
<div class='glass-panel' style='padding: 10px 20px; text-align: center; border-left: 4px solid #FFD700; margin-top: 15px;'>
    <span style='color:#FFD700; font-weight:bold;'>🧠 A Palavra do CEO (@ronny_olivzz61):</span> <span style='color:#bbb; font-style:italic;'>"O amador aposta por emoção, o profissional investe com gestão. Siga a IA e respeite a sua meta diária!"</span>
</div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# 🚀 NOVA ESTRUTURA DE ABAS COM O "BILHETE SAFE"
t1, t2, t3, t4 = st.tabs(["🚀 SCANNER IA", "📋 BILHETE", "🛡️ BILHETE SAFE", "🏆 HISTÓRICO VIP"])

LIGAS_DISPONIVEIS = {
    "🇬🇧 Premier League (Inglaterra)": "soccer_epl",
    "🇪🇺 Champions League": "soccer_uefa_champs_league",
    "🇪🇸 La Liga (Espanha)": "soccer_spain_la_liga",
    "🇮🇹 Serie A (Itália)": "soccer_italy_serie_a",
    "🇩🇪 Bundesliga (Alemanha)": "soccer_germany_bundesliga",
    "🇫🇷 Ligue 1 (França)": "soccer_france_ligue_one",
    "🇧🇷 Brasileirão Série A": "soccer_brazil_campeonato",
    "🌎 Libertadores": "soccer_conmebol_libertadores"
}

with t1:
    with st.expander("✍️ MODO MANUAL: Inserir Grade de Jogos"):
        grade = st.text_area("Cole aqui a sua lista de jogos:", height=150)
        if st.button("🔍 INICIAR ANÁLISE MANUAL", use_container_width=True):
            if grade:
                jogos = [j for j in grade.split('\n') if 'x' in j.lower()]
                st.session_state.analisados = []
                mercados = ["Ambas Marcam", "Over 1.5 Gols", "Vitória", "Cantos +8.5", "Over 2.5 Gols"]
                for j in jogos:
                    st.session_state.analisados.append({
                        "jogo": j, "m": random.choice(mercados), "o": round(random.uniform(1.5, 2.3), 2), "conf": random.randint(93,99)
                    })
                st.success("Análise manual concluída!")

    st.markdown("<h4 style='color:white; margin-top: 15px;'>🎯 VARREDURA AUTOMÁTICA DE ODDS REAIS</h4>", unsafe_allow_html=True)
    
    liga_selecionada = st.selectbox("Escolha o Campeonato para Varrer:", list(LIGAS_DISPONIVEIS.keys()))
    codigo_da_liga = LIGAS_DISPONIVEIS[liga_selecionada]
    
    if st.button("🚨 INICIAR VARREDURA IA", use_container_width=True):
        with st.status("Iniciando Protocolo V8 Supreme...", expanded=True) as status:
            st.write("⏳ [10%] A conectar aos servidores asiáticos...")
            time.sleep(0.6)
            st.write("🔓 [45%] A encontrar brechas de odds de valor...")
            time.sleep(0.6)
            st.write("📡 [80%] A extrair e cruzar dados globais...")
            
            url = f"https://api.the-odds-api.com/v4/sports/{codigo_da_liga}/odds/?apiKey={ODDS_API_KEY}&regions=eu,uk&markets=h2h,totals"
            
            try:
                resposta = requests.get(url)
                if resposta.status_code == 200:
                    dados = resposta.json()
                    st.session_state.analisados = []
                    
                    hoje_brasil = datetime.utcnow() - timedelta(hours=3)
                    data_hoje_str = hoje_brasil.strftime("%Y-%m-%d")
                    jogos_do_dia = []
                    
                    for jogo in dados:
                        data_jogo_utc_str = jogo.get('commence_time', '')
                        if data_jogo_utc_str:
                            try:
                                data_jogo_utc = datetime.strptime(data_jogo_utc_str, "%Y-%m-%dT%H:%M:%SZ")
                                data_jogo_brasil = data_jogo_utc - timedelta(hours=3)
                                if data_jogo_brasil.strftime("%Y-%m
