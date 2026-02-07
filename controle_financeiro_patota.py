import streamlit as st
import pandas as pd
import plotly.express as px

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Finanças da Patota", page_icon="⚽", layout="wide")

# --- CARREGAR DADOS DO GOOGLE SHEETS (EM TEMPO REAL) ---
@st.cache_data(ttl=60) # Atualiza o cache a cada 60 segundos
def carregar_dados():
    # Links gerados pelo Rafael
    url_fluxo = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTp9Eoyr5oJkOhw-7GElhvo2p8h73J_kbsee2JjUDjPNO18Lv7pv5oU3w7SC9d_II2WVRB_E4TUd1XK/pub?gid=1108345129&single=true&output=csv"
    url_parametros = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTp9Eoyr5oJkOhw-7GElhvo2p8h73J_kbsee2JjUDjPNO18Lv7pv5oU3w7SC9d_II2WVRB_E4TUd1XK/pub?gid=972176032&single=true&output=csv"
    url_jogadores = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTp9Eoyr5oJkOhw-7GElhvo2p8h73J_kbsee2JjUDjPNO18Lv7pv5oU3w7SC9d_II2WVRB_E4TUd1XK/pub?gid=508755914&single=true&output=csv"
    
    try:
        # Lê os CSVs direto da nuvem
        # decimal=',' e thousands='.' garantem que o Python entenda '1.200,50' se sua planilha estiver em PT-BR
        df_fluxo = pd.read_csv(url_fluxo) 
        df_jogadores = pd.read_csv(url_jogadores)
        df_parametros = pd.read_csv(url_parametros)
        
        # Tratamento de erro caso venha texto na coluna de valor
        if df_fluxo['Valor'].dtype == 'object':
             df_fluxo['Valor'] = df_fluxo['Valor'].str.replace('.', '', regex=False).str.replace(',', '.', regex=False).astype(float)
             
        if df_parametros['Valor'].dtype == 'object':
             df_parametros['Valor'] = df_parametros['Valor'].str.replace('.', '', regex=False).str.replace(',', '.', regex=False).astype(float)

        return df_fluxo, df_jogadores, df_parametros
    except Exception as e:
        st.error(f"⚠️ Erro de Conexão com a Planilha: {e}")
        return None, None, None

df_fluxo, df_jogadores, df_parametros = carregar_dados()

# --- VERIFICAÇÃO DE SEGURANÇA ---
if df_fluxo is None:
    st.stop()

# --- CÁLCULOS DO DT (Lógica de Negócio) ---
# 1. Saldo Real (Apenas o que já foi PAGO)
saldo_atual = df_fluxo[df_fluxo['Status'] == 'Pago']['Valor'].sum()

# 2. Pendências (Dinheiro que deveria ter entrado)
pendencias = df_fluxo[(df_fluxo['Status'] == 'Pendente') & (df_fluxo['Tipo'] == 'Entrada')]
total_pendente = pendencias['Valor'].sum()

# 3. Meta da Reserva (Barra de Progresso)
try:
    meta_reserva = df_parametros[df_parametros['Parametro'] == 'Meta_Reserva']['Valor'].values[0]
    progresso_meta = min(int((saldo_atual / meta_reserva) * 100), 100)
except:
    meta_reserva = 800 # Valor padrão caso falhe a leitura
    progresso_meta = 0

# --- O SITE COMEÇA AQUI ---
st.title("⚽ Painel Financeiro da Patota")
st.markdown(f"**Conectado ao Google Sheets 🟢** | Dados atualizados automaticamente.")

# PLACAR GERAL (KPIs)
col1, col2, col3 = st.columns(3)
col1.metric("💰 Saldo em Caixa", f"R$ {saldo_atual:,.2f}")
col2.metric("⚠️ A Receber (Pendências)", f"R$ {total_pendente:,.2f}", delta_color="inverse")
col3.metric("🎯 Meta Reserva", f"{progresso_meta}%")

# Barra de Progresso
st.progress(progresso_meta / 100)
st.caption(f"Meta: R$ {meta_reserva:,.2f} | Atual: R$ {saldo_atual:,.2f}")

st.divider()

# --- ÁREA 1: QUEM ESTÁ DEVENDO? ---
st.subheader("📋 Mural da Transparência (Pendências)")

if not pendencias.empty:
    st.warning(f"Total pendente: **R$ {total_pendente:,.2f}**")
    
    # Define as colunas que queremos mostrar
    colunas_para_mostrar = ['Mes_Ref', 'Nome', 'Categoria', 'Valor']
    
    # Só adiciona 'Obs' se ela realmente existir na planilha
    if 'Obs' in pendencias.columns:
        colunas_para_mostrar.append('Obs')
        
    st.dataframe(
        pendencias[colunas_para_mostrar],
        hide_index=True,
        use_container_width=True
    )
else:
    st.success("✅ Ninguém devendo! O time está em dia.")

st.divider()

# --- ÁREA 2: GRÁFICOS ---
col_graf1, col_graf2 = st.columns(2)

with col_graf1:
    st.subheader("📊 Origem do Dinheiro")
    entradas = df_fluxo[df_fluxo['Tipo'] == 'Entrada']
    if not entradas.empty:
        fig_pizza = px.pie(entradas, values='Valor', names='Categoria', hole=0.4)
        st.plotly_chart(fig_pizza, use_container_width=True)

with col_graf2:
    st.subheader("🗓️ Histórico Mensal")
    fig_barras = px.bar(df_fluxo, x='Mes_Ref', y='Valor', color='Tipo', barmode='group',
                        color_discrete_map={'Entrada': 'green', 'Saída': 'red'})
    st.plotly_chart(fig_barras, use_container_width=True)
