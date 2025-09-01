from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
import io
import pandas as pd
from datetime import datetime

def build_pdf_bytes(df: pd.DataFrame, meta_info: dict, filters_info: dict) -> bytes:
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    # --- Cabeçalho ---
    c.setFont("Helvetica-Bold", 16)
    c.drawString(2*cm, height - 2*cm, "📊 Relatório BanVic Analytics")

    c.setFont("Helvetica", 10)
    c.drawString(2*cm, height - 2.7*cm, f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    c.drawString(2*cm, height - 3.2*cm, f"Agência: {filters_info.get('agency', 'Todas')}")
    c.drawString(2*cm, height - 3.7*cm, f"Cliente: {filters_info.get('client', 'Todos')}")
    c.drawString(2*cm, height - 4.2*cm, f"Período: {filters_info.get('start')} até {filters_info.get('end')}")

    # --- KPIs ---
    c.setFont("Helvetica-Bold", 12)
    c.drawString(2*cm, height - 5*cm, "📌 KPIs Gerais")
    total_transacoes = len(df)
    total_volume = df["valor"].sum() if not df.empty else 0
    ticket_medio = total_volume / total_transacoes if total_transacoes > 0 else 0

    c.setFont("Helvetica", 10)
    c.drawString(2*cm, height - 5.7*cm, f"Total Transações: {total_transacoes}")
    c.drawString(2*cm, height - 6.2*cm, f"Volume Total (R$): {total_volume:,.2f}")
    c.drawString(2*cm, height - 6.7*cm, f"Ticket Médio (R$): {ticket_medio:,.2f}")

    # --- Top 5 Clientes ---
    c.setFont("Helvetica-Bold", 12)
    c.drawString(2*cm, height - 7.7*cm, "👥 Top 5 Clientes por Volume")
    c.setFont("Helvetica", 10)

    top_clientes = df.groupby("conta_id")["valor"].sum().reset_index()
    top_clientes = top_clientes.sort_values("valor", ascending=False).head(5)
    y = height - 8.2*cm
    for idx, row in top_clientes.iterrows():
        cliente_nome = meta_info["agencias_df"].loc[meta_info["agencias_df"]["agencia_id"]==row["conta_id"], "nome_agencia"].values
        nome = cliente_nome[0] if len(cliente_nome) > 0 else f"Conta {row['conta_id']}"
        c.drawString(2.2*cm, y, f"{nome}: R$ {row['valor']:,.2f}")
        y -= 0.5*cm

    # Rodapé
    c.setFont("Helvetica-Oblique", 8)
    c.drawString(2*cm, 1.5*cm, "BanVic Analytics - Relatório Gerado Automaticamente")

    c.showPage()
    c.save()

    buffer.seek(0)
    return buffer.getvalue()
