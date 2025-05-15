import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.utils import ImageReader
from zipfile import ZipFile
import os
from datetime import datetime

@st.cache_data(show_spinner=False)
def load_excel(file):
    ce = pd.read_excel(file, sheet_name="Conto Economico")
    att = pd.read_excel(file, sheet_name="Attivo")
    pas = pd.read_excel(file, sheet_name="Passivo")
    return ce, att, pas

@st.cache_data(show_spinner=False)
def load_benchmark(file, default_benchmark):
    if file is None:
        return default_benchmark.copy()
    df_bm = pd.read_csv(file)
    return {row["KPI"]: row["Valore"] for _, row in df_bm.iterrows()}

def calcola_kpi(ce, att, pas, benchmark):
    def get_val(df, voce_col, voce_name):
        subset = df[df[voce_col] == voce_name]
        return subset["Importo (€)"].values[0] if not subset.empty else 0

    try:
        ricavi       = get_val(ce, "Voce", "Ricavi")
        utile_netto  = get_val(ce, "Voce", "Utile netto")
        ebit         = get_val(ce, "Voce", "EBIT")
        spese_oper   = get_val(ce, "Voce", "Spese operative")
        ammortamenti = get_val(ce, "Voce", "Ammortamenti")
        oneri_fin    = get_val(ce, "Voce", "Oneri finanziari")
        mol          = ricavi - spese_oper

        liquidita    = get_val(att, "Attività", "Disponibilità liquide")
        debiti_brevi = get_val(pas, "Passività e Patrimonio Netto", "Debiti a breve")
        patrimonio   = get_val(pas, "Passività e Patrimonio Netto", "Patrimonio netto")
        totale_att   = att["Importo (€)"].sum()

        if any(v == 0 for v in [ricavi, patrimonio, totale_att, debiti_brevi]):
            return {"Errore": "Uno o più valori chiave sono zero o mancanti."}

        ebitda = ebit + spese_oper
        eda_m  = round(ebitda / ricavi * 100, 2)
        roe    = round(utile_netto / patrimonio * 100, 2)
        roi    = round(ebit / totale_att * 100, 2)
        curr_r = round(liquidita / debiti_brevi, 2)

        indice = round(((eda_m / benchmark.get("EBITDA Margin", 1)) +
                        (roe / benchmark.get("ROE", 1)) +
                        (roi / benchmark.get("ROI", 1)) +
                        (curr_r / benchmark.get("Current Ratio", 1))) / 4 * 10, 1)

        valutazione = "Ottima solidità ✅"
        if any([eda_m < 10, roe < 5, roi < 5, curr_r < 1]):
            valutazione = "⚠️ Alcuni indici critici"
        if all([eda_m < 10, roe < 5, roi < 5, curr_r < 1]):
            valutazione = "❌ Situazione critica"

        kpi_row = {
            "EBITDA Margin": eda_m, "ROE": roe, "ROI": roi, "Current Ratio": curr_r,
            "Indice Sintetico": indice, "Valutazione": valutazione,
            "Ricavi": ricavi, "EBIT": ebit, "Spese Operative": spese_oper,
            "Ammortamenti": ammortamenti, "Oneri Finanziari": oneri_fin,
            "MOL": mol, "Totale Attivo": totale_att, "Patrimonio Netto": patrimonio,
            "Liquidità": liquidita, "Debiti a Breve": debiti_brevi
        }

        return kpi_row

    except Exception as e:
        return {"Errore": str(e)}

def estrai_aziende_anni_disponibili(bilanci_dict):
    aziende = sorted(set(k[0] for k in bilanci_dict.keys()))
    anni = sorted(set(k[1] for k in bilanci_dict.keys()))
    return aziende, anni

def filtra_bilanci(bilanci_dict, azienda, anni):
    return [df for (az, anno), df in bilanci_dict.items() if az == azienda and anno in anni]

