# =========================================================
# ESTILOS VISUALES DEL DASHBOARD
# Archivo: styles.py
# =========================================================

import base64
import re
from pathlib import Path

import config

def image_to_base64(image_path: str) -> str | None:
    """
    Convierte una imagen local a base64 para incrustarla en CSS.
    """
    try:
        path = Path(image_path)
        if not path.exists():
            return None

        with open(path, "rb") as file:
            return base64.b64encode(file.read()).decode("utf-8")
    except Exception:
        return None

def apply_login_background(image_path: str) -> str:
    """
    Aplica una imagen de fondo SOLO para la pantalla de inicio de sesión.
    
    Uso recomendado en app.py, dentro de render_login_screen():
        st.markdown(
            styles.apply_login_background("assets/fondo.png"),
            unsafe_allow_html=True
        )
    """
    image_base64 = image_to_base64(image_path)

    if not image_base64:
        return ""

    return f"""
    <style>
    /* =====================================================
       FONDO EXCLUSIVO PARA LOGIN
       ===================================================== */
    .stApp {{
        background-image:
            linear-gradient(rgba(255, 255, 255, 0.38), rgba(255, 255, 255, 0.38)),
            url("data:image/png;base64,{image_base64}") !important;
        background-size: cover !important;
        background-position: center center !important;
        background-repeat: no-repeat !important;
        background-attachment: fixed !important;
    }}

    .block-container {{
        position: relative !important;
        z-index: 2 !important;
    }}
    

    /* =====================================================
       FIX DEFINITIVO - QUITAR RECTÁNGULO DEL TÍTULO
       ===================================================== */
    .dashboard-main-title {{
        background: transparent !important;
        border: none !important;
        outline: none !important;
        box-shadow: none !important;
    }}


</style>
    """

