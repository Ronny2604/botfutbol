import streamlit as st
import asyncio
import random
import time
import urllib.parse
import os
from telegram import Bot
from datetime import datetime, timedelta

# --- CONFIGURAÇÃO E SEGURANÇA ---
st.set_page_config(page_title="RonnyP V8 PLATINUM", layout="wide", initial_sidebar_state="expanded")

MASTER_KEY = "ronnyp@2025"
FILE_KEYS = "keys.txt" 
TOKEN = '8543393879:AAEsaXAAq2A19zbmMEfHZb-R7nLL-VdierU'
CHAT_ID = '-1003799258159'
LINK_CANAL = "https://t.me/+_4ZgNo3xYFo5M2Ex"
LINK_SUPORTE = "https://wa.me/5561996193390?text=Olá%20RonnyP,%20gostaria%20de%20adquirir%20minha%20Key%20de%20acesso%20VIP!"

# --- GERENCIAMENTO DE KEYS COM TEMPO ---
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

# Inicialização de Sessão
if 'autenticado' not in st.session_state: st.session_state.autenticado = False
if 'bilhete' not in st.session_state: st.session_state.bilhete = []
if 'analisados' not in st.session_state: st.session_state.analisados = []
if 'boas_vindas' not in st.session_state: st.session_state.boas_vindas = False

# Verificação de Acesso
query_params = st.query_params
url_key = query_params.get("acesso")
db_keys = carregar_keys()

def valida_chave(chave):
    if chave == MASTER_KEY: return True, True
    if chave in db_keys:
        if datetime.now() < db_keys[chave]: return True, False
    return False, False

if url_key and not st.session_state.autenticado:
    auth, admin = valida_chave(url_key)
    if auth:
        st.session_state.autenticado = True
        st.session_state.is_admin = admin

# --- ESTILOS ---
st.markdown(f"""
    <style>
    .stApp {{ background-color: #040d1a; }}
    .mobile-title {{ font-size: 1.6rem; color: #00d4ff; text-align: center; font-weight: bold; margin-bottom: 1rem; }}
    .mobile-card {{ background: #0a1626; border: 1px solid #1a2a3a; border-radius: 12px; padding: 15px; margin-bottom: 12px; }}
    .market-box {{ background: #132338; padding: 12px; border-radius: 8px; border-left: 4px solid #00d4ff; margin: 10px 0; }}
    .btn-casa {{ background: linear-gradient(90deg, #0052ff, #00d4ff); color: white !important; padding: 10px; border-radius: 8px; display: block; text-align: center; font-weight: bold; margin-bottom: 10px; text-decoration: none; }}
    .btn-canal {{ background: #0088cc; color: white !important; padding: 12px; border-radius: 10px; display: block; text-align: center; font-weight: bold; margin-bottom: 15px; text-decoration: none; }}
    .stButton>button {{ height: 3rem; border-radius: 10px !important; background: #00d4ff !important; color: #040d1a !important; font-weight: bold !important; width: 100%; }}
    </style>
    """, unsafe_allow_html=True)

