import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px
from io import BytesIO
import streamlit as st
import pandas as pd

@st.cache_data(show_spinner=False)
def genera_grafico_voci(df):
    if "Voce" in df.columns and "Importo (€)" in df.columns:
        fig, ax = plt.subplots(figsize=(6, 4), dpi=150)
        data = df.groupby("Voce")["Importo (€)"].sum().sort_values()
        bars = ax.barh(data.index, data.values, color="#ff7f0e")
        ax.set_title("📊 Distribuzione Voci di Bilancio")
        for bar in bars:
            ax.text(
                bar.get_width() + max(data.values)*0.01,
                bar.get_y() + bar.get_height()/2,
                f"{bar.get_width():,.0f} €",
                va='center', fontsize=8
            )
        plt.tight_layout()
        buf = BytesIO()
        plt.savefig(buf, format='png', dpi=150)
        buf.seek(0)
        return buf
    return None

@st.cache_data(show_spinner=False)
def grafico_plotly_kpi(df):
    if df.empty or "Azienda" not in df.columns or "Indice Sintetico" not in df.columns:
        return None
    df = df.copy()
    df["Etichetta"] = df["Azienda"].astype(str) + " " + df["Anno"].astype(str)
    df = df.sort_values("Indice Sintetico", ascending=False)
    fig = px.bar(
        df, x="Etichetta", y="Indice Sintetico", color="Azienda",
        color_discrete_sequence=px.colors.qualitative.Set2,
        text="Indice Sintetico",
        labels={"Indice Sintetico": "Indice (/100)", "Etichetta": "Azienda e Anno"},
        title="🏆 Classifica Indice Sintetico"
    )
    # Linea benchmark
    bm = df[df["Azienda"].str.lower().str.contains("benchmark")]["Indice Sintetico"].mean()
    if pd.notna(bm):
        fig.add_hline(
            y=bm, line_dash="dash", line_color="#999",
            annotation_text="Benchmark", annotation_position="top right"
        )
    fig.update_traces(texttemplate="%{text:.1f}", textposition="outside")
    fig.update_layout(
        yaxis_range=[0, max(110, (bm or 0)*1.1)],
        height=400, template="simple_white",
        margin=dict(t=60, l=40, r=40, b=40)
    )
    return fig

@st.cache_data(show_spinner=False)
def genera_radar_kpi(kpi_dict, benchmark=None):
    import pandas as pd
    import plotly.graph_objects as go

    labels = ["EBITDA Margin", "ROE", "ROI", "Current Ratio"]
    values = []
    bench_vals = []

    for lab in labels:
        # Estrai raw value da dict o da pandas Series/row
        if isinstance(kpi_dict, dict):
            raw = kpi_dict.get(lab, 0)
        else:
            raw = kpi_dict.get(lab, 0) if hasattr(kpi_dict, "get") else (
                kpi_dict[lab] if lab in kpi_dict else 0
            )
        # Converti in float, fallback a 0
        try:
            v = float(raw)
        except Exception:
            v = 0.0

        # Scala solo Current Ratio su 0–100
        if lab == "Current Ratio":
            v *= 20

        values.append(v)

        # Se presente, estrai benchmark analogamente
        if benchmark and lab in benchmark:
            try:
                b_raw = benchmark.get(lab, 0)
                b = float(b_raw)
            except Exception:
                b = 0.0
            if lab == "Current Ratio":
                b *= 20
            bench_vals.append(b)

    # Costruisci figura
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=labels,
        fill='toself',
        name='Azienda'
    ))
    if bench_vals:
        fig.add_trace(go.Scatterpolar(
            r=bench_vals,
            theta=labels,
            fill='toself',
            name='Benchmark',
            line=dict(dash='dot')
        ))

    # Scala del radar in base al massimo valore
    max_val = max(values + bench_vals) * 1.1 if (values or bench_vals) else 1.0
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, max_val])
        ),
        showlegend=True,
        height=400,
        title="🎯 Radar KPI Avanzati"
    )
    return fig


