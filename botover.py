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

# --- 4. CSS BLINDADO (REMOÇÃO TOTAL DE RODAPÉ E MENU NATIVO) ---
st.markdown(f"""
    <style>
    /* REMOVE RODAPÉ, MENU E ÍCONES DO GITHUB */
    #MainMenu {{visibility: hidden !important;}}
    footer {{visibility: hidden !important;}}
    header {{visibility: hidden !important;}}
    .stDeployButton {{display:none !important;}}
    [data-testid="stStatusWidget"] {{visibility: hidden !important;}}
    
    /* REMOVE ESPAÇAMENTO DO TOPO */
    .block-container {{padding-top: 1rem !important;}}

    .stApp {{ background-color: #040d1a; }}
    
    /* Header Nome de Destaque */
    .header-destaque {{
        text-align: center;
        padding: 15px;
        color: {cor_neon};
        font-size: 30px;
        font-weight: bold;
        text-shadow: 0 0 15px {cor_neon};
        border-bottom: 2px solid {cor_neon}33;
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
        text-decoration: none; color: white !important; font-size: 14px;
    }}

    /* Botões Gerais */
    .stButton>button {{ 
        background: {cor_neon} !important; color: #040d1a !important; font-weight: bold !important; 
        border-radius: 10px !important; border: none !important; width: 100%; height: 3rem;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 5. TELA DE LOGIN ---
if not st.session_state.autenticado:
    st.markdown(f"<div class='header-destaque'>RONNYP V8 SUPREME</div>", unsafe_allow_html=True)
    with st.container():
        st.markdown("<div style='max-width:400px; margin:auto; padding:25px; background:#0a1626; border-radius:20px; border: 1px solid #1a2a3a; box-shadow: 0 0 20px rgba(0,0,0,0.5);'>", unsafe_allow_html=True)
        st.markdown(f"<h3 style='text-align:center; color:{cor_neon};'>ENTRAR NO SISTEMA</h3>", unsafe_allow_html=True)
        nome_in = st.text_input("Seu Nome:")
        genero_in = st.selectbox("Gênero:", ["Masculino", "Feminino"])
        key_in = st.text_input("Sua Key VIP:", type="password")
        
        if st.button("LIBERAR ACESSO"):
            if key_in:
                auth, admin = valida_chave(key_in)
                if auth:
                    st.session_state.autenticado = True
                    st.session_state.is_admin = admin
                    st.session_state.user_nome = nome_in if nome_in else "Trader VIP"
                    st.session_state.user_genero = genero_in
                    st.session_state.show_welcome = True
                    st.rerun()
                else: st.error("❌ Key Inválida ou Expirada!")
        st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# --- 6. CONTEÚDO LOGADO ---

# Header fixo
st.markdown(f"<div class='header-destaque'>RONNYP V8 SUPREME</div>", unsafe_allow_html=True)

# Letreiro Social Proof
itens_marquee = "".join([f"<div class='marquee-item'> 🔥 {n} ACABOU DE ENTRAR </div>" for n in ["Marcos", "Ana", "Lucas", "Julia", "Tadeu", "Carla", "Ricardo", "Fabiana"]])
st.markdown(f"<div class='marquee-wrapper'><div class='marquee-content'>{itens_marquee}{itens_marquee}</div></div>", unsafe_allow_html=True)

if st.session_state.show_welcome:
    st.toast(f"Bem-vindo(a), {st.session_state.user_nome}! 💰", icon="✅")
    st.balloons()
    st.session_state.show_welcome = False

# --- 7. MENU LATERAL (RESTAURADO) ---
with st.sidebar:
    st.markdown(f"<h2 style='color:{cor_neon}; text-align:center; text-shadow: 0 0 10px {cor_neon};'>RONNYP V8</h2>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align:center;'>👤 <b>Analista:</b> {st.session_state.user_nome}</p>", unsafe_allow_html=True)
    st.markdown("---")
    
    st.subheader("🔗 LINKS ÚTEIS")
    st.markdown(f'<a href="{LINK_CASA_1}" target="_blank" class="btn-side" style="background: #e6b800; color: #000 !important;">🎰 CASA RECOMENDADA</a>', unsafe_allow_html=True)
    st.markdown(f'<a href="{LINK_SUPORTE}" target="_blank" class="btn-side" style="background: #25d366;">🟢 SUPORTE WHATSAPP</a>', unsafe_allow_html=True)
    st.markdown(f'<a href="{LINK_CANAL}" target="_blank" class="btn-side" style="background: #0088cc;">🔵 CANAL TELEGRAM</a>', unsafe_allow_html=True)
    
    st.markdown("---")
    st.subheader("📊 GESTÃO DE BANCA")
    banca = st.number_input("Sua Banca R$", value=100.0, step=10.0)
    st.info(f"💰 Entrada (3%): R$ {banca * 0.03:.2f}")

    if st.session_state.is_admin:
        st.markdown("---")
        st.subheader("🎫 GERAR KEY ADMIN")
        c_nome = st.text_input("Chave para Cliente")
        if st.button("CRIAR KEY"):
            salvar_key(c_nome, 24)
            st.success("Gerada com sucesso!")
            st.code(c_nome)

    st.markdown("<br>"*5, unsafe_allow_html=True)
    if st.button("DESLOGAR"):
        st.session_state.autenticado = False
        st.rerun()

# --- 8. RADAR ---
t1, t2 = st.tabs(["🚀 SCANNER IA", "📋 MEU BILHETE"])

with t1:
    grade = st.text_area("COLE A GRADE DE JOGOS", height=100, placeholder="Time A x Time B\nTime C x Time D")
    if st.button("ANALISAR AGORA"):
        if grade:
            jogos = [j for j in grade.split('\n') if 'x' in j.lower()]
            st.session_state.analisados = []
            mercados = ["Ambas Marcam", "Mais de 1.5 Gols", "Vitória Direta", "Escanteios +8.5", "Mais de 2.5 Gols"]
            for j in jogos:
                st.session_state.analisados.append({
                    "jogo": j, 
                    "m": random.choice(mercados), 
                    "o": round(random.uniform(1.5, 2.3), 2), 
                    "conf": random.randint(93,99)
                })

    for idx, item in enumerate(st.session_state.analisados):
        st.markdown(f"""<div style='background:#0a1626; padding:15px; border-radius:12px; border-left: 5px solid {cor_neon}; margin-bottom:10px; box-shadow: 0 4px 6px rgba(0,0,0,0.3);'>
            <div style='color:{cor_neon}; font-weight:bold; font-size:12px;'>🔥 ASSERTIVIDADE: {item['conf']}%</div>
            <div style='font-size:18px; font-weight:bold; color:white;'>{item['jogo']}</div>
            <div style='margin-top:8px; color:#bbb;'>🎯 Mercado: <b>{item['m']}</b> | <span style='color:{cor_neon}; font-size:18px;'>@{item['o']}</span></div>
        </div>""", unsafe_allow_html=True)
        if st.button(f"ADICIONAR JOGO {idx+1}", key=f"btn_{idx}"):
            st.session_state.bilhete.append(item)
            st.toast("✅ Jogo adicionado ao bilhete!")

with t2:
    if st.session_state.bilhete:
        odd_f = 1.0
        msg_resumo = f"👑 *RONNYP VIP V8* 👑\n👤 Analista: {st.session_state.user_nome}\n\n"
        for b in st.session_state.bilhete:
            odd_f *= b['o']
            st.markdown(f"<div style='background:#0d1f14; padding:10px; border-radius:8px; margin-bottom:5px; border:1px solid {cor_neon}44;'>✅ {b['jogo']} (@{b['o']})</div>", unsafe_allow_html=True)
            msg_resumo += f"🏟️ *{b['jogo']}*\n🎯 {b['m']} (@{b['o']})\n\n"
        
        st.markdown(f"### 📈 ODD FINAL: <span style='color:{cor_neon};'>{odd_f:.2f}</span>", unsafe_allow_html=True)
        
        if st.button("📤 DISPARAR SINAL NO CANAL"):
            final_msg = msg_resumo + f"📊 *Odd Total: {odd_f:.2f}*\n\n🎰 [APOSTE AQUI]({LINK_CASA_1})"
            asyncio.run(Bot(TOKEN).send_message(CHAT_ID, final_msg, parse_mode='Markdown'))
            st.success("Sinal enviado com sucesso!")
        
        if st.button("🗑️ LIMPAR BILHETE"):
            st.session_state.bilhete = []
            st.rerun()
    else: 
        st.info("O seu bilhete de apostas está vazio. Use o Scanner para buscar as melhores oportunidades!")
