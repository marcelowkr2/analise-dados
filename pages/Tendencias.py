# pages/4_Tendencias.py
import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from math import erf

st.set_page_config(page_title="Tendências | BanVic", layout="wide")

# Verificar se as variáveis de sessão existem
if "df_filtered" not in st.session_state:
    st.warning("Volte para a página inicial e aplique os filtros primeiro.")
    st.stop()

df = st.session_state["df_filtered"]
date_col = st.session_state["date_col"]
amount_col = st.session_state["amount_col"]

st.title("Tendências e Hipóteses")

if df.empty:
    st.warning("Sem dados no período selecionado.")
else:
    # Months even vs odd
    df["_month"] = df[date_col].dt.month
    df["_month_period"] = df[date_col].dt.to_period("M")
    
    # CORREÇÃO: Converter Period para string antes do groupby
    monthly = df.groupby("_month_period").agg(month_volume=(amount_col,"sum")).reset_index()
    
    # CORREÇÃO: Converter Period para string para serialização JSON
    monthly["_month_period_str"] = monthly["_month_period"].astype(str)
    monthly["_month_num"] = monthly["_month_period"].dt.month
    monthly["is_even"] = monthly["_month_num"] % 2 == 0

    even = monthly.loc[monthly["is_even"], "month_volume"].astype(float)
    odd = monthly.loc[~monthly["is_even"], "month_volume"].astype(float)

    # Welch-like t (approx using normal)
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

    test = approx_welch(even, odd)
    st.subheader("Meses pares vs ímpares")
    st.markdown(f"- Média meses pares: **R$ {test['mean_even']:,.2f}** (n={len(even)})")
    st.markdown(f"- Média meses ímpares: **R$ {test['mean_odd']:,.2f}** (n={len(odd)})")
    st.markdown(f"- Estatística t (aprox): **{test['t']:.3f}**, p (aprox): **{test['p']:.3f}**")
    
    if test['p'] < 0.05:
        st.success("✅ Diferença estatisticamente significativa (p < 0.05)")
    else:
        st.info("ℹ️ Diferença não estatisticamente significativa")

    # CORREÇÃO: Usar a coluna string em vez do objeto Period
    fig = px.bar(monthly, x="_month_period_str", y="month_volume", 
                 title="Volume Mensal (pares vs ímpares)",
                 labels={"_month_period_str": "Mês", "month_volume": "Volume (R$)"},
                 color="is_even",
                 color_discrete_map={True: '#1f77b4', False: '#ff7f0e'})
    
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.subheader("Sazonalidade semanal (média por dia)")
    
    # Traduzir dias da semana para português
    weekday_map = {
        0: "segunda-feira",
        1: "terça-feira", 
        2: "quarta-feira",
        3: "quinta-feira",
        4: "sexta-feira",
        5: "sábado",
        6: "domingo"
    }
    
    df["_weekday_pt"] = df[date_col].dt.dayofweek.map(weekday_map)
    weekly = df.groupby("_weekday_pt").agg(
        n_transacoes=(amount_col,"count"), 
        volume=(amount_col,"sum"),
        volume_medio=(amount_col,"mean")
    ).reset_index()
    
    order = ["segunda-feira","terça-feira","quarta-feira","quinta-feira","sexta-feira","sábado","domingo"]
    weekly["_order"] = weekly["_weekday_pt"].apply(lambda x: order.index(x) if x in order else 7)
    weekly = weekly.sort_values("_order")
    
    # Gráfico de volume total por dia
    fig1 = px.bar(weekly, x="_weekday_pt", y="volume", 
                  title="Volume total por dia da semana",
                  labels={"_weekday_pt": "Dia da Semana", "volume": "Volume Total (R$)"})
    st.plotly_chart(fig1, use_container_width=True)
    
    # Gráfico de volume médio por dia
    fig2 = px.bar(weekly, x="_weekday_pt", y="volume_medio", 
                  title="Volume médio por dia da semana",
                  labels={"_weekday_pt": "Dia da Semana", "volume_medio": "Volume Médio por Transação (R$)"})
    st.plotly_chart(fig2, use_container_width=True)
    
    st.markdown("---")
    st.subheader("Análise Horária (se disponível)")
    
    # Verificar se temos informação de hora
    if df[date_col].dt.hour.nunique() > 1:
        df["_hour"] = df[date_col].dt.hour
        hourly = df.groupby("_hour").agg(
            n_transacoes=(amount_col, "count"),
            volume=(amount_col, "sum"),
            volume_medio=(amount_col, "mean")
        ).reset_index()
        
        fig3 = px.line(hourly, x="_hour", y="volume", 
                      title="Volume por Hora do Dia",
                      labels={"_hour": "Hora", "volume": "Volume (R$)"})
        st.plotly_chart(fig3, use_container_width=True)
        
        fig4 = px.bar(hourly, x="_hour", y="n_transacoes",
                     title="Número de Transações por Hora",
                     labels={"_hour": "Hora", "n_transacoes": "Número de Transações"})
        st.plotly_chart(fig4, use_container_width=True)
    else:
        st.info("Informação de hora não disponível ou insuficiente para análise horária")
    
    st.markdown("---")
    st.subheader("Distribuição de Valores")
    
    # Histograma de valores das transações
    fig5 = px.histogram(df, x=amount_col, 
                       title="Distribuição dos Valores das Transações",
                       labels={amount_col: "Valor (R$)", "count": "Frequência"},
                       nbins=50)
    st.plotly_chart(fig5, use_container_width=True)
    
    # Box plot para outliers
    fig6 = px.box(df, y=amount_col, 
                 title="Box Plot - Distribuição de Valores",
                 labels={amount_col: "Valor (R$)"})
    st.plotly_chart(fig6, use_container_width=True)