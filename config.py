# =========================================================
# CONFIGURACIÓN GENERAL DEL DASHBOARD
# Archivo: config.py
# =========================================================

# ---------------------------------------------------------
# IDENTIDAD DE LA APLICACIÓN
# ---------------------------------------------------------
APP_TITLE = "ACCO Brands | Reportes"
APP_ICON = "assets/acco_icon.png"
APP_LAYOUT = "wide"
APP_SIDEBAR_STATE = "expanded"

# ---------------------------------------------------------
# TEXTOS GENERALES
# ---------------------------------------------------------
MAIN_TITLE = "ACCO BRANDS"
SUBTITLE = "REPORTES CORPORATIVOS"
WELCOME_MESSAGE = "Dashboard ejecutivo para análisis comercial y financiero"

# ---------------------------------------------------------
# CONFIGURACIÓN DE LOGIN Y ROLES
# ---------------------------------------------------------
# Usuarios autorizados para entrar a la app.
# - admin/admin: usuario para Natalia y jefa; puede cargar y guardar datos.
# - viewer/viewer: usuario de consulta; no ve la carga de datos.
VALID_USERS = {
    "admin": "admin",
    "viewer": "viewer",
}

# Usuarios con permiso para cargar/actualizar información.
ADMIN_USERS = ["admin"]

# Carpeta temporal donde Streamlit guardará la última carga administrativa.
# Nota: en Streamlit Cloud esta persistencia es útil para pruebas, pero puede perderse si la app reinicia.
PERSISTENT_DATA_PATH = "persistent_data"
PERSISTENT_DATA_FILE_NAME = "latest_dashboard_data.pkl.gz"

# Backend de persistencia.
# - "auto": usa GitHub si existen secretos; si no, usa local.
# - "local": útil para localhost.
# - "github": recomendado para Streamlit Cloud porque sobrevive reinicios.
PERSISTENCE_BACKEND = "auto"

# Configuración para GitHub Storage.
# En Streamlit Cloud se recomienda manejar estos valores como Secrets:
# GITHUB_TOKEN, GITHUB_REPO, GITHUB_BRANCH, GITHUB_PERSISTENCE_PATH.
GITHUB_BRANCH = "main"
GITHUB_PERSISTENCE_PATH = "persistent_data/latest_dashboard_data.pkl.gz"

# ---------------------------------------------------------
# PALETA DE COLORES CORPORATIVA
# ---------------------------------------------------------
COLOR_PRIMARY = "#E60023"
COLOR_SECONDARY = "#1F2A44"
COLOR_BACKGROUND = "#F4F6F8"
COLOR_SURFACE = "#FFFFFF"
COLOR_TEXT = "#1E1E1E"
COLOR_MUTED = "#6B7280"
COLOR_BORDER = "#D9DEE5"
COLOR_SUCCESS = "#1E9E63"
COLOR_WARNING = "#D97706"
COLOR_ERROR = "#C0392B"

# ---------------------------------------------------------
# RUTAS DE RECURSOS VISUALES
# ---------------------------------------------------------
LOGO_PATH = "assets/logo.png"
BACKGROUND_PATH = "assets/fondo.jpg"

# ---------------------------------------------------------
# PANTALLA DE INICIO CORPORATIVA
# ---------------------------------------------------------
HOME_BANNER_PATHS = [
    "assets/home_banner_1.jpg",
    "assets/home_banner_2.jpg",
]
HOME_MODULES_TITLE = "Conoce nuestros módulos"
HOME_MODULES_SUBTITLE = (
    "Cada sección está diseñada para ayudarte a analizar y entender tu información "
    "de forma simple y eficiente."
)
HOME_MODULE_CARDS = [
    {"title": "Carga de datos", "description": "Carga y valida automáticamente el archivo corporativo de ventas y planes.", "icon": "📁"},
    {"title": "Visión general", "description": "Procesa la base de ventas y genera indicadores generales de la información.", "icon": "📈"},
    {"title": "Base MTD", "description": "Construye comparativos MTD, YTD y BTS para Plan Cliente y Plan SKU.", "icon": "📊"},
    {"title": "Oficina de ventas", "description": "Analiza el desempeño por oficina de ventas.", "icon": "🏢"},
    {"title": "Segmento y Categoría", "description": "Evalúa resultados por segmento de negocio, región y categoría de material.", "icon": "🌐"},
    {"title": "Canal", "description": "Consulta el desempeño de ventas por canal corporativo.", "icon": "🛒"},
    {"title": "Ranking Clientes", "description": "Visualiza el Top 15 de clientes y sus variaciones vs Plan y PY.", "icon": "👥"},
    {"title": "Dashboard", "description": "Accede al resumen ejecutivo con gráficos y KPIs consolidados.", "icon": "🖥️"},
]
HOME_TRUST_ITEMS = [
    {"title": "Información confiable", "description": "Todos los datos provienen de fuentes corporativas y cuentan con validaciones automáticas.", "icon": "🛡️"},
    {"title": "Seguridad y control", "description": "La información se mantiene segura y disponible únicamente para usuarios autorizados.", "icon": "🔒"},
    {"title": "¿Necesitas ayuda?", "description": "Si tienes alguna duda, contacta al equipo de análisis o soporte de información.", "icon": "🎧"},
]