@st.cache_data(show_spinner=False)
def grafico_gauge_indice(valori: dict, benchmark: dict) -> go.Figure:
    """
    Crea un layout 2x2 con gauge KPI strutturali, titoli esterni e delta leggibile.
    """

    fig = go.Figure()
    kpi_order = list(valori.keys())

    for i, kpi in enumerate(kpi_order):
        val = valori.get(kpi)
        ref = benchmark.get(kpi, None)
        if val is None:
            continue

        # Layout 2x2: domain (x,y) manuale
        row, col = divmod(i, 2)
        domain_x = [0.05, 0.48] if col == 0 else [0.52, 0.95]
        domain_y = [0.55, 0.95] if row == 0 else [0.05, 0.45]

        # Intervallo benchmark
        if "indebit" in kpi.lower() or "debito" in kpi.lower():
            target_min = 0
            target_max = ref if ref else 1
        else:
            target_min = ref if ref else 1
            target_max = ref * 2 if ref else 3

        fig.add_trace(go.Indicator(
            mode="gauge+number+delta",
            value=val,
            domain={'x': domain_x, 'y': domain_y},
            number={'font': {'size': 26}},
            delta={
                'reference': ref,
                'relative': False,
                'position': "bottom",
                'increasing': {'color': "green"},
                'decreasing': {'color': "red"},
                'font': {'size': 14}
            },
            gauge={
                'axis': {'range': [0, target_max * 1.2]},
                'bar': {'color': "#1E88E5"},
                'steps': [
                    {'range': [0, target_min], 'color': "#f8d7da"},
                    {'range': [target_min, target_max], 'color': "#d4edda"},
                ],
                'threshold': {
                    'line': {'color': "black", 'width': 2},
                    'thickness': 0.8,
                    'value': ref if ref else target_max
                }
            }
        ))

        # === Titolo esterno (sopra il gauge)
        fig.add_annotation(
            text=f"<b>{kpi}</b>",
            x=sum(domain_x)/2,
            y=domain_y[1] + 0.07,
            xref="paper",
            yref="paper",
            showarrow=False,
            font=dict(size=16)
        )

    fig.update_layout(
        margin=dict(t=40, b=40, l=40, r=40),
        height=600,
        paper_bgcolor="white"
    )

    return fig



@st.cache_data(show_spinner=False)
def genera_heatmap_aziende(bilanci_dict):
    frames = []
    for (az, an), entry in bilanci_dict.items():
        if isinstance(entry, dict) and "completo" in entry:
            df = entry["completo"].copy()
        else:
            parts = [entry[k] for k in ("CE","Attivo","Passivo") if k in entry]
            df = pd.concat(parts, ignore_index=True) if parts else pd.DataFrame()
        if df.empty or "Voce" not in df or "Importo (€)" not in df:
            continue
        df = df[["Voce","Importo (€)"]].copy()
        df["Tag"] = f"{az} ({an})"
        frames.append(df)
    if not frames:
        return None
    df_heat = pd.concat(frames, ignore_index=True)
    pivot = df_heat.pivot_table(index="Voce", columns="Tag", values="Importo (€)", aggfunc="sum").fillna(0)
    heat = go.Heatmap(
        z=pivot.values, x=pivot.columns, y=pivot.index,
        colorscale="RdBu", reversescale=True,
        colorbar=dict(title="€"),
        hovertemplate="Voce: %{y}<br>Tag: %{x}<br>Valore: %{z:,.0f}€<extra></extra>"
    )
    fig = go.Figure(data=[heat])
    fig.update_layout(
        title="🌡️ Heatmap Voci di Bilancio tra Aziende/Anni",
        xaxis_title="Azienda (Anno)", yaxis_title="Voce",
        template="simple_white",
        margin=dict(l=100, r=40, t=60, b=80),
        height=600
    )
    return fig

