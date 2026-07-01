# =========================================================
# APLICACIÓN PRINCIPAL DEL DASHBOARD
# ETAPA 1 + ETAPA 2 + ETAPA 3 + ETAPA 4 + ETAPA 5 + ETAPA 6 + ETAPA 7 + ETAPA 8
# Archivo: app.py
# =========================================================

from html import escape
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
import math
import pickle

import streamlit as st

import charts
import config
import data_loader
import data_processor
import exports
import persistence
import styles
import validators

# =========================================================
# 1. CONFIGURACIÓN GENERAL DE LA PÁGINA
# =========================================================
st.set_page_config(
    page_title=config.APP_TITLE,
    page_icon=config.APP_ICON,
    layout=config.APP_LAYOUT,
    initial_sidebar_state=config.APP_SIDEBAR_STATE,
)

# =========================================================
# 2. CARGA DE ESTILOS GLOBALES
# =========================================================
st.markdown(styles.build_global_css(), unsafe_allow_html=True)

# =========================================================
# 3. ESTADO DE SESIÓN
# =========================================================
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if "user_role" not in st.session_state:
    st.session_state["user_role"] = ""

if "df_sales" not in st.session_state:
    st.session_state["df_sales"] = None

if "df_plan_client" not in st.session_state:
    st.session_state["df_plan_client"] = None

if "df_plan_sku" not in st.session_state:
    st.session_state["df_plan_sku"] = None

if "sales_valid" not in st.session_state:
    st.session_state["sales_valid"] = False

if "plan_client_valid" not in st.session_state:
    st.session_state["plan_client_valid"] = False

if "plan_sku_valid" not in st.session_state:
    st.session_state["plan_sku_valid"] = False

if "df_processed_sales" not in st.session_state:
    st.session_state["df_processed_sales"] = None

if "df_mtd_base" not in st.session_state:
    st.session_state["df_mtd_base"] = None

if "mtd_payload" not in st.session_state:
    st.session_state["mtd_payload"] = None

if "report1_payload" not in st.session_state:
    st.session_state["report1_payload"] = None

if "report2_payload" not in st.session_state:
    st.session_state["report2_payload"] = None

if "report2_category_payload" not in st.session_state:
    st.session_state["report2_category_payload"] = None

if "report3_payload" not in st.session_state:
    st.session_state["report3_payload"] = None

if "report4_payload" not in st.session_state:
    st.session_state["report4_payload"] = None

if "currency_mode" not in st.session_state:
    st.session_state["currency_mode"] = config.DEFAULT_CURRENCY

if "exchange_rate" not in st.session_state:
    st.session_state["exchange_rate"] = float(config.DEFAULT_EXCHANGE_RATE)

if "exchange_rate_input_display" not in st.session_state:
    st.session_state["exchange_rate_input_display"] = round(float(config.DEFAULT_EXCHANGE_RATE), 4)

if "mensaje_exito" not in st.session_state:
    st.session_state["mensaje_exito"] = None

if "mensaje_error" not in st.session_state:
    st.session_state["mensaje_error"] = None

if "mensaje_warning" not in st.session_state:
    st.session_state["mensaje_warning"] = None

if "persistent_data_loaded" not in st.session_state:
    st.session_state["persistent_data_loaded"] = False

if "persistent_data_metadata" not in st.session_state:
    st.session_state["persistent_data_metadata"] = None

if "upload_reset_counter" not in st.session_state:
    st.session_state["upload_reset_counter"] = 0

if "suppress_persistent_autoload" not in st.session_state:
    st.session_state["suppress_persistent_autoload"] = False

if "login_error_message" not in st.session_state:
    st.session_state["login_error_message"] = None

# =========================================================
# 3.1 CONTROL DE VERSIÓN DE LÓGICA DE REPORTES
# =========================================================
# Cuando se reemplaza data_processor.py/app.py, Streamlit puede conservar en
# st.session_state reportes construidos con la lógica anterior. Eso hace que
# parezca que el código nuevo no cambió nada.
# Esta llave fuerza a limpiar SOLO los reportes y filtros de R1/R2/R3 para que
# se reconstruyan con la lógica actual. No toca archivos cargados ni Reporte 4.
REPORT_LOGIC_VERSION_R123 = "r123_filtros_categorias_reales_na_v20260624_08"
if st.session_state.get("report_logic_version_r123") != REPORT_LOGIC_VERSION_R123:
    for _key in [
        "mtd_payload",
        "df_mtd_base",
        "report1_payload",
        "report2_payload",
        "report2_category_payload",
        "report3_payload",
    ]:
        st.session_state[_key] = None

    for _key in list(st.session_state.keys()):
        if _key.startswith((
            "report1_",
            "report2_",
            "report3_",
        )):
            st.session_state.pop(_key, None)

    st.session_state["report_logic_version_r123"] = REPORT_LOGIC_VERSION_R123

# =========================================================
# 4. CONFIGURACIÓN GLOBAL DE MONEDA
# =========================================================
def is_blank_number(value) -> bool:
    if value is None:
        return True

    try:
        numeric_value = float(value)
        return math.isnan(numeric_value)
    except (TypeError, ValueError):
        return True


def normalize_currency_mode(currency_value: str | None) -> str:
    return "USD" if str(currency_value or "").strip().upper() == "USD" else config.DEFAULT_CURRENCY


def get_active_currency_mode() -> str:
    return normalize_currency_mode(
        st.session_state.get("currency_mode", config.DEFAULT_CURRENCY)
    )


def get_active_exchange_rate() -> float:
    raw_value = st.session_state.get("exchange_rate", config.DEFAULT_EXCHANGE_RATE)

    try:
        numeric_value = float(raw_value)
    except (TypeError, ValueError):
        numeric_value = float(config.DEFAULT_EXCHANGE_RATE)

    if numeric_value <= 0:
        numeric_value = float(config.DEFAULT_EXCHANGE_RATE)

    return numeric_value


def get_normalized_exchange_rate_4() -> float:
    return round(float(get_active_exchange_rate()), 4)


def set_currency_mode(currency_mode: str) -> None:
    st.session_state["currency_mode"] = normalize_currency_mode(currency_mode)


def get_currency_status_label() -> str:
    return "USD" if get_active_currency_mode() == "USD" else config.DEFAULT_CURRENCY


def get_currency_kpi_suffix() -> str:
    return f"K {get_currency_status_label()}"


def convert_monetary_value(value):
    if is_blank_number(value):
        return value

    numeric_value = float(value)

    if get_active_currency_mode() == "USD":
        exchange_rate = get_active_exchange_rate()
        return numeric_value / exchange_rate

    return numeric_value


def format_monetary_value(
    value,
    is_percent: bool = False,
    allow_blank: bool = False,
) -> str:
    if is_blank_number(value):
        return "" if allow_blank and not is_percent else (
            "0.00%" if is_percent else ("" if allow_blank else "-")
        )

    numeric_value = float(value)

    if is_percent:
        if numeric_value < 0:
            return f"({abs(numeric_value) * 100:,.2f}%)"
        return f"{numeric_value * 100:,.2f}%"

    converted_value = convert_monetary_value(numeric_value)

    # Regla visual: cero real se muestra como guion.
    if abs(float(converted_value)) < 1e-9:
        return "" if allow_blank else "-"

    value_k = float(converted_value) / 1000
    rounded_value = round(value_k)

    # Regla de formato acordada: reportes en miles, SIN decimales.
    # Si al expresarlo en miles redondea a 0, se muestra como guion.
    # No se muestran valores tipo 0.3 / (0.3).
    if rounded_value == 0:
        return "" if allow_blank else "-"

    if rounded_value < 0:
        return f"({abs(rounded_value):,})"
    return f"{rounded_value:,}"


def convert_currency_columns_for_display(df_table, monetary_columns: list[str] | None = None):
    if df_table is None:
        return df_table

    if get_active_currency_mode() != "USD":
        return df_table

    df_display = df_table.copy()

    if monetary_columns is None:
        monetary_columns = [
            "Actual",
            "Plan",
            "PY",
            "Var VS Plan",
            "Var VS PY",
            config.COL_GSNR,
            config.COL_GROSS_MARGIN,
            "Importe Vtas Brutas",
            "Importe Devoluciones",
            "Importe Fact No Embq",
            "Costo Vtas Netas",
        ]

    for column_name in monetary_columns:
        if column_name in df_display.columns:
            df_display[column_name] = df_display[column_name].apply(convert_monetary_value)

    return df_display


def convert_report_table_for_export(df_table):
    return convert_currency_columns_for_display(
        df_table,
        monetary_columns=["Actual", "Plan", "PY", "Var VS Plan", "Var VS PY"],
    )


def build_currency_sidebar_status_html() -> str:
    active_currency = get_currency_status_label()
    exchange_rate_value = get_normalized_exchange_rate_4()

    currency_usage_text = (
        "Conversión activa a dólares."
        if active_currency == "USD"
        else "Visualización en pesos mexicanos."
    )

    return (
        f"<b>Usuario activo:</b> {escape(st.session_state.get('user_role', 'N/A'))}<br>"
        f"<b>Moneda base:</b> {escape(active_currency)}<br>"
        f"<b>Tipo de cambio actual:</b> {exchange_rate_value:,.4f} MXN por USD<br>"
        f"<span style='color:#C8CDD5;'>{currency_usage_text}</span>"
    )


