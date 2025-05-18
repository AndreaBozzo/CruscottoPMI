# style.py — Definizione stile condiviso per CruscottoPMI

PALETTE = {
    "positivo": "#2ECC71",   # verde brillante
    "negativo": "#E74C3C",   # rosso acceso
    "neutro":   "#F1C40F",   # giallo
    "sfondo_box": "#F9F9F9", # grigio chiarissimo
    "bordo_box":  "#DDDDDD", # grigio bordo
    "testo": "#2C3E50"       # blu/grigio scuro
}

def kpi_card(nome, valore, colore, icona=""):
    return f"""
    <div style='
        border-radius: 1rem;
        padding: 1.2rem;
        margin-bottom: 0.5rem;
        background: rgba(255, 255, 255, 0.15);
        color: #111;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        backdrop-filter: blur(10px);
        transition: transform 0.2s ease-in-out;
        border: 1px solid rgba(255,255,255,0.3);
    ' onmouseover='this.style.transform=\"scale(1.03)\"' onmouseout='this.style.transform=\"scale(1)\"'>
        <div style='font-size: 1.4em; font-weight: 600; color: #111;'>{icona} {nome}</div>
        <div style='font-size: 2em; font-weight: bold; color: {colore}; margin-top: 0.5rem;'>{valore}</div>
    </div>
    """
