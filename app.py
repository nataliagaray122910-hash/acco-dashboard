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

import config
import data_loader
import data_processor
import exports
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
            "0.00%" if is_percent else ("" if allow_blank else "0")
        )

    numeric_value = float(value)

    if is_percent:
        if numeric_value < 0:
            return f"({abs(numeric_value) * 100:,.2f}%)"
        return f"{numeric_value * 100:,.2f}%"

    converted_value = convert_monetary_value(numeric_value)
    value_k = float(converted_value) / 1000
    rounded_value = round(value_k)

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
    Carpeta temporal dentro del entorno de la app.
    En Streamlit Cloud puede perderse si la app reinicia; sirve para Fase 1.
    """
    folder_name = getattr(config, "PERSISTENT_DATA_PATH", "persistent_data")
    folder = Path(folder_name)
    folder.mkdir(parents=True, exist_ok=True)
    return folder


def get_persistent_data_file() -> Path:
    return get_persistent_data_folder() / "latest_dashboard_data.pkl"


def delete_persistent_data() -> bool:
    """
    Borra la carga administrativa guardada para viewers y limpia datos calculados
    de la sesión actual.
    """
    try:
        persistent_file = get_persistent_data_file()

        if persistent_file.exists():
            persistent_file.unlink()

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
            "persistent_data_loaded": False,
            "persistent_data_metadata": None,
            "suppress_persistent_autoload": True,
            "sales_upload_signature": "",
            "plan_client_upload_signature": "",
            "plan_sku_upload_signature": "",
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
    return get_persistent_data_file().exists()


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
    sin subir archivos. Es persistencia temporal de Fase 1.
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
        "df_sales": st.session_state.get("df_sales"),
        "df_plan_client": st.session_state.get("df_plan_client"),
        "df_plan_sku": st.session_state.get("df_plan_sku"),
        "df_processed_sales": st.session_state.get("df_processed_sales"),
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
        with open(get_persistent_data_file(), "wb") as file:
            pickle.dump(payload, file)

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
    Esto permite que viewers consulten reportes sin cargar archivos.
    """
    if st.session_state.get("persistent_data_loaded"):
        return True

    if not persistent_data_exists():
        return False

    try:
        with open(get_persistent_data_file(), "rb") as file:
            payload = pickle.load(file)

        st.session_state["df_sales"] = payload.get("df_sales")
        st.session_state["df_plan_client"] = payload.get("df_plan_client")
        st.session_state["df_plan_sku"] = payload.get("df_plan_sku")
        st.session_state["df_processed_sales"] = payload.get("df_processed_sales")

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
    """
    if is_admin_user():
        return config.MAIN_MENU_OPTIONS

    return [option for option in config.MAIN_MENU_OPTIONS if option != "Carga de datos"]


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

        st.text_input("Usuario", key="input_user")
        st.text_input("Contraseña", type="password", key="input_password")

        st.markdown("<br>", unsafe_allow_html=True)
        st.button("Iniciar sesión", on_click=check_login, use_container_width=True)

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

    without_kens_options = get_filter_options_from_table(
        payload["mtd_without_kens_table"],
        lambda row: str(row.get("Oficina de Ventas", "")).strip(),
    )
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

    kens_options = get_filter_options_from_multiple_tables(
        [
            payload["mtd_kens_table"],
            payload["ytd_kens_table"],
        ],
        lambda row: str(row.get("Oficina de Ventas", "")).strip(),
    )
    applied_kens_labels = get_valid_applied_filter_values(
        "report1_kens_dimension_applied",
        kens_options,
    )

    filtered_mtd_kens = filter_report_1_with_kens_table(
        payload["mtd_kens_table"],
        applied_kens_labels,
    )
    filtered_ytd_kens = filter_report_1_with_kens_table(
        payload["ytd_kens_table"],
        applied_kens_labels,
    )

    return {
        "summary": payload["summary"],
        "report_title": build_report_context_title(
            "Reporte 1 - Channel Corp",
            payload["summary"]["latest_year"],
            payload["summary"]["latest_month"],
        ),
        "mtd_without_kens": convert_report_table_for_export(filtered_mtd_without_kens),
        "ytd_without_kens": convert_report_table_for_export(filtered_ytd_without_kens),
        "mtd_kens": convert_report_table_for_export(filtered_mtd_kens),
        "ytd_kens": convert_report_table_for_export(filtered_ytd_kens),
    }


def get_current_report_2_segment_export_tables() -> dict | None:
    payload = st.session_state.get("report2_payload")
    if payload is None:
        return None

    segment_region_options = get_filter_options_from_table(
        payload["mtd_segment_region_table"],
        build_report_2_segment_region_display_label,
    )
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

    return {
        "summary": payload["summary"],
        "report_title": build_report_context_title(
            "Reporte 2 - Segment x Region",
            payload["summary"]["latest_year"],
            payload["summary"]["latest_month"],
        ),
        "mtd": convert_report_table_for_export(filtered_mtd_segment),
        "ytd": convert_report_table_for_export(filtered_ytd_segment),
    }


def get_current_report_2_category_export_tables() -> dict | None:
    payload = st.session_state.get("report2_category_payload")
    if payload is None:
        return None

    category_options = get_filter_options_from_table(
        payload["mtd_category_table"],
        lambda row: str(row.get("Category", "")).strip(),
    )
    applied_category_labels = get_valid_applied_filter_values(
        "report2_category_dimension_applied",
        category_options,
    )

    filtered_mtd_category = filter_report_2_category_table(
        payload["mtd_category_table"],
        applied_category_labels,
    )
    filtered_ytd_category = filter_report_2_category_table(
        payload["ytd_category_table"],
        applied_category_labels,
    )

    return {
        "summary": payload["summary"],
        "report_title": build_report_context_title(
            "Reporte 2 - Category",
            payload["summary"]["latest_year"],
            payload["summary"]["latest_month"],
        ),
        "mtd": convert_report_table_for_export(filtered_mtd_category),
        "ytd": convert_report_table_for_export(filtered_ytd_category),
    }


def get_current_report_3_export_tables() -> dict | None:
    payload = st.session_state.get("report3_payload")
    if payload is None:
        return None

    channel_options = get_filter_options_from_table(
        payload["mtd_channel_table"],
        build_report_3_display_label,
    )
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

    return {
        "summary": payload["summary"],
        "report_title": build_report_context_title(
            "Reporte 3 - Channel",
            payload["summary"]["latest_year"],
            payload["summary"]["latest_month"],
        ),
        "mtd": convert_report_table_for_export(filtered_mtd_channel),
        "ytd": convert_report_table_for_export(filtered_ytd_channel),
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
        # respetando el orden fijo del Excel y mostrando el grupo de cada cliente.
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
            "validators.py, data_processor.py, exports.py y app.py"
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
    channel_value = str(row.get("Channel", "")).strip()
    if channel_value == "GOBA":
        return "BARRILITO"
    return channel_value


def get_filter_options_from_table(
    df_table,
    label_builder,
) -> list[str]:
    if df_table is None or df_table.empty:
        return []

    options: list[str] = []

    for _, row in df_table.iterrows():
        if is_special_report_row(row):
            continue

        label_value = str(label_builder(row)).strip()
        if label_value:
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
            if is_special_report_row(row):
                continue

            label_value = str(label_builder(row)).strip()
            if label_value:
                options.append(label_value)

    return sorted(set(options))


def get_valid_applied_filter_values(
    applied_key: str,
    available_options: list[str],
) -> list[str]:
    applied_values = st.session_state.get(applied_key)

    if not available_options:
        return []

    if not applied_values:
        return available_options.copy()

    valid_values = [value for value in applied_values if value in available_options]

    if not valid_values:
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


def render_dimension_filter_block(
    filter_label: str,
    widget_key: str,
    applied_key: str,
    available_options: list[str],
) -> list[str]:
    if not available_options:
        st.info("No hay valores disponibles para filtrar en este bloque.")
        return []

    default_values = get_valid_applied_filter_values(applied_key, available_options)

    current_widget_values = st.session_state.get(widget_key)
    if current_widget_values is None:
        st.session_state[widget_key] = default_values.copy()
    else:
        valid_widget_values = [
            value for value in current_widget_values if value in available_options
        ]
        if not valid_widget_values:
            valid_widget_values = default_values.copy()
        st.session_state[widget_key] = valid_widget_values

    st.multiselect(
        filter_label,
        options=available_options,
        key=widget_key,
        placeholder="Selecciona uno o varios valores",
    )

    return get_valid_applied_filter_values(applied_key, available_options)


def filter_report_1_without_kens_table(
    df_table,
    selected_labels: list[str],
):
    if df_table is None or df_table.empty:
        return df_table

    selected_set = set(selected_labels)

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


def filter_report_1_with_kens_table(
    df_table,
    selected_labels: list[str],
):
    if df_table is None or df_table.empty:
        return df_table

    selected_set = set(selected_labels)

    normal_rows = df_table[
        ~df_table["__is_total__"].fillna(False)
        & ~df_table["__is_highlight__"].fillna(False)
        & ~df_table.get("__is_grand_total__", False)
    ].copy()

    filtered_normals = normal_rows[
        normal_rows["Oficina de Ventas"].astype(str).isin(selected_set)
    ].copy()

    highlight_template = df_table[df_table["__is_highlight__"].fillna(False)].copy()

    rows = []

    for _, row in filtered_normals.iterrows():
        rows.append(dict(row))

    if not highlight_template.empty:
        highlight_row_template = highlight_template.iloc[0].to_dict()

        total_actual = filtered_normals["Actual"].apply(safe_float).sum()
        total_py = filtered_normals["PY"].apply(safe_float).sum()

        original_plan = highlight_row_template.get("Plan")
        total_plan = None if is_blank_number(original_plan) else safe_float(original_plan)

        rows.append(
            recalculate_row_metrics(
                highlight_row_template,
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

    selected_set = set(selected_labels)
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

    selected_set = set(selected_labels)
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

    selected_set = set(selected_labels)
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

    selected_set = set(selected_labels)
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
        '<div class="horizontal-table-card">'
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
        '<div class="horizontal-table-card">'
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
        Mostrar el comparativo ejecutivo MTD / YTD del Canal Corporativo, con ACCO + BARRILITO
        por separado de KENS, usando BASE SAP y Plan2026 by Client.
        """
    )
    st.markdown(report_box_html, unsafe_allow_html=True)

    st.markdown("### 1. Construir Reporte 1")
    st.markdown(
        '<div class="report-note">Primero construye el reporte para habilitar la vista. Después podrás cambiar el Año, el Mes y la primera columna del bloque superior. En el bloque WITH KENS solo se conserva el filtro de oficina de ventas.</div>',
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
    st.markdown("### 2. Resumen del corte")

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
                "Bloque superior",
                "ACCO + BARRILITO",
                "Comparativos WITHOUT KENS",
            ),
            unsafe_allow_html=True,
        )

    with col3:
        st.markdown(
            styles.build_info_card(
                "Bloque inferior",
                "KENS",
                "Comparativos WITH KENS",
            ),
            unsafe_allow_html=True,
        )

    st.markdown("---")
    st.markdown("### 3. Channel Corp MTD / YTD")

    selected_year_without_kens, selected_month_without_kens = render_period_filter_block(
        "Filtro del bloque: Channel Corp WITHOUT KENS",
        "report1_without_kens_year",
        "report1_without_kens_month",
    )

    payload = st.session_state.get("report1_payload")

    without_kens_options = get_filter_options_from_table(
        payload["mtd_without_kens_table"],
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
            "Aplicar filtro - Channel Corp WITHOUT KENS",
            key="btn_report1_without_kens",
            use_container_width=True,
        ):
            sync_dimension_filter_to_applied_state(
                "report1_without_kens_dimension_widget",
                "report1_without_kens_dimension_applied",
                without_kens_options,
            )
            run_report_1_build(
                selected_year=selected_year_without_kens,
                selected_month=selected_month_without_kens,
            )

    payload = st.session_state.get("report1_payload")

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
        kens_export_options = get_filter_options_from_multiple_tables(
            [
                payload["mtd_kens_table"],
                payload["ytd_kens_table"],
            ],
            lambda row: str(row.get("Oficina de Ventas", "")).strip(),
        )

        report_1_bytes = exports.build_report_1_excel_bytes(
            mtd_without_kens_df=convert_report_table_for_export(filtered_mtd_without_kens),
            ytd_without_kens_df=convert_report_table_for_export(filtered_ytd_without_kens),
            mtd_kens_df=convert_report_table_for_export(
                filter_report_1_with_kens_table(
                    payload["mtd_kens_table"],
                    get_valid_applied_filter_values(
                        "report1_kens_dimension_applied",
                        kens_export_options,
                    ),
                )
            ),
            ytd_kens_df=convert_report_table_for_export(
                filter_report_1_with_kens_table(
                    payload["ytd_kens_table"],
                    get_valid_applied_filter_values(
                        "report1_kens_dimension_applied",
                        kens_export_options,
                    ),
                )
            ),
            report_title=build_report_context_title(
                "Reporte 1 - Channel Corp",
                selected_year_without_kens,
                selected_month_without_kens,
            ),
        )
        render_icon_download_button(
            data=report_1_bytes,
            file_name=build_excel_filename(
                "reporte_1",
                selected_year_without_kens,
                selected_month_without_kens,
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
                    "MTD Channel CORP WITHOUT KENS",
                    selected_year_without_kens,
                    selected_month_without_kens,
                ),
                filtered_mtd_without_kens,
            ),
            unsafe_allow_html=True,
        )

    with top_right:
        st.markdown(
            build_report_1_table_html(
                build_report_context_title(
                    "YTD Channel CORP WITHOUT KENS",
                    selected_year_without_kens,
                    selected_month_without_kens,
                ),
                filtered_ytd_without_kens,
            ),
            unsafe_allow_html=True,
        )

    st.markdown("---")
    st.markdown("### 4. Channel Corp MTD / YTD WITH KENS")

    payload = st.session_state.get("report1_payload")

    kens_options = get_filter_options_from_multiple_tables(
        [
            payload["mtd_kens_table"],
            payload["ytd_kens_table"],
        ],
        lambda row: str(row.get("Oficina de Ventas", "")).strip(),
    )

    render_dimension_filter_block(
        "OFICINA DE VENTAS",
        "report1_kens_dimension_widget",
        "report1_kens_dimension_applied",
        kens_options,
    )

    if st.button(
        "Aplicar filtro - Channel Corp WITH KENS",
        key="btn_report1_kens_dimension_only",
        use_container_width=True,
    ):
        sync_dimension_filter_to_applied_state(
            "report1_kens_dimension_widget",
            "report1_kens_dimension_applied",
            kens_options,
        )

    payload = st.session_state.get("report1_payload")

    applied_kens_labels = get_valid_applied_filter_values(
        "report1_kens_dimension_applied",
        kens_options,
    )

    filtered_mtd_kens = filter_report_1_with_kens_table(
        payload["mtd_kens_table"],
        applied_kens_labels,
    )
    filtered_ytd_kens = filter_report_1_with_kens_table(
        payload["ytd_kens_table"],
        applied_kens_labels,
    )

    st.markdown(
        '<div class="report-note">En este bloque se muestran los renglones informativos por oficina de ventas y, al final, el renglón consolidado de <b>IT: IT Distributors</b>, que permanece visible y se recalcula conforme al filtro seleccionado.</div>',
        unsafe_allow_html=True,
    )

    bottom_left, bottom_right = st.columns(2)

    with bottom_left:
        st.markdown(
            build_report_1_table_html(
                build_report_context_title(
                    "MTD Channel CORP WITH KENS",
                    selected_year_without_kens,
                    selected_month_without_kens,
                ),
                filtered_mtd_kens,
            ),
            unsafe_allow_html=True,
        )

    with bottom_right:
        st.markdown(
            build_report_1_table_html(
                build_report_context_title(
                    "YTD Channel CORP WITH KENS",
                    selected_year_without_kens,
                    selected_month_without_kens,
                ),
                filtered_ytd_kens,
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

    st.markdown("### 1. Construir Reporte Segment x Region")
    st.button(
        "Construir Reporte Segment x Region",
        on_click=run_report_2_build,
        use_container_width=True,
    )

    payload = st.session_state.get("report2_payload")

    st.markdown("---")
    st.markdown("### 2. Resumen del corte")

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
                    "ACCO / BARRILITO / KENS",
                    "Segmentos consolidados visibles en esta vista",
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
    st.markdown("### 3. Segment x Region MTD / YTD")

    payload = st.session_state.get("report2_payload")

    if payload is None:
        st.info("Aún no se ha construido el bloque Segment x Region.")
    else:
        selected_year_segment, selected_month_segment = render_period_filter_block(
            "Filtro del bloque: Segment x Region",
            "report2_segment_year",
            "report2_segment_month",
        )

        segment_region_options = get_filter_options_from_table(
            payload["mtd_segment_region_table"],
            build_report_2_segment_region_display_label,
        )

        render_dimension_filter_block(
            "SEGMENTO / REGIÓN",
            "report2_segment_dimension_widget",
            "report2_segment_dimension_applied",
            segment_region_options,
        )

        if selected_year_segment is not None and selected_month_segment is not None:
            if st.button(
                "Aplicar filtro - Segment x Region",
                key="btn_report2_segment",
                use_container_width=True,
            ):
                sync_dimension_filter_to_applied_state(
                    "report2_segment_dimension_widget",
                    "report2_segment_dimension_applied",
                    segment_region_options,
                )
                run_report_2_build(
                    selected_year=selected_year_segment,
                    selected_month=selected_month_segment,
                )

        payload = st.session_state.get("report2_payload")

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
                mtd_segment_df=convert_report_table_for_export(filtered_mtd_segment),
                ytd_segment_df=convert_report_table_for_export(filtered_ytd_segment),
                report_title=build_report_context_title(
                    "Reporte 2 - Segment x Region",
                    selected_year_segment,
                    selected_month_segment,
                ),
            )
            render_icon_download_button(
                data=segment_bytes,
                file_name=build_excel_filename(
                    "reporte_2_segment_region",
                    selected_year_segment,
                    selected_month_segment,
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
                        selected_year_segment,
                        selected_month_segment,
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
                        selected_year_segment,
                        selected_month_segment,
                    ),
                    filtered_ytd_segment,
                    "SEGMENTO / REGIÓN",
                    "segment_region",
                ),
                unsafe_allow_html=True,
            )

    st.markdown("---")
    st.markdown("### 4. Construir Reporte Category")
    st.button(
        "Construir Reporte Category",
        on_click=run_report_2_category_build,
        use_container_width=True,
    )

    payload_category = st.session_state.get("report2_category_payload")

    st.markdown("---")
    st.markdown("### 5. Category MTD / YTD")

    if payload_category is None:
        st.info("Aún no se ha construido el Reporte Category.")
    else:
        selected_year_category, selected_month_category = render_period_filter_block(
            "Filtro del bloque: Category",
            "report2_category_year",
            "report2_category_month",
        )

        category_options = get_filter_options_from_table(
            payload_category["mtd_category_table"],
            lambda row: str(row.get("Category", "")).strip(),
        )

        render_dimension_filter_block(
            "CATEGORY",
            "report2_category_dimension_widget",
            "report2_category_dimension_applied",
            category_options,
        )

        if selected_year_category is not None and selected_month_category is not None:
            if st.button(
                "Aplicar filtro - Category",
                key="btn_report2_category",
                use_container_width=True,
            ):
                sync_dimension_filter_to_applied_state(
                    "report2_category_dimension_widget",
                    "report2_category_dimension_applied",
                    category_options,
                )
                run_report_2_category_build(
                    selected_year=selected_year_category,
                    selected_month=selected_month_category,
                )

        payload_category = st.session_state.get("report2_category_payload")

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
                mtd_category_df=convert_report_table_for_export(filtered_mtd_category),
                ytd_category_df=convert_report_table_for_export(filtered_ytd_category),
                report_title=build_report_context_title(
                    "Reporte 2 - Category",
                    selected_year_category,
                    selected_month_category,
                ),
            )
            render_icon_download_button(
                data=category_bytes,
                file_name=build_excel_filename(
                    "reporte_2_category",
                    selected_year_category,
                    selected_month_category,
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
                        selected_year_category,
                        selected_month_category,
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
                        selected_year_category,
                        selected_month_category,
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

    st.markdown("### 1. Construir Reporte 3")
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
    st.markdown("### 2. Resumen del corte")

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
                "ACCO / ECO / EXP / BARRILITO / KEN",
                "Canales consolidados visibles en esta vista",
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
    st.markdown("### 3. Channel MTD / YTD")

    selected_year_channel, selected_month_channel = render_period_filter_block(
        "Filtro del bloque: Channel",
        "report3_channel_year",
        "report3_channel_month",
    )

    payload = st.session_state.get("report3_payload")

    channel_options = get_filter_options_from_table(
        payload["mtd_channel_table"],
        build_report_3_display_label,
    )

    render_dimension_filter_block(
        "CHANNEL",
        "report3_channel_dimension_widget",
        "report3_channel_dimension_applied",
        channel_options,
    )

    if selected_year_channel is not None and selected_month_channel is not None:
        if st.button(
            "Aplicar filtro - Channel",
            key="btn_report3_channel",
            use_container_width=True,
        ):
            sync_dimension_filter_to_applied_state(
                "report3_channel_dimension_widget",
                "report3_channel_dimension_applied",
                channel_options,
            )
            run_report_3_build(
                selected_year=selected_year_channel,
                selected_month=selected_month_channel,
            )

    payload = st.session_state.get("report3_payload")

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
            mtd_channel_df=convert_report_table_for_export(filtered_mtd_channel),
            ytd_channel_df=convert_report_table_for_export(filtered_ytd_channel),
            report_title=build_report_context_title(
                "Reporte 3 - Channel",
                selected_year_channel,
                selected_month_channel,
            ),
        )
        render_icon_download_button(
            data=report_3_bytes,
            file_name=build_excel_filename(
                "reporte_3",
                selected_year_channel,
                selected_month_channel,
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
                    selected_year_channel,
                    selected_month_channel,
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
                    selected_year_channel,
                    selected_month_channel,
                ),
                filtered_ytd_channel,
            ),
            unsafe_allow_html=True,
        )

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


