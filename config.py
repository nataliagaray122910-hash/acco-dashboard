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
# CONFIGURACIÓN DE LOGIN TEMPORAL
# ---------------------------------------------------------
VALID_USERS = {
    "admin": "admin"
}

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
    "Reporte 1",
    "Reporte 2",
    "Reporte 3",
    "Reporte 4",
    "Base MTD",
]

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

# ---------------------------------------------------------
# TOOLTIPS DE BOTONES INDIVIDUALES
# ---------------------------------------------------------
EXPORT_REPORT_1_HELP = "Descargar Reporte 1"
EXPORT_REPORT_2_SEGMENT_HELP = "Descargar Segment x Region"
EXPORT_REPORT_2_CATEGORY_HELP = "Descargar Category"
EXPORT_REPORT_3_HELP = "Descargar Reporte 3"
EXPORT_REPORT_4_HELP = "Descargar Reporte 4"

# ---------------------------------------------------------
# NOMBRES DE HOJAS EXCEL
# ---------------------------------------------------------
EXPORT_SHEET_REPORT_1 = "Reporte 1"
EXPORT_SHEET_REPORT_2_SEGMENT = "Reporte 2 - Segment"
EXPORT_SHEET_REPORT_2_CATEGORY = "Reporte 2 - Category"
EXPORT_SHEET_REPORT_3 = "Reporte 3"
EXPORT_SHEET_REPORT_4 = "Reporte 4"

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
REPORT_1_MAIN_HEADING = "Canal Corporativo MTD / YTD"
REPORT_1_SUBHEADING = (
    "Comparativo ejecutivo entre Actual, Plan y PY para Canal Corporativo, "
    "separando ACCO + BARRILITO y KENS."
)

# ---------------------------------------------------------
# TEXTOS DE FILTROS - REPORTE 1
# ---------------------------------------------------------
REPORT_1_FILTER_WITHOUT_KENS_TITLE = "Filtro del bloque: Channel Corp WITHOUT KENS"
REPORT_1_FILTER_WITH_KENS_TITLE = "Filtro del bloque: Channel Corp WITH KENS"

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
REPORT_1_KENS_TOTAL_LABEL = "Total KENS"

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
    "GSNR",
]

REQUIRED_COLUMNS_REPORT_2_CATEGORY_PLAN_SKU = [
    "Corpo Category",
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
REPORT_3_MAIN_HEADING = "Desempeño Comercial por Canal"
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
REPORT_4_MAIN_HEADING = "Top 15 Clientes"
REPORT_4_SUBHEADING = (
    "Comparativo ejecutivo entre Actual, Plan y PY para los 15 clientes "
    "estratégicos definidos por el negocio, utilizando BASE SAP y Plan2026 by Client."
)

# ---------------------------------------------------------
# TEXTOS DE FILTROS - REPORTE 4
# ---------------------------------------------------------
REPORT_4_FILTER_TOP_CLIENTS_TITLE = "Filtro del bloque: Top 15 Clients"

# ---------------------------------------------------------
# COLUMNAS REQUERIDAS PARA REPORTE 4
# ---------------------------------------------------------
REQUIRED_COLUMNS_REPORT_4_SALES = [
    "Periodo",
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
    "Cliente",
    "Client",
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
    "Cliente",
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
# CLIENTES OBJETIVO DEL REPORTE 4
# ---------------------------------------------------------
REPORT_4_TOP_CLIENTS_ORDER = [
    "Abastecedora de Oficinas",
    "TONY Tiendas",
    "Nueva Walmart de México",
    "SAMS",
    "Super Papelera",
    "Casa de Papelería M",
    "AMAZON México",
    "DC Mayorista",
    "Mercado Libre",
    "Papelera del Norte de la Laguna",
    "La Hidalgo Mercería y Papelería",
    "Coriba & Cornejo",
    "Operadora OMX",
    "Merlín Paola Lopez Vázquez",
    "Proveedora Escolar",
]

# ---------------------------------------------------------
# REGLAS ESPECIALES DE CLIENTE
# ---------------------------------------------------------
REPORT_4_WALMART_CLIENT_CODES = [
    "C02468",
    "C01804",
    "C01628",
]

REPORT_4_SAMS_CLIENT_CODES = [
    "C00938",
]

REPORT_4_MERCADO_LIBRE_CLIENT_CODES = [
    "D00014",
]

# ---------------------------------------------------------
# HOMOLOGACIÓN VISUAL DE CLIENTES
# Esta estructura es solo interna del algoritmo.
# NO se mostrará en la visualización.
# ---------------------------------------------------------
REPORT_4_CLIENT_NAME_RULES = [
    {
        "display_name": "Abastecedora de Oficinas",
        "source_names": ["ABASTECEDORA DE OFICINAS"],
        "source_codes": [],
    },
    {
        "display_name": "TONY Tiendas",
        "source_names": ["TONY TIENDAS"],
        "source_codes": [],
    },
    {
        "display_name": "Nueva Walmart de México",
        "source_names": ["NUEVA WAL MART DE MEXICO"],
        "source_codes": ["C02468", "C01804", "C01628"],
    },
    {
        "display_name": "SAMS",
        "source_names": ["NUEVA WAL MART DE MEXICO"],
        "source_codes": ["C00938"],
    },
    {
        "display_name": "Super Papelera",
        "source_names": ["SUPER PAPELERA"],
        "source_codes": [],
    },
    {
        "display_name": "Casa de Papelería M",
        "source_names": ["CASA DE PAPELERIA M"],
        "source_codes": [],
    },
    {
        "display_name": "AMAZON México",
        "source_names": ["SERVICIOS COMERCIALES AMAZON MEXICO"],
        "source_codes": [],
    },
    {
        "display_name": "DC Mayorista",
        "source_names": ["DC MAYORISTA"],
        "source_codes": [],
    },
    {
        "display_name": "Mercado Libre",
        "source_names": ["PUBLICO EN GENERAL"],
        "source_codes": ["D00014"],
    },
    {
        "display_name": "Papelera del Norte de la Laguna",
        "source_names": ["PAPELERA DEL NORTE DE LA LAGUNA"],
        "source_codes": [],
    },
    {
        "display_name": "La Hidalgo Mercería y Papelería",
        "source_names": ["LA HIDALGO MERCERIA Y PAPELERIA"],
        "source_codes": [],
    },
    {
        "display_name": "Coriba & Cornejo",
        "source_names": ["CORIBA & CORNEJO"],
        "source_codes": [],
    },
    {
        "display_name": "Operadora OMX",
        "source_names": ["OPERADORA OMX"],
        "source_codes": [],
    },
    {
        "display_name": "Merlín Paola Lopez Vázquez",
        "source_names": ["MERLIN PAOLA LOPEZ VAZQUEZ"],
        "source_codes": [],
    },
    {
        "display_name": "Proveedora Escolar",
        "source_names": ["PROVEEDORA ESCOLAR"],
        "source_codes": [],
    },
]

REPORT_4_TOTAL_LABEL = "Total General"

# ---------------------------------------------------------
# MENSAJES DE REPORTE 4
# ---------------------------------------------------------
MSG_REPORT_4_BUILD_SUCCESS = "Reporte 4 construido correctamente."
MSG_REPORT_4_BUILD_ERROR = "Ocurrió un error al construir el Reporte 4."
MSG_REPORT_4_BUILD_MISSING_FILES = (
    "Para construir el Reporte 4 primero debes tener ventas procesadas "
    "y plan por cliente cargado."
)