# =========================================================
# CARGA AUTOMÁTICA DESDE SHAREPOINT SINCRONIZADO
# =========================================================
# Esta opción NO usa API, credenciales ni links directos de SharePoint.
# Lee el archivo desde la carpeta sincronizada de OneDrive/SharePoint
# en la computadora donde se ejecuta la app localmente.

SYNCED_SHAREPOINT_ENABLED = False

SYNCED_SHAREPOINT_FILE_NAME = "BASE FINAL ACUMULADA VENTAS CORPO 2024-2026.xlsx"

SYNCED_SHAREPOINT_FILE_PATH = (
    r"C:\Users\pncarden\OneDrive - ACCO Brands Corporation"
    r"\Supply Chain Finance - REPORTES"
    r"\BASE FINAL ACUMULADA VENTAS CORPO 2024-2026.xlsx"
)

SYNCED_SHAREPOINT_BUTTON_LABEL = "Actualizar desde SharePoint sincronizado"

SYNCED_SHAREPOINT_LOAD_SUCCESS = (
    "Archivo cargado correctamente desde la carpeta sincronizada de SharePoint."
)

SYNCED_SHAREPOINT_LOAD_ERROR = (
    "No fue posible cargar el archivo desde la carpeta sincronizada de SharePoint."
)

# ---------------------------------------------------------
# CONFIGURACIÓN GLOBAL DE MONEDA
# ---------------------------------------------------------
DEFAULT_CURRENCY = "MXN"
DEFAULT_EXCHANGE_RATE = 20.00

SUPPORTED_CURRENCIES = [
    "MXN",
    "USD",
]

CURRENCY_LABEL_MXN = "MXN"
CURRENCY_LABEL_USD = "USD"

CURRENCY_SECTION_TITLE = "Moneda"
CURRENCY_STATUS_LABEL = "Moneda base"
CURRENCY_EXCHANGE_RATE_LABEL = "Tipo de cambio (MXN por 1 USD)"
CURRENCY_BUTTON_USE_MXN = "Usar MXN"
CURRENCY_BUTTON_USE_USD = "Cambiar a USD"
CURRENCY_HELP_TEXT = (
    "Este cambio es global y persistente durante la sesión. "
    "Todo inicia en MXN y solo cambia cuando el usuario lo decide."
)

# ---------------------------------------------------------
# MENÚ PRINCIPAL DE NAVEGACIÓN
# ---------------------------------------------------------
MAIN_MENU_OPTIONS = [
    "Inicio",
    "Carga de datos",
    "Visión general",
    "Oficina de ventas",
    "Segmento y Categoría",
    "Canal",
    "Ranking Clientes",
    "Base MTD",
    "Dashboard",
]

# ---------------------------------------------------------
# DASHBOARD EJECUTIVO
# ---------------------------------------------------------
DASHBOARD_TITLE = "Mexico Dashboard 2026"
DASHBOARD_SUBTITLE = "EXECUTIVE SALES PERFORMANCE"
DASHBOARD_BUTTON_LABEL = "Cargar Dashboard"
DASHBOARD_CURRENCY_LABEL = "$Kmxn"

# =========================================================
# CONFIGURACIÓN DE EXPORTACIONES
# =========================================================

# ---------------------------------------------------------
# FORMATO GENERAL DE EXPORTACIÓN
# ---------------------------------------------------------
EXPORT_FILE_EXTENSION = "xlsx"
EXPORT_EXCEL_MIME = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
EXPORT_ICON_LABEL = "⭳"