def build_global_css() -> str:
    """
    Construye el CSS global del dashboard.
    """
    return f"""
    <style>
    .stApp {{
        background: #FFFFFF;
    }}

    html, body, [class*="css"] {{
        font-family: "Segoe UI", Arial, sans-serif;
        color: {config.COLOR_TEXT};
    }}

    /* =====================================================
       HEADER SUPERIOR STREAMLIT
       ===================================================== */
    header[data-testid="stHeader"] {{
        background: #000000 !important;
        height: 4.6rem !important;
        border-bottom: 0 !important;
        box-shadow: none !important;
    }}

    div[data-testid="stToolbar"] {{
        top: 0.6rem !important;
    }}

    div[data-testid="stDecoration"] {{
        background: #000000 !important;
    }}

    /* Botón colapsar/expandir sidebar */
    button[kind="header"] {{
        color: #FFFFFF !important;
    }}

    button[kind="header"] svg {{
        color: #FFFFFF !important;
        fill: #FFFFFF !important;
    }}

    [data-testid="collapsedControl"] {{
        color: #FFFFFF !important;
    }}

    [data-testid="collapsedControl"] svg {{
        color: #FFFFFF !important;
        fill: #FFFFFF !important;
    }}

    /* =====================================================
       AJUSTE GLOBAL DE CONTENIDO
       ===================================================== */
    .block-container {{
        padding-top: 3.1rem;
        padding-bottom: 2rem;
        padding-left: 2rem;
        padding-right: 2rem;
    }}

    .main .block-container > div:first-child {{
        margin-top: 0;
    }}

    div[data-testid="stAlert"] {{
        margin-top: 0.35rem;
        margin-bottom: 0.9rem;
        border-radius: 16px;
    }}

    /* =====================================================
       SIDEBAR NEGRO CORPORATIVO
       ===================================================== */
    section[data-testid="stSidebar"] {{
        background: #000000 !important;
        border-right: 1px solid #161616 !important;
    }}

    section[data-testid="stSidebar"] * {{
        color: #FFFFFF !important;
    }}

    section[data-testid="stSidebar"] .stMarkdown,
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] span,
    section[data-testid="stSidebar"] div {{
        color: #FFFFFF !important;
    }}

    section[data-testid="stSidebar"] hr {{
        border-color: #202020 !important;
    }}

    section[data-testid="stSidebar"] .stCaption {{
        color: #C8CDD5 !important;
    }}

    /* =====================================================
       BOTÓN DESCARGA GLOBAL SIDEBAR
       ===================================================== */
    section[data-testid="stSidebar"] .stDownloadButton > button {{
        background: rgba(255, 255, 255, 0.10) !important;
        color: #FFFFFF !important;
        border: 1px solid rgba(255, 255, 255, 0.18) !important;
        border-radius: 14px !important;
        padding: 0.70rem 1.2rem !important;
        font-weight: 700 !important;
        box-shadow: none !important;
        transition: all 0.2s ease !important;
    }}

    section[data-testid="stSidebar"] .stDownloadButton > button:hover {{
        background: rgba(255, 255, 255, 0.16) !important;
        color: #FFFFFF !important;
        border: 1px solid rgba(255, 255, 255, 0.26) !important;
        box-shadow: none !important;
    }}

    section[data-testid="stSidebar"] .stDownloadButton > button:focus {{
        outline: none !important;
        color: #FFFFFF !important;
        border: 1px solid rgba(255, 255, 255, 0.28) !important;
        box-shadow: 0 0 0 0.12rem rgba(255, 255, 255, 0.08) !important;
    }}

    /* =====================================================
       HEADER PRINCIPAL CORRIDO
       ===================================================== */
    .top-header-bar-bg {{
        background: #000000;
        height: 116px;
        margin-left: -2rem;
        margin-right: -2rem;
        margin-top: -0.45rem;
        margin-bottom: -92px;
    }}

    .header-inline-row {{
        display: flex;
        align-items: center;
        gap: 0.95rem;
        padding-top: 1.15rem;
        padding-left: 0.3rem;
    }}

    .header-logout-wrap {{
        padding-top: 0.9rem;
    }}

    .brand-logo-box {{
        width: 30px !important;
        height: 30px !important;
        min-width: 30px !important;
        min-height: 30px !important;
        background: #FF002B !important;
        border-radius: 0 !important;
        box-shadow: none !important;
        outline: none !important;
        display: inline-block;
        flex-shrink: 0;
    }}

    .brand-title-group {{
        display: flex;
        flex-direction: column;
        gap: 0.15rem;
    }}

    .brand-title {{
        font-size: 2.15rem;
        font-weight: 800;
        color: #FFFFFF;
        line-height: 1.05;
        letter-spacing: 0.3px;
        margin: 0;
    }}

    .brand-subtitle {{
        font-size: 1rem;
        font-weight: 600;
        color: #D6D9DF;
        letter-spacing: 0.35px;
        margin: 0;
        text-transform: uppercase;
    }}

    /* =====================================================
       LOGO SIDEBAR
       ===================================================== */
    .sidebar-brand {{
        display: flex;
        align-items: center;
        gap: 0.8rem;
        margin-top: 0.1rem;
        margin-bottom: 1.25rem;
    }}

    .sidebar-brand-box {{
        width: 24px !important;
        height: 24px !important;
        min-width: 24px !important;
        min-height: 24px !important;
        background: #FF002B !important;
        border-radius: 0 !important;
        box-shadow: none !important;
        outline: none !important;
        display: inline-block;
        flex-shrink: 0;
    }}

    .sidebar-brand-text {{
        color: #FFFFFF !important;
        font-size: 1.5rem;
        font-weight: 800;
        line-height: 1;
        letter-spacing: 0.2px;
    }}

    .main-title {{
        font-size: 2.4rem;
        font-weight: 800;
        color: {config.COLOR_SECONDARY};
        margin-bottom: 0.2rem;
        letter-spacing: 0.3px;
    }}

    .main-subtitle {{
        font-size: 1.15rem;
        font-weight: 500;
        color: {config.COLOR_MUTED};
        margin-bottom: 1.5rem;
    }}

    .section-title {{
        font-size: 1.35rem;
        font-weight: 700;
        color: {config.COLOR_SECONDARY};
        margin-top: 1rem;
        margin-bottom: 0.85rem;
        border-left: 5px solid #E60023;
        padding-left: 0.75rem;
    }}

    /* =====================================================
       HERO / LOGIN
       ===================================================== */
    .hero-box {{
        background: #FFFFFF;
        border: 1px solid #E7EAF0;
        border-radius: 24px;
        padding: 2rem;
        box-shadow: 0 12px 30px rgba(15, 23, 42, 0.08);
        margin-bottom: 1.5rem;
    }}

    .hero-title {{
        font-size: 2.2rem;
        font-weight: 800;
        color: {config.COLOR_SECONDARY};
        margin-bottom: 0.4rem;
    }}

    .hero-text {{
        font-size: 1rem;
        color: {config.COLOR_MUTED};
        line-height: 1.6;
    }}

    .hero-title-row {{
        display: flex;
        align-items: center;
        gap: 0.85rem;
        margin-bottom: 0.4rem;
    }}

    .hero-logo-box {{
        width: 28px;
        height: 28px;
        min-width: 28px;
        min-height: 28px;
        background: #FF002B;
        border-radius: 0;
        display: inline-block;
        flex-shrink: 0;
    }}

    /* =====================================================
       TARJETAS
       ===================================================== */
    .custom-card {{
        background: #FFFFFF;
        border: 1px solid #E7EAF0;
        border-radius: 20px;
        padding: 1.3rem;
        box-shadow: 0 10px 24px rgba(15, 23, 42, 0.07);
        margin-bottom: 1rem;
        height: 100%;
    }}

    .card-title {{
        font-size: 0.95rem;
        font-weight: 700;
        color: {config.COLOR_MUTED};
        margin-bottom: 0.35rem;
        text-transform: uppercase;
        letter-spacing: 0.4px;
    }}

    .card-value {{
        font-size: 1.8rem;
        font-weight: 800;
        color: {config.COLOR_SECONDARY};
        margin-bottom: 0.2rem;
    }}

    .card-description {{
        font-size: 0.95rem;
        color: {config.COLOR_MUTED};
        line-height: 1.5;
    }}

    .info-box {{
        background: #FFFFFF;
        border: 1px solid #E7EAF0;
        border-left: 5px solid #E60023;
        border-radius: 18px;
        padding: 1rem 1rem;
        margin-bottom: 1rem;
        box-shadow: 0 8px 20px rgba(15, 23, 42, 0.05);
    }}

    .info-box-title {{
        font-size: 1rem;
        font-weight: 700;
        color: {config.COLOR_SECONDARY};
        margin-bottom: 0.45rem;
    }}

    .info-box-body {{
        font-size: 1rem;
        color: #434C5E;
        line-height: 1.7;
    }}

    .sidebar-box {{
        background: #111111;
        border: 1px solid #232323;
        border-left: 5px solid #E60023;
        border-radius: 16px;
        padding: 1rem;
        margin-bottom: 1rem;
        box-shadow: none;
    }}

    .sidebar-box strong {{
        color: #FFFFFF !important;
    }}

    /* =====================================================
       BLOQUE DE MONEDA EN SIDEBAR
       ===================================================== */
    .currency-box {{
        background: linear-gradient(180deg, rgba(255,255,255,0.06) 0%, rgba(255,255,255,0.03) 100%);
        border: 1px solid rgba(255,255,255,0.12);
        border-left: 5px solid #E60023;
        border-radius: 16px;
        padding: 1rem 1rem 0.85rem 1rem;
        margin-top: 0.2rem;
        margin-bottom: 1rem;
    }}

    .currency-box-title {{
        font-size: 0.98rem;
        font-weight: 800;
        color: #FFFFFF !important;
        margin-bottom: 0.3rem;
    }}

    .currency-box-subtitle {{
        font-size: 0.88rem;
        color: #C8CDD5 !important;
        line-height: 1.5;
        margin-bottom: 0.75rem;
    }}

    /* =====================================================
       BOTONES
       ===================================================== */
    .stButton > button {{
        background: #E60023 !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 14px !important;
        padding: 0.70rem 1.2rem !important;
        font-weight: 700 !important;
        transition: all 0.2s ease !important;
        box-shadow: 0 8px 18px rgba(230, 0, 35, 0.20) !important;
    }}

    .stButton > button:hover {{
        background: #C4001E !important;
        box-shadow: 0 10px 22px rgba(230, 0, 35, 0.28) !important;
    }}

    .stButton > button:focus {{
        outline: none !important;
        box-shadow: 0 0 0 0.2rem rgba(230, 0, 35, 0.18) !important;
    }}

    /* =====================================================
       LOGIN FORM - ENTER SIN CAMBIAR DISEÑO
       Quita el borde automático de st.form y conserva el botón rojo.
       ===================================================== */
    div[data-testid="stForm"] {{
        border: none !important;
        background: transparent !important;
        padding: 0 !important;
        margin: 0 !important;
        box-shadow: none !important;
        outline: none !important;
    }}

    div[data-testid="stForm"] > div {{
        border: none !important;
        background: transparent !important;
        padding: 0 !important;
        margin: 0 !important;
        box-shadow: none !important;
        outline: none !important;
    }}

    div[data-testid="stForm"] [data-testid="stFormSubmitButton"] > button,
    .stFormSubmitButton > button {{
        background: #E60023 !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 14px !important;
        padding: 0.70rem 1.2rem !important;
        font-weight: 700 !important;
        transition: all 0.2s ease !important;
        box-shadow: 0 8px 18px rgba(230, 0, 35, 0.20) !important;
    }}

    div[data-testid="stForm"] [data-testid="stFormSubmitButton"] > button:hover,
    .stFormSubmitButton > button:hover {{
        background: #C4001E !important;
        color: #FFFFFF !important;
        box-shadow: 0 10px 22px rgba(230, 0, 35, 0.28) !important;
    }}

    div[data-testid="stForm"] [data-testid="stFormSubmitButton"] > button:focus,
    .stFormSubmitButton > button:focus {{
        outline: none !important;
        color: #FFFFFF !important;
        box-shadow: 0 0 0 0.2rem rgba(230, 0, 35, 0.18) !important;
    }}


    /* Botones dentro del sidebar */
    section[data-testid="stSidebar"] .stButton > button {{
        width: 100% !important;
    }}

    /* =====================================================
       INPUTS
       ===================================================== */
    .stTextInput input,
    .stNumberInput input,
    .stFileUploader {{
        border-radius: 12px !important;
    }}

    .stTextInput input:focus,
    .stNumberInput input:focus {{
        border-color: #E60023 !important;
        box-shadow: 0 0 0 0.15rem rgba(230, 0, 35, 0.14) !important;
    }}

    .stSelectbox label,
    .stMultiSelect label {{
        font-size: 0.93rem !important;
        font-weight: 700 !important;
        color: {config.COLOR_SECONDARY} !important;
        margin-bottom: 0.2rem !important;
    }}

    .stSelectbox div[data-baseweb="select"] > div,
    .stMultiSelect div[data-baseweb="select"] > div {{
        min-height: 46px !important;
        border-radius: 14px !important;
        border: 1px solid #DCE3EC !important;
        background: #FFFFFF !important;
        box-shadow: 0 2px 8px rgba(15, 23, 42, 0.04) !important;
    }}

    .stSelectbox div[data-baseweb="select"] > div:hover,
    .stMultiSelect div[data-baseweb="select"] > div:hover {{
        border-color: #C9D3DF !important;
    }}

    .stSelectbox div[data-baseweb="select"] > div:focus-within,
    .stMultiSelect div[data-baseweb="select"] > div:focus-within {{
        border-color: #E60023 !important;
        box-shadow: 0 0 0 0.16rem rgba(230, 0, 35, 0.12) !important;
    }}

    /* =====================================================
       EXPANDER MONEDA EN SIDEBAR
       ===================================================== */
    section[data-testid="stSidebar"] details {{
        background: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.12) !important;
        border-radius: 14px !important;
        margin-top: 0.35rem !important;
        margin-bottom: 1rem !important;
        overflow: hidden !important;
    }}

    section[data-testid="stSidebar"] details summary {{
        padding: 0.75rem 0.9rem !important;
        font-weight: 700 !important;
        color: #FFFFFF !important;
        background: rgba(255, 255, 255, 0.04) !important;
    }}

    section[data-testid="stSidebar"] details summary:hover {{
        background: rgba(255, 255, 255, 0.08) !important;
    }}

    section[data-testid="stSidebar"] details[open] summary {{
        border-bottom: 1px solid rgba(255, 255, 255, 0.10) !important;
    }}

    /* =====================================================
       NUMBER INPUT DENTRO DEL SIDEBAR
       Corregido para que el texto se vea negro
       ===================================================== */
    section[data-testid="stSidebar"] .stNumberInput {{
        margin-top: 0.25rem !important;
        margin-bottom: 0.2rem !important;
    }}

    section[data-testid="stSidebar"] .stNumberInput label {{
        color: #FFFFFF !important;
        font-size: 0.92rem !important;
        font-weight: 700 !important;
        margin-bottom: 0.28rem !important;
    }}

    section[data-testid="stSidebar"] .stNumberInput div[data-baseweb="input"] {{
        background: #FFFFFF !important;
        border: 1px solid rgba(255, 255, 255, 0.16) !important;
        border-radius: 14px !important;
        min-height: 46px !important;
        box-shadow: none !important;
    }}

    section[data-testid="stSidebar"] .stNumberInput div[data-baseweb="input"]:hover {{
        border-color: rgba(255, 255, 255, 0.24) !important;
        background: #FFFFFF !important;
    }}

    section[data-testid="stSidebar"] .stNumberInput div[data-baseweb="input"]:focus-within {{
        border-color: #E60023 !important;
        box-shadow: 0 0 0 0.14rem rgba(230, 0, 35, 0.16) !important;
        background: #FFFFFF !important;
    }}

    section[data-testid="stSidebar"] .stNumberInput input {{
        background: transparent !important;
        color: #000000 !important;
        -webkit-text-fill-color: #000000 !important;
        border: none !important;
        caret-color: #000000 !important;
        font-weight: 600 !important;
    }}

    section[data-testid="stSidebar"] .stNumberInput input::placeholder {{
        color: #6B7280 !important;
        opacity: 1 !important;
    }}

    section[data-testid="stSidebar"] .stNumberInput button {{
        background: transparent !important;
        border: none !important;
        color: #000000 !important;
        box-shadow: none !important;
    }}

    section[data-testid="stSidebar"] .stNumberInput button:hover {{
        background: rgba(0, 0, 0, 0.06) !important;
    }}

    section[data-testid="stSidebar"] .stNumberInput svg {{
        color: #000000 !important;
        fill: #000000 !important;
    }}

    /* =====================================================
       BLOQUES DE FILTROS
       ===================================================== */
    .filter-box {{
        background: linear-gradient(180deg, #FFFFFF 0%, #FBFCFE 100%);
        border: 1px solid #E7EAF0;
        border-left: 5px solid #E60023;
        border-radius: 20px;
        padding: 1rem 1.1rem;
        margin-top: 0.25rem;
        margin-bottom: 0.95rem;
        box-shadow: 0 10px 24px rgba(15, 23, 42, 0.05);
    }}

    .filter-box-title {{
        font-size: 1rem;
        font-weight: 800;
        color: {config.COLOR_SECONDARY};
        margin-bottom: 0.3rem;
    }}

    .filter-box-subtitle {{
        font-size: 0.93rem;
        color: {config.COLOR_MUTED};
        line-height: 1.55;
    }}

    /* =====================================================
       NUEVO BLOQUE VISUAL PARA FILTRO DE DIMENSIÓN
       ===================================================== */
    .dimension-filter-box {{
        background: #FFFFFF;
        border: 1px solid #E7EAF0;
        border-left: 5px solid {config.COLOR_SECONDARY};
        border-radius: 18px;
        padding: 0.95rem 1rem;
        margin-top: -0.15rem;
        margin-bottom: 0.95rem;
        box-shadow: 0 8px 20px rgba(15, 23, 42, 0.05);
    }}

    .dimension-filter-title {{
        font-size: 0.98rem;
        font-weight: 800;
        color: {config.COLOR_SECONDARY};
        margin-bottom: 0.22rem;
    }}

    .dimension-filter-subtitle {{
        font-size: 0.90rem;
        color: {config.COLOR_MUTED};
        line-height: 1.5;
        margin-bottom: 0.35rem;
    }}

    /* =====================================================
       RADIO BUTTONS SIDEBAR
       ===================================================== */
    section[data-testid="stSidebar"] div[role="radiogroup"] > label {{
        background: transparent !important;
        border-radius: 12px !important;
        padding: 0.2rem 0.3rem !important;
    }}

    section[data-testid="stSidebar"] div[role="radiogroup"] label,
    section[data-testid="stSidebar"] div[role="radiogroup"] label p,
    section[data-testid="stSidebar"] div[role="radiogroup"] span {{
        font-size: 1rem !important;
        font-weight: 700 !important;
        line-height: 1.35 !important;
    }}

    section[data-testid="stSidebar"] input[type="radio"] {{
        accent-color: #E60023 !important;
    }}

    section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {{
        color: #FFFFFF !important;
        font-weight: 500;
    }}

    /* =====================================================
       CHIPS / TABLAS HORIZONTALES
       ===================================================== */
    .metric-legend {{
        display: flex;
        flex-wrap: wrap;
        gap: 0.6rem;
        margin-bottom: 1rem;
    }}

    .metric-chip {{
        display: inline-block;
        padding: 0.45rem 0.85rem;
        border-radius: 999px;
        color: white;
        font-weight: 700;
        font-size: 0.9rem;
        box-shadow: 0 4px 10px rgba(31, 42, 68, 0.10);
    }}

    .chip-real {{
        background: #0B5A7A;
    }}

    .chip-client {{
        background: #ED7D31;
    }}

    .chip-sku {{
        background: #2E7D32;
    }}

    .horizontal-table-card {{
        background: white;
        border: 1px solid #E7EAF0;
        border-radius: 20px;
        padding: 1rem;
        box-shadow: 0 10px 24px rgba(15, 23, 42, 0.06);
        margin-bottom: 1rem;
    }}

    .horizontal-table-title {{
        font-size: 1.08rem;
        font-weight: 800;
        color: {config.COLOR_SECONDARY};
        margin-bottom: 0.8rem;
    }}

    .h-table {{
        display: grid;
        width: 100%;
        gap: 0;
    }}

    .h-table-8 {{
        grid-template-columns: 1.2fr 1fr 1fr 1fr 1fr 1fr 1fr 1fr;
    }}

    .h-table-5 {{
        grid-template-columns: 1.2fr 1fr 1fr 1fr 1fr;
    }}

    .h-table-header {{
        margin-bottom: 0.35rem;
    }}

    .h-cell {{
        padding: 0.78rem 0.7rem;
        border: 1px solid #E5E7EB;
        font-size: 0.93rem;
    }}

    .h-header {{
        font-weight: 700;
        color: white;
        text-align: center;
    }}

    .h-header-real {{
        background: #0B5A7A;
    }}

    .plan-header-client {{
        background: #ED7D31;
        color: white;
    }}

    .plan-header-sku {{
        background: #2E7D32;
        color: white;
    }}

    .h-header-neutral {{
        background: {config.COLOR_SECONDARY};
        color: white;
    }}

    .h-row-label {{
        background: #F8FAFC;
        color: {config.COLOR_SECONDARY};
        font-weight: 700;
    }}

    .h-value {{
        background: white;
        text-align: right;
        font-variant-numeric: tabular-nums;
    }}

    
    /* =====================================================
       BASE MTD - NÚMEROS MÁS GRANDES EN TABLAS EJECUTIVAS
       Solo afecta los valores numéricos de las tablas de Base MTD.
       No modifica encabezados, etiquetas de periodo ni tarjetas KPI.
       ===================================================== */
    .base-mtd-number-table-card .h-value {{
        font-size: 1.18rem !important;
        font-weight: 650 !important;
        line-height: 1.25 !important;
    }}

    .base-mtd-number-table-card .negative-value {{
        font-size: 1.18rem !important;
        font-weight: 800 !important;
        line-height: 1.25 !important;
    }}

.negative-value {{
        color: {config.COLOR_ERROR};
        font-weight: 700;
    }}

    .neutral-value {{
        color: {config.COLOR_TEXT};
    }}

    /* =====================================================
       REPORTES EJECUTIVOS
       ===================================================== */
    .report-title-box {{
        background: #FFFFFF;
        border: 1px solid #E7EAF0;
        border-radius: 22px;
        padding: 1.35rem 1.4rem;
        box-shadow: 0 10px 24px rgba(15, 23, 42, 0.06);
        margin-bottom: 1rem;
    }}

    .report-title-main {{
        font-size: 1.55rem;
        font-weight: 800;
        color: {config.COLOR_SECONDARY};
        margin-bottom: 0.35rem;
    }}

    .report-title-sub {{
        font-size: 0.98rem;
        color: {config.COLOR_MUTED};
        line-height: 1.6;
    }}

    .report-note {{
        font-size: 0.92rem;
        color: {config.COLOR_MUTED};
        margin-top: 0.2rem;
        margin-bottom: 0.9rem;
        line-height: 1.5;
    }}

    .report-table-card {{
        background: white;
        border: 1px solid #E7EAF0;
        border-radius: 20px;
        padding: 1rem;
        box-shadow: 0 10px 24px rgba(15, 23, 42, 0.06);
        margin-bottom: 1rem;
        overflow: hidden;
    }}

    .report-table-title {{
        font-size: 1.02rem;
        font-weight: 800;
        color: {config.COLOR_SECONDARY};
        margin-bottom: 0.8rem;
    }}

    .report-table-scroll {{
        overflow-x: auto;
        overflow-y: hidden;
        border-radius: 14px;
    }}

    .report-grid {{
        display: grid;
        width: 100%;
        min-width: 980px;
        gap: 0;
    }}

    .report-grid-8 {{
        grid-template-columns: 2.15fr 1fr 1fr 1fr 1fr 1fr 1fr 1fr;
    }}

    .report-grid-9 {{
        grid-template-columns: 1.65fr 2.05fr 1fr 1fr 1fr 1fr 1fr 1fr 1fr;
        min-width: 1180px;
    }}

    .report-grid-11 {{
        grid-template-columns: 1.45fr 1.20fr 1.90fr 2.15fr 0.85fr 0.85fr 0.85fr 1fr 1fr 1fr 1fr;
        min-width: 1550px;
    }}

    .report-row {{
        display: contents;
    }}

    .report-cell {{
        border: 1px solid #E5E7EB;
        padding: 0.72rem 0.55rem;
        min-height: 52px;
        display: flex;
        align-items: center;
        justify-content: center;
        text-align: center;
        font-size: 0.92rem;
        line-height: 1.35;
        background: white;
        box-sizing: border-box;
        font-variant-numeric: tabular-nums;
        white-space: nowrap;
    }}

    .report-header {{
        color: white;
        font-weight: 800;
    }}

    .report-header-neutral {{
        background: {config.COLOR_SECONDARY};
    }}

    .report-header-actual {{
        background: #0B5A7A;
    }}

    .report-header-plan {{
        background: #D4A017;
        color: white;
    }}

    .report-header-py {{
        background: #0B5A7A;
    }}

    .report-label-cell {{
        background: #F8FAFC;
        color: {config.COLOR_SECONDARY};
        font-weight: 700;
        position: sticky;
        left: 0;
        z-index: 3;
        justify-content: flex-start;
        text-align: left;
        padding-left: 0.85rem;
    }}

    .report-header-sticky {{
        position: sticky;
        left: 0;
        z-index: 4;
        justify-content: flex-start;
        text-align: left;
        padding-left: 0.85rem;
    }}

    /* =====================================================
       HEADER CATEGORY FIJO EN VERTICAL Y HORIZONTAL
       ===================================================== */
    .report-category-header-sticky {{
        position: sticky !important;
        left: 0 !important;
        top: 0 !important;
        z-index: 180 !important;
        justify-content: flex-start;
        text-align: left;
        padding-left: 0.85rem;
        background: #1F2A44 !important;
        box-shadow: 4px 0 8px rgba(15, 23, 42, 0.16);
    }}

    .report-value-cell {{
        color: {config.COLOR_TEXT};
    }}

    .report-negative {{
        color: {config.COLOR_ERROR};
        font-weight: 700;
    }}

    .report-total .report-cell {{
        font-weight: 800;
        background: #F3F6FA;
    }}

    .report-total .report-label-cell {{
        background: #F3F6FA;
    }}

    .report-highlight .report-cell {{
        background: #E8F3E6;
        font-weight: 800;
    }}

    .report-highlight .report-label-cell {{
        background: #DCEFD8;
    }}

    .report-spacer {{
        height: 0.35rem;
    }}

    /* =====================================================
       FIX FINAL: ENCABEZADOS FIJOS Y PRIMERA COLUMNA FIJA
       ===================================================== */
    .report-table-scroll {{
        overflow-x: auto !important;
        overflow-y: auto !important;
        max-height: 560px !important;
        border-radius: 14px;
        border: 1px solid #E5E7EB;
        position: relative;
        background: #FFFFFF;
    }}

    .report-category-scroll {{
        max-height: 620px !important;
        position: relative !important;
    }}

    .report-table-scroll > .report-grid:first-child {{
        position: sticky !important;
        top: 0 !important;
        z-index: 70 !important;
        background: #FFFFFF !important;
    }}

    .report-header {{
        position: sticky !important;
        top: 0 !important;
        z-index: 80 !important;
    }}

    .report-header-sticky {{
        position: sticky !important;
        top: 0 !important;
        left: 0 !important;
        z-index: 95 !important;
    }}

    .report-category-grid {{
        display: grid !important;
        grid-template-columns: 1.45fr 1.20fr 1.90fr 2.15fr 0.85fr 0.85fr 0.85fr 1fr 1fr 1fr 1fr !important;
        min-width: 1550px !important;
        width: 100% !important;
        gap: 0 !important;
    }}

    .report-category-header-sticky {{
        position: sticky !important;
        left: 0 !important;
        top: 0 !important;
        z-index: 120 !important;
        justify-content: flex-start;
        text-align: left;
        padding-left: 0.85rem;
        background: #1F2A44 !important;
        box-shadow: 4px 0 8px rgba(15, 23, 42, 0.16);
    }}

    .report-sticky-cell {{
        position: sticky !important;
        left: 0 !important;
        z-index: 30 !important;
        background: #F8FAFC;
        box-shadow: 4px 0 8px rgba(15, 23, 42, 0.08);
    }}

    .report-category-grid .report-sticky-cell {{
        position: sticky !important;
        left: 0 !important;
        z-index: 30 !important;
        background: #F8FAFC !important;
    }}

    .report-category-grid .report-header {{
        position: sticky !important;
        top: 0 !important;
        z-index: 90 !important;
    }}

    .report-category-grid .report-category-header-sticky {{
        z-index: 130 !important;
    }}

    .report-category-product-cell {{
        background: #F8FAFC;
        color: {config.COLOR_SECONDARY};
        font-weight: 700;
        justify-content: flex-start;
        text-align: left;
        padding-left: 0.85rem;
        position: static !important;
        left: auto !important;
        z-index: 1 !important;
    }}

    .report-total .report-sticky-cell {{
        background: #F3F6FA !important;
    }}

    .report-highlight .report-sticky-cell {{
        background: #DCEFD8 !important;
    }}

    /* =====================================================
       AJUSTE REPORTE 4: ALINEACIÓN + CLIENT NAME FIJO
       ===================================================== */
    .report-grid-9 {{
        grid-template-columns: 2.45fr 1.05fr 0.95fr 0.95fr 0.95fr 1.08fr 1.08fr 1.08fr 1.08fr !important;
        min-width: 1280px !important;
        width: 100% !important;
        align-items: stretch !important;
    }}

    .report-grid-9 .report-cell {{
        min-width: 0 !important;
        box-sizing: border-box !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
    }}

    .report-grid-9 .report-header-sticky,
    .report-grid-9 .report-sticky-cell,
    .report-grid-9 .report4-sticky-cell,
    .report-grid-9 .report4-sticky-header {{
        position: sticky !important;
        left: 0 !important;
        z-index: 110 !important;
        justify-content: flex-start !important;
        text-align: left !important;
        padding-left: 0.85rem !important;
        box-shadow: 4px 0 8px rgba(15, 23, 42, 0.10) !important;
    }}

    .report-grid-9 .report-header-sticky,
    .report-grid-9 .report4-sticky-header {{
        top: 0 !important;
        z-index: 170 !important;
        background: #1F2A44 !important;
    }}

    .report-grid-9 .report-sticky-cell,
    .report-grid-9 .report4-sticky-cell {{
        background: #F8FAFC !important;
        color: #1F2A44 !important;
        font-weight: 700 !important;
    }}

    .report-grid-9 .report-total .report-sticky-cell,
    .report-grid-9 .report-total .report4-sticky-cell {{
        background: #F3F6FA !important;
    }}

    .report-grid-9 .report-highlight .report-sticky-cell,
    .report-grid-9 .report-highlight .report4-sticky-cell {{
        background: #DCEFD8 !important;
    }}

    /* Grid HTML específica para Reporte 4. */
    .report4-grid {{
        display: grid !important;
        grid-template-columns: 2.45fr 1.05fr 0.95fr 0.95fr 0.95fr 1.08fr 1.08fr 1.08fr 1.08fr !important;
        min-width: 1280px !important;
        width: 100% !important;
        gap: 0 !important;
        align-items: stretch !important;
    }}

    .report4-grid .report-cell {{
        min-width: 0 !important;
        box-sizing: border-box !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
    }}

    .report4-grid .report-header {{
        position: sticky !important;
        top: 0 !important;
        z-index: 140 !important;
    }}

    .report4-sticky-cell {{
        position: sticky !important;
        left: 0 !important;
        z-index: 110 !important;
        background: #F8FAFC !important;
        color: #1F2A44 !important;
        font-weight: 700 !important;
        justify-content: flex-start !important;
        text-align: left !important;
        padding-left: 0.85rem !important;
        box-shadow: 4px 0 8px rgba(15, 23, 42, 0.10) !important;
    }}

    .report4-sticky-header {{
        position: sticky !important;
        top: 0 !important;
        left: 0 !important;
        z-index: 190 !important;
        background: #1F2A44 !important;
        justify-content: flex-start !important;
        text-align: left !important;
        padding-left: 0.85rem !important;
        box-shadow: 4px 0 8px rgba(15, 23, 42, 0.14) !important;
    }}

    .report4-code-cell {{
        position: static !important;
        left: auto !important;
        z-index: 1 !important;
        background: #F8FAFC !important;
        color: #1F2A44 !important;
        font-weight: 700 !important;
        justify-content: flex-start !important;
        text-align: left !important;
        padding-left: 0.85rem !important;
        box-shadow: none !important;
    }}

    .report4-code-header {{
        position: sticky !important;
        top: 0 !important;
        z-index: 140 !important;
        background: #1F2A44 !important;
    }}

    .report4-total-cell.report4-sticky-cell,
    .report-total .report4-sticky-cell {{
        background: #F3F6FA !important;
    }}

    .report4-highlight-cell.report4-sticky-cell,
    .report-highlight .report4-sticky-cell {{
        background: #DCEFD8 !important;
    }}


    /* =====================================================
       FIX DEFINITIVO REPORTE 4:
       CLIENT NAME + ENCABEZADO FIJOS
       ===================================================== */
    .report4-scroll {{
        overflow-x: auto !important;
        overflow-y: auto !important;
        max-height: 560px !important;
        position: relative !important;
        isolation: isolate !important;
        background: #FFFFFF !important;
    }}

    .report4-scroll > .report4-grid:first-child {{
        position: relative !important;
        top: auto !important;
        z-index: auto !important;
        background: #FFFFFF !important;
    }}

    .report4-grid {{
        display: grid !important;
        grid-template-columns: 2.45fr 1.05fr 0.95fr 0.95fr 0.95fr 1.08fr 1.08fr 1.08fr 1.08fr !important;
        min-width: 1280px !important;
        width: 100% !important;
        gap: 0 !important;
        align-items: stretch !important;
    }}

    .report4-grid > .report-cell {{
        min-width: 0 !important;
        box-sizing: border-box !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
        white-space: nowrap !important;
    }}

    .report4-grid > .report-cell:nth-child(-n+9) {{
        position: sticky !important;
        top: 0 !important;
        z-index: 220 !important;
    }}

    .report4-grid > .report-cell:nth-child(9n+1) {{
        position: sticky !important;
        left: 0 !important;
        z-index: 210 !important;
        justify-content: flex-start !important;
        text-align: left !important;
        padding-left: 0.85rem !important;
        box-shadow: 4px 0 8px rgba(15, 23, 42, 0.14) !important;
    }}

    .report4-grid > .report-cell:first-child,
    .report4-grid > .report4-sticky-header:first-child {{
        position: sticky !important;
        top: 0 !important;
        left: 0 !important;
        z-index: 320 !important;
        background: #1F2A44 !important;
        color: #FFFFFF !important;
        justify-content: flex-start !important;
        text-align: left !important;
        padding-left: 0.85rem !important;
        box-shadow: 4px 0 8px rgba(15, 23, 42, 0.18) !important;
    }}

    .report4-grid > .report4-sticky-cell {{
        background: #F8FAFC !important;
        color: #1F2A44 !important;
        font-weight: 700 !important;
    }}

    .report4-grid > .report4-code-cell {{
        position: static !important;
        left: auto !important;
        z-index: 1 !important;
        background: #F8FAFC !important;
        color: #1F2A44 !important;
        font-weight: 700 !important;
        justify-content: flex-start !important;
        text-align: left !important;
        padding-left: 0.85rem !important;
        box-shadow: none !important;
    }}

    .report4-grid > .report4-code-header {{
        position: sticky !important;
        top: 0 !important;
        left: auto !important;
        z-index: 220 !important;
        background: #1F2A44 !important;
        color: #FFFFFF !important;
        box-shadow: none !important;
    }}

    .report4-grid > .report4-total-cell {{
        background: #F3F6FA !important;
        font-weight: 800 !important;
    }}

    .report4-grid > .report4-highlight-cell {{
        background: #DCEFD8 !important;
        font-weight: 800 !important;
    }}


    /* =====================================================
       BASE MTD - VISTA EJECUTIVA SUPERIOR
       ===================================================== */
    .base-mtd-toolbar {{
        display: flex;
        align-items: end;
        gap: 0.85rem;
        margin-top: 0.85rem;
        margin-bottom: 1.05rem;
    }}

    .base-mtd-toolbar-left {{
        flex: 1 1 auto;
        display: grid;
        grid-template-columns: 0.9fr 1fr;
        gap: 0.8rem;
        max-width: 560px;
    }}

    .base-mtd-toolbar-middle {{
        flex: 1.2 1 auto;
        display: flex;
        align-items: center;
        justify-content: flex-start;
        gap: 0.6rem;
        padding-bottom: 0.18rem;
    }}

    .base-mtd-toolbar-right {{
        flex: 0 0 auto;
        display: flex;
        justify-content: flex-end;
        align-items: center;
        padding-bottom: 0.05rem;
    }}

    .base-mtd-kpi-grid {{
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: 1rem;
        margin-top: 1rem;
        margin-bottom: 1.05rem;
    }}

    .base-mtd-kpi-card {{
        background: #FFFFFF;
        border: 1px solid #E7EAF0;
        border-radius: 20px;
        padding: 1.2rem 1.25rem;
        min-height: 118px;
        display: flex;
        align-items: center;
        gap: 1.05rem;
        box-shadow: 0 10px 26px rgba(15, 23, 42, 0.06);
    }}

    .base-mtd-kpi-icon {{
        width: 56px;
        height: 56px;
        min-width: 56px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        color: #FFFFFF;
        font-size: 1.65rem;
        font-weight: 900;
        box-shadow: 0 10px 18px rgba(15, 23, 42, 0.14);
    }}

    .base-mtd-kpi-icon-blue {{
        background: linear-gradient(135deg, #0B5A7A 0%, #0E7AA2 100%);
    }}

    .base-mtd-kpi-icon-orange {{
        background: linear-gradient(135deg, #ED7D31 0%, #FF9A4A 100%);
    }}

    .base-mtd-kpi-icon-green {{
        background: linear-gradient(135deg, #1B7A3A 0%, #2E9E4E 100%);
    }}

    .base-mtd-kpi-body {{
        display: flex;
        flex-direction: column;
        gap: 0.12rem;
        min-width: 0;
    }}

    .base-mtd-kpi-title {{
        font-size: 0.88rem;
        font-weight: 800;
        color: #1F2A44;
        line-height: 1.25;
        text-transform: none;
    }}

    .base-mtd-kpi-value {{
        font-size: 1.75rem;
        font-weight: 900;
        color: #111827;
        line-height: 1.15;
        letter-spacing: 0.1px;
    }}

    .base-mtd-kpi-description {{
        font-size: 0.92rem;
        color: #667085;
        line-height: 1.35;
        margin-top: 0.15rem;
    }}

    .base-mtd-download-wrap .stDownloadButton > button {{
        background: #FFFFFF !important;
        color: #1F2A44 !important;
        border: 1px solid #DCE3EC !important;
        border-radius: 14px !important;
        padding: 0.66rem 1.1rem !important;
        font-weight: 800 !important;
        box-shadow: 0 4px 12px rgba(15, 23, 42, 0.06) !important;
    }}

    .base-mtd-download-wrap .stDownloadButton > button:hover {{
        background: #F8FAFC !important;
        color: #111827 !important;
        border-color: #C9D3DF !important;
        box-shadow: 0 6px 16px rgba(15, 23, 42, 0.09) !important;
    }}

    /* Botón individual del Dashboard: compacto, alineado a la derecha. */
    .dashboard-download-wrap .stDownloadButton > button {{
        width: 46px !important;
        min-width: 46px !important;
        height: 46px !important;
        padding: 0 !important;
        border-radius: 14px !important;
        background: #FFFFFF !important;
        color: #1F2A44 !important;
        border: 1px solid #DCE3EC !important;
        box-shadow: 0 4px 12px rgba(15, 23, 42, 0.06) !important;
    }}

    .dashboard-download-wrap .stDownloadButton > button:hover {{
        background: #F8FAFC !important;
        border-color: #C9D3DF !important;
        box-shadow: 0 6px 16px rgba(15, 23, 42, 0.09) !important;
    }}

    .base-mtd-compact-note {{
        font-size: 0.92rem;
        color: #667085;
        margin-top: 0.15rem;
        margin-bottom: 0.65rem;
        line-height: 1.45;
    }}

    .base-mtd-section-heading {{
        font-size: 1.45rem;
        font-weight: 800;
        color: #1F2A44;
        margin-top: 1.15rem;
        margin-bottom: 0.35rem;
    }}

    @media (max-width: 1200px) {{
        .base-mtd-toolbar {{
            flex-direction: column;
            align-items: stretch;
        }}

        .base-mtd-toolbar-left {{
            max-width: 100%;
        }}

        .base-mtd-kpi-grid {{
            grid-template-columns: 1fr;
        }}
    }}


    /* =====================================================
       REFINAMIENTO EJECUTIVO: TABLAS Y GRÁFICOS
       ===================================================== */
    .report-table-card,
    .horizontal-table-card,
    .custom-card,
    .report-title-box,
    .base-mtd-kpi-card {{
        border: 1px solid #E8ECF3 !important;
        box-shadow: 0 12px 30px rgba(15, 23, 42, 0.055) !important;
    }}

    .report-table-scroll {{
        border: none !important;
        background: #FFFFFF !important;
        box-shadow: inset 0 0 0 1px #EEF1F5 !important;
    }}

    .report-cell {{
        border-left: none !important;
        border-right: none !important;
        border-top: none !important;
        border-bottom: 1px solid #EEF1F5 !important;
        min-height: 48px !important;
        padding: 0.68rem 0.62rem !important;
        background: #FFFFFF !important;
    }}

    .report-header {{
        border-bottom: none !important;
        box-shadow: none !important;
        letter-spacing: 0.15px !important;
        min-height: 50px !important;
    }}

    .report-label-cell,
    .report4-sticky-cell,
    .report4-code-cell,
    .report-category-product-cell,
    .report-sticky-cell {{
        background: #FAFBFD !important;
        color: #1F2A44 !important;
        border-bottom: 1px solid #EEF1F5 !important;
    }}

    .report-total .report-cell,
    .report-total .report-label-cell,
    .report4-total-cell,
    .report4-total-cell.report4-sticky-cell {{
        background: #F3F6FA !important;
        font-weight: 900 !important;
    }}

    .report-highlight .report-cell,
    .report-highlight .report-label-cell,
    .report4-highlight-cell,
    .report4-highlight-cell.report4-sticky-cell {{
        background: #E8F5EA !important;
        font-weight: 900 !important;
    }}

    .report-table-title {{
        font-size: 1.06rem !important;
        margin-bottom: 0.95rem !important;
    }}

    .report-note {{
        color: #667085 !important;
        font-size: 0.93rem !important;
    }}

    .stTabs [data-baseweb="tab-list"] {{
        gap: 0.25rem !important;
        border-bottom: 1px solid #EEF1F5 !important;
    }}

    .stTabs [data-baseweb="tab"] {{
        border-radius: 999px 999px 0 0 !important;
        padding: 0.55rem 0.9rem !important;
        font-weight: 700 !important;
    }}

    /* Botones más compactos para filtros: deja de sentirse como barra completa */
    div[data-testid="stButton"] > button {{
        min-height: 46px !important;
    }}

    .js-plotly-plot .plotly .modebar {{
        opacity: 0.35 !important;
        transition: opacity 0.2s ease !important;
    }}

    .js-plotly-plot .plotly .modebar:hover {{
        opacity: 1 !important;
    }}

    /* =====================================================
       ESTADO DE PROCESAMIENTO
       Mantiene visible el componente nativo sin convertirlo en una
       tarjeta pesada ni añadir una falsa apariencia de modal.
       ===================================================== */
    div[data-testid="stStatusWidget"],
    details[data-testid="stStatusWidget"] {{
        width: 100% !important;
        margin: 0.75rem 0 1rem 0 !important;
        border: 1px solid #DCE3EC !important;
        border-left: 4px solid #E60023 !important;
        border-radius: 12px !important;
        background: #FFFFFF !important;
        box-shadow: none !important;
        overflow: hidden !important;
    }}

    div[data-testid="stStatusWidget"] summary,
    details[data-testid="stStatusWidget"] summary {{
        min-height: 48px !important;
        padding: 0.65rem 0.85rem !important;
        background: #FFFFFF !important;
        color: #1F2A44 !important;
        font-weight: 800 !important;
    }}

    div[data-testid="stStatusWidget"] [data-testid="stMarkdownContainer"],
    details[data-testid="stStatusWidget"] [data-testid="stMarkdownContainer"] {{
        color: #434C5E !important;
        font-size: 0.94rem !important;
        line-height: 1.45 !important;
    }}

    div[data-testid="stStatusWidget"] svg,
    details[data-testid="stStatusWidget"] svg {{
        color: #E60023 !important;
        fill: #E60023 !important;
    }}


    /* =====================================================
       OCULTAR FOOTER
       ===================================================== */
    footer {{
        visibility: hidden;
    }}

    /* =====================================================
       RESPONSIVE
       ===================================================== */
    @media (max-width: 1200px) {{
        .report-grid {{
            min-width: 920px;
        }}

        .block-container {{
            padding-top: 3rem;
            padding-left: 1.2rem;
            padding-right: 1.2rem;
        }}

        .top-header-bar-bg {{
            margin-left: -1.2rem;
            margin-right: -1.2rem;
        }}

        .brand-title {{
            font-size: 1.85rem;
        }}
    }}

    @media (max-width: 768px) {{
        .block-container {{
            padding-top: 2.8rem;
            padding-left: 0.9rem;
            padding-right: 0.9rem;
        }}

        .top-header-bar-bg {{
            margin-left: -0.9rem;
            margin-right: -0.9rem;
            height: 106px;
            margin-bottom: -82px;
        }}

        .hero-title {{
            font-size: 1.8rem;
        }}

        .brand-title {{
            font-size: 1.55rem;
        }}

        .brand-subtitle {{
            font-size: 0.9rem;
        }}
    }}
    

    /* =====================================================
       OVERRIDE FINAL - TABLAS EJECUTIVAS LIMPIAS
       Quita apariencia de Excel: sin bordes verticales, menos ruido,
       encabezados recuperados y números más legibles.
       ===================================================== */
    .report-table-card {{
        background: #FFFFFF !important;
        border: 1px solid #E7EAF0 !important;
        border-radius: 22px !important;
        padding: 1.05rem 1.1rem !important;
        box-shadow: 0 12px 28px rgba(15, 23, 42, 0.065) !important;
        margin-bottom: 1.15rem !important;
    }}

    .report-table-title {{
        font-size: 1.05rem !important;
        font-weight: 850 !important;
        color: #1F2A44 !important;
        margin: 0 0 0.85rem 0 !important;
        letter-spacing: 0.01em !important;
    }}

    .report-table-scroll {{
        border: 1px solid #EEF1F5 !important;
        border-radius: 16px !important;
        background: #FFFFFF !important;
        box-shadow: inset 0 0 0 1px rgba(255,255,255,0.55) !important;
        overflow-x: auto !important;
        overflow-y: auto !important;
    }}

    .report-cell {{
        border-left: none !important;
        border-right: none !important;
        border-top: none !important;
        border-bottom: 1px solid #EEF1F5 !important;
        background: #FFFFFF !important;
        min-height: 50px !important;
        padding: 0.74rem 0.72rem !important;
        font-size: 0.92rem !important;
        color: #1F2A44 !important;
    }}

    .report-value-cell {{
        justify-content: flex-end !important;
        text-align: right !important;
        color: #263244 !important;
        font-weight: 500 !important;
        font-variant-numeric: tabular-nums !important;
        letter-spacing: 0.01em !important;
    }}

    .report-label-cell,
    .report-sticky-cell,
    .report4-sticky-cell,
    .report-category-product-cell {{
        background: #FBFCFE !important;
        color: #1F2A44 !important;
        font-weight: 750 !important;
        justify-content: flex-start !important;
        text-align: left !important;
        box-shadow: 4px 0 10px rgba(15, 23, 42, 0.045) !important;
    }}

    .report-header,
    .report-header-neutral,
    .report-header-sticky,
    .report4-sticky-header,
    .report-category-header-sticky {{
        background: #1F2A44 !important;
        color: #FFFFFF !important;
        border-bottom: none !important;
        font-weight: 850 !important;
        letter-spacing: 0.02em !important;
        text-transform: uppercase !important;
    }}

    .report-header-actual {{
        background: #0B5A7A !important;
        color: #FFFFFF !important;
    }}

    .report-header-plan {{
        background: #D4A017 !important;
        color: #FFFFFF !important;
    }}

    .report-header-py {{
        background: #0B5A7A !important;
        color: #FFFFFF !important;
    }}

    .report-negative {{
        color: #C0392B !important;
        font-weight: 800 !important;
    }}

    .report-total .report-cell,
    .report4-total-cell {{
        background: #F3F6FA !important;
        color: #1F2A44 !important;
        font-weight: 850 !important;
        border-top: 1px solid #DCE3EC !important;
    }}

    .report-highlight .report-cell,
    .report4-highlight-cell {{
        background: #E8F3E6 !important;
        color: #16351F !important;
        font-weight: 850 !important;
        border-top: 1px solid #CDE8D0 !important;
    }}

    .report-total .report-label-cell,
    .report-total .report-sticky-cell,
    .report-total .report4-sticky-cell {{
        background: #F3F6FA !important;
    }}

    .report-highlight .report-label-cell,
    .report-highlight .report-sticky-cell,
    .report-highlight .report4-sticky-cell {{
        background: #DCEFD8 !important;
    }}

    .report-note {{
        color: #667085 !important;
        font-size: 0.93rem !important;
        margin: 0.2rem 0 0.85rem 0 !important;
    }}

    /* Reduce el peso visual de separadores de Streamlit */
    hr {{
        border: none !important;
        border-top: 1px solid #E9EDF3 !important;
        margin: 1.45rem 0 !important;
    }}

    /* Títulos más limpios, sin apariencia de documento numerado */
    h3 {{
        color: #1F2A44 !important;
        font-weight: 850 !important;
        letter-spacing: -0.01em !important;
    }}

    /* Botones de acción más compactos para filtros y construcción */
    div[data-testid="stButton"] > button {{
        min-height: 44px !important;
        border-radius: 14px !important;
    }}

    /* =====================================================
       DASHBOARD EJECUTIVO - PRIMERA ETAPA
       ===================================================== */
    
.dashboard-stage-card {{
        background: transparent !important;
        border: none !important;
        border-radius: 0 !important;
        padding: 0 !important;
        box-shadow: none !important;
        margin-top: 0.75rem !important;
        margin-bottom: 1rem !important;
        outline: none !important;
    }}

    .dashboard-stage-card,
    .dashboard-stage-card div,
    .dashboard-stage-card section,
    .dashboard-stage-card *,
    .dashboard-kpi-panel,
    .dashboard-kpi-panel *,
    .dashboard-main-title {{
        border: none !important;
        outline: none !important;
        box-shadow: none !important;
        background-image: none !important;
    }}

    .dashboard-main-title {{
        text-align: center;
        color: #E60023;
        font-size: 1.7rem;
        font-weight: 900;
        letter-spacing: 0.2px;
        margin: 0 0 1.15rem 0;
        padding: 0;
        background: transparent !important;
        border: 0 !important;
        box-shadow: none !important;
        outline: none !important;
    }}
    .dashboard-header-grid {{
        display: grid;
        grid-template-columns: 1fr 1fr 1fr;
        gap: 1.2rem;
        align-items: center;
        margin-bottom: 0.85rem;
    }}
    .dashboard-period-box {{
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 0.85rem;
        min-height: 48px;
    }}
    .dashboard-period-box-left {{
        justify-content: flex-start;
        padding-left: 2.5rem;
    }}
    .dashboard-period-label {{
        color: #E60023;
        font-size: 1.03rem;
        font-weight: 900;
        line-height: 1.25;
        text-align: right;
    }}
    .dashboard-period-value {{
        color: #0F172A;
        font-size: 1.05rem;
        font-weight: 900;
        line-height: 1.25;
    }}
    .dashboard-currency-label {{
        font-size: 0.78rem;
        color: #0F172A;
        font-weight: 800;
        text-align: left;
        margin-left: 2.5rem;
        margin-bottom: 0.15rem;
    }}
    .dashboard-kpi-grid {{
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 1.35rem;
        align-items: start;
    }}
    .dashboard-kpi-panel {{
        background: transparent;
        border: none !important;
        border-radius: 0;
        overflow: visible;
        box-shadow: none !important;
    }}
    .dashboard-kpi-panel-title {{
        width: 190px;
        margin: 0.55rem auto 0.7rem auto;
        padding: 0.15rem 0.75rem;
        border: none !important;
        color: #111111;
        background: transparent;
        font-size: 0.98rem;
        line-height: 1.15;
        font-weight: 900;
        text-align: center;
        box-shadow: none !important;
        outline: none !important;
    }}
    .dashboard-table-wrap {{
        width: 100%;
        overflow-x: auto;
    }}
    .dashboard-kpi-table {{
        width: 100%;
        border-collapse: collapse;
        table-layout: fixed;
        font-size: 0.82rem;
        font-variant-numeric: tabular-nums;
    }}
    .dashboard-kpi-table th {{
        background: #FFFFFF;
        color: #111827;
        font-weight: 900;
        border-bottom: 2px solid #111111;
        padding: 0.35rem 0.35rem;
        text-align: right;
        white-space: nowrap;
    }}
    .dashboard-kpi-table th:first-child {{
        text-align: center;
        width: 20%;
    }}
    .dashboard-kpi-table td {{
        padding: 0.36rem 0.35rem;
        border-bottom: 1px solid #E7EAF0;
        text-align: right;
        color: #111827;
        font-weight: 700;
        white-space: nowrap;
    }}
    .dashboard-kpi-table td:first-child {{
        text-align: center;
        font-weight: 900;
        color: #111827;
    }}
    .dashboard-row-gsnr td,
    .dashboard-row-bts td {{
        background: #E5E7EB;
    }}
    .dashboard-row-achievement td {{
        background: #FFFFFF;
    }}
    .dashboard-negative {{
        color: #C0392B !important;
        font-weight: 900 !important;
    }}
    .dashboard-neutral {{
        color: #111827;
    }}
    .dashboard-muted-cell {{
        color: #8A94A6 !important;
        font-weight: 600 !important;
    }}
    .dashboard-lock-box {{
        background: #FFFFFF;
        border: 1px solid #E7EAF0;
        border-left: 5px solid #E60023;
        border-radius: 18px;
        padding: 1rem 1.15rem;
        margin-top: 0.75rem;
        margin-bottom: 1rem;
        box-shadow: 0 8px 20px rgba(15, 23, 42, 0.05);
    }}
    .dashboard-lock-title {{
        color: #1F2A44;
        font-size: 1rem;
        font-weight: 900;
        margin-bottom: 0.35rem;
    }}
    .dashboard-lock-text {{
        color: #4B5563;
        font-size: 0.94rem;
        line-height: 1.55;
    }}
    @media (max-width: 1100px) {{
        .dashboard-header-grid,
        .dashboard-kpi-grid {{
            grid-template-columns: 1fr;
        }}
        .dashboard-period-box-left {{
            justify-content: center;
            padding-left: 0;
        }}
        .dashboard-currency-label {{
            margin-left: 0;
            text-align: center;
        }}
    }}



    /* =====================================================
       FIX DEFINITIVO - QUITAR RECTÁNGULO DEL TÍTULO
       ===================================================== */
    .dashboard-main-title {{
        background: transparent !important;
        border: none !important;
        outline: none !important;
        box-shadow: none !important;
    }}


</style>
    """

