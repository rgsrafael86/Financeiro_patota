import streamlit as st
import pandas as pd
import plotly.express as px

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Finanças da Patota", page_icon="⚽", layout="wide")

# --- CARREGAR DADOS ---
@st.cache_data
def carregar_dados():
    arquivo = "Controle_Financeiro_Patota.xlsx"
    try:
        # Lê as 3 abas essenciais
        df_fluxo = pd.read_excel(arquivo, sheet_name="Fluxo_Caixa")
        df_jogadores = pd.read_excel(arquivo, sheet_name="Base_Jogadores")
        df_parametros = pd.read_excel(arquivo, sheet_name="Parametros")
        return df_fluxo, df_jogadores, df_parametros
    except FileNotFoundError:
        return None, None, None

df_fluxo, df_jogadores, df_parametros = carregar_dados()

# --- VERIFICAÇÃO DE SEGURANÇA ---
if df_fluxo is None:
    st.error("⚠️ Erro: Não encontrei o arquivo 'Controle_Financeiro_Patota.xlsx'. Verifique se ele foi enviado para o GitHub!")
    st.stop()

# --- CÁLCULOS DO DT (Lógica de Negócio) ---
# 1. Saldo Real (Apenas o que já foi PAGO)
saldo_atual = df_fluxo[df_fluxo['Status'] == 'Pago']['Valor'].sum()

# 2. Pendências (Dinheiro que deveria ter entrado)
pendencias = df_fluxo[(df_fluxo['Status'] == 'Pendente') & (df_fluxo['Tipo'] == 'Entrada')]
total_pendente = pendencias['Valor'].sum()

# 3. Meta da Reserva (Barra de Progresso)
meta_reserva = df_parametros[df_parametros['Parametro'] == 'Meta_Reserva']['Valor'].values[0]
progresso_meta = min(int((saldo_atual / meta_reserva) * 100), 100)

# --- O SITE COMEÇA AQUI ---
st.title("⚽ Painel Financeiro da Patota")
st.markdown(f"**Atualizado em:** {pd.Timestamp.now().strftime('%d/%m/%Y')}")

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
    # Mostra tabela limpa
    st.dataframe(
        pendencias[['Mes_Ref', 'Nome', 'Categoria', 'Valor', 'Obs']],
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
