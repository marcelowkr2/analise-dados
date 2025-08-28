# pages/3_Clientes.py
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Clientes | BanVic", layout="wide")

# Verificar se as variáveis de sessão existem
if "df_filtered" not in st.session_state:
    st.warning("Volte para a página inicial e aplique os filtros primeiro.")
    st.stop()

df = st.session_state["df_filtered"].copy()  # Fazer cópia para não modificar o original
amount_col = st.session_state["amount_col"]
clientes_df = st.session_state["clientes_df"]
client_id_col = st.session_state.get("client_id_col")

st.title("Análise de Clientes")

# Debug: mostrar colunas disponíveis
if st.checkbox("Mostrar colunas disponíveis (debug)"):
    st.write("Colunas no DataFrame de transações:", list(df.columns))
    if clientes_df is not None:
        st.write("Colunas na tabela de clientes:", list(clientes_df.columns))
        # Verificar colunas duplicadas
        trans_duplicates = [col for col in df.columns if list(df.columns).count(col) > 1]
        clientes_duplicates = [col for col in clientes_df.columns if list(clientes_df.columns).count(col) > 1]
        if trans_duplicates:
            st.error(f"Colunas duplicadas nas transações: {trans_duplicates}")
        if clientes_duplicates:
            st.error(f"Colunas duplicadas nos clientes: {clientes_duplicates}")

# Tentar identificar coluna de cliente de várias formas
if client_id_col is None or client_id_col not in df.columns:
    possible_client_cols = [
        c for c in df.columns 
        if any(kw in c.lower() for kw in [
            "cliente", "client", "customer", "cust_id", "id_cliente", 
            "cod_cliente", "client_id", "customer_id", "cpf", "cnpj", "documento"
        ])
    ]
    
    if possible_client_cols:
        client_id_col = possible_client_cols[0]
        st.session_state["client_id_col"] = client_id_col
        st.info(f"Coluna de cliente identificada: **{client_id_col}**")
    else:
        st.warning("Coluna de cliente não identificada automaticamente.")
        st.stop()

# SOLUÇÃO DEFINITIVA: Abordagem ultra-segura para evitar colunas duplicadas
if clientes_df is not None and not clientes_df.empty:
    # Fazer cópia profunda e limpar colunas duplicadas
    clientes_clean = clientes_df.copy()
    
    # Remover colunas duplicadas do DataFrame de clientes
    clientes_clean = clientes_clean.loc[:, ~clientes_clean.columns.duplicated()]
    
    # Encontrar coluna de nome e ID na tabela de clientes
    client_name_col = next((c for c in clientes_clean.columns 
                           if any(kw in c.lower() for kw in ["nome", "name", "razao", "razão", "fantasia", "cliente"])), None)
    
    client_id_master = next((c for c in clientes_clean.columns 
                            if any(kw in c.lower() for kw in ["id", "codigo", "código", "cliente", "customer", "cpf", "cnpj"])), 
                           None)
    
    if client_name_col and client_id_master:
        try:
            # Criar DataFrame temporário apenas com as colunas necessárias
            clientes_temp = clientes_clean[[client_id_master, client_name_col]].copy()
            clientes_temp = clientes_temp.drop_duplicates()
            
            # Garantir que não há colunas duplicadas
            clientes_temp = clientes_temp.loc[:, ~clientes_temp.columns.duplicated()]
            
            # Renomear colunas com um sufixo único baseado no timestamp
            import time
            unique_suffix = f"_{int(time.time())}_{hash(client_id_master) % 1000}"
            
            clientes_temp_renamed = clientes_temp.rename(columns={
                client_id_master: f"{client_id_master}{unique_suffix}",
                client_name_col: f"{client_name_col}{unique_suffix}"
            })
            
            # Verificar e remover qualquer coluna duplicada que possa existir
            cols_to_drop = []
            for col in clientes_temp_renamed.columns:
                if col in df.columns:
                    cols_to_drop.append(col)
            
            if cols_to_drop:
                st.warning(f"Removendo colunas duplicadas: {cols_to_drop}")
                clientes_temp_renamed = clientes_temp_renamed.drop(columns=cols_to_drop)
            
            # Converter para string para evitar problemas de tipo
            right_key = f"{client_id_master}{unique_suffix}"
            clientes_temp_renamed[right_key] = clientes_temp_renamed[right_key].astype(str)
            df[client_id_col] = df[client_id_col].astype(str)
            
            # Fazer o merge de forma segura
            df = pd.merge(
                df, 
                clientes_temp_renamed, 
                left_on=client_id_col, 
                right_on=right_key, 
                how="left"
            )
            
            # Criar label do cliente
            client_name_col_renamed = f"{client_name_col}{unique_suffix}"
            if client_name_col_renamed in df.columns:
                df["client_label"] = df[client_name_col_renamed].fillna(df[client_id_col].astype(str))
                # Remover coluna temporária
                df = df.drop(columns=[client_name_col_renamed], errors="ignore")
            else:
                df["client_label"] = df[client_id_col].astype(str)
            
            # Remover coluna de ID temporária
            if right_key in df.columns:
                df = df.drop(columns=[right_key], errors="ignore")
            
            st.success(f"Clientes vinculados com sucesso: {client_id_master} → {client_name_col}")
            
        except Exception as e:
            st.error(f"Erro técnico ao vincular clientes: {str(e)}")
            st.info("Usando apenas IDs das transações (fallback)")
            df["client_label"] = df[client_id_col].astype(str)
    else:
        df["client_label"] = df[client_id_col].astype(str)
        missing = []
        if not client_name_col: missing.append("nome")
        if not client_id_master: missing.append("ID")
        st.info(f"Usando IDs de cliente (colunas {missing} não disponíveis)")
