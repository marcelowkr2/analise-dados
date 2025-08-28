import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import io
from pathlib import Path
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image as ReportLabImage
)
from reportlab.lib.units import inch
from reportlab.lib.utils import ImageReader
import matplotlib.pyplot as plt
import locale
import os
import traceback

st.set_page_config(page_title="BanVic Analytics", page_icon="📊", layout="wide")
DATA_DIR = Path("data")

# locale (tentativa pt_BR)
try:
    locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')
except Exception:
    try:
        locale.setlocale(locale.LC_TIME, 'Portuguese_Brazil.1252')
    except Exception:
        st.warning("Não foi possível configurar o locale para português. As datas serão em inglês.")

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

def find_file(names):
    for n in names:
        p = DATA_DIR / n
        if p.exists():
            return p
    return None

@st.cache_data
def load_csv_auto(path):
    # path might be None
    if path is None:
        return None
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
    return cols[0] if cols else None

def to_datetime_safe(s):
    return pd.to_datetime(s, errors="coerce", dayfirst=True)

def format_date_pt_br(date_obj):
    try:
        if pd.isna(date_obj):
            return "N/A"
        # se for pandas Timestamp ou datetime
        if hasattr(date_obj, "strftime"):
            return date_obj.strftime("%d/%m/%Y")
        return str(date_obj)
    except:
        return str(date_obj)

