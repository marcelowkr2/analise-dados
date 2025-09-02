import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

st.set_page_config(page_title="Tendências | BanVic", layout="wide")

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
  font-size: 20px;
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

st.title("📈 Tendências e Insights Avançados")
st.markdown("Análise detalhada de padrões, sazonalidade e performance")

# Carregar DataFrame filtrado
df = st.session_state.get("df_filtered", pd.DataFrame())
date_col = st.session_state.get("date_col", None)
amount_col = st.session_state.get("amount_col", None)

if df.empty or date_col is None or amount_col is None:
    st.warning("Volte para a página inicial e aplique os filtros primeiro.")
    st.stop()

# --- FILTROS DINÂMICOS ---
st.sidebar.markdown('<div class="section-header"><h3>🔍 Filtros</h3></div>', unsafe_allow_html=True)

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

# --- KPIs Rápidos ---
st.markdown('<div class="section-header"><h3>📊 Métricas Principais</h3></div>', unsafe_allow_html=True)

# KPIs principais em cards modernos
st.markdown('<div class="kpi-grid">', unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

with col1:
    total_transacoes = len(df)
    st.markdown(kpi_card("Total Transações", f"{total_transacoes:,}", "💳", "metric-card-1"), unsafe_allow_html=True)

with col2:
    volume_total = df[amount_col].sum()
    st.markdown(kpi_card("Volume Total", f"R$ {volume_total:,.2f}", "💰", "metric-card-2"), unsafe_allow_html=True)

with col3:
    ticket_medio = volume_total / total_transacoes if total_transacoes > 0 else 0
    st.markdown(kpi_card("Ticket Médio", f"R$ {ticket_medio:,.2f}", "🎫", "metric-card-3"), unsafe_allow_html=True)

with col4:
    periodo_dias = (df[date_col].max() - df[date_col].min()).days
    st.markdown(kpi_card("Período Analisado", f"{periodo_dias} dias", "📅", "metric-card-4"), unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# --- FUNÇÃO PARA TOP 10 COM CRESCIMENTO ---
def top_entities(df, entity_col, amount_col, top_n=10):
    temp = df.groupby([entity_col, df[date_col].dt.to_period("M")]).agg(
        volume=(amount_col, "sum"),
        n_transacoes=(amount_col, "count"),
        media=(amount_col, "mean")
    ).reset_index()
    temp["_month_str"] = temp[date_col].astype(str)
    
    # Crescimento percentual mês a mês
    temp["crescimento_pct"] = temp.groupby(entity_col)["volume"].pct_change() * 100
    
    # Top N por volume total
    total = temp.groupby(entity_col)["volume"].sum().sort_values(ascending=False).head(top_n).reset_index()
    return temp, total

# --- Top 10 Agências ---
if "Agencia" in df.columns:
    st.markdown('<div class="section-header"><h3>🏢 Top 10 Agências</h3></div>', unsafe_allow_html=True)
    
    df["amount"] = df[amount_col]  # temporário para função
    monthly_agencias, top_agencias = top_entities(df, "Agencia", "amount", top_n=10)
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        y=top_agencias["Agencia"],
        x=top_agencias["volume"],
        orientation='h',
        marker=dict(
            color=top_agencias["volume"],
            colorscale='Viridis',
            line=dict(width=0)
        ),
        hovertemplate='<b>%{y}</b><br>Volume: R$ %{x:,.2f}<extra></extra>'
    ))
    
    fig.update_layout(
        title=dict(
            text="Top 10 Agências por Volume",
            font=dict(size=18, color='#1e293b'),
            x=0.5,
            xanchor='center'
        ),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#64748b'),
        height=500,
        xaxis=dict(
            title="Volume Total (R$)",
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
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Tabela detalhada
    st.dataframe(
        top_agencias.rename(columns={"volume": "Volume Total (R$)"}),
        use_container_width=True,
        hide_index=True
    )

# --- Top 10 Clientes ---
if "Cliente" in df.columns:
    st.markdown('<div class="section-header"><h3>👥 Top 10 Clientes</h3></div>', unsafe_allow_html=True)
    
    monthly_clientes, top_clientes = top_entities(df, "Cliente", "amount", top_n=10)
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        y=top_clientes["Cliente"],
        x=top_clientes["volume"],
        orientation='h',
        marker=dict(
            color=top_clientes["volume"],
            colorscale='Plasma',
            line=dict(width=0)
        ),
        hovertemplate='<b>%{y}</b><br>Volume: R$ %{x:,.2f}<extra></extra>'
    ))
    
    fig.update_layout(
        title=dict(
            text="Top 10 Clientes por Volume",
            font=dict(size=18, color='#1e293b'),
            x=0.5,
            xanchor='center'
        ),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#64748b'),
        height=500,
        xaxis=dict(
            title="Volume Total (R$)",
            gridcolor='#e2e8f0',
            tickformat=",.2f"
        ),
        yaxis=dict(
            title="Cliente",
            categoryorder='total ascending',
            gridcolor='#e2e8f0'
        ),
        showlegend=False
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Tabela detalhada
    st.dataframe(
        top_clientes.rename(columns={"volume": "Volume Total (R$)"}),
        use_container_width=True,
        hide_index=True
    )

# --- Evolução Mensal com Média Móvel ---
st.markdown('<div class="section-header"><h3>📅 Evolução Mensal</h3></div>', unsafe_allow_html=True)

df["_month"] = df[date_col].dt.to_period("M")
monthly = df.groupby("_month")[amount_col].sum().reset_index()
monthly["month_str"] = monthly["_month"].astype(str)
monthly["media_movel_3m"] = monthly[amount_col].rolling(3).mean()
monthly["crescimento_pct"] = monthly[amount_col].pct_change()*100

fig = go.Figure()

# Volume mensal
fig.add_trace(go.Scatter(
    x=monthly["month_str"],
    y=monthly[amount_col],
    mode='lines+markers',
    name='Volume Mensal',
    line=dict(color='#2563eb', width=3),
    marker=dict(size=8, color='#2563eb'),
    hovertemplate='<b>%{x}</b><br>Volume: R$ %{y:,.2f}<extra></extra>'
))

# Média móvel
fig.add_trace(go.Scatter(
    x=monthly["month_str"],
    y=monthly["media_movel_3m"],
    mode='lines',
    name='Média Móvel 3M',
    line=dict(color='#ef4444', width=3, dash='dash'),
    hovertemplate='<b>%{x}</b><br>Média Móvel: R$ %{y:,.2f}<extra></extra>'
))

fig.update_layout(
    title=dict(
        text="Volume Mensal com Média Móvel (3 meses)",
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

st.plotly_chart(fig, use_container_width=True)

# --- Sazonalidade Semanal ---
st.markdown('<div class="section-header"><h3>📊 Sazonalidade Semanal</h3></div>', unsafe_allow_html=True)

weekday_map = {
    0:"Segunda-feira", 1:"Terça-feira", 2:"Quarta-feira", 3:"Quinta-feira",
    4:"Sexta-feira", 5:"Sábado", 6:"Domingo"
}
df["_weekday_pt"] = df[date_col].dt.dayofweek.map(weekday_map)
weekly = df.groupby("_weekday_pt").agg(
    n_transacoes=(amount_col,"count"),
    volume=(amount_col,"sum"),
    volume_medio=(amount_col,"mean")
).reset_index()

order = ["Segunda-feira","Terça-feira","Quarta-feira","Quinta-feira","Sexta-feira","Sábado","Domingo"]
weekly["_order"] = weekly["_weekday_pt"].apply(lambda x: order.index(x))
weekly = weekly.sort_values("_order")

col1, col2 = st.columns(2)

with col1:
    fig1 = go.Figure()
    
    fig1.add_trace(go.Bar(
        x=weekly["_weekday_pt"],
        y=weekly["volume"],
        marker=dict(
            color=weekly["volume"],
            colorscale='Blues',
            line=dict(width=0)
        ),
        hovertemplate='<b>%{x}</b><br>Volume: R$ %{y:,.2f}<extra></extra>'
    ))
    
    fig1.update_layout(
        title=dict(
            text="Volume Total por Dia da Semana",
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
            title="Volume Total (R$)",
            gridcolor='#e2e8f0',
            tickformat=",.2f"
        ),
        showlegend=False
    )
    
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    fig2 = go.Figure()
    
    fig2.add_trace(go.Bar(
        x=weekly["_weekday_pt"],
        y=weekly["volume_medio"],
        marker=dict(
            color=weekly["volume_medio"],
            colorscale='Greens',
            line=dict(width=0)
        ),
        hovertemplate='<b>%{x}</b><br>Volume Médio: R$ %{y:,.2f}<extra></extra>'
    ))
    
    fig2.update_layout(
        title=dict(
            text="Volume Médio por Dia da Semana",
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
            title="Volume Médio (R$)",
            gridcolor='#e2e8f0',
            tickformat=",.2f"
        ),
        showlegend=False
    )
    
    st.plotly_chart(fig2, use_container_width=True)

# --- Análise Horária ---
st.markdown('<div class="section-header"><h3>⏰ Análise Horária</h3></div>', unsafe_allow_html=True)

if df[date_col].dt.hour.nunique() > 1:
    df["_hour"] = df[date_col].dt.hour
    hourly = df.groupby("_hour").agg(
        n_transacoes=(amount_col,"count"),
        volume=(amount_col,"sum"),
        volume_medio=(amount_col,"mean")
    ).reset_index()
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig3 = go.Figure()
        
        fig3.add_trace(go.Scatter(
            x=hourly["_hour"],
            y=hourly["volume"],
            mode='lines+markers',
            line=dict(color='#ef4444', width=3),
            marker=dict(size=8, color='#ef4444'),
            hovertemplate='<b>Hora %{x}:00</b><br>Volume: R$ %{y:,.2f}<extra></extra>'
        ))
        
        fig3.update_layout(
            title=dict(
                text="Volume por Hora",
                font=dict(size=18, color='#1e293b'),
                x=0.5,
                xanchor='center'
            ),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#64748b'),
            height=400,
            xaxis=dict(
                title="Hora do Dia",
                gridcolor='#e2e8f0'
            ),
            yaxis=dict(
                title="Volume (R$)",
                gridcolor='#e2e8f0',
                tickformat=",.2f"
            ),
            showlegend=False
        )
        
        st.plotly_chart(fig3, use_container_width=True)
    
    with col2:
        fig4 = go.Figure()
        
        fig4.add_trace(go.Bar(
            x=hourly["_hour"],
            y=hourly["n_transacoes"],
            marker=dict(
                color=hourly["n_transacoes"],
                colorscale='Purples',
                line=dict(width=0)
            ),
            hovertemplate='<b>Hora %{x}:00</b><br>Transações: %{y:,}<extra></extra>'
        ))
        
        fig4.update_layout(
            title=dict(
                text="Número de Transações por Hora",
                font=dict(size=18, color='#1e293b'),
                x=0.5,
                xanchor='center'
            ),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#64748b'),
            height=400,
            xaxis=dict(
                title="Hora do Dia",
                gridcolor='#e2e8f0'
            ),
            yaxis=dict(
                title="Nº Transações",
                gridcolor='#e2e8f0'
            ),
            showlegend=False
        )
        
        st.plotly_chart(fig4, use_container_width=True)
else:
    st.info("ℹ️ Informação de hora não disponível ou insuficiente.")

# --- Distribuição de Valores ---
st.markdown('<div class="section-header"><h3>💰 Distribuição de Valores</h3></div>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    fig5 = px.histogram(df, x=amount_col, nbins=50, 
                       labels={amount_col:"Valor da Transação (R$)", "count":"Frequência"},
                       title="Distribuição de Valores das Transações",
                       color_discrete_sequence=['#3b82f6'])
    
    fig5.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#64748b'),
        height=400,
        showlegend=False,
        xaxis=dict(tickformat=",.2f")
    )
    
    st.plotly_chart(fig5, use_container_width=True)

with col2:
    fig6 = px.box(df, y=amount_col, 
                 labels={amount_col:"Valor da Transação (R$)"}, 
                 title="Box Plot - Distribuição de Valores",
                 color_discrete_sequence=['#f59e0b'])
    
    fig6.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#64748b'),
        height=400,
        showlegend=False,
        yaxis=dict(tickformat=",.2f")
    )
    
    st.plotly_chart(fig6, use_container_width=True)

# --- Estatísticas Descritivas ---
st.markdown('<div class="section-header"><h3>📋 Estatísticas Descritivas</h3></div>', unsafe_allow_html=True)

stats = df[amount_col].describe()
stats_display = pd.DataFrame({
    'Estatística': ['Mínimo', '1º Quartil', 'Mediana', 'Média', '3º Quartil', 'Máximo', 'Desvio Padrão'],
    'Valor (R$)': [
        f"{stats['min']:,.2f}",
        f"{stats['25%']:,.2f}", 
        f"{stats['50%']:,.2f}",
        f"{stats['mean']:,.2f}",
        f"{stats['75%']:,.2f}",
        f"{stats['max']:,.2f}",
        f"{stats['std']:,.2f}"
    ]
})

st.dataframe(stats_display, use_container_width=True, hide_index=True)

# --- Footer ---
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 20px;'>
    <p>© 2024 BanVic — Análise de Tendências</p>
    <p>Desenvolvido por Marcelo Pires | 📊 Painel de Business Intelligence</p>
</div>
""", unsafe_allow_html=True)