# ---------------------------------------------------------
# BOTÓN GLOBAL
# ---------------------------------------------------------
EXPORT_ALL_REPORTS_BUTTON_LABEL = "Descargar todos los reportes"
EXPORT_ALL_REPORTS_FILE_NAME = "reportes_corporativos.xlsx"
EXPORT_ALL_REPORTS_HELP = "Descargar todos los reportes construidos en un solo archivo Excel"

# ---------------------------------------------------------
# NOMBRES DE ARCHIVOS INDIVIDUALES
# ---------------------------------------------------------
EXPORT_REPORT_1_FILE_BASE = "reporte_1"
EXPORT_REPORT_2_SEGMENT_FILE_BASE = "reporte_2_segment_region"
EXPORT_REPORT_2_CATEGORY_FILE_BASE = "reporte_2_category"
EXPORT_REPORT_3_FILE_BASE = "reporte_3"
EXPORT_REPORT_4_FILE_BASE = "reporte_4"
EXPORT_BASE_MTD_FILE_BASE = "base_mtd"

# ---------------------------------------------------------
# TOOLTIPS DE BOTONES INDIVIDUALES
# ---------------------------------------------------------
EXPORT_REPORT_1_HELP = "Descargar Reporte 1"
EXPORT_REPORT_2_SEGMENT_HELP = "Descargar Segment x Region"
EXPORT_REPORT_2_CATEGORY_HELP = "Descargar Category"
EXPORT_REPORT_3_HELP = "Descargar Reporte 3"
EXPORT_REPORT_4_HELP = "Descargar Reporte 4"
EXPORT_BASE_MTD_HELP = "Descargar Base MTD"

# ---------------------------------------------------------
# NOMBRES DE HOJAS EXCEL
# ---------------------------------------------------------
EXPORT_SHEET_REPORT_1 = "Reporte 1"
EXPORT_SHEET_REPORT_2_SEGMENT = "Reporte 2 - Segment"
EXPORT_SHEET_REPORT_2_CATEGORY = "Reporte 2 - Category"
EXPORT_SHEET_REPORT_3 = "Reporte 3"
EXPORT_SHEET_REPORT_4 = "Reporte 4"
EXPORT_SHEET_BASE_MTD = "Base MTD"
EXPORT_SHEET_BASE_MTD_CLIENT = "Base MTD Cliente"
EXPORT_SHEET_BASE_MTD_SKU = "Base MTD SKU"
EXPORT_SHEET_BASE_MTD_BTS = "BTS"

# =========================================================
# ETAPA 2: CONFIGURACIÓN DE CARGA Y VALIDACIÓN DE ARCHIVOS
# =========================================================

# ---------------------------------------------------------
# TIPOS DE ARCHIVO
# ---------------------------------------------------------
ALLOWED_FILE_TYPES = ["xlsx", "xls", "csv"]

# ---------------------------------------------------------
# KEYS DE CARGA
# ---------------------------------------------------------
FILE_KEY_SALES = "sales_file"
FILE_KEY_PLAN_CLIENT = "plan_client_file"
FILE_KEY_PLAN_SKU = "plan_sku_file"

# ---------------------------------------------------------
# COLUMNAS MÍNIMAS ESPERADAS
# ---------------------------------------------------------
EXPECTED_COLUMNS_SALES = [
    "Periodo",
]

EXPECTED_COLUMNS_PLAN_CLIENT = [
    "Segment",
    "Client",
]

EXPECTED_COLUMNS_PLAN_SKU = [
    "Material",
]

# ---------------------------------------------------------
# MENSAJES REUTILIZABLES
# ---------------------------------------------------------
MSG_UPLOAD_SUCCESS = "Archivo cargado correctamente."
MSG_UPLOAD_ERROR = "No fue posible leer el archivo."
MSG_VALIDATION_OK = "La estructura mínima del archivo es válida."
MSG_VALIDATION_FAIL = "El archivo no contiene las columnas mínimas requeridas."

# =========================================================
# ETAPA 3: CONFIGURACIÓN DE PROCESAMIENTO
# =========================================================

# ---------------------------------------------------------
# COLUMNAS NUMÉRICAS DE VENTAS
# ---------------------------------------------------------
SALES_NUMERIC_COLUMNS = [
    "Importe Vtas Brutas",
    "Importe Devoluciones",
    "Importe Fact No Embq",
    "Costo Vtas Netas",
    "Cant Vtas Netas",
    "GSNR",
]

# ---------------------------------------------------------
# COLUMNAS MÍNIMAS PARA PROCESAR VENTAS
# ---------------------------------------------------------
REQUIRED_COLUMNS_SALES_PROCESS = [
    "Periodo",
    "Costo Vtas Netas",
]

