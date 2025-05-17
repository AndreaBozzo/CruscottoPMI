
from reportlab.platypus import SimpleDocTemplate, Paragraph, PageBreak, Spacer, Image as PlatypusImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_RIGHT, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from io import BytesIO
from datetime import datetime

def genera_super_pdf(df_kpi, df_voci, df_yoy, note,
                     grafico_kpi_buf=None, titolo_grafico=None,
                     grafico_extra_buf=None, titolo_extra=None):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=2*cm, leftMargin=2*cm, topMargin=2.5*cm, bottomMargin=2*cm)
    elements = []
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="Right", alignment=TA_RIGHT))
    styles.add(ParagraphStyle(name="Left", alignment=TA_LEFT))
    styles.add(ParagraphStyle(name="HeaderBlock", fontSize=14, leading=18, alignment=TA_LEFT, spaceAfter=12))
    styles.add(ParagraphStyle(name="Mono", fontName="Helvetica", fontSize=10, leading=14, alignment=TA_LEFT))

    elements.append(Paragraph("🧭 <b>CruscottoPMI</b><br/>Report Finanziario Aziendale", styles["HeaderBlock"]))
    now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    elements.append(Paragraph(f"<i>Generato il {now}</i>", styles['Normal']))
    elements.append(Spacer(1, 0.5 * cm))

    if note:
        elements.append(Paragraph("<b>📝 Note Personali</b>", styles['Heading2']))
        for line in note.splitlines():
            elements.append(Paragraph(line, styles['Normal']))
        elements.append(Spacer(1, 0.3 * cm))

    def add_image_section(img_buf, title):
        elements.append(PageBreak())
        elements.append(Paragraph(f"{title}", styles['Heading2']))
        img = PlatypusImage(img_buf, width=16*cm)
        img.hAlign = "CENTER"
        elements.append(Spacer(1, 0.2 * cm))
        elements.append(img)
        elements.append(Spacer(1, 0.5 * cm))

    if grafico_kpi_buf:
        grafico_title = titolo_grafico if titolo_grafico else "📊 Grafico KPI"
        add_image_section(grafico_kpi_buf, grafico_title)

    if grafico_extra_buf:
        extra_title = titolo_extra if titolo_extra else "📊 Grafico Extra"
        add_image_section(grafico_extra_buf, extra_title)

    def add_vertical_block(title, df):
        if df.empty:
            return

        # Filtro KPI: solo sintetici se siamo nella sezione KPI
        if title == "📊 KPI":
            keep_cols = ["ROE", "EBITDA Margin", "ROI", "Current Ratio", "Variazione %", "Azienda", "Anno"]
            df = df[[col for col in keep_cols if col in df.columns]]

        elements.append(PageBreak())
        elements.append(Paragraph(f"<b>{title}</b>", styles['Heading2']))
        elements.append(Spacer(1, 0.2 * cm))
        for idx, row in df.iterrows():
            row_label = ""
            if "Azienda" in df.columns and "Anno" in df.columns:
                row_label = f" ({row['Azienda']} - {row['Anno']})"
            for col in df.columns:
                if col in ["Azienda", "Anno"]:
                    continue
                val = row[col]
                if isinstance(val, (int, float)):
                    val_str = f"{val:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                    if col in ["ROE", "EBITDA Margin", "ROI", "Current Ratio"]:
                        try:
                            if float(val) < 0 or (col == "Current Ratio" and float(val) < 1):
                                val_str = f"<font color='red'>{val_str}</font>"
                        except:
                            pass
                    if col == "Variazione %":
                        try:
                            if float(val) > 0:
                                val_str = f"<font color='green'>{val_str}</font>"
                            elif float(val) < 0:
                                val_str = f"<font color='red'>{val_str}</font>"
                        except:
                            pass
                else:
                    val_str = str(val)
                full_label = f"<b>{col}{row_label}:</b> {val_str}"
                elements.append(Paragraph(full_label, styles["Mono"]))
                elements.append(Spacer(1, 0.1 * cm))

    add_vertical_block("📊 KPI", df_kpi)
    add_vertical_block("📑 Voci di Bilancio", df_voci)
    add_vertical_block("🔁 Analisi YoY", df_yoy)

    doc.build(elements)
    buffer.seek(0)
    return buffer

from fpdf import FPDF

def genera_pdf_yoy(buffer, df_yoy, azienda, anno1, anno2, nota=""):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, f"Report YoY – {azienda}", ln=True)

    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 10, f"Confronto tra {anno1} e {anno2}", ln=True)

    pdf.ln(5)
    if nota:
        pdf.set_font("Arial", "I", 11)
        pdf.multi_cell(0, 8, f"Nota: {nota}")
        pdf.ln(2)

    pdf.set_font("Arial", "B", 12)
    pdf.cell(100, 8, "Voce", border=1)
    pdf.cell(40, 8, "Variazione (%)", border=1, ln=True)

    pdf.set_font("Arial", "", 11)
    for _, row in df_yoy.iterrows():
        voce = str(row["Voce"])
        var = f"{row['Variazione (%)']:+.2f}%"
        pdf.cell(100, 8, voce[:40], border=1)
        pdf.cell(40, 8, var, border=1, ln=True)

    pdf.output(buffer)
