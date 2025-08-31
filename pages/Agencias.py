import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Agências | BanVic", layout="wide")

# Verificar se as variáveis de sessão existem
if "df_filtered" not in st.session_state:
    st.warning("Volte para a página inicial e aplique os filtros primeiro.")
    st.stop()

df = st.session_state["df_filtered"].copy()
amount_col = st.session_state["amount_col"]

st.title("📊 Análise Detalhada por Agência")

# Verificar se temos informações das agências
if "agencia_nome" not in df.columns:
    st.error("Informações de agências não disponíveis.")
    st.stop()

if df.empty:
    st.warning("Sem dados no período selecionado.")
else:
    # Preparar dados dos últimos 6 meses
    date_col = st.session_state["date_col"]
    max_date = df[date_col].max()
    
    if pd.notna(max_date):
        start_6m = max_date - pd.DateOffset(months=6)
        last6 = df[df[date_col] >= start_6m]
    else:
        last6 = df

    if not last6.empty:
        # Calcular saques (assumindo que valores negativos são saques)
        last6["eh_saque"] = last6[amount_col] < 0
        saques = last6[last6["eh_saque"]]
        
        # Agrupar por agência com todas as informações
        agrupamento = last6.groupby(["agencia_nome", "agencia_uf", "agencia_tipo", "agencia_cidade"]).agg(
            num_transacoes=(amount_col, "count"),
            total_saques=("eh_saque", "sum"),
            arrecadacao_total=(amount_col, "sum"),
            ticket_medio=(amount_col, "mean")
        ).reset_index().sort_values("num_transacoes", ascending=False)

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
        col1, col2, col3 = st.columns(3)
        
        with col1:
            uf_options = ["Todos"] + sorted(agrupamento["agencia_uf"].dropna().unique().tolist())
            uf_selecionado = st.selectbox("Filtrar por UF:", uf_options)
            
        with col2:
            tipo_options = ["Todos"] + sorted(agrupamento["agencia_tipo"].dropna().unique().tolist())
            tipo_selecionado = st.selectbox("Filtrar por Tipo:", tipo_options)
            
        with col3:
            top_n = st.slider("Top N Agências:", 5, 50, 20)

        # Aplicar filtros
        agrupamento_filtrado = agrupamento.copy()
        if uf_selecionado != "Todos":
            agrupamento_filtrado = agrupamento_filtrado[agrupamento_filtrado["agencia_uf"] == uf_selecionado]
        if tipo_selecionado != "Todos":
            agrupamento_filtrado = agrupamento_filtrado[agrupamento_filtrado["agencia_tipo"] == tipo_selecionado]

        st.subheader("🏆 Ranking de Agências")
        
        # Gráfico de top agências por transações
        top_agencias = agrupamento_filtrado.head(top_n).sort_values("num_transacoes", ascending=True)
        fig1 = px.bar(top_agencias, 
                     x="num_transacoes", 
                     y="agencia_nome", 
                     orientation="h", 
                     title=f"Top {top_n} Agências - Número de Transações",
                     labels={"num_transacoes": "Nº Transações", "agencia_nome": "Agência"},
                     hover_data=["agencia_uf", "agencia_tipo", "arrecadacao_total"])
        st.plotly_chart(fig1, use_container_width=True)

        # Gráfico de arrecadação por UF
        fig2 = px.treemap(agrupamento_filtrado, 
                         path=["agencia_uf", "agencia_nome"],
                         values="arrecadacao_total",
                         title="Arrecadação por UF e Agência",
                         hover_data=["num_transacoes", "total_saques"])
        st.plotly_chart(fig2, use_container_width=True)

        # Tabela detalhada
        st.subheader("📋 Tabela Completa de Agências")
        
        agrupamento_display = agrupamento_filtrado.copy()
        agrupamento_display["arrecadacao_total"] = agrupamento_display["arrecadacao_total"].round(2)
        agrupamento_display["ticket_medio"] = agrupamento_display["ticket_medio"].round(2)
        
        st.dataframe(
            agrupamento_display,
            column_config={
                "agencia_nome": st.column_config.TextColumn("Agência", width="large"),
                "agencia_uf": st.column_config.TextColumn("UF", width="small"),
                "agencia_tipo": st.column_config.TextColumn("Tipo", width="medium"),
                "agencia_cidade": st.column_config.TextColumn("Cidade", width="medium"),
                "num_transacoes": st.column_config.NumberColumn("Nº Transações", format="%d"),
                "total_saques": st.column_config.NumberColumn("Total Saques", format="%d"),
                "arrecadacao_total": st.column_config.NumberColumn("Arrecadação Total", format="R$ %.2f"),
                "ticket_medio": st.column_config.NumberColumn("Ticket Médio", format="R$ %.2f")
            },
            use_container_width=True,
            height=600
        )
        
        # Download dos dados
        csv = agrupamento_display.to_csv(index=False)
        st.download_button(
            label="📥 Download CSV Completo",
            data=csv,
            file_name="detalhes_agencias.csv",
            mime="text/csv"
        )

    else:
        st.warning("Não há dados nos últimos 6 meses.")

# Análise adicional por UF e Tipo
st.markdown("---")
st.subheader("📊 Análise por UF e Tipo de Agência")

if not last6.empty:
    # Análise por UF
    por_uf = last6.groupby("agencia_uf").agg(
        num_agencias=("agencia_nome", "nunique"),
        num_transacoes=(amount_col, "count"),
        total_saques=("eh_saque", "sum"),
        arrecadacao_total=(amount_col, "sum")
    ).reset_index().sort_values("arrecadacao_total", ascending=False)

    col1, col2 = st.columns(2)
    
    with col1:
        fig3 = px.bar(por_uf, x="agencia_uf", y="arrecadacao_total",
                     title="Arrecadação por UF",
                     labels={"agencia_uf": "UF", "arrecadacao_total": "Arrecadação Total"})
        st.plotly_chart(fig3, use_container_width=True)
    
    with col2:
        fig4 = px.pie(por_uf, values="num_transacoes", names="agencia_uf",
                     title="Distribuição de Transações por UF")
        st.plotly_chart(fig4, use_container_width=True)

    # Análise por Tipo
    por_tipo = last6.groupby("agencia_tipo").agg(
        num_agencias=("agencia_nome", "nunique"),
        num_transacoes=(amount_col, "count"),
        total_saques=("eh_saque", "sum"),
        arrecadacao_total=(amount_col, "sum")
    ).reset_index()

    col1, col2 = st.columns(2)
    
    with col1:
        fig5 = px.bar(por_tipo, x="agencia_tipo", y="arrecadacao_total",
                     title="Arrecadação por Tipo",
                     labels={"agencia_tipo": "Tipo", "arrecadacao_total": "Arrecadação Total"})
        st.plotly_chart(fig5, use_container_width=True)
    
    with col2:
        fig6 = px.pie(por_tipo, values="num_transacoes", names="agencia_tipo",
                     title="Distribuição de Transações por Tipo")
        st.plotly_chart(fig6, use_container_width=True)