def genera_grafico_kpi(df):
    if "Azienda" in df.columns and "Indice Sintetico" in df.columns:
        fig, ax = plt.subplots(figsize=(6, 4), dpi=150)
        bars = ax.bar(df["Azienda"], df["Indice Sintetico"], color="#1f77b4")
        ax.set_title("Indice Sintetico per Azienda")
        ax.set_ylabel("Valore")
        ax.set_xticklabels(df["Azienda"], rotation=45, ha="right")
        for bar in bars:
            yval = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2, yval + 0.5, f"{yval:.1f}", ha='center', fontsize=8)
        plt.tight_layout()
        buf = BytesIO()
        plt.savefig(buf, format='png', dpi=150)
        buf.seek(0)
        return buf
    return None

def genera_grafico_voci(df):
    if "Voce" in df.columns and "Importo (€)" in df.columns:
        fig, ax = plt.subplots(figsize=(6, 4), dpi=150)
        data = df.groupby("Voce")["Importo (€)"].sum().sort_values()
        bars = ax.barh(data.index, data.values, color="#ff7f0e")
        ax.set_title("Distribuzione delle Voci di Bilancio")
        for bar in bars:
            xval = bar.get_width()
            ax.text(xval + max(data.values)*0.01, bar.get_y() + bar.get_height()/2, f"{xval:,.0f}", va='center', fontsize=8)
        plt.tight_layout()
        buf = BytesIO()
        plt.savefig(buf, format='png', dpi=150)
        buf.seek(0)
        return buf
    return None

