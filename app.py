# =========================================================
# APLICACIÓN PRINCIPAL DEL DASHBOARD
# ETAPA 1 + ETAPA 2 + ETAPA 3 + ETAPA 4 + ETAPA 5 + ETAPA 6 + ETAPA 7 + ETAPA 8
# Archivo: app.py
# =========================================================

from html import escape
import math

import streamlit as st

import config
import data_loader
import data_processor
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

# =========================================================
# 4. FUNCIONES DE AUTENTICACIÓN
# =========================================================
def check_login() -> None:
    user = st.session_state.get("input_user", "").strip()
    password = st.session_state.get("input_password", "").strip()

    if user in config.VALID_USERS and config.VALID_USERS[user] == password:
        st.session_state["authenticated"] = True
        st.session_state["user_role"] = user
    else:
        st.error("Credenciales incorrectas. Verifica usuario y contraseña.")

def logout() -> None:
    st.session_state["authenticated"] = False
    st.session_state["user_role"] = ""
    st.session_state["input_user"] = ""
    st.session_state["input_password"] = ""

# =========================================================
# 5. PANTALLA DE LOGIN
# =========================================================
def render_login_screen() -> None:
    left_col, center_col, right_col = st.columns([1, 1.5, 1])

    with center_col:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown(styles.build_hero_section(), unsafe_allow_html=True)

        st.text_input("Usuario", key="input_user")
        st.text_input("Contraseña", type="password", key="input_password")

        st.markdown("<br>", unsafe_allow_html=True)
        st.button("Iniciar sesión", on_click=check_login, use_container_width=True)

# =========================================================
# 6. ENCABEZADO PRINCIPAL
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
        st.markdown('</div>', unsafe_allow_html=True)

# =========================================================
# 7. SIDEBAR
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

        sidebar_html = (
            f"<b>Usuario activo:</b> {escape(st.session_state.get('user_role', 'N/A'))}<br>"
            f"<b>Moneda base:</b> {escape(config.DEFAULT_CURRENCY)}"
        )
        st.markdown(
            styles.build_sidebar_box(sidebar_html),
            unsafe_allow_html=True,
        )

        selected_option = st.radio(
            "Selecciona una sección",
            config.MAIN_MENU_OPTIONS,
            index=0,
        )

        st.markdown("---")
        st.markdown("### Estado del proyecto")
        st.caption("Etapa actual: Etapa 8")
        st.caption(
            "Módulos activos: config.py, styles.py, data_loader.py, "
            "validators.py, data_processor.py y app.py"
        )

        return selected_option

# =========================================================
# 8. VALIDACIÓN AUXILIAR
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
# 9. HELPERS DE FILTROS DE PERIODO
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
# 9.1 HELPERS DE FILTROS POR PRIMERA COLUMNA
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
        pct_var_vs_plan = (
            0.0 if plan_value == 0 else (actual_value - plan_value) / plan_value
        )

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
        default=st.session_state[widget_key],
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

        if not is_total and not is_grand_total:
            label_value = str(row.get("Category", "")).strip()
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
# 10. PROCESAMIENTO DE VENTAS
# =========================================================
def run_sales_processing() -> None:
    df_sales = st.session_state.get("df_sales")

    if df_sales is None:
        st.error(config.MSG_PROCESSING_MISSING_FILES)
        return

    is_ready, missing_columns = validators.validate_dataframe_for_processing(
        df_sales,
        config.REQUIRED_COLUMNS_SALES_PROCESS,
    )

    if not is_ready:
        st.error(config.MSG_VALIDATION_FAIL)
        st.warning(
            f"Columnas faltantes para procesar ventas: {', '.join(missing_columns)}"
        )
        return

    try:
        df_processed = data_processor.process_sales_data(df_sales)
        st.session_state["df_processed_sales"] = df_processed
        st.success(config.MSG_PROCESSING_SUCCESS)
    except Exception as exc:
        st.error(f"{config.MSG_PROCESSING_ERROR} Detalle: {exc}")

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

    total_gsnr_k = total_gsnr / 1000
    total_gm_k = total_gm / 1000

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            styles.build_info_card(
                "Registros procesados",
                f"{total_rows:,}",
                "Total de filas en la base procesada",
            ),
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            styles.build_info_card(
                "GSNR total (K)",
                f"{round(total_gsnr_k):,}",
                "Suma del GSNR contenido en BASE SAP, expresada en miles",
            ),
            unsafe_allow_html=True,
        )

    with col3:
        st.markdown(
            styles.build_info_card(
                "Gross Margin total (K)",
                f"{round(total_gm_k):,}",
                "GSNR menos Costo Vtas Netas, expresado en miles",
            ),
            unsafe_allow_html=True,
        )