def _clean_info_box_text(text: str) -> tuple[str, str]:
    """
    Limpia texto con HTML simple y separa título/cuerpo para evitar
    que se vean etiquetas como </b><br> en pantalla.
    """
    raw_text = str(text or "").strip()

    title_match = re.search(
        r"<(?:b|strong)>(.*?)</(?:b|strong)>\s*<br\s*/?>?",
        raw_text,
        flags=re.IGNORECASE | re.DOTALL,
    )

    if title_match:
        title = re.sub(r"\s+", " ", title_match.group(1)).strip()
        body = raw_text[title_match.end():]
    else:
        normalized = re.sub(r"<br\s*/?>", "\n", raw_text, flags=re.IGNORECASE)
        normalized = re.sub(r"</?(?:b|strong|code)>", "", normalized, flags=re.IGNORECASE)
        lines = [line.strip() for line in normalized.splitlines() if line.strip()]

        if not lines:
            return "", ""

        title = lines[0]
        body = " ".join(lines[1:]) if len(lines) > 1 else ""

    body = re.sub(r"<br\s*/?>", " ", body, flags=re.IGNORECASE)
    body = re.sub(r"</?(?:b|strong|code)>", "", body, flags=re.IGNORECASE)
    body = re.sub(r"\s+", " ", body).strip()

    return title, body

