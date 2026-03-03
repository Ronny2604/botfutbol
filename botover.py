import streamlit as st
import random
import time
import urllib.parse
import requests
import hashlib
import pandas as pd
from datetime import datetime, timedelta

# --- 1. CONFIGURAÇÃO BASE ---
st.set_page_config(page_title="V8 SUPREME PRO", layout="wide", initial_sidebar_state="collapsed")
LINK_IMG_FUNDO = "https://raw.githubusercontent.com/Ronny2604/botfutbol/main/photo_5172618853803035536_c.png"
API_KEY_PADRAO = "da4633249ece20283d29604cec7a7114"

# --- 2. BLINDAGEM DE MEMÓRIA (ANTI-CRASH TOTAL) ---
if 'autenticado' not in st.session_state: st.session_state['autenticado'] = False
if 'user_nome' not in st.session_state: st.session_state['user_nome'] = ""
if 'bilhete' not in st.session_state: st.session_state['bilhete'] = []
if 'analisados' not in st.session_state: st.session_state['analisados'] = []
if 'analises_salvas' not in st.session_state: st.session_state['analises_salvas'] = []
if 'tema_escolhido' not in st.session_state: st.session_state['tema_escolhido'] = "🟢 Verde Hacker"
if 'is_vip' not in st.session_state: st.session_state['is_vip'] = True 
if 'boss_mode' not in st.session_state: st.session_state['boss_mode'] = False
if 'api_key_odds' not in st.session_state: st.session_state['api_key_odds'] = API_KEY_PADRAO
if 'avatar' not in st.session_state: st.session_state['avatar'] = "🐺"
if 'moeda' not in st.session_state: st.session_state['moeda'] = "R$"
if 'titulo_apostador' not in st.session_state: st.session_state['titulo_apostador'] = "[O Estrategista]"
if 'mod_grafico' not in st.session_state: st.session_state['mod_grafico'] = True
if 'bancas' not in st.session_state: st.session_state['bancas'] = {"Betano": 1000.0, "Bet365": 500.0, "Betfair": 0.0}
if 'historico_banca' not in st.session_state: st.session_state['historico_banca'] = [1500.0]
if 'total_jogos' not in st.session_state: st.session_state['total_jogos'] = 1248
if 'total_acertos' not in st.session_state: st.session_state['total_acertos'] = 1115

# --- FUNÇÕES DE SISTEMA ---
def fmt_moeda(valor):
    moeda = st.session_state.get('moeda', 'R$')
    return f"{moeda} {valor:,.2f}"

def tocar_som():
    som_str = '<audio autoplay style="display:none;"><source src="https://assets.mixkit.co/active_storage/sfx/2003/2003-preview.mp3" type="audio/mpeg"></audio>'
    st.markdown(som_str, unsafe_allow_html=True)

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
    url = f"https://api.the-odds-api.com/v4/sports/{codigo_da_liga}/odds/?apiKey={api_key}&regions=eu,uk&markets=h2h"
    try:
        r = requests.get(url, timeout=5)
        if r.status_code == 200 and isinstance(r.json(), list): return r.json()
    except: pass
    return None

jogos_vitrine = gerar_dados_mock()

# --- 3. CONTROLE DE TEMA (SEGURO) ---
tema = st.session_state.get('tema_escolhido', "🟢 Verde Hacker")
if "Ouro" in tema: cor_neon = "#FFD700"
elif "Azul" in tema: cor_neon = "#00e5ff"
elif "Vermelho" in tema: cor_neon = "#ff3333"
elif "Rosa" in tema: cor_neon = "#ff00ff"
else: cor_neon = "#00ff88"

grad = f"linear-gradient(135deg, {cor_neon}20, rgba(0,0,0,0))"

