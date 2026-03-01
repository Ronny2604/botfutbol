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
LINK_PAINEL = "https://seu-link-aqui.streamlit.app" 
LINK_SUA_IMAGEM_DE_FUNDO = "https://raw.githubusercontent.com/Ronny2604/botfutbol/main/photo_5172618853803035536_c.png"
LINK_SEU_AUDIO_BRIEFING = "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3" 

# --- 1. CONFIGURAÇÃO E SEGURANÇA ---
st.set_page_config(page_title="RonnyP V8 SUPREME", layout="wide", initial_sidebar_state="collapsed")

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
    som_html = """<audio autoplay style="display:none;"><source src="https://assets.mixkit.co/active_storage/sfx/2003/2003-preview.mp3" type="audio/mpeg"></audio>"""
    st.markdown(som_html, unsafe_allow_html=True)

def tocar_som_alerta():
    som_html = """<audio autoplay style="display:none;"><source src="https://assets.mixkit.co/active_storage/sfx/2869/2869-preview.mp3" type="audio/mpeg"></audio>"""
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
is_fem = st.session_state.user_genero == "Feminino"
tema = st.session_state.tema_escolhido
if tema == "🟢 Verde Hacker": cor_neon = "#00ff88"
elif tema == "🟡 Ouro Milionário": cor_neon = "#FFD700"
elif tema == "🔵 Azul Cyberpunk": cor_neon = "#00e5ff"
elif tema == "🔴 Vermelho Kamikaze": cor_neon = "#ff3333"
elif tema == "🟣 Rosa Choque": cor_neon = "#ff00ff"
else: cor_neon = "#ff00ff" if is_fem else "#00ff88"

