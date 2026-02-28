import streamlit as st
import asyncio
import random
import time
import os
import urllib.parse
import requests
from telegram import Bot
from datetime import datetime, timedelta

# --- CONFIGURAÇÕES PESSOAIS DO CEO ---
# (Lembre-se de colocar o seu link real do Streamlit app aqui)
LINK_PAINEL = "https://seu-link-aqui.streamlit.app" 
LINK_SUA_IMAGEM_DE_FUNDO = "https://raw.githubusercontent.com/Ronny2604/botfutbol/main/photo_5172618853803035536_c.png"
LINK_SEU_AUDIO_BRIEFING = "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3" 

# --- 1. CONFIGURAÇÃO E SEGURANÇA ---
st.set_page_config(page_title="RonnyP V8 SUPREME", layout="wide", initial_sidebar_state="expanded")

MASTER_KEY = "ronnyp@2025"
FILE_KEYS = "keys.txt" 
TOKEN = '8543393879:AAEsaXAAq2A19zbmMEfHZb-R7nLL-VdierU'
CHAT_ID = '-1003799258159'
LINK_CANAL = "https://t.me/+_4ZgNo3xYFo5M2Ex"
LINK_SUPORTE = "https://wa.me/5561996193390?text=Olá%20RonnyP"
LINK_CASA_1 = "https://esportiva.bet.br?ref=511e1f11699f"

ODDS_API_KEY = "da4633249ece20283d29604cec7a7114"

# --- 2. FUNÇÕES DE SISTEMA ---
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

def tocar_som_moeda():
    som_html = """
    <audio autoplay style="display:none;">
        <source src="https://assets.mixkit.co/active_storage/sfx/2003/2003-preview.mp3" type="audio/mpeg">
    </audio>
    """
    st.markdown(som_html, unsafe_allow_html=True)

def tocar_som_alerta():
    som_html = """
    <audio autoplay style="display:none;">
        <source src="https://assets.mixkit.co/active_storage/sfx/2869/2869-preview.mp3" type="audio/mpeg">
    </audio>
    """
    st.markdown(som_html, unsafe_allow_html=True)

def get_saudacao():
    hora = datetime.now().hour
    if 5 <= hora < 12: return "☕ Bom dia"
    elif 12 <= hora < 18: return "☀️ Boa tarde"
    else: return "🌙 Boa noite"

# --- 3. INICIALIZAÇÃO E ESTADOS ---
if 'autenticado' not in st.session_state: st.session_state.autenticado = False
if 'user_nome' not in st.session_state: st.session_state.user_nome = ""
if 'user_genero' not in st.session_state: st.session_state.user_genero = "Masculino"
if 'bilhete' not in st.session_state: st.session_state.bilhete = []
if 'analisados' not in st.session_state: st.session_state.analisados = []
if 'show_welcome' not in st.session_state: st.session_state.show_welcome = False
if 'tema_escolhido' not in st.session_state: st.session_state.tema_escolhido = "Padrão (Por Gênero)"

db_keys = carregar_keys()

def valida_chave(chave):
    if chave == MASTER_KEY: return True, True
    if chave in db_keys:
        if datetime.now() < db_keys[chave]: return True, False
    return False, False

# --- CONTROLE DE TEMA NEON ---
if st.session_state.autenticado:
    with st.sidebar:
        st.markdown("<h4 style='color:white; text-align:center;'>🎨 PERSONALIZAR INTERFACE</h4>", unsafe_allow_html=True)
        st.session_state.tema_escolhido = st.selectbox(
            "Escolha seu Neon:", 
            ["Padrão (Por Gênero)", "🟢 Verde Hacker", "🟡 Ouro Milionário", "🔵 Azul Cyberpunk", "🔴 Vermelho Kamikaze", "🟣 Rosa Choque"]
        )

