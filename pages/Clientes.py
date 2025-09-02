import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import numpy as np

st.set_page_config(page_title="Clientes | BanVic", layout="wide")

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

# Verificar se as variáveis de sessão existem
if "df_filtered" not in st.session_state:
    st.warning("Volte para a página inicial e aplique os filtros primeiro.")
    st.stop()

df = st.session_state["df_filtered"].copy()
amount_col = st.session_state["amount_col"]

st.title("👥 Análise Detalhada de Clientes")
st.markdown("Análise completa do perfil e comportamento dos clientes")

# Verificar se temos informações dos clientes
client_cols = [col for col in df.columns if col.startswith('cliente_')]
if not client_cols:
    st.error("Informações detalhadas de clientes não disponíveis.")
    st.stop()

# Criar label do cliente
if "cliente_nome_completo" in df.columns:
    df["client_label"] = df["cliente_nome_completo"]
elif "cliente_primeiro_nome" in df.columns:
    df["client_label"] = df["cliente_primeiro_nome"]
else:
    df["client_label"] = "Cliente " + df[st.session_state["client_id_col"]].astype(str)

# Função para extrair cidade e estado do endereço
def extrair_cidade_uf(endereco):
    if pd.isna(endereco) or not isinstance(endereco, str):
        return None, None
    
    # Procurar padrão comum de cidade/UF no final do endereço
    partes = endereco.split(',')
    if len(partes) >= 2:
        ultima_parte = partes[-1].strip()
        # Verificar se contém padrão de UF (2 letras maiúsculas)
        if len(ultima_parte) >= 2 and ultima_parte[-2:].isupper() and ultima_parte[-2:].isalpha():
            uf = ultima_parte[-2:]
            cidade = partes[-2].strip() if len(partes) >= 2 else ultima_parte[:-2].strip()
            return cidade, uf
    
    return None, None

