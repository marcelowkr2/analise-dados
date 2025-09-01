import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Balanço Agências", page_icon="🏦", layout="wide")
st.title("🏦 Balanço por Agência")

DATA_DIR = "data"

@st.cache_data
def load_data():
    propostas = pd.read_csv(f"{DATA_DIR}/propostas_credito.csv", low_memory=False)
    transacoes = pd.read_csv(f"{DATA_DIR}/transacoes.csv", low_memory=False)
    colaboradores = pd.read_csv(f"{DATA_DIR}/colaboradores.csv", low_memory=False)
    colaborador_ag = pd.read_csv(f"{DATA_DIR}/colaborador_agencia.csv", low_memory=False)
    return propostas, transacoes, colaboradores, colaborador_ag

propostas, transacoes, colaboradores, colaborador_ag = load_data()

# ---------- Tratamento ----------
propostas["data_entrada_proposta"] = pd.to_datetime(propostas["data_entrada_proposta"], errors="coerce")
transacoes["data_transacao"] = pd.to_datetime(transacoes["data_transacao"], errors="coerce")

# Merge colaboradores -> agência
colab_ag = colaboradores.merge(colaborador_ag, on="cod_colaborador", how="left")

# Merge propostas -> colaborador -> agência
propostas_ag = propostas.merge(colab_ag, on="cod_colaborador", how="left")

# ---------- KPIs ----------
st.subheader("📌 Indicadores por Agência")

df_ag = propostas_ag.groupby("cod_agencia").agg(
    qtd_propostas=("cod_proposta", "count"),
    valor_total_propostas=("valor_proposta", "sum"),
    valor_total_financiado=("valor_financiamento", "sum"),
    ticket_medio=("valor_proposta", "mean"),
).reset_index()

col1, col2, col3 = st.columns(3)
col1.metric("Total de Agências", df_ag["cod_agencia"].nunique())
col2.metric("Propostas Totais", int(df_ag["qtd_propostas"].sum()))
col3.metric("Volume Total Propostas", f"R$ {df_ag['valor_total_propostas'].sum():,.2f}")

st.dataframe(df_ag)

# ---------- Gráficos ----------
st.subheader("📈 Análises Visuais")

col1, col2 = st.columns(2)

with col1:
    fig1 = px.bar(df_ag, x="cod_agencia", y="valor_total_propostas",
                  title="Valor Total de Propostas por Agência", text_auto=".2s")
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    fig2 = px.bar(df_ag, x="cod_agencia", y="qtd_propostas",
                  title="Quantidade de Propostas por Agência", text_auto=True)
    st.plotly_chart(fig2, use_container_width=True)

# ---------- Evolução Temporal ----------
st.subheader("📆 Evolução de Propostas")
df_time = propostas_ag.groupby(propostas_ag["data_entrada_proposta"].dt.to_period("M")).agg(
    total_valor=("valor_proposta", "sum")
).reset_index()
df_time["mes"] = df_time["data_entrada_proposta"].dt.to_timestamp()

fig3 = px.line(df_time, x="mes", y="total_valor", markers=True,
               title="Evolução Mensal do Valor das Propostas")
st.plotly_chart(fig3, use_container_width=True)