def build_hero_section() -> str:
    """
    Construye el bloque principal de bienvenida.
    """
    return f"""
    <div class="hero-box">
        <div class="hero-title-row">
            <div class="hero-logo-box"></div>
            <div class="hero-title">{config.MAIN_TITLE}</div>
        </div>
        <div class="main-subtitle">{config.SUBTITLE}</div>
        <div class="hero-text">{config.WELCOME_MESSAGE}</div>
    </div>
    """

def build_info_card(
    title: str,
    value: str,
    description: str = "",
    icon_override: str | None = None,
    color_override: str | None = None,
) -> str:
    """
    Genera una tarjeta ejecutiva con icono, usando el mismo lenguaje visual
    que Base MTD y Visión general.

    icon_override y color_override son opcionales para casos específicos,
    sin alterar el comportamiento de las tarjetas existentes.
    """
    title_text = str(title or "").strip().lower()

    if "periodo" in title_text or "fecha" in title_text:
        icon = "◷"
        color = "blue"
    elif "plan" in title_text or "regla" in title_text:
        icon = "↗"
        color = "orange"
    elif "cruce" in title_text or "código" in title_text or "codigo" in title_text:
        icon = "⛓"
        color = "green"
    elif "bloque" in title_text or "orden" in title_text or "segment" in title_text:
        icon = "▦"
        color = "blue"
    else:
        icon = "•"
        color = "blue"

    if icon_override is not None and str(icon_override).strip():
        icon = str(icon_override).strip()

    if color_override is not None and str(color_override).strip():
        color = str(color_override).strip().lower()

    return build_base_mtd_kpi_card(
        title=title.upper(),
        value=value,
        description=description,
        icon=icon,
        color=color,
    )

