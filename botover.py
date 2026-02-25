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

# --- 3. INICIALIZAÇÃO ---
if 'autenticado' not in st.session_state: st.session_state.autenticado = False
if 'user_nome' not in st.session_state: st.session_state.user_nome = ""
if 'user_genero' not in st.session_state: st.session_state.user_genero = "Masculino"
if 'bilhete' not in st.session_state: st.session_state.bilhete = []
if 'analisados' not in st.session_state: st.session_state.analisados = []
if 'show_welcome' not in st.session_state: st.session_state.show_welcome = False

db_keys = carregar_keys()

def valida_chave(chave):
    if chave == MASTER_KEY: return True, True
    if chave in db_keys:
        if datetime.now() < db_keys[chave]: return True, False
    return False, False

# Cores Dinâmicas
is_fem = st.session_state.user_genero == "Feminino"
cor_neon = "#ff00ff" if is_fem else "#00ff00"
bg_marquee = "#1a001a" if is_fem else "#00120a"

# --- 4. CSS SUPREME ---
st.markdown(f"""
    <style>
    #MainMenu {{visibility: hidden !important;}}
    .stDeployButton {{display:none !important;}}
    footer {{visibility: hidden !important;}}
    [data-testid="stActionButtonIcon"] {{display: none !important;}}
    header[data-testid="stHeader"] {{ background-color: rgba(4, 13, 26, 0.9) !important; border-bottom: 1px solid {cor_neon}33; }}
    .stApp {{ background-color: #040d1a; }}
    .header-destaque {{ text-align: center; padding: 10px; color: {cor_neon}; font-size: 26px; font-weight: bold; text-shadow: 0 0 15px {cor_neon}; margin-top: -20px; }}
    .marquee-wrapper {{ width: 100%; overflow: hidden; background: {bg_marquee}; border-bottom: 2px solid {cor_neon}; padding: 10px 0; display: flex; margin-bottom: 15px; }}
    .marquee-content {{ display: flex; white-space: nowrap; animation: marquee 30s linear infinite; }}
    .marquee-item {{ padding: 0 40px; color: {cor_neon}; font-weight: bold; text-shadow: 0 0 5px {cor_neon}; }}
    @keyframes marquee {{ 0% {{ transform: translateX(0); }} 100% {{ transform: translateX(-50%); }} }}
    .btn-side {{ display: block; padding: 12px; margin-bottom: 10px; text-align: center; border-radius: 8px; font-weight: bold; text-decoration: none; color: white !important; font-size: 14px; }}
    .stButton>button {{ background: {cor_neon} !important; color: #040d1a !important; font-weight: bold !important; border-radius: 10px !important; border: none !important; }}
    </style>
    """, unsafe_allow_html=True)

