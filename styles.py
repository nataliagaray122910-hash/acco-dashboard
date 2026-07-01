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
        border-bottom: 1px solid #111111 !important;
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
        margin-top: -0.2rem;
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

def build_info_card(title: str, value: str, description: str = "") -> str:
    """
    Genera una tarjeta ejecutiva con icono, usando el mismo lenguaje visual
    que Base MTD y Visión general.
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
    font-size: 0.82rem;
}

.dashboard-clients-table .dashboard-col-client-name {
    width: 31%;
}

.dashboard-clients-table .dashboard-col-client-code {
    width: 9%;
}

.dashboard-clients-table .dashboard-col-num {
    width: 8.55%;
}

.dashboard-clients-table .dashboard-col-pct {
    width: 8.55%;
}

.dashboard-clients-table th {
    font-size: 0.76rem !important;
}

.dashboard-clients-table td {
    font-size: 0.78rem !important;
    padding: 0.27rem 0.24rem !important;
}

.dashboard-client-name {
    max-width: 1px;
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

