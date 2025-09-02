import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import numpy as np

st.set_page_config(page_title="Agências | BanVic", layout="wide")

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

def load_data_directly():
    """Carrega dados diretamente para evitar problemas de filtro"""
    try:
        # Tenta carregar os dados originais
        from Dashboard import load_data, guess_col, to_datetime_safe
        data = load_data()
        
        transacoes = data.get("transacoes")
        agencias = data.get("agencias")
        
        if transacoes is None:
            st.error("Arquivo de transações não encontrado.")
            return None, None, None
            
        # Identificar colunas
        date_col = guess_col(transacoes, ["data","date","dt","timestamp","created","datahora","datetime"])
        amount_col = guess_col(transacoes, ["valor","amount","vlr","montante","price","total","value"])
        agency_id_col = guess_col(transacoes, ["agencia","branch","agency","branch_id","cod_agencia","id_agencia"])
        
        # Processar dados
        transacoes["_dt"] = to_datetime_safe(transacoes[date_col]) if date_col in transacoes.columns else pd.NaT
        transacoes["_amt"] = pd.to_numeric(transacoes[amount_col], errors="coerce") if amount_col in transacoes.columns else pd.to_numeric(transacoes.iloc[:,0], errors="coerce")
        
        return transacoes, agencias, agency_id_col
        
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
        return None, None, None

# Verificar se temos dados na sessão OU carregar diretamente
if "df_filtered" in st.session_state:
    df = st.session_state["df_filtered"].copy()
    amount_col = st.session_state.get("amount_col", "_amt")
    date_col = st.session_state.get("date_col", "_dt")
else:
    # Carregar dados diretamente
    df, agencias, agency_id_col = load_data_directly()
    if df is None:
        st.warning("Volte para a página inicial primeiro.")
        st.stop()
    amount_col = "_amt"
    date_col = "_dt"

st.title("🏢 Análise Detalhada por Agência")

# Verificar se temos informações das agências
agencia_cols = [col for col in df.columns if col.startswith('agencia_')]
if not agencia_cols:
    st.error("Informações de agências não disponíveis.")
    st.stop()

if df.empty:
    st.warning("Sem dados no período selecionado.")
    st.stop()

# Identificar colunas de agência disponíveis
agencia_nome_col = "agencia_nome" if "agencia_nome" in df.columns else None
agencia_uf_col = "agencia_uf" if "agencia_uf" in df.columns else None
agencia_tipo_col = "agencia_tipo" if "agencia_tipo" in df.columns else None
agencia_cidade_col = "agencia_cidade" if "agencia_cidade" in df.columns else None

# Usar TODOS os dados disponíveis (não aplicar filtro de tempo)
last6 = df.copy()

if last6.empty:
    st.warning("Não há dados disponíveis.")
    st.stop()

# Calcular saques (assumindo que valores negativos são saques)
last6["eh_saque"] = last6[amount_col] < 0

# Lista de colunas para agrupamento
group_cols = []
if agencia_nome_col: group_cols.append(agencia_nome_col)
if agencia_uf_col: group_cols.append(agencia_uf_col)
if agencia_tipo_col: group_cols.append(agencia_tipo_col)
if agencia_cidade_col: group_cols.append(agencia_cidade_col)

# Agrupar por agência com todas as informações disponíveis
agrupamento = last6.groupby(group_cols).agg(
    num_transacoes=(amount_col, "count"),
    total_saques=("eh_saque", "sum"),
    arrecadacao_total=(amount_col, "sum"),
    ticket_medio=(amount_col, "mean"),
    volume_total_positivo=(amount_col, lambda x: x[x > 0].sum()),
    volume_total_negativo=(amount_col, lambda x: x[x < 0].sum())
).reset_index().sort_values("num_transacoes", ascending=False)

# Calcular métricas adicionais
agrupamento["percentual_saques"] = (agrupamento["total_saques"] / agrupamento["num_transacoes"] * 100).round(1)
agrupamento["saldo_liquido"] = agrupamento["volume_total_positivo"] + agrupamento["volume_total_negativo"]

st.markdown('<div class="section-header"><h3>📊 Métricas Principais</h3></div>', unsafe_allow_html=True)

