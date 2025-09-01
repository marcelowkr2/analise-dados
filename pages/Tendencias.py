import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

st.set_page_config(page_title="Tendências | BanVic", layout="wide")

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

st.title("📈 Tendências e Insights Avançados")

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

col1, col2, col3, col4 = st.columns(4)

with col1:
    total_transacoes = len(df)
    st.markdown(kpi_card("💳 Total Transações", f"{total_transacoes:,}", "metric-card-1"), unsafe_allow_html=True)

with col2:
    volume_total = df[amount_col].sum()
    st.markdown(kpi_card("💰 Volume Total", f"R$ {volume_total:,.2f}", "metric-card-2"), unsafe_allow_html=True)

with col3:
    ticket_medio = volume_total / total_transacoes if total_transacoes > 0 else 0
    st.markdown(kpi_card("🎫 Ticket Médio", f"R$ {ticket_medio:,.2f}", "metric-card-3"), unsafe_allow_html=True)

with col4:
    periodo_dias = (df[date_col].max() - df[date_col].min()).days
    st.markdown(kpi_card("📅 Período Analisado", f"{periodo_dias} dias", "metric-card-4"), unsafe_allow_html=True)

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
    
    fig = px.bar(
        top_agencias.sort_values("volume", ascending=True), 
        x="volume", y="Agencia", orientation='h',
        labels={"volume":"Volume Total (R$)", "Agencia":"Agência"},
        title="Top 10 Agências por Volume",
        color="volume",
        color_continuous_scale='Viridis'
    )
    
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        height=500
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
    
    fig = px.bar(
        top_clientes.sort_values("volume", ascending=True), 
        x="volume", y="Cliente", orientation='h',
        labels={"volume":"Volume Total (R$)", "Cliente":"Cliente"},
        title="Top 10 Clientes por Volume",
        color="volume",
        color_continuous_scale='Plasma'
    )
    
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        height=500
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

fig = px.line(
    monthly, x="month_str", y=amount_col,
    labels={"month_str":"Mês", amount_col:"Volume (R$)"},
    title="Volume Mensal com Média Móvel (3 meses)",
    color_discrete_sequence=['#4ECDC4']
)

fig.add_scatter(
    x=monthly["month_str"], y=monthly["media_movel_3m"], 
    mode="lines", name="Média Móvel 3M",
    line=dict(color='#FF6B6B', width=3, dash='dash')
)

fig.update_layout(
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    height=400
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
    fig1 = px.bar(weekly, x="_weekday_pt", y="volume", 
                 labels={"_weekday_pt":"Dia da Semana", "volume":"Volume Total (R$)"},
                 title="Volume Total por Dia da Semana",
                 color="volume",
                 color_continuous_scale='Blues')
    
    fig1.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        height=400
    )
    
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    fig2 = px.bar(weekly, x="_weekday_pt", y="volume_medio",
                 labels={"_weekday_pt":"Dia da Semana", "volume_medio":"Volume Médio (R$)"},
                 title="Volume Médio por Dia da Semana",
                 color="volume_medio",
                 color_continuous_scale='Greens')
    
    fig2.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        height=400
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
        fig3 = px.line(hourly, x="_hour", y="volume", 
                      title="Volume por Hora", 
                      labels={"_hour":"Hora do Dia", "volume":"Volume (R$)"},
                      color_discrete_sequence=['#FF6384'])
        
        fig3.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            height=400
        )
        
        st.plotly_chart(fig3, use_container_width=True)
    
    with col2:
        fig4 = px.bar(hourly, x="_hour", y="n_transacoes", 
                     title="Número de Transações por Hora", 
                     labels={"_hour":"Hora do Dia", "n_transacoes":"Nº Transações"},
                     color="n_transacoes",
                     color_continuous_scale='Purples')
        
        fig4.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            height=400
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
                       color_discrete_sequence=['#36A2EB'])
    
    fig5.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        height=400
    )
    
    st.plotly_chart(fig5, use_container_width=True)

with col2:
    fig6 = px.box(df, y=amount_col, 
                 labels={amount_col:"Valor da Transação (R$)"}, 
                 title="Box Plot - Distribuição de Valores",
                 color_discrete_sequence=['#FF9A3D'])
    
    fig6.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        height=400
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