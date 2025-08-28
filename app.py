# app.py
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import io
from pathlib import Path
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from reportlab.lib import utils
from PIL import Image
import locale

# ---------- Config ----------
st.set_page_config(page_title="BanVic Analytics", page_icon="📊", layout="wide")
DATA_DIR = Path("data")

# Tentar configurar locale para português
try:
    locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')
except:
    try:
        locale.setlocale(locale.LC_TIME, 'Portuguese_Brazil.1252')
    except:
        st.warning("Não foi possível configurar o locale para português. As datas serão em inglês.")

# ---------- CSS (cards + refinamento visual) ----------
CSS = """
<style>
/* page background */
[data-testid="stAppViewContainer"]{
  background: linear-gradient(180deg,#f7fbff 0%, #ffffff 100%);
}

/* card grid */
.kpi-grid{
  display:flex;
  gap:12px;
  margin-bottom:12px;
}
.kpi-card{
  flex:1;
  background: white;
  border-radius: 12px;
  padding: 18px;
  box-shadow: 0 6px 18px rgba(28,45,70,0.06);
  border: 1px solid rgba(16,24,40,0.04);
}
.kpi-title{
  color:#6b7280;
  font-size:13px;
  margin-bottom:8px;
}
.kpi-value{
  font-size:22px;
  font-weight:700;
  color:#0f172a;
}
.kpi-delta{
  color:#10b981;
  font-weight:600;
  margin-top:6px;
}
.section-card{
  background:white;
  padding:16px;
  border-radius:10px;
  box-shadow: 0 6px 18px rgba(28,45,70,0.04);
  border: 1px solid rgba(16,24,40,0.04);
  margin-bottom:16px;
}
.small-muted{ color:#6b7280; font-size:13px; }
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

# ---------- Helpers (load / guess columns) ----------
def find_file(names):
    for n in names:
        p = DATA_DIR / n
        if p.exists():
            return p
    return None

@st.cache_data
def load_csv_auto(path):
    try:
        return pd.read_csv(path)
    except Exception:
        try:
            return pd.read_csv(path, sep=";")
        except Exception:
            return pd.read_csv(path, encoding="latin1", sep=";")

@st.cache_data
def load_data():
    files = {
        "transacoes": find_file(["transacoes.csv","transactions.csv","transacao.csv"]),
        "agencias": find_file(["agencias.csv","agencias_brv.csv","agencia.csv","branches.csv"]),
        "clientes": find_file(["clientes.csv","cliente.csv","customers.csv"]),
    }
    out = {}
    for k,p in files.items():
        out[k] = load_csv_auto(p) if p is not None else None
    return out

def guess_col(df, keywords):
    if df is None: return None
    cols = list(df.columns)
    for kw in keywords:
        for c in cols:
            if kw in c.lower():
                return c
    # fallback: return first
    return cols[0] if cols else None

def to_datetime_safe(s):
    return pd.to_datetime(s, errors="coerce", dayfirst=True)

# Função para formatar datas em português
def format_date_pt_br(date_obj):
    try:
        if pd.isna(date_obj):
            return "N/A"
        return date_obj.strftime("%d/%m/%Y")
    except:
        return str(date_obj)

# ---------- Load ----------
data = load_data()
transacoes = data.get("transacoes")
agencias = data.get("agencias")
clientes = data.get("clientes")

if transacoes is None:
    st.error("Arquivo de transações não encontrado em `data/`. Adicione `transacoes.csv` e recarregue.")
    st.stop()

# normalize whitespace in headers
transacoes.columns = [c.strip() for c in transacoes.columns]
if agencias is not None: agencias.columns = [c.strip() for c in agencias.columns]
if clientes is not None: clientes.columns = [c.strip() for c in clientes.columns]

# guess useful cols
date_col = guess_col(transacoes, ["data","date","dt","timestamp","created"])
amount_col = guess_col(transacoes, ["valor","amount","vlr","montante","price"])
agency_id_col = guess_col(transacoes, ["agencia","branch","agency","branch_id"])
client_id_col = guess_col(transacoes, ["cliente","client","customer","cust_id"])
status_col = guess_col(transacoes, ["status","situacao","resultado","aprov"])

# create parsed columns
transacoes["_dt"] = to_datetime_safe(transacoes[date_col]) if date_col in transacoes.columns else pd.NaT
transacoes["_amt"] = pd.to_numeric(transacoes[amount_col], errors="coerce") if amount_col in transacoes.columns else pd.to_numeric(transacoes.iloc[:,0], errors="coerce")
# normalized status flag
if status_col and status_col in transacoes.columns:
    s = transacoes[status_col].astype(str).str.lower()
    transacoes["_approved"] = s.str.contains("aprova|aprov|ok|sucess|conclu", na=False)
else:
    transacoes["_approved"] = True

# ---------- Sidebar filters ----------
st.sidebar.title("Filtros")
min_date = transacoes["_dt"].min()
max_date = transacoes["_dt"].max()

# Handle NaT values for date range
if pd.isna(min_date) or pd.isna(max_date):
    min_date = datetime.today()
    max_date = datetime.today()

# Converter para date objects para o date_input
min_date_date = min_date.date() if not pd.isna(min_date) else datetime.today().date()
max_date_date = max_date.date() if not pd.isna(max_date) else datetime.today().date()

# Date input com formato brasileiro
date_range = st.sidebar.date_input(
    "Período", 
    value=[min_date_date, max_date_date],
    format="DD/MM/YYYY"
)

# agencia select
ag_name_col = None
ag_master_id_col = None
if agencias is not None:
    ag_name_col = guess_col(agencias, ["nome","name","descricao","city","cidade"])
    ag_master_id_col = guess_col(agencias, ["id","agencia","branch","branch_id"])

agency_options = ["Todas"]
if agencias is not None and ag_name_col in agencias.columns:
    agency_options += sorted(agencias[ag_name_col].astype(str).unique().tolist())
elif agency_id_col in transacoes.columns:
    agency_options += sorted(transacoes[agency_id_col].astype(str).unique().tolist())

sel_ag = st.sidebar.selectbox("Agência", agency_options)

# client filter (optional)
client_options = ["Todos"]
if clientes is not None:
    cli_name = guess_col(clientes, ["nome","name","razao","cliente"])
    if cli_name in clientes.columns:
        client_options += sorted(clientes[cli_name].astype(str).unique().tolist())
sel_client = st.sidebar.selectbox("Cliente (opcional)", client_options)

# Apply filters
df = transacoes.copy()
if date_range and len(date_range) == 2:
    start, end = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
    # Ensure both datetime objects are timezone-naive or both timezone-aware
    if hasattr(df["_dt"].dtype, 'tz'):
        # If _dt is timezone-aware, make start/end timezone-aware with same timezone
        start = start.tz_localize(df["_dt"].dt.tz)
        end = end.tz_localize(df["_dt"].dt.tz)
    else:
        # If _dt is timezone-naive, ensure start/end are also timezone-naive
        start = start.tz_localize(None) if hasattr(start, 'tz') and start.tz is not None else start
        end = end.tz_localize(None) if hasattr(end, 'tz') and end.tz is not None else end
    
    df = df.loc[(df["_dt"] >= start) & (df["_dt"] <= end)]

if sel_ag != "Todas" and agency_id_col in df.columns:
    # try map name -> id if agency master table present
    if agencias is not None and ag_name_col and ag_master_id_col:
        ids = agencias.loc[agencias[ag_name_col].astype(str) == sel_ag, ag_master_id_col].unique()
        if len(ids):
            df = df[df[agency_id_col].isin(ids)]
        else:
            df = df[df[agency_id_col].astype(str) == sel_ag]
    else:
        df = df[df[agency_id_col].astype(str) == sel_ag]

if sel_client != "Todos" and client_id_col in df.columns and clientes is not None:
    # try join by name if possible
    cli_name_col = guess_col(clientes, ["nome","name","razao"])
    cli_id_master = guess_col(clientes, ["id","cliente","customer"])
    if cli_name_col and cli_id_master:
        ids = clientes.loc[clientes[cli_name_col].astype(str) == sel_client, cli_id_master].unique()
        if len(ids):
            df = df[df[client_id_col].isin(ids)]
    else:
        df = df[df[client_id_col].astype(str) == sel_client]

# save filtered df in session_state for PDF
st.session_state["df_filtrado"] = df
st.session_state["meta_info"] = {
    "date_col": "_dt",
    "amount_col": "_amt",
    "agency_id_col": agency_id_col,
    "client_id_col": client_id_col,
    "agencias_df": agencias,
    "clientes_df": clientes
}

# ---------- Header / KPIs (cards) ----------
st.title("BanVic Analytics — Dashboard")
st.markdown("Painel interativo com KPIs, ranking de agências, análise de clientes e tendências. Use os filtros na lateral.")

# compute KPIs
total_trans = int(len(df))
total_vol = float(df["_amt"].sum(skipna=True)) if "_amt" in df.columns else 0.0
ticket = total_vol / total_trans if total_trans > 0 else 0.0
aprov_rate = df["_approved"].mean() * 100 if "_approved" in df.columns else np.nan

# small helper to render cards
def kpi_card(title, value, delta=None, fmt=None):
    delta_html = f'<div class="kpi-delta">{delta}</div>' if delta is not None else ""
    val = f"{value}" if fmt is None else fmt.format(value)
    html = f"""
    <div class="kpi-card">
      <div class="kpi-title">{title}</div>
      <div class="kpi-value">{val}</div>
      {delta_html}
    </div>
    """
    return html

cols = st.columns([1,1,1,1])
with cols[0]:
    st.markdown(kpi_card("Total de Transações", f"{total_trans:,}".replace(",", ".")), unsafe_allow_html=True)
with cols[1]:
    st.markdown(kpi_card("Volume Total (R$)", f"{total_vol:,.2f}".replace(",", ".")), unsafe_allow_html=True)
with cols[2]:
    st.markdown(kpi_card("Ticket Médio (R$)", f"{ticket:,.2f}".replace(",", ".")), unsafe_allow_html=True)
with cols[3]:
    aprov_display = f"{aprov_rate:.1f}%" if not np.isnan(aprov_rate) else "N/A"
    st.markdown(kpi_card("Taxa de Aprovação", aprov_display), unsafe_allow_html=True)

st.markdown("---")

# ---------- Layout: left filters + right content (using columns) ----------
left, right = st.columns([1.1, 2.8])

with left:
    st.markdown('<div class="section-card"> <h4>Resumo Rápido</h4>', unsafe_allow_html=True)
    if date_range and len(date_range) == 2:
        start, end = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
        # Usar formatação brasileira
        st.write(f"Período: **{format_date_pt_br(start)}** → **{format_date_pt_br(end)}**")
    st.write(f"Agência: **{sel_ag}**")
    st.write(f"Clientes (filtro): **{sel_client}**")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="section-card"> <h4>Export</h4>', unsafe_allow_html=True)
    st.write("Exportar relatório PDF com os dados e gráficos do período e filtros aplicados.")
    if st.button("Gerar e baixar PDF"):
        # generate pdf bytes and provide download button
        buffer = io.BytesIO()
        # Build PDF with ReportLab into buffer
        c = canvas.Canvas(buffer, pagesize=A4)
        W, H = A4
        # Cover
        c.setFont("Helvetica-Bold", 18)
        c.drawString(2*cm, H-2.5*cm, "BanVic - Relatório Analítico")
        c.setFont("Helvetica", 10)
        c.drawString(2*cm, H-3.5*cm, f"Período: {format_date_pt_br(start)} → {format_date_pt_br(end)}")
        c.drawString(2*cm, H-4.0*cm, f"Filtro Agência: {sel_ag}")
        c.drawString(2*cm, H-4.5*cm, f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        c.line(2*cm, H-5*cm, W-2*cm, H-5*cm)
        c.showPage()

        # KPIs page
        c.setFont("Helvetica-Bold", 14)
        c.drawString(2*cm, H-2.5*cm, "KPIs")
        c.setFont("Helvetica", 11)
        c.drawString(2*cm, H-3.5*cm, f"Total de Transações: {total_trans}")
        c.drawString(2*cm, H-4.0*cm, f"Volume Total (R$): {total_vol:,.2f}")
        c.drawString(2*cm, H-4.5*cm, f"Ticket Médio (R$): {ticket:,.2f}")
        c.drawString(2*cm, H-5.0*cm, f"Taxa de Aprovação: {aprov_display}")
        c.showPage()

        # Gráfico: volume mensal
        try:
            tmp = df.copy()
            tmp["_month"] = tmp["_dt"].dt.to_period("M").dt.to_timestamp()
            monthly = tmp.groupby("_month")["_amt"].sum().reset_index().sort_values("_month")
            # save plot as image (matplotlib) to embed in PDF
            import matplotlib.pyplot as plt
            fig, ax = plt.subplots(figsize=(8,3.5))
            # Formatando as datas no eixo X como DD/MM/YYYY
            monthly["_month_str"] = monthly["_month"].dt.strftime("%d/%m/%Y")
            ax.plot(monthly["_month_str"], monthly["_amt"], marker="o")
            ax.set_title("Volume Mensal")
            ax.set_xlabel("Mês")
            ax.set_ylabel("Volume (R$)")
            plt.xticks(rotation=45, ha="right")
            plt.tight_layout()
            img_buf = io.BytesIO()
            fig.savefig(img_buf, format="png", dpi=150)
            plt.close(fig)
            img_buf.seek(0)
            # draw image on pdf
            img = utils.ImageReader(img_buf)
            iw, ih = img.getSize()
            max_w = W - 4*cm
            max_h = H/2
            ratio = min(max_w/iw, max_h/ih)
            w, h = iw*ratio, ih*ratio
            c.drawImage(img, 2*cm, H-3.5*cm - h, width=w, height=h)
            c.showPage()
        except Exception as e:
            c.setFont("Helvetica", 10)
            c.drawString(2*cm, H-3.5*cm, "Erro ao gerar gráfico no PDF: " + str(e))
            c.showPage()

        # Resto do código do PDF permanece igual...
        # ... [o restante do código do PDF]

        c.setFont("Helvetica", 10)
        c.drawString(2*cm, 2*cm, "Relatório gerado automaticamente — BanVic Analytics")
        c.save()
        buffer.seek(0)

        btn = st.download_button("📥 Baixar Relatório PDF", data=buffer, file_name=f"Relatorio_BanVic_{start.strftime('%d-%m-%Y')}_{end.strftime('%d-%m-%Y')}.pdf", mime="application/pdf")
    st.markdown("</div>", unsafe_allow_html=True)

with right:
    # Main visualizations
    st.markdown('<div class="section-card"><h4>Volume Mensal</h4>', unsafe_allow_html=True)
    if df.empty:
        st.warning("Sem dados no período selecionado.")
    else:
        df["_month"] = df["_dt"].dt.to_period("M").dt.to_timestamp()
        monthly = df.groupby("_month")["_amt"].sum().reset_index().sort_values("_month")
        # Formatando as datas para o gráfico
        monthly["_month_str"] = monthly["_month"].dt.strftime("%d/%m/%Y")
        fig = px.line(monthly, x="_month_str", y="_amt", markers=True, title="Volume Mensal")
        fig.update_layout(xaxis_title="Mês", yaxis_title="Volume (R$)")
        st.plotly_chart(fig, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # Resto do código permanece similar, mas você pode atualizar outros gráficos também...

# ---------- Save variables for pages ----------
st.session_state["df_filtered"] = df
st.session_state["amount_col"] = "_amt"
st.session_state["date_col"] = "_dt"
st.session_state["agency_id_col"] = agency_id_col
st.session_state["client_id_col"] = client_id_col
st.session_state["agencias_df"] = agencias
st.session_state["clientes_df"] = clientes

# ---------- Footer ----------
st.markdown("---")
st.markdown("© BanVic — Dashboard de Analytics. Desenvolvido como PoC.")


st.markdown('<div class="section-card"><h4>Top Agências (6 meses)</h4>', unsafe_allow_html=True)
try:
    tmp = df.copy()
    max_date = tmp["_dt"].max()
    start6 = max_date - pd.DateOffset(months=6)
    tmp6 = tmp[tmp["_dt"] >= start6]
    
    # label agency - CORREÇÃO: verificar se o DataFrame não é None e não está vazio
    agencies = st.session_state["meta_info"]["agencias_df"]
    if agencies is not None and not agencies.empty:
        ag_name = guess_col(agencies, ["nome","name","descricao","city","cidade"])
        ag_id = guess_col(agencies, ["id","agencia","branch","branch_id"])
        
        if ag_name and ag_id in agencies.columns and agency_id_col in tmp6.columns:
            # CORREÇÃO: garantir que as colunas tenham o mesmo tipo antes do merge
            mapa = agencies[[ag_id, ag_name]].drop_duplicates()
            
            # Converter ambas as colunas para string para evitar conflitos de tipo
            tmp6[agency_id_col] = tmp6[agency_id_col].astype(str)
            mapa[ag_id] = mapa[ag_id].astype(str)
            
            tmp6 = tmp6.merge(mapa, left_on=agency_id_col, right_on=ag_id, how="left")
            tmp6["ag_label"] = tmp6[ag_name].fillna(tmp6[agency_id_col].astype(str))
        else:
            tmp6["ag_label"] = tmp6[agency_id_col].astype(str) if agency_id_col in tmp6.columns else "desconhecida"
    else:
        tmp6["ag_label"] = tmp6[agency_id_col].astype(str) if agency_id_col in tmp6.columns else "desconhecida"

    if not tmp6.empty:
        ranking6 = tmp6.groupby("ag_label")["_amt"].agg(["count","sum"]).reset_index().rename(columns={"count":"n_trans","sum":"volume"}).sort_values("n_trans", ascending=False)
        
        if not ranking6.empty:
            st.plotly_chart(px.bar(ranking6.head(10).sort_values("n_trans"), 
                                  x="n_trans", y="ag_label", 
                                  orientation="h", 
                                  title="Top 10 - nº transações (6m)",
                                  labels={"n_trans": "Número de Transações", "ag_label": "Agência"}),
                           use_container_width=True)
            st.dataframe(ranking6.head(50).reset_index(drop=True))
        else:
            st.info("Nenhum dado disponível para o ranking de agências.")
    else:
        st.info("Nenhum dado disponível para os últimos 6 meses.")
        
except Exception as e:
    st.error("Erro ao calcular top agências: " + str(e))
    import traceback
    st.error(f"Detalhes do erro: {traceback.format_exc()}")
st.markdown("</div>", unsafe_allow_html=True)

st.markdown('<div class="section-card"><h4>Sazonalidade - Dia da Semana</h4>', unsafe_allow_html=True)
try:
    df["_weekday_pt"] = df["_dt"].dt.dayofweek.map({0:"segunda-feira",1:"terça-feira",2:"quarta-feira",3:"quinta-feira",4:"sexta-feira",5:"sábado",6:"domingo"})
    weekly = df.groupby("_weekday_pt")["_amt"].agg(["count","sum"]).reset_index().rename(columns={"count":"n_trans","sum":"volume"})
    order = ["segunda-feira","terça-feira","quarta-feira","quinta-feira","sexta-feira","sábado","domingo"]
    weekly["_ord"] = weekly["_weekday_pt"].apply(lambda x: order.index(x) if x in order else 99)
    weekly = weekly.sort_values("_ord")
    st.plotly_chart(px.bar(weekly, x="_weekday_pt", y="volume", title="Volume por Dia da Semana"), use_container_width=True)
except Exception as e:
    st.error("Erro sazonalidade: " + str(e))
st.markdown("</div>", unsafe_allow_html=True)


# ---------- Save variables for pages ----------
st.session_state["df_filtered"] = df
st.session_state["amount_col"] = "_amt"
st.session_state["date_col"] = "_dt"
st.session_state["agency_id_col"] = agency_id_col
st.session_state["client_id_col"] = client_id_col
st.session_state["agencias_df"] = agencias
st.session_state["clientes_df"] = clientes

# ---------- Footer ----------
st.markdown("---")
st.markdown("© BanVic — Dashboard de Analytics. Desenvolvido como PoC.")