import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# --- 1. CONFIGURAÇÃO (Modo Wide para PC) ---
st.set_page_config(page_title="PATOTA AJAX BADENBALL", page_icon="⚽", layout="wide")

# --- 2. CSS "CYBERPUNK" (Visual Dark e Neon) ---
st.markdown("""
    <style>
    .stApp { background-color: #000000; }
    h1, h2, h3, h4, h5 { font-family: 'Helvetica', sans-serif; color: #ffffff; }
    
    /* KPI CARDS (Placares) */
    .kpi-container {
        background: linear-gradient(180deg, #1a1a1a 0%, #000000 100%);
        border: 1px solid #333;
        border-top: 4px solid #00d4ff; /* Azul Neon */
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 0 15px rgba(0, 212, 255, 0.2);
        margin-bottom: 20px;
    }
    .kpi-label { color: #888; font-size: 14px; text-transform: uppercase; margin-bottom: 5px; }
    .kpi-value { color: #ffffff; font-weight: 900; font-size: 40px; }

    /* CARD DE JOGADOR (Mural) */
    .player-card {
        background-color: #121212;
        border: 1px solid #8a2be2; /* Roxo */
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 10px;
        text-align: center;
    }
    .player-name { color: #ffffff; font-weight: bold; font-size: 18px; }
    .player-desc { color: #888; font-size: 12px; margin-bottom: 5px; }
    .player-debt { color: #ff4444; font-weight: 900; font-size: 22px; }

    /* MOBILE: Aumenta fontes no celular */
    @media (max-width: 768px) {
        .kpi-value { font-size: 50px !important; }
        .stImage > img { width: 100% !important; max-width: 300px !important; }
    }
    </style>
""", unsafe_allow_html=True)

# --- 3. DADOS E FUNÇÕES ---
def limpar_moeda(valor):
    if isinstance(valor, str):
        limpo = valor.replace('R$', '').replace(' ', '').replace('.', '').replace(',', '.')
        try: return float(limpo)
        except: return 0.0
    return valor

@st.cache_data(ttl=60)
def carregar_dados():
    # Seus links do Google Sheets
    url_fluxo = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTp9Eoyr5oJkOhw-7GElhvo2p8h73J_kbsee2JjUDjPNO18Lv7pv5oU3w7SC9d_II2WVRB_E4TUd1XK/pub?gid=1108345129&single=true&output=csv"
    url_parametros = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTp9Eoyr5oJkOhw-7GElhvo2p8h73J_kbsee2JjUDjPNO18Lv7pv5oU3w7SC9d_II2WVRB_E4TUd1XK/pub?gid=972176032&single=true&output=csv"
    
    try:
        df_fluxo = pd.read_csv(url_fluxo)
        df_parametros = pd.read_csv(url_parametros)
        
        # Limpeza de dados
        if df_fluxo['Valor'].dtype == 'object': 
            df_fluxo['Valor'] = df_fluxo['Valor'].apply(limpar_moeda)
        if df_parametros['Valor'].dtype == 'object': 
            df_parametros['Valor'] = df_parametros['Valor'].apply(limpar_moeda)
            
        return df_fluxo, df_parametros
    except: return None, None

df_fluxo, df_parametros = carregar_dados()

if df_fluxo is None:
    st.error("⚠️ Erro ao conectar com a planilha. Verifique os links.")
    st.stop()

# Cálculos
saldo_atual = df_fluxo[df_fluxo['Status'] == 'Pago']['Valor'].sum()
pendencias = df_fluxo[(df_fluxo['Status'] == 'Pendente') & (df_fluxo['Tipo'] == 'Entrada')]
total_pendente = pendencias['Valor'].sum()

try:
    meta_reserva = df_parametros[df_parametros['Parametro'] == 'Meta_Reserva']['Valor'].values[0]
    progresso_meta = min(int((saldo_atual / meta_reserva) * 100), 100)
except: 
    meta_reserva = 800
    progresso_meta = 0

