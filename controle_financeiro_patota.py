import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# --- 1. CONFIGURAÇÃO ---
st.set_page_config(page_title="PATOTA AJAX BADENBALL", page_icon="⚽", layout="wide")

# --- 2. CSS "CYBERPUNK" (Ajustado para Header Esquerdo) ---
st.markdown("""
    <style>
    .stApp { background-color: #000000; }
    h1, h2, h3, h4, h5 { font-family: 'Helvetica', sans-serif; color: #ffffff; }
    
    /* KPI CARDS */
    .kpi-container {
        background: linear-gradient(180deg, #1a1a1a 0%, #000000 100%);
        border: 1px solid #333;
        border-top: 4px solid #00d4ff;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 0 15px rgba(0, 212, 255, 0.2);
        margin-bottom: 20px;
    }
    .kpi-label { color: #888; font-size: 14px; text-transform: uppercase; margin-bottom: 5px; }
    .kpi-value { color: #ffffff; font-weight: 900; font-size: 40px; }

    /* PLAYER CARD */
    .player-card {
        background-color: #121212;
        border: 1px solid #8a2be2;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 10px;
        text-align: center;
    }
    .player-name { color: #ffffff; font-weight: bold; font-size: 18px; }
    .player-desc { color: #888; font-size: 12px; margin-bottom: 5px; }
    .player-debt { color: #ff4444; font-weight: 900; font-size: 22px; }

    /* MOBILE ADJUSTMENTS */
    @media (max-width: 768px) {
        .kpi-value { font-size: 50px !important; }
        /* No celular, centraliza o header para não ficar estranho */
        .header-text { text-align: center !important; }
        .stImage { margin: 0 auto; }
    }
    </style>
""", unsafe_allow_html=True)

# --- 3. DADOS ---
def limpar_moeda(valor):
    if isinstance(valor, str):
        limpo = valor.replace('R$', '').replace(' ', '').replace('.', '').replace(',', '.')
        try: return float(limpo)
        except: return 0.0
    return valor

@st.cache_data(ttl=60)
def carregar_dados():
    url_fluxo = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTp9Eoyr5oJkOhw-7GElhvo2p8h73J_kbsee2JjUDjPNO18Lv7pv5oU3w7SC9d_II2WVRB_E4TUd1XK/pub?gid=1108345129&single=true&output=csv"
    url_parametros = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTp9Eoyr5oJkOhw-7GElhvo2p8h73J_kbsee2JjUDjPNO18Lv7pv5oU3w7SC9d_II2WVRB_E4TUd1XK/pub?gid=972176032&single=true&output=csv"
    try:
        df_fluxo = pd.read_csv(url_fluxo)
        df_parametros = pd.read_csv(url_parametros)
        if df_fluxo['Valor'].dtype == 'object': df_fluxo['Valor'] = df_fluxo['Valor'].apply(limpar_moeda)
        if df_parametros['Valor'].dtype == 'object': df_parametros['Valor'] = df_parametros['Valor'].apply(limpar_moeda)
        return df_fluxo, df_parametros
    except: return None, None

df_fluxo, df_parametros = carregar_dados()
if df_fluxo is None: st.stop()

# Cálculos
saldo_atual = df_fluxo[df_fluxo['Status'] == 'Pago']['Valor'].sum()
pendencias = df_fluxo[(df_fluxo['Status'] == 'Pendente') & (df_fluxo['Tipo'] == 'Entrada')]
total_pendente = pendencias['Valor'].sum()
try:
    meta_reserva = df_parametros[df_parametros['Parametro'] == 'Meta_Reserva']['Valor'].values[0]
    progresso_meta = min(int((saldo_atual / meta_reserva) * 100), 100)
except: meta_reserva = 800; progresso_meta = 0

# --- 4. HEADER NOVO (LOGO ESQUERDA + TEXTO DIREITA) ---
# Cria duas colunas: Coluna 1 (Pequena) para logo, Coluna 2 (Grande) para texto
col_logo, col_texto = st.columns([1, 4])

with col_logo:
    try:
        # width=150 garante que não fique gigante, mas visível à esquerda
        st.image("logo.png", width=150) 
    except:
        st.markdown("⚽")

with col_texto:
    # Título sempre visível agora, alinhado à esquerda
    st.markdown("<h1 style='text-align: left; margin-bottom: 0px; margin-top: 10px;'>AJAX BADENBALL</h1>", unsafe_allow_html=True)
    st.markdown("<h5 style='text-align: left; color: #8a2be2; margin-top: 0px;'>QUINTAS-FEIRAS | 18:30</h5>", unsafe_allow_html=True)

st.markdown("---")

# --- 5. PLACAR ---
c1, c2, c3 = st.columns(3)
with c1:
    st.markdown(f"""<div class="kpi-container"><div class="kpi-label">SALDO EM CAIXA</div><div class="kpi-value" style="color: #00d4ff;">R$ {saldo_atual:,.0f}</div></div>""", unsafe_allow_html=True)
with c2:
    st.markdown(f"""<div class="kpi-container" style="border-top-color: #ff4444;"><div class="kpi-label">TOTAL PENDENTE</div><div class="kpi-value" style="color: #ff4444;">R$ {total_pendente:,.0f}</div></div>""", unsafe_allow_html=True)
with c3:
    cor_meta = "#00ff00" if progresso_meta >= 100 else "#e0e0e0"
    st.markdown(f"""<div class="kpi-container" style="border-top-color: #8a2be2;"><div class="kpi-label">META DA RESERVA</div><div class="kpi-value" style="color: {cor_meta};">{progresso_meta}%</div></div>""", unsafe_allow_html=True)

# --- 6. MURAL ---
st.markdown("<h3 style='color: #8a2be2 !important;'>📋 PENDÊNCIAS</h3>", unsafe_allow_html=True)
if not pendencias.empty:
    pendencias = pendencias.reset_index(drop=True)
    cols = st.columns(3)
    for index, row in pendencias.iterrows():
        with cols[index % 3]:
            st.markdown(f"""<div class="player-card"><div class="player-name">{row['Nome']}</div><div class="player-desc">{row['Categoria']} • {row['Mes_Ref']}</div><div class="player-debt">R$ {row['Valor']:.0f}</div></div>""", unsafe_allow_html=True)
else:
    st.success("✅ Ninguém devendo!")

st.markdown("---")

# --- 7. GRÁFICOS ---
g1, g2 = st.columns(2)
with g1:
    st.markdown("#### RECEITA POR TIPO")
    entradas = df_fluxo[df_fluxo['Tipo'] == 'Entrada']
    if not entradas.empty:
        fig = px.pie(entradas, values='Valor', names='Categoria', hole=0.5, color_discrete_sequence=['#00d4ff', '#8a2be2', '#ffffff'])
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="#fff")
        st.plotly_chart(fig, use_container_width=True)
with g2:
    st.markdown("#### CAIXA MENSAL")
    df_mensal = df_fluxo.groupby('Mes_Ref')['Valor'].sum().reset_index()
    if not df_mensal.empty:
        fig = px.bar(df_mensal, x='Mes_Ref', y='Valor', text_auto=True)
        fig.update_traces(marker_color='#8a2be2', marker_line_color
