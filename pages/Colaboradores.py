import streamlit as st
import pandas as pd

st.set_page_config(page_title="Colaboradores | BanVic", layout="wide")

# Carregar colaboradores
if "df_colaboradores" not in st.session_state:
    try:
        st.session_state.df_colaboradores = pd.read_csv("colaboradores.csv")
    except FileNotFoundError:
        st.error("Arquivo colaboradores.csv não encontrado!")
        st.stop()

df_colaboradores = st.session_state.df_colaboradores

st.title("👥 Colaboradores")

st.dataframe(df_colaboradores)

# Exemplo: adicionar salário fictício
if "salario_base" not in df_colaboradores.columns:
    df_colaboradores["salario_base"] = [3500, 4200, 5000]  # ajustar manual ou calcular

custo_total = df_colaboradores["salario_base"].sum()

st.metric("💸 Custo Total da Folha", f"R$ {custo_total:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
