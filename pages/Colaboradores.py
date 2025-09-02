import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

st.set_page_config(page_title="Colaboradores | BanVic", layout="wide", page_icon="👥")

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

# Função para encontrar a coluna de nome
def encontrar_coluna_nome(df):
    possiveis_nomes = ['nome', 'name', 'colaborador', 'employee', 'funcionario', 'nome_colaborador']
    for col in df.columns:
        if any(nome in col.lower() for nome in possiveis_nomes):
            return col
    # Se não encontrar, retorna a primeira coluna que parece ser texto
    for col in df.columns:
        if df[col].dtype == 'object' and len(df[col].unique()) > 1:
            return col
    return df.columns[0]  # Fallback para primeira coluna

# Carregar dados
@st.cache_data
def load_data():
    try:
        df_colaboradores = pd.read_csv("data/colaboradores.csv")
    except FileNotFoundError:
        try:
            df_colaboradores = pd.read_csv("colaboradores.csv")
        except FileNotFoundError:
            st.error("Arquivo colaboradores.csv não encontrado!")
            return None
    
    # Encontrar coluna de nome
    nome_col = encontrar_coluna_nome(df_colaboradores)
    st.session_state.nome_col = nome_col
    
    # Adicionar dados fictícios para análise mais rica
    if "salario_base" not in df_colaboradores.columns:
        np.random.seed(42)
        df_colaboradores["salario_base"] = np.random.randint(3000, 8000, len(df_colaboradores))
    
    if "idade" not in df_colaboradores.columns:
        np.random.seed(42)
        df_colaboradores["idade"] = np.random.randint(25, 55, len(df_colaboradores))
    
    if "departamento" not in df_colaboradores.columns:
        departamentos = ["TI", "Vendas", "RH", "Financeiro", "Operações", "Marketing"]
        df_colaboradores["departamento"] = np.random.choice(departamentos, len(df_colaboradores))
    
    if "data_admissao" not in df_colaboradores.columns:
        dates = pd.date_range('2018-01-01', '2023-12-31', periods=len(df_colaboradores))
        df_colaboradores["data_admissao"] = np.random.choice(dates, len(df_colaboradores), replace=False)
    
    if "desempenho" not in df_colaboradores.columns:
        df_colaboradores["desempenho"] = np.random.uniform(6, 10, len(df_colaboradores)).round(1)
    
    return df_colaboradores

df_colaboradores = load_data()

if df_colaboradores is None:
    st.stop()

# Obter coluna de nome
nome_col = st.session_state.get('nome_col', 'nome')

st.title("👥 Análise de Colaboradores")
st.markdown("Dashboard interativo para análise completa do quadro de colaboradores")

# ===== METRICAS PRINCIPAIS =====
st.markdown('<div class="section-header"><h3>📊 Métricas Principais</h3></div>', unsafe_allow_html=True)

