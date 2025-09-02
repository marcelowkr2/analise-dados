import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from math import erf

st.set_page_config(page_title="Resumo | BanVic", layout="wide")

# CSS MODERNIZADO - VERSÃO 2.0
st.markdown("""
<style>
:root {
    --primary: #2563eb;
    --primary-dark: #1d4ed8;
    --secondary: #7c3aed;
    --accent: #10b981;
    --danger: #ef4444;
    --warning: #f59e0b;
    --info: #06b6d4;
    --light: #f8fafc;
    --dark: #1e293b;
    --gray: #64748b;
    --gray-light: #e2e8f0;
}

/* page background */
[data-testid="stAppViewContainer"]{
  background: linear-gradient(135deg, #f1f5f9 0%, #e2e8f0 100%);
  font-family: 'Inter', 'Segoe UI', system-ui, sans-serif;
}

/* Main title */
h1 {
  color: var(--dark) !important;
  font-weight: 700 !important;
  margin-bottom: 0.5rem !important;
  background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

/* Metric cards */
.kpi-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
}

.metric-card {
  background: white;
  border-radius: 16px;
  padding: 20px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.08);
  border: 1px solid var(--gray-light);
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.metric-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 30px rgba(0,0,0,0.12);
}

.metric-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(90deg, var(--primary), var(--secondary));
}

.metric-title {
  color: var(--gray);
  font-size: 14px;
  margin-bottom: 8px;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 8px;
}

.metric-value {
  font-size: 24px;
  font-weight: 700;
  color: var(--dark);
  margin: 0;
  line-height: 1.2;
}

.kpi-delta {
  font-weight: 600;
  margin-top: 8px;
  font-size: 12px;
  display: flex;
  align-items: center;
  gap: 4px;
}

.kpi-delta.positive { color: var(--accent); }
.kpi-delta.negative { color: var(--danger); }

.section-card {
  background: white;
  padding: 24px;
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.08);
  border: 1px solid var(--gray-light);
  margin-bottom: 24px;
}

.section-header {
  background: linear-gradient(90deg, var(--primary) 0%, var(--primary-dark) 100%);
  color: white;
  padding: 16px 20px;
  border-radius: 12px;
  margin: 20px 0;
  font-weight: 600;
  font-size: 18px;
}

.small-muted { 
  color: var(--gray); 
  font-size: 13px; 
}

/* Sidebar styling */
[data-testid="stSidebar"] {
  background: linear-gradient(180deg, #2c3e50 0%, #3498db 50%);
}
[data-testid="stSidebar"] .stSelectbox, 
[data-testid="stSidebar"] .stDateInput,
[data-testid="stSidebar"] .stButton {
  background: white;
  border-radius: 8px;
  padding: 8px;
}

[data-testid="stSidebar"] * {
color: #FFFFFF !important;   /* branco */
font-weight: 600;            /* negrito */
font-size: 16px;             /* tamanho do texto */
}


[data-testid="stSidebar"] h2, 
[data-testid="stSidebar"] h3,
[data-testid="stSidebar"] p {
  color: black !important;
}

/* Botões principais */
.stButton button {
  background: linear-gradient(90deg, var(--primary) 0%, var(--primary-dark) 100%) !important;
  color: white !important;
  border: none !important;
  border-radius: 8px !important;
  padding: 10px 16px !important;
  font-weight: 600 !important;
  transition: all 0.3s ease !important;
}

.stButton button:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3) !important;
}

/* Cores temáticas para métricas */
.metric-card-1::before { background: linear-gradient(90deg, #ef4444 0%, #f97316 100%) !important; }
.metric-card-2::before { background: linear-gradient(90deg, #3b82f6 0%, #06b6d4 100%) !important; }
.metric-card-3::before { background: linear-gradient(90deg, #f59e0b 0%, #ec4899 100%) !important; }
.metric-card-4::before { background: linear-gradient(90deg, #8b5cf6 0%, #ec4899 100%) !important; }

/* Tabelas */
.dataframe {
  border-radius: 8px !important;
  overflow: hidden !important;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1) !important;
}

/* Gráficos container */
.js-plotly-plot .plotly, .element-container {
  border-radius: 12px;
  overflow: hidden;
}

/* Footer */
footer {
  color: var(--gray) !important;
  font-size: 14px !important;
  text-align: center !important;
  margin-top: 2rem !important;
}
</style>
""", unsafe_allow_html=True)

def kpi_card(title, value, icon="📊", card_class="", delta=None):
    val = f"{value}"
    
    delta_html = ""
    if delta is not None:
        delta_class = "positive" if delta >= 0 else "negative"
        delta_icon = "↗️" if delta >= 0 else "↘️"
        delta_html = f'<div class="kpi-delta {delta_class}">{delta_icon} {abs(delta):.1f}%</div>'
    
    html = f"""
    <div class="metric-card {card_class}">
      <div class="metric-title">{icon} {title}</div>
      <div class="metric-value">{val}</div>
      {delta_html}
    </div>
    """
    return html

st.title("📊 Resumo Geral")
st.markdown("Visão consolidada das métricas e tendências principais")

