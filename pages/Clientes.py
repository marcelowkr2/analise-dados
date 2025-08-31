import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

st.set_page_config(page_title="Clientes | BanVic", layout="wide")

# Verificar se as variáveis de sessão existem
if "df_filtered" not in st.session_state:
    st.warning("Volte para a página inicial e aplique os filtros primeiro.")
    st.stop()

df = st.session_state["df_filtered"].copy()
amount_col = st.session_state["amount_col"]

st.title("👥 Análise Detalhada de Clientes")

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
    st.subheader("📊 Métricas Gerais")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total de Clientes", f"{len(clientes_completos):,}")
    with col2:
        st.metric("Volume Total", f"R$ {clientes_completos['volume_total'].sum():,.2f}")
    with col3:
        avg_trans = clientes_completos['n_transacoes'].mean()
        st.metric("Média Transações/Cliente", f"{avg_trans:.1f}")
    with col4:
        st.metric("Ticket Médio", f"R$ {clientes_completos['ticket_medio'].mean():,.2f}")

    # Filtros
    st.subheader("🔍 Filtros")
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

    st.subheader("🏆 Top Clientes por Volume")
    
    # Gráfico de top clientes
    top_clientes = clientes_filtrados.head(top_n).sort_values("volume_total", ascending=True)
    
    # CORREÇÃO: Verificar quais colunas estão disponíveis para o hover_data
    hover_columns = ["n_transacoes", "ticket_medio"]
    available_columns = [col for col in ["cliente_tipo", "cliente_email", "cliente_uf"] 
                        if col in top_clientes.columns]
    hover_columns.extend(available_columns)
    
    fig1 = px.bar(top_clientes, 
                 x="volume_total", 
                 y="client_label", 
                 orientation='h',
                 title=f"Top {top_n} Clientes por Volume",
                 labels={"volume_total": "Volume Total (R$)", "client_label": "Cliente"},
                 hover_data=hover_columns)
    
    st.plotly_chart(fig1, use_container_width=True)

    # Análise por tipo de cliente
    if "cliente_tipo" in clientes_filtrados.columns:
        st.subheader("📈 Análise por Tipo de Cliente")
        
        por_tipo = clientes_filtrados.groupby("cliente_tipo").agg(
            num_clientes=("client_label", "count"),
            volume_total=("volume_total", "sum"),
            media_transacoes=("n_transacoes", "mean")
        ).reset_index()
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig2 = px.pie(por_tipo, values="volume_total", names="cliente_tipo",
                         title="Distribuição de Volume por Tipo")
            st.plotly_chart(fig2, use_container_width=True)
        
        with col2:
            fig3 = px.bar(por_tipo, x="cliente_tipo", y="num_clientes",
                         title="Número de Clientes por Tipo",
                         labels={"cliente_tipo": "Tipo", "num_clientes": "Nº Clientes"})
            st.plotly_chart(fig3, use_container_width=True)

    # Análise por UF se disponível
    if "cliente_uf" in clientes_filtrados.columns:
        st.subheader("🗺️ Análise por Estado (UF)")
        
        por_uf = clientes_filtrados.groupby("cliente_uf").agg(
            num_clientes=("client_label", "count"),
            volume_total=("volume_total", "sum"),
            media_transacoes=("n_transacoes", "mean")
        ).reset_index()
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig4 = px.bar(por_uf.sort_values("volume_total", ascending=False).head(10),
                         x="cliente_uf", y="volume_total",
                         title="Top 10 Estados por Volume",
                         labels={"volume_total": "Volume Total (R$)", "cliente_uf": "UF"})
            st.plotly_chart(fig4, use_container_width=True)
        
        with col2:
            fig5 = px.bar(por_uf.sort_values("num_clientes", ascending=False).head(10),
                         x="cliente_uf", y="num_clientes",
                         title="Top 10 Estados por Nº de Clientes",
                         labels={"cliente_uf": "UF", "num_clientes": "Nº Clientes"})
            st.plotly_chart(fig5, use_container_width=True)

    # Tabela detalhada
    st.subheader("📋 Tabela Completa de Clientes")
    
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
    
    # Configuração das colunas para a tabela
    column_config = {
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
        mime="text/csv"
    )

    # Análise demográfica
    if "idade" in clientes_filtrados.columns:
        st.subheader("👥 Análise Demográfica")
        
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
            
            fig6 = px.bar(por_idade, x="faixa_etaria", y="num_clientes",
                         title="Distribuição por Faixa Etária",
                         labels={"faixa_etaria": "Faixa Etária", "num_clientes": "Nº Clientes"})
            st.plotly_chart(fig6, use_container_width=True)
        
        with col2:
            fig7 = px.scatter(clientes_filtrados, x="idade", y="volume_total",
                             title="Volume vs Idade",
                             labels={"idade": "Idade", "volume_total": "Volume Total"},
                             hover_data=["client_label"])
            st.plotly_chart(fig7, use_container_width=True)

else:
    st.warning("Não foi possível realizar a análise de clientes.")