# KPIs principais em cards modernos
st.markdown('<div class="kpi-grid">', unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(kpi_card("Total de Colaboradores", f"{len(df_colaboradores):,}", "👥", "metric-card-1"), unsafe_allow_html=True)

with col2:
    custo_total = df_colaboradores["salario_base"].sum()
    st.markdown(kpi_card("Custo Total da Folha", f"R$ {custo_total:,.0f}", "💰", "metric-card-2"), unsafe_allow_html=True)

with col3:
    salario_medio = custo_total / len(df_colaboradores)
    st.markdown(kpi_card("Salário Médio", f"R$ {salario_medio:,.0f}", "💸", "metric-card-3"), unsafe_allow_html=True)

with col4:
    idade_media = df_colaboradores["idade"].mean()
    st.markdown(kpi_card("Idade Média", f"{idade_media:.1f} anos", "🎂", "metric-card-4"), unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# ===== GRÁFICOS PRINCIPAIS =====
col_left, col_right = st.columns([2, 1])

with col_left:
    st.markdown('<div class="section-header"><h3>📈 Distribuição Salarial</h3></div>', unsafe_allow_html=True)
    
    fig_salarios = px.histogram(df_colaboradores, x="salario_base", 
                               nbins=15, 
                               title="Distribuição de Salários",
                               labels={"salario_base": "Salário Base (R$)"},
                               color_discrete_sequence=['#3b82f6'])
    
    fig_salarios.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#64748b'),
        height=400,
        showlegend=False,
        xaxis=dict(tickformat=",.0f")
    )
    
    st.plotly_chart(fig_salarios, use_container_width=True)

with col_right:
    st.markdown('<div class="section-header"><h3>🎯 Desempenho Médio</h3></div>', unsafe_allow_html=True)
    
    desempenho_medio = df_colaboradores["desempenho"].mean()
    fig_desempenho = go.Figure(go.Indicator(
        mode = "gauge+number+delta",
        value = desempenho_medio,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "Desempenho Médio (0-10)", 'font': {'size': 16}},
        gauge = {
            'axis': {'range': [0, 10], 'tickwidth': 1, 'tickcolor': "darkblue"},
            'bar': {'color': "#10b981"},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, 6], 'color': "#ef4444"},
                {'range': [6, 8], 'color': "#f59e0b"},
                {'range': [8, 10], 'color': "#10b981"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 8
            }
        }
    ))
    
    fig_desempenho.update_layout(
        height=300,
        margin=dict(l=30, r=30, t=50, b=30),
        font=dict(color='#64748b')
    )
    
    st.plotly_chart(fig_desempenho, use_container_width=True)

# ===== ANÁLISE POR DEPARTAMENTO =====
st.markdown('<div class="section-header"><h3>🏢 Análise por Departamento</h3></div>', unsafe_allow_html=True)

if "departamento" in df_colaboradores.columns:
    dept_stats = df_colaboradores.groupby("departamento").agg({
        "salario_base": ["count", "mean", "sum"],
        "idade": "mean",
        "desempenho": "mean"
    }).round(2)
    
    dept_stats.columns = ["Qtd Colaboradores", "Salário Médio", "Custo Total", "Idade Média", "Desempenho Médio"]
    dept_stats = dept_stats.reset_index()
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig_dept_qtd = go.Figure()
        
        fig_dept_qtd.add_trace(go.Bar(
            x=dept_stats["departamento"],
            y=dept_stats["Qtd Colaboradores"],
            marker=dict(
                color=dept_stats["Qtd Colaboradores"],
                colorscale='Blues',
                line=dict(width=0)
            ),
            hovertemplate='<b>%{x}</b><br>Colaboradores: %{y:,}<br>Salário Médio: R$ %{customdata:,.0f}<extra></extra>',
            customdata=dept_stats['Salário Médio']
        ))
        
        fig_dept_qtd.update_layout(
            title=dict(
                text="Colaboradores por Departamento",
                font=dict(size=18, color='#1e293b'),
                x=0.5,
                xanchor='center'
            ),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#64748b'),
            height=400,
            xaxis=dict(
                title="Departamento",
                gridcolor='#e2e8f0'
            ),
            yaxis=dict(
                title="Nº Colaboradores",
                gridcolor='#e2e8f0'
            ),
            showlegend=False
        )
        
        st.plotly_chart(fig_dept_qtd, use_container_width=True)
    
    with col2:
        fig_dept_salario = go.Figure()
        
        fig_dept_salario.add_trace(go.Bar(
            x=dept_stats["departamento"],
            y=dept_stats["Salário Médio"],
            marker=dict(
                color=dept_stats["Salário Médio"],
                colorscale='Greens',
                line=dict(width=0)
            ),
            hovertemplate='<b>%{x}</b><br>Salário Médio: R$ %{y:,.0f}<br>Colaboradores: %{customdata:,}<extra></extra>',
            customdata=dept_stats['Qtd Colaboradores']
        ))
        
        fig_dept_salario.update_layout(
            title=dict(
                text="Salário Médio por Departamento",
                font=dict(size=18, color='#1e293b'),
                x=0.5,
                xanchor='center'
            ),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#64748b'),
            height=400,
            xaxis=dict(
                title="Departamento",
                gridcolor='#e2e8f0'
            ),
            yaxis=dict(
                title="Salário Médio (R$)",
                gridcolor='#e2e8f0',
                tickformat=",.0f"
            ),
            showlegend=False
        )
        
        st.plotly_chart(fig_dept_salario, use_container_width=True)