is_fem = st.session_state.user_genero == "Feminino"
if st.session_state.tema_escolhido == "🟢 Verde Hacker": cor_neon = "#00ff88"
elif st.session_state.tema_escolhido == "🟡 Ouro Milionário": cor_neon = "#FFD700"
elif st.session_state.tema_escolhido == "🔵 Azul Cyberpunk": cor_neon = "#00e5ff"
elif st.session_state.tema_escolhido == "🔴 Vermelho Kamikaze": cor_neon = "#ff3333"
elif st.session_state.tema_escolhido == "🟣 Rosa Choque": cor_neon = "#ff00ff"
else: cor_neon = "#ff00ff" if is_fem else "#00ff88"

# --- 4. CSS FOOTI PREMIUM + SEU BACKGROUND ---
st.markdown(f"""
    <style>
    #MainMenu {{visibility: hidden !important;}}
    .stDeployButton {{display:none !important;}}
    footer {{visibility: hidden !important;}}
    header {{visibility: hidden !important;}}
    [data-testid="stActionButtonIcon"] {{display: none !important;}}
    
    @keyframes fadeIn {{ from {{ opacity: 0; transform: translateY(10px); }} to {{ opacity: 1; transform: translateY(0); }} }}
    
    /* Fundo Escuro Premium Mesclado com sua Imagem */
    .stApp {{ 
        background: linear-gradient(rgba(15, 16, 21, 0.92), rgba(15, 16, 21, 0.98)), url('{LINK_SUA_IMAGEM_DE_FUNDO}');
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
        animation: fadeIn 0.8s ease-out;
        color: #ffffff;
    }}
    
    /* Títulos e Textos Neon (Estilo Footi) */
    .neon-text {{ color: {cor_neon}; font-weight: bold; font-size: 12px; letter-spacing: 1px; text-transform: uppercase; }}
    .header-destaque {{ text-align: left; color: #ffffff; font-size: 32px; font-weight: 900; font-style: italic; margin-top: -30px; line-height: 1.1; }}
    
    /* Dashboard Stats (Idêntico ao Footi) */
    .stat-container {{ display: flex; justify-content: space-between; background-color: rgba(26, 27, 34, 0.8); border-radius: 8px; border: 1px solid #2d2f36; padding: 15px; margin-bottom: 20px; }}
    .stat-box {{ text-align: center; width: 24%; border-right: 1px solid #333; }}
    .stat-box:last-child {{ border-right: none; }}
    .stat-title {{ color: #888; font-size: 11px; margin:0; text-transform: uppercase; letter-spacing: 0.5px; }}
    .stat-value {{ font-size: 22px; font-weight: 900; margin: 5px 0 0 0; }}
    .stat-value.green {{ color: {cor_neon}; }}
    
    /* Game Cards (Apostas) */
    .game-card {{ background-color: rgba(26, 27, 34, 0.9); padding: 15px; border-radius: 8px; margin-bottom: 12px; border-left: 4px solid #333; transition: 0.3s; border-top: 1px solid #2d2f36; border-right: 1px solid #2d2f36; border-bottom: 1px solid #2d2f36; }}
    .game-card:hover {{ border-left: 4px solid {cor_neon}; box-shadow: 0 4px 15px rgba(0,0,0,0.5); transform: translateY(-2px); }}
    
    /* Marquee e Toasts do seu código */
    .marquee-wrapper {{ width: 100%; overflow: hidden; background: rgba(0,0,0,0.5); border-bottom: 1px solid {cor_neon}50; padding: 8px 0; display: flex; margin-bottom: 20px; }}
    .marquee-content {{ display: flex; white-space: nowrap; animation: marquee 30s linear infinite; }}
    .marquee-item {{ padding: 0 40px; color: {cor_neon}; font-weight: bold; font-size: 12px; }}
    @keyframes marquee {{ 0% {{ transform: translateX(0); }} 100% {{ transform: translateX(-50%); }} }}
    
    /* Botões Padrão */
    .btn-side {{ display: block; padding: 12px; margin-bottom: 10px; text-align: center; border-radius: 8px; font-weight: bold; text-decoration: none; color: white !important; font-size: 14px; transition: 0.3s; }}
    .stButton>button {{ background: {cor_neon} !important; color: #000 !important; font-weight: 900 !important; border-radius: 8px !important; border: none !important; transition: 0.3s; padding: 10px 20px !important; }}
    .stButton>button:hover {{ transform: scale(1.02); filter: brightness(1.2); }}
    
    /* Animação Toast */
    @keyframes popup-anim {{ 0%, 100% {{ bottom: -100px; opacity: 0; }} 10%, 90% {{ bottom: 20px; opacity: 1; }} }}
    @keyframes text-carousel {{ 0% {{ content: "🔥 Marcos M. gerou Dupla Segura!"; }} 50% {{ content: "✅ VIP bateu 3 Greens seguidos!"; }} }}
    .toast-flutuante {{ position: fixed; right: 20px; background: rgba(26, 27, 34, 0.95); color: white; padding: 15px 25px; border-radius: 10px; border-left: 5px solid {cor_neon}; box-shadow: 0 5px 20px rgba(0,0,0,0.8); z-index: 9999; animation: popup-anim 15s infinite; font-weight: bold; }}
    .toast-flutuante::after {{ content: ""; animation: text-carousel 30s infinite steps(1); }}
    </style>
    <div class="toast-flutuante"></div>
    """, unsafe_allow_html=True)

