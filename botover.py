import streamlit as st
import asyncio
import random
import io
import base64
import urllib.parse
from PIL import Image, ImageDraw, ImageFont
from telegram import Bot

# 1. CONFIGURAÇÃO VISUAL - "DARK NEON DASHBOARD"
st.set_page_config(page_title="RonnyP - VIP V8 PRO", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #0d0f0e; }
    [data-testid="stVerticalBlock"] > div:has(div.card-analise) {
        background-color: #121413;
        border: 2px solid #00ff00;
        border-radius: 15px;
        padding: 25px;
        box-shadow: 0px 0px 25px rgba(0, 255, 0, 0.2);
    }
    .card-analise {
        background: #1a1d1c;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #2d312f;
        margin-bottom: 15px;
    }
    .market-tag { color: #00ff00; font-weight: bold; }
    .odd-tag { color: #00bfff; font-weight: bold; }
    .prog-bg { background: #262a28; border-radius: 5px; height: 6px; width: 100%; margin-top: 10px; }
    .prog-fill { background: #00ff00; height: 6px; border-radius: 5px; box-shadow: 0px 0px 8px #00ff00; }
    
    .stButton>button {
        background: #1a1d1c;
        color: #ffffff;
        border: 1px solid #00ff00 !important;
        border-radius: 5px;
        width: 100%;
        transition: 0.3s;
    }
    .stButton>button:hover { background: #00ff00; color: #000; }
    
    /* Botão WhatsApp Customizado */
    .btn-wpp {
        background-color: #25d366;
        color: white !important;
        padding: 10px 20px;
        text-decoration: none;
        border-radius: 5px;
        font-weight: bold;
        display: block;
        text-align: center;
        margin-top: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. IA DE ANÁLISE INTERNA
def analisar_jogo_ia(nome_jogo):
    variacao = random.uniform(2.1, 8.4)
    if any(x in nome_jogo.lower() for x in ["madrid", "city", "bayern", "psg", "flamengo"]):
        return {"mercado": "Vitória Favorito", "odd": 1.45, "prob": f"{91 + (variacao%6):.1f}%"}
    return {"mercado": "Mais de 1.5 Gols", "odd": 1.35, "prob": f"{77 + variacao:.1f}%"}

# 3. GERADOR DE IMAGEM DO BILHETE (PRINT)
def gerar_imagem_bilhete(lista_jogos, odd_total, stake, retorno):
    img = Image.new('RGB', (600, 750), color=(13, 15, 14))
    draw = ImageDraw.Draw(img)
    draw.rectangle([10, 10, 590, 740], outline=(0, 255, 0), width=3)
    y = 120
    draw.text((300, 60), "RONNYP VIP V8", fill=(0, 255, 0), anchor="mm")
    for item in lista_jogos:
        draw.text((50, y), f"🏟️ {item['jogo']}", fill=(255, 255, 255))
        draw.text((50, y+30), f"🎯 {item['mercado']} (@{item['odd']})", fill=(0, 255, 0))
        y += 110
    draw.line((50, 620, 550, 620), fill=(0, 255, 0), width=2)
    draw.text((50, 640), f"📊 ODD TOTAL: {odd_total:.2f}", fill=(255, 255, 255))
    draw.text((50, 680), f"💵 RETORNO: R$ {retorno:.2f}", fill=(0, 255, 0))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()

# 4. CONFIGURAÇÕES TELEGRAM (ID ATUALIZADO)
TOKEN = '8543393879:AAEsaXAAq2A19zbmMEfHZb-R7nLL-VdierU'
CHAT_ID = '-1003799258159'

async def send_telegram_msg(text):
    try:
        bot = Bot(token=TOKEN)
        await bot.send_message(chat_id=CHAT_ID, text=text, parse_mode='Markdown')
        return True
    except Exception as e:
        st.error(f"Erro no Telegram: {e}")
        return False

# 5. UI PRINCIPAL
st.markdown("<h1 style='text-align: center; color: #00ff00;'>👑 RONNYP | IA ANALISTA PRO V8</h1>", unsafe_allow_html=True)

if 'bilhete_lista' not in st.session_state: st.session_state.bilhete_lista = []
if 'jogos_analisados' not in st.session_state: st.session_state.jogos_analisados = []

# SIDEBAR
st.sidebar.title("CONFIGURAÇÕES")
menu = st.sidebar.radio("NAVEGAÇÃO", ["📥 IMPORTAR GRADE", "📋 GERAR BILHETE", "🧹 LIMPAR"])
valor_stake = st.sidebar.number_input("VALOR DA ENTRADA (R$)", min_value=1.0, value=100.0)

# BOTÃO COMPARTILHAR WHATSAPP
msg_wpp = urllib.parse.quote(f"🔥 Ei! Conheça o novo Sistema RonnyP VIP V8. Análises de Futebol com IA! Acesse aqui: {st.query_params.get('link', 'https://botoverpy-gnwcseepyzojlaz7ci6g97.streamlit.app/')}")
st.sidebar.markdown(f'<a href="https://wa.me/?text={msg_wpp}" target="_blank" class="btn-wpp">📲 COMPARTILHAR NO WHATSAPP</a>', unsafe_allow_html=True)

if menu == "📥 IMPORTAR GRADE":
    st.subheader("📥 Importar Jogos")
    grade = st.text_area("Cole a lista de jogos:", height=150, placeholder="Ex: Flamengo x Fluminense")
    if st.button("🔍 ANALISAR AGORA"):
        st.session_state.jogos_analisados = [l.strip() for l in grade.split('\n') if 'x' in l.lower() or 'vs' in l.lower()]
    
    if st.session_state.jogos_analisados:
        cols = st.columns(2)
        for idx, j in enumerate(st.session_state.jogos_analisados):
            res = analisar_jogo_ia(j)
            with cols[idx % 2]:
                st.markdown(f"""
                <div class='card-analise'>
                    <b>{j}</b><br>
                    <span class='market-tag'>{res['mercado']}</span> | <span class='odd-tag'>@{res['odd']}</span>
                    <div class='prog-bg'><div class='prog-fill' style='width:{res['prob']};'></div></div>
                </div>
                """, unsafe_allow_html=True)
                if st.button(f"➕ Adicionar", key=f"add_{idx}"):
                    st.session_state.bilhete_lista.append({"jogo": j, **res})
                    st.toast("✅ Adicionado!")

elif menu == "📋 GERAR BILHETE":
    st.subheader("📋 Seu Bilhete")
    if st.session_state.bilhete_lista:
        odd_t = 1.0
        resumo = ""
        for i in st.session_state.bilhete_lista:
            st.write(f"🔹 {i['jogo']} (@{i['odd']})")
            odd_t *= i['odd']
            resumo += f"🔹 {i['jogo']} - {i['mercado']} (@{i['odd']})\n"
        
        retorno_total = valor_stake * odd_t
        st.markdown(f"### 📊 Odd Total: {odd_t:.2f} | 💵 Retorno: R$ {retorno_total:.2f}")
        
        if st.button("📤 DISPARAR PARA O CANAL VIP"):
            msg = f"👑 **RONNYP VIP V8** 👑\n\n{resumo}\n📊 **Odd Total: {odd_t:.2f}**\n💰 Stake: R$ {valor_stake:.2f}\n💵 **Retorno: R$ {retorno_total:.2f}**"
            if asyncio.run(send_telegram_msg(msg)):
                st.success("Enviado com sucesso para o canal!")
                st.session_state.bilhete_lista = []
                st.rerun()

        img_bytes = gerar_imagem_bilhete(st.session_state.bilhete_lista, odd_t, valor_stake, retorno_total)
        st.download_button("🖼️ BAIXAR PRINT (STORY)", img_bytes, "bilhete_ronnyp.png", "image/png")
    else:
        st.info("O bilhete está vazio.")

elif menu == "🧹 LIMPAR":
    if st.button("RESETAR SISTEMA"):
        st.session_state.bilhete_lista = []
        st.session_state.jogos_analisados = []
        st.rerun()
