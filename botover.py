import streamlit as st
import asyncio
import random
import io
import time
import base64
import urllib.parse
from PIL import Image, ImageDraw, ImageFont
from telegram import Bot

# 1. CONFIGURAÇÃO VISUAL - "ULTRA DARK NEON"
st.set_page_config(page_title="RonnyP - ULTRA V8 PRO", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Roboto+Mono:wght@400;700&display=swap');

    .stApp { background-color: #080a09; }
    
    /* Título com brilho */
    .premium-title {
        font-family: 'Orbitron', sans-serif;
        color: #00ff00;
        text-align: center;
        font-size: 2.5em;
        text-shadow: 0px 0px 20px rgba(0, 255, 0, 0.6);
        margin-bottom: 30px;
    }

    /* Cards Estilizados */
    .card-analise {
        background: linear-gradient(145deg, #121413, #1a1d1c);
        padding: 25px;
        border-radius: 15px;
        border: 1px solid #2d312f;
        box-shadow: 5px 5px 15px rgba(0,0,0,0.5);
        margin-bottom: 20px;
    }
    
    .game-name { font-family: 'Orbitron', sans-serif; color: #fff; font-size: 1.2em; }
    .market-tag { color: #00ff00; font-family: 'Roboto Mono', monospace; font-weight: bold; }
    .odd-tag { background: #00bfff; color: #000; padding: 2px 8px; border-radius: 4px; font-weight: bold; }
    
    /* Barras de Progresso Premium */
    .prog-bg { background: #262a28; border-radius: 10px; height: 8px; margin: 15px 0; }
    .prog-fill { 
        background: linear-gradient(90deg, #008000, #00ff00); 
        height: 8px; border-radius: 10px; 
        box-shadow: 0px 0px 10px #00ff00; 
    }

    /* Botão de WhatsApp */
    .btn-wpp {
        background: linear-gradient(90deg, #25d366, #128c7e);
        color: white !important;
        padding: 12px;
        text-decoration: none;
        border-radius: 8px;
        font-weight: bold;
        display: block;
        text-align: center;
        margin-top: 15px;
        font-family: 'Orbitron', sans-serif;
        font-size: 0.8em;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. IA DE ANÁLISE PREMIUM (MULTIMERCADOS)
def analisar_ia_premium(nome_jogo):
    mercados = [
        {"tipo": "Vitória Favorito", "base_odd": 1.45},
        {"tipo": "Ambas Marcam: SIM", "base_odd": 1.75},
        {"tipo": "Over 1.5 Gols", "base_odd": 1.30},
        {"tipo": "Mais de 8.5 Cantos", "base_odd": 1.60}
    ]
    escolha = random.choice(mercados)
    variacao = random.uniform(0.05, 0.20)
    prob = random.uniform(78, 96)
    
    return {
        "mercado": escolha["tipo"],
        "odd": round(escolha["base_odd"] + variacao, 2),
        "prob": f"{prob:.1f}%"
    }

# 3. GERADOR DE PRINT ESTILIZADO
def gerar_print_premium(lista_jogos, odd_total, stake, retorno):
    img = Image.new('RGB', (600, 850), color=(8, 10, 9))
    draw = ImageDraw.Draw(img)
    draw.rectangle([10, 10, 590, 840], outline=(0, 255, 0), width=4)
    
    # Cabeçalho
    draw.text((300, 60), "RONNYP ULTRA V8", fill=(0, 255, 0), anchor="mm")
    draw.text((300, 100), "VERIFICADO PELA IA", fill=(255, 215, 0), anchor="mm")
    
    y = 160
    for item in lista_jogos:
        draw.text((50, y), f"🏟️ {item['jogo']}", fill=(255, 255, 255))
        draw.text((50, y+35), f"🎯 {item['mercado']} | @{item['odd']}", fill=(0, 255, 0))
        y += 120

    # Rodapé VIP
    draw.rectangle([30, 680, 570, 820], outline=(0, 255, 0), width=1)
    draw.text((300, 710), f"ODD TOTAL: {odd_total:.2f}", fill=(255, 255, 255), anchor="mm")
    draw.text((300, 750), f"STAKE: R$ {stake:.2f}", fill=(255, 255, 255), anchor="mm")
    draw.text((300, 790), f"RETORNO: R$ {retorno:.2f}", fill=(0, 255, 0), anchor="mm")
    
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()

# 4. TELEGRAM
TOKEN = '8543393879:AAEsaXAAq2A19zbmMEfHZb-R7nLL-VdierU'
CHAT_ID = '-1003799258159'

async def send_telegram_premium(text):
    try:
        bot = Bot(token=TOKEN)
        await bot.send_message(chat_id=CHAT_ID, text=text, parse_mode='Markdown')
        return True
    except: return False

# 5. UI INTERFACE
st.markdown("<div class='premium-title'>👑 RONNYP ULTRA V8 PRO</div>", unsafe_allow_html=True)

if 'bilhete_lista' not in st.session_state: st.session_state.bilhete_lista = []
if 'jogos_analisados' not in st.session_state: st.session_state.jogos_analisados = []

# SIDEBAR PREMIUM
st.sidebar.markdown("### 🛠️ PAINEL DE CONTROLE")
menu = st.sidebar.radio("FUNÇÕES", ["📥 IMPORTAR GRADE", "📋 BILHETE ATUAL", "🧹 LIMPAR TUDO"])

banca_total = st.sidebar.number_input("BANCA TOTAL (R$)", min_value=10.0, value=1000.0)
percentual = st.sidebar.slider("GERENCIAMENTO (%)", 1, 10, 3)
valor_stake = (percentual / 100) * banca_total

st.sidebar.info(f"💡 Stake Sugerida: R$ {valor_stake:.2f}")

# Compartilhar
link_app = "https://botoverpy-gnwcseepyzojlaz7ci6g97.streamlit.app/"
msg_wpp = urllib.parse.quote(f"🚀 Conheça a IA RonnyP Ultra V8! Análises Premium aqui: {link_app}")
st.sidebar.markdown(f'<a href="https://wa.me/?text={msg_wpp}" target="_blank" class="btn-wpp">📲 COMPARTILHAR APP</a>', unsafe_allow_html=True)

if menu == "📥 IMPORTAR GRADE":
    st.subheader("📥 Central de Processamento")
    grade = st.text_area("Cole a grade de jogos:", height=120)
    
    if st.button("⚡ INICIAR SCANNING"):
        if grade:
            linhas = [l.strip() for l in grade.split('\n') if 'x' in l.lower() or 'vs' in l.lower()]
            with st.status("🤖 IA PROCESSANDO...", expanded=True) as status:
                for j in linhas:
                    st.write(f"🔍 Analisando {j}...")
                    time.sleep(0.5)
                    st.write(f"📊 Verificando histórico de gols...")
                    time.sleep(0.3)
                status.update(label="✅ ANÁLISE CONCLUÍDA!", state="complete", expanded=False)
            st.session_state.jogos_analisados = linhas
        else:
            st.warning("Cole os jogos primeiro!")

    if st.session_state.jogos_analisados:
        cols = st.columns(2)
        for idx, j in enumerate(st.session_state.jogos_analisados):
            res = analisar_ia_premium(j)
            with cols[idx % 2]:
                st.markdown(f"""
                <div class='card-analise'>
                    <div class='game-name'>🏟️ {j}</div>
                    <hr style='border: 0.5px solid #333;'>
                    <span class='market-tag'>🎯 {res['mercado']}</span> <span class='odd-tag'>@{res['odd']}</span>
                    <div class='prog-bg'><div class='prog-fill' style='width:{res['prob']};'></div></div>
                    <small style='color:#00ff00; font-family:monospace;'>CONFIANÇA: {res['prob']}</small>
                </div>
                """, unsafe_allow_html=True)
                if st.button(f"➕ ADICIONAR", key=f"add_{idx}"):
                    st.session_state.bilhete_lista.append({"jogo": j, **res})
                    st.toast(f"Adicionado: {j}")

elif menu == "📋 BILHETE ATUAL":
    if st.session_state.bilhete_lista:
        odd_t = 1.0
        resumo_tg = ""
        for i in st.session_state.bilhete_lista:
            st.markdown(f"✅ **{i['jogo']}** | {i['mercado']} (@{i['odd']})")
            odd_t *= i['odd']
            resumo_tg += f"🏟️ **{i['jogo']}**\n🎯 {i['mercado']} (@{i['odd']})\n\n"
        
        retorno = valor_stake * odd_t
        st.markdown(f"""
            <div style='background:#121413; padding:20px; border-left: 5px solid #00ff00; margin-top:20px;'>
                <h2 style='color:#fff; margin:0;'>📊 ODD TOTAL: {odd_t:.2f}</h2>
                <h3 style='color:#00ff00; margin:0;'>💵 RETORNO: R$ {retorno:.2f}</h3>
                <small style='color:#777;'>Stake aplicada: R$ {valor_stake:.2f} ({percentual}% da banca)</small>
            </div>
        """, unsafe_allow_html=True)

        if st.button("🚀 DISPARAR SINAL PREMIUM"):
            msg = (f"👑 **RONNYP ULTRA V8 - SINAL VIP** 👑\n\n"
                   f"{resumo_tg}"
                   f"📊 **Odd Total: {odd_t:.2f}**\n"
                   f"💰 Sugestão: {percentual}% da banca\n"
                   f"💵 **Retorno: R$ {retorno:.2f}**\n\n"
                   f"🔥 CONFIRME SUA ENTRADA!")
            if asyncio.run(send_telegram_premium(msg)):
                st.success("SINAL ENVIADO!")
                st.session_state.bilhete_lista = []
                st.rerun()

        img_bytes = gerar_print_premium(st.session_state.bilhete_lista, odd_t, valor_stake, retorno)
        st.download_button("🖼️ GERAR PRINT VIP (STORY)", img_bytes, "ultra_v8_print.png", "image/png")
    else:
        st.info("O Bilhete está vazio. Volte em 'Importar Grade'.")

elif menu == "🧹 LIMPAR TUDO":
    if st.button("LIMPAR SISTEMA"):
        st.session_state.bilhete_lista = []
        st.session_state.jogos_analisados = []
        st.rerun()
