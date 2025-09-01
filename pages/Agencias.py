import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import numpy as np

st.set_page_config(page_title="Agências | BanVic", layout="wide")

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

st.title("📊 Análise Detalhada por Agência")

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

# Resto do código permanece igual a partir daqui...
# [O restante do código que eu forneci anteriormente continua igual]

st.subheader("📈 Métricas por Agência - Últimos 6 meses")

# KPIs principais
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Agências", f"{len(agrupamento):,}")
with col2:
    total_trans = agrupamento["num_transacoes"].sum()
    st.metric("Total Transações", f"{total_trans:,}")
with col3:
    total_saques = agrupamento["total_saques"].sum()
    st.metric("Total Saques", f"{total_saques:,}")
with col4:
    total_arrecadacao = agrupamento["arrecadacao_total"].sum()
    st.metric("Arrecadação Total", f"R$ {total_arrecadacao:,.2f}")

# Filtros
st.subheader("🔍 Filtros")
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

st.subheader(f"🏆 Todas as Agências ({len(agrupamento_filtrado)} agências)")

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
    mime="text/csv"
)

# Gráficos comparativos
st.markdown("---")
st.subheader("📊 Visualizações Comparativas")

col1, col2 = st.columns(2)

with col1:
    # Top 20 agências por transações
    top_20 = agrupamento_filtrado.head(20).sort_values("num_transacoes", ascending=True)
    fig1 = px.bar(top_20, 
                 x="num_transacoes", 
                 y=agencia_nome_col, 
                 orientation="h", 
                 title="Top 20 Agências - Nº de Transações",
                 labels={"num_transacoes": "Nº Transações", agencia_nome_col: "Agência"})
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    # Top 20 agências por arrecadação
    top_20_arrecadacao = agrupamento_filtrado.head(20).sort_values("arrecadacao_total", ascending=True)
    fig2 = px.bar(top_20_arrecadacao, 
                 x="arrecadacao_total", 
                 y=agencia_nome_col, 
                 orientation="h", 
                 title="Top 20 Agências - Arrecadação",
                 labels={"arrecadacao_total": "Arrecadação (R$)", agencia_nome_col: "Agência"})
    st.plotly_chart(fig2, use_container_width=True)

# Scatter plot comparativo
st.subheader("📈 Relação entre Transações e Arrecadação")
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
st.plotly_chart(fig3, use_container_width=True)

# Análise por UF se disponível
if agencia_uf_col:
    st.markdown("---")
    st.subheader("🗺️ Análise por UF")
    
    por_uf = agrupamento_filtrado.groupby(agencia_uf_col).agg(
        num_agencias=(agencia_nome_col, "nunique"),
        num_transacoes=("num_transacoes", "sum"),
        total_arrecadacao=("arrecadacao_total", "sum"),
        media_ticket=("ticket_medio", "mean")
    ).reset_index().sort_values("total_arrecadacao", ascending=False)
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig4 = px.bar(por_uf, x=agencia_uf_col, y="num_agencias",
                     title="Número de Agências por UF",
                     labels={agencia_uf_col: "UF", "num_agencias": "Nº Agências"})
        st.plotly_chart(fig4, use_container_width=True)
    
    with col2:
        fig5 = px.bar(por_uf, x=agencia_uf_col, y="total_arrecadacao",
                     title="Arrecadação Total por UF",
                     labels={agencia_uf_col: "UF", "total_arrecadacao": "Arrecadação Total (R$)"})
        st.plotly_chart(fig5, use_container_width=True)

# Estatísticas gerais
st.markdown("---")
st.subheader("📊 Estatísticas Gerais das Agências")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Média Transações/Agência", f"{agrupamento_filtrado['num_transacoes'].mean():.0f}")
with col2:
    st.metric("Média Arrecadação/Agência", f"R$ {agrupamento_filtrado['arrecadacao_total'].mean():,.2f}")
with col3:
    st.metric("Média Ticket Médio", f"R$ {agrupamento_filtrado['ticket_medio'].mean():,.2f}")
with col4:
    st.metric("Taxa Média de Saques", f"{agrupamento_filtrado['percentual_saques'].mean():.1f}%")

# Distribuição dos valores
st.subheader("📊 Distribuição dos Valores")
col1, col2 = st.columns(2)

with col1:
    fig6 = px.histogram(agrupamento_filtrado, x="num_transacoes", 
                       title="Distribuição do Número de Transações",
                       labels={"num_transacoes": "Nº Transações", "count": "Nº Agências"})
    st.plotly_chart(fig6, use_container_width=True)

with col2:
    fig7 = px.histogram(agrupamento_filtrado, x="arrecadacao_total", 
                       title="Distribuição da Arrecadação",
                       labels={"arrecadacao_total": "Arrecadação (R$)", "count": "Nº Agências"})
    st.plotly_chart(fig7, use_container_width=True)

# Busca rápida por agência específica
st.markdown("---")
st.subheader("🔍 Buscar Agência Específica")

if agencia_nome_col:
    agencia_busca = st.selectbox("Digite o nome da agência:", 
                               [""] + sorted(agrupamento_filtrado[agencia_nome_col].unique().tolist()))
    
    if agencia_busca:
        agencia_info = agrupamento_filtrado[agrupamento_filtrado[agencia_nome_col] == agencia_busca].iloc[0]
        
        st.success(f"**Informações detalhadas de {agencia_busca}:**")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Ranking", f"#{agrupamento_filtrado[agrupamento_filtrado[agencia_nome_col] == agencia_busca].index[0] + 1}")
            st.metric("Nº Transações", f"{agencia_info['num_transacoes']:,}")
        
        with col2:
            st.metric("Arrecadação Total", f"R$ {agencia_info['arrecadacao_total']:,.2f}")
            st.metric("Ticket Médio", f"R$ {agencia_info['ticket_medio']:,.2f}")
        
        with col3:
            st.metric("Total Saques", f"{agencia_info['total_saques']:,}")
            st.metric("% Saques", f"{agencia_info['percentual_saques']}%")
        
        with col4:
            st.metric("Saldo Líquido", f"R$ {agencia_info['saldo_liquido']:,.2f}")
            if agencia_uf_col:
                st.metric("UF", agencia_info[agencia_uf_col])