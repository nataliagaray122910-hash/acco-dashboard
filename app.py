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
import time

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

# Streamlit marca como "stale" los elementos del render anterior mientras
# ejecuta un nuevo rerun. Como esta app tiene vistas pesadas (gráficas,
# reportes y dashboard), esos elementos podían permanecer visibles en gris
# durante la navegación y dar la impresión de que se mezclaban pestañas.
#
# Esta regla los oculta globalmente en cuanto Streamlit los marca como stale.
# No elimina session_state, filtros, payloads ni datos persistidos.
st.markdown(
    """
    <style>
    [data-stale="true"] {
        display: none !important;
        visibility: hidden !important;
        pointer-events: none !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

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

if "df_fcst_client" not in st.session_state:
    st.session_state["df_fcst_client"] = None

if "df_fcst_sku" not in st.session_state:
    st.session_state["df_fcst_sku"] = None

if "forecast_name" not in st.session_state:
    st.session_state["forecast_name"] = ""

if "forecast_client_sheet_name" not in st.session_state:
    st.session_state["forecast_client_sheet_name"] = ""

if "forecast_sku_sheet_name" not in st.session_state:
    st.session_state["forecast_sku_sheet_name"] = ""

if "sales_valid" not in st.session_state:
    st.session_state["sales_valid"] = False

if "plan_client_valid" not in st.session_state:
    st.session_state["plan_client_valid"] = False

if "plan_sku_valid" not in st.session_state:
    st.session_state["plan_sku_valid"] = False

if "fcst_client_valid" not in st.session_state:
    st.session_state["fcst_client_valid"] = False

if "fcst_sku_valid" not in st.session_state:
    st.session_state["fcst_sku_valid"] = False

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
REPORT_LOGIC_VERSION_R123 = "filters_applied_state_v20260813_04"
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

# La lógica del Ranking de Clientes se versiona por separado para invalidar
# payloads construidos antes de conservar clientes sin código y corregir O16/O18.
REPORT_LOGIC_VERSION_R4 = "ranking_search_clean_v20260813_02"
if st.session_state.get("report_logic_version_r4") != REPORT_LOGIC_VERSION_R4:
    st.session_state["report4_payload"] = None

    for _key in list(st.session_state.keys()):
        if _key.startswith("report4_"):
            st.session_state.pop(_key, None)

    st.session_state.pop("__global_export_signature", None)
    st.session_state.pop("__global_export_bytes", None)
    st.session_state["report_logic_version_r4"] = REPORT_LOGIC_VERSION_R4

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
    # Regla global de visualización para reportes:
    # valores inexistentes o cero se muestran como guion para dejar claro
    # que no hay registro, sin aparentar un error del programa.
    if is_blank_number(value):
        return "-"

    numeric_value = float(value)

    if is_percent:
        if abs(numeric_value) < 1e-12:
            return "-"
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
            "Fcst",
            "PY",
            "Var VS Plan",
            "Var VS Fcst",
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
        monetary_columns=["Actual", "Plan", "Fcst", "PY", "Var VS Plan", "Var VS Fcst", "Var VS PY"],
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
# 4.2.1 PERSISTENCIA DE ESTADO ENTRE VISTAS
# =========================================================
VIEW_STATE_KEYS_TO_PRESERVE = (
    "base_mtd_year",
    "base_mtd_month",
    "report1_without_kens_year",
    "report1_without_kens_month",
    "report2_segment_year",
    "report2_segment_month",
    "report2_category_year",
    "report2_category_month",
    "report3_channel_year",
    "report3_channel_month",
    "report4_clients_year",
    "report4_clients_month",
)


def preserve_view_state_across_navigation() -> None:
    """
    Conserva selecciones de Año/Mes aunque el widget no se renderice
    temporalmente porque el usuario cambió de sección.

    Los payloads, filtros aplicados y bases ya viven en st.session_state;
    esta función refuerza únicamente los estados de widgets que Streamlit
    podría limpiar al dejar de mostrarlos durante una navegación.
    """
    for key in VIEW_STATE_KEYS_TO_PRESERVE:
        if key in st.session_state:
            st.session_state[key] = st.session_state[key]


# =========================================================

# =========================================================
# 4.3 INDICADOR GENERAL DE PROCESOS
# =========================================================
def execute_with_status(title: str, action) -> bool:
    """
    Ejecuta una acción pesada mostrando etapas reales.

    El callback acepta el formato usado por data_loader.py,
    data_processor.py, persistence.py y exports.py:
        progress_callback(message=..., step=..., total_steps=...)
    """
    started_at = time.perf_counter()

    with st.status(title, expanded=True) as status_box:
        def progress(
            message: str,
            step: int | None = None,
            total_steps: int | None = None,
            **_,
        ) -> None:
            if step is not None and total_steps is not None:
                status_box.write(
                    f"**Etapa {int(step)} de {int(total_steps)}:** {message}"
                )
            else:
                status_box.write(str(message))

        try:
            result = bool(action(progress))
        except Exception as exc:
            result = False
            set_error_message(f"Ocurrió un error inesperado. Detalle: {exc}")

        elapsed = time.perf_counter() - started_at

        if result:
            status_box.update(
                label=f"Proceso completado en {elapsed:.1f} segundos",
                state="complete",
                expanded=False,
            )
        else:
            status_box.update(
                label=f"El proceso no pudo completarse · {elapsed:.1f} segundos",
                state="error",
                expanded=True,
            )

    return result


def execute_initial_data_loading(action) -> bool:
    """
    Indicador amigable para la preparación automática al entrar a la app.

    A diferencia de execute_with_status(), no muestra etapas técnicas ni
    callbacks de procesamiento. El usuario solo ve que la información se
    está preparando y, al terminar, el aviso desaparece.
    """
    loading_placeholder = st.empty()

    loading_placeholder.markdown(
        styles.build_initial_loading_html(
            title="Cargando información, espere un momento...",
            subtitle=(
                "Estamos preparando la información más reciente para que "
                "puedas consultar e interactuar con los reportes."
            ),
        ),
        unsafe_allow_html=True,
    )

    try:
        result = bool(action())
    except Exception as exc:
        result = False
        set_error_message(f"Ocurrió un error inesperado. Detalle: {exc}")
    finally:
        loading_placeholder.empty()

    return result


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


def delete_persistent_data(progress=None) -> bool:
    """
    Borra la carga administrativa guardada para viewers y limpia datos calculados
    de la sesión actual.
    """
    try:
        persistence.delete_dashboard_payload(progress_callback=progress)

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
            "df_fcst_client": None,
            "df_fcst_sku": None,
            "forecast_name": "",
            "forecast_client_sheet_name": "",
            "forecast_sku_sheet_name": "",
            "df_processed_sales": None,
            "sales_valid": False,
            "plan_client_valid": False,
            "plan_sku_valid": False,
            "fcst_client_valid": False,
            "fcst_sku_valid": False,
            "sales_missing_columns": [],
            "plan_client_missing_columns": [],
            "plan_sku_missing_columns": [],
            "fcst_client_missing_columns": [],
            "fcst_sku_missing_columns": [],
            "sales_file_name": "",
            "plan_client_file_name": "",
            "plan_sku_file_name": "",
            "fcst_client_file_name": "",
            "fcst_sku_file_name": "",
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

    st.session_state.pop("__global_export_signature", None)
    st.session_state.pop("__global_export_bytes", None)


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
        "fcst_client_file_name": st.session_state.get("fcst_client_file_name", "Forecast by Client"),
        "fcst_sku_file_name": st.session_state.get("fcst_sku_file_name", "Forecast by SKU"),
        "forecast_name": st.session_state.get("forecast_name", ""),
        "forecast_client_sheet_name": st.session_state.get("forecast_client_sheet_name", ""),
        "forecast_sku_sheet_name": st.session_state.get("forecast_sku_sheet_name", ""),
    }


def save_current_data_for_viewers(progress=None) -> bool:
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
            st.session_state.get("df_fcst_client") is not None,
            st.session_state.get("df_fcst_sku") is not None,
        ]
    )

    required_data_valid = all(
        [
            st.session_state.get("sales_valid", False),
            st.session_state.get("plan_client_valid", False),
            st.session_state.get("plan_sku_valid", False),
            st.session_state.get("fcst_client_valid", False),
            st.session_state.get("fcst_sku_valid", False),
        ]
    )

    if not required_data_loaded or not required_data_valid:
        set_warning_message(
            "Para guardar la carga administrativa, primero deben estar cargadas y validadas las cinco hojas funcionales."
        )
        return False

    metadata = build_persistent_metadata()

    payload = {
        "metadata": metadata,
        "payload_version": "viewer_raw_inputs_with_forecast_v4",
        "df_sales": st.session_state.get("df_sales"),
        "df_plan_client": st.session_state.get("df_plan_client"),
        "df_plan_sku": st.session_state.get("df_plan_sku"),
        "df_fcst_client": st.session_state.get("df_fcst_client"),
        "df_fcst_sku": st.session_state.get("df_fcst_sku"),
        "forecast_name": st.session_state.get("forecast_name", ""),
        "forecast_client_sheet_name": st.session_state.get("forecast_client_sheet_name", ""),
        "forecast_sku_sheet_name": st.session_state.get("forecast_sku_sheet_name", ""),
        # IMPORTANTE:
        # No se guarda df_processed_sales en la carga compartida.
        # Cada viewer debe procesar ventas en su propia sesión.
        "sales_valid": st.session_state.get("sales_valid", False),
        "plan_client_valid": st.session_state.get("plan_client_valid", False),
        "plan_sku_valid": st.session_state.get("plan_sku_valid", False),
        "fcst_client_valid": st.session_state.get("fcst_client_valid", False),
        "fcst_sku_valid": st.session_state.get("fcst_sku_valid", False),
        "sales_missing_columns": st.session_state.get("sales_missing_columns", []),
        "plan_client_missing_columns": st.session_state.get("plan_client_missing_columns", []),
        "plan_sku_missing_columns": st.session_state.get("plan_sku_missing_columns", []),
        "fcst_client_missing_columns": st.session_state.get("fcst_client_missing_columns", []),
        "fcst_sku_missing_columns": st.session_state.get("fcst_sku_missing_columns", []),
        "sales_file_name": st.session_state.get("sales_file_name", "Archivo cargado por administrador"),
        "plan_client_file_name": st.session_state.get("plan_client_file_name", "Archivo cargado por administrador"),
        "plan_sku_file_name": st.session_state.get("plan_sku_file_name", "Archivo cargado por administrador"),
        "fcst_client_file_name": st.session_state.get("fcst_client_file_name", "Archivo cargado por administrador"),
        "fcst_sku_file_name": st.session_state.get("fcst_sku_file_name", "Archivo cargado por administrador"),
    }

    try:
        persistence.save_dashboard_payload(payload, progress_callback=progress)

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
        df_fcst_client = payload.get("df_fcst_client")
        df_fcst_sku = payload.get("df_fcst_sku")

        if (
            df_sales is None
            or df_plan_client is None
            or df_plan_sku is None
            or df_fcst_client is None
            or df_fcst_sku is None
        ):
            # Payloads anteriores a la incorporación de Forecast no se restauran
            # como carga completa, porque ya no contienen las cinco hojas requeridas.
            return False

        st.session_state["df_sales"] = df_sales
        st.session_state["df_plan_client"] = df_plan_client
        st.session_state["df_plan_sku"] = df_plan_sku
        st.session_state["df_fcst_client"] = df_fcst_client
        st.session_state["df_fcst_sku"] = df_fcst_sku
        st.session_state["forecast_name"] = payload.get("forecast_name", "")
        st.session_state["forecast_client_sheet_name"] = payload.get("forecast_client_sheet_name", "")
        st.session_state["forecast_sku_sheet_name"] = payload.get("forecast_sku_sheet_name", "")

        # IMPORTANTE:
        # La carga administrativa compartida solo trae las bases originales.
        # La base procesada, reportes y filtros se limpian para que cada viewer
        # viva el flujo completo en su propia sesión.
        clear_user_generated_work_state()

        st.session_state["sales_valid"] = payload.get("sales_valid", True)
        st.session_state["plan_client_valid"] = payload.get("plan_client_valid", True)
        st.session_state["plan_sku_valid"] = payload.get("plan_sku_valid", True)
        st.session_state["fcst_client_valid"] = payload.get("fcst_client_valid", True)
        st.session_state["fcst_sku_valid"] = payload.get("fcst_sku_valid", True)

        st.session_state["sales_missing_columns"] = payload.get("sales_missing_columns", [])
        st.session_state["plan_client_missing_columns"] = payload.get("plan_client_missing_columns", [])
        st.session_state["plan_sku_missing_columns"] = payload.get("plan_sku_missing_columns", [])
        st.session_state["fcst_client_missing_columns"] = payload.get("fcst_client_missing_columns", [])
        st.session_state["fcst_sku_missing_columns"] = payload.get("fcst_sku_missing_columns", [])

        st.session_state["sales_file_name"] = payload.get("sales_file_name", "Archivo cargado por administrador")
        st.session_state["plan_client_file_name"] = payload.get("plan_client_file_name", "Archivo cargado por administrador")
        st.session_state["plan_sku_file_name"] = payload.get("plan_sku_file_name", "Archivo cargado por administrador")
        st.session_state["fcst_client_file_name"] = payload.get("fcst_client_file_name", "Archivo cargado por administrador")
        st.session_state["fcst_sku_file_name"] = payload.get("fcst_sku_file_name", "Archivo cargado por administrador")

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
    """
    Renderiza el inicio de sesión.

    La validación se ejecuta únicamente cuando:
    - se presiona el botón "Iniciar sesión"; o
    - se presiona Enter dentro del formulario.

    Mostrar u ocultar la contraseña con el icono del ojo no ejecuta
    la validación ni permite entrar automáticamente.
    """
    st.markdown(
        styles.apply_login_background("assets/fondo.png"),
        unsafe_allow_html=True,
    )

    left_col, center_col, right_col = st.columns([1, 1.5, 1])

    with center_col:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown(styles.build_hero_section(), unsafe_allow_html=True)

        with st.form(
            key="login_form",
            clear_on_submit=False,
            enter_to_submit=True,
            border=False,
        ):
            st.text_input(
                "Usuario",
                key="input_user",
            )
            st.text_input(
                "Contraseña",
                type="password",
                key="input_password",
            )

            st.markdown("<br>", unsafe_allow_html=True)

            login_submitted = st.form_submit_button(
                "Iniciar sesión",
                use_container_width=True,
            )

        if login_submitted:
            check_login()
            if st.session_state.get("authenticated"):
                st.rerun()

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


def get_current_dashboard_export_tables() -> dict | None:
    """
    Reúne exactamente los insumos que alimentan la vista ejecutiva del Dashboard.

    La descarga individual y la hoja incluida en la descarga global utilizan
    las tablas completas del periodo activo, sin depender de filtros visuales.
    """
    mtd_payload = st.session_state.get("mtd_payload")
    report1_payload = st.session_state.get("report1_payload")
    report2_payload = st.session_state.get("report2_payload")
    report2_category_payload = st.session_state.get("report2_category_payload")
    report3_payload = st.session_state.get("report3_payload")
    report4_payload = st.session_state.get("report4_payload")

    required_payloads = [
        mtd_payload,
        report1_payload,
        report2_payload,
        report2_category_payload,
        report3_payload,
        report4_payload,
    ]
    if any(payload is None for payload in required_payloads):
        return None

    year = int(mtd_payload["latest_year"])
    month = int(mtd_payload["latest_month"])

    return {
        "report_title": build_report_context_title(
            "Mexico Dashboard 2026",
            year,
            month,
        ),
        "latest_year": year,
        "latest_month": month,
        "month_label": get_dashboard_month_label_en(month),
        "currency_label": "$Kmxn" if get_currency_status_label() == "MXN" else "$Kusd",
        "client_table": convert_report_table_for_export(mtd_payload["client_table"]),
        "bts_table": convert_report_table_for_export(mtd_payload["bts_table"]),
        "report1_mtd": convert_report_table_for_export(report1_payload["mtd_without_kens_table"]),
        "report1_ytd": convert_report_table_for_export(report1_payload["ytd_without_kens_table"]),
        "segment_mtd": convert_report_table_for_export(report2_payload["mtd_segment_region_table"]),
        "segment_ytd": convert_report_table_for_export(report2_payload["ytd_segment_region_table"]),
        "category_mtd": convert_report_table_for_export(report2_category_payload["mtd_category_table"]),
        "category_ytd": convert_report_table_for_export(report2_category_payload["ytd_category_table"]),
        "channel_mtd": convert_report_table_for_export(report3_payload["mtd_channel_table"]),
        "channel_ytd": convert_report_table_for_export(report3_payload["ytd_channel_table"]),
        "ranking_mtd": convert_report_table_for_export(report4_payload["mtd_top_clients_table"]),
        "ranking_ytd": convert_report_table_for_export(report4_payload["ytd_top_clients_table"]),
    }


def get_full_reports_export_bytes() -> bytes:
    """
    Genera la descarga global una sola vez por combinación de reportes/moneda.
    Evita reconstruir el Excel completo al cambiar de sección en el sidebar.
    """
    signature = (
        id(st.session_state.get("mtd_payload")),
        id(st.session_state.get("report1_payload")),
        id(st.session_state.get("report2_payload")),
        id(st.session_state.get("report2_category_payload")),
        id(st.session_state.get("report3_payload")),
        id(st.session_state.get("report4_payload")),
        bool(st.session_state.get("dashboard_loaded", False)),
        get_active_currency_mode(),
        get_normalized_exchange_rate_4(),
    )

    if st.session_state.get("__global_export_signature") == signature:
        cached_bytes = st.session_state.get("__global_export_bytes")
        if cached_bytes is not None:
            return cached_bytes

    base_mtd_tables = get_current_base_mtd_export_tables()
    report_1_tables = get_current_report_1_export_tables()
    report_2_segment_tables = get_current_report_2_segment_export_tables()
    report_2_category_tables = get_current_report_2_category_export_tables()
    report_3_tables = get_current_report_3_export_tables()
    report_4_tables = get_current_report_4_export_tables()
    dashboard_tables = get_current_dashboard_export_tables()

    export_bytes = exports.build_full_reports_excel_bytes(
        base_mtd_tables=base_mtd_tables,
        report_1_tables=report_1_tables,
        report_2_segment_tables=report_2_segment_tables,
        report_2_category_tables=report_2_category_tables,
        report_3_tables=report_3_tables,
        report_4_tables=report_4_tables,
        dashboard_tables=dashboard_tables,
    )

    st.session_state["__global_export_signature"] = signature
    st.session_state["__global_export_bytes"] = export_bytes
    return export_bytes

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
            key="main_navigation",
        )

        # Los avisos pertenecen a la vista donde fueron generados.
        # Al cambiar de sección se eliminan para que un error de Ranking no
        # aparezca posteriormente en Category, Canal u otra pestaña.
        previous_section = st.session_state.get("__active_dashboard_section__")
        if previous_section is not None and previous_section != selected_option:
            st.session_state["mensaje_exito"] = None
            st.session_state["mensaje_error"] = None
            st.session_state["mensaje_warning"] = None

        st.session_state["__active_dashboard_section__"] = selected_option

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
                get_current_dashboard_export_tables() is not None,
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
        st.markdown(styles.build_project_progress_html(), unsafe_allow_html=True)

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
            "La información de ventas todavía no está disponible para habilitar los filtros de Año y Mes."
        )
        return None, None

    # Inicializa/corrige el estado ANTES de crear los widgets.
    # Así evitamos combinar un valor por `index=` con otro valor ya presente
    # en st.session_state, que es lo que genera el warning amarillo de Streamlit.
    current_year = st.session_state.get(year_key, latest_year)
    if current_year not in years:
        current_year = latest_year
    st.session_state[year_key] = current_year

    col1, col2 = st.columns(2)

    with col1:
        selected_year = st.selectbox(
            "Año",
            options=years,
            key=year_key,
        )

    available_months = get_available_months_for_year(selected_year)

    if not available_months:
        st.warning("No hay meses disponibles para el año seleccionado.")
        return selected_year, None

    current_month = st.session_state.get(month_key)

    if selected_year == latest_year:
        fallback_month = latest_month
    else:
        fallback_month = max(available_months)

    if current_month not in available_months:
        current_month = fallback_month
    st.session_state[month_key] = current_month

    with col2:
        selected_month = st.selectbox(
            "Mes de corte",
            options=available_months,
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
def run_sales_processing(progress=None) -> bool:
    df_sales = st.session_state.get("df_sales")

    if df_sales is None:
        set_error_message(config.MSG_PROCESSING_MISSING_FILES)
        return False

    is_ready, missing_columns = validators.validate_dataframe_for_processing(
        df_sales,
        config.REQUIRED_COLUMNS_SALES_PROCESS,
    )

    if not is_ready:
        set_error_message(config.MSG_VALIDATION_FAIL)
        set_warning_message(
            f"Columnas faltantes para procesar ventas: {', '.join(missing_columns)}"
        )
        return False

    try:
        df_processed = data_processor.process_sales_data(
            df_sales,
            progress_callback=progress,
        )
        st.session_state["df_processed_sales"] = df_processed
        clear_report_payloads()
        set_success_message(config.MSG_PROCESSING_SUCCESS)
        return True
    except Exception as exc:
        set_error_message(f"{config.MSG_PROCESSING_ERROR} Detalle: {exc}")
        return False


def ensure_sales_processed_automatically(show_status: bool = True) -> bool:
    """
    Procesa BASE SAP automáticamente cuando ya existe una carga válida
    y la sesión todavía no tiene df_processed_sales.

    Experiencia de usuario:
    - No reprocesa en cada rerun.
    - En la preparación automática inicial NO muestra etapas técnicas.
    - El aviso amigable desaparece al terminar y la vista continúa normalmente.
    """
    df_sales = st.session_state.get("df_sales")
    df_processed = st.session_state.get("df_processed_sales")

    if df_sales is None:
        return False

    if df_processed is not None and not getattr(df_processed, "empty", False):
        return True

    if not st.session_state.get("sales_valid", False):
        return False

    if show_status:
        result = execute_initial_data_loading(
            lambda: run_sales_processing(progress=None)
        )
    else:
        result = run_sales_processing(progress=None)

    # El procesamiento fue automático: no mostramos el mensaje técnico
    # "Procesamiento completado correctamente" después de entrar.
    if result and st.session_state.get("mensaje_exito") == config.MSG_PROCESSING_SUCCESS:
        st.session_state["mensaje_exito"] = None

    return result

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
    progress=None,
) -> bool:
    df_processed_sales = st.session_state.get("df_processed_sales")
    df_plan_client = st.session_state.get("df_plan_client")
    df_plan_sku = st.session_state.get("df_plan_sku")

    if (
        df_processed_sales is None
        or df_plan_client is None
        or df_plan_sku is None
    ):
        set_error_message(config.MSG_MTD_BUILD_MISSING_FILES)
        return False
    try:
        payload = data_processor.build_mtd_payload(
            df_processed_sales,
            df_plan_client,
            df_plan_sku,
            selected_year=selected_year,
            selected_month=selected_month,
            progress_callback=progress,
        )
        st.session_state["mtd_payload"] = payload
        st.session_state["df_mtd_base"] = None
        set_success_message(config.MSG_MTD_BUILD_SUCCESS)
        return True
    except Exception as exc:
        set_error_message(f"{config.MSG_MTD_BUILD_ERROR} Detalle: {exc}")
        return False


def render_mtd_base_summary() -> None:
    payload = st.session_state.get("mtd_payload")

    if payload is None:
        st.info("Todavía no existe una Base MTD construida.")
        return

    latest_month = payload["latest_month"]
    latest_year = payload["latest_year"]
    summary = payload["summary"]
    plan_summary = payload["plan_summary"]
    fcst_summary = payload.get("fcst_summary", {})
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

    # 8 KPIs: Actual, Plan, Forecast y BTS.
    row1 = st.columns(4)
    row2 = st.columns(4)

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

    with row1[3]:
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

    with row2[0]:
        st.markdown(
            styles.build_base_mtd_kpi_card(
                title=f"MTD FCST TOTAL ({get_currency_kpi_suffix()})",
                value=format_monetary_value(summary.get("mtd_fcst_total_k", 0.0) * 1000),
                description="Forecast del mes de corte seleccionado.",
                icon="F",
                color="pink",
            ),
            unsafe_allow_html=True,
        )

    with row2[1]:
        st.markdown(
            styles.build_base_mtd_kpi_card(
                title=f"YTD FCST TOTAL ({get_currency_kpi_suffix()})",
                value=format_monetary_value(summary.get("ytd_fcst_total_k", 0.0) * 1000),
                description="Forecast acumulado de enero al mes de corte.",
                icon="Σ",
                color="pink",
            ),
            unsafe_allow_html=True,
        )

    with row2[2]:
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

    with row2[3]:
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

    # Validaciones existentes de Plan.
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

    # Validaciones nuevas de Forecast Cliente vs Forecast SKU.
    if fcst_summary:
        if fcst_summary.get("mtd_fcst_match", False):
            st.success("Validación MTD Forecast: Forecast Cliente y Forecast SKU coinciden.")
        else:
            st.warning(
                "Validación MTD Forecast: Forecast Cliente y Forecast SKU no coinciden. "
                f"Diferencia detectada: {round(convert_monetary_value(fcst_summary.get('mtd_fcst_diff', 0.0)) / 1000):,}"
            )

        if fcst_summary.get("ytd_fcst_match", False):
            st.success("Validación YTD Forecast: Forecast Cliente y Forecast SKU coinciden.")
        else:
            st.warning(
                "Validación YTD Forecast: Forecast Cliente y Forecast SKU no coinciden. "
                f"Diferencia detectada: {round(convert_monetary_value(fcst_summary.get('ytd_fcst_diff', 0.0)) / 1000):,}"
            )

def format_table_value(value: float, is_percent: bool = False) -> str:
    return format_monetary_value(value, is_percent=is_percent)


def build_mtd_legend_html() -> str:
    forecast_name = str(st.session_state.get("forecast_name", "Fcst") or "Fcst").strip()

    return (
        '<div class="metric-legend">'
        '<span class="metric-chip chip-real">REAL (BASE SAP)</span>'
        '<span class="metric-chip chip-client">Plan2026 by Client</span>'
        '<span class="metric-chip chip-sku">Plan2026 by SKU</span>'
        f'<span class="metric-chip chip-fcst-client">{escape(forecast_name)} by Client</span>'
        f'<span class="metric-chip chip-fcst-sku">{escape(forecast_name)} by SKU</span>'
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
    progress=None,
) -> bool:
    df_processed_sales = st.session_state.get("df_processed_sales")
    df_plan_client = st.session_state.get("df_plan_client")

    if df_processed_sales is None or df_plan_client is None:
        set_error_message(config.MSG_REPORT_1_BUILD_MISSING_FILES)
        return False
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
        return False
    if not is_plan_ready:
        set_error_message(config.MSG_VALIDATION_FAIL)
        set_warning_message(
            f"Columnas faltantes para Reporte 1 en plan por cliente: {', '.join(missing_plan)}"
        )
        return False
    try:
        payload = data_processor.build_report_1_payload(
            df_processed_sales,
            df_plan_client,
            selected_year=selected_year,
            selected_month=selected_month,
            progress_callback=progress,
        )
        st.session_state["report1_payload"] = payload
        set_success_message(config.MSG_REPORT_1_BUILD_SUCCESS)
        return True
    except Exception as exc:
        set_error_message(f"{config.MSG_REPORT_1_BUILD_ERROR} Detalle: {exc}")
        return False


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

    payload = st.session_state.get("report1_payload")

    if payload is None:
        st.markdown("### Construir Reporte")
        st.markdown(
            '<div class="report-note">Primero construye el reporte para habilitar la vista. Después podrás cambiar el Año, el Mes y la primera columna del reporte.</div>',
            unsafe_allow_html=True,
        )

        if st.button("Construir Reporte 1", use_container_width=True):
            build_ok = execute_with_status(
                "Construyendo Reporte 1...",
                lambda progress: run_report_1_build(progress=progress),
            )
            if build_ok:
                st.rerun()

        st.markdown("---")
        st.info("Aún no se ha construido el Reporte 1.")
        return

    selected_year_without_kens, selected_month_without_kens = render_report_period_row(
        "report1_without_kens_year", "report1_without_kens_month",
        "btn_report1_period_top",
        lambda year, month: run_report_1_build(selected_year=year, selected_month=month),
    )
    if selected_year_without_kens is not None and selected_month_without_kens is not None:
        render_independent_executive_summary(selected_year_without_kens, selected_month_without_kens)

    st.markdown("---")
    st.markdown("### Oficina de ventas MTD / YTD")

    payload = st.session_state.get("report1_payload")

    without_kens_options = get_filter_options_from_multiple_tables(
        [
            payload["mtd_without_kens_table"],
            payload["ytd_without_kens_table"],
        ],
        lambda row: str(row.get("Oficina de Ventas", "")).strip(),
    )

    active_year_report1 = payload["summary"]["latest_year"]
    active_month_report1 = payload["summary"]["latest_month"]

    report_1_bytes = exports.build_report_1_excel_bytes(
        mtd_without_kens_df=convert_report_table_for_export(
            payload["mtd_without_kens_table"]
        ),
        ytd_without_kens_df=convert_report_table_for_export(
            payload["ytd_without_kens_table"]
        ),
        report_title=build_report_context_title(
            "Reporte 1 - Oficina de ventas",
            active_year_report1,
            active_month_report1,
        ),
    )

    def _render_report1_download():
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

    applied_without_kens_labels = render_filter_download_row(
        "OFICINA DE VENTAS",
        "report1_without_kens_dimension_widget",
        "report1_without_kens_dimension_applied",
        without_kens_options,
        _render_report1_download,
    )

    filtered_mtd_without_kens = filter_report_1_without_kens_table(
        payload["mtd_without_kens_table"],
        applied_without_kens_labels,
    )
    filtered_ytd_without_kens = filter_report_1_without_kens_table(
        payload["ytd_without_kens_table"],
        applied_without_kens_labels,
    )

    st.markdown(
        '<div class="report-note compact-report-note">Las tablas MTD y YTD se muestran lado a lado para facilitar la lectura ejecutiva.</div>',
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
    progress=None,
) -> bool:
    df_processed_sales = st.session_state.get("df_processed_sales")
    df_plan_sku = st.session_state.get("df_plan_sku")

    if df_processed_sales is None or df_plan_sku is None:
        set_error_message(config.MSG_REPORT_2_BUILD_MISSING_FILES)
        return False
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
        return False
    if not is_plan_ready:
        set_error_message(config.MSG_VALIDATION_FAIL)
        set_warning_message(
            f"Columnas faltantes para Reporte 2 en plan por SKU: {', '.join(missing_plan)}"
        )
        return False
    try:
        payload = data_processor.build_report_2_segment_region_payload(
            df_processed_sales,
            df_plan_sku,
            selected_year=selected_year,
            selected_month=selected_month,
            progress_callback=progress,
        )
        st.session_state["report2_payload"] = payload
        set_success_message(config.MSG_REPORT_2_BUILD_SUCCESS)
        return True
    except Exception as exc:
        set_error_message(f"{config.MSG_REPORT_2_BUILD_ERROR} Detalle: {exc}")
        return False


def run_report_2_category_build(
    selected_year: int | None = None,
    selected_month: int | None = None,
    progress=None,
) -> bool:
    df_processed_sales = st.session_state.get("df_processed_sales")
    df_plan_sku = st.session_state.get("df_plan_sku")

    if df_processed_sales is None or df_plan_sku is None:
        set_error_message(config.MSG_REPORT_2_CATEGORY_BUILD_MISSING_FILES)
        return False
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
        return False
    if not is_plan_ready:
        set_error_message(config.MSG_VALIDATION_FAIL)
        set_warning_message(
            f"Columnas faltantes para Reporte Category en plan por SKU: {', '.join(missing_plan)}"
        )
        return False
    try:
        payload = data_processor.build_report_2_category_payload(
            df_processed_sales,
            df_plan_sku,
            selected_year=selected_year,
            selected_month=selected_month,
            progress_callback=progress,
        )
        st.session_state["report2_category_payload"] = payload
        set_success_message(config.MSG_REPORT_2_CATEGORY_BUILD_SUCCESS)
        return True
    except Exception as exc:
        set_error_message(f"{config.MSG_REPORT_2_CATEGORY_BUILD_ERROR} Detalle: {exc}")
        return False


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

    payload = st.session_state.get("report2_payload")
    payload_category = st.session_state.get("report2_category_payload")

    if payload is None:
        st.markdown("### Construir Segment x Region")
        if st.button("Construir Reporte Segment x Region", use_container_width=True):
            build_ok = execute_with_status(
                "Construyendo Segment x Region...",
                lambda progress: run_report_2_build(progress=progress),
            )
            if build_ok:
                st.rerun()

    # El periodo y el Resumen ejecutivo solo aparecen cuando el usuario
    # ya construyó al menos uno de los dos bloques de esta pestaña.
    selected_year_segment = None
    selected_month_segment = None

    if payload is not None or payload_category is not None:
        def _apply_report2_period(year, month):
            ok_segment = True
            ok_category = True

            if st.session_state.get("report2_payload") is not None:
                ok_segment = run_report_2_build(
                    selected_year=year,
                    selected_month=month,
                )

            if st.session_state.get("report2_category_payload") is not None:
                ok_category = run_report_2_category_build(
                    selected_year=year,
                    selected_month=month,
                )

            return bool(ok_segment and ok_category)

        selected_year_segment, selected_month_segment = render_report_period_row(
            "report2_segment_year",
            "report2_segment_month",
            "btn_report2_period_top",
            _apply_report2_period,
        )

        if (
            selected_year_segment is not None
            and selected_month_segment is not None
        ):
            st.session_state["report2_category_year"] = selected_year_segment
            st.session_state["report2_category_month"] = selected_month_segment
            render_independent_executive_summary(
                selected_year_segment,
                selected_month_segment,
            )

    st.markdown("---")
    st.markdown("### Segment x Region MTD / YTD")

    payload = st.session_state.get("report2_payload")

    if payload is None:
        st.info("Aún no se ha construido el bloque Segment x Region.")
    else:
        segment_region_options = get_filter_options_from_multiple_tables(
            [
                payload["mtd_segment_region_table"],
                payload["ytd_segment_region_table"],
            ],
            build_report_2_segment_region_display_label,
        )

        active_year_segment = payload["summary"]["latest_year"]
        active_month_segment = payload["summary"]["latest_month"]

        segment_bytes = exports.build_report_2_segment_excel_bytes(
            mtd_segment_df=convert_report_table_for_export(
                payload["mtd_segment_region_table"]
            ),
            ytd_segment_df=convert_report_table_for_export(
                payload["ytd_segment_region_table"]
            ),
            report_title=build_report_context_title(
                "Reporte 2 - Segment x Region",
                active_year_segment,
                active_month_segment,
            ),
        )

        def _render_segment_download():
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

        applied_segment_region_labels = render_filter_download_row(
            "SEGMENTO / REGIÓN",
            "report2_segment_dimension_widget",
            "report2_segment_dimension_applied",
            segment_region_options,
            _render_segment_download,
        )

        filtered_mtd_segment = filter_report_2_segment_region_table(
            payload["mtd_segment_region_table"],
            applied_segment_region_labels,
        )
        filtered_ytd_segment = filter_report_2_segment_region_table(
            payload["ytd_segment_region_table"],
            applied_segment_region_labels,
        )

        st.markdown(
            '<div class="report-note compact-report-note">Las tablas MTD y YTD se muestran lado a lado para facilitar la lectura ejecutiva.</div>',
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

    payload_category = st.session_state.get("report2_category_payload")

    if payload_category is None:
        st.markdown("---")
        st.markdown("### Construir Category")
        if st.button("Construir Reporte Category", use_container_width=True):
            build_ok = execute_with_status(
                "Construyendo Reporte Category...",
                lambda progress: run_report_2_category_build(progress=progress),
            )
            if build_ok:
                st.rerun()

    st.markdown("---")
    st.markdown("### Category MTD / YTD")

    if payload_category is None:
        st.info("Aún no se ha construido el Reporte Category.")
    else:
        selected_year_category = (
            selected_year_segment
            if selected_year_segment is not None
            else payload_category["summary"]["latest_year"]
        )
        selected_month_category = (
            selected_month_segment
            if selected_month_segment is not None
            else payload_category["summary"]["latest_month"]
        )

        category_options = get_filter_options_from_multiple_tables(
            [
                payload_category["mtd_category_table"],
                payload_category["ytd_category_table"],
            ],
            lambda row: str(row.get("Category", "")).strip(),
        )

        active_year_category = payload_category["summary"]["latest_year"]
        active_month_category = payload_category["summary"]["latest_month"]

        category_bytes = exports.build_report_2_category_excel_bytes(
            mtd_category_df=convert_report_table_for_export(
                payload_category["mtd_category_table"]
            ),
            ytd_category_df=convert_report_table_for_export(
                payload_category["ytd_category_table"]
            ),
            report_title=build_report_context_title(
                "Reporte 2 - Category",
                active_year_category,
                active_month_category,
            ),
        )

        def _render_category_download():
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

        applied_category_labels = render_filter_download_row(
            "CATEGORY",
            "report2_category_dimension_widget",
            "report2_category_dimension_applied",
            category_options,
            _render_category_download,
        )

        filtered_mtd_category = filter_report_2_category_table(
            payload_category["mtd_category_table"],
            applied_category_labels,
        )
        filtered_ytd_category = filter_report_2_category_table(
            payload_category["ytd_category_table"],
            applied_category_labels,
        )

        st.markdown(
            '<div class="report-note compact-report-note">Este bloque es independiente del anterior. Las tablas MTD y YTD se muestran lado a lado para facilitar la lectura ejecutiva.</div>',
            unsafe_allow_html=True,
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
    progress=None,
) -> bool:
    df_processed_sales = st.session_state.get("df_processed_sales")
    df_plan_sku = st.session_state.get("df_plan_sku")

    if df_processed_sales is None or df_plan_sku is None:
        set_error_message(config.MSG_REPORT_3_BUILD_MISSING_FILES)
        return False
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
        return False
    if not is_plan_ready:
        set_error_message(config.MSG_VALIDATION_FAIL)
        set_warning_message(
            f"Columnas faltantes para Reporte 3 en plan por SKU: {', '.join(missing_plan)}"
        )
        return False
    try:
        payload = data_processor.build_report_3_channel_payload(
            df_processed_sales,
            df_plan_sku,
            selected_year=selected_year,
            selected_month=selected_month,
            progress_callback=progress,
        )
        st.session_state["report3_payload"] = payload
        set_success_message(config.MSG_REPORT_3_BUILD_SUCCESS)
        return True
    except Exception as exc:
        set_error_message(f"{config.MSG_REPORT_3_BUILD_ERROR} Detalle: {exc}")
        return False


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

    payload = st.session_state.get("report3_payload")

    if payload is None:
        st.markdown("### Construir Reporte")
        if st.button("Construir Reporte 3", use_container_width=True):
            build_ok = execute_with_status(
                "Construyendo Reporte 3...",
                lambda progress: run_report_3_build(progress=progress),
            )
            if build_ok:
                st.rerun()

        st.markdown("---")
        st.info("Aún no se ha construido el Reporte 3.")
        return

    selected_year_channel, selected_month_channel = render_report_period_row(
        "report3_channel_year", "report3_channel_month",
        "btn_report3_period_top",
        lambda year, month: run_report_3_build(selected_year=year, selected_month=month),
    )
    if selected_year_channel is not None and selected_month_channel is not None:
        render_independent_executive_summary(selected_year_channel, selected_month_channel)

    st.markdown("---")
    st.markdown("### Channel MTD / YTD")

    payload = st.session_state.get("report3_payload")

    channel_options = get_filter_options_from_multiple_tables(
        [
            payload["mtd_channel_table"],
            payload["ytd_channel_table"],
        ],
        build_report_3_display_label,
    )

    active_year_channel = payload["summary"]["latest_year"]
    active_month_channel = payload["summary"]["latest_month"]

    report_3_bytes = exports.build_report_3_excel_bytes(
        mtd_channel_df=convert_report_table_for_export(payload["mtd_channel_table"]),
        ytd_channel_df=convert_report_table_for_export(payload["ytd_channel_table"]),
        report_title=build_report_context_title(
            "Reporte 3 - Channel",
            active_year_channel,
            active_month_channel,
        ),
    )

    def _render_report3_download():
        render_icon_download_button(
            data=report_3_bytes,
            file_name=build_excel_filename(
                "reporte_3",
                active_year_channel,
                active_month_channel,
            ),
            key="download_report_3_icon_top",
            help_text="Descargar Reporte 3",
        )

    applied_channel_labels = render_filter_download_row(
        "CHANNEL",
        "report3_channel_dimension_widget",
        "report3_channel_dimension_applied",
        channel_options,
        _render_report3_download,
    )

    filtered_mtd_channel = filter_report_3_channel_table(
        payload["mtd_channel_table"],
        applied_channel_labels,
    )
    filtered_ytd_channel = filter_report_3_channel_table(
        payload["ytd_channel_table"],
        applied_channel_labels,
    )

    st.markdown(
        '<div class="report-note compact-report-note">Las tablas MTD y YTD se muestran lado a lado para facilitar la lectura ejecutiva.</div>',
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
    progress=None,
) -> bool:
    df_processed_sales = st.session_state.get("df_processed_sales")
    df_plan_client = st.session_state.get("df_plan_client")

    if df_processed_sales is None or df_plan_client is None:
        set_error_message(config.MSG_REPORT_4_BUILD_MISSING_FILES)
        return False
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
        return False
    if not is_plan_ready:
        set_error_message(config.MSG_VALIDATION_FAIL)
        set_warning_message(
            f"Columnas faltantes para Reporte 4 en plan por cliente: {', '.join(missing_plan)}"
        )
        return False
    try:
        payload = data_processor.build_report_4_top_clients_payload(
            df_processed_sales,
            df_plan_client,
            selected_year=selected_year,
            selected_month=selected_month,
            progress_callback=progress,
        )
        st.session_state["report4_payload"] = payload
        set_success_message(config.MSG_REPORT_4_BUILD_SUCCESS)
        return True
    except Exception as exc:
        set_error_message(f"{config.MSG_REPORT_4_BUILD_ERROR} Detalle: {exc}")
        return False


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

    payload = st.session_state.get("report4_payload")

    if payload is None:
        st.markdown("### Construir Reporte")
        if st.button("Construir Reporte 4", use_container_width=True):
            build_ok = execute_with_status(
                "Construyendo Ranking de Clientes...",
                lambda progress: run_report_4_build(progress=progress),
            )
            if build_ok:
                st.rerun()

        st.markdown("---")
        st.info("Aún no se ha construido el Reporte 4.")
        return

    selected_year_clients, selected_month_clients = render_report_period_row(
        "report4_clients_year", "report4_clients_month",
        "btn_report4_period_top",
        lambda year, month: run_report_4_build(selected_year=year, selected_month=month),
    )
    if selected_year_clients is not None and selected_month_clients is not None:
        render_independent_executive_summary(selected_year_clients, selected_month_clients)

    st.markdown("---")

    payload = st.session_state.get("report4_payload")

    report_4_bytes = exports.build_report_4_excel_bytes(
        mtd_top_clients_df=convert_report_table_for_export(
            payload["mtd_top_clients_table"]
        ),
        ytd_top_clients_df=convert_report_table_for_export(
            payload["ytd_top_clients_table"]
        ),
        report_title=build_report_context_title(
            "Reporte 4 - Ranking de Clientes",
            payload["summary"]["latest_year"],
            payload["summary"]["latest_month"],
        ),
    )

    title_col, download_col = st.columns([12, 1], vertical_alignment="center")
    with title_col:
        st.markdown("### Ranking de Clientes MTD / YTD")
    with download_col:
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

    render_client_search(payload)

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
            payload.get("mtd_group_16_50_table", data_processor.pd.DataFrame()),
            payload.get("ytd_group_16_50_table", data_processor.pd.DataFrame()),
            payload["summary"]["latest_year"],
            payload["summary"]["latest_month"],
        )

    with st.expander("Ver detalle: Clients 51 to 100", expanded=False):
        render_report_4_detail_block(
            "Clients 51 to 100",
            payload.get("mtd_group_51_100_table", data_processor.pd.DataFrame()),
            payload.get("ytd_group_51_100_table", data_processor.pd.DataFrame()),
            payload["summary"]["latest_year"],
            payload["summary"]["latest_month"],
        )

    with st.expander("Ver detalle: Other clients", expanded=False):
        render_report_4_detail_block(
            "Other clients",
            payload.get("mtd_group_other_table", data_processor.pd.DataFrame()),
            payload.get("ytd_group_other_table", data_processor.pd.DataFrame()),
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
        missing_dependencies.append("La información de ventas todavía no está preparada.")

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
        if is_grand_total or client_name.lower() in {
            "total", "total general", "grand total", "total mexico", "total méxico"
        }:
            client_name = "Total Mexico"

        rows_html_parts.append(
            f'<tr{row_class}>'
            f'<td class="dashboard-compact-label dashboard-client-name">{escape(client_name)}</td>'
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

    if st.button("Cargar Dashboard", use_container_width=True):
        execute_with_status(
            "Validando y cargando Dashboard...",
            lambda progress: (
                progress("Verificando que todos los reportes estén construidos") or
                load_dashboard_view_state() or
                progress("Preparando la vista ejecutiva") or
                bool(st.session_state.get("dashboard_loaded", False))
            ),
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

    dashboard_tables = get_current_dashboard_export_tables()
    if dashboard_tables is not None:
        spacer_col, download_col = st.columns([12, 1])
        with download_col:
            dashboard_bytes = exports.build_dashboard_excel_bytes(
                dashboard_tables=dashboard_tables,
                report_title=dashboard_tables.get("report_title"),
                sheet_name=getattr(config, "EXPORT_SHEET_DASHBOARD", "Dashboard"),
            )
            render_icon_download_button(
                data=dashboard_bytes,
                file_name=build_excel_filename(
                    getattr(config, "EXPORT_DASHBOARD_FILE_BASE", "dashboard_ejecutivo"),
                    dashboard_tables.get("latest_year"),
                    dashboard_tables.get("latest_month"),
                ),
                key="download_dashboard_icon_top",
                help_text=getattr(
                    config,
                    "EXPORT_DASHBOARD_HELP",
                    "Descargar Dashboard ejecutivo",
                ),
            )

    st.markdown(
        build_dashboard_stage_one_html(payload),
        unsafe_allow_html=True,
    )

# =========================================================
# 18. VISTAS PRINCIPALES
# =========================================================
def render_home_view() -> None:
    """Portada corporativa y guía visual de módulos."""
    st.markdown(styles.build_home_start_css(), unsafe_allow_html=True)
    st.markdown(
        styles.build_home_carousel(config.HOME_BANNER_PATHS),
        unsafe_allow_html=True,
    )

    # Recupera el aviso verde que confirma si existe información disponible.
    # Se muestra justo debajo del carrusel y antes de la guía de módulos.
    render_persistent_data_status()

    st.markdown(
        styles.build_home_modules_html(
            modules=config.HOME_MODULE_CARDS,
            title=config.HOME_MODULES_TITLE,
            subtitle=config.HOME_MODULES_SUBTITLE,
        ),
        unsafe_allow_html=True,
    )
    st.markdown(
        styles.build_home_trust_strip_html(config.HOME_TRUST_ITEMS),
        unsafe_allow_html=True,
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
        Cargar correctamente el archivo corporativo de ventas, planes y Forecast,
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
    fcst_client_loaded = st.session_state.get("df_fcst_client") is not None
    fcst_sku_loaded = st.session_state.get("df_fcst_sku") is not None

    # Tarjetas superiores: se conservan en tres columnas iguales.
    col1, col2, col3 = st.columns(3)

    with col1:
        sales_status_placeholder = st.empty()
        sales_status_placeholder.markdown(
            styles.build_info_card(
                "Ventas",
                "Cargado" if sales_loaded else "Pendiente",
                "Hoja BASE SAP del archivo corporativo",
            ),
            unsafe_allow_html=True,
        )

    with col2:
        plan_client_status_placeholder = st.empty()
        plan_client_status_placeholder.markdown(
            styles.build_info_card(
                "Plan Cliente",
                "Cargado" if plan_client_loaded else "Pendiente",
                "Hoja Plan2026 by Client",
            ),
            unsafe_allow_html=True,
        )

    with col3:
        plan_sku_status_placeholder = st.empty()
        plan_sku_status_placeholder.markdown(
            styles.build_info_card(
                "Plan SKU",
                "Cargado" if plan_sku_loaded else "Pendiente",
                "Hoja Plan2026 by SKU",
            ),
            unsafe_allow_html=True,
        )

    # Forecast: dos tarjetas con exactamente el mismo ancho que una tarjeta
    # de la fila superior. Los márgenes laterales de 0.5 + 0.5 las centran
    # como bloque dentro del ancho disponible.
    fcst_left_spacer, col4, col5, fcst_right_spacer = st.columns([0.5, 1, 1, 0.5])

    with col4:
        fcst_client_status_placeholder = st.empty()
        fcst_client_status_placeholder.markdown(
            styles.build_info_card(
                "Forecast Cliente",
                "Cargado" if fcst_client_loaded else "Pendiente",
                st.session_state.get("forecast_client_sheet_name") or "Hoja FcstX+Y by Client",
                icon_override="◈",
                color_override="green",
            ),
            unsafe_allow_html=True,
        )

    with col5:
        fcst_sku_status_placeholder = st.empty()
        fcst_sku_status_placeholder.markdown(
            styles.build_info_card(
                "Forecast SKU",
                "Cargado" if fcst_sku_loaded else "Pendiente",
                st.session_state.get("forecast_sku_sheet_name") or "Hoja FcstX+Y by SKU",
                icon_override="◈",
                color_override="green",
            ),
            unsafe_allow_html=True,
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
        "Sube una sola vez el Excel corporativo. La app leerá internamente BASE SAP, "
        "Plan2026 by Client, Plan2026 by SKU y detectará automáticamente el par activo "
        "de hojas Forecast by Client / by SKU."
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

                loaded_payload: dict = {}

                load_ok = execute_with_status(
                    "Cargando archivo corporativo...",
                    lambda progress: (
                        loaded_payload.update(
                            data_loader.load_dashboard_excel_from_uploaded_file(
                                uploaded_master_file,
                                progress_callback=progress,
                            )
                        )
                        or True
                    ),
                )

                if not load_ok:
                    raise RuntimeError("No fue posible completar la lectura del archivo corporativo.")

                payload = loaded_payload
                df_sales = payload.get("df_sales")
                df_plan_client = payload.get("df_plan_client")
                df_plan_sku = payload.get("df_plan_sku")
                df_fcst_client = payload.get("df_fcst_client")
                df_fcst_sku = payload.get("df_fcst_sku")

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
                is_valid_fcst_client, missing_fcst_client = validators.validate_required_columns(
                    df_fcst_client,
                    config.EXPECTED_COLUMNS_FCST_CLIENT,
                )
                is_valid_fcst_sku, missing_fcst_sku = validators.validate_required_columns(
                    df_fcst_sku,
                    config.EXPECTED_COLUMNS_FCST_SKU,
                )

                st.session_state["df_sales"] = df_sales
                st.session_state["df_plan_client"] = df_plan_client
                st.session_state["df_plan_sku"] = df_plan_sku
                st.session_state["df_fcst_client"] = df_fcst_client
                st.session_state["df_fcst_sku"] = df_fcst_sku

                st.session_state["forecast_name"] = payload.get("forecast_name", "")
                st.session_state["forecast_client_sheet_name"] = payload.get("forecast_client_sheet_name", "")
                st.session_state["forecast_sku_sheet_name"] = payload.get("forecast_sku_sheet_name", "")

                st.session_state["sales_valid"] = is_valid_sales
                st.session_state["plan_client_valid"] = is_valid_plan_client
                st.session_state["plan_sku_valid"] = is_valid_plan_sku
                st.session_state["fcst_client_valid"] = is_valid_fcst_client
                st.session_state["fcst_sku_valid"] = is_valid_fcst_sku

                st.session_state["sales_missing_columns"] = missing_sales
                st.session_state["plan_client_missing_columns"] = missing_plan_client
                st.session_state["plan_sku_missing_columns"] = missing_plan_sku
                st.session_state["fcst_client_missing_columns"] = missing_fcst_client
                st.session_state["fcst_sku_missing_columns"] = missing_fcst_sku

                st.session_state["master_upload_signature"] = master_signature
                st.session_state["master_file_name"] = uploaded_master_file.name
                st.session_state["sales_file_name"] = f"{uploaded_master_file.name} | BASE SAP"
                st.session_state["plan_client_file_name"] = f"{uploaded_master_file.name} | Plan2026 by Client"
                st.session_state["plan_sku_file_name"] = f"{uploaded_master_file.name} | Plan2026 by SKU"
                st.session_state["fcst_client_file_name"] = (
                    f"{uploaded_master_file.name} | {payload.get('forecast_client_sheet_name', 'Forecast by Client')}"
                )
                st.session_state["fcst_sku_file_name"] = (
                    f"{uploaded_master_file.name} | {payload.get('forecast_sku_sheet_name', 'Forecast by SKU')}"
                )

                # Actualiza inmediatamente las cinco tarjetas del resumen de carga
                # en el mismo ciclo de Streamlit. Esto evita que permanezcan en
                # "Pendiente" después de que las hojas ya fueron cargadas.
                sales_status_placeholder.markdown(
                    styles.build_info_card(
                        "Ventas",
                        "Cargado",
                        "Hoja BASE SAP del archivo corporativo",
                    ),
                    unsafe_allow_html=True,
                )
                plan_client_status_placeholder.markdown(
                    styles.build_info_card(
                        "Plan Cliente",
                        "Cargado",
                        "Hoja Plan2026 by Client",
                    ),
                    unsafe_allow_html=True,
                )
                plan_sku_status_placeholder.markdown(
                    styles.build_info_card(
                        "Plan SKU",
                        "Cargado",
                        "Hoja Plan2026 by SKU",
                    ),
                    unsafe_allow_html=True,
                )
                fcst_client_status_placeholder.markdown(
                    styles.build_info_card(
                        "Forecast Cliente",
                        "Cargado",
                        payload.get("forecast_client_sheet_name") or "Hoja FcstX+Y by Client",
                        icon_override="◈",
                        color_override="green",
                    ),
                    unsafe_allow_html=True,
                )
                fcst_sku_status_placeholder.markdown(
                    styles.build_info_card(
                        "Forecast SKU",
                        "Cargado",
                        payload.get("forecast_sku_sheet_name") or "Hoja FcstX+Y by SKU",
                        icon_override="◈",
                        color_override="green",
                    ),
                    unsafe_allow_html=True,
                )

                st.session_state["df_processed_sales"] = None
                st.session_state["persistent_data_loaded"] = False
                st.session_state["persistent_data_metadata"] = None

                clear_report_payloads()

                if all([
                    is_valid_sales,
                    is_valid_plan_client,
                    is_valid_plan_sku,
                    is_valid_fcst_client,
                    is_valid_fcst_sku,
                ]):
                    detected_forecast = payload.get("forecast_name", "Forecast")

                    # La BASE SAP se procesa automáticamente en cuanto la carga
                    # corporativa queda validada. El usuario ya no necesita ir
                    # a Visión general ni presionar un botón adicional.
                    processing_ok = ensure_sales_processed_automatically(show_status=False)

                    if processing_ok:
                        st.success(
                            f"Archivo corporativo cargado y preparado correctamente. "
                            f"Las cinco hojas funcionales fueron validadas. "
                            f"Forecast detectado: {detected_forecast}."
                        )
                    else:
                        st.warning(
                            "El archivo corporativo fue validado, pero no fue posible preparar "
                            "automáticamente la base de ventas. Revisa los avisos mostrados por la app."
                        )
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
    # VISTA PREVIA - FORECAST POR CLIENTE
    # =====================================================
    st.markdown(
        f'<div class="base-mtd-section-heading">{escape(config.FCST_CLIENT_DISPLAY_TITLE)}</div>',
        unsafe_allow_html=True,
    )

    if st.session_state.get("df_fcst_client") is not None:
        fcst_client_missing = st.session_state.get("fcst_client_missing_columns", [])
        render_file_validation_result(
            is_valid=st.session_state.get("fcst_client_valid", False),
            missing_columns=fcst_client_missing,
            success_message=config.MSG_VALIDATION_OK,
        )

        fcst_client_file_name = st.session_state.get(
            "fcst_client_file_name",
            "Archivo cargado en sesión",
        )
        st.caption(f"Archivo en sesión: {fcst_client_file_name}")

        render_preview_expander(
            config.FCST_CLIENT_PREVIEW_TITLE,
            st.session_state.get("df_fcst_client"),
            rows=10,
            convert_currency=False,
        )
    else:
        st.info("Aún no se ha cargado la hoja Forecast by Client.")

    st.markdown("---")

    # =====================================================
    # VISTA PREVIA - FORECAST POR SKU
    # =====================================================
    st.markdown(
        f'<div class="base-mtd-section-heading">{escape(config.FCST_SKU_DISPLAY_TITLE)}</div>',
        unsafe_allow_html=True,
    )

    if st.session_state.get("df_fcst_sku") is not None:
        fcst_sku_missing = st.session_state.get("fcst_sku_missing_columns", [])
        render_file_validation_result(
            is_valid=st.session_state.get("fcst_sku_valid", False),
            missing_columns=fcst_sku_missing,
            success_message=config.MSG_VALIDATION_OK,
        )

        fcst_sku_file_name = st.session_state.get(
            "fcst_sku_file_name",
            "Archivo cargado en sesión",
        )
        st.caption(f"Archivo en sesión: {fcst_sku_file_name}")

        render_preview_expander(
            config.FCST_SKU_PREVIEW_TITLE,
            st.session_state.get("df_fcst_sku"),
            rows=10,
            convert_currency=False,
        )
    else:
        st.info("Aún no se ha cargado la hoja Forecast by SKU.")

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
    fcst_client_loaded = st.session_state.get("df_fcst_client") is not None
    fcst_sku_loaded = st.session_state.get("df_fcst_sku") is not None

    if all([
        sales_loaded,
        plan_client_loaded,
        plan_sku_loaded,
        fcst_client_loaded,
        fcst_sku_loaded,
    ]):
        st.info(
            "Cuando las cinco hojas funcionales estén validadas, guarda esta carga para que los usuarios viewer puedan consultar la app sin subir archivos."
        )
        if st.button("Guardar carga administrativa para viewers", use_container_width=True):
            save_ok = execute_with_status(
                "Guardando carga administrativa...",
                lambda progress: save_current_data_for_viewers(progress=progress),
            )
            if save_ok:
                # No forzamos un rerun aquí: así el estado de Guardar no puede
                # reutilizarse visualmente como si fuera el estado de Eliminar.
                render_global_alerts()
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
        if st.button(
            "Borrar carga guardada para viewers",
            use_container_width=True,
        ):
            delete_ok = execute_with_status(
                "Eliminando carga guardada...",
                lambda progress: delete_persistent_data(progress=progress),
            )
            if delete_ok:
                # Igual que al guardar, mostramos el resultado en este mismo render
                # para evitar estados "fantasma" durante un rerun inmediato.
                render_global_alerts()

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

    # La BASE SAP ya se procesa automáticamente después de una carga válida
    # o al recuperar la carga administrativa de un viewer.
    # Visión general queda exclusivamente como pantalla de consulta y análisis.
    df_processed = st.session_state.get("df_processed_sales")

    if df_processed is None or df_processed.empty:
        st.info(
            "La información de ventas todavía no está disponible. "
            "Cuando exista una carga válida, la app la preparará automáticamente."
        )

    st.markdown(
        '<div class="base-mtd-section-heading">Tendencia Historica</div>',
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
        st.info("No hay información suficiente para construir la tendencia histórica.")

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
        st.info("La base de ventas todavía no está disponible.")

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
        st.info("No hay información preparada para mostrar todavía.")


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

        if st.button("Construir Base MTD", use_container_width=True):
            build_ok = execute_with_status(
                "Construyendo Base MTD...",
                lambda progress: run_mtd_build(progress=progress),
            )
            if build_ok:
                st.rerun()

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

    render_report_period_row(
        "base_mtd_year",
        "base_mtd_month",
        "btn_base_mtd_period_filter",
        lambda year, month: run_mtd_build(
            selected_year=year,
            selected_month=month,
        ),
    )

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
# INTEGRACIÓN FORECAST - OVERRIDES CONSERVADORES
# =========================================================
# El código original de la aplicación permanece completo arriba.
# Estas redefiniciones se cargan antes de main() y añaden únicamente
# Forecast a Base MTD, reportes, filtros, conversiones y tablas visuales.
# =========================================================


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
            "Fcst",
            "PY",
            "Var VS Plan",
            "Var VS Fcst",
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
        monetary_columns=["Actual", "Plan", "Fcst", "PY", "Var VS Plan", "Var VS Fcst", "Var VS PY"],
    )


def recalculate_row_metrics(template_row, actual: float, plan, fcst, py: float):
    row=dict(template_row); actual_value=safe_float(actual); py_value=safe_float(py)
    plan_value=None if plan is None else safe_float(plan); fcst_value=None if fcst is None else safe_float(fcst)
    row.update({"Actual":actual_value,"Plan":plan_value,"Fcst":fcst_value,"PY":py_value})
    row["Var VS Plan"]=None if plan_value is None else actual_value-plan_value; row["%Var VS Plan"]=None if plan_value is None else (0.0 if plan_value==0 else (actual_value-plan_value)/plan_value)
    row["Var VS Fcst"]=None if fcst_value is None else actual_value-fcst_value; row["%Var VS Fcst"]=None if fcst_value is None else (0.0 if fcst_value==0 else (actual_value-fcst_value)/fcst_value)
    row["Var VS PY"]=actual_value-py_value; row["%Var VS PY"]=0.0 if py_value==0 else (actual_value-py_value)/py_value
    return row


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
        total_fcst = filtered_normals["Fcst"].apply(lambda x: safe_float(x, 0.0)).sum()
        total_py = filtered_normals["PY"].apply(safe_float).sum()

        rows.append(
            recalculate_row_metrics(
                total_row_template, actual=total_actual, plan=total_plan, fcst=total_fcst, py=total_py,
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
            total_fcst = segment_rows["Fcst"].apply(safe_float).sum()
            total_py = segment_rows["PY"].apply(safe_float).sum()

            rows.append(
                recalculate_row_metrics(
                    row, actual=total_actual, plan=total_plan, fcst=total_fcst, py=total_py,
                )
            )
            continue

        if is_grand_total:
            grand_actual = filtered_normals["Actual"].apply(safe_float).sum()
            grand_plan = filtered_normals["Plan"].apply(safe_float).sum()
            grand_fcst = filtered_normals["Fcst"].apply(safe_float).sum()
            grand_py = filtered_normals["PY"].apply(safe_float).sum()

            rows.append(
                recalculate_row_metrics(
                    row, actual=grand_actual, plan=grand_plan, fcst=grand_fcst, py=grand_py,
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
            total_fcst = category_rows["Fcst"].apply(safe_float).sum()
            total_py = category_rows["PY"].apply(safe_float).sum()

            rows.append(
                recalculate_row_metrics(
                    row, actual=total_actual, plan=total_plan, fcst=total_fcst, py=total_py,
                )
            )
            continue

        if is_grand_total:
            grand_actual = filtered_normals["Actual"].apply(safe_float).sum()
            grand_plan = filtered_normals["Plan"].apply(safe_float).sum()
            grand_fcst = filtered_normals["Fcst"].apply(safe_float).sum()
            grand_py = filtered_normals["PY"].apply(safe_float).sum()

            rows.append(
                recalculate_row_metrics(
                    row, actual=grand_actual, plan=grand_plan, fcst=grand_fcst, py=grand_py,
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
            grand_fcst = filtered_normals["Fcst"].apply(safe_float).sum()
            grand_py = filtered_normals["PY"].apply(safe_float).sum()

            rows.append(
                recalculate_row_metrics(
                    row, actual=grand_actual, plan=grand_plan, fcst=grand_fcst, py=grand_py,
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
            grand_fcst = filtered_normals["Fcst"].apply(safe_float).sum()
            grand_py = filtered_normals["PY"].apply(safe_float).sum()

            rows.append(
                recalculate_row_metrics(
                    row, actual=grand_actual, plan=grand_plan, fcst=grand_fcst, py=grand_py,
                )
            )

    return data_processor.pd.DataFrame(rows)


def run_mtd_build(selected_year: int | None=None, selected_month: int | None=None, progress=None) -> bool:
    dfs={k:st.session_state.get(k) for k in ["df_processed_sales","df_plan_client","df_plan_sku","df_fcst_client","df_fcst_sku"]}
    if any(v is None for v in dfs.values()):
        set_error_message("Para construir Base MTD se requieren ventas procesadas, Plan Cliente, Plan SKU, Forecast Cliente y Forecast SKU."); return False
    try:
        payload=data_processor.build_mtd_payload(dfs["df_processed_sales"],dfs["df_plan_client"],dfs["df_plan_sku"],dfs["df_fcst_client"],dfs["df_fcst_sku"],forecast_name=st.session_state.get("forecast_name","Fcst"),selected_year=selected_year,selected_month=selected_month,progress_callback=progress)
        st.session_state["mtd_payload"]=payload; st.session_state["df_mtd_base"]=None; set_success_message(config.MSG_MTD_BUILD_SUCCESS); return True
    except Exception as exc:
        set_error_message(f"{config.MSG_MTD_BUILD_ERROR} Detalle: {exc}"); return False


def build_horizontal_plan_table_html(title: str, df_table, plan_variant: str) -> str:
    if df_table is None or df_table.empty: return ""
    visible=["Periodo","Actual","Plan","Var VS Plan","%Var VS Plan","Fcst","Var VS Fcst","%Var VS Fcst","PY","Var VS PY","%Var VS PY"]
    header_class={"Actual":"h-header-real","Plan":"plan-header-client" if plan_variant=="client" else "plan-header-sku","Fcst":"fcst-header-client" if plan_variant=="client" else "fcst-header-sku","PY":"h-header-real","Var VS Plan":"var-header-plan","%Var VS Plan":"var-header-plan","Var VS Fcst":"var-header-fcst","%Var VS Fcst":"var-header-fcst","Var VS PY":"var-header-py","%Var VS PY":"var-header-py"}
    grid="grid-template-columns:1.2fr "+" ".join(["1fr"]*(len(visible)-1))
    heads=''.join([f'<div class="h-cell h-header {header_class.get(c,"h-header-neutral")}">{escape(c)}</div>' for c in visible])
    rows=[]
    for _,r in df_table.iterrows():
        cells=[f'<div class="h-cell h-row-label">{escape(str(r.get("Periodo","")))}</div>']
        for c in visible[1:]:
            v=r.get(c); pct=c.startswith("%"); cls="negative-value" if safe_float(v)<0 else "neutral-value"; cells.append(f'<div class="h-cell h-value {cls}">{format_monetary_value(v,is_percent=pct)}</div>')
        rows.append(''.join(cells))
    return f'<div class="horizontal-table-card base-mtd-number-table-card"><div class="horizontal-table-title">{escape(title)}</div><div class="h-table" style="{grid}">{heads}{"".join(rows)}</div></div>'


def run_report_1_build(selected_year: int | None=None, selected_month: int | None=None, progress=None) -> bool:
    sales=st.session_state.get("df_processed_sales"); plan=st.session_state.get("df_plan_client"); fcst=st.session_state.get("df_fcst_client")
    if sales is None or plan is None or fcst is None:
        set_error_message("Para construir Reporte 1 se requieren ventas procesadas, Plan Cliente y Forecast Cliente."); return False
    try:
        st.session_state["report1_payload"]=data_processor.build_report_1_payload(sales,plan,fcst,forecast_name=st.session_state.get("forecast_name","Fcst"),selected_year=selected_year,selected_month=selected_month,progress_callback=progress)
        set_success_message(config.MSG_REPORT_1_BUILD_SUCCESS); return True
    except Exception as exc:
        set_error_message(f"{config.MSG_REPORT_1_BUILD_ERROR} Detalle: {exc}"); return False


def build_report_1_table_html(title: str, df_table) -> str:
    if df_table is None or df_table.empty:
        return f'<div class="report-table-card"><div class="report-table-title">{escape(title)}</div><div>Sin información disponible</div></div>'
    visible=[c for c in df_table.columns if not str(c).startswith("__") and c not in {"TOP","Grupo"}]
    metric_classes={"Actual":"report-header-actual","Plan":"report-header-plan","Fcst":"report-header-fcst","PY":"report-header-py","Var VS Plan":"report-header-var-plan","%Var VS Plan":"report-header-var-plan","Var VS Fcst":"report-header-var-fcst","%Var VS Fcst":"report-header-var-fcst","Var VS PY":"report-header-var-py","%Var VS PY":"report-header-var-py"}
    grid=f"grid-template-columns: minmax(220px,2.2fr) " + " ".join(["minmax(105px,1fr)" for _ in visible[1:]]) + "; min-width:"+str(max(1100,len(visible)*125))+"px;"
    headers=[]
    for i,col in enumerate(visible):
        cls="report-header-neutral report-header-sticky" if i==0 else metric_classes.get(col,"report-header-neutral")
        headers.append(f'<div class="report-cell report-header {cls}">{escape(str(col))}</div>')
    rows=[]
    for _,row in df_table.iterrows():
        row_cls="report-total" if bool(row.get("__is_total__",False) or row.get("__is_grand_total__",False)) else ("report-highlight" if bool(row.get("__is_highlight__",False)) else "")
        cells=[]
        for i,col in enumerate(visible):
            val=row.get(col)
            if i==0:
                text=str(val or ""); cells.append(f'<div class="report-cell report-label-cell">{escape(text)}</div>')
            else:
                is_pct=str(col).startswith("%"); formatted=format_monetary_value(val,is_percent=is_pct,allow_blank=True); neg=" report-negative" if safe_float(val)<0 else ""
                cells.append(f'<div class="report-cell report-value-cell{neg}">{formatted}</div>')
        rows.append(f'<div class="report-row {row_cls}">'+"".join(cells)+"</div>")
    return f'<div class="report-table-card"><div class="report-table-title">{escape(title)}</div><div class="report-table-scroll"><div class="report-grid report-grid-dynamic" style="{grid}">'+"".join(headers)+"".join(rows)+'</div></div></div>'


def run_report_2_build(selected_year: int | None=None, selected_month: int | None=None, progress=None) -> bool:
    sales=st.session_state.get("df_processed_sales"); plan=st.session_state.get("df_plan_sku"); fcst=st.session_state.get("df_fcst_sku")
    if sales is None or plan is None or fcst is None:
        set_error_message("Para construir Segment x Region se requieren ventas procesadas, Plan SKU y Forecast SKU."); return False
    try:
        st.session_state["report2_payload"]=data_processor.build_report_2_segment_region_payload(sales,plan,fcst,forecast_name=st.session_state.get("forecast_name","Fcst"),selected_year=selected_year,selected_month=selected_month,progress_callback=progress)
        set_success_message(config.MSG_REPORT_2_BUILD_SUCCESS); return True
    except Exception as exc:
        set_error_message(f"{config.MSG_REPORT_2_BUILD_ERROR} Detalle: {exc}"); return False


def run_report_2_category_build(selected_year: int | None=None, selected_month: int | None=None, progress=None) -> bool:
    sales=st.session_state.get("df_processed_sales"); plan=st.session_state.get("df_plan_sku"); fcst=st.session_state.get("df_fcst_sku")
    if sales is None or plan is None or fcst is None:
        set_error_message("Para construir Category se requieren ventas procesadas, Plan SKU y Forecast SKU."); return False
    try:
        st.session_state["report2_category_payload"]=data_processor.build_report_2_category_payload(sales,plan,fcst,forecast_name=st.session_state.get("forecast_name","Fcst"),selected_year=selected_year,selected_month=selected_month,progress_callback=progress)
        set_success_message(config.MSG_REPORT_2_CATEGORY_BUILD_SUCCESS); return True
    except Exception as exc:
        set_error_message(f"{config.MSG_REPORT_2_CATEGORY_BUILD_ERROR} Detalle: {exc}"); return False


def build_report_2_table_html(title: str, df_table, first_header: str, view_type: str) -> str:
    """
    Renderiza Segment x Region y Category con Forecast.

    Corrección específica de layout:
    - Segment x Region conserva 2 columnas dimensionales antes de las métricas.
    - Category conserva 4 columnas dimensionales antes de las métricas.
    - Las dimensiones se muestran como texto (Material ya no se formatea como importe).
    - Las 10 métricas mantienen el orden Actual, Plan, Fcst, PY y variaciones.
    - Se conserva el scroll horizontal para no comprimir ni montar encabezados.
    """
    if df_table is None or df_table.empty:
        return (
            '<div class="report-table-card">'
            f'<div class="report-table-title">{escape(title)}</div>'
            '<div>Sin información disponible</div>'
            '</div>'
        )

    metric_columns = [
        "Actual",
        "Plan",
        "Var VS Plan",
        "%Var VS Plan",
        "Fcst",
        "Var VS Fcst",
        "%Var VS Fcst",
        "PY",
        "Var VS PY",
        "%Var VS PY",
    ]

    metric_classes = {
        "Actual": "report-header-actual",
        "Plan": "report-header-plan",
        "Fcst": "report-header-fcst",
        "PY": "report-header-py",
        "Var VS Plan": "report-header-var-plan",
        "%Var VS Plan": "report-header-var-plan",
        "Var VS Fcst": "report-header-var-fcst",
        "%Var VS Fcst": "report-header-var-fcst",
        "Var VS PY": "report-header-var-py",
        "%Var VS PY": "report-header-var-py",
    }

    if view_type == "category":
        dimension_columns = [
            "Category",
            "Material",
            "Categoría del Material",
            "Descripción del Material",
        ]
        dimension_widths = [
            "minmax(235px,1.55fr)",
            "minmax(145px,1.00fr)",
            "minmax(225px,1.55fr)",
            "minmax(270px,1.85fr)",
        ]
        scroll_class = "report-table-scroll report-category-scroll"
        card_class = "report-table-card report-category-card"
    elif view_type == "segment_region":
        dimension_columns = ["Segmento", "Región"]
        dimension_widths = [
            "minmax(220px,1.65fr)",
            "minmax(170px,1.20fr)",
        ]
        scroll_class = "report-table-scroll"
        card_class = "report-table-card"
    else:
        available_non_metric = [
            c for c in df_table.columns
            if not str(c).startswith("__")
            and c not in {"Grupo"}
            and c not in metric_columns
        ]
        dimension_columns = available_non_metric[:1] or [first_header]
        dimension_widths = ["minmax(220px,2.2fr)"]
        scroll_class = "report-table-scroll"
        card_class = "report-table-card"

    # Solo incluye columnas que realmente existen en el DataFrame.
    dimension_columns = [c for c in dimension_columns if c in df_table.columns]
    metrics_present = [c for c in metric_columns if c in df_table.columns]
    visible_columns = dimension_columns + metrics_present

    grid_template = " ".join(
        dimension_widths[:len(dimension_columns)]
        + ["minmax(108px,1fr)" for _ in metrics_present]
    )
    min_width = max(
        1280,
        235 * len(dimension_columns) + 112 * len(metrics_present),
    )
    grid_style = (
        f"grid-template-columns:{grid_template};"
        f"min-width:{min_width}px;"
        "width:100%;"
    )

    headers: list[str] = []

    for index, column_name in enumerate(visible_columns):
        if column_name in metric_classes:
            header_class = metric_classes[column_name]
        else:
            header_class = "report-header-neutral"
            if index == 0:
                if view_type == "category":
                    header_class += " report-category-header-sticky"
                else:
                    header_class += " report-header-sticky"

        headers.append(
            f'<div class="report-cell report-header {header_class}">'
            f'{escape(str(column_name).upper())}'
            '</div>'
        )

    rows: list[str] = []

    for _, row in df_table.iterrows():
        is_total = bool(row.get("__is_total__", False))
        is_grand_total = bool(row.get("__is_grand_total__", False))
        is_highlight = bool(row.get("__is_highlight__", False))

        row_classes = ["report-row"]
        if is_total:
            row_classes.append("report-total")
        if is_grand_total or is_highlight:
            row_classes.append("report-highlight")

        cells: list[str] = []

        for index, column_name in enumerate(visible_columns):
            value = row.get(column_name)

            if column_name in dimension_columns:
                # Las dimensiones son texto; nunca se formatean como importes.
                if value is None:
                    text_value = ""
                else:
                    try:
                        text_value = "" if data_processor.pd.isna(value) else str(value)
                    except Exception:
                        text_value = str(value)

                cell_class = "report-cell report-category-product-cell"
                if index == 0:
                    cell_class = "report-cell report-label-cell report-sticky-cell"

                cells.append(
                    f'<div class="{cell_class}">{escape(text_value)}</div>'
                )
                continue

            is_percent = str(column_name).startswith("%")
            formatted = format_monetary_value(
                value,
                is_percent=is_percent,
                allow_blank=True,
            )
            negative_class = (
                " report-negative"
                if safe_float(value) < 0
                else ""
            )

            cells.append(
                f'<div class="report-cell report-value-cell{negative_class}">'
                f'{formatted}'
                '</div>'
            )

        rows.append(
            f'<div class="{" ".join(row_classes)}">'
            + "".join(cells)
            + "</div>"
        )

    return (
        f'<div class="{card_class}">'
        f'<div class="report-table-title">{escape(title)}</div>'
        f'<div class="{scroll_class}">'
        f'<div class="report-grid report-grid-dynamic" style="{grid_style}">'
        + "".join(headers)
        + "".join(rows)
        + "</div>"
        + "</div>"
        + "</div>"
    )


def run_report_3_build(selected_year: int | None=None, selected_month: int | None=None, progress=None) -> bool:
    sales=st.session_state.get("df_processed_sales"); plan=st.session_state.get("df_plan_sku"); fcst=st.session_state.get("df_fcst_sku")
    if sales is None or plan is None or fcst is None:
        set_error_message("Para construir Reporte 3 se requieren ventas procesadas, Plan SKU y Forecast SKU."); return False
    try:
        st.session_state["report3_payload"]=data_processor.build_report_3_channel_payload(sales,plan,fcst,forecast_name=st.session_state.get("forecast_name","Fcst"),selected_year=selected_year,selected_month=selected_month,progress_callback=progress)
        set_success_message(config.MSG_REPORT_3_BUILD_SUCCESS); return True
    except Exception as exc:
        set_error_message(f"{config.MSG_REPORT_3_BUILD_ERROR} Detalle: {exc}"); return False


def build_report_3_table_html(title: str, df_table) -> str:
    if df_table is None or df_table.empty:
        return f'<div class="report-table-card"><div class="report-table-title">{escape(title)}</div><div>Sin información disponible</div></div>'
    visible=[c for c in df_table.columns if not str(c).startswith("__") and c not in {"TOP","Grupo"}]
    metric_classes={"Actual":"report-header-actual","Plan":"report-header-plan","Fcst":"report-header-fcst","PY":"report-header-py","Var VS Plan":"report-header-var-plan","%Var VS Plan":"report-header-var-plan","Var VS Fcst":"report-header-var-fcst","%Var VS Fcst":"report-header-var-fcst","Var VS PY":"report-header-var-py","%Var VS PY":"report-header-var-py"}
    grid=f"grid-template-columns: minmax(220px,2.2fr) " + " ".join(["minmax(105px,1fr)" for _ in visible[1:]]) + "; min-width:"+str(max(1100,len(visible)*125))+"px;"
    headers=[]
    for i,col in enumerate(visible):
        cls="report-header-neutral report-header-sticky" if i==0 else metric_classes.get(col,"report-header-neutral")
        headers.append(f'<div class="report-cell report-header {cls}">{escape(str(col))}</div>')
    rows=[]
    for _,row in df_table.iterrows():
        row_cls="report-total" if bool(row.get("__is_total__",False) or row.get("__is_grand_total__",False)) else ("report-highlight" if bool(row.get("__is_highlight__",False)) else "")
        cells=[]
        for i,col in enumerate(visible):
            val=row.get(col)
            if i==0:
                text=str(val or ""); cells.append(f'<div class="report-cell report-label-cell">{escape(text)}</div>')
            else:
                is_pct=str(col).startswith("%"); formatted=format_monetary_value(val,is_percent=is_pct,allow_blank=True); neg=" report-negative" if safe_float(val)<0 else ""
                cells.append(f'<div class="report-cell report-value-cell{neg}">{formatted}</div>')
        rows.append(f'<div class="report-row {row_cls}">'+"".join(cells)+"</div>")
    return f'<div class="report-table-card"><div class="report-table-title">{escape(title)}</div><div class="report-table-scroll"><div class="report-grid report-grid-dynamic" style="{grid}">'+"".join(headers)+"".join(rows)+'</div></div></div>'


def run_report_4_build(selected_year: int | None=None, selected_month: int | None=None, progress=None) -> bool:
    sales=st.session_state.get("df_processed_sales"); plan=st.session_state.get("df_plan_client"); fcst=st.session_state.get("df_fcst_client")
    if sales is None or plan is None or fcst is None:
        set_error_message("Para construir Ranking Clientes se requieren ventas procesadas, Plan Cliente y Forecast Cliente."); return False
    try:
        st.session_state["report4_payload"]=data_processor.build_report_4_top_clients_payload(sales,plan,fcst,forecast_name=st.session_state.get("forecast_name","Fcst"),selected_year=selected_year,selected_month=selected_month,progress_callback=progress)
        set_success_message(config.MSG_REPORT_4_BUILD_SUCCESS); return True
    except Exception as exc:
        set_error_message(f"{config.MSG_REPORT_4_BUILD_ERROR} Detalle: {exc}"); return False


def build_report_4_table_html(title: str, df_table) -> str:
    if df_table is None or df_table.empty:
        return f'<div class="report-table-card"><div class="report-table-title">{escape(title)}</div><div>Sin información disponible</div></div>'
    visible=[c for c in df_table.columns if not str(c).startswith("__") and c not in {"TOP","Grupo"}]
    metric_classes={"Actual":"report-header-actual","Plan":"report-header-plan","Fcst":"report-header-fcst","PY":"report-header-py","Var VS Plan":"report-header-var-plan","%Var VS Plan":"report-header-var-plan","Var VS Fcst":"report-header-var-fcst","%Var VS Fcst":"report-header-var-fcst","Var VS PY":"report-header-var-py","%Var VS PY":"report-header-var-py"}
    grid=f"grid-template-columns: minmax(220px,2.2fr) " + " ".join(["minmax(105px,1fr)" for _ in visible[1:]]) + "; min-width:"+str(max(1100,len(visible)*125))+"px;"
    headers=[]
    for i,col in enumerate(visible):
        cls="report-header-neutral report-header-sticky" if i==0 else metric_classes.get(col,"report-header-neutral")
        headers.append(f'<div class="report-cell report-header {cls}">{escape(str(col))}</div>')
    rows=[]
    for _,row in df_table.iterrows():
        row_cls="report-total" if bool(row.get("__is_total__",False) or row.get("__is_grand_total__",False)) else ("report-highlight" if bool(row.get("__is_highlight__",False)) else "")
        cells=[]
        for i,col in enumerate(visible):
            val=row.get(col)
            if i==0:
                text=str(val or ""); cells.append(f'<div class="report-cell report-label-cell">{escape(text)}</div>')
            else:
                is_pct=str(col).startswith("%"); formatted=format_monetary_value(val,is_percent=is_pct,allow_blank=True); neg=" report-negative" if safe_float(val)<0 else ""
                cells.append(f'<div class="report-cell report-value-cell{neg}">{formatted}</div>')
        rows.append(f'<div class="report-row {row_cls}">'+"".join(cells)+"</div>")
    return f'<div class="report-table-card"><div class="report-table-title">{escape(title)}</div><div class="report-table-scroll"><div class="report-grid report-grid-dynamic" style="{grid}">'+"".join(headers)+"".join(rows)+'</div></div></div>'

# Fuerza reconstrucción de reportes con la estructura Forecast actual.
REPORT_LOGIC_VERSION_R123 = "filters_applied_state_v20260813_04"
if st.session_state.get("report_logic_version_r123") != REPORT_LOGIC_VERSION_R123:
    clear_report_payloads()
    for _key in list(st.session_state.keys()):
        if _key.startswith(("report1_", "report2_", "report3_", "report4_", "base_mtd_")):
            st.session_state.pop(_key, None)
    st.session_state["report_logic_version_r123"] = REPORT_LOGIC_VERSION_R123

# =========================================================
# CORRECCIONES FINALES DE PRESENTACIÓN Y BASE MTD
# =========================================================
# Se redefinen únicamente los renderers afectados. Las definiciones originales
# se conservan completas arriba para mantener el historial y las demás reglas.

def build_horizontal_plan_table_html(title: str, df_table, plan_variant: str) -> str:
    if df_table is None or df_table.empty:
        return ""
    visible=["Periodo","Actual","Plan","Var VS Plan","%Var VS Plan","Fcst","Var VS Fcst","%Var VS Fcst","PY","Var VS PY","%Var VS PY"]
    is_client=plan_variant=="client"
    header_class={
        "Actual":"h-header-real",
        "Plan":"plan-header-client" if is_client else "plan-header-sku",
        "Fcst":"fcst-header-client" if is_client else "fcst-header-sku",
        "PY":"h-header-real",
        "Var VS Plan":"var-header-plan-client" if is_client else "var-header-plan-sku",
        "%Var VS Plan":"var-header-plan-client" if is_client else "var-header-plan-sku",
        "Var VS Fcst":"var-header-fcst-client" if is_client else "var-header-fcst-sku",
        "%Var VS Fcst":"var-header-fcst-client" if is_client else "var-header-fcst-sku",
        "Var VS PY":"var-header-py",
        "%Var VS PY":"var-header-py",
    }
    grid="grid-template-columns:1.2fr "+" ".join(["1fr"]*(len(visible)-1))
    heads=''.join(f'<div class="h-cell h-header {header_class.get(c,"h-header-neutral")}">{escape(c)}</div>' for c in visible)
    rows=[]
    for _,r in df_table.iterrows():
        cells=[f'<div class="h-cell h-row-label">{escape(str(r.get("Periodo","")))}</div>']
        for c in visible[1:]:
            v=r.get(c); pct=c.startswith("%")
            cls="negative-value" if safe_float(v)<0 else "neutral-value"
            cells.append(f'<div class="h-cell h-value {cls}">{format_monetary_value(v,is_percent=pct)}</div>')
        rows.append(''.join(cells))
    return f'<div class="horizontal-table-card base-mtd-number-table-card"><div class="horizontal-table-title">{escape(title)}</div><div class="h-table" style="{grid}">{heads}{"".join(rows)}</div></div>'

def build_report_2_table_html(title: str, df_table, first_header: str, view_type: str) -> str:
    """
    Render efectivo de Segment x Region y Category.

    Orden ejecutivo:
    Actual -> Plan -> Var VS Plan -> %Var VS Plan ->
    Fcst -> Var VS Fcst -> %Var VS Fcst ->
    PY -> Var VS PY -> %Var VS PY.
    """
    if df_table is None or df_table.empty:
        return f'<div class="report-table-card"><div class="report-table-title">{escape(title)}</div><div>Sin información disponible</div></div>'
    metrics=["Actual","Plan","Var VS Plan","%Var VS Plan","Fcst","Var VS Fcst","%Var VS Fcst","PY","Var VS PY","%Var VS PY"]
    metric_classes={"Actual":"report-header-actual","Plan":"report-header-plan","Fcst":"report-header-fcst","PY":"report-header-py","Var VS Plan":"report-header-var-plan","%Var VS Plan":"report-header-var-plan","Var VS Fcst":"report-header-var-fcst","%Var VS Fcst":"report-header-var-fcst","Var VS PY":"report-header-var-py","%Var VS PY":"report-header-var-py"}
    if view_type=="category":
        dims=["Category","Material","Categoría del Material","Descripción del Material"]
        widths=["minmax(235px,1.55fr)","minmax(145px,1fr)","minmax(225px,1.55fr)","minmax(270px,1.85fr)"]
        scroll_class="report-table-scroll report-category-scroll"
    else:
        dims=["Segmento","Región"] if view_type=="segment_region" else [first_header]
        widths=["minmax(220px,1.65fr)","minmax(170px,1.2fr)"][:len(dims)]
        scroll_class="report-table-scroll"
    dims=[c for c in dims if c in df_table.columns]; metrics=[c for c in metrics if c in df_table.columns]
    visible=dims+metrics
    template=" ".join(widths[:len(dims)]+["minmax(108px,1fr)" for _ in metrics])
    min_width=max(1280,235*len(dims)+112*len(metrics))
    style=f"grid-template-columns:{template};min-width:{min_width}px;width:100%;"
    headers=[]
    for i,c in enumerate(visible):
        cls=metric_classes.get(c,"report-header-neutral")
        if i==0: cls += " report-category-header-sticky" if view_type=="category" else " report-header-sticky"
        headers.append(f'<div class="report-cell report-header {cls}" title="{escape(str(c))}">{escape(str(c).upper())}</div>')
    rows=[]
    for _,row in df_table.iterrows():
        classes=["report-row"]
        if bool(row.get("__is_total__",False)): classes.append("report-total")
        if bool(row.get("__is_grand_total__",False) or row.get("__is_highlight__",False)): classes.append("report-highlight")
        cells=[]
        for i,c in enumerate(visible):
            value=row.get(c)
            if c in dims:
                text="" if value is None else str(value)
                cls="report-cell report-category-product-cell report-text-clamped"
                if i==0: cls="report-cell report-label-cell report-sticky-cell report-text-clamped"
                cells.append(f'<div class="{cls}" title="{escape(text)}">{escape(text)}</div>')
            else:
                pct=c.startswith("%"); neg=" report-negative" if safe_float(value)<0 else ""
                cells.append(f'<div class="report-cell report-value-cell{neg}">{format_monetary_value(value,is_percent=pct,allow_blank=True)}</div>')
        rows.append(f'<div class="{" ".join(classes)}">'+''.join(cells)+'</div>')
    return f'<div class="report-table-card"><div class="report-table-title">{escape(title)}</div><div class="{scroll_class}"><div class="report-grid report-grid-dynamic" style="{style}">'+''.join(headers)+''.join(rows)+'</div></div></div>'


# =========================================================
# DASHBOARD CON FORECAST
# =========================================================
DASHBOARD_METRIC_COLUMNS = [
    "Actual",
    "Plan",
    "Fcst",
    "PY",
    "Var VS Plan",
    "%Var VS Plan",
    "Var VS Fcst",
    "%Var VS Fcst",
    "Var VS PY",
    "%Var VS PY",
]


def _dashboard_metric_cell(row, column_name: str) -> str:
    return dashboard_compact_td(
        row.get(column_name),
        is_percent=column_name.startswith("%"),
        allow_blank=True,
    )


def _dashboard_generic_compact_table_html(
    title: str,
    df_table,
    label_column: str,
    label_header: str,
    label_builder=None,
    extra_block_class: str = "",
) -> str:
    """
    Tabla compacta estándar del Dashboard con Forecast.

    Orden:
    Actual | Plan | Fcst | PY |
    Var VS Plan | %Var VS Plan |
    Var VS Fcst | %Var VS Fcst |
    Var VS PY | %Var VS PY
    """
    if df_table is None or getattr(df_table, "empty", True):
        return (
            f'<div class="dashboard-compact-block {escape(extra_block_class)}">'
            f'<div class="dashboard-compact-title-box">{escape(title)}</div>'
            '<div class="dashboard-kpi-muted">Información no disponible.</div>'
            '</div>'
        )

    rows_html_parts: list[str] = []

    for _, row in df_table.iterrows():
        is_total = bool(row.get("__is_total__", False))
        is_grand_total = bool(row.get("__is_grand_total__", False))
        is_group_summary = bool(row.get("__is_group_summary__", False))

        if is_grand_total:
            row_class = ' class="dashboard-compact-grand-total"'
        elif is_total or is_group_summary:
            row_class = ' class="dashboard-compact-total"'
        else:
            row_class = ""

        if label_builder is not None:
            label_value = str(label_builder(row) or "").strip()
        else:
            label_value = str(row.get(label_column, "") or "").strip()

        if is_grand_total or label_value.lower() in {
            "total",
            "total general",
            "grand total",
            "total mexico",
            "total méxico",
        }:
            label_value = "Total Mexico"

        metric_cells = "".join(
            _dashboard_metric_cell(row, column_name)
            for column_name in DASHBOARD_METRIC_COLUMNS
        )

        rows_html_parts.append(
            f'<tr{row_class}>'
            f'<td class="dashboard-compact-label" title="{escape(label_value)}">'
            f'{escape(label_value)}'
            '</td>'
            f'{metric_cells}'
            '</tr>'
        )

    headers = "".join(
        f"<th>{escape(column_name)}</th>"
        for column_name in DASHBOARD_METRIC_COLUMNS
    )

    return (
        f'<div class="dashboard-compact-block {escape(extra_block_class)}">'
        f'<div class="dashboard-compact-title-box">{escape(title)}</div>'
        '<div class="dashboard-compact-table-wrap dashboard-forecast-table-wrap">'
        '<table class="dashboard-compact-table dashboard-forecast-table">'
        '<thead><tr>'
        f'<th>{escape(label_header)}</th>'
        f'{headers}'
        '</tr></thead>'
        '<tbody>'
        + "".join(rows_html_parts)
        + '</tbody></table></div></div>'
    )


def build_dashboard_metric_row(
    metric_name: str,
    actual,
    plan,
    fcst,
    py,
    var_plan,
    pct_var_plan,
    var_fcst,
    pct_var_fcst,
    var_py,
    pct_var_py,
    row_class: str = "",
) -> str:
    return (
        f'<tr class="{escape(row_class)}">'
        f'<td class="dashboard-kpi-name">{escape(metric_name)}</td>'
        f'{dashboard_td(actual)}'
        f'{dashboard_td(plan)}'
        f'{dashboard_td(fcst)}'
        f'{dashboard_td(py)}'
        f'{dashboard_td(var_plan)}'
        f'{dashboard_td(pct_var_plan, is_percent=True)}'
        f'{dashboard_td(var_fcst)}'
        f'{dashboard_td(pct_var_fcst, is_percent=True)}'
        f'{dashboard_td(var_py)}'
        f'{dashboard_td(pct_var_py, is_percent=True)}'
        '</tr>'
    )


def build_dashboard_achievement_row(gsnr_row) -> str:
    if gsnr_row is None:
        actual_value = None
        plan_value = None
        fcst_value = None
        py_value = None
    else:
        actual_value = safe_float(gsnr_row.get("Actual"))
        plan_value = safe_float(gsnr_row.get("Plan"))
        fcst_value = safe_float(gsnr_row.get("Fcst"))
        py_value = safe_float(gsnr_row.get("PY"))

    achievement_plan = (
        None
        if actual_value is None or plan_value in (None, 0)
        else actual_value / plan_value
    )
    achievement_fcst = (
        None
        if actual_value is None or fcst_value in (None, 0)
        else actual_value / fcst_value
    )
    achievement_py = (
        None
        if actual_value is None or py_value in (None, 0)
        else actual_value / py_value
    )

    return (
        '<tr class="dashboard-achievement-row">'
        '<td class="dashboard-kpi-name">% achievement</td>'
        f'{dashboard_td(None)}'
        f'{dashboard_td(None)}'
        f'{dashboard_td(None)}'
        f'{dashboard_td(None)}'
        f'{dashboard_percent_closed_td(achievement_plan)}'
        f'{dashboard_td(None)}'
        f'{dashboard_percent_closed_td(achievement_fcst)}'
        f'{dashboard_td(None)}'
        f'{dashboard_percent_closed_td(achievement_py)}'
        f'{dashboard_td(None)}'
        '</tr>'
    )


def build_dashboard_kpi_table_html(title: str, rows_html: str) -> str:
    headers = "".join(
        f"<th>{escape(column_name)}</th>"
        for column_name in DASHBOARD_METRIC_COLUMNS
    )

    return (
        '<div class="dashboard-kpi-panel">'
        f'<div class="dashboard-kpi-panel-title">{escape(title)}</div>'
        '<div class="dashboard-kpi-table-wrap dashboard-forecast-table-wrap">'
        '<table class="dashboard-kpi-table dashboard-forecast-table">'
        '<thead><tr>'
        '<th>KPI</th>'
        f'{headers}'
        '</tr></thead>'
        '<tbody>'
        f'{rows_html}'
        '</tbody></table></div></div>'
    )


def build_dashboard_report1_compact_table_html(title: str, df_table) -> str:
    return _dashboard_generic_compact_table_html(
        title=title,
        df_table=df_table,
        label_column="Oficina de Ventas",
        label_header="Channel",
    )


def build_dashboard_segment_compact_table_html(title: str, df_table) -> str:
    return _dashboard_generic_compact_table_html(
        title=title,
        df_table=df_table,
        label_column="Segmento",
        label_header="Segment / Region",
        label_builder=build_report_2_segment_region_display_label,
    )


def build_dashboard_category_compact_table_html(title: str, df_table) -> str:
    return _dashboard_generic_compact_table_html(
        title=title,
        df_table=df_table,
        label_column="Category",
        label_header="Category",
    )


def build_dashboard_report3_compact_table_html(title: str, df_table) -> str:
    return _dashboard_generic_compact_table_html(
        title=title,
        df_table=df_table,
        label_column="Channel",
        label_header="Channel",
        label_builder=lambda row: (
            str(row.get("Channel", "") or "").strip()
            or build_report_3_display_label(row)
        ),
    )


def build_dashboard_report4_compact_table_html(title: str, df_table) -> str:
    return _dashboard_generic_compact_table_html(
        title=title,
        df_table=df_table,
        label_column="Client Name",
        label_header="Client Name",
        extra_block_class="dashboard-clients-block",
    )


def build_dashboard_stage_one_html(payload: dict) -> str:
    latest_month = int(payload["latest_month"])
    latest_year = int(payload["latest_year"])

    month_label = get_dashboard_month_label_en(latest_month)
    currency_label = (
        "$Kmxn"
        if get_currency_status_label() == "MXN"
        else "$Kusd"
    )

    client_table = payload.get("client_table")
    bts_table = payload.get("bts_table")

    mtd_gsnr = dashboard_safe_get_row(client_table, "MTD")
    ytd_gsnr = dashboard_safe_get_row(client_table, "YTD")
    mtd_bts = dashboard_safe_get_row(bts_table, "MTD")
    ytd_bts = dashboard_safe_get_row(bts_table, "YTD")

    def gsnr_row(period_row, css_class: str) -> str:
        return build_dashboard_metric_row(
            metric_name="GSNR",
            actual=None if period_row is None else period_row.get("Actual"),
            plan=None if period_row is None else period_row.get("Plan"),
            fcst=None if period_row is None else period_row.get("Fcst"),
            py=None if period_row is None else period_row.get("PY"),
            var_plan=None if period_row is None else period_row.get("Var VS Plan"),
            pct_var_plan=None if period_row is None else period_row.get("%Var VS Plan"),
            var_fcst=None if period_row is None else period_row.get("Var VS Fcst"),
            pct_var_fcst=None if period_row is None else period_row.get("%Var VS Fcst"),
            var_py=None if period_row is None else period_row.get("Var VS PY"),
            pct_var_py=None if period_row is None else period_row.get("%Var VS PY"),
            row_class=css_class,
        )

    month_rows = (
        gsnr_row(mtd_gsnr, "dashboard-gsnr-row")
        + build_dashboard_achievement_row(mtd_gsnr)
        + build_dashboard_metric_row(
            metric_name=f"BTS ({month_label})",
            actual=None if mtd_bts is None else mtd_bts.get("Actual"),
            plan=None,
            fcst=None,
            py=None if mtd_bts is None else mtd_bts.get("PY"),
            var_plan=None,
            pct_var_plan=None,
            var_fcst=None,
            pct_var_fcst=None,
            var_py=None if mtd_bts is None else mtd_bts.get("Var VS PY"),
            pct_var_py=None if mtd_bts is None else mtd_bts.get("%Var VS PY"),
            row_class="dashboard-bts-row",
        )
    )

    ytd_rows = (
        gsnr_row(ytd_gsnr, "dashboard-gsnr-row")
        + build_dashboard_achievement_row(ytd_gsnr)
        + build_dashboard_metric_row(
            metric_name=f"BTS (Oct-{month_label})",
            actual=None if ytd_bts is None else ytd_bts.get("Actual"),
            plan=None,
            fcst=None,
            py=None if ytd_bts is None else ytd_bts.get("PY"),
            var_plan=None,
            pct_var_plan=None,
            var_fcst=None,
            pct_var_fcst=None,
            var_py=None if ytd_bts is None else ytd_bts.get("Var VS PY"),
            pct_var_py=None if ytd_bts is None else ytd_bts.get("%Var VS PY"),
            row_class="dashboard-bts-row",
        )
    )

    return (
        '<div class="dashboard-stage-card dashboard-scroll-aligned-layout">'
        '<div style="display:flex; align-items:flex-start; '
        'justify-content:flex-start; margin:0 0 8px 0;">'
        '<table style="border-collapse:collapse; '
        'font-family:Segoe UI, Arial, sans-serif; '
        'font-size:15px; color:#1F2A44;">'
        '<tr>'
        '<td style="font-weight:800; color:#E60023; '
        'padding:0 20px 4px 0;">Month</td>'
        f'<td style="font-weight:700; padding:0 0 4px 0;">'
        f'{escape(month_label)}</td>'
        '</tr>'
        '<tr>'
        '<td style="font-weight:800; color:#E60023; '
        'padding:0 20px 4px 0;">Year</td>'
        f'<td style="font-weight:700; padding:0 0 4px 0;">'
        f'{escape(str(latest_year))}</td>'
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

    # Conserva el estado propio de filtros/periodos aunque una sección
    # deje de renderizarse temporalmente.
    preserve_view_state_across_navigation()

    render_main_header()
    selected = render_sidebar()

    st.session_state["__last_selected_section"] = selected

    # Si la sesión acaba de recuperar la carga administrativa (por ejemplo,
    # un usuario viewer después de login/reboot), prepara BASE SAP una sola vez.
    # Si ya existe df_processed_sales, esta función no vuelve a procesar.
    ensure_sales_processed_automatically(show_status=(selected == "Inicio"))

    render_global_alerts()

    # Solo se ejecuta la vista seleccionada.
    # Los elementos de la vista anterior que Streamlit marque como stale
    # quedan ocultos por la regla CSS global definida al inicio del archivo.
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
# CORRECCIÓN FINAL: RANKING DE CLIENTES Y FORMATO GLOBAL
# =========================================================
def build_report_4_table_html(title: str, df_table) -> str:
    """
    Renderiza Ranking de Clientes conservando visibles las dos dimensiones.
    Solo Client Name permanece fijo; Cliente se desplaza con las métricas.
    """
    if df_table is None or df_table.empty:
        return (
            '<div class="report-table-card">'
            f'<div class="report-table-title">{escape(title)}</div>'
            '<div class="report-empty-state">-</div>'
            '</div>'
        )

    preferred = [
        "TOP", "Client Name", "Cliente", "Actual", "Plan",
        "Var VS Plan", "%Var VS Plan", "Fcst", "Var VS Fcst", "%Var VS Fcst",
        "PY", "Var VS PY", "%Var VS PY",
    ]
    visible = [c for c in preferred if c in df_table.columns]
    visible += [
        c for c in df_table.columns
        if c not in visible and not str(c).startswith("__") and c not in {"Grupo"}
    ]

    metric_classes = {
        "Actual": "report-header-actual", "Plan": "report-header-plan",
        "Fcst": "report-header-fcst", "PY": "report-header-py",
        "Var VS Plan": "report-header-var-plan", "%Var VS Plan": "report-header-var-plan",
        "Var VS Fcst": "report-header-var-fcst", "%Var VS Fcst": "report-header-var-fcst",
        "Var VS PY": "report-header-var-py", "%Var VS PY": "report-header-var-py",
    }

    widths = []
    for col in visible:
        if col == "Client Name": widths.append("minmax(230px,230px)")
        elif col == "Cliente": widths.append("minmax(105px,105px)")
        else: widths.append("minmax(108px,1fr)")
    grid = f"grid-template-columns:{' '.join(widths)};min-width:{335 + 112 * max(len(visible)-2, 0)}px;width:100%;"

    headers = []
    for col in visible:
        if col == "Client Name": cls = "report-header-neutral report4-name-header"
        elif col == "Cliente": cls = "report-header-neutral report4-code-header"
        else: cls = metric_classes.get(col, "report-header-neutral")
        headers.append(f'<div class="report-cell report-header {cls}" title="{escape(str(col))}">{escape(str(col).upper())}</div>')

    rows = []
    for _, row in df_table.iterrows():
        row_classes = ["report-row"]
        if bool(row.get("__is_total__", False) or row.get("__is_group_summary__", False)):
            row_classes.append("report-total")
        if bool(row.get("__is_grand_total__", False) or row.get("__is_highlight__", False)):
            row_classes.append("report-highlight")

        cells = []
        for col in visible:
            value = row.get(col)
            if col in {"Client Name", "Cliente"}:
                text = "" if value is None else str(value).strip()
                if col == "Client Name": cls = "report-cell report4-name-cell report-text-clamped"
                else: cls = "report-cell report4-code-cell report-text-clamped"
                cells.append(f'<div class="{cls}" title="{escape(text)}">{escape(text)}</div>')
            else:
                is_pct = str(col).startswith("%")
                formatted = format_monetary_value(value, is_percent=is_pct, allow_blank=False)
                negative = " report-negative" if safe_float(value) < 0 else ""
                cells.append(f'<div class="report-cell report-value-cell report4-metric-cell{negative}">{formatted}</div>')
        rows.append(f'<div class="{" ".join(row_classes)}">' + "".join(cells) + "</div>")

    return (
        '<div class="report-table-card report4-card">'
        f'<div class="report-table-title">{escape(title)}</div>'
        '<div class="report-table-scroll report4-scroll-fixed">'
        f'<div class="report-grid report-grid-dynamic report4-grid-fixed" style="{grid}">'
        + "".join(headers) + "".join(rows)
        + '</div></div></div>'
    )


# =========================================================
# 19.5 REFINAMIENTO EJECUTIVO 2026-08-13
# =========================================================
def render_dimension_filter_block(
    filter_label: str,
    widget_key: str,
    applied_key: str,
    available_options: list[str],
) -> list[str]:
    """
    Filtro compacto tipo Excel.

    Reglas:
    - Marcar/desmarcar dentro del formulario NO provoca rerun.
    - "Aplicar selección" usa exactamente las casillas elegidas.
    - "All / Seleccionar todo" restaura el universo completo.
    - Valores especiales como VARIOS, #N/A, Blanks u Other NO fuerzan
      nuevamente la selección total después de que el usuario aplicó
      explícitamente un subconjunto.
    """
    available_options = sorted({
        str(value).strip()
        for value in (available_options or [])
        if str(value).strip()
        and not is_forbidden_filter_label(str(value).strip())
    })

    if not available_options:
        st.info("No hay valores disponibles para filtrar en este bloque.")
        st.session_state[widget_key] = []
        st.session_state[applied_key] = []
        return []

    options_state_key = f"{widget_key}__available_options"
    pending_key = f"{widget_key}__pending_values"

    previous_options = list(st.session_state.get(options_state_key, []) or [])
    options_changed = set(previous_options) != set(available_options)
    had_pending_values = pending_key in st.session_state

    # La selección aplicada se lee directamente; no usamos el helper viejo
    # que obligaba a volver a "All" si VARIOS/#N/A no estaban seleccionados.
    stored_applied = st.session_state.get(applied_key)
    if stored_applied is None:
        stored_applied = available_options.copy()

    if had_pending_values:
        candidate_values = list(st.session_state.pop(pending_key) or [])
        selected = [v for v in candidate_values if v in available_options]
    elif options_changed:
        selected = available_options.copy()
    else:
        selected = [v for v in list(stored_applied or []) if v in available_options]

    if not selected:
        selected = available_options.copy()

    selected_set = set(selected)

    draft_keys = {}
    for idx, option in enumerate(available_options):
        draft_key = f"{widget_key}__draft_{idx}_{abs(hash(option))}"
        draft_keys[option] = draft_key

        if had_pending_values or options_changed or draft_key not in st.session_state:
            st.session_state[draft_key] = option in selected_set

    summary_text = (
        f"{filter_label} · {len(selected_set)}/{len(available_options)} seleccionados"
    )

    with st.expander(summary_text, expanded=False):
        with st.form(
            key=f"{widget_key}__excel_filter_form",
            clear_on_submit=False,
            border=False,
        ):
            for option in available_options:
                st.checkbox(option, key=draft_keys[option])

            action_col_1, action_col_2 = st.columns(2)

            with action_col_1:
                apply_clicked = st.form_submit_button(
                    "Aplicar selección",
                    use_container_width=True,
                )

            with action_col_2:
                all_clicked = st.form_submit_button(
                    "All / Seleccionar todo",
                    use_container_width=True,
                )

    if all_clicked:
        st.session_state[pending_key] = available_options.copy()
        st.session_state[applied_key] = available_options.copy()
        st.session_state[widget_key] = available_options.copy()
        st.session_state[options_state_key] = available_options.copy()
        st.rerun()

    if apply_clicked:
        chosen = [
            option
            for option in available_options
            if bool(st.session_state.get(draft_keys[option], False))
        ]

        # Cero seleccionados se interpreta como All para evitar tabla vacía.
        if not chosen:
            st.session_state[pending_key] = available_options.copy()
            st.session_state[applied_key] = available_options.copy()
            st.session_state[widget_key] = available_options.copy()
            st.session_state[options_state_key] = available_options.copy()
            st.rerun()

        st.session_state[applied_key] = chosen.copy()
        st.session_state[widget_key] = chosen.copy()
        st.session_state[options_state_key] = available_options.copy()
        st.rerun()

    applied_values = [
        value
        for value in list(st.session_state.get(applied_key, selected) or [])
        if value in available_options
    ]
    if not applied_values:
        applied_values = available_options.copy()

    st.session_state[widget_key] = applied_values.copy()
    st.session_state[options_state_key] = available_options.copy()

    return applied_values


def render_filter_download_row(
    filter_label: str,
    widget_key: str,
    applied_key: str,
    available_options: list[str],
    download_renderer,
) -> list[str]:
    """
    Coloca el filtro de dimensión y el botón individual de descarga
    en la misma fila para eliminar espacios verticales innecesarios.
    """
    filter_col, download_col = st.columns([12, 1], vertical_alignment="top")

    with filter_col:
        selected_values = render_dimension_filter_block(
            filter_label,
            widget_key,
            applied_key,
            available_options,
        )

    with download_col:
        download_renderer()

    return selected_values


def render_report_period_row(
    year_key: str,
    month_key: str,
    button_key: str,
    on_apply,
) -> tuple[int | None, int | None]:
    """
    Filtro de periodo con estado BORRADOR y estado APLICADO.

    Regla de experiencia:
    - Cambiar Año o Mes dentro del formulario NO ejecuta el reporte.
    - El periodo visible en resumen/tablas sigue siendo el último aplicado.
    - Solo al presionar "Aplicar" se reconstruye el reporte y se confirma
      el nuevo periodo.
    """
    years, latest_year, latest_month = get_available_year_month_options()

    if not years:
        st.info(
            "La información de ventas todavía no está disponible para habilitar Año y Mes."
        )
        return None, None

    applied_year_key = f"{year_key}__applied"
    applied_month_key = f"{month_key}__applied"
    draft_year_key = f"{year_key}__draft"
    draft_month_key = f"{month_key}__draft"

    # Estado aplicado: es el único que alimenta resúmenes y contenido visible.
    applied_year = st.session_state.get(
        applied_year_key,
        st.session_state.get(year_key, latest_year),
    )
    if applied_year not in years:
        applied_year = latest_year

    available_applied_months = get_available_months_for_year(int(applied_year))
    applied_fallback_month = (
        latest_month
        if int(applied_year) == int(latest_year)
        and latest_month in available_applied_months
        else (max(available_applied_months) if available_applied_months else latest_month)
    )

    applied_month = st.session_state.get(
        applied_month_key,
        st.session_state.get(month_key, applied_fallback_month),
    )
    if applied_month not in available_applied_months:
        applied_month = applied_fallback_month

    st.session_state[applied_year_key] = int(applied_year)
    st.session_state[applied_month_key] = int(applied_month)
    # Compatibilidad con el resto del código existente.
    st.session_state[year_key] = int(applied_year)
    st.session_state[month_key] = int(applied_month)

    # En un st.form los cambios no provocan rerun hasta presionar Aplicar.
    # Para permitir cambiar año y mes de una sola vez, el selector de mes usa
    # la unión de meses existentes en toda la base. La combinación se valida
    # contra el año elegido únicamente al enviar el formulario.
    all_months = sorted(
        {
            month
            for year_value in years
            for month in get_available_months_for_year(int(year_value))
        }
    )

    if not all_months:
        st.warning("No hay meses disponibles en la información procesada.")
        return int(applied_year), int(applied_month)

    if st.session_state.get(draft_year_key) not in years:
        st.session_state[draft_year_key] = int(applied_year)

    if st.session_state.get(draft_month_key) not in all_months:
        st.session_state[draft_month_key] = int(applied_month)

    with st.form(
        key=f"{button_key}__form",
        clear_on_submit=False,
        enter_to_submit=False,
        border=False,
    ):
        c1, c2, c3 = st.columns([1.1, 1.25, 0.95])

        with c1:
            draft_year = st.selectbox(
                "Año",
                options=years,
                key=draft_year_key,
            )

        with c2:
            draft_month = st.selectbox(
                "Mes de corte",
                options=all_months,
                key=draft_month_key,
                format_func=get_month_label,
            )

        with c3:
            st.markdown("<br>", unsafe_allow_html=True)
            submitted = st.form_submit_button(
                "Aplicar",
                use_container_width=True,
            )

    if submitted:
        valid_months_for_draft_year = get_available_months_for_year(int(draft_year))

        if int(draft_month) not in valid_months_for_draft_year:
            st.warning(
                f"{get_month_label(int(draft_month))} no está disponible para "
                f"{int(draft_year)}. Selecciona un mes válido antes de aplicar."
            )
        else:
            applied_ok = bool(on_apply(int(draft_year), int(draft_month)))

            if applied_ok:
                st.session_state[applied_year_key] = int(draft_year)
                st.session_state[applied_month_key] = int(draft_month)
                st.session_state[year_key] = int(draft_year)
                st.session_state[month_key] = int(draft_month)
                st.rerun()

    return (
        int(st.session_state[applied_year_key]),
        int(st.session_state[applied_month_key]),
    )

def get_independent_executive_summary(year: int, month: int) -> dict | None:
    """Resumen por pestaña sin depender de que Base MTD haya sido construida."""
    required = [
        st.session_state.get("df_processed_sales"),
        st.session_state.get("df_plan_client"),
        st.session_state.get("df_plan_sku"),
        st.session_state.get("df_fcst_client"),
        st.session_state.get("df_fcst_sku"),
    ]
    if any(df is None for df in required):
        return None
    cache_key = f"__exec_summary_{int(year)}_{int(month)}"
    if cache_key not in st.session_state:
        try:
            st.session_state[cache_key] = data_processor.build_executive_summary_payload(
                *required,
                selected_year=int(year),
                selected_month=int(month),
            )
        except Exception as exc:
            st.warning(f"No fue posible calcular el resumen ejecutivo. Detalle: {exc}")
            return None
    return st.session_state.get(cache_key)


def render_independent_executive_summary(year: int, month: int) -> None:
    summary = get_independent_executive_summary(year, month)
    if not summary:
        return
    st.markdown("### Resumen ejecutivo")
    currency = get_currency_kpi_suffix()
    cards = [
        ("MTD ACT TOTAL", summary["mtd_act_total_k"], "Valor real del mes de corte.", "$", "blue"),
        ("YTD ACT TOTAL", summary["ytd_act_total_k"], "Acumulado real de enero al corte.", "Σ", "blue"),
        ("MTD PLAN TOTAL", summary["mtd_plan_total_k"], "Plan del mes de corte.", "↗", "orange"),
        ("YTD PLAN TOTAL", summary["ytd_plan_total_k"], "Plan acumulado de enero al corte.", "Σ", "orange"),
        ("MTD FCST TOTAL", summary["mtd_fcst_total_k"], "Forecast del mes de corte.", "F", "pink"),
        ("YTD FCST TOTAL", summary["ytd_fcst_total_k"], "Forecast acumulado de enero al corte.", "Σ", "pink"),
        ("BTS ACTUAL", summary["bts_actual_k"], "BTS acumulado desde octubre al corte.", "▣", "green"),
        ("BTS PY COMPLETO", summary["bts_py_full_k"], "Ciclo BTS previo completo como referencia.", "↺", "green"),
    ]
    for start in (0, 4):
        cols = st.columns(4)
        for col, (title, value, desc, icon, color) in zip(cols, cards[start:start+4]):
            with col:
                st.markdown(styles.build_base_mtd_kpi_card(
                    title=f"{title} ({currency})",
                    value=f"{convert_monetary_value(value * 1000) / 1000:,.0f}",
                    description=desc,
                    icon=icon,
                    color=color,
                ), unsafe_allow_html=True)


def build_report_4_table_html(title: str, df_table) -> str:
    """
    Ranking con TOP visible como primera columna.

    Ajustes visuales:
    - TOP angosto y centrado.
    - Client Name con mayor ancho para evitar nombres cortados.
    - Cliente alineado a la izquierda.
    - Métricas con ancho uniforme.
    """
    if df_table is None or df_table.empty:
        return (
            '<div class="report-table-card">'
            f'<div class="report-table-title">{escape(title)}</div>'
            '<div class="report-empty-state">-</div></div>'
        )

    preferred = [
        "TOP",
        "Client Name",
        "Cliente",
        "Actual",
        "Plan",
        "Var VS Plan",
        "%Var VS Plan",
        "Fcst",
        "Var VS Fcst",
        "%Var VS Fcst",
        "PY",
        "Var VS PY",
        "%Var VS PY",
    ]
    visible = [column for column in preferred if column in df_table.columns]

    metric_classes = {
        "Actual": "report-header-actual",
        "Plan": "report-header-plan",
        "Fcst": "report-header-fcst",
        "PY": "report-header-py",
        "Var VS Plan": "report-header-var-plan",
        "%Var VS Plan": "report-header-var-plan",
        "Var VS Fcst": "report-header-var-fcst",
        "%Var VS Fcst": "report-header-var-fcst",
        "Var VS PY": "report-header-var-py",
        "%Var VS PY": "report-header-var-py",
    }

    widths = []
    minimum_width = 0

    for column in visible:
        if column == "TOP":
            widths.append("68px")
            minimum_width += 68
        elif column == "Client Name":
            widths.append("320px")
            minimum_width += 320
        elif column == "Cliente":
            widths.append("112px")
            minimum_width += 112
        else:
            widths.append("118px")
            minimum_width += 118

    grid_style = (
        f"grid-template-columns:{' '.join(widths)};"
        f"min-width:{minimum_width}px;"
        "width:100%;"
    )

    headers = []
    for column in visible:
        header_class = (
            "report-header-neutral"
            if column in {"TOP", "Client Name", "Cliente"}
            else metric_classes.get(column, "report-header-neutral")
        )

        extra_class = ""
        if column == "TOP":
            extra_class = " report4-top-header"
        elif column == "Client Name":
            extra_class = " report4-name-display-header"
        elif column == "Cliente":
            extra_class = " report4-code-display-header"

        headers.append(
            f'<div class="report-cell report-header {header_class}{extra_class}">'
            f'{escape(str(column).upper())}</div>'
        )

    rows = []

    for _, row in df_table.iterrows():
        row_class = "report-row"

        if bool(
            row.get("__is_total__", False)
            or row.get("__is_group_summary__", False)
        ):
            row_class += " report-total"

        if bool(
            row.get("__is_grand_total__", False)
            or row.get("__is_highlight__", False)
        ):
            row_class += " report-highlight"

        cells = []

        for column in visible:
            value = row.get(column)

            if column == "TOP":
                top_value = safe_float(value, 0.0)
                text = "" if top_value <= 0 else f"{int(top_value):,}"
                cells.append(
                    f'<div class="report-cell report4-top-cell">{escape(text)}</div>'
                )
                continue

            if column == "Client Name":
                text = "" if value is None else str(value).strip()
                cells.append(
                    f'<div class="report-cell report4-name-display-cell" '
                    f'title="{escape(text)}">{escape(text)}</div>'
                )
                continue

            if column == "Cliente":
                text = "" if value is None else str(value).strip()
                cells.append(
                    f'<div class="report-cell report4-code-display-cell" '
                    f'title="{escape(text)}">{escape(text)}</div>'
                )
                continue

            is_percent = str(column).startswith("%")
            negative_class = (
                " report-negative"
                if safe_float(value) < 0
                else ""
            )

            cells.append(
                f'<div class="report-cell report-value-cell{negative_class}">'
                f'{format_monetary_value(value, is_percent=is_percent)}</div>'
            )

        rows.append(
            f'<div class="{row_class}">'
            + "".join(cells)
            + "</div>"
        )

    return (
        '<div class="report-table-card report4-card">'
        f'<div class="report-table-title">{escape(title)}</div>'
        '<div class="report-table-scroll report4-modern-scroll">'
        f'<div class="report-grid report-grid-dynamic report4-modern-grid" '
        f'style="{grid_style}">'
        + "".join(headers)
        + "".join(rows)
        + "</div></div></div>"
    )


def render_client_search(payload: dict) -> None:
    """
    Búsqueda parcial tipo Ctrl+F sobre el ranking completo MTD/YTD.

    Los importes se muestran con el mismo formato ejecutivo de los reportes:
    miles, sin decimales, separador de miles y negativos entre paréntesis.
    """
    st.markdown("### Buscar cliente")
    st.caption(
        "Escribe una parte del nombre o del código. "
        "La búsqueda revisa todos los clientes considerados en el periodo, "
        "no solamente el Top 15."
    )

    query = st.text_input(
        "Buscar por nombre o código",
        key="report4_client_search",
        placeholder="Ej. amazon, papel, C018",
    )
    query = str(query or "").strip().lower()

    if not query:
        return

    has_match = False

    for label, key in (
        ("MTD", "mtd_detail_table"),
        ("YTD", "ytd_detail_table"),
    ):
        df = payload.get(key)

        if df is None or df.empty:
            continue

        client_name_series = (
            df["Client Name"].astype(str)
            if "Client Name" in df.columns
            else data_processor.pd.Series("", index=df.index)
        )
        client_code_series = (
            df["Cliente"].astype(str)
            if "Cliente" in df.columns
            else data_processor.pd.Series("", index=df.index)
        )

        mask = (
            client_name_series.str.lower().str.contains(query, regex=False)
            | client_code_series.str.lower().str.contains(query, regex=False)
        )

        matches = df.loc[mask].copy()

        if matches.empty:
            continue

        has_match = True
        st.markdown(f"**{label}: {len(matches)} coincidencia(s)**")

        display_rows = []

        for _, row in matches.head(25).iterrows():
            top_value = safe_float(row.get("TOP"), 0.0)

            display_rows.append(
                {
                    "TOP": "" if top_value <= 0 else f"{int(top_value):,}",
                    "Client Name": str(row.get("Client Name", "") or "").strip(),
                    "Cliente": str(row.get("Cliente", "") or "").strip(),
                    "Actual": format_monetary_value(row.get("Actual")),
                    "Plan": format_monetary_value(row.get("Plan")),
                    "Fcst": format_monetary_value(row.get("Fcst")),
                    "PY": format_monetary_value(row.get("PY")),
                }
            )

        display_df = data_processor.pd.DataFrame(display_rows)

        st.dataframe(
            display_df,
            hide_index=True,
            use_container_width=True,
            column_config={
                "TOP": st.column_config.TextColumn("TOP", width="small"),
                "Client Name": st.column_config.TextColumn(
                    "Client Name",
                    width="large",
                ),
                "Cliente": st.column_config.TextColumn(
                    "Cliente",
                    width="small",
                ),
                "Actual": st.column_config.TextColumn("Actual", width="small"),
                "Plan": st.column_config.TextColumn("Plan", width="small"),
                "Fcst": st.column_config.TextColumn("Fcst", width="small"),
                "PY": st.column_config.TextColumn("PY", width="small"),
            },
        )

    if not has_match:
        st.info(
            "No se encontraron clientes que contengan ese texto o código "
            "dentro del periodo seleccionado."
        )


# =========================================================
# 20. EJECUCIÓN PRINCIPAL
# =========================================================
main()