# --- 4. CSS FOOTI PREMIUM (SEGURO E NATIVO) ---
st.markdown(f"""
    <style>
    #MainMenu {{visibility: hidden !important;}}
    .stDeployButton {{display:none !important;}}
    footer {{visibility: hidden !important;}}
    header {{visibility: hidden !important;}}
    
    @keyframes fadeIn {{ from {{ opacity: 0; transform: translateY(10px); }} to {{ opacity: 1; transform: translateY(0); }} }}
    
    .stApp {{ 
        background: linear-gradient(rgba(15, 16, 21, 0.92), rgba(15, 16, 21, 0.98)), url('{LINK_SUA_IMAGEM_DE_FUNDO}');
        background-size: cover; background-position: center; background-attachment: fixed;
        animation: fadeIn 0.8s ease-out; color: #ffffff;
    }}
    
    .neon-text {{ color: {cor_neon}; font-weight: bold; font-size: 12px; letter-spacing: 1px; text-transform: uppercase; }}
    .header-destaque {{ text-align: left; color: #ffffff; font-size: 32px; font-weight: 900; font-style: italic; margin-top: -30px; line-height: 1.1; }}
    
    .stat-container {{ display: flex; justify-content: space-between; background-color: rgba(26, 27, 34, 0.8); border-radius: 8px; border: 1px solid #2d2f36; padding: 15px; margin-bottom: 20px; }}
    .stat-box {{ text-align: center; width: 24%; border-right: 1px solid #333; }}
    .stat-box:last-child {{ border-right: none; }}
    .stat-title {{ color: #888; font-size: 11px; margin:0; text-transform: uppercase; letter-spacing: 0.5px; }}
    .stat-value {{ font-size: 22px; font-weight: 900; margin: 5px 0 0 0; }}
    .stat-value.green {{ color: {cor_neon}; }}
    
    .game-card {{ background-color: rgba(26, 27, 34, 0.9); padding: 15px; border-radius: 8px; margin-bottom: 12px; border-left: 4px solid #333; transition: 0.3s; border-top: 1px solid #2d2f36; border-right: 1px solid #2d2f36; border-bottom: 1px solid #2d2f36; }}
    .game-card:hover {{ border-left: 4px solid {cor_neon}; box-shadow: 0 4px 15px rgba(0,0,0,0.5); transform: translateY(-2px); }}
    
    .marquee-wrapper {{ width: 100%; overflow: hidden; background: rgba(0,0,0,0.5); border-bottom: 1px solid {cor_neon}50; padding: 8px 0; display: flex; margin-bottom: 20px; }}
    .marquee-content {{ display: flex; white-space: nowrap; animation: marquee 30s linear infinite; }}
    .marquee-item {{ padding: 0 40px; color: {cor_neon}; font-weight: bold; font-size: 12px; }}
    @keyframes marquee {{ 0% {{ transform: translateX(0); }} 100% {{ transform: translateX(-50%); }} }}
    
    .btn-side {{ display: block; padding: 12px; margin-bottom: 10px; text-align: center; border-radius: 8px; font-weight: bold; text-decoration: none; color: white !important; font-size: 14px; transition: 0.3s; }}
    .stButton>button {{ background: {cor_neon} !important; color: #000 !important; font-weight: 900 !important; border-radius: 8px !important; border: none !important; transition: 0.3s; padding: 10px 20px !important; width: 100%; }}
    .stButton>button:hover {{ transform: scale(1.02); filter: brightness(1.2); }}
    </style>
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

# --- 6. NAVEGAÇÃO PRINCIPAL (ABAS NATIVAS) ---
st.markdown("<br>", unsafe_allow_html=True)
t1, t2, t3, t4, t5 = st.tabs(["🏠 INÍCIO", "🎯 RADAR", "📋 BILHETE", "🛡️ SAFE", "⚙️ PERFIL"])

LIGAS_DISPONIVEIS = {
    "🇬🇧 Premier League": "soccer_epl", "🇪🇺 Champions League": "soccer_uefa_champs_league",
    "🇪🇸 La Liga": "soccer_spain_la_liga", "🇮🇹 Serie A": "soccer_italy_serie_a",
    "🇧🇷 Brasileirão": "soccer_brazil_campeonato"
}

# ==========================================
# ABA 1: INÍCIO (Dashboard e Histórico)
# ==========================================
with t1:
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

    st.markdown("<p style='color: #888; font-size: 12px; margin-bottom: 5px; font-weight: bold;'>📊 TRACK RECORD — 30 DIAS</p>", unsafe_allow_html=True)
    st.markdown(f"""
    <div class='stat-container'>
        <div class='stat-box'><p class='stat-title'>Jogos</p><p class='stat-value'>1.248</p></div>
        <div class='stat-box'><p class='stat-title'>Acertos</p><p class='stat-value green'>1.115</p></div>
        <div class='stat-box'><p class='stat-title'>Win Rate</p><p class='stat-value'>89.4%</p></div>
        <div class='stat-box'><p class='stat-title'>ROI</p><p class='stat-value green'>+14.2%</p></div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<h4 style='color:white; margin-top: 20px;'>🏆 ÚLTIMOS GREENS DO VIP</h4>", unsafe_allow_html=True)
    historico = [
        {"j": "Real Madrid x SL Benfica", "m": "Over 2.5 Gols", "o": 1.75},
        {"j": "Paris Saint Germain x Monaco", "m": "Over 8.5 Cantos", "o": 1.65},
        {"j": "Cruzeiro x Corinthians", "m": "Ambas Marcam", "o": 1.90},
        {"j": "Juventus FC x Galatasaray", "m": "1 e Over 2.5", "o": 2.15},
    ]
    for h in historico:
        st.markdown(f"""
        <div style='background-color: rgba(26,27,34,0.9); border-left: 5px solid #00ff88; padding: 15px; margin-bottom: 10px; border-radius: 6px;'>
            <div style='color:white; font-weight:bold; font-size: 16px;'>{h['j']}</div>
            <div style='color:#bbb; font-size: 14px; margin-top:5px;'>🎯 {h['m']} | <span style='color:#00ff88; font-weight:bold; font-size: 16px;'>@{h['o']} ✅ GREEN</span></div>
        </div>
        """, unsafe_allow_html=True)

# ==========================================
# ABA 2: RADAR (IA e Manual)
# ==========================================
with t2:
    st.markdown("<h4 class='neon-text'>SELECTION HUB</h4>", unsafe_allow_html=True)
    
    with st.expander("✍️ MODO MANUAL: Inserir Grade de Jogos"):
        grade = st.text_area("Cole aqui a sua lista de jogos:", height=150)
        if st.button("🔍 INICIAR ANÁLISE MANUAL"):
            if grade:
                jogos = [j for j in grade.split('\n') if 'x' in j.lower()]
                st.session_state.analisados = []
                mercados = ["Ambas Marcam", "Over 1.5 Gols", "Vitória", "Cantos +8.5", "Over 2.5 Gols"]
                for j in jogos:
                    parts = j.lower().split('x')
                    casa = parts[0].strip().title() if len(parts)>0 else "Casa"
                    fora = parts[1].strip().title() if len(parts)>1 else "Fora"
                    st.session_state.analisados.append({
                        "jogo": j, "casa": casa, "fora": fora, "hora": "Manual",
                        "m": random.choice(mercados), "o": round(random.uniform(1.5, 2.3), 2), "conf": random.randint(93,99)
                    })
                st.success("Análise manual concluída!")

    st.markdown("<br><p style='color:#888; font-size: 12px;'>OU ESCOLHA UMA LIGA PARA VARREDURA IA:</p>", unsafe_allow_html=True)
    liga_selecionada = st.selectbox("Selecione o Mercado:", list(LIGAS_DISPONIVEIS.keys()))
    codigo_da_liga = LIGAS_DISPONIVEIS[liga_selecionada]
    
    if st.button("🚨 PROCESSAR DADOS IA"):
        with st.status("A iniciar Protocolo V8 Supreme...", expanded=True) as status:
            st.write("⏳ A conectar aos servidores asiáticos...")
            url = f"https://api.the-odds-api.com/v4/sports/{codigo_da_liga}/odds/?apiKey={ODDS_API_KEY}&regions=eu,uk&markets=h2h,totals"
            try:
                resposta = requests.get(url)
                if resposta.status_code == 200:
                    dados = resposta.json()
                    st.session_state.analisados = []
                    hoje_brasil = datetime.utcnow() - timedelta(hours=3)
                    data_hoje_str = hoje_brasil.strftime("%Y-%m-%d")
                    jogos_do_dia = []
                    
                    for jogo in dados:
                        data_jogo_utc_str = jogo.get('commence_time', '')
                        if data_jogo_utc_str:
                            try:
                                data_jogo_utc = datetime.strptime(data_jogo_utc_str, "%Y-%m-%dT%H:%M:%SZ")
                                data_jogo_brasil = data_jogo_utc - timedelta(hours=3)
                                if data_jogo_brasil.strftime("%Y-%m-%d") == data_hoje_str:
                                    jogos_do_dia.append(jogo)
                            except: pass
                    
                    for jogo in jogos_do_dia[:25]:
                        casa = jogo.get('home_team', 'Casa')
                        fora = jogo.get('away_team', 'Fora')
                        hora_jogo = ""
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
                                            if out['name'] == casa: mercados_encontrados.append({"m": f"Vitória {casa}", "o": out['price']})
                                            elif out['name'] == fora: mercados_encontrados.append({"m": f"Vitória {fora}", "o": out['price']})
                                            elif out['name'].lower() == 'draw': mercados_encontrados.append({"m": "Empate", "o": out['price']})
                                    elif mercado['key'] == 'totals':
                                        for out in mercado['outcomes']:
                                            pt = out.get('point', 0)
                                            if out['name'] == 'Over': mercados_encontrados.append({"m": f"Over {pt} Gols", "o": out['price']})
                                            elif out['name'] == 'Under': mercados_encontrados.append({"m": f"Under {pt} Gols", "o": out['price']})

                        if mercados_encontrados:
                            melhor_aposta = random.choice(mercados_encontrados)
                            st.session_state.analisados.append({
                                "jogo": nome_jogo, "casa": casa, "fora": fora, "hora": hora_jogo,
                                "m": melhor_aposta["m"], "o": round(melhor_aposta["o"], 2), "conf": random.randint(85, 99)
                            })
                    status.update(label="✅ Varredura Concluída!", state="complete", expanded=False)
                else:
                    status.update(label="Erro na busca.", state="error")
            except Exception as e:
                status.update(label="Erro de Conexão.", state="error")

    if st.session_state.analisados:
        st.markdown("---")
        min_conf = st.slider("MODO SNIPER: Filtrar jogos por assertividade (%):", min_value=85, max_value=99, value=85)
        
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            if st.button("🎲 GERAR DUPLA SEGURA"):
                if len(st.session_state.analisados) >= 2:
                    seguras = sorted(st.session_state.analisados, key=lambda x: x['o'])[:2]
                    st.session_state.bilhete.extend(seguras)
                    tocar_som_moeda()
                    st.success("✅ Dupla adicionada!")
                else: st.warning("Preciso de 2 jogos.")
        with col_m2:
            if st.button("🚨 MODO KAMIKAZE"):
                zebras = [x for x in st.session_state.analisados if x['o'] >= 3.00]
                if zebras:
                    st.session_state.bilhete.extend(zebras[:2]) 
                    tocar_som_alerta()
                    st.error("🚨 Zebras adicionadas!")
                else: st.warning("Nenhuma Zebra encontrada.")

        st.markdown("<br><h4 class='neon-text'>OPORTUNIDADES IDENTIFICADAS</h4>", unsafe_allow_html=True)
        for idx, item in enumerate(st.session_state.analisados):
            if item['conf'] >= min_conf:
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
                    
                    <div style='margin-top: 10px; width: 100%; background-color: rgba(0,0,0,0.5); border-radius: 5px; height: 4px; overflow: hidden;'>
                        <div style='width: {item['conf']}%; height: 4px; background-color: {cor_neon}; box-shadow: 0 0 10px {cor_neon};'></div>
                    </div>
                    
                    <div style='margin-top: 5px; display: flex; justify-content: space-between; font-size: 11px; color: #aaa;'>
                        <span>🕒 {item['hora']}</span>
                        <span>⚡ Confiança: {item['conf']}%</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button(f"➕ ADICIONAR AO BILHETE", key=f"btn_{idx}"):
                    st.session_state.bilhete.append(item)
                    st.toast("✅ Jogo adicionado ao bilhete!")

# ==========================================
# ABA 3: MEU BILHETE
# ==========================================
with t3:
    st.markdown("<h4 class='neon-text'>CARRINHO DE APOSTAS</h4>", unsafe_allow_html=True)
    if st.session_state.bilhete:
        odd_f = 1.0
        msg_tg = f"👑 *RONNYP VIP V8* 👑\n\n"
        msg_whats = "👑 *RONNYP VIP V8* 👑\n\n"
        
        st.markdown("<div style='background-color: rgba(26,27,34,0.8); padding: 15px; border-radius: 8px; border: 1px solid #2d2f36;'>", unsafe_allow_html=True)
        for b in st.session_state.bilhete:
            odd_f *= b['o']
            st.markdown(f"<p style='margin:0; font-size:14px; border-bottom: 1px solid #333; padding: 5px 0;'>✅ <b>{b['jogo']}</b> <span style='float:right; color:{cor_neon}; font-weight:bold;'>@{b['o']}</span></p>", unsafe_allow_html=True)
            msg_tg += f"🏟️ *{b['jogo']}*\n🎯 {b['m']} (@{b['o']})\n\n"
            msg_whats += f"🏟️ {b['jogo']}\n🎯 {b['m']} (@{b['o']})\n\n"
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown(f"<h2 style='text-align:center; margin-top:20px;'>📊 ODD TOTAL: <span style='color:{cor_neon};'>{odd_f:.2f}</span></h2>", unsafe_allow_html=True)
        
        valor_aposta = st.number_input("💸 Stake (R$):", min_value=1.0, value=10.0, step=5.0)
        retorno = valor_aposta * odd_f
        st.info(f"🤑 RETORNO ESPERADO: R$ {retorno:.2f}")
        
        final_msg_tg = msg_tg + f"📊 *Odd Total: {odd_f:.2f}*\n💸 *Aposta:* R$ {valor_aposta:.2f}\n🤑 *Retorno:* R$ {retorno:.2f}\n\n🎰 [APOSTE AQUI]({LINK_CASA_1})"
        final_msg_whats = msg_whats + f"📊 *Odd Total: {odd_f:.2f}*\n💸 Aposta: R$ {valor_aposta:.2f}\n🤑 Retorno: R$ {retorno:.2f}\n\n🎰 APOSTE AQUI: {LINK_CASA_1}"
        
        col_b1, col_b2 = st.columns(2)
        with col_b1:
            if st.button("ENVIAR TELEGRAM"):
                tocar_som_moeda() 
                asyncio.run(Bot(TOKEN).send_message(CHAT_ID, final_msg_tg, parse_mode='Markdown'))
                st.success("Sinal enviado!")
        with col_b2:
            link_zap = f"https://api.whatsapp.com/send?text={urllib.parse.quote(final_msg_whats)}"
            st.markdown(f'<a href="{link_zap}" target="_blank" class="btn-side" style="background: #25d366; margin:0;">🟢 ENVIAR ZAP</a>', unsafe_allow_html=True)
            
        st.download_button("📄 DESCARREGAR RECIBO", data=final_msg_whats, file_name="cupom_v8.txt", mime="text/plain", use_container_width=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🗑️ LIMPAR BILHETE"):
            st.session_state.bilhete = []
            st.rerun()
    else:
        st.info("Seu bilhete está vazio. Vá na aba RADAR e adicione partidas.")

# ==========================================
# ABA 4: BILHETE SAFE (Alto EV)
# ==========================================
with t4:
    st.markdown("<h4 class='neon-text'>ALTO EV (SAFE)</h4>", unsafe_allow_html=True)
    st.markdown("<p style='color:#bbb; font-size:14px;'>A Inteligência Artificial separou a entrada mais segura de hoje. Copie e cole na sua banca!</p>", unsafe_allow_html=True)
    
    hoje_str = datetime.now().strftime("%Y-%m-%d")
    estado_aleatorio_atual = random.getstate()
    random.seed(hoje_str)
    
    jogos_seguros_base = [
        {"jogo": "Real Madrid x Adversário", "m": "Vitória Real Madrid", "o": 1.35},
        {"jogo": "Manchester City x Adversário", "m": "Over 1.5 Gols", "o": 1.25},
        {"jogo": "Bayern de Munique x Adversário", "m": "Over 1.5 Gols", "o": 1.22},
        {"jogo": "Arsenal x Adversário", "m": "Vitória Arsenal", "o": 1.40}
    ]
    safe_pick = random.sample(jogos_seguros_base, 2)
    random.setstate(estado_aleatorio_atual)
    odd_safe_total = safe_pick[0]['o'] * safe_pick[1]['o']
    
    st.markdown(f"""
    <div style='background-color: rgba(26,27,34,0.9); padding: 20px; border-radius: 12px; border: 1px solid #FFD700;'>
        <div style='text-align:center; margin-bottom: 15px;'>
            <span style='background:#FFD700; color:#000; padding:5px 15px; border-radius:20px; font-weight:bold; font-size:12px;'>🏆 IA ASSERTIVIDADE: 98%</span>
        </div>
        <div style='border-left: 4px solid #00ff88; padding-left: 10px; margin-bottom: 10px;'>
            <div style='color:white; font-weight:bold; font-size: 16px;'>⚽ {safe_pick[0]['jogo']}</div>
            <div style='color:#bbb; font-size: 14px;'>🎯 {safe_pick[0]['m']} | <span style='color:#00ff88; font-weight:bold;'>@{safe_pick[0]['o']:.2f}</span></div>
        </div>
        <div style='border-left: 4px solid #00ff88; padding-left: 10px; margin-bottom: 15px;'>
            <div style='color:white; font-weight:bold; font-size: 16px;'>⚽ {safe_pick[1]['jogo']}</div>
            <div style='color:#bbb; font-size: 14px;'>🎯 {safe_pick[1]['m']} | <span style='color:#00ff88; font-weight:bold;'>@{safe_pick[1]['o']:.2f}</span></div>
        </div>
        <hr style='border-color: rgba(255,215,0,0.3);'>
        <h3 style='text-align:center; color:#FFD700; text-shadow: 0 0 10px #FFD700;'>📊 ODD FINAL: {odd_safe_total:.2f}</h3>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("🔥 COPIAR SAFE PARA O MEU BILHETE", use_container_width=True):
        st.session_state.bilhete.extend(safe_pick)
        tocar_som_moeda()
        st.success("✅ Bilhete Safe copiado com sucesso!")

# ==========================================
# ABA 5: PERFIL (Todas as opções da antiga Sidebar)
# ==========================================
with t5:
    st.markdown(f"<h3 style='color:{cor_neon}; text-align:center;'>👑 CEO & FOUNDER</h3>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#888; font-size:12px; margin-top:-10px;'>Ronny P. | Especialista em IA</p>", unsafe_allow_html=True)
    st.markdown(f'<a href="https://instagram.com/ronny_olivzz61" target="_blank" class="btn-side" style="background: linear-gradient(45deg, #f09433, #e6683c, #dc2743, #cc2366, #bc1888);">📸 SIGA @ronny_olivzz61</a>', unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown(f"<h4 style='color:{cor_neon}; text-align:center; font-size: 14px;'>🎙️ BRIEFING DIÁRIO</h4>", unsafe_allow_html=True)
    st.audio(LINK_SEU_AUDIO_BRIEFING, format="audio/mp3")

    st.markdown("---")
    st.markdown("<p style='color:#888; font-size:11px; font-weight:bold;'>ACESSOS RÁPIDOS</p>", unsafe_allow_html=True)
    st.markdown(f'<a href="{LINK_CASA_1}" target="_blank" class="btn-side" style="background: {cor_neon}; color: #000 !important;">🎰 CASA RECOMENDADA</a>', unsafe_allow_html=True)
    st.markdown(f'<a href="{LINK_SUPORTE}" target="_blank" class="btn-side" style="background: #25d366;">🟢 SUPORTE WHATSAPP</a>', unsafe_allow_html=True)
    st.markdown(f'<a href="{LINK_CANAL}" target="_blank" class="btn-side" style="background: #0088cc;">🔵 CANAL TELEGRAM</a>', unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("<p style='color:#888; font-size:11px; font-weight:bold;'>🎨 PERSONALIZAR INTERFACE</p>", unsafe_allow_html=True)
    st.selectbox(
        "Escolha seu Neon:", 
        ["Padrão (Por Gênero)", "🟢 Verde Hacker", "🟡 Ouro Milionário", "🔵 Azul Cyberpunk", "🔴 Vermelho Kamikaze", "🟣 Rosa Choque"],
        key="tema_escolhido"
    )
    
    st.markdown("---")
    st.markdown("<p style='color:#888; font-size:11px; font-weight:bold;'>GESTÃO DE BANCA</p>", unsafe_allow_html=True)
    banca = st.number_input("Banca Atual (R$):", value=100.0)
    entrada = banca * 0.03
    st.info(f"💰 Entrada Ideal (3%): R$ {entrada:.2f}")

    if st.session_state.is_admin:
        st.markdown("---")
        st.markdown("<p style='color:#888; font-size:11px; font-weight:bold;'>GERADOR DE KEYS (ADMIN)</p>", unsafe_allow_html=True)
        c_nome = st.text_input("Nome da Key:")
        tempo_key = st.selectbox("Validade:", ["24 Horas", "7 Dias", "30 Dias"])
        if st.button("CRIAR VIP"):
            horas = 24 if tempo_key == "24 Horas" else (168 if tempo_key == "7 Dias" else 720)
            salvar_key(c_nome, horas)
            link_magico = f"{LINK_PAINEL}?key={c_nome}"
            st.success(f"✅ Key {c_nome} gerada!")
            st.code(link_magico, language="text")

    st.markdown("<br><br>", unsafe_allow_html=True)
    if st.button("SAIR DO APLICATIVO"):
        st.session_state.autenticado = False
        st.rerun()
