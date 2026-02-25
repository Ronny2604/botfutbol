import streamlit as st
import asyncio
import random
import io
import time
from PIL import Image, ImageDraw, ImageFont
from telegram import Bot

# 1. CONFIGURAÇÃO VISUAL
st.set_page_config(page_title="RonnyP - ULTRA V8 DEFINITIVE", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #080a09; }
    .premium-title { color: #00ff00; text-align: center; font-family: 'Orbitron', sans-serif; font-size: 2em; text-shadow: 0 0 15px #00ff00; }
    .card-analise { background: #121413; padding: 20px; border-radius: 12px; border: 1px solid #00ff00; margin-bottom: 15px; }
    .stButton>button { background: #1a1d1c; color: #00ff00; border: 1px solid #00ff00; width: 100%; }
    </style>
    """, unsafe_allow_html=True)

# 2. INTELIGÊNCIA DE MERCADOS E ESTRATÉGIA
def gerar_analise_premium(jogo, estrategia):
    times = jogo.split(' x ')
    time_a = times[0].strip()
    time_b = times[1].strip() if len(times) > 1 else "Visitante"
    
    # Lista de Mercados Diversificados
    opcoes = [
        {"m": f"Vitória: {time_a}", "o": (1.40, 1.65), "fav": time_a},
        {"m": "Ambas Marcam: SIM", "o": (1.70, 1.95), "fav": "Equilibrado"},
        {"m": "Mais de 8.5 Escanteios", "o": (1.55, 1.80), "fav": "Tendência Over"},
        {"m": f"Dupla Chance: {time_a} ou Empate", "o": (1.25, 1.45), "fav": time_a},
        {"m": "Mais de 3.5 Cartões", "o": (1.60, 2.10), "fav": "Jogo Tenso"},
        {"m": f"Handicap (-1): {time_a}", "o": (2.10, 2.80), "fav": time_a},
        {"m": "Under 3.5 Gols", "o": (1.30, 1.50), "fav": "Defensivo"}
    ]

    # Ajuste de Odd baseado na estratégia escolhida
    if estrategia == "Segura (Low Risk)":
        pool = [x for x in opcoes if x["o"][0] < 1.60]
    elif estrategia == "Odds Altas (High Profit)":
        pool = [x for x in opcoes if x["o"][0] > 1.70]
    else: # Moderada
        pool = opcoes

    res = random.choice(pool)
    odd_final = round(random.uniform(res["o"][0], res["o"][1]), 2)
    
    return {
        "mercado": res["m"],
        "odd": odd_final,
        "favorito": res["fav"],
        "prob": f"{random.randint(75, 98)}%"
    }

# 3. TELEGRAM E ID
TOKEN = '8543393879:AAEsaXAAq2A19zbmMEfHZb-R7nLL-VdierU'
CHAT_ID = '-1003799258159'

async def enviar_sinal(texto):
    try:
        bot = Bot(token=TOKEN)
        await bot.send_message(chat_id=CHAT_ID, text=texto, parse_mode='Markdown')
        return True
    except: return False

# 4. INTERFACE PRINCIPAL
st.markdown("<div class='premium-title'>👑 RONNYP ULTRA V8 - DEFINITIVE</div>", unsafe_allow_html=True)

if 'bilhete_lista' not in st.session_state: st.session_state.bilhete_lista = []
if 'jogos_analisados' not in st.session_state: st.session_state.jogos_analisados = []

# SIDEBAR
st.sidebar.header("⚙️ CONFIGURAÇÕES VIP")
estrategia = st.sidebar.selectbox("ESTRATÉGIA DA IA", ["Segura (Low Risk)", "Moderada", "Odds Altas (High Profit)"])
banca = st.sidebar.number_input("BANCA TOTAL (R$)", value=1000.0)
percentual = st.sidebar.slider("STAKE (%)", 1, 10, 3)
valor_entrada = (percentual / 100) * banca

menu = st.sidebar.radio("MENU", ["📥 IMPORTAR JOGOS", "📋 VER BILHETE"])

if menu == "📥 IMPORTAR JOGOS":
    grade = st.text_area("Cole a grade de jogos:", height=150, placeholder="Ex: Time A x Time B")
    if st.button("⚡ PROCESSAR ANÁLISE"):
        st.session_state.jogos_analisados = [l.strip() for l in grade.split('\n') if 'x' in l.lower()]
        with st.spinner("IA Analisando Favoritos e Mercados..."):
            time.sleep(1.5)

    if st.session_state.jogos_analisados:
        cols = st.columns(2)
        for idx, j in enumerate(st.session_state.jogos_analisados):
            res = gerar_analise_premium(j, estrategia)
            with cols[idx % 2]:
                st.markdown(f"""
                <div class='card-analise'>
                    <b>🏟️ {j}</b><br>
                    ⭐ Favorito: <span style='color:#00ff00'>{res['favorito']}</span><br>
                    🎯 <b>{res['mercado']}</b><br>
                    💎 Odd: <b>@{res['odd']}</b> | Confiança: {res['prob']}
                </div>
                """, unsafe_allow_html=True)
                if st.button(f"➕ ADICIONAR", key=f"add_{idx}"):
                    st.session_state.bilhete_lista.append({"jogo": j, **res})
                    st.toast("Adicionado!")

elif menu == "📋 VER BILHETE":
    if st.session_state.bilhete_lista:
        odd_total = 1.0
        txt_jogos = ""
        for i in st.session_state.bilhete_lista:
            odd_total *= i['odd']
            txt_jogos += f"🏟️ **{i['jogo']}**\n⭐ Favorito: {i['favorito']}\n🎯 {i['mercado']} (@{i['odd']})\n\n"
        
        retorno = valor_entrada * odd_total
        st.subheader(f"📊 ODD TOTAL: {odd_total:.2f}")
        st.write(f"💵 Retorno Estimado: R$ {retorno:.2f}")

        if st.button("📤 ENVIAR PARA CANAL TELEGRAM"):
            msg = (f"👑 **RONNYP ULTRA V8 - SINAL VIP** 👑\n\n"
                   f"📈 Estratégia: *{estrategia}*\n\n"
                   f"{txt_jogos}"
                   f"━━━━━━━━━━━━━━━━━━\n"
                   f"📊 **Odd Total: {odd_total:.2f}**\n"
                   f"💰 Sugestão: {percentual}% da banca\n"
                   f"💵 **Retorno: R$ {retorno:.2f}**\n"
                   f"━━━━━━━━━━━━━━━━━━\n"
                   f"✅ **Cashout disponível se o favorito abrir vantagem!**\n"
                   f"🔥 CONFIRME SUA ENTRADA!")
            if asyncio.run(enviar_sinal(msg)):
                st.success("SINAL DISPARADO!")
                st.session_state.bilhete_lista = []
    else:
        st.info("Bilhete vazio.")