def render_currency_controls() -> None:
    st.markdown("### Moneda")
    st.caption(
        "Primero eliges si quieres ver la información en MXN o en USD. "
        "El tipo de cambio solo se aplica cuando la moneda activa es USD."
    )

    current_currency = get_active_currency_mode()

    st.markdown(
        styles.build_currency_box(
            title="Configuración de moneda",
            subtitle=(
                f"Moneda activa: {get_currency_status_label()} · "
                f"Tipo de cambio actual: {get_normalized_exchange_rate_4():,.4f} MXN por USD"
            ),
        ),
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(2)

    with col1:
        st.button(
            "Usar MXN",
            key="btn_currency_mxn",
            on_click=set_currency_mode,
            args=(config.DEFAULT_CURRENCY,),
            use_container_width=True,
            disabled=current_currency == config.DEFAULT_CURRENCY,
        )

    with col2:
        st.button(
            "Cambiar a USD",
            key="btn_currency_usd",
            on_click=set_currency_mode,
            args=("USD",),
            use_container_width=True,
            disabled=current_currency == "USD",
        )

    with st.expander("Configurar tipo de cambio"):
        st.caption("Este valor solo se usa cuando la moneda activa es USD.")

        raw_exchange_rate = st.number_input(
            "Tipo de cambio (MXN por 1 USD)",
            min_value=0.0001,
            value=float(get_normalized_exchange_rate_4()),
            step=0.0001,
            format="%.4f",
            key="exchange_rate_input_display",
        )

        clean_exchange_rate = round(float(raw_exchange_rate), 4)

        if clean_exchange_rate <= 0:
            clean_exchange_rate = float(config.DEFAULT_EXCHANGE_RATE)

        st.session_state["exchange_rate"] = clean_exchange_rate

# =========================================================
# 4.1 HELPER DE VISTA PREVIA
# =========================================================
def render_preview_expander(
    title: str,
    df_preview,
    rows: int = 10,
    convert_currency: bool = False,
) -> None:
    if df_preview is None or df_preview.empty:
        return

    preview_df = df_preview.head(rows).copy()

    if convert_currency:
        preview_df = convert_currency_columns_for_display(preview_df)

    with st.expander(title, expanded=False):
        st.dataframe(preview_df, width="stretch")


def remove_private_processed_columns(df_table):
    """
    Oculta columnas internas/sensibles de la base procesada en vistas previas
    y cualquier descarga directa de esa sección.

    Nota: la base procesada completa se conserva en sesión para cálculos,
    reportes, tarjetas y gráficas. Esto solo afecta lo que se muestra/exporta
    desde Visión general.
    """
    if df_table is None:
        return df_table

    hidden_columns = {
        "Gross Margin",
        "Costo Vtas Netas",
        getattr(config, "COL_GROSS_MARGIN", "Gross Margin"),
    }

    columns_to_drop = [
        column_name for column_name in df_table.columns
        if str(column_name).strip() in hidden_columns
    ]

    if not columns_to_drop:
        return df_table

    return df_table.drop(columns=columns_to_drop, errors="ignore")

# =========================================================
# 4.2 HELPERS DE ALERTAS VISUALES
# =========================================================
def set_success_message(message: str) -> None:
    st.session_state["mensaje_exito"] = message


def set_error_message(message: str) -> None:
    st.session_state["mensaje_error"] = message


def set_warning_message(message: str) -> None:
    st.session_state["mensaje_warning"] = message


def render_global_alerts() -> None:
    if st.session_state.get("mensaje_exito"):
        st.success(st.session_state["mensaje_exito"])
        st.session_state["mensaje_exito"] = None

    if st.session_state.get("mensaje_error"):
        st.error(st.session_state["mensaje_error"])
        st.session_state["mensaje_error"] = None

    if st.session_state.get("mensaje_warning"):
        st.warning(st.session_state["mensaje_warning"])
        st.session_state["mensaje_warning"] = None

# =========================================================

# =========================================================
# 4.3 HELPERS DE ROLES Y PERSISTENCIA TEMPORAL
# =========================================================
def is_admin_user() -> bool:
    """
    Identifica si el usuario actual puede cargar y guardar archivos.
    Para esta fase, admin / admin será el perfil de carga.
    """
    current_user = str(st.session_state.get("user_role", "")).strip()
    admin_users = getattr(config, "ADMIN_USERS", ["admin"])
    return current_user in admin_users


def get_persistent_data_folder() -> Path:
    """
    Carpeta local de respaldo para ejecución en localhost.
    La persistencia principal se administra desde persistence.py.
    """
    return persistence.get_local_persistence_folder()


def get_persistent_data_file() -> Path:
    return persistence.get_local_persistence_file()


def delete_persistent_data() -> bool:
    """
    Borra la carga administrativa guardada para viewers y limpia datos calculados
    de la sesión actual.
    """
    try:
        persistence.delete_dashboard_payload()

        st.session_state["persistent_data_loaded"] = False
        st.session_state["persistent_data_metadata"] = None
        st.session_state["suppress_persistent_autoload"] = True

        st.session_state["df_processed_sales"] = None
        clear_report_payloads()

        set_success_message("Carga guardada para viewers eliminada correctamente.")
        return True

    except Exception as exc:
        set_error_message(f"No fue posible borrar la carga guardada. Detalle: {exc}")
        return False

def clear_current_session_data() -> bool:
    """
    Limpia la carga actual de la sesión admin y reinicia visualmente los file_uploader.
    Sirve para empezar desde cero sin que se mezclen archivos anteriores.
    """
    try:
        keys_to_reset = {
            "df_sales": None,
            "df_plan_client": None,
            "df_plan_sku": None,
            "df_processed_sales": None,
            "sales_valid": False,
            "plan_client_valid": False,
            "plan_sku_valid": False,
            "sales_missing_columns": [],
            "plan_client_missing_columns": [],
            "plan_sku_missing_columns": [],
            "sales_file_name": "",
            "plan_client_file_name": "",
            "plan_sku_file_name": "",
            "master_file_name": "",
            "master_upload_signature": "",
            "persistent_data_loaded": False,
            "persistent_data_metadata": None,
            "suppress_persistent_autoload": True,
            "sales_upload_signature": "",
            "plan_client_upload_signature": "",
            "plan_sku_upload_signature": "",
            "master_upload_signature": "",
            "master_file_name": "",
        }

        for key, value in keys_to_reset.items():
            st.session_state[key] = value

        # Cambia las llaves de los file_uploader para que Streamlit Cloud
        # olvide visualmente los archivos que seguían seleccionados en el navegador.
        st.session_state["upload_reset_counter"] = int(
            st.session_state.get("upload_reset_counter", 0)
        ) + 1

        clear_report_payloads()
        set_success_message("Sesión limpiada correctamente. Puedes volver a cargar los archivos desde cero.")
        return True

    except Exception as exc:
        set_error_message(f"No fue posible limpiar la sesión. Detalle: {exc}")
        return False


def persistent_data_exists() -> bool:
    return persistence.persistent_data_exists()


def should_autoload_persistent_data() -> bool:
    """
    Decide si la app debe intentar recuperar la última carga guardada.

    Regla corregida para Streamlit Cloud:
    - Si la sesión ya tiene datos cargados, no se toca nada.
    - Si la sesión está vacía, SIEMPRE se intenta leer el respaldo persistente.

    No se usa suppress_persistent_autoload para bloquear la recuperación
    después de reboot, porque esa bandera podía impedir que la app jalara el
    archivo aunque sí existiera en GitHub.
    """
    return st.session_state.get("df_sales") is None


def ensure_persistent_data_loaded_if_available(show_message: bool = False) -> bool:
    """
    Intenta cargar la última carga administrativa guardada cuando la sesión
    actual está vacía.

    Se llama al inicio del flujo principal y en Carga de datos. Si GitHub no
    tiene payload o hay algún problema temporal, simplemente deja la sesión
    vacía sin romper la app.
    """
    if st.session_state.get("df_sales") is not None:
        return True

    return load_persistent_data_to_session(show_message=show_message)


def clear_report_payloads() -> None:
    """
    Limpia reportes construidos cuando cambia la fuente de datos.
    No borra archivos cargados ni vistas previas.
    """
    for key in [
        "mtd_payload",
        "df_mtd_base",
        "report1_payload",
        "report2_payload",
        "report2_category_payload",
        "report3_payload",
        "report4_payload",
    ]:
        st.session_state[key] = None


def clear_user_generated_work_state() -> None:
    """
    Limpia TODO lo que un usuario pudo construir dentro de su propia sesión.

    Regla de negocio para viewers:
    - La carga administrativa compartida SOLO ahorra el paso de cargar el Excel.
    - La base procesada, Base MTD, reportes, filtros y descargas construidas
      deben iniciar vacías para cada sesión/usuario.
    """
    st.session_state["df_processed_sales"] = None
    clear_report_payloads()

    keys_to_clear_by_prefix = (
        "base_mtd_",
        "report1_",
        "report2_",
        "report3_",
        "report4_",
    )

    for key in list(st.session_state.keys()):
        if key.startswith(keys_to_clear_by_prefix):
            st.session_state.pop(key, None)


def build_persistent_metadata() -> dict:
    mexico_tz = ZoneInfo("America/Mexico_City")

    return {
        "updated_at": datetime.now(mexico_tz).strftime("%d/%m/%Y %H:%M"),
        "updated_by": st.session_state.get("user_role", "admin"),
        "sales_file_name": st.session_state.get("sales_file_name", "Archivo de ventas"),
        "plan_client_file_name": st.session_state.get("plan_client_file_name", "Plan2026 by Client"),
        "plan_sku_file_name": st.session_state.get("plan_sku_file_name", "Plan2026 by SKU"),
    }


def save_current_data_for_viewers() -> bool:
    """
    Guarda la carga actual para que usuarios viewer puedan consultarla
    sin subir archivos.

    La sesión se conserva en st.session_state para velocidad, pero el respaldo
    real se delega a persistence.py para no depender únicamente del entorno
    temporal de Streamlit Cloud.
    """
    required_data_loaded = all(
        [
            st.session_state.get("df_sales") is not None,
            st.session_state.get("df_plan_client") is not None,
            st.session_state.get("df_plan_sku") is not None,
        ]
    )

    required_data_valid = all(
        [
            st.session_state.get("sales_valid", False),
            st.session_state.get("plan_client_valid", False),
            st.session_state.get("plan_sku_valid", False),
        ]
    )

    if not required_data_loaded or not required_data_valid:
        set_warning_message(
            "Para guardar la carga administrativa, primero deben estar cargados y validados los tres archivos."
        )
        return False

    metadata = build_persistent_metadata()

    payload = {
        "metadata": metadata,
        "payload_version": "viewer_raw_inputs_only_v3",
        "df_sales": st.session_state.get("df_sales"),
        "df_plan_client": st.session_state.get("df_plan_client"),
        "df_plan_sku": st.session_state.get("df_plan_sku"),
        # IMPORTANTE:
        # No se guarda df_processed_sales en la carga compartida.
        # Cada viewer debe procesar ventas en su propia sesión.
        "sales_valid": st.session_state.get("sales_valid", False),
        "plan_client_valid": st.session_state.get("plan_client_valid", False),
        "plan_sku_valid": st.session_state.get("plan_sku_valid", False),
        "sales_missing_columns": st.session_state.get("sales_missing_columns", []),
        "plan_client_missing_columns": st.session_state.get("plan_client_missing_columns", []),
        "plan_sku_missing_columns": st.session_state.get("plan_sku_missing_columns", []),
        "sales_file_name": st.session_state.get("sales_file_name", "Archivo cargado por administrador"),
        "plan_client_file_name": st.session_state.get("plan_client_file_name", "Archivo cargado por administrador"),
        "plan_sku_file_name": st.session_state.get("plan_sku_file_name", "Archivo cargado por administrador"),
    }

    try:
        persistence.save_dashboard_payload(payload)

        st.session_state["persistent_data_loaded"] = True
        st.session_state["persistent_data_metadata"] = metadata
        st.session_state["suppress_persistent_autoload"] = False
        set_success_message(
            "Carga administrativa guardada correctamente. Ya está disponible para usuarios viewer."
        )
        return True
    except Exception as exc:
        set_error_message(f"No fue posible guardar la carga administrativa. Detalle: {exc}")
        return False

def load_persistent_data_to_session(show_message: bool = False) -> bool:
    """
    Carga en la sesión actual la última información guardada por admin.

    Corrección clave:
    En vez de depender primero de persistent_data_exists(), se intenta cargar
    directamente el payload. Esto evita que una verificación previa bloquee la
    restauración en Streamlit Cloud aunque el archivo sí exista en GitHub.
    """
    if st.session_state.get("persistent_data_loaded") and st.session_state.get("df_sales") is not None:
        return True

    try:
        payload = persistence.load_dashboard_payload()

        if not payload:
            return False

        df_sales = payload.get("df_sales")
        df_plan_client = payload.get("df_plan_client")
        df_plan_sku = payload.get("df_plan_sku")

        if df_sales is None or df_plan_client is None or df_plan_sku is None:
            return False

        st.session_state["df_sales"] = df_sales
        st.session_state["df_plan_client"] = df_plan_client
        st.session_state["df_plan_sku"] = df_plan_sku

        # IMPORTANTE:
        # La carga administrativa compartida solo trae las bases originales.
        # La base procesada, reportes y filtros se limpian para que cada viewer
        # viva el flujo completo en su propia sesión.
        clear_user_generated_work_state()

        st.session_state["sales_valid"] = payload.get("sales_valid", True)
        st.session_state["plan_client_valid"] = payload.get("plan_client_valid", True)
        st.session_state["plan_sku_valid"] = payload.get("plan_sku_valid", True)

        st.session_state["sales_missing_columns"] = payload.get("sales_missing_columns", [])
        st.session_state["plan_client_missing_columns"] = payload.get("plan_client_missing_columns", [])
        st.session_state["plan_sku_missing_columns"] = payload.get("plan_sku_missing_columns", [])

        st.session_state["sales_file_name"] = payload.get("sales_file_name", "Archivo cargado por administrador")
        st.session_state["plan_client_file_name"] = payload.get("plan_client_file_name", "Archivo cargado por administrador")
        st.session_state["plan_sku_file_name"] = payload.get("plan_sku_file_name", "Archivo cargado por administrador")

        metadata = payload.get("metadata", {})
        st.session_state["persistent_data_metadata"] = metadata
        st.session_state["persistent_data_loaded"] = True
        st.session_state["suppress_persistent_autoload"] = False

        clear_report_payloads()

        if show_message:
            set_success_message("Información cargada automáticamente desde la última carga administrativa.")

        return True
    except Exception as exc:
        set_error_message(f"No fue posible cargar la información guardada. Detalle: {exc}")
        return False

def get_menu_options_for_current_user() -> list[str]:
    """
    Admin ve todo. Viewer no ve Carga de datos.

    Dashboard se agrega al final del flujo, debajo de Base MTD, porque
    depende de la base procesada, Base MTD y reportes previamente construidos.
    """
    base_options = [option for option in list(config.MAIN_MENU_OPTIONS) if option != "Dashboard"]

    if "Base MTD" in base_options:
        insert_position = base_options.index("Base MTD") + 1
        base_options.insert(insert_position, "Dashboard")
    else:
        base_options.append("Dashboard")

    if is_admin_user():
        return base_options

    return [option for option in base_options if option != "Carga de datos"]


def render_persistent_data_status() -> None:
    metadata = st.session_state.get("persistent_data_metadata")

    if st.session_state.get("df_sales") is not None:
        if metadata:
            updated_at = metadata.get("updated_at", "fecha no disponible")
            updated_by = metadata.get("updated_by", "administrador")
            st.success(
                f"Información disponible para consulta. Última carga administrativa: {updated_at} por {updated_by}."
            )
        else:
            st.success("Información disponible en sesión para consulta.")
        return

    if not is_admin_user():
        st.warning(
            "Todavía no hay información cargada por administrador. Solicita que un usuario admin realice la carga inicial."
        )
# 5. FUNCIONES DE AUTENTICACIÓN
# =========================================================
def check_login() -> None:
    user = st.session_state.get("input_user", "").strip()
    password = st.session_state.get("input_password", "").strip()

    valid_users = dict(getattr(config, "VALID_USERS", {"admin": "admin"}))
    valid_users.setdefault("admin", "admin")
    valid_users.setdefault("viewer", "viewer")

    if user in valid_users and valid_users[user] == password:
        # Cada inicio de sesión debe arrancar con una experiencia limpia.
        # Esto evita que un viewer herede lo que construyó el admin u otro viewer
        # en el mismo navegador/sesión anterior.
        previous_user = st.session_state.get("user_role", "")
        if previous_user != user or user == "viewer":
            clear_user_generated_work_state()

        # Limpia cualquier error anterior del login para que no se arrastre
        # a la pantalla principal después de autenticar correctamente.
        st.session_state["authenticated"] = True
        st.session_state["user_role"] = user
        st.session_state["login_error_message"] = None
        st.session_state["mensaje_error"] = None
        st.session_state["mensaje_warning"] = None
    else:
        # Este error pertenece únicamente a la pantalla de login.
        # No se manda a render_global_alerts para evitar que aparezca dentro del dashboard.
        st.session_state["authenticated"] = False
        st.session_state["user_role"] = ""
        st.session_state["login_error_message"] = "Credenciales incorrectas. Verifica usuario y contraseña."


def logout() -> None:
    # Al cerrar sesión se limpia lo que el usuario construyó.
    # Las bases cargadas pueden permanecer en memoria local, pero los procesamientos
    # y reportes NO deben pasar de un usuario/rol a otro.
    clear_user_generated_work_state()

    st.session_state["authenticated"] = False
    st.session_state["user_role"] = ""
    st.session_state["input_user"] = ""
    st.session_state["input_password"] = ""
    st.session_state["currency_mode"] = config.DEFAULT_CURRENCY
    st.session_state["exchange_rate"] = float(config.DEFAULT_EXCHANGE_RATE)
    st.session_state.pop("exchange_rate_input_display", None)

# =========================================================
# 6. PANTALLA DE LOGIN
# =========================================================
def render_login_screen() -> None:
    # Aplica la imagen de fondo únicamente en la pantalla de inicio de sesión.
    st.markdown(
        styles.apply_login_background("assets/fondo.png"),
        unsafe_allow_html=True,
    )

    left_col, center_col, right_col = st.columns([1, 1.5, 1])

    with center_col:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown(styles.build_hero_section(), unsafe_allow_html=True)

        # Login con inputs normales para conservar el diseño original.
        # La contraseña usa on_change para que Enter dispare la misma validación
        # que el botón, sin depender de st.form.
        st.text_input("Usuario", key="input_user")
        st.text_input(
            "Contraseña",
            type="password",
            key="input_password",
            on_change=check_login,
        )

        st.markdown("<br>", unsafe_allow_html=True)
        st.button(
            "Iniciar sesión",
            on_click=check_login,
            use_container_width=True,
        )

        if st.session_state.get("login_error_message"):
            st.error(st.session_state["login_error_message"])

# =========================================================
# 7. ENCABEZADO PRINCIPAL
# =========================================================
def render_main_header() -> None:
    st.markdown('<div class="top-header-bar-bg"></div>', unsafe_allow_html=True)

    col1, col2 = st.columns([5.8, 1.35], gap="large")

    with col1:
        st.markdown(
            f"""
            <div class="header-inline-row">
                <div class="brand-logo-box"></div>
                <div class="brand-title-group">
                    <div class="brand-title">{escape(config.MAIN_TITLE)}</div>
                    <div class="brand-subtitle">{escape(config.SUBTITLE)}</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown('<div class="header-logout-wrap">', unsafe_allow_html=True)
        st.button("Cerrar sesión", on_click=logout, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

# =========================================================
# 8. HELPERS DE EXPORTACIÓN
# =========================================================
EXCEL_MIME = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


def build_report_context_title(report_name: str, year: int | None, month: int | None) -> str:
    if year is None or month is None:
        period_text = "Periodo no especificado"
    else:
        period_text = f"{get_month_label(int(month))} {int(year)}"

    currency_label = get_currency_status_label()

    if currency_label == "USD":
        return (
            f"{report_name} | {period_text} | USD | "
            f"TC: {get_normalized_exchange_rate_4():,.4f} MXN/USD"
        )

    return f"{report_name} | {period_text} | MXN"


def build_excel_filename(base_name: str, year: int | None = None, month: int | None = None) -> str:
    currency_label = get_currency_status_label().lower()

    if year is not None and month is not None:
        month_label = get_month_label(int(month)).lower()
        return f"{base_name}_{month_label}_{int(year)}_{currency_label}.xlsx"

    return f"{base_name}_{currency_label}.xlsx"


def render_icon_download_button(
    data: bytes,
    file_name: str,
    key: str,
    help_text: str,
) -> None:
    st.download_button(
        label="⭳",
        data=data,
        file_name=file_name,
        mime=EXCEL_MIME,
        key=key,
        help=help_text,
        use_container_width=False,
    )


def get_current_report_1_export_tables() -> dict | None:
    payload = st.session_state.get("report1_payload")
    if payload is None:
        return None

    # Las descargas NO deben depender de los filtros visuales.
    # Se exportan las tablas completas construidas para el periodo activo.
    return {
        "summary": payload["summary"],
        "report_title": build_report_context_title(
            "Reporte 1 - Oficina de ventas",
            payload["summary"]["latest_year"],
            payload["summary"]["latest_month"],
        ),
        "mtd_without_kens": convert_report_table_for_export(payload["mtd_without_kens_table"]),
        "ytd_without_kens": convert_report_table_for_export(payload["ytd_without_kens_table"]),
    }

def get_current_report_2_segment_export_tables() -> dict | None:
    payload = st.session_state.get("report2_payload")
    if payload is None:
        return None

    # Las descargas NO deben depender de los filtros visuales.
    return {
        "summary": payload["summary"],
        "report_title": build_report_context_title(
            "Reporte 2 - Segment x Region",
            payload["summary"]["latest_year"],
            payload["summary"]["latest_month"],
        ),
        "mtd": convert_report_table_for_export(payload["mtd_segment_region_table"]),
        "ytd": convert_report_table_for_export(payload["ytd_segment_region_table"]),
    }

def get_current_report_2_category_export_tables() -> dict | None:
    payload = st.session_state.get("report2_category_payload")
    if payload is None:
        return None

    # Las descargas NO deben depender de los filtros visuales.
    return {
        "summary": payload["summary"],
        "report_title": build_report_context_title(
            "Reporte 2 - Category",
            payload["summary"]["latest_year"],
            payload["summary"]["latest_month"],
        ),
        "mtd": convert_report_table_for_export(payload["mtd_category_table"]),
        "ytd": convert_report_table_for_export(payload["ytd_category_table"]),
    }

def get_current_report_3_export_tables() -> dict | None:
    payload = st.session_state.get("report3_payload")
    if payload is None:
        return None

    # Las descargas NO deben depender de los filtros visuales.
    return {
        "summary": payload["summary"],
        "report_title": build_report_context_title(
            "Reporte 3 - Channel",
            payload["summary"]["latest_year"],
            payload["summary"]["latest_month"],
        ),
        "mtd": convert_report_table_for_export(payload["mtd_channel_table"]),
        "ytd": convert_report_table_for_export(payload["ytd_channel_table"]),
    }

def get_current_report_4_export_tables() -> dict | None:
    payload = st.session_state.get("report4_payload")
    if payload is None:
        return None

    return {
        "summary": payload["summary"],
        "report_title": build_report_context_title(
            "Reporte 4 - Ranking de Clientes",
            payload["summary"]["latest_year"],
            payload["summary"]["latest_month"],
        ),
        # Para exportación global se usa el detalle completo MTD/YTD,
        # respetando el ranking dinámico y mostrando el grupo de cada cliente.
        # La descarga global debe respetar la misma vista ejecutiva que se ve en pantalla:
        # Top 15 cliente por cliente + Total Top 15 + bloques resumen + Total Mexico.
        "mtd": convert_report_table_for_export(payload["mtd_top_clients_table"]),
        "ytd": convert_report_table_for_export(payload["ytd_top_clients_table"]),
        "mtd_summary": convert_report_table_for_export(payload["mtd_summary_table"]),
        "ytd_summary": convert_report_table_for_export(payload["ytd_summary_table"]),
    }


def build_base_mtd_plan_summary_export_df(plan_summary: dict | None):
    if not plan_summary:
        return data_processor.pd.DataFrame()

    rows = [
        {
            "Validación": "MTD Plan Cliente vs Plan SKU",
            "Plan Cliente": plan_summary.get("mtd_plan_client", 0.0),
            "Plan SKU": plan_summary.get("mtd_plan_sku", 0.0),
            "Diferencia": plan_summary.get("mtd_plan_diff", 0.0),
            "Estatus": "Coincide" if plan_summary.get("mtd_plan_match", False) else "No coincide",
        },
        {
            "Validación": "YTD Plan Cliente vs Plan SKU",
            "Plan Cliente": plan_summary.get("ytd_plan_client", 0.0),
            "Plan SKU": plan_summary.get("ytd_plan_sku", 0.0),
            "Diferencia": plan_summary.get("ytd_plan_diff", 0.0),
            "Estatus": "Coincide" if plan_summary.get("ytd_plan_match", False) else "No coincide",
        },
    ]

    return data_processor.pd.DataFrame(rows)


def get_current_base_mtd_export_tables() -> dict | None:
    payload = st.session_state.get("mtd_payload")
    if payload is None:
        return None

    return {
        "summary": payload,
        "report_title": build_report_context_title(
            "Base MTD",
            payload["latest_year"],
            payload["latest_month"],
        ),
        "client_table": convert_report_table_for_export(payload["client_table"]),
        "sku_table": convert_report_table_for_export(payload["sku_table"]),
        "bts_table": convert_report_table_for_export(payload["bts_table"]),
        "plan_summary_table": convert_report_table_for_export(
            build_base_mtd_plan_summary_export_df(payload.get("plan_summary"))
        ),
    }


def get_full_reports_export_bytes() -> bytes:
    base_mtd_tables = get_current_base_mtd_export_tables()
    report_1_tables = get_current_report_1_export_tables()
    report_2_segment_tables = get_current_report_2_segment_export_tables()
    report_2_category_tables = get_current_report_2_category_export_tables()
    report_3_tables = get_current_report_3_export_tables()
    report_4_tables = get_current_report_4_export_tables()

    return exports.build_full_reports_excel_bytes(
        base_mtd_tables=base_mtd_tables,
        report_1_tables=report_1_tables,
        report_2_segment_tables=report_2_segment_tables,
        report_2_category_tables=report_2_category_tables,
        report_3_tables=report_3_tables,
        report_4_tables=report_4_tables,
    )

# =========================================================
# 9. SIDEBAR
# =========================================================
def render_sidebar() -> str:
    with st.sidebar:
        st.markdown(
            """
            <div class="sidebar-brand">
                <div class="sidebar-brand-box"></div>
                <div class="sidebar-brand-text">ACCO BRANDS</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("## Panel de navegación")

        st.markdown(
            styles.build_sidebar_box(build_currency_sidebar_status_html()),
            unsafe_allow_html=True,
        )

        render_currency_controls()

        menu_options = get_menu_options_for_current_user()

        selected_option = st.radio(
            "Selecciona una sección",
            menu_options,
            index=0,
        )

        st.markdown("---")
        st.markdown("### Descarga global")

        has_any_report = any(
            [
                st.session_state.get("mtd_payload") is not None,
                st.session_state.get("report1_payload") is not None,
                st.session_state.get("report2_payload") is not None,
                st.session_state.get("report2_category_payload") is not None,
                st.session_state.get("report3_payload") is not None,
                st.session_state.get("report4_payload") is not None,
            ]
        )

        if has_any_report:
            all_reports_bytes = get_full_reports_export_bytes()
            st.download_button(
                label="Descargar todos los reportes",
                data=all_reports_bytes,
                file_name=build_excel_filename("reportes_corporativos"),
                mime=EXCEL_MIME,
                key="btn_sidebar_download_all_reports",
                use_container_width=True,
            )
        else:
            st.caption("Construye al menos un reporte para habilitar la descarga global.")

        st.markdown("---")
        st.markdown("### Estado del proyecto")
        st.caption("Etapa actual: Etapa 8")
        st.caption(
            "Módulos activos: config.py, styles.py, data_loader.py, "
            "validators.py, data_processor.py, exports.py, charts.py y app.py"
        )

        return selected_option

# =========================================================
# 10. VALIDACIÓN AUXILIAR
# =========================================================
def render_file_validation_result(
    is_valid: bool,
    missing_columns: list[str],
    success_message: str,
) -> None:
    if is_valid:
        st.success(success_message)
    else:
        st.error(config.MSG_VALIDATION_FAIL)
        if missing_columns:
            st.warning(f"Columnas faltantes: {', '.join(missing_columns)}")


# =========================================================
# 10.1 CARGA DESDE SHAREPOINT SINCRONIZADO
# =========================================================
def apply_synced_sharepoint_payload_to_session(payload: dict, source_file_name: str) -> bool:
    """
    Recibe los DataFrames leídos desde la carpeta sincronizada de SharePoint
    y los deja en las mismas variables de sesión que usa la carga manual.

    No procesa automáticamente la base ni construye reportes; solo carga y valida.
    """
    df_sales = payload.get("df_sales")
    df_plan_client = payload.get("df_plan_client")
    df_plan_sku = payload.get("df_plan_sku")

    is_valid_sales, missing_sales = validators.validate_required_columns(
        df_sales,
        config.EXPECTED_COLUMNS_SALES,
    )
    is_valid_plan_client, missing_plan_client = validators.validate_required_columns(
        df_plan_client,
        config.EXPECTED_COLUMNS_PLAN_CLIENT,
    )
    is_valid_plan_sku, missing_plan_sku = validators.validate_required_columns(
        df_plan_sku,
        config.EXPECTED_COLUMNS_PLAN_SKU,
    )

    st.session_state["df_sales"] = df_sales
    st.session_state["df_plan_client"] = df_plan_client
    st.session_state["df_plan_sku"] = df_plan_sku

    st.session_state["sales_valid"] = is_valid_sales
    st.session_state["plan_client_valid"] = is_valid_plan_client
    st.session_state["plan_sku_valid"] = is_valid_plan_sku

    st.session_state["sales_missing_columns"] = missing_sales
    st.session_state["plan_client_missing_columns"] = missing_plan_client
    st.session_state["plan_sku_missing_columns"] = missing_plan_sku

    st.session_state["sales_file_name"] = f"{source_file_name} | BASE SAP"
    st.session_state["plan_client_file_name"] = f"{source_file_name} | Plan2026 by Client"
    st.session_state["plan_sku_file_name"] = f"{source_file_name} | Plan2026 by SKU"

    st.session_state["df_processed_sales"] = None
    st.session_state["suppress_persistent_autoload"] = True
    st.session_state["persistent_data_loaded"] = False
    st.session_state["persistent_data_metadata"] = None

    clear_report_payloads()

    return all([is_valid_sales, is_valid_plan_client, is_valid_plan_sku])


def load_synced_sharepoint_file_to_session() -> bool:
    """
    Carga automáticamente el Excel sincronizado desde OneDrive/SharePoint.

    Esta opción no usa API, usuario, contraseña ni link de navegador.
    Solo lee la ruta local configurada en config.py.
    """
    if not getattr(config, "SYNCED_SHAREPOINT_ENABLED", False):
        set_warning_message("La carga desde SharePoint sincronizado está deshabilitada en config.py.")
        return False

    file_path = str(getattr(config, "SYNCED_SHAREPOINT_FILE_PATH", "") or "").strip()
    source_file_name = str(
        getattr(config, "SYNCED_SHAREPOINT_FILE_NAME", "Archivo sincronizado de SharePoint")
        or "Archivo sincronizado de SharePoint"
    ).strip()

    if not file_path:
        set_error_message("No se encontró la ruta del archivo sincronizado en config.py.")
        return False

    try:
        payload = data_loader.load_dashboard_excel_from_synced_path(file_path)
        all_valid = apply_synced_sharepoint_payload_to_session(
            payload=payload,
            source_file_name=source_file_name,
        )

        if all_valid:
            set_success_message(
                getattr(
                    config,
                    "SYNCED_SHAREPOINT_LOAD_SUCCESS",
                    "Archivo cargado correctamente desde la carpeta sincronizada de SharePoint.",
                )
            )
        else:
            set_warning_message(
                "El archivo sincronizado se cargó, pero alguna hoja no contiene las columnas mínimas esperadas. "
                "Revisa las validaciones mostradas en pantalla."
            )

        return all_valid

    except Exception as exc:
        set_error_message(
            f"{getattr(config, 'SYNCED_SHAREPOINT_LOAD_ERROR', 'No fue posible cargar el archivo desde SharePoint sincronizado.')} "
            f"Detalle: {exc}"
        )
        return False


# =========================================================
# 11. HELPERS DE FILTROS DE PERIODO
# =========================================================
def get_available_year_month_options() -> tuple[list[int], int | None, int | None]:
    df_processed = st.session_state.get("df_processed_sales")

    if df_processed is None or df_processed.empty:
        return [], None, None

    if config.COL_YEAR not in df_processed.columns or config.COL_MONTH not in df_processed.columns:
        return [], None, None

    valid_periods = (
        df_processed[[config.COL_YEAR, config.COL_MONTH]]
        .dropna()
        .copy()
    )

    if valid_periods.empty:
        return [], None, None

    valid_periods[config.COL_YEAR] = valid_periods[config.COL_YEAR].astype(int)
    valid_periods[config.COL_MONTH] = valid_periods[config.COL_MONTH].astype(int)

    valid_periods = valid_periods[
        valid_periods[config.COL_MONTH].between(1, 12)
    ].copy()

    if valid_periods.empty:
        return [], None, None

    years = sorted(valid_periods[config.COL_YEAR].unique().tolist())
    latest_year = int(valid_periods[config.COL_YEAR].max())
    latest_month = int(
        valid_periods.loc[
            valid_periods[config.COL_YEAR] == latest_year,
            config.COL_MONTH,
        ].max()
    )

    return years, latest_year, latest_month


def get_available_months_for_year(selected_year: int) -> list[int]:
    df_processed = st.session_state.get("df_processed_sales")

    if df_processed is None or df_processed.empty:
        return []

    if config.COL_YEAR not in df_processed.columns or config.COL_MONTH not in df_processed.columns:
        return []

    valid_months = (
        df_processed.loc[
            df_processed[config.COL_YEAR] == selected_year,
            config.COL_MONTH,
        ]
        .dropna()
        .astype(int)
        .tolist()
    )

    valid_months = sorted({month for month in valid_months if 1 <= month <= 12})
    return valid_months


def get_month_label(month_number: int) -> str:
    month_labels = {
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
    return month_labels.get(month_number, str(month_number))


def render_period_filter_block(
    block_title: str,
    year_key: str,
    month_key: str,
) -> tuple[int | None, int | None]:
    years, latest_year, latest_month = get_available_year_month_options()

    st.markdown(
        f"""
        <div class="filter-box">
            <div class="filter-box-title">{escape(block_title)}</div>
            <div class="filter-box-subtitle">
                Selecciona el año y el mes de corte para recalcular este bloque.
                El MTD mostrará solo el mes elegido y el YTD acumulará de enero a ese mismo mes.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if not years:
        st.info(
            "Primero necesitas procesar la base de ventas para habilitar los filtros de Año y Mes."
        )
        return None, None

    default_year = st.session_state.get(year_key, latest_year)
    if default_year not in years:
        default_year = latest_year

    year_index = years.index(default_year)

    col1, col2 = st.columns(2)

    with col1:
        selected_year = st.selectbox(
            "Año",
            options=years,
            index=year_index,
            key=year_key,
        )

    available_months = get_available_months_for_year(selected_year)

    if not available_months:
        st.warning("No hay meses disponibles para el año seleccionado.")
        return selected_year, None

    default_month = st.session_state.get(month_key)

    if selected_year == latest_year:
        fallback_month = latest_month
    else:
        fallback_month = max(available_months)

    if default_month not in available_months:
        default_month = fallback_month

    month_index = available_months.index(default_month)

    with col2:
        selected_month = st.selectbox(
            "Mes de corte",
            options=available_months,
            index=month_index,
            key=month_key,
            format_func=get_month_label,
        )

    return selected_year, selected_month

# =========================================================
# 11.1 HELPERS DE FILTROS POR PRIMERA COLUMNA
# =========================================================
def is_special_report_row(row) -> bool:
    return bool(
        row.get("__is_total__", False)
        or row.get("__is_grand_total__", False)
        or row.get("__is_highlight__", False)
    )


def safe_float(value, default: float = 0.0) -> float:
    if value is None:
        return default

    try:
        numeric_value = float(value)
        if math.isnan(numeric_value):
            return default
        return numeric_value
    except (TypeError, ValueError):
        return default


def recalculate_row_metrics(
    template_row,
    actual: float,
    plan,
    py: float,
):
    row = dict(template_row)

    actual_value = safe_float(actual)
    py_value = safe_float(py)

    if plan is None:
        plan_value = None
        var_vs_plan = None
        pct_var_vs_plan = None
    else:
        plan_value = safe_float(plan)
        var_vs_plan = actual_value - plan_value
        pct_var_vs_plan = 0.0 if plan_value == 0 else (actual_value - plan_value) / plan_value

    var_vs_py = actual_value - py_value
    pct_var_vs_py = 0.0 if py_value == 0 else (actual_value - py_value) / py_value

    row["Actual"] = actual_value
    row["Plan"] = plan_value
    row["PY"] = py_value
    row["Var VS Plan"] = var_vs_plan
    row["%Var VS Plan"] = pct_var_vs_plan
    row["Var VS PY"] = var_vs_py
    row["%Var VS PY"] = pct_var_vs_py

    return row


def build_report_2_segment_region_display_label(row) -> str:
    is_grand_total = bool(row.get("__is_grand_total__", False))
    segment_value = str(row.get("Segmento", "")).strip()
    region_value = str(row.get("Región", "")).strip()

    if is_grand_total:
        return segment_value

    if region_value:
        return f"{segment_value} | {region_value}"

    return segment_value


def build_report_3_display_label(row) -> str:
    channel_value = data_processor.normalize_report_3_channel_label(row.get("Channel", ""))
    if channel_value == "GOBA":
        return "BARRILITO"
    return channel_value


def is_filter_option_excluded_row(row) -> bool:
    """
    Excluye únicamente filas de total al construir las opciones de filtros.

    #N/A, VARIOS, Blanks y Other son valores válidos, no se deben ocultar.
    """
    return bool(
        row.get("__is_total__", False)
        or row.get("__is_grand_total__", False)
    )


def is_forbidden_filter_label(label_value: str) -> bool:
    """Oculta placeholders técnicos de la UI; NO oculta #N/A/Blanks/VARIOS/Other."""
    clean_value = str(label_value or "").strip().upper()
    return clean_value in {"ZZZZ", "ZZZ"} or clean_value.endswith("| ZZZZ") or "| ZZZZ" in clean_value


def contains_valid_special_dimension(options: list[str]) -> bool:
    clean_options = {str(value or "").strip().upper() for value in options}
    return bool(clean_options.intersection({"#N/A", "N/A", "NA", "BLANKS", "BLANK", "(BLANK)", "VARIOS", "OTHER"}))


def get_filter_options_from_table(
    df_table,
    label_builder,
) -> list[str]:
    if df_table is None or df_table.empty:
        return []

    options: list[str] = []

    for _, row in df_table.iterrows():
        if is_filter_option_excluded_row(row):
            continue

        label_value = str(label_builder(row)).strip()
        if (
            label_value
            and label_value.lower() not in {"total", "total general", "grand total", "total mexico"}
            and not is_forbidden_filter_label(label_value)
        ):
            options.append(label_value)

    return sorted(set(options))


def get_filter_options_from_multiple_tables(
    tables: list,
    label_builder,
) -> list[str]:
    options: list[str] = []

    for df_table in tables:
        if df_table is None or df_table.empty:
            continue

        for _, row in df_table.iterrows():
            if is_filter_option_excluded_row(row):
                continue

            label_value = str(label_builder(row)).strip()
            if (
                label_value
                and label_value.lower() not in {"total", "total general", "grand total", "total mexico"}
                and not is_forbidden_filter_label(label_value)
            ):
                options.append(label_value)

    return sorted(set(options))


def get_valid_applied_filter_values(
    applied_key: str,
    available_options: list[str],
) -> list[str]:
    if not available_options:
        return []

    applied_values = st.session_state.get(applied_key)

    if not applied_values:
        return available_options.copy()

    valid_values = [value for value in applied_values if value in available_options]

    if not valid_values:
        return available_options.copy()

    # Si aparecen #N/A, Blanks, VARIOS u Other y el filtro viejo no los tenía,
    # se selecciona TODO para que ninguna categoría real quede oculta.
    available_specials = {
        value for value in available_options
        if str(value or "").strip().upper() in {"#N/A", "N/A", "NA", "BLANKS", "BLANK", "(BLANK)", "VARIOS", "OTHER"}
        or "| #N/A" in str(value or "").upper()
        or "| VARIOS" in str(value or "").upper()
        or "| BLANK" in str(value or "").upper()
    }
    if available_specials and not available_specials.issubset(set(valid_values)):
        return available_options.copy()

    # REGLA FORZADA - NO OCULTAR CATEGORÍAS NUEVAS:
    # Si el universo del reporte cambió y el filtro aplicado quedó como subconjunto
    # viejo, se vuelve a seleccionar TODO. Así #N/A, Blanks, VARIOS, Other o
    # dimensiones nuevas no quedan escondidas por session_state anterior.
    options_state_key = applied_key.replace("_applied", "_widget__available_options")
    previous_options = st.session_state.get(options_state_key, [])
    if previous_options and set(previous_options) != set(available_options):
        return available_options.copy()

    return valid_values


def sync_dimension_filter_to_applied_state(
    widget_key: str,
    applied_key: str,
    available_options: list[str],
) -> None:
    widget_values = st.session_state.get(widget_key, [])

    valid_values = [value for value in widget_values if value in available_options]

    if not valid_values and available_options:
        valid_values = available_options.copy()

    st.session_state[applied_key] = valid_values


def apply_dimension_filter_after_rebuild(
    widget_key: str,
    applied_key: str,
    old_options: list[str],
    new_options: list[str],
    selected_before_rebuild: list[str] | None = None,
) -> None:
    """
    Sincroniza filtros dinámicos después de reconstruir un reporte.

    IMPORTANTE STREAMLIT:
    Esta función puede ejecutarse después de que el multiselect ya fue
    instanciado en el mismo rerun. Por eso NO modifica directamente
    st.session_state[widget_key]. En su lugar deja un valor pendiente,
    hace st.rerun() en el bloque del botón, y render_dimension_filter_block
    aplica ese pendiente ANTES de crear el widget en el siguiente rerun.
    """
    old_options = list(old_options or [])
    new_options = list(new_options or [])

    if selected_before_rebuild is None:
        selected_before_rebuild = st.session_state.get(widget_key, [])

    selected_before_rebuild = list(selected_before_rebuild or [])

    had_all_old_options = (
        not old_options
        or set(selected_before_rebuild) == set(old_options)
    )

    # Regla de estabilidad: si cambió el universo de opciones al reconstruir
    # por año/mes, el filtro vuelve a incluir TODAS las opciones disponibles
    # del nuevo periodo. Así no se quedan fuera #N/A, VARIOS, Blanks, Other
    # ni categorías nuevas solo porque en el periodo anterior no existían.
    options_changed = set(old_options) != set(new_options)

    if options_changed or had_all_old_options:
        final_values = new_options.copy()
    else:
        final_values = [value for value in selected_before_rebuild if value in new_options]

    if not final_values and new_options:
        final_values = new_options.copy()

    st.session_state[f"{widget_key}__pending_values"] = final_values
    st.session_state[applied_key] = final_values
    st.session_state[f"{widget_key}__available_options"] = new_options.copy()


def render_dimension_filter_block(
    filter_label: str,
    widget_key: str,
    applied_key: str,
    available_options: list[str],
) -> list[str]:
    """
    Filtro dinámico seguro para Streamlit.

    Corrección aplicada:
    - El multiselect ya no reutiliza siempre la misma llave visual cuando cambia
      el universo de opciones. Se crea una llave interna por universo de opciones.
    - Así, cuando aparecen categorías nuevas (#N/A, VARIOS, Blanks, Other, etc.),
      el widget se reinicia con TODAS las opciones del periodo nuevo.
    - La llave lógica original se conserva en session_state para que el resto
      del código no cambie.
    """
    if not available_options:
        st.info("No hay valores disponibles para filtrar en este bloque.")
        st.session_state[applied_key] = []
        st.session_state[widget_key] = []
        return []

    available_options = [
        str(value).strip()
        for value in available_options
        if str(value).strip() and not is_forbidden_filter_label(str(value).strip())
    ]
    available_options = sorted(set(available_options))

    options_state_key = f"{widget_key}__available_options"
    pending_values_key = f"{widget_key}__pending_values"

    previous_options = st.session_state.get(options_state_key, [])
    previous_options_set = set(previous_options or [])
    current_options_set = set(available_options)

    options_changed = previous_options_set != current_options_set

    # Si viene una selección pendiente de una reconstrucción, se respeta.
    # Si el universo cambió y no hay pendiente, se selecciona TODO el universo nuevo.
    if pending_values_key in st.session_state:
        candidate_values = st.session_state.pop(pending_values_key)
        default_values = [value for value in candidate_values if value in available_options]
        if not default_values:
            default_values = available_options.copy()
    elif options_changed:
        default_values = available_options.copy()
    else:
        default_values = get_valid_applied_filter_values(applied_key, available_options)

    if not default_values:
        default_values = available_options.copy()

    available_specials = {
        value for value in available_options
        if str(value or "").strip().upper() in {"#N/A", "N/A", "NA", "BLANKS", "BLANK", "(BLANK)", "VARIOS", "OTHER"}
        or "| #N/A" in str(value or "").upper()
        or "| VARIOS" in str(value or "").upper()
        or "| BLANK" in str(value or "").upper()
    }
    if available_specials and not available_specials.issubset(set(default_values)):
        default_values = available_options.copy()

    # Llave visual variable: evita que Streamlit conserve un multiselect viejo
    # que no tenía #N/A / VARIOS / Blanks / Other.
    options_signature = abs(hash(tuple(available_options)))
    ui_widget_key = f"{widget_key}__ui_{options_signature}"

    selected_values = st.multiselect(
        filter_label,
        options=available_options,
        default=default_values,
        key=ui_widget_key,
        placeholder="Selecciona uno o varios valores",
    )

    selected_values = [value for value in selected_values if value in available_options]
    if not selected_values:
        selected_values = available_options.copy()

    # Llaves lógicas usadas por el resto del código.
    st.session_state[widget_key] = selected_values.copy()
    st.session_state[applied_key] = selected_values.copy()
    st.session_state[options_state_key] = available_options.copy()
    st.session_state[f"{widget_key}__current_ui_key"] = ui_widget_key

    return selected_values


def filter_report_1_without_kens_table(
    df_table,
    selected_labels: list[str],
):
    if df_table is None or df_table.empty:
        return df_table

    selected_set = {label for label in set(selected_labels) if not is_forbidden_filter_label(label)}

    normal_rows = df_table[
        ~df_table["__is_total__"].fillna(False)
        & ~df_table["__is_highlight__"].fillna(False)
        & ~df_table.get("__is_grand_total__", False)
    ].copy()

    filtered_normals = normal_rows[
        normal_rows["Oficina de Ventas"].astype(str).isin(selected_set)
    ].copy()

    total_template = df_table[df_table["__is_total__"].fillna(False)].copy()

    rows = []

    for _, row in filtered_normals.iterrows():
        rows.append(dict(row))

    if not total_template.empty:
        total_row_template = total_template.iloc[0].to_dict()

        total_actual = filtered_normals["Actual"].apply(safe_float).sum()
        total_plan = filtered_normals["Plan"].apply(lambda x: safe_float(x, 0.0)).sum()
        total_py = filtered_normals["PY"].apply(safe_float).sum()

        rows.append(
            recalculate_row_metrics(
                total_row_template,
                actual=total_actual,
                plan=total_plan,
                py=total_py,
            )
        )

    return data_processor.pd.DataFrame(rows)



def filter_report_2_segment_region_table(
    df_table,
    selected_labels: list[str],
):
    if df_table is None or df_table.empty:
        return df_table

    selected_set = {label for label in set(selected_labels) if not is_forbidden_filter_label(label)}
    rows: list[dict] = []

    normal_mask = (
        ~df_table["__is_total__"].fillna(False)
        & ~df_table["__is_grand_total__"].fillna(False)
    )

    filtered_normals = df_table.loc[normal_mask].copy()
    filtered_normals["__display_label__"] = filtered_normals.apply(
        build_report_2_segment_region_display_label,
        axis=1,
    )
    filtered_normals = filtered_normals[
        filtered_normals["__display_label__"].isin(selected_set)
    ].copy()

    for _, row in df_table.iterrows():
        is_total = bool(row.get("__is_total__", False))
        is_grand_total = bool(row.get("__is_grand_total__", False))

        if not is_total and not is_grand_total:
            label_value = build_report_2_segment_region_display_label(row)
            if label_value in selected_set:
                row_copy = dict(row)
                row_copy.pop("__display_label__", None)
                rows.append(row_copy)
            continue

        if is_total and not is_grand_total:
            segment_value = str(row.get("Segmento", "")).strip()
            segment_rows = filtered_normals[
                filtered_normals["Segmento"].astype(str).str.strip() == segment_value
            ].copy()

            total_actual = segment_rows["Actual"].apply(safe_float).sum()
            total_plan = segment_rows["Plan"].apply(safe_float).sum()
            total_py = segment_rows["PY"].apply(safe_float).sum()

            rows.append(
                recalculate_row_metrics(
                    row,
                    actual=total_actual,
                    plan=total_plan,
                    py=total_py,
                )
            )
            continue

        if is_grand_total:
            grand_actual = filtered_normals["Actual"].apply(safe_float).sum()
            grand_plan = filtered_normals["Plan"].apply(safe_float).sum()
            grand_py = filtered_normals["PY"].apply(safe_float).sum()

            rows.append(
                recalculate_row_metrics(
                    row,
                    actual=grand_actual,
                    plan=grand_plan,
                    py=grand_py,
                )
            )

    return data_processor.pd.DataFrame(rows)


def filter_report_2_category_table(
    df_table,
    selected_labels: list[str],
):
    if df_table is None or df_table.empty:
        return df_table

    selected_set = {label for label in set(selected_labels) if not is_forbidden_filter_label(label)}
    rows: list[dict] = []

    normal_mask = (
        ~df_table["__is_total__"].fillna(False)
        & ~df_table["__is_grand_total__"].fillna(False)
    )

    filtered_normals = df_table.loc[normal_mask].copy()
    filtered_normals = filtered_normals[
        filtered_normals["Category"].astype(str).isin(selected_set)
    ].copy()

    for _, row in df_table.iterrows():
        is_total = bool(row.get("__is_total__", False))
        is_grand_total = bool(row.get("__is_grand_total__", False))
        category_value = str(row.get("Category", "")).strip()

        if not is_total and not is_grand_total:
            if category_value in selected_set:
                rows.append(dict(row))
            continue

        if is_total and not is_grand_total:
            if category_value not in selected_set:
                continue

            category_rows = filtered_normals[
                filtered_normals["Category"].astype(str).str.strip() == category_value
            ].copy()

            total_actual = category_rows["Actual"].apply(safe_float).sum()
            total_plan = category_rows["Plan"].apply(safe_float).sum()
            total_py = category_rows["PY"].apply(safe_float).sum()

            rows.append(
                recalculate_row_metrics(
                    row,
                    actual=total_actual,
                    plan=total_plan,
                    py=total_py,
                )
            )
            continue

        if is_grand_total:
            grand_actual = filtered_normals["Actual"].apply(safe_float).sum()
            grand_plan = filtered_normals["Plan"].apply(safe_float).sum()
            grand_py = filtered_normals["PY"].apply(safe_float).sum()

            rows.append(
                recalculate_row_metrics(
                    row,
                    actual=grand_actual,
                    plan=grand_plan,
                    py=grand_py,
                )
            )

    return data_processor.pd.DataFrame(rows)


def filter_report_3_channel_table(
    df_table,
    selected_labels: list[str],
):
    if df_table is None or df_table.empty:
        return df_table

    selected_set = {label for label in set(selected_labels) if not is_forbidden_filter_label(label)}
    rows: list[dict] = []

    normal_mask = (
        ~df_table["__is_total__"].fillna(False)
        & ~df_table["__is_grand_total__"].fillna(False)
    )

    filtered_normals = df_table.loc[normal_mask].copy()
    filtered_normals["__display_label__"] = filtered_normals.apply(
        build_report_3_display_label,
        axis=1,
    )
    filtered_normals = filtered_normals[
        filtered_normals["__display_label__"].isin(selected_set)
    ].copy()

    for _, row in df_table.iterrows():
        is_total = bool(row.get("__is_total__", False))
        is_grand_total = bool(row.get("__is_grand_total__", False))

        if not is_total and not is_grand_total:
            label_value = build_report_3_display_label(row)
            if label_value in selected_set:
                row_copy = dict(row)
                row_copy.pop("__display_label__", None)
                rows.append(row_copy)
            continue

        if is_grand_total:
            grand_actual = filtered_normals["Actual"].apply(safe_float).sum()
            grand_plan = filtered_normals["Plan"].apply(safe_float).sum()
            grand_py = filtered_normals["PY"].apply(safe_float).sum()

            rows.append(
                recalculate_row_metrics(
                    row,
                    actual=grand_actual,
                    plan=grand_plan,
                    py=grand_py,
                )
            )

    return data_processor.pd.DataFrame(rows)


def filter_report_4_top_clients_table(
    df_table,
    selected_labels: list[str],
):
    if df_table is None or df_table.empty:
        return df_table

    selected_set = {label for label in set(selected_labels) if not is_forbidden_filter_label(label)}
    rows: list[dict] = []

    normal_mask = (
        ~df_table["__is_total__"].fillna(False)
        & ~df_table["__is_grand_total__"].fillna(False)
    )

    filtered_normals = df_table.loc[normal_mask].copy()
    filtered_normals = filtered_normals[
        filtered_normals["Client Name"].astype(str).isin(selected_set)
    ].copy()

    for _, row in df_table.iterrows():
        is_total = bool(row.get("__is_total__", False))
        is_grand_total = bool(row.get("__is_grand_total__", False))

        if not is_total and not is_grand_total:
            label_value = str(row.get("Client Name", "")).strip()
            if label_value in selected_set:
                rows.append(dict(row))
            continue

        if is_grand_total:
            grand_actual = filtered_normals["Actual"].apply(safe_float).sum()
            grand_plan = filtered_normals["Plan"].apply(safe_float).sum()
            grand_py = filtered_normals["PY"].apply(safe_float).sum()

            rows.append(
                recalculate_row_metrics(
                    row,
                    actual=grand_actual,
                    plan=grand_plan,
                    py=grand_py,
                )
            )

    return data_processor.pd.DataFrame(rows)

# =========================================================
# 12. PROCESAMIENTO DE VENTAS
# =========================================================
def run_sales_processing() -> None:
    df_sales = st.session_state.get("df_sales")

    if df_sales is None:
        set_error_message(config.MSG_PROCESSING_MISSING_FILES)
        return

    is_ready, missing_columns = validators.validate_dataframe_for_processing(
        df_sales,
        config.REQUIRED_COLUMNS_SALES_PROCESS,
    )

    if not is_ready:
        set_error_message(config.MSG_VALIDATION_FAIL)
        set_warning_message(
            f"Columnas faltantes para procesar ventas: {', '.join(missing_columns)}"
        )
        return

    try:
        df_processed = data_processor.process_sales_data(df_sales)
        st.session_state["df_processed_sales"] = df_processed
        set_success_message(config.MSG_PROCESSING_SUCCESS)
    except Exception as exc:
        set_error_message(f"{config.MSG_PROCESSING_ERROR} Detalle: {exc}")


def render_processed_data_summary() -> None:
    df_processed = st.session_state.get("df_processed_sales")

    if df_processed is None or df_processed.empty:
        st.info("Todavía no existe una base procesada.")
        return

    total_rows = len(df_processed)
    total_gsnr = (
        df_processed[config.COL_GSNR].sum()
        if config.COL_GSNR in df_processed.columns
        else 0
    )
    total_gm = (
        df_processed[config.COL_GROSS_MARGIN].sum()
        if config.COL_GROSS_MARGIN in df_processed.columns
        else 0
    )

    # Se usan columnas nativas para asegurar que las 3 tarjetas
    # permanezcan en la misma fila, igual que en Base MTD.
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            styles.build_base_mtd_kpi_card(
                title="REGISTROS PROCESADOS",
                value=f"{total_rows:,}",
                description="Total de filas en la base procesada.",
                icon="#",
                color="blue",
            ),
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            styles.build_base_mtd_kpi_card(
                title=f"GSNR TOTAL ({get_currency_kpi_suffix()})",
                value=format_monetary_value(total_gsnr),
                description="Suma del GSNR contenido en BASE SAP, expresada en miles.",
                icon="$",
                color="green",
            ),
            unsafe_allow_html=True,
        )

    with col3:
        st.markdown(
            styles.build_base_mtd_kpi_card(
                title=f"GROSS MARGIN TOTAL ({get_currency_kpi_suffix()})",
                value=format_monetary_value(total_gm),
                description="GSNR menos Costo Vtas Netas, expresado en miles.",
                icon="Σ",
                color="orange",
            ),
            unsafe_allow_html=True,
        )

# =========================================================
# 13. BASE MTD
# =========================================================
def run_mtd_build(
    selected_year: int | None = None,
    selected_month: int | None = None,
) -> None:
    df_processed_sales = st.session_state.get("df_processed_sales")
    df_plan_client = st.session_state.get("df_plan_client")
    df_plan_sku = st.session_state.get("df_plan_sku")

    if (
        df_processed_sales is None
        or df_plan_client is None
        or df_plan_sku is None
    ):
        set_error_message(config.MSG_MTD_BUILD_MISSING_FILES)
        return

    try:
        payload = data_processor.build_mtd_payload(
            df_processed_sales,
            df_plan_client,
            df_plan_sku,
            selected_year=selected_year,
            selected_month=selected_month,
        )
        st.session_state["mtd_payload"] = payload
        st.session_state["df_mtd_base"] = None
        set_success_message(config.MSG_MTD_BUILD_SUCCESS)
    except Exception as exc:
        set_error_message(f"{config.MSG_MTD_BUILD_ERROR} Detalle: {exc}")


def render_mtd_base_summary() -> None:
    payload = st.session_state.get("mtd_payload")

    if payload is None:
        st.info("Todavía no existe una Base MTD construida.")
        return

    latest_month = payload["latest_month"]
    latest_year = payload["latest_year"]
    summary = payload["summary"]
    plan_summary = payload["plan_summary"]
    bts_summary = payload["bts_summary"]

    period_label = f"{get_month_label(int(latest_month))} {int(latest_year)}"

    st.markdown(
        '<div class="base-mtd-section-heading">Resumen ejecutivo</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        <div class="base-mtd-compact-note">
            Periodo activo: <b>{escape(period_label)}</b> ·
            Moneda: <b>{escape(get_currency_status_label())}</b> ·
            TC: <b>{get_normalized_exchange_rate_4():,.4f} MXN/USD</b>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Se usan columnas nativas de Streamlit para garantizar 3 tarjetas arriba
    # y 3 tarjetas abajo. No se usa un contenedor grid HTML abierto, porque
    # Streamlit envuelve cada markdown y puede romper la cuadrícula visual.
    row1 = st.columns(3)
    row2 = st.columns(3)

    with row1[0]:
        st.markdown(
            styles.build_base_mtd_kpi_card(
                title=f"MTD ACT TOTAL ({get_currency_kpi_suffix()})",
                value=format_monetary_value(summary["mtd_act_total_k"] * 1000),
                description="Valor real del mes de corte seleccionado.",
                icon="$",
                color="blue",
            ),
            unsafe_allow_html=True,
        )

    with row1[1]:
        st.markdown(
            styles.build_base_mtd_kpi_card(
                title=f"YTD ACT TOTAL ({get_currency_kpi_suffix()})",
                value=format_monetary_value(summary["ytd_act_total_k"] * 1000),
                description="Acumulado real de enero al mes de corte.",
                icon="Σ",
                color="blue",
            ),
            unsafe_allow_html=True,
        )

    with row1[2]:
        st.markdown(
            styles.build_base_mtd_kpi_card(
                title=f"MTD PLAN TOTAL ({get_currency_kpi_suffix()})",
                value=format_monetary_value(summary["mtd_plan_total_k"] * 1000),
                description="Plan del mes de corte seleccionado.",
                icon="↗",
                color="orange",
            ),
            unsafe_allow_html=True,
        )

    with row2[0]:
        st.markdown(
            styles.build_base_mtd_kpi_card(
                title=f"YTD PLAN TOTAL ({get_currency_kpi_suffix()})",
                value=format_monetary_value(summary["ytd_plan_total_k"] * 1000),
                description="Plan acumulado de enero al mes de corte.",
                icon="Σ",
                color="orange",
            ),
            unsafe_allow_html=True,
        )

    with row2[1]:
        st.markdown(
            styles.build_base_mtd_kpi_card(
                title=f"BTS ACTUAL ({get_currency_kpi_suffix()})",
                value=format_monetary_value(bts_summary["bts_actual_k"] * 1000),
                description="BTS acumulado desde octubre al corte seleccionado.",
                icon="🎒",
                color="green",
            ),
            unsafe_allow_html=True,
        )

    with row2[2]:
        st.markdown(
            styles.build_base_mtd_kpi_card(
                title=f"BTS PY COMPLETO ({get_currency_kpi_suffix()})",
                value=format_monetary_value(bts_summary["bts_py_full_k"] * 1000),
                description="Ciclo BTS previo completo como referencia.",
                icon="↺",
                color="green",
            ),
            unsafe_allow_html=True,
        )

    # IMPORTANTE:
    # Estos avisos se conservan igual, porque son validaciones funcionales
    # que ya existían en la vista original.
    if plan_summary["mtd_plan_match"]:
        st.success("Validación MTD Plan: Plan Cliente y Plan SKU coinciden.")
    else:
        st.warning(
            "Validación MTD Plan: Plan Cliente y Plan SKU no coinciden. "
            f"Diferencia detectada: {round(convert_monetary_value(plan_summary['mtd_plan_diff']) / 1000):,}"
        )

    if plan_summary["ytd_plan_match"]:
        st.success("Validación YTD Plan: Plan Cliente y Plan SKU coinciden.")
    else:
        st.warning(
            "Validación YTD Plan: Plan Cliente y Plan SKU no coinciden. "
            f"Diferencia detectada: {round(convert_monetary_value(plan_summary['ytd_plan_diff']) / 1000):,}"
        )

def format_table_value(value: float, is_percent: bool = False) -> str:
    return format_monetary_value(value, is_percent=is_percent)


def build_mtd_legend_html() -> str:
    return (
        '<div class="metric-legend">'
        '<span class="metric-chip chip-real">REAL (BASE SAP)</span>'
        '<span class="metric-chip chip-client">Plan2026 by Client</span>'
        '<span class="metric-chip chip-sku">Plan2026 by SKU</span>'
        "</div>"
    )


def build_horizontal_plan_table_html(title: str, df_table, plan_variant: str) -> str:
    plan_header_class = "plan-header-client" if plan_variant == "client" else "plan-header-sku"

    header_html = (
        '<div class="h-table h-table-8 h-table-header">'
        '<div class="h-cell h-header h-header-neutral">Periodo</div>'
        '<div class="h-cell h-header h-header-real">Actual</div>'
        f'<div class="h-cell h-header {plan_header_class}">Plan</div>'
        '<div class="h-cell h-header h-header-real">PY</div>'
        '<div class="h-cell h-header h-header-neutral">Var VS Plan</div>'
        '<div class="h-cell h-header h-header-neutral">%Var VS Plan</div>'
        '<div class="h-cell h-header h-header-neutral">Var VS PY</div>'
        '<div class="h-cell h-header h-header-neutral">%Var VS PY</div>'
        "</div>"
    )

    rows_html_parts: list[str] = []

    for _, row in df_table.iterrows():
        actual_value = float(row["Actual"])
        plan_value = float(row["Plan"])
        py_value = float(row["PY"])
        var_plan_value = float(row["Var VS Plan"])
        pct_plan_value = float(row["%Var VS Plan"])
        var_py_value = float(row["Var VS PY"])
        pct_py_value = float(row["%Var VS PY"])

        row_html = (
            '<div class="h-table h-table-8 h-table-row">'
            f'<div class="h-cell h-row-label">{escape(str(row["Periodo"]))}</div>'
            f'<div class="h-cell h-value {"negative-value" if actual_value < 0 else "neutral-value"}">{format_table_value(actual_value)}</div>'
            f'<div class="h-cell h-value {"negative-value" if plan_value < 0 else "neutral-value"}">{format_table_value(plan_value)}</div>'
            f'<div class="h-cell h-value {"negative-value" if py_value < 0 else "neutral-value"}">{format_table_value(py_value)}</div>'
            f'<div class="h-cell h-value {"negative-value" if var_plan_value < 0 else "neutral-value"}">{format_table_value(var_plan_value)}</div>'
            f'<div class="h-cell h-value {"negative-value" if pct_plan_value < 0 else "neutral-value"}">{format_table_value(pct_plan_value, True)}</div>'
            f'<div class="h-cell h-value {"negative-value" if var_py_value < 0 else "neutral-value"}">{format_table_value(var_py_value)}</div>'
            f'<div class="h-cell h-value {"negative-value" if pct_py_value < 0 else "neutral-value"}">{format_table_value(pct_py_value, True)}</div>'
            "</div>"
        )
        rows_html_parts.append(row_html)

    rows_html = "".join(rows_html_parts)

    return (
        '<div class="horizontal-table-card base-mtd-number-table-card">'
        f'<div class="horizontal-table-title">{escape(title)}</div>'
        f"{header_html}"
        f"{rows_html}"
        "</div>"
    )


def build_bts_table_html(title: str, df_table) -> str:
    header_html = (
        '<div class="h-table h-table-5 h-table-header">'
        '<div class="h-cell h-header h-header-neutral">Periodo</div>'
        '<div class="h-cell h-header h-header-real">Actual</div>'
        '<div class="h-cell h-header h-header-real">PY</div>'
        '<div class="h-cell h-header h-header-neutral">Var VS PY</div>'
        '<div class="h-cell h-header h-header-neutral">%Var VS PY</div>'
        "</div>"
    )

    rows_html_parts: list[str] = []

    for _, row in df_table.iterrows():
        actual_value = float(row["Actual"])
        py_value = float(row["PY"])
        var_py_value = float(row["Var VS PY"])
        pct_py_value = float(row["%Var VS PY"])

        row_html = (
            '<div class="h-table h-table-5 h-table-row">'
            f'<div class="h-cell h-row-label">{escape(str(row["Periodo"]))}</div>'
            f'<div class="h-cell h-value {"negative-value" if actual_value < 0 else "neutral-value"}">{format_table_value(actual_value)}</div>'
            f'<div class="h-cell h-value {"negative-value" if py_value < 0 else "neutral-value"}">{format_table_value(py_value)}</div>'
            f'<div class="h-cell h-value {"negative-value" if var_py_value < 0 else "neutral-value"}">{format_table_value(var_py_value)}</div>'
            f'<div class="h-cell h-value {"negative-value" if pct_py_value < 0 else "neutral-value"}">{format_table_value(pct_py_value, True)}</div>'
            "</div>"
        )
        rows_html_parts.append(row_html)

    rows_html = "".join(rows_html_parts)

    return (
        '<div class="horizontal-table-card base-mtd-number-table-card">'
        f'<div class="horizontal-table-title">{escape(title)}</div>'
        f"{header_html}"
        f"{rows_html}"
        "</div>"
    )

# =========================================================
# 14. REPORTE 1
# =========================================================
def run_report_1_build(
    selected_year: int | None = None,
    selected_month: int | None = None,
) -> None:
    df_processed_sales = st.session_state.get("df_processed_sales")
    df_plan_client = st.session_state.get("df_plan_client")

    if df_processed_sales is None or df_plan_client is None:
        set_error_message(config.MSG_REPORT_1_BUILD_MISSING_FILES)
        return

    is_sales_ready, missing_sales = validators.validate_dataframe_for_processing(
        df_processed_sales,
        config.REQUIRED_COLUMNS_REPORT_1_SALES,
    )
    is_plan_ready, missing_plan = validators.validate_dataframe_for_processing(
        df_plan_client,
        config.REQUIRED_COLUMNS_REPORT_1_PLAN_CLIENT,
    )

    if not is_sales_ready:
        set_error_message(config.MSG_VALIDATION_FAIL)
        set_warning_message(
            f"Columnas faltantes para Reporte 1 en ventas: {', '.join(missing_sales)}"
        )
        return

    if not is_plan_ready:
        set_error_message(config.MSG_VALIDATION_FAIL)
        set_warning_message(
            f"Columnas faltantes para Reporte 1 en plan por cliente: {', '.join(missing_plan)}"
        )
        return

    try:
        payload = data_processor.build_report_1_payload(
            df_processed_sales,
            df_plan_client,
            selected_year=selected_year,
            selected_month=selected_month,
        )
        st.session_state["report1_payload"] = payload
        set_success_message(config.MSG_REPORT_1_BUILD_SUCCESS)
    except Exception as exc:
        set_error_message(f"{config.MSG_REPORT_1_BUILD_ERROR} Detalle: {exc}")


def format_report_1_value(value, is_percent: bool = False, allow_blank: bool = False) -> str:
    if not is_percent and not is_blank_number(value):
        try:
            if float(value) == 0:
                return "-"
        except (TypeError, ValueError):
            pass
    return format_monetary_value(value, is_percent=is_percent, allow_blank=allow_blank)


def build_report_1_title_box_html() -> str:
    return (
        '<div class="report-title-box">'
        f'<div class="report-title-main">{escape(config.REPORT_1_MAIN_HEADING)}</div>'
        f'<div class="report-title-sub">{escape(config.REPORT_1_SUBHEADING)}</div>'
        "</div>"
    )


def build_report_1_table_html(title: str, df_table) -> str:
    header_html = (
        '<div class="report-grid report-grid-8">'
        '<div class="report-cell report-header report-header-neutral report-header-sticky">OFICINA DE VENTAS</div>'
        '<div class="report-cell report-header report-header-actual">Actual</div>'
        '<div class="report-cell report-header report-header-plan">Plan</div>'
        '<div class="report-cell report-header report-header-py">PY</div>'
        '<div class="report-cell report-header report-header-neutral">Var VS Plan</div>'
        '<div class="report-cell report-header report-header-neutral">%Var VS Plan</div>'
        '<div class="report-cell report-header report-header-neutral">Var VS PY</div>'
        '<div class="report-cell report-header report-header-neutral">%Var VS PY</div>'
        "</div>"
    )

    rows_html_parts: list[str] = []

    for _, row in df_table.iterrows():
        is_total = bool(row.get("__is_total__", False))
        is_highlight = bool(row.get("__is_highlight__", False))

        row_class = "report-row"
        if is_total:
            row_class += " report-total"
        if is_highlight:
            row_class += " report-highlight"

        actual_value = row["Actual"]
        plan_value = row["Plan"]
        py_value = row["PY"]
        var_plan_value = row["Var VS Plan"]
        pct_plan_value = row["%Var VS Plan"]
        var_py_value = row["Var VS PY"]
        pct_py_value = row["%Var VS PY"]

        actual_negative = (not is_blank_number(actual_value)) and float(actual_value) < 0
        plan_negative = (not is_blank_number(plan_value)) and float(plan_value) < 0
        py_negative = (not is_blank_number(py_value)) and float(py_value) < 0
        var_plan_negative = (not is_blank_number(var_plan_value)) and float(var_plan_value) < 0
        pct_plan_negative = (not is_blank_number(pct_plan_value)) and float(pct_plan_value) < 0
        var_py_negative = (not is_blank_number(var_py_value)) and float(var_py_value) < 0
        pct_py_negative = (not is_blank_number(pct_py_value)) and float(pct_py_value) < 0

        row_html = (
            f'<div class="{row_class}">'
            f'<div class="report-cell report-label-cell">{escape(str(row["Oficina de Ventas"]))}</div>'
            f'<div class="report-cell report-value-cell {"report-negative" if actual_negative else ""}">{format_report_1_value(actual_value)}</div>'
            f'<div class="report-cell report-value-cell {"report-negative" if plan_negative else ""}">{format_report_1_value(plan_value, allow_blank=True)}</div>'
            f'<div class="report-cell report-value-cell {"report-negative" if py_negative else ""}">{format_report_1_value(py_value)}</div>'
            f'<div class="report-cell report-value-cell {"report-negative" if var_plan_negative else ""}">{format_report_1_value(var_plan_value, allow_blank=True)}</div>'
            f'<div class="report-cell report-value-cell {"report-negative" if pct_plan_negative else ""}">{format_report_1_value(pct_plan_value, is_percent=True, allow_blank=True)}</div>'
            f'<div class="report-cell report-value-cell {"report-negative" if var_py_negative else ""}">{format_report_1_value(var_py_value, allow_blank=True)}</div>'
            f'<div class="report-cell report-value-cell {"report-negative" if pct_py_negative else ""}">{format_report_1_value(pct_py_value, is_percent=True, allow_blank=True)}</div>'
            "</div>"
        )
        rows_html_parts.append(row_html)

    rows_html = "".join(rows_html_parts)

    return (
        '<div class="report-table-card">'
        f'<div class="report-table-title">{escape(title)}</div>'
        '<div class="report-table-scroll">'
        f"{header_html}"
        f'<div class="report-grid report-grid-8">{rows_html}</div>'
        "</div>"
        "</div>"
    )


def render_report_1_view() -> None:
    st.markdown(
        f'<div class="section-title">{config.REPORT_1_TITLE}</div>',
        unsafe_allow_html=True,
    )

    st.markdown(build_report_1_title_box_html(), unsafe_allow_html=True)

    report_box_html = styles.build_info_box(
        """
        <b>Objetivo de esta vista:</b><br>
        Mostrar el comparativo ejecutivo MTD / YTD de Oficina de ventas, con el bloque completo ACCO + BARR + KENS, usando BASE SAP y Plan2026 by Client.
        """
    )
    st.markdown(report_box_html, unsafe_allow_html=True)

    st.markdown("### Construir Reporte")
    st.markdown(
        '<div class="report-note">Primero construye el reporte para habilitar la vista. Después podrás cambiar el Año, el Mes y la primera columna del reporte.</div>',
        unsafe_allow_html=True,
    )

    st.button(
        "Construir Reporte 1",
        on_click=run_report_1_build,
        use_container_width=True,
    )

    payload = st.session_state.get("report1_payload")

    if payload is None:
        st.markdown("---")
        st.info("Aún no se ha construido el Reporte 1.")
        return

    st.markdown("---")
    st.markdown("### Resumen ejecutivo")

    latest_month = payload["summary"]["latest_month"]
    latest_year = payload["summary"]["latest_year"]

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(
            styles.build_info_card(
                "Periodo actual",
                f"{latest_month:02d}/{latest_year}",
                "Periodo de corte seleccionado desde BASE SAP",
            ),
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            styles.build_info_card(
                "Bloque completo",
                "ACCO + BARR + KENS",
                "Comparativo completo",
            ),
            unsafe_allow_html=True,
        )

    st.markdown("---")
    st.markdown("### Oficina de ventas MTD / YTD")

    selected_year_without_kens, selected_month_without_kens = render_period_filter_block(
        "Filtro del bloque: Oficina de ventas",
        "report1_without_kens_year",
        "report1_without_kens_month",
    )

    payload = st.session_state.get("report1_payload")

    without_kens_options = get_filter_options_from_multiple_tables(
        [
            payload["mtd_without_kens_table"],
            payload["ytd_without_kens_table"],
        ],
        lambda row: str(row.get("Oficina de Ventas", "")).strip(),
    )

    render_dimension_filter_block(
        "OFICINA DE VENTAS",
        "report1_without_kens_dimension_widget",
        "report1_without_kens_dimension_applied",
        without_kens_options,
    )

    if selected_year_without_kens is not None and selected_month_without_kens is not None:
        if st.button(
            "Aplicar filtro",
            key="btn_report1_without_kens",
            use_container_width=False,
        ):
            old_without_kens_options = without_kens_options.copy()
            selected_without_kens_before = st.session_state.get(
                "report1_without_kens_dimension_widget",
                old_without_kens_options.copy(),
            )
            run_report_1_build(
                selected_year=selected_year_without_kens,
                selected_month=selected_month_without_kens,
            )
            payload_after = st.session_state.get("report1_payload")
            new_without_kens_options = get_filter_options_from_multiple_tables(
                [
                    payload_after["mtd_without_kens_table"],
                    payload_after["ytd_without_kens_table"],
                ],
                lambda row: str(row.get("Oficina de Ventas", "")).strip(),
            )
            apply_dimension_filter_after_rebuild(
                "report1_without_kens_dimension_widget",
                "report1_without_kens_dimension_applied",
                old_without_kens_options,
                new_without_kens_options,
                selected_without_kens_before,
            )
            st.rerun()

    payload = st.session_state.get("report1_payload")

    active_year_report1 = payload["summary"]["latest_year"]
    active_month_report1 = payload["summary"]["latest_month"]

    applied_without_kens_labels = get_valid_applied_filter_values(
        "report1_without_kens_dimension_applied",
        without_kens_options,
    )

    filtered_mtd_without_kens = filter_report_1_without_kens_table(
        payload["mtd_without_kens_table"],
        applied_without_kens_labels,
    )
    filtered_ytd_without_kens = filter_report_1_without_kens_table(
        payload["ytd_without_kens_table"],
        applied_without_kens_labels,
    )

    export_col_left, export_col_right = st.columns([12, 1])
    with export_col_right:
        report_1_bytes = exports.build_report_1_excel_bytes(
            mtd_without_kens_df=convert_report_table_for_export(payload["mtd_without_kens_table"]),
            ytd_without_kens_df=convert_report_table_for_export(payload["ytd_without_kens_table"]),
            report_title=build_report_context_title(
                "Reporte 1 - Oficina de ventas",
                active_year_report1,
                active_month_report1,
            ),
        )
        render_icon_download_button(
            data=report_1_bytes,
            file_name=build_excel_filename(
                "reporte_1",
                active_year_report1,
                active_month_report1,
            ),
            key="download_report_1_icon_top",
            help_text="Descargar Reporte 1",
        )

    st.markdown(
        '<div class="report-note">Las tablas MTD y YTD se muestran lado a lado para facilitar la lectura ejecutiva.</div>',
        unsafe_allow_html=True,
    )

    top_left, top_right = st.columns(2)

    with top_left:
        st.markdown(
            build_report_1_table_html(
                build_report_context_title(
                    "MTD Oficina de ventas",
                    active_year_report1,
                    active_month_report1,
                ),
                filtered_mtd_without_kens,
            ),
            unsafe_allow_html=True,
        )

    with top_right:
        st.markdown(
            build_report_1_table_html(
                build_report_context_title(
                    "YTD Oficina de ventas",
                    active_year_report1,
                    active_month_report1,
                ),
                filtered_ytd_without_kens,
            ),
            unsafe_allow_html=True,
        )


# =========================================================
# 15. REPORTE 2
# =========================================================
def run_report_2_build(
    selected_year: int | None = None,
    selected_month: int | None = None,
) -> None:
    df_processed_sales = st.session_state.get("df_processed_sales")
    df_plan_sku = st.session_state.get("df_plan_sku")

    if df_processed_sales is None or df_plan_sku is None:
        set_error_message(config.MSG_REPORT_2_BUILD_MISSING_FILES)
        return

    is_sales_ready, missing_sales = validators.validate_dataframe_for_processing(
        df_processed_sales,
        config.REQUIRED_COLUMNS_REPORT_2_SALES,
    )
    is_plan_ready, missing_plan = validators.validate_dataframe_for_processing(
        df_plan_sku,
        config.REQUIRED_COLUMNS_REPORT_2_PLAN_SKU,
    )

    if not is_sales_ready:
        set_error_message(config.MSG_VALIDATION_FAIL)
        set_warning_message(
            f"Columnas faltantes para Reporte 2 en ventas: {', '.join(missing_sales)}"
        )
        return

    if not is_plan_ready:
        set_error_message(config.MSG_VALIDATION_FAIL)
        set_warning_message(
            f"Columnas faltantes para Reporte 2 en plan por SKU: {', '.join(missing_plan)}"
        )
        return

    try:
        payload = data_processor.build_report_2_segment_region_payload(
            df_processed_sales,
            df_plan_sku,
            selected_year=selected_year,
            selected_month=selected_month,
        )
        st.session_state["report2_payload"] = payload
        set_success_message(config.MSG_REPORT_2_BUILD_SUCCESS)
    except Exception as exc:
        set_error_message(f"{config.MSG_REPORT_2_BUILD_ERROR} Detalle: {exc}")


def run_report_2_category_build(
    selected_year: int | None = None,
    selected_month: int | None = None,
) -> None:
    df_processed_sales = st.session_state.get("df_processed_sales")
    df_plan_sku = st.session_state.get("df_plan_sku")

    if df_processed_sales is None or df_plan_sku is None:
        set_error_message(config.MSG_REPORT_2_CATEGORY_BUILD_MISSING_FILES)
        return

    is_sales_ready, missing_sales = validators.validate_dataframe_for_processing(
        df_processed_sales,
        config.REQUIRED_COLUMNS_REPORT_2_CATEGORY_SALES,
    )
    is_plan_ready, missing_plan = validators.validate_dataframe_for_processing(
        df_plan_sku,
        config.REQUIRED_COLUMNS_REPORT_2_CATEGORY_PLAN_SKU,
    )

    if not is_sales_ready:
        set_error_message(config.MSG_VALIDATION_FAIL)
        set_warning_message(
            f"Columnas faltantes para Reporte Category en ventas: {', '.join(missing_sales)}"
        )
        return

    if not is_plan_ready:
        set_error_message(config.MSG_VALIDATION_FAIL)
        set_warning_message(
            f"Columnas faltantes para Reporte Category en plan por SKU: {', '.join(missing_plan)}"
        )
        return

    try:
        payload = data_processor.build_report_2_category_payload(
            df_processed_sales,
            df_plan_sku,
            selected_year=selected_year,
            selected_month=selected_month,
        )
        st.session_state["report2_category_payload"] = payload
        set_success_message(config.MSG_REPORT_2_CATEGORY_BUILD_SUCCESS)
    except Exception as exc:
        set_error_message(f"{config.MSG_REPORT_2_CATEGORY_BUILD_ERROR} Detalle: {exc}")


def format_report_2_value(value, is_percent: bool = False) -> str:
    if not is_percent and not is_blank_number(value):
        try:
            if float(value) == 0:
                return "-"
        except (TypeError, ValueError):
            pass
    return format_monetary_value(value, is_percent=is_percent)


def build_report_2_title_box_html() -> str:
    return (
        '<div class="report-title-box">'
        f'<div class="report-title-main">{escape(config.REPORT_2_MAIN_HEADING)}</div>'
        f'<div class="report-title-sub">{escape(config.REPORT_2_SUBHEADING)}</div>'
        "</div>"
    )


def build_report_2_table_html(title: str, df_table, first_header: str, view_type: str) -> str:
    is_category_view = view_type == "category"

    if is_category_view:
        grid_class = "report-grid report-grid-11 report-category-grid"
        header_html = (
            '<div class="report-cell report-header report-header-neutral report-category-header-sticky">CATEGORY</div>'
            '<div class="report-cell report-header report-header-neutral">MATERIAL</div>'
            '<div class="report-cell report-header report-header-neutral">CATEGORÍA DEL MATERIAL</div>'
            '<div class="report-cell report-header report-header-neutral">DESCRIPCIÓN DEL MATERIAL</div>'
            '<div class="report-cell report-header report-header-actual">Actual</div>'
            '<div class="report-cell report-header report-header-plan">Plan</div>'
            '<div class="report-cell report-header report-header-py">PY</div>'
            '<div class="report-cell report-header report-header-neutral">Var VS Plan</div>'
            '<div class="report-cell report-header report-header-neutral">%Var VS Plan</div>'
            '<div class="report-cell report-header report-header-neutral">Var VS PY</div>'
            '<div class="report-cell report-header report-header-neutral">%Var VS PY</div>'
        )
    else:
        grid_class = "report-grid report-grid-8"
        header_html = (
            f'<div class="{grid_class}">'
            f'<div class="report-cell report-header report-header-neutral report-header-sticky">{escape(first_header)}</div>'
            '<div class="report-cell report-header report-header-actual">Actual</div>'
            '<div class="report-cell report-header report-header-plan">Plan</div>'
            '<div class="report-cell report-header report-header-py">PY</div>'
            '<div class="report-cell report-header report-header-neutral">Var VS Plan</div>'
            '<div class="report-cell report-header report-header-neutral">%Var VS Plan</div>'
            '<div class="report-cell report-header report-header-neutral">Var VS PY</div>'
            '<div class="report-cell report-header report-header-neutral">%Var VS PY</div>'
            "</div>"
        )

    rows_html_parts: list[str] = []

    for _, row in df_table.iterrows():
        is_total = bool(row.get("__is_total__", False))
        is_grand_total = bool(row.get("__is_grand_total__", False))

        row_class = "report-row"
        if is_total:
            row_class += " report-total"
        if is_grand_total:
            row_class += " report-highlight"

        if view_type == "segment_region":
            label_value = build_report_2_segment_region_display_label(row)
            material_value = ""
            product_value = ""
            description_value = ""
        elif is_category_view:
            label_value = str(row.get("Category", "")).strip()
            material_value = str(row.get("Material", "")).strip()
            product_value = str(row.get("Categoría del Material", "")).strip()
            description_value = str(row.get("Descripción del Material", "")).strip()
        else:
            label_value = str(row.get("Category", "")).strip()
            material_value = ""
            product_value = ""
            description_value = ""

        actual_value = row["Actual"]
        plan_value = row["Plan"]
        py_value = row["PY"]
        var_plan_value = row["Var VS Plan"]
        pct_plan_value = row["%Var VS Plan"]
        var_py_value = row["Var VS PY"]
        pct_py_value = row["%Var VS PY"]

        actual_negative = (not is_blank_number(actual_value)) and float(actual_value) < 0
        plan_negative = (not is_blank_number(plan_value)) and float(plan_value) < 0
        py_negative = (not is_blank_number(py_value)) and float(py_value) < 0
        var_plan_negative = (not is_blank_number(var_plan_value)) and float(var_plan_value) < 0
        pct_plan_negative = (not is_blank_number(pct_plan_value)) and float(pct_plan_value) < 0
        var_py_negative = (not is_blank_number(var_py_value)) and float(var_py_value) < 0
        pct_py_negative = (not is_blank_number(pct_py_value)) and float(pct_py_value) < 0

        if is_category_view:
            row_html = (
                f'<div class="{row_class}">'
                f'<div class="report-cell report-label-cell report-sticky-cell">{escape(label_value)}</div>'
                f'<div class="report-cell report-category-product-cell">{escape(material_value)}</div>'
                f'<div class="report-cell report-category-product-cell">{escape(product_value)}</div>'
                f'<div class="report-cell report-category-product-cell">{escape(description_value)}</div>'
                f'<div class="report-cell report-value-cell {"report-negative" if actual_negative else ""}">{format_report_2_value(actual_value)}</div>'
                f'<div class="report-cell report-value-cell {"report-negative" if plan_negative else ""}">{format_report_2_value(plan_value)}</div>'
                f'<div class="report-cell report-value-cell {"report-negative" if py_negative else ""}">{format_report_2_value(py_value)}</div>'
                f'<div class="report-cell report-value-cell {"report-negative" if var_plan_negative else ""}">{format_report_2_value(var_plan_value)}</div>'
                f'<div class="report-cell report-value-cell {"report-negative" if pct_plan_negative else ""}">{format_report_2_value(pct_plan_value, is_percent=True)}</div>'
                f'<div class="report-cell report-value-cell {"report-negative" if var_py_negative else ""}">{format_report_2_value(var_py_value)}</div>'
                f'<div class="report-cell report-value-cell {"report-negative" if pct_py_negative else ""}">{format_report_2_value(pct_py_value, is_percent=True)}</div>'
                "</div>"
            )
        else:
            row_html = (
                f'<div class="{row_class}">'
                f'<div class="report-cell report-label-cell">{escape(label_value)}</div>'
                f'<div class="report-cell report-value-cell {"report-negative" if actual_negative else ""}">{format_report_2_value(actual_value)}</div>'
                f'<div class="report-cell report-value-cell {"report-negative" if plan_negative else ""}">{format_report_2_value(plan_value)}</div>'
                f'<div class="report-cell report-value-cell {"report-negative" if py_negative else ""}">{format_report_2_value(py_value)}</div>'
                f'<div class="report-cell report-value-cell {"report-negative" if var_plan_negative else ""}">{format_report_2_value(var_plan_value)}</div>'
                f'<div class="report-cell report-value-cell {"report-negative" if pct_plan_negative else ""}">{format_report_2_value(pct_plan_value, is_percent=True)}</div>'
                f'<div class="report-cell report-value-cell {"report-negative" if var_py_negative else ""}">{format_report_2_value(var_py_value)}</div>'
                f'<div class="report-cell report-value-cell {"report-negative" if pct_py_negative else ""}">{format_report_2_value(pct_py_value, is_percent=True)}</div>'
                "</div>"
            )

        rows_html_parts.append(row_html)

    rows_html = "".join(rows_html_parts)

    if is_category_view:
        return (
            '<div class="report-table-card report-category-card">'
            f'<div class="report-table-title">{escape(title)}</div>'
            '<div class="report-table-scroll report-category-scroll">'
            f'<div class="{grid_class}">{header_html}{rows_html}</div>'
            "</div>"
            "</div>"
        )

    return (
        '<div class="report-table-card">'
        f'<div class="report-table-title">{escape(title)}</div>'
        '<div class="report-table-scroll">'
        f"{header_html}"
        f'<div class="{grid_class}">{rows_html}</div>'
        "</div>"
        "</div>"
    )


def render_report_2_view() -> None:
    st.markdown(
        f'<div class="section-title">{config.REPORT_2_TITLE}</div>',
        unsafe_allow_html=True,
    )

    st.markdown(build_report_2_title_box_html(), unsafe_allow_html=True)

    report_box_html = styles.build_info_box(
        """
        <b>Objetivo de esta vista:</b><br>
        Mostrar el comparativo ejecutivo MTD / YTD por Segmento y Región,
        usando BASE SAP y Plan2026 by SKU, excluyendo AFI: Afiliadas.
        """
    )
    st.markdown(report_box_html, unsafe_allow_html=True)

    st.markdown("### Construir Segment x Region")
    st.button(
        "Construir Reporte Segment x Region",
        on_click=run_report_2_build,
        use_container_width=True,
    )

    payload = st.session_state.get("report2_payload")

    st.markdown("---")
    st.markdown("### Resumen ejecutivo")

    if payload is None:
        st.info("Aún no se ha construido el Reporte Segment x Region.")
    else:
        latest_month = payload["summary"]["latest_month"]
        latest_year = payload["summary"]["latest_year"]

        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown(
                styles.build_info_card(
                    "Periodo actual",
                    f"{latest_month:02d}/{latest_year}",
                    "Periodo de corte seleccionado desde BASE SAP",
                ),
                unsafe_allow_html=True,
            )

        with col2:
            st.markdown(
                styles.build_info_card(
                    "Segmentos visibles",
                    "Dinámicos",
                    "Se muestran los segmentos con Actual, Plan o PY",
                ),
                unsafe_allow_html=True,
            )

        with col3:
            st.markdown(
                styles.build_info_card(
                    "Regla aplicada",
                    "AFI excluido",
                    "Se excluye AFI: Afiliadas en la construcción del reporte",
                ),
                unsafe_allow_html=True,
            )

    st.markdown("---")
    st.markdown("### Segment x Region MTD / YTD")

    payload = st.session_state.get("report2_payload")

    if payload is None:
        st.info("Aún no se ha construido el bloque Segment x Region.")
    else:
        selected_year_segment, selected_month_segment = render_period_filter_block(
            "Filtro del bloque: Segment x Region",
            "report2_segment_year",
            "report2_segment_month",
        )

        segment_region_options = get_filter_options_from_multiple_tables(
            [
                payload["mtd_segment_region_table"],
                payload["ytd_segment_region_table"],
            ],
            build_report_2_segment_region_display_label,
        )

        render_dimension_filter_block(
            "SEGMENTO / REGIÓN",
            "report2_segment_dimension_widget",
            "report2_segment_dimension_applied",
            segment_region_options,
        )

        segment_apply_clicked = False

        if selected_year_segment is not None and selected_month_segment is not None:
            if st.button(
                "Aplicar filtro",
                key="btn_report2_segment",
                use_container_width=False,
            ):
                old_segment_region_options = segment_region_options.copy()
                selected_segment_before = st.session_state.get(
                    "report2_segment_dimension_widget",
                    old_segment_region_options.copy(),
                )
                run_report_2_build(
                    selected_year=selected_year_segment,
                    selected_month=selected_month_segment,
                )
                payload_after = st.session_state.get("report2_payload")
                new_segment_region_options = get_filter_options_from_multiple_tables(
                    [
                        payload_after["mtd_segment_region_table"],
                        payload_after["ytd_segment_region_table"],
                    ],
                    build_report_2_segment_region_display_label,
                )
                apply_dimension_filter_after_rebuild(
                    "report2_segment_dimension_widget",
                    "report2_segment_dimension_applied",
                    old_segment_region_options,
                    new_segment_region_options,
                    selected_segment_before,
                )
                st.rerun()

        payload = st.session_state.get("report2_payload")

        # Después de reconstruir el reporte, se recalculan las opciones con el payload nuevo.
        # Esto evita tener que dar dos o tres clics para que aparezcan categorías nuevas como #N/A o VARIOS.
        segment_region_options = get_filter_options_from_multiple_tables(
            [
                payload["mtd_segment_region_table"],
                payload["ytd_segment_region_table"],
            ],
            build_report_2_segment_region_display_label,
        )

        # No se reinicia la selección aplicada después de reconstruir.
        # El filtro seleccionado por el usuario ya se guardó antes de correr el reporte.

        active_year_segment = payload["summary"]["latest_year"]
        active_month_segment = payload["summary"]["latest_month"]

        applied_segment_region_labels = get_valid_applied_filter_values(
            "report2_segment_dimension_applied",
            segment_region_options,
        )

        filtered_mtd_segment = filter_report_2_segment_region_table(
            payload["mtd_segment_region_table"],
            applied_segment_region_labels,
        )
        filtered_ytd_segment = filter_report_2_segment_region_table(
            payload["ytd_segment_region_table"],
            applied_segment_region_labels,
        )

        export_col_left, export_col_right = st.columns([12, 1])
        with export_col_right:
            segment_bytes = exports.build_report_2_segment_excel_bytes(
                mtd_segment_df=convert_report_table_for_export(payload["mtd_segment_region_table"]),
                ytd_segment_df=convert_report_table_for_export(payload["ytd_segment_region_table"]),
                report_title=build_report_context_title(
                    "Reporte 2 - Segment x Region",
                    active_year_segment,
                    active_month_segment,
                ),
            )
            render_icon_download_button(
                data=segment_bytes,
                file_name=build_excel_filename(
                    "reporte_2_segment_region",
                    active_year_segment,
                    active_month_segment,
                ),
                key="download_report_2_segment_icon",
                help_text="Descargar Segment x Region",
            )

        st.markdown(
            '<div class="report-note">Las tablas MTD y YTD se muestran lado a lado para facilitar la lectura ejecutiva.</div>',
            unsafe_allow_html=True,
        )

        left_col, right_col = st.columns(2)

        with left_col:
            st.markdown(
                build_report_2_table_html(
                    build_report_context_title(
                        "MTD Segment x Region",
                        active_year_segment,
                        active_month_segment,
                    ),
                    filtered_mtd_segment,
                    "SEGMENTO / REGIÓN",
                    "segment_region",
                ),
                unsafe_allow_html=True,
            )

        with right_col:
            st.markdown(
                build_report_2_table_html(
                    build_report_context_title(
                        "YTD Segment x Region",
                        active_year_segment,
                        active_month_segment,
                    ),
                    filtered_ytd_segment,
                    "SEGMENTO / REGIÓN",
                    "segment_region",
                ),
                unsafe_allow_html=True,
            )

        # Los heatmaps de Segment x Region se retiraron de la vista ejecutiva
        # para mantener el reporte más limpio y concentrado en las tablas MTD/YTD.

    st.markdown("---")
    st.markdown("### Construir Category")
    st.button(
        "Construir Reporte Category",
        on_click=run_report_2_category_build,
        use_container_width=True,
    )

    payload_category = st.session_state.get("report2_category_payload")

    st.markdown("---")
    st.markdown("### Category MTD / YTD")

    if payload_category is None:
        st.info("Aún no se ha construido el Reporte Category.")
    else:
        selected_year_category, selected_month_category = render_period_filter_block(
            "Filtro del bloque: Category",
            "report2_category_year",
            "report2_category_month",
        )

        category_options = get_filter_options_from_multiple_tables(
            [
                payload_category["mtd_category_table"],
                payload_category["ytd_category_table"],
            ],
            lambda row: str(row.get("Category", "")).strip(),
        )

        render_dimension_filter_block(
            "CATEGORY",
            "report2_category_dimension_widget",
            "report2_category_dimension_applied",
            category_options,
        )

        category_apply_clicked = False

        if selected_year_category is not None and selected_month_category is not None:
            if st.button(
                "Aplicar filtro",
                key="btn_report2_category",
                use_container_width=False,
            ):
                old_category_options = category_options.copy()
                selected_category_before = st.session_state.get(
                    "report2_category_dimension_widget",
                    old_category_options.copy(),
                )
                run_report_2_category_build(
                    selected_year=selected_year_category,
                    selected_month=selected_month_category,
                )
                payload_category_after = st.session_state.get("report2_category_payload")
                new_category_options = get_filter_options_from_multiple_tables(
                    [
                        payload_category_after["mtd_category_table"],
                        payload_category_after["ytd_category_table"],
                    ],
                    lambda row: str(row.get("Category", "")).strip(),
                )
                apply_dimension_filter_after_rebuild(
                    "report2_category_dimension_widget",
                    "report2_category_dimension_applied",
                    old_category_options,
                    new_category_options,
                    selected_category_before,
                )
                st.rerun()

        payload_category = st.session_state.get("report2_category_payload")

        category_options = get_filter_options_from_multiple_tables(
            [
                payload_category["mtd_category_table"],
                payload_category["ytd_category_table"],
            ],
            lambda row: str(row.get("Category", "")).strip(),
        )

        # No se reinicia la selección aplicada después de reconstruir.
        # El filtro seleccionado por el usuario ya se guardó antes de correr el reporte.

        active_year_category = payload_category["summary"]["latest_year"]
        active_month_category = payload_category["summary"]["latest_month"]

        st.markdown(
            '<div class="report-note">Este bloque es independiente del anterior. Las tablas MTD y YTD se muestran lado a lado para facilitar la lectura ejecutiva.</div>',
            unsafe_allow_html=True,
        )

        applied_category_labels = get_valid_applied_filter_values(
            "report2_category_dimension_applied",
            category_options,
        )

        filtered_mtd_category = filter_report_2_category_table(
            payload_category["mtd_category_table"],
            applied_category_labels,
        )
        filtered_ytd_category = filter_report_2_category_table(
            payload_category["ytd_category_table"],
            applied_category_labels,
        )

        export_col_left, export_col_right = st.columns([12, 1])
        with export_col_right:
            category_bytes = exports.build_report_2_category_excel_bytes(
                mtd_category_df=convert_report_table_for_export(payload_category["mtd_category_table"]),
                ytd_category_df=convert_report_table_for_export(payload_category["ytd_category_table"]),
                report_title=build_report_context_title(
                    "Reporte 2 - Category",
                    active_year_category,
                    active_month_category,
                ),
            )
            render_icon_download_button(
                data=category_bytes,
                file_name=build_excel_filename(
                    "reporte_2_category",
                    active_year_category,
                    active_month_category,
                ),
                key="download_report_2_category_icon",
                help_text="Descargar Category",
            )

        left_col, right_col = st.columns(2)

        with left_col:
            st.markdown(
                build_report_2_table_html(
                    build_report_context_title(
                        "MTD Category",
                        active_year_category,
                        active_month_category,
                    ),
                    filtered_mtd_category,
                    "CATEGORY",
                    "category",
                ),
                unsafe_allow_html=True,
            )

        with right_col:
            st.markdown(
                build_report_2_table_html(
                    build_report_context_title(
                        "YTD Category",
                        active_year_category,
                        active_month_category,
                    ),
                    filtered_ytd_category,
                    "CATEGORY",
                    "category",
                ),
                unsafe_allow_html=True,
            )

# =========================================================
# 16. REPORTE 3
# =========================================================
def run_report_3_build(
    selected_year: int | None = None,
    selected_month: int | None = None,
) -> None:
    df_processed_sales = st.session_state.get("df_processed_sales")
    df_plan_sku = st.session_state.get("df_plan_sku")

    if df_processed_sales is None or df_plan_sku is None:
        set_error_message(config.MSG_REPORT_3_BUILD_MISSING_FILES)
        return

    is_sales_ready, missing_sales = validators.validate_dataframe_for_processing(
        df_processed_sales,
        config.REQUIRED_COLUMNS_REPORT_3_SALES,
    )
    is_plan_ready, missing_plan = validators.validate_dataframe_for_processing(
        df_plan_sku,
        config.REQUIRED_COLUMNS_REPORT_3_PLAN_SKU,
    )

    if not is_sales_ready:
        set_error_message(config.MSG_VALIDATION_FAIL)
        set_warning_message(
            f"Columnas faltantes para Reporte 3 en ventas: {', '.join(missing_sales)}"
        )
        return

    if not is_plan_ready:
        set_error_message(config.MSG_VALIDATION_FAIL)
        set_warning_message(
            f"Columnas faltantes para Reporte 3 en plan por SKU: {', '.join(missing_plan)}"
        )
        return

    try:
        payload = data_processor.build_report_3_channel_payload(
            df_processed_sales,
            df_plan_sku,
            selected_year=selected_year,
            selected_month=selected_month,
        )
        st.session_state["report3_payload"] = payload
        set_success_message(config.MSG_REPORT_3_BUILD_SUCCESS)
    except Exception as exc:
        set_error_message(f"{config.MSG_REPORT_3_BUILD_ERROR} Detalle: {exc}")


def format_report_3_value(value, is_percent: bool = False) -> str:
    if not is_percent and not is_blank_number(value):
        try:
            if float(value) == 0:
                return "-"
        except (TypeError, ValueError):
            pass
    return format_monetary_value(value, is_percent=is_percent)


def build_report_3_title_box_html() -> str:
    return (
        '<div class="report-title-box">'
        f'<div class="report-title-main">{escape(config.REPORT_3_MAIN_HEADING)}</div>'
        f'<div class="report-title-sub">{escape(config.REPORT_3_SUBHEADING)}</div>'
        "</div>"
    )


def build_report_3_table_html(title: str, df_table) -> str:
    header_html = (
        '<div class="report-grid report-grid-8">'
        '<div class="report-cell report-header report-header-neutral report-header-sticky">CHANNEL</div>'
        '<div class="report-cell report-header report-header-actual">Actual</div>'
        '<div class="report-cell report-header report-header-plan">Plan</div>'
        '<div class="report-cell report-header report-header-py">PY</div>'
        '<div class="report-cell report-header report-header-neutral">Var VS Plan</div>'
        '<div class="report-cell report-header report-header-neutral">%Var VS Plan</div>'
        '<div class="report-cell report-header report-header-neutral">Var VS PY</div>'
        '<div class="report-cell report-header report-header-neutral">%Var VS PY</div>'
        "</div>"
    )

    rows_html_parts: list[str] = []

    for _, row in df_table.iterrows():
        is_total = bool(row.get("__is_total__", False))
        is_grand_total = bool(row.get("__is_grand_total__", False))

        row_class = "report-row"
        if is_total:
            row_class += " report-total"
        if is_grand_total:
            row_class += " report-highlight"

        channel_value = build_report_3_display_label(row)

        actual_value = row["Actual"]
        plan_value = row["Plan"]
        py_value = row["PY"]
        var_plan_value = row["Var VS Plan"]
        pct_plan_value = row["%Var VS Plan"]
        var_py_value = row["Var VS PY"]
        pct_py_value = row["%Var VS PY"]

        actual_negative = (not is_blank_number(actual_value)) and float(actual_value) < 0
        plan_negative = (not is_blank_number(plan_value)) and float(plan_value) < 0
        py_negative = (not is_blank_number(py_value)) and float(py_value) < 0
        var_plan_negative = (not is_blank_number(var_plan_value)) and float(var_plan_value) < 0
        pct_plan_negative = (not is_blank_number(pct_plan_value)) and float(pct_plan_value) < 0
        var_py_negative = (not is_blank_number(var_py_value)) and float(var_py_value) < 0
        pct_py_negative = (not is_blank_number(pct_py_value)) and float(pct_py_value) < 0

        row_html = (
            f'<div class="{row_class}">'
            f'<div class="report-cell report-label-cell">{escape(channel_value)}</div>'
            f'<div class="report-cell report-value-cell {"report-negative" if actual_negative else ""}">{format_report_3_value(actual_value)}</div>'
            f'<div class="report-cell report-value-cell {"report-negative" if plan_negative else ""}">{format_report_3_value(plan_value)}</div>'
            f'<div class="report-cell report-value-cell {"report-negative" if py_negative else ""}">{format_report_3_value(py_value)}</div>'
            f'<div class="report-cell report-value-cell {"report-negative" if var_plan_negative else ""}">{format_report_3_value(var_plan_value)}</div>'
            f'<div class="report-cell report-value-cell {"report-negative" if pct_plan_negative else ""}">{format_report_3_value(pct_plan_value, is_percent=True)}</div>'
            f'<div class="report-cell report-value-cell {"report-negative" if var_py_negative else ""}">{format_report_3_value(var_py_value)}</div>'
            f'<div class="report-cell report-value-cell {"report-negative" if pct_py_negative else ""}">{format_report_3_value(pct_py_value, is_percent=True)}</div>'
            "</div>"
        )
        rows_html_parts.append(row_html)

    rows_html = "".join(rows_html_parts)

    return (
        '<div class="report-table-card">'
        f'<div class="report-table-title">{escape(title)}</div>'
        '<div class="report-table-scroll">'
        f"{header_html}"
        f'<div class="report-grid report-grid-8">{rows_html}</div>'
        "</div>"
        "</div>"
    )


def render_report_3_view() -> None:
    st.markdown(
        f'<div class="section-title">{config.REPORT_3_TITLE}</div>',
        unsafe_allow_html=True,
    )

    st.markdown(build_report_3_title_box_html(), unsafe_allow_html=True)

    report_box_html = styles.build_info_box(
        """
        <b>Objetivo de esta vista:</b><br>
        Mostrar el comparativo ejecutivo MTD / YTD por Channel,
        usando BASE SAP y Plan2026 by SKU.
        """
    )
    st.markdown(report_box_html, unsafe_allow_html=True)

    st.markdown("### Construir Reporte")
    st.button(
        "Construir Reporte 3",
        on_click=run_report_3_build,
        use_container_width=True,
    )

    payload = st.session_state.get("report3_payload")

    if payload is None:
        st.markdown("---")
        st.info("Aún no se ha construido el Reporte 3.")
        return

    st.markdown("---")
    st.markdown("### Resumen ejecutivo")

    latest_month = payload["summary"]["latest_month"]
    latest_year = payload["summary"]["latest_year"]

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            styles.build_info_card(
                "Periodo actual",
                f"{latest_month:02d}/{latest_year}",
                "Periodo de corte seleccionado desde BASE SAP",
            ),
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            styles.build_info_card(
                "Canales visibles",
                "Dinámicos",
                "Se muestran todos los canales con Actual, Plan o PY",
            ),
            unsafe_allow_html=True,
        )

    with col3:
        st.markdown(
            styles.build_info_card(
                "Fuente de plan",
                "Plan SKU",
                "Comparativo contra Plan2026 by SKU",
            ),
            unsafe_allow_html=True,
        )

    st.markdown("---")
    st.markdown("### Channel MTD / YTD")

    selected_year_channel, selected_month_channel = render_period_filter_block(
        "Filtro del bloque: Channel",
        "report3_channel_year",
        "report3_channel_month",
    )

    payload = st.session_state.get("report3_payload")

    channel_options = get_filter_options_from_multiple_tables(
        [
            payload["mtd_channel_table"],
            payload["ytd_channel_table"],
        ],
        build_report_3_display_label,
    )

    render_dimension_filter_block(
        "CHANNEL",
        "report3_channel_dimension_widget",
        "report3_channel_dimension_applied",
        channel_options,
    )

    channel_apply_clicked = False

    if selected_year_channel is not None and selected_month_channel is not None:
        if st.button(
            "Aplicar filtro",
            key="btn_report3_channel",
            use_container_width=False,
        ):
            old_channel_options = channel_options.copy()
            selected_channel_before = st.session_state.get(
                "report3_channel_dimension_widget",
                old_channel_options.copy(),
            )
            run_report_3_build(
                selected_year=selected_year_channel,
                selected_month=selected_month_channel,
            )
            payload_after = st.session_state.get("report3_payload")
            new_channel_options = get_filter_options_from_multiple_tables(
                [
                    payload_after["mtd_channel_table"],
                    payload_after["ytd_channel_table"],
                ],
                build_report_3_display_label,
            )
            apply_dimension_filter_after_rebuild(
                "report3_channel_dimension_widget",
                "report3_channel_dimension_applied",
                old_channel_options,
                new_channel_options,
                selected_channel_before,
            )
            st.rerun()

    payload = st.session_state.get("report3_payload")

    # Después de reconstruir el reporte, se recalculan las opciones con el payload nuevo.
    # Esto evita tener que dar dos o tres clics para que aparezcan canales nuevos como #N/A.
    channel_options = get_filter_options_from_multiple_tables(
        [
            payload["mtd_channel_table"],
            payload["ytd_channel_table"],
        ],
        build_report_3_display_label,
    )

    # No se reinicia la selección aplicada después de reconstruir.
    # El filtro seleccionado por el usuario ya se guardó antes de correr el reporte.

    active_year_channel = payload["summary"]["latest_year"]
    active_month_channel = payload["summary"]["latest_month"]

    applied_channel_labels = get_valid_applied_filter_values(
        "report3_channel_dimension_applied",
        channel_options,
    )

    filtered_mtd_channel = filter_report_3_channel_table(
        payload["mtd_channel_table"],
        applied_channel_labels,
    )
    filtered_ytd_channel = filter_report_3_channel_table(
        payload["ytd_channel_table"],
        applied_channel_labels,
    )

    export_col_left, export_col_right = st.columns([12, 1])
    with export_col_right:
        report_3_bytes = exports.build_report_3_excel_bytes(
            mtd_channel_df=convert_report_table_for_export(payload["mtd_channel_table"]),
            ytd_channel_df=convert_report_table_for_export(payload["ytd_channel_table"]),
            report_title=build_report_context_title(
                "Reporte 3 - Channel",
                active_year_channel,
                active_month_channel,
            ),
        )
        render_icon_download_button(
            data=report_3_bytes,
            file_name=build_excel_filename(
                "reporte_3",
                active_year_channel,
                active_month_channel,
            ),
            key="download_report_3_icon",
            help_text="Descargar Reporte 3",
        )

    st.markdown(
        '<div class="report-note">Las tablas MTD y YTD se muestran lado a lado para facilitar la lectura ejecutiva. El Total General permanece visible y se recalcula conforme al filtro seleccionado.</div>',
        unsafe_allow_html=True,
    )

    left_col, right_col = st.columns(2)

    with left_col:
        st.markdown(
            build_report_3_table_html(
                build_report_context_title(
                    "MTD Channel",
                    active_year_channel,
                    active_month_channel,
                ),
                filtered_mtd_channel,
            ),
            unsafe_allow_html=True,
        )

    with right_col:
        st.markdown(
            build_report_3_table_html(
                build_report_context_title(
                    "YTD Channel",
                    active_year_channel,
                    active_month_channel,
                ),
                filtered_ytd_channel,
            ),
            unsafe_allow_html=True,
        )

    st.markdown("---")
    st.markdown("### Comparativo por Channel")
    st.markdown(
        '<div class="report-note">Gráfica de barras verticales con dos botones internos: MTD y YTD. Cada vista compara Actual, Plan y PY por Channel con colores diferenciados y valores visibles.</div>',
        unsafe_allow_html=True,
    )

    channel_bar_fig = charts.build_channel_mix_grouped_bar_interactive_chart(
        df_mtd_channel=filtered_mtd_channel,
        df_ytd_channel=filtered_ytd_channel,
        title=get_currency_kpi_suffix(),
        currency_mode=get_active_currency_mode(),
        exchange_rate=get_active_exchange_rate(),
    )

    if channel_bar_fig is not None:
        st.plotly_chart(channel_bar_fig, use_container_width=True)
    else:
        st.info("No hay información suficiente para construir la gráfica de barras.")

# =========================================================
# 17. REPORTE 4
# =========================================================
def run_report_4_build(
    selected_year: int | None = None,
    selected_month: int | None = None,
) -> None:
    df_processed_sales = st.session_state.get("df_processed_sales")
    df_plan_client = st.session_state.get("df_plan_client")

    if df_processed_sales is None or df_plan_client is None:
        set_error_message(config.MSG_REPORT_4_BUILD_MISSING_FILES)
        return

    is_sales_ready, missing_sales = validators.validate_dataframe_for_processing(
        df_processed_sales,
        config.REQUIRED_COLUMNS_REPORT_4_SALES,
    )
    is_plan_ready, missing_plan = validators.validate_dataframe_for_processing(
        df_plan_client,
        config.REQUIRED_COLUMNS_REPORT_4_PLAN_CLIENT,
    )

    if not is_sales_ready:
        set_error_message(config.MSG_VALIDATION_FAIL)
        set_warning_message(
            f"Columnas faltantes para Reporte 4 en ventas: {', '.join(missing_sales)}"
        )
        return

    if not is_plan_ready:
        set_error_message(config.MSG_VALIDATION_FAIL)
        set_warning_message(
            f"Columnas faltantes para Reporte 4 en plan por cliente: {', '.join(missing_plan)}"
        )
        return

    try:
        payload = data_processor.build_report_4_top_clients_payload(
            df_processed_sales,
            df_plan_client,
            selected_year=selected_year,
            selected_month=selected_month,
        )
        st.session_state["report4_payload"] = payload
        set_success_message(config.MSG_REPORT_4_BUILD_SUCCESS)
    except Exception as exc:
        set_error_message(f"{config.MSG_REPORT_4_BUILD_ERROR} Detalle: {exc}")


def format_report_4_value(value, is_percent: bool = False, zero_as_dash: bool = False) -> str:
    if zero_as_dash and not is_percent and not is_blank_number(value):
        try:
            if float(value) == 0:
                return "-"
        except (TypeError, ValueError):
            pass

    return format_monetary_value(value, is_percent=is_percent)


def build_report_4_title_box_html() -> str:
    return (
        '<div class="report-title-box">'
        f'<div class="report-title-main">{escape(config.REPORT_4_MAIN_HEADING)}</div>'
        f'<div class="report-title-sub">{escape(config.REPORT_4_SUBHEADING)}</div>'
        "</div>"
    )


def build_report_4_table_html(title: str, df_table) -> str:
    """
    Renderiza las tablas del Reporte 4 con una sola grid HTML.

    Esto evita el desfase entre encabezados y columnas porque el header y
    los renglones viven dentro del mismo contenedor CSS grid.
    """
    visible_columns = [
        "Client Name",
        "Cliente",
        "Actual",
        "Plan",
        "PY",
        "Var VS Plan",
        "%Var VS Plan",
        "Var VS PY",
        "%Var VS PY",
    ]

    if df_table is None or df_table.empty:
        return (
            '<div class="report-table-card report4-card">'
            f'<div class="report-table-title">{escape(title)}</div>'
            '<div class="report-table-scroll report4-scroll">'
            '<div class="report-note">Sin información disponible.</div>'
            '</div>'
            '</div>'
        )

    df_original = df_table.copy().reset_index(drop=True)
    df_visible = df_original.copy()

    for column_name in visible_columns:
        if column_name not in df_visible.columns:
            df_visible[column_name] = "" if column_name in {"Cliente", "Client Name"} else 0.0

    df_visible = df_visible[visible_columns].copy()

    cells_html_parts: list[str] = [
        '<div class="report-cell report-header report-header-neutral report4-sticky-header">CLIENT NAME</div>',
        '<div class="report-cell report-header report-header-neutral report4-code-header">CLIENTE</div>',
        '<div class="report-cell report-header report-header-actual">Actual</div>',
        '<div class="report-cell report-header report-header-plan">Plan</div>',
        '<div class="report-cell report-header report-header-py">PY</div>',
        '<div class="report-cell report-header report-header-neutral">Var VS Plan</div>',
        '<div class="report-cell report-header report-header-neutral">%Var VS Plan</div>',
        '<div class="report-cell report-header report-header-neutral">Var VS PY</div>',
        '<div class="report-cell report-header report-header-neutral">%Var VS PY</div>',
    ]

    for row_index, row in df_visible.iterrows():
        original_row = df_original.iloc[row_index]

        is_total = bool(original_row.get("__is_total__", False))
        is_grand_total = bool(original_row.get("__is_grand_total__", False))
        is_group_summary = bool(original_row.get("__is_group_summary__", False))

        state_class = ""
        if is_total or is_group_summary:
            state_class = " report4-total-cell"
        if is_grand_total:
            state_class = " report4-highlight-cell"

        client_code = str(row.get("Cliente", "")).strip()
        client_name = str(row.get("Client Name", "")).strip()

        actual_value = row["Actual"]
        plan_value = row["Plan"]
        py_value = row["PY"]
        var_plan_value = row["Var VS Plan"]
        pct_plan_value = row["%Var VS Plan"]
        var_py_value = row["Var VS PY"]
        pct_py_value = row["%Var VS PY"]

        actual_negative = (not is_blank_number(actual_value)) and float(actual_value) < 0
        plan_negative = (not is_blank_number(plan_value)) and float(plan_value) < 0
        py_negative = (not is_blank_number(py_value)) and float(py_value) < 0
        var_plan_negative = (not is_blank_number(var_plan_value)) and float(var_plan_value) < 0
        pct_plan_negative = (not is_blank_number(pct_plan_value)) and float(pct_plan_value) < 0
        var_py_negative = (not is_blank_number(var_py_value)) and float(var_py_value) < 0
        pct_py_negative = (not is_blank_number(pct_py_value)) and float(pct_py_value) < 0

        cells_html_parts.extend(
            [
                f'<div class="report-cell report4-sticky-cell{state_class}" title="{escape(client_name)}">{escape(client_name)}</div>',
                f'<div class="report-cell report4-code-cell{state_class}">{escape(client_code)}</div>',
                f'<div class="report-cell report-value-cell{state_class} {"report-negative" if actual_negative else ""}">{format_report_4_value(actual_value, zero_as_dash=not (is_total or is_group_summary or is_grand_total))}</div>',
                f'<div class="report-cell report-value-cell{state_class} {"report-negative" if plan_negative else ""}">{format_report_4_value(plan_value, zero_as_dash=not (is_total or is_group_summary or is_grand_total))}</div>',
                f'<div class="report-cell report-value-cell{state_class} {"report-negative" if py_negative else ""}">{format_report_4_value(py_value, zero_as_dash=not (is_total or is_group_summary or is_grand_total))}</div>',
                f'<div class="report-cell report-value-cell{state_class} {"report-negative" if var_plan_negative else ""}">{format_report_4_value(var_plan_value)}</div>',
                f'<div class="report-cell report-value-cell{state_class} {"report-negative" if pct_plan_negative else ""}">{format_report_4_value(pct_plan_value, is_percent=True)}</div>',
                f'<div class="report-cell report-value-cell{state_class} {"report-negative" if var_py_negative else ""}">{format_report_4_value(var_py_value)}</div>',
                f'<div class="report-cell report-value-cell{state_class} {"report-negative" if pct_py_negative else ""}">{format_report_4_value(pct_py_value, is_percent=True)}</div>',
            ]
        )

    cells_html = "".join(cells_html_parts)

    return (
        '<div class="report-table-card report4-card">'
        f'<div class="report-table-title">{escape(title)}</div>'
        '<div class="report-table-scroll report4-scroll">'
        f'<div class="report-grid report4-grid">{cells_html}</div>'
        '</div>'
        '</div>'
    )

def render_report_4_detail_block(title: str, mtd_df, ytd_df, year_value, month_value) -> None:
    st.markdown(f"### {title}")
    left_col, right_col = st.columns(2)

    with left_col:
        st.markdown(
            build_report_4_table_html(
                build_report_context_title(f"MTD {title}", year_value, month_value),
                mtd_df,
            ),
            unsafe_allow_html=True,
        )

    with right_col:
        st.markdown(
            build_report_4_table_html(
                build_report_context_title(f"YTD {title}", year_value, month_value),
                ytd_df,
            ),
            unsafe_allow_html=True,
        )


def render_report_4_view() -> None:
    st.markdown(
        f'<div class="section-title">{config.REPORT_4_TITLE}</div>',
        unsafe_allow_html=True,
    )

    st.markdown(build_report_4_title_box_html(), unsafe_allow_html=True)

    report_box_html = styles.build_info_box(
        """
        <b>Objetivo de esta vista:</b><br>
        Mostrar el comparativo ejecutivo MTD / YTD del ranking dinámico de clientes,
        ordenado por Actual y cruzando BASE SAP y Plan2026 by Client mediante código de cliente.
        """
    )
    st.markdown(report_box_html, unsafe_allow_html=True)

    st.markdown("### Construir Reporte")
    st.button(
        "Construir Reporte 4",
        on_click=run_report_4_build,
        use_container_width=True,
    )

    payload = st.session_state.get("report4_payload")

    if payload is None:
        st.markdown("---")
        st.info("Aún no se ha construido el Reporte 4.")
        return

    st.markdown("---")
    st.markdown("### Resumen ejecutivo")

    latest_month = payload["summary"]["latest_month"]
    latest_year = payload["summary"]["latest_year"]

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            styles.build_info_card(
                "Periodo actual",
                f"{latest_month:02d}/{latest_year}",
                "Periodo de corte seleccionado desde BASE SAP",
            ),
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            styles.build_info_card(
                "Orden del reporte",
                "Ranking dinámico",
                "MTD y YTD se ordenan por Actual de mayor a menor",
            ),
            unsafe_allow_html=True,
        )

    with col3:
        st.markdown(
            styles.build_info_card(
                "Cruce principal",
                "Código cliente",
                "Actual, PY y Plan se cruzan por código de cliente",
            ),
            unsafe_allow_html=True,
        )

    st.markdown("---")
    st.markdown("### Ranking de Clientes MTD / YTD")

    selected_year_clients, selected_month_clients = render_period_filter_block(
        "Filtro del bloque: Ranking de Clientes",
        "report4_clients_year",
        "report4_clients_month",
    )

    if selected_year_clients is not None and selected_month_clients is not None:
        if st.button(
            "Aplicar filtro",
            key="btn_report4_clients",
            use_container_width=False,
        ):
            run_report_4_build(
                selected_year=selected_year_clients,
                selected_month=selected_month_clients,
            )
            st.rerun()

    payload = st.session_state.get("report4_payload")

    report_4_bytes = exports.build_report_4_excel_bytes(
        mtd_top_clients_df=convert_report_table_for_export(payload["mtd_top_clients_table"]),
        ytd_top_clients_df=convert_report_table_for_export(payload["ytd_top_clients_table"]),
        report_title=build_report_context_title(
            "Reporte 4 - Ranking de Clientes",
            payload["summary"]["latest_year"],
            payload["summary"]["latest_month"],
        ),
    )

    export_col_left, export_col_right = st.columns([12, 1])
    with export_col_right:
        render_icon_download_button(
            data=report_4_bytes,
            file_name=build_excel_filename(
                "reporte_4",
                payload["summary"]["latest_year"],
                payload["summary"]["latest_month"],
            ),
            key="download_report_4_icon_top",
            help_text="Descargar Reporte 4",
        )

    st.markdown(
        '<div class="report-note">La vista ejecutiva muestra el Top 15 cliente por cliente y, enseguida, los bloques 16–50, 51–100 y Other clients como filas resumen. Los bloques se pueden desplegar para ver el detalle por código de cliente.</div>',
        unsafe_allow_html=True,
    )

    # Primero se muestra la tabla ejecutiva principal.
    # Después se coloca la gráfica, justo antes de los detalles desplegables.
    render_report_4_detail_block(
        "Vista ejecutiva: Top 15 + bloques resumen",
        payload["mtd_top_clients_table"],
        payload["ytd_top_clients_table"],
        payload["summary"]["latest_year"],
        payload["summary"]["latest_month"],
    )

    st.markdown("---")
    st.markdown("### Ranking Clients")

    chart_tab_mtd, chart_tab_ytd = st.tabs(["MTD", "YTD"])

    with chart_tab_mtd:
        mtd_chart = charts.build_report_4_ranking_chart(
            df_report_4=payload["mtd_top_clients_table"],
            title=f"Ranking Clientes MTD · Top 15 + bloques · {get_currency_kpi_suffix()}",
            currency_mode=get_active_currency_mode(),
            exchange_rate=get_active_exchange_rate(),
        )

        if mtd_chart is not None:
            st.plotly_chart(mtd_chart, use_container_width=True)
        else:
            st.info("No hay información suficiente para graficar el ranking MTD.")

    with chart_tab_ytd:
        ytd_chart = charts.build_report_4_ranking_chart(
            df_report_4=payload["ytd_top_clients_table"],
            title=f"Ranking Clientes YTD · Top 15 + bloques · {get_currency_kpi_suffix()}",
            currency_mode=get_active_currency_mode(),
            exchange_rate=get_active_exchange_rate(),
        )

        if ytd_chart is not None:
            st.plotly_chart(ytd_chart, use_container_width=True)
        else:
            st.info("No hay información suficiente para graficar el ranking YTD.")

    st.markdown("---")
    st.markdown("### Pareto dinámico de concentración")
    st.markdown(
        '<div class="report-note">El Pareto ordena clientes por Actual para mostrar concentración de ventas. La línea negra indica el porcentaje acumulado y permite identificar qué tantos clientes explican la mayor parte del total.</div>',
        unsafe_allow_html=True,
    )

    pareto_tabs = st.tabs([
        "MTD vs Plan",
        "MTD vs PY",
        "YTD vs Plan",
        "YTD vs PY",
    ])

    pareto_specs = [
        (payload["mtd_top_clients_table"], "plan", "MTD vs Plan"),
        (payload["mtd_top_clients_table"], "py", "MTD vs PY"),
        (payload["ytd_top_clients_table"], "plan", "YTD vs Plan"),
        (payload["ytd_top_clients_table"], "py", "YTD vs PY"),
    ]

    for pareto_tab, (pareto_df, comparison_type, pareto_title) in zip(pareto_tabs, pareto_specs):
        with pareto_tab:
            pareto_fig = charts.build_report_4_pareto_chart(
                df_report_4=pareto_df,
                title=f"Pareto Clientes {pareto_title} · {get_currency_kpi_suffix()}",
                comparison_type=comparison_type,
                currency_mode=get_active_currency_mode(),
                exchange_rate=get_active_exchange_rate(),
            )

            if pareto_fig is not None:
                st.plotly_chart(pareto_fig, use_container_width=True)
            else:
                st.info("No hay información suficiente para construir este Pareto.")

    with st.expander("Ver detalle: Clients 16 to 50", expanded=False):
        render_report_4_detail_block(
            "Clients 16 to 50",
            payload["mtd_group_16_50_table"],
            payload["ytd_group_16_50_table"],
            payload["summary"]["latest_year"],
            payload["summary"]["latest_month"],
        )

    with st.expander("Ver detalle: Clients 51 to 100", expanded=False):
        render_report_4_detail_block(
            "Clients 51 to 100",
            payload["mtd_group_51_100_table"],
            payload["ytd_group_51_100_table"],
            payload["summary"]["latest_year"],
            payload["summary"]["latest_month"],
        )

    with st.expander("Ver detalle: Other clients", expanded=False):
        render_report_4_detail_block(
            "Other clients",
            payload["mtd_group_other_table"],
            payload["ytd_group_other_table"],
            payload["summary"]["latest_year"],
            payload["summary"]["latest_month"],
        )



# =========================================================
# 17.1 DASHBOARD EJECUTIVO - ETAPA 1
# =========================================================
def load_dashboard_view_state() -> None:
    """
    El Dashboard no calcula ni reconstruye información.
    Solo habilita la visualización cuando ya existen todos los insumos.
    """
    st.session_state["dashboard_loaded"] = True


def get_dashboard_missing_dependencies() -> list[str]:
    """
    Valida el flujo completo antes de mostrar el Dashboard.
    Orden requerido:
    1) Ventas procesadas
    2) Base MTD construida
    3) Reportes 1, 2 Segment, 2 Category, 3 y 4 construidos
    """
    missing_dependencies: list[str] = []

    df_processed = st.session_state.get("df_processed_sales")
    if df_processed is None or getattr(df_processed, "empty", False):
        missing_dependencies.append("Primero procesa la base de ventas en Visión general.")

    if st.session_state.get("mtd_payload") is None:
        missing_dependencies.append("Primero construye la Base MTD.")

    if st.session_state.get("report1_payload") is None:
        missing_dependencies.append("Primero construye Oficina de ventas.")

    if st.session_state.get("report2_payload") is None:
        missing_dependencies.append("Primero construye Segmento x Región.")

    if st.session_state.get("report2_category_payload") is None:
        missing_dependencies.append("Primero construye Category.")

    if st.session_state.get("report3_payload") is None:
        missing_dependencies.append("Primero construye Canal.")

    if st.session_state.get("report4_payload") is None:
        missing_dependencies.append("Primero construye Ranking Clientes.")

    return missing_dependencies


def get_dashboard_month_label_en(month_number: int) -> str:
    month_labels = {
        1: "January",
        2: "February",
        3: "March",
        4: "April",
        5: "May",
        6: "June",
        7: "July",
        8: "August",
        9: "September",
        10: "October",
        11: "November",
        12: "December",
    }
    return month_labels.get(int(month_number), str(month_number))


def dashboard_safe_get_row(df_table, period_label: str):
    if df_table is None or df_table.empty:
        return None

    if "Periodo" not in df_table.columns:
        return None

    filtered = df_table[
        df_table["Periodo"].astype(str).str.upper().str.strip() == str(period_label).upper()
    ]

    if filtered.empty:
        return None

    return filtered.iloc[0]


def dashboard_format_value(value, is_percent: bool = False, allow_blank: bool = True) -> str:
    formatted = format_monetary_value(
        value,
        is_percent=is_percent,
        allow_blank=allow_blank,
    )
    return formatted if formatted != "" else "-"


def dashboard_value_class(value) -> str:
    if is_blank_number(value):
        return "dashboard-kpi-muted"

    try:
        return "dashboard-kpi-negative" if float(value) < 0 else "dashboard-kpi-neutral"
    except (TypeError, ValueError):
        return "dashboard-kpi-neutral"


def dashboard_td(value, is_percent: bool = False, allow_blank: bool = True) -> str:
    return (
        f'<td class="{dashboard_value_class(value)}">'
        f'{escape(dashboard_format_value(value, is_percent=is_percent, allow_blank=allow_blank))}'
        '</td>'
    )


def build_dashboard_metric_row(
    metric_name: str,
    actual,
    plan,
    py,
    var_plan,
    pct_var_plan,
    var_py,
    pct_var_py,
    row_class: str = "",
) -> str:
    return (
        f'<tr class="{escape(row_class)}">'
        f'<td class="dashboard-kpi-name">{escape(metric_name)}</td>'
        f'{dashboard_td(actual)}'
        f'{dashboard_td(plan)}'
        f'{dashboard_td(py)}'
        f'{dashboard_td(var_plan)}'
        f'{dashboard_td(pct_var_plan, is_percent=True)}'
        f'{dashboard_td(var_py)}'
        f'{dashboard_td(pct_var_py, is_percent=True)}'
        '</tr>'
    )


def dashboard_percent_closed_td(value, allow_blank: bool = True) -> str:
    """
    Formato especial para % achievement del Dashboard.
    Se muestra como porcentaje cerrado, sin decimales, igual que el archivo de referencia.
    """
    if is_blank_number(value):
        formatted_value = "-" if allow_blank else "0%"
        cell_class = "dashboard-kpi-muted"
    else:
        numeric_value = float(value)
        formatted_value = f"{numeric_value * 100:,.0f}%"
        cell_class = "dashboard-kpi-negative" if numeric_value < 0 else "dashboard-kpi-neutral"

    return f'<td class="{cell_class}">{escape(formatted_value)}</td>'


def build_dashboard_achievement_row(gsnr_row) -> str:
    if gsnr_row is None:
        achievement_plan = None
        achievement_py = None
    else:
        actual_value = safe_float(gsnr_row.get("Actual"))
        plan_value = safe_float(gsnr_row.get("Plan"))
        py_value = safe_float(gsnr_row.get("PY"))
        achievement_plan = None if plan_value == 0 else actual_value / plan_value
        achievement_py = None if py_value == 0 else actual_value / py_value

    # En el dashboard de referencia, el % achievement va debajo de las columnas
    # de variación contra Plan y contra PY, no debajo de las columnas %Var.
    return (
        '<tr class="dashboard-achievement-row">'
        '<td class="dashboard-kpi-name">% achievement</td>'
        f'{dashboard_td(None)}'
        f'{dashboard_td(None)}'
        f'{dashboard_td(None)}'
        f'{dashboard_percent_closed_td(achievement_plan)}'
        f'{dashboard_td(None)}'
        f'{dashboard_percent_closed_td(achievement_py)}'
        f'{dashboard_td(None)}'
        '</tr>'
    )


def build_dashboard_kpi_table_html(title: str, rows_html: str) -> str:
    return (
        '<div class="dashboard-kpi-panel">'
        f'<div class="dashboard-kpi-panel-title">{escape(title)}</div>'
        '<div class="dashboard-kpi-table-wrap">'
        '<table class="dashboard-kpi-table">'
        '<thead>'
        '<tr>'
        '<th>KPI</th>'
        '<th>Actual</th>'
        '<th>Plan</th>'
        '<th>PY</th>'
        '<th>Var vs Plan</th>'
        '<th>%Var vs Plan</th>'
        '<th>Var vs PY</th>'
        '<th>%Var vs PY</th>'
        '</tr>'
        '</thead>'
        '<tbody>'
        f'{rows_html}'
        '</tbody>'
        '</table>'
        '</div>'
        '</div>'
    )


def build_dashboard_css_html() -> str:
    return styles.build_dashboard_css_html()

def dashboard_get_report1_payload() -> dict | None:
    return st.session_state.get("report1_payload")


def dashboard_is_zero_value(value) -> bool:
    if is_blank_number(value):
        return False
    try:
        return abs(float(value)) < 1e-12
    except (TypeError, ValueError):
        return False


def dashboard_format_compact_value(value, is_percent: bool = False, allow_blank: bool = True) -> str:
    """
    Formato para tablas compactas del Dashboard.
    En estos reportes ejecutivos, 0 se muestra como "-".
    """
    if is_blank_number(value):
        return "-"

    try:
        numeric_value = float(value)
        if abs(numeric_value) < 0.0000001:
            return "-"
    except (TypeError, ValueError):
        pass

    return dashboard_format_value(value, is_percent=is_percent, allow_blank=allow_blank)

def dashboard_compact_td(value, is_percent: bool = False, allow_blank: bool = True) -> str:
    return (
        f'<td class="{dashboard_value_class(value)}">'
        f'{escape(dashboard_format_compact_value(value, is_percent=is_percent, allow_blank=allow_blank))}'
        '</td>'
    )


def build_dashboard_ellipsis_row(colspan: int = 8) -> str:
    return (
        '<tr class="dashboard-ellipsis">'
        f'<td colspan="{int(colspan)}">⋮</td>'
        '</tr>'
    )


def build_dashboard_report1_compact_table_html(
    title: str,
    df_table,
) -> str:
    """
    Construye la tabla compacta del Reporte 1 para Dashboard.

    Reglas visuales del Dashboard:
    - No oculta filas con puntos suspensivos en Channel.
    - Muestra 0 como "-".
    - Conserva porcentajes de variación.
    - Mantiene columnas fijas para que Monthly y YTD queden alineados.
    """
    if df_table is None or getattr(df_table, "empty", True):
        return (
            '<div class="dashboard-compact-block">'
            f'<div class="dashboard-compact-title-box">{escape(title)}</div>'
            '<div class="dashboard-kpi-muted">Información no disponible.</div>'
            '</div>'
        )

    detail_rows = []
    total_rows = []

    for _, row in df_table.iterrows():
        if bool(row.get("__is_total__", False)) or bool(row.get("__is_grand_total__", False)):
            total_rows.append(row)
        else:
            detail_rows.append(row)

    rows_html_parts: list[str] = []

    for row in detail_rows:
        label_value = str(row.get("Oficina de Ventas", "")).strip()
        rows_html_parts.append(
            '<tr>'
            f'<td class="dashboard-compact-label">{escape(label_value)}</td>'
            f'{dashboard_compact_td(row.get("Actual"))}'
            f'{dashboard_compact_td(row.get("Plan"))}'
            f'{dashboard_compact_td(row.get("PY"))}'
            f'{dashboard_compact_td(row.get("Var VS Plan"))}'
            f'{dashboard_compact_td(row.get("%Var VS Plan"), is_percent=True)}'
            f'{dashboard_compact_td(row.get("Var VS PY"))}'
            f'{dashboard_compact_td(row.get("%Var VS PY"), is_percent=True)}'
            '</tr>'
        )

    for row in total_rows:
        label_value = str(row.get("Oficina de Ventas", "Total Mexico")).strip()
        if label_value.lower() in {"total", "total kens", "total general"}:
            label_value = "Total Mexico"

        rows_html_parts.append(
            '<tr class="dashboard-compact-total">'
            f'<td class="dashboard-compact-label">{escape(label_value)}</td>'
            f'{dashboard_compact_td(row.get("Actual"))}'
            f'{dashboard_compact_td(row.get("Plan"))}'
            f'{dashboard_compact_td(row.get("PY"))}'
            f'{dashboard_compact_td(row.get("Var VS Plan"))}'
            f'{dashboard_compact_td(row.get("%Var VS Plan"), is_percent=True)}'
            f'{dashboard_compact_td(row.get("Var VS PY"))}'
            f'{dashboard_compact_td(row.get("%Var VS PY"), is_percent=True)}'
            '</tr>'
        )

    rows_html = "".join(rows_html_parts)

    return (
        '<div class="dashboard-compact-block">'
        f'<div class="dashboard-compact-title-box">{escape(title)}</div>'
        '<div class="dashboard-compact-table-wrap">'
        '<table class="dashboard-compact-table">'
        '<colgroup>'
        '<col class="dashboard-col-channel">'
        '<col class="dashboard-col-num">'
        '<col class="dashboard-col-num">'
        '<col class="dashboard-col-num">'
        '<col class="dashboard-col-num">'
        '<col class="dashboard-col-pct">'
        '<col class="dashboard-col-num">'
        '<col class="dashboard-col-pct">'
        '</colgroup>'
        '<thead>'
        '<tr>'
        '<th>Channel</th>'
        '<th>Actual</th>'
        '<th>Plan</th>'
        '<th>PY</th>'
        '<th>Var vs Plan</th>'
        '<th>%Var vs Plan</th>'
        '<th>Var vs PY</th>'
        '<th>%Var vs PY</th>'
        '</tr>'
        '</thead>'
        '<tbody>'
        f'{rows_html}'
        '</tbody>'
        '</table>'
        '</div>'
        '</div>'
    )


def build_dashboard_empty_report1_row(label_value: str) -> dict:
    return {
        "Oficina de Ventas": label_value,
        "Actual": 0.0,
        "Plan": 0.0,
        "PY": 0.0,
        "Var VS Plan": 0.0,
        "%Var VS Plan": None,
        "Var VS PY": 0.0,
        "%Var VS PY": None,
        "__is_total__": False,
        "__is_highlight__": False,
    }


def dashboard_report1_label_order(mtd_table, ytd_table) -> list[str]:
    """
    Define un orden fijo de canales para que Monthly y YTD tengan la misma altura
    y no se desalineen cuando un canal no tiene ventas en el mes.
    """
    configured_labels = []
    for code in getattr(config, "REPORT_1_CHANNEL_ORDER", []):
        clean_code = str(code).strip().upper()
        if clean_code in {"AF", "AFI"}:
            continue
        label = config.REPORT_1_CHANNEL_LABELS.get(clean_code, clean_code)
        if label and label not in configured_labels:
            configured_labels.append(label)

    existing_labels = []
    for df_table in [mtd_table, ytd_table]:
        if df_table is None or getattr(df_table, "empty", True):
            continue
        for _, row in df_table.iterrows():
            if bool(row.get("__is_total__", False)) or bool(row.get("__is_grand_total__", False)):
                continue
            label = str(row.get("Oficina de Ventas", "")).strip()
            if label and label not in existing_labels:
                existing_labels.append(label)

    extra_labels = [label for label in existing_labels if label not in configured_labels]
    return configured_labels + extra_labels


def dashboard_complete_report1_table(df_table, ordered_labels: list[str]):
    """
    Rellena canales faltantes con cero para que el Dashboard no cambie de tamaño.
    """
    if df_table is None or getattr(df_table, "empty", True):
        rows = [build_dashboard_empty_report1_row(label) for label in ordered_labels]
        rows.append({
            **build_dashboard_empty_report1_row("Total Mexico"),
            "__is_total__": True,
        })
        return data_processor.pd.DataFrame(rows)

    total_rows = []
    detail_by_label = {}

    for _, row in df_table.iterrows():
        label = str(row.get("Oficina de Ventas", "")).strip()
        if bool(row.get("__is_total__", False)) or bool(row.get("__is_grand_total__", False)):
            total_rows.append(dict(row))
        else:
            detail_by_label[label] = dict(row)

    completed_rows = []
    for label in ordered_labels:
        completed_rows.append(detail_by_label.get(label, build_dashboard_empty_report1_row(label)))

    if total_rows:
        completed_rows.extend(total_rows)
    else:
        completed_rows.append({
            **build_dashboard_empty_report1_row("Total Mexico"),
            "__is_total__": True,
        })

    return data_processor.pd.DataFrame(completed_rows)

def build_dashboard_report1_section_html() -> str:
    report1_payload = dashboard_get_report1_payload()

    if report1_payload is None:
        return ""

    mtd_table = report1_payload.get("mtd_without_kens_table")
    ytd_table = report1_payload.get("ytd_without_kens_table")

    ordered_labels = dashboard_report1_label_order(mtd_table, ytd_table)
    mtd_table = dashboard_complete_report1_table(mtd_table, ordered_labels)
    ytd_table = dashboard_complete_report1_table(ytd_table, ordered_labels)

    return (
        '<div class="dashboard-report-section">'
        '<div class="dashboard-report-pair-grid">'
        f'{build_dashboard_report1_compact_table_html("Sales by Channel Monthly", mtd_table)}'
        f'{build_dashboard_report1_compact_table_html("Sales by Channel YTD", ytd_table)}'
        '</div>'
        '</div>'
    )


def dashboard_get_report2_payload() -> dict | None:
    return st.session_state.get("report2_payload")


def build_dashboard_segment_empty_row(segment_value: str, region_value: str) -> dict:
    return {
        "Segmento": str(segment_value or "").strip(),
        "Región": str(region_value or "").strip(),
        "Actual": 0.0,
        "Plan": 0.0,
        "PY": 0.0,
        "Var VS Plan": 0.0,
        "%Var VS Plan": None,
        "Var VS PY": 0.0,
        "%Var VS PY": None,
        "__is_total__": False,
        "__is_grand_total__": False,
    }


def dashboard_segment_key(row) -> tuple[str, str]:
    return (
        str(row.get("Segmento", "")).strip(),
        str(row.get("Región", "")).strip(),
    )


def dashboard_segment_detail_order(mtd_table, ytd_table) -> list[tuple[str, str]]:
    """
    Mantiene Segment x Region ordenado por grupo:
    detalle de regiones -> total del segmento -> Total General.
    También toma la unión de MTD/YTD para que ambos bloques tengan la misma altura.
    """
    ordered_keys: list[tuple[str, str]] = []

    for df_table in [mtd_table, ytd_table]:
        if df_table is None or getattr(df_table, "empty", True):
            continue

        for _, row in df_table.iterrows():
            if bool(row.get("__is_total__", False)) or bool(row.get("__is_grand_total__", False)):
                continue

            key = dashboard_segment_key(row)
            if key[0] and key not in ordered_keys:
                ordered_keys.append(key)

    return ordered_keys


def dashboard_segment_totals_by_segment(df_table) -> dict[str, dict]:
    totals: dict[str, dict] = {}

    if df_table is None or getattr(df_table, "empty", True):
        return totals

    for _, row in df_table.iterrows():
        if bool(row.get("__is_total__", False)) and not bool(row.get("__is_grand_total__", False)):
            segment_value = str(row.get("Segmento", "")).strip()
            if segment_value:
                totals[segment_value] = dict(row)

    return totals


def dashboard_segment_grand_total_row(df_table) -> dict | None:
    if df_table is None or getattr(df_table, "empty", True):
        return None

    for _, row in df_table.iterrows():
        if bool(row.get("__is_grand_total__", False)):
            return dict(row)

    return None


def dashboard_complete_segment_table(df_table, ordered_keys: list[tuple[str, str]]):
    """
    Completa filas faltantes con cero, pero respeta el orden correcto:
    ACCO detalle -> ACCO Total -> BARRILITO detalle -> BARRILITO Total -> KENS detalle -> KENS Total -> Total General.
    """
    detail_by_key: dict[tuple[str, str], dict] = {}

    if df_table is not None and not getattr(df_table, "empty", True):
        for _, row in df_table.iterrows():
            if bool(row.get("__is_total__", False)) or bool(row.get("__is_grand_total__", False)):
                continue
            detail_by_key[dashboard_segment_key(row)] = dict(row)

    totals_by_segment = dashboard_segment_totals_by_segment(df_table)
    grand_total = dashboard_segment_grand_total_row(df_table)

    segment_order: list[str] = []
    keys_by_segment: dict[str, list[tuple[str, str]]] = {}

    for key in ordered_keys:
        segment_value, _ = key
        if segment_value not in segment_order:
            segment_order.append(segment_value)
        keys_by_segment.setdefault(segment_value, []).append(key)

    completed_rows: list[dict] = []

    for segment_value in segment_order:
        for key in keys_by_segment.get(segment_value, []):
            completed_rows.append(
                detail_by_key.get(
                    key,
                    build_dashboard_segment_empty_row(
                        segment_value=key[0],
                        region_value=key[1],
                    ),
                )
            )

        if segment_value in totals_by_segment:
            completed_rows.append(totals_by_segment[segment_value])

    if grand_total is not None:
        completed_rows.append(grand_total)

    return data_processor.pd.DataFrame(completed_rows)


def build_dashboard_segment_compact_table_html(title: str, df_table) -> str:
    """
    Segment x Region en el mismo formato aprobado del Dashboard.
    No usa puntos suspensivos.
    """
    if df_table is None or getattr(df_table, "empty", True):
        return (
            '<div class="dashboard-compact-block">'
            f'<div class="dashboard-compact-title-box">{escape(title)}</div>'
            '<div class="dashboard-kpi-muted">Información no disponible.</div>'
            '</div>'
        )

    rows_html_parts: list[str] = []

    for _, row in df_table.iterrows():
        is_total = bool(row.get("__is_total__", False))
        is_grand_total = bool(row.get("__is_grand_total__", False))

        row_class = ""
        if is_total or is_grand_total:
            row_class = ' class="dashboard-compact-total"'

        label_value = build_report_2_segment_region_display_label(row)
        if is_grand_total:
            label_value = "Total Mexico"

        rows_html_parts.append(
            f'<tr{row_class}>'
            f'<td class="dashboard-compact-label">{escape(label_value)}</td>'
            f'{dashboard_compact_td(row.get("Actual"))}'
            f'{dashboard_compact_td(row.get("Plan"))}'
            f'{dashboard_compact_td(row.get("PY"))}'
            f'{dashboard_compact_td(row.get("Var VS Plan"))}'
            f'{dashboard_compact_td(row.get("%Var VS Plan"), is_percent=True)}'
            f'{dashboard_compact_td(row.get("Var VS PY"))}'
            f'{dashboard_compact_td(row.get("%Var VS PY"), is_percent=True)}'
            '</tr>'
        )

    rows_html = "".join(rows_html_parts)

    return (
        '<div class="dashboard-compact-block">'
        f'<div class="dashboard-compact-title-box">{escape(title)}</div>'
        '<div class="dashboard-compact-table-wrap">'
        '<table class="dashboard-compact-table">'
        '<colgroup>'
        '<col class="dashboard-col-channel">'
        '<col class="dashboard-col-num">'
        '<col class="dashboard-col-num">'
        '<col class="dashboard-col-num">'
        '<col class="dashboard-col-num">'
        '<col class="dashboard-col-pct">'
        '<col class="dashboard-col-num">'
        '<col class="dashboard-col-pct">'
        '</colgroup>'
        '<thead>'
        '<tr>'
        '<th>Segment / Region</th>'
        '<th>Actual</th>'
        '<th>Plan</th>'
        '<th>PY</th>'
        '<th>Var vs Plan</th>'
        '<th>%Var vs Plan</th>'
        '<th>Var vs PY</th>'
        '<th>%Var vs PY</th>'
        '</tr>'
        '</thead>'
        '<tbody>'
        f'{rows_html}'
        '</tbody>'
        '</table>'
        '</div>'
        '</div>'
    )


def build_dashboard_report2_segment_section_html() -> str:
    report2_payload = dashboard_get_report2_payload()

    if report2_payload is None:
        return ""

    mtd_table = report2_payload.get("mtd_segment_region_table")
    ytd_table = report2_payload.get("ytd_segment_region_table")

    ordered_keys = dashboard_segment_detail_order(mtd_table, ytd_table)
    mtd_table = dashboard_complete_segment_table(mtd_table, ordered_keys)
    ytd_table = dashboard_complete_segment_table(ytd_table, ordered_keys)

    return (
        '<div class="dashboard-report-section">'
        '<div class="dashboard-report-pair-grid">'
        f'{build_dashboard_segment_compact_table_html("Segment x Region Monthly", mtd_table)}'
        f'{build_dashboard_segment_compact_table_html("Segment x Region YTD", ytd_table)}'
        '</div>'
        '</div>'
    )


def dashboard_get_report2_category_payload() -> dict | None:
    return st.session_state.get("report2_category_payload")


def build_dashboard_category_empty_row(category_value: str) -> dict:
    return {
        "Category": str(category_value or "").strip(),
        "Actual": 0.0,
        "Plan": 0.0,
        "PY": 0.0,
        "Var VS Plan": 0.0,
        "%Var VS Plan": None,
        "Var VS PY": 0.0,
        "%Var VS PY": None,
        "__is_total__": False,
        "__is_grand_total__": False,
    }


def dashboard_category_label(row) -> str:
    return str(row.get("Category", "")).strip()


def dashboard_category_order(mtd_table, ytd_table) -> list[str]:
    """
    Obtiene la lista de categorías en el orden del reporte existente.
    Toma la unión de MTD/YTD para que ambos bloques tengan la misma altura.
    """
    ordered_labels: list[str] = []

    for df_table in [mtd_table, ytd_table]:
        if df_table is None or getattr(df_table, "empty", True):
            continue

        for _, row in df_table.iterrows():
            if bool(row.get("__is_grand_total__", False)):
                continue

            category_value = dashboard_category_label(row)
            if category_value and category_value not in ordered_labels:
                ordered_labels.append(category_value)

    return ordered_labels


def dashboard_aggregate_category_table(df_table, ordered_labels: list[str]):
    """
    Resume Category para el Dashboard a una fila por categoría.
    No muestra Material, Categoría del Material ni Descripción.

    Usa únicamente los renglones de total por categoría cuando existen
    (__is_total__ = True), porque esos ya traen el total correcto del reporte.
    Si no existieran, suma el detalle por categoría como respaldo.
    """
    if df_table is None or getattr(df_table, "empty", True):
        rows = [build_dashboard_category_empty_row(label) for label in ordered_labels]
        rows.append({
            **build_dashboard_category_empty_row("Total Mexico"),
            "__is_grand_total__": True,
        })
        return data_processor.pd.DataFrame(rows)

    rows_by_category: dict[str, dict] = {}
    detail_by_category: dict[str, list[dict]] = {}
    grand_total_row: dict | None = None

    for _, row in df_table.iterrows():
        row_dict = dict(row)
        category_value = str(row_dict.get("Category", "")).strip()

        if bool(row_dict.get("__is_grand_total__", False)):
            grand_total_row = row_dict
            continue

        if not category_value:
            continue

        if bool(row_dict.get("__is_total__", False)):
            rows_by_category[category_value] = row_dict
        else:
            detail_by_category.setdefault(category_value, []).append(row_dict)

    # Respaldo: si alguna categoría no trae fila total, se suma su detalle.
    for category_value, detail_rows in detail_by_category.items():
        if category_value in rows_by_category:
            continue

        if not detail_rows:
            continue

        template_row = dict(detail_rows[0])
        total_actual = sum(safe_float(row.get("Actual")) for row in detail_rows)
        total_plan = sum(safe_float(row.get("Plan")) for row in detail_rows)
        total_py = sum(safe_float(row.get("PY")) for row in detail_rows)

        total_row = recalculate_row_metrics(
            template_row,
            actual=total_actual,
            plan=total_plan,
            py=total_py,
        )
        total_row["Category"] = category_value
        total_row["__is_total__"] = False
        total_row["__is_grand_total__"] = False
        rows_by_category[category_value] = total_row

    completed_rows: list[dict] = []

    for category_value in ordered_labels:
        if str(category_value).strip().lower() in {"total mexico", "total general", "grand total"}:
            continue

        row = rows_by_category.get(
            category_value,
            build_dashboard_category_empty_row(category_value),
        )
        row["Category"] = category_value
        row["__is_total__"] = False
        row["__is_grand_total__"] = False
        completed_rows.append(row)

    if grand_total_row is not None:
        grand_total_row["Category"] = "Total Mexico"
        grand_total_row["__is_total__"] = False
        grand_total_row["__is_grand_total__"] = True
        completed_rows.append(grand_total_row)
    else:
        grand_actual = sum(safe_float(row.get("Actual")) for row in completed_rows)
        grand_plan = sum(safe_float(row.get("Plan")) for row in completed_rows)
        grand_py = sum(safe_float(row.get("PY")) for row in completed_rows)

        total_template = build_dashboard_category_empty_row("Total Mexico")
        total_row = recalculate_row_metrics(
            total_template,
            actual=grand_actual,
            plan=grand_plan,
            py=grand_py,
        )
        total_row["Category"] = "Total Mexico"
        total_row["__is_total__"] = False
        total_row["__is_grand_total__"] = True
        completed_rows.append(total_row)

    return data_processor.pd.DataFrame(completed_rows)


def build_dashboard_category_compact_table_html(title: str, df_table) -> str:
    """
    Category en formato ejecutivo para Dashboard.
    Una fila por categoría, sin detalle por material y sin puntos suspensivos.
    """
    if df_table is None or getattr(df_table, "empty", True):
        return (
            '<div class="dashboard-compact-block">'
            f'<div class="dashboard-compact-title-box">{escape(title)}</div>'
            '<div class="dashboard-kpi-muted">Información no disponible.</div>'
            '</div>'
        )

    rows_html_parts: list[str] = []

    for _, row in df_table.iterrows():
        is_total = bool(row.get("__is_total__", False))
        is_grand_total = bool(row.get("__is_grand_total__", False))

        row_class = ""
        if is_total or is_grand_total:
            row_class = ' class="dashboard-compact-total"'

        label_value = str(row.get("Category", "")).strip()
        if is_grand_total:
            label_value = "Total Mexico"

        rows_html_parts.append(
            f'<tr{row_class}>'
            f'<td class="dashboard-compact-label">{escape(label_value)}</td>'
            f'{dashboard_compact_td(row.get("Actual"))}'
            f'{dashboard_compact_td(row.get("Plan"))}'
            f'{dashboard_compact_td(row.get("PY"))}'
            f'{dashboard_compact_td(row.get("Var VS Plan"))}'
            f'{dashboard_compact_td(row.get("%Var VS Plan"), is_percent=True)}'
            f'{dashboard_compact_td(row.get("Var VS PY"))}'
            f'{dashboard_compact_td(row.get("%Var VS PY"), is_percent=True)}'
            '</tr>'
        )

    rows_html = "".join(rows_html_parts)

    return (
        '<div class="dashboard-compact-block">'
        f'<div class="dashboard-compact-title-box">{escape(title)}</div>'
        '<div class="dashboard-compact-table-wrap">'
        '<table class="dashboard-compact-table">'
        '<colgroup>'
        '<col class="dashboard-col-channel">'
        '<col class="dashboard-col-num">'
        '<col class="dashboard-col-num">'
        '<col class="dashboard-col-num">'
        '<col class="dashboard-col-num">'
        '<col class="dashboard-col-pct">'
        '<col class="dashboard-col-num">'
        '<col class="dashboard-col-pct">'
        '</colgroup>'
        '<thead>'
        '<tr>'
        '<th>Category</th>'
        '<th>Actual</th>'
        '<th>Plan</th>'
        '<th>PY</th>'
        '<th>Var vs Plan</th>'
        '<th>%Var vs Plan</th>'
        '<th>Var vs PY</th>'
        '<th>%Var vs PY</th>'
        '</tr>'
        '</thead>'
        '<tbody>'
        f'{rows_html}'
        '</tbody>'
        '</table>'
        '</div>'
        '</div>'
    )


def build_dashboard_report2_category_section_html() -> str:
    report2_category_payload = dashboard_get_report2_category_payload()

    if report2_category_payload is None:
        return ""

    mtd_table = report2_category_payload.get("mtd_category_table")
    ytd_table = report2_category_payload.get("ytd_category_table")

    ordered_labels = dashboard_category_order(mtd_table, ytd_table)
    mtd_table = dashboard_aggregate_category_table(mtd_table, ordered_labels)
    ytd_table = dashboard_aggregate_category_table(ytd_table, ordered_labels)

    return (
        '<div class="dashboard-report-section">'
        '<div class="dashboard-report-pair-grid">'
        f'{build_dashboard_category_compact_table_html("Sales by Category Monthly", mtd_table)}'
        f'{build_dashboard_category_compact_table_html("Sales by Category YTD", ytd_table)}'
        '</div>'
        '</div>'
    )


def dashboard_get_report3_payload() -> dict | None:
    return st.session_state.get("report3_payload")


def build_dashboard_report3_empty_row(channel_value: str) -> dict:
    return {
        "Channel": str(channel_value or "").strip(),
        "Actual": 0.0,
        "Plan": 0.0,
        "PY": 0.0,
        "Var VS Plan": 0.0,
        "%Var VS Plan": None,
        "Var VS PY": 0.0,
        "%Var VS PY": None,
        "__is_total__": False,
        "__is_grand_total__": False,
    }


def dashboard_report3_channel_order(mtd_table, ytd_table) -> list[str]:
    """
    Orden fijo para que el reporte de Desempeño Comercial quede completo
    y con la misma altura en Monthly/YTD.
    """
    configured_labels = []

    for channel_value in getattr(config, "REPORT_3_CHANNEL_ORDER", []):
        label_value = str(channel_value or "").strip()
        if label_value == "GOBA":
            label_value = "BARRILITO"
        if label_value and label_value not in configured_labels:
            configured_labels.append(label_value)

    existing_labels = []
    for df_table in [mtd_table, ytd_table]:
        if df_table is None or getattr(df_table, "empty", True):
            continue

        for _, row in df_table.iterrows():
            if bool(row.get("__is_total__", False)) or bool(row.get("__is_grand_total__", False)):
                continue

            label_value = build_report_3_display_label(row)
            if label_value and label_value not in existing_labels:
                existing_labels.append(label_value)

    extra_labels = [label for label in existing_labels if label not in configured_labels]

    if configured_labels:
        return configured_labels + extra_labels

    return existing_labels


def dashboard_complete_report3_table(df_table, ordered_labels: list[str]):
    """
    Completa canales faltantes con cero para que Monthly/YTD mantengan
    la misma estructura visual.
    """
    if df_table is None or getattr(df_table, "empty", True):
        rows = [build_dashboard_report3_empty_row(label) for label in ordered_labels]
        rows.append({
            **build_dashboard_report3_empty_row("Total Mexico"),
            "__is_grand_total__": True,
        })
        return data_processor.pd.DataFrame(rows)

    detail_by_label: dict[str, dict] = {}
    total_rows: list[dict] = []

    for _, row in df_table.iterrows():
        row_dict = dict(row)

        if bool(row_dict.get("__is_total__", False)) or bool(row_dict.get("__is_grand_total__", False)):
            total_rows.append(row_dict)
            continue

        label_value = build_report_3_display_label(row_dict)
        row_dict["Channel"] = label_value
        detail_by_label[label_value] = row_dict

    completed_rows: list[dict] = []

    for label_value in ordered_labels:
        completed_rows.append(
            detail_by_label.get(
                label_value,
                build_dashboard_report3_empty_row(label_value),
            )
        )

    if total_rows:
        for total_row in total_rows:
            total_row["Channel"] = "Total Mexico"
            completed_rows.append(total_row)
    else:
        grand_actual = sum(safe_float(row.get("Actual")) for row in completed_rows)
        grand_plan = sum(safe_float(row.get("Plan")) for row in completed_rows)
        grand_py = sum(safe_float(row.get("PY")) for row in completed_rows)

        total_template = build_dashboard_report3_empty_row("Total Mexico")
        total_row = recalculate_row_metrics(
            total_template,
            actual=grand_actual,
            plan=grand_plan,
            py=grand_py,
        )
        total_row["Channel"] = "Total Mexico"
        total_row["__is_grand_total__"] = True
        completed_rows.append(total_row)

    return data_processor.pd.DataFrame(completed_rows)


def build_dashboard_report3_compact_table_html(title: str, df_table) -> str:
    """
    Desempeño Comercial / Reporte 3 en el formato estándar del Dashboard.
    Como es pequeño, se muestra completo.
    """
    if df_table is None or getattr(df_table, "empty", True):
        return (
            '<div class="dashboard-compact-block">'
            f'<div class="dashboard-compact-title-box">{escape(title)}</div>'
            '<div class="dashboard-kpi-muted">Información no disponible.</div>'
            '</div>'
        )

    rows_html_parts: list[str] = []

    for _, row in df_table.iterrows():
        is_total = bool(row.get("__is_total__", False))
        is_grand_total = bool(row.get("__is_grand_total__", False))

        row_class = ""
        if is_total or is_grand_total:
            row_class = ' class="dashboard-compact-total"'

        label_value = str(row.get("Channel", "")).strip()
        if not label_value:
            label_value = build_report_3_display_label(row)

        if is_total or is_grand_total:
            label_value = "Total Mexico"

        rows_html_parts.append(
            f'<tr{row_class}>'
            f'<td class="dashboard-compact-label">{escape(label_value)}</td>'
            f'{dashboard_compact_td(row.get("Actual"))}'
            f'{dashboard_compact_td(row.get("Plan"))}'
            f'{dashboard_compact_td(row.get("PY"))}'
            f'{dashboard_compact_td(row.get("Var VS Plan"))}'
            f'{dashboard_compact_td(row.get("%Var VS Plan"), is_percent=True)}'
            f'{dashboard_compact_td(row.get("Var VS PY"))}'
            f'{dashboard_compact_td(row.get("%Var VS PY"), is_percent=True)}'
            '</tr>'
        )

    rows_html = "".join(rows_html_parts)

    return (
        '<div class="dashboard-compact-block">'
        f'<div class="dashboard-compact-title-box">{escape(title)}</div>'
        '<div class="dashboard-compact-table-wrap">'
        '<table class="dashboard-compact-table">'
        '<colgroup>'
        '<col class="dashboard-col-channel">'
        '<col class="dashboard-col-num">'
        '<col class="dashboard-col-num">'
        '<col class="dashboard-col-num">'
        '<col class="dashboard-col-num">'
        '<col class="dashboard-col-pct">'
        '<col class="dashboard-col-num">'
        '<col class="dashboard-col-pct">'
        '</colgroup>'
        '<thead>'
        '<tr>'
        '<th>Channel</th>'
        '<th>Actual</th>'
        '<th>Plan</th>'
        '<th>PY</th>'
        '<th>Var vs Plan</th>'
        '<th>%Var vs Plan</th>'
        '<th>Var vs PY</th>'
        '<th>%Var vs PY</th>'
        '</tr>'
        '</thead>'
        '<tbody>'
        f'{rows_html}'
        '</tbody>'
        '</table>'
        '</div>'
        '</div>'
    )


def build_dashboard_report3_section_html() -> str:
    report3_payload = dashboard_get_report3_payload()

    if report3_payload is None:
        return ""

    mtd_table = report3_payload.get("mtd_channel_table")
    ytd_table = report3_payload.get("ytd_channel_table")

    ordered_labels = dashboard_report3_channel_order(mtd_table, ytd_table)
    mtd_table = dashboard_complete_report3_table(mtd_table, ordered_labels)
    ytd_table = dashboard_complete_report3_table(ytd_table, ordered_labels)

    return (
        '<div class="dashboard-report-section">'
        '<div class="dashboard-report-pair-grid">'
        f'{build_dashboard_report3_compact_table_html("Sales by Channel Monthly", mtd_table)}'
        f'{build_dashboard_report3_compact_table_html("Sales by Channel YTD", ytd_table)}'
        '</div>'
        '</div>'
    )



def dashboard_get_report4_payload() -> dict | None:
    return st.session_state.get("report4_payload")


def build_dashboard_report4_compact_table_html(title: str, df_table) -> str:
    """
    Ranking Clientes para Dashboard.

    Usa la vista ejecutiva ya construida en Reporte 4:
    Top 15 cliente por cliente + bloques resumen + Total Mexico.
    No recalcula ranking; solo imprime el payload existente con el formato compacto del Dashboard.
    """
    if df_table is None or df_table.empty:
        return (
            '<div class="dashboard-compact-block dashboard-clients-block">'
            f'<div class="dashboard-compact-title-box">{escape(title)}</div>'
            '<div class="dashboard-kpi-muted">Información no disponible.</div>'
            '</div>'
        )

    rows_html_parts: list[str] = []

    for _, row in df_table.iterrows():
        is_total = bool(row.get("__is_total__", False))
        is_grand_total = bool(row.get("__is_grand_total__", False))
        is_group_summary = bool(row.get("__is_group_summary__", False))

        row_class = ""
        if is_total or is_group_summary:
            row_class = ' class="dashboard-compact-total"'
        if is_grand_total:
            row_class = ' class="dashboard-compact-grand-total"'

        client_name = str(row.get("Client Name", "")).strip()
        client_code = str(row.get("Cliente", "")).strip()

        rows_html_parts.append(
            f'<tr{row_class}>'
            f'<td class="dashboard-compact-label dashboard-client-name">{escape(client_name)}</td>'
            f'<td class="dashboard-compact-code">{escape(client_code)}</td>'
            f'{dashboard_compact_td(row.get("Actual"), allow_blank=False)}'
            f'{dashboard_compact_td(row.get("Plan"), allow_blank=True)}'
            f'{dashboard_compact_td(row.get("PY"), allow_blank=True)}'
            f'{dashboard_compact_td(row.get("Var VS Plan"), allow_blank=True)}'
            f'{dashboard_compact_td(row.get("%Var VS Plan"), is_percent=True, allow_blank=True)}'
            f'{dashboard_compact_td(row.get("Var VS PY"), allow_blank=True)}'
            f'{dashboard_compact_td(row.get("%Var VS PY"), is_percent=True, allow_blank=True)}'
            '</tr>'
        )

    rows_html = "".join(rows_html_parts)

    return (
        '<div class="dashboard-compact-block dashboard-clients-block">'
        f'<div class="dashboard-compact-title-box">{escape(title)}</div>'
        '<div class="dashboard-compact-table-wrap dashboard-clients-table-wrap">'
        '<table class="dashboard-compact-table dashboard-clients-table">'
        '<colgroup>'
        '<col class="dashboard-col-client-name">'
        '<col class="dashboard-col-client-code">'
        '<col class="dashboard-col-num">'
        '<col class="dashboard-col-num">'
        '<col class="dashboard-col-num">'
        '<col class="dashboard-col-num">'
        '<col class="dashboard-col-pct">'
        '<col class="dashboard-col-num">'
        '<col class="dashboard-col-pct">'
        '</colgroup>'
        '<thead>'
        '<tr>'
        '<th>Client Name</th>'
        '<th>Cliente</th>'
        '<th>Actual</th>'
        '<th>Plan</th>'
        '<th>PY</th>'
        '<th>Var vs Plan</th>'
        '<th>%Var vs Plan</th>'
        '<th>Var vs PY</th>'
        '<th>%Var vs PY</th>'
        '</tr>'
        '</thead>'
        '<tbody>'
        f'{rows_html}'
        '</tbody>'
        '</table>'
        '</div>'
        '</div>'
    )


def build_dashboard_report4_section_html() -> str:
    report4_payload = dashboard_get_report4_payload()

    if report4_payload is None:
        return ""

    mtd_table = report4_payload.get("mtd_top_clients_table")
    ytd_table = report4_payload.get("ytd_top_clients_table")

    return (
        '<div class="dashboard-report-section dashboard-report-clients-section">'
        '<div class="dashboard-report-pair-grid">'
        f'{build_dashboard_report4_compact_table_html("Ranking Clientes MTD", mtd_table)}'
        f'{build_dashboard_report4_compact_table_html("Ranking Clientes YTD", ytd_table)}'
        '</div>'
        '</div>'
    )


def build_dashboard_stage_one_html(payload: dict) -> str:
    latest_month = int(payload["latest_month"])
    latest_year = int(payload["latest_year"])

    month_label = get_dashboard_month_label_en(latest_month)
    currency_label = "$Kmxn" if get_currency_status_label() == "MXN" else "$Kusd"

    client_table = payload.get("client_table")
    bts_table = payload.get("bts_table")

    mtd_gsnr = dashboard_safe_get_row(client_table, "MTD")
    ytd_gsnr = dashboard_safe_get_row(client_table, "YTD")
    mtd_bts = dashboard_safe_get_row(bts_table, "MTD")
    ytd_bts = dashboard_safe_get_row(bts_table, "YTD")

    month_rows = (
        build_dashboard_metric_row(
            metric_name="GSNR",
            actual=None if mtd_gsnr is None else mtd_gsnr.get("Actual"),
            plan=None if mtd_gsnr is None else mtd_gsnr.get("Plan"),
            py=None if mtd_gsnr is None else mtd_gsnr.get("PY"),
            var_plan=None if mtd_gsnr is None else mtd_gsnr.get("Var VS Plan"),
            pct_var_plan=None if mtd_gsnr is None else mtd_gsnr.get("%Var VS Plan"),
            var_py=None if mtd_gsnr is None else mtd_gsnr.get("Var VS PY"),
            pct_var_py=None if mtd_gsnr is None else mtd_gsnr.get("%Var VS PY"),
            row_class="dashboard-gsnr-row",
        )
        + build_dashboard_achievement_row(mtd_gsnr)
        + build_dashboard_metric_row(
            metric_name=f"BTS ({month_label})",
            actual=None if mtd_bts is None else mtd_bts.get("Actual"),
            plan=None,
            py=None if mtd_bts is None else mtd_bts.get("PY"),
            var_plan=None,
            pct_var_plan=None,
            var_py=None if mtd_bts is None else mtd_bts.get("Var VS PY"),
            pct_var_py=None if mtd_bts is None else mtd_bts.get("%Var VS PY"),
            row_class="dashboard-bts-row",
        )
    )

    ytd_rows = (
        build_dashboard_metric_row(
            metric_name="GSNR",
            actual=None if ytd_gsnr is None else ytd_gsnr.get("Actual"),
            plan=None if ytd_gsnr is None else ytd_gsnr.get("Plan"),
            py=None if ytd_gsnr is None else ytd_gsnr.get("PY"),
            var_plan=None if ytd_gsnr is None else ytd_gsnr.get("Var VS Plan"),
            pct_var_plan=None if ytd_gsnr is None else ytd_gsnr.get("%Var VS Plan"),
            var_py=None if ytd_gsnr is None else ytd_gsnr.get("Var VS PY"),
            pct_var_py=None if ytd_gsnr is None else ytd_gsnr.get("%Var VS PY"),
            row_class="dashboard-gsnr-row",
        )
        + build_dashboard_achievement_row(ytd_gsnr)
        + build_dashboard_metric_row(
            metric_name=f"BTS (Oct-{month_label})",
            actual=None if ytd_bts is None else ytd_bts.get("Actual"),
            plan=None,
            py=None if ytd_bts is None else ytd_bts.get("PY"),
            var_plan=None,
            pct_var_plan=None,
            var_py=None if ytd_bts is None else ytd_bts.get("Var VS PY"),
            pct_var_py=None if ytd_bts is None else ytd_bts.get("%Var VS PY"),
            row_class="dashboard-bts-row",
        )
    )

    return (
        '<div class="dashboard-stage-card">'
        '<div style="display:flex; align-items:flex-start; justify-content:flex-start; margin:0 0 8px 0;">'
        '<table style="border-collapse:collapse; font-family:Segoe UI, Arial, sans-serif; font-size:15px; color:#1F2A44;">'
        '<tr>'
        '<td style="font-weight:800; color:#E60023; padding:0 20px 4px 0;">Month</td>'
        f'<td style="font-weight:700; padding:0 0 4px 0;">{escape(month_label)}</td>'
        '</tr>'
        '<tr>'
        '<td style="font-weight:800; color:#E60023; padding:0 20px 4px 0;">Year</td>'
        f'<td style="font-weight:700; padding:0 0 4px 0;">{escape(str(latest_year))}</td>'
        '</tr>'
        '</table>'
        '</div>'
        '<div class="dashboard-main-title-box">'
        '<div class="dashboard-main-title">Mexico Dashboard 2026</div>'
        '</div>'
        f'<div class="dashboard-currency-label">{escape(currency_label)}</div>'
        '<div class="dashboard-kpi-grid">'
        f'{build_dashboard_kpi_table_html("Sales Month", month_rows)}'
        f'{build_dashboard_kpi_table_html("Sales YTD", ytd_rows)}'
        '</div>'
        f'{build_dashboard_report1_section_html()}'
        f'{build_dashboard_report2_segment_section_html()}'
        f'{build_dashboard_report2_category_section_html()}'
        f'{build_dashboard_report3_section_html()}'
        f'{build_dashboard_report4_section_html()}'
        '</div>'
    )


def render_dashboard_dependency_box(missing_dependencies: list[str]) -> None:
    items_html = "".join(
        f"<li>{escape(message)}</li>"
        for message in missing_dependencies
    )

    st.markdown(
        (
            '<div class="dashboard-lock-box">'
            '<div class="dashboard-lock-title">Dashboard pendiente de cargar</div>'
            '<div class="dashboard-lock-text">'
            'Para cargar el Dashboard ejecutivo primero deben existir todos los insumos construidos:'
            f'<ul>{items_html}</ul>'
            '</div>'
            '</div>'
        ),
        unsafe_allow_html=True,
    )


def render_dashboard_view() -> None:
    st.markdown(build_dashboard_css_html(), unsafe_allow_html=True)

    st.markdown(
        '<div class="section-title">Dashboard</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        styles.build_info_box(
            """
            <b>Objetivo de esta vista:</b><br>
            Mostrar el Dashboard ejecutivo consolidado con KPIs y reportes principales
            construidos previamente en la app.
            """
        ),
        unsafe_allow_html=True,
    )

    st.button(
        "Cargar Dashboard",
        on_click=load_dashboard_view_state,
        use_container_width=True,
    )

    if not st.session_state.get("dashboard_loaded", False):
        st.info("Da clic en Cargar Dashboard para validar los insumos y mostrar la vista ejecutiva.")
        return

    missing_dependencies = get_dashboard_missing_dependencies()

    if missing_dependencies:
        render_dashboard_dependency_box(missing_dependencies)
        return

    payload = st.session_state.get("mtd_payload")

    if payload is None:
        st.info("Aún no existe información de Base MTD para el Dashboard.")
        return

    st.markdown(
        '<div class="base-mtd-compact-note">Los valores se muestran en miles. Los negativos se muestran en rojo; los valores positivos se mantienen neutros.</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        build_dashboard_stage_one_html(payload),
        unsafe_allow_html=True,
    )

# =========================================================
# 18. VISTAS PRINCIPALES
# =========================================================
def render_home_view() -> None:
    home_box_html = styles.build_info_box(
        """
        <b>Etapa actual:</b><br>
        Reestructura de carga para ventas, plan por cliente y plan por SKU,
        más incorporación de Reporte 1, Reporte 2, Reporte 3 y Reporte 4 ejecutivo.
        """
    )
    st.markdown(home_box_html, unsafe_allow_html=True)

    render_persistent_data_status()

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            styles.build_info_card(
                "Módulos base",
                "8",
                "config.py, styles.py, data_loader.py, validators.py, "
                "data_processor.py, exports.py, charts.py y app.py",
            ),
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            styles.build_info_card(
                "Estatus",
                "Activo",
                "La app ya carga ventas y planes, procesa la base y muestra Reportes 1, 2, 3 y 4",
            ),
            unsafe_allow_html=True,
        )

    with col3:
        st.markdown(
            styles.build_info_card(
                "Siguiente etapa",
                "Refinamiento visual",
                "Ajustes finales de diseño, alertas y validación ejecutiva",
            ),
            unsafe_allow_html=True,
        )

    st.markdown(
        '<div class="section-title">Resumen de la etapa</div>',
        unsafe_allow_html=True,
    )

    st.write(
        """
        En esta versión ya contamos con:

        - configuración centralizada
        - estilo visual corporativo
        - login temporal de desarrollo
        - navegación base
        - carga de archivo de ventas
        - carga de plan por cliente
        - carga de plan por SKU
        - persistencia de archivos en sesión
        - procesamiento inicial de la base de ventas
        - construcción inicial de la Base MTD
        - primer reporte ejecutivo MTD / YTD por Canal Corporativo
        - segundo reporte ejecutivo MTD / YTD por Segmento, Región y Categoría
        - tercer reporte ejecutivo MTD / YTD por Channel
        - cuarto reporte ejecutivo MTD / YTD por Top 15 clientes
        - exportación individual por reporte en Excel
        - exportación global de reportes en Excel

        En la siguiente etapa se continuará con el refinamiento visual final
        y la corrección de alertas en pantalla.
        """
    )