def build_info_box(text: str) -> str:
    """
    Construye una caja informativa.
    """
    title, body = _clean_info_box_text(text)

    if title and body:
        content = (
            f'<div class="info-box-title">{title}</div>'
            f'<div class="info-box-body">{body}</div>'
        )
    elif title:
        content = f'<div class="info-box-title">{title}</div>'
    else:
        content = f'<div class="info-box-body">{body}</div>'

    return f"""
    <div class="info-box">
        {content}
    </div>
    """

def build_sidebar_box(text: str) -> str:
    """
    Construye una caja visual para sidebar.
    """
    return f"""
    <div class="sidebar-box">
        {text}
    </div>
    """

def build_currency_box(title: str, subtitle: str = "") -> str:
    """
    Construye una caja visual para el bloque de moneda en sidebar.
    """
    subtitle_html = (
        f'<div class="currency-box-subtitle">{subtitle}</div>'
        if str(subtitle).strip()
        else ""
    )

    return f"""
    <div class="currency-box">
        <div class="currency-box-title">{title}</div>
        {subtitle_html}
    </div>
    """

def build_base_mtd_kpi_card(
    title: str,
    value: str,
    description: str = "",
    icon: str = "$",
    color: str = "blue",
) -> str:
    """
    Tarjeta KPI ejecutiva para la vista superior de Base MTD.
    """
    safe_color = str(color or "blue").strip().lower()
    if safe_color not in {"blue", "orange", "green"}:
        safe_color = "blue"

    return f"""
    <div class="base-mtd-kpi-card">
        <div class="base-mtd-kpi-icon base-mtd-kpi-icon-{safe_color}">{icon}</div>
        <div class="base-mtd-kpi-body">
            <div class="base-mtd-kpi-title">{title}</div>
            <div class="base-mtd-kpi-value">{value}</div>
            <div class="base-mtd-kpi-description">{description}</div>
        </div>
    </div>
    """


def build_dashboard_css_html() -> str:
    """
    Estilos reutilizables del Dashboard ejecutivo.

    Reglas visuales:
    - No encierra Mexico Dashboard 2026.
    - No encierra Sales Month / Sales YTD.
    - Sí encierra títulos de reportes internos como Sales by Channel Monthly/YTD.
    - Mantiene columnas alineadas con table-layout fixed y colgroup.
    - Usa doble línea bajo encabezados y sobre Total Mexico.
    - Total Mexico lleva franja verde.
    """
    return """
<style>
.dashboard-stage-card {
    background: transparent !important;
    border: none !important;
    border-radius: 0 !important;
    padding: 0 !important;
    box-shadow: none !important;
    margin-top: 0.75rem !important;
    margin-bottom: 1rem !important;
    outline: none !important;
}

.dashboard-stage-card,
.dashboard-main-title,
.dashboard-main-title-box,
.dashboard-kpi-panel,
.dashboard-kpi-panel-title {
    box-shadow: none !important;
    outline: none !important;
}

.dashboard-main-title-box {
    border: none !important;
    padding: 0 !important;
    text-align: center !important;
    margin-bottom: 1.85rem !important;
    background: transparent !important;
}

.dashboard-main-title {
    color: #E60023 !important;
    font-size: 1.85rem !important;
    line-height: 1.1 !important;
    font-weight: 900 !important;
    letter-spacing: 0.15px !important;
    text-align: center !important;
    background: transparent !important;
    border: none !important;
}

.dashboard-header-row {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 2rem;
    align-items: start;
    margin-bottom: 0.45rem;
}

.dashboard-period-left {
    display: flex;
    align-items: flex-start;
    justify-content: flex-start;
    gap: 1.2rem;
    padding-left: 5.5rem;
}

.dashboard-period-right {
    display: flex;
    align-items: flex-start;
    justify-content: center;
    gap: 0.7rem;
}

.dashboard-period-label {
    color: #E60023;
    font-weight: 900;
    font-size: 1.08rem;
    line-height: 1.35;
    text-align: right;
}

.dashboard-period-value {
    color: #000000;
    font-weight: 850;
    font-size: 1.08rem;
    line-height: 1.35;
}

.dashboard-currency-label {
    margin-top: 0.45rem;
    margin-left: 4.1rem;
    color: #000000;
    font-weight: 800;
    font-size: 0.86rem;
}

.dashboard-kpi-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1.15rem;
    margin-top: 0.25rem;
}

.dashboard-kpi-panel {
    background: transparent !important;
    border: none !important;
}

.dashboard-kpi-panel-title {
    border: none !important;
    text-align: center;
    color: #000000;
    background: transparent !important;
    font-size: 1.05rem;
    font-weight: 900;
    padding: 0.35rem 0.65rem;
    margin-bottom: 0.18rem;
}

.dashboard-kpi-table-wrap,
.dashboard-compact-table-wrap {
    width: 100%;
    overflow-x: auto;
}

.dashboard-kpi-table,
.dashboard-compact-table {
    width: 100%;
    border-collapse: collapse;
    table-layout: fixed;
    font-variant-numeric: tabular-nums;
}

.dashboard-kpi-table th {
    background: #FFFFFF;
    color: #000000;
    font-size: 0.74rem;
    font-weight: 900;
    text-align: center;
    padding: 0.23rem 0.24rem;
    border-bottom: 2px solid #111111;
    white-space: nowrap;
}

.dashboard-kpi-table th:first-child {
    width: 28%;
}

.dashboard-kpi-table td {
    color: #000000;
    font-size: 0.82rem;
    font-weight: 650;
    text-align: right;
    padding: 0.31rem 0.34rem;
    border-bottom: 1px solid rgba(0, 0, 0, 0.06);
    white-space: nowrap;
}

.dashboard-kpi-name {
    text-align: center !important;
    color: #000000 !important;
    font-weight: 900 !important;
}

.dashboard-gsnr-row td {
    background: #D9DDE3 !important;
}

.dashboard-achievement-row td {
    background: #FFFFFF !important;
    font-weight: 800 !important;
}

.dashboard-bts-row td {
    background: #F1F3F5 !important;
}

.dashboard-kpi-negative,
.dashboard-compact-table .dashboard-kpi-negative {
    color: #C0392B !important;
    font-weight: 900 !important;
}

.dashboard-kpi-neutral {
    color: #000000 !important;
}

.dashboard-kpi-muted {
    color: #000000 !important;
}

.dashboard-report-section {
    margin-top: 1.65rem;
}

.dashboard-report-pair-grid {
    display: grid;
    grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
    gap: 1.15rem;
    align-items: start;
}

.dashboard-compact-block {
    width: 100%;
    min-width: 0;
}

.dashboard-compact-title-box {
    display: inline-block;
    width: auto;
    max-width: max-content;
    color: #000000;
    background: #D9DDE3;
    border: 1.5px solid #111111;
    font-size: 1.04rem;
    font-weight: 900;
    text-align: center;
    line-height: 1.15;
    padding: 0.18rem 0.42rem;
    margin: 0 0 0.70rem 0;
    box-sizing: border-box;
}

.dashboard-compact-table {
    font-size: 0.88rem;
    border-collapse: separate;
    border-spacing: 0;
}

.dashboard-compact-table .dashboard-col-channel {
    width: 24%;
}

.dashboard-compact-table .dashboard-col-num {
    width: 10.85%;
}

.dashboard-compact-table .dashboard-col-pct {
    width: 10.85%;
}

.dashboard-compact-table th {
    background: #FFFFFF;
    color: #000000;
    font-size: 0.82rem;
    font-weight: 900;
    text-align: right;
    padding: 0.25rem 0.24rem;
    border-bottom: 4px double #111111 !important;
    white-space: nowrap;
    vertical-align: bottom;
}

.dashboard-compact-table th:first-child {
    text-align: center;
}

.dashboard-compact-table thead tr {
    border-bottom: 4px double #111111 !important;
}

.dashboard-compact-table tbody tr:first-child td {
    border-top: 0 !important;
}

.dashboard-compact-table td {
    color: #000000;
    font-size: 0.86rem;
    font-weight: 720;
    text-align: right;
    padding: 0.30rem 0.28rem;
    border-bottom: none;
    white-space: nowrap;
    vertical-align: middle;
}

.dashboard-compact-label {
    text-align: left !important;
    font-weight: 850 !important;
    color: #000000 !important;
    overflow: hidden;
    text-overflow: ellipsis;
}

.dashboard-compact-total td {
    border-top: 4px double #111111 !important;
    font-weight: 900 !important;
    background: #F1F3F5 !important;
}

.dashboard-compact-total .dashboard-compact-label {
    text-align: center !important;
}

.dashboard-ellipsis td {
    text-align: center !important;
    color: #1F2A44 !important;
    font-weight: 900 !important;
    letter-spacing: 0.16em;
    border-bottom: none !important;
    padding: 0.02rem 0 !important;
    background: transparent !important;
}

.dashboard-compact-grand-total td {
    border-top: 4px double #111111 !important;
    font-weight: 950 !important;
    background: #E5E7EB !important;
}

.dashboard-clients-block .dashboard-compact-title-box {
    background: #D9DDE3 !important;
}

.dashboard-clients-table {
    width: 100% !important;
    table-layout: fixed !important;
    border-collapse: separate !important;
    border-spacing: 0 !important;
    font-size: 0.82rem;
}

/* 26% para el nombre y 10.571% para cada una de las siete métricas.
   El mismo colgroup gobierna encabezados y cuerpo, evitando desplazamientos. */
.dashboard-clients-table .dashboard-col-client-name {
    width: 26% !important;
}

.dashboard-clients-table .dashboard-col-num,
.dashboard-clients-table .dashboard-col-pct {
    width: 10.5714% !important;
}

.dashboard-clients-table th,
.dashboard-clients-table td {
    box-sizing: border-box !important;
    min-width: 0 !important;
    overflow: hidden !important;
    text-overflow: ellipsis !important;
    white-space: nowrap !important;
}

.dashboard-clients-table th {
    font-size: 0.74rem !important;
    padding: 0.25rem 0.18rem !important;
    text-align: right !important;
}

.dashboard-clients-table th:first-child {
    text-align: center !important;
}

.dashboard-clients-table td {
    font-size: 0.78rem !important;
    padding: 0.27rem 0.18rem !important;
    text-align: right !important;
}

.dashboard-clients-table td:first-child {
    text-align: left !important;
}

.dashboard-client-name {
    max-width: 0 !important;
    overflow: hidden !important;
    text-overflow: ellipsis !important;
    white-space: nowrap !important;
}

.dashboard-compact-code {
    color: #1F2A44 !important;
    font-weight: 820 !important;
    text-align: left !important;
    overflow: hidden;
    text-overflow: ellipsis;
}

.dashboard-lock-box {
    background: #FFFFFF;
    border: 1px solid #E7EAF0;
    border-left: 5px solid #E60023;
    border-radius: 18px;
    padding: 1rem 1.15rem;
    box-shadow: 0 8px 20px rgba(15, 23, 42, 0.05);
    margin-top: 0.9rem;
}

.dashboard-lock-title {
    font-size: 1.05rem;
    font-weight: 900;
    color: #1F2A44;
    margin-bottom: 0.45rem;
}

.dashboard-lock-text {
    font-size: 0.95rem;
    color: #434C5E;
    line-height: 1.65;
}

@media (max-width: 1100px) {
    .dashboard-header-row,
    .dashboard-kpi-grid,
    .dashboard-report-pair-grid {
        grid-template-columns: 1fr;
    }

    .dashboard-period-left {
        padding-left: 0;
        justify-content: center;
    }

    .dashboard-currency-label {
        margin-left: 0;
        text-align: center;
    }
}
</style>
"""


