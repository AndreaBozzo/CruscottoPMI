import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px
from io import BytesIO
import streamlit as st
import pandas as pd

@st.cache_data(show_spinner=False)
@st.cache_data(show_spinner=False)
def genera_grafico_voci(df):
    if "Voce" in df.columns and "Importo (€)" in df.columns:
        fig, ax = plt.subplots(figsize=(6, 4), dpi=150)
        data = df.groupby("Voce")["Importo (€)"].sum().sort_values()
        bars = ax.barh(data.index, data.values, color="#ff7f0e")
        ax.set_title("Distribuzione Voci di Bilancio")
        for bar in bars:
            ax.text(bar.get_width() + max(data.values)*0.01, bar.get_y() + bar.get_height()/2, f"{bar.get_width():,.0f}", va='center', fontsize=8)
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
        df,
        x="Etichetta",
        y="Indice Sintetico",
        color="Azienda",
        color_discrete_sequence=px.colors.qualitative.Set2,
        text="Indice Sintetico",
        labels={"Indice Sintetico": "Indice (/100)", "Etichetta": "Azienda e Anno"},
        title="🏆 Classifica Indice Sintetico"
    )

    fig.add_shape(
        type="line",
        x0=-0.5,
        x1=len(df) - 0.5,
        y0=60,
        y1=60,
        line=dict(color="black", width=2, dash="dash"),
        name="Benchmark"
    )

    fig.update_traces(texttemplate="%{text:.1f}", textposition="outside")
    fig.update_layout(
        yaxis_range=[0, 110],
        height=400,
        uniformtext_minsize=8,
        uniformtext_mode="hide",
        showlegend=True,
        template="simple_white",
        margin=dict(t=60, l=40, r=40, b=40)
    )
    return fig

@st.cache_data(show_spinner=False)
def genera_radar_kpi(kpi_dict):
    labels = ["EBITDA Margin", "ROE", "ROI", "Current Ratio"]
    values = [kpi_dict.get(k, 0) for k in labels]

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=labels,
        fill='toself',
        name='KPI'
    ))

    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True)),
        showlegend=False,
        height=400,
        title="Radar KPI"
    )

    return fig
@st.cache_data(show_spinner=False)
def grafico_gauge_indice(df, benchmark=None):
    benchmark = benchmark or {}
    indicatori = [
        "Indice liquidità",
        "Indice indebitamento",
        "Equity ratio",
        "Return on Equity"
    ]

    fig = go.Figure()
    for i, indice in enumerate(indicatori):
        valore = df.get(indice, None)
        if valore is None or not isinstance(valore, (int, float)):
            continue
        ref = benchmark.get(indice, None)

        fig.add_trace(go.Indicator(
            mode="gauge+number+delta" if ref is not None else "gauge+number",
            value=valore,
            domain={"row": i // 2, "column": i % 2},
            title={"text": indice},
            delta={"reference": ref} if ref is not None else None,
            gauge={
                "axis": {"range": [None, max(valore * 1.5, ref or 1.0)]},
                "bar": {"color": "steelblue"},
            }
        ))

    if not fig.data:
        return None

    fig.update_layout(
        grid={"rows": 2, "columns": 2, "pattern": "independent"},
        height=500,
        margin=dict(l=40, r=40, t=60, b=40),
        title="⏱️ Indicatori Strutturali"
    )
    return fig


@st.cache_data(show_spinner=False)
def grafico_confronto_indice(indice, benchmark_val=60):
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=["Azienda"],
        y=[indice],
        name="Indice Azienda",
        marker_color="#1f77b4"
    ))
    fig.add_trace(go.Bar(
        x=["Benchmark"],
        y=[benchmark_val],
        name="Benchmark",
        marker_color="#95a5a6"
    ))
    fig.update_layout(
        title="Indice Sintetico vs Benchmark",
        yaxis_title="Valore",
        barmode='group',
        height=300,
        template="simple_white"
    )
    return fig

@st.cache_data(show_spinner=False)
def genera_grafico_kpi(df):
    import plotly.express as px
    import plotly.graph_objects as go

    if df.empty:
        return None

    # Rimuove colonne non KPI
    exclude = ["Azienda", "Anno", "Indice Sintetico", "Valutazione"]
    kpi_cols = [col for col in df.columns if col not in exclude]
    azienda = df["Azienda"].iloc[0]
    anno = df["Anno"].iloc[0]

    dati = df[kpi_cols].T
    dati.index.name = "KPI"
    dati = dati.rename(columns={dati.columns[0]: "Valore"}).reset_index()

    dati = dati.sort_values("Valore", ascending=False)

    fig = px.bar(
        dati,
        x="KPI",
        y="Valore",
        title=f"KPI {azienda} – {anno}",
        text_auto='.2s',
        height=400
    )

    fig.update_layout(
        xaxis_title="",
        yaxis_title="Valore",
        showlegend=False,
        margin=dict(l=40, r=40, t=60, b=40)
    )

    return fig

def genera_heatmap_aziende(bilanci_dict):
    """
    Crea una heatmap confrontando le aziende sui valori delle voci di bilancio.
    """
    dati = []

    for (azienda, anno), df in bilanci_dict.items():
        if "Voce" in df.columns and "Importo (€)" in df.columns:
            agg = df.groupby("Voce")["Importo (€)"].sum().rename(f"{azienda} ({anno})")
            dati.append(agg)

    if not dati:
        return None

    df_heat = pd.concat(dati, axis=1).fillna(0)
    fig = px.imshow(df_heat, aspect="auto", color_continuous_scale="RdBu_r",
                    labels=dict(x="Azienda", y="Voce", color="Importo (€)"),
                    title="🌡️ Heatmap Voci di Bilancio tra Aziende/Anni")
    fig.update_layout(margin=dict(l=40, r=40, t=60, b=40))
    return fig