# ===== ANÁLISE POR IDADE =====
st.markdown('<div class="section-header"><h3>👥 Análise Demográfica</h3></div>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    fig_idade = px.histogram(df_colaboradores, x="idade", nbins=10,
                            title="Distribuição por Idade",
                            labels={"idade": "Idade", "count": "Nº Colaboradores"},
                            color_discrete_sequence=['#2563eb'])
    
    fig_idade.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#64748b'),
        height=400,
        showlegend=False,
        xaxis=dict(gridcolor='#e2e8f0'),
        yaxis=dict(gridcolor='#e2e8f0')
    )
    
    st.plotly_chart(fig_idade, use_container_width=True)

with col2:
    if "data_admissao" in df_colaboradores.columns:
        df_colaboradores["ano_admissao"] = pd.to_datetime(df_colaboradores["data_admissao"]).dt.year
        admissao_por_ano = df_colaboradores["ano_admissao"].value_counts().sort_index().reset_index()
        admissao_por_ano.columns = ["Ano", "Contratações"]
        
        fig_admissao = px.line(admissao_por_ano, x="Ano", y="Contratações",
                              markers=True,
                              title="Contratações por Ano",
                              labels={"Ano": "Ano", "Contratações": "Nº Contratações"},
                              color_discrete_sequence=['#ef4444'])
        
        fig_admissao.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#64748b'),
            height=400,
            xaxis=dict(gridcolor='#e2e8f0'),
            yaxis=dict(gridcolor='#e2e8f0')
        )
        
        st.plotly_chart(fig_admissao, use_container_width=True)

# ===== TOP COLLABORADORES =====
st.markdown('<div class="section-header"><h3>⭐ Top Colaboradores</h3></div>', unsafe_allow_html=True)

# Verificar quais colunas estão disponíveis para o gráfico de top colaboradores
colunas_disponiveis = []
if nome_col in df_colaboradores.columns:
    colunas_disponiveis.append(nome_col)
if "departamento" in df_colaboradores.columns:
    colunas_disponiveis.append("departamento")
if "salario_base" in df_colaboradores.columns:
    colunas_disponiveis.append("salario_base")
if "desempenho" in df_colaboradores.columns:
    colunas_disponiveis.append("desempenho")

if len(colunas_disponiveis) >= 2 and "desempenho" in colunas_disponiveis:
    try:
        # Ordenar por desempenho
        top_colaboradores = df_colaboradores.nlargest(10, "desempenho")[colunas_disponiveis]
        
        # Criar gráfico baseado nas colunas disponíveis
        if nome_col in colunas_disponiveis:
            fig_top = go.Figure()
            
            fig_top.add_trace(go.Bar(
                y=top_colaboradores[nome_col],
                x=top_colaboradores["desempenho"],
                orientation='h',
                marker=dict(
                    color=top_colaboradores["salario_base"] if "salario_base" in colunas_disponiveis else top_colaboradores["desempenho"],
                    colorscale='Viridis',
                    line=dict(width=0)
                ),
                hovertemplate='<b>%{y}</b><br>Desempenho: %{x:.1f}<br>Salário: R$ %{customdata:,.0f}<extra></extra>',
                customdata=top_colaboradores['salario_base'] if "salario_base" in colunas_disponiveis else [0] * len(top_colaboradores)
            ))
            
            fig_top.update_layout(
                title=dict(
                    text="Top 10 Colaboradores por Desempenho",
                    font=dict(size=18, color='#1e293b'),
                    x=0.5,
                    xanchor='center'
                ),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#64748b'),
                height=500,
                xaxis=dict(
                    title="Desempenho",
                    gridcolor='#e2e8f0'
                ),
                yaxis=dict(
                    title="Colaborador",
                    categoryorder='total ascending',
                    gridcolor='#e2e8f0'
                ),
                showlegend=False
            )
            
            st.plotly_chart(fig_top, use_container_width=True)
        else:
            st.info("Não foi possível criar gráfico de top colaboradores - coluna de nome não encontrada")
    except Exception as e:
        st.warning(f"Não foi possível criar gráfico de top colaboradores: {str(e)}")
