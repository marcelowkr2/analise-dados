# pages/1_Resumo.py
import streamlit as st
import plotly.express as px
import pandas as pd
import numpy as np
from math import erf

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

# ----------------- Volume por Dia da Semana -----------------
st.subheader("Volume por Dia da Semana")
weekday_map = {
    "Monday": "Segunda-feira",
    "Tuesday": "Terça-feira", 
    "Wednesday": "Quarta-feira",
    "Thursday": "Quinta-feira",
    "Friday": "Sexta-feira",
    "Saturday": "Sábado",
    "Sunday": "Domingo"
}

df["dia_semana_en"] = df[date_col].dt.day_name()
df["dia_semana_pt"] = df["dia_semana_en"].map(weekday_map)
dia_order = ["Segunda-feira", "Terça-feira", "Quarta-feira", "Quinta-feira", "Sexta-feira", "Sábado", "Domingo"]
volume_por_dia = df.groupby("dia_semana_pt")[amount_col].sum().reindex(dia_order)

graf1 = px.bar(x=volume_por_dia.index, y=volume_por_dia.values,
               labels={"x": "Dia da Semana", "y": "Volume (R$)"},
               title="Distribuição por Dia da Semana")
st.plotly_chart(graf1, use_container_width=True)

# ----------------- Dias Pares vs Ímpares -----------------
st.subheader("Arrecadação: Dias Pares vs Dias Ímpares")
df["dia_num"] = df[date_col].dt.day
df["par"] = df["dia_num"] % 2 == 0

pares = df[df["par"]][amount_col]
impares = df[~df["par"]][amount_col]

def approx_welch(x, y):
    x = x.dropna().values.astype(float)
    y = y.dropna().values.astype(float)
    nx, ny = len(x), len(y)
    if nx < 2 or ny < 2:
        return {"mean_even": np.nan, "mean_odd": np.nan, "t": np.nan, "p": np.nan}
    mx, my = x.mean(), y.mean()
    vx, vy = x.var(ddof=1), y.var(ddof=1)
    t = (mx - my) / np.sqrt(vx/nx + vy/ny)
    z = abs(t)
    p = 2*(1 - 0.5*(1+erf(z/np.sqrt(2))))
    return {"mean_even": mx, "mean_odd": my, "t": t, "p": p}

test = approx_welch(pares, impares)
st.markdown(f"- Média dias pares: **R$ {test['mean_even']:,.2f}** (n={len(pares)})")
st.markdown(f"- Média dias ímpares: **R$ {test['mean_odd']:,.2f}** (n={len(impares)})")
st.markdown(f"- Estatística t (aprox): **{test['t']:.3f}**, p (aprox): **{test['p']:.3f}**")
st.success("✅ Diferença estatisticamente significativa (p < 0.05)" if test['p'] < 0.05 else "ℹ️ Diferença não estatisticamente significativa")

volume_paridade = df.groupby("par")[amount_col].sum().rename({True:"Pares", False:"Ímpares"})
graf_paridade = px.bar(x=volume_paridade.index.map({True:"Pares", False:"Ímpares"}), y=volume_paridade.values,
                       labels={"x":"Paridade do Dia", "y":"Volume (R$)"},
                       title="Volume Total: Dias Pares vs Dias Ímpares")
st.plotly_chart(graf_paridade, use_container_width=True)

# ----------------- Tendência Mensal -----------------
st.subheader("Tendência Mensal")
df["mes"] = df[date_col].dt.to_period("M")
volume_mensal = df.groupby(df["mes"].astype(str))[amount_col].sum().reset_index()
graf2 = px.line(volume_mensal, x="mes", y=amount_col, 
                labels={"mes": "Mês", amount_col: "Volume (R$)"},
                title="Evolução do Volume Mensal")
st.plotly_chart(graf2, use_container_width=True)

# ----------------- Tendência Mensal Dias Pares vs Ímpares -----------------
st.subheader("Tendência Mensal: Dias Pares vs Dias Ímpares")
df["mes_str"] = df["mes"].astype(str)
mensal_paridade = df.groupby(["mes_str", "par"])[amount_col].sum().reset_index()
mensal_paridade["Paridade"] = mensal_paridade["par"].map({True:"Pares", False:"Ímpares"})

graf3 = px.line(mensal_paridade, x="mes_str", y=amount_col, color="Paridade",
                labels={"mes_str":"Mês", amount_col:"Volume (R$)", "Paridade":"Dia"},
                title="Evolução Mensal Separada: Dias Pares vs Ímpares")
st.plotly_chart(graf3, use_container_width=True)