def format_report_4_value(value, is_percent: bool = False) -> str:
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
                f'<div class="report-cell report-value-cell{state_class} {"report-negative" if actual_negative else ""}">{format_report_4_value(actual_value)}</div>',
                f'<div class="report-cell report-value-cell{state_class} {"report-negative" if plan_negative else ""}">{format_report_4_value(plan_value)}</div>',
                f'<div class="report-cell report-value-cell{state_class} {"report-negative" if py_negative else ""}">{format_report_4_value(py_value)}</div>',
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
        Mostrar el comparativo ejecutivo MTD / YTD del ranking fijo de clientes,
        cruzando BASE SAP y Plan2026 by Client mediante código de cliente.
        """
    )
    st.markdown(report_box_html, unsafe_allow_html=True)

    st.markdown("### 1. Construir Reporte 4")
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
    st.markdown("### 2. Resumen del corte")

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
                "Ranking fijo",
                "Orden definido por negocio; no se reordena por GSNR",
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
    st.markdown("### 3. Ranking de Clientes MTD / YTD")

    selected_year_clients, selected_month_clients = render_period_filter_block(
        "Filtro del bloque: Ranking de Clientes",
        "report4_clients_year",
        "report4_clients_month",
    )

    if selected_year_clients is not None and selected_month_clients is not None:
        if st.button(
            "Aplicar filtro - Ranking de Clientes",
            key="btn_report4_clients",
            use_container_width=True,
        ):
            run_report_4_build(
                selected_year=selected_year_clients,
                selected_month=selected_month_clients,
            )

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

    render_report_4_detail_block(
        "Vista ejecutiva: Top 15 + bloques resumen",
        payload["mtd_top_clients_table"],
        payload["ytd_top_clients_table"],
        payload["summary"]["latest_year"],
        payload["summary"]["latest_month"],
    )

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
                "7",
                "config.py, styles.py, data_loader.py, validators.py, "
                "data_processor.py, exports.py y app.py",
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

    st.markdown(
        '<div class="section-title">Carga de datos</div>',
        unsafe_allow_html=True,
    )

    upload_box_html = styles.build_info_box(
        """
        <b>Objetivo de esta etapa:</b><br>
        Cargar correctamente la base de ventas y los archivos comparativos
        de plan por cliente y plan por SKU, manteniendo persistencia y vista previa.
        """
    )
    st.markdown(upload_box_html, unsafe_allow_html=True)


    # =====================================================
    # CARGA AUTOMÁTICA DESDE SHAREPOINT SINCRONIZADO
    # =====================================================
    st.markdown("### Carga automática desde SharePoint sincronizado")
    st.caption(
        "Esta opción lee el Excel desde la carpeta de SharePoint sincronizada con OneDrive. "
        "La carga manual se conserva como respaldo."
    )

    if getattr(config, "SYNCED_SHAREPOINT_ENABLED", False):
        st.button(
            getattr(
                config,
                "SYNCED_SHAREPOINT_BUTTON_LABEL",
                "Actualizar desde SharePoint sincronizado",
            ),
            on_click=load_synced_sharepoint_file_to_session,
            use_container_width=True,
        )
    else:
        st.warning("La carga desde SharePoint sincronizado está deshabilitada en config.py.")

    st.markdown("---")

    # =====================================================
    # 1. ARCHIVO DE VENTAS
    # =====================================================
    st.markdown("### 1. Archivo de ventas")
    uploaded_sales = st.file_uploader(
        "Carga el archivo de ventas",
        type=config.ALLOWED_FILE_TYPES,
        key=f"{config.FILE_KEY_SALES}_{st.session_state.get('upload_reset_counter', 0)}",
    )

    if uploaded_sales is not None:
        try:
            st.session_state["suppress_persistent_autoload"] = True
            df_sales = data_loader.load_sales_file(uploaded_sales)
            is_valid_sales, missing_sales = validators.validate_required_columns(
                df_sales,
                config.EXPECTED_COLUMNS_SALES,
            )

            st.session_state["df_sales"] = df_sales
            st.session_state["sales_valid"] = is_valid_sales
            st.session_state["sales_missing_columns"] = missing_sales
            st.session_state["sales_file_name"] = uploaded_sales.name

        except Exception as exc:
            st.error(f"{config.MSG_UPLOAD_ERROR} Detalle: {exc}")

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

    st.markdown("---")

    # =====================================================
    # 2. ARCHIVO DE PLAN POR CLIENTE
    # =====================================================
    st.markdown("### 2. Archivo de plan por cliente")
    uploaded_plan_client = st.file_uploader(
        "Carga el archivo Plan2026 by Client",
        type=config.ALLOWED_FILE_TYPES,
        key=f"{config.FILE_KEY_PLAN_CLIENT}_{st.session_state.get('upload_reset_counter', 0)}",
    )

    if uploaded_plan_client is not None:
        try:
            st.session_state["suppress_persistent_autoload"] = True
            df_plan_client = data_loader.load_plan_client_file(uploaded_plan_client)
            is_valid_plan_client, missing_plan_client = validators.validate_required_columns(
                df_plan_client,
                config.EXPECTED_COLUMNS_PLAN_CLIENT,
            )

            st.session_state["df_plan_client"] = df_plan_client
            st.session_state["plan_client_valid"] = is_valid_plan_client
            st.session_state["plan_client_missing_columns"] = missing_plan_client
            st.session_state["plan_client_file_name"] = uploaded_plan_client.name

        except Exception as exc:
            st.error(f"{config.MSG_UPLOAD_ERROR} Detalle: {exc}")

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

    st.markdown("---")

    # =====================================================
    # 3. ARCHIVO DE PLAN POR SKU
    # =====================================================
    st.markdown("### 3. Archivo de plan por SKU")
    uploaded_plan_sku = st.file_uploader(
        "Carga el archivo Plan2026 by SKU",
        type=config.ALLOWED_FILE_TYPES,
        key=f"{config.FILE_KEY_PLAN_SKU}_{st.session_state.get('upload_reset_counter', 0)}",
    )

    if uploaded_plan_sku is not None:
        try:
            st.session_state["suppress_persistent_autoload"] = True
            df_plan_sku = data_loader.load_plan_sku_file(uploaded_plan_sku)
            is_valid_plan_sku, missing_plan_sku = validators.validate_required_columns(
                df_plan_sku,
                config.EXPECTED_COLUMNS_PLAN_SKU,
            )

            st.session_state["df_plan_sku"] = df_plan_sku
            st.session_state["plan_sku_valid"] = is_valid_plan_sku
            st.session_state["plan_sku_missing_columns"] = missing_plan_sku
            st.session_state["plan_sku_file_name"] = uploaded_plan_sku.name

        except Exception as exc:
            st.error(f"{config.MSG_UPLOAD_ERROR} Detalle: {exc}")

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

    st.markdown("---")

    # =====================================================
    # RESUMEN
    # =====================================================
    st.markdown("### 4. Resumen del estado de carga")

    sales_loaded = st.session_state.get("df_sales") is not None
    plan_client_loaded = st.session_state.get("df_plan_client") is not None
    plan_sku_loaded = st.session_state.get("df_plan_sku") is not None

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            styles.build_info_card(
                "Ventas",
                "Cargado" if sales_loaded else "Pendiente",
                "Archivo base de ventas",
            ),
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            styles.build_info_card(
                "Plan Cliente",
                "Cargado" if plan_client_loaded else "Pendiente",
                "Archivo comparativo por cliente",
            ),
            unsafe_allow_html=True,
        )

    with col3:
        st.markdown(
            styles.build_info_card(
                "Plan SKU",
                "Cargado" if plan_sku_loaded else "Pendiente",
                "Archivo comparativo por material",
            ),
            unsafe_allow_html=True,
        )



    st.markdown("---")
    st.markdown("### 5. Guardar carga para usuarios viewer")

    if sales_loaded and plan_client_loaded and plan_sku_loaded:
        st.info(
            "Cuando los tres archivos estén validados, guarda esta carga para que los usuarios viewer puedan consultar la app sin subir archivos."
        )
        st.button(
            "Guardar carga administrativa para viewers",
            on_click=save_current_data_for_viewers,
            use_container_width=True,
        )
    else:
        st.caption("Carga los tres archivos para habilitar el guardado administrativo.")

    # =====================================================
    # LIMPIEZA DE SESIÓN Y CARGA GUARDADA
    # =====================================================
    st.markdown("---")
    st.markdown("### 6. Limpieza de carga guardada")
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
        '<div class="base-mtd-section-heading">Vista previa de la base procesada</div>',
        unsafe_allow_html=True,
    )

    if df_processed is not None and not df_processed.empty:
        render_preview_expander(
            "Vista previa - Base procesada",
            df_processed,
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
            config.COL_GROSS_MARGIN,
        ]

        available_columns = [col for col in columns_to_show if col in df_processed.columns]

        render_preview_expander(
            "Vista previa - Columnas clave",
            df_processed[available_columns],
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
        "En BTS se compara el periodo actual contra PY acumulado al mismo corte. "
        "La lógica respeta el ciclo Back To School de octubre a agosto."
    )

    st.markdown(
        build_bts_table_html(
            build_report_context_title(
                "BTS Actual vs PY comparable",
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

    if (
        st.session_state.get("df_sales") is None
        and not st.session_state.get("suppress_persistent_autoload", False)
    ):
        load_persistent_data_to_session(show_message=False)

    render_main_header()
    render_global_alerts()
    selected = render_sidebar()

    if selected == "Inicio":
        render_home_view()
    elif selected == "Carga de datos":
        if is_admin_user():
            render_upload_view()
        else:
            render_home_view()
    elif selected == "Visión general":
        render_overview_view()
    elif selected == "Canal Corporativo":
        render_report_1_view()
    elif selected == "Segmento y Categoría":
        render_report_2_view()
    elif selected == "Desempeño Comercial":
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