if "df_filtered" not in st.session_state:
    st.warning("Volte para a página inicial e aplique os filtros primeiro.")
    st.stop()

df = st.session_state["df_filtered"]
date_col = st.session_state["date_col"]
amount_col = st.session_state["amount_col"]

if df.empty:
    st.warning("Sem dados no período selecionado.")
    st.stop()

# ----------------- KPIs Rápidos -----------------
st.markdown('<div class="section-header"><h3>📈 Métricas Principais</h3></div>', unsafe_allow_html=True)

# KPIs principais em cards modernos
st.markdown('<div class="kpi-grid">', unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

with col1:
    total_transacoes = len(df)
    st.markdown(kpi_card("Total de Transações", f"{total_transacoes:,}", "💳", "metric-card-1"), unsafe_allow_html=True)

with col2:
    volume_total = df[amount_col].sum()
    st.markdown(kpi_card("Volume Total", f"R$ {volume_total:,.2f}", "💰", "metric-card-2"), unsafe_allow_html=True)

with col3:
    ticket_medio = volume_total / total_transacoes if total_transacoes > 0 else 0
    st.markdown(kpi_card("Ticket Médio", f"R$ {ticket_medio:,.2f}", "🎫", "metric-card-3"), unsafe_allow_html=True)

with col4:
    dias_cobertura = (df[date_col].max() - df[date_col].min()).days
    st.markdown(kpi_card("Dias Analisados", f"{dias_cobertura}", "📅", "metric-card-4"), unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# ----------------- Volume por Dia da Semana -----------------
st.markdown('<div class="section-header"><h3>📅 Volume por Dia da Semana</h3></div>', unsafe_allow_html=True)

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

graf1 = go.Figure()

graf1.add_trace(go.Bar(
    x=volume_por_dia.index,
    y=volume_por_dia.values,
    marker=dict(
        color=volume_por_dia.values,
        colorscale='Blues',
        line=dict(width=0)
    ),
    hovertemplate='<b>%{x}</b><br>Volume: R$ %{y:,.2f}<extra></extra>'
))

graf1.update_layout(
    title=dict(
        text="Distribuição por Dia da Semana",
        font=dict(size=18, color='#1e293b'),
        x=0.5,
        xanchor='center'
    ),
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    font=dict(color='#64748b'),
    height=400,
    xaxis=dict(
        title="Dia da Semana",
        gridcolor='#e2e8f0'
    ),
    yaxis=dict(
        title="Volume (R$)",
        gridcolor='#e2e8f0',
        tickformat=",.2f"
    ),
    showlegend=False
)

st.plotly_chart(graf1, use_container_width=True)

# ----------------- Dias Pares vs Ímpares -----------------
st.markdown('<div class="section-header"><h3>⚖️ Análise: Dias Pares vs Ímpares</h3></div>', unsafe_allow_html=True)

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

# Cards de comparação
st.markdown('<div class="kpi-grid">', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(kpi_card("Média Dias Pares", f"R$ {test['mean_even']:,.2f}", "📊", "metric-card-1"), unsafe_allow_html=True)
    st.caption(f"N = {len(pares)} transações")

with col2:
    st.markdown(kpi_card("Média Dias Ímpares", f"R$ {test['mean_odd']:,.2f}", "📈", "metric-card-2"), unsafe_allow_html=True)
    st.caption(f"N = {len(impares)} transações")

with col3:
    diff_percent = ((test['mean_even'] - test['mean_odd']) / test['mean_odd'] * 100) if test['mean_odd'] != 0 else 0
    diff_color = "🟢" if diff_percent > 0 else "🔴"
    st.markdown(kpi_card("Diferença", f"{diff_percent:+.1f}%", "📉", "metric-card-3"), unsafe_allow_html=True)
    st.caption(f"Pares vs Ímpares {diff_color}")

st.markdown('</div>', unsafe_allow_html=True)

# Resultado estatístico
if test['p'] < 0.05:
    st.success(f"✅ **Diferença estatisticamente significativa** (p = {test['p']:.3f})")
else:
    st.info(f"ℹ️ **Diferença não estatisticamente significativa** (p = {test['p']:.3f})")

# Gráfico de comparação
volume_paridade = df.groupby("par")[amount_col].sum().rename({True:"Pares", False:"Ímpares"})
graf_paridade = go.Figure()

graf_paridade.add_trace(go.Bar(
    x=["Pares", "Ímpares"],
    y=volume_paridade.values,
    marker=dict(
        color=['#ef4444', '#3b82f6'],
        line=dict(width=0)
    ),
    hovertemplate='<b>%{x}</b><br>Volume: R$ %{y:,.2f}<extra></extra>'
))

graf_paridade.update_layout(
    title=dict(
        text="Volume Total: Dias Pares vs Dias Ímpares",
        font=dict(size=18, color='#1e293b'),
        x=0.5,
        xanchor='center'
    ),
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    font=dict(color='#64748b'),
    height=400,
    xaxis=dict(
        title="Paridade do Dia",
        gridcolor='#e2e8f0'
    ),
    yaxis=dict(
        title="Volume Total (R$)",
        gridcolor='#e2e8f0',
        tickformat=",.2f"
    ),
    showlegend=False
)

st.plotly_chart(graf_paridade, use_container_width=True)

# ----------------- Tendência Mensal -----------------
st.markdown('<div class="section-header"><h3>📈 Tendência Mensal</h3></div>', unsafe_allow_html=True)

df["mes"] = df[date_col].dt.to_period("M")
volume_mensal = df.groupby(df["mes"].astype(str))[amount_col].sum().reset_index()
volume_mensal.columns = ["Mês", "Volume"]

graf2 = go.Figure()

graf2.add_trace(go.Scatter(
    x=volume_mensal["Mês"],
    y=volume_mensal["Volume"],
    mode='lines+markers',
    line=dict(color='#2563eb', width=3),
    marker=dict(size=8, color='#2563eb'),
    hovertemplate='<b>%{x}</b><br>Volume: R$ %{y:,.2f}<extra></extra>'
))

graf2.update_layout(
    title=dict(
        text="Evolução do Volume Mensal",
        font=dict(size=18, color='#1e293b'),
        x=0.5,
        xanchor='center'
    ),
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    font=dict(color='#64748b'),
    height=400,
    xaxis=dict(
        title="Mês",
        gridcolor='#e2e8f0'
    ),
    yaxis=dict(
        title="Volume (R$)",
        gridcolor='#e2e8f0',
        tickformat=",.2f"
    ),
    showlegend=False
)

st.plotly_chart(graf2, use_container_width=True)

# ----------------- Tendência Mensal Dias Pares vs Ímpares -----------------
st.markdown('<div class="section-header"><h3>📊 Tendência Mensal: Dias Pares vs Ímpares</h3></div>', unsafe_allow_html=True)

df["mes_str"] = df["mes"].astype(str)
mensal_paridade = df.groupby(["mes_str", "par"])[amount_col].sum().reset_index()
mensal_paridade["Paridade"] = mensal_paridade["par"].map({True:"Pares", False:"Ímpares"})

graf3 = go.Figure()

# Adicionar linha para dias pares
pares_data = mensal_paridade[mensal_paridade["Paridade"] == "Pares"]
graf3.add_trace(go.Scatter(
    x=pares_data["mes_str"],
    y=pares_data[amount_col],
    mode='lines+markers',
    name='Pares',
    line=dict(color='#ef4444', width=3),
    marker=dict(size=6, color='#ef4444'),
    hovertemplate='<b>Pares - %{x}</b><br>Volume: R$ %{y:,.2f}<extra></extra>'
))

# Adicionar linha para dias ímpares
impares_data = mensal_paridade[mensal_paridade["Paridade"] == "Ímpares"]
graf3.add_trace(go.Scatter(
    x=impares_data["mes_str"],
    y=impares_data[amount_col],
    mode='lines+markers',
    name='Ímpares',
    line=dict(color='#3b82f6', width=3),
    marker=dict(size=6, color='#3b82f6'),
    hovertemplate='<b>Ímpares - %{x}</b><br>Volume: R$ %{y:,.2f}<extra></extra>'
))

graf3.update_layout(
    title=dict(
        text="Evolução Mensal: Dias Pares vs Ímpares",
        font=dict(size=18, color='#1e293b'),
        x=0.5,
        xanchor='center'
    ),
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    font=dict(color='#64748b'),
    height=400,
    xaxis=dict(
        title="Mês",
        gridcolor='#e2e8f0'
    ),
    yaxis=dict(
        title="Volume (R$)",
        gridcolor='#e2e8f0',
        tickformat=",.2f"
    ),
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1
    )
)

st.plotly_chart(graf3, use_container_width=True)

# ----------------- Estatísticas Adicionais -----------------
st.markdown('<div class="section-header"><h3>📋 Estatísticas Detalhadas</h3></div>', unsafe_allow_html=True)

st.markdown('<div class="kpi-grid">', unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

with col1:
    media_diaria = volume_total / dias_cobertura if dias_cobertura > 0 else 0
    st.markdown(kpi_card("Média Diária", f"R$ {media_diaria:,.2f}", "📅", "metric-card-1"), unsafe_allow_html=True)

with col2:
    transacoes_dia = total_transacoes / dias_cobertura if dias_cobertura > 0 else 0
    st.markdown(kpi_card("Transações/Dia", f"{transacoes_dia:.1f}", "💳", "metric-card-2"), unsafe_allow_html=True)

with col3:
    maior_dia = df.groupby(date_col)[amount_col].sum().max()
    st.markdown(kpi_card("Maior Volume em 1 Dia", f"R$ {maior_dia:,.2f}", "🚀", "metric-card-3"), unsafe_allow_html=True)

with col4:
    menor_dia = df.groupby(date_col)[amount_col].sum().min()
    st.markdown(kpi_card("Menor Volume em 1 Dia", f"R$ {menor_dia:,.2f}", "📉", "metric-card-4"), unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# ----------------- Footer -----------------
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 20px;'>
    <p>© 2024 BanVic — Resumo Analítico</p>
    <p>Desenvolvido por Marcelo Pires | 📊 Painel de Business Intelligence</p>
</div>
""", unsafe_allow_html=True)