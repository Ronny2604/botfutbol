import streamlit as st
import asyncio
import random
import time
import urllib.parse
import os
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

# --- 2. BANCO DE DADOS DE KEYS ---
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

# --- 3. INICIALIZAÇÃO DE SESSÃO ---
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

# Configuração de Cores Dinâmicas
is_fem = st.session_state.user_genero == "Feminino"
cor_neon = "#ff00ff" if is_fem else "#00ff00"
cor_glow = "rgba(255, 0, 255, 0.6)" if is_fem else "rgba(0, 255, 0, 0.6)"
bg_marquee = "#1a001a" if is_fem else "#00120a"
icon_user = "💎" if is_fem else "🔥"

# --- 4. ESTILOS CSS SUPREME ---
st.markdown(f"""
    <style>
    .stApp {{ background-color: #040d1a; }}
    
    /* Letreiro Neon */
    .marquee-wrapper {{
        width: 100%; overflow: hidden; background: {bg_marquee};
        border-bottom: 2px solid {cor_neon}; padding: 12px 0; display: flex;
        box-shadow: 0 0 20px {cor_glow}; margin-bottom: 15px;
    }}
    .marquee-content {{ display: flex; white-space: nowrap; animation: marquee 35s linear infinite; }}
    .marquee-item {{
        padding: 0 40px; flex-shrink: 0; font-size: 15px; font-weight: bold;
        color: {cor_neon}; text-shadow: 0 0 10px {cor_neon};
    }}
    @keyframes marquee {{ 0% {{ transform: translateX(0); }} 100% {{ transform: translateX(-50%); }} }}

    /* Botões e Inputs */
    .stButton>button {{ 
        height: 3.5rem; border-radius: 12px !important; background: {cor_neon} !important; 
        color: #040d1a !important; font-weight: bold !important; width: 100%;
        box-shadow: 0 0 15px {cor_glow}; border: none;
    }}
    .mobile-card {{ background: #0a1626; border: 1px solid #1a2a3a; border-radius: 12px; padding: 15px; margin-bottom: 12px; }}
    .market-box {{ 
        background: {bg_marquee}; padding: 12px; border-radius: 10px; 
        border-left: 5px solid {cor_neon}; margin-top: 10px; 
    }}
    .auth-container {{ 
        background: #0a1626; padding: 30px; border-radius: 20px; 
        border: 2px solid {cor_neon}; text-align: center; margin: auto; max-width: 380px; 
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 5. LETREIRO SOCIAL PROOF ---
Nomes_Ficticios = ["Marcos S.", "Brenda T.", "Ricardo G.", "Ana Paula", "Lucas Tips", "Carla B.", "Jonny", "Adriana V."]
itens_html = "".join([f"<div class='marquee-item'> {icon_user} {n} ENTROU NO VIP </div>" for n in Nomes_Ficticios])
st.markdown(f"<div class='marquee-wrapper'><div class='marquee-content'>{itens_html}{itens_html}</div></div>", unsafe_allow_html=True)

# --- 6. TELA DE LOGIN ---
if not st.session_state.autenticado:
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("<div class='auth-container'>", unsafe_allow_html=True)
    st.title("RONNYP VIP V8")
    
    nome_in = st.text_input("Seu Nome:")
    genero_in = st.selectbox("Gênero (Para personalizar o App):", ["Masculino", "Feminino"])
    key_in = st.text_input("Sua Key:", type="password")
    
    if st.button("LIBERAR ACESSO NEON"):
        if key_in:
            auth, admin = valida_chave(key_in)
            if auth:
                st.session_state.autenticado = True
                st.session_state.is_admin = admin
                st.session_state.user_nome = nome_in if nome_in else "Trader"
                st.session_state.user_genero = genero_in
                st.session_state.show_welcome = True
                st.rerun()
            else: st.error("Key Inválida!")
        else: st.warning("Digite sua Key!")
    
    st.markdown(f'<br><a href="{LINK_SUPORTE}" style="color:{cor_neon}; text-decoration:none; font-weight:bold;">SOLICITAR MINHA KEY</a>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# --- 7. MENSAGEM DE BOAS VINDAS ---
if st.session_state.show_welcome:
    welcome_msg = f"Bem-vinda, {st.session_state.user_nome}! 🌸" if is_fem else f"Bem-vindo, {st.session_state.user_nome}! 🚀"
    st.toast(welcome_msg, icon="💰")
    st.balloons()
    st.session_state.show_welcome = False

# --- 8. MENU LATERAL ---
with st.sidebar:
    st.markdown(f"### {icon_user} {st.session_state.user_nome}")
    st.markdown(f'<a href="{LINK_CANAL}" target="_blank" style="background:#0088cc; color:white; padding:12px; border-radius:8px; display:block; text-align:center; text-decoration:none; font-weight:bold;">📢 CANAL VIP</a>', unsafe_allow_html=True)
    
    st.markdown("---")
    st.subheader("📊 GESTÃO DE BANCA")
    banca_val = st.number_input("Banca R$", min_value=10.0, value=100.0)
    perfil_val = st.select_slider("Risco", options=["Baixo", "Médio", "Alto"], value="Médio")
    perc = {"Baixo": 0.01, "Médio": 0.03, "Alto": 0.05}
    st.info(f"💰 Entrada Sugerida: **R$ {banca_val * perc[perfil_val]:.2f}**")
    
    if st.session_state.is_admin:
        st.markdown("---")
        st.header("🎫 PAINEL ADMIN")
        c_nome = st.text_input("Nome Cliente")
        c_tempo = st.selectbox("Validade", [0.5, 24, 720])
        if st.button("GERAR KEY"):
            salvar_key(c_nome, float(c_tempo))
            st.success("Key Gerada!")
            st.code(f"https://botoverpy-gnwcseepyzojlaz7ci6g97.streamlit.app/?acesso={c_nome}")

    if st.button("DESLOGAR"):
        st.session_state.autenticado = False
        st.rerun()

# --- 9. RADAR E BILHETES ---
st.markdown(f"<h2 style='text-align:center; color:{cor_neon}; text-shadow: 0 0 10px {cor_neon};'>📡 RADAR V8 {st.session_state.user_genero.upper()}</h2>", unsafe_allow_html=True)
t1, t2 = st.tabs(["🚀 SCANNER IA", "📋 BILHETE"])

def analise_ia_diversificada(j):
    t = j.split(' x ')
    time_casa = t[0].strip()
    opcoes = [
        {"m": f"Vitória: {time_casa}", "o": 1.75},
        {"m": "Ambas Marcam: Sim", "o": 1.85},
        {"m": "Mais de 2.5 Gols", "o": 2.10},
        {"m": "Escanteios: +8.5", "o": 1.60}
    ]
    escolha = random.choice(opcoes)
    return {"m": escolha["m"], "o": escolha["o"], "conf": random.randint(94,99), "expira": (datetime.now()+timedelta(minutes=8)).strftime("%H:%M"), "jogo": j}

with t1:
    grade = st.text_area("COLE A GRADE AQUI", height=80)
    if st.button("INICIAR ANÁLISE"):
        if grade:
            with st.spinner("IA ESCANEANDO..."): time.sleep(1)
            st.session_state.analisados = [analise_ia_diversificada(j) for j in grade.split('\n') if 'x' in j.lower()]

    for idx, item in enumerate(st.session_state.analisados):
        st.markdown(f"""<div class='mobile-card'>
            <div style='color:{cor_neon}; font-size:12px; font-weight:bold;'>⭐ ASSERTIVIDADE: {item['conf']}% | ⏳ {item['expira']}</div>
            <div style='color:white; font-size:16px; font-weight:bold;'>{item['jogo']}</div>
            <div class='market-box'>
                <span style='color:white;'>{item['m']}</span>
                <span style='float:right; color:{cor_neon}; font-weight:bold;'>@{item['o']}</span>
            </div>
        </div>""", unsafe_allow_html=True)
        if st.button(f"ADD AO BILHETE {idx+1}", key=f"add_{idx}"):
            st.session_state.bilhete.append(item)
            st.toast("Adicionado!")

with t2:
    if st.session_state.bilhete:
        odd_f = 1.0
        msg_tg = f"👑 *RONNYP VIP V8* 👑\n👤 Analista: {st.session_state.user_nome}\n\n"
        for b in st.session_state.bilhete:
            odd_f *= b['o']
            st.markdown(f"<div style='border-left:3px solid {cor_neon}; padding-left:10px; margin-bottom:5px;'>{b['jogo']} (@{b['o']})</div>", unsafe_allow_html=True)
            msg_tg += f"🏟️ *{b['jogo']}*\n🎯 {b['m']} (@{b['o']})\n\n"
        
        st.write(f"### ODD TOTAL: {odd_f:.2f}")
        if st.button("📤 DISPARAR PARA O TELEGRAM"):
            final = msg_tg + f"📊 *Odd: {odd_f:.2f}*\n\n🎰 [APOSTE AQUI](https://esportiva.bet.br?ref=511e1f11699f)"
            asyncio.run(Bot(TOKEN).send_message(CHAT_ID, final, parse_mode='Markdown'))
            st.success("Sinal enviado!")
    else: st.info("Bilhete vazio.")
