import streamlit as st
import plotly.express as px
import pandas as pd
import numpy as np
from math import erf

st.set_page_config(page_title="Resumo | BanVic", layout="wide")

# CSS MODERNIZADO
st.markdown("""
<style>
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 16px;
        padding: 20px;
        color: white;
        text-align: center;
        box-shadow: 0 8px 25px rgba(0,0,0,0.1);
        margin-bottom: 16px;
    }
    .metric-title {
        font-size: 14px;
        font-weight: 300;
        margin-bottom: 10px;
        opacity: 0.9;
    }
    .metric-value {
        font-size: 20px;
        font-weight: 400;
        color: #ffffff;
        margin: 0;
    }
    .section-card {
        background: white;
        padding: 20px;
        border-radius: 16px;
        box-shadow: 0 8px 25px rgba(0,0,0,0.08);
        margin-bottom: 24px;
        border: none;
    }
    .section-header {
        background: linear-gradient(90deg, #4b6cb7 0%, #182848 100%);
        color: white;
        padding: 15px;
        border-radius: 12px;
        margin: 20px 0;
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
    
    /* Cores temáticas para métricas */
    .metric-card-1 { background: linear-gradient(135deg, #FF6B6B 0%, #EE5A24 100%) !important; }
    .metric-card-2 { background: linear-gradient(135deg, #36A2EB 0%, #4ECDC4 100%) !important; }
    .metric-card-3 { background: linear-gradient(135deg, #FFD93D 0%, #FF9A3D 100%) !important; }
    .metric-card-4 { background: linear-gradient(135deg, #6A11CB 0%, #2575FC 100%) !important; }
</style>
""", unsafe_allow_html=True)

def kpi_card(title, value, card_class=""):
    html = f"""
    <div class="metric-card {card_class}">
        <div class="metric-title">{title}</div>
        <div class="metric-value">{value}</div>
    </div>
    """
    return html

st.title("📊 Resumo Geral")

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

col1, col2, col3, col4 = st.columns(4)

with col1:
    total_transacoes = len(df)
    st.markdown(kpi_card("💳 Total de Transações", f"{total_transacoes:,}", "metric-card-1"), unsafe_allow_html=True)

with col2:
    volume_total = df[amount_col].sum()
    st.markdown(kpi_card("💰 Volume Total", f"R$ {volume_total:,.2f}", "metric-card-2"), unsafe_allow_html=True)

with col3:
    ticket_medio = volume_total / total_transacoes if total_transacoes > 0 else 0
    st.markdown(kpi_card("🎫 Ticket Médio", f"R$ {ticket_medio:,.2f}", "metric-card-3"), unsafe_allow_html=True)

with col4:
    dias_cobertura = (df[date_col].max() - df[date_col].min()).days
    st.markdown(kpi_card("📅 Dias Analisados", f"{dias_cobertura}", "metric-card-4"), unsafe_allow_html=True)

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

graf1 = px.bar(x=volume_por_dia.index, y=volume_por_dia.values,
               labels={"x": "Dia da Semana", "y": "Volume (R$)"},
               title="Distribuição por Dia da Semana",
               color=volume_por_dia.values,
               color_continuous_scale='Blues')