def render_upload_view() -> None:
    if not is_admin_user():
        st.markdown(
            '<div class="section-title">Acceso restringido</div>',
            unsafe_allow_html=True,
        )
        st.warning("Esta sección solo está disponible para usuarios administradores.")
        render_persistent_data_status()
        return

    # Refuerzo para Streamlit Cloud:
    # si la app acaba de despertar/reiniciar y la sesión está vacía,
    # se restaura aquí la última carga guardada antes de pintar las tarjetas.
    ensure_persistent_data_loaded_if_available(show_message=False)

    st.markdown(
        '<div class="section-title">Carga de datos</div>',
        unsafe_allow_html=True,
    )

    upload_box_html = styles.build_info_box(
        """
        <b>Objetivo de esta etapa:</b><br>
        Cargar correctamente el archivo corporativo de ventas y planes,
        manteniendo persistencia, validaciones y vistas previas por hoja.
        """
    )
    st.markdown(upload_box_html, unsafe_allow_html=True)

    # =====================================================
    # RESUMEN DEL ESTADO DE CARGA
    # =====================================================
    st.markdown(
        '<div class="base-mtd-section-heading">Resumen del estado de carga</div>',
        unsafe_allow_html=True,
    )

    sales_loaded = st.session_state.get("df_sales") is not None
    plan_client_loaded = st.session_state.get("df_plan_client") is not None
    plan_sku_loaded = st.session_state.get("df_plan_sku") is not None

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            styles.build_info_card(
                "Ventas",
                "Cargado" if sales_loaded else "Pendiente",
                "Hoja BASE SAP del archivo corporativo",
            ),
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            styles.build_info_card(
                "Plan Cliente",
                "Cargado" if plan_client_loaded else "Pendiente",
                "Hoja Plan2026 by Client",
            ),
            unsafe_allow_html=True,
        )

    with col3:
        st.markdown(
            styles.build_info_card(
                "Plan SKU",
                "Cargado" if plan_sku_loaded else "Pendiente",
                "Hoja Plan2026 by SKU",
            ),
            unsafe_allow_html=True,
        )

    st.markdown("---")

    # =====================================================
    # CARGA AUTOMÁTICA DESDE SHAREPOINT / ONEDRIVE
    # BLOQUEADA TEMPORALMENTE
    # =====================================================
    # NOTA IMPORTANTE:
    # Esta funcionalidad se deja visible, pero SIN USO.
    # No se elimina la lógica interna para poder reactivarla en el futuro
    # si el equipo decide volver a usar la ruta sincronizada.
    #
    # Mientras esté bloqueada:
    # - el botón aparece deshabilitado
    # - no se puede hacer clic
    # - no se ejecuta load_synced_sharepoint_file_to_session()
    # - la app trabaja únicamente con carga manual del archivo corporativo
    # =====================================================
    st.markdown(
        '<div class="base-mtd-section-heading">Carga automática desde OneDrive / SharePoint</div>',
        unsafe_allow_html=True,
    )
    st.caption(
        "Función temporalmente deshabilitada. Actualmente la app trabaja únicamente "
        "con la carga manual del archivo corporativo."
    )

    st.button(
        getattr(
            config,
            "SYNCED_SHAREPOINT_BUTTON_LABEL",
            "Actualizar desde OneDrive / SharePoint",
        ),
        disabled=True,
        use_container_width=True,
        help=(
            "Función temporalmente deshabilitada. "
            "Actualmente la app trabaja solo con carga manual."
        ),
    )

    st.warning(
        "La carga automática desde OneDrive/SharePoint está temporalmente deshabilitada. "
        "Usa la carga manual del archivo corporativo."
    )

    st.markdown("---")

    # =====================================================
    # CARGA MANUAL ÚNICA DEL ARCHIVO CORPORATIVO
    # =====================================================
    st.markdown(
        '<div class="base-mtd-section-heading">Carga manual del archivo corporativo</div>',
        unsafe_allow_html=True,
    )
    st.caption(
        "Sube una sola vez el Excel corporativo. La app leerá internamente las hojas BASE SAP, "
        "Plan2026 by Client y Plan2026 by SKU."
    )

    uploaded_master_file = st.file_uploader(
        "Carga el archivo corporativo completo",
        type=config.ALLOWED_FILE_TYPES,
        key=f"master_dashboard_file_{st.session_state.get('upload_reset_counter', 0)}",
    )

    if uploaded_master_file is not None:
        try:
            master_signature = f"{uploaded_master_file.name}|{len(uploaded_master_file.getvalue())}"

            if master_signature != st.session_state.get("master_upload_signature", ""):
                st.session_state["suppress_persistent_autoload"] = True

                with st.spinner("Leyendo archivo corporativo y separando hojas..."):
                    payload = data_loader.load_dashboard_excel_from_uploaded_file(uploaded_master_file)
                    df_sales = payload.get("df_sales")
                    df_plan_client = payload.get("df_plan_client")
                    df_plan_sku = payload.get("df_plan_sku")

                is_valid_sales, missing_sales = validators.validate_required_columns(
                    df_sales,
                    config.EXPECTED_COLUMNS_SALES,
                )
                is_valid_plan_client, missing_plan_client = validators.validate_required_columns(
                    df_plan_client,
                    config.EXPECTED_COLUMNS_PLAN_CLIENT,
                )
                is_valid_plan_sku, missing_plan_sku = validators.validate_required_columns(
                    df_plan_sku,
                    config.EXPECTED_COLUMNS_PLAN_SKU,
                )

                st.session_state["df_sales"] = df_sales
                st.session_state["df_plan_client"] = df_plan_client
                st.session_state["df_plan_sku"] = df_plan_sku

                st.session_state["sales_valid"] = is_valid_sales
                st.session_state["plan_client_valid"] = is_valid_plan_client
                st.session_state["plan_sku_valid"] = is_valid_plan_sku

                st.session_state["sales_missing_columns"] = missing_sales
                st.session_state["plan_client_missing_columns"] = missing_plan_client
                st.session_state["plan_sku_missing_columns"] = missing_plan_sku

                st.session_state["master_upload_signature"] = master_signature
                st.session_state["master_file_name"] = uploaded_master_file.name
                st.session_state["sales_file_name"] = f"{uploaded_master_file.name} | BASE SAP"
                st.session_state["plan_client_file_name"] = f"{uploaded_master_file.name} | Plan2026 by Client"
                st.session_state["plan_sku_file_name"] = f"{uploaded_master_file.name} | Plan2026 by SKU"

                st.session_state["df_processed_sales"] = None
                st.session_state["persistent_data_loaded"] = False
                st.session_state["persistent_data_metadata"] = None

                clear_report_payloads()

                if all([is_valid_sales, is_valid_plan_client, is_valid_plan_sku]):
                    st.success("Archivo corporativo cargado correctamente. Las tres hojas mínimas fueron validadas.")
                else:
                    st.warning(
                        "El archivo corporativo se cargó, pero alguna hoja no contiene las columnas mínimas esperadas. "
                        "Revisa las validaciones de cada bloque."
                    )

        except Exception as exc:
            st.error(f"{config.MSG_UPLOAD_ERROR} Detalle: {exc}")

    st.markdown("---")

    # =====================================================
    # VISTA PREVIA - ARCHIVO DE VENTAS
    # =====================================================
    st.markdown(
        '<div class="base-mtd-section-heading">Archivo de ventas</div>',
        unsafe_allow_html=True,
    )

    if st.session_state.get("df_sales") is not None:
        sales_missing = st.session_state.get("sales_missing_columns", [])
        render_file_validation_result(
            is_valid=st.session_state.get("sales_valid", False),
            missing_columns=sales_missing,
            success_message=config.MSG_VALIDATION_OK,
        )

        sales_file_name = st.session_state.get("sales_file_name", "Archivo cargado en sesión")
        st.caption(f"Archivo en sesión: {sales_file_name}")

        render_preview_expander(
            "Vista previa - Archivo de ventas",
            st.session_state.get("df_sales"),
            rows=10,
            convert_currency=False,
        )
    else:
        st.info("Aún no se ha cargado la hoja BASE SAP.")

    st.markdown("---")

    # =====================================================
    # VISTA PREVIA - PLAN POR CLIENTE
    # =====================================================
    st.markdown(
        '<div class="base-mtd-section-heading">Archivo de plan por cliente</div>',
        unsafe_allow_html=True,
    )

    if st.session_state.get("df_plan_client") is not None:
        plan_client_missing = st.session_state.get("plan_client_missing_columns", [])
        render_file_validation_result(
            is_valid=st.session_state.get("plan_client_valid", False),
            missing_columns=plan_client_missing,
            success_message=config.MSG_VALIDATION_OK,
        )

        plan_client_file_name = st.session_state.get("plan_client_file_name", "Archivo cargado en sesión")
        st.caption(f"Archivo en sesión: {plan_client_file_name}")

        render_preview_expander(
            "Vista previa - Plan2026 by Client",
            st.session_state.get("df_plan_client"),
            rows=10,
            convert_currency=False,
        )
    else:
        st.info("Aún no se ha cargado la hoja Plan2026 by Client.")

    st.markdown("---")

    # =====================================================
    # VISTA PREVIA - PLAN POR SKU
    # =====================================================
    st.markdown(
        '<div class="base-mtd-section-heading">Archivo de plan por SKU</div>',
        unsafe_allow_html=True,
    )

    if st.session_state.get("df_plan_sku") is not None:
        plan_sku_missing = st.session_state.get("plan_sku_missing_columns", [])
        render_file_validation_result(
            is_valid=st.session_state.get("plan_sku_valid", False),
            missing_columns=plan_sku_missing,
            success_message=config.MSG_VALIDATION_OK,
        )

        plan_sku_file_name = st.session_state.get("plan_sku_file_name", "Archivo cargado en sesión")
        st.caption(f"Archivo en sesión: {plan_sku_file_name}")

        render_preview_expander(
            "Vista previa - Plan2026 by SKU",
            st.session_state.get("df_plan_sku"),
            rows=10,
            convert_currency=False,
        )
    else:
        st.info("Aún no se ha cargado la hoja Plan2026 by SKU.")

    st.markdown("---")

    # =====================================================
    # GUARDAR CARGA PARA VIEWERS
    # =====================================================
    st.markdown(
        '<div class="base-mtd-section-heading">Guardar carga para usuarios viewer</div>',
        unsafe_allow_html=True,
    )

    sales_loaded = st.session_state.get("df_sales") is not None
    plan_client_loaded = st.session_state.get("df_plan_client") is not None
    plan_sku_loaded = st.session_state.get("df_plan_sku") is not None

    if sales_loaded and plan_client_loaded and plan_sku_loaded:
        st.info(
            "Cuando las tres hojas estén validadas, guarda esta carga para que los usuarios viewer puedan consultar la app sin subir archivos."
        )
        st.button(
            "Guardar carga administrativa para viewers",
            on_click=save_current_data_for_viewers,
            use_container_width=True,
        )
    else:
        st.caption("Carga el archivo corporativo completo para habilitar el guardado administrativo.")

    # =====================================================
    # LIMPIEZA DE SESIÓN Y CARGA GUARDADA
    # =====================================================
    st.markdown("---")
    st.markdown(
        '<div class="base-mtd-section-heading">Limpieza de carga guardada</div>',
        unsafe_allow_html=True,
    )
    st.caption(
        "Usa estos botones si Streamlit Cloud sigue mostrando datos anteriores "
        "o si necesitas empezar una carga completamente desde cero."
    )

    col_clear_session, col_clear_persistent = st.columns(2)

    with col_clear_session:
        st.button(
            "Limpiar sesión actual",
            on_click=clear_current_session_data,
            use_container_width=True,
        )

    with col_clear_persistent:
        st.button(
            "Borrar carga guardada para viewers",
            on_click=delete_persistent_data,
            use_container_width=True,
        )

    render_persistent_data_status()

