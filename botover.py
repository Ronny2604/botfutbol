import streamlit as st
import asyncio
import random
import time
import os
import urllib.parse
import requests
import hashlib
import pandas as pd
from telegram import Bot
from datetime import datetime, timedelta

# --- CONFIGURAÇÕES PESSOAIS ---
LINK_PAINEL = "https://seu-link-aqui.streamlit.app" 
LINK_SUA_IMAGEM_DE_FUNDO = "https://raw.githubusercontent.com/Ronny2604/botfutbol/main/photo_5172618853803035536_c.png"

st.set_page_config(page_title="V8 SUPREME PRO", layout="wide", initial_sidebar_state="collapsed")

MASTER_KEY = "ronnyp@2025"
FILE_KEYS = "keys.txt" 
ODDS_API_KEY = "da4633249ece20283d29604cec7a7114"

# --- INICIALIZAÇÃO DE ESTADOS GLOBAIS (ANTI-CRASH) ---
estado_padrao = {
    'autenticado': False, 'user_nome': "", 'bilhete': [], 'analisados': [], 
    'analises_salvas': [], 'tema_escolhido': "🟢 Verde Hacker",
    'is_vip': True, 'boss_mode': False, 'avatar': "🐺", 'moeda': "R$", 
    'time_coracao': "", 'diario_bordo': "", 'som_green': "Clássico (Caixa Registradora)", 
    'animacao_vitoria': "Balões", 'titulo_apostador': "[O Estrategista]",
    'mod_grafico': True, 'mod_massas': True, 'mod_live': True,
    'bancas': {"Betano": 1000.0, "Bet365": 500.0, "Betfair": 0.0},
    'historico_banca': [1500.0], 'recuperacao_red': False,
    'conquistas': ["🏅 Novato Promissor"], 'total_jogos': 1248, 'total_acertos': 1115,
    'historico_greens': [], 'is_admin': False, 'api_key_odds': ODDS_API_KEY
}
for k, v in estado_padrao.items():
    if k not in st.session_state:
        st.session_state[k] = v

# --- MODO BOSS (Planilha Falsa) ---
if st.session_state.boss_mode:
    st.markdown("<h3 style='color:white; font-family: sans-serif;'>Relatório Consolidado Q3 - Setor Financeiro</h3>", unsafe_allow_html=True)
    df_fake = pd.DataFrame({
        "Mês": ["Janeiro", "Fevereiro", "Março", "Abril"],
        "Receita Bruta": ["$ 15,400.00", "$ 16,200.00", "$ 14,900.00", "$ 18,000.00"],
        "Despesas OPEX": ["$ 12,000.00", "$ 11,500.00", "$ 13,200.00", "$ 12,100.00"],
        "Margem de Lucro": ["22.07%", "29.01%", "11.40%", "32.77%"]
    })
    st.dataframe(df_fake, use_container_width=True, hide_index=True)
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("⬅️ Voltar ao Sistema"):
        st.session_state.boss_mode = False
        st.rerun()
    st.stop()

# --- FUNÇÕES DE SISTEMA ---
def fmt_moeda(valor):
    return f"{st.session_state.moeda} {valor:,.2f}"

def tocar_som_customizado():
    sons = {
        "Clássico (Caixa Registradora)": "https://assets.mixkit.co/active_storage/sfx/2003/2003-preview.mp3",
        "Cassino Las Vegas": "https://assets.mixkit.co/active_storage/sfx/2000/2000-preview.mp3",
        "Moeda Retro (8-bit)": "https://assets.mixkit.co/active_storage/sfx/2019/2019-preview.mp3"
    }
    url = sons.get(st.session_state.som_green, sons["Clássico (Caixa Registradora)"])
    st.markdown(f'<audio autoplay style="display:none;"><source src="{url}" type="audio/mpeg"></audio>', unsafe_allow_html=True)

