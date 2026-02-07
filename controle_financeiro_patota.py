import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="AJAX BADENBALL", page_icon="⚽", layout="wide")

# --- CSS CUSTOMIZADO (CORES DO TIME) ---
st.markdown("""
    <style>
    .stProgress > div > div > div > div { background-color: #FFD700; } /* Barra Amarela */
    h1, h2, h3 { color: #D4001C; } /* Títulos Vermelhos */
    .stMetric { background-color: #f0f2f6; padding: 10px; border-radius: 10px; border-left: 5px solid #D4001C; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNÇÃO DE LIMPEZA ---
def limpar_moeda(valor):
    if isinstance(valor, str):
        limpo = valor.replace('R$', '').replace(' ', '').replace('.', '').replace(',', '.')
        try: return float(limpo)
        except: return 0.0
    return valor

# --- CARREGAR DADOS ---
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

# --- CÁLCULOS ---
saldo_atual = df_fluxo[df_fluxo['Status'] == 'Pago']['Valor'].sum()
pendencias = df_fluxo[(df_fluxo['Status'] == 'Pendente') & (df_fluxo['Tipo'] == 'Entrada')]
total_pendente = pendencias['Valor'].sum()
meta_reserva = df_parametros[df_parametros['Parametro'] == 'Meta_Reserva']['Valor'].values[0]
progresso_meta = min(int((saldo_atual / meta_reserva) * 100), 100)

# --- CABEÇALHO ---
col_logo, col_titulo = st.columns([1, 4])
with col_logo:
    try: st.image("logo.png", width=110) # Certifique-se de subir o arquivo 'logo.png' no GitHub
    except: st.markdown("## 🍌")
with col_titulo:
    st.title("AJAX BADENBALL")
    st.markdown(f"🗓️ **Temporada:** {datetime.now().year} | 📍 **Quintas 18:30**")

# PLACAR
c1, c2, c3 = st.columns(3)
c1.metric("💰 Caixa", f"R$ {saldo_atual:,.2f}")
c2.metric("⚠️ Pendente", f"R$ {total_pendente:,.2f}")
c3.metric("🎯 Meta", f"{progresso_meta}%")

st.progress(progresso_meta / 100)

# MURAL MOBILE-FRIENDLY
st.subheader("📋 Mural da Transparência")
if not pendencias.empty:
    for _, row in pendencias.iterrows():
        with st.container(border=True):
            col_a, col_b = st.columns([3, 1])
            col_a.markdown(f"**{row['Nome']}**")
            col_a.caption(f"{row['Mes_Ref']} • {row['Categoria']}")
            col_b.markdown(f"**R$ {row['Valor']:.0f}**")
else:
    st.success("✅ Tudo em dia!")

# GRÁFICO DE RESULTADO
st.subheader("📈 Resultado Líquido")
df_mensal = df_fluxo.groupby('Mes_Ref')['Valor'].sum().reset_index()
fig = px.bar(df_mensal, x='Mes_Ref', y='Valor', color='Valor', 
             color_continuous_scale=['#D4001C', '#1C83E1'], text_auto=True)
st.plotly_chart(fig, use_container_width=True)
