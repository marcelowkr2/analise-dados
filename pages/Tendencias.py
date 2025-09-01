# pages/4_Tendencias.py
import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from math import erf

st.set_page_config(page_title="Tendências | BanVic", layout="wide")
st.title("📈 Tendências Avançadas")

# ---------------------------
# Verificação inicial
# ---------------------------
if "df_filtered" not in st.session_state:
    st.warning("Volte para a página inicial e aplique os filtros primeiro.")
    st.stop()

df = st.session_state["df_filtered"].copy()
date_col = st.session_state["date_col"]
amount_col = st.session_state["amount_col"]

if df.empty:
    st.warning("Sem dados no período selecionado.")
    st.stop()

# ---------------------------
# Filtros interativos
# ---------------------------
st.sidebar.subheader("Filtros")

# Função para criar filtro seguro
def safe_multiselect(label, column_name):
    if column_name in df.columns:
        options = df[column_name].unique()
        return st.sidebar.multiselect(label, options=options, default=list(options))
    return None

clientes = safe_multiselect("Selecionar Cliente(s)", "Cliente")
agencias = safe_multiselect("Selecionar Agência(s)", "Agencia")

# Filtro de período
periodo = st.sidebar.date_input(
    "Período",
    value=(df[date_col].min().date(), df[date_col].max().date())
)

# Aplicar filtros
if clientes is not None:
    df = df[df["Cliente"].isin(clientes)]
if agencias is not None:
    df = df[df["Agencia"].isin(agencias)]
df = df[(df[date_col].dt.date >= periodo[0]) & (df[date_col].dt.date <= periodo[1])]

if df.empty:
    st.warning("Não há dados para os filtros selecionados.")
    st.stop()

# ---------------------------
# KPIs principais
# ---------------------------
total_volume = df[amount_col].sum()
total_transacoes = df.shape[0]
media_transacao = df[amount_col].mean()
max_valor = df[amount_col].max()
min_valor = df[amount_col].min()

st.subheader("📊 Principais Indicadores")
k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Total Volume (R$)", f"{total_volume:,.2f}")
k2.metric("Total Transações", f"{total_transacoes}")
k3.metric("Média Transação (R$)", f"{media_transacao:,.2f}")
k4.metric("Maior Valor (R$)", f"{max_valor:,.2f}")
k5.metric("Menor Valor (R$)", f"{min_valor:,.2f}")

st.markdown("---")

# ---------------------------
# Tendência Mensal com Média Móvel
# ---------------------------
st.subheader("📅 Evolução Mensal")
df["_month_period"] = df[date_col].dt.to_period("M")
monthly = df.groupby("_month_period").agg(volume=(amount_col,"sum")).reset_index()
monthly["_month_str"] = monthly["_month_period"].astype(str)
monthly["media_movel"] = monthly["volume"].rolling(3, min_periods=1).mean()

fig = px.line(monthly, x="_month_str", y="volume", title="Volume Mensal com Média Móvel 3M",
              labels={"_month_str":"Mês","volume":"Volume (R$)"})
fig.add_scatter(x=monthly["_month_str"], y=monthly["media_movel"], mode='lines',
                name='Média Móvel 3M', line=dict(color='red', dash='dash'))
st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# ---------------------------
# Sazonalidade Semanal
# ---------------------------
st.subheader("📆 Sazonalidade Semanal")
weekday_map = {0:"Segunda-feira",1:"Terça-feira",2:"Quarta-feira",3:"Quinta-feira",
               4:"Sexta-feira",5:"Sábado",6:"Domingo"}
df["_weekday_pt"] = df[date_col].dt.dayofweek.map(weekday_map)
weekly = df.groupby("_weekday_pt").agg(
    n_transacoes=(amount_col,"count"),
    volume=(amount_col,"sum"),
    media=(amount_col,"mean")
).reset_index()
order = ["Segunda-feira","Terça-feira","Quarta-feira","Quinta-feira","Sexta-feira","Sábado","Domingo"]
weekly["_order"] = weekly["_weekday_pt"].apply(lambda x: order.index(x))
weekly = weekly.sort_values("_order")

col1, col2 = st.columns(2)
fig1 = px.bar(weekly, x="_weekday_pt", y="volume", title="Volume Total por Dia da Semana",
              labels={"_weekday_pt":"Dia","volume":"Volume (R$)"})
col1.plotly_chart(fig1, use_container_width=True)

fig2 = px.bar(weekly, x="_weekday_pt", y="media", title="Média por Transação por Dia",
              labels={"_weekday_pt":"Dia","media":"Valor Médio (R$)"})
col2.plotly_chart(fig2, use_container_width=True)

st.markdown("---")

# ---------------------------
# Distribuição e Outliers
# ---------------------------
st.subheader("💰 Distribuição e Outliers")
col1, col2 = st.columns(2)

fig3 = px.histogram(df, x=amount_col, nbins=50, title="Distribuição de Valores",
                    labels={amount_col:"Valor (R$)","count":"Frequência"})
col1.plotly_chart(fig3, use_container_width=True)

fig4 = px.box(df, y=amount_col, points="outliers", title="Box Plot - Outliers",
             labels={amount_col:"Valor (R$)"})
col2.plotly_chart(fig4, use_container_width=True)

st.markdown("---")

# ---------------------------
# Análise Horária
# ---------------------------
st.subheader("⏰ Análise Horária")
if df[date_col].dt.hour.nunique() > 1:
    df["_hour"] = df[date_col].dt.hour
    hourly = df.groupby("_hour").agg(
        n_transacoes=(amount_col,"count"),
        volume=(amount_col,"sum"),
        media=(amount_col,"mean")
    ).reset_index()
    col1, col2 = st.columns(2)
    fig5 = px.line(hourly, x="_hour", y="volume", title="Volume por Hora",
                   labels={"_hour":"Hora","volume":"Volume (R$)"})
    col1.plotly_chart(fig5, use_container_width=True)

    fig6 = px.bar(hourly, x="_hour", y="n_transacoes", title="Transações por Hora",
                  labels={"_hour":"Hora","n_transacoes":"Transações"})
    col2.plotly_chart(fig6, use_container_width=True)
else:
    st.info("Informação de hora não disponível ou insuficiente para análise horária")