@st.cache_data(show_spinner=False)
def genera_trend_kpi(df_kpi, kpi, benchmark):
    import plotly.express as px

    # Filtra e prepara i dati
    df = df_kpi[df_kpi["KPI"] == kpi].copy()
    df["Anno"] = pd.to_numeric(df["Anno"], errors="coerce")
    df["Valore"] = pd.to_numeric(df["Valore"], errors="coerce")
    df = df.sort_values(["Azienda", "Anno"])

    # Inizializza la figura
    fig = go.Figure()
    colors = px.colors.qualitative.Plotly
    companies = sorted(df["Azienda"].unique())

    # Una serie per ciascuna azienda, con colori distinti
    for idx, azi in enumerate(companies):
        df_az = df[df["Azienda"] == azi]
        fig.add_trace(go.Scatter(
            x=df_az["Anno"],
            y=df_az["Valore"],
            mode="lines+markers",
            name=azi,
            line=dict(color=colors[idx % len(colors)], width=3),
            marker=dict(size=8, color=colors[idx % len(colors)])
        ))

    # Linea di benchmark orizzontale
    b = benchmark.get(kpi, None)
    if b is not None:
        # Determina l'intervallo X
        anni = df["Anno"].dropna().unique()
        if len(anni):
            x0, x1 = anni.min(), anni.max()
            fig.add_shape(
                type="line",
                x0=x0, x1=x1,
                y0=b, y1=b,
                xref="x", yref="y",
                line=dict(dash="dash", color="black", width=2)
            )
            fig.add_annotation(
                x=x1, y=b,
                text="Benchmark",
                xanchor="right", yanchor="bottom",
                font=dict(color="black"),
                showarrow=False
            )

    # Aggiorna asse Y per includere dati e benchmark
    vals = df["Valore"].dropna().tolist()
    if b is not None:
        vals.append(b)
    if vals:
        y_max = max(vals) * 1.1
        fig.update_yaxes(range=[0, y_max])

    # Layout finale
    fig.update_layout(
        title=f"Trend {kpi}",
        xaxis_title="Anno",
        yaxis_title="Valore",
        template="simple_white",
        margin=dict(t=60, l=40, r=40, b=40),
        height=400
    )

    return fig


@st.cache_data(show_spinner=False)
def genera_grafico_confronto_kpi(df_kpi, kpi, anno, benchmark):
    df = df_kpi[(df_kpi["KPI"]==kpi)&(df_kpi["Anno"]==anno)].copy()
    df["Valore"] = pd.to_numeric(df["Valore"], errors="coerce")
    data = df.groupby("Azienda")["Valore"].mean().sort_values(ascending=False)
    fig = go.Figure()
    fig.add_trace(go.Bar(x=data.index, y=data.values, name="Aziende",
                         marker_color="#1f77b4", text=[f"{v:.1f}" for v in data.values],
                         textposition="outside"))
    b = benchmark.get(kpi, None)
    if b is not None:
        fig.add_trace(go.Bar(x=["Benchmark"], y=[b], name="Benchmark",
                             marker_color="rgba(150,150,150,0.5)",
                             text=[f"{b:.1f}"], textposition="outside"))
    fig.update_layout(title=f"Confronto {kpi}", yaxis_title="Valore",
                      barmode="group", template="simple_white",
                      margin=dict(t=60,l=40,r=40,b=40), height=400)
    return fig

def kpi_card(titolo, valore, benchmark=None, inverti_colori=False):
    """
    Rende un KPI in formato card HTML, con stile condizionato e supporto benchmark.
    :param titolo: Nome del KPI da mostrare
    :param valore: Valore numerico del KPI
    :param benchmark: Valore atteso/benchmark di confronto
    :param inverti_colori: True se valori più bassi sono migliori (es. debito)
    :return: HTML string
    """

    # === Valida valore
    if valore is None or not isinstance(valore, (int, float)):
        return f"<div class='card warning'><b>{titolo}</b><br><span class='kpi-warning'>N/D</span></div>"

    # === Definizione colore semaforico
    classe = "kpi-positivo"
    if benchmark is not None:
        try:
            if inverti_colori:
                if valore <= benchmark:
                    classe = "kpi-positivo"
                elif valore <= benchmark * 1.2:
                    classe = "kpi-benchmark"
                else:
                    classe = "kpi-negativo"
            else:
                if valore >= benchmark:
                    classe = "kpi-positivo"
                elif valore >= benchmark * 0.8:
                    classe = "kpi-benchmark"
                else:
                    classe = "kpi-negativo"
        except:
            classe = "kpi-benchmark"
    else:
        classe = "kpi-benchmark"

    # === Format valore numerico
    valore_fmt = f"{valore:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    # === Output HTML coerente con theme.css
    html = f"""
    <div class='card'>
        <div style='font-weight: 600; font-size: 0.9rem;'>{titolo}</div>
        <div class='{classe}' style='font-size: 1.6rem;'>{valore_fmt}</div>
    </div>
    """
    return html