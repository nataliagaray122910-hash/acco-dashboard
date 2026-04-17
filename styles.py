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
        <div class="hero-title">{config.MAIN_TITLE}</div>
        <div class="main-subtitle">{config.SUBTITLE}</div>
        <div class="hero-text">{config.WELCOME_MESSAGE}</div>
    </div>
    """

def build_info_card(title: str, value: str, description: str = "") -> str:
    """
    Genera una tarjeta visual simple.
    """
    return f"""
    <div class="custom-card">
        <div class="card-title">{title}</div>
        <div class="card-value">{value}</div>
        <div class="card-description">{description}</div>
    </div>
    """

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