# --- 5. TELA DE LOGIN ---
if not st.session_state.autenticado:
    st.markdown(f"<div class='header-destaque'>RONNYP V8 SUPREME</div>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    with st.container():
        st.markdown("<div style='max-width:400px; margin:auto; padding:25px; background:#0a1626; border-radius:20px; border: 1px solid #1a2a3a;'>", unsafe_allow_html=True)
        st.markdown(f"<h3 style='text-align:center; color:{cor_neon};'>ACESSO VIP</h3>", unsafe_allow_html=True)
        nome_in = st.text_input("Seu Nome:")
        genero_in = st.selectbox("Gênero:", ["Masculino", "Feminino"])
        key_in = st.text_input("Sua Key:", type="password")
        
        if st.button("ACESSAR RADAR"):
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
    st.toast(f"Bem-vindo(a), {st.session_state.user_nome}! 💰")
    st.balloons()
    st.session_state.show_welcome = False

# --- 7. MENU LATERAL & ADMIN ---
with st.sidebar:
    st.markdown(f"<h1 style='color:{cor_neon}; text-align:center; text-shadow: 0 0 10px {cor_neon}; margin-top:-30px;'>RONNYP V8</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align:center;'>👤 <b>{st.session_state.user_nome}</b></p>", unsafe_allow_html=True)
    st.markdown("---")
    
    st.subheader("🔗 ACESSOS RÁPIDOS")
    st.markdown(f'<a href="{LINK_CASA_1}" target="_blank" class="btn-side" style="background: #e6b800; color: #000 !important;">🎰 CASA RECOMENDADA</a>', unsafe_allow_html=True)
    st.markdown(f'<a href="{LINK_SUPORTE}" target="_blank" class="btn-side" style="background: #25d366;">🟢 SUPORTE WHATSAPP</a>', unsafe_allow_html=True)
    st.markdown(f'<a href="{LINK_CANAL}" target="_blank" class="btn-side" style="background: #0088cc;">🔵 CANAL TELEGRAM</a>', unsafe_allow_html=True)
    
    st.markdown("---")
    st.subheader("📊 GESTÃO")
    banca = st.number_input("Banca R$", value=100.0)
    st.info(f"💰 Entrada (3%): R$ {banca * 0.03:.2f}")

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
            st.success(f"Key criada! Validade: {tempo_key}")
            st.code(c_nome)

    st.markdown("<br>"*5, unsafe_allow_html=True)
    if st.button("SAIR"):
        st.session_state.autenticado = False
        st.rerun()

# --- 8. RADAR E SISTEMA PREMIUM ---
# ADICIONAMOS A TERCEIRA ABA (HISTÓRICO VIP)
t1, t2, t3 = st.tabs(["🚀 SCANNER IA", "📋 BILHETE", "🏆 HISTÓRICO VIP"])

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
    grade = st.text_area("COLE A GRADE (Para uso manual)", height=60)
    st.markdown("---")
    st.markdown("<h4 style='color:white;'>🎯 VARREDURA PROFUNDA DE MERCADOS</h4>", unsafe_allow_html=True)
    
    liga_selecionada = st.selectbox("Escolha o Campeonato:", list(LIGAS_DISPONIVEIS.keys()))
    codigo_da_liga = LIGAS_DISPONIVEIS[liga_selecionada]
    
    col1, col2 = st.columns(2)
    with col1:
        btn_manual = st.button("INICIAR MANUAL")
    with col2:
        btn_api = st.button("🚨 BUSCAR ODDS REAIS")

    if btn_manual:
        if grade:
            jogos = [j for j in grade.split('\n') if 'x' in j.lower()]
            st.session_state.analisados = []
            mercados = ["Ambas Marcam", "Over 1.5 Gols", "Vitória", "Cantos +8.5", "Over 2.5 Gols"]
            for j in jogos:
                st.session_state.analisados.append({
                    "jogo": j, "m": random.choice(mercados), "o": round(random.uniform(1.5, 2.3), 2), "conf": random.randint(93,99)
                })
                
    if btn_api:
        with st.status(f"Analisando jogos da {liga_selecionada}...", expanded=True) as status:
            st.write("📡 Conectando com a base de dados esportiva...")
            
            url = f"https://api.the-odds-api.com/v4/sports/{codigo_da_liga}/odds/?apiKey={ODDS_API_KEY}&regions=eu,uk&markets=h2h,totals"
            
            try:
                resposta = requests.get(url)
                if resposta.status_code == 200:
                    st.write("🔍 Processando estatísticas de Gols e Probabilidades de Vitória...")
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
                                if data_jogo_brasil.strftime("%Y-%m-%d") == data_hoje_str:
                                    jogos_do_dia.append(jogo)
                            except: pass
                    
                    for jogo in jogos_do_dia[:20]:
                        casa = jogo.get('home_team', 'Casa')
                        fora = jogo.get('away_team', 'Fora')
                        
                        hora_jogo = ""
                        try:
                            dj_utc = datetime.strptime(jogo.get('commence_time', ''), "%Y-%m-%dT%H:%M:%SZ")
                            dj_br = dj_utc - timedelta(hours=3)
                            hora_jogo = dj_br.strftime("%H:%M")
                        except: pass
                        
                        nome_jogo = f"🕒 {hora_jogo} | {casa} x {fora}"
                        mercados_encontrados = []
                        
                        if jogo.get('bookmakers'):
                            for bookie in jogo['bookmakers']:
                                for mercado in bookie.get('markets', []):
                                    if mercado['key'] == 'h2h':
                                        for out in mercado['outcomes']:
                                            if out['name'] == casa: mercados_encontrados.append({"m": f"Vitória {casa}", "o": out['price']})
                                            elif out['name'] == fora: mercados_encontrados.append({"m": f"Vitória {fora}", "o": out['price']})
                                            elif out['name'].lower() == 'draw': mercados_encontrados.append({"m": "Empate", "o": out['price']})
                                    elif mercado['key'] == 'totals':
                                        for out in mercado['outcomes']:
                                            pt = out.get('point', 0)
                                            if out['name'] == 'Over':
                                                mercados_encontrados.append({"m": f"Over {pt