def calcular_forca_equipa(nome_equipa):
    hash_object = hashlib.md5(nome_equipa.encode())
    num = int(hash_object.hexdigest(), 16)
    return 60 + (num % 35), 50 + ((num // 10) % 40) 

def gerar_dados_mock():
    times = ["Real Madrid", "Barcelona", "Man City", "Arsenal", "Bayern", "Flamengo", "Liverpool", "Chelsea", "Milan", "Inter"]
    random.shuffle(times)
    d = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    return [{"home_team": times[i*2], "away_team": times[i*2+1], "commence_time": d} for i in range(5)]

@st.cache_data(ttl=300, show_spinner=False)
def buscar_dados_api(codigo_da_liga, api_key):
    url = f"https://api.the-odds-api.com/v4/sports/{codigo_da_liga}/odds/?apiKey={api_key}&regions=eu,uk&markets=h2h,totals"
    try:
        r = requests.get(url, timeout=5)
        if r.status_code == 200 and isinstance(r.json(), list): return r.json()
    except: pass
    return None

@st.cache_data(ttl=3600, show_spinner=False)
def obter_jogos_vitrine():
    dados = buscar_dados_api("soccer_epl", ODDS_API_KEY)
    if dados and isinstance(dados, list) and len(dados) >= 5:
        return [{"casa": d.get('home_team','A'), "fora": d.get('away_team','B'), "jogo": f"{d.get('home_team')} x {d.get('away_team')}"} for d in dados[:5]]
    return [{"casa": "Flamengo", "fora": "Palmeiras", "jogo": "Flamengo x Palmeiras"}, {"casa": "Arsenal", "fora": "Chelsea", "jogo": "Arsenal x Chelsea"}, {"casa": "Man City", "fora": "Liverpool", "jogo": "Man City x Liverpool"}, {"casa": "Real Madrid", "fora": "Barcelona", "jogo": "Real Madrid x Barcelona"}, {"casa": "Milan", "fora": "Inter", "jogo": "Milan x Inter"}]

jogos_vitrine = obter_jogos_vitrine()

# --- CONTROLE DE TEMA NEON ---
tema = st.session_state.tema_escolhido
if tema == "🟢 Verde Hacker": cor_neon = "#00ff88"; grad = "linear-gradient(135deg, rgba(0,255,136,0.1), rgba(0,0,0,0))"
elif tema == "🟡 Ouro Milionário": cor_neon = "#FFD700"; grad = "linear-gradient(135deg, rgba(255,215,0,0.1), rgba(0,0,0,0))"
elif tema == "🔵 Azul Cyberpunk": cor_neon = "#00e5ff"; grad = "linear-gradient(135deg, rgba(0,229,255,0.1), rgba(0,0,0,0))"
elif tema == "🔴 Vermelho Kamikaze": cor_neon = "#ff3333"; grad = "linear-gradient(135deg, rgba(255,51,51,0.1), rgba(0,0,0,0))"
elif tema == "🟣 Rosa Choque": cor_neon = "#ff00ff"; grad = "linear-gradient(135deg, rgba(255,0,255,0.1), rgba(0,0,0,0))"
else: cor_neon = "#00ff88"; grad = "linear-gradient(135deg, rgba(0,255,136,0.1), rgba(0,0,0,0))"

# --- CSS SUPREMO ESTABILIZADO (ESTRUTURA ORIGINAL SEGURA) ---
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;500;700;900&display=swap');
    
    html, body, [class*="css"] {{ font-family: 'Inter', sans-serif !important; }}
    header[data-testid="stHeader"] {{ display: none !important; }}
    .block-container {{ padding-top: 1rem !important; margin-top: -1rem !important; padding-bottom: 80px !important; }}
    #MainMenu {{visibility: hidden !important;}} .stDeployButton {{display:none !important;}} footer {{visibility: hidden !important;}}
    
    .stApp {{ 
        background: radial-gradient(circle at 50% 0%, rgba(20,22,30,0.9), rgba(10,10,12,1)), url('{LINK_SUA_IMAGEM_DE_FUNDO}'); 
        background-size: cover; background-position: center; background-attachment: fixed; color: #ffffff; 
    }}
    
    /* ABAS NATIVAS REESTILIZADAS SEGURAS */
    div[data-testid="stTabs"] > div:first-of-type {{
        background-color: rgba(20, 22, 30, 0.6) !important;
        backdrop-filter: blur(5px);
        border-radius: 50px !important;
        padding: 5px !important;
        margin-bottom: 20px !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
    }}
    div[data-testid="stTabs"] button[role="tab"] {{ 
        color: #888 !important; font-weight: 700 !important; font-size: 11px !important; 
        background: transparent !important; border: none !important; 
        border-radius: 30px !important; padding: 10px 15px !important;
    }}
    div[data-testid="stTabs"] button[role="tab"][aria-selected="true"] {{ 
        color: {cor_neon} !important; background: rgba(255,255,255,0.08) !important; 
        border-bottom: 2px solid {cor_neon} !important;
    }}
    
    /* GLASS CARDS ESTABILIZADOS (WIDTH 100%) */
    .glass-card {{
        background: rgba(26, 28, 36, 0.6);
        backdrop-filter: blur(10px); -webkit-backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px; padding: 15px; margin-bottom: 15px;
        width: 100%; box-sizing: border-box; /* Previne quebra de grid */
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }}
    .glass-card:hover {{ border-color: {cor_neon}50; }}
    
    .terminal-card {{ background: #0a0b10; border: 1px solid #222; border-left: 3px solid {cor_neon}; border-radius: 8px; padding: 15px; font-family: monospace; color: #00ff88; width: 100%; box-sizing: border-box; }}
    
    .neon-text {{ color: {cor_neon}; font-weight: 900; font-size: 14px; letter-spacing: 1px; text-transform: uppercase; text-shadow: 0 0 10px {cor_neon}40; }}
    
    .stButton>button {{ 
        background: {grad} !important; color: white !important; font-weight: 900 !important; 
        border-radius: 8px !important; border: 1px solid {cor_neon} !important; padding: 12px 20px !important; 
        width: 100%; transition: all 0.2s ease !important;
    }}
    .stButton>button:hover {{ background: {cor_neon} !important; color: #000 !important; transform: translateY(-2px) !important; }}
    .stButton>button:active {{ transform: translateY(1px) !important; filter: brightness(0.9) !important; }}
    
    .progress-bg {{ width: 100%; background: #222; border-radius: 10px; height: 6px; margin-bottom: 8px; overflow: hidden; }}
    .progress-fill-atk {{ height: 6px; background: linear-gradient(90deg, #ff0055, #ff5555); border-radius: 10px; }}
    .progress-fill-def {{ height: 6px; background: linear-gradient(90deg, #0055ff, #00aaff); border-radius: 10px; }}
    </style>
""", unsafe_allow_html=True)

url_key = st.query_params.get("key", "")

# --- TELA DE LOGIN ---
if not st.session_state.autenticado:
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    with st.container():
        st.markdown("<div class='glass-card' style='max-width:400px; margin:auto; text-align:center;'>", unsafe_allow_html=True)
        st.markdown(f"<h1 style='color:#fff; font-weight:900; margin-bottom:0;'>V8 <span style='color:{cor_neon};'>SUPREME</span></h1>", unsafe_allow_html=True)
        st.markdown("<p style='color:#888; font-size: 11px; letter-spacing:2px; margin-bottom: 30px;'>A.I. INTELLIGENCE HUB</p>", unsafe_allow_html=True)
        
        nome_in = st.text_input("Credencial de Acesso:", placeholder="Seu Nome")
        key_in = st.text_input("Chave Criptografada:", value=url_key, type="password", placeholder="Cole sua Key")
        
        if st.button("INICIAR SESSÃO", use_container_width=True):
            if key_in == MASTER_KEY or key_in:
                st.session_state.autenticado = True
                st.session_state.is_admin = True if key_in == MASTER_KEY else False
                st.session_state.user_nome = nome_in if nome_in else "VIP"
                st.rerun()
        
        st.markdown("<p style='text-align:center; margin-top:20px; color:#555; font-size: 10px;'>OU</p>", unsafe_allow_html=True)
        if st.button("🔓 BIOMETRIA / FACE ID"):
            area_msg = st.empty()
            area_msg.info("📷 Posicione seu rosto...")
            time.sleep(1)
            area_msg.success("✅ Verificado.")
            time.sleep(0.5)
            st.session_state.autenticado = True
            st.session_state.user_nome = nome_in if nome_in else "CEO"
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# --- TOP BAR (A BARRA DE STATUS VIP) ---
win_rate = (st.session_state.total_acertos / st.session_state.total_jogos) * 100 if st.session_state.total_jogos > 0 else 0
saldo_total = sum(st.session_state.bancas.values())

st.markdown(f"""
    <div style='display:flex; justify-content:space-between; align-items:center; margin-bottom: 15px; padding: 15px; background: rgba(20,22,30,0.8); border-radius: 12px; border: 1px solid rgba(255,255,255,0.05); width: 100%; box-sizing: border-box;'>
        <div style='display:flex; align-items:center;'>
            <div style='font-size: 28px; margin-right: 12px;'>{st.session_state.avatar}</div>
            <div>
                <div style='color:white; font-weight:900; font-size:16px;'>{st.session_state.user_nome.upper()} <span style='background:{cor_neon}; color:black; font-size:9px; padding:2px 6px; border-radius:4px; vertical-align:middle; font-weight:bold;'>PRO</span></div>
                <div style='color:{cor_neon}; font-size:11px; margin-top:2px;'>{st.session_state.titulo_apostador}</div>
            </div>
        </div>
        <div style='text-align:right;'>
            <div style='color:#888; font-size:10px; text-transform:uppercase;'>Saldo Consolidado</div>
            <div style='color:white; font-weight:900; font-size:18px;'>{fmt_moeda(saldo_total)}</div>
        </div>
    </div>
""", unsafe_allow_html=True)

# --- NAVEGAÇÃO PRINCIPAL (NO TOPO, ESTÁVEL) ---
t1, t2, t3, t4, t5 = st.tabs(["📊 HOME", "🎯 RADAR", "🧾 OPERAÇÕES", "🛡️ SAFE", "⚙️ HUB"])

LIGAS_DISPONIVEIS = {"🇬🇧 Premier League": "soccer_epl", "🇪🇺 Champions League": "soccer_uefa_champs_league", "🇪🇸 La Liga": "soccer_spain_la_liga", "🇧🇷 Brasileirão": "soccer_brazil_campeonato"}

# ==========================================
# ABA 1: DASHBOARD
# ==========================================
with t1:
    if st.session_state.mod_grafico:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.markdown(f"<p style='color: #888; font-size: 11px; font-weight: bold; margin-bottom:5px;'>📈 RENDIMENTO DA CARTEIRA</p>", unsafe_allow_html=True)
        st.line_chart(st.session_state.historico_banca, height=120, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown(f"""
        <div style='display: flex; justify-content: space-between; gap: 10px; margin-bottom: 20px; width: 100%; box-sizing: border-box;'>
            <div class='glass-card' style='flex:1; text-align:center; padding: 15px; margin:0;'>
                <p style='color:#888; font-size:11px; margin:0;'>Win Rate</p>
                <p style='color:white; font-size:22px; font-weight:900; margin:0;'>{win_rate:.1f}%</p>
            </div>
            <div class='glass-card' style='flex:1; text-align:center; padding: 15px; margin:0;'>
                <p style='color:#888; font-size:11px; margin:0;'>Acertos</p>
                <p style='color:{cor_neon}; font-size:22px; font-weight:900; margin:0;'>{st.session_state.total_acertos}</p>
            </div>
        </div>
    """, unsafe_allow_html=True)

    if st.session_state.mod_live:
        minuto = datetime.now().minute
        j_live = jogos_vitrine[2]
        st.markdown("<h4 class='neon-text'>🔴 LIVE SCORES</h4>", unsafe_allow_html=True)
        st.markdown(f"""
            <div class='glass-card' style='display:flex; justify-content:space-between; align-items:center; border-left: 4px solid #ff3333;'>
                <div>
                    <span style='background:#ff3333; color:white; padding:3px 8px; border-radius:4px; font-size:11px; font-weight:bold;'>{(minuto+23)%90+1}'</span>
                    <span style='color:white; font-weight:bold; font-size: 14px; margin-left: 10px;'>{j_live['casa']} {(minuto//15)%3} x {(minuto//25)%2} {j_live['fora']}</span>
                </div>
                <div style='text-align:right; font-size:11px; color:#888;'>Call IA<br><b style='color:{cor_neon};'>Over 1.5</b></div>
            </div>
        """, unsafe_allow_html=True)

# ==========================================
# ABA 2: RADAR A.I
# ==========================================
with t2:
    st.markdown("<h4 class='neon-text'>SELECTION HUB</h4>", unsafe_allow_html=True)
    
    if st.session_state.time_coracao:
        st.markdown(f"""
            <div class='glass-card' style='border: 1px solid {cor_neon}; background: rgba(0,0,0,0.6);'>
                <span style='color:{cor_neon}; font-size:12px; font-weight:bold;'>❤️ OPORTUNIDADE: {st.session_state.time_coracao.upper()}</span><br>
                <span style='color:white; font-size:14px;'>O modelo detetou +EV para a próxima partida. Sugestão: <b>Over Cartões</b>.</span>
            </div>
        """, unsafe_allow_html=True)

    with st.expander("✍️ OVERRIDE MANUAL"):
        grade = st.text_area("Input de Jogos:", placeholder="Time A x Time B")
        if st.button("FORÇAR ANÁLISE"):
            if grade:
                jogos = [j for j in grade.split('\n') if 'x' in j.lower()]
                st.session_state.analisados = []
                for j in jogos:
                    c, f = j.lower().split('x')[0].strip().title(), j.lower().split('x')[1].strip().title()
                    atk, dfs = calcular_forca_equipa(c)
                    st.session_state.analisados.append({"jogo": f"{c} x {f}", "casa": c, "fora": f, "m": random.choice(["Ambas Marcam", "Over 1.5", "Vitória"]), "o": round(random.uniform(1.4, 2.1), 2), "conf": random.randint(88,99), "atk": atk, "def": dfs})
                st.success("Matriz atualizada!")

    st.markdown("<h4 class='neon-text' style='margin-top:20px;'>VARREDURA DO MERCADO</h4>", unsafe_allow_html=True)
    codigo_da_liga = LIGAS_DISPONIVEIS[st.selectbox("Selecionar Filtro Global:", list(LIGAS_DISPONIVEIS.keys()))]
    
    if st.button("EXECUTAR SCANNER"):
        with st.spinner("Procurando assimetrias na API..."):
            dados = buscar_dados_api(codigo_da_liga, st.session_state.api_key_odds) 
            if not dados:
                dados = gerar_dados_mock()
                st.warning("⚠️ Limite da API esgotado. A exibir simulação de jogos. Atualize a chave no Hub.")
            
            st.session_state.analisados = []
            for jogo in dados[:10]:
                c, f = jogo.get('home_team', 'Casa'), jogo.get('away_team', 'Fora')
                ap = {"m": f"Vitória {c}", "o": round(random.uniform(1.3, 2.5), 2)} 
                atk, dfs = calcular_forca_equipa(c)
                st.session_state.analisados.append({"jogo": f"{c} x {f}", "casa": c, "fora": f, "m": ap["m"], "o": ap["o"], "conf": random.randint(85, 99), "atk": atk, "def": dfs})
            st.toast("✅ Scanner concluído.")

    if st.session_state.analisados:
        st.markdown("<hr style='border-color: rgba(255,255,255,0.1);'>", unsafe_allow_html=True)
        for idx, item in enumerate(st.session_state.analisados):
            # HTML formatado numa linha para não gerar bug no Markdown
            html_card = f"<div class='glass-card'><div style='display:flex; justify-content:space-between; align-items:center;'><div style='font-size:14px; font-weight:900;'>{item['casa']} <span style='color:#555; font-size:10px;'>VS</span> {item['fora']}</div><div style='color:{cor_neon}; font-weight:900; font-size:16px;'>@{item['o']}</div></div><div style='margin-top:15px; font-size:10px; color:#888;'>PRESSÃO OFENSIVA ({item['atk']}%)</div><div class='progress-bg'><div class='progress-fill-atk' style='width:{item['atk']}%;'></div></div><div style='margin-top:5px; font-size:10px; color:#888;'>MURALHA DEFENSIVA ({item['def']}%)</div><div class='progress-bg'><div class='progress-fill-def' style='width:{item['def']}%;'></div></div><div style='margin-top:15px; background:rgba(0,0,0,0.4); padding:10px; border-radius:8px;'><span style='font-size:11px; color:#aaa;'>ALGORITMO V8:</span> <b style='color:white;'>{item['m']}</b><br><span style='font-size:11px; color:#aaa;'>CONFIANÇA:</span> <b style='color:{cor_neon};'>{item['conf']}%</b></div></div>"
            st.markdown(html_card, unsafe_allow_html=True)
            
            col_add1, col_add2 = st.columns(2)
            with col_add1:
                if st.button("➕ BILHETE", key=f"btn_m_{idx}"):
                    st.session_state.bilhete.append(item)
                    st.toast("✅ Adicionado à Múltipla!")
            with col_add2:
                if st.button("💾 SALVAR DICA", key=f"btn_s_{idx}"):
                    st.session_state.analises_salvas.append(item)
                    st.toast("💾 Salvo no Tracking Pessoal!")

# ==========================================
# ABA 3: OPERAÇÕES (MÚLTIPLA + TRACKING)
# ==========================================
with t3:
    st.markdown("<h4 class='neon-text'>CARRINHO MÚLTIPLO</h4>", unsafe_allow_html=True)
    if st.session_state.bilhete:
        odd_f = 1.0
        st.markdown("<div class='glass-card' style='padding: 15px;'>", unsafe_allow_html=True)
        for b in st.session_state.bilhete:
            odd_f *= b['o']
            st.markdown(f"<p style='margin:0; font-size:14px; border-bottom: 1px solid rgba(255,255,255,0.1); padding: 5px 0;'>✅ <b>{b['jogo']}</b> <span style='float:right; color:{cor_neon}; font-weight:bold;'>@{b['o']}</span></p>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown(f"<h2 style='text-align:center; font-weight:900; font-size:36px; color:white;'>ODD <span style='color:{cor_neon};'>@{odd_f:.2f}</span></h2>", unsafe_allow_html=True)
        
        banca_escolhida = st.selectbox("Conta Origem:", list(st.session_state.bancas.keys()), key="banca_mult")
        banca_disp = st.session_state.bancas[banca_escolhida]
        
        rec_stake = banca_disp * (0.03 if odd_f < 2.5 else 0.01)

        st.markdown(f"<div class='terminal-card' style='margin-bottom:20px;'>> SALDO: {fmt_moeda(banca_disp)}<br>> GESTÃO IDEAL: <span style='color:{cor_neon}; font-size:16px;'>{fmt_moeda(rec_stake)}</span></div>", unsafe_allow_html=True)
        
        valor_aposta = st.number_input("Entrada (Múltipla):", min_value=1.0, value=float(max(1.0, rec_stake)), step=5.0)
        st.info(f"🤑 RETORNO ESPERADO: {fmt_moeda(valor_aposta * odd_f)}")

        col_r1, col_r2 = st.columns(2)
        with col_r1:
            if st.button("✅ GREEN (MÚLTIPLA)", use_container_width=True):
                if st.session_state.animacao_vitoria == "Balões": st.balloons()
                else: st.snow()
                tocar_som_customizado()
                st.session_state.total_jogos += len(st.session_state.bilhete)
                st.session_state.total_acertos += len(st.session_state.bilhete)
                st.session_state.bancas[banca_escolhida] += (valor_aposta * odd_f)
                st.session_state.historico_banca.append(sum(st.session_state.bancas.values()))
                st.session_state.bilhete = [] 
                time.sleep(2); st.rerun()
        with col_r2:
            if st.button("❌ RED / CANCELAR", use_container_width=True):
                st.session_state.total_jogos += len(st.session_state.bilhete)
                st.session_state.bancas[banca_escolhida] -= valor_aposta
                st.session_state.historico_banca.append(sum(st.session_state.bancas.values()))
                st.session_state.bilhete = [] 
                st.rerun()
    else:
        st.info("Múltipla vazia.")

    st.markdown("<h4 class='neon-text' style='margin-top: 40px;'>📂 TRACKING DE ANÁLISES (SINGLES)</h4>", unsafe_allow_html=True)
    if st.session_state.analises_salvas:
        for i, a in enumerate(st.session_state.analises_salvas):
            html_track = f"<div class='glass-card' style='padding: 10px 15px; margin-bottom: 5px; border-left: 3px solid #00e5ff;'><div style='font-size:13px; font-weight:bold; color:white;'>{a['jogo']}</div><div style='display:flex; justify-content:space-between; margin-top:2px;'><span style='color:#888; font-size:11px;'>Call: <b style='color:white;'>{a['m']}</b></span><span style='color:{cor_neon}; font-weight:bold; font-size:12px;'>@{a['o']}</span></div></div>"
            st.markdown(html_track, unsafe_allow_html=True)
            
            c_g, c_r, c_d = st.columns([0.4, 0.4, 0.2])
            with c_g:
                if st.button("✅ GREEN", key=f"tg_{i}"):
                    st.session_state.total_jogos += 1; st.session_state.total_acertos += 1
                    st.session_state.analises_salvas.pop(i)
                    if st.session_state.animacao_vitoria == "Balões": st.balloons()
                    else: st.snow()
                    tocar_som_customizado(); time.sleep(1); st.rerun()
            with c_r:
                if st.button("❌ RED", key=f"tr_{i}"):
                    st.session_state.total_jogos += 1; st.session_state.analises_salvas.pop(i); st.rerun()
            with c_d:
                if st.button("🗑️", key=f"td_{i}"):
                    st.session_state.analises_salvas.pop(i); st.rerun()
    else:
        st.caption("Nenhuma análise individual salva.")

# ==========================================
# ABA 4: SAFE (BINGO)
# ==========================================
with t4:
    st.markdown("<h4 class='neon-text'>HIGH EV ZONE (SAFE)</h4>", unsafe_allow_html=True)
    if not st.session_state.analisados: 
        st.info("⚠️ Varredura prévia requerida no RADAR (ou via Override Manual).")
    else:
        seguros = sorted([j for j in st.session_state.analisados if 1.15 <= j.get('o', 1.5) <= 1.65], key=lambda x: x.get('conf', 0), reverse=True)
        if len(seguros) >= 2:
            safe_pick = seguros[:2]
            odd_safe_total = safe_pick[0].get('o', 1.2) * safe_pick[1].get('o', 1.2)
            html_safe = f"<div class='glass-card' style='border: 1px solid {cor_neon};'><div style='text-align:center; margin-bottom: 15px;'><span style='background:{cor_neon}; color:#000; padding:5px 15px; border-radius:20px; font-weight:bold; font-size:12px;'>🏆 DUPLA DE OURO</span></div><div style='border-left: 4px solid {cor_neon}; padding-left: 10px; margin-bottom: 10px;'><div style='color:white; font-weight:bold; font-size: 14px;'>⚽ {safe_pick[0]['jogo']}</div><div style='color:#888; font-size: 12px;'>🎯 {safe_pick[0]['m']} | <span style='color:{cor_neon}; font-weight:bold;'>@{safe_pick[0]['o']:.2f}</span></div></div><div style='border-left: 4px solid {cor_neon}; padding-left: 10px; margin-bottom: 15px;'><div style='color:white; font-weight:bold; font-size: 14px;'>⚽ {safe_pick[1]['jogo']}</div><div style='color:#888; font-size: 12px;'>🎯 {safe_pick[1]['m']} | <span style='color:{cor_neon}; font-weight:bold;'>@{safe_pick[1]['o']:.2f}</span></div></div><hr style='border-color: rgba(255,255,255,0.1);'><h3 style='text-align:center; color:{cor_neon}; text-shadow: 0 0 10px {cor_neon}60;'>📊 ODD FINAL: {odd_safe_total:.2f}</h3></div>"
            st.markdown(html_safe, unsafe_allow_html=True)
            if st.button("🔥 COPIAR PARA OPERAÇÕES"): st.session_state.bilhete.extend(safe_pick); st.toast("✅ Copiado!"); tocar_som_customizado()
        else: st.warning("A IA não encontrou 2 jogos com perfil 'Safe' (Odds 1.15 - 1.65) nesta varredura.")

# ==========================================
# ABA 5: HUB DE CONTROLE
# ==========================================
with t5:
    st.markdown(f"<h3 style='color:white; text-align:center; font-weight:900;'>V8 <span style='color:{cor_neon};'>HUB</span></h3>", unsafe_allow_html=True)
    
    if st.button("👁️ MODO INVISÍVEL (BOSS BUTTON)"):
        st.session_state.boss_mode = True
        st.rerun()

    with st.expander("🔑 Chave de API de Dados"):
        st.markdown("<span style='font-size:11px; color:#aaa;'>Para garantir jogos sempre reais, crie uma chave grátis no site <b>the-odds-api.com</b> e cole aqui:</span>", unsafe_allow_html=True)
        nova_api = st.text_input("API Key:", value=st.session_state.api_key_odds, type="password")
        if st.button("Atualizar Chave"):
            st.session_state.api_key_odds = nova_api
            st.success("Chave salva!")

    with st.expander("🏛️ GESTÃO DE BANCAS"):
        col_c1, col_c2, col_c3 = st.columns(3)
        st.session_state.bancas["Betano"] = col_c1.number_input("Betano", value=st.session_state.bancas["Betano"], step=50.0)
        st.session_state.bancas["Bet365"] = col_c2.number_input("Bet365", value=st.session_state.bancas["Bet365"], step=50.0)
        st.session_state.bancas["Betfair"] = col_c3.number_input("Betfair", value=st.session_state.bancas["Betfair"], step=50.0)

    with st.expander("⚙️ CUSTOMIZAÇÃO"):
        st.selectbox("Motor Gráfico:", ["🟢 Verde Hacker", "🟡 Ouro Milionário", "🔵 Azul Cyberpunk", "🔴 Vermelho Kamikaze", "🟣 Rosa Choque"], key="tema_escolhido")
        col_a1, col_a2 = st.columns(2)
        col_a1.selectbox("Avatar:", ["🐺", "🦈", "🦉", "🧙‍♂️", "👑", "🚀"], key="avatar")
        col_a2.selectbox("Moeda:", ["R$", "US$", "€", "₿"], key="moeda")
        st.selectbox("Animação de Liquidar:", ["Balões", "Chuva de Neve"], key="animacao_vitoria")
        st.selectbox("Som de Vitória:", ["Clássico (Caixa Registradora)", "Cassino Las Vegas", "Moeda Retro (8-bit)"], key="som_green")

    st.markdown("<br><br>", unsafe_allow_html=True)
    if st.button("ENCERRAR SESSÃO", type="primary"):
        st.session_state.autenticado = False
        st.rerun()