def render_overview_view() -> None:
    st.markdown(
        '<div class="section-title">Visión general</div>',
        unsafe_allow_html=True,
    )

    overview_box_html = styles.build_info_box(
        """
        <b>Objetivo de esta etapa:</b><br>
        Limpiar datos de ventas, transformar la columna Periodo,
        respetar el GSNR existente de BASE SAP y calcular Gross Margin.
        """
    )
    st.markdown(overview_box_html, unsafe_allow_html=True)

    # Botón único de procesamiento, sin crear un apartado adicional.
    st.button(
        "Procesar base de ventas",
        on_click=run_sales_processing,
        use_container_width=True,
    )

    st.markdown(
        '<div class="base-mtd-section-heading">Resumen de la base procesada</div>',
        unsafe_allow_html=True,
    )

    render_processed_data_summary()

    df_processed = st.session_state.get("df_processed_sales")

    st.markdown(
        '<div class="base-mtd-section-heading">Tendencia Mensual</div>',
        unsafe_allow_html=True,
    )

    trend_fig = charts.build_monthly_gsnr_trend_chart(
        df_processed_sales=df_processed,
        currency_mode=get_active_currency_mode(),
        exchange_rate=get_active_exchange_rate(),
    )

    if trend_fig is not None:
        st.plotly_chart(trend_fig, use_container_width=True)
    else:
        st.info("No hay información suficiente para construir la tendencia mensual.")

    st.markdown(
        '<div class="base-mtd-section-heading">Vista previa de la base procesada</div>',
        unsafe_allow_html=True,
    )

    if df_processed is not None and not df_processed.empty:
        render_preview_expander(
            "Vista previa - Base procesada",
            remove_private_processed_columns(df_processed),
            rows=20,
            convert_currency=True,
        )
    else:
        st.info("Aún no se ha procesado ninguna base.")

    # Única línea divisoria de esta vista, para separar la vista previa
    # de la validación visual de columnas clave.
    st.markdown("---")

    st.markdown(
        '<div class="base-mtd-section-heading">Validación visual de columnas clave</div>',
        unsafe_allow_html=True,
    )

    if df_processed is not None and not df_processed.empty:
        columns_to_show = [
            "Periodo",
            config.COL_YEAR,
            config.COL_MONTH,
            "Material",
            config.COL_GSNR,
        ]

        available_columns = [col for col in columns_to_show if col in df_processed.columns]

        render_preview_expander(
            "Vista previa - Columnas clave",
            remove_private_processed_columns(df_processed[available_columns]),
            rows=20,
            convert_currency=True,
        )
    else:
        st.info("No hay columnas procesadas para mostrar todavía.")


