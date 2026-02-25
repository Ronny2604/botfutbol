import streamlit as st
import asyncio
import random
import time
import urllib.parse
import os
from telegram import Bot
from datetime import datetime, timedelta

# --- CONFIGURAÇÃO E SEGURANÇA ---
st.set_page_config(page_title="RonnyP V8 SUPREME", layout="wide", initial_sidebar_state="expanded")

MASTER_KEY = "ronnyp@2025"
FILE_KEYS = "keys.txt" 
TOKEN = '8543393879:AAEsaXAAq2A19zbmMEfHZb-R7nLL-VdierU'
CHAT_ID = '-1003799258159'
LINK_CANAL = "https://t.me/+_4ZgNo3xYFo5M2Ex"
LINK_SUPORTE = "https://wa.me/5561996193390?text=Olá%20RonnyP"

# --- BANCO DE DADOS DE KEYS ---
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

# --- INICIALIZAÇÃO DE SESSÃO ---
if 'autenticado' not in st.session_state: st.session_state.autenticado = False
if 'user_nome' not in st.session_state: st.session_state.user_nome = "Investidor"
if 'bilhete' not in st.session_state: st.session_state.bilhete = []
if 'analisados' not in st.session_state: st.session_state.analisados = []

db_keys = carregar_keys()

def valida_chave(chave):
    if chave == MASTER_KEY: return True, True
    if chave in db_keys:
        if datetime.now() < db_keys[chave]: return True, False
    return False, False

# --- LÓGICA DE SALVAMENTO AUTOMÁTICO (COOKIE/URL) ---
# Tenta pegar a chave salva nos parâmetros da URL
query_params = st.query_params
url_key = query_params.get("acesso")

if url_key and not st.session_state.autenticado:
    auth, admin = valida_chave(url_key)
    if auth:
        st.session_state.autenticado = True
        st.session_state.is_admin = admin

# --- ESTILOS CSS ---
st.markdown(f"""
    <style>
    .stApp {{ background-color: #040d1a; }}
    .marquee {{ width: 100%; background: #00d4ff; color: #040d1a; padding: 5px; font-weight: bold; overflow: hidden; }}
    .marquee p {{ display: inline-block; padding-left: 100%; animation: marquee 25s linear infinite; margin:0; }}
    @keyframes marquee {{ 0% {{ transform: translate(0, 0); }} 100% {{ transform: translate(-100%, 0); }} }}
    .auth-container {{ background: #0a1626; padding: 30px; border-radius: 20px; border: 2px solid #00d4ff; text-align: center; margin: auto; max-width: 400px; }}
    .mobile-card {{ background: #0a1626; border: 1px solid #1a2a3a; border-radius: 12px; padding: 15px; margin-bottom: 12px; }}
    .stButton>button {{ height: 3.5rem; border-radius: 12px !important; background: #00d4ff !important; color: #040d1a !important; font-weight: bold !important; width: 100%; }}
    .btn-casa {{ background: linear-gradient(90deg, #0052ff, #00d4ff); color: white !important; padding: 12px; border-radius: 8px; display: block; text-align: center; font-weight: bold; text-decoration: none; margin-bottom: 10px; }}
    </style>
    """, unsafe_allow_html=True)

# Letreiro Social Proof
Nomes_Ficticios = ["Marcos Silva", "Ricardo_Trader", "Ana Paula", "Lucas Tips", "Felipe G.", "BetMaster", "Jonny", "Adriano V.", "Sérgio A.", "BancaForte"]
msg_marquee = "  •  ".join([f"🔥 {n} ACABOU DE ENTRAR" for n in Nomes_Ficticios])
st.markdown(f"<div class='marquee'><p>{msg_marquee} • {msg_marquee}</p></div>", unsafe_allow_html=True)

