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

# Traduzir dias da semana para português
weekday_map = {
    "Monday": "Segunda-feira",
    "Tuesday": "Terça-feira", 
    "Wednesday": "Quarta-feira",
    "Thursday": "Quinta-feira",
    "Friday": "Sexta-feira",
    "Saturday": "Sábado",
    "Sunday": "Domingo"
}

st.subheader("Volume por Dia da Semana")
df["dia_semana_en"] = df[date_col].dt.day_name()
df["dia_semana_pt"] = df["dia_semana_en"].map(weekday_map)

# Ordem correta dos dias
dia_order = ["Segunda-feira", "Terça-feira", "Quarta-feira", "Quinta-feira", "Sexta-feira", "Sábado", "Domingo"]
volume_por_dia = df.groupby("dia_semana_pt")[amount_col].sum().reindex(dia_order)

graf1 = px.bar(x=volume_por_dia.index, y=volume_por_dia.values,
               labels={"x": "Dia da Semana", "y": "Volume (R$)"}, 
               title="Distribuição por Dia da Semana")
st.plotly_chart(graf1, use_container_width=True)

st.subheader("Tendência Mensal")
df["mes"] = df[date_col].dt.to_period("M").astype(str)
volume_mensal = df.groupby("mes")[amount_col].sum().reset_index()

graf2 = px.line(volume_mensal, x="mes", y=amount_col, 
                labels={"mes": "Mês", amount_col: "Volume (R$)"},
                title="Evolução do Volume Mensal")
st.plotly_chart(graf2, use_container_width=True)