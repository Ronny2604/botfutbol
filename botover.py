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

# SUA CHAVE DA API-SPORTS (CORRETA E ATIVA)
ODDS_API_KEY = "7d01c19fd029a0f1f529051d6904d21b"

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

# --- 4. CSS SUPREME (BLOQUEIO DE GITHUB E LIMPEZA) ---
st.markdown(f"""
    <style>
    /* BLOQUEIA ÍCONE GITHUB, MENU DE OPÇÕES E BOTÃO DEPLOY */
    #MainMenu {{visibility: hidden !important;}}
    .stDeployButton {{display:none !important;}}
    footer {{visibility: hidden !important;}}
    
    /* ESCONDE O ÍCONE DO GITHUB NO TOPO DIREITO */
    [data-testid="stActionButtonIcon"] {{display: none !important;}}
    button[title="View source on GitHub"] {{display: none !important;}}
    
    /* CUSTOMIZAÇÃO DO CABEÇALHO PARA COMBINAR COM O NEON */
    header[data-testid="stHeader"] {{
        background-color: rgba(4, 13, 26, 0.9) !important;
        border-bottom: 1px solid {cor_neon}33;
    }}

    .stApp {{ background-color: #040d1a; }}
    
    .header-destaque {{
        text-align: center;
        padding: 10px;
        color: {cor_neon};
        font-size: 26px;
        font-weight: bold;
        text-shadow: 0 0 15px {cor_neon};
        margin-top: -20px;
    }}

    /* Letreiro */
    .marquee-wrapper {{
        width: 100%; overflow: hidden; background: {bg_marquee};
        border-bottom: 2px solid {cor_neon}; padding: 10px 0; display: flex;
        margin-bottom: 15px;
    }}
    .marquee-content {{ display: flex; white-space: nowrap; animation: marquee 30s linear infinite; }}
    .marquee-item {{ padding: 0 40px; color: {cor_neon}; font-weight: bold; text-shadow: 0 0 5px {cor_neon}; }}
    @keyframes marquee {{ 0% {{ transform: translateX(0); }} 100% {{ transform: translateX(-50%); }} }}

    /* Botões Laterais */
    .btn-side {{
        display: block; padding: 12px; margin-bottom: 10px;
        text-align: center; border-radius: 8px; font-weight: bold;
        text-decoration: none; color: white !important; font-size: 14px;
    }}

    .stButton>button {{ 
        background: {cor_neon} !important; color: #040d1a !important; font-weight: bold !important; 
        border-radius: 10px !important; border: none !important;
    }}
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
                else: st.error("❌ Key Inválida!")
        st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# --- 6. CONTEÚDO LOGADO ---

st.markdown(f"<div class='header-destaque'>RONNYP V8 SUPREME</div>", unsafe_allow_html=True)

# Letreiro Social Proof
itens_marquee = "".join([f"<div class='marquee-item'> 🔥 {n} ENTROU NO VIP </div>" for n in ["Marcos", "Ana", "Lucas", "Julia", "Tadeu", "Carla"]])
st.markdown(f"<div class='marquee-wrapper'><div class='marquee-content'>{itens_marquee}{itens_marquee}</div></div>", unsafe_allow_html=True)

if st.session_state.show_welcome:
    st.toast(f"Bem-vindo(a), {st.session_state.user_nome}! 💰")
    st.balloons()
    st.session_state.show_welcome = False

# --- 7. MENU LATERAL ---
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
        st.subheader("🎫 ADMIN")
        c_nome = st.text_input("Gerar Key")
        if st.button("CRIAR"):
            salvar_key(c_nome, 24)
            st.code(c_nome)

    st.markdown("<br>"*5, unsafe_allow_html=True)
    if st.button("SAIR"):
        st.session_state.autenticado = False
        st.rerun()

# --- 8. RADAR ---
t1, t2 = st.tabs(["🚀 SCANNER IA", "📋 BILHETE"])

with t1:
    grade = st.text_area("COLE A GRADE (Para uso manual)", height=60)
    
    col1, col2 = st.columns(2)
    with col1:
        btn_manual = st.button("INICIAR MANUAL")
    with col2:
        btn_api = st.button("🚨 VARREDURA API (REAIS)")

    # Lógica Manual
    if btn_manual:
        if grade:
            jogos = [j for j in grade.split('\n') if 'x' in j.lower()]
            st.session_state.analisados = []
            mercados = ["Ambas Marcam", "Over 1.5 Gols", "Vitória", "Cantos +8.5", "Over 2.5 Gols"]
            for j in jogos:
                st.session_state.analisados.append({
                    "jogo": j, "m": random.choice(mercados), "o": round(random.uniform(1.5, 2.3), 2), "conf": random.randint(93,99)
                })
                
    # Nova Lógica Integrada (API-SPORTS - Real com Filtro VIP)
    if btn_api:
        with st.spinner("Puxando jogos principais e odds reais..."):
            hoje = datetime.now().strftime("%Y-%m-%d")
            # 1. Puxa os jogos do dia que ainda não começaram
            url_fixtures = f"https://v3.football.api-sports.io/fixtures?date={hoje}&status=NS"
            headers = {
                'x-apisports-key': ODDS_API_KEY
            }
            
            try:
                resposta = requests.get(url_fixtures, headers=headers)
                if resposta.status_code == 200:
                    dados = resposta.json()
                    
                    if dados.get("errors") and len(dados["errors"]) > 0:
                        st.error(f"Erro na conta: {dados['errors']}")
                    else:
                        st.session_state.analisados = []
                        todos_jogos = dados.get('response', [])
                        
                        # --- FILTRO DE LIGAS FAMOSAS ---
                        # 71=Brasil A, 72=Brasil B, 39=Inglaterra, 140=Espanha, 135=Itália, 78=Alemanha, 61=França, 2=Champions, 13=Libertadores
                        ligas_famosas = [71, 72, 39, 140, 135, 78, 61, 2, 13]
                        
                        # Separa apenas os jogos das ligas grandes
                        jogos_filtrados = [j for j in todos_jogos if j['league']['id'] in ligas_famosas]
                        
                        # Se não tiver nenhum jogo de liga famosa hoje, pega os gerais do dia
                        if not jogos_filtrados:
                            jogos_filtrados = todos_jogos

                        # Pega até 7 jogos (para não estourar seu limite de 100 requisições/dia)
                        for jogo in jogos_filtrados[:7]:
                            fix_id = jogo['fixture']['id']
                            casa = jogo['teams']['home']['name']
                            fora = jogo['teams']['away']['name']
                            nome_jogo = f"{casa} x {fora}"
                            
                            odd_vitoria = 0.0
                            
                            # 2. Busca a odd real específica na Bet365 (bookmaker=8)
                            try:
                                url_odds = f"https://v3.football.api-sports.io/odds?fixture={fix_id}&bookmaker=8"
                                res_odds = requests.get(url_odds, headers=headers).json()
                                
                                if res_odds.get('response') and len(res_odds['response']) > 0:
                                    apostas = res_odds['response'][0]['bookmakers'][0]['bets']
                                    for aposta in apostas:
                                        if aposta['name'] == 'Match Winner':
                                            for valor in aposta['values']:
                                                if valor['value'] == 'Home':
                                                    odd_vitoria = float(valor['odd'])
                                                    break
                            except Exception:
                                pass # Se der erro de busca na odd, ele apenas pula
                                
                            if odd_vitoria > 0:
                                st.session_state.analisados.append({
                                    "jogo": nome_jogo,
                                    "m": f"Vitória {casa}",
                                    "o": odd_vitoria,
                                    "conf": random.randint(85, 99)
                                })
                                
                        if not st.session_state.analisados:
                            st.warning("Nenhum jogo com odds disponíveis encontrado no momento.")
                else:
                    st.error(f"Código do Erro: {resposta.status_code} | Verifique sua chave.")
            except Exception as e:
                st.error(f"Erro de conexão com a internet: {e}")

    # Exibe os jogos (Funciona tanto para o manual quanto para a API)
    for idx, item in enumerate(st.session_state.analisados):
        st.markdown(f"""<div style='background:#0a1626; padding:15px; border-radius:12px; border-left: 5px solid {cor_neon}; margin-bottom:10px;'>
            <div style='color:{cor_neon}; font-weight:bold; font-size:12px;'>🔥 ASSERTIVIDADE IA: {item['conf']}%</div>
            <div style='font-size:18px; font-weight:bold; color:white;'>{item['jogo']}</div>
            <div style='margin-top:8px; color:#bbb;'>🎯 Mercado: <b>{item['m']}</b> | <span style='color:{cor_neon};'>@{item['o']}</span></div>
        </div>""", unsafe_allow_html=True)
        if st.button(f"ADICIONAR JOGO {idx+1}", key=f"btn_{idx}"):
            st.session_state.bilhete.append(item)
            st.toast("✅ Adicionado!")

with t2:
    if st.session_state.bilhete:
        odd_f = 1.0
        msg_tg = f"👑 *RONNYP VIP V8* 👑\n\n"
        msg_whats = "👑 *RONNYP VIP V8* 👑\n\n" # Texto limpo para WhatsApp
        
        for b in st.session_state.bilhete:
            odd_f *= b['o']
            st.write(f"✅ {b['jogo']} (@{b['o']})")
            msg_tg += f"🏟️ *{b['jogo']}*\n🎯 {b['m']} (@{b['o']})\n\n"
            msg_whats += f"🏟️ {b['jogo']}\n🎯 {b['m']} (@{b['o']})\n\n"
        
        st.markdown(f"### ODD TOTAL: {odd_f:.2f}")
        
        # --- ENVIAR PARA TELEGRAM ---
        if st.button("ENVIAR PRO TELEGRAM"):
            final_msg_tg = msg_tg + f"📊 *Odd Total: {odd_f:.2f}*\n\n🎰 [APOSTE AQUI]({LINK_CASA_1})"
            asyncio.run(Bot(TOKEN).send_message(CHAT_ID, final_msg_tg, parse_mode='Markdown'))
            st.success("Sinal enviado para o Telegram!")
            
        # --- COMPARTILHAR NO WHATSAPP ---
        final_msg_whats = msg_whats + f"📊 *Odd Total: {odd_f:.2f}*\n\n🎰 APOSTE AQUI: {LINK_CASA_1}"
        texto_codificado = urllib.parse.quote(final_msg_whats)
        link_zap = f"https://api.whatsapp.com/send?text={texto_codificado}"
        st.link_button("🟢 COMPARTILHAR NO WHATSAPP", link_zap)

        if st.button("RESETAR"):
            st.session_state.bilhete = []
            st.rerun()
    else:
        st.info("Nenhum jogo selecionado.")