# Análise de clientes
if not df.empty and "client_label" in df.columns:
    # Calcular idade se data de nascimento disponível
    if "cliente_data_nascimento" in df.columns:
        try:
            df["cliente_data_nascimento"] = pd.to_datetime(df["cliente_data_nascimento"], errors="coerce")
            hoje = datetime.now()
            df["idade"] = (hoje - df["cliente_data_nascimento"]).dt.days // 365
        except:
            pass

    # Extrair cidade e UF do endereço se disponível
    if "cliente_endereco" in df.columns and "cliente_cidade" not in df.columns:
        df[["cliente_cidade", "cliente_uf"]] = df["cliente_endereco"].apply(
            lambda x: pd.Series(extrair_cidade_uf(x)) if pd.notna(x) else pd.Series([None, None])
        )

    # Agrupar dados dos clientes
    client_info_cols = ["client_label"]
    info_cols = []
    
    # Lista de todas as colunas possíveis de clientes
    possible_client_cols = [
        "cliente_email", "cliente_tipo", "cliente_cpf", "cliente_data_nascimento",
        "cliente_endereco", "cliente_cep", "cliente_cidade", "cliente_uf", "idade"
    ]
    
    # Adicionar apenas colunas que existem no DataFrame
    for col in possible_client_cols:
        if col in df.columns:
            info_cols.append(col)

    # Agrupar informações básicas dos clientes
    if info_cols:
        clientes_info = df[client_info_cols + info_cols].drop_duplicates("client_label")
    else:
        clientes_info = df[client_info_cols].drop_duplicates("client_label")
    
    # Agrupar métricas financeiras
    ranking_clients = df.groupby("client_label").agg(
        n_transacoes=(amount_col, "count"), 
        volume_total=(amount_col, "sum"),
        ticket_medio=(amount_col, "mean"),
        primeira_transacao=(st.session_state["date_col"], "min"),
        ultima_transacao=(st.session_state["date_col"], "max"),
        # Calcular saques
        total_saques=(amount_col, lambda x: (x < 0).sum()),
        total_depositos=(amount_col, lambda x: (x > 0).sum())
    ).reset_index()

    # Combinar informações
    clientes_completos = ranking_clients.merge(clientes_info, on="client_label", how="left")
    clientes_completos = clientes_completos.sort_values("volume_total", ascending=False)

    # Estatísticas básicas
    st.markdown('<div class="section-header"><h3>📊 Métricas Gerais</h3></div>', unsafe_allow_html=True)
    
    # KPIs principais em cards modernos
    st.markdown('<div class="kpi-grid">', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(kpi_card("Total de Clientes", f"{len(clientes_completos):,}", "👥", "metric-card-1"), unsafe_allow_html=True)
    with col2:
        st.markdown(kpi_card("Volume Total", f"R$ {clientes_completos['volume_total'].sum():,.2f}", "💰", "metric-card-2"), unsafe_allow_html=True)
    with col3:
        avg_trans = clientes_completos['n_transacoes'].mean()
        st.markdown(kpi_card("Média Transações/Cliente", f"{avg_trans:.1f}", "💳", "metric-card-3"), unsafe_allow_html=True)
    with col4:
        st.markdown(kpi_card("Ticket Médio", f"R$ {clientes_completos['ticket_medio'].mean():,.2f}", "🎫", "metric-card-4"), unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

    # Filtros
    st.markdown('<div class="section-header"><h3>🔍 Filtros</h3></div>', unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if "cliente_tipo" in clientes_completos.columns:
            tipo_options = ["Todos"] + sorted(clientes_completos["cliente_tipo"].dropna().unique().tolist())
            tipo_selecionado = st.selectbox("Filtrar por Tipo:", tipo_options)
        else:
            tipo_selecionado = "Todos"
    
    with col2:
        if "cliente_uf" in clientes_completos.columns:
            uf_options = ["Todos"] + sorted(clientes_completos["cliente_uf"].dropna().unique().tolist())
            uf_selecionado = st.selectbox("Filtrar por UF:", uf_options)
        else:
            uf_selecionado = "Todos"
    
    with col3:
        faixa_volume = st.selectbox("Faixa de Volume:", 
                                  ["Todos", "Até R$ 1.000", "R$ 1.000 - 5.000", "R$ 5.000 - 10.000", "Acima de R$ 10.000"])
    
    with col4:
        top_n = st.slider("Top N Clientes:", 10, 100, 25)

    # Aplicar filtros
    clientes_filtrados = clientes_completos.copy()
    
    if "cliente_tipo" in clientes_filtrados.columns and tipo_selecionado != "Todos":
        clientes_filtrados = clientes_filtrados[clientes_filtrados["cliente_tipo"] == tipo_selecionado]
    
    if "cliente_uf" in clientes_filtrados.columns and uf_selecionado != "Todos":
        clientes_filtrados = clientes_filtrados[clientes_filtrados["cliente_uf"] == uf_selecionado]
    
    if faixa_volume != "Todos":
        if faixa_volume == "Até R$ 1.000":
            clientes_filtrados = clientes_filtrados[clientes_filtrados["volume_total"] <= 1000]
        elif faixa_volume == "R$ 1.000 - 5.000":
            clientes_filtrados = clientes_filtrados[(clientes_filtrados["volume_total"] > 1000) & (clientes_filtrados["volume_total"] <= 5000)]
        elif faixa_volume == "R$ 5.000 - 10.000":
            clientes_filtrados = clientes_filtrados[(clientes_filtrados["volume_total"] > 5000) & (clientes_filtrados["volume_total"] <= 10000)]
        else:
            clientes_filtrados = clientes_filtrados[clientes_filtrados["volume_total"] > 10000]

    st.markdown('<div class="section-header"><h3>🏆 Top Clientes por Volume</h3></div>', unsafe_allow_html=True)
    
    # Gráfico de top clientes
    top_clientes = clientes_filtrados.head(top_n).sort_values("volume_total", ascending=True)
    
    # CORREÇÃO: Verificar quais colunas estão disponíveis para o hover_data
    hover_columns = ["n_transacoes", "ticket_medio"]
    available_columns = [col for col in ["cliente_tipo", "cliente_email", "cliente_uf"] 
                        if col in top_clientes.columns]
    hover_columns.extend(available_columns)
    
    fig1 = go.Figure()
    
    fig1.add_trace(go.Bar(
        y=top_clientes["client_label"],
        x=top_clientes["volume_total"],
        orientation='h',
        marker=dict(
            color=top_clientes["volume_total"],
            colorscale='Viridis',
            line=dict(width=0)
        ),
        hovertemplate='<b>%{y}</b><br>Volume: R$ %{x:,.2f}<br>Transações: %{customdata[0]:,}<br>Ticket: R$ %{customdata[1]:.2f}<extra></extra>',
        customdata=np.stack((top_clientes['n_transacoes'], top_clientes['ticket_medio']), axis=-1)
    ))
    
    fig1.update_layout(
        title=dict(
            text=f"Top {top_n} Clientes por Volume",
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
    
    st.plotly_chart(fig1, use_container_width=True)

    # Análise por tipo de cliente
    if "cliente_tipo" in clientes_filtrados.columns:
        st.markdown('<div class="section-header"><h3>📈 Análise por Tipo de Cliente</h3></div>', unsafe_allow_html=True)
        
        por_tipo = clientes_filtrados.groupby("cliente_tipo").agg(
            num_clientes=("client_label", "count"),
            volume_total=("volume_total", "sum"),
            media_transacoes=("n_transacoes", "mean"),
            media_ticket=("ticket_medio", "mean")
        ).reset_index()
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig2 = px.pie(por_tipo, values="volume_total", names="cliente_tipo",
                         title="Distribuição de Volume por Tipo",
                         color_discrete_sequence=px.colors.qualitative.Set3,
                         hole=0.4)
            
            fig2.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#64748b'),
                height=400,
                showlegend=True,
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=-0.2,
                    xanchor="center",
                    x=0.5
                )
            )
            
            st.plotly_chart(fig2, use_container_width=True)
        
        with col2:
            fig3 = go.Figure()
            
            fig3.add_trace(go.Bar(
                x=por_tipo["cliente_tipo"],
                y=por_tipo["num_clientes"],
                marker=dict(
                    color=por_tipo["num_clientes"],
                    colorscale='Blues',
                    line=dict(width=0)
                ),
                hovertemplate='<b>%{x}</b><br>Clientes: %{y:,}<br>Volume Total: R$ %{customdata:,.2f}<extra></extra>',
                customdata=por_tipo['volume_total']
            ))
            
            fig3.update_layout(
                title=dict(
                    text="Número de Clientes por Tipo",
                    font=dict(size=18, color='#1e293b'),
                    x=0.5,
                    xanchor='center'
                ),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#64748b'),
                height=400,
                xaxis=dict(
                    title="Tipo de Cliente",
                    gridcolor='#e2e8f0'
                ),
                yaxis=dict(
                    title="Nº Clientes",
                    gridcolor='#e2e8f0'
                ),
                showlegend=False
            )
            
            st.plotly_chart(fig3, use_container_width=True)

    # Análise por UF se disponível
    if "cliente_uf" in clientes_filtrados.columns:
        st.markdown('<div class="section-header"><h3>🗺️ Análise por Estado (UF)</h3></div>', unsafe_allow_html=True)
        
        por_uf = clientes_filtrados.groupby("cliente_uf").agg(
            num_clientes=("client_label", "count"),
            volume_total=("volume_total", "sum"),
            media_transacoes=("n_transacoes", "mean"),
            media_ticket=("ticket_medio", "mean")
        ).reset_index()
        
        col1, col2 = st.columns(2)
        
        with col1:
            top_10_volume = por_uf.sort_values("volume_total", ascending=False).head(10)
            
            fig4 = go.Figure()
            
            fig4.add_trace(go.Bar(
                x=top_10_volume["cliente_uf"],
                y=top_10_volume["volume_total"],
                marker=dict(
                    color=top_10_volume["volume_total"],
                    colorscale='Greens',
                    line=dict(width=0)
                ),
                hovertemplate='<b>%{x}</b><br>Volume: R$ %{y:,.2f}<br>Clientes: %{customdata:,}<extra></extra>',
                customdata=top_10_volume['num_clientes']
            ))
            
            fig4.update_layout(
                title=dict(
                    text="Top 10 Estados por Volume",
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
                    title="Volume Total (R$)",
                    gridcolor='#e2e8f0',
                    tickformat=",.2f"
                ),
                showlegend=False
            )
            
            st.plotly_chart(fig4, use_container_width=True)
        
        with col2:
            top_10_clientes = por_uf.sort_values("num_clientes", ascending=False).head(10)
            
            fig5 = go.Figure()
            
            fig5.add_trace(go.Bar(
                x=top_10_clientes["cliente_uf"],
                y=top_10_clientes["num_clientes"],
                marker=dict(
                    color=top_10_clientes["num_clientes"],
                    colorscale='Purples',
                    line=dict(width=0)
                ),
                hovertemplate='<b>%{x}</b><br>Clientes: %{y:,}<br>Volume: R$ %{customdata:,.2f}<extra></extra>',
                customdata=top_10_clientes['volume_total']
            ))
            
            fig5.update_layout(
                title=dict(
                    text="Top 10 Estados por Nº de Clientes",
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
                    title="Nº Clientes",
                    gridcolor='#e2e8f0'
                ),
                showlegend=False
            )
            
            st.plotly_chart(fig5, use_container_width=True)

    # Tabela detalhada
    st.markdown('<div class="section-header"><h3>📋 Tabela Completa de Clientes</h3></div>', unsafe_allow_html=True)
    
    # Selecionar colunas para mostrar
    colunas_mostrar = ["client_label", "n_transacoes", "volume_total", "ticket_medio", 
                       "total_saques", "total_depositos"]
    
    # Adicionar colunas disponíveis
    additional_cols = ["cliente_tipo", "cliente_email", "idade", "cliente_endereco", "cliente_cep", "cliente_cidade", "cliente_uf"]
    for col in additional_cols:
        if col in clientes_filtrados.columns:
            colunas_mostrar.append(col)
    
    clientes_display = clientes_filtrados[colunas_mostrar].copy()
    clientes_display["volume_total"] = clientes_display["volume_total"].round(2)
    clientes_display["ticket_medio"] = clientes_display["ticket_medio"].round(2)
    
    # Adicionar ranking
    clientes_display["Ranking"] = range(1, len(clientes_display) + 1)
    
    # Configuração das colunas para a tabela
    column_config = {
        "Ranking": st.column_config.NumberColumn("Rank", format="%d", width="small"),
        "client_label": st.column_config.TextColumn("Cliente", width="large"),
        "n_transacoes": st.column_config.NumberColumn("Nº Transações", format="%d"),
        "volume_total": st.column_config.NumberColumn("Volume Total", format="R$ %.2f"),
        "ticket_medio": st.column_config.NumberColumn("Ticket Médio", format="R$ %.2f"),
        "total_saques": st.column_config.NumberColumn("Total Saques", format="%d"),
        "total_depositos": st.column_config.NumberColumn("Total Depósitos", format="%d")
    }
    
    # Adicionar configurações para colunas adicionais se existirem
    if "cliente_tipo" in clientes_display.columns:
        column_config["cliente_tipo"] = st.column_config.TextColumn("Tipo", width="medium")
    if "cliente_email" in clientes_display.columns:
        column_config["cliente_email"] = st.column_config.TextColumn("Email", width="medium")
    if "idade" in clientes_display.columns:
        column_config["idade"] = st.column_config.NumberColumn("Idade", format="%d")
    if "cliente_endereco" in clientes_display.columns:
        column_config["cliente_endereco"] = st.column_config.TextColumn("Endereço", width="large")
    if "cliente_cep" in clientes_display.columns:
        column_config["cliente_cep"] = st.column_config.TextColumn("CEP", width="small")
    if "cliente_cidade" in clientes_display.columns:
        column_config["cliente_cidade"] = st.column_config.TextColumn("Cidade", width="medium")
    if "cliente_uf" in clientes_display.columns:
        column_config["cliente_uf"] = st.column_config.TextColumn("UF", width="small")
    
    st.dataframe(
        clientes_display.head(100),
        column_config=column_config,
        use_container_width=True,
        height=600
    )
    
    # Download dos dados
    csv = clientes_display.to_csv(index=False, encoding='utf-8-sig')
    st.download_button(
        label="📥 Download CSV Completo",
        data=csv,
        file_name="detalhes_clientes.csv",
        mime="text/csv",
        use_container_width=True
    )

    # Análise demográfica
    if "idade" in clientes_filtrados.columns:
        st.markdown('<div class="section-header"><h3>👥 Análise Demográfica</h3></div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Distribuição por faixa etária
            clientes_filtrados["faixa_etaria"] = pd.cut(clientes_filtrados["idade"], 
                                                       bins=[0, 18, 25, 35, 45, 55, 65, 100],
                                                       labels=["0-18", "19-25", "26-35", "36-45", "46-55", "56-65", "65+"])
            por_idade = clientes_filtrados.groupby("faixa_etaria").agg(
                num_clientes=("client_label", "count"),
                volume_medio=("volume_total", "mean")
            ).reset_index()
            
            fig6 = go.Figure()
            
            fig6.add_trace(go.Bar(
                x=por_idade["faixa_etaria"],
                y=por_idade["num_clientes"],
                marker=dict(
                    color=por_idade["num_clientes"],
                    colorscale='Oranges',
                    line=dict(width=0)
                ),
                hovertemplate='<b>%{x}</b><br>Clientes: %{y:,}<br>Volume Médio: R$ %{customdata:,.2f}<extra></extra>',
                customdata=por_idade['volume_medio']
            ))
            
            fig6.update_layout(
                title=dict(
                    text="Distribuição por Faixa Etária",
                    font=dict(size=18, color='#1e293b'),
                    x=0.5,
                    xanchor='center'
                ),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#64748b'),
                height=400,
                xaxis=dict(
                    title="Faixa Etária",
                    gridcolor='#e2e8f0'
                ),
                yaxis=dict(
                    title="Nº Clientes",
                    gridcolor='#e2e8f0'
                ),
                showlegend=False
            )
            
            st.plotly_chart(fig6, use_container_width=True)
        
        with col2:
            fig7 = px.scatter(clientes_filtrados, x="idade", y="volume_total",
                             title="Volume vs Idade",
                             labels={"idade": "Idade", "volume_total": "Volume Total"},
                             hover_data=["client_label"],
                             color="volume_total",
                             color_continuous_scale='Viridis')
            
            fig7.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#64748b'),
                height=400
            )
            
            st.plotly_chart(fig7, use_container_width=True)

else:
    st.warning("Não foi possível realizar a análise de clientes.")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 20px;'>
    <p>© 2024 BanVic — Análise de Clientes</p>
    <p>Desenvolvido por Marcelo Pires | 📊 Painel de Business Intelligence</p>
</div>
""", unsafe_allow_html=True)