from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from io import BytesIO
from datetime import datetime
import json

RISK_COLORS = {
    "CRITICAL": colors.HexColor("#f85149"),
    "ATTENTION": colors.HexColor("#e3b341"),
    "COMMON": colors.HexColor("#3fb950"),
}

def generate_pdf_report(scans: list) -> bytes:
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
        rightMargin=2*cm, leftMargin=2*cm,
        topMargin=2*cm, bottomMargin=2*cm)

    styles = getSampleStyleSheet()
    elements = []

    # Título
    title_style = ParagraphStyle('title',
        fontSize=20, alignment=TA_CENTER,
        textColor=colors.HexColor("#e6edf3"),
        spaceAfter=6)
    sub_style = ParagraphStyle('sub',
        fontSize=10, alignment=TA_CENTER,
        textColor=colors.HexColor("#8b949e"),
        spaceAfter=20)

    elements.append(Paragraph("Scanner-Pro", title_style))
    elements.append(Paragraph("Relatório de Segurança", title_style))
    elements.append(Paragraph(f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}", sub_style))
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#30363d")))
    elements.append(Spacer(1, 20))

    # Sumário executivo
    total_scans = len(scans)
    total_ports = sum(s["total_open_ports"] for s in scans)
    critical = attention = common = 0
    for scan in scans:
        results = scan["results"] if isinstance(scan["results"], list) else json.loads(scan["results"])
        for r in results:
            if r["risk"] == "CRITICAL": critical += 1
            elif r["risk"] == "ATTENTION": attention += 1
            else: common += 1

    section_style = ParagraphStyle('section',
        fontSize=12, textColor=colors.HexColor("#8b949e"),
        spaceBefore=16, spaceAfter=12)
    elements.append(Paragraph("SUMÁRIO EXECUTIVO", section_style))

    summary_data = [
        ["Total de Scans", "Portas Abertas", "Críticas", "Atenção", "Comuns"],
        [str(total_scans), str(total_ports), str(critical), str(attention), str(common)]
    ]
    summary_table = Table(summary_data, colWidths=[3.4*cm]*5)
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#161b22")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.HexColor("#8b949e")),
        ('BACKGROUND', (0,1), (-1,1), colors.HexColor("#0d1117")),
        ('TEXTCOLOR', (0,1), (-1,1), colors.HexColor("#e6edf3")),
        ('TEXTCOLOR', (2,1), (2,1), colors.HexColor("#f85149")),
        ('TEXTCOLOR', (3,1), (3,1), colors.HexColor("#e3b341")),
        ('TEXTCOLOR', (4,1), (4,1), colors.HexColor("#3fb950")),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('FONTSIZE', (0,1), (-1,1), 14),
        ('ROWBACKGROUNDS', (0,0), (-1,-1), [colors.HexColor("#161b22"), colors.HexColor("#0d1117")]),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#30363d")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#30363d")),
        ('TOPPADDING', (0,0), (-1,-1), 10),
        ('BOTTOMPADDING', (0,0), (-1,-1), 10),
    ]))
    elements.append(summary_table)
    elements.append(Spacer(1, 20))
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#30363d")))

    # Detalhamento por alvo
    elements.append(Paragraph("DETALHAMENTO POR ALVO", section_style))

    target_style = ParagraphStyle('target',
        fontSize=11, textColor=colors.HexColor("#e6edf3"),
        spaceBefore=12, spaceAfter=6)
    date_style = ParagraphStyle('date',
        fontSize=9, textColor=colors.HexColor("#8b949e"),
        spaceAfter=8)

    for scan in scans:
        results = scan["results"] if isinstance(scan["results"], list) else json.loads(scan["results"])
        created = scan["created_at"]
        if isinstance(created, str):
            try:
                created = datetime.fromisoformat(created).strftime('%d/%m/%Y %H:%M')
            except:
                pass

        elements.append(Paragraph(f"Alvo: {scan['target']}", target_style))
        elements.append(Paragraph(f"Data: {created} | Portas abertas: {scan['total_open_ports']}", date_style))

        if results:
            port_data = [["Porta", "Serviço", "Risco"]]
            for r in results:
                port_data.append([str(r["port"]), r["service"], r["risk"]])

            port_table = Table(port_data, colWidths=[4*cm, 8*cm, 5*cm])
            port_style_list = [
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#161b22")),
                ('TEXTCOLOR', (0,0), (-1,0), colors.HexColor("#8b949e")),
                ('FONTSIZE', (0,0), (-1,-1), 9),
                ('ALIGN', (0,0), (-1,-1), 'LEFT'),
                ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#30363d")),
                ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#21262d")),
                ('TOPPADDING', (0,0), (-1,-1), 6),
                ('BOTTOMPADDING', (0,0), (-1,-1), 6),
            ]
            for i, r in enumerate(results, start=1):
                risk_color = RISK_COLORS.get(r["risk"], colors.white)
                port_style_list.append(('TEXTCOLOR', (2,i), (2,i), risk_color))
                bg = colors.HexColor("#0d1117") if i % 2 == 0 else colors.HexColor("#161b22")
                port_style_list.append(('BACKGROUND', (0,i), (-1,i), bg))
                port_style_list.append(('TEXTCOLOR', (0,i), (1,i), colors.HexColor("#e6edf3")))

            port_table.setStyle(TableStyle(port_style_list))
            elements.append(port_table)
        else:
            elements.append(Paragraph("Nenhuma porta aberta encontrada.", date_style))

        elements.append(Spacer(1, 12))

    doc.build(elements)
    return buffer.getvalue()