# ---------------------------------------------------------
# NOMBRES DE COLUMNAS DERIVADAS
# ---------------------------------------------------------
COL_YEAR = "Año"
COL_MONTH = "Mes"
COL_GSNR = "GSNR"
COL_GROSS_MARGIN = "Gross Margin"

# ---------------------------------------------------------
# MAPA DE MESES
# ---------------------------------------------------------
MONTH_MAP = {
    "01": 1, "1": 1, "jan": 1, "january": 1, "ene": 1, "enero": 1,
    "02": 2, "2": 2, "feb": 2, "february": 2, "febrero": 2,
    "03": 3, "3": 3, "mar": 3, "march": 3, "marzo": 3,
    "04": 4, "4": 4, "apr": 4, "april": 4, "abr": 4, "abril": 4,
    "05": 5, "5": 5, "may": 5, "mayo": 5,
    "06": 6, "6": 6, "jun": 6, "june": 6, "junio": 6,
    "07": 7, "7": 7, "jul": 7, "july": 7, "julio": 7,
    "08": 8, "8": 8, "aug": 8, "august": 8, "ago": 8, "agosto": 8,
    "09": 9, "9": 9, "sep": 9, "sept": 9, "september": 9, "septiembre": 9,
    "10": 10, "oct": 10, "october": 10, "octubre": 10,
    "11": 11, "nov": 11, "november": 11, "noviembre": 11,
    "12": 12, "dec": 12, "december": 12, "dic": 12, "diciembre": 12,
}

# ---------------------------------------------------------
# ETIQUETAS VISUALES DE MESES
# ---------------------------------------------------------
MONTH_LABELS = {
    1: "Enero",
    2: "Febrero",
    3: "Marzo",
    4: "Abril",
    5: "Mayo",
    6: "Junio",
    7: "Julio",
    8: "Agosto",
    9: "Septiembre",
    10: "Octubre",
    11: "Noviembre",
    12: "Diciembre",
}

# ---------------------------------------------------------
# TEXTOS GENERALES DE FILTROS
# ---------------------------------------------------------
FILTER_YEAR_LABEL = "Año"
FILTER_MONTH_LABEL = "Mes de corte"
FILTER_BOX_DEFAULT_TITLE = "Filtros de periodo"
FILTER_BOX_DEFAULT_SUBTITLE = (
    "Selecciona el año y el mes de corte para recalcular este bloque. "
    "El MTD mostrará solo el mes elegido y el YTD acumulará de enero a ese mismo mes."
)

# ---------------------------------------------------------
# MENSAJES DE PROCESAMIENTO
# ---------------------------------------------------------
MSG_PROCESSING_SUCCESS = "Procesamiento completado correctamente."
MSG_PROCESSING_ERROR = "Ocurrió un error durante el procesamiento."
MSG_PROCESSING_MISSING_FILES = "Para procesar, primero debes cargar un archivo de ventas válido."

# =========================================================
# ETAPA 4: CONFIGURACIÓN DE BASE MTD
# =========================================================

# ---------------------------------------------------------
# COLUMNAS ESTÁNDAR DE BASE MTD
# ---------------------------------------------------------
COL_KEY = "Concatenate"

COL_MTD_ACT = "MTD Act"
COL_MTD_PY = "MTD PY"
COL_MTD_PLAN = "MTD Plan"
COL_MTD_VAR_VS_PY = "MTD Var vs PY"
COL_MTD_PCT_VAR_VS_PY = "MTD % Var vs PY"
COL_MTD_VAR_VS_PLAN = "MTD Var vs Plan"
COL_MTD_PCT_VAR_VS_PLAN = "MTD % Var vs Plan"

COL_YTD_ACT = "YTD Act"
COL_YTD_PY = "YTD PY"
COL_YTD_PLAN = "YTD Plan"
COL_YTD_VAR_VS_PY = "YTD Var vs PY"
COL_YTD_PCT_VAR_VS_PY = "YTD % Var vs PY"
COL_YTD_VAR_VS_PLAN = "YTD Var vs Plan"
COL_YTD_PCT_VAR_VS_PLAN = "YTD % Var vs Plan"

COL_PCT_GM = "% GM"
COL_WEIGHT = "Weight"

# ---------------------------------------------------------
# COLUMNAS NUEVAS: COMPARATIVO ACTUALS VS PLAN CLIENTE
# ---------------------------------------------------------
COL_CLIENT_KEY = "LLAVE_CLIENTE"
COL_CLIENT_SEGMENT = "Segmento"
COL_CLIENT_REGION = "Región"
COL_CLIENT_CLIENT = "Cliente"
COL_CLIENT_NAME = "Nombre Cliente"
COL_CLIENT_ZONE = "Zona"