# --- 4. CSS MINIMALISTA (SEM MARGENS QUE QUEBRAM TELA) ---
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;500;700;900&display=swap');
    
    html, body, [class*="css"] {{ font-family: 'Inter', sans-serif !important; }}
    header[data-testid="stHeader"] {{ display: none !important; }}
    .block-container {{ padding-top: 1rem !important; padding-bottom: 50px !important; }}
    #MainMenu, .stDeployButton, footer {{ display: none !important; }}
    
    /* Fundo Seguro */
    .stApp {{ 
        background: radial-gradient(circle at 50% 0%, rgba(20,22,30,0.9), rgba(10,10,12,1)), url('{LINK_IMG_FUNDO}'); 
        background-size: cover; 
        background-position: center; 
        background-attachment: fixed; 
        color: #ffffff; 
    }}
    
    /* Abas Nativas (Pílula) */
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
    
    /* Cartões de Vidro Seguros */
    .glass-card {{
        background: rgba(26, 28, 36, 0.6);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px; 
        padding: 15px; 
        margin-bottom: 15px;
    }}
    
    .terminal-card {{ background: #0a0b10; border: 1px solid #222; border-left: 3px solid {cor_neon}; border-radius: 8px; padding: 15px; font-family: monospace; color: {cor_neon}; }}
    .neon-text {{ color: {cor_neon}; font-weight: 900; font-size: 14px; letter-spacing: 1px; text-transform: uppercase; }}
    
    .stButton>button {{ 
        background: {grad} !important; color: white !important; font-weight: 900 !important; 
        border-radius: 8px !important; border: 1px solid {cor_neon} !important; 
        padding: 10px !important; width: 100%; transition: all 0.2s ease !important;
    }}
    .stButton>button:hover {{ background: {cor_neon} !important; color: #000 !important; }}
    
    .progress-bg {{ width: 100%; background: #222; border-radius: 10px; height: 6px; margin-bottom: 8px; overflow: hidden; }}
    .progress-fill-atk {{ height: 6px; background: linear-gradient(90deg, #ff0055, #ff5555); border-radius: 10px; }}
    .progress-fill-def {{ height: 6px; background: linear-gradient(90deg, #0055ff, #00aaff); border-radius: 10px; }}
    
    /* Ocultar barra de rolagem */
    ::-webkit-scrollbar {{ display: none; }}
    </style>
""", unsafe_allow_html=True)

# --- 5. TELA DE LOGIN ---
if not st.session_state.get('autenticado'):
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    with st.container():
        st.markdown(f"<div class='glass-card' style='text-align:center;'><h1 style='color:#fff; font-weight:900; margin-bottom:0;'>V8 <span style='color:{cor_neon};'>SUPREME</span></h1><p style='color:#888; font-size: 11px; letter-spacing:2px; margin-bottom: 30px;'>A.I. INTELLIGENCE HUB</p></div>", unsafe_allow_html=True)
        nome_in = st.text_input("Credencial de Acesso:", placeholder="Seu Nome")
        if st.button("INICIAR SESSÃO"):
            st.session_state['autenticado'] = True
            st.session_state['user_nome'] = nome_in if nome_in else "VIP"
            st.rerun()
    st.stop()

# --- 6. TOP BAR VIP ---
t_jogos = st.session_state.get('total_jogos', 1)
t_acertos = st.session_state.get('total_acertos', 0)
win_rate = (t_acertos / t_jogos) * 100 if t_jogos > 0 else 0
bancas_dict = st.session_state.get('bancas', {})
saldo_total = sum(bancas_dict.values())

html_topbar = (
    f"<div style='display:flex; justify-content:space-between; align-items:center; margin-bottom: 15px; padding: 15px; background: rgba(20,22,30,0.8); border-radius: 12px; border: 1px solid rgba(255,255,255,0.05);'>"
    f"<div style='display:flex; align-items:center;'>"
    f"<div style='font-size: 28px; margin-right: 12px;'>{st.session_state.get('avatar')}</div>"
    f"<div>"
    f"<div style='color:white; font-weight:900; font-size:16px;'>{str(st.session_state.get('user_nome')).upper()} <span style='background:{cor_neon}; color:black; font-size:9px; padding:2px 6px; border-radius:4px; font-weight:bold;'>PRO</span></div>"
    f"<div style='color:{cor_neon}; font-size:11px;'>{st.session_state.get('titulo_apostador')}</div>"
    f"</div></div>"
    f"<div style='text-align:right;'>"
    f"<div style='color:#888; font-size:10px; text-transform:uppercase;'>Saldo Total</div>"
    f"<div style='color:white; font-weight:900; font-size:18px;'>{fmt_moeda(saldo_total)}</div>"
    f"</div></div>"
)
st.markdown(html_topbar, unsafe_allow_html=True)

# --- 7. NAVEGAÇÃO PRINCIPAL ---
t1, t2, t3, t4, t5 = st.tabs(["📊 HOME", "🎯 RADAR", "🧾 OPERAÇÕES", "🛡️ SAFE", "⚙️ HUB"])

# ==========================================
# ABA 1: DASHBOARD
# ==========================================
with t1:
    if st.session_state.get('mod_grafico'):
        st.markdown(f"<div class='glass-card'><p style='color: #888; font-size: 11px; font-weight: bold; margin-bottom:5px;'>📈 RENDIMENTO</p></div>", unsafe_allow_html=True)
        st.line_chart(st.session_state.get('historico_banca', []), height=120, use_container_width=True)

    html_stats = (
        f"<div style='display: flex; gap: 10px; margin-bottom: 20px;'>"
        f"<div class='glass-card' style='flex:1; text-align:center; padding: 15px; margin:0;'>"
        f"<p style='color:#888; font-size:11px; margin:0;'>Win Rate</p>"
        f"<p style='color:white; font-size:22px; font-weight:900; margin:0;'>{win_rate:.1f}%</p>"
        f"</div>"
        f"<div class='glass-card' style='flex:1; text-align:center; padding: 15px; margin:0;'>"
        f"<p style='color:#888; font-size:11px; margin:0;'>Acertos</p>"
        f"<p style='color:{cor_neon}; font-size:22px; font-weight:900; margin:0;'>{t_acertos}</p>"
        f"</div></div>"
    )
    st.markdown(html_stats, unsafe_allow_html=True)

# ==========================================
# ABA 2: RADAR A.I E MERCADOS
# ==========================================
with t2:
    st.markdown("<h4 class='neon-text'>VARREDURA DO MERCADO</h4>", unsafe_allow_html=True)
    
    LIGAS = {"🇪🇺 Champions League": "soccer_uefa_champs_league", "🇬🇧 Premier League": "soccer_epl", "🇪🇸 La Liga": "soccer_spain_la_liga", "🇧🇷 Brasileirão": "soccer_brazil_campeonato"}
    
    col_f1, col_f2 = st.columns(2)
    with col_f1: liga_sel = st.selectbox("Liga:", list(LIGAS.keys()))
    with col_f2: merc_sel = st.selectbox("Mercado:", ["🤖 IA Decide", "🏆 Resultado Final", "⚽ Gols", "🔄 Ambas Marcam", "🚩 Escanteios", "🟨 Cartões"])

    if st.button("EXECUTAR SCANNER", use_container_width=True):
        with st.spinner("Buscando dados..."):
            dados = buscar_dados_api(LIGAS[liga_sel], st.session_state.get('api_key_odds')) 
            if not dados:
                dados = gerar_dados_mock()
                st.warning("⚠️ API indisponível. A exibir simulação global.")
            
            st.session_state['analisados'] = []
            for jogo in dados[:10]:
                c, f = jogo.get('home_team', 'Casa'), jogo.get('away_team', 'Fora')
                
                # Regras de mercado selecionado
                if merc_sel == "⚽ Gols": m = random.choice(["Over 1.5 Gols", "Over 2.5 Gols", "Under 3.5 Gols"])
                elif merc_sel == "🔄 Ambas Marcam": m = "Ambas Marcam: Sim"
                elif merc_sel == "🚩 Escanteios": m = random.choice(["Over 8.5 Cantos", "Over 9.5 Cantos"])
                elif merc_sel == "🟨 Cartões": m = random.choice(["Over 4.5 Cartões", "Over 5.5 Cartões"])
                elif merc_sel == "🏆 Resultado Final": m = random.choice([f"Vitória {c}", f"Vitória {f}", "Empate"])
                else: m = random.choice([f"Vitória {c}", "Ambas Marcam: Sim", "Over 1.5 Gols"])
                
                odd = round(random.uniform(1.3, 2.5), 2)
                atk, dfs = calcular_forca_equipa(c)
                st.session_state['analisados'].append({"jogo": f"{c} x {f}", "casa": c, "fora": f, "m": m, "o": odd, "conf": random.randint(85, 99), "atk": atk, "def": dfs})

    with st.expander("✍️ Modo Manual (Sua Grade)"):
        grade = st.text_area("Input de Jogos (Ex: Flamengo x Vasco):", label_visibility="collapsed")
        if st.button("Forçar Análise Manual"):
            if grade:
                st.session_state['analisados'] = []
                for j in [x for x in grade.split('\n') if 'x' in x.lower()]:
                    c, f = j.lower().split('x')[0].strip().title(), j.lower().split('x')[1].strip().title()
                    atk, dfs = calcular_forca_equipa(c)
                    
                    if merc_sel == "⚽ Gols": m = "Over 1.5 Gols"
                    elif merc_sel == "🔄 Ambas Marcam": m = "Ambas Marcam: Sim"
                    elif merc_sel == "🚩 Escanteios": m = "Over 8.5 Cantos"
                    elif merc_sel == "🟨 Cartões": m = "Over 4.5 Cartões"
                    elif merc_sel == "🏆 Resultado Final": m = f"Vitória {c}"
                    else: m = "Aposta Sugerida"
                    
                    st.session_state['analisados'].append({"jogo": f"{c} x {f}", "casa": c, "fora": f, "m": m, "o": round(random.uniform(1.4, 2.1),2), "conf": random.randint(88, 99), "atk": atk, "def": dfs})
                st.rerun()

    if st.session_state.get('analisados'):
        st.markdown("<hr style='border-color: rgba(255,255,255,0.1);'>", unsafe_allow_html=True)
        for idx, item in enumerate(st.session_state.get('analisados')):
            # String concatenada para evitar 100% o bug do Markdown
            html_card = (
                f"<div class='glass-card'>"
                f"<div style='display:flex; justify-content:space-between; align-items:center;'>"
                f"<div style='font-size:14px; font-weight:900;'>{item['casa']} <span style='color:#555; font-size:10px;'>VS</span> {item['fora']}</div>"
                f"<div style='color:{cor_neon}; font-weight:900; font-size:16px;'>@{item['o']:.2f}</div>"
                f"</div>"
                f"<div style='margin-top:15px; font-size:10px; color:#888;'>PRESSÃO OFENSIVA ({item['atk']}%)</div>"
                f"<div class='progress-bg'><div class='progress-fill-atk' style='width:{item['atk']}%;'></div></div>"
                f"<div style='margin-top:5px; font-size:10px; color:#888;'>MURALHA DEFENSIVA ({item['def']}%)</div>"
                f"<div class='progress-bg'><div class='progress-fill-def' style='width:{item['def']}%;'></div></div>"
                f"<div style='margin-top:15px; background:rgba(0,0,0,0.4); padding:10px; border-radius:8px;'>"
                f"<span style='font-size:11px; color:#aaa;'>ALGORITMO V8:</span> <b style='color:white;'>{item['m']}</b><br>"
                f"<span style='font-size:11px; color:#aaa;'>CONFIANÇA:</span> <b style='color:{cor_neon};'>{item['conf']}%</b>"
                f"</div></div>"
            )
            st.markdown(html_card, unsafe_allow_html=True)
            
            c_add1, c_add2 = st.columns(2)
            with c_add1:
                if st.button("➕ BILHETE", key=f"m_{idx}"):
                    st.session_state['bilhete'].append(item)
                    st.toast("✅ Adicionado!")
            with c_add2:
                if st.button("💾 SALVAR DICA", key=f"s_{idx}"):
                    st.session_state['analises_salvas'].append(item)
                    st.toast("💾 Salvo no Tracking!")

# ==========================================
# ABA 3: OPERAÇÕES (MÚLTIPLA E TRACKING)
# ==========================================
with t3:
    st.markdown("<h4 class='neon-text'>CARRINHO MÚLTIPLO</h4>", unsafe_allow_html=True)
    if st.session_state.get('bilhete'):
        odd_f = 1.0
        html_b = "<div class='glass-card' style='padding: 15px;'>"
        for b in st.session_state.get('bilhete'):
            odd_f *= b['o']
            html_b += f"<p style='margin:0; font-size:14px; border-bottom: 1px solid rgba(255,255,255,0.1); padding: 5px 0;'>✅ <b>{b['jogo']}</b> <span style='float:right; color:{cor_neon}; font-weight:bold;'>@{b['o']:.2f}</span><br><span style='font-size:11px; color:#aaa;'>Mercado: {b['m']}</span></p>"
        html_b += "</div>"
        st.markdown(html_b, unsafe_allow_html=True)
        
        st.markdown(f"<h2 style='text-align:center; font-weight:900; font-size:36px; color:white;'>ODD <span style='color:{cor_neon};'>@{odd_f:.2f}</span></h2>", unsafe_allow_html=True)
        
        bancas_atuais = st.session_state.get('bancas', {})
        banca_escolhida = st.selectbox("Conta Origem:", list(bancas_atuais.keys()))
        banca_disp = bancas_atuais[banca_escolhida]
        rec_stake = banca_disp * (0.03 if odd_f < 2.5 else 0.01)

        st.markdown(f"<div class='terminal-card' style='margin-bottom:20px;'>> SALDO: {fmt_moeda(banca_disp)}<br>> GESTÃO IDEAL: <span style='color:{cor_neon}; font-size:16px;'>{fmt_moeda(rec_stake)}</span></div>", unsafe_allow_html=True)
        
        valor = st.number_input("Entrada (Múltipla):", min_value=1.0, value=float(max(1.0, rec_stake)), step=5.0)
        
        c1, c2 = st.columns(2)
        with c1:
            if st.button("✅ BATER GREEN"):
                st.session_state['bancas'][banca_escolhida] += (valor * odd_f)
                st.session_state['historico_banca'].append(sum(st.session_state['bancas'].values()))
                st.session_state['bilhete'] = []
                tocar_som()
                time.sleep(1); st.rerun()
        with c2:
            if st.button("❌ RED / CANCELAR"):
                st.session_state['bancas'][banca_escolhida] -= valor
                st.session_state['historico_banca'].append(sum(st.session_state['bancas'].values()))
                st.session_state['bilhete'] = []
                st.rerun()
    else:
        st.info("Múltipla vazia.")

    st.markdown("<h4 class='neon-text' style='margin-top: 40px;'>📂 TRACKING INDIVIDUAL</h4>", unsafe_allow_html=True)
    if st.session_state.get('analises_salvas'):
        for i, a in enumerate(st.session_state.get('analises_salvas')):
            html_t = f"<div class='glass-card' style='padding: 10px 15px; margin-bottom: 5px; border-left: 3px solid #00e5ff;'><div style='font-size:13px; font-weight:bold; color:white;'>{a['jogo']}</div><div style='display:flex; justify-content:space-between; margin-top:2px;'><span style='color:#888; font-size:11px;'>Call: <b style='color:white;'>{a['m']}</b></span><span style='color:{cor_neon}; font-weight:bold; font-size:12px;'>@{a['o']:.2f}</span></div></div>"
            st.markdown(html_t, unsafe_allow_html=True)
            c_g, c_r, c_d = st.columns([0.4, 0.4, 0.2])
            with c_g:
                if st.button("✅ WIN", key=f"tw_{i}"):
                    st.session_state['total_jogos'] += 1; st.session_state['total_acertos'] += 1
                    st.session_state['analises_salvas'].pop(i); tocar_som(); time.sleep(1); st.rerun()
            with c_r:
                if st.button("❌ LOSS", key=f"tl_{i}"):
                    st.session_state['total_jogos'] += 1; st.session_state['analises_salvas'].pop(i); st.rerun()
            with c_d:
                if st.button("🗑️", key=f"td_{i}"):
                    st.session_state['analises_salvas'].pop(i); st.rerun()
    else:
        st.caption("Nenhuma análise salva.")

# ==========================================
# ABA 4: SAFE BINGO
# ==========================================
with t4:
    st.markdown("<h4 class='neon-text'>HIGH EV ZONE (SAFE)</h4>", unsafe_allow_html=True)
    if not st.session_state.get('analisados'): 
        st.info("⚠️ Faça uma Varredura no Radar ou use o Override Manual primeiro.")
    else:
        seguros = sorted([j for j in st.session_state.get('analisados') if 1.15 <= j.get('o', 1.5) <= 1.65], key=lambda x: x.get('conf', 0), reverse=True)
        if len(seguros) >= 2:
            s1, s2 = seguros[0], seguros[1]
            odd_s = s1['o'] * s2['o']
            html_s = (
                f"<div class='glass-card' style='border: 1px solid {cor_neon};'>"
                f"<div style='text-align:center; margin-bottom: 15px;'><span style='background:{cor_neon}; color:#000; padding:5px 15px; border-radius:20px; font-weight:bold; font-size:12px;'>🏆 DUPLA DE OURO</span></div>"
                f"<div style='border-left: 4px solid {cor_neon}; padding-left: 10px; margin-bottom: 10px;'><div style='color:white; font-weight:bold; font-size: 14px;'>⚽ {s1['jogo']}</div><div style='color:#888; font-size: 12px;'>🎯 {s1['m']} | <span style='color:{cor_neon}; font-weight:bold;'>@{s1['o']:.2f}</span></div></div>"
                f"<div style='border-left: 4px solid {cor_neon}; padding-left: 10px; margin-bottom: 15px;'><div style='color:white; font-weight:bold; font-size: 14px;'>⚽ {s2['jogo']}</div><div style='color:#888; font-size: 12px;'>🎯 {s2['m']} | <span style='color:{cor_neon}; font-weight:bold;'>@{s2['o']:.2f}</span></div></div>"
                f"<hr style='border-color: rgba(255,255,255,0.1);'><h3 style='text-align:center; color:{cor_neon};'>📊 ODD FINAL: {odd_s:.2f}</h3></div>"
            )
            st.markdown(html_s, unsafe_allow_html=True)
            if st.button("🔥 COPIAR PARA OPERAÇÕES"): 
                st.session_state['bilhete'].extend([s1, s2]); st.toast("✅ Copiado!"); tocar_som()
        else: st.warning("Sem jogos com perfil Safe (Odds 1.15 - 1.65).")

# ==========================================
# ABA 5: HUB VIP
# ==========================================
with t5:
    st.markdown(f"<h3 style='color:white; text-align:center; font-weight:900;'>V8 <span style='color:{cor_neon};'>HUB</span></h3>", unsafe_allow_html=True)

    with st.expander("🔑 Chave de API de Dados"):
        st.markdown("<span style='font-size:11px; color:#aaa;'>Crie uma chave grátis em the-odds-api.com e cole aqui para jogos reais.</span>", unsafe_allow_html=True)
        nova_api = st.text_input("API Key:", value=st.session_state.get('api_key_odds'), type="password")
        if st.button("Salvar Chave"): st.session_state['api_key_odds'] = nova_api; st.success("Salva!")

    with st.expander("🏛️ GESTÃO DE BANCAS"):
        st.session_state['bancas']["Betano"] = st.number_input("Betano", value=st.session_state.get('bancas')["Betano"], step=50.0)
        st.session_state['bancas']["Bet365"] = st.number_input("Bet365", value=st.session_state.get('bancas')["Bet365"], step=50.0)

    with st.expander("⚙️ CUSTOMIZAÇÃO"):
        st.selectbox("Tema do App:", ["🟢 Verde Hacker", "🟡 Ouro Milionário", "🔵 Azul Cyberpunk", "🔴 Vermelho Kamikaze", "🟣 Rosa Choque"], key="tema_escolhido")
        st.selectbox("Moeda:", ["R$", "US$", "€", "₿"], key="moeda")

    if st.button("ENCERRAR SESSÃO", type="primary", use_container_width=True):
        st.session_state['autenticado'] = False; st.rerun()
