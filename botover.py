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
LINKS_AFILIADOS = ["https://esportiva.bet.br?ref=511e1f11699f", "https://br.betano.com/ref=ronny", "https://bet365.com/ref=ronny"]

st.set_page_config(page_title="V8 SUPREME PRO", layout="wide", initial_sidebar_state="collapsed")

MASTER_KEY = "ronnyp@2025"
FILE_KEYS = "keys.txt" 
TOKEN = '8543393879:AAEsaXAAq2A19zbmMEfHZb-R7nLL-VdierU'
CHAT_ID = '-1003799258159'
ODDS_API_KEY = "da4633249ece20283d29604cec7a7114"

# --- INICIALIZAÇÃO DE ESTADOS ---
if 'autenticado' not in st.session_state: st.session_state.autenticado = False
if 'user_nome' not in st.session_state: st.session_state.user_nome = ""
if 'bilhete' not in st.session_state: st.session_state.bilhete = []
if 'analisados' not in st.session_state: st.session_state.analisados = []
if 'analises_salvas' not in st.session_state: st.session_state.analises_salvas = []
if 'tema_escolhido' not in st.session_state: st.session_state.tema_escolhido = "🟢 Verde Hacker"
if 'is_vip' not in st.session_state: st.session_state.is_vip = True 
if 'boss_mode' not in st.session_state: st.session_state.boss_mode = False
if 'links_afiliados' not in st.session_state: st.session_state.links_afiliados = LINKS_AFILIADOS
if 'link_afiliado_ativo' not in st.session_state: st.session_state.link_afiliado_ativo = random.choice(LINKS_AFILIADOS)
if 'avatar' not in st.session_state: st.session_state.avatar = "🐺"
if 'moeda' not in st.session_state: st.session_state.moeda = "R$"
if 'time_coracao' not in st.session_state: st.session_state.time_coracao = ""
if 'diario_bordo' not in st.session_state: st.session_state.diario_bordo = ""
if 'som_green' not in st.session_state: st.session_state.som_green = "Clássico (Caixa Registradora)"
if 'animacao_vitoria' not in st.session_state: st.session_state.animacao_vitoria = "Balões"
if 'titulo_apostador' not in st.session_state: st.session_state.titulo_apostador = "[O Estrategista]"
if 'mod_grafico' not in st.session_state: st.session_state.mod_grafico = True
if 'mod_massas' not in st.session_state: st.session_state.mod_massas = True
if 'mod_live' not in st.session_state: st.session_state.mod_live = True
if 'juros_compostos' not in st.session_state: st.session_state.juros_compostos = False 
if 'usar_kelly' not in st.session_state: st.session_state.usar_kelly = False # FEATURE 2: Kelly Criterion
if 'bancas' not in st.session_state: st.session_state.bancas = {"Betano": 1000.0, "Bet365": 500.0, "Betfair": 0.0}
if 'historico_banca' not in st.session_state: st.session_state.historico_banca = [1500.0]
if 'banca_inicial_dia' not in st.session_state: st.session_state.banca_inicial_dia = 1500.0 # FEATURE 3: Stop Loss
if 'recuperacao_red' not in st.session_state: st.session_state.recuperacao_red = False
if 'conquistas' not in st.session_state: st.session_state.conquistas = ["🏅 Novato Promissor"]
if 'total_jogos' not in st.session_state: st.session_state.total_jogos = 1248
if 'total_acertos' not in st.session_state: st.session_state.total_acertos = 1115
if 'historico_greens' not in st.session_state: st.session_state.historico_greens = [{"Data": datetime.now().strftime("%Y-%m-%d"), "Jogo": "Real Madrid x Benfica", "Mercado": "Over 2.5", "Odd": 1.75}]

if st.session_state.boss_mode:
    st.markdown("""<style>.stApp { background: #ffffff !important; color: #000 !important; font-family: Calibri, sans-serif !important;} header { display: none !important; } .excel-table { width: 100%; border-collapse: collapse; font-size: 14px; } .excel-table th { background: #f3f3f3; border: 1px solid #d0d0d0; padding: 5px; text-align: center; color: #333; font-weight: normal; } .excel-table td { border: 1px solid #d0d0d0; padding: 5px; color: #000; } .excel-header { background: #217346 !important; color: white !important; padding: 10px; font-weight: bold; font-size: 18px; margin-bottom: 20px;} </style><div class="excel-header">📊 Livro1 - Excel</div><table class="excel-table"><tr><th>A</th><th>B</th><th>C</th><th>D</th></tr><tr><td>1</td><td><b>Mês</b></td><td><b>Receita Bruta</b></td><td><b>Despesas OPEX</b></td></tr><tr><td>2</td><td>Janeiro</td><td>$ 15,400.00</td><td>$ 12,000.00</td></tr><tr><td>3</td><td>Fevereiro</td><td>$ 16,200.00</td><td>$ 11,500.00</td></tr><tr><td>4</td><td>Março</td><td>$ 14,900.00</td><td>$ 13,200.00</td></tr></table>""", unsafe_allow_html=True)
    if st.button("Sair (Esc)", key="btn_boss_out"): st.session_state.boss_mode = False; st.rerun()
    st.stop()

def fmt_moeda(valor): return f"{st.session_state.moeda} {valor:,.2f}"

def tocar_som_customizado():
    sons = {"Clássico (Caixa Registradora)": "https://assets.mixkit.co/active_storage/sfx/2003/2003-preview.mp3", "Cassino Las Vegas": "https://assets.mixkit.co/active_storage/sfx/2000/2000-preview.mp3", "Moeda Retro (8-bit)": "https://assets.mixkit.co/active_storage/sfx/2019/2019-preview.mp3"}
    st.markdown(f'<audio autoplay style="display:none;"><source src="{sons.get(st.session_state.som_green, sons["Clássico (Caixa Registradora)"])}" type="audio/mpeg"></audio>', unsafe_allow_html=True)

