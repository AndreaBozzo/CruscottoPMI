import os
from io import BytesIO
from datetime import datetime

import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer,
                                PageBreak, Image as PlatypusImage,
                                Table, TableStyle, Frame, PageTemplate)

def genera_super_pdf(
    azienda,
    anno,
    df_kpi=None,
    df_voci=None,
    df_yoy=None,
    nota=None,
    radar_img=None,
    gauge_img=None,
    heatmap_img=None,
    trend_img=None,
    logo_path="logo.png"
):
    buffer = BytesIO()
    styles = getSampleStyleSheet()

    # callback per numeri di pagina e footer su tutte le pagine
    def _footer(canvas, doc):
        canvas.saveState()
        # numero di pagina
        page_num = f"Pagina {doc.page}"
        canvas.setFont("Helvetica", 8)
        canvas.drawCentredString(A4[0] / 2, 1 * cm, page_num)
        # data di generazione
        now = datetime.now().strftime("%d/%m/%Y %H:%M")
        footer_text = f"Generato il {now}"
        canvas.drawRightString(A4[0] - 1 * cm, 1 * cm, footer_text)
        canvas.restoreState()

    # costruzione document
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                            rightMargin=2*cm, leftMargin=2*cm,
                            topMargin=2*cm, bottomMargin=2*cm)

    doc.addPageTemplates([PageTemplate(id='All', frames=[Frame(doc.leftMargin, doc.bottomMargin,
                                                                doc.width, doc.height)],
                                       onPage=_footer)])
    elements = []

    logo_file = logo_path
    if not os.path.exists(logo_file):
        alt = os.path.join("assets", os.path.basename(logo_path))
        if os.path.exists(alt):
            logo_file = alt

    # Se il file esiste, lo inserisci
    if os.path.exists(logo_file):
        img = PlatypusImage(logo_file, width=6*cm, height=6*cm)
        elements.append(img)
        elements.append(Spacer(1, 12))

    # Titolo e sottotitolo
    title = Paragraph(f"<b>Report Analitico Azienda</b>", styles["Title"])
    elements.append(title)
    subtitle = Paragraph(f"<b>{azienda} – {anno}</b>", styles["Heading2"])
    elements.append(subtitle)
    gen_date = datetime.now().strftime("%d %B %Y, %H:%M")
    elements.append(Paragraph(f"Data generazione: {gen_date}", styles["Normal"]))
    elements.append(PageBreak())

    # === Nota introduttiva ===
    if nota:
        elements.append(Paragraph("📝 Nota introduttiva", styles["Heading2"]))
        elements.append(Paragraph(nota, styles["BodyText"]))
        elements.append(Spacer(1, 12))

    # === Sezioni con grafici ===
    def _append_img(section_title, img_list):
        if img_list:
            elements.append(Paragraph(section_title, styles["Heading2"]))
            for name, data in img_list:
                bio = BytesIO(data)
                img = PlatypusImage(bio, width=16*cm, height=9*cm)
                elements.append(img)
                elements.append(Spacer(1, 12))

    _append_img("🎯 Radar KPI", radar_img or [])
    _append_img("⏱️ Indicatori Strutturali", gauge_img or [])
    _append_img("🌡️ Heatmap Voci di Bilancio", heatmap_img or [])
    _append_img("📈 Trend KPI", trend_img or [])

    # === Tabelle KPI, Voci, YoY ===
    def _append_table(df, title, max_rows=40, fontsize=8):
        if df is not None and not df.empty:
            elements.append(Paragraph(title, styles["Heading2"]))
            data = [list(df.columns)] + df.values.tolist()
            # limitiamo righe
            data = data[: max_rows + 1]
            table = Table(data, hAlign="LEFT")
            table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#DDDDDD")),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#999999")),
                ("FONTSIZE", (0, 0), (-1, -1), fontsize),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ]))
            elements.append(table)
            elements.append(PageBreak())

    _append_table(df_kpi, "📊 KPI", max_rows=20, fontsize=8)
    _append_table(df_voci, "📁 Voci di Bilancio", max_rows=20, fontsize=7)
    _append_table(df_yoy, "📉 Analisi YoY", max_rows=20, fontsize=7)

    # === Build finale ===
    doc.build(elements)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes
