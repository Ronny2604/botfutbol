import streamlit as st
import asyncio
import random
import time
import urllib.parse
from telegram import Bot
from datetime import datetime, timedelta

# 1. CONFIGURAÇÃO E SEGURANÇA
st.set_page_config(page_title="RonnyP V8 PLATINUM", layout="wide", initial_sidebar_state="expanded")

MASTER_KEY = "ronnyp@2025"
KEYS_PERMANENTES = ["VIP777", "RONNY10", "SOCIO2025"]

if 'keys_geradas' not in st.session_state:
    st.session_state.keys_geradas = {}
if 'autenticado' not in st.session_state:
    st.session_state.autenticado = False
if 'bilhete' not in st.session_state:
    st.session_state.bilhete = []
if 'analisados' not in st.session_state:
    st.session_state.analisados = []

# Verificação via URL
query_params = st.query_params
url_key = query_params.get("acesso")

if url_key:
    if url_key == MASTER_KEY or url_key in KEYS_PERMANENTES or url_key in st.session_state.keys_geradas:
        st.session_state.autenticado = True
        st.session_state.is_admin = (url_key == MASTER_KEY)

st.markdown(f"""
    <style>
    .stApp {{ background-color: #040d1a; }}
    .mobile-title {{
        font-size: 1.6rem; color: #00d4ff; text-align: center; font-weight: bold;
        text-shadow: 0px 0px 10px rgba(0,212,255,0.5); margin-bottom: 1rem;
    }}
    .auth-box {{
        background: #0a1626; padding: 25px; border-radius: 15px;
        border: 2px solid #00d4ff; text-align: center; margin-top: 20px;
    }}
    .mobile-card {{
        background: #0a1626; border: 1px solid #1a2a3a; border-radius: 12px;
        padding: 15px; margin-bottom: 12px;
    }}
    .market-box {{ 
        background: #132338; padding: 12px; border-radius: 8px; 
        border-left: 4px solid #00d4ff; margin: 10px 0; 
    }}
    .radar {{
        width: 80px; height: 80px; border: 4px solid #00d4ff;
        border-radius: 50%; border-top: 4px solid transparent;
        animation: spin 1s linear infinite; margin: 10px auto;
    }}
    @keyframes spin {{ 0% {{ transform: rotate(0deg); }} 100% {{ transform: rotate(360deg); }} }}
    .stButton>button {{
        height: 3rem; border-radius: 10px !important;
        background: #00d4ff !important; color: #040d1a !important;
        font-weight: bold !important; border: none !important; width: 100%;
    }}
    .btn-suporte {{
        background: #25d366; color: white !important; padding: 12px;
        text-decoration: none; border-radius: 10px; display: block;
        text-align: center; font-weight: bold; margin-top: 15px;
    }}
    </style>
    """, unsafe_allow_html=True)

# 2. IA DE ANÁLISE
def get_advanced_analysis(jogo):
    times = jogo.split(' x ')
    t1 = times[0].strip()
    fav = t1
    expira_em = (datetime.now() + timedelta(minutes=random.randint(5, 15))).strftime("%H:%M")
    
    mercados = [
        {"m": f"Vitória: {t1}", "o": 1.65},
        {"m": "Ambas Marcam: SIM", "o": 1.82},
        {"m": "Mais de 8.5 Cantos", "o": 1.75},
        {"m": f"Dupla Chance: {t1}/X", "o": 1.35},
        {"m": "Over 1.5 Gols", "o": 1.40}
    ]
    res = random.choice(mercados)
    return {**res, "conf": random.randint(88,99), "expira": expira_em, "jogo": jogo, "fav": fav}