# --- TELA DE ACESSO ---
if not st.session_state.autenticado:
    st.markdown("<div class='mobile-title'>👑 RONNYP VIP V8</div>", unsafe_allow_html=True)
    st.markdown("<div style='background: #0a1626; padding: 25px; border-radius: 15px; border: 2px solid #00d4ff; text-align: center;'>", unsafe_allow_html=True)
    st.subheader("🔐 ACESSO RESTRITO")
    key_input = st.text_input("Sua KEY:", type="password")
    if st.button("LIBERAR"):
        auth, admin = valida_chave(key_input)
        if auth:
            st.session_state.autenticado = True
            st.session_state.is_admin = admin
            st.rerun()
        else: st.error("Chave inválida ou expirada!")
    st.markdown(f'<a href="{LINK_SUPORTE}" style="background:#25d366; color:white; padding:12px; display:block; border-radius:10px; text-decoration:none; font-weight:bold; margin-top:15px;">💬 ADQUIRIR KEY</a>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# --- MENSAGEM DE BOAS-VINDAS ---
if not st.session_state.boas_vindas:
    st.balloons()
    st.toast("🚀 IA RonnyP V8 Conectada!", icon="💰")
    st.session_state.boas_vindas = True

# --- MENU LATERAL ---
with st.sidebar:
    st.markdown(f"### 🟢 STATUS: {'ADMIN' if st.session_state.is_admin else 'VIP'}")
    
    st.markdown(f'<a href="{LINK_CANAL}" target="_blank" class="btn-canal">📢 ENTRAR NO CANAL</a>', unsafe_allow_html=True)
    
    if st.session_state.is_admin:
        st.header("🎫 GERAR ACESSO")
        nome = st.text_input("Nome do Cliente (Sem espaços)")
        tempo = st.selectbox("Validade", ["0.5 (Teste 30min)", "24 (1 Dia)", "720 (30 Dias)"])
        if st.button("GERAR LINK"):
            if nome:
                exp_date = salvar_key(nome, float(tempo))
                link = f"https://botoverpy-gnwcseepyzojlaz7ci6g97.streamlit.app/?acesso={nome}"
                st.success(f"Até: {exp_date.strftime('%d/%m %H:%M')}")
                st.code(link)
    
    st.markdown("---")
    st.markdown("### 🏦 CASAS SUGERIDAS")
    st.markdown(f'<a href="https://esportiva.bet.br?ref=511e1f11699f" target="_blank" class="btn-casa">🎰 ESPORTIVA BET</a>', unsafe_allow_html=True)
    st.markdown(f'<a href="{LINK_SUPORTE}" class="btn-casa" style="background:#25d366;">🛠️ SUPORTE</a>', unsafe_allow_html=True)
    
    if st.button("SAIR"):
        st.session_state.autenticado = False
        st.rerun()

# --- APP ---
st.markdown("<div class='mobile-title'>RONNYP VIP V8 PLATINUM</div>", unsafe_allow_html=True)
tab1, tab2, tab3 = st.tabs(["📡 RADAR IA", "📋 BILHETE", "✅ GREEN"])

def get_analysis(jogo):
    times = jogo.split(' x ')
    t1 = times[0].strip()
    exp = (datetime.now() + timedelta(minutes=random.randint(6, 12))).strftime("%H:%M")
    res = random.choice([{"m": f"Vitória: {t1}", "o": 1.62}, {"m": "Ambas Marcam", "o": 1.80}, {"m": "Over 1.5 Gols", "o": 1.40}])
    return {**res, "conf": random.randint(88,99), "expira": exp, "jogo": jogo, "fav": t1}

with tab1:
    grade = st.text_area("COLE A GRADE", height=80, placeholder="Time A x Time B")
    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("🚀 INICIAR VARREDURA"):
            if grade:
                with st.spinner("IA ESCANEANDO..."): time.sleep(1.5)
                jogos = [l.strip() for l in grade.split('\n') if 'x' in l.lower()]
                st.session_state.analisados = [get_analysis(j) for j in jogos]
    with col_b:
        if st.button("🧹 LIMPAR GRADE"):
            st.session_state.analisados = []
            st.rerun()

    for idx, item in enumerate(st.session_state.analisados):
        st.markdown(f"""<div class='mobile-card'>
            <span style='background:#ff4b4b; color:white; padding:2px 8px; border-radius:5px; font-size:10px; float:right;'>⏳ {item['expira']}</span>
            <div style='color:#00ff00; font-size:11px; font-weight:bold;'>⭐ FAV: {item['fav']}</div>
            <div style='color:white; font-weight:bold;'>{item['jogo']}</div>
            <div class='market-box'><span style='color:white;'>{item['m']}</span><span style='float:right; color:#00d4ff; font-weight:bold;'>@{item['o']}</span></div>
        </div>""", unsafe_allow_html=True)
        if st.button(f"ADICIONAR {idx+1}", key=f"add_{idx}"):
            st.session_state.bilhete.append(item)
            st.toast("✅ No Bilhete!")

with tab2:
    if st.session_state.bilhete:
        odd_t = 1.0
        resumo_tg = "👑 *RONNYP VIP V8* 👑\n\n"
        for b in st.session_state.bilhete:
            odd_t *= b['o']
            st.write(f"🔹 **{b['jogo']}** (@{b['o']})")
            resumo_tg += f"🏟️ *{b['jogo']}*\n🎯 {b['m']} (@{b['o']})\n\n"
        st.markdown(f"### 📈 ODD TOTAL: {odd_t:.2f}")
        
        if st.button("📤 DISPARAR NO CANAL"):
            msg_final = resumo_tg + f"📊 *Odd: {odd_t:.2f}*\n\n🎰 [APOSTE AQUI](https://esportiva.bet.br?ref=511e1f11699f)\n📢 [ENTRE NO CANAL]({LINK_CANAL})"
            asyncio.run(Bot(TOKEN).send_message(CHAT_ID, msg_final, parse_mode='Markdown', disable_web_page_preview=True))
            st.success("Sinal enviado!")
        
        wpp_link = urllib.parse.quote(resumo_tg.replace("*","") + f"Odd: {odd_t:.2f}\nCanal: {LINK_CANAL}")
        st.markdown(f'<a href="https://wa.me/?text={wpp_link}" target="_blank" style="background:#25d366; color:white; padding:15px; border-radius:10px; display:block; text-align:center; text-decoration:none; font-weight:bold; margin-top:10px;">📲 WHATSAPP</a>', unsafe_allow_html=True)
        
        if st.button("🗑️ LIMPAR BILHETE"):
            st.session_state.bilhete = []
            st.rerun()
    else: st.info("Vazio.")

with tab3:
    if st.button("✅ NOTIFICAR GREEN"):
        asyncio.run(Bot(TOKEN).send_message(CHAT_ID, f"✅✅✅ GREEN! ✅✅✅\n\n📢 {LINK_CANAL}"))
        st.balloons()