# ---------------------------------------------------------
# TEXTOS DE BASE MTD
# ---------------------------------------------------------
BASE_MTD_TITLE = "Base MTD"
BASE_MTD_MAIN_HEADING = "Base MTD / YTD"
BASE_MTD_SUBHEADING = (
    "Comparativo general entre Actual, Plan y PY para el mes de corte seleccionado, "
    "incluyendo validación de Plan Cliente vs Plan SKU y cálculo BTS."
)

BASE_MTD_FILTER_TITLE = "Filtros de Base MTD"
BASE_MTD_FILTER_SUBTITLE = (
    "Selecciona el año y el mes de corte para recalcular MTD, YTD y BTS. "
    "MTD muestra solo el mes elegido; YTD acumula enero a mes de corte; "
    "BTS respeta el ciclo octubre-agosto."
)

BASE_MTD_CLIENT_TABLE_TITLE = "Base MTD vs Plan Cliente"
BASE_MTD_SKU_TABLE_TITLE = "Base MTD vs Plan SKU"
BASE_MTD_BTS_TABLE_TITLE = "Back To School (BTS) MTD / YTD"
BASE_MTD_PLAN_VALIDATION_TITLE = "Validación Plan Cliente vs Plan SKU"
BASE_MTD_DOWNLOAD_LABEL = "Descargar Base MTD"

# ---------------------------------------------------------
# MENSAJES DE BASE MTD
# ---------------------------------------------------------
MSG_MTD_BUILD_SUCCESS = "Base MTD construida correctamente."
MSG_MTD_BUILD_ERROR = "Ocurrió un error al construir la base MTD."
MSG_MTD_BUILD_MISSING_FILES = (
    "Para construir la Base MTD primero debes tener ventas procesadas, "
    "plan por cliente y plan por SKU cargados."
)

# =========================================================
# ETAPA 5: REPORTE 1
# =========================================================

# ---------------------------------------------------------
# TEXTOS DE REPORTE 1
# ---------------------------------------------------------
REPORT_1_TITLE = "Reporte 1"
REPORT_1_MAIN_HEADING = "Oficina de ventas MTD / YTD"
REPORT_1_SUBHEADING = (
    "Comparativo ejecutivo entre Actual, Plan y PY para Oficina de ventas, "
    "separando ACCO + BARR + KENS."
)

# ---------------------------------------------------------
# TEXTOS DE FILTROS - REPORTE 1
# ---------------------------------------------------------
REPORT_1_FILTER_WITHOUT_KENS_TITLE = "Filtro del bloque: Oficina de ventas"

# ---------------------------------------------------------
# COLUMNAS REQUERIDAS PARA REPORTE 1
# ---------------------------------------------------------
REQUIRED_COLUMNS_REPORT_1_SALES = [
    "Periodo",
    "Segm Neg",
    "Oficina de Ventas",
    "GSNR",
]

REQUIRED_COLUMNS_REPORT_1_PLAN_CLIENT = [
    "Channel",
]

# ---------------------------------------------------------
# SEGMENTOS Y CATÁLOGOS DE REPORTE 1
# ---------------------------------------------------------
REPORT_1_SEGMENTS_WITHOUT_KENS = ["ACCO", "GOBA"]
REPORT_1_SEGMENT_KENS = "KENS"

REPORT_1_CHANNEL_ORDER = [
    "BB",
    "DC",
    "ET",
    "IO",
    "IT",
    "OS",
    "OT",
    "RE",
    "SR",
    "VA",
    "VR",
    "WS",
]

REPORT_1_CHANNEL_LABELS = {
    "BB": "BB: Business to Business",
    "DC": "DC: Direct to Consumer",
    "ET": "ET: E-Tail",
    "IO": "IO: Indep Office Dealers",
    "IT": "IT: IT Distributors",
    "OS": "OS: Office Super Stores",
    "OT": "OT: All Other",
    "RE": "RE: Retailers",
    "SR": "SR: Small Retail",
    "VA": "VA: Various",
    "VR": "VR: VAR's/System Integr",
    "WS": "WS: Wholesalers",
}

REPORT_1_TOTAL_LABEL = "Total"

