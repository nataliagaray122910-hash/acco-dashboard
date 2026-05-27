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
    "Canal Corporativo",
    "Segmento y Categoría",
    "Desempeño Comercial",
    "Ranking Clientes",
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
REPORT_4_MAIN_HEADING = "Ranking de Clientes"
REPORT_4_SUBHEADING = (
    "Comparativo ejecutivo MTD / YTD por cliente, respetando el orden fijo definido "
    "por negocio y cruzando Actual/PY/Plan por código de cliente."
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
REPORT_4_CLIENT_CATALOG = [
    {
        "code": "C01433",
        "source_name": "TONY TIENDAS",
        "display_name": "TONY TIENDAS",
        "top": 1
    },
    {
        "code": "C02359",
        "source_name": "ABASTECEDORA DE OFICINAS",
        "display_name": "ABASTECEDORA DE OFICINAS - Barrilito",
        "top": 2
    },
    {
        "code": "C00011",
        "source_name": "ABASTECEDORA DE OFICINAS",
        "display_name": "ABASTECEDORA DE OFICINAS - ACCO",
        "top": 3
    },
    {
        "code": "C00134",
        "source_name": "SUPER PAPELERA",
        "display_name": "SUPER PAPELERA",
        "top": 4
    },
    {
        "code": "C01819",
        "source_name": "SERVICIOS COMERCIALES AMAZON MEXICO",
        "display_name": "SERVICIOS COMERCIALES AMAZON MEXICO",
        "top": 5
    },
    {
        "code": "C00713",
        "source_name": "DC MAYORISTA",
        "display_name": "DC MAYORISTA",
        "top": 6
    },
    {
        "code": "D00014",
        "source_name": "PUBLICO EN GENERAL",
        "display_name": "MERCADO LIBRE",
        "top": 7
    },
    {
        "code": "C00017",
        "source_name": "PAPELERA DEL NORTE DE LA LAGUNA",
        "display_name": "PAPELERA DEL NORTE DE LA LAGUNA",
        "top": 8
    },
    {
        "code": "C02081",
        "source_name": "LA HIDALGO MERCERIA Y PAPELERIA",
        "display_name": "LA HIDALGO MERCERIA Y PAPELERIA",
        "top": 9
    },
    {
        "code": "C00938",
        "source_name": "NUEVA WAL MART DE MEXICO",
        "display_name": "SAMS",
        "top": 10
    },
    {
        "code": "C00068",
        "source_name": "PROVEEDORA ESCOLAR",
        "display_name": "PROVEEDORA ESCOLAR",
        "top": 11
    },
    {
        "code": "C02061",
        "source_name": "CORIBA & CORNEJO",
        "display_name": "CORIBA & CORNEJO",
        "top": 12
    },
    {
        "code": "C02073",
        "source_name": "GONZALEZ PEREIRA SOCIEDAD ANONIMA",
        "display_name": "GONZALEZ PEREIRA SOCIEDAD ANONIMA",
        "top": 13
    },
    {
        "code": "C00825",
        "source_name": "CASA DE PAPELERIA M",
        "display_name": "CASA DE PAPELERIA M - ACCO",
        "top": 14
    },
    {
        "code": "C02166",
        "source_name": "MERLIN PAOLA LOPEZ VAZQUEZ",
        "display_name": "MERLIN PAOLA LOPEZ VAZQUEZ",
        "top": 15
    },
    {
        "code": "C02128",
        "source_name": "OPERADORA OMX",
        "display_name": "OPERADORA OMX",
        "top": 16
    },
    {
        "code": "C00982",
        "source_name": "COMERCIAL TUKSONORA",
        "display_name": "COMERCIAL TUKSONORA",
        "top": 17
    },
    {
        "code": "C01628",
        "source_name": "NUEVA WAL MART DE MEXICO",
        "display_name": "SUPERCENTER",
        "top": 18
    },
    {
        "code": "C00044",
        "source_name": "SAN FELIPE ESCOLAR",
        "display_name": "SAN FELIPE ESCOLAR",
        "top": 19
    },
    {
        "code": "C00274",
        "source_name": "OFIX",
        "display_name": "OFIX",
        "top": 20
    },
    {
        "code": "C01052",
        "source_name": "GRUPO PAPELERO GUTIERREZ",
        "display_name": "GRUPO PAPELERO GUTIERREZ",
        "top": 21
    },
    {
        "code": "C02391",
        "source_name": "CASA DE PAPELERIA M",
        "display_name": "CASA DE PAPELERIA M - Barrilito",
        "top": 22
    },
    {
        "code": "C02106",
        "source_name": "ALVA PAPELERIA",
        "display_name": "ALVA PAPELERIA",
        "top": 23
    },
    {
        "code": "C00005",
        "source_name": "ABASTECEDORA LUMEN",
        "display_name": "ABASTECEDORA LUMEN",
        "top": 24
    },
    {
        "code": "C02239",
        "source_name": "ALHELI ZULEMA SANCHEZ ELIZONDO",
        "display_name": "ALHELI ZULEMA SANCHEZ ELIZONDO",
        "top": 25
    },
    {
        "code": "C00194",
        "source_name": "PRODUCCIONES CONTI",
        "display_name": "PRODUCCIONES CONTI",
        "top": 26
    },
    {
        "code": "C01805",
        "source_name": "SUPERMERCADOS INTERNACIONALES H E B",
        "display_name": "SUPERMERCADOS INTERNACIONALES H E B",
        "top": 27
    },
    {
        "code": "C01266",
        "source_name": "FORMAS EFICIENTES",
        "display_name": "FORMAS EFICIENTES",
        "top": 28
    },
    {
        "code": "C00057",
        "source_name": "ALMACEN PAPELERO SALDAÑA",
        "display_name": "ALMACEN PAPELERO SALDAÑA",
        "top": 29
    },
    {
        "code": "C02181",
        "source_name": "GRUPO COMERCIAL DSW",
        "display_name": "GRUPO COMERCIAL DSW",
        "top": 30
    },
    {
        "code": "C00381",
        "source_name": "COMERCIAL PAPELERA DE VICTORIA",
        "display_name": "COMERCIAL PAPELERA DE VICTORIA",
        "top": 31
    },
    {
        "code": "C01205",
        "source_name": "COMERCIALIZADORA COMPUTEL DEL SURES",
        "display_name": "COMERCIALIZADORA COMPUTEL DEL SURES",
        "top": 32
    },
    {
        "code": "C02125",
        "source_name": "INGRAM MICRO MEXICO",
        "display_name": "INGRAM MICRO MEXICO USD",
        "top": 33
    },
    {
        "code": "C02126",
        "source_name": "CORPORATIVO PAPELERO ANCE",
        "display_name": "CORPORATIVO PAPELERO ANCE",
        "top": 34
    },
    {
        "code": "C00591",
        "source_name": "JORGE LOPEZ LOPEZ",
        "display_name": "JORGE LOPEZ LOPEZ",
        "top": 35
    },
    {
        "code": "B13147",
        "source_name": "TIENDAS TRES B",
        "display_name": "TIENDAS TRES B",
        "top": 36
    },
    {
        "code": "C01727",
        "source_name": "LUIS ARTURO DEL REAL MONTEMAYOR",
        "display_name": "LUIS ARTURO DEL REAL MONTEMAYOR",
        "top": 37
    },
    {
        "code": "C09093",
        "source_name": "CIA. COMERCIAL CARIBE, C. POR A.",
        "display_name": "CIA. COMERCIAL CARIBE, C. POR A.",
        "top": 38
    },
    {
        "code": "C01804",
        "source_name": "NUEVA WAL MART DE MEXICO",
        "display_name": "BODEGA AURRERA",
        "top": 39
    },
    {
        "code": "C00039",
        "source_name": "TLAQUEPAQUE ESCOLAR",
        "display_name": "TLAQUEPAQUE ESCOLAR",
        "top": 40
    },
    {
        "code": "C02206",
        "source_name": "CT INTERNACIONAL DEL NOROESTE",
        "display_name": "CT INTERNACIONAL DEL NOROESTE",
        "top": 41
    },
    {
        "code": "C02158",
        "source_name": "TECHSMART MAYOREO",
        "display_name": "TECHSMART MAYOREO",
        "top": 42
    },
    {
        "code": "C00771",
        "source_name": "EXEL DEL NORTE",
        "display_name": "EXEL DEL NORTE",
        "top": 43
    },
    {
        "code": "C01734",
        "source_name": "DISTRIBUIDORES Y FABRICANTES DE",
        "display_name": "DISTRIBUIDORES Y FABRICANTES DE",
        "top": 44
    },
    {
        "code": "B12985",
        "source_name": "RUBIO DE B C",
        "display_name": "RUBIO DE B C",
        "top": 45
    },
    {
        "code": "C00304",
        "source_name": "INGRAM MICRO MEXICO",
        "display_name": "INGRAM MICRO MEXICO MXN",
        "top": 46
    },
    {
        "code": "C00040",
        "source_name": "RAMIRO LORENZO MENDOZA AGUILA",
        "display_name": "RAMIRO LORENZO MENDOZA AGUILA",
        "top": 47
    },
    {
        "code": "C02153",
        "source_name": "ENCUADERNACION GENERAL",
        "display_name": "ENCUADERNACION GENERAL",
        "top": 48
    },
    {
        "code": "C02318",
        "source_name": "RICARDO MATA VELAZQUEZ",
        "display_name": "RICARDO MATA VELAZQUEZ",
        "top": 49
    },
    {
        "code": "C09060",
        "source_name": "UTILES DE HONDURAS, S.A. DE C.V.",
        "display_name": "UTILES DE HONDURAS, S.A. DE C.V.",
        "top": 50
    },
    {
        "code": "C01193",
        "source_name": "EBENEZER PAPELERA",
        "display_name": "EBENEZER PAPELERA",
        "top": 51
    },
    {
        "code": "C02294",
        "source_name": "ENVASES Y EMPAQUES DEL PACIFICO",
        "display_name": "ENVASES Y EMPAQUES DEL PACIFICO",
        "top": 52
    },
    {
        "code": "C01541",
        "source_name": "CICOVISA",
        "display_name": "CICOVISA",
        "top": 53
    },
    {
        "code": "C02469",
        "source_name": "TECNOLOGIA SMARTBITT",
        "display_name": "TECNOLOGIA SMARTBITT USD",
        "top": 54
    },
    {
        "code": "B13687",
        "source_name": "NICOLAS HILARIO QUINTERO",
        "display_name": "NICOLAS HILARIO QUINTERO",
        "top": 55
    },
    {
        "code": "G47474",
        "source_name": "DISTRIBUIDORA PAPELERA DE TEHUACAN",
        "display_name": "DISTRIBUIDORA PAPELERA DE TEHUACAN",
        "top": 56
    },
    {
        "code": "C02291",
        "source_name": "COMERCIAL GARZA REYNA",
        "display_name": "COMERCIAL GARZA REYNA",
        "top": 57
    },
    {
        "code": "C00054",
        "source_name": "LA MARIPOSA DE LEON",
        "display_name": "LA MARIPOSA DE LEON",
        "top": 58
    },
    {
        "code": "B13990",
        "source_name": "JUAN CARLOS RODRIGUEZ PONCE",
        "display_name": "JUAN CARLOS RODRIGUEZ PONCE",
        "top": 59
    },
    {
        "code": "D00044",
        "source_name": "CLIENTE DUMMY Z44",
        "display_name": "CLIENTE DUMMY Z44",
        "top": 60
    },
    {
        "code": "C09021",
        "source_name": "LARACH Y CIA S. DE R.L. DE C.V.",
        "display_name": "LARACH Y CIA S. DE R.L. DE C.V.",
        "top": 61
    },
    {
        "code": "C00103",
        "source_name": "CENTRO PAPELERO MARVA",
        "display_name": "CENTRO PAPELERO MARVA",
        "top": 62
    },
    {
        "code": "C00066",
        "source_name": "DISTRIBUIDORA MAYORISTA DE OFICINAS",
        "display_name": "DISTRIBUIDORA MAYORISTA DE OFICINAS",
        "top": 63
    },
    {
        "code": "C02261",
        "source_name": "ZERO MUNDO PAPELERO",
        "display_name": "ZERO MUNDO PAPELERO",
        "top": 64
    },
    {
        "code": "C09069",
        "source_name": "CORPORACION FATIMA, S.A.",
        "display_name": "CORPORACION FATIMA, S.A.",
        "top": 65
    },
    {
        "code": "C09095",
        "source_name": "LIBRERIA Y PAPELERIA PROGRESO, S.A.",
        "display_name": "LIBRERIA Y PAPELERIA PROGRESO, S.A.",
        "top": 66
    },
    {
        "code": "C02149",
        "source_name": "SUSANA ALICIA RAMIREZ TRESS",
        "display_name": "SUSANA ALICIA RAMIREZ TRESS",
        "top": 67
    },
    {
        "code": "C02189",
        "source_name": "PAPELERIA EL CISNE DE ZAMORA",
        "display_name": "PAPELERIA EL CISNE DE ZAMORA",
        "top": 68
    },
    {
        "code": "C02209",
        "source_name": "MAYOREO DE PLUMAS",
        "display_name": "MAYOREO DE PLUMAS",
        "top": 69
    },
    {
        "code": "C00916",
        "source_name": "DEX DEL NOROESTE",
        "display_name": "DEX DEL NOROESTE",
        "top": 70
    },
    {
        "code": "C00035",
        "source_name": "GRUPO PAPELERAMA",
        "display_name": "GRUPO PAPELERAMA",
        "top": 71
    },
    {
        "code": "C01005",
        "source_name": "OFIMART DEL CENTRO",
        "display_name": "OFIMART DEL CENTRO",
        "top": 72
    },
    {
        "code": "C00428",
        "source_name": "DU PAPIER DISTRIBUIDORA PAPELERA",
        "display_name": "DU PAPIER DISTRIBUIDORA PAPELERA",
        "top": 73
    },
    {
        "code": "C00488",
        "source_name": "COSTCO DE MEXICO",
        "display_name": "COSTCO",
        "top": 74
    },
    {
        "code": "C02447",
        "source_name": "SG SOLUCIONES",
        "display_name": "SG SOLUCIONES",
        "top": 75
    },
    {
        "code": "C01391",
        "source_name": "LUZ LETICIA LOZA PEREZ",
        "display_name": "LUZ LETICIA LOZA PEREZ",
        "top": 76
    },
    {
        "code": "C01858",
        "source_name": "COMERCIAL CITY FRESKO",
        "display_name": "COMERCIAL CITY FRESKO",
        "top": 77
    },
    {
        "code": "B13337",
        "source_name": "COMERGALV",
        "display_name": "COMERGALV",
        "top": 78
    },
    {
        "code": "C00021",
        "source_name": "VAZQUEZ HERMANOS Y COMPAÑIA",
        "display_name": "VAZQUEZ HERMANOS Y COMPAÑIA",
        "top": 79
    },
    {
        "code": "B30005",
        "source_name": "OPERADORA FUTURAMA",
        "display_name": "OPERADORA FUTURAMA",
        "top": 80
    },
    {
        "code": "C02474",
        "source_name": "COMERCIALIZADORA DE VALOR AGREGADO",
        "display_name": "COMERCIALIZADORA DE VALOR AGREGADO USD",
        "top": 81
    },
    {
        "code": "B13872",
        "source_name": "PROVEEDORA DE NEGOCIOS SARO",
        "display_name": "PROVEEDORA DE NEGOCIOS SARO",
        "top": 82
    },
    {
        "code": "C02058",
        "source_name": "MUÑOZ CAMPOS",
        "display_name": "MUÑOZ CAMPOS",
        "top": 83
    },
    {
        "code": "C02406",
        "source_name": "SAMUEL RAMIREZ TENORIO",
        "display_name": "SAMUEL RAMIREZ TENORIO",
        "top": 84
    },
    {
        "code": "C00026",
        "source_name": "EL ALMACEN PAPELERIA",
        "display_name": "EL ALMACEN PAPELERIA",
        "top": 85
    },
    {
        "code": "C02093",
        "source_name": "YGNACIA CANDELARIA MARTINEZ URBINA",
        "display_name": "YGNACIA CANDELARIA MARTINEZ URBINA",
        "top": 86
    },
    {
        "code": "C02429",
        "source_name": "LUZ MARIA RAMIREZ CAMACHO",
        "display_name": "LUZ MARIA RAMIREZ CAMACHO",
        "top": 87
    },
    {
        "code": "C00013",
        "source_name": "UNION PAPELERA DE MEXICO",
        "display_name": "UNION PAPELERA DE MEXICO",
        "top": 88
    },
    {
        "code": "C00097",
        "source_name": "PAPELERIA EL IRIS DE JALAPA",
        "display_name": "PAPELERIA EL IRIS DE JALAPA",
        "top": 89
    },
    {
        "code": "C01826",
        "source_name": "SUPER GUTIERREZ",
        "display_name": "SUPER GUTIERREZ",
        "top": 90
    },
    {
        "code": "C01857",
        "source_name": "OPM PAPELERIA",
        "display_name": "OPM PAPELERIA",
        "top": 91
    },
    {
        "code": "C02098",
        "source_name": "PLATINO SOCIEDAD ANONIMA",
        "display_name": "PLATINO SOCIEDAD ANONIMA",
        "top": 92
    },
    {
        "code": "C00053",
        "source_name": "NEWBERRY Y COMPAÑIA",
        "display_name": "NEWBERRY Y COMPAÑIA",
        "top": 93
    },
    {
        "code": "C02102",
        "source_name": "ALADINO DE LOS MOCHIS",
        "display_name": "ALADINO DE LOS MOCHIS",
        "top": 94
    },
    {
        "code": "B10014",
        "source_name": "CASA DIAZ DE MAQUINAS DE COSER",
        "display_name": "CASA DIAZ DE MAQUINAS DE COSER",
        "top": 95
    },
    {
        "code": "B10031",
        "source_name": "CASA MARCUS",
        "display_name": "CASA MARCUS",
        "top": 96
    },
    {
        "code": "C02233",
        "source_name": "MER-PAP",
        "display_name": "MER-PAP",
        "top": 97
    },
    {
        "code": "D00011",
        "source_name": "CLIENTE DUMMY Z13 INDUSTRIAL",
        "display_name": "CLIENTE DUMMY Z13 INDUSTRIAL",
        "top": 98
    },
    {
        "code": "C02238",
        "source_name": "ARTURO GAMA DUFOUR",
        "display_name": "ARTURO GAMA DUFOUR",
        "top": 99
    },
    {
        "code": "C00043",
        "source_name": "PAPELERA PRINCIPADO",
        "display_name": "PAPELERA PRINCIPADO",
        "top": 100
    },
    {
        "code": "G47637",
        "source_name": "LA ESTRELLA DIVISION PAPELERIA",
        "display_name": "LA ESTRELLA DIVISION PAPELERIA",
        "top": 101
    },
    {
        "code": "C02145",
        "source_name": "ROSALBA LETICIA CAMILO GUTIERREZ",
        "display_name": "ROSALBA LETICIA CAMILO GUTIERREZ",
        "top": 102
    },
    {
        "code": "C09119",
        "source_name": "LIBRERIA E IMPRENTA VIVIAN SA",
        "display_name": "LIBRERIA E IMPRENTA VIVIAN SA",
        "top": 103
    },
    {
        "code": "C00699",
        "source_name": "PAPELERIA PERFUMERIA Y MERCERIA EL",
        "display_name": "PAPELERIA PERFUMERIA Y MERCERIA EL",
        "top": 104
    },
    {
        "code": "C02431",
        "source_name": "SOLUCIONES CORPORATIVAS BALHER",
        "display_name": "SOLUCIONES CORPORATIVAS BALHER",
        "top": 105
    },
    {
        "code": "C01684",
        "source_name": "EL NUEVO JAPON DE MEXICO",
        "display_name": "EL NUEVO JAPON DE MEXICO",
        "top": 106
    },
    {
        "code": "C00112",
        "source_name": "ROMANO DISTRIBUIDORA DE ARTICULOS",
        "display_name": "ROMANO DISTRIBUIDORA DE ARTICULOS",
        "top": 107
    },
    {
        "code": "B20074",
        "source_name": "ACCESORIOS PARA COMPUTADORAS Y OFIC",
        "display_name": "ACCESORIOS PARA COMPUTADORAS Y OFIC",
        "top": 108
    },
    {
        "code": "C00065",
        "source_name": "PAPELERA ANZURES",
        "display_name": "PAPELERA ANZURES",
        "top": 109
    },
    {
        "code": "C02116",
        "source_name": "PAPELERIA Y MERCERIA AMA",
        "display_name": "PAPELERIA Y MERCERIA AMA",
        "top": 110
    },
    {
        "code": "C00023",
        "source_name": "DISTRIBUIDORA GARDI",
        "display_name": "DISTRIBUIDORA GARDI",
        "top": 111
    },
    {
        "code": "C02218",
        "source_name": "JORGE BASILIO HAWACH CHARUR",
        "display_name": "JORGE BASILIO HAWACH CHARUR",
        "top": 112
    },
    {
        "code": "C02057",
        "source_name": "JAVIER BARBA GUERRERO",
        "display_name": "JAVIER BARBA GUERRERO",
        "top": 113
    },
    {
        "code": "B10564",
        "source_name": "PAPELERIA Y MERCERIA LA CANICA",
        "display_name": "PAPELERIA Y MERCERIA LA CANICA",
        "top": 114
    },
    {
        "code": "C00272",
        "source_name": "PROVEEDORA DE OFICINAS LA ESFERA DE",
        "display_name": "PROVEEDORA DE OFICINAS LA ESFERA DE",
        "top": 115
    },
    {
        "code": "C00016",
        "source_name": "PROVEEDORA DE IMPRENTAS",
        "display_name": "PROVEEDORA DE IMPRENTAS",
        "top": 116
    },
    {
        "code": "C02407",
        "source_name": "EL PUNTO FINO DE OAXACA DISTRIBUIDO",
        "display_name": "EL PUNTO FINO DE OAXACA DISTRIBUIDO",
        "top": 117
    },
    {
        "code": "B20538",
        "source_name": "EMPRESAS NOLASCO INC.",
        "display_name": "EMPRESAS NOLASCO INC.",
        "top": 118
    },
    {
        "code": "G18305",
        "source_name": "ABASTECEDOR CORPORATIVO",
        "display_name": "ABASTECEDOR CORPORATIVO",
        "top": 119
    },
    {
        "code": "B12897",
        "source_name": "PAPELERIA BREVA",
        "display_name": "PAPELERIA BREVA",
        "top": 120
    },
    {
        "code": "B30029",
        "source_name": "OPERADORA MERCO",
        "display_name": "OPERADORA MERCO",
        "top": 121
    },
    {
        "code": "C02334",
        "source_name": "HECTOR CASTILLO SANCHEZ",
        "display_name": "HECTOR CASTILLO SANCHEZ",
        "top": 122
    },
    {
        "code": "C02441",
        "source_name": "CONNECTED VENTURES MEXICO",
        "display_name": "CONNECTED VENTURES MEXICO",
        "top": 123
    },
    {
        "code": "B10404",
        "source_name": "JOSE ANGEL RANGEL RODRIGUEZ",
        "display_name": "JOSE ANGEL RANGEL RODRIGUEZ",
        "top": 124
    },
    {
        "code": "C01302",
        "source_name": "DISTRIBUIDORA DE MARCAS DEL CARIBE",
        "display_name": "DISTRIBUIDORA DE MARCAS DEL CARIBE",
        "top": 125
    },
    {
        "code": "C02172",
        "source_name": "PAPELERIA DANY",
        "display_name": "PAPELERIA DANY",
        "top": 126
    },
    {
        "code": "B10538",
        "source_name": "MERCERIA Y JUGUETERIA MONTERREY",
        "display_name": "MERCERIA Y JUGUETERIA MONTERREY",
        "top": 127
    },
    {
        "code": "C01189",
        "source_name": "GUARNERO SUMINISTROS PARA OFICINA",
        "display_name": "GUARNERO SUMINISTROS PARA OFICINA",
        "top": 128
    },
    {
        "code": "C01532",
        "source_name": "PROMOCIONES GRAFICAS MEXICANAS",
        "display_name": "PROMOCIONES GRAFICAS MEXICANAS",
        "top": 129
    },
    {
        "code": "C09271",
        "source_name": "REIMEX INTERNATIONAL LLC",
        "display_name": "REIMEX INTERNATIONAL LLC",
        "top": 130
    },
    {
        "code": "C02135",
        "source_name": "DISTRIBUIDORA PAPELERA NUPON",
        "display_name": "DISTRIBUIDORA PAPELERA NUPON",
        "top": 131
    },
    {
        "code": "C01859",
        "source_name": "PROVEEDORA DE SEGURIDAD INDUSTRIAL",
        "display_name": "PROVEEDORA DE SEGURIDAD INDUSTRIAL",
        "top": 132
    },
    {
        "code": "C02118",
        "source_name": "JOSE TRINIDAD AZPEITIA DE LA TORRE",
        "display_name": "JOSE TRINIDAD AZPEITIA DE LA TORRE",
        "top": 133
    },
    {
        "code": "C02297",
        "source_name": "MARCOS JIMENEZ GONZALEZ",
        "display_name": "MARCOS JIMENEZ GONZALEZ",
        "top": 134
    },
    {
        "code": "C01898",
        "source_name": "CONSORCIO GAVA",
        "display_name": "CONSORCIO GAVA",
        "top": 135
    },
    {
        "code": "C01082",
        "source_name": "PAPELERIA CONSUMIBLES Y ACCESORIOS",
        "display_name": "PAPELERIA CONSUMIBLES Y ACCESORIOS",
        "top": 136
    },
    {
        "code": "C00674",
        "source_name": "ZAPOPAN ESCOLAR",
        "display_name": "ZAPOPAN ESCOLAR",
        "top": 137
    },
    {
        "code": "C00009",
        "source_name": "PAPELERA DABO",
        "display_name": "PAPELERA DABO",
        "top": 138
    },
    {
        "code": "C02439",
        "source_name": "ARIANA CASTILLO RODRIGUEZ",
        "display_name": "ARIANA CASTILLO RODRIGUEZ",
        "top": 139
    },
    {
        "code": "B20112",
        "source_name": "LIBRERIA LENDOIRO PAPELERIA. CXA",
        "display_name": "LIBRERIA LENDOIRO PAPELERIA. CXA",
        "top": 140
    },
    {
        "code": "C02210",
        "source_name": "GRUPO EMPRESARIAL GOSE",
        "display_name": "GRUPO EMPRESARIAL GOSE",
        "top": 141
    },
    {
        "code": "C01844",
        "source_name": "MAYORISTAS EN PAPELERIA, EQUIPO DE",
        "display_name": "MAYORISTAS EN PAPELERIA, EQUIPO DE",
        "top": 142
    },
    {
        "code": "C02311",
        "source_name": "POSADAS & COLIN GRUPO PAPELERO",
        "display_name": "POSADAS & COLIN GRUPO PAPELERO",
        "top": 143
    },
    {
        "code": "C00436",
        "source_name": "PROVEEDORA PAPELERA KINO",
        "display_name": "PROVEEDORA PAPELERA KINO",
        "top": 144
    },
    {
        "code": "C01330",
        "source_name": "JUAN GUILLERMO VILLA SANCHEZ",
        "display_name": "JUAN GUILLERMO VILLA SANCHEZ",
        "top": 145
    },
    {
        "code": "C02389",
        "source_name": "MERCERIA CASA JIRASH",
        "display_name": "MERCERIA CASA JIRASH",
        "top": 146
    },
    {
        "code": "G56967",
        "source_name": "LA ESTRELLA DIVISION PAPELERIA ZARA",
        "display_name": "LA ESTRELLA DIVISION PAPELERIA ZARA",
        "top": 147
    },
    {
        "code": "C02258",
        "source_name": "SALDAÑA PAPELERIA",
        "display_name": "SALDAÑA PAPELERIA",
        "top": 148
    },
    {
        "code": "C00137",
        "source_name": "MARIA DE LOURDES MARIN RAMIREZ",
        "display_name": "MARIA DE LOURDES MARIN RAMIREZ",
        "top": 149
    },
    {
        "code": "C00038",
        "source_name": "MAYORISTA PAPELERA",
        "display_name": "MAYORISTA PAPELERA",
        "top": 150
    },
    {
        "code": "C02168",
        "source_name": "SERVICIO COMERCIAL GARIS",
        "display_name": "SERVICIO COMERCIAL GARIS",
        "top": 151
    },
    {
        "code": "G19020",
        "source_name": "BADAFI",
        "display_name": "BADAFI",
        "top": 152
    },
    {
        "code": "B10321",
        "source_name": "SEDERIA LA NUEVA",
        "display_name": "SEDERIA LA NUEVA",
        "top": 153
    },
    {
        "code": "C01771",
        "source_name": "TIENDAS GRAN D",
        "display_name": "TIENDAS GRAN D",
        "top": 154
    },
    {
        "code": "B10465",
        "source_name": "PAPELERIA ALAMEDA",
        "display_name": "PAPELERIA ALAMEDA",
        "top": 155
    },
    {
        "code": "C02388",
        "source_name": "ADRIAN LOPEZ DE LEON",
        "display_name": "ADRIAN LOPEZ DE LEON",
        "top": 156
    },
    {
        "code": "B14122",
        "source_name": "JUGUETE JUGUETON",
        "display_name": "JUGUETE JUGUETON",
        "top": 157
    },
    {
        "code": "C02405",
        "source_name": "HAALLEM EDUARDO CRUZ NOYOLA",
        "display_name": "HAALLEM EDUARDO CRUZ NOYOLA",
        "top": 158
    },
    {
        "code": "C01863",
        "source_name": "JESUS MANUEL BARBA GUERRERO",
        "display_name": "JESUS MANUEL BARBA GUERRERO",
        "top": 159
    },
    {
        "code": "C02289",
        "source_name": "PAPELERA VELSA DE MEXICO",
        "display_name": "PAPELERA VELSA DE MEXICO",
        "top": 160
    },
    {
        "code": "B14400",
        "source_name": "AISA COMPUTO Y PAPELERIA",
        "display_name": "AISA COMPUTO Y PAPELERIA",
        "top": 161
    },
    {
        "code": "C02436",
        "source_name": "BANCO SANTANDER MEXICO S.A.,",
        "display_name": "BANCO SANTANDER MEXICO S.A.,",
        "top": 162
    },
    {
        "code": "B10378",
        "source_name": "PAPELERIA Y MERCERIA GUERRA",
        "display_name": "PAPELERIA Y MERCERIA GUERRA",
        "top": 163
    },
    {
        "code": "B10030",
        "source_name": "EG TLAPALERO",
        "display_name": "EG TLAPALERO",
        "top": 164
    },
    {
        "code": "C02066",
        "source_name": "LIBRERIA PATRIA DE MONCLOVA",
        "display_name": "LIBRERIA PATRIA DE MONCLOVA",
        "top": 165
    },
    {
        "code": "C01785",
        "source_name": "JOSE HUMBERTO RODRIGUEZ",
        "display_name": "JOSE HUMBERTO RODRIGUEZ",
        "top": 166
    },
    {
        "code": "C02131",
        "source_name": "PAPELERIAS COLIBRI",
        "display_name": "PAPELERIAS COLIBRI",
        "top": 167
    },
    {
        "code": "C01864",
        "source_name": "LUIS PEREZ SANTIAGO",
        "display_name": "LUIS PEREZ SANTIAGO",
        "top": 168
    },
    {
        "code": "C02046",
        "source_name": "LEALGIL Y CIA",
        "display_name": "LEALGIL Y CIA",
        "top": 169
    },
    {
        "code": "C02032",
        "source_name": "COSTCO DE MEXICO",
        "display_name": "COSTCO ECO",
        "top": 170
    },
    {
        "code": "B10391",
        "source_name": "PAPELERIA MARON",
        "display_name": "PAPELERIA MARON",
        "top": 171
    },
    {
        "code": "C01585",
        "source_name": "OFILLEVA",
        "display_name": "OFILLEVA",
        "top": 172
    },
    {
        "code": "G56968",
        "source_name": "CORPORATIVO PAPELERO DEL SUR ESTREL",
        "display_name": "CORPORATIVO PAPELERO DEL SUR ESTREL",
        "top": 173
    },
    {
        "code": "B14381",
        "source_name": "COMERCIAL PAPELERA LA GRAN BE",
        "display_name": "COMERCIAL PAPELERA LA GRAN BE",
        "top": 174
    },
    {
        "code": "C01050",
        "source_name": "ALMACENES FARAH",
        "display_name": "ALMACENES FARAH",
        "top": 175
    },
    {
        "code": "B14329",
        "source_name": "IRAM MONTIEL YAÑEZ",
        "display_name": "IRAM MONTIEL YAÑEZ",
        "top": 176
    },
    {
        "code": "C02462",
        "source_name": "JICO INGENIERIA Y PROYECTOS ELECTRI",
        "display_name": "JICO INGENIERIA Y PROYECTOS ELECTRI",
        "top": 177
    },
    {
        "code": "C00122",
        "source_name": "COMERCIOS UNIDOS",
        "display_name": "COMERCIOS UNIDOS",
        "top": 178
    },
    {
        "code": "C02472",
        "source_name": "MARCO ANTONIO FRANCISCO",
        "display_name": "MARCO ANTONIO FRANCISCO",
        "top": 179
    },
    {
        "code": "B12883",
        "source_name": "ADOLFO RAMIREZ FUNCKE",
        "display_name": "ADOLFO RAMIREZ FUNCKE",
        "top": 180
    },
    {
        "code": "C00077",
        "source_name": "AVANCE Y TECNOLOGIA EN PLASTICOS",
        "display_name": "AVANCE Y TECNOLOGIA EN PLASTICOS",
        "top": 181
    },
    {
        "code": "C02065",
        "source_name": "EL GUERRERO PAPELERIA",
        "display_name": "EL GUERRERO PAPELERIA",
        "top": 182
    },
    {
        "code": "C02177",
        "source_name": "OPERADORA DE OFICINAS",
        "display_name": "OPERADORA DE OFICINAS",
        "top": 183
    },
    {
        "code": "C00049",
        "source_name": "PAPELERIA LAREDO",
        "display_name": "PAPELERIA LAREDO",
        "top": 184
    },
    {
        "code": "B13401",
        "source_name": "ECOPAPEL DE COMITAN",
        "display_name": "ECOPAPEL DE COMITAN",
        "top": 185
    },
    {
        "code": "C02152",
        "source_name": "ALBERTO PEDROZA GONZALEZ",
        "display_name": "ALBERTO PEDROZA GONZALEZ",
        "top": 186
    },
    {
        "code": "B13605",
        "source_name": "JOSE LUIS RUIZ MEJIA",
        "display_name": "JOSE LUIS RUIZ MEJIA",
        "top": 187
    },
    {
        "code": "C01890",
        "source_name": "TECNOLOGIA UNIVERSAL MITA",
        "display_name": "TECNOLOGIA UNIVERSAL MITA",
        "top": 188
    },
    {
        "code": "C02071",
        "source_name": "PAPELERIA ESPA&OLA DE MATAMOROS",
        "display_name": "PAPELERIA ESPA&OLA DE MATAMOROS",
        "top": 189
    },
    {
        "code": "B20072",
        "source_name": "ALMACEN EL AHORRO",
        "display_name": "ALMACEN EL AHORRO",
        "top": 190
    },
    {
        "code": "C00677",
        "source_name": "DISTRIBUIDORA PAPELERA MEXICO",
        "display_name": "DISTRIBUIDORA PAPELERA MEXICO",
        "top": 191
    },
    {
        "code": "C02316",
        "source_name": "DISTRIBUIDORA CHARUR",
        "display_name": "DISTRIBUIDORA CHARUR",
        "top": 192
    },
    {
        "code": "C02401",
        "source_name": "GEM VENTAS",
        "display_name": "GEM VENTAS",
        "top": 193
    },
    {
        "code": "C01780",
        "source_name": "MARIO CABALLERO GARCIA",
        "display_name": "MARIO CABALLERO GARCIA",
        "top": 194
    },
    {
        "code": "C02454",
        "source_name": "TECNOLOGIA SMARTBITT",
        "display_name": "TECNOLOGIA SMARTBITT  MXN",
        "top": 195
    },
    {
        "code": "C02055",
        "source_name": "OFIBIZMART",
        "display_name": "OFIBIZMART",
        "top": 196
    },
    {
        "code": "C00506",
        "source_name": "WILCON INGENIERIA Y DIBUJO",
        "display_name": "WILCON INGENIERIA Y DIBUJO",
        "top": 197
    },
    {
        "code": "B13638",
        "source_name": "ALICIA MUÑOZ GONZALEZ",
        "display_name": "ALICIA MUÑOZ GONZALEZ",
        "top": 198
    },
    {
        "code": "C02385",
        "source_name": "OPERADORA EMPRESARIAL IZVA",
        "display_name": "OPERADORA EMPRESARIAL IZVA",
        "top": 199
    },
    {
        "code": "B10799",
        "source_name": "MARIA IDALIA JARAMILLO CARRIZALES",
        "display_name": "MARIA IDALIA JARAMILLO CARRIZALES",
        "top": 200
    },
    {
        "code": "G47297",
        "source_name": "JOSE HERIBERTO ALMADA HERNANDEZ",
        "display_name": "JOSE HERIBERTO ALMADA HERNANDEZ",
        "top": 201
    },
    {
        "code": "C09251",
        "source_name": "THE BUSINESS SUPPLY GROUP LTD",
        "display_name": "THE BUSINESS SUPPLY GROUP LTD",
        "top": 202
    },
    {
        "code": "B14337",
        "source_name": "LUCIA DE LOURDES CANCINO LIEVANO",
        "display_name": "LUCIA DE LOURDES CANCINO LIEVANO",
        "top": 203
    },
    {
        "code": "C01701",
        "source_name": "DISTRIBUIDORA GUERRA",
        "display_name": "DISTRIBUIDORA GUERRA",
        "top": 204
    },
    {
        "code": "C02038",
        "source_name": "GRUPO LYPRO",
        "display_name": "GRUPO LYPRO",
        "top": 205
    },
    {
        "code": "C00875",
        "source_name": "FELIX NEVAREZ ARREDONDO",
        "display_name": "FELIX NEVAREZ ARREDONDO",
        "top": 206
    },
    {
        "code": "C02308",
        "source_name": "MERCERIA Y PAPELERIA",
        "display_name": "MERCERIA Y PAPELERIA",
        "top": 207
    },
    {
        "code": "G57016",
        "source_name": "ALPHA DIGITAL",
        "display_name": "ALPHA DIGITAL",
        "top": 208
    },
    {
        "code": "B11490",
        "source_name": "PAPELERIA SALAMAN",
        "display_name": "PAPELERIA SALAMAN",
        "top": 209
    },
    {
        "code": "C02356",
        "source_name": "THEOFFER",
        "display_name": "THEOFFER",
        "top": 210
    },
    {
        "code": "C01781",
        "source_name": "MAPEQ MAYORISTAS EN PAPELERIA",
        "display_name": "MAPEQ MAYORISTAS EN PAPELERIA",
        "top": 211
    },
    {
        "code": "C01185",
        "source_name": "JOSE ARTURO GONZALEZ CRISTERNA",
        "display_name": "JOSE ARTURO GONZALEZ CRISTERNA",
        "top": 212
    },
    {
        "code": "B10034",
        "source_name": "FERRETERA KIMURA",
        "display_name": "FERRETERA KIMURA",
        "top": 213
    },
    {
        "code": "C01897",
        "source_name": "ABASTECEDORA OLINKA",
        "display_name": "ABASTECEDORA OLINKA",
        "top": 214
    },
    {
        "code": "C02245",
        "source_name": "RAFAEL SANCHEZ JUAREZ",
        "display_name": "RAFAEL SANCHEZ JUAREZ",
        "top": 215
    },
    {
        "code": "B13342",
        "source_name": "CONCEPCION GONZALEZ GOMEZ",
        "display_name": "CONCEPCION GONZALEZ GOMEZ",
        "top": 216
    },
    {
        "code": "C02240",
        "source_name": "PAPELERIA ROMAPAVE",
        "display_name": "PAPELERIA ROMAPAVE",
        "top": 217
    },
    {
        "code": "C01602",
        "source_name": "SERVICIOS DIGIREY",
        "display_name": "SERVICIOS DIGIREY",
        "top": 218
    },
    {
        "code": "B11128",
        "source_name": "MARIA GUADALUPE CHAVEZ REGALADO",
        "display_name": "MARIA GUADALUPE CHAVEZ REGALADO",
        "top": 219
    },
    {
        "code": "C02392",
        "source_name": "GGRIDIGEM",
        "display_name": "GGRIDIGEM",
        "top": 220
    },
    {
        "code": "C02070",
        "source_name": "GRUPO HILBURN",
        "display_name": "GRUPO HILBURN",
        "top": 221
    },
    {
        "code": "C00060",
        "source_name": "PAPELERIA Y LIBRERIA PATRIA DE MONT",
        "display_name": "PAPELERIA Y LIBRERIA PATRIA DE MONT",
        "top": 222
    },
    {
        "code": "C02315",
        "source_name": "CONSORCIO INFINITY HERSI",
        "display_name": "CONSORCIO INFINITY HERSI",
        "top": 223
    },
    {
        "code": "C09133",
        "source_name": "ACCO BRANDS CHILE S.A.",
        "display_name": "ACCO BRANDS CHILE S.A.",
        "top": 224
    },
    {
        "code": "",
        "source_name": "ACCO BRANDS CHILE SpA.",
        "display_name": "ACCO BRANDS CHILE SpA.",
        "top": 225
    },
    {
        "code": "C01401",
        "source_name": "PAPELERIA LOZANO HERMANOS",
        "display_name": "PAPELERIA LOZANO HERMANOS",
        "top": 226
    },
    {
        "code": "C02396",
        "source_name": "JESSICA HANNAH CRUZ HEDGES",
        "display_name": "JESSICA HANNAH CRUZ HEDGES",
        "top": 227
    },
    {
        "code": "B13541",
        "source_name": "TERESA DE JESUS MARTINEZ DE LA CRUZ",
        "display_name": "TERESA DE JESUS MARTINEZ DE LA CRUZ",
        "top": 228
    },
    {
        "code": "B13714",
        "source_name": "SERGIO MARTIN LOPEZ GARCIA",
        "display_name": "SERGIO MARTIN LOPEZ GARCIA",
        "top": 229
    },
    {
        "code": "C02282",
        "source_name": "R. MERCANTILES S.C.C",
        "display_name": "R. MERCANTILES S.C.C",
        "top": 230
    },
    {
        "code": "B13992",
        "source_name": "ISAC SURIANO NIÑO",
        "display_name": "ISAC SURIANO NIÑO",
        "top": 231
    },
    {
        "code": "B13738",
        "source_name": "CITLALLI MEZA CARDENAS",
        "display_name": "CITLALLI MEZA CARDENAS",
        "top": 232
    },
    {
        "code": "C02225",
        "source_name": "DISTRIBUIDORA OC MEXICO",
        "display_name": "DISTRIBUIDORA OC MEXICO",
        "top": 233
    },
    {
        "code": "B14104",
        "source_name": "CESAR OSVALDO BARBA GUERRERO",
        "display_name": "CESAR OSVALDO BARBA GUERRERO",
        "top": 234
    },
    {
        "code": "C02198",
        "source_name": "EDUARDO NIETO RUIZ",
        "display_name": "EDUARDO NIETO RUIZ",
        "top": 235
    },
    {
        "code": "C02361",
        "source_name": "CESAR AUGUSTO VEGA MADRID",
        "display_name": "CESAR AUGUSTO VEGA MADRID",
        "top": 236
    },
    {
        "code": "B14308",
        "source_name": "ARMANDO CORDOVA ARENAS",
        "display_name": "ARMANDO CORDOVA ARENAS",
        "top": 237
    },
    {
        "code": "B11119",
        "source_name": "BELEN LEZAMA",
        "display_name": "BELEN LEZAMA",
        "top": 238
    },
    {
        "code": "(blank)",
        "source_name": "VENTA A EMPLEADOS",
        "display_name": "VENTA A EMPLEADOS",
        "top": 239
    },
    {
        "code": "C02176",
        "source_name": "TIENDAS PAPERIX",
        "display_name": "TIENDAS PAPERIX",
        "top": 241
    },
    {
        "code": "C00080",
        "source_name": "EL NORTE PAPELERIA",
        "display_name": "EL NORTE PAPELERIA",
        "top": 242
    },
    {
        "code": "C02151",
        "source_name": "JESUS RAMIREZ ANDRADE",
        "display_name": "JESUS RAMIREZ ANDRADE",
        "top": 243
    },
    {
        "code": "B10325",
        "source_name": "MERCERIA REGINA",
        "display_name": "MERCERIA REGINA",
        "top": 244
    },
    {
        "code": "C02234",
        "source_name": "DIANA GUADALUPE PEREA BARRIOS",
        "display_name": "DIANA GUADALUPE PEREA BARRIOS",
        "top": 245
    },
    {
        "code": "B10794",
        "source_name": "FERRE PAT",
        "display_name": "FERRE PAT",
        "top": 246
    },
    {
        "code": "C00249",
        "source_name": "PAPELERA CUAUHTEMOC DE TOLUCA",
        "display_name": "PAPELERA CUAUHTEMOC DE TOLUCA",
        "top": 247
    },
    {
        "code": "B10494",
        "source_name": "PAPELERIA SARACHO",
        "display_name": "PAPELERIA SARACHO",
        "top": 248
    },
    {
        "code": "C02269",
        "source_name": "ENRIQUE CHEVAILE ABAD",
        "display_name": "ENRIQUE CHEVAILE ABAD",
        "top": 249
    },
    {
        "code": "B12734",
        "source_name": "PAPELERIA MODERNA",
        "display_name": "PAPELERIA MODERNA",
        "top": 250
    },
    {
        "code": "C02403",
        "source_name": "ELISA RAMIREZ MICHEL",
        "display_name": "ELISA RAMIREZ MICHEL",
        "top": 251
    },
    {
        "code": "C00472",
        "source_name": "GRUPO LEBA",
        "display_name": "GRUPO LEBA",
        "top": 252
    },
    {
        "code": "B12945",
        "source_name": "MERCERIA ARMENTA",
        "display_name": "MERCERIA ARMENTA",
        "top": 253
    },
    {
        "code": "B13172",
        "source_name": "FRANCISCO JUAN PABLO BECERRA ALCACI",
        "display_name": "FRANCISCO JUAN PABLO BECERRA ALCACI",
        "top": 254
    },
    {
        "code": "C02129",
        "source_name": "DUMGAR",
        "display_name": "DUMGAR",
        "top": 255
    },
    {
        "code": "C00191",
        "source_name": "PAPELERIA FOYO",
        "display_name": "PAPELERIA FOYO",
        "top": 256
    },
    {
        "code": "C01855",
        "source_name": "SUPER FARMACIA LEON",
        "display_name": "SUPER FARMACIA LEON",
        "top": 257
    },
    {
        "code": "B10708",
        "source_name": "MERCERIA Y JUGUETERIA EL LEON",
        "display_name": "MERCERIA Y JUGUETERIA EL LEON",
        "top": 258
    },
    {
        "code": "B11278",
        "source_name": "PAPELANDIA",
        "display_name": "PAPELANDIA",
        "top": 259
    },
    {
        "code": "D00002",
        "source_name": "CLIENTE DUMMY ST Z14",
        "display_name": "CLIENTE DUMMY ST Z14",
        "top": 260
    },
    {
        "code": "C02278",
        "source_name": "BOTICA GUADALUPE DE PARRAL",
        "display_name": "BOTICA GUADALUPE DE PARRAL",
        "top": 261
    },
    {
        "code": "C02345",
        "source_name": "JORGE AZPEITIA DE LA TORRE",
        "display_name": "JORGE AZPEITIA DE LA TORRE",
        "top": 262
    },
    {
        "code": "C02243",
        "source_name": "F. DOMENE Y SOCIOS",
        "display_name": "F. DOMENE Y SOCIOS",
        "top": 263
    },
    {
        "code": "C02112",
        "source_name": "EVA RESENDIZ RIOS",
        "display_name": "EVA RESENDIZ RIOS",
        "top": 264
    },
    {
        "code": "C02309",
        "source_name": "HENKI IX DISTRIBUCIONES",
        "display_name": "HENKI IX DISTRIBUCIONES",
        "top": 265
    },
    {
        "code": "C00403",
        "source_name": "PAPELERIA TURIN",
        "display_name": "PAPELERIA TURIN",
        "top": 266
    },
    {
        "code": "B13041",
        "source_name": "MARTHA GUADALUPE CRUZ SANCHEZ",
        "display_name": "MARTHA GUADALUPE CRUZ SANCHEZ",
        "top": 267
    },
    {
        "code": "C00092",
        "source_name": "ABC PAPELERIAS Y SERVICIOS",
        "display_name": "ABC PAPELERIAS Y SERVICIOS",
        "top": 268
    },
    {
        "code": "C02017",
        "source_name": "SISCOPRINT",
        "display_name": "SISCOPRINT",
        "top": 269
    },
    {
        "code": "B14317",
        "source_name": "FERRETODO M.R.O.",
        "display_name": "FERRETODO M.R.O.",
        "top": 270
    },
    {
        "code": "C02281",
        "source_name": "GRUPO PAPELERO RIED",
        "display_name": "GRUPO PAPELERO RIED",
        "top": 271
    },
    {
        "code": "B14414",
        "source_name": "OPERADORA DE SOLUCIONES PAPIRA",
        "display_name": "OPERADORA DE SOLUCIONES PAPIRA",
        "top": 272
    },
    {
        "code": "B10672",
        "source_name": "ORGANIZACION PAPELERA OMEGA",
        "display_name": "ORGANIZACION PAPELERA OMEGA",
        "top": 273
    },
    {
        "code": "C02268",
        "source_name": "FLORENCIO CAZARES Y COMPAÑIA",
        "display_name": "FLORENCIO CAZARES Y COMPAÑIA",
        "top": 274
    },
    {
        "code": "C02043",
        "source_name": "THORO ENTERPRISES DE MEXICO",
        "display_name": "THORO ENTERPRISES DE MEXICO",
        "top": 275
    },
    {
        "code": "B13696",
        "source_name": "VICTOR UGO CRUZ MOTA",
        "display_name": "VICTOR UGO CRUZ MOTA",
        "top": 276
    },
    {
        "code": "C02105",
        "source_name": "RICARDO ALBERTO ROJAS JIMENEZ",
        "display_name": "RICARDO ALBERTO ROJAS JIMENEZ",
        "top": 277
    },
    {
        "code": "C02473",
        "source_name": "COMERCIALIZADORA DE VALOR AGREGADO",
        "display_name": "COMERCIALIZADORA DE VALOR AGREGADO   MXN",
        "top": 278
    },
    {
        "code": "C02075",
        "source_name": "LUIS ARTURO ESQUIVEL GRACIDA",
        "display_name": "LUIS ARTURO ESQUIVEL GRACIDA",
        "top": 279
    },
    {
        "code": "C02036",
        "source_name": "LONDON INTEGRATION",
        "display_name": "LONDON INTEGRATION",
        "top": 280
    },
    {
        "code": "C02167",
        "source_name": "ARISTEO LLAVEN TOLEDO",
        "display_name": "ARISTEO LLAVEN TOLEDO",
        "top": 281
    },
    {
        "code": "C01519",
        "source_name": "OFFICENTER DE FRONTERA",
        "display_name": "OFFICENTER DE FRONTERA",
        "top": 282
    },
    {
        "code": "C02067",
        "source_name": "ARTURO VALDES PEREZ",
        "display_name": "ARTURO VALDES PEREZ",
        "top": 283
    },
    {
        "code": "B14030",
        "source_name": "ANTONIO CEJA MARON",
        "display_name": "ANTONIO CEJA MARON",
        "top": 284
    },
    {
        "code": "C02230",
        "source_name": "DANIELA MORALES TRINIDAD",
        "display_name": "DANIELA MORALES TRINIDAD",
        "top": 285
    },
    {
        "code": "C00647",
        "source_name": "PATRICIA MARIA MALDONADO TIRADO",
        "display_name": "PATRICIA MARIA MALDONADO TIRADO",
        "top": 286
    },
    {
        "code": "C02366",
        "source_name": "MIGUEL ALEJANDRO TUZ AGUILAR",
        "display_name": "MIGUEL ALEJANDRO TUZ AGUILAR",
        "top": 287
    },
    {
        "code": "C00076",
        "source_name": "PAPELERIA Y LIBRERIA CENTRAL DE",
        "display_name": "PAPELERIA Y LIBRERIA CENTRAL DE",
        "top": 288
    },
    {
        "code": "D00007",
        "source_name": "CLIENTE DUMMY Z15 DESC 43%",
        "display_name": "CLIENTE DUMMY Z15 DESC 43%",
        "top": 289
    },
    {
        "code": "C02363",
        "source_name": "BRAULIO CAMACHO VELAZQUEZ",
        "display_name": "BRAULIO CAMACHO VELAZQUEZ",
        "top": 290
    },
    {
        "code": "C00628",
        "source_name": "CLIP'S MART",
        "display_name": "CLIP'S MART",
        "top": 291
    },
    {
        "code": "B30074",
        "source_name": "TIENDAS GARCES",
        "display_name": "TIENDAS GARCES",
        "top": 292
    },
    {
        "code": "B13742",
        "source_name": "DISTRIBUCION VACEDEC",
        "display_name": "DISTRIBUCION VACEDEC",
        "top": 293
    },
    {
        "code": "C02440",
        "source_name": "TECH SOLUTIONS GROUP S.A.",
        "display_name": "TECH SOLUTIONS GROUP S.A.",
        "top": 294
    },
    {
        "code": "B10527",
        "source_name": "FERRETERA ELIZONDO HERMANOS",
        "display_name": "FERRETERA ELIZONDO HERMANOS",
        "top": 295
    },
    {
        "code": "C02419",
        "source_name": "101 Biz, Inc",
        "display_name": "101 Biz, Inc",
        "top": 296
    },
    {
        "code": "C02127",
        "source_name": "PAQUIN",
        "display_name": "PAQUIN",
        "top": 297
    },
    {
        "code": "G46853",
        "source_name": "BLUE AND WHITE DE MONTERREY",
        "display_name": "BLUE AND WHITE DE MONTERREY",
        "top": 298
    },
    {
        "code": "C02390",
        "source_name": "ZAZUETA COMERCIAL DE HERMOSILLO",
        "display_name": "ZAZUETA COMERCIAL DE HERMOSILLO",
        "top": 299
    },
    {
        "code": "B13706",
        "source_name": "FRANCISCO JAVIER ESPINOSA CRUZ",
        "display_name": "FRANCISCO JAVIER ESPINOSA CRUZ",
        "top": 300
    },
    {
        "code": "B10687",
        "source_name": "MA. DE LOURDES AGUILERA ESCOBAR",
        "display_name": "MA. DE LOURDES AGUILERA ESCOBAR",
        "top": 301
    },
    {
        "code": "C02314",
        "source_name": "PROVEEDORA DE OFICINAS Y DESPACHOS",
        "display_name": "PROVEEDORA DE OFICINAS Y DESPACHOS",
        "top": 302
    },
    {
        "code": "B10524",
        "source_name": "EL NUEVO MUNDO MONTERREY",
        "display_name": "EL NUEVO MUNDO MONTERREY",
        "top": 303
    },
    {
        "code": "C00162",
        "source_name": "LIBRERIAS GONVILL",
        "display_name": "LIBRERIAS GONVILL",
        "top": 304
    },
    {
        "code": "C02107",
        "source_name": "COMERCIAL AMERICA DE ZAMORA",
        "display_name": "COMERCIAL AMERICA DE ZAMORA",
        "top": 305
    },
    {
        "code": "C00669",
        "source_name": "PAPELERIA RUY SANCHEZ",
        "display_name": "PAPELERIA RUY SANCHEZ",
        "top": 306
    },
    {
        "code": "C00898",
        "source_name": "MARIO ORDAZ LEON",
        "display_name": "MARIO ORDAZ LEON",
        "top": 307
    },
    {
        "code": "C02346",
        "source_name": "COMERCIALIZADORA Y PAPELERIA JFM",
        "display_name": "COMERCIALIZADORA Y PAPELERIA JFM",
        "top": 308
    },
    {
        "code": "C02322",
        "source_name": "BLANCA MIRLA BAUTISTA CALDERON",
        "display_name": "BLANCA MIRLA BAUTISTA CALDERON",
        "top": 309
    },
    {
        "code": "C02350",
        "source_name": "PAPELERIA KARLITA",
        "display_name": "PAPELERIA KARLITA",
        "top": 310
    },
    {
        "code": "B11098",
        "source_name": "RAQUEL MIREYA LOPEZ VAZQUEZ",
        "display_name": "RAQUEL MIREYA LOPEZ VAZQUEZ",
        "top": 311
    },
    {
        "code": "C01707",
        "source_name": "COFI GRUPO PAPELERO",
        "display_name": "COFI GRUPO PAPELERO",
        "top": 312
    },
    {
        "code": "C02186",
        "source_name": "ANSELMO HERNANDEZ SOLANO",
        "display_name": "ANSELMO HERNANDEZ SOLANO",
        "top": 313
    },
    {
        "code": "C01757",
        "source_name": "LA BODEGUITA DE LOS SUEÑOS",
        "display_name": "LA BODEGUITA DE LOS SUEÑOS",
        "top": 314
    },
    {
        "code": "G41043",
        "source_name": "IRMA AIDA RODRIGUEZ COTA",
        "display_name": "IRMA AIDA RODRIGUEZ COTA",
        "top": 315
    },
    {
        "code": "B12851",
        "source_name": "LIBRERIA RAMIREZ JUGUETILANDIA",
        "display_name": "LIBRERIA RAMIREZ JUGUETILANDIA",
        "top": 316
    },
    {
        "code": "B10035",
        "source_name": "FERRETERIA LA LIBRA",
        "display_name": "FERRETERIA LA LIBRA",
        "top": 317
    },
    {
        "code": "C02448",
        "source_name": "RAUL ALBERTO HERNANDEZ PEREZ",
        "display_name": "RAUL ALBERTO HERNANDEZ PEREZ",
        "top": 318
    },
    {
        "code": "B14277",
        "source_name": "JOSE FRANCISCO HERNANDEZ LEON",
        "display_name": "JOSE FRANCISCO HERNANDEZ LEON",
        "top": 319
    },
    {
        "code": "B11518",
        "source_name": "ANA ISABEL CASTRO GARZA",
        "display_name": "ANA ISABEL CASTRO GARZA",
        "top": 320
    },
    {
        "code": "C02270",
        "source_name": "MONICA SANCHEZ RODRIGUEZ",
        "display_name": "MONICA SANCHEZ RODRIGUEZ",
        "top": 321
    },
    {
        "code": "B14327",
        "source_name": "CINTHIA LIZETH DAVILA GONZALEZ",
        "display_name": "CINTHIA LIZETH DAVILA GONZALEZ",
        "top": 322
    },
    {
        "code": "B11052",
        "source_name": "EL SURTIDOR DEL TAPICERO",
        "display_name": "EL SURTIDOR DEL TAPICERO",
        "top": 323
    },
    {
        "code": "B10980",
        "source_name": "TOMAS ENRIQUE ALTAMIRANO ROCHA",
        "display_name": "TOMAS ENRIQUE ALTAMIRANO ROCHA",
        "top": 324
    },
    {
        "code": "B13545",
        "source_name": "SILVIA SUSANA VELOZ NUÑEZ",
        "display_name": "SILVIA SUSANA VELOZ NUÑEZ",
        "top": 325
    },
    {
        "code": "C01703",
        "source_name": "COMERCIALIZADORA ZEGUIZ",
        "display_name": "COMERCIALIZADORA ZEGUIZ",
        "top": 326
    },
    {
        "code": "C02162",
        "source_name": "EL ESCRITORIO MODERNO",
        "display_name": "EL ESCRITORIO MODERNO",
        "top": 327
    },
    {
        "code": "B11308",
        "source_name": "PAPELERIA Y VARIOS",
        "display_name": "PAPELERIA Y VARIOS",
        "top": 328
    },
    {
        "code": "B10639",
        "source_name": "VIDRIO ELECTRICA DE PATZCUARO",
        "display_name": "VIDRIO ELECTRICA DE PATZCUARO",
        "top": 329
    },
    {
        "code": "B10381",
        "source_name": "CARLOS RICARDO ALANIS GALINDO",
        "display_name": "CARLOS RICARDO ALANIS GALINDO",
        "top": 330
    },
    {
        "code": "C02154",
        "source_name": "PAPELERIA LOS AMATES",
        "display_name": "PAPELERIA LOS AMATES",
        "top": 331
    },
    {
        "code": "G42485",
        "source_name": "ADELA BLANCAS GONZALEZ",
        "display_name": "ADELA BLANCAS GONZALEZ",
        "top": 332
    },
    {
        "code": "C02097",
        "source_name": "REY EDUARDO ZAMBRANO HERNANDEZ",
        "display_name": "REY EDUARDO ZAMBRANO HERNANDEZ",
        "top": 333
    },
    {
        "code": "C02254",
        "source_name": "GENNY ROCIO DEL ROSARIO CERON MENDO",
        "display_name": "GENNY ROCIO DEL ROSARIO CERON MENDO",
        "top": 334
    },
    {
        "code": "C01016",
        "source_name": "SHARP SAN LUIS",
        "display_name": "SHARP SAN LUIS",
        "top": 335
    },
    {
        "code": "B13305",
        "source_name": "JUANA ACEVEDO RODRIGUEZ",
        "display_name": "JUANA ACEVEDO RODRIGUEZ",
        "top": 336
    },
    {
        "code": "C01314",
        "source_name": "DISTRIBUIDORA PROESA",
        "display_name": "DISTRIBUIDORA PROESA",
        "top": 337
    },
    {
        "code": "B10963",
        "source_name": "MIREYA",
        "display_name": "MIREYA",
        "top": 338
    },
    {
        "code": "C02374",
        "source_name": "DISTRIBUIDORA EL TIGRE DEL SURESTE",
        "display_name": "DISTRIBUIDORA EL TIGRE DEL SURESTE",
        "top": 339
    },
    {
        "code": "C02271",
        "source_name": "RODRIGO MANZO FOYO",
        "display_name": "RODRIGO MANZO FOYO",
        "top": 340
    },
    {
        "code": "C00774",
        "source_name": "GRUPO COMERCIALIZADOR PAPELERO MATI",
        "display_name": "GRUPO COMERCIALIZADOR PAPELERO MATI",
        "top": 341
    },
    {
        "code": "C02164",
        "source_name": "OFIMEX PAPELERA",
        "display_name": "OFIMEX PAPELERA",
        "top": 342
    },
    {
        "code": "B10382",
        "source_name": "DISTRIBUIDORA DE MERCERIA",
        "display_name": "DISTRIBUIDORA DE MERCERIA",
        "top": 343
    },
    {
        "code": "B20086",
        "source_name": "LIBRERIA SAN JERONIMO",
        "display_name": "LIBRERIA SAN JERONIMO",
        "top": 344
    },
    {
        "code": "C00707",
        "source_name": "PRONTO PAPER DISTRIBUIDORES",
        "display_name": "PRONTO PAPER DISTRIBUIDORES",
        "top": 345
    },
    {
        "code": "B13723",
        "source_name": "MIGUEL ANGEL LOPEZ CASTRO",
        "display_name": "MIGUEL ANGEL LOPEZ CASTRO",
        "top": 346
    },
    {
        "code": "C02296",
        "source_name": "JUAN CARLOS VAZQUEZ VAZQUEZ",
        "display_name": "JUAN CARLOS VAZQUEZ VAZQUEZ",
        "top": 347
    },
    {
        "code": "B10998",
        "source_name": "PAPELERIA ELIZABETH",
        "display_name": "PAPELERIA ELIZABETH",
        "top": 348
    },
    {
        "code": "B13848",
        "source_name": "CARDA SAR Y SELECTA",
        "display_name": "CARDA SAR Y SELECTA",
        "top": 349
    },
    {
        "code": "C09437",
        "source_name": "FARMACIAS ARROCHA S.A.",
        "display_name": "FARMACIAS ARROCHA S.A.",
        "top": 350
    },
    {
        "code": "C02136",
        "source_name": "PROVEEDORA INDUSTRIAL SIVA",
        "display_name": "PROVEEDORA INDUSTRIAL SIVA",
        "top": 351
    },
    {
        "code": "C02329",
        "source_name": "ROSA VIRGINIA MEUNIER GRANIEL",
        "display_name": "ROSA VIRGINIA MEUNIER GRANIEL",
        "top": 352
    },
    {
        "code": "B10830",
        "source_name": "MIGUEL ANGEL GARCIA SALDAÑA",
        "display_name": "MIGUEL ANGEL GARCIA SALDAÑA",
        "top": 353
    },
    {
        "code": "B13375",
        "source_name": "FRANCIS ALEJANDRA DORING MENDOZA",
        "display_name": "FRANCIS ALEJANDRA DORING MENDOZA",
        "top": 354
    },
    {
        "code": "G46752",
        "source_name": "PAPELERA GOBA",
        "display_name": "PAPELERA GOBA",
        "top": 355
    },
    {
        "code": "B11503",
        "source_name": "GRAN MERCERIA EL SURTIDOR",
        "display_name": "GRAN MERCERIA EL SURTIDOR",
        "top": 356
    },
    {
        "code": "B11282",
        "source_name": "CASA KIMOTO",
        "display_name": "CASA KIMOTO",
        "top": 357
    },
    {
        "code": "C00234",
        "source_name": "PAPELERIA MV",
        "display_name": "PAPELERIA MV",
        "top": 358
    },
    {
        "code": "C02386",
        "source_name": "JUAN ANTONIO HERNANDEZ CIRA",
        "display_name": "JUAN ANTONIO HERNANDEZ CIRA",
        "top": 359
    },
    {
        "code": "B11509",
        "source_name": "OSCAR CADENA",
        "display_name": "OSCAR CADENA",
        "top": 360
    },
    {
        "code": "C02394",
        "source_name": "MARIA DE LOURDES ANDRADE GUTIERREZ",
        "display_name": "MARIA DE LOURDES ANDRADE GUTIERREZ",
        "top": 361
    },
    {
        "code": "B13758",
        "source_name": "DP PELETEROS",
        "display_name": "DP PELETEROS",
        "top": 362
    },
    {
        "code": "C01225",
        "source_name": "DISTRIBUCION INTEGRAL PAPELERA",
        "display_name": "DISTRIBUCION INTEGRAL PAPELERA",
        "top": 363
    },
    {
        "code": "B11968",
        "source_name": "JORGE ALBERTO SANCHEZ HIDALGO GONZA",
        "display_name": "JORGE ALBERTO SANCHEZ HIDALGO GONZA",
        "top": 364
    },
    {
        "code": "C02288",
        "source_name": "PAPELERIA LA EXPOSICION",
        "display_name": "PAPELERIA LA EXPOSICION",
        "top": 365
    },
    {
        "code": "C02470",
        "source_name": "SESITI",
        "display_name": "SESITI",
        "top": 366
    },
    {
        "code": "C02467",
        "source_name": "CASILLAS PARRA BOLIVAR GUILLERMO",
        "display_name": "CASILLAS PARRA BOLIVAR GUILLERMO",
        "top": 367
    },
    {
        "code": "B20563",
        "source_name": "MANPALIDER S.A.",
        "display_name": "MANPALIDER S.A.",
        "top": 368
    },
    {
        "code": "C01777",
        "source_name": "ANA CELIA CARDENAS MARTINEZ",
        "display_name": "ANA CELIA CARDENAS MARTINEZ",
        "top": 369
    },
    {
        "code": "C02449",
        "source_name": "ABRAHAM ARRIAGA PARADA",
        "display_name": "ABRAHAM ARRIAGA PARADA",
        "top": 370
    },
    {
        "code": "C02382",
        "source_name": "DOLORES SOCORRO ESPINOSA REYES",
        "display_name": "DOLORES SOCORRO ESPINOSA REYES",
        "top": 371
    },
    {
        "code": "C02368",
        "source_name": "DISTRIBUIDORES DE SUMINISTROS",
        "display_name": "DISTRIBUIDORES DE SUMINISTROS",
        "top": 372
    },
    {
        "code": "B11718",
        "source_name": "COMERCIALIZADORA Y DISTRIBUIDORA",
        "display_name": "COMERCIALIZADORA Y DISTRIBUIDORA",
        "top": 373
    },
    {
        "code": "B13447",
        "source_name": "EUSTOLIA HERNANDEZ GOMEZ",
        "display_name": "EUSTOLIA HERNANDEZ GOMEZ",
        "top": 374
    },
    {
        "code": "C02265",
        "source_name": "MYRNA ELENA TAPIA IBARS",
        "display_name": "MYRNA ELENA TAPIA IBARS",
        "top": 375
    },
    {
        "code": "C01278",
        "source_name": "MONICA LIZETH ORDAZ CORONA",
        "display_name": "MONICA LIZETH ORDAZ CORONA",
        "top": 376
    },
    {
        "code": "B13126",
        "source_name": "PELETEX",
        "display_name": "PELETEX",
        "top": 377
    },
    {
        "code": "B13198",
        "source_name": "NORMA ELIZABETH CANALES AGUILERA",
        "display_name": "NORMA ELIZABETH CANALES AGUILERA",
        "top": 378
    },
    {
        "code": "C00182",
        "source_name": "REPARTO",
        "display_name": "REPARTO",
        "top": 379
    },
    {
        "code": "B13917",
        "source_name": "MARIA ESTELA HERRERA PEREZ",
        "display_name": "MARIA ESTELA HERRERA PEREZ",
        "top": 380
    },
    {
        "code": "C09089",
        "source_name": "LIBRERIA Y DISTRIBUIDORA",
        "display_name": "LIBRERIA Y DISTRIBUIDORA",
        "top": 381
    },
    {
        "code": "C02266",
        "source_name": "GABRIELA CUELLAR SANTANA",
        "display_name": "GABRIELA CUELLAR SANTANA",
        "top": 382
    },
    {
        "code": "C02442",
        "source_name": "DAVID ALEJANDRO GONZALEZ GARCIA",
        "display_name": "DAVID ALEJANDRO GONZALEZ GARCIA",
        "top": 383
    },
    {
        "code": "C02460",
        "source_name": "CENTRO FOTOGRAFICO Y COMPUTO",
        "display_name": "CENTRO FOTOGRAFICO Y COMPUTO",
        "top": 384
    },
    {
        "code": "B10581",
        "source_name": "FERRETERIA GUADALAJARA",
        "display_name": "FERRETERIA GUADALAJARA",
        "top": 385
    },
    {
        "code": "C01705",
        "source_name": "JOSE ANGEL GUSTAVO MONDRAGON ORDAZ",
        "display_name": "JOSE ANGEL GUSTAVO MONDRAGON ORDAZ",
        "top": 386
    },
    {
        "code": "C02415",
        "source_name": "ENRIQUE MORQUECHO GONZALEZ",
        "display_name": "ENRIQUE MORQUECHO GONZALEZ",
        "top": 387
    },
    {
        "code": "C02237",
        "source_name": "ASTROFOTO PAPELERIA",
        "display_name": "ASTROFOTO PAPELERIA",
        "top": 388
    },
    {
        "code": "C01508",
        "source_name": "YAMEL GUADALUPE CEJA ARJONA",
        "display_name": "YAMEL GUADALUPE CEJA ARJONA",
        "top": 389
    },
    {
        "code": "C02400",
        "source_name": "FRANCISCO JAVIER OCHOA NAJERA",
        "display_name": "FRANCISCO JAVIER OCHOA NAJERA",
        "top": 390
    },
    {
        "code": "B13183",
        "source_name": "MARTHA LIZETTE GONZALEZ ALVAREZ",
        "display_name": "MARTHA LIZETTE GONZALEZ ALVAREZ",
        "top": 391
    },
    {
        "code": "C01560",
        "source_name": "GEOECO DEL BAJIO",
        "display_name": "GEOECO DEL BAJIO",
        "top": 392
    },
    {
        "code": "C02456",
        "source_name": "DISTRIBUIDOR DE ARTICULOS DE OFICIN",
        "display_name": "DISTRIBUIDOR DE ARTICULOS DE OFICIN",
        "top": 393
    },
    {
        "code": "C02404",
        "source_name": "OLGA VICTORIA ALVARADO AGUILAR",
        "display_name": "OLGA VICTORIA ALVARADO AGUILAR",
        "top": 394
    },
    {
        "code": "G57012",
        "source_name": "PROVEEDORA DE SUMINISTROS EL REY",
        "display_name": "PROVEEDORA DE SUMINISTROS EL REY",
        "top": 395
    },
    {
        "code": "B10762",
        "source_name": "MAQUINAS DE COSER DE CHIHUAHUA",
        "display_name": "MAQUINAS DE COSER DE CHIHUAHUA",
        "top": 396
    },
    {
        "code": "B13593",
        "source_name": "ADRIANA ORDUÑA ALANIS",
        "display_name": "ADRIANA ORDUÑA ALANIS",
        "top": 397
    },
    {
        "code": "B14271",
        "source_name": "RAFAEL PALESTINO FLORES",
        "display_name": "RAFAEL PALESTINO FLORES",
        "top": 398
    },
    {
        "code": "B11367",
        "source_name": "CONSORCIO PAPELERO RIME",
        "display_name": "CONSORCIO PAPELERO RIME",
        "top": 399
    },
    {
        "code": "B12604",
        "source_name": "DISTRIBUIDORA CASTRO'S",
        "display_name": "DISTRIBUIDORA CASTRO'S",
        "top": 400
    },
    {
        "code": "B10571",
        "source_name": "ANA BERTHA MARTIN BARAJAS",
        "display_name": "ANA BERTHA MARTIN BARAJAS",
        "top": 401
    },
    {
        "code": "B11058",
        "source_name": "MERCERIA Y BONETERIA SANTA TERESITA",
        "display_name": "MERCERIA Y BONETERIA SANTA TERESITA",
        "top": 402
    },
    {
        "code": "C02144",
        "source_name": "GRUPO COMERCIAL DAMAG",
        "display_name": "GRUPO COMERCIAL DAMAG",
        "top": 403
    },
    {
        "code": "C09315",
        "source_name": "ANATEK INVESTMENT, INC.",
        "display_name": "ANATEK INVESTMENT, INC.",
        "top": 404
    },
    {
        "code": "C02217",
        "source_name": "JORGE OSCAR GARCIA NAVARRETE",
        "display_name": "JORGE OSCAR GARCIA NAVARRETE",
        "top": 405
    },
    {
        "code": "C01767",
        "source_name": "ESPACIO MATERIAL",
        "display_name": "ESPACIO MATERIAL",
        "top": 406
    },
    {
        "code": "B13652",
        "source_name": "JOSE LUIS PINEDA DE LA ROSA",
        "display_name": "JOSE LUIS PINEDA DE LA ROSA",
        "top": 407
    },
    {
        "code": "B13114",
        "source_name": "DORALICIA FERNANDEZ HERNANDEZ",
        "display_name": "DORALICIA FERNANDEZ HERNANDEZ",
        "top": 408
    },
    {
        "code": "C02304",
        "source_name": "CASA MARYS",
        "display_name": "CASA MARYS",
        "top": 409
    },
    {
        "code": "C02068",
        "source_name": "ELIZABETH MACIAS FLORES",
        "display_name": "ELIZABETH MACIAS FLORES",
        "top": 410
    },
    {
        "code": "B13278",
        "source_name": "CICLON DE SALDOS DE TIJUANA",
        "display_name": "CICLON DE SALDOS DE TIJUANA",
        "top": 411
    },
    {
        "code": "C09037",
        "source_name": "LIBRERIA CERVANTES S.A. DE C.V.",
        "display_name": "LIBRERIA CERVANTES S.A. DE C.V.",
        "top": 412
    },
    {
        "code": "B10774",
        "source_name": "CONSORCIO FERRETERO ALVAREZ",
        "display_name": "CONSORCIO FERRETERO ALVAREZ",
        "top": 413
    },
    {
        "code": "B10738",
        "source_name": "OLIVIA GUEVARA GOMEZ",
        "display_name": "OLIVIA GUEVARA GOMEZ",
        "top": 414
    },
    {
        "code": "C02285",
        "source_name": "REMIGIO LOPEZ BONILLA",
        "display_name": "REMIGIO LOPEZ BONILLA",
        "top": 415
    },
    {
        "code": "B12163",
        "source_name": "COLIBRI PAPELERIA",
        "display_name": "COLIBRI PAPELERIA",
        "top": 416
    },
    {
        "code": "B10313",
        "source_name": "LA MERCANTIL PELETERA",
        "display_name": "LA MERCANTIL PELETERA",
        "top": 417
    },
    {
        "code": "C02287",
        "source_name": "COMERCIAL TOACHE",
        "display_name": "COMERCIAL TOACHE",
        "top": 418
    },
    {
        "code": "C02420",
        "source_name": "OFI MARKET",
        "display_name": "OFI MARKET",
        "top": 419
    },
    {
        "code": "B10501",
        "source_name": "JOSE NEVAREZ GARIBAY",
        "display_name": "JOSE NEVAREZ GARIBAY",
        "top": 420
    },
    {
        "code": "C01567",
        "source_name": "MARIA CECILIA ALCOCER BUHL",
        "display_name": "MARIA CECILIA ALCOCER BUHL",
        "top": 421
    },
    {
        "code": "C02421",
        "source_name": "NUEVA LAGUNILLA DE HERMOSILLO",
        "display_name": "NUEVA LAGUNILLA DE HERMOSILLO",
        "top": 422
    },
    {
        "code": "B10673",
        "source_name": "EL LAPIZ ROJO DE URUAPAN",
        "display_name": "EL LAPIZ ROJO DE URUAPAN",
        "top": 423
    },
    {
        "code": "C02241",
        "source_name": "CAPACITACION Y SUMINISTROS KAHA",
        "display_name": "CAPACITACION Y SUMINISTROS KAHA",
        "top": 424
    },
    {
        "code": "B13894",
        "source_name": "PALMISS",
        "display_name": "PALMISS",
        "top": 425
    },
    {
        "code": "B14299",
        "source_name": "EDWIN HOMERO JIMENEZ GIL",
        "display_name": "EDWIN HOMERO JIMENEZ GIL",
        "top": 426
    },
    {
        "code": "B10518",
        "source_name": "CASA GUERRA DE MONTERREY",
        "display_name": "CASA GUERRA DE MONTERREY",
        "top": 427
    },
    {
        "code": "C02444",
        "source_name": "VERONICA LAURA ARANGO FLORES",
        "display_name": "VERONICA LAURA ARANGO FLORES",
        "top": 428
    },
    {
        "code": "B10580",
        "source_name": "EVA MARTIN MUÑOZ",
        "display_name": "EVA MARTIN MUÑOZ",
        "top": 429
    },
    {
        "code": "B14086",
        "source_name": "JOSE DE JESUS RAMOS VILLAFAÑA",
        "display_name": "JOSE DE JESUS RAMOS VILLAFAÑA",
        "top": 430
    },
    {
        "code": "C02211",
        "source_name": "SOLUCIONES INDUSTRIALES PRYMA",
        "display_name": "SOLUCIONES INDUSTRIALES PRYMA",
        "top": 431
    },
    {
        "code": "B10978",
        "source_name": "SUCURSAL PAPELERA",
        "display_name": "SUCURSAL PAPELERA",
        "top": 432
    },
    {
        "code": "B14204",
        "source_name": "ESTAMBRES PAPEL O TIJERA",
        "display_name": "ESTAMBRES PAPEL O TIJERA",
        "top": 433
    },
    {
        "code": "B11514",
        "source_name": "MARIA DEL CARMEN AMEZCUA MELGAREJO",
        "display_name": "MARIA DEL CARMEN AMEZCUA MELGAREJO",
        "top": 434
    },
    {
        "code": "C02255",
        "source_name": "DUSA PAPELERA",
        "display_name": "DUSA PAPELERA",
        "top": 435
    },
    {
        "code": "B10111",
        "source_name": "MARIA DEL CARMEN RUIZ MARTINEZ",
        "display_name": "MARIA DEL CARMEN RUIZ MARTINEZ",
        "top": 436
    },
    {
        "code": "C01584",
        "source_name": "PERLA MORALES MONTUFAR",
        "display_name": "PERLA MORALES MONTUFAR",
        "top": 437
    },
    {
        "code": "C02250",
        "source_name": "PAPELERIA ROUHANA",
        "display_name": "PAPELERIA ROUHANA",
        "top": 438
    },
    {
        "code": "B11433",
        "source_name": "RAFAEL BARRIENTOS JASSO",
        "display_name": "RAFAEL BARRIENTOS JASSO",
        "top": 439
    },
    {
        "code": "B12180",
        "source_name": "MARI TERE CASTAÑEDA GARCIA",
        "display_name": "MARI TERE CASTAÑEDA GARCIA",
        "top": 440
    },
    {
        "code": "B11897",
        "source_name": "CASA BRITO DE MAQUINAS DE COSER",
        "display_name": "CASA BRITO DE MAQUINAS DE COSER",
        "top": 441
    },
    {
        "code": "B14272",
        "source_name": "MARIA DEL ROSARIO REGINO RAMIREZ",
        "display_name": "MARIA DEL ROSARIO REGINO RAMIREZ",
        "top": 442
    },
    {
        "code": "B14402",
        "source_name": "MARISOL JIMENEZ NUÑEZ",
        "display_name": "MARISOL JIMENEZ NUÑEZ",
        "top": 443
    },
    {
        "code": "C02179",
        "source_name": "ELISEO MORALES AVILA",
        "display_name": "ELISEO MORALES AVILA",
        "top": 444
    },
    {
        "code": "C02242",
        "source_name": "JOSE MANUEL EUDAVE RAMOS",
        "display_name": "JOSE MANUEL EUDAVE RAMOS",
        "top": 445
    },
    {
        "code": "B20163",
        "source_name": "ABC SCHOOL SUPPLY",
        "display_name": "ABC SCHOOL SUPPLY",
        "top": 446
    },
    {
        "code": "C02468",
        "source_name": "NUEVA WAL MART DE MEXICO",
        "display_name": "SAMS.COM",
        "top": 447
    },
    {
        "code": "C01586",
        "source_name": "COPISISTEMAS DE YUCATAN",
        "display_name": "COPISISTEMAS DE YUCATAN",
        "top": 448
    },
    {
        "code": "C02090",
        "source_name": "CARLOS ALBERTO GARDEA GONZALEZ",
        "display_name": "CARLOS ALBERTO GARDEA GONZALEZ",
        "top": 449
    },
    {
        "code": "B13368",
        "source_name": "JOSE LUIS CORONADO GUERRERO",
        "display_name": "JOSE LUIS CORONADO GUERRERO",
        "top": 450
    },
    {
        "code": "G47303",
        "source_name": "CONCEPCION PACHECO GARCIA",
        "display_name": "CONCEPCION PACHECO GARCIA",
        "top": 451
    },
    {
        "code": "B10058",
        "source_name": "TELAS JUNCO",
        "display_name": "TELAS JUNCO",
        "top": 452
    },
    {
        "code": "B13481",
        "source_name": "BRAULIO CAMACHO VILLEGAS",
        "display_name": "BRAULIO CAMACHO VILLEGAS",
        "top": 453
    },
    {
        "code": "B10577",
        "source_name": "DE ANDA HERMANOS MERCERIA Y BONETER",
        "display_name": "DE ANDA HERMANOS MERCERIA Y BONETER",
        "top": 454
    },
    {
        "code": "B13280",
        "source_name": "FRANCISCO ESTRADA VICTORIA",
        "display_name": "FRANCISCO ESTRADA VICTORIA",
        "top": 455
    },
    {
        "code": "C02428",
        "source_name": "SUMINISTROS DE OFICINA Y PAPELERIA",
        "display_name": "SUMINISTROS DE OFICINA Y PAPELERIA",
        "top": 456
    },
    {
        "code": "C01828",
        "source_name": "DISTRIBUIDOR PAPELERO DE TOLUCA",
        "display_name": "DISTRIBUIDOR PAPELERO DE TOLUCA",
        "top": 457
    },
    {
        "code": "B12642",
        "source_name": "MA DEL CARMEN RODRIGUEZ RODRIGUEZ",
        "display_name": "MA DEL CARMEN RODRIGUEZ RODRIGUEZ",
        "top": 458
    },
    {
        "code": "B10842",
        "source_name": "DISTRIBUIDORA COMERCIAL LA PALMA",
        "display_name": "DISTRIBUIDORA COMERCIAL LA PALMA",
        "top": 459
    },
    {
        "code": "B11894",
        "source_name": "FARMACIA NUEVA CENTRAL",
        "display_name": "FARMACIA NUEVA CENTRAL",
        "top": 460
    },
    {
        "code": "B14079",
        "source_name": "ZENAIDA PEREZ PELAYO",
        "display_name": "ZENAIDA PEREZ PELAYO",
        "top": 461
    },
    {
        "code": "B14072",
        "source_name": "RODRIGO DE LA PARRA MORENO",
        "display_name": "RODRIGO DE LA PARRA MORENO",
        "top": 462
    },
    {
        "code": "G47298",
        "source_name": "DECOP DE SAN LUIS",
        "display_name": "DECOP DE SAN LUIS",
        "top": 463
    },
    {
        "code": "C02383",
        "source_name": "PERLA CECILIA MACIEL MONCADA",
        "display_name": "PERLA CECILIA MACIEL MONCADA",
        "top": 464
    },
    {
        "code": "B12856",
        "source_name": "MERCERIA LA SUPER",
        "display_name": "MERCERIA LA SUPER",
        "top": 465
    },
    {
        "code": "B14048",
        "source_name": "IRMA SERRANO MALDONADO",
        "display_name": "IRMA SERRANO MALDONADO",
        "top": 466
    },
    {
        "code": "C02224",
        "source_name": "ERICK OVIEL DIAZ MENDEZ",
        "display_name": "ERICK OVIEL DIAZ MENDEZ",
        "top": 467
    },
    {
        "code": "C02471",
        "source_name": "PRICEWATERHOUSECOOPERS REPÚBLICA",
        "display_name": "PRICEWATERHOUSECOOPERS REPÚBLICA",
        "top": 468
    },
    {
        "code": "B10517",
        "source_name": "CASA ENRIQUE DE MONTERREY",
        "display_name": "CASA ENRIQUE DE MONTERREY",
        "top": 469
    },
    {
        "code": "B14124",
        "source_name": "JUAN ENRIQUE BECERRIL RAIGOZA",
        "display_name": "JUAN ENRIQUE BECERRIL RAIGOZA",
        "top": 470
    },
    {
        "code": "B13502",
        "source_name": "NUEVO CENTRO FERRETERO SERUR",
        "display_name": "NUEVO CENTRO FERRETERO SERUR",
        "top": 471
    },
    {
        "code": "C02437",
        "source_name": "JAC PATRIMONIAL",
        "display_name": "JAC PATRIMONIAL",
        "top": 472
    },
    {
        "code": "B13653",
        "source_name": "DAVLU DISTRIBUIDORA",
        "display_name": "DAVLU DISTRIBUIDORA",
        "top": 473
    },
    {
        "code": "C02395",
        "source_name": "COMERCIALIZADORA MEXICANA GC2",
        "display_name": "COMERCIALIZADORA MEXICANA GC2",
        "top": 474
    },
    {
        "code": "C02343",
        "source_name": "RAUL BAUTISTA ANTONIO",
        "display_name": "RAUL BAUTISTA ANTONIO",
        "top": 475
    },
    {
        "code": "B12917",
        "source_name": "ADRIANA ARENAS OLIVERAS",
        "display_name": "ADRIANA ARENAS OLIVERAS",
        "top": 476
    },
    {
        "code": "B13053",
        "source_name": "JESSICA NOEMI HERNANDEZ DE LA ROSA",
        "display_name": "JESSICA NOEMI HERNANDEZ DE LA ROSA",
        "top": 477
    },
    {
        "code": "C02035",
        "source_name": "ROBERTO LEM GONZALEZ",
        "display_name": "ROBERTO LEM GONZALEZ",
        "top": 478
    },
    {
        "code": "C00392",
        "source_name": "M.C. PAPELERIAS",
        "display_name": "M.C. PAPELERIAS",
        "top": 479
    },
    {
        "code": "B13642",
        "source_name": "JAIME ALLENDE CARRERA",
        "display_name": "JAIME ALLENDE CARRERA",
        "top": 480
    },
    {
        "code": "B12335",
        "source_name": "VICTOR MANUEL OCHOA CARRASCO",
        "display_name": "VICTOR MANUEL OCHOA CARRASCO",
        "top": 481
    },
    {
        "code": "B11186",
        "source_name": "PAPELERAMA DEL NOROESTE",
        "display_name": "PAPELERAMA DEL NOROESTE",
        "top": 482
    },
    {
        "code": "C02434",
        "source_name": "MILTON MARIO RAMIREZ LOPEZ",
        "display_name": "MILTON MARIO RAMIREZ LOPEZ",
        "top": 483
    },
    {
        "code": "B12745",
        "source_name": "MINERVA EVANGELINA GARMA",
        "display_name": "MINERVA EVANGELINA GARMA",
        "top": 484
    },
    {
        "code": "C02272",
        "source_name": "FELIX HERNANDEZ CRUZ",
        "display_name": "FELIX HERNANDEZ CRUZ",
        "top": 485
    },
    {
        "code": "C02223",
        "source_name": "HEMBERLY HERNANDEZ ALVARADO",
        "display_name": "HEMBERLY HERNANDEZ ALVARADO",
        "top": 486
    },
    {
        "code": "C02236",
        "source_name": "PENELOPE ESMERALDA GOMEZ BARQUET",
        "display_name": "PENELOPE ESMERALDA GOMEZ BARQUET",
        "top": 487
    },
    {
        "code": "B10076",
        "source_name": "COMERCIALIZADORA FRANCO",
        "display_name": "COMERCIALIZADORA FRANCO",
        "top": 488
    },
    {
        "code": "B10133",
        "source_name": "DIVOMEX",
        "display_name": "DIVOMEX",
        "top": 489
    },
    {
        "code": "C02155",
        "source_name": "GRUPO VEROMO",
        "display_name": "GRUPO VEROMO",
        "top": 490
    },
    {
        "code": "B14282",
        "source_name": "FERRETODO DEL BAJIO",
        "display_name": "FERRETODO DEL BAJIO",
        "top": 491
    },
    {
        "code": "C02229",
        "source_name": "RAUL EDUARDO OCHOA CARRASCO",
        "display_name": "RAUL EDUARDO OCHOA CARRASCO",
        "top": 492
    },
    {
        "code": "C02319",
        "source_name": "MINELIA FLORES ZI",
        "display_name": "MINELIA FLORES ZI",
        "top": 493
    },
    {
        "code": "B10997",
        "source_name": "PAPELERIA Y LIBRERIA HIDALGO",
        "display_name": "PAPELERIA Y LIBRERIA HIDALGO",
        "top": 494
    },
    {
        "code": "B14220",
        "source_name": "JUAN MANUEL ZALDIVAR CHIAPA",
        "display_name": "JUAN MANUEL ZALDIVAR CHIAPA",
        "top": 495
    },
    {
        "code": "G47030",
        "source_name": "FERNANDO YUJI HAYAMA TSUTSUMI",
        "display_name": "FERNANDO YUJI HAYAMA TSUTSUMI",
        "top": 496
    },
    {
        "code": "C02399",
        "source_name": "FERRESANPA",
        "display_name": "FERRESANPA",
        "top": 497
    },
    {
        "code": "B10067",
        "source_name": "TELAS Y DECORACIONES DEL RIO",
        "display_name": "TELAS Y DECORACIONES DEL RIO",
        "top": 498
    },
    {
        "code": "C02465",
        "source_name": "JAVIER FEDERICO CISNEROS RODRIGUEZ",
        "display_name": "JAVIER FEDERICO CISNEROS RODRIGUEZ",
        "top": 499
    },
    {
        "code": "B13484",
        "source_name": "BERNARDO BAUTISTA CALDERON",
        "display_name": "BERNARDO BAUTISTA CALDERON",
        "top": 500
    },
    {
        "code": "B10026",
        "source_name": "FERRECSA",
        "display_name": "FERRECSA",
        "top": 501
    },
    {
        "code": "B10039",
        "source_name": "FERREKUPER",
        "display_name": "FERREKUPER",
        "top": 502
    },
    {
        "code": "C02352",
        "source_name": "HERMINIO AGUILAR CHAVEZ",
        "display_name": "HERMINIO AGUILAR CHAVEZ",
        "top": 503
    },
    {
        "code": "C01900",
        "source_name": "SURTIDORA PECO",
        "display_name": "SURTIDORA PECO",
        "top": 504
    },
    {
        "code": "C02475",
        "source_name": "GABRIELA GAMBOA LOPEZ",
        "display_name": "GABRIELA GAMBOA LOPEZ",
        "top": 505
    },
    {
        "code": "B10018",
        "source_name": "FERRETERA MAX",
        "display_name": "FERRETERA MAX",
        "top": 506
    },
    {
        "code": "B13587",
        "source_name": "GRUPO REYES PAPELERIA LIBRERIA Y",
        "display_name": "GRUPO REYES PAPELERIA LIBRERIA Y",
        "top": 507
    },
    {
        "code": "B13474",
        "source_name": "ERICK HERNANDEZ GARCIA",
        "display_name": "ERICK HERNANDEZ GARCIA",
        "top": 508
    },
    {
        "code": "B10480",
        "source_name": "LA AGUJITA",
        "display_name": "LA AGUJITA",
        "top": 509
    },
    {
        "code": "G50267",
        "source_name": "D.R. SAGITARIO",
        "display_name": "D.R. SAGITARIO",
        "top": 510
    },
    {
        "code": "B11352",
        "source_name": "LA ESCOLAR DE TEXCOCO",
        "display_name": "LA ESCOLAR DE TEXCOCO",
        "top": 511
    },
    {
        "code": "C02411",
        "source_name": "ELOISA MORALES GUZMAN",
        "display_name": "ELOISA MORALES GUZMAN",
        "top": 512
    },
    {
        "code": "B10079",
        "source_name": "OSCAR TORRES MIRANDA",
        "display_name": "OSCAR TORRES MIRANDA",
        "top": 513
    },
    {
        "code": "B10582",
        "source_name": "FERRETERIAS MONTERREY DE OCCIDENTE",
        "display_name": "FERRETERIAS MONTERREY DE OCCIDENTE",
        "top": 514
    },
    {
        "code": "C02347",
        "source_name": "VERONICA LILIANA SALAS CORDERO",
        "display_name": "VERONICA LILIANA SALAS CORDERO",
        "top": 515
    },
    {
        "code": "B13300",
        "source_name": "DISTRIBUIDORA GAR-PREC",
        "display_name": "DISTRIBUIDORA GAR-PREC",
        "top": 516
    },
    {
        "code": "C02451",
        "source_name": "T. EN COLOMBIA S.A.",
        "display_name": "T. EN COLOMBIA S.A.",
        "top": 517
    },
    {
        "code": "C02323",
        "source_name": "SUPERMERCADO AL MAS BARATO",
        "display_name": "SUPERMERCADO AL MAS BARATO",
        "top": 518
    },
    {
        "code": "C09328",
        "source_name": "COPIDESA",
        "display_name": "COPIDESA",
        "top": 519
    },
    {
        "code": "B13228",
        "source_name": "ROBERTO LEAL MARGAILLAN",
        "display_name": "ROBERTO LEAL MARGAILLAN",
        "top": 520
    },
    {
        "code": "C02312",
        "source_name": "ENNA ROSA LOPEZ PATRON",
        "display_name": "ENNA ROSA LOPEZ PATRON",
        "top": 521
    },
    {
        "code": "B10746",
        "source_name": "MA. MAGDALENA GONZALEZ ACEVES",
        "display_name": "MA. MAGDALENA GONZALEZ ACEVES",
        "top": 522
    },
    {
        "code": "B10419",
        "source_name": "LIBRERIA JUAREZ DE VALLES",
        "display_name": "LIBRERIA JUAREZ DE VALLES",
        "top": 523
    },
    {
        "code": "C02443",
        "source_name": "GRISELL ORTIZ MARTINEZ",
        "display_name": "GRISELL ORTIZ MARTINEZ",
        "top": 524
    },
    {
        "code": "C02424",
        "source_name": "FERNANDO VILLAVICENCIO MEDINA",
        "display_name": "FERNANDO VILLAVICENCIO MEDINA",
        "top": 525
    },
    {
        "code": "B13963",
        "source_name": "ROBERTO VALENCIA COLECIO",
        "display_name": "ROBERTO VALENCIA COLECIO",
        "top": 526
    },
    {
        "code": "B14245",
        "source_name": "ADELINA HILDA PACHECO",
        "display_name": "ADELINA HILDA PACHECO",
        "top": 527
    },
    {
        "code": "C01993",
        "source_name": "ASTRID LETICIA BERGENGRUEN BRIONES",
        "display_name": "ASTRID LETICIA BERGENGRUEN BRIONES",
        "top": 528
    },
    {
        "code": "B13306",
        "source_name": "EDGAR JESUS MORALES RAMIREZ",
        "display_name": "EDGAR JESUS MORALES RAMIREZ",
        "top": 529
    },
    {
        "code": "B10735",
        "source_name": "HERMILA MATA CARRASCO",
        "display_name": "HERMILA MATA CARRASCO",
        "top": 530
    },
    {
        "code": "B13683",
        "source_name": "LUIS MANUEL LEON NEVAREZ",
        "display_name": "LUIS MANUEL LEON NEVAREZ",
        "top": 531
    },
    {
        "code": "B13556",
        "source_name": "EL LEON DE LAS TELAS",
        "display_name": "EL LEON DE LAS TELAS",
        "top": 532
    },
    {
        "code": "C01865",
        "source_name": "COMERCIALIZADORA SURTIDORA ESCOLAR",
        "display_name": "COMERCIALIZADORA SURTIDORA ESCOLAR",
        "top": 533
    },
    {
        "code": "C02430",
        "source_name": "CECILIA ELENA MELENDEZ RUIZ",
        "display_name": "CECILIA ELENA MELENDEZ RUIZ",
        "top": 534
    },
    {
        "code": "C02387",
        "source_name": "MARIA DE LOURDES ALCANTARA GONZALEZ",
        "display_name": "MARIA DE LOURDES ALCANTARA GONZALEZ",
        "top": 535
    },
    {
        "code": "C02457",
        "source_name": "IMPRESOS PUNTUAL",
        "display_name": "IMPRESOS PUNTUAL",
        "top": 536
    },
    {
        "code": "B10751",
        "source_name": "SILVIA LUZ BLANCO CORRAL",
        "display_name": "SILVIA LUZ BLANCO CORRAL",
        "top": 537
    },
    {
        "code": "C02159",
        "source_name": "TAMEG GRUPO COMERCIAL",
        "display_name": "TAMEG GRUPO COMERCIAL",
        "top": 538
    },
    {
        "code": "B11866",
        "source_name": "DEPORTES Y REGALOS SAMAR",
        "display_name": "DEPORTES Y REGALOS SAMAR",
        "top": 539
    },
    {
        "code": "C02458",
        "source_name": "CELIA ESTEFANIA ALVAREZ ESCALERA",
        "display_name": "CELIA ESTEFANIA ALVAREZ ESCALERA",
        "top": 540
    },
    {
        "code": "B10176",
        "source_name": "PAPELERIA EL ANCLA",
        "display_name": "PAPELERIA EL ANCLA",
        "top": 541
    },
    {
        "code": "B10283",
        "source_name": "COMPAÑIA PAPELERA FUTURAMA",
        "display_name": "COMPAÑIA PAPELERA FUTURAMA",
        "top": 542
    },
    {
        "code": "B10230",
        "source_name": "MARIA ELENA HAYAMA TSUTSUMI",
        "display_name": "MARIA ELENA HAYAMA TSUTSUMI",
        "top": 543
    },
    {
        "code": "B11720",
        "source_name": "JOSE ALFREDO CAUDILLO AGUILAR",
        "display_name": "JOSE ALFREDO CAUDILLO AGUILAR",
        "top": 544
    },
    {
        "code": "C00569",
        "source_name": "LA REYNA DE MESONES",
        "display_name": "LA REYNA DE MESONES",
        "top": 545
    },
    {
        "code": "B10628",
        "source_name": "LAS FABRICAS MARGAILLAN",
        "display_name": "LAS FABRICAS MARGAILLAN",
        "top": 546
    },
    {
        "code": "C00164",
        "source_name": "PAPELERIA DEL ISTMO PACIFICO",
        "display_name": "PAPELERIA DEL ISTMO PACIFICO",
        "top": 547
    },
    {
        "code": "B14267",
        "source_name": "PAPELERIA Y TLAPALERIA EL AGUILAR",
        "display_name": "PAPELERIA Y TLAPALERIA EL AGUILAR",
        "top": 548
    },
    {
        "code": "C02427",
        "source_name": "SANDRA BERENICE CORONADO BECERRA",
        "display_name": "SANDRA BERENICE CORONADO BECERRA",
        "top": 549
    },
    {
        "code": "B14265",
        "source_name": "MIRIAM JENNIFER PENAGOS PEREZ",
        "display_name": "MIRIAM JENNIFER PENAGOS PEREZ",
        "top": 550
    },
    {
        "code": "B13616",
        "source_name": "ARTURO DE LA CONCEPCION GONZALEZ",
        "display_name": "ARTURO DE LA CONCEPCION GONZALEZ",
        "top": 551
    },
    {
        "code": "C02165",
        "source_name": "JAYRA GUADALUPE GUTIERREZ UREÑA",
        "display_name": "JAYRA GUADALUPE GUTIERREZ UREÑA",
        "top": 552
    },
    {
        "code": "C00493",
        "source_name": "ILSE CHANG DIAZ FONG",
        "display_name": "ILSE CHANG DIAZ FONG",
        "top": 553
    },
    {
        "code": "B13453",
        "source_name": "DIANA VANESSA ALCAZAR ROSAS",
        "display_name": "DIANA VANESSA ALCAZAR ROSAS",
        "top": 554
    },
    {
        "code": "B11060",
        "source_name": "OCTAVIO JIMENEZ ORTIZ",
        "display_name": "OCTAVIO JIMENEZ ORTIZ",
        "top": 555
    },
    {
        "code": "B13006",
        "source_name": "EQUIPOS VILLELA Y COPYJET",
        "display_name": "EQUIPOS VILLELA Y COPYJET",
        "top": 556
    },
    {
        "code": "B10387",
        "source_name": "CASA KURI",
        "display_name": "CASA KURI",
        "top": 557
    },
    {
        "code": "B10068",
        "source_name": "FERRE. V. K",
        "display_name": "FERRE. V. K",
        "top": 558
    },
    {
        "code": "B10737",
        "source_name": "JUAN CARLOS RODRIGUEZ DELGADO",
        "display_name": "JUAN CARLOS RODRIGUEZ DELGADO",
        "top": 559
    },
    {
        "code": "G07708",
        "source_name": "PRODUTEC DE QUERETARO",
        "display_name": "PRODUTEC DE QUERETARO",
        "top": 560
    },
    {
        "code": "C02375",
        "source_name": "ELIA MORENO MEDINA",
        "display_name": "ELIA MORENO MEDINA",
        "top": 561
    },
    {
        "code": "C01340",
        "source_name": "COPYCANON",
        "display_name": "COPYCANON",
        "top": 562
    },
    {
        "code": "B13262",
        "source_name": "FERRETERIA EL GLOBO DE AGUASCALIENT",
        "display_name": "FERRETERIA EL GLOBO DE AGUASCALIENT",
        "top": 563
    },
    {
        "code": "C02182",
        "source_name": "LANDFORT SAS",
        "display_name": "LANDFORT SAS",
        "top": 564
    },
    {
        "code": "B13383",
        "source_name": "SANTOS RODRIGUEZ VITE",
        "display_name": "SANTOS RODRIGUEZ VITE",
        "top": 565
    },
    {
        "code": "B13211",
        "source_name": "J JESUS ACOSTA GALLEGOS",
        "display_name": "J JESUS ACOSTA GALLEGOS",
        "top": 566
    },
    {
        "code": "B11302",
        "source_name": "NAVA PELETEROS",
        "display_name": "NAVA PELETEROS",
        "top": 567
    },
    {
        "code": "C02463",
        "source_name": "BELLARDINA",
        "display_name": "BELLARDINA",
        "top": 568
    },
    {
        "code": "B13310",
        "source_name": "MAQUINAS DE COSER DOÑA FLOR",
        "display_name": "MAQUINAS DE COSER DOÑA FLOR",
        "top": 569
    },
    {
        "code": "C02161",
        "source_name": "GONZALO ALFARO ROSALES",
        "display_name": "GONZALO ALFARO ROSALES",
        "top": 570
    },
    {
        "code": "B14143",
        "source_name": "SERGIO MANUEL AGUIRRE GOMEZ",
        "display_name": "SERGIO MANUEL AGUIRRE GOMEZ",
        "top": 571
    },
    {
        "code": "B11327",
        "source_name": "JAIME ENDO SUZUKI",
        "display_name": "JAIME ENDO SUZUKI",
        "top": 572
    },
    {
        "code": "C02452",
        "source_name": "JOSE LUIS MIRANDA GUERRA",
        "display_name": "JOSE LUIS MIRANDA GUERRA",
        "top": 573
    },
    {
        "code": "B13144",
        "source_name": "MIGUEL ANGEL FIGUEROA GALLEGOS",
        "display_name": "MIGUEL ANGEL FIGUEROA GALLEGOS",
        "top": 574
    },
    {
        "code": "C02422",
        "source_name": "HUGO ENRIQUE CASTILLO MARTINEZ",
        "display_name": "HUGO ENRIQUE CASTILLO MARTINEZ",
        "top": 575
    },
    {
        "code": "C02360",
        "source_name": "JAGUEN",
        "display_name": "JAGUEN",
        "top": 576
    },
    {
        "code": "B10589",
        "source_name": "JOSE MATIAS CURIEL LOMELI",
        "display_name": "JOSE MATIAS CURIEL LOMELI",
        "top": 577
    },
    {
        "code": "B13962",
        "source_name": "MARIA DEL PILAR HUIZAR AVILA",
        "display_name": "MARIA DEL PILAR HUIZAR AVILA",
        "top": 578
    },
    {
        "code": "B10009",
        "source_name": "AUGUSTO LUIS NAVA ARELLANO",
        "display_name": "AUGUSTO LUIS NAVA ARELLANO",
        "top": 579
    },
    {
        "code": "C02085",
        "source_name": "MARIA DEL CARMEN INOCENCIO CASILLAS",
        "display_name": "MARIA DEL CARMEN INOCENCIO CASILLAS",
        "top": 580
    },
    {
        "code": "C02262",
        "source_name": "ARMANDO SAENZ LOPEZ",
        "display_name": "ARMANDO SAENZ LOPEZ",
        "top": 581
    },
    {
        "code": "C02088",
        "source_name": "OVED HERNANDEZ CIRA",
        "display_name": "OVED HERNANDEZ CIRA",
        "top": 582
    },
    {
        "code": "C00254",
        "source_name": "PAPELERIA PENSIL",
        "display_name": "PAPELERIA PENSIL",
        "top": 583
    },
    {
        "code": "C02219",
        "source_name": "JAVIER RAMIREZ BAÑUELOS",
        "display_name": "JAVIER RAMIREZ BAÑUELOS",
        "top": 584
    },
    {
        "code": "C02455",
        "source_name": "PATRICIA CARMONA REYES",
        "display_name": "PATRICIA CARMONA REYES",
        "top": 585
    },
    {
        "code": "B12993",
        "source_name": "FLOR MERCEDES RAMIREZ BERNACHE",
        "display_name": "FLOR MERCEDES RAMIREZ BERNACHE",
        "top": 586
    },
    {
        "code": "C02412",
        "source_name": "NAVARRO PAPELERA",
        "display_name": "NAVARRO PAPELERA",
        "top": 587
    },
    {
        "code": "C02342",
        "source_name": "ONLINE CAREER CENTER MEXICO",
        "display_name": "ONLINE CAREER CENTER MEXICO",
        "top": 588
    },
    {
        "code": "C02464",
        "source_name": "BEATRIZ GARCIA MORALES",
        "display_name": "BEATRIZ GARCIA MORALES",
        "top": 589
    },
    {
        "code": "G94980",
        "source_name": "UNIVERSIDAD NACIONAL AUTONOMA DE ME",
        "display_name": "UNIVERSIDAD NACIONAL AUTONOMA DE ME",
        "top": 590
    },
    {
        "code": "B11478",
        "source_name": "PAPELERIA 2001",
        "display_name": "PAPELERIA 2001",
        "top": 591
    },
    {
        "code": "B13054",
        "source_name": "FRANCISCO JAVIER HERNANDEZ FLORES",
        "display_name": "FRANCISCO JAVIER HERNANDEZ FLORES",
        "top": 592
    },
    {
        "code": "B13896",
        "source_name": "MIGUEL ANGEL HERNANDEZ PEREZ",
        "display_name": "MIGUEL ANGEL HERNANDEZ PEREZ",
        "top": 593
    },
    {
        "code": "C00936",
        "source_name": "HUMBERTO MARMOLEJO ESQUEDA",
        "display_name": "HUMBERTO MARMOLEJO ESQUEDA",
        "top": 594
    },
    {
        "code": "B10618",
        "source_name": "DIANA GUADALUPE HERNANDEZ PEREZ",
        "display_name": "DIANA GUADALUPE HERNANDEZ PEREZ",
        "top": 595
    },
    {
        "code": "B12153",
        "source_name": "LUCILA EMILIANA PEÑA MONTOR",
        "display_name": "LUCILA EMILIANA PEÑA MONTOR",
        "top": 596
    },
    {
        "code": "B13522",
        "source_name": "JOSE FRANCISCO DIAZ DE LEON CERDA",
        "display_name": "JOSE FRANCISCO DIAZ DE LEON CERDA",
        "top": 597
    },
    {
        "code": "B13415",
        "source_name": "MARIO ALBERTO ROMO GONZALEZ",
        "display_name": "MARIO ALBERTO ROMO GONZALEZ",
        "top": 598
    },
    {
        "code": "D00030",
        "source_name": "CLIENTE DUMMY KENSINGTON",
        "display_name": "CLIENTE DUMMY KENSINGTON",
        "top": 599
    },
    {
        "code": "B12548",
        "source_name": "FYSSSA HOGAR",
        "display_name": "FYSSSA HOGAR",
        "top": 600
    },
    {
        "code": "C02461",
        "source_name": "ALBA JOVITA GARCIA CALDERA",
        "display_name": "ALBA JOVITA GARCIA CALDERA",
        "top": 601
    },
    {
        "code": "C02418",
        "source_name": "MIGUEL CARRILLO MARTINEZ",
        "display_name": "MIGUEL CARRILLO MARTINEZ",
        "top": 602
    },
    {
        "code": "B11679",
        "source_name": "DIEGO GIL TENORIO",
        "display_name": "DIEGO GIL TENORIO",
        "top": 603
    },
    {
        "code": "B10809",
        "source_name": "MA. GUADALUPE LORANCA MONTIEL",
        "display_name": "MA. GUADALUPE LORANCA MONTIEL",
        "top": 604
    },
    {
        "code": "C00093",
        "source_name": "ROGAS",
        "display_name": "ROGAS",
        "top": 605
    },
    {
        "code": "B14105",
        "source_name": "JESUS MANUEL BARBA CUEVAS",
        "display_name": "JESUS MANUEL BARBA CUEVAS",
        "top": 606
    },
    {
        "code": "B14167",
        "source_name": "RICARDO YUKIO SHIMIZU NAGAI",
        "display_name": "RICARDO YUKIO SHIMIZU NAGAI",
        "top": 607
    },
    {
        "code": "C01289",
        "source_name": "BLANCA DEL ROSARIO GARCIA CUE",
        "display_name": "BLANCA DEL ROSARIO GARCIA CUE",
        "top": 608
    },
    {
        "code": "B11871",
        "source_name": "MARIA SANDRA GARCIA GARCIA",
        "display_name": "MARIA SANDRA GARCIA GARCIA",
        "top": 609
    },
    {
        "code": "B14325",
        "source_name": "CARLOS HERMOSILLO ALVAREZ",
        "display_name": "CARLOS HERMOSILLO ALVAREZ",
        "top": 610
    },
    {
        "code": "G48719",
        "source_name": "DIRECCION SPORT",
        "display_name": "DIRECCION SPORT",
        "top": 611
    },
    {
        "code": "B14385",
        "source_name": "ADRIANA JIMENEZ ALARCON",
        "display_name": "ADRIANA JIMENEZ ALARCON",
        "top": 612
    },
    {
        "code": "B81712",
        "source_name": "SEVERO FERNANDEZ TRISTAN",
        "display_name": "SEVERO FERNANDEZ TRISTAN",
        "top": 613
    },
    {
        "code": "C02453",
        "source_name": "JUAN MANUEL CODEMO GUZMAN",
        "display_name": "JUAN MANUEL CODEMO GUZMAN",
        "top": 614
    },
    {
        "code": "B11041",
        "source_name": "INNOVACIONES Y MANUALIDADES DE OAXA",
        "display_name": "INNOVACIONES Y MANUALIDADES DE OAXA",
        "top": 615
    },
    {
        "code": "C01766",
        "source_name": "PAPIERWAREN",
        "display_name": "PAPIERWAREN",
        "top": 616
    },
    {
        "code": "B11776",
        "source_name": "CLEMENTINA SILVA LOBATO",
        "display_name": "CLEMENTINA SILVA LOBATO",
        "top": 617
    },
    {
        "code": "B14273",
        "source_name": "ALBERTO ROSAS HERNANDEZ",
        "display_name": "ALBERTO ROSAS HERNANDEZ",
        "top": 618
    },
    {
        "code": "B13224",
        "source_name": "JOSE DE JESUS LARA RODRIGUEZ",
        "display_name": "JOSE DE JESUS LARA RODRIGUEZ",
        "top": 619
    },
    {
        "code": "C00402",
        "source_name": "DISTRIBUIDORA MARIN",
        "display_name": "DISTRIBUIDORA MARIN",
        "top": 620
    },
    {
        "code": "D00033",
        "source_name": "PUBLICO EN GENERAL",
        "display_name": "ACCO EXPRESS",
        "top": 621
    },
    {
        "code": "B13847",
        "source_name": "PISO PAPELES NACIONALES",
        "display_name": "PISO PAPELES NACIONALES",
        "top": 622
    },
    {
        "code": "C02410",
        "source_name": "GRUPO CORPORATIVO BARAC",
        "display_name": "GRUPO CORPORATIVO BARAC",
        "top": 623
    }
]

# ---------------------------------------------------------
# RENOMBRES SOLO PARA CLIENTES CON NOMBRE REPETIDO
# Si el código no está en este diccionario, se conserva el nombre normal.
# ---------------------------------------------------------
REPORT_4_CLIENT_NAME_OVERRIDES = {
    "C02359": "ABASTECEDORA DE OFICINAS - Barrilito",
    "C00011": "ABASTECEDORA DE OFICINAS - ACCO",
    "D00014": "MERCADO LIBRE",
    "C00938": "SAMS",
    "C00825": "CASA DE PAPELERIA M - ACCO",
    "C01628": "SUPERCENTER",
    "C02391": "CASA DE PAPELERIA M - Barrilito",
    "C02125": "INGRAM MICRO MEXICO USD",
    "C01804": "BODEGA AURRERA",
    "C00304": "INGRAM MICRO MEXICO MXN",
    "C02469": "TECNOLOGIA SMARTBITT USD",
    "C00488": "COSTCO",
    "C02474": "COMERCIALIZADORA DE VALOR AGREGADO USD",
    "C02032": "COSTCO ECO",
    "C02454": "TECNOLOGIA SMARTBITT  MXN",
    "C02473": "COMERCIALIZADORA DE VALOR AGREGADO   MXN",
    "C02468": "SAMS.COM",
    "D00033": "ACCO EXPRESS"
}

REPORT_4_GROUP_TOP_15 = "Top 15 Clients"
REPORT_4_GROUP_16_50 = "Clients 16 to 50"
REPORT_4_GROUP_51_100 = "Clients 51 to 100"
REPORT_4_GROUP_OTHER = "Other clients"
REPORT_4_TOTAL_LABEL = "Total Mexico"

# ---------------------------------------------------------
# MENSAJES DE REPORTE 4
# ---------------------------------------------------------
MSG_REPORT_4_BUILD_SUCCESS = "Reporte 4 construido correctamente."
MSG_REPORT_4_BUILD_ERROR = "Ocurrió un error al construir el Reporte 4."
MSG_REPORT_4_BUILD_MISSING_FILES = (
    "Para construir el Reporte 4 primero debes tener ventas procesadas "
    "y plan por cliente cargado."
)


