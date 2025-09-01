# pages/1_Resumo.py
import streamlit as st
import plotly.express as px
import pandas as pd

st.set_page_config(page_title="Resumo | BanVic", layout="wide")

st.title("📌 Resumo Geral")

if "df_filtered" not in st.session_state:
    st.warning("Volte para a página inicial e aplique os filtros primeiro.")
    st.stop()

df = st.session_state["df_filtered"]
date_col = st.session_state["date_col"]
amount_col = st.session_state["amount_col"]

if df.empty:
    st.warning("Sem dados no período selecionado.")
    st.stop()

# ---------------------------
# KPIs
# ---------------------------
total_volume = df[amount_col].sum()
media_diaria = df.groupby(df[date_col].dt.date)[amount_col].sum().mean()
max_volume = df.groupby(df[date_col].dt.date)[amount_col].sum().max()
min_volume = df.groupby(df[date_col].dt.date)[amount_col].sum().min()

st.subheader("📊 Principais Indicadores")
kpi1, kpi2, kpi3, kpi4 = st.columns(4)
kpi1.metric("Total (R$)", f"{total_volume:,.2f}")
kpi2.metric("Média Diária (R$)", f"{media_diaria:,.2f}")
kpi3.metric("Maior Dia (R$)", f"{max_volume:,.2f}")
kpi4.metric("Menor Dia (R$)", f"{min_volume:,.2f}")

# ---------------------------
# Distribuição por Dia da Semana
# ---------------------------
st.subheader("📅 Volume por Dia da Semana")
weekday_map = {
    "Monday": "Segunda-feira",
    "Tuesday": "Terça-feira", 
    "Wednesday": "Quarta-feira",
    "Thursday": "Quinta-feira",
    "Friday": "Sexta-feira",
    "Saturday": "Sábado",
    "Sunday": "Domingo"
}

df["dia_semana_pt"] = df[date_col].dt.day_name().map(weekday_map)
dia_order = ["Segunda-feira", "Terça-feira", "Quarta-feira", "Quinta-feira", "Sexta-feira", "Sábado", "Domingo"]
volume_por_dia = df.groupby("dia_semana_pt")[amount_col].sum().reindex(dia_order)

graf1 = px.bar(
    x=volume_por_dia.index,
    y=volume_por_dia.values,
    labels={"x": "Dia da Semana", "y": "Volume (R$)"},
    title="Distribuição por Dia da Semana",
    color=volume_por_dia.values,
    color_continuous_scale="Blues"
)
graf1.update_layout(showlegend=False)
st.plotly_chart(graf1, use_container_width=True)

# ---------------------------
# Tendência Mensal
# ---------------------------
st.subheader("📈 Tendência Mensal")
df["mes"] = df[date_col].dt.to_period("M").astype(str)
volume_mensal = df.groupby("mes")[amount_col].sum().reset_index()

graf2 = px.line(
    volume_mensal, 
    x="mes", 
    y=amount_col, 
    labels={"mes": "Mês", amount_col: "Volume (R$)"},
    title="Evolução do Volume Mensal",
    markers=True
)
st.plotly_chart(graf2, use_container_width=True)

# ---------------------------
# Insights automáticos
# ---------------------------
st.subheader("💡 Insights")
maior_dia = volume_por_dia.idxmax()
menor_dia = volume_por_dia.idxmin()
maior_mes = volume_mensal.loc[volume_mensal[amount_col].idxmax(), "mes"]
menor_mes = volume_mensal.loc[volume_mensal[amount_col].idxmin(), "mes"]

st.markdown(f"- O dia da semana com maior volume é **{maior_dia}** e o menor é **{menor_dia}**.")
st.markdown(f"- O mês com maior volume é **{maior_mes}** e o menor é **{menor_mes}**.")
st.markdown(f"- O volume total no período é **R$ {total_volume:,.2f}**.")