# ---------------------------------------------------------
# MENSAJES DE REPORTE 1
# ---------------------------------------------------------
MSG_REPORT_1_BUILD_SUCCESS = "Reporte 1 construido correctamente."
MSG_REPORT_1_BUILD_ERROR = "Ocurrió un error al construir el Reporte 1."
MSG_REPORT_1_BUILD_MISSING_FILES = (
    "Para construir el Reporte 1 primero debes tener ventas procesadas "
    "y plan por cliente cargado."
)

# =========================================================
# ETAPA 6: REPORTE 2
# =========================================================

# ---------------------------------------------------------
# TEXTOS DE REPORTE 2
# ---------------------------------------------------------
REPORT_2_TITLE = "Reporte 2"
REPORT_2_MAIN_HEADING = "Comparativo Comercial: Segmento, Región y Categoría"
REPORT_2_SUBHEADING = (
    "Comparativo ejecutivo entre Actual, Plan y PY por Segmento x Región "
    "y por Category, utilizando BASE SAP y Plan2026 by SKU."
)

# ---------------------------------------------------------
# TEXTOS DE FILTROS - REPORTE 2
# ---------------------------------------------------------
REPORT_2_FILTER_SEGMENT_REGION_TITLE = "Filtro del bloque: Segment x Region"
REPORT_2_FILTER_CATEGORY_TITLE = "Filtro del bloque: Category"

# ---------------------------------------------------------
# SEGMENT X REGION
# ---------------------------------------------------------
REQUIRED_COLUMNS_REPORT_2_SALES = [
    "Periodo",
    "Segm Neg",
    "Region",
    "Grupo de vendedores",
    "GSNR",
]

REQUIRED_COLUMNS_REPORT_2_PLAN_SKU = [
    "Segmento",
    "Region",
]

REPORT_2_EXCLUDED_VENDOR_GROUP = "AFI: Afiliadas"

# ---------------------------------------------------------
# REGLAS ESPECÍFICAS BASE MTD / BTS
# ---------------------------------------------------------
# Base MTD general: Actual, PY, Plan Cliente y Plan SKU no consideran afiliadas.
BASE_MTD_EXCLUDED_VENDOR_GROUPS = [
    "AFI: Afiliadas",
    "AFI",
    "AF: Afiliadas",
    "AF",
]

# BTS: solo GOBA/BARRILITO y se excluyen estos grupos de vendedores.
BASE_MTD_BTS_EXCLUDED_VENDOR_GROUPS = [
    "AFI: Afiliadas",
    "AFI",
    "AF: Afiliadas",
    "AF",
    "ECO: Ecommerce",
    "ECO",
    "EXP: Exportaciones",
    "EXP",
    "KEN: Kensington",
    "KEN",
    "NGI: Neg Internacionales",
    "NGI",
]

REPORT_2_SEGMENT_ORDER = [
    "ACCO",
    "GOBA",
    "KENS",
]

REPORT_2_REGION_ORDER = [
    "ECO",
    "EXP",
    "KEN",
    "NORTE",
    "RETAIL",
    "SUR",
]

REPORT_2_TOTAL_LABEL = "Total"
REPORT_2_GRAND_TOTAL_LABEL = "Total General"

MSG_REPORT_2_BUILD_SUCCESS = "Reporte 2 construido correctamente."
MSG_REPORT_2_BUILD_ERROR = "Ocurrió un error al construir el Reporte 2."
MSG_REPORT_2_BUILD_MISSING_FILES = (
    "Para construir el Reporte 2 primero debes tener ventas procesadas "
    "y plan por SKU cargado."
)

# ---------------------------------------------------------
# CATEGORY
# ---------------------------------------------------------
REQUIRED_COLUMNS_REPORT_2_CATEGORY_SALES = [
    "Periodo",
    "Corpo Category",
    "Grupo de vendedores",
    "Material",
    "Descripción del Material",
    "GSNR",
]

REQUIRED_COLUMNS_REPORT_2_CATEGORY_PLAN_SKU = [
    "Corpo Category",
    "Material",
    "Descripción del Material",
]

MSG_REPORT_2_CATEGORY_BUILD_SUCCESS = "Reporte Category construido correctamente."
MSG_REPORT_2_CATEGORY_BUILD_ERROR = "Ocurrió un error al construir el Reporte Category."
MSG_REPORT_2_CATEGORY_BUILD_MISSING_FILES = (
    "Para construir el Reporte Category primero debes tener ventas procesadas "
    "y plan por SKU cargado."
)

# =========================================================
# ETAPA 7: REPORTE 3
# =========================================================