# =========================================================
# PANTALLA DE INICIO CORPORATIVA
# =========================================================
def build_home_start_css() -> str:
    """CSS exclusivo para reproducir la portada corporativa del boceto."""
    return """
    <style>
    .home-carousel {position:relative;width:100%;overflow:hidden;border-radius:18px;border:1px solid #edf0f4;background:#fff;box-shadow:0 8px 24px rgba(15,23,42,.045);margin:.35rem 0 .85rem 0;isolation:isolate}
    .home-carousel input {position:absolute;opacity:0;pointer-events:none}
    .home-carousel-viewport {position:relative;width:100%;aspect-ratio:1130/297;overflow:hidden;background:#f8fafc}
    .home-carousel-slide {position:absolute;inset:0;opacity:0;transform:translateX(1.5%);transition:opacity .55s ease,transform .55s ease;pointer-events:none}
    .home-carousel-slide img {display:block;width:100%;height:100%;object-fit:cover;object-position:center center;image-rendering:auto}
    #home-slide-1:checked ~ .home-carousel-viewport .home-slide-1,
    #home-slide-2:checked ~ .home-carousel-viewport .home-slide-2 {opacity:1;transform:translateX(0);pointer-events:auto}
    .home-carousel-arrow {position:absolute;top:50%;z-index:8;width:42px;height:42px;margin-top:-21px;border-radius:50%;display:none;align-items:center;justify-content:center;background:rgba(255,255,255,.94);color:#111827;font-size:1.55rem;font-weight:900;line-height:1;cursor:pointer;box-shadow:0 8px 20px rgba(15,23,42,.18);user-select:none;transition:transform .18s ease,background .18s ease}
    .home-carousel-arrow:hover {transform:scale(1.06);background:#fff}
    .home-carousel-arrow-left {left:14px}
    .home-carousel-arrow-right {right:14px}
    #home-slide-1:checked ~ .home-carousel-viewport .arrow-from-1,
    #home-slide-2:checked ~ .home-carousel-viewport .arrow-from-2 {display:flex}
    .home-carousel-dots {position:absolute;left:50%;bottom:13px;z-index:9;display:flex;gap:9px;transform:translateX(-50%)}
    .home-carousel-dot {width:12px;height:12px;border-radius:50%;background:rgba(255,255,255,.72);border:2px solid rgba(255,255,255,.95);cursor:pointer;box-shadow:0 2px 8px rgba(15,23,42,.18)}
    #home-slide-1:checked ~ .home-carousel-viewport .dot-1,
    #home-slide-2:checked ~ .home-carousel-viewport .dot-2 {background:#f20032;border-color:#fff}
    .home-section-heading {display:flex;align-items:stretch;gap:.85rem;margin:.15rem 0 .15rem 0}
    .home-section-heading::before {content:"";display:block;width:4px;min-width:4px;border-radius:99px;background:#f20032}
    .home-section-title {margin:0;color:#111d33;font-size:1.45rem;font-weight:850;line-height:1.2}
    .home-section-subtitle {margin:.18rem 0 1.15rem 1.05rem;color:#536174;font-size:.96rem;line-height:1.45}
    .home-module-grid {display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:.95rem;margin-bottom:1.35rem}
    .home-module-card {min-height:142px;display:flex;align-items:center;gap:1rem;padding:1.15rem 1.05rem;border-radius:18px;border:1px solid #e6eaf0;background:linear-gradient(180deg,#fff 0%,#fefefe 100%);box-shadow:0 10px 24px rgba(15,23,42,.055);transition:transform .18s ease,box-shadow .18s ease;box-sizing:border-box}
    .home-module-card:hover {transform:translateY(-2px);box-shadow:0 14px 28px rgba(15,23,42,.085)}
    .home-module-icon {width:68px;height:68px;min-width:68px;border-radius:50%;display:flex;align-items:center;justify-content:center;background:linear-gradient(145deg,#fff,#f4f5f7);box-shadow:0 7px 16px rgba(15,23,42,.08);font-size:2.15rem;line-height:1}
    .home-module-content {min-width:0}
    .home-module-title {color:#111d33;font-size:1.02rem;font-weight:850;line-height:1.25;margin:0 0 .45rem 0}
    .home-module-description {color:#405069;font-size:.88rem;line-height:1.48;margin:0}
    .home-trust-strip {display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:0;padding:1.25rem 1.35rem;border-radius:18px;background:linear-gradient(100deg,#fff7f7 0%,#fffafa 52%,#fff5f5 100%);border:1px solid #fde9ec;box-shadow:0 8px 22px rgba(230,0,35,.035)}
    .home-trust-item {display:flex;align-items:center;gap:1rem;padding:.2rem 1.15rem;min-height:86px;box-sizing:border-box}
    .home-trust-item + .home-trust-item {border-left:1px solid #f3d5da}
    .home-trust-icon {width:58px;height:58px;min-width:58px;border-radius:50%;background:#fff;display:flex;align-items:center;justify-content:center;color:#f20032;font-size:1.75rem;font-weight:900;box-shadow:0 7px 18px rgba(15,23,42,.07)}
    .home-trust-title {color:#111d33;font-weight:850;font-size:1rem;margin-bottom:.35rem}
    .home-trust-description {color:#405069;font-size:.88rem;line-height:1.48}
    .project-status-label {color:#fff!important;font-size:.88rem;line-height:1.45;margin-bottom:.6rem}
    .project-progress-row {display:flex;align-items:center;gap:.65rem}
    .project-progress-track {height:12px;flex:1;overflow:hidden;border-radius:99px;background:#191919}
    .project-progress-fill {width:85%;height:100%;border-radius:99px;background:#f20032}
    .project-progress-value {color:#fff;font-weight:800;font-size:.9rem}
    @media (max-width:1250px){.home-module-grid{grid-template-columns:repeat(2,minmax(0,1fr))}}
    @media (max-width:800px){.home-module-grid{grid-template-columns:1fr}.home-trust-strip{grid-template-columns:1fr}.home-trust-item + .home-trust-item{border-left:0;border-top:1px solid #f3d5da}}
    </style>
    """


def build_home_carousel(image_paths: list[str]) -> str:
    """Construye un carrusel corporativo CSS, sin JavaScript ni dependencias."""
    valid_images: list[str] = []

    for image_path in list(image_paths or []):
        image_base64 = image_to_base64(image_path)
        if image_base64:
            suffix = Path(image_path).suffix.lower()
            mime = "image/jpeg" if suffix in {".jpg", ".jpeg"} else "image/png"
            valid_images.append(f"data:{mime};base64,{image_base64}")

    if not valid_images:
        return (
            '<div class="home-carousel" style="padding:2rem">'
            '<b>No se encontraron los banners corporativos.</b></div>'
        )

    if len(valid_images) == 1:
        return (
            '<div class="home-carousel">'
            '<div class="home-carousel-viewport">'
            f'<div class="home-carousel-slide" style="opacity:1;transform:none">'
            f'<img src="{valid_images[0]}" alt="ACCO Brands Reportes Corporativos"></div>'
            '</div></div>'
        )

    first_image, second_image = valid_images[:2]

    return (
        '<div class="home-carousel">'
        '<input type="radio" name="home-carousel" id="home-slide-1" checked>'
        '<input type="radio" name="home-carousel" id="home-slide-2">'
        '<div class="home-carousel-viewport">'
        f'<div class="home-carousel-slide home-slide-1"><img src="{first_image}" alt="Banner corporativo ACCO Brands 1"></div>'
        f'<div class="home-carousel-slide home-slide-2"><img src="{second_image}" alt="Banner corporativo ACCO Brands 2"></div>'
        '<label class="home-carousel-arrow home-carousel-arrow-left arrow-from-1" for="home-slide-2" aria-label="Banner anterior">‹</label>'
        '<label class="home-carousel-arrow home-carousel-arrow-right arrow-from-1" for="home-slide-2" aria-label="Banner siguiente">›</label>'
        '<label class="home-carousel-arrow home-carousel-arrow-left arrow-from-2" for="home-slide-1" aria-label="Banner anterior">‹</label>'
        '<label class="home-carousel-arrow home-carousel-arrow-right arrow-from-2" for="home-slide-1" aria-label="Banner siguiente">›</label>'
        '<div class="home-carousel-dots">'
        '<label class="home-carousel-dot dot-1" for="home-slide-1" aria-label="Mostrar banner 1"></label>'
        '<label class="home-carousel-dot dot-2" for="home-slide-2" aria-label="Mostrar banner 2"></label>'
        '</div></div></div>'
    )


def build_home_modules_html(modules: list[dict], title: str, subtitle: str) -> str:
    cards = []
    for module in modules:
        cards.append(
            f'<div class="home-module-card">'
            f'<div class="home-module-icon">{module.get("icon", "•")}</div>'
            f'<div class="home-module-content">'
            f'<div class="home-module-title">{module.get("title", "")}</div>'
            f'<div class="home-module-description">{module.get("description", "")}</div>'
            f'</div></div>'
        )
    return (
        f'<div class="home-section-heading"><div><div class="home-section-title">{title}</div></div></div>'
        f'<div class="home-section-subtitle">{subtitle}</div>'
        f'<div class="home-module-grid">{"".join(cards)}</div>'
    )


def build_home_trust_strip_html(items: list[dict]) -> str:
    blocks = []
    for item in items:
        blocks.append(
            f'<div class="home-trust-item">'
            f'<div class="home-trust-icon">{item.get("icon", "•")}</div>'
            f'<div><div class="home-trust-title">{item.get("title", "")}</div>'
            f'<div class="home-trust-description">{item.get("description", "")}</div></div>'
            f'</div>'
        )
    return f'<div class="home-trust-strip">{"".join(blocks)}</div>'


def build_project_progress_html() -> str:
    return (
        '<div class="project-status-label">Etapa actual: Refinamiento visual</div>'
        '<div class="project-progress-row">'
        '<div class="project-progress-track"><div class="project-progress-fill"></div></div>'
        '<div class="project-progress-value">85%</div></div>'
    )


def build_dashboard_download_anchor() -> str:
    """Marcador visual reutilizable para la zona de descarga del Dashboard."""
    return '<div class="dashboard-download-wrap"></div>'

# =========================================================
# INTEGRACIÓN FORECAST - EXTENSIÓN DE ESTILOS
# =========================================================
_build_global_css_base = build_global_css

def build_global_css() -> str:
    """
    Conserva todos los estilos originales e inserta las reglas Forecast
    dentro del mismo bloque <style>, evitando que Streamlit muestre CSS
    como texto visible en la página.
    """
    css = _build_global_css_base()

    forecast_rules = f"""
    /* Forecast: colores según las tablas Excel de referencia */
    .fcst-header-client {{
        background: {getattr(config, "COLOR_HEADER_FCST_CLIENT", "#E83E62")} !important;
        color: #FFFFFF !important;
    }}

    /* En TODOS los reportes, la columna Fcst usa el mismo verde que sus variaciones. */
    .report-header-fcst {{
        background: {getattr(config, "COLOR_HEADER_VAR_FCST", "#34A853")} !important;
        color: #FFFFFF !important;
    }}

    .fcst-header-sku {{
        background: {getattr(config, "COLOR_HEADER_FCST_SKU", "#FFC34D")} !important;
        color: #FFFFFF !important;
    }}

    /* Acotaciones de Base MTD: Forecast Cliente rosa / Forecast SKU amarillo claro */
    .chip-fcst-client {{
        background: {getattr(config, "COLOR_HEADER_FCST_CLIENT", "#E83E62")} !important;
        color: #FFFFFF !important;
    }}

    .chip-fcst-sku {{
        background: {getattr(config, "COLOR_HEADER_FCST_SKU", "#FFC34D")} !important;
        color: #1F2A44 !important;
    }}

    .base-mtd-kpi-icon-pink {{
        background: linear-gradient(135deg, #E83E62 0%, #F36A86 100%) !important;
    }}

    .var-header-plan,
    .report-header-var-plan {{
        background: {getattr(config, "COLOR_HEADER_VAR_PLAN", "#F4B400")} !important;
        color: #FFFFFF !important;
    }}

    .var-header-fcst,
    .report-header-var-fcst {{
        background: {getattr(config, "COLOR_HEADER_VAR_FCST", "#34A853")} !important;
        color: #FFFFFF !important;
    }}

    .var-header-py,
    .report-header-var-py {{
        background: {getattr(config, "COLOR_HEADER_VAR_PY", "#0B5A7A")} !important;
        color: #FFFFFF !important;
    }}



    /* Base MTD: cada variación usa el color de su fuente/acotación. */
    .var-header-plan-client {{ background: #ED7D31 !important; color:#FFFFFF !important; }}
    .var-header-plan-sku {{ background: #2E7D32 !important; color:#FFFFFF !important; }}
    .var-header-fcst-client {{ background: #E83E62 !important; color:#FFFFFF !important; }}
    .var-header-fcst-sku {{ background: #FFC34D !important; color:#1F2A44 !important; }}

    /* Category: ningún texto puede invadir columnas vecinas. */
    .report-text-clamped,
    .report-category-product-cell,
    .report-category-grid .report-cell {{
        min-width: 0 !important;
        max-width: 100% !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
        white-space: nowrap !important;
        word-break: normal !important;
    }}

    .report-category-grid .report-header,
    .report-grid-dynamic .report-header {{
        min-width: 0 !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
        white-space: nowrap !important;
    }}

        /* Nuevos tamaños: 1 dimensión + 10 métricas */
    .h-table-11 {{
        grid-template-columns: 1.20fr repeat(10, minmax(105px, 1fr));
        min-width: 1260px;
    }}

    .report-grid-11-metrics {{
        grid-template-columns: 2.15fr repeat(10, minmax(105px, 1fr));
        min-width: 1420px;
    }}

    /* Ranking: 2 dimensiones + 10 métricas */
    .report-grid-12 {{
        grid-template-columns: 1.65fr 2.05fr repeat(10, minmax(105px, 1fr));
        min-width: 1640px;
    }}

    /* Category: 4 dimensiones + 10 métricas */
    .report-grid-14 {{
        grid-template-columns:
            1.45fr 1.20fr 1.90fr 2.15fr
            repeat(10, minmax(105px, 1fr));
        min-width: 2020px;
    }}
    """

    closing_tag = "</style>"
    closing_index = css.rfind(closing_tag)

    if closing_index == -1:
        # Salvaguarda: si por alguna razón el CSS original no contiene cierre,
        # se devuelve un único bloque válido.
        return f"<style>{forecast_rules}</style>" + css

    return (
        css[:closing_index]
        + forecast_rules
        + "\n"
        + css[closing_index:]
    )


