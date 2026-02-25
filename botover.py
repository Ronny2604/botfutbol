import streamlit as st
import asyncio
import random
import time
import urllib.parse
from telegram import Bot
from datetime import datetime, timedelta

# 1. CONFIGURAÇÃO E SEGURANÇA
st.set_page_config(page_title="RonnyP V8 PLATINUM", layout="wide")

# --- SENHA MESTRA DO DONO ---
MASTER_KEY = "ronnyp@2025"

# --- CHAVES QUE NUNCA EXPIRAM (Coloque aqui as chaves de quem pagou mensal) ---
KEYS_PERMANENTES = ["VIP777", "RONNY10", "SOCIO2025", "TESTEGUIDO"]

# Inicializa o dicionário de chaves temporárias na memória do servidor
if 'keys_geradas' not in st.session_state:
    st.session_state.keys_geradas = {}

# Pega os parâmetros da URL
query_params = st.query_params
url_key = query_params.get("acesso")

if 'autenticado' not in st.session_state:
    st.session_state.autenticado = False

# Lógica de Autenticação (URL, Permanente ou Temporária)
if url_key:
    if url_key == MASTER_KEY or url_key in KEYS_PERMANENTES or url_key in st.session_state.keys_geradas:
        st.session_state.autenticado = True
        st.session_state.is_admin = (url_key == MASTER_KEY)

# Estilos Visuais
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
    .btn-suporte {{
        background: #25d366; color: white !important; padding: 12px;
        text-decoration: none; border-radius: 10px; display: block;
        text-align: center; font-weight: bold; margin-top: 15px;
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
    </style>
    """, unsafe_allow_html=True)

# 2. TELA DE ACESSO
def verificar_acesso():
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
            else:
                st.error("Key inválida!")
        
        st.markdown(f'<a href="https://wa.me/5561996193390" class="btn-suporte">💬 ADQUIRIR ACESSO VIP</a>', unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        return False
    return True

# 3. LOGICA PRINCIPAL
if verificar_acesso():
    
    # PEGAR LINK BASE DO APP AUTOMATICAMENTE
    # Link atual do seu app: https://botoverpy-gnwcseepyzojlaz7ci6g97.streamlit.app/
    base_url = "https://botoverpy-gnwcseepyzojlaz7ci6g97.streamlit.app/"

    with st.sidebar:
        st.markdown(f"### 🟢 LOGADO COMO: {'ADMIN' if st.session_state.is_admin else 'VIP'}")
        
        if st.session_state.is_admin:
            st.markdown("---")
            st.header("🎫 GERADOR DE LINKS")
            nome_cliente = st.text_input("Nome do Cliente (Sem espaços)", placeholder="Ex: JoaoSilva")
            
            if st.button("GERAR LINK PERSONALIZADO"):
                if nome_cliente:
                    # Registra a key na sessão
                    st.session_state.keys_geradas[nome_cliente] = True
                    # Gera o link completo
                    link_completo = f"{base_url}?acesso={nome_cliente}"
                    
                    st.success("Link gerado com sucesso!")
                    st.code(link_completo, language="text")
                    st.info("Copie o link acima e envie para o cliente. Ele entrará sem precisar de senha.")
                else:
                    st.warning("Digite um nome para a Key.")

        if st.button("SAIR (LOGOUT)"):
            st.session_state.autenticado = False
            st.rerun()

    # --- RESTANTE DO APP (RADAR, BILHETE, ETC) ---
    st.markdown("<div class='mobile-title'>PLATINUM V8 RADAR</div>", unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["📡 RADAR IA", "📋 MEU BILHETE"])
    
    if 'bilhete' not in st.session_state: st.session_state.bilhete = []
    
    with tab1:
        grade = st.text_area("COLE A GRADE", height=80)
        if st.button("SCANNER IA"):
            with st.empty():
                st.markdown("<div class='radar'></div>", unsafe_allow_html=True)
                time.sleep(2)
            st.success("Análise concluída!")
            # Simulando um resultado para teste
            if grade:
                st.session_state.jogo_teste = {"j": grade.split('\n')[0], "m": "Vitória Favorito", "o": 1.70}
                st.markdown(f"**Jogo:** {st.session_state.jogo_teste['j']}  \n**🎯 {st.session_state.jogo_teste['m']}** (@{st.session_state.jogo_teste['o']})")
                if st.button("Adicionar ao Bilhete"):
                    st.session_state.bilhete.append(st.session_state.jogo_teste)
                    st.toast("Adicionado!")

    with tab2:
        if st.session_state.bilhete:
            for b in st.session_state.bilhete:
                st.write(f"✅ {b['j']} - @{b['o']}")
            if st.button("LIMPAR"):
                st.session_state.bilhete = []
                st.rerun()
        else:
            st.info("Nenhum jogo no bilhete.")