# KPIs principais em cards modernos
st.markdown('<div class="kpi-grid">', unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown(kpi_card("Total Agências", f"{len(agrupamento):,}", "🏢", "metric-card-1"), unsafe_allow_html=True)
with col2:
    total_trans = agrupamento["num_transacoes"].sum()
    st.markdown(kpi_card("Total Transações", f"{total_trans:,}", "💳", "metric-card-2"), unsafe_allow_html=True)
with col3:
    total_saques = agrupamento["total_saques"].sum()
    st.markdown(kpi_card("Total Saques", f"{total_saques:,}", "💰", "metric-card-3"), unsafe_allow_html=True)
with col4:
    total_arrecadacao = agrupamento["arrecadacao_total"].sum()
    st.markdown(kpi_card("Arrecadação Total", f"R$ {total_arrecadacao:,.2f}", "📈", "metric-card-4"), unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# Filtros
st.markdown('<div class="section-header"><h3>🔍 Filtros</h3></div>', unsafe_allow_html=True)
col1, col2, col3, col4 = st.columns(4)

with col1:
    if agencia_uf_col:
        uf_options = ["Todas"] + sorted(agrupamento[agencia_uf_col].dropna().unique().tolist())
        uf_selecionado = st.selectbox("Filtrar por UF:", uf_options)
    else:
        uf_selecionado = "Todas"
        st.info("UF não disponível")

with col2:
    if agencia_tipo_col:
        tipo_options = ["Todos"] + sorted(agrupamento[agencia_tipo_col].dropna().unique().tolist())
        tipo_selecionado = st.selectbox("Filtrar por Tipo:", tipo_options)
    else:
        tipo_selecionado = "Todos"
        st.info("Tipo não disponível")

with col3:
    # Filtro por volume mínimo
    volume_min = st.number_input("Volume Mínimo (R$):", 
                               min_value=0, 
                               max_value=int(agrupamento["arrecadacao_total"].max()),
                               value=0,
                               step=1000)

with col4:
    # Ordenação
    ordenacao = st.selectbox("Ordenar por:", 
                           ["Nº Transações (↓)", "Arrecadação (↓)", "Ticket Médio (↓)", 
                            "Nº Transações (↑)", "Arrecadação (↑)", "Ticket Médio (↑)"])

# Aplicar filtros
agrupamento_filtrado = agrupamento.copy()

if uf_selecionado != "Todas" and agencia_uf_col:
    agrupamento_filtrado = agrupamento_filtrado[agrupamento_filtrado[agencia_uf_col] == uf_selecionado]

if tipo_selecionado != "Todos" and agencia_tipo_col:
    agrupamento_filtrado = agrupamento_filtrado[agrupamento_filtrado[agencia_tipo_col] == tipo_selecionado]

# Filtro por volume
agrupamento_filtrado = agrupamento_filtrado[agrupamento_filtrado["arrecadacao_total"] >= volume_min]

# Ordenação
if ordenacao == "Nº Transações (↓)":
    agrupamento_filtrado = agrupamento_filtrado.sort_values("num_transacoes", ascending=False)
elif ordenacao == "Arrecadação (↓)":
    agrupamento_filtrado = agrupamento_filtrado.sort_values("arrecadacao_total", ascending=False)
elif ordenacao == "Ticket Médio (↓)":
    agrupamento_filtrado = agrupamento_filtrado.sort_values("ticket_medio", ascending=False)
elif ordenacao == "Nº Transações (↑)":
    agrupamento_filtrado = agrupamento_filtrado.sort_values("num_transacoes", ascending=True)
elif ordenacao == "Arrecadação (↑)":
    agrupamento_filtrado = agrupamento_filtrado.sort_values("arrecadacao_total", ascending=True)
elif ordenacao == "Ticket Médio (↑)":
    agrupamento_filtrado = agrupamento_filtrado.sort_values("ticket_medio", ascending=True)

st.markdown('<div class="section-header"><h3>🏆 Ranking de Agências</h3></div>', unsafe_allow_html=True)

# Tabela completa com TODAS as agências
agrupamento_display = agrupamento_filtrado.copy()
agrupamento_display["arrecadacao_total"] = agrupamento_display["arrecadacao_total"].round(2)
agrupamento_display["ticket_medio"] = agrupamento_display["ticket_medio"].round(2)
agrupamento_display["volume_total_positivo"] = agrupamento_display["volume_total_positivo"].round(2)
agrupamento_display["volume_total_negativo"] = agrupamento_display["volume_total_negativo"].round(2)
agrupamento_display["saldo_liquido"] = agrupamento_display["saldo_liquido"].round(2)

# Adicionar ranking
agrupamento_display["Ranking"] = range(1, len(agrupamento_display) + 1)

# Configuração das colunas
column_config = {
    "Ranking": st.column_config.NumberColumn("Rank", format="%d", width="small"),
    agencia_nome_col: st.column_config.TextColumn("Agência", width="large"),
    "num_transacoes": st.column_config.NumberColumn("Nº Transações", format="%d", width="medium"),
    "total_saques": st.column_config.NumberColumn("Saques", format="%d", width="small"),
    "percentual_saques": st.column_config.NumberColumn("% Saques", format="%.1f%%", width="small"),
    "arrecadacao_total": st.column_config.NumberColumn("Arrecadação Total", format="R$ %.2f", width="medium"),
    "volume_total_positivo": st.column_config.NumberColumn("Entradas", format="R$ %.2f", width="medium"),
    "volume_total_negativo": st.column_config.NumberColumn("Saídas", format="R$ %.2f", width="medium"),
    "saldo_liquido": st.column_config.NumberColumn("Saldo Líquido", format="R$ %.2f", width="medium"),
    "ticket_medio": st.column_config.NumberColumn("Ticket Médio", format="R$ %.2f", width="medium")
}

# Adicionar colunas adicionais se disponíveis
if agencia_uf_col:
    column_config[agencia_uf_col] = st.column_config.TextColumn("UF", width="small")
if agencia_tipo_col:
    column_config[agencia_tipo_col] = st.column_config.TextColumn("Tipo", width="medium")
if agencia_cidade_col:
    column_config[agencia_cidade_col] = st.column_config.TextColumn("Cidade", width="medium")

# Reordenar colunas para visualização melhor
colunas_ordenadas = ["Ranking", agencia_nome_col]
if agencia_uf_col: colunas_ordenadas.append(agencia_uf_col)
if agencia_tipo_col: colunas_ordenadas.append(agencia_tipo_col)
if agencia_cidade_col: colunas_ordenadas.append(agencia_cidade_col)
colunas_ordenadas.extend([
    "num_transacoes", "total_saques", "percentual_saques",
    "arrecadacao_total", "volume_total_positivo", "volume_total_negativo",
    "saldo_liquido", "ticket_medio"
])

# Mostrar estatísticas de resumo
st.info(f"**Resumo:** {len(agrupamento_filtrado)} agências | "
        f"Transações: {agrupamento_filtrado['num_transacoes'].sum():,} | "
        f"Arrecadação: R$ {agrupamento_filtrado['arrecadacao_total'].sum():,.2f}")

# Tabela com todas as agências
st.dataframe(
    agrupamento_display[colunas_ordenadas],
    column_config=column_config,
    use_container_width=True,
    height=600
)

# Download dos dados
csv = agrupamento_display[colunas_ordenadas].to_csv(index=False, encoding='utf-8-sig')
st.download_button(
    label="📥 Download CSV Completo",
    data=csv,
    file_name="detalhes_agencias_completo.csv",
    mime="text/csv",
    use_container_width=True
)

# Gráficos comparativos
st.markdown('<div class="section-header"><h3>📊 Visualizações Comparativas</h3></div>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    # Top 20 agências por transações
    top_20 = agrupamento_filtrado.head(20).sort_values("num_transacoes", ascending=True)
    fig1 = go.Figure()
    
    fig1.add_trace(go.Bar(
        y=top_20[agencia_nome_col],
        x=top_20["num_transacoes"],
        orientation='h',
        marker=dict(
            color=top_20["num_transacoes"],
            colorscale='Blues',
            line=dict(width=0)
        ),
        hovertemplate='<b>%{y}</b><br>Transações: %{x:,}<br>Ticket Médio: R$ %{customdata:.2f}<extra></extra>',
        customdata=top_20['ticket_medio']
    ))
    
    fig1.update_layout(
        title=dict(
            text="Top 20 Agências - Nº de Transações",
            font=dict(size=18, color='#1e293b'),
            x=0.5,
            xanchor='center'
        ),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#64748b'),
        height=400,
        xaxis=dict(
            title="Nº Transações",
            gridcolor='#e2e8f0'
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
    # Top 20 agências por arrecadação
    top_20_arrecadacao = agrupamento_filtrado.head(20).sort_values("arrecadacao_total", ascending=True)
    fig2 = go.Figure()
    
    fig2.add_trace(go.Bar(
        y=top_20_arrecadacao[agencia_nome_col],
        x=top_20_arrecadacao["arrecadacao_total"],
        orientation='h',
        marker=dict(
            color=top_20_arrecadacao["arrecadacao_total"],
            colorscale='Viridis',
            line=dict(width=0)
        ),
        hovertemplate='<b>%{y}</b><br>Arrecadação: R$ %{x:,.2f}<br>Transações: %{customdata:,}<extra></extra>',
        customdata=top_20_arrecadacao['num_transacoes']
    ))
    
    fig2.update_layout(
        title=dict(
            text="Top 20 Agências - Arrecadação",
            font=dict(size=18, color='#1e293b'),
            x=0.5,
            xanchor='center'
        ),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#64748b'),
        height=400,
        xaxis=dict(
            title="Arrecadação (R$)",
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
    
    st.plotly_chart(fig2, use_container_width=True)

# Scatter plot comparativo
st.markdown('<div class="section-header"><h3>📈 Relação entre Transações e Arrecadação</h3></div>', unsafe_allow_html=True)

fig3 = px.scatter(agrupamento_filtrado, 
                 x="num_transacoes", 
                 y="arrecadacao_total",
                 size="ticket_medio",
                 color=agencia_uf_col if agencia_uf_col else None,
                 hover_name=agencia_nome_col,
                 title="Relação: Transações vs Arrecadação",
                 labels={
                     "num_transacoes": "Número de Transações",
                     "arrecadacao_total": "Arrecadação Total (R$)",
                     "ticket_medio": "Ticket Médio",
                     agencia_uf_col: "UF" if agencia_uf_col else None
                 })
    
fig3.update_layout(
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    font=dict(color='#64748b'),
    height=500
)

st.plotly_chart(fig3, use_container_width=True)

# Análise por UF se disponível
if agencia_uf_col:
    st.markdown('<div class="section-header"><h3>🗺️ Análise por UF</h3></div>', unsafe_allow_html=True)
    
    por_uf = agrupamento_filtrado.groupby(agencia_uf_col).agg(
        num_agencias=(agencia_nome_col, "nunique"),
        num_transacoes=("num_transacoes", "sum"),
        total_arrecadacao=("arrecadacao_total", "sum"),
        media_ticket=("ticket_medio", "mean")
    ).reset_index().sort_values("total_arrecadacao", ascending=False)
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig4 = go.Figure()
        
        fig4.add_trace(go.Bar(
            x=por_uf[agencia_uf_col],
            y=por_uf["num_agencias"],
            marker=dict(
                color=por_uf["num_agencias"],
                colorscale='Purples',
                line=dict(width=0)
            ),
            hovertemplate='<b>%{x}</b><br>Agências: %{y}<br>Arrecadação Total: R$ %{customdata:,.2f}<extra></extra>',
            customdata=por_uf['total_arrecadacao']
        ))
        
        fig4.update_layout(
            title=dict(
                text="Número de Agências por UF",
                font=dict(size=18, color='#1e293b'),
                x=0.5,
                xanchor='center'
            ),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#64748b'),
            height=400,
            xaxis=dict(
                title="UF",
                gridcolor='#e2e8f0'
            ),
            yaxis=dict(
                title="Nº Agências",
                gridcolor='#e2e8f0'
            ),
            showlegend=False
        )
        
        st.plotly_chart(fig4, use_container_width=True)
    
    with col2:
        fig5 = go.Figure()
        
        fig5.add_trace(go.Bar(
            x=por_uf[agencia_uf_col],
            y=por_uf["total_arrecadacao"],
            marker=dict(
                color=por_uf["total_arrecadacao"],
                colorscale='Greens',
                line=dict(width=0)
            ),
            hovertemplate='<b>%{x}</b><br>Arrecadação: R$ %{y:,.2f}<br>Agências: %{customdata}<extra></extra>',
            customdata=por_uf['num_agencias']
        ))
        
        fig5.update_layout(
            title=dict(
                text="Arrecadação Total por UF",
                font=dict(size=18, color='#1e293b'),
                x=0.5,
                xanchor='center'
            ),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#64748b'),
            height=400,
            xaxis=dict(
                title="UF",
                gridcolor='#e2e8f0'
            ),
            yaxis=dict(
                title="Arrecadação Total (R$)",
                gridcolor='#e2e8f0',
                tickformat=",.2f"
            ),
            showlegend=False
        )
        
        st.plotly_chart(fig5, use_container_width=True)

# Estatísticas gerais
st.markdown('<div class="section-header"><h3>📊 Estatísticas Gerais</h3></div>', unsafe_allow_html=True)

st.markdown('<div class="kpi-grid">', unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(kpi_card("Média Transações/Agência", f"{agrupamento_filtrado['num_transacoes'].mean():.0f}", "📊", "metric-card-1"), unsafe_allow_html=True)
with col2:
    st.markdown(kpi_card("Média Arrecadação/Agência", f"R$ {agrupamento_filtrado['arrecadacao_total'].mean():,.2f}", "💰", "metric-card-2"), unsafe_allow_html=True)
with col3:
    st.markdown(kpi_card("Média Ticket Médio", f"R$ {agrupamento_filtrado['ticket_medio'].mean():,.2f}", "🎫", "metric-card-3"), unsafe_allow_html=True)
with col4:
    st.markdown(kpi_card("Taxa Média de Saques", f"{agrupamento_filtrado['percentual_saques'].mean():.1f}%", "📉", "metric-card-4"), unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# Distribuição dos valores
st.markdown('<div class="section-header"><h3>📈 Distribuição dos Valores</h3></div>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    fig6 = px.histogram(agrupamento_filtrado, x="num_transacoes", 
                       title="Distribuição do Número de Transações",
                       labels={"num_transacoes": "Nº Transações", "count": "Nº Agências"},
                       color_discrete_sequence=['#FF6B6B'])
    
    fig6.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#64748b'),
        height=400,
        showlegend=False
    )
    
    st.plotly_chart(fig6, use_container_width=True)

with col2:
    fig7 = px.histogram(agrupamento_filtrado, x="arrecadacao_total", 
                       title="Distribuição da Arrecadação",
                       labels={"arrecadacao_total": "Arrecadação (R$)", "count": "Nº Agências"},
                       color_discrete_sequence=['#36A2EB'])
    
    fig7.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#64748b'),
        height=400,
        showlegend=False
    )
    
    st.plotly_chart(fig7, use_container_width=True)

# Busca rápida por agência específica
st.markdown('<div class="section-header"><h3>🔍 Buscar Agência Específica</h3></div>', unsafe_allow_html=True)

if agencia_nome_col:
    agencia_busca = st.selectbox("Digite o nome da agência:", 
                               [""] + sorted(agrupamento_filtrado[agencia_nome_col].unique().tolist()))
    
    if agencia_busca:
        agencia_info = agrupamento_filtrado[agrupamento_filtrado[agencia_nome_col] == agencia_busca].iloc[0]
        
        st.success(f"**Informações detalhadas de {agencia_busca}:**")
        
        st.markdown('<div class="kpi-grid">', unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(kpi_card("Ranking", f"#{agrupamento_filtrado[agrupamento_filtrado[agencia_nome_col] == agencia_busca].index[0] + 1}", "🏆", "metric-card-1"), unsafe_allow_html=True)
        with col2:
            st.markdown(kpi_card("Nº Transações", f"{agencia_info['num_transacoes']:,}", "💳", "metric-card-2"), unsafe_allow_html=True)
        with col3:
            st.markdown(kpi_card("Arrecadação Total", f"R$ {agencia_info['arrecadacao_total']:,.2f}", "💰", "metric-card-3"), unsafe_allow_html=True)
        with col4:
            st.markdown(kpi_card("Ticket Médio", f"R$ {agencia_info['ticket_medio']:,.2f}", "🎫", "metric-card-4"), unsafe_allow_html=True)
        
        col5, col6, col7, col8 = st.columns(4)
        
        with col5:
            st.markdown(kpi_card("Total Saques", f"{agencia_info['total_saques']:,}", "📉", "metric-card-5"), unsafe_allow_html=True)
        with col6:
            st.markdown(kpi_card("% Saques", f"{agencia_info['percentual_saques']}%", "📊", "metric-card-6"), unsafe_allow_html=True)
        with col7:
            st.markdown(kpi_card("Saldo Líquido", f"R$ {agencia_info['saldo_liquido']:,.2f}", "⚖️", "metric-card-1"), unsafe_allow_html=True)
        with col8:
            if agencia_uf_col:
                st.markdown(kpi_card("UF", agencia_info[agencia_uf_col], "📍", "metric-card-2"), unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 20px;'>
    <p>© 2024 BanVic — Análise de Agências</p>
    <p>Desenvolvido por Marcelo Pires | 📊 Painel de Business Intelligence</p>
</div>
""", unsafe_allow_html=True)