# =========================================================
# BASE MTD - SOPORTE DE KPI FORECAST
# =========================================================
def build_base_mtd_kpi_card(
    title: str,
    value: str,
    description: str = "",
    icon: str = "$",
    color: str = "blue",
) -> str:
    """
    Tarjeta KPI ejecutiva para Base MTD.
    Conserva blue/orange/green y añade pink para Forecast.
    """
    safe_color = str(color or "blue").strip().lower()
    if safe_color not in {"blue", "orange", "green", "pink"}:
        safe_color = "blue"

    return f"""
    <div class="base-mtd-kpi-card">
        <div class="base-mtd-kpi-icon base-mtd-kpi-icon-{safe_color}">{icon}</div>
        <div class="base-mtd-kpi-body">
            <div class="base-mtd-kpi-title">{title}</div>
            <div class="base-mtd-kpi-value">{value}</div>
            <div class="base-mtd-kpi-description">{description}</div>
        </div>
    </div>
    """

# =========================================================
# DASHBOARD CON FORECAST - ANCHO Y SCROLL
# =========================================================
_build_dashboard_css_html_before_forecast = build_dashboard_css_html

def build_dashboard_css_html() -> str:
    """
    Conserva todo el CSS original del Dashboard y agrega únicamente
    el ancho necesario para imprimir Forecast y sus variaciones.
    """
    css = _build_dashboard_css_html_before_forecast()

    forecast_dashboard_rules = """
    .dashboard-forecast-table-wrap {
        overflow-x: auto !important;
        overflow-y: hidden !important;
        width: 100% !important;
        max-width: 100% !important;
    }

    .dashboard-forecast-table {
        min-width: 1280px !important;
        width: 100% !important;
        table-layout: fixed !important;
    }

    .dashboard-forecast-table th,
    .dashboard-forecast-table td {
        white-space: nowrap !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
        min-width: 88px !important;
    }

    .dashboard-forecast-table th:first-child,
    .dashboard-forecast-table td:first-child {
        min-width: 210px !important;
        width: 210px !important;
        text-align: left !important;
    }

    .dashboard-kpi-grid {
        align-items: start !important;
    }
    """

    closing_tag = "</style>"
    closing_index = css.rfind(closing_tag)

    if closing_index == -1:
        return css + f"<style>{forecast_dashboard_rules}</style>"

    return (
        css[:closing_index]
        + forecast_dashboard_rules
        + css[closing_index:]
    )

# =========================================================
# DASHBOARD SIN DESPLAZAMIENTO HORIZONTAL
# =========================================================
_build_dashboard_css_html_before_no_scroll = build_dashboard_css_html

def build_dashboard_css_html() -> str:
    """
    Conserva todos los estilos anteriores y aplica al Dashboard final
    una distribución vertical de ancho completo, sin barras horizontales.
    """
    css = _build_dashboard_css_html_before_no_scroll()

    no_scroll_rules = """
    /* El Dashboard completo permanece dentro del ancho visible. */
    .dashboard-no-scroll-layout {
        width: 100% !important;
        max-width: 100% !important;
        overflow-x: hidden !important;
        box-sizing: border-box !important;
    }

    /* Sales Month y Sales YTD: uno debajo del otro. */
    .dashboard-no-scroll-layout .dashboard-kpi-grid {
        display: grid !important;
        grid-template-columns: minmax(0, 1fr) !important;
        gap: 1.35rem !important;
        width: 100% !important;
        max-width: 100% !important;
    }

    /* Todos los pares Monthly/YTD pasan a distribución vertical. */
    .dashboard-no-scroll-layout .dashboard-report-pair-grid {
        display: grid !important;
        grid-template-columns: minmax(0, 1fr) !important;
        gap: 1.35rem !important;
        width: 100% !important;
        max-width: 100% !important;
    }

    .dashboard-no-scroll-layout .dashboard-report-section,
    .dashboard-no-scroll-layout .dashboard-compact-block,
    .dashboard-no-scroll-layout .dashboard-kpi-panel {
        width: 100% !important;
        max-width: 100% !important;
        min-width: 0 !important;
        box-sizing: border-box !important;
    }

    /* Quita las barras horizontales internas. */
    .dashboard-no-scroll-layout .dashboard-forecast-table-wrap,
    .dashboard-no-scroll-layout .dashboard-compact-table-wrap,
    .dashboard-no-scroll-layout .dashboard-kpi-table-wrap,
    .dashboard-no-scroll-layout .dashboard-clients-table-wrap,
    .dashboard-no-scroll-layout .dashboard-table-wrap {
        width: 100% !important;
        max-width: 100% !important;
        min-width: 0 !important;
        overflow-x: hidden !important;
        overflow-y: visible !important;
    }

    /* Las tablas se ajustan exactamente al ancho de la página. */
    .dashboard-no-scroll-layout .dashboard-forecast-table,
    .dashboard-no-scroll-layout .dashboard-compact-table,
    .dashboard-no-scroll-layout .dashboard-kpi-table,
    .dashboard-no-scroll-layout .dashboard-clients-table {
        width: 100% !important;
        max-width: 100% !important;
        min-width: 0 !important;
        table-layout: fixed !important;
        border-collapse: collapse !important;
        font-size: 0.72rem !important;
    }

    /* Primera columna más amplia; las diez métricas comparten el resto. */
    .dashboard-no-scroll-layout .dashboard-forecast-table th:first-child,
    .dashboard-no-scroll-layout .dashboard-forecast-table td:first-child,
    .dashboard-no-scroll-layout .dashboard-compact-table th:first-child,
    .dashboard-no-scroll-layout .dashboard-compact-table td:first-child,
    .dashboard-no-scroll-layout .dashboard-kpi-table th:first-child,
    .dashboard-no-scroll-layout .dashboard-kpi-table td:first-child {
        width: 20% !important;
        max-width: 20% !important;
        min-width: 0 !important;
        text-align: left !important;
    }

    .dashboard-no-scroll-layout .dashboard-forecast-table th:not(:first-child),
    .dashboard-no-scroll-layout .dashboard-forecast-table td:not(:first-child),
    .dashboard-no-scroll-layout .dashboard-compact-table th:not(:first-child),
    .dashboard-no-scroll-layout .dashboard-compact-table td:not(:first-child),
    .dashboard-no-scroll-layout .dashboard-kpi-table th:not(:first-child),
    .dashboard-no-scroll-layout .dashboard-kpi-table td:not(:first-child) {
        width: 8% !important;
        max-width: 8% !important;
        min-width: 0 !important;
        text-align: right !important;
    }

    /* Encabezados legibles en dos líneas cuando sea necesario. */
    .dashboard-no-scroll-layout .dashboard-forecast-table th,
    .dashboard-no-scroll-layout .dashboard-compact-table th,
    .dashboard-no-scroll-layout .dashboard-kpi-table th {
        white-space: normal !important;
        overflow-wrap: anywhere !important;
        word-break: normal !important;
        line-height: 1.12 !important;
        padding: 0.38rem 0.18rem !important;
        vertical-align: bottom !important;
        font-size: 0.68rem !important;
    }

    /* Valores alineados y sin invadir columnas vecinas. */
    .dashboard-no-scroll-layout .dashboard-forecast-table td,
    .dashboard-no-scroll-layout .dashboard-compact-table td,
    .dashboard-no-scroll-layout .dashboard-kpi-table td {
        white-space: nowrap !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
        padding: 0.38rem 0.20rem !important;
        line-height: 1.2 !important;
        box-sizing: border-box !important;
    }

    .dashboard-no-scroll-layout .dashboard-compact-label,
    .dashboard-no-scroll-layout .dashboard-client-name,
    .dashboard-no-scroll-layout .dashboard-kpi-name {
        white-space: nowrap !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
        padding-left: 0.35rem !important;
        text-align: left !important;
    }

    /* Títulos alineados al inicio del bloque correspondiente. */
    .dashboard-no-scroll-layout .dashboard-compact-title-box,
    .dashboard-no-scroll-layout .dashboard-kpi-panel-title {
        width: auto !important;
        max-width: 100% !important;
        margin-left: 0 !important;
        margin-right: 0 !important;
        text-align: left !important;
    }

    /* Evita que reglas anteriores vuelvan a imponer anchos grandes. */
    .dashboard-no-scroll-layout col,
    .dashboard-no-scroll-layout .dashboard-col-label,
    .dashboard-no-scroll-layout .dashboard-col-client-name,
    .dashboard-no-scroll-layout .dashboard-col-num,
    .dashboard-no-scroll-layout .dashboard-col-pct {
        min-width: 0 !important;
    }

    @media (max-width: 1100px) {
        .dashboard-no-scroll-layout .dashboard-forecast-table,
        .dashboard-no-scroll-layout .dashboard-compact-table,
        .dashboard-no-scroll-layout .dashboard-kpi-table,
        .dashboard-no-scroll-layout .dashboard-clients-table {
            font-size: 0.66rem !important;
        }

        .dashboard-no-scroll-layout .dashboard-forecast-table th,
        .dashboard-no-scroll-layout .dashboard-compact-table th,
        .dashboard-no-scroll-layout .dashboard-kpi-table th {
            font-size: 0.62rem !important;
            padding-left: 0.10rem !important;
            padding-right: 0.10rem !important;
        }

        .dashboard-no-scroll-layout .dashboard-forecast-table td,
        .dashboard-no-scroll-layout .dashboard-compact-table td,
        .dashboard-no-scroll-layout .dashboard-kpi-table td {
            padding-left: 0.12rem !important;
            padding-right: 0.12rem !important;
        }
    }
    """

    closing_tag = "</style>"
    closing_index = css.rfind(closing_tag)

    if closing_index == -1:
        return css + f"<style>{no_scroll_rules}</style>"

    return css[:closing_index] + no_scroll_rules + css[closing_index:]

# =========================================================
# DASHBOARD LADO A LADO CON SCROLL ALINEADO
# =========================================================
_build_dashboard_css_html_before_aligned_scroll = build_dashboard_css_html