def genera_pdf(df, note, grafico_kpi_buf=None, grafico_voci_buf=None):
    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    width, height = A4

    logo_path = os.path.join(".github", "logo.png")
    if os.path.exists(logo_path):
        logo = ImageReader(logo_path)
        c.drawImage(logo, width/2 - 3*cm, height - 7*cm, width=6*cm, preserveAspectRatio=True, mask='auto')

    c.setFont("Helvetica-Bold", 20)
    c.drawCentredString(width / 2, height - 8.5 * cm, "Report Finanziario PMI")
    c.setFont("Helvetica", 12)
    c.drawCentredString(width / 2, height - 10 * cm, f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    c.showPage()

    # Sommario
    c.setFont("Helvetica-Bold", 16)
    c.drawString(2 * cm, height - 2 * cm, "📄 Sommario")
    c.setFont("Helvetica", 11)
    y = height - 3 * cm
    c.drawString(2 * cm, y, "1. KPI Aziendali")
    y -= 0.6 * cm
    if grafico_kpi_buf:
        c.drawString(2 * cm, y, "2. Grafico KPI")
        y -= 0.6 * cm
    if grafico_voci_buf:
        c.drawString(2 * cm, y, "3. Grafico Voci di Bilancio")
        y -= 0.6 * cm
    if note:
        c.drawString(2 * cm, y, "4. Note dell’utente")
    c.showPage()

    # KPI Aziendali
    c.setFont("Helvetica-Bold", 16)
    c.drawString(2 * cm, height - 2 * cm, "📊 KPI Aziendali")
    c.setFont("Helvetica", 10)
    y = height - 3.5 * cm
    for idx, row in df.iterrows():
        for key in ["Azienda", "Anno", "EBITDA Margin", "ROE", "ROI", "Current Ratio", "Indice Sintetico", "Valutazione"]:
            val = row.get(key, "-")
            c.drawString(2 * cm, y, f"{key}: {val}")
            y -= 0.5 * cm
        y -= 0.3 * cm
        if y < 4 * cm:
            c.showPage()
            y = height - 3.2 * cm

    # Grafico KPI
    if grafico_kpi_buf:
        c.showPage()
        c.setFont("Helvetica-Bold", 16)
        c.drawString(2 * cm, height - 2 * cm, "📈 Grafico KPI")
        grafico_img = ImageReader(grafico_kpi_buf)
        c.drawImage(grafico_img, 2 * cm, height - 16 * cm, width - 4 * cm, 12 * cm, preserveAspectRatio=True, mask='auto')

    # Grafico Voci
    if grafico_voci_buf:
        c.showPage()
        c.setFont("Helvetica-Bold", 16)
        c.drawString(2 * cm, height - 2 * cm, "📊 Grafico Voci di Bilancio")
        grafico_voci_img = ImageReader(grafico_voci_buf)
        c.drawImage(grafico_voci_img, 2 * cm, height - 16 * cm, width - 4 * cm, 12 * cm, preserveAspectRatio=True, mask='auto')

    # Note utente
    if note:
        c.showPage()
        c.setFont("Helvetica-Bold", 12)
        c.drawString(2 * cm, height - 2 * cm, "📝 Note dell'utente")
        c.setFont("Helvetica", 10)
        y = height - 3 * cm
        for line in note.splitlines():
            c.drawString(2 * cm, y, line)
            y -= 0.5 * cm
            if y < 3 * cm:
                c.showPage()
                y = height - 3 * cm

    c.save()
    buf.seek(0)
    return buf

# === SUPER PDF MIGLIORATO ===
def genera_super_pdf(df_kpi, df_voci, df_yoy, note):
    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    width, height = A4

    logo_path = os.path.join("assets", "logo.png")
    st.write("✅ Verifica logo - Path:", logo_path)
    st.write("✅ Logo trovato:", os.path.exists(logo_path))

    if os.path.exists(logo_path):
        logo = ImageReader(logo_path)
    try:
        c.drawImage(logo, x=2*cm, y=height - 5*cm, width=4*cm, height=2*cm, mask='auto')
        c.setStrokeColorRGB(0.2, 0.2, 0.2)
        c.rect(2*cm, height - 5*cm, 4*cm, 2*cm)  # bordo per visibilità
    except Exception as e:
        print("Errore logo:", e)
        st.warning(f"Errore nel disegno del logo: {e}")


    c.setFont("Helvetica-Bold", 20)
    c.drawCentredString(width / 2, height - 8.5 * cm, "Report Finanziario Completo")
    c.setFont("Helvetica", 12)
    c.drawCentredString(width / 2, height - 10 * cm, f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    c.showPage()

    def draw_table(title, df):
        if df.empty:
            return
        c.setFont("Helvetica-Bold", 16)
        c.drawString(2 * cm, height - 2 * cm, title)
        c.setFont("Helvetica", 10)
        y = height - 3.5 * cm
        for _, row in df.iterrows():
            lines = []
            for k, v in row.items():
                if isinstance(v, float):
                    v = round(v, 2)
                lines.append(f"{k}: {v}")
            for line in lines:
                if len(line) > 110:
                    parts = [line[i:i+110] for i in range(0, len(line), 110)]
                    for p in parts:
                        c.drawString(2 * cm, y, p)
                        y -= 0.4 * cm
                else:
                    c.drawString(2 * cm, y, line)
                    y -= 0.4 * cm
                if y < 3.5 * cm:
                    c.showPage()
                    y = height - 3.5 * cm
            y -= 0.3 * cm  # separatore tra righe
        c.showPage()

    draw_table("📊 KPI Aziendali", df_kpi)
    draw_table("📘 Voci di Bilancio", df_voci)
    draw_table("📈 Analisi Variazioni YoY", df_yoy)

    if note:
        c.setFont("Helvetica-Bold", 16)
        c.drawString(2 * cm, height - 2 * cm, "📝 Note dell'utente")
        c.setFont("Helvetica", 10)
        y = height - 3.5 * cm
        for line in note.splitlines():
            for part in [line[i:i+120] for i in range(0, len(line), 120)]:
                c.drawString(2 * cm, y, part)
                y -= 0.5 * cm
                if y < 3 * cm:
                    c.showPage()
                    y = height - 3 * cm

    c.save()
    buf.seek(0)
    return buf
