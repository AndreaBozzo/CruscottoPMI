import os
from io import BytesIO
from datetime import datetime

import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak, Image as PlatypusImage,
    Table, TableStyle, Frame, PageTemplate
)

def genera_super_pdf(
    azienda,
    anno,
    df_kpi,
    benchmark,
    df_yoy=None,
    df_voci=None,
    nota=None,
    osservazioni_kpi=None,
    radar_img=None,
    gauge_img=None,
    heatmap_img=None,
    trend_img=None,
    logo_path="logo.png"
):
    buffer = BytesIO()
    styles = getSampleStyleSheet()

    # Stili custom
    title_style = ParagraphStyle("CustomTitle", parent=styles["Title"],
                                 fontSize=22, leading=26, alignment=1,
                                 textColor=colors.HexColor("#2C3E50"), spaceAfter=20)
    subtitle_style = ParagraphStyle("CustomSubtitle", parent=styles["Heading2"],
                                    fontSize=14, alignment=1,
                                    textColor=colors.HexColor("#34495E"), spaceAfter=10)
    heading_style = ParagraphStyle("CustomHeading2", parent=styles["Heading2"],
                                   fontSize=12, spaceBefore=8, spaceAfter=8,
                                   textColor=colors.HexColor("#2980B9"))
    body_style = ParagraphStyle("CustomBody", parent=styles["BodyText"],
                                fontSize=10, leading=12, alignment=4,
                                spaceAfter=8)

    def _footer(canvas, doc):
        canvas.saveState()
        canvas.setFont("Helvetica", 8)
        canvas.drawCentredString(A4[0]/2, 1*cm, f"Pagina {doc.page}")
        footer_txt = f"Generato il {datetime.now().strftime('%d/%m/%Y %H:%M')}"
        canvas.drawRightString(A4[0]-1*cm, 1*cm, footer_txt)
        canvas.restoreState()

    doc = SimpleDocTemplate(buffer, pagesize=A4,
                            rightMargin=2*cm, leftMargin=2*cm,
                            topMargin=2*cm, bottomMargin=2*cm)
    doc.addPageTemplates([PageTemplate(id='All',
        frames=[Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height)],
        onPage=_footer)])

    elements = []

    # Copertina
    logo_file = logo_path
    if not os.path.exists(logo_file):
        alt = os.path.join("assets", os.path.basename(logo_path))
        if os.path.exists(alt): logo_file = alt
    if os.path.exists(logo_file):
        img = PlatypusImage(logo_file, width=8*cm, height=8*cm)
        elements.extend([img, Spacer(1,20)])
    elements.extend([
        Paragraph("Report Analitico Azienda", title_style),
        Paragraph(f"{azienda} – {anno}", subtitle_style),
        Paragraph(f"Data generazione: {datetime.now().strftime('%d/%m/%Y, %H:%M')}", body_style),
        PageBreak()
    ])

    # Nota introduttiva
    if nota:
        elements.extend([
            Paragraph("📝 Nota introduttiva", heading_style),
            Paragraph(nota, body_style),
            PageBreak()
        ])

    # Osservazioni KPI
    if osservazioni_kpi:
        elements.append(Paragraph("💬 Osservazioni KPI", heading_style))
        for t in osservazioni_kpi:
            elements.append(Paragraph(f"• {t}", body_style))
        elements.append(PageBreak())

    # Grafici Radar, Heatmap, Trend
    def _append_section(titolo, img_list):
        if img_list:
            elements.append(Paragraph(titolo, heading_style))
            for name, data in img_list:
                bio = BytesIO(data)
                img = PlatypusImage(bio, width=15*cm, height=8*cm)
                elements.extend([img, Spacer(1,12)])
            elements.append(PageBreak())

    _append_section("🎯 Radar KPI", radar_img or [])
    _append_section("🌡️ Heatmap Voci di Bilancio", heatmap_img or [])
    _append_section("📈 Trend KPI", trend_img or [])

    # === Gauge KPI strutturali (uno per pagina)
    if gauge_img:
        for name, data in gauge_img:
            elements.append(Paragraph(f"⏱️ Gauge – {name.replace('gauge_','').replace('.png','')}", heading_style))
            bio = BytesIO(data)
            # uso dimensioni maggiori e proporzioni corrette
            img = PlatypusImage(bio, width=14*cm, height=5*cm)
            elements.extend([Spacer(1,12), img, PageBreak()])

    # KPI Sintetici tabellari
    if df_kpi is not None and not df_kpi.empty:
        kpi_sint = ["ROE","ROI","EBITDA Margin","Indice Sintetico"]
        df_s = df_kpi[df_kpi["KPI"].isin(kpi_sint)]
        if not df_s.empty:
            tbl = [["KPI","Valore","Benchmark"]]
            for _,r in df_s.iterrows():
                ref = benchmark.get(r["KPI"])
                tbl.append([r["KPI"],f"{r['Valore']:.2f}", f"{ref:.2f}" if ref else "–"])
            table = Table(tbl, colWidths=[5*cm,3*cm,3*cm], hAlign="LEFT")
            table.setStyle(TableStyle([
                ("BACKGROUND",(0,0),(-1,0),colors.HexColor("#DDDDDD")),
                ("GRID",(0,0),(-1,-1),0.5,colors.HexColor("#999999")),
                ("ROWBACKGROUNDS",(1,1),(-1,-1),[colors.white,colors.HexColor("#F5F5F5")]),
                ("ALIGN",(1,0),(-1,-1),"CENTER"),
                ("VALIGN",(0,0),(-1,-1),"MIDDLE")
            ]))
            elements.extend([Paragraph("📊 KPI Sintetici", heading_style), table, PageBreak()])

    # Tabelle Voci di Bilancio e YoY
    def _append_table(df, titolo):
        if df is not None and not df.empty:
            data = [list(df.columns)] + df.values.tolist()
            table = Table(data, hAlign="LEFT")
            table.setStyle(TableStyle([
                ("BACKGROUND",(0,0),(-1,0),colors.HexColor("#ECECEC")),
                ("GRID",(0,0),(-1,-1),0.3,colors.HexColor("#CCCCCC")),
                ("FONTSIZE",(0,0),(-1,-1),8),
                ("VALIGN",(0,0),(-1,-1),"MIDDLE"),
                ("ALIGN",(1,1),(-1,-1),"RIGHT"),
            ]))
            elements.extend([Paragraph(titolo, heading_style), table, PageBreak()])

    _append_table(df_voci, "📁 Voci di Bilancio")
    _append_table(df_yoy, "📉 Analisi YoY")

    # Build
    doc.build(elements)
    pdf = buffer.getvalue()
    buffer.close()
    return pdf
