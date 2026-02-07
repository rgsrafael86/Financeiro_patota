import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# --- 1. CONFIGURAÇÃO DA PÁGINA (WIDESCREEN) ---
st.set_page_config(page_title="PATOTA AJAX BADENBALL", page_icon="⚽", layout="wide")

# --- 2. CSS AVANÇADO (RESPONSIVIDADE E TEMA DARK) ---
st.markdown("""
    <style>
    /* Fundo Geral */
    .stApp {
        background-color: #050505; /* Preto quase absoluto */
    }

    /* Títulos */
    h1, h2, h3 {
        color: #FFFFFF !important;
        font-family: 'Arial Black', sans-serif;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    /* KPI BOXES (Os Cartões com Números) */
    .kpi-card {
        background: linear-gradient(135deg, #2b004a 0%, #000000 100%); /* Roxo escuro para preto */
        border-left: 5px solid #00d4ff; /* Azul Neon na borda */
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 15px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    }
    
    .kpi-label {
        font-size: 1.2rem;
        color: #b3b3b3;
        font-weight: 600;
        margin-bottom: 5px;
    }
    
    .kpi-value {
        font-size: 3rem; /* FONTE GIGANTE PARA CELULAR */
        font-weight: 800;
        color: #ffffff;
        line-height: 1.1;
    }

    /* Cards de Devedores (Mural) */
    .debtor-card {
        background-color: #111;
        border: 1px solid #333;
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 10px;
        text-align: center;
    }
    .debtor-name { color: #00d4ff; font-weight: bold; font-size: 1.1rem; }
    .debtor-value { color: #ff4b4b; font-weight: bold; font-size: 1.3rem; margin-top: 5px;}
    
    /* Centralizar Logo */
    .logo-container {
        display: flex;
        justify_content: center;
        margin-bottom: 20px;
    }
    
    /* Ajuste para mobile (sobrescreve se a tela for pequena) */
    @media (max-width: 640px) {
        .kpi-value { font-size: 2.5rem; } /* Levemente menor no celular para não quebrar */
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. FUNÇÕES E DADOS ---
def limpar_moeda(valor):
    if isinstance(valor, str):
        limpo = valor.replace('R$', '').replace(' ', '').replace('.', '').replace(',', '.')
        try: return float(limpo)
        except: return 0.0
    return valor

@st.cache_data(ttl=60)
def carregar_dados():
    # Links fornecidos
    url_fluxo = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTp9Eoyr5oJkOhw-7GElhvo2p8h73J_kbsee2JjUDjPNO18Lv7pv5oU3w7SC9d_II2WVRB_E4TUd1XK/pub?gid=1108345129&single=true&output=csv"
    url_parametros = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTp9Eoyr5oJkOhw-7GElhvo2p8h73J_kbsee2JjUDjPNO18Lv7pv5oU3w7SC9d_II2WVRB_E4TUd1XK/pub?gid=972176032&single=true&output=csv"
    
    try:
        df_fluxo = pd.read_csv(url_fluxo)
        df_parametros = pd.read_csv(url_parametros)
        
        # Limpeza
        if df_fluxo['Valor'].dtype == 'object': df_fluxo['Valor'] = df_fluxo['Valor'].apply(limpar_moeda)
        if df_parametros['Valor'].dtype == 'object': df_parametros['Valor'] = df_parametros['Valor'].apply(limpar_moeda)
        
        return df_fluxo, df_parametros
    except Exception as e:
        return None, None

df_fluxo, df_parametros = carregar_dados()

if df_fluxo is None:
    st.error("Erro ao carregar planilha. Verifique a conexão.")
    st.stop()

# --- 4. CÁLCULOS ---
saldo_atual = df_fluxo[df_fluxo['Status'] == 'Pago']['Valor'].sum()
pendencias = df_fluxo[(df_fluxo['Status'] == 'Pendente') & (df_fluxo['Tipo'] == 'Entrada')]
total_pendente = pendencias['Valor'].sum()

try:
    meta_reserva = df_parametros[df_parametros['Parametro'] == 'Meta_Reserva']['Valor'].values[0]
    progresso_meta = min(int((saldo_atual / meta_reserva) * 100), 100)
except:
    meta_reserva = 800
    progresso_meta = 0

# --- 5. INTERFACE DO USUÁRIO ---

# --- Header com Logo Grande ---
col_L, col_C, col_R = st.columns([1, 2, 1])
with col_C:
    # Aumentei para 300px e usei coluna central para forçar o meio da tela
    try:
        st.image("logo.png", width=350) 
    except:
        st.markdown("<h1 style='text-align:center'>⚽</h1>", unsafe_allow_html=True)

st.markdown(f"<h3 style='text-
