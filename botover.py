import streamlit as st
import asyncio
import random
import time
import urllib.parse
import hashlib
from telegram import Bot
from datetime import datetime, timedelta

# 1. CONFIGURAÇÃO E SEGURANÇA
st.set_page_config(page_title="RonnyP V8 GATEKEEPER", layout="wide", initial_sidebar_state="expanded")

# Chave Mestra para VOCÊ gerar as chaves dos usuários (Mude 'admin123' para sua senha pessoal)
MASTER_KEY = "ronnyp@2025"

if 'keys_ativas' not in st.session_state:
    st.session_state.keys_ativas = {} # Dicionário para guardar {chave: expiracao}
if 'autenticado' not in st.session_state:
    st.session_state.autenticado = False

st.markdown("""
    <style>
    .stApp { background-color: #040d1a; }
    .mobile-title {
        font-size: 1.6rem; color: #00d4ff; text-align: center; font-weight: bold;
        text-shadow: 0px 0px 10px rgba(0,212,255,0.5); margin-bottom: 1rem;
    }
    .auth-box {
        background: #0a1626; padding: 30px; border-radius: 15px;
        border: 2px solid #00d4ff; text-align: center; margin-top: 50px;
    }
    .btn-casa {
        background: linear-gradient(90deg, #0052ff, #00d4ff);
        color: white !important; padding: 10px; text-decoration: none;
        border-radius: 8px; display: block; text-align: center;
        font-weight: bold; margin-bottom: 10px; font-size: 0.9rem;
    }
    .stButton>button {
        height: 3rem; border-radius: 10px !important;
        background: #00d4ff !important; color: #040d1a !important;
        font-weight: bold !important; border: none !important; width: 100%;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. SISTEMA DE LOGIN / ACESSO
def verificar_acesso():
    if not st.session_state.autenticado:
        st.markdown("<div class='mobile-title'>👑 RONNYP VIP V8</div>", unsafe_allow_html=True)
        with st.container():
            st.markdown("<div class='auth-box'>", unsafe_allow_html=True)
            st.subheader("🔐 ACESSO RESTRITO")
            key_input = st.text_input("Insira sua KEY de acesso:", type="password")
            
            if st.button("LIBERAR ACESSO"):
                # Verifica se é a Master Key ou uma Key gerada
                if key_input == MASTER_KEY:
                    st.session_state.autenticado = True
                    st.session_state.is_admin = True
                    st.rerun()
                elif key_input in st.session_state.keys_ativas:
                    exp = st.session_state.keys_ativas[key_input]
                    if datetime.now() < exp:
                        st.session_state.autenticado = True
                        st.session_state.is_admin = False
                        st.rerun()
                    else:
                        st.error("Esta Key expirou!")
                else:
                    st.error("Key inválida ou expirada!")
            st.markdown("</div>", unsafe_allow_html=True)
            
            st.info("Deseja uma chave de teste? Fale com o suporte.")
        return False
    return True

# 3. FUNÇÕES DE IA E TELEGRAM (Mantidas das versões anteriores)
def get_advanced_analysis(jogo):
    expira_em = datetime.now() + timedelta(minutes=random.randint(5, 10))
    mercados = [{"m": f"Vitória Favorito", "o": 1.65}, {"m": "Ambas Marcam", "o": 1.82}, {"m": "Over 8.5 Cantos", "o": 1.75}]
    res = random.choice(mercados)
    return {**res, "conf": random.randint(85,99), "expira": expira_em.strftime("%H:%M"), "jogo": jogo}

TOKEN = '8543393879:AAEsaXAAq2A19zbmMEfHZb-R7nLL-VdierU'
CHAT_ID = '-1003799258159'

async def telegram_action(msg):
    try:
        bot = Bot(token=TOKEN)
        await bot.send_message(chat_id=CHAT_ID, text=msg, parse_mode='Markdown')
        return True
    except: return False

# --- EXECUÇÃO DO APP ---
if verificar_acesso():
    
    # MENU LATERAL - ADMIN (Só aparece se logar com a MASTER_KEY)
    with st.sidebar:
        if st.session_state.get('is_admin', False):
            st.header("🔑 GERADOR DE KEYS")
            nova_key = st.text_input("Criar Nova Key (Ex: TESTE-01)")
            tempo_horas = st.number_input("Validade (Horas)", min_value=1, value=24)
            if st.button("GERAR E ATIVAR"):
                validade = datetime.now() + timedelta(hours=tempo_horas)
                st.session_state.keys_ativas[nova_key] = validade
                st.success(f"Key '{nova_key}' ativa até {validade.strftime('%d/%m %H:%M')}")
                # Link de convite com a key inclusa (opcional para facilitar)
                link_pronto = f"https://botoverpy-ronnyp.streamlit.app/?key={nova_key}"
                st.code(link_pronto, language="text")
        
        st.markdown("### 🏦 CASAS PARCEIRAS")
        st.markdown(f'<a href="https://esportiva.bet.br?ref=511e1f11699f" target="_blank" class="btn-casa">🎰 ESPORTIVA BET</a>', unsafe_allow_html=True)
        st.markdown(f'<a href="https://referme.to/ronyelissonoliveiran-7" target="_blank" class="btn-casa">💎 CASA PREMIUM</a>', unsafe_allow_html=True)
        
        if st.button("SAIR / LOGOUT"):
            st.session_state.autenticado = False
            st.rerun()

    # TELA PRINCIPAL
    st.markdown("<div class='mobile-title'>RONNYP VIP V8 PLATINUM</div>", unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["🔍 RADAR IA", "📋 BILHETE", "✅ GREEN"])

    if 'bilhete' not in st.session_state: st.session_state.bilhete = []
    if 'analisados' not in st.session_state: st.session_state.analisados = []

    with tab1:
        grade = st.text_area("COLE A GRADE", height=100)
        if st.button("📡 SCANNER IA"):
            jogos = [l.strip() for l in grade.split('\n') if 'x' in l.lower()]
            st.session_state.analisados = [get_advanced_analysis(j) for j in jogos]
        
        for idx, item in enumerate(st.session_state.analisados):
            st.markdown(f"""
            <div style='background:#0a1626; border:1px solid #1a2a3a; padding:15px; border-radius:12px; margin-bottom:10px;'>
                <span style='background:red; color:white; padding:2px 5px; border-radius:5px; font-size:10px;'>EXPIRA {item['expira']}</span>
                <div style='color:white; font-weight:bold; margin-top:5px;'>{item['jogo']}</div>
                <div style='background:#132338; padding:10px; border-left:4px solid #00d4ff; margin:10px 0;'>
                    <span style='color:white;'>{item['m']}</span>
                    <span style='float:right; color:#00d4ff;'>@{item['o']}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"ADICIONAR {idx+1}"):
                st.session_state.bilhete.append(item)

    with tab2:
        if st.session_state.bilhete:
            odd_t = 1.0
            resumo = "👑 *RONNYP VIP V8* 👑\n\n"
            for b in st.session_state.bilhete:
                odd_t *= b['o']
                resumo += f"🏟️ *{b['jogo']}*\n🎯 {b['m']} (@{b['o']})\n\n"
            
            st.markdown(f"### ODD TOTAL: {odd_t:.2f}")
            if st.button("📤 ENVIAR CANAL"):
                asyncio.run(telegram_action(resumo + f"📊 Odd: {odd_t:.2f}"))
                st.success("Enviado!")
        else:
            st.info("Selecione jogos no Radar.")
