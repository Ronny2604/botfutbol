import streamlit as st
import asyncio
import random
import io
import base64
from PIL import Image, ImageDraw, ImageFont
from telegram import Bot

# 1. CONFIGURAÇÃO VISUAL - "DARK NEON DASHBOARD"
st.set_page_config(page_title="RonnyP - VIP V8 PRO", layout="wide")

# Função para converter imagem local em base64 (Marca d'água no fundo)
def get_base64(bin_file):
    try:
        with open(bin_file, 'rb') as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except: return None

logo_bg = get_base64('photo_5172618853803035536_c.jpg')
bg_css = f'url("data:image/jpg;base64,{logo_bg}")' if logo_bg else "none"

st.markdown(f"""
    <style>
    .stApp {{
        background: linear-gradient(rgba(13, 15, 14, 0.9), rgba(13, 15, 14, 0.9)), {bg_css};
        background-size: 300px;
        background-repeat: repeat;
    }}
    [data-testid="stVerticalBlock"] > div:has(div.card-analise) {{
        background-color: #121413;
        border: 2px solid #00ff00;
        border-radius: 15px;
        padding: 25px;
        box-shadow: 0px 0px 25px rgba(0, 255, 0, 0.2);
    }}
    .card-analise {{
        background: #1a1d1c;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #2d312f;
        margin-bottom: 15px;
    }}
    .market-tag {{ color: #00ff00; font-weight: bold; }}
    .odd-tag {{ color: #00bfff; font-weight: bold; }}
    .prog-fill {{ background: #00ff00; height: 6px; border-radius: 5px; box-shadow: 0px 0px 8px #00ff00; }}
    .stButton>button {{ background: #1a1d1c; color: #fff; border: 1px solid #00ff00; border-radius: 5px; width: 100%; }}
    </style>
    """, unsafe_allow_html=True)

# 2. IA DE ANÁLISE (SIMULADA - SEM NECESSIDADE DE API KEY)
def analisar_jogo_ia(nome_jogo):
    variacao = random.uniform(2.1, 8.4)
    # Lógica simples para gerar palpites baseados no nome do time
    if "madrid" in nome_jogo.lower() or "city" in nome_jogo.lower():
        return {"mercado": "Vitória Favorito", "odd": 1.45, "prob": f"{92 + (variacao%5):.1f}%"}
    return {"mercado": "Mais de 1.5 Gols", "odd": 1.38, "prob": f"{78 + variacao:.1f}%"}

# 3. GERADOR DE IMAGEM (PRINT)
def gerar_imagem_bilhete(lista_jogos, odd_total, stake, retorno):
    img = Image.new('RGB', (600, 700), color=(13, 15, 14))
    draw = ImageDraw.Draw(img)
    try:
        draw.rectangle([10, 10, 590, 690], outline=(0, 255, 0), width=3)
        y = 100
        draw.text((300, 50), "RONNYP VIP V8", fill=(0, 255, 0), anchor="mm")
        for item in lista_jogos:
            draw.text((50, y), f"🏟️ {item['jogo']}", fill=(255, 255, 255))
            draw.text((50, y+30), f"🎯 {item['mercado']} (@{item['odd']})", fill=(0, 255, 0))
            y += 100
        draw.text((50, 600), f"📊 ODD: {odd_total:.2f} | 💵 RETORNO: R$ {retorno:.2f}", fill=(0, 255, 0))
    except: pass
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()

# 4. CONFIGURAÇÕES TELEGRAM
TOKEN = '8543393879:AAEsaXAAq2A19zbmMEfHZb-R7nLL-VdierU'
CHAT_ID = '7997581470' # <--- Certifique-se de que o Bot é admin deste Canal!

async def send_telegram_msg(text):
    bot = Bot(token=TOKEN)
    await bot.send_message(chat_id=CHAT_ID, text=text, parse_mode='Markdown')

# 5. UI PRINCIPAL
st.markdown("<h1 style='text-align: center; color: #00ff00;'>👑 RONNYP | VIP V8 PRO</h1>", unsafe_allow_html=True)

if 'bilhete_lista' not in st.session_state: st.session_state.bilhete_lista = []
if 'jogos_analisados' not in st.session_state: st.session_state.jogos_analisados = []

menu = st.sidebar.radio("MENU", ["📥 IMPORTAR GRADE", "📋 GERAR BILHETE"])
valor_stake = st.sidebar.number_input("STAKE (R$)", min_value=1.0, value=100.0)

if menu == "📥 IMPORTAR GRADE":
    input_jogos = st.text_area("Cole os jogos (Ex: Real Madrid x Barcelona):", height=150)
    if st.button("🔍 ANALISAR AGORA"):
        st.session_state.jogos_analisados = [l.strip() for l in input_jogos.split('\n') if 'x' in l.lower() or 'vs' in l.lower()]
    
    if st.session_state.jogos_analisados:
        cols = st.columns(2)
        for idx, j in enumerate(st.session_state.jogos_analisados):
            res = analisar_jogo_ia(j)
            with cols[idx % 2]:
                st.markdown(f"<div class='card-analise'><b>{j}</b><br><span class='market-tag'>{res['mercado']}</span> | <span class='odd-tag'>@{res['odd']}</span><div style='background:#333; height:6px; margin-top:10px;'><div class='prog-fill' style='width:{res['prob']};'></div></div></div>", unsafe_allow_html=True)
                if st.button(f"➕ ADICIONAR", key=f"btn_{idx}"):
                    st.session_state.bilhete_lista.append({"jogo": j, **res})
                    st.toast("Adicionado!")

elif menu == "📋 GERAR BILHETE":
    if st.session_state.bilhete_lista:
        odd_t = 1.0
        resumo = ""
        for i in st.session_state.bilhete_lista:
            st.write(f"✅ {i['jogo']} (@{i['odd']})")
            odd_t *= i['odd']
            resumo += f"✅ {i['jogo']} - {i['mercado']} (@{i['odd']})\n"
        
        retorno = valor_stake * odd_t
        st.subheader(f"📊 ODD TOTAL: {odd_t:.2f} | 💵 RETORNO: R$ {retorno:.2f}")
        
        if st.button("📤 ENVIAR PARA TELEGRAM"):
            msg = f"👑 **RONNYP VIP SINAL** 👑\n\n{resumo}\n📊 Odd: {odd_t:.2f}\n💰 Stake: R$ {valor_stake}\n💵 Retorno: R$ {retorno:.2f}"
            asyncio.run(send_telegram_msg(msg))
            st.session_state.bilhete_lista = []
            st.success("Enviado e Limpo!")
            st.rerun()
            
        img_bytes = gerar_imagem_bilhete(st.session_state.bilhete_lista, odd_t, valor_stake, retorno)
        st.download_button("🖼️ BAIXAR PRINT PARA STORIES", img_bytes, "bilhete.png", "image/png")
    else:
        st.info("Bilhete vazio.")