else:
    df["client_label"] = df[client_id_col].astype(str) if client_id_col in df.columns else "desconhecida"
    st.info("Tabela de clientes não disponível - usando IDs das transações")

# SOLUÇÃO DE FALLBACK GARANTIDA (descomente se necessário)
# df["client_label"] = df[client_id_col].astype(str) if client_id_col in df.columns else "desconhecida"

# Análise de clientes
if not df.empty and "client_label" in df.columns:
    # Verificar se há dados suficientes
    unique_clients = df["client_label"].nunique()
    
    if unique_clients == 0:
        st.warning("Nenhum cliente identificado para análise.")
        st.stop()
    
    ranking_clients = df.groupby("client_label").agg(
        n_transacoes=(amount_col, "count"), 
        volume=(amount_col, "sum"),
        ticket_medio=(amount_col, "mean")
    ).reset_index().sort_values("volume", ascending=False)
    
    # Estatísticas básicas
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total de Clientes", f"{len(ranking_clients):,}")
    with col2:
        if not ranking_clients.empty:
            top_client = ranking_clients.iloc[0]["client_label"]
            top_volume = ranking_clients.iloc[0]["volume"]
            st.metric("Maior Cliente", top_client, f"R$ {top_volume:,.2f}")
        else:
            st.metric("Maior Cliente", "N/A")
    with col3:
        total_volume = ranking_clients["volume"].sum()
        st.metric("Volume Total", f"R$ {total_volume:,.2f}")
    
    st.subheader("Top 20 Clientes por Volume")
    
    if not ranking_clients.empty:
        # Gráfico de top clientes
        top_20 = ranking_clients.head(20).sort_values("volume", ascending=True)
        fig = px.bar(top_20, 
                    x="volume", 
                    y="client_label", 
                    orientation='h',
                    title="Top 20 Clientes por Volume",
                    labels={"volume": "Volume (R$)", "client_label": "Cliente"},
                    hover_data=["n_transacoes", "ticket_medio"])
        st.plotly_chart(fig, use_container_width=True)
        
        # Tabela detalhada
        st.subheader("Tabela Completa de Clientes")
        ranking_clients_display = ranking_clients.copy()
        ranking_clients_display["volume"] = ranking_clients_display["volume"].round(2)
        ranking_clients_display["ticket_medio"] = ranking_clients_display["ticket_medio"].round(2)
        
        st.dataframe(
            ranking_clients_display.head(100),
            column_config={
                "client_label": "Cliente",
                "n_transacoes": st.column_config.NumberColumn("Nº Transações", format="%d"),
                "volume": st.column_config.NumberColumn("Volume", format="R$ %.2f"),
                "ticket_medio": st.column_config.NumberColumn("Ticket Médio", format="R$ %.2f")
            },
            use_container_width=True,
            height=400
        )
        
        # Download dos dados
        csv = ranking_clients_display.to_csv(index=False)
        st.download_button(
            label="📥 Download CSV",
            data=csv,
            file_name="ranking_clientes.csv",
            mime="text/csv"
        )
    else:
        st.warning("Nenhum dado de cliente disponível para análise.")
else:
    st.warning("Não foi possível realizar a análise de clientes.")