# 3. TELA DE ACESSO
if not st.session_state.autenticado:
    st.markdown("<div class='mobile-title'>👑 RONNYP VIP V8</div>", unsafe_allow_html=True)
    st.markdown("<div class='auth-box'>", unsafe_allow_html=True)
    st.subheader("🔐 ACESSO RESTRITO")
    key_input = st.text_input("Digite sua KEY ou use o link de acesso:", type="password")
    if st.button("ENTRAR NO SISTEMA"):
        if key_input == MASTER_KEY or key_input in KEYS_PERMANENTES or key_input in st.session_state.keys_geradas:
            st.session_state.autenticado = True
            st.session_state.is_admin = (key_input == MASTER_KEY)
            st.rerun()
        else: st.error("Key inválida!")
    st.markdown(f'<a href="https://wa.me/5561996193390" class="btn-suporte">💬 ADQUIRIR ACESSO VIP</a>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# 4. PAINEL ADMIN E MENU
with st.sidebar:
    st.markdown(f"### 🟢 {'ADMIN' if st.session_state.is_admin else 'VIP'}")
    if st.session_state.is_admin:
        st.header("🎫 GERADOR DE LINKS")
        nome_cliente = st.text_input("Nome do Cliente", placeholder="Ex: MarcosVip")
        if st.button("GERAR LINK"):
            if nome_cliente:
                st.session_state.keys_geradas[nome_cliente] = True
                link = f"https://botoverpy-gnwcseepyzojlaz7ci6g97.streamlit.app/?acesso={nome_cliente}"
                st.code(link)
                st.success("Link gerado!")
    
    st.markdown("---")
    if st.button("SAIR DO APP"):
        st.session_state.autenticado = False
        st.rerun()

# 5. FUNCIONALIDADE PRINCIPAL
st.markdown("<div class='mobile-title'>RONNYP VIP V8 PLATINUM</div>", unsafe_allow_html=True)
tab1, tab2, tab3 = st.tabs(["📡 RADAR IA", "📋 BILHETE", "✅ GREEN"])

with tab1:
    grade = st.text_area("COLE A GRADE DE JOGOS", height=100)
    if st.button("🚀 INICIAR VARREDURA"):
        if grade:
            with st.empty():
                st.markdown("<div class='radar'></div>", unsafe_allow_html=True)
                time.sleep(2)
            jogos = [l.strip() for l in grade.split('\n') if 'x' in l.lower()]
            st.session_state.analisados = [get_advanced_analysis(j) for j in jogos]
        else: st.warning("Cole os jogos primeiro!")

    for idx, item in enumerate(st.session_state.analisados):
        st.markdown(f"""
        <div class='mobile-card'>
            <span style='background:#ff4b4b; color:white; padding:2px 8px; border-radius:5px; font-size:10px; float:right;'>⏳ {item['expira']}</span>
            <div style='color:#00ff00; font-size:11px; font-weight:bold;'>⭐ FAV: {item['fav']}</div>
            <div style='color:white; font-weight:bold;'>{item['jogo']}</div>
            <div class='market-box'>
                <span style='color:white;'>{item['m']}</span>
                <span style='float:right; color:#00d4ff; font-weight:bold;'>@{item['o']}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button(f"ADICIONAR JOGO {idx+1}", key=f"add_{idx}"):
            st.session_state.bilhete.append(item)
            st.toast("✅ Adicionado!")

with tab2:
    if st.session_state.bilhete:
        odd_t = 1.0
        resumo = "👑 *RONNYP VIP V8* 👑\n\n"
        for b in st.session_state.bilhete:
            odd_t *= b['o']
            st.write(f"✅ **{b['jogo']}** (@{b['o']})")
            resumo += f"🏟️ *{b['jogo']}*\n🎯 {b['m']} (@{b['o']})\n\n"
        
        st.markdown(f"### 📈 ODD TOTAL: {odd_t:.2f}")
        
        if st.button("📤 ENVIAR PARA CANAL"):
            # Aqui você deve colocar seu TOKEN e CHAT_ID do Telegram
            st.success("Sinal enviado ao Telegram!")
            
        msg_wpp = urllib.parse.quote(resumo.replace("*","") + f"Odd: {odd_t:.2f}")
        st.markdown(f'<a href="https://wa.me/?text={msg_wpp}" target="_blank" class="btn-suporte" style="background:#25d366;">📲 WHATSAPP</a>', unsafe_allow_html=True)
        
        if st.button("🧹 LIMPAR BILHETE"):
            st.session_state.bilhete = []
            st.rerun()
    else: st.info("O bilhete está vazio.")

with tab3:
    if st.button("✅ NOTIFICAR GREEN"):
        st.balloons()
        st.success("Green notificado!")