def render_mtd_base_view() -> None:
    st.markdown(
        '<div class="section-title">Base MTD</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        styles.build_info_box(
            """
            <b>Objetivo de esta etapa:</b><br>
            Construir comparativos generales MTD / YTD para Plan2026 by Client
            y Plan2026 by SKU con base en REAL (BASE SAP).
            """
        ),
        unsafe_allow_html=True,
    )

    payload = st.session_state.get("mtd_payload")

    # =====================================================
    # Encabezado compacto: construcción inicial + filtros
    # =====================================================
    if payload is None:
        st.markdown(
            '<div class="base-mtd-section-heading">Construir Base MTD</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<div class="base-mtd-compact-note">Al construir por primera vez, se toma el último periodo disponible de BASE SAP.</div>',
            unsafe_allow_html=True,
        )

        st.button(
            "Construir Base MTD",
            on_click=run_mtd_build,
            use_container_width=True,
        )

        st.info("Aún no se ha construido la Base MTD.")
        return

    report_title = build_report_context_title(
        "Base MTD",
        payload["latest_year"],
        payload["latest_month"],
    )

    st.markdown(
        f"""
        <div class="base-mtd-section-heading">{escape(report_title)}</div>
        <div class="base-mtd-compact-note">
            Ajusta el Año y Mes de corte para recalcular MTD, YTD y BTS.
            El BTS respeta el ciclo octubre-agosto.
        </div>
        """,
        unsafe_allow_html=True,
    )

    years, latest_year, latest_month = get_available_year_month_options()

    if years:
        default_year = st.session_state.get("base_mtd_year", payload["latest_year"])
        if default_year not in years:
            default_year = latest_year

        year_index = years.index(default_year)

        filter_col_year, filter_col_month, filter_col_apply = st.columns(
            [1.1, 1.25, 0.95]
        )

        with filter_col_year:
            selected_year_mtd = st.selectbox(
                "Año",
                options=years,
                index=year_index,
                key="base_mtd_year",
            )

        available_months = get_available_months_for_year(selected_year_mtd)

        selected_month_mtd = None
        if available_months:
            default_month = st.session_state.get("base_mtd_month", payload["latest_month"])

            if selected_year_mtd == latest_year:
                fallback_month = latest_month
            else:
                fallback_month = max(available_months)

            if default_month not in available_months:
                default_month = fallback_month

            month_index = available_months.index(default_month)

            with filter_col_month:
                selected_month_mtd = st.selectbox(
                    "Mes de corte",
                    options=available_months,
                    index=month_index,
                    key="base_mtd_month",
                    format_func=get_month_label,
                )
        else:
            with filter_col_month:
                st.warning("Sin meses disponibles")

        with filter_col_apply:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button(
                "Aplicar",
                key="btn_base_mtd_period_filter",
                use_container_width=True,
                disabled=selected_month_mtd is None,
            ):
                run_mtd_build(
                    selected_year=selected_year_mtd,
                    selected_month=selected_month_mtd,
                )

    else:
        st.info("Primero necesitas procesar la base de ventas para habilitar los filtros de Año y Mes.")

    payload = st.session_state.get("mtd_payload")

    # =====================================================
    # Resumen ejecutivo con tarjetas nuevas
    # =====================================================
    render_mtd_base_summary()

    payload = st.session_state.get("mtd_payload")

    if payload is None:
        st.info("Aún no se ha construido la Base MTD.")
        return

    report_title = build_report_context_title(
        "Base MTD",
        payload["latest_year"],
        payload["latest_month"],
    )

    base_mtd_bytes = exports.build_base_mtd_excel_bytes(
        client_table_df=convert_report_table_for_export(payload["client_table"]),
        sku_table_df=convert_report_table_for_export(payload["sku_table"]),
        bts_table_df=convert_report_table_for_export(payload["bts_table"]),
        plan_summary_df=convert_report_table_for_export(
            build_base_mtd_plan_summary_export_df(payload.get("plan_summary"))
        ),
        report_title=report_title,
        sheet_name=getattr(config, "EXPORT_SHEET_BASE_MTD", "Base MTD"),
    )

    # =====================================================
    # Comparativos: se conserva la tabla original, solo se
    # compacta el encabezado y se integra la descarga.
    # =====================================================
    st.markdown(
        '<div class="base-mtd-section-heading">Comparativos MTD / YTD</div>',
        unsafe_allow_html=True,
    )

    legend_col, download_col = st.columns([10, 1.1])

    with legend_col:
        st.markdown(build_mtd_legend_html(), unsafe_allow_html=True)

    with download_col:
        download_label = getattr(config, "EXPORT_BASE_MTD_HELP", "Descargar Base MTD")
        render_icon_download_button(
            data=base_mtd_bytes,
            file_name=build_excel_filename(
                getattr(config, "EXPORT_BASE_MTD_FILE_BASE", "base_mtd"),
                payload["latest_year"],
                payload["latest_month"],
            ),
            key="download_base_mtd_icon",
            help_text=download_label,
        )

    st.markdown(
        build_horizontal_plan_table_html(
            build_report_context_title(
                "Plan2026 by Client",
                payload["latest_year"],
                payload["latest_month"],
            ),
            payload["client_table"],
            "client",
        ),
        unsafe_allow_html=True,
    )

    st.markdown(
        build_horizontal_plan_table_html(
            build_report_context_title(
                "Plan2026 by SKU",
                payload["latest_year"],
                payload["latest_month"],
            ),
            payload["sku_table"],
            "sku",
        ),
        unsafe_allow_html=True,
    )

    st.markdown("---")

    st.markdown(
        '<div class="base-mtd-section-heading">Comparativo BTS</div>',
        unsafe_allow_html=True,
    )

    st.caption(
        "En BTS se compara MTD y YTD contra PY al mismo corte. "
        "La lógica considera solo Barrilito y respeta el ciclo Back To School de octubre a agosto."
    )

    st.markdown(
        build_bts_table_html(
            build_report_context_title(
                "BTS MTD / YTD vs PY comparable",
                payload["latest_year"],
                payload["latest_month"],
            ),
            payload["bts_table"],
        ),
        unsafe_allow_html=True,
    )


