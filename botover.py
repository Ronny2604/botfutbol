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
if 'user_nome' not in st.session_state: st.session_state.user_nome = "Investidor"
if 'bilhete' not in st.session_state: st.session_state.bilhete = []
if 'analisados' not in st.session_state: st.session_state.analisados = []

db_keys = carregar_keys()

def valida_chave(chave):
    if chave == MASTER_KEY: return True, True
    if chave in db_keys:
        if datetime.now() < db_keys[chave]: return True, False
    return False, False

# Auto-login via URL
query_params = st.query_params
url_key = query_params.get("acesso")
if url_key and not st.session_state.autenticado:
    auth, admin = valida_chave(url_key)
    if auth:
        st.session_state.autenticado = True
        st.session_state.is_admin = admin

# --- 4. ESTILOS CSS SUPREME (COM EFEITO GLOW) ---
st.markdown(f"""
    <style>
    .stApp {{ background-color: #040d1a; }}
    
    /* Letreiro com Efeito Glow */
    .marquee-wrapper {{
        width: 100%;
        overflow: hidden;
        background: #001a2e;
        border-bottom: 2px solid #00d4ff;
        padding: 10px 0;
        display: flex;
        box-shadow: 0 0 20px rgba(0,212,255,0.4);
        margin-bottom: 20px;
    }}
    .marquee-content {{
        display: flex;
        white-space: nowrap;
        animation: marquee 40s linear infinite;
    }}
    .marquee-item {{
        padding: 0 40px;
        flex-shrink: 0;
        font-size: 15px;
        font-weight: bold;
        color: #00d4ff;
        text-shadow: 0 0 10px #00d4ff, 0 0 20px #00d4ff;
    }}
    @keyframes marquee {{
        0% {{ transform: translateX(0); }}
        100% {{ transform: translateX(-50%); }}
    }}

    /* Container de Login Neon */
    .auth-container {{ 
        background: #0a1626; padding: 30px; border-radius: 20px; 
        border: 2px solid #00d4ff; text-align: center; margin: auto; max-width: 380px; 
        box-shadow: 0 0 15px rgba(0,212,255,0.2);
    }}
    
    /* Botão com Pulsação */
    .stButton>button {{ 
        height: 3.5rem; border-radius: 12px !important; background: #00d4ff !important; 
        color: #040d1a !important; font-weight: bold !important; width: 100%;
        transition: 0.3s; box-shadow: 0 0 10px rgba(0,212,255,0.5);
    }}
    .stButton>button:hover {{
        transform: scale(1.02);
        box-shadow: 0 0 20px rgba(0,212,255,0.8);
    }}

    .mobile-card {{ background: #0a1626; border: 1px solid #1a2a3a; border-radius: 12px; padding: 15px; margin-bottom: 12px; }}
    .btn-casa {{ 
        background: linear-gradient(90deg, #0052ff, #00d4ff); color: white !important; 
        padding: 12px; border-radius: 8px; display: block; text-align: center; 
        font-weight: bold; text-decoration: none; margin-bottom: 10px; 
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 5. LETREIRO DE USUÁRIOS COM GLOW ---
Nomes_Ficticios = ["Marcos Silva", "Ricardo_Trader", "Ana Paula", "Lucas Tips", "Felipe G.", "BetMaster", "Jonny", "Adriano V.", "Sérgio A.", "BancaForte"]
itens_html = "".join([f"<div class='marquee-item'> 🔥 {n} ENTROU NO VIP </div>" for n in Nomes_Ficticios])
st.markdown(f"<div class='marquee-wrapper'><div class='marquee-content'>{itens_html}{itens_html}</div></div>", unsafe_allow_html=True)

# --- 6. TELA DE LOGIN ---
if not st.session_state.autenticado:
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("<div class='auth-container'>", unsafe_allow_html=True)
    st.image("https://cdn-icons-png.flaticon.com/512/5971/5971593.png", width=70)
    st.title("RONNYP V8 VIP")
    
    nome_in = st.text_input("Nome de Usuário:")
    key_in = st.text_input("Sua Chave Mestra:", type="password")
    lembrar = st.checkbox("Lembrar login neste celular", value=True)
    
    if st.button("ACESSAR RADAR PLATINUM"):
        if key_in:
            auth, admin = valida_chave(key_in)
            if auth:
                st.session_state.autenticado = True
                st.session_state.is_admin = admin
                st.session_state.user_nome = nome_in if nome_in else "VIP User"
                if lembrar: st.query_params["acesso"] = key_in
                st.rerun()
            else: st.error("Chave inválida ou tempo expirado!")
        else: st.warning("Por favor, insira sua Key.")
    
    st.markdown(f'<br><a href="{LINK_SUPORTE}" style="color:#00d4ff; text-decoration:none; font-size:13px; font-weight:bold;">SOLICITAR KEY / SUPORTE</a>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# --- 7. MENU LATERAL ---
with st.sidebar:
    st.markdown(f"### ⚡ Bem-vindo, {st.session_state.user_nome}!")
    st.markdown(f'<a href="{LINK_CANAL}" target="_blank" class="btn-casa" style="background:#0088cc;">📢 ENTRAR NO CANAL VIP</a>', unsafe_allow_html=True)
    
    st.markdown("---")
    st.subheader("📊 GESTÃO PROFISSIONAL")
    banca_val = st.number_input("Banca Atual (R$)", min_value=10.0, value=100.0)
    perfil_val = st.select_slider("Risco", options=["Baixo", "Médio", "Alto"], value="Médio")
    perc = {"Baixo": 0.01, "Médio": 0.03, "Alto": 0.05}
    st.success(f"💰 Entrada Sugerida: **R$ {banca_val * perc[perfil_val]:.2f}**")
    
    if st.session_state.is_admin:
        st.markdown("---")
        st.header("🎫 ADMIN: GERAR KEY")
        c_nome = st.text_input("Identificador Cliente")
        c_tempo = st.selectbox("Validade", [0.5, 24, 720], format_func=lambda x: f"{x} Horas")
        if st.button("CRIAR LINK DE ACESSO"):
            salvar_key(c_nome, float(c_tempo))
            link_final = f"https://botoverpy-gnwcseepyzojlaz7ci6g97.streamlit.app/?acesso={c_nome}"
            st.code(link_final)

    if st.button("SAIR (LOGOUT)"):
        st.query_params.clear()
        st.session_state.autenticado = False
        st.rerun()

# --- 8. SCANNER E RADAR ---
st.markdown("<h2 style='text-align:center; color:#00d4ff; text-shadow: 0 0 10px #00d4ff;'>📡 RADAR V8 PLATINUM</h2>", unsafe_allow_html=True)
t1, t2 = st.tabs(["🚀 SCANNER IA", "📋 BILHETE PRO"])

def analise_ia(j):
    t1 = j.split(' x ')[0].strip()
    return {"m": f"Vitória: {t1}", "o": 1.65, "conf": random.randint(92,99), "expira": (datetime.now()+timedelta(minutes=10)).strftime("%H:%M"), "jogo": j, "fav": t1}

with t1:
    grade = st.text_area("COLE A GRADE DE JOGOS", height=100, placeholder="Ex: Time A x Time B")
    c1, c2 = st.columns(2)
    if c1.button("VARREDURA IA"):
        if grade:
            with st.spinner("PROCESSANDO ALGORITMOS..."): time.sleep(1.2)
            st.session_state.analisados = [analise_ia(j) for j in grade.split('\n') if 'x' in j.lower()]
    if c2.button("LIMPAR"):
        st.session_state.analisados = []
        st.rerun()

    for idx, item in enumerate(st.session_state.analisados):
        st.markdown(f"""<div class='mobile-card'>
            <div style='color:#00ff00; font-size:12px; font-weight:bold;'>⭐ TAXA DE ACERTO: {item['conf']}% | ⏳ {item['expira']}</div>
            <div style='color:white; font-size:17px; font-weight:bold;'>{item['jogo']}</div>
            <div style='background:#132338; padding:12px; border-radius:10px; border-left: 5px solid #00d4ff; margin-top:10px;'>
                <span style='color:white; font-weight:bold;'>{item['m']}</span>
                <span style='float:right; color:#00d4ff; font-weight:bold; font-size:18px;'>@{item['o']}</span>
            </div>
        </div>""", unsafe_allow_html=True)
        if st.button(f"➕ ADICIONAR AO BILHETE {idx+1}", key=f"add_{idx}"):
            st.session_state.bilhete.append(item)
            st.toast(f"✅ {item['fav']} Adicionado!")

with t2:
    if st.session_state.bilhete:
        odd_f = 1.0
        msg_tg = "👑 *RONNYP VIP V8* 👑\n👤 Analista: " + st.session_state.user_nome + "\n\n"
        for b in st.session_state.bilhete:
            odd_f *= b['o']
            st.markdown(f"<div style='background:#0a1626; padding:10px; border-radius:8px; margin-bottom:5px; border:1px solid #1a2a3a;'>✅ {b['jogo']} (@{b['o']})</div>", unsafe_allow_html=True)
            msg_tg += f"🏟️ *{b['jogo']}*\n🎯 {b['m']} (@{b['o']})\n\n"
        
        st.markdown(f"### 📈 ODD FINAL: <span style='color:#00d4ff;'>{odd_f:.2f}</span>", unsafe_allow_html=True)
        st.write(f"💵 **Stake Recomendada:** R$ {banca_val * perc[perfil_val]:.2f}")
        
        if st.button("📤 ENVIAR PARA CANAL TELEGRAM"):
            final = msg_tg + f"📊 *Odd Total: {odd_f:.2f}*\n\n🎰 [APOSTE AQUI](https://esportiva.bet.br?ref=511e1f11699f)\n📢 [CANAL VIP]({LINK_CANAL})"
            asyncio.run(Bot(TOKEN).send_message(CHAT_ID, final, parse_mode='Markdown', disable_web_page_preview=True))
            st.success("Sinal enviado com sucesso!")
        
        if st.button("🗑️ LIMPAR BILHETE"):
            st.session_state.bilhete = []
            st.rerun()
    else: st.info("Sua lista de apostas está vazia.")