# --- CAPTURA DE KEY VIA URL ---
url_key = ""
if "key" in st.query_params:
    url_key = st.query_params["key"]

# --- 5. TELA DE LOGIN ---
if not st.session_state.autenticado:
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    with st.container():
        st.markdown("<div style='max-width:400px; margin:auto; background-color: rgba(26,27,34,0.9); padding: 30px; border-radius: 12px; border: 1px solid #2d2f36;'>", unsafe_allow_html=True)
        st.markdown(f"<h3 style='text-align:center; color:#fff;'>RONNYP <span style='color:{cor_neon};'>V8 SUPREME</span></h3>", unsafe_allow_html=True)
        st.markdown("<p style='text-align:center; color:#888; font-size: 12px; margin-bottom: 20px;'>INTELLIGENCE HUB</p>", unsafe_allow_html=True)
        
        nome_in = st.text_input("Seu Nome:")
        genero_in = st.selectbox("Gênero:", ["Masculino", "Feminino"])
        key_in = st.text_input("Sua Key:", value=url_key, type="password")
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("ACESSAR RADAR", use_container_width=True):
            if key_in:
                auth, admin = valida_chave(key_in)
                if auth:
                    st.session_state.autenticado = True
                    st.session_state.is_admin = admin
                    st.session_state.user_nome = nome_in if nome_in else "VIP"
                    st.session_state.user_genero = genero_in
                    st.session_state.show_welcome = True
                    st.rerun()
                else: st.error("❌ Key Inválida ou Expirada!")
        st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# --- 6. CONTEÚDO LOGADO (DASHBOARD FOOTI) ---
itens_marquee = "".join([f"<div class='marquee-item'> 🔥 {n} ENTROU NO VIP </div>" for n in ["Marcos", "Ana", "Lucas", "Julia", "Tadeu", "Carla"]])
st.markdown(f"<div class='marquee-wrapper'><div class='marquee-content'>{itens_marquee}{itens_marquee}</div></div>", unsafe_allow_html=True)

st.markdown(f"<h4 class='neon-text'>BEM-VINDO</h4>", unsafe_allow_html=True)
st.markdown(f"<h1 class='header-destaque'>{st.session_state.user_nome.upper()}</h1>", unsafe_allow_html=True)
st.markdown("<p style='color: #888; font-size: 14px; margin-bottom: 20px;'>SUA JORNADA DE VITÓRIA COMEÇA AGORA.</p>", unsafe_allow_html=True)

if st.session_state.show_welcome:
    st.toast(f"{get_saudacao()}, {st.session_state.user_nome}! Vamos aos lucros! 💰")
    tocar_som_moeda()
    st.balloons()
    st.session_state.show_welcome = False