def build_dashboard_css_html() -> str:
    """
    Conserva los estilos existentes y aplica la distribución final:

    - MTD y YTD permanecen lado a lado.
    - Sales Month y Sales YTD también tienen barra horizontal.
    - Cada panel desplaza únicamente su propia tabla.
    - Ambos paneles conservan el mismo ancho, altura y punto de inicio.
    """
    css = _build_dashboard_css_html_before_aligned_scroll()

    aligned_scroll_rules = """
    .dashboard-scroll-aligned-layout {
        width: 100% !important;
        max-width: 100% !important;
        min-width: 0 !important;
        overflow-x: hidden !important;
        box-sizing: border-box !important;
    }

    /* Mantiene MTD y YTD lado a lado en todos los bloques. */
    .dashboard-scroll-aligned-layout .dashboard-kpi-grid,
    .dashboard-scroll-aligned-layout .dashboard-report-pair-grid {
        display: grid !important;
        grid-template-columns: minmax(0, 1fr) minmax(0, 1fr) !important;
        gap: 1.35rem !important;
        align-items: start !important;
        width: 100% !important;
        max-width: 100% !important;
        min-width: 0 !important;
    }

    .dashboard-scroll-aligned-layout .dashboard-kpi-panel,
    .dashboard-scroll-aligned-layout .dashboard-report-section,
    .dashboard-scroll-aligned-layout .dashboard-compact-block {
        width: 100% !important;
        max-width: 100% !important;
        min-width: 0 !important;
        overflow: hidden !important;
        box-sizing: border-box !important;
    }

    /*
    La barra horizontal se aplica también al primer bloque Sales.
    Así Sales Month y Sales YTD se comportan exactamente igual que
    las tablas inferiores y dejan de verse desalineados.
    */
    .dashboard-scroll-aligned-layout .dashboard-kpi-table-wrap,
    .dashboard-scroll-aligned-layout .dashboard-forecast-table-wrap,
    .dashboard-scroll-aligned-layout .dashboard-compact-table-wrap,
    .dashboard-scroll-aligned-layout .dashboard-clients-table-wrap,
    .dashboard-scroll-aligned-layout .dashboard-table-wrap {
        display: block !important;
        width: 100% !important;
        max-width: 100% !important;
        min-width: 0 !important;
        overflow-x: auto !important;
        overflow-y: hidden !important;
        scrollbar-gutter: stable !important;
        padding-bottom: 0.22rem !important;
        box-sizing: border-box !important;
    }

    /* Todas las tablas usan el mismo ancho interno. */
    .dashboard-scroll-aligned-layout .dashboard-kpi-table,
    .dashboard-scroll-aligned-layout .dashboard-forecast-table,
    .dashboard-scroll-aligned-layout .dashboard-compact-table,
    .dashboard-scroll-aligned-layout .dashboard-clients-table {
        width: 1280px !important;
        min-width: 1280px !important;
        max-width: none !important;
        table-layout: fixed !important;
        border-collapse: collapse !important;
        font-size: 0.78rem !important;
    }

    /* Primera columna uniforme en KPI y reportes. */
    .dashboard-scroll-aligned-layout .dashboard-kpi-table th:first-child,
    .dashboard-scroll-aligned-layout .dashboard-kpi-table td:first-child,
    .dashboard-scroll-aligned-layout .dashboard-forecast-table th:first-child,
    .dashboard-scroll-aligned-layout .dashboard-forecast-table td:first-child,
    .dashboard-scroll-aligned-layout .dashboard-compact-table th:first-child,
    .dashboard-scroll-aligned-layout .dashboard-compact-table td:first-child {
        width: 220px !important;
        min-width: 220px !important;
        max-width: 220px !important;
        text-align: left !important;
    }

    .dashboard-scroll-aligned-layout .dashboard-kpi-table th,
    .dashboard-scroll-aligned-layout .dashboard-kpi-table td,
    .dashboard-scroll-aligned-layout .dashboard-forecast-table th,
    .dashboard-scroll-aligned-layout .dashboard-forecast-table td,
    .dashboard-scroll-aligned-layout .dashboard-compact-table th,
    .dashboard-scroll-aligned-layout .dashboard-compact-table td {
        min-width: 96px !important;
        white-space: nowrap !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
        box-sizing: border-box !important;
    }

    /*
    Los títulos no se desplazan con la tabla.
    Permanecen alineados arriba de cada panel.
    */
    .dashboard-scroll-aligned-layout .dashboard-kpi-panel-title {
        width: 190px !important;
        margin: 0.55rem auto 0.7rem auto !important;
        text-align: center !important;
    }

    .dashboard-scroll-aligned-layout .dashboard-compact-title-box {
        width: fit-content !important;
        max-width: 100% !important;
        margin-left: 0 !important;
        margin-right: 0 !important;
        text-align: left !important;
    }

    /* Altura consistente para que ambos paneles comiencen parejos. */
    .dashboard-scroll-aligned-layout .dashboard-kpi-panel {
        display: flex !important;
        flex-direction: column !important;
        align-self: stretch !important;
    }

    .dashboard-scroll-aligned-layout .dashboard-kpi-table-wrap {
        margin-top: 0 !important;
    }

    /* Revierte las reglas del bloque vertical anterior. */
    .dashboard-no-scroll-layout .dashboard-kpi-grid,
    .dashboard-no-scroll-layout .dashboard-report-pair-grid {
        grid-template-columns: minmax(0, 1fr) minmax(0, 1fr) !important;
    }

    @media (max-width: 900px) {
        .dashboard-scroll-aligned-layout .dashboard-kpi-grid,
        .dashboard-scroll-aligned-layout .dashboard-report-pair-grid {
            grid-template-columns: minmax(0, 1fr) !important;
        }
    }
    """

    closing_tag = "</style>"
    closing_index = css.rfind(closing_tag)

    if closing_index == -1:
        return css + f"<style>{aligned_scroll_rules}</style>"

    return (
        css[:closing_index]
        + aligned_scroll_rules
        + css[closing_index:]
    )



# =========================================================
# CORRECCIÓN FINAL DE ESTILOS: RANKING + NEGATIVOS EN TOTALES
# =========================================================
_original_build_global_css = build_global_css


def build_global_css() -> str:
    """
    Devuelve un único bloque <style> válido.

    Algunas extensiones anteriores de styles.py agregaban nuevos bloques
    <style> dentro de otro bloque <style>. El navegador interpretaba ese HTML
    anidado como texto visible. Aquí se eliminan todas las etiquetas de estilo
    intermedias y se vuelve a envolver el CSS completo una sola vez.
    """
    base_css = str(_original_build_global_css() or "")
    base_css = base_css.replace("<style>", "").replace("</style>", "")

    extra_rules = r"""
/* =====================================================
   REGLAS DEFINITIVAS DEL RANKING DE CLIENTES
   ===================================================== */

/* El contenedor puede desplazarse en ambas direcciones. */
.report4-scroll-fixed {
    overflow-x: auto !important;
    overflow-y: auto !important;
    max-height: 560px !important;
    position: relative !important;
    isolation: isolate !important;
    background: #FFFFFF !important;
}

/* Todas las celdas respetan el ancho de su columna y no invaden otras. */
.report4-grid-fixed > .report-cell {
    min-width: 0 !important;
    overflow: hidden !important;
    text-overflow: ellipsis !important;
    white-space: nowrap !important;
    box-sizing: border-box !important;
}

/* Todos los encabezados permanecen alineados y fijos únicamente en vertical. */
.report4-grid-fixed > .report-header {
    position: sticky !important;
    top: 0 !important;
    z-index: 300 !important;
}

/* ÚNICAMENTE CLIENT NAME, incluyendo su encabezado, queda fijo horizontalmente. */
.report4-name-header,
.report4-name-cell {
    position: sticky !important;
    left: 0 !important;
    justify-content: flex-start !important;
    text-align: left !important;
    padding-left: 0.85rem !important;
    box-shadow: 3px 0 5px rgba(15, 23, 42, 0.08) !important;
}

.report4-name-header {
    top: 0 !important;
    z-index: 330 !important;
    color: #FFFFFF !important;
    background: #1F2A44 !important;
    font-weight: 800 !important;
}

.report4-name-cell {
    z-index: 230 !important;
    color: #1F2A44 !important;
    background: #F8FAFC !important;
    font-weight: 700 !important;
}

/* CLIENTE (código) va en negritas, pero NO queda fijo horizontalmente. */
.report4-code-header {
    position: sticky !important;
    top: 0 !important;
    left: auto !important;
    z-index: 300 !important;
    color: #FFFFFF !important;
    background: #1F2A44 !important;
    font-weight: 800 !important;
    justify-content: flex-start !important;
    text-align: left !important;
    padding-left: 0.75rem !important;
    box-shadow: none !important;
}

.report4-code-cell {
    position: static !important;
    left: auto !important;
    z-index: 1 !important;
    color: #1F2A44 !important;
    background: #F8FAFC !important;
    font-weight: 700 !important;
    justify-content: flex-start !important;
    text-align: left !important;
    padding-left: 0.75rem !important;
    box-shadow: none !important;
}

/* Resultados normales: sin negritas. */
.report4-grid-fixed .report4-metric-cell,
.report4-grid-fixed .report-value-cell {
    font-weight: 500 !important;
}

/* Subtotales y totales: toda la fila en negritas. */
.report4-grid-fixed .report-total .report-cell,
.report4-grid-fixed .report-highlight .report-cell {
    font-weight: 800 !important;
}

.report4-grid-fixed .report-total .report-cell {
    background: #F3F6FA !important;
}

.report4-grid-fixed .report-highlight .report-cell {
    background: #DCEFD8 !important;
}

/* Conserva el fondo correcto de la primera columna y del código en totales. */
.report4-grid-fixed .report-total .report4-name-cell,
.report4-grid-fixed .report-total .report4-code-cell {
    background: #F3F6FA !important;
}

.report4-grid-fixed .report-highlight .report4-name-cell,
.report4-grid-fixed .report-highlight .report4-code-cell {
    background: #DCEFD8 !important;
}

/* Negativos normales: rojo, entre paréntesis desde app.py y sin negritas. */
.report4-grid-fixed .report-cell.report-negative {
    color: #C0392B !important;
    font-weight: 500 !important;
}

/* Negativos dentro de total o subtotal: rojo y en negritas. */
.report4-grid-fixed .report-total .report-cell.report-negative,
.report4-grid-fixed .report-highlight .report-cell.report-negative {
    color: #C0392B !important;
    font-weight: 800 !important;
}

/* Regla general para negativos de otros reportes:
   rojo; solo los totales y resaltados se conservan en negritas. */
.report-cell.report-negative {
    color: #C0392B !important;
}

.report-row:not(.report-total):not(.report-highlight) .report-cell.report-negative {
    font-weight: 500 !important;
}

.report-total .report-cell.report-negative,
.report-highlight .report-cell.report-negative {
    color: #C0392B !important;
    font-weight: 800 !important;
}

.report-empty-state {
    padding: 0.9rem;
    text-align: center;
    font-weight: 700;
    color: #1F2A44;
}
"""

    extra_rules = extra_rules.rstrip() + r"""
/* =====================================================
   ÚLTIMO OVERRIDE: PRIMERA COLUMNA COMPLETA FIJA
   Incluye CLIENT NAME y su encabezado.
   ===================================================== */
.report4-scroll-fixed .report4-grid-fixed > .report4-name-header {
    position: sticky !important;
    top: 0 !important;
    left: 0 !important;
    z-index: 9999 !important;
    display: flex !important;
    visibility: visible !important;
    opacity: 1 !important;
    color: #FFFFFF !important;
    background: #1F2A44 !important;
    font-weight: 800 !important;
    justify-content: flex-start !important;
    text-align: left !important;
    padding-left: 0.85rem !important;
    overflow: hidden !important;
    white-space: nowrap !important;
    box-shadow: 4px 0 8px rgba(15, 23, 42, 0.18) !important;
}

.report4-scroll-fixed .report4-grid-fixed > .report4-name-cell {
    position: sticky !important;
    left: 0 !important;
    z-index: 9000 !important;
    display: flex !important;
    visibility: visible !important;
    opacity: 1 !important;
    color: #1F2A44 !important;
    background: #F8FAFC !important;
    font-weight: 700 !important;
    justify-content: flex-start !important;
    text-align: left !important;
    padding-left: 0.85rem !important;
    overflow: hidden !important;
    text-overflow: ellipsis !important;
    white-space: nowrap !important;
    box-shadow: 4px 0 8px rgba(15, 23, 42, 0.12) !important;
}

.report4-scroll-fixed .report4-grid-fixed .report-total > .report4-name-cell {
    background: #F3F6FA !important;
    font-weight: 800 !important;
}

.report4-scroll-fixed .report4-grid-fixed .report-highlight > .report4-name-cell {
    background: #DCEFD8 !important;
    font-weight: 800 !important;
}
"""

    return "<style>\n" + base_css.strip() + "\n" + extra_rules.strip() + "\n</style>"


# =========================================================
# REFINAMIENTO EJECUTIVO 2026-08-13
# =========================================================
_build_global_css_before_exec_filters = build_global_css


def build_global_css() -> str:
    css = _build_global_css_before_exec_filters()

    extra = """<style>
/* =====================================================
   REFINAMIENTO FINAL DE FILTROS + RANKING
   ===================================================== */

/* Plan y sus dos variaciones usan exactamente el mismo color. */
.report-header-plan,
.report-header-var-plan,
.var-header-plan {
    background: #D4A017 !important;
    color: #FFFFFF !important;
}

/* El filtro cerrado tiene la misma presencia visual que un control normal. */
div[data-testid="stExpander"] {
    border-radius: 14px !important;
}

/* Evita espacios verticales exagerados entre filtro/descarga y las tablas. */
.compact-report-note {
    margin-top: 0.05rem !important;
    margin-bottom: 0.55rem !important;
}

/* Botones individuales de descarga: tamaño compacto y alineación con el expander. */
div[data-testid="stDownloadButton"] > button {
    min-width: 46px !important;
    width: 46px !important;
    height: 46px !important;
    min-height: 46px !important;
    padding: 0 !important;
    border-radius: 14px !important;
}

/* Formularios dentro de filtros: sin caja adicional ni padding innecesario. */
div[data-testid="stExpander"] div[data-testid="stForm"] {
    padding: 0.15rem 0 0 0 !important;
    margin: 0 !important;
}

/* Ranking: layout más limpio para TOP / nombre / código. */
.report4-modern-scroll {
    overflow-x: auto !important;
    overflow-y: auto !important;
    max-height: 590px !important;
    border-radius: 14px !important;
}

.report4-modern-grid > .report-cell {
    min-width: 0 !important;
    overflow: hidden !important;
    text-overflow: ellipsis !important;
    white-space: nowrap !important;
    box-sizing: border-box !important;
}

.report4-modern-grid > .report-header {
    position: sticky !important;
    top: 0 !important;
    z-index: 80 !important;
}

.report4-top-header,
.report4-top-cell {
    justify-content: center !important;
    text-align: center !important;
}

.report4-name-display-header,
.report4-name-display-cell,
.report4-code-display-header,
.report4-code-display-cell {
    justify-content: flex-start !important;
    text-align: left !important;
}

.report4-name-display-cell,
.report4-code-display-cell {
    background: #FBFCFE !important;
    color: #1F2A44 !important;
    font-weight: 700 !important;
}

.report4-modern-grid .report-total .report-cell {
    background: #F3F6FA !important;
    font-weight: 800 !important;
}

.report4-modern-grid .report-highlight .report-cell {
    background: #DCEFD8 !important;
    font-weight: 800 !important;
}

/* Negativos conservan rojo; en filas normales sin peso excesivo. */
.report4-modern-grid .report-row:not(.report-total):not(.report-highlight)
.report-cell.report-negative {
    color: #C0392B !important;
    font-weight: 500 !important;
}

/* Buscador del Ranking. */
.client-search-result {
    border: 1px solid #E7EAF0;
    border-left: 5px solid #E60023;
    border-radius: 16px;
    padding: 0.85rem 1rem;
    margin: 0.45rem 0;
    background: #FFFFFF;
}

.client-search-result strong {
    color: #1F2A44;
}

/* El botón global del sidebar NO debe heredar el tamaño compacto
   de los botones individuales de descarga del área principal. */
section[data-testid="stSidebar"] div[data-testid="stDownloadButton"] > button,
section[data-testid="stSidebar"] .stDownloadButton > button {
    width: 100% !important;
    min-width: 100% !important;
    height: auto !important;
    min-height: 46px !important;
    padding: 0.70rem 1.0rem !important;
    white-space: normal !important;
    word-break: normal !important;
    line-height: 1.25 !important;
}
</style>"""

    return css + "\n" + extra