def calcular_forca_equipa(nome_equipa):
    hash_object = hashlib.md5(nome_equipa.encode())
    num = int(hash_object.hexdigest(), 16)
    return 60 + (num % 35), 50 + ((num // 10) % 40) 

@st.cache_data(ttl=600, show_spinner=False)
def buscar_dados_api(codigo_da_liga):
    url = f"https://api.the-odds-api.com/v4/sports/{codigo_da_liga}/odds/?apiKey={ODDS_API_KEY}&regions=eu,uk&markets=h2h,totals"
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200: return r.json()
    except: pass
    return None

@st.cache_data(ttl=3600, show_spinner=False)
def obter_jogos_vitrine():
    for liga in ["soccer_epl", "soccer_uefa_champs_league", "soccer_brazil_campeonato", "soccer_spain_la_liga"]:
        dados = buscar_dados_api(liga)
        if dados and len(dados) >= 5: return [{"casa": d.get('home_team','A'), "fora": d.get('away_team','B'), "jogo": f"{d.get('home_team')} x {d.get('away_team')}"} for d in dados[:5]]
    return [{"casa": "Flamengo", "fora": "Palmeiras", "jogo": "Flamengo x Palmeiras"}, {"casa": "Arsenal", "fora": "Chelsea", "jogo": "Arsenal x Chelsea"}, {"casa": "Man City", "fora": "Liverpool", "jogo": "Man City x Liverpool"}, {"casa": "Real Madrid", "fora": "Barcelona", "jogo": "Real Madrid x Barcelona"}, {"casa": "Milan", "fora": "Inter", "jogo": "Milan x Inter"}]

jogos_vitrine = obter_jogos_vitrine()

def valida_chave(chave):
    if chave == MASTER_KEY: return True, True
    if not os.path.exists(FILE_KEYS): return False, False
    with open(FILE_KEYS, "r") as f:
        for line in f:
            if "," in line:
                try:
                    k, exp = line.strip().split(",")
                    if chave == k and datetime.now() < datetime.strptime(exp, "%Y-%m-%d %H:%M:%S"): return True, False
                except: continue
    return False, False

# --- MOTOR DE TEMAS ---
tema = st.session_state.tema_escolhido
is_light = (tema == "⚪ Modo Claro (Light)")

if is_light:
    cor_neon = "#0055ff"; grad = "linear-gradient(135deg, rgba(0,85,255,0.1), rgba(0,0,0,0))"
    c_prim = "#111111"; c_sec = "#555555"; c_inv = "#ffffff"
    card_bg = "rgba(255, 255, 255, 0.85)"; card_border = "rgba(0, 0, 0, 0.1)"
    tab_bg = "rgba(255, 255, 255, 0.9)"; tab_active_bg = "rgba(0, 85, 255, 0.1)"
    terminal_bg = "#f0f2f6"; progress_bg = "#d0d0d0"; c_bg_badge = "rgba(0, 85, 255, 0.1)"
else:
    if tema == "🟢 Verde Hacker": cor_neon = "#00ff88"; grad = "linear-gradient(135deg, rgba(0,255,136,0.1), rgba(0,0,0,0))"
    elif tema == "🟡 Ouro Milionário": cor_neon = "#FFD700"; grad = "linear-gradient(135deg, rgba(255,215,0,0.1), rgba(0,0,0,0))"
    elif tema == "🔵 Azul Cyberpunk": cor_neon = "#00e5ff"; grad = "linear-gradient(135deg, rgba(0,229,255,0.1), rgba(0,0,0,0))"
    elif tema == "🔴 Vermelho Kamikaze": cor_neon = "#ff3333"; grad = "linear-gradient(135deg, rgba(255,51,51,0.1), rgba(0,0,0,0))"
    elif tema == "🟣 Rosa Choque": cor_neon = "#ff00ff"; grad = "linear-gradient(135deg, rgba(255,0,255,0.1), rgba(0,0,0,0))"
    else: cor_neon = "#00ff88"; grad = "linear-gradient(135deg, rgba(0,255,136,0.1), rgba(0,0,0,0))"
    c_prim = "#ffffff"; c_sec = "#888888"; c_inv = "#000000"
    card_bg = "rgba(20, 22, 30, 0.65)"; card_border = "rgba(255, 255, 255, 0.1)"
    tab_bg = "rgba(10, 12, 18, 0.85)"; tab_active_bg = "rgba(255,255,255,0.1)"
    terminal_bg = "#050508"; progress_bg = "#222222"; c_bg_badge = "rgba(0,0,0,0.4)"

# --- CSS SUPREMO (COM FIX DO FUNDO PRETO) ---
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;500;700;900&display=swap');
    
    /* MUDANÇA 1: FUNDO 100% PREENCHIDO (FIM DAS BORDAS PRETAS) */
    html, body, [data-testid="stAppViewContainer"], .main {{
        background: transparent !important;
        font-family: 'Inter', sans-serif !important;
    }}
    #root {{
        background: {'linear-gradient(rgba(240,242,246,0.9), rgba(255,255,255,0.95))' if is_light else 'radial-gradient(circle at 50% 0%, rgba(20,22,30,0.9), rgba(10,10,12,1))'}, url('{LINK_SUA_IMAGEM_DE_FUNDO}') !important;
        background-size: cover !important;
        background-position: center !important;
        background-attachment: fixed !important;
        min-height: 100dvh !important;
        width: 100vw !important;
    }}

    header[data-testid="stHeader"] {{ display: none !important; }}
    .block-container {{ padding-top: 1rem !important; padding-bottom: 80px !important; max-width: 800px !important; }}
    #MainMenu, .stDeployButton, footer {{ display: none !important; }}
    
    .stMarkdown p, .stText p, h1, h2, h3, h4, h5, h6, label {{ color: {c_prim} !important; }}
    div[data-baseweb="select"] > div, div[data-baseweb="input"] > div, textarea {{ background-color: {card_bg} !important; color: {c_prim} !important; border: 1px solid {card_border} !important; }}
    
    ::-webkit-scrollbar {{ width: 0px; background: transparent; }} /* MUDANÇA 9: Scrollbar oculta no mobile */
    
    /* MUDANÇA 3: TIPOGRAFIA METÁLICA/GRADIENT */
    .metallic-text {{ 
        background: linear-gradient(180deg, #ffffff 0%, {cor_neon} 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 900; 
    }}
    
    /* MUDANÇA 2: MENU FIXED (STICKY HEADER) */
    div[data-testid="stTabs"] > div:first-of-type {{ 
        position: sticky !important; top: 10px !important; z-index: 999 !important;
        background-color: {tab_bg} !important; backdrop-filter: blur(15px) !important; 
        -webkit-backdrop-filter: blur(15px) !important; border-radius: 50px !important; 
        padding: 5px !important; margin-bottom: 20px !important; border: 1px solid {card_border} !important; 
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
    }}
    div[data-testid="stTabs"] button[role="tab"] {{ color: {c_sec} !important; font-weight: 700 !important; font-size: 11px !important; background: transparent !important; border: none !important; border-radius: 30px !important; padding: 10px 15px !important; transition: all 0.3s ease !important;}}
    div[data-testid="stTabs"] button[role="tab"]:hover {{ color: {c_prim} !important; }}
    div[data-testid="stTabs"] button[role="tab"][aria-selected="true"] {{ color: {cor_neon} !important; background: {tab_active_bg} !important; border-bottom: 2px solid {cor_neon} !important; }}
    
    /* MUDANÇA 4: BORDAS HOLOGRÁFICAS (3D BEVEL) */
    .glass-card {{ 
        background: {card_bg}; backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px);
        border: 1px solid {card_border}; border-radius: 16px; padding: 15px; margin-bottom: 15px; 
        width: 100%; box-sizing: border-box; transition: transform 0.3s ease, box-shadow 0.3s ease; 
        color: {c_prim};
        box-shadow: inset 0 1px 1px rgba(255,255,255,0.1), 0 8px 20px rgba(0,0,0,0.4);
    }}
    
    .terminal-card {{ background: {terminal_bg}; border: 1px solid {card_border}; border-left: 3px solid {cor_neon}; border-radius: 8px; padding: 15px; font-family: monospace; color: {cor_neon}; width: 100%; box-sizing: border-box; background-image: radial-gradient(rgba(255,255,255,0.05) 1px, transparent 1px); background-size: 10px 10px; }}
    .neon-text {{ color: {cor_neon}; font-weight: 900; font-size: 14px; letter-spacing: 1px; text-transform: uppercase; text-shadow: 0 0 10px {cor_neon}40; }}
    
    /* MUDANÇA 7: BOTÕES NEUMÓRFICOS */
    .stButton>button {{ 
        background: {grad} !important; color: {c_prim} !important; font-weight: 900 !important; 
        border-radius: 12px !important; border: 1px solid {cor_neon} !important; padding: 12px 20px !important; 
        width: 100%; transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important; 
        box-shadow: inset 0 1px 1px rgba(255,255,255,0.2), 0 4px 10px rgba(0,0,0,0.3) !important; 
    }}
    .stButton>button:hover {{ background: {cor_neon} !important; color: {c_inv} !important; transform: translateY(-2px) !important; box-shadow: 0 8px 20px {cor_neon}60 !important; }}
    .stButton>button:active {{ transform: translateY(2px) !important; box-shadow: inset 0 3px 5px rgba(0,0,0,0.5) !important; filter: brightness(0.9) !important; }}
    
    /* MUDANÇA 5: BARRAS ANIMADAS */
    .progress-bg {{ width: 100%; background: {progress_bg}; border-radius: 10px; height: 6px; margin-bottom: 8px; overflow: hidden; }}
    .progress-fill-atk {{ height: 6px; background: linear-gradient(90deg, #ff0055, #ff5555); border-radius: 10px; box-shadow: 0 0 10px #ff0055; transition: width 1.5s ease-out; }}
    .progress-fill-def {{ height: 6px; background: linear-gradient(90deg, #0055ff, #00aaff); border-radius: 10px; box-shadow: 0 0 10px #0055ff; transition: width 1.5s ease-out; }}
    
    /* MUDANÇA 6: EFEITO RESPIRAR (PULSAR) */
    .live-badge {{ background-color: #ff3333; color: white; padding: 2px 6px; border-radius: 4px; font-size: 10px; font-weight: bold; animation: pulsar 1.5s infinite; display: inline-block; }}
    @keyframes pulsar {{ 0% {{ box-shadow: 0 0 0 0 rgba(255,51,51,0.7); }} 70% {{ box-shadow: 0 0 0 6px rgba(255,51,51,0); }} 100% {{ box-shadow: 0 0 0 0 rgba(255,51,51,0); }} }}
    
    /* MUDANÇA 8: SKELETON LOADING TEXT */
    .loading-pulse {{ animation: pulse-text 1.5s infinite; color: {c_sec}; font-family: monospace; font-size: 12px; }}
    @keyframes pulse-text {{ 0% {{ opacity: 0.4; }} 50% {{ opacity: 1; }} 100% {{ opacity: 0.4; }} }}
    </style>
""", unsafe_allow_html=True)

url_key = st.query_params.get("key", "")

# --- 5. TELA DE LOGIN VIP ---
if not st.session_state.autenticado:
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    with st.container():
        st.markdown("<div class='glass-card' style='max-width:400px; margin:auto; text-align:center;'>", unsafe_allow_html=True)
        st.markdown(f"<h1 class='metallic-text' style='margin-bottom:0;'>V8 SUPREME</h1>", unsafe_allow_html=True)
        st.markdown(f"<p style='color:{c_sec}; font-size: 11px; letter-spacing:2px; margin-bottom: 30px;'>A.I. INTELLIGENCE HUB</p>", unsafe_allow_html=True)
        nome_in = st.text_input("Credencial de Acesso:", placeholder="Seu Nome")
        key_in = st.text_input("Chave Criptografada:", value=url_key, type="password", placeholder="Cole sua Key")
        if st.button("INICIAR SESSÃO", use_container_width=True):
            if key_in == MASTER_KEY or key_in: 
                st.session_state.autenticado = True; st.session_state.is_admin = True if key_in == MASTER_KEY else False; st.session_state.user_nome = nome_in if nome_in else "VIP"
                st.rerun()
        st.markdown(f"<p style='text-align:center; margin-top:20px; color:{c_sec}; font-size: 10px;'>OU</p>", unsafe_allow_html=True)
        if st.button("🔓 BIOMETRIA / FACE ID"):
            if url_key or nome_in: 
                area_msg = st.empty()
                area_msg.markdown("<p class='loading-pulse'>📷 Escaneando biometria facial...</p>", unsafe_allow_html=True); time.sleep(1)
                area_msg.success("✅ Acesso Autorizado."); time.sleep(0.5)
                st.session_state.autenticado = True; st.session_state.user_nome = nome_in if nome_in else "CEO"; st.rerun()
            else: st.warning("Requer credencial no dispositivo.")
        st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# --- NEWS TICKER ---
noticias = [f"🚨 URGENTE: {jogos_vitrine[3]['casa']} com surto viral no elenco.", "💰 Sindicato Asiático injetou $2M na linha de Over Gols.", "🔥 Win Rate global da IA atingiu 89.4% nas últimas 24h."]
st.markdown(f"<marquee style='background: {c_bg_badge}; color: {cor_neon}; padding: 5px; font-size: 11px; font-weight: bold; border-radius: 4px; margin-bottom: 10px;'>{' &nbsp; | &nbsp; '.join(noticias)}</marquee>", unsafe_allow_html=True)

win_rate = (st.session_state.total_acertos / st.session_state.total_jogos) * 100 if st.session_state.total_jogos > 0 else 0
saldo_total = sum(st.session_state.bancas.values())

# FEATURE 3: STOP LOSS (Alerta)
if saldo_total < st.session_state.banca_inicial_dia * 0.9:
    st.error("⚠️ ALERTA DE STOP LOSS: Sua banca caiu mais de 10% hoje. Aconselhamos encerrar as operações por 24h.")

# --- TOP BAR VIP ---
st.markdown(f"""
    <div style='display:flex; justify-content:space-between; align-items:center; margin-bottom: 15px; padding: 15px; background: {card_bg}; border-radius: 16px; border: 1px solid {card_border}; width: 100%; box-sizing: border-box; box-shadow: inset 0 1px 1px rgba(255,255,255,0.1), 0 4px 15px rgba(0,0,0,0.2);'>
        <div style='display:flex; align-items:center;'>
            <div style='font-size: 32px; margin-right: 12px; filter: drop-shadow(0 0 10px {cor_neon}80);'>{st.session_state.avatar}</div>
            <div>
                <div class='metallic-text' style='font-size:16px;'>{st.session_state.user_nome.upper()} <span style='background: linear-gradient(90deg, {cor_neon} 0%, {c_prim} 50%, {cor_neon} 100%); background-size: 200% auto; color: {c_inv}; font-size: 9px; padding: 2px 6px; border-radius: 4px; font-weight: 900; animation: shine 3s linear infinite; vertical-align: middle;'>PRO</span></div>
                <div style='color:{cor_neon}; font-size:11px; margin-top:2px;'>{st.session_state.titulo_apostador}</div>
            </div>
        </div>
        <div style='text-align:right;'>
            <div style='color:{c_sec}; font-size:10px; text-transform:uppercase; letter-spacing:1px;'>Portfólio Vivo</div>
            <div style='color:{c_prim}; font-weight:900; font-size:20px; letter-spacing:-1px;'>{fmt_moeda(saldo_total)}</div>
        </div>
    </div>
""", unsafe_allow_html=True)

# --- 6. NAVEGAÇÃO PRINCIPAL (STICKY) ---
t1, t2, t3, t4, t5 = st.tabs(["📊 HOME", "🎯 RADAR", "🧾 OPERAÇÕES", "🛡️ SAFE", "⚙️ HUB"])
LIGAS_DISPONIVEIS = {"🇬🇧 Premier League": "soccer_epl", "🇪🇺 Champions League": "soccer_uefa_champs_league", "🇪🇸 La Liga": "soccer_spain_la_liga", "🇧🇷 Brasileirão": "soccer_brazil_campeonato"}

# ==========================================
# ABA 1: DASHBOARD
# ==========================================
with t1:
    if st.session_state.mod_grafico:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.markdown(f"<p style='color: {c_sec}; font-size: 11px; font-weight: bold; margin-bottom:5px; text-transform:uppercase;'>📈 Rendimento Linear</p>", unsafe_allow_html=True)
        st.line_chart(st.session_state.historico_banca, height=120, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # FEATURE 1: FEAR & GREED INDEX
    fg_val = random.randint(30, 80)
    fg_cor = "#ff3333" if fg_val < 45 else ("#FFD700" if fg_val < 65 else "#00ff88")
    fg_text = "MEDO (Cautela)" if fg_val < 45 else ("NEUTRO" if fg_val < 65 else "GANÂNCIA (Agressivo)")
    
    st.markdown(f"""
        <div style='display: flex; justify-content: space-between; gap: 10px; margin-bottom: 20px; width: 100%; box-sizing: border-box;'>
            <div class='glass-card' style='flex:1; text-align:center; padding: 10px; margin:0;'>
                <p style='color:{c_sec}; font-size:10px; margin:0;'>Win Rate A.I.</p>
                <p style='color:{c_prim}; font-size:18px; font-weight:900; margin:0;'>{win_rate:.1f}%</p>
            </div>
            <div class='glass-card' style='flex:1; text-align:center; padding: 10px; margin:0;'>
                <p style='color:{c_sec}; font-size:10px; margin:0;'>Market Sentiment</p>
                <p style='color:{fg_cor}; font-size:14px; font-weight:900; margin:0; margin-top:2px;'>{fg_val} - {fg_text}</p>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # FEATURE 4: VIP LEADERBOARD
    st.markdown(f"<h4 class='metallic-text' style='font-size:14px; margin-top:10px;'>🏆 TOP 3 VIPS DO DIA</h4>", unsafe_allow_html=True)
    st.markdown(f"""
        <div class='glass-card' style='padding: 10px;'>
            <div style='display:flex; justify-content:space-between; border-bottom:1px solid {card_border}; padding-bottom:5px;'><span>🥇 TraderAlpha</span> <b style='color:{cor_neon};'>+{fmt_moeda(4520)}</b></div>
            <div style='display:flex; justify-content:space-between; border-bottom:1px solid {card_border}; padding:5px 0;'><span>🥈 {st.session_state.user_nome}</span> <b style='color:{cor_neon};'>+{fmt_moeda(1250)}</b></div>
            <div style='display:flex; justify-content:space-between; padding-top:5px;'><span>🥉 Lucas_Inv</span> <b style='color:{cor_neon};'>+{fmt_moeda(890)}</b></div>
        </div>
    """, unsafe_allow_html=True)

    # FEATURE 7: AI COACH
    coach_msg = "Sua taxa de acerto está excepcional. Mantenha a gestão atual e evite aumentar a stake pela emoção." if win_rate > 70 else "Foco na disciplina. O mercado é feito de ciclos. Use o modo recuperação se necessário."
    st.info(f"🧠 **Mentor V8:** {coach_msg}")

    if st.session_state.mod_live:
        minuto = datetime.now().minute
        j_live = jogos_vitrine[2]
        st.markdown(f"<h4 class='metallic-text' style='font-size:14px;'>🔴 LIVE SCORES</h4>", unsafe_allow_html=True)
        st.markdown(f"""
            <div class='glass-card' style='display:flex; justify-content:space-between; align-items:center; border-left: 4px solid #ff3333;'>
                <div><span class='live-badge'>{(minuto+23)%90+1}'</span> <span style='color:{c_prim}; font-weight:bold; font-size: 14px; margin-left: 10px;'>{j_live['casa']} {(minuto//15)%3} x {(minuto//25)%2} {j_live['fora']}</span></div>
                <div style='text-align:right; font-size:11px; color:{c_sec};'>A.I. Target<br><b style='color:{cor_neon};'>Over 1.5</b></div>
            </div>
        """, unsafe_allow_html=True)

# ==========================================
# ABA 2: RADAR A.I
# ==========================================
with t2:
    st.markdown("<h4 class='metallic-text'>SELECTION HUB</h4>", unsafe_allow_html=True)
    
    # FEATURE 10: SNIPER MODE TOGGLE
    modo_sniper = st.toggle("🎯 Ativar Foco Sniper (Apenas +95% Confiança)")

    if st.session_state.time_coracao and not modo_sniper:
        st.markdown(f"<div class='glass-card' style='border: 1px solid {cor_neon};'><span style='color:{cor_neon}; font-size:12px; font-weight:bold;'>❤️ TIME DO CORAÇÃO: {st.session_state.time_coracao.upper()}</span><br><span style='color:{c_prim}; font-size:14px;'>O modelo detetou +EV para a próxima partida.</span></div>", unsafe_allow_html=True)

    with st.expander("🤖 ORÁCULO A.I. (CHAT)"):
        pergunta = st.text_input("Comando de Análise:", placeholder="Ex: Analise a liquidez do Flamengo")
        if st.button("PROCESSAR DEEP DATA"):
            if pergunta:
                p_msg = st.empty()
                p_msg.markdown("<p class='loading-pulse'>> Estabelecendo handshake seguro...</p>", unsafe_allow_html=True)
                time.sleep(1)
                p_msg.markdown("<p class='loading-pulse'>> Compilando 10.000 variáveis em tempo real...</p>", unsafe_allow_html=True)
                time.sleep(1)
                t_alvo = pergunta.split()[-1].capitalize()
                p_msg.markdown(f"<div class='terminal-card' style='border-color:{cor_neon};'>> ALVO: {t_alvo.upper()}<br>> STATUS: OPORTUNIDADE +EV DETECTADA.<br>> SUGESTÃO: AGUARDAR ODD BATER @1.65.</div>", unsafe_allow_html=True)

    st.markdown(f"<br><p style='color:{c_sec}; font-size: 12px; font-weight:bold;'>VARREDURA DO MERCADO ASIÁTICO</p>", unsafe_allow_html=True)
    codigo_da_liga = LIGAS_DISPONIVEIS[st.selectbox("Selecionar Filtro Global:", list(LIGAS_DISPONIVEIS.keys()))]
    
    if st.button("EXECUTAR SCANNER QUANTITATIVO"):
        with st.spinner("Interceptando dados de bookmakers..."):
            dados = buscar_dados_api(codigo_da_liga) 
            if dados:
                st.session_state.analisados = []
                d_hoje = (datetime.utcnow() - timedelta(hours=3)).strftime("%Y-%m-%d")
                for jogo in [j for j in dados if j.get('commence_time', '').startswith(d_hoje)][:10]:
                    c, f = jogo.get('home_team', 'Casa'), jogo.get('away_team', 'Fora')
                    ap = {"m": f"Vitória {c}", "o": round(random.uniform(1.3, 2.5), 2)} 
                    atk, dfs = calcular_forca_equipa(c)
                    # FEATURE 6: DROPPING ODDS (Simulado)
                    drop = random.choice([True, False, False])
                    st.session_state.analisados.append({"jogo": f"{c} x {f}", "casa": c, "fora": f, "m": ap["m"], "o": ap["o"], "conf": random.randint(85, 99), "atk": atk, "def": dfs, "xg_c": round(random.uniform(0.5, 3.0), 2), "xg_f": round(random.uniform(0.2, 1.8), 2), "drop": drop})
                st.toast("✅ Scanner concluído com sucesso.")
            else: st.error("Erro na comunicação com a API de Odds.")

    if st.session_state.analisados:
        st.markdown(f"<hr style='border-color: {card_border};'>", unsafe_allow_html=True)
        for idx, item in enumerate(st.session_state.analisados):
            if modo_sniper and item['conf'] < 95: continue # Filtro Sniper ativado
            
            drop_html = f"<span style='color:#00e5ff; font-weight:bold; font-size:10px;'>📉 DROPPING ODD</span>" if item['drop'] else ""
            
            html_card = f"<div class='glass-card'><div style='display:flex; justify-content:space-between; align-items:center;'><div style='font-size:14px; font-weight:900; color:{c_prim};'>{item['casa']} <span style='color:{c_sec}; font-size:10px;'>VS</span> {item['fora']} {drop_html}</div><div style='color:{cor_neon}; font-weight:900; font-size:16px;'>@{item['o']}</div></div><div style='margin-top:15px; font-size:10px; color:{c_sec};'>PRESSÃO OFENSIVA (xG: {item['xg_c']})</div><div class='progress-bg'><div class='progress-fill-atk' style='width:{item['atk']}%;'></div></div><div style='margin-top:5px; font-size:10px; color:{c_sec};'>MURALHA DEFENSIVA (xG: {item['xg_f']})</div><div class='progress-bg'><div class='progress-fill-def' style='width:{item['def']}%;'></div></div><div style='margin-top:15px; background:{c_bg_badge}; padding:10px; border-radius:8px;'><span style='font-size:11px; color:{c_sec};'>ALGORITMO V8:</span> <b style='color:{c_prim};'>{item['m']}</b><br><span style='font-size:11px; color:{c_sec};'>CONFIANÇA:</span> <b style='color:{cor_neon};'>{item['conf']}%</b></div></div>"
            st.markdown(html_card, unsafe_allow_html=True)
            
            col_add1, col_add2 = st.columns(2)
            with col_add1:
                if st.button("➕ INJETAR BILHETE", key=f"btn_m_{idx}"): st.session_state.bilhete.append(item); st.toast("✅ Adicionado à Operação!")
            with col_add2:
                if st.button("💾 SALVAR DICA", key=f"btn_s_{idx}"): st.session_state.analises_salvas.append(item); st.toast("💾 Salvo no Tracking Pessoal!")

# ==========================================
# ABA 3: OPERAÇÕES (KELLY CRITERION INCLUSO)
# ==========================================
with t3:
    st.markdown("<h4 class='metallic-text'>CENTRAL DE OPERAÇÕES</h4>", unsafe_allow_html=True)
    if st.session_state.bilhete:
        odd_f = 1.0
        hash_bilhete = f"V8-{random.randint(1000, 9999)}"
        
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        for b in st.session_state.bilhete:
            odd_f *= b['o']
            st.markdown(f"<p style='margin:0; font-size:14px; border-bottom: 1px solid {card_border}; padding: 5px 0; color:{c_prim};'>✅ <b>{b['jogo']}</b> <span style='float:right; color:{cor_neon}; font-weight:bold;'>@{b['o']}</span></p>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown(f"<h2 style='text-align:center; font-weight:900; font-size:40px; color:{c_prim}; text-shadow: 0 0 25px {cor_neon}80;'>ODD <span style='color:{cor_neon};'>@{odd_f:.2f}</span></h2>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align:center; font-size:10px; color:{c_sec}; margin-top:-10px;'>Copy ID: {hash_bilhete}</p>", unsafe_allow_html=True)
        
        banca_escolhida = st.selectbox("Conta Origem:", list(st.session_state.bancas.keys()), key="banca_mult")
        banca_disp = st.session_state.bancas[banca_escolhida]
        
        # FEATURE 2: KELLY CRITERION
        st.session_state.usar_kelly = st.checkbox("🧠 Usar Critério de Kelly (Avançado)", value=st.session_state.usar_kelly)
        st.session_state.juros_compostos = st.checkbox("🔄 Alavancar Lucro Anterior", value=st.session_state.juros_compostos)
        
        if st.session_state.recuperacao_red: rec_stake = banca_disp * 0.005; risco = "🛡️ DEFESA"
        elif st.session_state.usar_kelly: 
            prob_vitoria = 1 / odd_f * 1.1 # Supõe leve vantagem
            kelly_pct = ((odd_f - 1) * prob_vitoria - (1 - prob_vitoria)) / (odd_f - 1)
            rec_stake = banca_disp * max(0.01, min(kelly_pct, 0.05)) # Trava max 5%
            risco = "🧮 KELLY MATEMÁTICO"
        else:
            rec_stake = banca_disp * (0.05 if st.session_state.juros_compostos else (0.03 if odd_f < 2.5 else 0.01))
            risco = "🔥 ALAVANCAGEM" if st.session_state.juros_compostos else ("🟢 BAIXO" if odd_f < 2.5 else "🔴 ALTO")

        st.markdown(f"<div class='terminal-card' style='margin-bottom:20px;'>> AVALIAÇÃO: {risco}<br>> GESTÃO RECOMENDADA: <span style='color:{cor_neon}; font-size:16px;'>{fmt_moeda(rec_stake)}</span></div>", unsafe_allow_html=True)
        
        valor_aposta = st.number_input("Entrada Efetiva:", min_value=1.0, value=float(max(1.0, rec_stake)), step=5.0)
        st.info(f"🤑 RETORNO ESTIMADO: {fmt_moeda(valor_aposta * odd_f)}")

        col_r1, col_r2 = st.columns(2)
        with col_r1:
            if st.button("✅ BATER GREEN (LIQUIDAR)"):
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
            if st.button("❌ ASSUMIR RED"):
                st.session_state.total_jogos += len(st.session_state.bilhete)
                st.session_state.bancas[banca_escolhida] -= valor_aposta
                st.session_state.historico_banca.append(sum(st.session_state.bancas.values()))
                st.session_state.bilhete = [] 
                st.rerun()
    else:
        st.info("Carrinho vazio.")

    st.markdown(f"<h4 class='metallic-text' style='margin-top: 40px;'>📂 TRACKING DE SINGLES</h4>", unsafe_allow_html=True)
    if st.session_state.analises_salvas:
        for i, a in enumerate(st.session_state.analises_salvas):
            html_track = f"<div class='glass-card' style='border-left: 3px solid #00e5ff; padding:10px;'><div style='font-size:13px; font-weight:bold; color:{c_prim};'>{a['jogo']}</div><div style='display:flex; justify-content:space-between; margin-top:2px;'><span style='color:{c_sec}; font-size:11px;'>Call: <b style='color:{c_prim};'>{a['m']}</b></span><span style='color:{cor_neon}; font-weight:bold; font-size:12px;'>@{a['o']}</span></div></div>"
            st.markdown(html_track, unsafe_allow_html=True)
            c_g, c_r, c_d = st.columns([0.4, 0.4, 0.2])
            with c_g:
                if st.button("✅ WIN", key=f"tg_{i}"):
                    st.session_state.total_jogos += 1; st.session_state.total_acertos += 1
                    st.session_state.historico_greens.insert(0, {"Data": datetime.now().strftime("%Y-%m-%d"), "Jogo": a['jogo'], "Mercado": a['m'], "Odd": a['o']})
                    st.session_state.analises_salvas.pop(i)
                    tocar_som_customizado(); time.sleep(1); st.rerun()
            with c_r:
                if st.button("❌ LOSS", key=f"tr_{i}"):
                    st.session_state.total_jogos += 1; st.session_state.analises_salvas.pop(i); st.rerun()
            with c_d:
                if st.button("🗑️", key=f"td_{i}"): st.session_state.analises_salvas.pop(i); st.rerun()
    else:
        st.caption("Nenhuma single salva para validação.")

# ==========================================
# ABA 4: SAFE (BINGO DO DIA)
# ==========================================
with t4:
    st.markdown("<h4 class='metallic-text'>ALTO EV (SAFE)</h4>", unsafe_allow_html=True)
    if not st.session_state.is_vip:
        st.markdown(f"<div class='glass-card' style='position:relative; text-align:center; overflow:hidden;'><div style='filter: blur(8px); padding:20px;'><h3 style='color:{c_prim};'>Dupla de Ouro</h3><p style='color:{c_sec};'>Odd: @1.85 | Confiança: 99%</p></div><div style='position:absolute; top:50%; left:50%; transform:translate(-50%, -50%); background:{c_bg_badge}; padding:20px; border-radius:12px; width:80%;'><h1>🔒</h1><h4 style='color:{cor_neon};'>ACESSO RESTRITO</h4><p style='font-size:11px; color:{c_prim};'>Eleve seu plano para Supremo.</p></div></div>", unsafe_allow_html=True)
    else:
        if not st.session_state.analisados: st.info("⚠️ Varredura prévia requerida no RADAR.")
        else:
            seguros = sorted([j for j in st.session_state.analisados if 1.15 <= j['o'] <= 1.65], key=lambda x: x['conf'], reverse=True)
            if len(seguros) >= 2:
                safe_pick = seguros[:2]
                odd_safe_total = safe_pick[0]['o'] * safe_pick[1]['o']
                media_conf = (safe_pick[0]['conf'] + safe_pick[1]['conf']) // 2
                html_safe = f"<div class='glass-card' style='border: 1px solid {cor_neon};'><div style='text-align:center; margin-bottom: 15px;'><span style='background:{cor_neon}; color:#000; padding:5px 15px; border-radius:20px; font-weight:bold; font-size:12px;'>🏆 IA ASSERTIVIDADE: {media_conf}%</span></div><div style='border-left: 4px solid {cor_neon}; padding-left: 10px; margin-bottom: 10px;'><div style='color:{c_prim}; font-weight:bold; font-size: 14px;'>⚽ {safe_pick[0]['jogo']}</div><div style='color:{c_sec}; font-size: 12px;'>🎯 {safe_pick[0]['m']} | <span style='color:{cor_neon}; font-weight:bold;'>@{safe_pick[0]['o']:.2f}</span></div></div><div style='border-left: 4px solid {cor_neon}; padding-left: 10px; margin-bottom: 15px;'><div style='color:{c_prim}; font-weight:bold; font-size: 14px;'>⚽ {safe_pick[1]['jogo']}</div><div style='color:{c_sec}; font-size: 12px;'>🎯 {safe_pick[1]['m']} | <span style='color:{cor_neon}; font-weight:bold;'>@{safe_pick[1]['o']:.2f}</span></div></div><hr style='border-color: {card_border};'><h3 style='text-align:center; color:{cor_neon}; text-shadow: 0 0 10px {cor_neon}60;'>📊 ODD FINAL: {odd_safe_total:.2f}</h3></div>"
                st.markdown(html_safe, unsafe_allow_html=True)
                if st.button("🔥 COPIAR PARA OPERAÇÕES"): st.session_state.bilhete.extend(safe_pick); st.toast("✅ Copiado!"); tocar_som_customizado()
            else: st.warning("A IA não encontrou perfil 'Safe' nesta varredura.")

# ==========================================
# ABA 5: HUB E PERFIL
# ==========================================
with t5:
    st.markdown(f"<h3 style='color:{c_prim}; text-align:center; font-weight:900;'>V8 <span style='color:{cor_neon};'>HUB</span></h3>", unsafe_allow_html=True)
    
    with st.expander("⚙️ CUSTOMIZAÇÃO EXTREMA"):
        st.selectbox("Motor Gráfico:", ["🟢 Verde Hacker", "🟡 Ouro Milionário", "🔵 Azul Cyberpunk", "🔴 Vermelho Kamikaze", "🟣 Rosa Choque", "⚪ Modo Claro (Light)"], key="tema_escolhido")
        col_a1, col_a2 = st.columns(2)
        col_a1.selectbox("Avatar:", ["🐺", "🦈", "🦉", "🧙‍♂️", "👑", "🚀"], key="avatar")
        col_a2.selectbox("Moeda:", ["R$", "US$", "€", "₿"], key="moeda")
        st.text_input("Foco Específico (Time):", placeholder="Ex: Flamengo", key="time_coracao")
        st.selectbox("Animação de Vitória:", ["Balões", "Chuva de Neve"], key="animacao_vitoria")
        st.selectbox("Som do Green:", ["Clássico (Caixa Registradora)", "Cassino Las Vegas", "Moeda Retro (8-bit)"], key="som_green")

    with st.expander("🏛️ GESTÃO DE BANCAS E RISCO"):
        col_c1, col_c2, col_c3 = st.columns(3)
        st.session_state.bancas["Betano"] = col_c1.number_input("Betano", value=st.session_state.bancas["Betano"], step=50.0)
        st.session_state.bancas["Bet365"] = col_c2.number_input("Bet365", value=st.session_state.bancas["Bet365"], step=50.0)
        st.session_state.bancas["Betfair"] = col_c3.number_input("Betfair", value=st.session_state.bancas["Betfair"], step=50.0)
        st.session_state.recuperacao_red = st.checkbox("🛡️ Ativar Protocolo de Defesa", value=st.session_state.recuperacao_red)

    with st.expander("🧩 WIDGETS DO DASHBOARD"):
        st.session_state.mod_grafico = st.checkbox("Exibir Gráfico de Rendimento", value=st.session_state.mod_grafico)
        st.session_state.mod_massas = st.checkbox("Exibir Smart Money (Trending)", value=st.session_state.mod_massas)
        st.session_state.mod_live = st.checkbox("Exibir Live Scores", value=st.session_state.mod_live)

    # FEATURE 8: EXPORTAÇÃO PARA CSV/EXCEL
    st.markdown(f"<p style='color:{c_sec}; font-size:11px; font-weight:bold; margin-top:20px;'>📑 COMPLIANCE E DADOS</p>", unsafe_allow_html=True)
    df_greens = pd.DataFrame(st.session_state.historico_greens)
    csv = df_greens.to_csv(index=False).encode('utf-8')
    st.download_button(label="📥 Baixar Histórico de Operações (CSV)", data=csv, file_name='v8_historico.csv', mime='text/csv', use_container_width=True)

    st.markdown(f"<p style='color:{c_sec}; font-size:11px; font-weight:bold; margin-top:20px;'>📓 DIÁRIO DE TRADER</p>", unsafe_allow_html=True)
    st.text_area("Notas Encriptadas:", value=st.session_state.diario_bordo, placeholder="Regra 1: Evitar MLS de madrugada...", key="diario_bordo", label_visibility="collapsed")

    if st.session_state.is_admin:
        st.markdown(f"<div class='glass-card' style='border-color:#ff3333; margin-top:20px;'><p style='color:#ff3333; font-size:11px; font-weight:bold;'>🛠️ ADMIN PANEL</p>", unsafe_allow_html=True)
        n_links = st.text_area("Links de Afiliados (1 por linha):", value="\n".join(st.session_state.links_afiliados), height=60)
        if st.button("Atualizar DB de Links"): st.session_state.links_afiliados = [l.strip() for l in n_links.split('\n') if l.strip()]
        c_nome = st.text_input("Nova Key:")
        if st.button("FORJAR ACESSO"):
            salvar_key(c_nome, 24)
            st.code(f"{LINK_PAINEL}?key={c_nome}")
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<br><br>", unsafe_allow_html=True)
    if st.button("ENCERRAR SESSÃO", type="primary"):
        st.session_state.autenticado = False
        st.rerun()
