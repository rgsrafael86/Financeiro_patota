import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np

# --- 1. CONFIGURAÇÃO ---
st.set_page_config(page_title="PATOTA AJAX BADENBALL", page_icon="⚽", layout="wide")

# --- 2. CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #000000; }
    h1, h2, h3, h4, h5, p, span, div { font-family: 'Helvetica', sans-serif; color: #ffffff; }
    
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

    .player-card {
        background-color: #121212;
        border: 1px solid #8a2be2;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 10px;
        text-align: center;
    }
    .player-debt { color: #ff4444; font-weight: bold; font-size: 20px; }

    @media (max-width: 768px) {
        .kpi-value { font-size: 50px !important; }
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

@st.cache_data(ttl=5)
def carregar_dados():
    url_fluxo = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTp9Eoyr5oJkOhw-7GElhvo2p8h73J_kbsee2JjUDjPNO18Lv7pv5oU3w7SC9d_II2WVRB_E4TUd1XK/pub?gid=1108345129&single=true&output=csv"
    url_param = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTp9Eoyr5oJkOhw-7GElhvo2p8h73J_kbsee2JjUDjPNO18Lv7pv5oU3w7SC9d_II2WVRB_E4TUd1XK/pub?gid=972176032&single=true&output=csv"
    try:
        df_f = pd.read_csv(url_fluxo)
        df_p = pd.read_csv(url_param)
        if df_f['Valor'].dtype == 'object': df_f['Valor'] = df_f['Valor'].apply(limpar_moeda)
        if df_p['Valor'].dtype == 'object': df_p['Valor'] = df_p['Valor'].apply(limpar_moeda)
        return df_f, df_p
    except: return None, None

df_fluxo, df_parametros = carregar_dados()
if df_fluxo is None: st.stop()

# --- 4. CÁLCULOS ---
def calcular_efeito_caixa(row):
    if str(row['Status']).strip().lower() != 'pago': return 0.0
    valor = abs(float(row['Valor']))
    tipo = str(row['Tipo']).strip().lower()
    if 'entrada' in tipo: return valor
    elif 'saída' in tipo or 'saida' in tipo: return -valor
    else: return 0.0

df_fluxo['Efeito_Caixa'] = df_fluxo.apply(calcular_efeito_caixa, axis=1)
saldo_atual = df_fluxo['Efeito_Caixa'].sum()

pendencias = df_fluxo[(df_fluxo['Status'] == 'Pendente') & (df_fluxo['Tipo'] == 'Entrada')]
total_pendente = pendencias['Valor'].sum()

try:
    meta_val = df_parametros[df_parametros['Parametro'] == 'Meta_Reserva']['Valor'].values[0]
    progresso_meta = min(int((saldo_atual / meta_val) * 100), 100)
except: meta_val = 800; progresso_meta = 0

# --- 5. GRÁFICO (PREPARAÇÃO) ---
meses_ordem = {
    'Janeiro': 1, 'Fevereiro': 2, 'Março': 3, 'Abril': 4, 'Maio': 5, 'Junho': 6,
    'Julho': 7, 'Agosto': 8, 'Setembro': 9, 'Outubro': 10, 'Novembro': 11, 'Dezembro': 12,
    'Jan': 1, 'Fev': 2, 'Mar': 3, 'Abr': 4, 'Mai': 5, 'Jun': 6,
    'Jul': 7, 'Ago': 8, 'Set': 9, 'Out': 10, 'Nov': 11, 'Dez': 12
}
def get_mes_num(m):
    try: return meses_ordem.get(m.split('/')[0].strip(), 0)
    except: return 0

df_graf = df_fluxo[df_fluxo['Efeito_Caixa'] != 0].copy()
df_graf['Mes_Num'] = df_graf['Mes_Ref'].apply(get_mes_num)
df_agrupado = df_graf.groupby(['Mes_Ref', 'Mes_Num'])['Efeito_Caixa'].sum().reset_index()
df_agrupado = df_agrupado.sort_values('Mes_Num')
df_agrupado['Saldo_Acumulado'] = df_agrupado['Efeito_Caixa'].cumsum()

# --- 6. VISUALIZAÇÃO ---
col_logo, col_txt = st.columns([1, 4])
with col_logo:
    try: st.image("logo.png", width=150)
    except: st.header("⚽")
with col_txt:
    st.markdown("""<div style="text-align: left; padding-top: 10px;">
        <h1 style="margin:0;">AJAX BADENBALL</h1>
        <h5 style="color: #8a2be2; margin:0;">QUINTAS-FEIRAS | 18:30</h5>
    </div>""", unsafe_allow_html=True)
st.markdown("---")

c1, c2, c3 = st.columns(3)
with c1:
    st.markdown(f"""<div class
