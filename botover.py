import streamlit as st
import asyncio
import random
import io
import urllib.parse
from PIL import Image, ImageDraw, ImageFont
from telegram import Bot

# 1. CONFIGURAÇÃO MOBILE-FIRST "BLUE PREMIUM"
st.set_page_config(page_title="RonnyP V8 BLUE", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    .block-container { padding-top: 1rem; padding-bottom: 1rem; padding-left: 0.5rem; padding-right: 0.5rem; }
    
    /* Paleta de Cores Blue Premium */
    .stApp { background-color: #040d1a; }
    
    .mobile-title {
        font-size: 1.4rem;
        color: #00d4ff;
        text-align: center;
        font-weight: bold;
        margin-bottom: 1rem;
        border-bottom: 1px solid #1a2a3a;
        padding-bottom: 10px;
    }

    .mobile-card {
        background: #0a1626;
        border: 1px solid #1a2a3a;
        border-radius: 12px;
        padding: 15px;
        margin-bottom: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    
    .game-header { color: #ffffff; font-size: 1rem; font-weight: bold; }
    .fav-tag { color: #00d4ff; font-size: 0.75rem; font-weight: bold; }
    .market-box { background: #132338; padding: 12px; border-radius: 8px; border-left: 4px solid #00d4ff; margin: 10px 0; }
    .odd-badge { background: #00d4ff; color: #040d1a; padding: 3px 10px; border-radius: 6px; font-weight: bold; float: right; }

    /* Botões Mobile */
    .stButton>button {
        height: 3.5rem;
        border-radius: 12px !important;
        background: #00d4ff !important;
        color: #040d1a !important;
        font-weight: bold !important;
        border: none !important;
        width: 100%;
    }
    
    /* Botão WhatsApp */
    .btn-wpp {
        background-color: #25d366;
        color: white !important;
        padding: 15px;
        text-decoration: none;
        border-radius: 12px;
        font-weight: bold;
        display: block;
        text-align: center;
        margin-top: 10px;
        font-size: 1rem;
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stTabs [data-baseweb="tab-list"] { background-color: #040d1a; border-radius: 10px; }
    .stTabs [data-baseweb="tab"] { color: #fff; }
    .stTabs [aria-selected="true"] { color: #00d4ff !important; border-bottom-color: #00d4ff !important; }
    </style>
    """, unsafe_allow_html=True)

# 2. IA DE ANÁLISE DIVERSIFICADA
def get_ia_analysis(jogo, est):
    times = jogo.split(' x ')
    t1 = times[0].strip()
    
    mercados = [
        {"m": f"Vitória: {t1}", "o": 1.62, "fav": t1},
        {"m": "Ambas Marcam: SIM", "o": 1.80, "fav": "Equilibrado"},
        {"m": "Mais de 8.5 Cantos", "o": 1.70, "fav": "Ataque"},
        {"m": f"Dupla Chance: {t1}/X", "o": 1.35, "fav": t1},
        {"m": "Handicap (0): " + t1, "o": 1.50, "fav": t1},
        {"m": "Over 1.5 Cartões", "o": 1.48, "fav": "Tenso"},
        {"m": "Under 3.5 Gols", "o": 1.38, "fav": "Defensivo"}
    ]
    
    if est == "Odds Altas":
        final = [x for x in mercados if x["o"] >= 1.70]
    elif est == "Segura":
        final = [x for x in mercados if x["o"] < 1.60]
    else:
        final = mercados

    return random.choice(final if final else mercados)

# 3. TELEGRAM CONFIG
TOKEN = '8543393879:AAEsaXAAq2A19zbmMEfHZb-R7nLL-VdierU'
CHAT_ID = '-1003799258159'

# 4. INTERFACE
st.markdown("<div class='mobile-title'>RONNYP VIP V8 BLUE</div>", unsafe_allow_html=True)

if 'bilhete' not in st.session_state: st.session_state.bilhete = []
if 'analisados' not in st.session_state: st.session_state.analisados = []

tab1, tab2, tab3 = st.tabs(["📥 GRADE", "📋 BILHETE", "⚙️ CONFIG"])

with tab3:
    st.subheader("Painel de Controle")
    estrategia = st.selectbox("Estratégia", ["Moderada", "Segura", "Odds Altas"])
    banca = st.number_input("Banca Atual (R$)", value=1000.0)
    percent = st.slider("Stake %", 1, 10, 3)
    valor_entrada = (percent/100) * banca
    st.info(f"Entrada Sugerida: R$ {valor_entrada:.2f}")

with tab1:
    grade = st.text_area("COLE OS JOGOS", height=120, placeholder="Ex: Flamengo x Vasco")
    if st.button("🔍 ANALISAR AGORA"):
        jogos = [l.strip() for l in grade.split('\n') if 'x' in l.lower()]
        st.session_state.analisados = []
        for j in jogos:
            res = get_ia_analysis(j, estrategia)
            st.session_state.analisados.append({"jogo": j, **res})
    
    for idx, item in enumerate(st.session_state.analisados):
        st.markdown(f"""
        <div class='mobile-card'>
            <div class='game-header'>{item['jogo']}</div>
            <div class='fav-tag'>⭐ FAVORITO: {item['fav']}</div>
            <div class='market-box'>
                <span style='color:#fff;'>{item['m']}</span>
                <span class='odd-badge'>@{item['o']}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button(f"ADICIONAR À LISTA {idx+1}", key=f"add_{idx}"):
            st.session_state.bilhete.append(item)
            st.toast("✅ Adicionado!")

with tab2:
    if st.session_state.bilhete:
        odd_t = 1.0
        resumo_texto = "👑 *RONNYP VIP V8 BLUE* 👑\n\n"
        for b in st.session_state.bilhete:
            odd_t *= b['o']
            st.markdown(f"🔹 **{b['jogo']}** (@{b['o']})")
            resumo_texto += f"🏟️ *{b['jogo']}*\n🎯 {b['m']} (@{b['o']})\n\n"
        
        retorno = valor_entrada * odd_t
        resumo_texto += f"📊 *Odd Total: {odd_t:.2f}*\n💰 Stake: R$ {valor_entrada:.2f}\n💵 *Retorno: R$ {retorno:.2f}*"
        
        st.markdown(f"### 🚀 ODD TOTAL: {odd_t:.2f}")
        st.markdown(f"## 💵 RETORNO: R$ {retorno:.2f}")
        
        # Botão Telegram
        if st.button("📤 ENVIAR PARA CANAL VIP"):
            async def send():
                bot = Bot(token=TOKEN)
                await bot.send_message(chat_id=CHAT_ID, text=resumo_texto, parse_mode='Markdown')
            asyncio.run(send())
            st.success("ENVIADO AO CANAL!")
        
        # Botão WhatsApp Compartilhar
        msg_wpp = urllib.parse.quote(resumo_texto.replace("*", "")) # Remove asteriscos para o WPP
        st.markdown(f'<a href="https://wa.me/?text={msg_wpp}" target="_blank" class="btn-wpp">📲 COMPARTILHAR NO WHATSAPP</a>', unsafe_allow_html=True)
        
        if st.button("🧹 LIMPAR BILHETE"):
            st.session_state.bilhete = []
            st.rerun()
    else:
        st.info("O bilhete está vazio.")
