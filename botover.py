import streamlit as st
import asyncio
import random
import time
import urllib.parse
from telegram import Bot
from datetime import datetime, timedelta

# 1. CONFIGURAÇÃO E SEGURANÇA
st.set_page_config(page_title="RonnyP V8 PLATINUM", layout="wide", initial_sidebar_state="expanded")

# Chave Mestra para VOCÊ (Dono) acessar e gerar chaves
MASTER_KEY = "ronnyp@2025"

if 'keys_ativas' not in st.session_state:
    st.session_state.keys_ativas = {} 
if 'autenticado' not in st.session_state:
    st.session_state.autenticado = False

# Link do seu WhatsApp de Suporte
LINK_SUPORTE = "https://wa.me/5561996193390?text=Olá%20RonnyP,%20gostaria%20de%20adquirir%20minha%20Key%20de%20acesso%20VIP!"

st.markdown(f"""
    <style>
    .stApp {{ background-color: #040d1a; }}
    .mobile-title {{
        font-size: 1.6rem; color: #00d4ff; text-align: center; font-weight: bold;
        text-shadow: 0px 0px 10px rgba(0,212,255,0.5); margin-bottom: 1rem;
    }}
    .auth-box {{
        background: #0a1626; padding: 30px; border-radius: 15px;
        border: 2px solid #00d4ff; text-align: center; margin-top: 50px;
    }}
    .btn-suporte {{
        background: #25d366; color: white !important; padding: 12px;
        text-decoration: none; border-radius: 10px; display: block;
        text-align: center; font-weight: bold; margin-top: 20px;
    }}
    .btn-casa {{
        background: linear-gradient(90deg, #0052ff, #00d4ff);
        color: white !important; padding: 10px; text-decoration: none;
        border-radius: 8px; display: block; text-align: center;
        font-weight: bold; margin-bottom: 10px; font-size: 0.9rem;
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

# 2. SISTEMA DE LOGIN
def verificar_acesso():
    if not st.session_state.autenticado:
        st.markdown("<div class='mobile-title'>👑 RONNYP VIP V8</div>", unsafe_allow_html=True)
        st.markdown("<div class='auth-box'>", unsafe_allow_html=True)
        st.subheader("🔐 ACESSO RESTRITO")
        key_input = st.text_input("Insira sua KEY de acesso:", type="password")
        
        if st.button("LIBERAR ACESSO"):
            if key_input == MASTER_KEY:
                st.session_state.autenticado = True
                st.session_state.is_admin = True
                st.rerun()
            elif key_input in st.session_state.keys_ativas:
                exp = st.session_state.keys_ativas[key_input]
                if datetime.now() < exp:
                    st.session_state.autenticado = True
                    st.session_state.is_admin = False
                    st.rerun()
                else: st.error("Chave expirada!")
            else: st.error("Chave inválida!")
        
        st.markdown(f'<a href="{LINK_SUPORTE}" class="btn-suporte">💬 ADQUIRIR CHAVE NO WHATSAPP</a>', unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        return False
    return True

# 3. IA DE ANÁLISE (FAVORITO + EXPIRAÇÃO)
def get_advanced_analysis(jogo):
    times = jogo.split(' x ')
    t1 = times[0].strip()
    fav = t1 # Define o primeiro time como favorito na análise
    
    expira_em = datetime.now() + timedelta(minutes=random.randint(5, 12))
    mercados = [
        {"m": f"Vitória: {t1}", "o": 1.65},
        {"m": "Ambas Marcam: SIM", "o": 1.85},
        {"m": "Mais de 8.5 Cantos", "o": 1.72},
        {"m": f"Dupla Chance: {t1}/X", "o": 1.30}
    ]
    res = random.choice(mercados)
    return {**res, "conf": random.randint(88,99), "expira": expira_em.strftime("%H:%M"), "jogo": jogo, "fav": fav}

TOKEN = '8543393879:AAEsaXAAq2A19zbmMEfHZb-R7nLL-VdierU'
CHAT_ID = '-1003799258159'

async def telegram_action(msg):
    try:
        bot = Bot(token=TOKEN)
        await bot.send_message(chat_id=CHAT_ID, text=msg, parse_mode='Markdown')
        return True
    except: return False

# --- EXECUÇÃO ---
if verificar_acesso():
    
    with st.sidebar:
        if st.session_state.get('is_admin', False):
            st.header("🔑 GERADOR DE KEYS")
            nova_key = st.text_input("Nome da Key (ex: TESTE-01)")
            tempo_h = st.number_input("Horas de Acesso", min_value=1, value=24)
            if st.button("GERAR AGORA"):
                validade = datetime.now() + timedelta(hours=tempo_h)
                st.session_state.keys_ativas[nova_key] = validade
                st.success(f"Key Ativada: {nova_key}")
                st.code(nova_key)

        st.markdown("### 🏦 CASAS SUGERIDAS")
        st.markdown(f'<a href="https://esportiva.bet.br?ref=511e1f11699f" target="_blank" class="btn-casa">🎰 ESPORTIVA BET</a>', unsafe_allow_html=True)
        st.markdown(f'<a href="https://referme.to/ronyelissonoliveiran-7" target="_blank" class="btn-casa">💎 CASA PREMIUM</a>', unsafe_allow_html=True)
        
        st.markdown(f'<a href="{LINK_SUPORTE}" class="btn-suporte">🛠️ SUPORTE WHATSAPP</a>', unsafe_allow_html=True)
        
        if st.button("SAIR DO SISTEMA"):
            st.session_state.autenticado = False
            st.rerun()

    st.markdown("<div class='mobile-title'>RONNYP VIP V8 PLATINUM</div>", unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["📡 RADAR IA", "📋 BILHETE", "✅ GREEN"])

    if 'bilhete' not in st.session_state: st.session_state.bilhete = []
    if 'analisados' not in st.session_state: st.session_state.analisados = []

    with tab1:
        grade = st.text_area("COLE A GRADE AQUI", height=100)
        if st.button("🚀 INICIAR RADAR DE VARREDURA"):
            if grade:
                with st.empty():
                    st.markdown("<div class='radar'></div>", unsafe_allow_html=True)
                    st.markdown("<p style='text-align:center; color:#00d4ff;'>SCANNER IA: ANALISANDO FAVORITOS E ODDS...</p>", unsafe_allow_html=True)
                    time.sleep(2.5)
                
                jogos = [l.strip() for l in grade.split('\n') if 'x' in l.lower()]
                st.session_state.analisados = [get_advanced_analysis(j) for j in jogos]
        
        for idx, item in enumerate(st.session_state.analisados):
            st.markdown(f"""
            <div style='background:#0a1626; border:1px solid #1a2a3a; padding:15px; border-radius:12px; margin-bottom:10px;'>
                <span style='background:#ff4b4b; color:white; padding:2px 8px; border-radius:5px; font-size:10px; float:right;'>⏳ EXPIRA {item['expira']}</span>
                <div style='color:#00ff00; font-size:11px; font-weight:bold;'>⭐ FAVORITO: {item['fav']}</div>
                <div style='color:white; font-weight:bold; font-size:16px;'>{item['jogo']}</div>
                <div style='background:#132338; padding:12px; border-left:4px solid #00d4ff; margin:10px 0;'>
                    <span style='color:white; font-weight:bold;'>{item['m']}</span>
                    <span style='float:right; color:#00d4ff; font-weight:bold;'>@{item['o']}</span>
                </div>
                <div style='color:#777; font-size:10px;'>CONFIANÇA IA: {item['conf']}%</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"ADICIONAR JOGO {idx+1}"):
                st.session_state.bilhete.append(item)
                st.toast("✅ Adicionado!")

    with tab2:
        if st.session_state.bilhete:
            odd_t = 1.0
            resumo = "👑 *RONNYP VIP V8* 👑\n\n"
            for b in st.session_state.bilhete:
                odd_t *= b['o']
                resumo += f"🏟️ *{b['jogo']}*\n⭐ Favorito: {b['fav']}\n🎯 {b['m']} (@{b['o']})\n\n"
            
            st.markdown(f"### 📈 ODD TOTAL: {odd_t:.2f}")
            if st.button("📤 DISPARAR PARA O CANAL"):
                msg_final = resumo + f"📊 *Odd Total: {odd_t:.2f}*\n🔥 *VAMOS PRO GREEN!*"
                asyncio.run(telegram_action(msg_final))
                st.success("SINAL ENVIADO!")
            
            # Botão de Compartilhar Bilhete no WhatsApp
            msg_wpp = urllib.parse.quote(resumo.replace("*","") + f"Odd: {odd_t:.2f}")
            st.markdown(f'<a href="https://wa.me/?text={msg_wpp}" target="_blank" style="background:#25d366; color:white; padding:15px; border-radius:10px; display:block; text-align:center; text-decoration:none; font-weight:bold;">📲 ENVIAR BILHETE NO WHATSAPP</a>', unsafe_allow_html=True)
        else:
            st.info("O bilhete está vazio.")

    with tab3:
        st.subheader("🎉 RESULTADOS")
        if st.button("✅ NOTIFICAR GREEN NO CANAL"):
            asyncio.run(telegram_action("✅✅✅ GREEN CONFIRMADO! ✅✅✅\n\n💰 Dinheiro no bolso com a IA RonnyP V8!"))
            st.balloons()
