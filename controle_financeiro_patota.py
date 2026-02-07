import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="PATOTA AJAX BADENBALL", page_icon="⚽", layout="wide")

# --- 2. ESTILOS CSS (Blindado) ---
st.markdown("""
    <style>
    /* Fundo preto */
    .stApp { background-color: #000000; }
    
    /* Fontes */
    h1, h2, h3, h4, h5, p, span { font-family: 'Helvetica', sans-serif; color: #ffffff; }
    
    /* Caixas dos KPIs (Placar) */
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

    /* Cards dos Jogadores */
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

    /* Ajustes para Celular */
    @media (max-width: 768px) {
        .kpi-value { font-size: 50px !important; }
        .stImage { margin: 0 auto; }
    }
    </style>
""", unsafe_allow_html=True)

# --- 3. FUNÇÕES DE DADOS ---
def limpar_moeda(valor):
    if isinstance(valor, str):
        limpo = valor.replace('R$', '').replace(' ', '').replace('.', '').replace(',', '.')
        try: return float(limpo)
        except: return 0.0
    return valor

@st.cache_data(ttl=60)
def carregar_dados():
    # Links das planilhas
    link_fluxo = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTp9Eoyr5oJkOhw-7GElhvo2p8h73J_kbsee2JjUDjPNO18Lv7pv5oU3w7SC9d_II2WVRB_E4TUd1XK/pub?gid=1108345129&single=true&output=csv"
    link_param = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTp9Eoyr5oJkOhw-7GElhvo2p8h73J_kbsee2JjUDjPNO18Lv7pv5oU3w7SC9d_II2WVRB_E4TUd1XK/pub?gid=972176032&single=true&output=csv"
    
    try:
        df_fluxo = pd.read_csv(link_fluxo)
        df_parametros = pd.read_csv(link_param)
        
        # Limpeza
        if df_fluxo['Valor'].dtype == 'object':
            df_fluxo['Valor'] = df_fluxo['Valor'].apply(limpar_moeda)
        if df_parametros['Valor'].dtype == 'object':
            df_parametros['Valor'] = df_parametros['Valor'].apply(limpar_moeda)
            
        return df_fluxo, df_parametros
    except:
        return None, None

# Carrega os dados
df_fluxo, df_parametros = carregar_dados()

# Verifica se carregou
if df_fluxo is None:
    st.error("Erro ao carregar dados. Verifique a internet ou os links.")
    st.stop()

# --- 4. CÁLCULOS ---
saldo_atual = df_fluxo[df_fluxo['Status'] == 'Pago']['Valor'].sum()
pendencias = df_fluxo[(df_fluxo['Status'] == 'Pendente') & (df_fluxo['Tipo'] == 'Entrada')]
total_pendente = pendencias['Valor'].sum()

try:
    meta_val = df_parametros[df_parametros['Parametro'] == 'Meta_Reserva']['Valor'].values[0]
    progresso_meta = min(int((saldo_atual / meta_val) * 100), 100)
except:
    meta_val = 800
    progresso_meta = 0

# --- 5. CABEÇALHO (LOGO ESQUERDA) ---
col_logo, col_texto = st.columns([1, 4])

with col_logo:
    try:
        st.image("logo.png", width=150)
    except:
        st.header("⚽")

with col_texto:
    # Usando HTML puro para garantir alinhamento
    st.markdown("""
    <div style="text-align: left; padding-top: 10px;">
        <h1 style="margin:0; padding:0; font-size: 40px;">AJAX BADENBALL</h1>
        <h5 style="color: #8a2be2; margin:0;">QUINTAS-FEIRAS | 18:30</h5>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# --- 6. PLACAR (KPIs) ---
c1, c2, c3 = st.columns(3)

with c1:
    # HTML separado para evitar erros de sintaxe
    html_c1 = f"""
    <div class="kpi-container">
        <div class="kpi-label">SALDO EM CAIXA</div>
        <div class="kpi-value" style="color: #00d4ff;">R$ {saldo_atual:,.0f}</div>
    </div>
    """
    st.markdown(html_c1, unsafe_allow_html=True)

with c2:
    html_c2 = f"""
    <div class="kpi-container" style="border-top-color: #ff4444;">
        <div class="kpi-label">TOTAL PENDENTE</div>
        <div class="kpi-value" style="color: #ff4444;">R$ {total_pendente:,.0f}</div>
    </div>
    """
    st.markdown(html_c2, unsafe_allow_html=True)

with c3:
    cor = "#00ff00" if progresso_meta >= 100 else "#e0e0e0"
    html_c3 = f"""
    <div class="kpi-container" style="border-top-color: #8a2be2;">
        <div class="kpi-label">META DA RESERVA</div>
        <div class="kpi-value" style="color: {cor};">{progresso_meta}%</div>
    </div>
    """
    st.markdown(html_c3, unsafe_allow_html=True)

# --- 7. MURAL DE PENDÊNCIAS ---
st.markdown("<h3 style='color: #8a2be2;'>📋 PENDÊNCIAS</h3>", unsafe_allow_html=True)

if not pendencias.empty:
    pendencias = pendencias.reset_index(drop=True)
    cols = st.columns(3)
    
    for i, row in pendencias.iterrows():
        # HTML seguro com aspas triplas
        card_html = f"""
        <div class="player-card">
            <div class="player-name">{row['Nome']}</div>
            <div class="player-desc">{row['Categoria']} • {row['Mes_Ref']}</div>
            <div class="player-debt">R$ {row['Valor']:.0f}</div>
        </div>
        """
        # Renderiza na coluna correta
        with cols[i % 3]:
            st.markdown(card_html, unsafe_allow_html=True)
else:
    st.success("✅ Ninguém devendo!")

st.markdown("---")

# --- 8. GRÁFICOS ---
g1, g2 = st.columns(2)

with g1:
    st.markdown("#### RECEITA POR TIPO")
    entradas = df_fluxo[df_fluxo['Tipo'] == 'Entrada']
    if not entradas.empty:
        fig = px.pie(
            entradas, 
            values='Valor', 
            names='Categoria', 
            hole=0.5,
            color_discrete_sequence=['#00d4ff', '#8a2be2', '#ffffff']
        )
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font_color="#fff"
        )
        st.plotly_chart(fig, use_container_width=True)

with g2:
    st.markdown("#### CAIXA MENSAL")
    df_mensal = df_fluxo.groupby('Mes_Ref')['Valor'].sum().reset_index()
    if not df_mensal.empty:
        fig = px.bar(df_mensal, x='Mes_Ref', y='Valor', text_auto=True)
        # Atenção aqui: parênteses fechados corretamente
        fig.update_traces(
            marker_color='#8a2be2',
            marker_line_color='#00d4ff',
            marker_line_width=2
        )
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font_color="#fff"
        )
        st.plotly_chart(fig, use_container_width=True)
