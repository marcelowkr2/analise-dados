import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Agências | BanVic", layout="wide")

# Verificar se as variáveis de sessão existem
if "df_filtered" not in st.session_state:
    st.warning("Volte para a página inicial e aplique os filtros primeiro.")
    st.stop()

df = st.session_state["df_filtered"]
amount_col = st.session_state["amount_col"]
agency_id_col = st.session_state["agency_id_col"]
agencias = st.session_state["agencias_df"]

st.title("Análise por Agência")

if df.empty:
    st.warning("Sem dados no período selecionado.")
else:
    # try to attach agency name
    if agencias is not None and not agencias.empty and agency_id_col is not None and agency_id_col in df.columns:
        ag_id_master = next((c for c in agencias.columns if "id" in c.lower() or "agencia" in c.lower() or "branch" in c.lower()), agencias.columns[0])
        ag_name = next((c for c in agencias.columns if any(k in c.lower() for k in ["nome","name","descricao","cidade","city"])), None)
        
        if ag_name is not None and ag_id_master in agencias.columns:
            mapa = agencias[[ag_id_master, ag_name]].drop_duplicates()
            
            # CORREÇÃO: garantir que as colunas tenham o mesmo tipo antes do merge
            df[agency_id_col] = df[agency_id_col].astype(str)
            mapa[ag_id_master] = mapa[ag_id_master].astype(str)
            
            df = df.merge(mapa, left_on=agency_id_col, right_on=ag_id_master, how="left")
            df["agencia_label"] = df[ag_name].fillna(df[agency_id_col].astype(str))
        else:
            df["agencia_label"] = df[agency_id_col].astype(str)
    else:
        df["agencia_label"] = df[agency_id_col].astype(str) if agency_id_col in df.columns else "desconhecida"

   
date_col = st.session_state["date_col"]
max_date = df[date_col].max()
start_6m = (max_date - pd.DateOffset(months=6))
last6 = df[df[date_col] >= start_6m]

if not last6.empty:
    
    if not last6.empty:
        ranking = last6.groupby("agencia_label").agg(
            n_transacoes=(amount_col, "count"), 
            volume=(amount_col, "sum")
        ).reset_index().sort_values("n_transacoes", ascending=False)

        st.subheader("Ranking - Últimos 6 meses")
        top3 = ranking.head(3)
        bottom3 = ranking.tail(3)

        c1, c2 = st.columns(2)
        if not top3.empty:
            c1.metric("Top 1 (transações)", f"{top3.iloc[0]['agencia_label']}", f"{top3.iloc[0]['n_transacoes']:,} transações")
        if not bottom3.empty:
            c2.metric("Bottom 1 (transações)", f"{bottom3.iloc[-1]['agencia_label']}", f"{bottom3.iloc[-1]['n_transacoes']:,} transações")

        st.plotly_chart(px.bar(ranking.head(10).sort_values("n_transacoes"), 
                              x="n_transacoes", y="agencia_label", 
                              orientation="h", 
                              title="Top 10 Agências (nº transações - 6m)"), 
                       use_container_width=True)

        st.markdown("### Tabela completa de agências")
        st.dataframe(ranking.reset_index(drop=True))
    else:
        st.warning("Não há dados nos últimos 6 meses.")