# =========================================================
# 11. BASE MTD
# =========================================================
def run_mtd_build() -> None:
    df_processed_sales = st.session_state.get("df_processed_sales")
    df_plan_client = st.session_state.get("df_plan_client")
    df_plan_sku = st.session_state.get("df_plan_sku")

    if (
        df_processed_sales is None
        or df_plan_client is None
        or df_plan_sku is None
    ):
        st.error(config.MSG_MTD_BUILD_MISSING_FILES)
        return

    try:
        payload = data_processor.build_mtd_payload(
            df_processed_sales,
            df_plan_client,
            df_plan_sku,
        )
        st.session_state["mtd_payload"] = payload
        st.session_state["df_mtd_base"] = None
        st.success(config.MSG_MTD_BUILD_SUCCESS)
    except Exception as exc:
        st.error(f"{config.MSG_MTD_BUILD_ERROR} Detalle: {exc}")

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

    st.caption(f"Periodo actual: {latest_month:02d}/{latest_year}")

    row1 = st.columns(3)
    row2 = st.columns(3)

    with row1[0]:
        st.markdown(
            styles.build_info_card(
                "MTD ACT TOTAL (K)",
                f"{round(summary['mtd_act_total_k']):,}",
                "Valor del último mes real disponible, expresado en miles",
            ),
            unsafe_allow_html=True,
        )

    with row1[1]:
        st.markdown(
            styles.build_info_card(
                "YTD ACT TOTAL (K)",
                f"{round(summary['ytd_act_total_k']):,}",
                "Acumulado del año al último mes, expresado en miles",
            ),
            unsafe_allow_html=True,
        )

    with row1[2]:
        st.markdown(
            styles.build_info_card(
                "MTD PLAN TOTAL (K)",
                f"{round(summary['mtd_plan_total_k']):,}",
                "Plan del último mes disponible, expresado en miles",
            ),
            unsafe_allow_html=True,
        )

    with row2[0]:
        st.markdown(
            styles.build_info_card(
                "YTD PLAN TOTAL (K)",
                f"{round(summary['ytd_plan_total_k']):,}",
                "Plan acumulado de enero al mes actual, expresado en miles",
            ),
            unsafe_allow_html=True,
        )

    with row2[1]:
        st.markdown(
            styles.build_info_card(
                "BTS ACTUAL (K)",
                f"{round(bts_summary['bts_actual_k']):,}",
                "BTS real acumulado desde octubre del año previo al mes actual",
            ),
            unsafe_allow_html=True,
        )

    with row2[2]:
        st.markdown(
            styles.build_info_card(
                "BTS PY COMPLETO (K)",
                f"{round(bts_summary['bts_py_full_k']):,}",
                "BTS del ciclo previo completo, mostrado como dato informativo",
            ),
            unsafe_allow_html=True,
        )

    if plan_summary["mtd_plan_match"]:
        st.success("Validación MTD Plan: Plan Cliente y Plan SKU coinciden.")
    else:
        st.warning(
            "Validación MTD Plan: Plan Cliente y Plan SKU no coinciden. "
            f"Diferencia detectada: {round(plan_summary['mtd_plan_diff']):,}"
        )

    if plan_summary["ytd_plan_match"]:
        st.success("Validación YTD Plan: Plan Cliente y Plan SKU coinciden.")
    else:
        st.warning(
            "Validación YTD Plan: Plan Cliente y Plan SKU no coinciden. "
            f"Diferencia detectada: {round(plan_summary['ytd_plan_diff']):,}"
        )

def format_table_value(value: float, is_percent: bool = False) -> str:
    if value is None:
        value = 0.0

    if is_percent:
        if value < 0:
            return f"({abs(value) * 100:,.2f}%)"
        return f"{value * 100:,.2f}%"

    value_k = value / 1000

    if value_k < 0:
        return f"({abs(round(value_k)):,.0f})"
    return f"{round(value_k):,.0f}"

def build_mtd_legend_html() -> str:
    return (
        '<div class="metric-legend">'
        '<span class="metric-chip chip-real">REAL (BASE SAP)</span>'
        '<span class="metric-chip chip-client">Plan2026 by Client</span>'
        '<span class="metric-chip chip-sku">Plan2026 by SKU</span>'
        '</div>'
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
        '</div>'
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
            '</div>'
        )
        rows_html_parts.append(row_html)

    rows_html = "".join(rows_html_parts)

    return (
        '<div class="horizontal-table-card">'
        f'<div class="horizontal-table-title">{escape(title)}</div>'
        f'{header_html}'
        f'{rows_html}'
        '</div>'
    )

def build_bts_table_html(title: str, df_table) -> str:
    header_html = (
        '<div class="h-table h-table-5 h-table-header">'
        '<div class="h-cell h-header h-header-neutral">Periodo</div>'
        '<div class="h-cell h-header h-header-real">Actual</div>'
        '<div class="h-cell h-header h-header-real">PY</div>'
        '<div class="h-cell h-header h-header-neutral">Var VS PY</div>'
        '<div class="h-cell h-header h-header-neutral">%Var VS PY</div>'
        '</div>'
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
            '</div>'
        )
        rows_html_parts.append(row_html)

    rows_html = "".join(rows_html_parts)

    return (
        '<div class="horizontal-table-card">'
        f'<div class="horizontal-table-title">{escape(title)}</div>'
        f'{header_html}'
        f'{rows_html}'
        '</div>'
    )