# ---------- Função para gerar PDF completo ----------
def generate_comprehensive_pdf(df, start_date, end_date, sel_ag, total_trans, total_vol, ticket, aprov_rate):
    """
    Gera relatório PDF completo com capa, KPIs, gráficos e ranking.
    Usa ImageReader com BytesIO para evitar problemas de arquivos temporários.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.5*inch, bottomMargin=0.5*inch)
    styles = getSampleStyleSheet()
    story = []

    # estilos
    title_style = ParagraphStyle('CustomTitle', parent=styles['Title'], fontSize=18, spaceAfter=20, alignment=1)
    heading_style = ParagraphStyle('CustomHeading', parent=styles['Heading2'], fontSize=14, spaceAfter=12, spaceBefore=12)
    normal_style = styles['Normal']

    # capa (função para a primeira página)
    def create_cover(canvas_obj, doc_obj):
        canvas_obj.saveState()
        canvas_obj.setFont('Helvetica-Bold', 20)
        canvas_obj.setFont('Helvetica', 12)
        canvas_obj.drawCentredString(A4[0]/2, A4[1]-2.5*inch, f"Período: {format_date_pt_br(start_date)} a {format_date_pt_br(end_date)}")
        canvas_obj.drawCentredString(A4[0]/2, A4[1]-3*inch, f"Agência: {sel_ag}")
        canvas_obj.drawCentredString(A4[0]/2, A4[1]-3.5*inch, f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
        canvas_obj.restoreState()

    # conteúdo (também aparece na primeira página)
    story.append(Paragraph("RELATÓRIO ANALÍTICO BANVIC", title_style))
    story.append(Spacer(1, 12))
    story.append(Paragraph(f"<b>Período:</b> {format_date_pt_br(start_date)} a {format_date_pt_br(end_date)}", normal_style))
    story.append(Paragraph(f"<b>Agência:</b> {sel_ag}", normal_style))
    story.append(Paragraph(f"<b>Gerado em:</b> {datetime.now().strftime('%d/%m/%Y %H:%M')}", normal_style))
    story.append(Spacer(1, 18))

    # KPIs
    story.append(Paragraph("PRINCIPAIS KPIs", heading_style))
    kpi_data = [
        ['KPI', 'Valor'],
        ['Total de Transações', f'{total_trans:,}'.replace(",", ".")],
        ['Volume Total', f'R$ {total_vol:,.2f}'.replace(",", ".")],
        ['Ticket Médio', f'R$ {ticket:,.2f}'.replace(",", ".")],
        ['Taxa de Aprovação', f'{aprov_rate:.1f}%' if not np.isnan(aprov_rate) else 'N/A']
    ]
    kpi_table = Table(kpi_data, colWidths=[2.5*inch, 2.5*inch])
    kpi_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#4B5563")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor("#F5F5DC")),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
    ]))
    story.append(kpi_table)
    story.append(Spacer(1, 12))

    # GRÁFICO: Volume Mensal (usa BytesIO -> ImageReader)
    story.append(Paragraph("VOLUME MENSAL", heading_style))
    try:
        if df is None or df.empty or "_dt" not in df.columns or "_amt" not in df.columns:
            story.append(Paragraph("Sem dados para o gráfico de volume mensal.", normal_style))
        else:
            df_temp = df.copy()
            # garantir coluna de datas
            df_temp["_month"] = df_temp["_dt"].dt.to_period("M").dt.to_timestamp()
            monthly = df_temp.groupby("_month")["_amt"].sum().reset_index().sort_values("_month")

            # se não houver dados suficientes
            if monthly.empty:
                story.append(Paragraph("Sem dados agregados por mês.", normal_style))
            else:
                fig, ax = plt.subplots(figsize=(8, 3.5))
                monthly["_month_str"] = monthly["_month"].dt.strftime("%m/%Y")
                ax.plot(monthly["_month_str"], monthly["_amt"], marker='o', linewidth=2)
                ax.set_title("Volume Mensal (R$)")
                ax.set_xlabel("Mês")
                ax.set_ylabel("Volume (R$)")
                plt.xticks(rotation=45, ha='right')
                plt.tight_layout()

                img_buffer = io.BytesIO()
                fig.savefig(img_buffer, format='png', dpi=150, bbox_inches='tight')
                plt.close(fig)
                img_buffer.seek(0)
                img_reader = ImageReader(img_buffer)
                story.append(ReportLabImage(img_reader, width=6*inch, height=3*inch))
    except Exception as e:
        story.append(Paragraph(f"Erro ao gerar gráfico: {str(e)}", normal_style))

    story.append(Spacer(1, 12))

    # RANKING TOP 10 AGÊNCIAS
    story.append(Paragraph("RANKING TOP 10 AGÊNCIAS", heading_style))
    try:
        tmp = df.copy() if df is not None else pd.DataFrame()
        meta = st.session_state.get("meta_info", {})
        agency_id_col = meta.get("agency_id_col")
        agencias_df = meta.get("agencias_df")

        if agency_id_col and agency_id_col in tmp.columns:
            if agencias_df is not None and not agencias_df.empty:
                ag_name_col = guess_col(agencias_df, ["nome","name","descricao","city","cidade"])
                ag_id_col = guess_col(agencias_df, ["id","agencia","branch","branch_id"])
                if ag_name_col and ag_id_col and ag_id_col in agencias_df.columns:
                    mapa = agencias_df[[ag_id_col, ag_name_col]].drop_duplicates()
                    mapa[ag_id_col] = mapa[ag_id_col].astype(str)
                    tmp[agency_id_col] = tmp[agency_id_col].astype(str)
                    tmp = tmp.merge(mapa, left_on=agency_id_col, right_on=ag_id_col, how="left")
                    tmp["ag_label"] = tmp[ag_name_col].fillna(tmp[agency_id_col].astype(str))
                else:
                    tmp["ag_label"] = tmp[agency_id_col].astype(str)
            else:
                tmp["ag_label"] = tmp[agency_id_col].astype(str)
        else:
            # fallback
            tmp["ag_label"] = tmp[agency_id_col].astype(str) if agency_id_col in tmp.columns else "desconhecida"

        ranking = tmp.groupby("ag_label")["_amt"].agg(["count", "sum"]).reset_index().sort_values("count", ascending=False)
        ranking_data = [['Posição', 'Agência', 'Transações', 'Volume (R$)']]
        for i, (_, row) in enumerate(ranking.head(10).iterrows(), 1):
            ranking_data.append([
                str(i),
                str(row['ag_label'])[:40],
                f"{int(row['count']):,}".replace(",", "."),
                f"R$ {float(row['sum']):,.2f}".replace(",", ".")
            ])

        if len(ranking_data) == 1:
            story.append(Paragraph("Sem dados para ranking.", normal_style))
        else:
            ranking_table = Table(ranking_data, colWidths=[0.5*inch, 2.5*inch, 1*inch, 1.5*inch])
            ranking_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#4B5563")),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor("#F5F5DC")),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
            ]))
            story.append(ranking_table)
    except Exception as e:
        story.append(Paragraph(f"Erro ao gerar ranking: {str(e)}", normal_style))

    story.append(Spacer(1, 12))

    # METODOLOGIA E RECOMENDAÇÕES
    story.append(Paragraph("METODOLOGIA E RECOMENDAÇÕES", heading_style))
    metodologia_text = """
    <b>Metodologia Utilizada:</b><br/>
    • Análise exploratória dos dados transacionais<br/>
    • Processamento e limpeza com Python/Pandas<br/>
    • Visualização com Plotly e Matplotlib<br/>
    • Desenvolvimento de dashboard interativo<br/>
    <br/>
    <b>Recomendações Estratégicas:</b><br/>
    • Focar nas agências de alto desempenho como benchmark<br/>
    • Implementar alertas para anomalias operacionais<br/>
    • Expandir análise para incluir dados demográficos<br/>
    • Desenvolver data warehouse corporativo<br/>
    """
    story.append(Paragraph(metodologia_text, normal_style))
    story.append(Spacer(1, 12))

    # Rodapé para páginas posteriores
    def add_footer(canvas_obj, doc_obj):
        canvas_obj.saveState()
        canvas_obj.setFont('Helvetica', 8)
        canvas_obj.drawString(0.5*inch, 0.5*inch, f"BanVic Analytics - Página {doc_obj.page}")
        canvas_obj.drawRightString(A4[0]-0.5*inch, 0.5*inch, datetime.now().strftime('%d/%m/%Y %H:%M'))
        canvas_obj.restoreState()

    # build PDF
    doc.build(story, onFirstPage=create_cover, onLaterPages=add_footer)
    buffer.seek(0)
    return buffer

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
if agencias is not None:
    agencias.columns = [c.strip() for c in agencias.columns]
if clientes is not None:
    clientes.columns = [c.strip() for c in clientes.columns]

# guess useful cols
date_col = guess_col(transacoes, ["data","date","dt","timestamp","created","datahora","datetime"])
amount_col = guess_col(transacoes, ["valor","amount","vlr","montante","price","total","value"])
agency_id_col = guess_col(transacoes, ["agencia","branch","agency","branch_id","cod_agencia","id_agencia"])
client_id_col = guess_col(transacoes, ["cliente","client","customer","cust_id","id_cliente","cod_cliente","cpf","cnpj","documento"])
status_col = guess_col(transacoes, ["status","situacao","resultado","aprov","approved","estado"])

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

min_date_date = min_date.date() if not pd.isna(min_date) else datetime.today().date()
max_date_date = max_date.date() if not pd.isna(max_date) else datetime.today().date()

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
start, end = None, None

if date_range and len(date_range) == 2:
    start, end = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
    # ensure naive datetimes for comparison
    start = pd.to_datetime(start).tz_localize("UTC")
    end = pd.to_datetime(end).tz_localize("UTC")
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
    if cli_name_col and cli_id_master and cli_name_col in clientes.columns:
        ids = clientes.loc[clientes[cli_name_col].astype(str) == sel_client, cli_id_master].unique()
        if len(ids):
            df = df[df[client_id_col].isin(ids)]
    else:
        df = df[df[client_id_col].astype(str) == sel_client]

# save filtered df and meta_info in session_state (padronizado)
st.session_state["df_filtered"] = df
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

# ---------- Layout: left filters + right content ----------
left, right = st.columns([1.1, 2.8])

with left:
    st.markdown('<div class="section-card"> <h4>Resumo Rápido</h4>', unsafe_allow_html=True)
    if date_range and len(date_range) == 2:
        st.write(f"Período: **{format_date_pt_br(start)}** → **{format_date_pt_br(end)}**")
    st.write(f"Agência: **{sel_ag}**")
    st.write(f"Clientes (filtro): **{sel_client}**")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="section-card"> <h4>Export</h4>', unsafe_allow_html=True)
    st.write("Exportar relatório PDF com os dados e gráficos do período e filtros aplicados.")

    if st.button("Gerar e baixar PDF"):
        try:
            pdf_buffer = generate_comprehensive_pdf(
                df=df,
                start_date=start,
                end_date=end,
                sel_ag=sel_ag,
                total_trans=total_trans,
                total_vol=total_vol,
                ticket=ticket,
                aprov_rate=aprov_rate
            )

            st.download_button(
                label="📥 Baixar Relatório PDF Completo",
                data=pdf_buffer,
                file_name=f"Relatorio_BanVic_{start.strftime('%d-%m-%Y')}_{end.strftime('%d-%m-%Y')}.pdf",
                mime="application/pdf"
            )

        except Exception as e:
            st.error(f"Erro ao gerar PDF: {str(e)}")
            st.error("Detalhes do erro:")
            st.code(traceback.format_exc())

    st.markdown("</div>", unsafe_allow_html=True)

with right:
    st.markdown('<div class="section-card"><h4>Volume Mensal</h4>', unsafe_allow_html=True)
    if df.empty:
        st.warning("Sem dados no período selecionado.")
    else:
        # prepare monthly chart
        if "_dt" in df.columns and "_amt" in df.columns:
            df["_month"] = df["_dt"].dt.to_period("M").dt.to_timestamp()
            monthly = df.groupby("_month")["_amt"].sum().reset_index().sort_values("_month")
            monthly["_month_str"] = monthly["_month"].dt.strftime("%m/%Y")
            fig = px.line(monthly, x="_month_str", y="_amt", markers=True, title="Volume Mensal")
            fig.update_layout(xaxis_title="Mês", yaxis_title="Volume (R$)")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Dados incompletos para gráfico mensal.")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="section-card"><h4>Top Agências (6 meses)</h4>', unsafe_allow_html=True)
    try:
        tmp = df.copy()
        if "_dt" in tmp.columns:
            max_date = tmp["_dt"].max()
            start6 = max_date - pd.DateOffset(months=6)
            tmp6 = tmp[tmp["_dt"] >= start6]
        else:
            tmp6 = tmp

        agencies = st.session_state.get("meta_info", {}).get("agencias_df")
        if agencies is not None and not agencies.empty and agency_id_col in tmp6.columns:
            ag_name = guess_col(agencies, ["nome","name","descricao","city","cidade"])
            ag_id = guess_col(agencies, ["id","agencia","branch","branch_id"])
            if ag_name and ag_id in agencies.columns:
                mapa = agencies[[ag_id, ag_name]].drop_duplicates()
                mapa[ag_id] = mapa[ag_id].astype(str)
                tmp6[agency_id_col] = tmp6[agency_id_col].astype(str)
                tmp6 = tmp6.merge(mapa, left_on=agency_id_col, right_on=ag_id, how="left")
                tmp6["ag_label"] = tmp6[ag_name].fillna(tmp6[agency_id_col].astype(str))
            else:
                tmp6["ag_label"] = tmp6[agency_id_col].astype(str)
        else:
            tmp6["ag_label"] = tmp6[agency_id_col].astype(str) if agency_id_col in tmp6.columns else "desconhecida"

        if not tmp6.empty:
            ranking6 = tmp6.groupby("ag_label")["_amt"].agg(["count","sum"]).reset_index().rename(columns={"count":"n_trans","sum":"volume"}).sort_values("n_trans", ascending=False)
            if not ranking6.empty:
                st.plotly_chart(px.bar(ranking6.head(10).sort_values("n_trans"), x="n_trans", y="ag_label", orientation="h",
                                       title="Top 10 - nº transações (6m)", labels={"n_trans": "Número de Transações", "ag_label": "Agência"}),
                               use_container_width=True)
                st.dataframe(ranking6.head(50).reset_index(drop=True))
            else:
                st.info("Nenhum dado disponível para o ranking de agências.")
        else:
            st.info("Nenhum dado disponível para os últimos 6 meses.")
    except Exception as e:
        st.error("Erro ao calcular top agências: " + str(e))
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="section-card"><h4>Sazonalidade - Dia da Semana</h4>', unsafe_allow_html=True)
    try:
        if "_dt" in df.columns and "_amt" in df.columns:
            df["_weekday_pt"] = df["_dt"].dt.dayofweek.map({0:"segunda-feira",1:"terça-feira",2:"quarta-feira",3:"quinta-feira",4:"sexta-feira",5:"sábado",6:"domingo"})
            weekly = df.groupby("_weekday_pt")["_amt"].agg(["count","sum"]).reset_index().rename(columns={"count":"n_trans","sum":"volume"})
            order = ["segunda-feira","terça-feira","quarta-feira","quinta-feira","sexta-feira","sábado","domingo"]
            weekly["_ord"] = weekly["_weekday_pt"].apply(lambda x: order.index(x) if x in order else 99)
            weekly = weekly.sort_values("_ord")
            st.plotly_chart(px.bar(weekly, x="_weekday_pt", y="volume", title="Volume por Dia da Semana"), use_container_width=True)
        else:
            st.info("Dados insuficientes para sazonalidade.")
    except Exception as e:
        st.error("Erro sazonalidade: " + str(e))
    st.markdown("</div>", unsafe_allow_html=True)

# ---------- Save compatibility keys in session_state ----------
# manter chaves individuais para compatibilidade com outras páginas
st.session_state["amount_col"] = "_amt"
st.session_state["date_col"] = "_dt"
st.session_state["agency_id_col"] = agency_id_col
st.session_state["client_id_col"] = client_id_col
st.session_state["agencias_df"] = agencias
st.session_state["clientes_df"] = clientes

# ---------- Footer ----------
st.markdown("---")
st.markdown("© BanVic — Dashboard de Analytics. Desenvolvido por Marcelo Pires.")
