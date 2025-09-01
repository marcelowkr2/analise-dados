# pages/Balanco_agencias.py
import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

st.set_page_config(page_title="Balanço Agências | BanVic", page_icon="🏦", layout="wide")

# ----------------- CSS MODERNIZADO -----------------
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
        font-weight: 700;
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
    .metric-card-5 { background: linear-gradient(135deg, #00b09b 0%, #96c93d 100%) !important; }
    .metric-card-6 { background: linear-gradient(135deg, #ff5e62 0%, #ff9966 100%) !important; }
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

# ----------------- CARREGAR DADOS -----------------
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
st.markdown('<div class="section-header"><h3>📌 Indicadores por Agência</h3></div>', unsafe_allow_html=True)

df_ag = propostas_ag.groupby("cod_agencia").agg(
    qtd_propostas=("cod_proposta", "count"),
    valor_total_propostas=("valor_proposta", "sum"),
    valor_total_financiado=("valor_financiamento", "sum"),
    ticket_medio=("valor_proposta", "mean"),
).reset_index()

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown(kpi_card("🏢 Total de Agências", df_ag["cod_agencia"].nunique(), "metric-card-1"), unsafe_allow_html=True)
with col2:
    st.markdown(kpi_card("💳 Propostas Totais", int(df_ag["qtd_propostas"].sum()), "metric-card-2"), unsafe_allow_html=True)
with col3:
    st.markdown(kpi_card("💰 Volume Total Propostas", f"R$ {df_ag['valor_total_propostas'].sum():,.2f}", "metric-card-3"), unsafe_allow_html=True)
with col4:
    st.markdown(kpi_card("🎫 Ticket Médio", f"R$ {df_ag['ticket_medio'].mean():,.2f}", "metric-card-4"), unsafe_allow_html=True)

st.markdown('<div class="section-header"><h3>🏆 Detalhes por Agência</h3></div>', unsafe_allow_html=True)
st.dataframe(df_ag)

# ---------- Gráficos ----------
st.markdown('<div class="section-header"><h3>📈 Análises Visuais</h3></div>', unsafe_allow_html=True)
col1, col2 = st.columns(2)

with col1:
    fig1 = px.bar(df_ag, x="cod_agencia", y="valor_total_propostas",
                  title="Valor Total de Propostas por Agência", text_auto=".2s")
    fig1.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', height=400)
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    fig2 = px.bar(df_ag, x="cod_agencia", y="qtd_propostas",
                  title="Quantidade de Propostas por Agência", text_auto=True)
    fig2.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', height=400)
    st.plotly_chart(fig2, use_container_width=True)

# ---------- Evolução Temporal ----------
st.markdown('<div class="section-header"><h3>📆 Evolução de Propostas</h3></div>', unsafe_allow_html=True)

df_time = propostas_ag.groupby(propostas_ag["data_entrada_proposta"].dt.to_period("M")).agg(
    total_valor=("valor_proposta", "sum")
).reset_index()
df_time["mes"] = df_time["data_entrada_proposta"].dt.to_timestamp()

fig3 = px.line(df_time, x="mes", y="total_valor", markers=True,
               title="Evolução Mensal do Valor das Propostas")
fig3.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', height=450)
st.plotly_chart(fig3, use_container_width=True)

# ---------- Footer ----------
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 20px;'>
    <p>© 2024 BanVic — Balanço de Agências</p>
    <p>Desenvolvido por Marcelo Pires | 📊 Painel de Business Intelligence</p>
</div>
""", unsafe_allow_html=True)