# =========================================================
# 12. REPORTE 1
# =========================================================
def run_report_1_build(
    selected_year: int | None = None,
    selected_month: int | None = None,
) -> None:
    df_processed_sales = st.session_state.get("df_processed_sales")
    df_plan_client = st.session_state.get("df_plan_client")

    if df_processed_sales is None or df_plan_client is None:
        st.error(config.MSG_REPORT_1_BUILD_MISSING_FILES)
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
        st.error(config.MSG_VALIDATION_FAIL)
        st.warning(
            f"Columnas faltantes para Reporte 1 en ventas: {', '.join(missing_sales)}"
        )
        return

    if not is_plan_ready:
        st.error(config.MSG_VALIDATION_FAIL)
        st.warning(
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
        st.success(config.MSG_REPORT_1_BUILD_SUCCESS)
    except Exception as exc:
        st.error(f"{config.MSG_REPORT_1_BUILD_ERROR} Detalle: {exc}")

def is_blank_number(value) -> bool:
    if value is None:
        return True

    try:
        numeric_value = float(value)
        return math.isnan(numeric_value)
    except (TypeError, ValueError):
        return True

def format_report_1_value(value, is_percent: bool = False, allow_blank: bool = False) -> str:
    if is_blank_number(value):
        return "" if allow_blank else ("0.00%" if is_percent else "0")

    numeric_value = float(value)

    if is_percent:
        if numeric_value < 0:
            return f"({abs(numeric_value) * 100:,.2f}%)"
        return f"{numeric_value * 100:,.2f}%"

    value_k = numeric_value / 1000

    rounded_value = round(value_k)

    if rounded_value < 0:
        return f"({abs(rounded_value):,})"
    return f"{rounded_value:,}"

def build_report_1_title_box_html() -> str:
    return (
        '<div class="report-title-box">'
        f'<div class="report-title-main">{escape(config.REPORT_1_MAIN_HEADING)}</div>'
        f'<div class="report-title-sub">{escape(config.REPORT_1_SUBHEADING)}</div>'
        '</div>'
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
        '</div>'
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
            '</div>'
        )
        rows_html_parts.append(row_html)

    rows_html = "".join(rows_html_parts)

    return (
        '<div class="report-table-card">'
        f'<div class="report-table-title">{escape(title)}</div>'
        '<div class="report-table-scroll">'
        f'{header_html}'
        f'<div class="report-grid report-grid-8">{rows_html}</div>'
        '</div>'
        '</div>'
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
        '<div class="report-note">Primero construye el reporte para habilitar la vista. Después podrás cambiar el Año, el Mes y la primera columna de cada bloque.</div>',
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
                "Último periodo real detectado desde BASE SAP",
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

    selected_without_kens_labels = render_dimension_filter_block(
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

    st.markdown(
        '<div class="report-note">Las tablas MTD y YTD se muestran lado a lado para facilitar la lectura ejecutiva.</div>',
        unsafe_allow_html=True,
    )

    top_left, top_right = st.columns(2)

    with top_left:
        st.markdown(
            build_report_1_table_html(
                "MTD Channel CORP WITHOUT KENS",
                filtered_mtd_without_kens,
            ),
            unsafe_allow_html=True,
        )

    with top_right:
        st.markdown(
            build_report_1_table_html(
                "YTD Channel CORP WITHOUT KENS",
                filtered_ytd_without_kens,
            ),
            unsafe_allow_html=True,
        )

    st.markdown("---")
    st.markdown("### 4. Channel Corp MTD / YTD WITH KENS")

    selected_year_kens, selected_month_kens = render_period_filter_block(
        "Filtro del bloque: Channel Corp WITH KENS",
        "report1_kens_year",
        "report1_kens_month",
    )

    payload = st.session_state.get("report1_payload")

    kens_options = get_filter_options_from_table(
        payload["mtd_kens_table"],
        lambda row: str(row.get("Oficina de Ventas", "")).strip(),
    )

    selected_kens_labels = render_dimension_filter_block(
        "OFICINA DE VENTAS",
        "report1_kens_dimension_widget",
        "report1_kens_dimension_applied",
        kens_options,
    )

    if selected_year_kens is not None and selected_month_kens is not None:
        if st.button(
            "Aplicar filtro - Channel Corp WITH KENS",
            key="btn_report1_kens",
            use_container_width=True,
        ):
            sync_dimension_filter_to_applied_state(
                "report1_kens_dimension_widget",
                "report1_kens_dimension_applied",
                kens_options,
            )
            run_report_1_build(
                selected_year=selected_year_kens,
                selected_month=selected_month_kens,
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
                "MTD Channel CORP WITH KENS",
                filtered_mtd_kens,
            ),
            unsafe_allow_html=True,
        )

    with bottom_right:
        st.markdown(
            build_report_1_table_html(
                "YTD Channel CORP WITH KENS",
                filtered_ytd_kens,
            ),
            unsafe_allow_html=True,
        )

# =========================================================
# 13. REPORTE 2
# =========================================================
def run_report_2_build(
    selected_year: int | None = None,
    selected_month: int | None = None,
) -> None:
    df_processed_sales = st.session_state.get("df_processed_sales")
    df_plan_sku = st.session_state.get("df_plan_sku")

    if df_processed_sales is None or df_plan_sku is None:
        st.error(config.MSG_REPORT_2_BUILD_MISSING_FILES)
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
        st.error(config.MSG_VALIDATION_FAIL)
        st.warning(
            f"Columnas faltantes para Reporte 2 en ventas: {', '.join(missing_sales)}"
        )
        return

    if not is_plan_ready:
        st.error(config.MSG_VALIDATION_FAIL)
        st.warning(
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
        st.success(config.MSG_REPORT_2_BUILD_SUCCESS)
    except Exception as exc:
        st.error(f"{config.MSG_REPORT_2_BUILD_ERROR} Detalle: {exc}")

def run_report_2_category_build(
    selected_year: int | None = None,
    selected_month: int | None = None,
) -> None:
    df_processed_sales = st.session_state.get("df_processed_sales")
    df_plan_sku = st.session_state.get("df_plan_sku")

    if df_processed_sales is None or df_plan_sku is None:
        st.error(config.MSG_REPORT_2_CATEGORY_BUILD_MISSING_FILES)
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
        st.error(config.MSG_VALIDATION_FAIL)
        st.warning(
            f"Columnas faltantes para Reporte Category en ventas: {', '.join(missing_sales)}"
        )
        return

    if not is_plan_ready:
        st.error(config.MSG_VALIDATION_FAIL)
        st.warning(
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
        st.success(config.MSG_REPORT_2_CATEGORY_BUILD_SUCCESS)
    except Exception as exc:
        st.error(f"{config.MSG_REPORT_2_CATEGORY_BUILD_ERROR} Detalle: {exc}")

def format_report_2_value(value, is_percent: bool = False) -> str:
    if is_blank_number(value):
        return "0.00%" if is_percent else "0"

    numeric_value = float(value)

    if is_percent:
        if numeric_value < 0:
            return f"({abs(numeric_value) * 100:,.2f}%)"
        return f"{numeric_value * 100:,.2f}%"

    value_k = numeric_value / 1000
    rounded_value = round(value_k)

    if rounded_value < 0:
        return f"({abs(rounded_value):,})"
    return f"{rounded_value:,}"

def build_report_2_title_box_html() -> str:
    return (
        '<div class="report-title-box">'
        f'<div class="report-title-main">{escape(config.REPORT_2_MAIN_HEADING)}</div>'
        f'<div class="report-title-sub">{escape(config.REPORT_2_SUBHEADING)}</div>'
        '</div>'
    )

def build_report_2_table_html(title: str, df_table, first_header: str, view_type: str) -> str:
    header_html = (
        '<div class="report-grid report-grid-8">'
        f'<div class="report-cell report-header report-header-neutral report-header-sticky">{escape(first_header)}</div>'
        '<div class="report-cell report-header report-header-actual">Actual</div>'
        '<div class="report-cell report-header report-header-plan">Plan</div>'
        '<div class="report-cell report-header report-header-py">PY</div>'
        '<div class="report-cell report-header report-header-neutral">Var VS Plan</div>'
        '<div class="report-cell report-header report-header-neutral">%Var VS Plan</div>'
        '<div class="report-cell report-header report-header-neutral">Var VS PY</div>'
        '<div class="report-cell report-header report-header-neutral">%Var VS PY</div>'
        '</div>'
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
        else:
            label_value = str(row.get("Category", "")).strip()

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
            f'<div class="report-cell report-label-cell">{escape(label_value)}</div>'
            f'<div class="report-cell report-value-cell {"report-negative" if actual_negative else ""}">{format_report_2_value(actual_value)}</div>'
            f'<div class="report-cell report-value-cell {"report-negative" if plan_negative else ""}">{format_report_2_value(plan_value)}</div>'
            f'<div class="report-cell report-value-cell {"report-negative" if py_negative else ""}">{format_report_2_value(py_value)}</div>'
            f'<div class="report-cell report-value-cell {"report-negative" if var_plan_negative else ""}">{format_report_2_value(var_plan_value)}</div>'
            f'<div class="report-cell report-value-cell {"report-negative" if pct_plan_negative else ""}">{format_report_2_value(pct_plan_value, is_percent=True)}</div>'
            f'<div class="report-cell report-value-cell {"report-negative" if var_py_negative else ""}">{format_report_2_value(var_py_value)}</div>'
            f'<div class="report-cell report-value-cell {"report-negative" if pct_py_negative else ""}">{format_report_2_value(pct_py_value, is_percent=True)}</div>'
            '</div>'
        )
        rows_html_parts.append(row_html)

    rows_html = "".join(rows_html_parts)

    return (
        '<div class="report-table-card">'
        f'<div class="report-table-title">{escape(title)}</div>'
        '<div class="report-table-scroll">'
        f'{header_html}'
        f'<div class="report-grid report-grid-8">{rows_html}</div>'
        '</div>'
        '</div>'
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
                    "Último periodo real detectado desde BASE SAP",
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

    selected_year_segment, selected_month_segment = render_period_filter_block(
        "Filtro del bloque: Segment x Region",
        "report2_segment_year",
        "report2_segment_month",
    )

    payload = st.session_state.get("report2_payload")

    if payload is not None:
        segment_region_options = get_filter_options_from_table(
            payload["mtd_segment_region_table"],
            build_report_2_segment_region_display_label,
        )
    else:
        segment_region_options = []

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

    st.markdown(
        '<div class="report-note">Las tablas MTD y YTD se muestran lado a lado para facilitar la lectura ejecutiva.</div>',
        unsafe_allow_html=True,
    )

    if payload is None:
        st.info("Aún no se ha construido el bloque Segment x Region.")
    else:
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

        left_col, right_col = st.columns(2)

        with left_col:
            st.markdown(
                build_report_2_table_html(
                    "MTD Segment x Region",
                    filtered_mtd_segment,
                    "SEGMENTO / REGIÓN",
                    "segment_region",
                ),
                unsafe_allow_html=True,
            )

        with right_col:
            st.markdown(
                build_report_2_table_html(
                    "YTD Segment x Region",
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

    selected_year_category, selected_month_category = render_period_filter_block(
        "Filtro del bloque: Category",
        "report2_category_year",
        "report2_category_month",
    )

    payload_category = st.session_state.get("report2_category_payload")

    if payload_category is not None:
        category_options = get_filter_options_from_table(
            payload_category["mtd_category_table"],
            lambda row: str(row.get("Category", "")).strip(),
        )
    else:
        category_options = []

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

    if payload_category is None:
        st.info("Aún no se ha construido el Reporte Category.")
    else:
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

        left_col, right_col = st.columns(2)

        with left_col:
            st.markdown(
                build_report_2_table_html(
                    "MTD Category",
                    filtered_mtd_category,
                    "CATEGORY",
                    "category",
                ),
                unsafe_allow_html=True,
            )

        with right_col:
            st.markdown(
                build_report_2_table_html(
                    "YTD Category",
                    filtered_ytd_category,
                    "CATEGORY",
                    "category",
                ),
                unsafe_allow_html=True,
            )

# =========================================================
# 14. REPORTE 3
# =========================================================
def run_report_3_build(
    selected_year: int | None = None,
    selected_month: int | None = None,
) -> None:
    df_processed_sales = st.session_state.get("df_processed_sales")
    df_plan_sku = st.session_state.get("df_plan_sku")

    if df_processed_sales is None or df_plan_sku is None:
        st.error(config.MSG_REPORT_3_BUILD_MISSING_FILES)
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
        st.error(config.MSG_VALIDATION_FAIL)
        st.warning(
            f"Columnas faltantes para Reporte 3 en ventas: {', '.join(missing_sales)}"
        )
        return

    if not is_plan_ready:
        st.error(config.MSG_VALIDATION_FAIL)
        st.warning(
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
        st.success(config.MSG_REPORT_3_BUILD_SUCCESS)
    except Exception as exc:
        st.error(f"{config.MSG_REPORT_3_BUILD_ERROR} Detalle: {exc}")

def format_report_3_value(value, is_percent: bool = False) -> str:
    if is_blank_number(value):
        return "0.00%" if is_percent else "0"

    numeric_value = float(value)

    if is_percent:
        if numeric_value < 0:
            return f"({abs(numeric_value) * 100:,.2f}%)"
        return f"{numeric_value * 100:,.2f}%"

    value_k = numeric_value / 1000
    rounded_value = round(value_k)

    if rounded_value < 0:
        return f"({abs(rounded_value):,})"
    return f"{rounded_value:,}"

def build_report_3_title_box_html() -> str:
    return (
        '<div class="report-title-box">'
        f'<div class="report-title-main">{escape(config.REPORT_3_MAIN_HEADING)}</div>'
        f'<div class="report-title-sub">{escape(config.REPORT_3_SUBHEADING)}</div>'
        '</div>'
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
        '</div>'
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
            '</div>'
        )
        rows_html_parts.append(row_html)

    rows_html = "".join(rows_html_parts)

    return (
        '<div class="report-table-card">'
        f'<div class="report-table-title">{escape(title)}</div>'
        '<div class="report-table-scroll">'
        f'{header_html}'
        f'<div class="report-grid report-grid-8">{rows_html}</div>'
        '</div>'
        '</div>'
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
                "Último periodo real detectado desde BASE SAP",
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
                "Regla aplicada",
                "AFI excluido",
                "Se excluye AFI: Afiliadas en la construcción del reporte",
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

    st.markdown(
        '<div class="report-note">Las tablas MTD y YTD se muestran lado a lado para facilitar la lectura ejecutiva. El Total General permanece visible y se recalcula conforme al filtro seleccionado.</div>',
        unsafe_allow_html=True,
    )

    left_col, right_col = st.columns(2)

    with left_col:
        st.markdown(
            build_report_3_table_html(
                "MTD Channel",
                filtered_mtd_channel,
            ),
            unsafe_allow_html=True,
        )

    with right_col:
        st.markdown(
            build_report_3_table_html(
                "YTD Channel",
                filtered_ytd_channel,
            ),
            unsafe_allow_html=True,
        )

# =========================================================
# 15. REPORTE 4
# =========================================================
def run_report_4_build(
    selected_year: int | None = None,
    selected_month: int | None = None,
) -> None:
    df_processed_sales = st.session_state.get("df_processed_sales")
    df_plan_client = st.session_state.get("df_plan_client")

    if df_processed_sales is None or df_plan_client is None:
        st.error(config.MSG_REPORT_4_BUILD_MISSING_FILES)
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
        st.error(config.MSG_VALIDATION_FAIL)
        st.warning(
            f"Columnas faltantes para Reporte 4 en ventas: {', '.join(missing_sales)}"
        )
        return

    if not is_plan_ready:
        st.error(config.MSG_VALIDATION_FAIL)
        st.warning(
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
        st.success(config.MSG_REPORT_4_BUILD_SUCCESS)
    except Exception as exc:
        st.error(f"{config.MSG_REPORT_4_BUILD_ERROR} Detalle: {exc}")

def format_report_4_value(value, is_percent: bool = False) -> str:
    if is_blank_number(value):
        return "0.00%" if is_percent else "0"

    numeric_value = float(value)

    if is_percent:
        if numeric_value < 0:
            return f"({abs(numeric_value) * 100:,.2f}%)"
        return f"{numeric_value * 100:,.2f}%"

    value_k = numeric_value / 1000
    rounded_value = round(value_k)

    if rounded_value < 0:
        return f"({abs(rounded_value):,})"
    return f"{rounded_value:,}"

def build_report_4_title_box_html() -> str:
    return (
        '<div class="report-title-box">'
        f'<div class="report-title-main">{escape(config.REPORT_4_MAIN_HEADING)}</div>'
        f'<div class="report-title-sub">{escape(config.REPORT_4_SUBHEADING)}</div>'
        '</div>'
    )

def build_report_4_table_html(title: str, df_table) -> str:
    header_html = (
        '<div class="report-grid report-grid-8">'
        '<div class="report-cell report-header report-header-neutral report-header-sticky">CLIENT NAME</div>'
        '<div class="report-cell report-header report-header-actual">Actual</div>'
        '<div class="report-cell report-header report-header-plan">Plan</div>'
        '<div class="report-cell report-header report-header-py">PY</div>'
        '<div class="report-cell report-header report-header-neutral">Var VS Plan</div>'
        '<div class="report-cell report-header report-header-neutral">%Var VS Plan</div>'
        '<div class="report-cell report-header report-header-neutral">Var VS PY</div>'
        '<div class="report-cell report-header report-header-neutral">%Var VS PY</div>'
        '</div>'
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

        client_value = str(row.get("Client Name", "")).strip()

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
            f'<div class="report-cell report-label-cell">{escape(client_value)}</div>'
            f'<div class="report-cell report-value-cell {"report-negative" if actual_negative else ""}">{format_report_4_value(actual_value)}</div>'
            f'<div class="report-cell report-value-cell {"report-negative" if plan_negative else ""}">{format_report_4_value(plan_value)}</div>'
            f'<div class="report-cell report-value-cell {"report-negative" if py_negative else ""}">{format_report_4_value(py_value)}</div>'
            f'<div class="report-cell report-value-cell {"report-negative" if var_plan_negative else ""}">{format_report_4_value(var_plan_value)}</div>'
            f'<div class="report-cell report-value-cell {"report-negative" if pct_plan_negative else ""}">{format_report_4_value(pct_plan_value, is_percent=True)}</div>'
            f'<div class="report-cell report-value-cell {"report-negative" if var_py_negative else ""}">{format_report_4_value(var_py_value)}</div>'
            f'<div class="report-cell report-value-cell {"report-negative" if pct_py_negative else ""}">{format_report_4_value(pct_py_value, is_percent=True)}</div>'
            '</div>'
        )
        rows_html_parts.append(row_html)

    rows_html = "".join(rows_html_parts)

    return (
        '<div class="report-table-card">'
        f'<div class="report-table-title">{escape(title)}</div>'
        '<div class="report-table-scroll">'
        f'{header_html}'
        f'<div class="report-grid report-grid-8">{rows_html}</div>'
        '</div>'
        '</div>'
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
        Mostrar el comparativo ejecutivo MTD / YTD del Top 15 de clientes estratégicos,
        usando BASE SAP y Plan2026 by Client.
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
                "Último periodo real detectado desde BASE SAP",
            ),
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            styles.build_info_card(
                "Clientes objetivo",
                "15",
                "Catálogo fijo de clientes estratégicos definido por negocio",
            ),
            unsafe_allow_html=True,
        )

    with col3:
        st.markdown(
            styles.build_info_card(
                "Fuente de plan",
                "Plan Cliente",
                "Comparativo contra Plan2026 by Client",
            ),
            unsafe_allow_html=True,
        )

    st.markdown("---")
    st.markdown("### 3. Top 15 Clients MTD / YTD")

    selected_year_clients, selected_month_clients = render_period_filter_block(
        "Filtro del bloque: Top 15 Clients",
        "report4_clients_year",
        "report4_clients_month",
    )

    payload = st.session_state.get("report4_payload")

    client_options = get_filter_options_from_table(
        payload["mtd_top_clients_table"],
        lambda row: str(row.get("Client Name", "")).strip(),
    )

    render_dimension_filter_block(
        "CLIENT NAME",
        "report4_clients_dimension_widget",
        "report4_clients_dimension_applied",
        client_options,
    )

    if selected_year_clients is not None and selected_month_clients is not None:
        if st.button(
            "Aplicar filtro - Top 15 Clients",
            key="btn_report4_clients",
            use_container_width=True,
        ):
            sync_dimension_filter_to_applied_state(
                "report4_clients_dimension_widget",
                "report4_clients_dimension_applied",
                client_options,
            )
            run_report_4_build(
                selected_year=selected_year_clients,
                selected_month=selected_month_clients,
            )

    payload = st.session_state.get("report4_payload")

    applied_client_labels = get_valid_applied_filter_values(
        "report4_clients_dimension_applied",
        client_options,
    )

    filtered_mtd_clients = filter_report_4_top_clients_table(
        payload["mtd_top_clients_table"],
        applied_client_labels,
    )
    filtered_ytd_clients = filter_report_4_top_clients_table(
        payload["ytd_top_clients_table"],
        applied_client_labels,
    )

    st.markdown(
        '<div class="report-note">Las tablas MTD y YTD se muestran lado a lado para facilitar la lectura ejecutiva. El Total General permanece visible y se recalcula conforme al filtro seleccionado.</div>',
        unsafe_allow_html=True,
    )

    left_col, right_col = st.columns(2)

    with left_col:
        st.markdown(
            build_report_4_table_html(
                "MTD Top 15 Clients",
                filtered_mtd_clients,
            ),
            unsafe_allow_html=True,
        )

    with right_col:
        st.markdown(
            build_report_4_table_html(
                "YTD Top 15 Clients",
                filtered_ytd_clients,
            ),
            unsafe_allow_html=True,
        )

# =========================================================
# 16. VISTAS PRINCIPALES
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

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            styles.build_info_card(
                "Módulos base",
                "6",
                "config.py, styles.py, data_loader.py, validators.py, "
                "data_processor.py y app.py",
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

        En la siguiente etapa se continuará con el refinamiento visual final
        y la corrección de alertas en pantalla.
        """
    )

def render_upload_view() -> None:
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

    st.markdown("### 1. Archivo de ventas")
    uploaded_sales = st.file_uploader(
        "Carga el archivo de ventas",
        type=config.ALLOWED_FILE_TYPES,
        key=config.FILE_KEY_SALES,
    )

    if uploaded_sales is not None:
        try:
            df_sales = data_loader.load_sales_file(uploaded_sales)
            is_valid_sales, missing_sales = validators.validate_required_columns(
                df_sales,
                config.EXPECTED_COLUMNS_SALES,
            )

            st.session_state["df_sales"] = df_sales
            st.session_state["sales_valid"] = is_valid_sales

            render_file_validation_result(
                is_valid_sales,
                missing_sales,
                f"{config.MSG_UPLOAD_SUCCESS} Ventas: {config.MSG_VALIDATION_OK}",
            )

            with st.expander("Vista previa de ventas"):
                st.dataframe(df_sales.head())

        except Exception as exc:
            st.error(f"{config.MSG_UPLOAD_ERROR} Detalle: {exc}")

    elif st.session_state.get("df_sales") is not None:
        st.success("Archivo de ventas ya cargado en sesión.")
        with st.expander("Vista previa de ventas"):
            st.dataframe(st.session_state["df_sales"].head())

    st.markdown("---")

    st.markdown("### 2. Archivo Plan por Cliente")
    uploaded_plan_client = st.file_uploader(
        "Carga el archivo comparativo por cliente",
        type=config.ALLOWED_FILE_TYPES,
        key=config.FILE_KEY_PLAN_CLIENT,
    )

    if uploaded_plan_client is not None:
        try:
            df_plan_client = data_loader.load_plan_client_file(uploaded_plan_client)
            is_valid_plan_client, missing_plan_client = validators.validate_required_columns(
                df_plan_client,
                config.EXPECTED_COLUMNS_PLAN_CLIENT,
            )

            st.session_state["df_plan_client"] = df_plan_client
            st.session_state["plan_client_valid"] = is_valid_plan_client

            render_file_validation_result(
                is_valid_plan_client,
                missing_plan_client,
                f"{config.MSG_UPLOAD_SUCCESS} Plan por Cliente: {config.MSG_VALIDATION_OK}",
            )

            with st.expander("Vista previa de plan por cliente"):
                st.dataframe(df_plan_client.head())

        except Exception as exc:
            st.error(f"{config.MSG_UPLOAD_ERROR} Detalle: {exc}")

    elif st.session_state.get("df_plan_client") is not None:
        st.success("Archivo de plan por cliente ya cargado en sesión.")
        with st.expander("Vista previa de plan por cliente"):
            st.dataframe(st.session_state["df_plan_client"].head())

    st.markdown("---")

    st.markdown("### 3. Archivo Plan por SKU")
    uploaded_plan_sku = st.file_uploader(
        "Carga el archivo comparativo por material",
        type=config.ALLOWED_FILE_TYPES,
        key=config.FILE_KEY_PLAN_SKU,
    )

    if uploaded_plan_sku is not None:
        try:
            df_plan_sku = data_loader.load_plan_sku_file(uploaded_plan_sku)
            is_valid_plan_sku, missing_plan_sku = validators.validate_required_columns(
                df_plan_sku,
                config.EXPECTED_COLUMNS_PLAN_SKU,
            )

            st.session_state["df_plan_sku"] = df_plan_sku
            st.session_state["plan_sku_valid"] = is_valid_plan_sku

            render_file_validation_result(
                is_valid_plan_sku,
                missing_plan_sku,
                f"{config.MSG_UPLOAD_SUCCESS} Plan por SKU: {config.MSG_VALIDATION_OK}",
            )

            with st.expander("Vista previa de plan por SKU"):
                st.dataframe(df_plan_sku.head())

        except Exception as exc:
            st.error(f"{config.MSG_UPLOAD_ERROR} Detalle: {exc}")

    elif st.session_state.get("df_plan_sku") is not None:
        st.success("Archivo de plan por SKU ya cargado en sesión.")
        with st.expander("Vista previa de plan por SKU"):
            st.dataframe(st.session_state["df_plan_sku"].head())

    st.markdown("---")

    st.markdown("### 4. Resumen del estado de carga")

    sales_loaded = st.session_state["df_sales"] is not None
    plan_client_loaded = st.session_state["df_plan_client"] is not None
    plan_sku_loaded = st.session_state["df_plan_sku"] is not None

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

    st.markdown("### 1. Ejecutar procesamiento inicial")
    st.button(
        "Procesar base de ventas",
        on_click=run_sales_processing,
        use_container_width=True,
    )

    st.markdown("---")
    st.markdown("### 2. Resumen de la base procesada")
    render_processed_data_summary()

    df_processed = st.session_state.get("df_processed_sales")

    st.markdown("---")
    st.markdown("### 3. Vista previa de la base procesada")

    if df_processed is not None and not df_processed.empty:
        st.dataframe(df_processed.head(20))
    else:
        st.info("Aún no se ha procesado ninguna base.")

    st.markdown("---")
    st.markdown("### 4. Validación visual de columnas clave")

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
        st.dataframe(df_processed[available_columns].head(20))
    else:
        st.info("No hay columnas procesadas para mostrar todavía.")

def render_mtd_base_view() -> None:
    st.markdown(
        '<div class="section-title">Base MTD</div>',
        unsafe_allow_html=True,
    )

    mtd_box_html = styles.build_info_box(
        """
        <b>Objetivo de esta etapa:</b><br>
        Construir comparativos generales MTD / YTD para Plan2026 by Client
        y Plan2026 by SKU con base en REAL (BASE SAP).
        """
    )
    st.markdown(mtd_box_html, unsafe_allow_html=True)

    st.markdown("### 1. Construir Base MTD")
    st.button(
        "Construir Base MTD",
        on_click=run_mtd_build,
        use_container_width=True,
    )

    st.markdown("---")
    st.markdown("### 2. Resumen ejecutivo")
    render_mtd_base_summary()

    payload = st.session_state.get("mtd_payload")

    if payload is None:
        st.markdown("---")
        st.info("Aún no se ha construido la Base MTD.")
        return

    st.markdown("---")
    st.markdown("### 3. Comparativos MTD / YTD")
    st.markdown(build_mtd_legend_html(), unsafe_allow_html=True)

    st.markdown(
        build_horizontal_plan_table_html(
            "Plan2026 by Client",
            payload["client_table"],
            "client",
        ),
        unsafe_allow_html=True,
    )

    st.markdown(
        build_horizontal_plan_table_html(
            "Plan2026 by SKU",
            payload["sku_table"],
            "sku",
        ),
        unsafe_allow_html=True,
    )

    st.markdown("---")
    st.markdown("### 4. Comparativo BTS")
    st.caption(
        "En BTS se compara el periodo actual contra PY acumulado al mismo corte del mes actual."
    )

    st.markdown(
        build_bts_table_html(
            "BTS Actual vs PY comparable",
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
# 17. FLUJO PRINCIPAL
# =========================================================
def main() -> None:
    if not st.session_state["authenticated"]:
        render_login_screen()
        return

    render_main_header()
    selected = render_sidebar()

    if selected == "Inicio":
        render_home_view()
    elif selected == "Carga de datos":
        render_upload_view()
    elif selected == "Visión general":
        render_overview_view()
    elif selected == "Reporte 1":
        render_report_1_view()
    elif selected == "Reporte 2":
        render_report_2_view()
    elif selected == "Reporte 3":
        render_report_3_view()
    elif selected == "Reporte 4":
        render_report_4_view()
    elif selected == "Base MTD":
        render_mtd_base_view()
    else:
        render_placeholder_view(selected)

# =========================================================
# 18. EJECUCIÓN PRINCIPAL
# =========================================================
main()