def render_placeholder_view(section_name: str) -> None:
    st.markdown(
        f'<div class="section-title">{section_name}</div>',
        unsafe_allow_html=True,
    )

    placeholder_box_html = styles.build_info_box(
        f"""
        <b>Sección en construcción:</b><br>
        La vista <code>{section_name}</code> quedará habilitada en etapas posteriores.
        """
    )
    st.markdown(placeholder_box_html, unsafe_allow_html=True)

# =========================================================
# 19. FLUJO PRINCIPAL
# =========================================================
def main() -> None:
    if not st.session_state["authenticated"]:
        render_login_screen()
        return

    # En localhost la sesión suele sobrevivir, pero en Streamlit Cloud puede
    # perderse por reboot/sleep. Por eso restauramos la última carga guardada
    # en cuanto el usuario entra, siempre que la sesión esté vacía.
    ensure_persistent_data_loaded_if_available(show_message=False)

    render_main_header()
    selected = render_sidebar()

    previous_section = st.session_state.get("__last_selected_section")
    if previous_section is not None and previous_section != selected:
        # Evita que avisos de una sección anterior aparezcan en otra pestaña.
        st.session_state["mensaje_exito"] = None
        st.session_state["mensaje_warning"] = None
    st.session_state["__last_selected_section"] = selected

    render_global_alerts()

    if selected == "Inicio":
        render_home_view()
    elif selected == "Carga de datos":
        if is_admin_user():
            render_upload_view()
        else:
            render_home_view()
    elif selected == "Dashboard":
        render_dashboard_view()
    elif selected == "Visión general":
        render_overview_view()
    elif selected == "Oficina de ventas":
        render_report_1_view()
    elif selected == "Segmento y Categoría":
        render_report_2_view()
    elif selected == "Canal":
        render_report_3_view()
    elif selected == "Ranking Clientes":
        render_report_4_view()
    elif selected == "Base MTD":
        render_mtd_base_view()
    else:   
        render_placeholder_view(selected)

# =========================================================
# 20. EJECUCIÓN PRINCIPAL
# =========================================================
main()