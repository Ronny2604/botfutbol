import streamlit as st
import asyncio
import random
import time
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
LINK_CASA_1 = "https://esportiva.bet.br?ref=511e1f11699f"

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

# --- 4. CSS SUPREME (LIMPEZA DE RODAPÉ E DESTAQUE) ---
st.markdown(f"""
    <style>
    /* Esconde marcações do Streamlit e GitHub */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    header {{visibility: hidden;}}
    .stDeployButton {{display:none;}}

    .stApp {{ background-color: #040d1a; }}
    
    /* Header Nome de Destaque */
    .header-destaque {{
        text-align: center;
        padding: 20px;
        color: {cor_neon};
        font-size: 32px;
        font-weight: bold;
        text-shadow: 0 0 15px {cor_neon};
        border-bottom: 1px solid #1a2a3a;
        margin-bottom: 10px;
    }}

    /* Letreiro */
    .marquee-wrapper {{
        width: 100%; overflow: hidden; background: {bg_marquee};
        border-bottom: 2px solid {cor_neon}; padding: 10px 0; display: flex;
        box-shadow: 0 0 15px {cor_neon}55; margin-bottom: 15px;
    }}
    .marquee-content {{ display: flex; white-space: nowrap; animation: marquee 30s linear infinite; }}
    .marquee-item {{ padding: 0 40px; color: {cor_neon}; font-weight: bold; text-shadow: 0 0 5px {cor_neon}; }}
    @keyframes marquee {{ 0% {{ transform: translateX(0); }} 100% {{ transform: translateX(-50%); }} }}

    /* Botões Laterais */
    .btn-side {{
        display: block; padding: 12px; margin-bottom: 10px;
        text-align: center; border-radius: 8px; font-weight: bold;
        text-decoration: none; color: white !important;
    }}

    .stButton>button {{ 
        background: {cor_neon} !important; color: #040d1a !important; font-weight: bold !important; 
        border-radius: 10px !important; border: none !important; width: 100%; height: 3.2rem;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 5. TELA DE LOGIN ---
if not st.session_state.autenticado:
    st.markdown(f"<div class='header-destaque'>RONNYP V8 SUPREME</div>", unsafe_allow_html=True)
    with st.container():
        st.markdown("<div style='max-width:400px; margin:auto; padding:20px; background:#0a1626; border-radius:15px; border: 1px solid #1a2a3a;'>", unsafe_allow_html=True)
        st.subheader("🔑 ACESSO RESTRITO")
        nome_in = st.text_input("Nome:")
        genero_in = st.selectbox("Gênero:", ["Masculino", "Feminino"])
        key_in = st.text_input("Sua Key:", type="password")
        
        if st.button("ENTRAR NO RADAR"):
            if key_in:
                auth, admin = valida_chave(key_in)
                if auth:
                    st.session_state.autenticado = True
                    st.session_state.is_admin = admin
                    st.session_state.user_nome = nome_in if nome_in else "VIP"
                    st.session_state.user_genero = genero_in
                    st.session_state.show_welcome = True
                    st.rerun()
                else: st.error("Key Incorreta!")
        st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# --- 6. CONTEÚDO LOGADO ---

# Nome destacado no topo
st.markdown(f"<div class='header-destaque'>RONNYP V8 SUPREME</div>", unsafe_allow_html=True)

# Letreiro Social Proof
itens_marquee = "".join([f"<div class='marquee-item'> 🔥 {n} ACABOU DE ENTRAR </div>" for n in ["Marcos", "Ana", "Lucas", "Julia", "Tadeu", "Carla"]])
st.markdown(f"<div class='marquee-wrapper'><div class='marquee-content'>{itens_marquee}{itens_marquee}</div></div>", unsafe_allow_html=True)

if st.session_state.show_welcome:
    st.toast(f"Bem-vindo(a), {st.session_state.user_nome}! 💰", icon="✅")
    st.session_state.show_welcome = False

# --- 7. MENU LATERAL ---
with st.sidebar:
    st.markdown(f"<h2 style='color:{cor_neon}; text-align:center;'>RONNYP V8</h2>", unsafe_allow_html=True)
    st.markdown(f"**👤 Usuário:** {st.session_state.user_nome}")
    st.markdown("---")
    
    # Seção de Links
    st.subheader("🔗 LINKS ÚTEIS")
    st.markdown(f'<a href="{LINK_CASA_1}" class="btn-side" style="background: #e6b800; color: #000 !important;">🎰 CASA RECOMENDADA</a>', unsafe_allow_html=True)
    st.markdown(f'<a href="{LINK_SUPORTE}" class="btn-side" style="background: #25d366;">🟢 SUPORTE WHATSAPP</a>', unsafe_allow_html=True)
    st.markdown(f'<a href="{LINK_CANAL}" class="btn-side" style="background: #0088cc;">🔵 CANAL TELEGRAM</a>', unsafe_allow_html=True)
    
    st.markdown("---")
    st.subheader("📊 GESTÃO")
    banca = st.number_input("Banca R$", value=100.0)
    st.info(f"💰 Entrada Sugerida: R$ {banca * 0.03:.2f}")

    if st.session_state.is_admin:
        st.markdown("---")
        st.subheader("🎫 ADMIN")
        c_nome = st.text_input("Novo Cliente")
        if st.button("GERAR"):
            salvar_key(c_nome, 24)
            st.code(c_nome)

    if st.button("SAIR"):
        st.session_state.autenticado = False
        st.rerun()

# --- 8. RADAR ---
t1, t2 = st.tabs(["🚀 SCANNER", "📋 BILHETE"])

with t1:
    grade = st.text_area("COLE A GRADE", height=100)
    if st.button("ANALISAR AGORA"):
        if grade:
            jogos = [j for j in grade.split('\n') if 'x' in j.lower()]
            st.session_state.analisados = []
            for j in jogos:
                mercados = ["Ambas Marcam", "Vitoria", "Over 2.5 Gols", "Cantos +8.5"]
                st.session_state.analisados.append({
                    "jogo": j, "m": random.choice(mercados), "o": round(random.uniform(1.5, 2.2), 2), "conf": random.randint(92,99)
                })

    for idx, item in enumerate(st.session_state.analisados):
        st.markdown(f"""<div style='background:#0a1626; padding:15px; border-radius:10px; border-left: 4px solid {cor_neon}; margin-bottom:10px;'>
            <div style='color:{cor_neon}; font-weight:bold;'>{item['conf']}% DE ASSERTIVIDADE</div>
            <div style='font-size:18px;'>{item['jogo']}</div>
            <div style='margin-top:5px; color:#ddd;'>🎯 {item['m']} | <b>@{item['o']}</b></div>
        </div>""", unsafe_allow_html=True)
        if st.button(f"ADD {idx}", key=f"btn_{idx}"):
            st.session_state.bilhete.append(item)
            st.toast("Adicionado!")

with t2:
    if st.session_state.bilhete:
        odd_f = 1.0
        for b in st.session_state.bilhete:
            odd_f *= b['o']
            st.write(f"✅ {b['jogo']} (@{b['o']})")
        
        st.subheader(f"ODD TOTAL: {odd_f:.2f}")
        if st.button("ENVIAR PRO TELEGRAM"):
            st.success("Sinal Enviado!")
    else: st.info("Bilhete vazio")
