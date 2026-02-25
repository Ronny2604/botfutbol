import streamlit as st
import asyncio
import random
import io
import time
from PIL import Image, ImageDraw, ImageFont
from telegram import Bot

# 1. CONFIGURAÇÃO MOBILE-FIRST (ESTILO APP)
st.set_page_config(page_title="RonnyP V8 MOBILE", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    /* Reset para Mobile */
    .block-container { padding-top: 1rem; padding-bottom: 1rem; padding-left: 0.5rem; padding-right: 0.5rem; }
    
    .stApp { background-color: #050706; }
    
    /* Título Mobile */
    .mobile-title {
        font-size: 1.5rem;
        color: #00ff00;
        text-align: center;
        font-weight: bold;
        text-transform: uppercase;
        margin-bottom: 1rem;
        border-bottom: 2px solid #00ff00;
        padding-bottom: 5px;
    }

    /* Cards de Jogo Estilo Mobile */
    .mobile-card {
        background: #111;
        border: 1px solid #222;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 10px;
    }
    
    .game-header { color: #fff; font-size: 1rem; font-weight: bold; margin-bottom: 5px; }
    .fav-tag { color: #00ff00; font-size: 0.8rem; text-transform: uppercase; }
    .market-box { background: #1a1a1a; padding: 10px; border-radius: 5px; border-left: 4px solid #00ff00; margin: 10px 0; }
    .odd-badge { background: #00ff00; color: #000; padding: 2px 8px; border-radius: 5px; font-weight: bold; float: right; }

    /* Botões Grandes para o Polegar */
    .stButton>button {
        height: 3.5rem;
        font-size: 1rem !important;
        font-weight: bold !important;
        border-radius: 12px !important;
        background: #111 !important;
        border: 1px solid #00ff00 !important;
        color: #00ff00 !important;
        width: 100%;
    }
    
    /* Input de Texto Otimizado */
    .stTextArea textarea { background-color: #111 !important; color: white !important; border: 1px solid #333 !important; }
    
    /* Esconder menu Streamlit para parecer App */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# 2. LOGICA DE IA (DIVERSIFICADA)
def get_ia_analysis(jogo, est):
    times = jogo.split(' x ')
    t1 = times[0].strip()
    t2 = times[1].strip() if len(times) > 1 else "Visitante"
    
    # Pool de mercados ultra variados
    pool = [
        {"m": f"Vitória: {t1}", "o": 1.55, "fav": t1, "cat": "Segura"},
        {"m": f"Handicap (-1): {t1}", "o": 2.20, "fav": t1, "cat": "Altas"},
        {"m": "Ambas Marcam: SIM", "o": 1.85, "fav": "Equilibrado", "cat": "Moderada"},
        {"m": "Mais de 8.5 Cantos", "o": 1.65, "fav": "Ataque Total", "cat": "Segura"},
        {"m": "Over 1.5 Cartões", "o": 1.45, "fav": "Jogo Tenso", "cat": "Segura"},
        {"m": f"Dupla Chance: {t1}/Empate", "o": 1.32, "fav": t1, "cat": "Segura"},
        {"m": "Under 3.5 Gols", "o": 1.40, "fav": "Defensivo", "cat": "Segura"}
    ]
    
    if est == "Odds Altas":
        final = [x for x in pool if x["o"] > 1.70]
    elif est == "Segura":
        final = [x for x in pool if x["o"] < 1.60]
    else:
        final = pool

    res = random.choice(final)
    return res

# 3. TELEGRAM CONFIG
TOKEN = '8543393879:AAEsaXAAq2A19zbmMEfHZb-R7nLL-VdierU'
CHAT_ID = '-1003799258159'

# 4. INTERFACE PRINCIPAL (TELA ÚNICA MOBILE)
st.markdown("<div class='mobile-title'>RONNYP VIP V8 PRO</div>", unsafe_allow_html=True)

if 'bilhete' not in st.session_state: st.session_state.bilhete = []
if 'analisados' not in st.session_state: st.session_state.analisados = []

# Tabs Mobile (Mais fácil que menu lateral)
tab1, tab2, tab3 = st.tabs(["📥 GRADE", "📋 BILHETE", "⚙️ CONFIG"])

with tab3:
    st.subheader("Configurações")
    estrategia = st.selectbox("Estratégia", ["Segura", "Moderada", "Odds Altas"])
    banca = st.number_input("Sua Banca (R$)", value=1000.0)
    percent = st.slider("Stake %", 1, 10, 3)
    valor_entrada = (percent/100) * banca
    st.success(f"Stake por sinal: R$ {valor_entrada:.2f}")

with tab1:
    grade = st.text_area("COLE A GRADE AQUI", height=120, placeholder="Time A x Time B\nTime C x Time D")
    if st.button("⚡ ANALISAR JOGOS"):
        jogos = [l.strip() for l in grade.split('\n') if 'x' in l.lower()]
        st.session_state.analisados = []
        for j in jogos:
            res = get_ia_analysis(j, estrategia)
            st.session_state.analisados.append({"jogo": j, **res})
    
    for idx, item in enumerate(st.session_state.analisados):
        st.markdown(f"""
        <div class='mobile-card'>
            <div class='game-header'>{item['jogo']}</div>
            <div class='fav-tag'>⭐ Favorito: {item['fav']}</div>
            <div class='market-box'>
                <span style='color:#00ff00; font-weight:bold;'>{item['m']}</span>
                <span class='odd-badge'>@{item['o']}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button(f"ADICIONAR JOGO {idx+1}", key=f"add_{idx}"):
            st.session_state.bilhete.append(item)
            st.toast("✅ Adicionado!")

with tab2:
    if st.session_state.bilhete:
        odd_t = 1.0
        resumo = ""
        for b in st.session_state.bilhete:
            odd_t *= b['o']
            st.markdown(f"✅ **{b['jogo']}** (@{b['o']})")
            resumo += f"🏟️ **{b['jogo']}**\n🎯 {b['m']} (@{b['o']})\n\n"
        
        retorno = valor_entrada * odd_t
        st.markdown(f"### ODD TOTAL: {odd_t:.2f}")
        st.markdown(f"## RETORNO: R$ {retorno:.2f}")
        
        if st.button("📤 ENVIAR PARA CANAL VIP"):
            msg = (f"👑 **RONNYP VIP V8 - MOBILE** 👑\n\n"
                   f"{resumo}"
                   f"📊 **Odd Total: {odd_t:.2f}**\n"
                   f"💰 Stake: {percent}% (R$ {valor_entrada:.2f})\n"
                   f"💵 **Retorno: R$ {retorno:.2f}**\n\n"
                   f"✅ Cashout Sugerido!\n"
                   f"🔥 VAMOS PRO GREEN!")
            
            async def send():
                bot = Bot(token=TOKEN)
                await bot.send_message(chat_id=CHAT_ID, text=msg, parse_mode='Markdown')
            
            asyncio.run(send())
            st.success("ENVIADO!")
            st.session_state.bilhete = []
    else:
        st.info("Nenhum jogo no bilhete.")