graf1.update_layout(
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    height=400
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
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(kpi_card("📊 Média Dias Pares", f"R$ {test['mean_even']:,.2f}", "metric-card-1"), unsafe_allow_html=True)
    st.caption(f"N = {len(pares)} transações")

with col2:
    st.markdown(kpi_card("📈 Média Dias Ímpares", f"R$ {test['mean_odd']:,.2f}", "metric-card-2"), unsafe_allow_html=True)
    st.caption(f"N = {len(impares)} transações")

with col3:
    diff_percent = ((test['mean_even'] - test['mean_odd']) / test['mean_odd'] * 100) if test['mean_odd'] != 0 else 0
    diff_color = "🟢" if diff_percent > 0 else "🔴"
    st.markdown(kpi_card("📉 Diferença", f"{diff_percent:+.1f}%", "metric-card-3"), unsafe_allow_html=True)
    st.caption(f"Pares vs Ímpares {diff_color}")

# Resultado estatístico
if test['p'] < 0.05:
    st.success(f"✅ **Diferença estatisticamente significativa** (p = {test['p']:.3f})")
else:
    st.info(f"ℹ️ **Diferença não estatisticamente significativa** (p = {test['p']:.3f})")

# Gráfico de comparação
volume_paridade = df.groupby("par")[amount_col].sum().rename({True:"Pares", False:"Ímpares"})
graf_paridade = px.bar(x=volume_paridade.index.map({True:"Pares", False:"Ímpares"}), y=volume_paridade.values,
                       labels={"x":"Paridade do Dia", "y":"Volume Total (R$)"},
                       title="Volume Total: Dias Pares vs Dias Ímpares",
                       color=volume_paridade.index.map({True:"Pares", False:"Ímpares"}),
                       color_discrete_sequence=['#FF6B6B', '#36A2EB'])

graf_paridade.update_layout(
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    height=400,
    showlegend=False
)

st.plotly_chart(graf_paridade, use_container_width=True)

# ----------------- Tendência Mensal -----------------
st.markdown('<div class="section-header"><h3>📈 Tendência Mensal</h3></div>', unsafe_allow_html=True)

df["mes"] = df[date_col].dt.to_period("M")
volume_mensal = df.groupby(df["mes"].astype(str))[amount_col].sum().reset_index()
volume_mensal.columns = ["Mês", "Volume"]

graf2 = px.line(volume_mensal, x="Mês", y="Volume", 
                labels={"Volume": "Volume (R$)"},
                title="Evolução do Volume Mensal",
                markers=True)

graf2.update_layout(
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    height=400
)

graf2.update_traces(line=dict(color='#4ECDC4', width=3), marker=dict(size=8, color='#4ECDC4'))

st.plotly_chart(graf2, use_container_width=True)

# ----------------- Tendência Mensal Dias Pares vs Ímpares -----------------
st.markdown('<div class="section-header"><h3>📊 Tendência Mensal: Dias Pares vs Ímpares</h3></div>', unsafe_allow_html=True)

df["mes_str"] = df["mes"].astype(str)
mensal_paridade = df.groupby(["mes_str", "par"])[amount_col].sum().reset_index()
mensal_paridade["Paridade"] = mensal_paridade["par"].map({True:"Pares", False:"Ímpares"})

graf3 = px.line(mensal_paridade, x="mes_str", y=amount_col, color="Paridade",
                labels={"mes_str":"Mês", amount_col:"Volume (R$)", "Paridade":"Tipo de Dia"},
                title="Evolução Mensal: Dias Pares vs Ímpares",
                color_discrete_map={"Pares": "#FF6B6B", "Ímpares": "#36A2EB"})

graf3.update_layout(
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    height=400
)

graf3.update_traces(line=dict(width=3), marker=dict(size=6))

st.plotly_chart(graf3, use_container_width=True)

# ----------------- Estatísticas Adicionais -----------------
st.markdown('<div class="section-header"><h3>📋 Estatísticas Detalhadas</h3></div>', unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

with col1:
    media_diaria = volume_total / dias_cobertura if dias_cobertura > 0 else 0
    st.metric("📅 Média Diária", f"R$ {media_diaria:,.2f}")

with col2:
    transacoes_dia = total_transacoes / dias_cobertura if dias_cobertura > 0 else 0
    st.metric("💳 Transações/Dia", f"{transacoes_dia:.1f}")

with col3:
    maior_dia = df.groupby(date_col)[amount_col].sum().max()
    st.metric("🚀 Maior Volume em 1 Dia", f"R$ {maior_dia:,.2f}")

with col4:
    menor_dia = df.groupby(date_col)[amount_col].sum().min()
    st.metric("📉 Menor Volume em 1 Dia", f"R$ {menor_dia:,.2f}")

# ----------------- Footer -----------------
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 20px;'>
    <p>© 2024 BanVic — Resumo Analítico</p>
    <p>Desenvolvido por Marcelo Pires | 📊 Painel de Business Intelligence</p>
</div>
""", unsafe_allow_html=True)