# ---------------------------------------------------------
# TEXTOS DE REPORTE 3
# ---------------------------------------------------------
REPORT_3_TITLE = "Reporte 3"
REPORT_3_MAIN_HEADING = "Canal"
REPORT_3_SUBHEADING = (
    "Comparativo ejecutivo entre Actual, Plan y PY por Channel, "
    "utilizando BASE SAP y Plan2026 by SKU."
)

# ---------------------------------------------------------
# TEXTOS DE FILTROS - REPORTE 3
# ---------------------------------------------------------
REPORT_3_FILTER_CHANNEL_TITLE = "Filtro del bloque: Channel"

# ---------------------------------------------------------
# COLUMNAS REQUERIDAS PARA REPORTE 3
# ---------------------------------------------------------
REQUIRED_COLUMNS_REPORT_3_SALES = [
    "Periodo",
    "Region",
    "Segm Neg",
    "Grupo de vendedores",
    "GSNR",
]

REQUIRED_COLUMNS_REPORT_3_PLAN_SKU = [
    "Region",
    "Segmento",
]

# ---------------------------------------------------------
# CATÁLOGOS Y REGLAS DE REPORTE 3
# ---------------------------------------------------------
REPORT_3_EXCLUDED_VENDOR_GROUP = "AFI: Afiliadas"

REPORT_3_CHANNEL_ORDER = [
    "ACCO",
    "ECO",
    "EXP",
    "BARRILITO",
    "KEN",
]

REPORT_3_REGION_TO_SEGMENT = [
    "NORTE",
    "SUR",
    "RETAIL",
]

REPORT_3_TOTAL_LABEL = "Total General"

# ---------------------------------------------------------
# MENSAJES DE REPORTE 3
# ---------------------------------------------------------
MSG_REPORT_3_BUILD_SUCCESS = "Reporte 3 construido correctamente."
MSG_REPORT_3_BUILD_ERROR = "Ocurrió un error al construir el Reporte 3."
MSG_REPORT_3_BUILD_MISSING_FILES = (
    "Para construir el Reporte 3 primero debes tener ventas procesadas "
    "y plan por SKU cargado."
)

# =========================================================
# ETAPA 8: REPORTE 4
# =========================================================

# ---------------------------------------------------------
# TEXTOS DE REPORTE 4
# ---------------------------------------------------------
REPORT_4_TITLE = "Reporte 4"
REPORT_4_MAIN_HEADING = "Ranking de Clientes"
REPORT_4_SUBHEADING = (
    "Comparativo ejecutivo MTD / YTD por cliente, construyendo el ranking dinámicamente "
    "con base en Actual y cruzando Actual/PY/Plan por código de cliente."
)

# ---------------------------------------------------------
# TEXTOS DE FILTROS - REPORTE 4
# ---------------------------------------------------------
REPORT_4_FILTER_TOP_CLIENTS_TITLE = "Filtro del bloque: Ranking de Clientes"

# ---------------------------------------------------------
# COLUMNAS REQUERIDAS PARA REPORTE 4
# ---------------------------------------------------------
REQUIRED_COLUMNS_REPORT_4_SALES = [
    "Periodo",
    "Cliente",
    "Nombre del Cliente",
    "GSNR",
]

REQUIRED_COLUMNS_REPORT_4_PLAN_CLIENT = [
    "Client",
]

# ---------------------------------------------------------
# COLUMNAS CANDIDATAS PARA IDENTIFICACIÓN DE CLIENTE
# ---------------------------------------------------------
REPORT_4_SALES_CLIENT_NAME_CANDIDATES = [
    "Nombre del Cliente",
    "Nombre Cliente",
    "Customer name",
    "Customer Name",
]

REPORT_4_SALES_CLIENT_CODE_CANDIDATES = [
    "Cliente",
    "Client",
    "Codigo de Cliente",
    "Código de Cliente",
    "Customer",
    "Customer Code",
]

REPORT_4_PLAN_CLIENT_NAME_CANDIDATES = [
    "Customer name",
    "Customer Name",
    "Nombre del Cliente",
    "Nombre Cliente",
]

REPORT_4_PLAN_CLIENT_CODE_CANDIDATES = [
    "Client",
    "Client Code",
    "codigo",
    "Código",
    "Codigo",
    "Customer",
    "Customer Code",
]

# ---------------------------------------------------------
# CATÁLOGO OFICIAL DE CLIENTES REPORTE 4
# Orden 100% fijo conforme al Excel proporcionado por negocio.
# La llave principal de cruce es el código de cliente.
# ---------------------------------------------------------
REPORT_4_CLIENT_CATALOG = []

