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
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

# CSS MODERNIZADO
CSS = """
<style>
/* page background */
[data-testid="stAppViewContainer"]{
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
}

/* card grid */
.kpi-grid{
  display: flex;
  gap: 16px;
  margin-bottom: 24px;
}
.kpi-card{
  flex: 1;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 16px;
  padding: 20px;
  box-shadow: 0 8px 25px rgba(0,0,0,0.1);
  border: none;
  transition: transform 0.3s ease;
}
.kpi-card:hover{
  transform: translateY(-5px);
}
.kpi-title{
  color: #ffffff;
  font-size: 14px;
  margin-bottom: 10px;
  font-weight: 300;
  opacity: 0.9;
}
.kpi-value{
  font-size: 20px;
  font-weight: 300;
  color: #ffffff;
  margin: 0;
}
.kpi-delta{
  color: #10b981;
  font-weight: 600;
  margin-top: 8px;
  font-size: 12px;
}
.section-card{
  background: white;
  padding: 20px;
  border-radius: 16px;
  box-shadow: 0 8px 25px rgba(0,0,0,0.08);
  border: none;
  margin-bottom: 24px;
}
.section-header {
  background: linear-gradient(90deg, #4b6cb7 0%, #182848 100%);
  color: white;
  padding: 15px;
  border-radius: 12px;
  margin: 20px 0;
}
.small-muted{ color:#6b7280; font-size:13px; }

/* Sidebar styling */
[data-testid="stSidebar"] {
  background: linear-gradient(180deg, #2c3e50 0%, #3498db 50%);
}
[data-testid="stSidebar"] .stSelectbox, 
[data-testid="stSidebar"] .stDateInput,
[data-testid="stSidebar"] .stButton {
  background: white;
  border-radius: 8px;
  padding: 8px;
}

[data-testid="stSidebar"] * {
color: #FFFFFF !important;   /* branco */
font-weight: 600;            /* negrito */
font-size: 16px;             /* tamanho do texto */
}


[data-testid="stSidebar"] h2, 
[data-testid="stSidebar"] h3,
[data-testid="stSidebar"] p {
  color: black !important;
}


/* Metric cards colors */
.metric-card-1 { background: linear-gradient(135deg, #FF6B6B 0%, #EE5A24 100%) !important; }
.metric-card-2 { background: linear-gradient(135deg, #36A2EB 0%, #4ECDC4 100%) !important; }
.metric-card-3 { background: linear-gradient(135deg, #FFD93D 0%, #FF9A3D 100%) !important; }
.metric-card-4 { background: linear-gradient(135deg, #6A11CB 0%, #2575FC 100%) !important; }
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

def extrair_cidade_uf(endereco):
    """
    Extrai cidade e UF de um endereço completo.
    """
    if pd.isna(endereco) or not isinstance(endereco, str):
        return None, None
    
    # Procurar padrão comum de cidade/UF no final do endereço
    partes = endereco.split(',')
    if len(partes) >= 2:
        ultima_parte = partes[-1].strip()
        # Verificar se contém padrão de UF (2 letras maiúsculas) no final
        if len(ultima_parte) >= 2 and ultima_parte[-2:].isupper() and ultima_parte[-2:].isalpha():
            uf = ultima_parte[-2:]
            cidade = partes[-2].strip() if len(partes) >= 2 else ultima_parte[:-2].strip()
            return cidade, uf
    
    # Tentar extrair de outras formas
    palavras = endereco.split()
    if len(palavras) >= 2:
        # Verificar se as duas últimas palavras formam um padrão de UF
        if len(palavras[-1]) == 2 and palavras[-1].isupper():
            uf = palavras[-1]
            cidade = palavras[-2] if len(palavras) >= 2 else None
            return cidade, uf
    
    return None, None

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
            monthly["_month_str"] = monthly["_month"].dt.strftime("%m/%Y")

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

    # RANKING TOP 10 AGÊNCIAS - VERSÃO CORRIGIDA
    story.append(Paragraph("RANKING TOP 10 AGÊNCIAS", heading_style))
    try:
        tmp = df.copy() if df is not None else pd.DataFrame()
        
        # Usar coluna de nome da agência se disponível
        if "agencia_nome" in tmp.columns:
            agency_label_col = "agencia_nome"
        else:
            # Fallback para ID da agência
            agency_id_col = st.session_state.get("meta_info", {}).get("agency_id_col")
            if agency_id_col and agency_id_col in tmp.columns:
                tmp["agencia_nome"] = tmp[agency_id_col].astype(str)
                agency_label_col = "agencia_nome"
            else:
                agency_label_col = None

        if agency_label_col and not tmp.empty:
            ranking = tmp.groupby(agency_label_col)["_amt"].agg(["count", "sum"]).reset_index().sort_values("count", ascending=False)
            ranking_data = [['Posição', 'Agência', 'Transações', 'Volume (R$)']]
            
            for i, (_, row) in enumerate(ranking.head(10).iterrows(), 1):
                ranking_data.append([
                    str(i),
                    str(row[agency_label_col])[:40],
                    f"{int(row['count']):,}".replace(",", "."),
                    f"R$ {float(row['sum']):,.2f}".replace(",", ".")
                ])

            if len(ranking_data) > 1:
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
            else:
                story.append(Paragraph("Sem dados para ranking.", normal_style))
        else:
            story.append(Paragraph("Informação de agência não disponível.", normal_style))
            
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

st.session_state["df_unfiltered"] = transacoes.copy()

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
    
    # Remover timezone de todas as datas para compatibilidade
    start = start.tz_localize(None) if hasattr(start, 'tz') else start
    end = end.tz_localize(None) if hasattr(end, 'tz') else end
    
if "_dt" in df.columns:
    df["_dt"] = pd.to_datetime(df["_dt"], errors="coerce")
    df["_dt"] = df["_dt"].dt.tz_localize(None)

    
    # Filtro seguro
    mask = (df["_dt"] >= start) & (df["_dt"] <= end)
    df = df.loc[mask]

# Agência filter
is_analysis_page = st.session_state.get('is_analysis_page', False)

# Agência filter - Só aplicar filtro se não for página de análise
if not st.session_state.get('is_analysis_page', False) and sel_ag != "Todas":
    if agency_id_col in df.columns:
        # try map name -> id if agency master table present
        if agencias is not None and ag_name_col and ag_master_id_col:
            # Primeiro filtramos as agências pelo nome selecionado
            ids = agencias.loc[agencias[ag_name_col].astype(str) == sel_ag, ag_master_id_col].unique()
            if len(ids):
                df = df[df[agency_id_col].isin(ids)]
            else:
                df = df[df[agency_id_col].astype(str) == sel_ag]
        else:
            df = df[df[agency_id_col].astype(str) == sel_ag]
    # try map name -> id if agency master table present
    if agencias is not None and ag_name_col and ag_master_id_col:
        # Primeiro filtramos as agências pelo nome selecionado
        ids = agencias.loc[agencias[ag_name_col].astype(str) == sel_ag, ag_master_id_col].unique()
        if len(ids):
            df = df[df[agency_id_col].isin(ids)]
        else:
            df = df[df[agency_id_col].astype(str) == sel_ag]
    else:
        df = df[df[agency_id_col].astype(str) == sel_ag]
    # try map name -> id if agency master table present
    if agencias is not None and ag_name_col and ag_master_id_col:
        # Primeiro filtramos as agências pelo nome selecionado
        ids = agencias.loc[agencias[ag_name_col].astype(str) == sel_ag, ag_master_id_col].unique()
        if len(ids):
            df = df[df[agency_id_col].isin(ids)]
        else:
            df = df[df[agency_id_col].astype(str) == sel_ag]
    else:
        df = df[df[agency_id_col].astype(str) == sel_ag]
    # try map name -> id if agency master table present
    if agencias is not None and ag_name_col and ag_master_id_col:
        # Primeiro filtramos as agências pelo nome selecionado
        ids = agencias.loc[agencias[ag_name_col].astype(str) == sel_ag, ag_master_id_col].unique()
        if len(ids):
            df = df[df[agency_id_col].isin(ids)]
        else:
            df = df[df[agency_id_col].astype(str) == sel_ag]
    else:
        df = df[df[agency_id_col].astype(str) == sel_ag]

# Client filter (optional) - CORREÇÃO PARA MOSTRAR NOMES
if sel_client != "Todos" and client_id_col in df.columns and clientes is not None:
    cli_name_col = guess_col(clientes, ["nome","name","razao"])
    cli_id_master = guess_col(clientes, ["id","cliente","customer"])
    if cli_name_col and cli_id_master:
        ids = clientes.loc[clientes[cli_name_col].astype(str) == sel_client, cli_id_master].unique()
        if len(ids):
            df = df[df[client_id_col].isin(ids)]
    else:
        df = df[df[client_id_col].astype(str) == sel_client]

    # try join by name if possible
    cli_name_col = guess_col(clientes, ["nome","name","razao"])
    cli_id_master = guess_col(clientes, ["id","cliente","customer"])
    if cli_name_col and cli_id_master and cli_name_col in clientes.columns:
        # Primeiro encontramos o ID do cliente selecionado pelo nome
        ids = clientes.loc[clientes[cli_name_col].astype(str) == sel_client, cli_id_master].unique()
        if len(ids):
            df = df[df[client_id_col].isin(ids)]
    else:
        df = df[df[client_id_col].astype(str) == sel_client]

# Processamento de informações de agências - VERSÃO OTIMIZADA
if agencias is not None and agency_id_col in df.columns:
    # Identificar colunas relevantes das agências
    ag_id_col = 'cod_agencia' if 'cod_agencia' in agencias.columns else None
    if not ag_id_col:
        ag_id_col = guess_col(agencias, ["cod_agencia", "id", "agencia", "branch", "branch_id"])
    
    ag_name_col = 'nome' if 'nome' in agencias.columns else guess_col(agencias, ["nome", "name", "descricao"])
    ag_cidade_col = 'cidade' if 'cidade' in agencias.columns else guess_col(agencias, ["cidade", "city"])
    ag_uf_col = 'uf' if 'uf' in agencias.columns else guess_col(agencias, ["uf", "estado", "state"])
    ag_tipo_col = 'tipo_agencia' if 'tipo_agencia' in agencias.columns else guess_col(agencias, ["tipo_agencia", "tipo", "type"])
    
    if ag_id_col:
        try:
            # Criar mapeamento com todas as informações das agências
            agencia_cols = [col for col in [ag_id_col, ag_name_col, ag_cidade_col, ag_uf_col, ag_tipo_col] 
                          if col is not None and col in agencias.columns]
            
            if agencia_cols:
                agencia_map = agencias[agencia_cols].drop_duplicates()
                
                # Converter para string para evitar problemas de tipo
                agencia_map[ag_id_col] = agencia_map[ag_id_col].astype(str)
                df[agency_id_col] = df[agency_id_col].astype(str)
                
                # Renomear colunas para evitar conflitos
                rename_dict = {ag_id_col: f"{ag_id_col}_agencia_map"}
                if ag_name_col and ag_name_col in agencia_map.columns: 
                    rename_dict[ag_name_col] = "agencia_nome"
                if ag_cidade_col and ag_cidade_col in agencia_map.columns: 
                    rename_dict[ag_cidade_col] = "agencia_cidade"
                if ag_uf_col and ag_uf_col in agencia_map.columns: 
                    rename_dict[ag_uf_col] = "agencia_uf"
                if ag_tipo_col and ag_tipo_col in agencia_map.columns: 
                    rename_dict[ag_tipo_col] = "agencia_tipo"
                
                agencia_map_renamed = agencia_map.rename(columns=rename_dict)
                
                # Fazer o merge
                df = df.merge(agencia_map_renamed, 
                             left_on=agency_id_col, 
                             right_on=f"{ag_id_col}_agencia_map", 
                             how="left")
                
                # Limpar coluna temporária
                if f"{ag_id_col}_agencia_map" in df.columns:
                    df = df.drop(columns=[f"{ag_id_col}_agencia_map"], errors="ignore")
        except Exception as e:
            st.error(f"Erro ao processar agências: {str(e)}")
            st.code(traceback.format_exc())
    else:
        st.warning("Não foi possível identificar a coluna de ID das agências.")

# ADICIONAR: Vincular informações completas de clientes
if clientes is not None and client_id_col in df.columns:
    try:
        # Verificar se já processamos clientes
        client_cols_expected = ['cliente_primeiro_nome', 'cliente_ultimo_nome', 'cliente_email', 
                               'cliente_tipo', 'cliente_cpf', 'cliente_data_nascimento', 
                           'cliente_endereco', 'cliente_cep', 'cliente_nome_completo']
        
        already_processed = any(col in df.columns for col in client_cols_expected)
        
        if not already_processed:
            logger.info("Processando informações de clientes...")
            
            # Identificar colunas relevantes dos clientes
            cli_id_col = guess_col(clientes, ["cod_cliente", "id", "cliente", "customer"])
            
            if cli_id_col:
                # Coletar todas as colunas disponíveis dos clientes
                all_client_cols = []
                possible_cols = [
                    "primeiro_nome", "ultimo_nome", "email", "tipo", "cpf", 
                    "data_nascimento", "endereco", "cep"
                ]
                
                col_mapping = {}
                for col_base in possible_cols:
                    col_name = guess_col(clientes, [col_base, f"cliente_{col_base}"])
                    if col_name and col_name in clientes.columns:
                        all_client_cols.append(col_name)
                        col_mapping[col_name] = f"cliente_{col_base}"
                
                # Garantir que temos a coluna ID
                if cli_id_col not in all_client_cols:
                    all_client_cols.insert(0, cli_id_col)
                
                # Criar mapeamento
                cliente_map = clientes[all_client_cols].drop_duplicates()
                cliente_map = cliente_map.loc[:, ~cliente_map.columns.duplicated()]
                
                # Converter para string para evitar problemas de tipo
                cliente_map[cli_id_col] = cliente_map[cli_id_col].astype(str)
                df[client_id_col] = df[client_id_col].astype(str)
                
                # Renomear colunas ANTES do merge para evitar conflitos
                rename_dict = {cli_id_col: "cliente_id_temp"}
                for old_name, new_name in col_mapping.items():
                    rename_dict[old_name] = new_name
                
                cliente_map_renamed = cliente_map.rename(columns=rename_dict)
                
                # Fazer o merge UMA ÚNICA VEZ com sufixos explícitos
                df = df.merge(cliente_map_renamed, 
                             left_on=client_id_col, 
                             right_on="cliente_id_temp", 
                             how="left",
                             suffixes=('', '_cliente'))
                
                # Criar nome completo do cliente
                if "cliente_primeiro_nome" in df.columns and "cliente_ultimo_nome" in df.columns:
                    df["cliente_nome_completo"] = df["cliente_primeiro_nome"] + " " + df["cliente_ultimo_nome"]
                elif "cliente_primeiro_nome" in df.columns:
                    df["cliente_nome_completo"] = df["cliente_primeiro_nome"]
                
                # Extrair cidade e UF do endereço
                if "cliente_endereco" in df.columns:
                    df[["cliente_cidade", "cliente_uf"]] = df["cliente_endereco"].apply(
                        lambda x: pd.Series(extrair_cidade_uf(x)) if pd.notna(x) else pd.Series([None, None])
                    )
                
                # Limpar coluna temporária
                df.drop(columns=["cliente_id_temp"], inplace=True, errors="ignore")
                
                logger.info(f" Colunas de cliente carregadas: {[col for col in df.columns if col.startswith('cliente_')]}")
            else:
                logger.warning(" Não foi possível identificar coluna de ID do cliente")
        else:
            logger.info(" Informações de clientes já processadas anteriormente")
            
    except Exception as e:
        logger.error(f" Erro ao processar clientes: {e}")
        logger.error(traceback.format_exc())

# Remover colunas com sufixo _x ou _y que podem ter sido criadas por merges duplicados
cols_to_drop = [col for col in df.columns if col.endswith(('_x', '_y'))]
if cols_to_drop:
    logger.warning(f"  Removendo colunas duplicadas: {cols_to_drop}")
    df.drop(columns=cols_to_drop, inplace=True)

# Salvar também uma versão não filtrada para as páginas de análise
st.session_state["df_unfiltered"] = df.copy()


st.session_state["df_filtered"] = df
st.session_state["meta_info"] = {
    "date_col": "_dt",
    "amount_col": "_amt",
    "agency_id_col": agency_id_col,
    "client_id_col": client_id_col,
    "agencias_df": agencias,
    "clientes_df": clientes,
    "agencia_nome_col": "agencia_nome",
    "cliente_nome_col": "cliente_nome_completo" if "cliente_nome_completo" in df.columns else "cliente_nome"
}

# ---------- Header / KPIs (cards) ----------
st.title("📊 BanVic Analytics Dashboard")
st.markdown("Painel interativo com KPIs, ranking de agências, análise de clientes e tendências. Use os filtros na lateral.")

# compute KPIs
total_trans = int(len(df))
total_vol = float(df["_amt"].sum(skipna=True)) if "_amt" in df.columns else 0.0
ticket = total_vol / total_trans if total_trans > 0 else 0.0
aprov_rate = df["_approved"].mean() * 100 if "_approved" in df.columns else np.nan

def kpi_card(title, value, card_class="", fmt=None):
    val = f"{value}" if fmt is None else fmt.format(value)
    html = f"""
    <div class="kpi-card {card_class}">
      <div class="kpi-title">{title}</div>
      <div class="kpi-value">{val}</div>
    </div>
    """
    return html

cols = st.columns([1,1,1,1])
with cols[0]:
    st.markdown(kpi_card("💳 Total de Transações", f"{total_trans:,}".replace(",", "."), "metric-card-1"), unsafe_allow_html=True)
with cols[1]:
    st.markdown(kpi_card("💰 Volume Total", f"R$ {total_vol:,.2f}".replace(",", "."), "metric-card-2"), unsafe_allow_html=True)
with cols[2]:
    st.markdown(kpi_card("🎫 Ticket Médio", f"R$ {ticket:,.2f}".replace(",", "."), "metric-card-3"), unsafe_allow_html=True)
with cols[3]:
    aprov_display = f"{aprov_rate:.1f}%" if not np.isnan(aprov_rate) else "N/A"
    st.markdown(kpi_card("✅ Taxa de Aprovação", aprov_display, "metric-card-4"), unsafe_allow_html=True)

st.markdown("---")

# ---------- Layout: left filters + right content ----------
left, right = st.columns([1.1, 2.8])

with left:
    st.markdown('<div class="section-card"> <h4>📋 Resumo Rápido</h4>', unsafe_allow_html=True)
    if date_range and len(date_range) == 2:
        st.write(f"**📅 Período:** {format_date_pt_br(start)} → {format_date_pt_br(end)}")
    st.write(f"**🏢 Agência:** {sel_ag}")
    st.write(f"**👥 Clientes (filtro):** {sel_client}")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="section-card"> <h4>📤 Exportar</h4>', unsafe_allow_html=True)
    st.write("Exportar relatório PDF com os dados e gráficos do período e filtros aplicados.")

    if st.button("📊 Gerar Relatório PDF", use_container_width=True):
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
                mime="application/pdf",
                use_container_width=True
            )

        except Exception as e:
            st.error(f"Erro ao gerar PDF: {str(e)}")
            st.code(traceback.format_exc())

    st.markdown("</div>", unsafe_allow_html=True)

with right:
    # GRÁFICO DE VOLUME MENSAL MELHORADO
    st.markdown('<div class="section-card"><h4>📈 Volume Mensal</h4>', unsafe_allow_html=True)
    if df.empty:
        st.warning("Sem dados no período selecionado.")
    else:
        if "_dt" in df.columns and "_amt" in df.columns:
            df["_month"] = df["_dt"].dt.to_period("M").dt.to_timestamp()
            monthly = df.groupby("_month")["_amt"].sum().reset_index().sort_values("_month")
            monthly["_month_str"] = monthly["_month"].dt.strftime("%b/%Y")
            
            fig = px.area(monthly, x="_month_str", y="_amt", 
                         title="Evolução do Volume Mensal",
                         labels={"_month_str": "Mês", "_amt": "Volume (R$)"},
                         color_discrete_sequence=['#4ECDC4'])
            
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(size=12),
                height=400,
                hovermode='x unified'
            )
            fig.update_traces(mode='lines+markers', marker=dict(size=8))
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Dados incompletos para gráfico mensal.")
    st.markdown("</div>", unsafe_allow_html=True)

    # TOP 10 AGÊNCIAS MELHORADO
    st.markdown('<div class="section-card"><h4>🏆 Top 10 Agências</h4>', unsafe_allow_html=True)
    
    try:
        tmp = st.session_state["df_unfiltered"].copy()
        
        if "agencia_nome" not in tmp.columns:
            agency_id_col = st.session_state.get("meta_info", {}).get("agency_id_col")
            if agency_id_col and agency_id_col in tmp.columns:
                tmp["agencia_nome"] = "Agência " + tmp[agency_id_col].astype(str)

        if "agencia_nome" in tmp.columns:
            tmp = tmp[tmp["agencia_nome"].notna() & (tmp["agencia_nome"].str.strip() != "")]
            
            ranking = tmp.groupby("agencia_nome").agg(
                num_transacoes=("_amt", "count"),
                volume_total=("_amt", "sum"),
                ticket_medio=("_amt", "mean")
            ).reset_index().sort_values("volume_total", ascending=False)

            top10 = ranking.head(10)

            # Gráfico de barras horizontais
            fig = px.bar(
                top10.sort_values("volume_total", ascending=True),
                x="volume_total",
                y="agencia_nome",
                orientation='h',
                title="Top 10 Agências por Volume Financeiro",
                labels={"volume_total": "Volume Total (R$)", "agencia_nome": "Agência"},
                color="num_transacoes",
                color_continuous_scale='Viridis',
                hover_data=["num_transacoes", "ticket_medio"]
            )
            
            fig.update_layout(
                height=500,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                yaxis={'categoryorder':'total ascending'}
            )
            
            st.plotly_chart(fig, use_container_width=True)

            # Tabela interativa
            st.subheader("📊 Detalhes do Ranking")
            
            top10_display = top10.copy()
            top10_display["volume_total"] = top10_display["volume_total"].apply(lambda x: f"R$ {x:,.2f}")
            top10_display["ticket_medio"] = top10_display["ticket_medio"].apply(lambda x: f"R$ {x:,.2f}")
            
            st.dataframe(
                top10_display,
                use_container_width=True,
                column_config={
                    "agencia_nome": "Agência",
                    "num_transacoes": "Transações",
                    "volume_total": "Volume Total",
                    "ticket_medio": "Ticket Médio"
                },
                hide_index=True
            )
        else:
            st.info("Informações de agência não disponíveis para ranking.")

    except Exception as e:
        st.error(f"Erro ao calcular ranking: {str(e)}")

    st.markdown("</div>", unsafe_allow_html=True)

    # SAZONALIDADE MELHORADA
    st.markdown('<div class="section-card"><h4>📅 Sazonalidade - Dia da Semana</h4>', unsafe_allow_html=True)
    
    try:
        if "_dt" in df.columns and "_amt" in df.columns:
            dias_semana = {
                0: "Segunda", 1: "Terça", 2: "Quarta", 
                3: "Quinta", 4: "Sexta", 5: "Sábado", 6: "Domingo"
            }
            
            df["_weekday"] = df["_dt"].dt.dayofweek.map(dias_semana)
            weekly = df.groupby("_weekday")["_amt"].agg(["count", "sum", "mean"]).reset_index()
            weekly.columns = ["Dia da Semana", "Transações", "Volume", "Ticket Médio"]
            
            # Ordenar pelos dias da semana
            ordem_dias = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"]
            weekly["Dia da Semana"] = pd.Categorical(weekly["Dia da Semana"], categories=ordem_dias, ordered=True)
            weekly = weekly.sort_values("Dia da Semana")
            
            fig = px.bar(weekly, x="Dia da Semana", y="Volume", 
                        title="Volume por Dia da Semana",
                        labels={"Volume": "Volume (R$)", "Dia da Semana": "Dia da Semana"},
                        color="Transações",
                        color_continuous_scale='Blues')
            
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Métricas adicionais
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("📈 Maior Volume", f"R$ {weekly['Volume'].max():,.2f}")
            with col2:
                st.metric("📉 Menor Volume", f"R$ {weekly['Volume'].min():,.2f}")
            with col3:
                st.metric("⚖️ Variação", f"{(weekly['Volume'].max()/weekly['Volume'].min()-1)*100:.1f}%")
                
        else:
            st.info("Dados insuficientes para análise de sazonalidade.")
            
    except Exception as e:
        st.error(f"Erro na análise de sazonalidade: {str(e)}")
    
    st.markdown("</div>", unsafe_allow_html=True)

    # NOVA SEÇÃO: DISTRIBUIÇÃO DE TRANSACOES
    st.markdown('<div class="section-card"><h4>📊 Distribuição de Transações</h4>', unsafe_allow_html=True)
    
    try:
        if "_amt" in df.columns:
            # Histograma de valores
            fig = px.histogram(df, x="_amt", nbins=20, 
                             title="Distribuição dos Valores das Transações",
                             labels={"_amt": "Valor da Transação (R$)"},
                             color_discrete_sequence=['#FF6B6B'])
            
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                height=400,
                showlegend=False
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Estatísticas
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Mínimo", f"R$ {df['_amt'].min():.2f}")
            with col2:
                st.metric("Máximo", f"R$ {df['_amt'].max():.2f}")
            with col3:
                st.metric("Mediana", f"R$ {df['_amt'].median():.2f}")
            with col4:
                st.metric("Desvio Padrão", f"R$ {df['_amt'].std():.2f}")
                
        else:
            st.info("Dados insuficientes para análise de distribuição.")
            
    except Exception as e:
        st.error(f"Erro na análise de distribuição: {str(e)}")
    
    st.markdown("</div>", unsafe_allow_html=True)


    

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