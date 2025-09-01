# pages/4_Tendencias.py
import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

st.set_page_config(page_title="Tendências | BanVic", layout="wide")
st.title("📈 Tendências e Insights Avançados")

# Carregar DataFrame filtrado
df = st.session_state.get("df_filtered", pd.DataFrame())
date_col = st.session_state.get("date_col", None)
amount_col = st.session_state.get("amount_col", None)

if df.empty or date_col is None or amount_col is None:
    st.warning("Volte para a página inicial e aplique os filtros primeiro.")
    st.stop()

# --- FILTROS DINÂMICOS ---
st.sidebar.subheader("Filtros")
if "Cliente" in df.columns:
    clientes_sel = st.sidebar.multiselect(
        "Selecionar Cliente(s)", df["Cliente"].unique(), df["Cliente"].unique()
    )
    df = df[df["Cliente"].isin(clientes_sel)]

if "Agencia" in df.columns:
    agencias_sel = st.sidebar.multiselect(
        "Selecionar Agência(s)", df["Agencia"].unique(), df["Agencia"].unique()
    )
    df = df[df["Agencia"].isin(agencias_sel)]

if df.empty:
    st.warning("Sem dados para o filtro selecionado.")
    st.stop()

# --- FUNÇÃO PARA TOP 10 COM CRESCIMENTO ---
def top_entities(df, entity_col, amount_col, top_n=10):
    temp = df.groupby([entity_col, df[date_col].dt.to_period("M")]).agg(
        volume=("amount", "sum"),
        n_transacoes=("amount", "count"),
        media=("amount", "mean")
    ).reset_index()
    temp["_month_str"] = temp[date_col].astype(str)
    
    # Crescimento percentual mês a mês
    temp["crescimento_pct"] = temp.groupby(entity_col)["volume"].pct_change() * 100
    
    # Top N por volume total
    total = temp.groupby(entity_col)["volume"].sum().sort_values(ascending=False).head(top_n).reset_index()
    return temp, total

# --- Top 10 Agências ---
if "Agencia" in df.columns:
    st.subheader("🏢 Top 10 Agências com Crescimento")
    df["amount"] = df[amount_col]  # temporário para função
    monthly_agencias, top_agencias = top_entities(df, "Agencia", "amount", top_n=10)
    
    st.table(top_agencias)
    
    fig = px.bar(
        top_agencias, x="Agencia", y="volume", text="volume",
        labels={"volume":"Volume Total (R$)", "Agencia":"Agência"},
        title="Top 10 Agências por Volume"
    )
    fig.update_traces(texttemplate='%{text:,.2f}', textposition='outside')
    st.plotly_chart(fig, use_container_width=True)

# --- Top 10 Clientes ---
if "Cliente" in df.columns:
    st.subheader("👥 Top 10 Clientes com Crescimento")
    monthly_clientes, top_clientes = top_entities(df, "Cliente", "amount", top_n=10)
    
    st.table(top_clientes)
    
    fig = px.bar(
        top_clientes, x="Cliente", y="volume", text="volume",
        labels={"volume":"Volume Total (R$)", "Cliente":"Cliente"},
        title="Top 10 Clientes por Volume"
    )
    fig.update_traces(texttemplate='%{text:,.2f}', textposition='outside')
    st.plotly_chart(fig, use_container_width=True)

# --- Evolução Mensal com Média Móvel ---
st.subheader("📅 Evolução Mensal")
df["_month"] = df[date_col].dt.to_period("M")
monthly = df.groupby("_month")[amount_col].sum().reset_index()
monthly["month_str"] = monthly["_month"].astype(str)
monthly["media_movel_3m"] = monthly[amount_col].rolling(3).mean()
monthly["crescimento_pct"] = monthly[amount_col].pct_change()*100

fig = px.line(
    monthly, x="month_str", y=amount_col,
    labels={"month_str":"Mês", amount_col:"Volume (R$)"},
    title="Volume Mensal com Média Móvel (3 meses)"
)
fig.add_scatter(x=monthly["month_str"], y=monthly["media_movel_3m"], mode="lines", name="Média Móvel 3M")
st.plotly_chart(fig, use_container_width=True)

# --- Sazonalidade Semanal ---
st.subheader("📊 Sazonalidade Semanal")
weekday_map = {0:"Segunda-feira",1:"Terça-feira",2:"Quarta-feira",3:"Quinta-feira",
               4:"Sexta-feira",5:"Sábado",6:"Domingo"}
df["_weekday_pt"] = df[date_col].dt.dayofweek.map(weekday_map)
weekly = df.groupby("_weekday_pt").agg(
    n_transacoes=(amount_col,"count"),
    volume=(amount_col,"sum"),
    volume_medio=(amount_col,"mean")
).reset_index()
order = ["Segunda-feira","Terça-feira","Quarta-feira","Quinta-feira","Sexta-feira","Sábado","Domingo"]
weekly["_order"] = weekly["_weekday_pt"].apply(lambda x: order.index(x))
weekly = weekly.sort_values("_order")

fig1 = px.bar(weekly, x="_weekday_pt", y="volume", text="volume", labels={"_weekday_pt":"Dia","volume":"Volume Total (R$)"},
              title="Volume Total por Dia da Semana")
fig1.update_traces(texttemplate='%{text:,.2f}', textposition='outside')
st.plotly_chart(fig1, use_container_width=True)

fig2 = px.bar(weekly, x="_weekday_pt", y="volume_medio", text="volume_medio",
              labels={"_weekday_pt":"Dia","volume_medio":"Volume Médio (R$)"},
              title="Volume Médio por Dia da Semana")
fig2.update_traces(texttemplate='%{text:,.2f}', textposition='outside')
st.plotly_chart(fig2, use_container_width=True)

# --- Análise Horária ---
st.subheader("⏰ Análise Horária")
if df[date_col].dt.hour.nunique() > 1:
    df["_hour"] = df[date_col].dt.hour
    hourly = df.groupby("_hour").agg(
        n_transacoes=(amount_col,"count"),
        volume=(amount_col,"sum"),
        volume_medio=(amount_col,"mean")
    ).reset_index()
    fig3 = px.line(hourly, x="_hour", y="volume", title="Volume por Hora", labels={"_hour":"Hora","volume":"Volume (R$)"})
    st.plotly_chart(fig3, use_container_width=True)
    
    fig4 = px.bar(hourly, x="_hour", y="n_transacoes", title="Número de Transações por Hora", labels={"_hour":"Hora","n_transacoes":"Transações"})
    st.plotly_chart(fig4, use_container_width=True)
else:
    st.info("Informação de hora não disponível ou insuficiente.")

# --- Distribuição de Valores ---
st.subheader("💰 Distribuição de Valores")
fig5 = px.histogram(df, x=amount_col, nbins=50, labels={amount_col:"Valor (R$)"}, title="Distribuição de Valores")
st.plotly_chart(fig5, use_container_width=True)

fig6 = px.box(df, y=amount_col, labels={amount_col:"Valor (R$)"}, title="Box Plot - Valores das Transações")
st.plotly_chart(fig6, use_container_width=True)