# ---------------------------------------------------------
# NOTA REPORTE 4
# ---------------------------------------------------------
# El Ranking de Clientes ya no usa un catálogo/top fijo.
# El orden se construye dinámicamente desde BASE SAP y Plan2026 by Client:
# MTD se ordena por Actual MTD y YTD se ordena por Actual YTD.
# Esta variable se conserva vacía para compatibilidad con versiones anteriores.

# ---------------------------------------------------------
# RENOMBRES SOLO PARA CLIENTES CON NOMBRE REPETIDO
# Si el código no está en este diccionario, se conserva el nombre normal.
# ---------------------------------------------------------
REPORT_4_CLIENT_NAME_OVERRIDES = {'C02359': 'ABASTECEDORA DE OFICINAS - Barrilito',
 'C00011': 'ABASTECEDORA DE OFICINAS - ACCO',
 'C01819': 'SERVICIOS COMERCIALES AMAZON MEXICO Ventas E - Commerce',
 'C00938': 'SAMS',
 'C00825': 'CASA DE PAPELERIA M - ACCO',
 'C01628': 'SUPERCENTER',
 'C02128': 'OPERADORA OMX Activo',
 'C01804': 'BODEGA AURRERA',
 'D00014': 'MERCADO LIBRE',
 'C00304': 'INGRAM MICRO MEXICO MXN',
 'C02391': 'CASA DE PAPELERIA M - Barrilito',
 'C00488': 'COSTCO',
 'C02125': 'INGRAM MICRO MEXICO USD',
 'C02469': 'TECNOLOGIA SMARTBITT  USD',
 'C02032': 'COSTCO ECO',
 'C02474': 'COMERCIALIZADORA DE VALOR AGREGADO   USD',
 '(blank)': '(blank)',
 '(Blanks)': '(Blanks)',
 'C02454': 'TECNOLOGIA SMARTBITT  MXN',
 'B14417': 'SERVICIOS COMERCIALES AMAZON MEXICO OBSOLETO',
 'C02473': 'COMERCIALIZADORA DE VALOR AGREGADO   MXN',
 'C02468': 'SAMS.COM',
 'D00033': 'ACCO EXPRESS'}

# ---------------------------------------------------------
# CÓDIGOS MANUALES SOLO PARA PLAN CLIENTE CON CLIENT VACÍO
# ---------------------------------------------------------
# Este NO es un catálogo de ranking. Únicamente se usa si Plan2026 by Client
# trae la columna Client vacía y negocio define explícitamente el código correcto.
REPORT_4_PLAN_CLIENT_NAME_TO_CODE_OVERRIDES = {}

REPORT_4_GROUP_TOP_15 = "Top 15 Clients"
REPORT_4_GROUP_16_50 = "Clients 16 to 50"
REPORT_4_GROUP_51_100 = "Clients 51 to 100"
REPORT_4_GROUP_OTHER = "Other clients"
REPORT_4_TOTAL_LABEL = "Total Mexico"

# ---------------------------------------------------------
# REGLA DE EXCLUSIÓN REPORTE 4
# ---------------------------------------------------------
# En el Ranking de Clientes no deben considerarse ventas pertenecientes
# a estas categorías del material, replicando el filtro aplicado en la
# tabla dinámica de Excel.
REPORT_4_MATERIAL_CATEGORY_COLUMN_CANDIDATES = [
    "Categoría del Material",
    "Categoria del Material",
    "Categoría Material",
    "Categoria Material",
]

REPORT_4_EXCLUDED_MATERIAL_CATEGORY_CODES = [
    "O14",
    "O15",
    "O16",
    "O17",
]

REPORT_4_EXCLUDED_MATERIAL_CATEGORY_LABELS = [
    "O14: POP MATERIAL",
    "O15: RAW MATERIAL",
    "O16: FINANCIAL DISCOUNTS",
    "O17: PROVISIONS",
]

# ---------------------------------------------------------
# MENSAJES DE REPORTE 4
# ---------------------------------------------------------
MSG_REPORT_4_BUILD_SUCCESS = "Reporte 4 construido correctamente."
MSG_REPORT_4_BUILD_ERROR = "Ocurrió un error al construir el Reporte 4."
MSG_REPORT_4_BUILD_MISSING_FILES = (
    "Para construir el Reporte 4 primero debes tener ventas procesadas "
    "y plan por cliente cargado."
)



