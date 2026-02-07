import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# --- 1. CONFIGURAÇÃO ---
st.set_page_config(page_title="PATOTA AJAX BADENBALL", page_icon="⚽", layout="wide")

# --- 2. CSS "CYBERPUNK" ---
st.markdown("""
    <style>
    .stApp { background-color: #000000; }
    h1, h2, h3, h4, h5, p, span, div { font-family: 'Helvetica', sans-serif; color: #ffffff; }
    
    /* KPI CONTAINER */
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

    /* CARDS */
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

@st.cache_data(ttl=60)
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

# --- 4. CÁLCULOS KPI ---
df_pagos = df_fluxo[df_fluxo['Status'] == 'Pago'].copy()
total_entradas = df_pagos[df_pagos['Tipo'] == 'Entrada']['Valor'].sum()
total_saidas = df_pagos[df_pagos['Tipo'] == 'Saída']['Valor'].sum()
saldo_atual = total_entradas - total_saidas

pendencias = df_fluxo[(df_fluxo['Status'] == 'Pendente') & (df_fluxo['Tipo'] == 'Entrada')]
total_pendente = pendencias['Valor'].sum()

try:
    meta_val = df_parametros[df_parametros['Parametro'] == 'Meta_Reserva']['Valor'].values[0]
    progresso_meta = min(int((saldo_atual / meta_val) * 100), 100)
except: meta_val = 800; progresso_meta = 0

# --- 5. LÓGICA DO GRÁFICO DE EVOLUÇÃO ---
# Prepara os dados para o gráfico de linha (Acumulado)
df_evo = df_pagos.copy()
# Transforma saídas em negativo para a soma funcionar
df_evo['Valor_Real'] = df_evo.apply(lambda x: x['Valor'] if x['Tipo'] == 'Entrada' else -x['Valor'], axis=1)

# Tenta converter Mes_Ref para data para ordenar corretamente (Jan, Fev, Mar...)
meses_map = {
    'Janeiro': 1, 'Fevereiro': 2, 'Março': 3, 'Abril': 4, 'Maio': 5, 'Junho': 6,
    'Julho': 7, 'Agosto': 8, 'Setembro': 9, 'Outubro': 10, 'Novembro': 11, 'Dezembro': 12,
    'Jan': 1, 'Fev': 2, 'Mar': 3, 'Abr': 4, 'Mai': 5, 'Jun': 6,
    'Jul': 7, 'Ago': 8, 'Set': 9, 'Out': 10, 'Nov': 11, 'Dez': 12
}

def parse_month(mes_str):
    # Tenta extrair o mês de strings como "Janeiro/2024" ou apenas "Janeiro"
    try:
        parte_mes = mes_str.split('/')[0].strip()
        return meses_map.get(parte_mes, 0)
    except: return 0

df_evo['Mes_Num'] = df_evo['Mes_Ref'].apply(parse_month)
# Agrupa por mês
df_grafico = df_evo.groupby(['Mes_Ref', 'Mes_Num'])['Valor_Real'].sum().reset_index()
# Ordena cronologicamente
df_grafico = df_grafico.sort_values('Mes_Num')

# Calcula o Saldo Acumulado (Evolução)
df_grafico['Saldo_Acumulado'] = df_grafico['Valor_Real'].cumsum()

# --- 6. VISUALIZAÇÃO ---

# Header
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

# Placar
c1, c2, c3 = st.columns(3)
with c1:
    st.markdown(f"""<div class="kpi-container"><div class="kpi-label">SALDO EM CAIXA</div><div class="kpi-value" style="color: #00d4ff;">R$ {saldo_atual:,.2f}</div></div>""", unsafe_allow_html=True)
with c2:
    st.markdown(f"""<div class="kpi-container" style="border-top-color: #ff4444;"><div class="kpi-label">A RECEBER</div><div class="kpi-value" style="color: #ff4444;">R$ {total_pendente:,.2f}</div></div>""", unsafe_allow_html=True)
with c3:
    cor = "#00ff00" if progresso_meta >= 100 else "#e0e0e0"
    st.markdown(f"""<div class="kpi-container" style="border-top-color: #8a2be2;"><div class="kpi-label">META RESERVA</div><div class="kpi-value" style="color: {cor};">{progresso_meta}%</div></div>""", unsafe_allow_html=True)

# Mural
st.markdown("<h3 style='color: #8a2be2;'>📋 DEVEDORES</h3>", unsafe_allow_html=True)
if not pendencias.empty:
    pendencias = pendencias.reset_index(drop=True)
    cols = st.columns(3)
    for i, row in pendencias.iterrows():
        with cols[i % 3]:
            st.markdown(f"""<div class="player-card"><div style="color:white; font-weight:bold;">{row['Nome']}</div><div style="color:#888; font-size:12px;">{row['Categoria']} • {row['Mes_Ref']}</div><div class="player-debt">R$ {row['Valor']:.0f}</div></div>""", unsafe_allow_html=True)
else:
    st.success("✅ Ninguém devendo!")

st.markdown("---")

# --- GRÁFICO DE LINHA (EVOLUÇÃO) ---
st.markdown("### 📈 EVOLUÇÃO DO CAIXA (ÚLTIMOS MESES)")

# Criação do Gráfico com Plotly Graph Objects (Mais flexível)
fig = go.Figure()

# 1. Linha do Saldo
fig.add_trace(go.Scatter(
    x=df_grafico['Mes_Ref'], 
    y=df_grafico['Saldo_Acumulado'],
    mode='lines+markers+text',
    name='Saldo Atual',
    line=dict(color='#00d4ff', width=4),
    marker=dict(size=10, color='#00d4ff'),
    text=df_grafico['Saldo_Acumulado'].apply(lambda x: f"R$ {x:.0f}"),
    textposition="top center"
))

# 2. Linha da Meta (Tracejada)
fig.add_trace(go.Scatter(
    x=df_grafico['Mes_Ref'],
    y=[meta_val] * len(df_grafico),
    mode='lines',
    name=f'Meta (R$ {meta_val})',
    line=dict(color='#00ff00', width=2, dash='dash')
))

# Layout do Gráfico (Transparente e Estiloso)
fig.update_layout(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    font=dict(color='white'),
    xaxis=dict(showgrid=False, linecolor='#333'),
    yaxis=dict(showgrid=True, gridcolor='#333', zeroline=True, zerolinecolor='#666'),
    legend=dict(orientation="h", y=1.1),
    margin=dict(l=0, r=0, t=30, b=0),
    height=400
)

st.plotly_chart(fig, use_container_width=True)

# --- AUDITORIA ---
st.markdown("---")
with st.expander("🕵️‍♂️ VER DADOS BRUTOS"):
    st.dataframe(df_fluxo, use_container_width=True)