else:
    st.info("Dados insuficientes para criar ranking de top colaboradores")

# ===== DATAFRAME INTERATIVO =====
st.markdown('<div class="section-header"><h3>📋 Dados Completos</h3></div>', unsafe_allow_html=True)

# Filtros interativos
col1, col2, col3 = st.columns(3)

with col1:
    if "departamento" in df_colaboradores.columns:
        dept_filter = st.multiselect("Filtrar por Departamento", 
                                    options=df_colaboradores["departamento"].unique())
    else:
        dept_filter = []

with col2:
    if "salario_base" in df_colaboradores.columns:
        salario_min, salario_max = st.slider("Faixa Salarial (R$)", 
                                            min_value=int(df_colaboradores["salario_base"].min()),
                                            max_value=int(df_colaboradores["salario_base"].max()),
                                            value=(int(df_colaboradores["salario_base"].min()), 
                                                   int(df_colaboradores["salario_base"].max())))
    else:
        salario_min, salario_max = 0, 1

with col3:
    if "idade" in df_colaboradores.columns:
        idade_min, idade_max = st.slider("Faixa Etária", 
                                        min_value=int(df_colaboradores["idade"].min()),
                                        max_value=int(df_colaboradores["idade"].max()),
                                        value=(int(df_colaboradores["idade"].min()), 
                                               int(df_colaboradores["idade"].max())))
    else:
        idade_min, idade_max = 0, 1

# Aplicar filtros
df_filtered = df_colaboradores.copy()
if dept_filter and "departamento" in df_filtered.columns:
    df_filtered = df_filtered[df_filtered["departamento"].isin(dept_filter)]
if "salario_base" in df_filtered.columns:
    df_filtered = df_filtered[(df_filtered["salario_base"] >= salario_min) & 
                             (df_filtered["salario_base"] <= salario_max)]
if "idade" in df_filtered.columns:
    df_filtered = df_filtered[(df_filtered["idade"] >= idade_min) & 
                             (df_filtered["idade"] <= idade_max)]

# Mostrar dataframe
st.dataframe(
    df_filtered,
    use_container_width=True,
    height=400,
    column_config={
        nome_col: "Nome",
        "departamento": "Departamento",
        "salario_base": st.column_config.NumberColumn("Salário", format="R$ %.2f"),
        "idade": "Idade",
        "desempenho": st.column_config.NumberColumn("Desempenho", format="%.1f"),
        "data_admissao": "Data Admissão"
    }
)

# ===== DOWNLOAD =====
st.markdown("---")
st.download_button(
    label="📥 Baixar Relatório de Colaboradores",
    data=df_filtered.to_csv(index=False),
    file_name="relatorio_colaboradores.csv",
    mime="text/csv",
    use_container_width=True
)

# ===== INFORMAÇÕES DO DATASET =====
with st.expander("ℹ️ Informações do Dataset"):
    st.write(f"**Total de registros:** {len(df_colaboradores)}")
    st.write(f"**Colunas:** {list(df_colaboradores.columns)}")
    st.write(f"**Coluna identificada como nome:** {nome_col}")
    st.write("**Amostra dos dados:**")
    st.dataframe(df_colaboradores.head(3), use_container_width=True)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 20px;'>
    <p>© 2024 BanVic — Análise de Colaboradores</p>
    <p>Desenvolvido por Marcelo Pires | 📊 Painel de Business Intelligence</p>
</div>
""", unsafe_allow_html=True)