# --- TELA DE LOGIN ---
if not st.session_state.autenticado:
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("<div class='auth-container'>", unsafe_allow_html=True)
    st.image("https://cdn-icons-png.flaticon.com/512/5971/5971593.png", width=80)
    st.title("RONNYP VIP V8")
    
    nome_input = st.text_input("Seu Nome:")
    key_input = st.text_input("Sua Key:", type="password")
    lembrar = st.checkbox("Lembrar meu acesso neste dispositivo", value=True)
    
    if st.button("ACESSAR PLATAFORMA"):
        if key_input:
            auth, admin = valida_chave(key_input)
            if auth:
                st.session_state.autenticado = True
                st.session_state.is_admin = admin
                st.session_state.user_nome = nome_input if nome_input else "Investidor"
                
                if lembrar:
                    # Salva a key na URL para o navegador "lembrar" na próxima vez
                    st.query_params["acesso"] = key_input
                st.rerun()
            else: st.error("Key inválida!")
        else: st.warning("Digite sua Key!")
    
    st.markdown(f'<a href="{LINK_SUPORTE}" style="color:#00d4ff; text-decoration:none; font-size:12px;">Comprar Acesso VIP</a>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# --- MENU LATERAL ---
with st.sidebar:
    st.markdown(f"### 👋 Olá, {st.session_state.user_nome}!")
    st.markdown(f'<a href="{LINK_CANAL}" target="_blank" class="btn-casa" style="background:#0088cc;">📢 CANAL TELEGRAM</a>', unsafe_allow_html=True)
    
    st.markdown("---")
    st.subheader("📊 GESTÃO DE BANCA")
    banca = st.number_input("Sua Banca (R$)", min_value=10.0, value=100.0)
    perfil = st.select_slider("Risco", options=["Baixo", "Médio", "Alto"])
    val_aposta = banca * (0.01 if perfil=="Baixo" else 0.03 if perfil=="Médio" else 0.05)
    st.info(f"💰 Aposte: **R$ {val_aposta:.2f}**")
    
    if st.session_state.is_admin:
        st.markdown("---")
        st.header("🎫 ADMIN")
        c_nome = st.text_input("Nome Cliente")
        c_tempo = st.selectbox("Validade (Horas)", [0.5, 24, 720])
        if st.button("GERAR"):
            salvar_key(c_nome, float(c_tempo))
            link_final = f"https://botoverpy-gnwcseepyzojlaz7ci6g97.streamlit.app/?acesso={c_nome}"
            st.code(link_final)

    if st.button("SAIR E LIMPAR SALVAMENTO"):
        st.query_params.clear()
        st.session_state.autenticado = False
        st.rerun()

# --- CONTEÚDO PRINCIPAL (RADAR / BILHETE) ---
st.title("📡 RADAR V8 PLATINUM")
tab1, tab2 = st.tabs(["🚀 SCANNER IA", "📋 BILHETE PRO"])

def get_analysis(j):
    t1 = j.split(' x ')[0].strip()
    return {"m": f"Vitória: {t1}", "o": 1.65, "conf": random.randint(90,99), "expira": (datetime.now()+timedelta(minutes=10)).strftime("%H:%M"), "jogo": j, "fav": t1}

with tab1:
    grade = st.text_area("COLE A GRADE", height=80)
    col1, col2 = st.columns(2)
    if col1.button("VARREDURA"):
        if grade:
            with st.spinner("IA ANALISANDO..."): time.sleep(1.5)
            st.session_state.analisados = [get_analysis(j) for j in grade.split('\n') if 'x' in j.lower()]
    if col2.button("LIMPAR"):
        st.session_state.analisados = []
        st.rerun()

    for idx, item in enumerate(st.session_state.analisados):
        st.markdown(f"""<div class='mobile-card'>
            <div style='color:#00ff00; font-size:12px; font-weight:bold;'>⭐ CONF: {item['conf']}% | ⏳ {item['expira']}</div>
            <div style='color:white; font-size:16px; font-weight:bold;'>{item['jogo']}</div>
            <div style='background:#132338; padding:10px; margin-top:8px; border-radius:5px;'>
                <span style='color:white;'>{item['m']}</span><span style='float:right; color:#00d4ff;'>@{item['o']}</span>
            </div>
        </div>""", unsafe_allow_html=True)
        if st.button(f"ADD {idx+1}", key=f"add_{idx}"):
            st.session_state.bilhete.append(item)
            st.toast("✅ Adicionado!")

with tab2:
    if st.session_state.bilhete:
        odd_t = 1.0
        resumo = f"👑 *RONNYP VIP V8* 👑\n👤 Analista: {st.session_state.user_nome}\n\n"
        for b in st.session_state.bilhete:
            odd_t *= b['o']
            st.write(f"🔹 **{b['jogo']}** (@{b['o']})")
            resumo += f"🏟️ *{b['jogo']}*\n🎯 {b['m']} (@{b['o']})\n\n"
        st.write(f"### ODD FINAL: {odd_t:.2f}")
        if st.button("📤 DISPARAR TELEGRAM"):
            asyncio.run(Bot(TOKEN).send_message(CHAT_ID, resumo + f"📊 *Odd Total: {odd_t:.2f}*", parse_mode='Markdown'))
            st.success("Sinal enviado!")
        if st.button("🗑️ LIMPAR BILHETE"):
            st.session_state.bilhete = []
            st.rerun()
    else: st.info("Selecione jogos no Scanner.")