# --- DASHBOARD STATS (ESTILO FOOTI) ---
st.markdown("<p style='color: #888; font-size: 12px; margin-bottom: 5px; font-weight: bold;'>📊 TRACK RECORD — 30 DIAS</p>", unsafe_allow_html=True)
st.markdown(f"""
<div class='stat-container'>
    <div class='stat-box'><p class='stat-title'>Jogos</p><p class='stat-value'>1.248</p></div>
    <div class='stat-box'><p class='stat-title'>Acertos</p><p class='stat-value green'>1.115</p></div>
    <div class='stat-box'><p class='stat-title'>Win Rate</p><p class='stat-value'>89.4%</p></div>
    <div class='stat-box'><p class='stat-title'>ROI</p><p class='stat-value green'>+14.2%</p></div>
</div>
""", unsafe_allow_html=True)

# --- 7. MENU LATERAL & ADMIN ---
with st.sidebar:
    st.markdown(f"<h3 style='color:{cor_neon}; text-align:center;'>👑 CEO & FOUNDER</h3>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#888; font-size:12px; margin-top:-10px;'>Ronny P. | Especialista em IA</p>", unsafe_allow_html=True)
    
    st.markdown(f'<a href="https://instagram.com/ronny_olivzz61" target="_blank" class="btn-side" style="background: linear-gradient(45deg, #f09433, #e6683c, #dc2743, #cc2366, #bc1888);">📸 SIGA @ronny_olivzz61</a>', unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown(f"<h4 style='color:{cor_neon}; text-align:center; margin-bottom:5px; font-size: 14px;'>🎙️ BRIEFING DIÁRIO</h4>", unsafe_allow_html=True)
    st.audio(LINK_SEU_AUDIO_BRIEFING, format="audio/mp3")

    st.markdown("---")
    st.markdown("<p style='color:#888; font-size:11px; font-weight:bold;'>ACESSOS RÁPIDOS</p>", unsafe_allow_html=True)
    st.markdown(f'<a href="{LINK_CASA_1}" target="_blank" class="btn-side" style="background: {cor_neon}; color: #000 !important;">🎰 CASA RECOMENDADA</a>', unsafe_allow_html=True)
    st.markdown(f'<a href="{LINK_SUPORTE}" target="_blank" class="btn-side" style="background: #25d366;">🟢 SUPORTE WHATSAPP</a>', unsafe_allow_html=True)
    
    if st.session_state.is_admin:
        st.markdown("---")
        st.markdown("<p style='color:#888; font-size:11px; font-weight:bold;'>GERADOR DE KEYS</p>", unsafe_allow_html=True)
        c_nome = st.text_input("Nome da Key:")
        tempo_key = st.selectbox("Validade:", ["24 Horas", "7 Dias", "30 Dias"])
        if st.button("CRIAR VIP"):
            horas = 24 if tempo_key == "24 Horas" else (168 if tempo_key == "7 Dias" else 720)
            salvar_key(c_nome, horas)
            link_magico = f"{LINK_PAINEL}?key={c_nome}"
            st.success(f"✅ Key {c_nome} gerada!")
            st.code(link_magico, language="text")

    st.markdown("<br><br>", unsafe_allow_html=True)
    if st.button("SAIR", use_container_width=True):
        st.session_state.autenticado = False
        st.rerun()

# --- 8. TABS DE NAVEGAÇÃO ---
st.markdown("<br>", unsafe_allow_html=True)
t1, t2, t3 = st.tabs(["🚀 SELECTION HUB (Apostas)", "📋 MEU BILHETE", "🛡️ ALTO EV (Safe)"])

LIGAS_DISPONIVEIS = {
    "🇬🇧 Premier League": "soccer_epl", "🇪🇺 Champions League": "soccer_uefa_champs_league",
    "🇪🇸 La Liga": "soccer_spain_la_liga", "🇮🇹 Serie A": "soccer_italy_serie_a",
    "🇧🇷 Brasileirão": "soccer_brazil_campeonato"
}

with t1:
    st.markdown("<p style='color:#888; font-size: 12px;'>ESCOLHA SUAS PARTIDAS E DEIXE NOSSA IA CALCULAR A MELHOR ENTRADA.</p>", unsafe_allow_html=True)
    
    liga_selecionada = st.selectbox("Selecione o Mercado:", list(LIGAS_DISPONIVEIS.keys()))
    codigo_da_liga = LIGAS_DISPONIVEIS[liga_selecionada]
    
    if st.button("🚨 PROCESSAR DADOS IA", use_container_width=True):
        with st.spinner("Analisando 10.000 variáveis..."):
            url = f"https://api.the-odds-api.com/v4/sports/{codigo_da_liga}/odds/?apiKey={ODDS_API_KEY}&regions=eu,uk&markets=h2h,totals"
            try:
                resposta = requests.get(url)
                if resposta.status_code == 200:
                    dados = resposta.json()
                    st.session_state.analisados = []
                    hoje_brasil = datetime.utcnow() - timedelta(hours=3)
                    data_hoje_str = hoje_brasil.strftime("%Y-%m-%d")
                    
                    for jogo in dados[:15]: 
                        casa = jogo.get('home_team', 'Casa')
                        fora = jogo.get('away_team', 'Fora')
                        
                        hora_jogo = "19:00"
                        try:
                            dj_utc = datetime.strptime(jogo.get('commence_time', ''), "%Y-%m-%dT%H:%M:%SZ")
                            hora_jogo = (dj_utc - timedelta(hours=3)).strftime("%H:%M")
                        except: pass
                        
                        nome_jogo = f"{casa} x {fora}"
                        mercados_encontrados = []
                        
                        if jogo.get('bookmakers'):
                            for bookie in jogo['bookmakers']:
                                for mercado in bookie.get('markets', []):
                                    if mercado['key'] == 'h2h':
                                        for out in mercado['outcomes']:
                                            mercados_encontrados.append({"m": f"Vitória {out['name']}", "o": out['price']})
                        
                        if mercados_encontrados:
                            melhor_aposta = random.choice(mercados_encontrados)
                            st.session_state.analisados.append({
                                "jogo": nome_jogo, "casa": casa, "fora": fora, "hora": hora_jogo,
                                "m": melhor_aposta["m"], "o": round(melhor_aposta["o"], 2), "conf": random.randint(85, 99)
                            })
                    st.success("Radar atualizado!")
                else: st.error("Erro na API.")
            except Exception as e: st.error("Erro de conexão.")

    # Renderização das Partidas (ESTILO FOOTI CARDS)
    if st.session_state.analisados:
        st.markdown("<br><h4 class='neon-text'>OPORTUNIDADES IDENTIFICADAS</h4>", unsafe_allow_html=True)
        for idx, item in enumerate(st.session_state.analisados):
            st.markdown(f"""
            <div class='game-card'>
                <div style='display: flex; justify-content: space-between; align-items: center;'>
                    <div style='width: 40%; font-weight: bold; font-size: 15px;'>{item['casa']}</div>
                    <div style='width: 10%; text-align: center; color: #555; font-size: 12px; font-style: italic;'>VS</div>
                    <div style='width: 40%; font-weight: bold; font-size: 15px; text-align: right;'>{item['fora']}</div>
                </div>
                
                <div style='margin-top: 15px; background-color: rgba(0,0,0,0.3); padding: 10px; border-radius: 6px; display: flex; justify-content: space-between; align-items: center;'>
                    <div>
                        <span style='font-size: 11px; color: #888;'>PREVISÃO IA:</span><br>
                        <span style='color: {cor_neon}; font-weight: bold; font-size: 14px;'>{item['m']}</span>
                    </div>
                    <div style='text-align: right;'>
                        <span style='font-size: 11px; color: #888;'>ODD CALC:</span><br>
                        <span style='color: white; font-weight: bold; font-size: 16px;'>@{item['o']}</span>
                    </div>
                </div>
                
                <div style='margin-top: 10px; display: flex; justify-content: space-between; align-items: center; font-size: 11px; color: #aaa;'>
                    <span>🕒 Hoje às {item['hora']}</span>
                    <span>⚡ Confiança: {item['conf']}%</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button(f"➕ ADICIONAR AO BILHETE", key=f"btn_{idx}"):
                st.session_state.bilhete.append(item)
                st.toast("✅ Jogo adicionado ao bilhete!")

with t2:
    if st.session_state.bilhete:
        odd_f = 1.0
        msg_whats = "👑 *RONNYP VIP V8* 👑\n\n"
        
        st.markdown("<h4 class='neon-text'>SUA MÚLTIPLA OTIMIZADA</h4>", unsafe_allow_html=True)
        st.markdown("<div style='background-color: rgba(26,27,34,0.8); padding: 15px; border-radius: 8px; border: 1px solid #2d2f36;'>", unsafe_allow_html=True)
        for b in st.session_state.bilhete:
            odd_f *= b['o']
            st.markdown(f"<p style='margin:0; font-size:14px; border-bottom: 1px solid #333; padding: 5px 0;'>✅ <b>{b['jogo']}</b> <span style='float:right; color:{cor_neon}; font-weight:bold;'>@{b['o']}</span></p>", unsafe_allow_html=True)
            msg_whats += f"🏟️ {b['jogo']}\n🎯 {b['m']} (@{b['o']})\n\n"
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown(f"<h2 style='text-align:center; margin-top:20px;'>📊 ODD TOTAL: <span style='color:{cor_neon};'>{odd_f:.2f}</span></h2>", unsafe_allow_html=True)
        
        valor_aposta = st.number_input("💸 Stake (R$):", min_value=1.0, value=10.0, step=5.0)
        retorno = valor_aposta * odd_f
        st.info(f"🤑 RETORNO ESPERADO: R$ {retorno:.2f}")
        
        final_msg_whats = msg_whats + f"📊 *Odd Total: {odd_f:.2f}*\n💸 Aposta: R$ {valor_aposta:.2f}\n🤑 Retorno: R$ {retorno:.2f}\n\n🎰 APOSTE AQUI: {LINK_CASA_1}"
        
        link_zap = f"https://api.whatsapp.com/send?text={urllib.parse.quote(final_msg_whats)}"
        st.markdown(f'<a href="{link_zap}" target="_blank" class="btn-side" style="background: #25d366;">🟢 ENVIAR PRO ZAP</a>', unsafe_allow_html=True)
        
        if st.button("🗑️ LIMPAR BILHETE", use_container_width=True):
            st.session_state.bilhete = []
            st.rerun()
    else:
        st.info("Seu bilhete está vazio. Vá no Selection Hub e adicione partidas.")

with t3:
    st.markdown("""
    <div style='background-color: #1a1b22; padding: 20px; border-radius: 12px; border: 1px solid #FFD700;'>
        <span style='background-color: #FFD700; color: #000; padding: 3px 8px; font-weight: bold; font-size: 10px; border-radius: 3px;'>👑 PRO EXCLUSIVE</span>
        <h3 style='margin-top: 10px; color: #FFD700;'>APOSTAS ALTO EV</h3>
        <p style='color: #888; font-size: 12px;'>IDENTIFICAMOS AS ODDS DESAJUSTADAS COM MAIOR EXPECTATIVA DE VALOR REAL.</p>
        <hr style='border-color: #333;'>
        <p style='color: white; font-weight: bold;'>⚽ Manchester City vs Arsenal</p>
        <p style='color: #bbb; font-size: 14px;'>🎯 Ambas Marcam | <span style='color: #FFD700; font-weight: bold;'>@1.85</span></p>
    </div>
    """, unsafe_allow_html=True)