# --- 4. HEADER (LOGO) ---
col_L, col_C, col_R = st.columns([1, 2, 1])
with col_C:
    try:
        # Tenta carregar a logo. Se falhar, mostra texto.
        st.image("logo.png", width=350) 
    except:
        st.markdown("<h1 style='text-align:center'>⚽ AJAX BADENBALL</h1>", unsafe_allow_html=True)

st.markdown("<h5 style='text-align: center; color: #8a2be2;'>QUINTAS-FEIRAS | 18:30</h5>", unsafe_allow_html=True)
st.markdown("---")

# --- 5. PLACAR (KPIs) ---
c1, c2, c3 = st.columns(3)

with c1:
    st.markdown(f"""
        <div class="kpi-container">
            <div class="kpi-label">SALDO EM CAIXA</div>
            <div class="kpi-value" style="color: #00d4ff;">R$ {saldo_atual:,.0f}</div>
        </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown(f"""
        <div class="kpi-container" style="border-top-color: #ff4444;">
            <div class="kpi-label">TOTAL PENDENTE</div>
            <div class="kpi-value" style="color: #ff4444;">R$ {total_pendente:,.0f}</div>
        </div>
    """, unsafe_allow_html=True)

with c3:
    cor_meta = "#00ff00" if progresso_meta >= 100 else "#e0e0e0"
    st.markdown(f"""
        <div class="kpi-container" style="border-top-color: #8a2be2;">
            <div class="kpi-label">META DA RESERVA</div>
            <div class="kpi-value" style="color: {cor_meta};">{progresso_meta}%</div>
        </div>
    """, unsafe_allow_html=True)

# --- 6. MURAL DE PENDÊNCIAS (CORRIGIDO) ---
st.markdown("<h3 style='color: #8a2be2 !important;'>📋 PENDÊNCIAS</h3>", unsafe_allow_html=True)

if not pendencias.empty:
    # Reiniciamos o índice para garantir que o loop funcione (0, 1, 2...)
    pendencias = pendencias.reset_index(drop=True)
    
    # Criamos as 3 colunas FORA do loop (Isso corrige o erro!)
    cols = st.columns(3)
    
    for index, row in pendencias.iterrows():
        # Distribui: Card 0 na Col 0, Card 1 na Col 1, Card 2 na Col 2, Card 3 na Col 0...
        col_atual = cols[index % 3]
        
        with col_atual:
            st.markdown(f"""
            <div class="player-card">
                <div class="player-name">{row['Nome']}</div>
                <div class="player-desc">{row['Categoria']} • {row['Mes_Ref']}</div>
                <div class="player-debt">R$ {row['Valor']:.0f}</div>
            </div>
            """, unsafe_allow_html=True)
else:
    st.success("✅ Ninguém devendo! O time está de parabéns.")

st.markdown("---")

# --- 7. GRÁFICOS ---
g1, g2 = st.columns(2)

with g1:
    st.markdown("#### RECEITA POR TIPO")
    # Filtra só o que é entrada para não mostrar gráfico vazio
    entradas = df_fluxo[df_fluxo['Tipo'] == 'Entrada']
    if not entradas.empty:
        fig_pizza = px.pie(entradas, values='Valor', names='Categoria', hole=0.5,
                           color_discrete_sequence=['#00d4ff', '#8a2be2', '#ffffff'])
        fig_pizza.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="#fff")
        st.plotly_chart(fig_pizza, use_container_width=True)

with g2:
    st.markdown("#### CAIXA MENSAL")
    df_mensal = df_fluxo.groupby('Mes_Ref')['Valor'].sum().reset_index()
    if not df_mensal.empty:
        fig_barras = px.bar(df_mensal, x='Mes_Ref', y='Valor', text_auto=True)
        fig_barras.update_traces(marker_color='#8a2be2', marker_line_color='#00d4ff', marker_line_width=2)
        fig_barras.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="#fff")
        st.plotly_chart(fig_barras, use_container_width=True)
