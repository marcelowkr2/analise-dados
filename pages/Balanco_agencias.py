# pages/Balanco_agencias.py
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

st.set_page_config(page_title="Balanço Agências | BanVic", page_icon="🏦", layout="wide")

# ----------------- CSS MODERNIZADO - VERSÃO 2.0 -----------------
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
  font-size: 20px;
  font-weight: 600;
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
  background: linear-gradient(180deg, var(--dark) 0%, var(--primary-dark) 100%);
}

[data-testid="stSidebar"] .stSelectbox, 
[data-testid="stSidebar"] .stDateInput,
[data-testid="stSidebar"] .stButton {
  background: white;
  border-radius: 8px;
  padding: 8px;
  border: 1px solid var(--gray-light);
}

[data-testid="stSidebar"] * {
  color: #FFFFFF !important;
  font-weight: 500 !important;
  font-size: 14px !important;
}

[data-testid="stSidebar"] .stButton button {
  background: linear-gradient(90deg, var(--accent) 0%, #0ca678 100%) !important;
  color: white !important;
  border: none !important;
  border-radius: 8px !important;
  padding: 10px 16px !important;
  font-weight: 600 !important;
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
.metric-card-5::before { background: linear-gradient(90deg, #00b09b 0%, #96c93d 100%) !important; }
.metric-card-6::before { background: linear-gradient(90deg, #ff5e62 0%, #ff9966 100%) !important; }

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
st.title("🏦 Balanço de Agências")
st.markdown("Análise detalhada de propostas de crédito e performance por agência")

st.markdown('<div class="section-header"><h3>📌 Indicadores por Agência</h3></div>', unsafe_allow_html=True)

df_ag = propostas_ag.groupby("cod_agencia").agg(
    qtd_propostas=("cod_proposta", "count"),
    valor_total_propostas=("valor_proposta", "sum"),
    valor_total_financiado=("valor_financiamento", "sum"),
    ticket_medio=("valor_proposta", "mean"),
).reset_index()

# KPIs principais em cards modernos
st.markdown('<div class="kpi-grid">', unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown(kpi_card("Total de Agências", df_ag["cod_agencia"].nunique(), "🏢", "metric-card-1"), unsafe_allow_html=True)
with col2:
    st.markdown(kpi_card("Propostas Totais", f"{int(df_ag['qtd_propostas'].sum()):,}", "💳", "metric-card-2"), unsafe_allow_html=True)
with col3:
    st.markdown(kpi_card("Volume Total Propostas", f"R$ {df_ag['valor_total_propostas'].sum():,.2f}", "💰", "metric-card-3"), unsafe_allow_html=True)
with col4:
    st.markdown(kpi_card("Ticket Médio", f"R$ {df_ag['ticket_medio'].mean():,.2f}", "🎫", "metric-card-4"), unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# ---------- Filtros ----------
st.markdown('<div class="section-header"><h3>🔍 Filtros</h3></div>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    # Filtro por quantidade mínima de propostas
    min_propostas = st.slider("Mínimo de Propostas:", 
                            min_value=0, 
                            max_value=int(df_ag["qtd_propostas"].max()),
                            value=0,
                            step=5)

with col2:
    # Ordenação
    ordenacao = st.selectbox("Ordenar por:", 
                           ["Quantidade Propostas (↓)", "Valor Total (↓)", "Ticket Médio (↓)", 
                            "Quantidade Propostas (↑)", "Valor Total (↑)", "Ticket Médio (↑)"])

# Aplicar filtros
df_ag_filtrado = df_ag[df_ag["qtd_propostas"] >= min_propostas].copy()

# Ordenação
if ordenacao == "Quantidade Propostas (↓)":
    df_ag_filtrado = df_ag_filtrado.sort_values("qtd_propostas", ascending=False)
elif ordenacao == "Valor Total (↓)":
    df_ag_filtrado = df_ag_filtrado.sort_values("valor_total_propostas", ascending=False)
elif ordenacao == "Ticket Médio (↓)":
    df_ag_filtrado = df_ag_filtrado.sort_values("ticket_medio", ascending=False)
elif ordenacao == "Quantidade Propostas (↑)":
    df_ag_filtrado = df_ag_filtrado.sort_values("qtd_propostas", ascending=True)
elif ordenacao == "Valor Total (↑)":
    df_ag_filtrado = df_ag_filtrado.sort_values("valor_total_propostas", ascending=True)
elif ordenacao == "Ticket Médio (↑)":
    df_ag_filtrado = df_ag_filtrado.sort_values("ticket_medio", ascending=True)

# ---------- Tabela Detalhada ----------
st.markdown('<div class="section-header"><h3>🏆 Detalhes por Agência</h3></div>', unsafe_allow_html=True)

# Formatar valores para exibição
df_display = df_ag_filtrado.copy()
df_display["valor_total_propostas"] = df_display["valor_total_propostas"].apply(lambda x: f"R$ {x:,.2f}")
df_display["valor_total_financiado"] = df_display["valor_total_financiado"].apply(lambda x: f"R$ {x:,.2f}")
df_display["ticket_medio"] = df_display["ticket_medio"].apply(lambda x: f"R$ {x:,.2f}")

# Adicionar ranking
df_display["Ranking"] = range(1, len(df_display) + 1)

# Configuração das colunas
column_config = {
    "Ranking": st.column_config.NumberColumn("Rank", format="%d", width="small"),
    "cod_agencia": st.column_config.TextColumn("Código Agência", width="medium"),
    "qtd_propostas": st.column_config.NumberColumn("Qtd Propostas", format="%d", width="medium"),
    "valor_total_propostas": st.column_config.TextColumn("Valor Total Propostas", width="large"),
    "valor_total_financiado": st.column_config.TextColumn("Valor Financiado", width="large"),
    "ticket_medio": st.column_config.TextColumn("Ticket Médio", width="medium")
}

st.dataframe(
    df_display[["Ranking", "cod_agencia", "qtd_propostas", "valor_total_propostas", "valor_total_financiado", "ticket_medio"]],
    column_config=column_config,
    use_container_width=True,
    height=400
)

# Download dos dados
csv = df_ag_filtrado.to_csv(index=False, encoding='utf-8-sig')
st.download_button(
    label="📥 Download CSV Completo",
    data=csv,
    file_name="balanco_agencias.csv",
    mime="text/csv",
    use_container_width=True
)

# ---------- Gráficos ----------
st.markdown('<div class="section-header"><h3>📈 Análises Visuais</h3></div>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    # Top 10 agências por valor total
    top_10_valor = df_ag_filtrado.head(10).sort_values("valor_total_propostas", ascending=True)
    
    fig1 = go.Figure()
    
    fig1.add_trace(go.Bar(
        y=top_10_valor["cod_agencia"].astype(str),
        x=top_10_valor["valor_total_propostas"],
        orientation='h',
        marker=dict(
            color=top_10_valor["valor_total_propostas"],
            colorscale='Viridis',
            line=dict(width=0)
        ),
        hovertemplate='<b>Agência %{y}</b><br>Valor: R$ %{x:,.2f}<br>Propostas: %{customdata:,}<extra></extra>',
        customdata=top_10_valor['qtd_propostas']
    ))
    
    fig1.update_layout(
        title=dict(
            text="Top 10 Agências - Valor Total de Propostas",
            font=dict(size=18, color='#1e293b'),
            x=0.5,
            xanchor='center'
        ),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#64748b'),
        height=400,
        xaxis=dict(
            title="Valor Total (R$)",
            gridcolor='#e2e8f0',
            tickformat=",.2f"
        ),
        yaxis=dict(
            title="Agência",
            categoryorder='total ascending',
            gridcolor='#e2e8f0'
        ),
        showlegend=False
    )
    
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    # Top 10 agências por quantidade
    top_10_qtd = df_ag_filtrado.head(10).sort_values("qtd_propostas", ascending=True)
    
    fig2 = go.Figure()
    
    fig2.add_trace(go.Bar(
        y=top_10_qtd["cod_agencia"].astype(str),
        x=top_10_qtd["qtd_propostas"],
        orientation='h',
        marker=dict(
            color=top_10_qtd["qtd_propostas"],
            colorscale='Blues',
            line=dict(width=0)
        ),
        hovertemplate='<b>Agência %{y}</b><br>Propostas: %{x:,}<br>Valor Total: R$ %{customdata:,.2f}<extra></extra>',
        customdata=top_10_qtd['valor_total_propostas']
    ))
    
    fig2.update_layout(
        title=dict(
            text="Top 10 Agências - Quantidade de Propostas",
            font=dict(size=18, color='#1e293b'),
            x=0.5,
            xanchor='center'
        ),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#64748b'),
        height=400,
        xaxis=dict(
            title="Quantidade de Propostas",
            gridcolor='#e2e8f0'
        ),
        yaxis=dict(
            title="Agência",
            categoryorder='total ascending',
            gridcolor='#e2e8f0'
        ),
        showlegend=False
    )
    
    st.plotly_chart(fig2, use_container_width=True)

# ---------- Evolução Temporal ----------
st.markdown('<div class="section-header"><h3>📆 Evolução de Propostas</h3></div>', unsafe_allow_html=True)

df_time = propostas_ag.groupby(propostas_ag["data_entrada_proposta"].dt.to_period("M")).agg(
    total_valor=("valor_proposta", "sum"),
    total_propostas=("cod_proposta", "count")
).reset_index()
df_time["mes"] = df_time["data_entrada_proposta"].dt.to_timestamp()

# Criar gráfico com eixos duplos
fig3 = make_subplots(specs=[[{"secondary_y": True}]])

# Adicionar linha do valor total
fig3.add_trace(
    go.Scatter(
        x=df_time["mes"],
        y=df_time["total_valor"],
        name="Valor Total (R$)",
        line=dict(color="#2563eb", width=3),
        hovertemplate='<b>%{x|%b/%Y}</b><br>Valor: R$ %{y:,.2f}<extra></extra>'
    ),
    secondary_y=False,
)

# Adicionar barras da quantidade
fig3.add_trace(
    go.Bar(
        x=df_time["mes"],
        y=df_time["total_propostas"],
        name="Quantidade Propostas",
        marker_color="#10b981",
        opacity=0.6,
        hovertemplate='<b>%{x|%b/%Y}</b><br>Propostas: %{y:,}<extra></extra>'
    ),
    secondary_y=True,
)

fig3.update_layout(
    title=dict(
        text="Evolução Mensal - Valor e Quantidade de Propostas",
        font=dict(size=18, color='#1e293b'),
        x=0.5,
        xanchor='center'
    ),
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    font=dict(color='#64748b'),
    height=450,
    xaxis=dict(
        title="Mês",
        gridcolor='#e2e8f0'
    ),
    yaxis=dict(
        title="Valor Total (R$)",
        gridcolor='#e2e8f0',
        tickformat=",.2f"
    ),
    yaxis2=dict(
        title="Quantidade de Propostas",
        gridcolor='#e2e8f0',
        side="right"
    ),
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1
    )
)

st.plotly_chart(fig3, use_container_width=True)

# ---------- Distribuição de Tickets ----------
st.markdown('<div class="section-header"><h3>📊 Distribuição de Valores</h3></div>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    # Histograma de valores das propostas
    fig4 = px.histogram(df_ag_filtrado, x="valor_total_propostas", 
                       title="Distribuição do Valor Total por Agência",
                       labels={"valor_total_propostas": "Valor Total (R$)", "count": "Nº Agências"},
                       color_discrete_sequence=['#3b82f6'])
    
    fig4.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#64748b'),
        height=400,
        showlegend=False,
        xaxis=dict(tickformat=",.2f")
    )
    
    st.plotly_chart(fig4, use_container_width=True)

with col2:
    # Histograma de quantidade de propostas
    fig5 = px.histogram(df_ag_filtrado, x="qtd_propostas", 
                       title="Distribuição da Quantidade por Agência",
                       labels={"qtd_propostas": "Quantidade de Propostas", "count": "Nº Agências"},
                       color_discrete_sequence=['#ef4444'])
    
    fig5.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#64748b'),
        height=400,
        showlegend=False
    )
    
    st.plotly_chart(fig5, use_container_width=True)

# ---------- Footer ----------
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 20px;'>
    <p>© 2024 BanVic — Balanço de Agências</p>
    <p>Desenvolvido por Marcelo Pires | 📊 Painel de Business Intelligence</p>
</div>
""", unsafe_allow_html=True)