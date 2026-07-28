# ===============================================================
# PROCESAMIENTO DE DATOS
# Archivo: data_processor.py
# ===============================================================

import re

import pandas as pd

import config

# --------------------------------------------------------------
# PROGRESO DE PROCESAMIENTO
# --------------------------------------------------------------
def emit_progress(progress_callback, message: str, step: int, total_steps: int) -> None:
    """
    Informa a la interfaz qué etapa real está comenzando.

    El callback es opcional, por lo que todas las llamadas existentes siguen
    funcionando. El módulo no dibuja componentes de Streamlit; solo reporta
    message, step y total_steps para que app.py los muestre.
    """
    if not callable(progress_callback):
        return

    try:
        progress_callback(
            message=message,
            step=int(step),
            total_steps=int(total_steps),
        )
    except TypeError:
        progress_callback(message)


# --------------------------------------------------------------
# CONSTANTES AUXILIARES
# --------------------------------------------------------------
MONTH_NAME_TO_NUMBER = {
    "jan": 1,
    "feb": 2,
    "mar": 3,
    "apr": 4,
    "may": 5,
    "jun": 6,
    "jul": 7,
    "aug": 8,
    "sep": 9,
    "oct": 10,
    "nov": 11,
    "dec": 12,
}

# --------------------------------------------------------------
# CONSTANTES AUXILIARES:
# Columnas monetarias comunes de salida
# Estas funciones se dejan listas para soporte de moneda,
# pero la app sigue mostrando MXN por defecto y convierte
# visualmente cuando el usuario cambia a USD.
# --------------------------------------------------------------
DEFAULT_MONETARY_COLUMNS = [
    "Actual",
    "Plan",
    "Fcst",
    "PY",
    "Var VS Plan",
    "Var VS Fcst",
    "Var VS PY",
    "Valor",
    config.COL_GSNR,
    config.COL_GROSS_MARGIN,
    "Importe Vtas Brutas",
    "Importe Devoluciones",
    "Importe Fact No Embq",
    "Costo Vtas Netas",
]

# --------------------------------------------------------------
# FUNCIÓN AUXILIAR:
# Limpia nombres de columnas
# --------------------------------------------------------------
def standardize_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [str(col).strip() for col in df.columns]
    return df

# --------------------------------------------------------------
# FUNCIÓN AUXILIAR:
# Limpia series numéricas
# --------------------------------------------------------------
def clean_numeric_series(series: pd.Series) -> pd.Series:
    cleaned = (
        series.astype(str)
        .str.replace(",", "", regex=False)
        .str.replace("$", "", regex=False)
        .str.replace(" ", "", regex=False)
        .str.replace("(", "-", regex=False)
        .str.replace(")", "", regex=False)
    )

    cleaned = cleaned.replace(
        to_replace=[r"^nan$", r"^None$", r"^-$", r"^$"],
        value="0",
        regex=True,
    )

    return pd.to_numeric(cleaned, errors="coerce").fillna(0)

# --------------------------------------------------------------
# FUNCIÓN AUXILIAR:
# Normaliza texto para comparar columnas
# --------------------------------------------------------------
def normalize_text(text: str) -> str:
    return re.sub(r"[^a-z0-9]", "", str(text).strip().lower())

# --------------------------------------------------------------
# FUNCIÓN AUXILIAR:
# Normaliza modo de moneda
# --------------------------------------------------------------
def normalize_currency_mode(currency_mode: str | None) -> str:
    return "USD" if str(currency_mode or "").strip().upper() == "USD" else config.DEFAULT_CURRENCY

# --------------------------------------------------------------
# FUNCIÓN AUXILIAR:
# Valida tipo de cambio
# --------------------------------------------------------------
def get_valid_exchange_rate(exchange_rate: float | int | str | None) -> float:
    try:
        numeric_value = float(exchange_rate)
    except (TypeError, ValueError):
        numeric_value = float(config.DEFAULT_EXCHANGE_RATE)

    if numeric_value <= 0:
        numeric_value = float(config.DEFAULT_EXCHANGE_RATE)

    return numeric_value

# --------------------------------------------------------------
# FUNCIÓN AUXILIAR:
# Convierte un valor monetario a la moneda solicitada
# Importante:
# La base lógica del negocio permanece en MXN.
# --------------------------------------------------------------
def convert_monetary_value(
    value,
    currency_mode: str = config.DEFAULT_CURRENCY,
    exchange_rate: float | int | str | None = None,
):
    if value is None:
        return value

    try:
        numeric_value = float(value)
    except (TypeError, ValueError):
        return value

    if pd.isna(numeric_value):
        return value

    normalized_currency = normalize_currency_mode(currency_mode)

    if normalized_currency == "USD":
        valid_exchange_rate = get_valid_exchange_rate(exchange_rate)
        return numeric_value / valid_exchange_rate

    return numeric_value

# --------------------------------------------------------------
# FUNCIÓN AUXILIAR:
# Convierte columnas monetarias de un DataFrame
# --------------------------------------------------------------
def convert_dataframe_currency(
    df: pd.DataFrame,
    currency_mode: str = config.DEFAULT_CURRENCY,
    exchange_rate: float | int | str | None = None,
    monetary_columns: list[str] | None = None,
) -> pd.DataFrame:
    if df is None:
        return df

    df_converted = df.copy()

    normalized_currency = normalize_currency_mode(currency_mode)
    if normalized_currency != "USD":
        return df_converted

    if monetary_columns is None:
        monetary_columns = DEFAULT_MONETARY_COLUMNS.copy()

    for column_name in monetary_columns:
        if column_name in df_converted.columns:
            df_converted[column_name] = df_converted[column_name].apply(
                lambda value: convert_monetary_value(
                    value,
                    currency_mode=normalized_currency,
                    exchange_rate=exchange_rate,
                )
            )

    return df_converted

# --------------------------------------------------------------
# FUNCIÓN AUXILIAR:
# Limpia columnas numéricas de ventas
# --------------------------------------------------------------
def clean_sales_numeric_columns(df_sales: pd.DataFrame) -> pd.DataFrame:
    df_sales = df_sales.copy()

    for col in config.SALES_NUMERIC_COLUMNS:
        if col in df_sales.columns:
            df_sales[col] = clean_numeric_series(df_sales[col])

    return df_sales

# --------------------------------------------------------------
# FUNCIÓN AUXILIAR:
# Parsea Periodo
# --------------------------------------------------------------
def parse_period_value(period_value):
    if pd.isna(period_value):
        return None, None

    text = str(period_value).strip().lower()

    match = re.search(r"(20\d{2})[-/]?(\d{1,2})", text)
    if match:
        return int(match.group(1)), int(match.group(2))

    match = re.search(r"(\d{1,2})[-/ ]+(20\d{2})", text)
    if match:
        return int(match.group(2)), int(match.group(1))

    return None, None

# --------------------------------------------------------------
# FUNCIÓN PRINCIPAL:
# Agrega Año y Mes
# --------------------------------------------------------------
def add_year_month_columns(df_sales: pd.DataFrame) -> pd.DataFrame:
    df_sales = df_sales.copy()

    if "Periodo" not in df_sales.columns:
        raise ValueError("No existe columna 'Periodo'")

    parsed = df_sales["Periodo"].apply(parse_period_value)

    if config.COL_YEAR not in df_sales.columns:
        df_sales[config.COL_YEAR] = parsed.apply(lambda x: x[0])
    else:
        df_sales[config.COL_YEAR] = df_sales[config.COL_YEAR].fillna(
            parsed.apply(lambda x: x[0])
        )

    if config.COL_MONTH not in df_sales.columns:
        df_sales[config.COL_MONTH] = parsed.apply(lambda x: x[1])
    else:
        df_sales[config.COL_MONTH] = df_sales[config.COL_MONTH].fillna(
            parsed.apply(lambda x: x[1])
        )

    df_sales[config.COL_YEAR] = pd.to_numeric(df_sales[config.COL_YEAR], errors="coerce")
    df_sales[config.COL_MONTH] = pd.to_numeric(df_sales[config.COL_MONTH], errors="coerce")

    return df_sales

# --------------------------------------------------------------
# FUNCIÓN PRINCIPAL:
# Calcula o respeta GSNR
# --------------------------------------------------------------
def calculate_gsnr(df_sales: pd.DataFrame) -> pd.DataFrame:
    df = df_sales.copy()

    if config.COL_GSNR in df.columns:
        df[config.COL_GSNR] = clean_numeric_series(df[config.COL_GSNR])
        return df

    required = [
        "Importe Vtas Brutas",
        "Importe Devoluciones",
        "Importe Fact No Embq",
    ]

    for col in required:
        if col not in df.columns:
            df[col] = 0

    df[config.COL_GSNR] = (
        df["Importe Vtas Brutas"]
        - df["Importe Devoluciones"]
        - df["Importe Fact No Embq"]
    )

    return df

# --------------------------------------------------------------
# FUNCIÓN PRINCIPAL:
# Calcula Gross Margin
# --------------------------------------------------------------
def calculate_gross_margin(df_sales: pd.DataFrame) -> pd.DataFrame:
    df = df_sales.copy()

    if "Costo Vtas Netas" not in df.columns:
        df["Costo Vtas Netas"] = 0

    df[config.COL_GROSS_MARGIN] = df[config.COL_GSNR] - df["Costo Vtas Netas"]

    return df

# --------------------------------------------------------------
# FUNCIÓN PRINCIPAL:
# Procesa ventas sin depender de mapeos
# --------------------------------------------------------------
def process_sales_data(
    df_sales: pd.DataFrame,
    progress_callback=None,
) -> pd.DataFrame:
    total_steps = 5

    emit_progress(progress_callback, "Estandarizando nombres de columnas", 1, total_steps)
    df_raw_audit = standardize_columns(df_sales)

    emit_progress(progress_callback, "Limpiando columnas numéricas de ventas", 2, total_steps)
    df = df_raw_audit.copy()
    df = clean_sales_numeric_columns(df)

    emit_progress(progress_callback, "Identificando Año y Mes desde Periodo", 3, total_steps)
    df = add_year_month_columns(df)

    emit_progress(progress_callback, "Calculando GSNR", 4, total_steps)
    df = calculate_gsnr(df)

    emit_progress(progress_callback, "Calculando Gross Margin", 5, total_steps)
    df = calculate_gross_margin(df)

    return df

# ==============================================================
# HELPERS GENERALES DE PERIODO
# ==============================================================

# --------------------------------------------------------------
# FUNCIÓN AUXILIAR:
# Obtiene lista de años válidos desde ventas
# --------------------------------------------------------------
def get_available_years_from_sales(df_processed_sales: pd.DataFrame) -> list[int]:
    if df_processed_sales is None or df_processed_sales.empty:
        return []

    if config.COL_YEAR not in df_processed_sales.columns:
        return []

    years = (
        pd.to_numeric(df_processed_sales[config.COL_YEAR], errors="coerce")
        .dropna()
        .astype(int)
        .tolist()
    )

    return sorted(set(years))

# --------------------------------------------------------------
# FUNCIÓN AUXILIAR:
# Obtiene lista de meses válidos para un año
# --------------------------------------------------------------
def get_available_months_from_sales_for_year(
    df_processed_sales: pd.DataFrame,
    selected_year: int,
) -> list[int]:
    if df_processed_sales is None or df_processed_sales.empty:
        return []

    required_cols = [config.COL_YEAR, config.COL_MONTH]
    if any(col not in df_processed_sales.columns for col in required_cols):
        return []

    months = (
        df_processed_sales.loc[
            pd.to_numeric(df_processed_sales[config.COL_YEAR], errors="coerce") == int(selected_year),
            config.COL_MONTH,
        ]
    )

    months = pd.to_numeric(months, errors="coerce").dropna().astype(int).tolist()
    months = sorted({month for month in months if 1 <= month <= 12})

    return months

# --------------------------------------------------------------
# FUNCIÓN AUXILIAR:
# Resuelve año y mes a usar en reportes
# Si no se recibe selección, usa el último periodo disponible
# --------------------------------------------------------------
def resolve_reporting_period(
    df_processed_sales: pd.DataFrame,
    selected_year: int | None = None,
    selected_month: int | None = None,
) -> tuple[int, int]:
    latest_year, latest_month = get_latest_actual_period_from_sales(df_processed_sales)

    if latest_year is None or latest_month is None:
        raise ValueError("No fue posible identificar el último periodo real disponible.")

    if selected_year is None and selected_month is None:
        return latest_year, latest_month

    available_years = get_available_years_from_sales(df_processed_sales)

    if selected_year is None:
        selected_year = latest_year

    selected_year = int(selected_year)

    if selected_year not in available_years:
        raise ValueError(
            f"El año seleccionado {selected_year} no existe en la base de ventas procesada."
        )

    available_months = get_available_months_from_sales_for_year(df_processed_sales, selected_year)

    if not available_months:
        raise ValueError(
            f"No existen meses válidos para el año seleccionado {selected_year}."
        )

    if selected_month is None:
        if selected_year == latest_year:
            selected_month = latest_month
        else:
            selected_month = max(available_months)

    selected_month = int(selected_month)

    if selected_month not in available_months:
        raise ValueError(
            f"El mes seleccionado {selected_month} no existe para el año {selected_year} en la base de ventas procesada."
        )

    return selected_year, selected_month

# ==============================================================
# ETAPA 4: BASE MTD
# ==============================================================

# --------------------------------------------------------------
# FUNCIÓN AUXILIAR:
# Detecta columnas GS mensuales del plan SKU
# --------------------------------------------------------------
def get_plan_sku_gs_columns(df_plan_sku: pd.DataFrame) -> dict[int, str]:
    detected = {}

    for col in df_plan_sku.columns:
        normalized = normalize_text(col)

        for month_name, month_number in MONTH_NAME_TO_NUMBER.items():
            if normalized == f"gs{month_name}" or normalized == f"gs{month_name}2026":
                detected[month_number] = col

    return detected

# --------------------------------------------------------------
# FUNCIÓN AUXILIAR:
# Detecta columnas mensuales del plan por cliente
# --------------------------------------------------------------
def get_plan_client_month_columns(df_plan_client: pd.DataFrame) -> dict[int, str]:
    detected = {}

    for col in df_plan_client.columns:
        normalized = normalize_text(col)

        for month_name, month_number in MONTH_NAME_TO_NUMBER.items():
            if normalized == month_name:
                detected[month_number] = col

    return detected

# --------------------------------------------------------------
# FUNCIÓN AUXILIAR:
# Detecta el primer renglón "Total" real en plan cliente
# --------------------------------------------------------------
def find_first_total_row(df: pd.DataFrame) -> int | None:
    object_cols = [col for col in df.columns if df[col].dtype == "object"]

    for idx, row in df.iterrows():
        values = [normalize_text(row[col]) for col in object_cols]
        if "total" in values:
            return idx

    return None

# --------------------------------------------------------------
# FUNCIÓN AUXILIAR:
# Obtiene el último periodo real desde ventas procesadas
# --------------------------------------------------------------
def get_latest_actual_period_from_sales(
    df_processed_sales: pd.DataFrame,
) -> tuple[int | None, int | None]:
    if df_processed_sales is None or df_processed_sales.empty:
        return None, None

    if config.COL_YEAR not in df_processed_sales.columns or config.COL_MONTH not in df_processed_sales.columns:
        return None, None

    valid = df_processed_sales[[config.COL_YEAR, config.COL_MONTH]].dropna().copy()
    if valid.empty:
        return None, None

    valid[config.COL_YEAR] = pd.to_numeric(valid[config.COL_YEAR], errors="coerce")
    valid[config.COL_MONTH] = pd.to_numeric(valid[config.COL_MONTH], errors="coerce")
    valid = valid.dropna()

    if valid.empty:
        return None, None

    latest_year = int(valid[config.COL_YEAR].max())
    latest_month = int(
        valid.loc[valid[config.COL_YEAR] == latest_year, config.COL_MONTH].max()
    )

    return latest_year, latest_month

# --------------------------------------------------------------
# FUNCIÓN AUXILIAR:
# Calcula actual y PY generales
# --------------------------------------------------------------
def get_vendor_group_exclusion_values() -> set[str]:
    """Valores de Grupo de Vendedores que deben excluirse en Base MTD/BTS."""
    configured_values = getattr(
        config,
        "BASE_MTD_EXCLUDED_VENDOR_GROUPS",
        ["AFI: Afiliadas"],
    )
    return {normalize_report_2_label(value) for value in configured_values}


def exclude_base_mtd_affiliates(df: pd.DataFrame) -> pd.DataFrame:
    """
    Excluye AFI: Afiliadas para los cálculos generales de Base MTD.

    Esta regla aplica a Actual, PY, Plan Cliente y Plan SKU dentro de Base MTD,
    sin modificar visualmente las tarjetas ni las tablas.
    """
    df = df.copy()

    vendor_group_col = find_first_existing_column(
        df,
        [
            "Grupo de vendedores",
            "Grupo de Vendedores",
            "Grupo vendedores",
            "Channel",
            "Canal",
            "Sales region short",
            "Sales Region Short",
            "Region",
            "Región",
        ],
    )

    if vendor_group_col is None:
        return df

    excluded_values = get_vendor_group_exclusion_values()
    vendor_series = df[vendor_group_col].apply(normalize_report_2_label)

    return df.loc[~vendor_series.isin(excluded_values)].copy()


def filter_sales_for_base_mtd_bts(df_processed_sales: pd.DataFrame) -> pd.DataFrame:
    """
    Filtra ventas para BTS conforme al Excel de referencia.

    Reglas:
    - Solo GOBA/BARRILITO.
    - No considera AFI, ECO, EXP, KEN ni NGI dentro de Grupo de Vendedores.
    """
    df = standardize_columns(df_processed_sales).copy()

    segment_col = find_first_existing_column(df, ["Segm Neg", "Segmento", "Segment"])
    vendor_group_col = find_first_existing_column(
        df,
        [
            "Grupo de vendedores",
            "Grupo de Vendedores",
            "Grupo vendedores",
            "Sales region short",
            "Sales Region Short",
            "Region",
            "Región",
        ],
    )

    if segment_col is not None:
        segment_series = df[segment_col].apply(normalize_report_2_segment_label)
        df = df.loc[segment_series.isin({"GOBA", "BARRILITO"})].copy()

    if vendor_group_col is not None:
        excluded_values = {
            normalize_report_2_label(value)
            for value in getattr(
                config,
                "BASE_MTD_BTS_EXCLUDED_VENDOR_GROUPS",
                [
                    "AFI: Afiliadas",
                    "ECO: Ecommerce",
                    "EXP: Exportaciones",
                    "KEN: Kensington",
                    "NGI: Neg Internacionales",
                ],
            )
        }
        vendor_series = df[vendor_group_col].apply(normalize_report_2_label)
        df = df.loc[~vendor_series.isin(excluded_values)].copy()

    return df


def calculate_actual_and_py_totals(
    df_processed_sales: pd.DataFrame,
    latest_year: int,
    latest_month: int,
) -> dict:
    df = exclude_base_mtd_affiliates(df_processed_sales)

    current_year_df = df[df[config.COL_YEAR] == latest_year].copy()
    previous_year_df = df[df[config.COL_YEAR] == (latest_year - 1)].copy()

    mtd_actual = current_year_df[
        current_year_df[config.COL_MONTH] == latest_month
    ][config.COL_GSNR].sum()

    ytd_actual = current_year_df[
        current_year_df[config.COL_MONTH] <= latest_month
    ][config.COL_GSNR].sum()

    mtd_py = previous_year_df[
        previous_year_df[config.COL_MONTH] == latest_month
    ][config.COL_GSNR].sum()

    ytd_py = previous_year_df[
        previous_year_df[config.COL_MONTH] <= latest_month
    ][config.COL_GSNR].sum()

    return {
        "mtd_actual": float(mtd_actual),
        "ytd_actual": float(ytd_actual),
        "mtd_py": float(mtd_py),
        "ytd_py": float(ytd_py),
    }


# --------------------------------------------------------------
# FUNCIÓN AUXILIAR:
# Suma valores del plan por cliente
# --------------------------------------------------------------
def get_plan_client_totals(
    df_plan_client: pd.DataFrame,
    latest_month: int,
) -> tuple[float, float]:
    df = standardize_columns(df_plan_client)
    df = remove_total_like_rows(df)
    df = exclude_base_mtd_affiliates(df)

    month_columns = get_plan_client_month_columns(df)

    if latest_month not in month_columns:
        raise ValueError(
            f"No se encontró la columna del mes {latest_month} en Plan por Cliente."
        )

    month_col = month_columns[latest_month]
    months_to_sum = [month_columns[m] for m in sorted(month_columns.keys()) if m <= latest_month]

    mtd_plan_client = clean_numeric_series(df[month_col]).sum() * 1000
    ytd_plan_client = sum(clean_numeric_series(df[col]).sum() for col in months_to_sum) * 1000

    return float(mtd_plan_client), float(ytd_plan_client)


# --------------------------------------------------------------
# FUNCIÓN AUXILIAR:
# Suma valores del plan por SKU
# --------------------------------------------------------------
def get_plan_sku_totals(
    df_plan_sku: pd.DataFrame,
    latest_month: int,
) -> tuple[float, float]:
    df = standardize_columns(df_plan_sku)
    df = exclude_base_mtd_affiliates(df)

    gs_columns = get_plan_sku_gs_columns(df)

    if latest_month not in gs_columns:
        raise ValueError(
            f"No se encontró la columna GS del mes {latest_month} en Plan por SKU."
        )

    month_col = gs_columns[latest_month]
    months_to_sum = [gs_columns[m] for m in sorted(gs_columns.keys()) if m <= latest_month]

    mtd_plan_sku = clean_numeric_series(df[month_col]).sum()
    ytd_plan_sku = sum(clean_numeric_series(df[col]).sum() for col in months_to_sum)

    return float(mtd_plan_sku), float(ytd_plan_sku)


# --------------------------------------------------------------
# FUNCIÓN AUXILIAR:
# Calcula resumen ejecutivo de plan y valida coincidencia entre hojas
# --------------------------------------------------------------
def calculate_plan_totals_summary(
    df_plan_client: pd.DataFrame,
    df_plan_sku: pd.DataFrame,
    latest_month: int,
) -> dict:
    mtd_client, ytd_client = get_plan_client_totals(df_plan_client, latest_month)
    mtd_sku, ytd_sku = get_plan_sku_totals(df_plan_sku, latest_month)

    mtd_diff = abs(mtd_client - mtd_sku)
    ytd_diff = abs(ytd_client - ytd_sku)

    tolerance = 1000.0

    return {
        "mtd_plan_client": mtd_client,
        "mtd_plan_sku": mtd_sku,
        "ytd_plan_client": ytd_client,
        "ytd_plan_sku": ytd_sku,
        "mtd_plan_total": mtd_client,
        "ytd_plan_total": ytd_client,
        "mtd_plan_match": mtd_diff <= tolerance,
        "ytd_plan_match": ytd_diff <= tolerance,
        "mtd_plan_diff": mtd_diff,
        "ytd_plan_diff": ytd_diff,
    }

# --------------------------------------------------------------
# FUNCIÓN AUXILIAR:
# Calcula BTS
# --------------------------------------------------------------
def calculate_bts_totals(
    df_processed_sales: pd.DataFrame,
    latest_year: int,
    latest_month: int,
) -> dict:
    df = filter_sales_for_base_mtd_bts(df_processed_sales)
    capped_month = min(latest_month, 8)

    current_year_df = df[df[config.COL_YEAR] == latest_year].copy()
    previous_year_df = df[df[config.COL_YEAR] == (latest_year - 1)].copy()

    bts_mtd_actual = current_year_df[
        current_year_df[config.COL_MONTH] == latest_month
    ][config.COL_GSNR].sum()

    bts_mtd_py = previous_year_df[
        previous_year_df[config.COL_MONTH] == latest_month
    ][config.COL_GSNR].sum()

    bts_ytd_actual = df[
        (
            (df[config.COL_YEAR] == latest_year - 1)
            & (df[config.COL_MONTH].between(10, 12))
        )
        |
        (
            (df[config.COL_YEAR] == latest_year)
            & (df[config.COL_MONTH].between(1, capped_month))
        )
    ][config.COL_GSNR].sum()

    bts_ytd_py_comparable = df[
        (
            (df[config.COL_YEAR] == latest_year - 2)
            & (df[config.COL_MONTH].between(10, 12))
        )
        |
        (
            (df[config.COL_YEAR] == latest_year - 1)
            & (df[config.COL_MONTH].between(1, capped_month))
        )
    ][config.COL_GSNR].sum()

    bts_py_full = df[
        (
            (df[config.COL_YEAR] == latest_year - 2)
            & (df[config.COL_MONTH].between(10, 12))
        )
        |
        (
            (df[config.COL_YEAR] == latest_year - 1)
            & (df[config.COL_MONTH].between(1, 8))
        )
    ][config.COL_GSNR].sum()

    return {
        "bts_mtd_actual": float(bts_mtd_actual),
        "bts_mtd_py": float(bts_mtd_py),
        "bts_ytd_actual": float(bts_ytd_actual),
        "bts_ytd_py_comparable": float(bts_ytd_py_comparable),
        # Alias conservados para no romper tarjetas ni referencias existentes.
        "bts_actual": float(bts_ytd_actual),
        "bts_py_comparable": float(bts_ytd_py_comparable),
        "bts_py_full": float(bts_py_full),
    }


# --------------------------------------------------------------
# FUNCIÓN AUXILIAR:
# División segura
# --------------------------------------------------------------
def safe_divide(numerator: float, denominator: float) -> float:
    if denominator == 0:
        return 0.0
    return float(numerator) / float(denominator)


def has_report_value(*values, tolerance: float = 1e-9) -> bool:
    """
    Regla general para TODOS los reportes:
    una fila se muestra si existe valor en Actual, Plan o PY.
    Solo se oculta cuando los tres valores son cero real.
    """
    for value in values:
        try:
            numeric_value = float(value)
        except (TypeError, ValueError):
            numeric_value = 0.0
        if pd.notna(numeric_value) and abs(numeric_value) > tolerance:
            return True
    return False


def is_forbidden_placeholder_segment(value) -> bool:
    """
    Segmentos técnicos que NO deben imprimirse como filas de reporte.
    ZZZZ era un placeholder interno del archivo/plan y no una categoría real
    para mostrar al usuario. #N/A, Blanks, VARIOS y Other NO se excluyen aquí.
    """
    try:
        normalized_value = normalize_special_dimension_label(
            value,
            blank_as="Blanks",
            goba_to_barrilito=True,
        )
    except Exception:
        normalized_value = str(value or "").strip().upper()

    return normalized_value in {"ZZZZ", "ZZZ"}


def normalize_special_dimension_label(value, *, blank_as: str = "Blanks", goba_to_barrilito: bool = False) -> str:
    """
    Normalización única para dimensiones de reportes.

    Regla crítica:
    - #N/A, N/A, NA, NaN/None/vacío real -> #N/A
    - (blank), Blank, Blanks -> Blanks, salvo que se pida otra salida
    - VARIOS / Other / demás valores se respetan; no se mezclan con ECO/EXP/etc.
    """
    if pd.isna(value):
        return "#N/A"

    text = re.sub(r"\s+", " ", str(value).strip())
    if not text:
        return "#N/A"

    upper_text = text.upper()

    if upper_text in {"#N/A", "N/A", "NA", "NAN", "NONE", "NULL", "NAT"}:
        return "#N/A"

    if upper_text in {"(BLANK)", "BLANK", "(BLANKS)", "BLANKS"}:
        return blank_as

    if goba_to_barrilito and upper_text == "GOBA":
        return "BARRILITO"

    return upper_text


def normalize_excel_pivot_dimension(value, *, blank_as: str = "#N/A", goba_to_barrilito: bool = False) -> str:
    """
    Normalización estricta para campos que vienen DIRECTO de una pivote de Excel.

    Esta función NO busca respaldos ni rellena una dimensión con otra.
    Si el campo real de la pivote viene vacío/NaN/#N/A, el resultado queda como #N/A
    para que nunca se mezcle dentro de ECO, EXP, ACCO, BARRILITO, etc.
    """
    if pd.isna(value):
        return "#N/A"

    text = re.sub(r"\s+", " ", str(value).strip())
    if not text:
        return "#N/A"

    upper_text = text.upper()

    if upper_text in {"#N/A", "N/A", "NA", "NAN", "NONE", "NULL", "NAT"}:
        return "#N/A"

    if upper_text in {"(BLANK)", "BLANK", "(BLANKS)", "BLANKS"}:
        return blank_as

    if goba_to_barrilito and upper_text == "GOBA":
        return "BARRILITO"

    return upper_text

# --------------------------------------------------------------
# FUNCIÓN AUXILIAR:
# Construye tabla horizontal MTD/YTD
# --------------------------------------------------------------
def build_horizontal_plan_table(
    mtd_actual: float,
    ytd_actual: float,
    mtd_plan: float,
    ytd_plan: float,
    mtd_py: float,
    ytd_py: float,
) -> pd.DataFrame:
    rows = [
        {
            "Periodo": "MTD",
            "Actual": mtd_actual,
            "Plan": mtd_plan,
            "PY": mtd_py,
            "Var VS Plan": mtd_actual - mtd_plan,
            "%Var VS Plan": safe_divide(mtd_actual - mtd_plan, mtd_plan),
            "Var VS PY": mtd_actual - mtd_py,
            "%Var VS PY": safe_divide(mtd_actual - mtd_py, mtd_py),
        },
        {
            "Periodo": "YTD",
            "Actual": ytd_actual,
            "Plan": ytd_plan,
            "PY": ytd_py,
            "Var VS Plan": ytd_actual - ytd_plan,
            "%Var VS Plan": safe_divide(ytd_actual - ytd_plan, ytd_plan),
            "Var VS PY": ytd_actual - ytd_py,
            "%Var VS PY": safe_divide(ytd_actual - ytd_py, ytd_py),
        },
    ]

    return pd.DataFrame(rows)

# --------------------------------------------------------------
# FUNCIÓN AUXILIAR:
# Construye tabla BTS
# --------------------------------------------------------------
def build_bts_table(
    bts_mtd_actual: float,
    bts_mtd_py: float,
    bts_ytd_actual: float,
    bts_ytd_py_comparable: float,
) -> pd.DataFrame:
    rows = [
        {
            "Periodo": "MTD",
            "Actual": bts_mtd_actual,
            "PY": bts_mtd_py,
            "Var VS PY": bts_mtd_actual - bts_mtd_py,
            "%Var VS PY": safe_divide(bts_mtd_actual - bts_mtd_py, bts_mtd_py),
        },
        {
            "Periodo": "YTD",
            "Actual": bts_ytd_actual,
            "PY": bts_ytd_py_comparable,
            "Var VS PY": bts_ytd_actual - bts_ytd_py_comparable,
            "%Var VS PY": safe_divide(
                bts_ytd_actual - bts_ytd_py_comparable,
                bts_ytd_py_comparable,
            ),
        },
    ]

    return pd.DataFrame(rows)


# --------------------------------------------------------------
# FUNCIÓN PRINCIPAL:
# Construye payload completo de la fase 4
# --------------------------------------------------------------
def build_mtd_payload(
    df_processed_sales: pd.DataFrame,
    df_plan_client: pd.DataFrame,
    df_plan_sku: pd.DataFrame,
    selected_year: int | None = None,
    selected_month: int | None = None,
    progress_callback=None,
) -> dict:
    total_steps = 7
    emit_progress(progress_callback, "Validando bases requeridas para Base MTD", 1, total_steps)
    if df_processed_sales is None or df_processed_sales.empty:
        raise ValueError("No existe base de ventas procesada.")

    if df_plan_client is None or df_plan_client.empty:
        raise ValueError("No existe archivo de plan por cliente cargado.")

    if df_plan_sku is None or df_plan_sku.empty:
        raise ValueError("No existe archivo de plan por SKU cargado.")

    emit_progress(progress_callback, "Resolviendo año y mes de reporte", 2, total_steps)
    report_year, report_month = resolve_reporting_period(
        df_processed_sales,
        selected_year=selected_year,
        selected_month=selected_month,
    )

    emit_progress(progress_callback, "Calculando Actual y PY", 3, total_steps)
    totals = calculate_actual_and_py_totals(
        df_processed_sales,
        report_year,
        report_month,
    )

    emit_progress(progress_callback, "Integrando y conciliando Plan Cliente y Plan SKU", 4, total_steps)
    plan_summary = calculate_plan_totals_summary(
        df_plan_client,
        df_plan_sku,
        report_month,
    )

    emit_progress(progress_callback, "Calculando indicadores BTS", 5, total_steps)
    bts_totals = calculate_bts_totals(
        df_processed_sales,
        report_year,
        report_month,
    )

    emit_progress(progress_callback, "Construyendo tablas comparativas MTD y YTD", 6, total_steps)
    client_table = build_horizontal_plan_table(
        totals["mtd_actual"],
        totals["ytd_actual"],
        plan_summary["mtd_plan_client"],
        plan_summary["ytd_plan_client"],
        totals["mtd_py"],
        totals["ytd_py"],
    )

    sku_table = build_horizontal_plan_table(
        totals["mtd_actual"],
        totals["ytd_actual"],
        plan_summary["mtd_plan_sku"],
        plan_summary["ytd_plan_sku"],
        totals["mtd_py"],
        totals["ytd_py"],
    )

    bts_table = build_bts_table(
        bts_totals["bts_mtd_actual"],
        bts_totals["bts_mtd_py"],
        bts_totals["bts_ytd_actual"],
        bts_totals["bts_ytd_py_comparable"],
    )

    emit_progress(progress_callback, "Preparando resumen final de Base MTD", 7, total_steps)
    summary = {
        "mtd_act_total_k": totals["mtd_actual"] / 1000,
        "ytd_act_total_k": totals["ytd_actual"] / 1000,
        "mtd_plan_total_k": plan_summary["mtd_plan_total"] / 1000,
        "ytd_plan_total_k": plan_summary["ytd_plan_total"] / 1000,
    }

    bts_summary = {
        "bts_actual_k": bts_totals["bts_actual"] / 1000,
        "bts_py_full_k": bts_totals["bts_py_full"] / 1000,
    }

    return {
        "latest_year": report_year,
        "latest_month": report_month,
        "summary": summary,
        "plan_summary": plan_summary,
        "bts_summary": bts_summary,
        "client_table": client_table,
        "sku_table": sku_table,
        "bts_table": bts_table,
    }

# ==============================================================
# ETAPA 5: REPORTE 1
# ==============================================================

# --------------------------------------------------------------
# FUNCIÓN AUXILIAR:
# Extrae código base de canal / oficina
# --------------------------------------------------------------
def extract_channel_code(value) -> str:
    """
    Extrae el código base de Oficina de Ventas / Channel sin perder categorías.

    Regla forzada para Reporte 1:
    - #N/A, N/A, NA -> "#N/A"
    - vacío real / NaN / None / texto nan -> "Blanks"
    - (blank), Blank, Blanks -> "Blanks"
    - cualquier otro valor se conserva como código base antes de ":".
    """
    if pd.isna(value):
        return "Blanks"

    text = str(value).strip()
    if not text:
        return "Blanks"

    upper_text = re.sub(r"\s+", " ", text).upper()

    if upper_text in {"#N/A", "N/A", "NA"}:
        return "#N/A"

    if upper_text in {"NAN", "NONE", "NULL", "NAT", "(BLANK)", "BLANK", "(BLANKS)", "BLANKS"}:
        return "Blanks"

    if ":" in text:
        code = text.split(":")[0].strip().upper()
    else:
        code = text.split()[0].strip().upper()

    if code in {"#N/A", "N/A", "NA"}:
        return "#N/A"

    if code in {"", "NAN", "NONE", "NULL", "NAT", "(BLANK)", "BLANK", "(BLANKS)", "BLANKS"}:
        return "Blanks"

    return code

# --------------------------------------------------------------
# FUNCIÓN AUXILIAR:
# Obtiene etiqueta visual de canal
# --------------------------------------------------------------
def get_channel_display_label(channel_code: str) -> str:
    clean_code = str(channel_code or "").strip()
    upper_code = clean_code.upper()

    if upper_code in {"#N/A", "N/A", "NA"}:
        return "#N/A"

    if not clean_code or upper_code in {"NAN", "NONE", "NULL", "NAT", "(BLANK)", "BLANK", "(BLANKS)", "BLANKS"}:
        return "Blanks"

    return config.REPORT_1_CHANNEL_LABELS.get(upper_code, clean_code)

# --------------------------------------------------------------
# FUNCIÓN AUXILIAR:
# Identifica códigos asociados a afiliadas
# --------------------------------------------------------------
def is_affiliate_channel_code(channel_code) -> bool:
    """
    Evita que AF / AFI / Afiliadas entren a Reporte 1.

    Esta regla se aplica a Plan por Cliente porque ahí pueden existir
    renglones de afiliadas aunque ventas ya venga filtrada por segmento.
    """
    clean_code = str(channel_code or "").strip().upper()
    return clean_code in {"AF", "AFI", "AFILIADAS", "AFFILIATES"}

# --------------------------------------------------------------
# FUNCIÓN AUXILIAR:
# Excluye filas tipo total del plan cliente
# --------------------------------------------------------------
def remove_total_like_rows(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    object_cols = [col for col in df.columns if df[col].dtype == "object"]
    if not object_cols:
        return df

    keep_mask = []

    for _, row in df.iterrows():
        values = [normalize_text(row[col]) for col in object_cols]
        keep_mask.append("total" not in values)

    return df.loc[keep_mask].reset_index(drop=True)

# --------------------------------------------------------------
# FUNCIÓN AUXILIAR:
# Limpia y prepara plan cliente para reporte 1
# --------------------------------------------------------------
def prepare_plan_client_for_report_1(df_plan_client: pd.DataFrame) -> pd.DataFrame:
    df = standardize_columns(df_plan_client)
    df = remove_total_like_rows(df)

    if "Channel" not in df.columns:
        raise ValueError("No existe columna 'Channel' en Plan por Cliente.")

    df["__channel_code__"] = df["Channel"].apply(extract_channel_code)
    df = df[~df["__channel_code__"].apply(is_affiliate_channel_code)].copy()

    month_columns = get_plan_client_month_columns(df)
    if not month_columns:
        raise ValueError("No se detectaron columnas mensuales válidas en Plan por Cliente.")

    for col in month_columns.values():
        df[col] = clean_numeric_series(df[col]) * 1000

    return df

# --------------------------------------------------------------
# FUNCIÓN AUXILIAR:
# Agrega plan por canal para MTD y YTD
# --------------------------------------------------------------
def get_plan_channel_totals_for_report_1(
    df_plan_client: pd.DataFrame,
    latest_month: int,
) -> tuple[dict[str, float], dict[str, float]]:
    df = prepare_plan_client_for_report_1(df_plan_client)
    month_columns = get_plan_client_month_columns(df)

    if latest_month not in month_columns:
        raise ValueError(
            f"No se encontró la columna del mes {latest_month} en Plan por Cliente."
        )

    month_col = month_columns[latest_month]
    months_to_sum = [month_columns[m] for m in sorted(month_columns.keys()) if m <= latest_month]

    mtd_grouped = (
        df.groupby("__channel_code__", dropna=False)[month_col]
        .sum()
        .to_dict()
    )

    ytd_series = df[months_to_sum].sum(axis=1)
    ytd_grouped = (
        pd.DataFrame({
            "__channel_code__": df["__channel_code__"],
            "__ytd__": ytd_series,
        })
        .groupby("__channel_code__", dropna=False)["__ytd__"]
        .sum()
        .to_dict()
    )

    def normalize_report_1_dict_key(raw_key) -> str:
        return extract_channel_code(raw_key)

    def normalize_grouped_dict(values: dict) -> dict[str, float]:
        normalized: dict[str, float] = {}
        for key, value in values.items():
            clean_key = normalize_report_1_dict_key(key)
            if is_affiliate_channel_code(clean_key):
                continue
            normalized[clean_key] = normalized.get(clean_key, 0.0) + float(value)
        return normalized

    mtd_grouped = normalize_grouped_dict(mtd_grouped)
    ytd_grouped = normalize_grouped_dict(ytd_grouped)

    return mtd_grouped, ytd_grouped

# --------------------------------------------------------------
# FUNCIÓN AUXILIAR:
# Filtra ventas para reporte 1
# --------------------------------------------------------------
def find_report_1_sales_channel_column(df: pd.DataFrame) -> str | None:
    """
    Reporte 1 - BASE SAP.

    Regla estricta según la pivote de Excel:
    - El reporte se agrupa por Oficina de Ventas.
    - No se usa Channel, Canal, Grupo de vendedores ni ninguna columna alterna.
    - Si Oficina de Ventas viene vacío/NaN, se conserva como Blanks mediante extract_channel_code().
    """
    return find_first_existing_column(
        df,
        [
            "Oficina de Ventas",
            "Oficina Ventas",
            "Office Sales",
            "Sales Office",
        ],
    )


def normalize_report_1_segment_value(value) -> str:
    """Normaliza segmento para filtrar Reporte 1 sin borrar #N/A."""
    if pd.isna(value):
        return "#N/A"
    text = str(value).strip().upper()
    if not text or text in {"NAN", "NONE", "NULL", "NAT", "N/A", "NA"}:
        return "#N/A"
    return text


def filter_sales_for_report_1(
    df_processed_sales: pd.DataFrame,
    segment_values: list[str] | None = None,
    single_segment: str | None = None,
) -> pd.DataFrame:
    df = standardize_columns(df_processed_sales).copy()
    df = exclude_afi_affiliates(df)

    segment_col = find_first_existing_column(df, ["Segm Neg", "Segmento", "Segment"])
    channel_col = find_report_1_sales_channel_column(df)
    gsnr_col = find_first_existing_column(df, [config.COL_GSNR, "GSNR"])

    required_cols = [segment_col, channel_col, gsnr_col, config.COL_YEAR, config.COL_MONTH]
    if any(col is None for col in required_cols):
        raise ValueError(
            "Faltan columnas requeridas en ventas para Reporte 1. "
            "Se requieren Segmento, Oficina de Ventas/Channel, GSNR, Año y Mes."
        )

    df["__segment__"] = df[segment_col].apply(normalize_report_1_segment_value)
    df["__channel_code__"] = df[channel_col].apply(extract_channel_code)
    df[config.COL_GSNR] = clean_numeric_series(df[gsnr_col])

    if segment_values is not None:
        # REGLA FORZADA R1 - LEER TODO:
        # Este reporte se agrupa por Oficina de Ventas. No debe depender de una
        # lista cerrada de segmentos, porque eso puede ocultar Blanks/#N/A/VARIOS
        # u oficinas nuevas con venta. AFI ya fue excluido arriba; lo demás se conserva.
        pass

    if single_segment is not None:
        target = str(single_segment).strip().upper()
        df = df[df["__segment__"] == target].copy()

    return df

# --------------------------------------------------------------
# FUNCIÓN AUXILIAR:
# Agrega ventas por canal para MTD y YTD
# --------------------------------------------------------------
def get_sales_channel_totals_for_report_1(
    df_sales_filtered: pd.DataFrame,
    selected_year: int,
    selected_month: int,
) -> tuple[dict[str, float], dict[str, float], dict[str, float], dict[str, float]]:
    current_year_df = df_sales_filtered[df_sales_filtered[config.COL_YEAR] == selected_year].copy()
    previous_year_df = df_sales_filtered[df_sales_filtered[config.COL_YEAR] == (selected_year - 1)].copy()

    mtd_actual = (
        current_year_df[current_year_df[config.COL_MONTH] == selected_month]
        .groupby("__channel_code__", dropna=False)[config.COL_GSNR]
        .sum()
        .to_dict()
    )

    ytd_actual = (
        current_year_df[current_year_df[config.COL_MONTH] <= selected_month]
        .groupby("__channel_code__", dropna=False)[config.COL_GSNR]
        .sum()
        .to_dict()
    )

    mtd_py = (
        previous_year_df[previous_year_df[config.COL_MONTH] == selected_month]
        .groupby("__channel_code__", dropna=False)[config.COL_GSNR]
        .sum()
        .to_dict()
    )

    ytd_py = (
        previous_year_df[previous_year_df[config.COL_MONTH] <= selected_month]
        .groupby("__channel_code__", dropna=False)[config.COL_GSNR]
        .sum()
        .to_dict()
    )

    def clean_dict(values: dict) -> dict[str, float]:
        cleaned = {}
        for key, value in values.items():
            clean_key = extract_channel_code(key)

            if is_affiliate_channel_code(clean_key):
                continue

            cleaned[clean_key] = cleaned.get(clean_key, 0.0) + float(value)
        return cleaned

    return (
        clean_dict(mtd_actual),
        clean_dict(ytd_actual),
        clean_dict(mtd_py),
        clean_dict(ytd_py),
    )

# --------------------------------------------------------------
# FUNCIÓN AUXILIAR:
# Construye renglón estándar
# --------------------------------------------------------------
def build_report_1_row(
    office_label: str,
    actual: float,
    plan: float | None,
    py: float,
    is_total: bool = False,
    is_highlight: bool = False,
) -> dict:
    row = {
        "Oficina de Ventas": office_label,
        "Actual": float(actual),
        "Plan": None if plan is None else float(plan),
        "PY": float(py),
        "Var VS Plan": None,
        "%Var VS Plan": None,
        "Var VS PY": float(actual) - float(py),
        "%Var VS PY": safe_divide(float(actual) - float(py), float(py)),
        "__is_total__": is_total,
        "__is_highlight__": is_highlight,
    }

    if plan is not None:
        row["Var VS Plan"] = float(actual) - float(plan)
        row["%Var VS Plan"] = safe_divide(float(actual) - float(plan), float(plan))

    return row

# --------------------------------------------------------------
# FUNCIÓN AUXILIAR:
# Ordena códigos del Reporte 1 sin ocultar códigos nuevos
# --------------------------------------------------------------
def get_ordered_report_1_codes(
    codes_present: set[str],
    exclude_codes: set[str] | None = None,
) -> list[str]:
    """
    Mantiene el orden corporativo configurado para los códigos conocidos,
    pero agrega al final cualquier código nuevo que aparezca en Actual, Plan o PY.

    Antes, si un código no estaba en config.REPORT_1_CHANNEL_ORDER, no se mostraba.
    Con esta función, el orden de config funciona como preferencia visual,
    no como candado de filas.
    """
    exclude_codes = exclude_codes or set()

    clean_codes = set()
    for code in codes_present:
        clean_code = normalize_special_dimension_label(code, blank_as="Blanks")
        if clean_code in exclude_codes:
            continue
        if is_affiliate_channel_code(clean_code):
            continue
        clean_codes.add(clean_code)

    configured_order = [
        str(code).strip().upper()
        for code in getattr(config, "REPORT_1_CHANNEL_ORDER", [])
        if str(code).strip()
    ]

    configured_codes = [
        code for code in configured_order
        if code in clean_codes and code not in exclude_codes
    ]

    extra_codes = sorted(
        code for code in clean_codes
        if code not in set(configured_order) and code not in exclude_codes
    )

    return configured_codes + extra_codes

# --------------------------------------------------------------
# FUNCIÓN AUXILIAR:
# Construye tabla WITHOUT KENS
# --------------------------------------------------------------
def build_report_1_without_kens_table(
    actual_dict: dict[str, float],
    plan_dict: dict[str, float],
    py_dict: dict[str, float],
) -> pd.DataFrame:
    codes_present = set(actual_dict.keys()) | set(plan_dict.keys()) | set(py_dict.keys())

    ordered_codes = get_ordered_report_1_codes(
        codes_present=codes_present,
        # Bloque superior actualizado: ahora es Channel Corp completo.
        # Ya no se excluye IT porque KENS también debe formar parte del bloque superior.
        exclude_codes={"AF", "AFI"},
    )

    rows = []
    total_actual = 0.0
    total_plan = 0.0
    total_py = 0.0

    for code in ordered_codes:
        actual = float(actual_dict.get(code, 0.0))
        plan = float(plan_dict.get(code, 0.0))
        py = float(py_dict.get(code, 0.0))

        # Se muestra si tiene venta en Actual, Plan o PY.
        # Solo se oculta cuando los tres valores son cero real.
        if not has_report_value(actual, plan, py):
            continue

        total_actual += actual
        total_plan += plan
        total_py += py

        rows.append(
            build_report_1_row(
                office_label=get_channel_display_label(code),
                actual=actual,
                plan=plan,
                py=py,
            )
        )

    rows.append(
        build_report_1_row(
            office_label=config.REPORT_1_TOTAL_LABEL,
            actual=total_actual,
            plan=total_plan,
            py=total_py,
            is_total=True,
        )
    )

    return pd.DataFrame(rows)


# --------------------------------------------------------------
# FUNCIÓN PRINCIPAL:
# Construye payload completo de Reporte 1
# --------------------------------------------------------------
def build_report_1_payload(
    df_processed_sales: pd.DataFrame,
    df_plan_client: pd.DataFrame,
    selected_year: int | None = None,
    selected_month: int | None = None,
    progress_callback=None,
) -> dict:
    total_steps = 6
    emit_progress(progress_callback, "Validando bases para Reporte 1", 1, total_steps)
    if df_processed_sales is None or df_processed_sales.empty:
        raise ValueError("No existe base de ventas procesada.")

    if df_plan_client is None or df_plan_client.empty:
        raise ValueError("No existe archivo de plan por cliente cargado.")

    emit_progress(progress_callback, "Resolviendo periodo del Reporte 1", 2, total_steps)
    report_year, report_month = resolve_reporting_period(
        df_processed_sales,
        selected_year=selected_year,
        selected_month=selected_month,
    )

    emit_progress(progress_callback, "Preparando Plan por Oficina de Ventas", 3, total_steps)
    plan_mtd_by_channel, plan_ytd_by_channel = get_plan_channel_totals_for_report_1(
        df_plan_client,
        report_month,
    )

    emit_progress(progress_callback, "Preparando ventas Actual y PY por Oficina", 4, total_steps)
    sales_without_kens = filter_sales_for_report_1(
        df_processed_sales,
        # Bloque superior actualizado: ACCO + BARRILITO + KENS.
        segment_values=list(config.REPORT_1_SEGMENTS_WITHOUT_KENS) + [config.REPORT_1_SEGMENT_KENS],
    )

    (
        mtd_actual_without_kens,
        ytd_actual_without_kens,
        mtd_py_without_kens,
        ytd_py_without_kens,
    ) = get_sales_channel_totals_for_report_1(
        sales_without_kens,
        report_year,
        report_month,
    )

    emit_progress(progress_callback, "Construyendo tablas MTD y YTD", 5, total_steps)
    mtd_without_kens_table = build_report_1_without_kens_table(
        actual_dict=mtd_actual_without_kens,
        plan_dict=plan_mtd_by_channel,
        py_dict=mtd_py_without_kens,
    )

    ytd_without_kens_table = build_report_1_without_kens_table(
        actual_dict=ytd_actual_without_kens,
        plan_dict=plan_ytd_by_channel,
        py_dict=ytd_py_without_kens,
    )


    emit_progress(progress_callback, "Preparando resumen final del Reporte 1", 6, total_steps)
    summary = {
        "latest_year": report_year,
        "latest_month": report_month,
        "segments_without_kens_label": "ACCO + BARR + KENS",
    }

    return {
        "summary": summary,
        "mtd_without_kens_table": mtd_without_kens_table,
        "ytd_without_kens_table": ytd_without_kens_table,
    }

# ==============================================================
# ETAPA 6: REPORTE 2 - SEGMENT X REGION
# ==============================================================

# --------------------------------------------------------------
# FUNCIÓN AUXILIAR:
# Busca la primera columna existente entre varias opciones
# --------------------------------------------------------------
def find_first_existing_column(df: pd.DataFrame, candidate_columns: list[str]) -> str | None:
    normalized_map = {normalize_text(col): col for col in df.columns}

    for candidate in candidate_columns:
        normalized_candidate = normalize_text(candidate)
        if normalized_candidate in normalized_map:
            return normalized_map[normalized_candidate]

    return None

def normalize_dimension_candidate_value(value) -> str:
    """
    Normalización de apoyo SOLO para elegir columnas de dimensión.
    No se usa para sumar importes; solo ayuda a decidir qué columna trae
    las categorías reales del reporte.
    """
    if pd.isna(value):
        return "#N/A"

    text = re.sub(r"\s+", " ", str(value).strip())
    if not text:
        return "#N/A"

    upper_text = text.upper()

    if upper_text in {"#N/A", "N/A", "NA", "NAN", "NONE", "NULL", "NAT"}:
        return "#N/A"

    if upper_text in {"(BLANK)", "BLANK", "(BLANKS)", "BLANKS"}:
        return "Blanks"

    if upper_text == "GOBA":
        return "BARRILITO"

    return upper_text


# --------------------------------------------------------------
# FUNCIÓN AUXILIAR CRÍTICA:
# Resuelve dimensiones por fila sin perder #N/A / Blanks / VARIOS.
# --------------------------------------------------------------
def is_explicit_na_like(value) -> bool:
    if pd.isna(value):
        return True
    text = re.sub(r"\s+", " ", str(value).strip()).upper()
    return text in {"", "#N/A", "N/A", "NA", "NAN", "NONE", "NULL", "NAT"}


def is_explicit_blank_like(value) -> bool:
    if pd.isna(value):
        return False
    text = re.sub(r"\s+", " ", str(value).strip()).upper()
    return text in {"(BLANK)", "BLANK", "(BLANKS)", "BLANKS"}


def normalize_business_dimension_value(value, *, goba_to_barrilito: bool = False) -> str:
    """
    Normaliza una dimensión de negocio sin ocultar categorías especiales.

    Regla global para reportes:
    - vacío / NaN / N/A / #N/A -> #N/A
    - blank explícito -> Blanks
    - GOBA -> BARRILITO solo cuando el reporte lo requiere
    - cualquier otra categoría se respeta en mayúsculas
    """
    if pd.isna(value):
        return "#N/A"

    text = re.sub(r"\s+", " ", str(value).strip())
    if not text:
        return "#N/A"

    upper_text = text.upper()

    if upper_text in {"#N/A", "N/A", "NA", "NAN", "NONE", "NULL", "NAT"}:
        return "#N/A"

    if upper_text in {"(BLANK)", "BLANK", "(BLANKS)", "BLANKS"}:
        return "Blanks"

    if goba_to_barrilito and upper_text == "GOBA":
        return "BARRILITO"

    return upper_text


def normalize_special_override_dimension(value) -> str | None:
    """
    Detecta SOLO valores especiales reales que deben ganar sobre Region/Channel.

    Este fix es para los casos que se veían en Excel como #N/A o Blanks, pero
    la app los metía en ECO/EXP porque otra columna traía ECO/EXP. Si una fila
    trae Channel/Canal/Oficina explícitamente vacío, NaN, #N/A o Blanks, esa
    fila debe conservarse como #N/A/Blanks y NO heredarse a ECO/EXP.
    """
    if pd.isna(value):
        return "#N/A"

    text = re.sub(r"\s+", " ", str(value).strip())
    if not text:
        return "#N/A"

    upper_text = text.upper()

    if upper_text in {"#N/A", "N/A", "NA", "NAN", "NONE", "NULL", "NAT"}:
        return "#N/A"

    if upper_text in {"(BLANK)", "BLANK", "(BLANKS)", "BLANKS"}:
        return "Blanks"

    return None


def get_first_special_dimension_override(row: pd.Series, candidate_columns: list[str]) -> str | None:
    """
    Revisa varias columnas de la MISMA fila y conserva #N/A/Blanks reales.

    Esto corrige el caso donde Excel sí tiene la categoría #N/A, pero otra
    columna trae EXP/ECO y el reporte terminaba mandando esa venta ahí.
    Solo regresa algo cuando el valor es explícitamente especial.
    """
    for col in candidate_columns:
        if col not in row.index:
            continue
        special_value = normalize_special_override_dimension(row.get(col))
        if special_value is not None:
            return special_value
    return None


def get_all_matching_columns(df: pd.DataFrame, candidate_columns: list[str]) -> list[str]:
    """Obtiene todas las columnas que coinciden con los nombres candidatos."""
    found: list[str] = []
    normalized_candidates = {normalize_text(name) for name in candidate_columns}
    for col in df.columns:
        if normalize_text(col) in normalized_candidates and col not in found:
            found.append(col)
    return found


def choose_column_preferring_real_specials(df: pd.DataFrame, candidate_columns: list[str]) -> str | None:
    """
    Si hay columnas duplicadas/parecidas, elige la que trae más #N/A/Blanks reales.
    Esto evita agarrar una columna alterna que ya venía rellena como EXP/ECO.
    """
    columns = get_all_matching_columns(df, candidate_columns)
    if not columns:
        return None

    def _score(col: str) -> tuple[int, int, int]:
        normalized = df[col].apply(normalize_special_override_dimension)
        special_count = int(normalized.notna().sum())
        non_zero_count = int(df[col].notna().sum())
        # Menor índice gana en empate para respetar orden del archivo.
        return (special_count, non_zero_count, -list(df.columns).index(col))

    return sorted(columns, key=_score, reverse=True)[0]


def resolve_special_dimension_override_from_row(row: pd.Series, candidate_columns: list[str]) -> str | None:
    """Busca #N/A/Blanks explícitos por fila en columnas alternas de la dimensión."""
    for col in candidate_columns:
        if col not in row.index:
            continue
        override_value = normalize_special_override_dimension(row.get(col))
        if override_value is not None:
            return override_value
    return None


def get_existing_columns_in_order(df: pd.DataFrame, candidate_names: list[str]) -> list[str]:
    return get_candidate_columns_by_names(df, candidate_names)


def resolve_dimension_from_row(
    row: pd.Series,
    preferred_columns: list[str],
    fallback_columns: list[str] | None = None,
    *,
    goba_to_barrilito: bool = False,
) -> str:
    """
    Resuelve una categoría POR FILA.

    Esto es lo que faltaba en R1/R2/R3: no basta con elegir una sola columna
    para todo el DataFrame, porque hay filas donde una columna alterna trae EXP/ECO
    y la dimensión real viene como #N/A o vacía. Esa fila NO se debe meter en EXP.

    Orden:
    1) si la columna preferida existe, se usa aunque venga vacía, porque vacío = #N/A.
    2) si no existe ninguna preferida, se buscan columnas fallback.
    3) jamás se reemplaza un #N/A/vacío real por EXP/ECO/NORTE/etc. de otra columna.
    """
    for col in preferred_columns:
        if col in row.index:
            return normalize_business_dimension_value(
                row.get(col),
                goba_to_barrilito=goba_to_barrilito,
            )

    for col in (fallback_columns or []):
        if col in row.index:
            return normalize_business_dimension_value(
                row.get(col),
                goba_to_barrilito=goba_to_barrilito,
            )

    return "#N/A"


def get_candidate_columns_by_names(df: pd.DataFrame, candidate_names: list[str]) -> list[str]:
    """
    Devuelve columnas candidatas respetando el orden solicitado, sin duplicados.
    """
    if df is None or df.empty:
        return []

    columns = list(df.columns)
    normalized_map: dict[str, list[str]] = {}

    for col in columns:
        normalized_map.setdefault(normalize_text(col), []).append(col)

    result: list[str] = []

    for name in candidate_names:
        normalized_name = normalize_text(name)
        for col in normalized_map.get(normalized_name, []):
            if col not in result:
                result.append(col)

    return result


def score_dimension_column(
    df: pd.DataFrame,
    column_name: str,
    expected_values: set[str] | None = None,
    priority_bonus: int = 0,
) -> tuple[int, int, int, int, str]:
    """
    Califica una columna candidata.

    La razón del score es resolver el problema actual:
    cuando existen dos columnas posibles (por ejemplo Region y Sales region short,
    o Channel y Grupo de vendedores), NO debemos escoger a ciegas la primera.
    Debe ganar la columna que realmente trae más categorías útiles, incluyendo
    #N/A, Blanks, VARIOS u Other.
    """
    if column_name not in df.columns:
        return (-1, -1, -1, -1, column_name)

    series = df[column_name]
    normalized = series.apply(normalize_dimension_candidate_value)

    non_empty_count = int((normalized.astype(str).str.strip() != "").sum())
    unique_values = set(normalized.dropna().astype(str).str.strip())

    special_values = {"#N/A", "Blanks", "VARIOS", "VARIOUS", "OTHER", "OTHERS"}
    special_count = len(unique_values & special_values)

    expected_count = 0
    if expected_values:
        expected_count = len(unique_values & expected_values)

    useful_unique_count = len(unique_values - {"", "NAN", "NONE", "NULL", "NAT"})

    return (
        special_count,
        expected_count,
        useful_unique_count,
        non_empty_count + int(priority_bonus),
        column_name,
    )


def choose_best_dimension_column(
    df: pd.DataFrame,
    candidate_names: list[str],
    expected_values: set[str] | None = None,
) -> str | None:
    """
    Elige la mejor columna real para una dimensión.

    Esto evita el error de meter ventas de #N/A en EXP/ECO solo porque el código
    eligió otra columna que también existía, pero no era la del pivote.
    """
    candidates = get_candidate_columns_by_names(df, candidate_names)

    if not candidates:
        return None

    scored: list[tuple[tuple[int, int, int, int, str], str]] = []

    for priority_index, col in enumerate(candidates):
        # Pequeño bono por prioridad, pero menor que encontrar #N/A/Blanks/VARIOS.
        priority_bonus = max(len(candidates) - priority_index, 0)
        score = score_dimension_column(
            df,
            col,
            expected_values=expected_values,
            priority_bonus=priority_bonus,
        )
        scored.append((score, col))

    scored.sort(reverse=True, key=lambda item: item[0])
    return scored[0][1]


# --------------------------------------------------------------
# FUNCIÓN AUXILIAR:
# Detecta la columna correcta de región para Reporte 2
# --------------------------------------------------------------
def find_report_2_region_column(df: pd.DataFrame) -> str | None:
    """
    Detecta la columna REAL de Región para Segment x Region.

    Corrección final:
    Para este reporte el pivote usa la columna Region. Por eso se respeta
    Region/Región antes que cualquier otra columna parecida. El scoring anterior
    podía elegir una columna alterna y mezclar importes de #N/A, VARIOS o Blanks
    dentro de ECO/EXP/NORTE/etc.
    """
    preferred_columns = [
        "Region",
        "REGION",
        "Región",
        "REGIÓN",
    ]

    column = find_first_existing_column(df, preferred_columns)
    if column is not None:
        return column

    return None




# --------------------------------------------------------------
# FUNCIÓN AUXILIAR:
# Normaliza texto visible para Región
# --------------------------------------------------------------
def normalize_report_2_label(value) -> str:
    """Normaliza Región para Segment x Region igual que la pivote: vacío/#N/A queda #N/A."""
    return normalize_excel_pivot_dimension(value, blank_as="#N/A")


# --------------------------------------------------------------
# FUNCIÓN AUXILIAR:
# Normaliza texto visible para Segmento
# GOBA se sustituye por BARRILITO
# ZZZZ se excluye después en filtros
# --------------------------------------------------------------
# --------------------------------------------------------------
# FUNCIÓN AUXILIAR:
# Normaliza texto visible para Segmento
# GOBA se sustituye por BARRILITO
# ZZZZ se excluye después en filtros
# --------------------------------------------------------------
def normalize_report_2_segment_label(value) -> str:
    """Normaliza Segmento sin borrar #N/A; GOBA se muestra como BARRILITO."""
    return normalize_special_dimension_label(value, blank_as="Blanks", goba_to_barrilito=True)


# --------------------------------------------------------------
# FUNCIÓN AUXILIAR:
# Normaliza Category para Reporte 2
# --------------------------------------------------------------
def normalize_report_2_category_label(value) -> str:
    """Normaliza Category sin mezclar #N/A con Blanks."""
    return normalize_special_dimension_label(value, blank_as="Blanks")


def normalize_report_2_sales_category_label(value) -> str:
    """BASE SAP: #N/A/NA se conserva como #N/A; Blanks se conserva como Blanks."""
    return normalize_special_dimension_label(value, blank_as="Blanks")


def normalize_report_2_plan_category_label(value) -> str | None:
    """
    Plan2026 by SKU: normaliza valores explícitos de Corpo Category.

    Importante:
    - Si el valor viene vacío/NaN, NO se decide aquí si es #N/A o Blanks.
    - La decisión dinámica de vacíos se hace por fila en
      resolve_report_2_plan_category_from_row().
    """
    if pd.isna(value):
        return None

    text = re.sub(r"\s+", " ", str(value).strip())
    if not text:
        return None

    upper_text = text.upper()

    if upper_text in {"#N/A", "N/A", "NA"}:
        return "#N/A"

    if upper_text in {"(BLANK)", "BLANK", "(BLANKS)", "BLANKS"}:
        return "Blanks"

    if upper_text in {"NAN", "NONE", "NULL", "NAT"}:
        return None

    return text


def classify_report_2_category_value(value) -> str | None:
    """
    Clasifica una etiqueta de categoría sin adivinar ni mezclar.

    Regresa:
    - "#N/A" cuando el valor trae explícitamente #N/A / N/A / NA.
    - "Blanks" cuando el valor trae explícitamente blank / blanks / (blank).
    - None cuando el valor realmente está vacío o no sirve para clasificar.
    - La categoría original cuando es una categoría normal.
    """
    if pd.isna(value):
        return None

    text = re.sub(r"\s+", " ", str(value).strip())
    if not text:
        return None

    upper_text = text.upper()

    if upper_text in {"#N/A", "N/A", "NA"}:
        return "#N/A"

    if upper_text in {"(BLANK)", "BLANK", "(BLANKS)", "BLANKS"}:
        return "Blanks"

    if upper_text in {"NAN", "NONE", "NULL", "NAT"}:
        return None

    return text


def get_report_2_category_helper_columns(row: pd.Series, category_col: str) -> list[str]:
    """
    Busca columnas auxiliares del Plan que pueden conservar la categoría real.

    Importante para Plan2026 by SKU:
    algunas filas pueden traer Corpo Category vacío, pero otra columna como
    Rule: Seg-Corpo category conserva #N/A. Esa columna debe revisarse antes
    de mandar la fila a Blanks.
    """
    helper_columns: list[str] = []
    category_col_normalized = normalize_text(category_col)

    priority_names = [
        "Rule: Seg-Corpo category",
        "Rule Seg-Corpo category",
        "Rule: Seg Corpo category",
        "Rule Seg Corpo category",
        "Seg-Corpo category",
        "Seg Corpo category",
        "Rule: Seg-Corpo Category",
        "Rule Seg-Corpo Category",
        "Corpo Category",
        "CorpoCategory",
        "Category",
    ]
    priority_normalized = [normalize_text(name) for name in priority_names]

    for target in priority_normalized:
        for col in row.index:
            normalized_col = normalize_text(col)
            if normalized_col == category_col_normalized:
                continue
            if normalized_col == target and col not in helper_columns:
                helper_columns.append(col)

    for col in row.index:
        normalized_col = normalize_text(col)
        if normalized_col == category_col_normalized:
            continue
        if col in helper_columns:
            continue
        if "category" in normalized_col and (
            "rule" in normalized_col
            or "seg" in normalized_col
            or "corpo" in normalized_col
        ):
            helper_columns.append(col)

    return helper_columns


def resolve_report_2_plan_category_from_row(row: pd.Series, category_col: str) -> str:
    """
    Resuelve Corpo Category del Plan SIN fijar categorías ni montos.

    Regla dinámica:
    1) Si Corpo Category trae una categoría explícita, se respeta:
       - #N/A / N/A / NA -> #N/A
       - (blank) / Blanks -> Blanks
       - cualquier categoría normal -> igual
    2) Si Corpo Category viene vacío/NaN:
       - si la fila trae Material o Descripción del Material útil, se clasifica como #N/A.
       - si NO trae Material ni Descripción útil, se clasifica como Blanks.

    Nota:
    No se usa local Sub category / Categoría del Material para decidir #N/A,
    porque en el Plan existen filas tipo Blanks que sí traen subcategoría
    pero NO traen material/descripcion real. Usar esa columna mete esos importes
    dentro de #N/A y descuadra las sumas.
    """
    explicit_category = normalize_report_2_plan_category_label(row.get(category_col, None))
    if explicit_category is not None:
        return explicit_category

    material_description_candidates = [
        "Material",
        "Descripción del Material",
        "Descripcion del Material",
        "Descripción Material",
        "Descripcion Material",
    ]

    for candidate_col in material_description_candidates:
        if candidate_col not in row.index:
            continue

        value = row.get(candidate_col)
        if pd.isna(value):
            continue

        text = re.sub(r"\s+", " ", str(value).strip())
        if not text:
            continue

        upper_text = text.upper()
        if upper_text in {"#N/A", "N/A", "NA", "NAN", "NONE", "NULL", "NAT", "(BLANK)", "BLANK", "(BLANKS)", "BLANKS"}:
            continue

        return "#N/A"

    return "Blanks"

# --------------------------------------------------------------
# FUNCIÓN AUXILIAR:
# Normaliza producto / subcategoría para Reporte 2 Category
# --------------------------------------------------------------
def normalize_report_2_product_label(value) -> str:
    if pd.isna(value):
        return "#N/A"

    text = re.sub(r"\s+", " ", str(value).strip())
    if not text:
        return "#N/A"

    upper_text = text.upper()

    if upper_text in {"#N/A", "N/A", "NA", "NAN", "NONE", "NULL", "NAT"}:
        return "#N/A"

    return text

# --------------------------------------------------------------
# FUNCIÓN AUXILIAR:
# Normaliza Channel para Reporte 3
# --------------------------------------------------------------
def normalize_report_3_channel_label(value) -> str:
    """Normaliza Channel para Reporte 3 sin ocultar #N/A, Blanks, VARIOS u Other."""
    # Reporte 3 debe comportarse como la pivote: si Channel/REGION viene vacío o #N/A, se muestra #N/A.
    return normalize_excel_pivot_dimension(value, blank_as="#N/A", goba_to_barrilito=True)


# --------------------------------------------------------------
# FUNCIÓN AUXILIAR:
# Normaliza nombre cliente para Reporte 4
# --------------------------------------------------------------
# --------------------------------------------------------------
# FUNCIÓN AUXILIAR:
# Normaliza nombre cliente para Reporte 4
# --------------------------------------------------------------
def normalize_report_4_client_name(value) -> str:
    if pd.isna(value):
        return ""

    text = re.sub(r"\s+", " ", str(value).strip())
    if not text:
        return ""

    return text.upper().replace(",", "")

# --------------------------------------------------------------
# FUNCIÓN AUXILIAR:
# Normaliza código cliente para Reporte 4
# --------------------------------------------------------------
def normalize_report_4_client_code(value) -> str:
    if pd.isna(value):
        return ""

    text = str(value).strip().upper()
    if text in {"", "NAN", "NONE", "NULL", "NAT", "(BLANK)", "BLANK", "(BLANKS)", "BLANKS"}:
        return ""

    return text

# --------------------------------------------------------------
# FUNCIÓN AUXILIAR:
# Excluye AFI: Afiliadas
# --------------------------------------------------------------
def exclude_afi_affiliates(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    vendor_group_col = find_first_existing_column(
        df,
        [
            "Grupo de vendedores",
            "Grupo de Vendedores",
            "Grupo vendedores",
        ],
    )

    if vendor_group_col is None:
        return df

    excluded_value = normalize_report_2_label(config.REPORT_2_EXCLUDED_VENDOR_GROUP)

    vendor_series = df[vendor_group_col].apply(normalize_report_2_label)
    df = df.loc[vendor_series != excluded_value].copy()

    return df

# --------------------------------------------------------------
# FUNCIÓN AUXILIAR:
# Prepara ventas para Reporte 2
# --------------------------------------------------------------
def prepare_sales_for_report_2(df_processed_sales: pd.DataFrame) -> pd.DataFrame:
    df = standardize_columns(df_processed_sales)
    df = exclude_afi_affiliates(df)

    # MISMA ESTRUCTURA QUE LA PIVOTE DE EXCEL:
    # Rows = Segm Neg + Region.
    # Regla estricta: NO se usan Channel/Canal/Oficina/Sales Region como respaldo.
    # Si Region viene vacío/NaN/#N/A, se queda como #N/A.
    segment_col = find_first_existing_column(df, ["Segm Neg", "Segmento", "Segment"])
    region_col = find_first_existing_column(df, ["Region", "REGION", "Región", "REGIÓN"])
    gsnr_col = find_first_existing_column(df, [config.COL_GSNR, "GSNR"])

    required_columns = [segment_col, region_col, gsnr_col, config.COL_YEAR, config.COL_MONTH]
    if any(col is None for col in required_columns):
        raise ValueError(
            "Faltan columnas requeridas en ventas para Reporte 2. "
            "Se requieren Segm Neg, Region, GSNR, Año y Mes."
        )

    df = df.copy()
    df["__segment__"] = df[segment_col].apply(normalize_report_2_segment_label)
    df["__region__"] = df[region_col].apply(normalize_report_2_label)
    df["__gsnr__"] = clean_numeric_series(df[gsnr_col])

    return df


def prepare_plan_sku_for_report_2(df_plan_sku: pd.DataFrame) -> pd.DataFrame:
    df = standardize_columns(df_plan_sku)
    df = exclude_afi_affiliates(df)

    # MISMA ESTRUCTURA QUE LA PIVOTE DE EXCEL:
    # Rows = Segmento + REGION.
    # Regla estricta: NO se usan Channel/Canal/Sales Region como respaldo.
    # Si REGION viene vacío/NaN/#N/A, se queda como #N/A.
    segment_col = find_first_existing_column(df, ["Segmento", "SEGMENTO", "Segment", "Segm Neg"])
    region_col = find_first_existing_column(df, ["REGION", "Region", "Región", "REGIÓN"])

    if segment_col is None or region_col is None:
        raise ValueError(
            "Faltan columnas requeridas en Plan por SKU para Reporte 2. "
            "Se requieren Segmento y REGION."
        )

    month_columns = get_plan_sku_gs_columns(df)
    if not month_columns:
        raise ValueError("No se detectaron columnas mensuales válidas en Plan por SKU.")

    df = df.copy()
    df["__segment__"] = df[segment_col].apply(normalize_report_2_segment_label)
    df["__region__"] = df[region_col].apply(normalize_report_2_label)

    for col in month_columns.values():
        df[col] = clean_numeric_series(df[col])

    return df


def get_sales_segment_region_totals_for_report_2(
    df_processed_sales: pd.DataFrame,
    selected_year: int,
    selected_month: int,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    df = prepare_sales_for_report_2(df_processed_sales)

    current_year_df = df[df[config.COL_YEAR] == selected_year].copy()
    previous_year_df = df[df[config.COL_YEAR] == (selected_year - 1)].copy()

    mtd_actual = (
        current_year_df[current_year_df[config.COL_MONTH] == selected_month]
        .groupby(["__segment__", "__region__"], dropna=False)["__gsnr__"]
        .sum()
        .reset_index()
        .rename(
            columns={
                "__segment__": "Segmento",
                "__region__": "Región",
                "__gsnr__": "Valor",
            }
        )
    )

    ytd_actual = (
        current_year_df[current_year_df[config.COL_MONTH] <= selected_month]
        .groupby(["__segment__", "__region__"], dropna=False)["__gsnr__"]
        .sum()
        .reset_index()
        .rename(
            columns={
                "__segment__": "Segmento",
                "__region__": "Región",
                "__gsnr__": "Valor",
            }
        )
    )

    mtd_py = (
        previous_year_df[previous_year_df[config.COL_MONTH] == selected_month]
        .groupby(["__segment__", "__region__"], dropna=False)["__gsnr__"]
        .sum()
        .reset_index()
        .rename(
            columns={
                "__segment__": "Segmento",
                "__region__": "Región",
                "__gsnr__": "Valor",
            }
        )
    )

    ytd_py = (
        previous_year_df[previous_year_df[config.COL_MONTH] <= selected_month]
        .groupby(["__segment__", "__region__"], dropna=False)["__gsnr__"]
        .sum()
        .reset_index()
        .rename(
            columns={
                "__segment__": "Segmento",
                "__region__": "Región",
                "__gsnr__": "Valor",
            }
        )
    )

    return mtd_actual, ytd_actual, mtd_py, ytd_py

# --------------------------------------------------------------
# FUNCIÓN AUXILIAR:
# Agrega plan Segment x Region
# --------------------------------------------------------------
def get_plan_segment_region_totals_for_report_2(
    df_plan_sku: pd.DataFrame,
    latest_month: int,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    df = prepare_plan_sku_for_report_2(df_plan_sku)
    gs_columns = get_plan_sku_gs_columns(df)

    if latest_month not in gs_columns:
        raise ValueError(
            f"No se encontró la columna GS del mes {latest_month} en Plan por SKU."
        )

    month_col = gs_columns[latest_month]
    months_to_sum = [gs_columns[m] for m in sorted(gs_columns.keys()) if m <= latest_month]

    mtd_plan = (
        df.groupby(["__segment__", "__region__"], dropna=False)[month_col]
        .sum()
        .reset_index()
        .rename(
            columns={
                "__segment__": "Segmento",
                "__region__": "Región",
                month_col: "Valor",
            }
        )
    )

    ytd_plan = (
        df.assign(__ytd__=df[months_to_sum].sum(axis=1))
        .groupby(["__segment__", "__region__"], dropna=False)["__ytd__"]
        .sum()
        .reset_index()
        .rename(
            columns={
                "__segment__": "Segmento",
                "__region__": "Región",
                "__ytd__": "Valor",
            }
        )
    )

    return mtd_plan, ytd_plan

# --------------------------------------------------------------
# FUNCIÓN AUXILIAR:
# Convierte agregados a diccionario
# --------------------------------------------------------------
def aggregated_segment_region_df_to_dict(df: pd.DataFrame) -> dict[tuple[str, str], float]:
    if df is None or df.empty:
        return {}

    result = {}

    for _, row in df.iterrows():
        key = (
            normalize_report_2_segment_label(row["Segmento"]),
            normalize_report_2_label(row["Región"]),
        )
        result[key] = result.get(key, 0.0) + float(row["Valor"])

    return result

# --------------------------------------------------------------
# FUNCIÓN AUXILIAR:
# Llave de orden para segmento
# --------------------------------------------------------------
def get_report_2_segment_sort_key(segment_value: str) -> tuple[int, str]:
    normalized_value = normalize_report_2_segment_label(segment_value)

    segment_order = ["ACCO", "BARRILITO", "KENS"]

    if normalized_value in segment_order:
        return segment_order.index(normalized_value), normalized_value

    return len(segment_order), normalized_value

# --------------------------------------------------------------
# FUNCIÓN AUXILIAR:
# Llave de orden para región
# --------------------------------------------------------------
def get_report_2_region_sort_key(region_value: str) -> tuple[int, str]:
    normalized_value = normalize_report_2_label(region_value)

    if normalized_value in config.REPORT_2_REGION_ORDER:
        return config.REPORT_2_REGION_ORDER.index(normalized_value), normalized_value

    return len(config.REPORT_2_REGION_ORDER), normalized_value

# --------------------------------------------------------------
# FUNCIÓN AUXILIAR:
# Construye renglón de Reporte 2
# --------------------------------------------------------------
def build_report_2_row(
    segment_label: str,
    region_label: str,
    actual: float,
    plan: float,
    py: float,
    is_total: bool = False,
    is_grand_total: bool = False,
) -> dict:
    return {
        "Segmento": segment_label,
        "Región": region_label,
        "Actual": float(actual),
        "Plan": float(plan),
        "PY": float(py),
        "Var VS Plan": float(actual) - float(plan),
        "%Var VS Plan": safe_divide(float(actual) - float(plan), float(plan)),
        "Var VS PY": float(actual) - float(py),
        "%Var VS PY": safe_divide(float(actual) - float(py), float(py)),
        "__is_total__": is_total,
        "__is_grand_total__": is_grand_total,
    }

# --------------------------------------------------------------
# FUNCIÓN AUXILIAR:
# Construye tabla final Segment x Region
# --------------------------------------------------------------
def build_report_2_segment_region_table(
    actual_df: pd.DataFrame,
    plan_df: pd.DataFrame,
    py_df: pd.DataFrame,
) -> pd.DataFrame:
    actual_dict = aggregated_segment_region_df_to_dict(actual_df)
    plan_dict = aggregated_segment_region_df_to_dict(plan_df)
    py_dict = aggregated_segment_region_df_to_dict(py_df)

    all_keys = set(actual_dict.keys()) | set(plan_dict.keys()) | set(py_dict.keys())

    grouped_regions_by_segment: dict[str, list[str]] = {}

    for segment_value, region_value in all_keys:
        # ZZZZ es placeholder técnico: se elimina.
        # #N/A, Blanks, VARIOS, Other y cualquier categoría real SÍ se conservan.
        if is_forbidden_placeholder_segment(segment_value):
            continue
        grouped_regions_by_segment.setdefault(segment_value, []).append(region_value)

    ordered_segments = sorted(
        grouped_regions_by_segment.keys(),
        key=get_report_2_segment_sort_key,
    )

    rows: list[dict] = []

    grand_total_actual = 0.0
    grand_total_plan = 0.0
    grand_total_py = 0.0

    for segment_value in ordered_segments:
        region_values = sorted(
            set(grouped_regions_by_segment.get(segment_value, [])),
            key=get_report_2_region_sort_key,
        )

        total_actual = 0.0
        total_plan = 0.0
        total_py = 0.0

        for region_value in region_values:
            key = (segment_value, region_value)

            actual_value = float(actual_dict.get(key, 0.0))
            plan_value = float(plan_dict.get(key, 0.0))
            py_value = float(py_dict.get(key, 0.0))

            # Se muestra si tiene venta en Actual, Plan o PY.
            if not has_report_value(actual_value, plan_value, py_value):
                continue

            total_actual += actual_value
            total_plan += plan_value
            total_py += py_value

            rows.append(
                build_report_2_row(
                    segment_label=segment_value,
                    region_label=region_value,
                    actual=actual_value,
                    plan=plan_value,
                    py=py_value,
                )
            )

        # Solo se imprime el total del segmento si el segmento tuvo al menos
        # un valor real en Actual, Plan o PY. Evita filas tipo ZZZZ | Total en cero.
        if has_report_value(total_actual, total_plan, total_py):
            rows.append(
                build_report_2_row(
                    segment_label=segment_value,
                    region_label=config.REPORT_2_TOTAL_LABEL,
                    actual=total_actual,
                    plan=total_plan,
                    py=total_py,
                    is_total=True,
                )
            )

        grand_total_actual += total_actual
        grand_total_plan += total_plan
        grand_total_py += total_py

    rows.append(
        build_report_2_row(
            segment_label=config.REPORT_2_GRAND_TOTAL_LABEL,
            region_label="",
            actual=grand_total_actual,
            plan=grand_total_plan,
            py=grand_total_py,
            is_total=True,
            is_grand_total=True,
        )
    )

    return pd.DataFrame(rows)

# --------------------------------------------------------------
# FUNCIÓN PRINCIPAL:
# Construye payload de Reporte 2 - Segment x Region
# --------------------------------------------------------------
def build_report_2_segment_region_payload(
    df_processed_sales: pd.DataFrame,
    df_plan_sku: pd.DataFrame,
    selected_year: int | None = None,
    selected_month: int | None = None,
    progress_callback=None,
) -> dict:
    total_steps = 6
    emit_progress(progress_callback, "Validando bases para Segment x Region", 1, total_steps)
    if df_processed_sales is None or df_processed_sales.empty:
        raise ValueError("No existe base de ventas procesada.")

    if df_plan_sku is None or df_plan_sku.empty:
        raise ValueError("No existe archivo de plan por SKU cargado.")

    emit_progress(progress_callback, "Resolviendo periodo de Segment x Region", 2, total_steps)
    report_year, report_month = resolve_reporting_period(
        df_processed_sales,
        selected_year=selected_year,
        selected_month=selected_month,
    )

    emit_progress(progress_callback, "Calculando Actual y PY por Segmento y Región", 3, total_steps)
    mtd_actual_df, ytd_actual_df, mtd_py_df, ytd_py_df = get_sales_segment_region_totals_for_report_2(
        df_processed_sales,
        report_year,
        report_month,
    )

    emit_progress(progress_callback, "Integrando Plan por Segmento y Región", 4, total_steps)
    mtd_plan_df, ytd_plan_df = get_plan_segment_region_totals_for_report_2(
        df_plan_sku,
        report_month,
    )

    emit_progress(progress_callback, "Construyendo tablas MTD y YTD", 5, total_steps)
    mtd_table = build_report_2_segment_region_table(
        actual_df=mtd_actual_df,
        plan_df=mtd_plan_df,
        py_df=mtd_py_df,
    )

    ytd_table = build_report_2_segment_region_table(
        actual_df=ytd_actual_df,
        plan_df=ytd_plan_df,
        py_df=ytd_py_df,
    )

    mtd_total_row = mtd_table[mtd_table["Segmento"] == config.REPORT_2_GRAND_TOTAL_LABEL]
    ytd_total_row = ytd_table[ytd_table["Segmento"] == config.REPORT_2_GRAND_TOTAL_LABEL]

    emit_progress(progress_callback, "Preparando resumen final de Segment x Region", 6, total_steps)
    summary = {
        "latest_year": report_year,
        "latest_month": report_month,
        "mtd_actual_total_k": float(mtd_total_row["Actual"].sum()) / 1000,
        "mtd_plan_total_k": float(mtd_total_row["Plan"].sum()) / 1000,
        "mtd_py_total_k": float(mtd_total_row["PY"].sum()) / 1000,
        "ytd_actual_total_k": float(ytd_total_row["Actual"].sum()) / 1000,
        "ytd_plan_total_k": float(ytd_total_row["Plan"].sum()) / 1000,
        "ytd_py_total_k": float(ytd_total_row["PY"].sum()) / 1000,
    }

    return {
        "summary": summary,
        "mtd_segment_region_table": mtd_table,
        "ytd_segment_region_table": ytd_table,
    }

# ==============================================================
# ETAPA 6.1: REPORTE 2 - CATEGORY
# ============================================================== 

# --------------------------------------------------------------
# FUNCIÓN AUXILIAR:
# Normaliza Material para Reporte 2 Category
# --------------------------------------------------------------
def normalize_report_2_material_label(value) -> str:
    if pd.isna(value):
        return "#N/A"

    text = re.sub(r"\s+", " ", str(value).strip())
    if not text:
        return "#N/A"

    upper_text = text.upper()

    if upper_text in {"#N/A", "N/A", "NA", "NAN", "NONE", "NULL", "NAT"}:
        return "#N/A"

    return text

# --------------------------------------------------------------
# FUNCIÓN AUXILIAR:
# Normaliza Descripción del Material para Reporte 2 Category
# --------------------------------------------------------------
def normalize_report_2_material_description_label(value) -> str:
    if pd.isna(value):
        return "#N/A"

    text = re.sub(r"\s+", " ", str(value).strip())
    if not text:
        return "#N/A"

    upper_text = text.upper()

    if upper_text in {"#N/A", "N/A", "NA", "NAN", "NONE", "NULL", "NAT"}:
        return "#N/A"

    return text

# --------------------------------------------------------------
# FUNCIÓN AUXILIAR:
# Prepara ventas para Reporte 2 Category
# --------------------------------------------------------------
def prepare_sales_for_report_2_category(df_processed_sales: pd.DataFrame) -> pd.DataFrame:
    df = standardize_columns(df_processed_sales)
    df = exclude_afi_affiliates(df)

    category_col = find_first_existing_column(
        df,
        [
            "Corpo Category",
            "CorpoCategory",
            "Category",
        ],
    )
    material_col = find_first_existing_column(df, ["Material"])
    product_col = find_first_existing_column(
        df,
        [
            "Categoría del Material",
            "Categoria del Material",
            "Categoría Material",
            "Categoria Material",
            "local Sub category",
            "Local Sub category",
            "Sub category",
            "Subcategory",
        ],
    )
    description_col = find_first_existing_column(
        df,
        [
            "Descripción del Material",
            "Descripcion del Material",
            "Descripción Material",
            "Descripcion Material",
        ],
    )
    gsnr_col = find_first_existing_column(df, [config.COL_GSNR, "GSNR"])

    required_columns = [
        category_col,
        material_col,
        description_col,
        gsnr_col,
        config.COL_YEAR,
        config.COL_MONTH,
    ]
    if any(col is None for col in required_columns):
        raise ValueError(
            "Faltan columnas requeridas en ventas para Reporte Category. "
            "Se requieren Corpo Category, Material, Descripción del Material, GSNR, Año y Mes."
        )

    df = df.copy()
    df["__category__"] = df[category_col].apply(normalize_report_2_sales_category_label)
    df["__material__"] = df[material_col].apply(normalize_report_2_material_label)
    df["__description__"] = df[description_col].apply(normalize_report_2_material_description_label)

    if product_col is None:
        df["__product__"] = "#N/A"
    else:
        df["__product__"] = df[product_col].apply(normalize_report_2_product_label)

    df["__gsnr__"] = clean_numeric_series(df[gsnr_col])

    return df

# --------------------------------------------------------------
# FUNCIÓN AUXILIAR:
# Prepara plan SKU para Reporte 2 Category
# --------------------------------------------------------------
def prepare_plan_sku_for_report_2_category(df_plan_sku: pd.DataFrame) -> pd.DataFrame:
    df = standardize_columns(df_plan_sku)
    df = exclude_afi_affiliates(df)

    category_col = find_first_existing_column(
        df,
        [
            "Corpo Category",
            "CorpoCategory",
            "Category",
        ],
    )
    material_col = find_first_existing_column(df, ["Material"])
    product_col = find_first_existing_column(
        df,
        [
            "local Sub category",
            "Local Sub category",
            "Sub category",
            "Subcategory",
            "Categoría del Material",
            "Categoria del Material",
            "Categoría Material",
            "Categoria Material",
        ],
    )
    description_col = find_first_existing_column(
        df,
        [
            "Descripción del Material",
            "Descripcion del Material",
            "Descripción Material",
            "Descripcion Material",
        ],
    )

    required_columns = [category_col, material_col, description_col]
    if any(col is None for col in required_columns):
        raise ValueError(
            "Faltan columnas requeridas en Plan por SKU para Reporte Category. "
            "Se requieren Corpo Category, Material y Descripción del Material."
        )

    month_columns = get_plan_sku_gs_columns(df)
    if not month_columns:
        raise ValueError("No se detectaron columnas mensuales válidas en Plan por SKU.")

    df = df.copy()
    df["__category__"] = df.apply(
        lambda row: resolve_report_2_plan_category_from_row(row, category_col),
        axis=1,
    )
    df["__material__"] = df[material_col].apply(normalize_report_2_material_label)
    df["__description__"] = df[description_col].apply(normalize_report_2_material_description_label)

    if product_col is None:
        df["__product__"] = "#N/A"
    else:
        df["__product__"] = df[product_col].apply(normalize_report_2_product_label)

    for col in month_columns.values():
        df[col] = clean_numeric_series(df[col])

    return df

# --------------------------------------------------------------
# FUNCIÓN AUXILIAR:
# Agrega ventas Category + Material + Categoría del Material + Descripción del Material
# --------------------------------------------------------------
def get_sales_category_totals_for_report_2(
    df_processed_sales: pd.DataFrame,
    selected_year: int,
    selected_month: int,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    df = prepare_sales_for_report_2_category(df_processed_sales)
    group_columns = ["__category__", "__material__", "__product__", "__description__"]

    current_year_df = df[df[config.COL_YEAR] == selected_year].copy()
    previous_year_df = df[df[config.COL_YEAR] == (selected_year - 1)].copy()

    rename_columns = {
        "__category__": "Category",
        "__material__": "Material",
        "__product__": "Categoría del Material",
        "__description__": "Descripción del Material",
        "__gsnr__": "Valor",
    }

    mtd_actual = (
        current_year_df[current_year_df[config.COL_MONTH] == selected_month]
        .groupby(group_columns, dropna=False)["__gsnr__"]
        .sum()
        .reset_index()
        .rename(columns=rename_columns)
    )

    ytd_actual = (
        current_year_df[current_year_df[config.COL_MONTH] <= selected_month]
        .groupby(group_columns, dropna=False)["__gsnr__"]
        .sum()
        .reset_index()
        .rename(columns=rename_columns)
    )

    mtd_py = (
        previous_year_df[previous_year_df[config.COL_MONTH] == selected_month]
        .groupby(group_columns, dropna=False)["__gsnr__"]
        .sum()
        .reset_index()
        .rename(columns=rename_columns)
    )

    ytd_py = (
        previous_year_df[previous_year_df[config.COL_MONTH] <= selected_month]
        .groupby(group_columns, dropna=False)["__gsnr__"]
        .sum()
        .reset_index()
        .rename(columns=rename_columns)
    )

    return mtd_actual, ytd_actual, mtd_py, ytd_py

# --------------------------------------------------------------
# FUNCIÓN AUXILIAR:
# Agrega plan Category + Material + Categoría del Material + Descripción del Material
# --------------------------------------------------------------
def get_plan_category_totals_for_report_2(
    df_plan_sku: pd.DataFrame,
    latest_month: int,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    df = prepare_plan_sku_for_report_2_category(df_plan_sku)
    gs_columns = get_plan_sku_gs_columns(df)
    group_columns = ["__category__", "__material__", "__product__", "__description__"]

    if latest_month not in gs_columns:
        raise ValueError(
            f"No se encontró la columna GS del mes {latest_month} en Plan por SKU."
        )

    month_col = gs_columns[latest_month]
    months_to_sum = [gs_columns[m] for m in sorted(gs_columns.keys()) if m <= latest_month]

    rename_columns = {
        "__category__": "Category",
        "__material__": "Material",
        "__product__": "Categoría del Material",
        "__description__": "Descripción del Material",
        month_col: "Valor",
        "__ytd__": "Valor",
    }

    mtd_plan = (
        df.groupby(group_columns, dropna=False)[month_col]
        .sum()
        .reset_index()
        .rename(columns=rename_columns)
    )

    ytd_plan = (
        df.assign(__ytd__=df[months_to_sum].sum(axis=1))
        .groupby(group_columns, dropna=False)["__ytd__"]
        .sum()
        .reset_index()
        .rename(columns=rename_columns)
    )

    return mtd_plan, ytd_plan

# --------------------------------------------------------------
# FUNCIÓN AUXILIAR:
# Convierte agregados Category + Material + Categoría del Material + Descripción a diccionario
# --------------------------------------------------------------
def aggregated_category_df_to_dict(df: pd.DataFrame) -> dict[tuple[str, str, str, str], float]:
    if df is None or df.empty:
        return {}

    result = {}

    for _, row in df.iterrows():
        key = (
            normalize_report_2_category_label(row.get("Category", "#N/A")),
            normalize_report_2_material_label(row.get("Material", "#N/A")),
            normalize_report_2_product_label(row.get("Categoría del Material", "#N/A")),
            normalize_report_2_material_description_label(row.get("Descripción del Material", "#N/A")),
        )
        result[key] = result.get(key, 0.0) + float(row["Valor"])

    return result

# --------------------------------------------------------------
# FUNCIÓN AUXILIAR:
# Llave de orden para Category
# --------------------------------------------------------------
def get_report_2_category_sort_key(category_value: str) -> str:
    normalized_value = normalize_report_2_category_label(category_value)
    if normalized_value == "#N/A":
        return "zzzzzz_#n/a"
    if normalized_value == "Blanks":
        return "zzzzzz_blanks"
    return normalized_value.lower()

# --------------------------------------------------------------
# FUNCIÓN AUXILIAR:
# Llave de orden para Material
# --------------------------------------------------------------
def get_report_2_material_sort_key(material_value: str) -> str:
    normalized_value = normalize_report_2_material_label(material_value)
    if normalized_value == "#N/A":
        return "zzzzzz_#n/a"
    return normalized_value.lower()

# --------------------------------------------------------------
# FUNCIÓN AUXILIAR:
# Llave de orden para Categoría del Material
# --------------------------------------------------------------
def get_report_2_product_sort_key(product_value: str) -> str:
    normalized_value = normalize_report_2_product_label(product_value)
    if normalized_value == "#N/A":
        return "zzzzzz_#n/a"
    return normalized_value.lower()

# --------------------------------------------------------------
# FUNCIÓN AUXILIAR:
# Llave de orden para Descripción del Material
# --------------------------------------------------------------
def get_report_2_description_sort_key(description_value: str) -> str:
    normalized_value = normalize_report_2_material_description_label(description_value)
    if normalized_value == "#N/A":
        return "zzzzzz_#n/a"
    return normalized_value.lower()

# --------------------------------------------------------------
# FUNCIÓN AUXILIAR:
# Construye renglón de Reporte Category
# --------------------------------------------------------------
def build_report_2_category_row(
    category_label: str,
    material_label: str,
    product_label: str,
    description_label: str,
    actual: float,
    plan: float,
    py: float,
    is_total: bool = False,
    is_grand_total: bool = False,
) -> dict:
    return {
        "Category": category_label,
        "Material": material_label,
        "Categoría del Material": product_label,
        "Descripción del Material": description_label,
        "Actual": float(actual),
        "Plan": float(plan),
        "PY": float(py),
        "Var VS Plan": float(actual) - float(plan),
        "%Var VS Plan": safe_divide(float(actual) - float(plan), float(plan)),
        "Var VS PY": float(actual) - float(py),
        "%Var VS PY": safe_divide(float(actual) - float(py), float(py)),
        "__is_total__": is_total,
        "__is_grand_total__": is_grand_total,
    }

# --------------------------------------------------------------
# FUNCIÓN AUXILIAR:
# Construye tabla final Category + Material + Categoría del Material + Descripción del Material
# --------------------------------------------------------------
def build_report_2_category_table(
    actual_df: pd.DataFrame,
    plan_df: pd.DataFrame,
    py_df: pd.DataFrame,
) -> pd.DataFrame:
    actual_dict = aggregated_category_df_to_dict(actual_df)
    plan_dict = aggregated_category_df_to_dict(plan_df)
    py_dict = aggregated_category_df_to_dict(py_df)

    all_keys = set(actual_dict.keys()) | set(plan_dict.keys()) | set(py_dict.keys())

    grouped_details_by_category: dict[str, list[tuple[str, str, str]]] = {}

    for category_value, material_value, product_value, description_value in all_keys:
        grouped_details_by_category.setdefault(category_value, []).append(
            (material_value, product_value, description_value)
        )

    ordered_categories = sorted(
        grouped_details_by_category.keys(),
        key=get_report_2_category_sort_key,
    )

    rows: list[dict] = []

    grand_total_actual = 0.0
    grand_total_plan = 0.0
    grand_total_py = 0.0

    for category_value in ordered_categories:
        detail_values = sorted(
            set(grouped_details_by_category.get(category_value, [])),
            key=lambda item: (
                get_report_2_material_sort_key(item[0]),
                get_report_2_product_sort_key(item[1]),
                get_report_2_description_sort_key(item[2]),
            ),
        )

        total_actual = 0.0
        total_plan = 0.0
        total_py = 0.0

        for material_value, product_value, description_value in detail_values:
            key = (category_value, material_value, product_value, description_value)

            actual_value = float(actual_dict.get(key, 0.0))
            plan_value = float(plan_dict.get(key, 0.0))
            py_value = float(py_dict.get(key, 0.0))

            if not has_report_value(actual_value, plan_value, py_value):
                continue

            rows.append(
                build_report_2_category_row(
                    category_label=category_value,
                    material_label=material_value,
                    product_label=product_value,
                    description_label=description_value,
                    actual=actual_value,
                    plan=plan_value,
                    py=py_value,
                )
            )

            total_actual += actual_value
            total_plan += plan_value
            total_py += py_value

        rows.append(
            build_report_2_category_row(
                category_label=category_value,
                material_label="",
                product_label=config.REPORT_2_TOTAL_LABEL,
                description_label="",
                actual=total_actual,
                plan=total_plan,
                py=total_py,
                is_total=True,
            )
        )

        grand_total_actual += total_actual
        grand_total_plan += total_plan
        grand_total_py += total_py

    rows.append(
        build_report_2_category_row(
            category_label=config.REPORT_2_GRAND_TOTAL_LABEL,
            material_label="",
            product_label="",
            description_label="",
            actual=grand_total_actual,
            plan=grand_total_plan,
            py=grand_total_py,
            is_total=True,
            is_grand_total=True,
        )
    )

    return pd.DataFrame(rows)

# --------------------------------------------------------------
# FUNCIÓN PRINCIPAL:
# Construye payload de Reporte 2 - Category
# --------------------------------------------------------------
def build_report_2_category_payload(
    df_processed_sales: pd.DataFrame,
    df_plan_sku: pd.DataFrame,
    selected_year: int | None = None,
    selected_month: int | None = None,
    progress_callback=None,
) -> dict:
    total_steps = 6
    emit_progress(progress_callback, "Validando bases para Category", 1, total_steps)
    if df_processed_sales is None or df_processed_sales.empty:
        raise ValueError("No existe base de ventas procesada.")

    if df_plan_sku is None or df_plan_sku.empty:
        raise ValueError("No existe archivo de plan por SKU cargado.")

    emit_progress(progress_callback, "Resolviendo periodo de Category", 2, total_steps)
    report_year, report_month = resolve_reporting_period(
        df_processed_sales,
        selected_year=selected_year,
        selected_month=selected_month,
    )

    emit_progress(progress_callback, "Calculando Actual y PY por categoría y material", 3, total_steps)
    mtd_actual_df, ytd_actual_df, mtd_py_df, ytd_py_df = get_sales_category_totals_for_report_2(
        df_processed_sales,
        report_year,
        report_month,
    )

    emit_progress(progress_callback, "Integrando Plan por categoría y material", 4, total_steps)
    mtd_plan_df, ytd_plan_df = get_plan_category_totals_for_report_2(
        df_plan_sku,
        report_month,
    )

    emit_progress(progress_callback, "Construyendo tablas MTD y YTD de Category", 5, total_steps)
    mtd_table = build_report_2_category_table(
        actual_df=mtd_actual_df,
        plan_df=mtd_plan_df,
        py_df=mtd_py_df,
    )

    ytd_table = build_report_2_category_table(
        actual_df=ytd_actual_df,
        plan_df=ytd_plan_df,
        py_df=ytd_py_df,
    )

    mtd_total_row = mtd_table[mtd_table["Category"] == config.REPORT_2_GRAND_TOTAL_LABEL]
    ytd_total_row = ytd_table[ytd_table["Category"] == config.REPORT_2_GRAND_TOTAL_LABEL]

    emit_progress(progress_callback, "Preparando resumen final de Category", 6, total_steps)
    summary = {
        "latest_year": report_year,
        "latest_month": report_month,
        "mtd_actual_total_k": float(mtd_total_row["Actual"].sum()) / 1000,
        "mtd_plan_total_k": float(mtd_total_row["Plan"].sum()) / 1000,
        "mtd_py_total_k": float(mtd_total_row["PY"].sum()) / 1000,
        "ytd_actual_total_k": float(ytd_total_row["Actual"].sum()) / 1000,
        "ytd_plan_total_k": float(ytd_total_row["Plan"].sum()) / 1000,
        "ytd_py_total_k": float(ytd_total_row["PY"].sum()) / 1000,
    }

    return {
        "summary": summary,
        "mtd_category_table": mtd_table,
        "ytd_category_table": ytd_table,
    }

# ==============================================================
# ETAPA 7: REPORTE 3 - CHANNEL
# ==============================================================

# --------------------------------------------------------------
# FUNCIÓN AUXILIAR:
# Construye Channel para Reporte 3
# Si existe Canal, lo usa.
# IMPORTANTE: no usa "Canal de Ventas" porque ese campo contiene canales comerciales tipo 10/20/30,
# y el Reporte 3 debe conservar el nivel corporativo ACCO/ECO/EXP/BARRILITO/KEN/#N/A.
# Si no existe, aplica la lógica:
# NORTE / SUR / RETAIL -> Segmento
# resto -> Region
# --------------------------------------------------------------
def build_report_3_channel_series_from_sales(df: pd.DataFrame) -> pd.Series:
    """
    Reporte 3 - ACTUAL/PY (BASE SAP).

    Regla estricta según Excel:
    - Se lee la columna Channel directa de BASE SAP.
    - No se usa Canal, Oficina de Ventas, Region, Segmento ni concatenado.
    - Si Channel viene vacío/NaN/#N/A, se queda como #N/A.
    """
    channel_col = find_first_existing_column(df, ["Channel", "CHANNEL"])

    if channel_col is None:
        raise ValueError(
            "No se encontró la columna exacta 'Channel' en BASE SAP para Reporte 3. "
            "En ventas, Reporte 3 debe leer Channel directo; el concatenado solo aplica al Plan."
        )

    return df[channel_col].apply(normalize_report_3_channel_label)


def build_report_3_channel_series_from_plan(df: pd.DataFrame) -> pd.Series:
    """
    Reporte 3 - PLAN.

    Regla obligatoria del concatenado:
    - Si REGION es NORTE / SUR / RETAIL => usar Segmento.
    - Si REGION es ECO / EXP / KEN / VARIOS / #N/A / Other / etc. => usar REGION.
    - Si REGION está vacío/NaN/#N/A => #N/A.
    - GOBA se visualiza como BARRILITO.

    No se revisan columnas alternas; cada fila conserva su etiqueta correspondiente.
    """
    region_col = find_first_existing_column(df, ["REGION", "Region", "Región", "REGIÓN"])
    segment_col = find_first_existing_column(df, ["Segmento", "SEGMENTO", "Segment", "Segm Neg"])

    if region_col is None or segment_col is None:
        raise ValueError(
            "Faltan columnas requeridas para construir Channel en Plan. "
            "Reporte 3 Plan requiere REGION + Segmento para aplicar el concatenado."
        )

    def _resolve_row(row: pd.Series) -> str:
        region_value = normalize_report_3_channel_label(row.get(region_col))
        segment_value = normalize_report_2_segment_label(row.get(segment_col))

        if region_value in {"NORTE", "SUR", "RETAIL"}:
            return segment_value

        return region_value

    return df.apply(_resolve_row, axis=1)


def build_report_3_channel_series(df: pd.DataFrame) -> pd.Series:
    return build_report_3_channel_series_from_plan(df)

# --------------------------------------------------------------
# FUNCIÓN AUXILIAR:
# Prepara ventas para Reporte 3
# --------------------------------------------------------------
def prepare_sales_for_report_3(df_processed_sales: pd.DataFrame) -> pd.DataFrame:
    df = standardize_columns(df_processed_sales)
    df = exclude_afi_affiliates(df)

    gsnr_col = find_first_existing_column(df, [config.COL_GSNR, "GSNR"])

    required_columns = [gsnr_col, config.COL_YEAR, config.COL_MONTH]
    if any(col is None for col in required_columns):
        raise ValueError(
            "Faltan columnas requeridas en ventas para Reporte 3. "
            "Se requieren GSNR, Año y Mes."
        )

    df = df.copy()
    df["__channel__"] = build_report_3_channel_series_from_sales(df)
    df["__gsnr__"] = clean_numeric_series(df[gsnr_col])

    # No se eliminan vacíos / N/A: ya fueron normalizados como #N/A.
    # Si existe información en Actual, Plan o PY, debe mostrarse.

    return df

# --------------------------------------------------------------
# FUNCIÓN AUXILIAR:
# Prepara plan SKU para Reporte 3
# --------------------------------------------------------------
def prepare_plan_sku_for_report_3(df_plan_sku: pd.DataFrame) -> pd.DataFrame:
    df = standardize_columns(df_plan_sku)
    df = exclude_afi_affiliates(df)

    month_columns = get_plan_sku_gs_columns(df)
    if not month_columns:
        raise ValueError("No se detectaron columnas mensuales válidas en Plan por SKU.")

    df = df.copy()
    df["__channel__"] = build_report_3_channel_series_from_plan(df)

    for col in month_columns.values():
        df[col] = clean_numeric_series(df[col])

    # No se eliminan vacíos / N/A: ya fueron normalizados como #N/A.
    # Si existe información en Actual, Plan o PY, debe mostrarse.

    return df

# --------------------------------------------------------------
# FUNCIÓN AUXILIAR:
# Agrega ventas Channel
# --------------------------------------------------------------
def get_sales_channel_totals_for_report_3(
    df_processed_sales: pd.DataFrame,
    selected_year: int,
    selected_month: int,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    df = prepare_sales_for_report_3(df_processed_sales)

    current_year_df = df[df[config.COL_YEAR] == selected_year].copy()
    previous_year_df = df[df[config.COL_YEAR] == (selected_year - 1)].copy()

    mtd_actual = (
        current_year_df[current_year_df[config.COL_MONTH] == selected_month]
        .groupby("__channel__", dropna=False)["__gsnr__"]
        .sum()
        .reset_index()
        .rename(
            columns={
                "__channel__": "Channel",
                "__gsnr__": "Valor",
            }
        )
    )

    ytd_actual = (
        current_year_df[current_year_df[config.COL_MONTH] <= selected_month]
        .groupby("__channel__", dropna=False)["__gsnr__"]
        .sum()
        .reset_index()
        .rename(
            columns={
                "__channel__": "Channel",
                "__gsnr__": "Valor",
            }
        )
    )

    mtd_py = (
        previous_year_df[previous_year_df[config.COL_MONTH] == selected_month]
        .groupby("__channel__", dropna=False)["__gsnr__"]
        .sum()
        .reset_index()
        .rename(
            columns={
                "__channel__": "Channel",
                "__gsnr__": "Valor",
            }
        )
    )

    ytd_py = (
        previous_year_df[previous_year_df[config.COL_MONTH] <= selected_month]
        .groupby("__channel__", dropna=False)["__gsnr__"]
        .sum()
        .reset_index()
        .rename(
            columns={
                "__channel__": "Channel",
                "__gsnr__": "Valor",
            }
        )
    )

    return mtd_actual, ytd_actual, mtd_py, ytd_py

# --------------------------------------------------------------
# FUNCIÓN AUXILIAR:
# Agrega plan Channel
# --------------------------------------------------------------
def get_plan_channel_totals_for_report_3(
    df_plan_sku: pd.DataFrame,
    latest_month: int,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    df = prepare_plan_sku_for_report_3(df_plan_sku)
    gs_columns = get_plan_sku_gs_columns(df)

    if latest_month not in gs_columns:
        raise ValueError(
            f"No se encontró la columna GS del mes {latest_month} en Plan por SKU."
        )

    month_col = gs_columns[latest_month]
    months_to_sum = [gs_columns[m] for m in sorted(gs_columns.keys()) if m <= latest_month]

    mtd_plan = (
        df.groupby("__channel__", dropna=False)[month_col]
        .sum()
        .reset_index()
        .rename(
            columns={
                "__channel__": "Channel",
                month_col: "Valor",
            }
        )
    )

    ytd_plan = (
        df.assign(__ytd__=df[months_to_sum].sum(axis=1))
        .groupby("__channel__", dropna=False)["__ytd__"]
        .sum()
        .reset_index()
        .rename(
            columns={
                "__channel__": "Channel",
                "__ytd__": "Valor",
            }
        )
    )

    return mtd_plan, ytd_plan

# --------------------------------------------------------------
# FUNCIÓN AUXILIAR:
# Convierte agregados Channel a diccionario
# --------------------------------------------------------------
def aggregated_channel_df_to_dict(df: pd.DataFrame) -> dict[str, float]:
    if df is None or df.empty:
        return {}

    result = {}

    for _, row in df.iterrows():
        key = normalize_report_3_channel_label(row["Channel"])
        # IMPORTANTE: no sobrescribir duplicados.
        # Si Actual, Plan o PY traen el mismo canal en más de una fuente/fila,
        # todos los importes deben sumarse para que #N/A, VARIOS y cualquier
        # canal dinámico cuadren contra Excel.
        result[key] = result.get(key, 0.0) + float(row["Valor"])

    return result

# --------------------------------------------------------------
# FUNCIÓN AUXILIAR:
# Llave de orden para Channel
# --------------------------------------------------------------
def get_report_3_channel_sort_key(channel_value: str) -> tuple[int, str]:
    normalized_value = normalize_report_3_channel_label(channel_value)

    if normalized_value in config.REPORT_3_CHANNEL_ORDER:
        return config.REPORT_3_CHANNEL_ORDER.index(normalized_value), normalized_value

    return len(config.REPORT_3_CHANNEL_ORDER), normalized_value

# --------------------------------------------------------------
# FUNCIÓN AUXILIAR:
# Construye renglón de Reporte 3
# --------------------------------------------------------------
def build_report_3_row(
    channel_label: str,
    actual: float,
    plan: float,
    py: float,
    is_total: bool = False,
    is_grand_total: bool = False,
) -> dict:
    return {
        "Channel": channel_label,
        "Actual": float(actual),
        "Plan": float(plan),
        "PY": float(py),
        "Var VS Plan": float(actual) - float(plan),
        "%Var VS Plan": safe_divide(float(actual) - float(plan), float(plan)),
        "Var VS PY": float(actual) - float(py),
        "%Var VS PY": safe_divide(float(actual) - float(py), float(py)),
        "__is_total__": is_total,
        "__is_grand_total__": is_grand_total,
    }

# --------------------------------------------------------------
# FUNCIÓN AUXILIAR:
# Construye tabla final Channel
# --------------------------------------------------------------
def build_report_3_channel_table(
    actual_df: pd.DataFrame,
    plan_df: pd.DataFrame,
    py_df: pd.DataFrame,
) -> pd.DataFrame:
    actual_dict = aggregated_channel_df_to_dict(actual_df)
    plan_dict = aggregated_channel_df_to_dict(plan_df)
    py_dict = aggregated_channel_df_to_dict(py_df)

    all_channels = set(actual_dict.keys()) | set(plan_dict.keys()) | set(py_dict.keys())

    ordered_channels = sorted(
        all_channels,
        key=get_report_3_channel_sort_key,
    )

    rows: list[dict] = []

    grand_total_actual = 0.0
    grand_total_plan = 0.0
    grand_total_py = 0.0

    for channel_value in ordered_channels:
        # ZZZZ nunca debe mostrarse como canal final.
        if is_forbidden_placeholder_segment(channel_value):
            continue

        actual_value = float(actual_dict.get(channel_value, 0.0))
        plan_value = float(plan_dict.get(channel_value, 0.0))
        py_value = float(py_dict.get(channel_value, 0.0))

        # Se muestra si tiene venta en Actual, Plan o PY.
        if not has_report_value(actual_value, plan_value, py_value):
            continue

        rows.append(
            build_report_3_row(
                channel_label=channel_value,
                actual=actual_value,
                plan=plan_value,
                py=py_value,
            )
        )

        grand_total_actual += actual_value
        grand_total_plan += plan_value
        grand_total_py += py_value

    rows.append(
        build_report_3_row(
            channel_label=config.REPORT_3_TOTAL_LABEL,
            actual=grand_total_actual,
            plan=grand_total_plan,
            py=grand_total_py,
            is_total=True,
            is_grand_total=True,
        )
    )

    return pd.DataFrame(rows)

# --------------------------------------------------------------
# FUNCIÓN PRINCIPAL:
# Construye payload de Reporte 3 - Channel
# --------------------------------------------------------------
def build_report_3_channel_payload(
    df_processed_sales: pd.DataFrame,
    df_plan_sku: pd.DataFrame,
    selected_year: int | None = None,
    selected_month: int | None = None,
    progress_callback=None,
) -> dict:
    total_steps = 6
    emit_progress(progress_callback, "Validando bases para Channel", 1, total_steps)
    if df_processed_sales is None or df_processed_sales.empty:
        raise ValueError("No existe base de ventas procesada.")

    if df_plan_sku is None or df_plan_sku.empty:
        raise ValueError("No existe archivo de plan por SKU cargado.")

    emit_progress(progress_callback, "Resolviendo periodo de Channel", 2, total_steps)
    report_year, report_month = resolve_reporting_period(
        df_processed_sales,
        selected_year=selected_year,
        selected_month=selected_month,
    )

    emit_progress(progress_callback, "Calculando Actual y PY por Channel", 3, total_steps)
    mtd_actual_df, ytd_actual_df, mtd_py_df, ytd_py_df = get_sales_channel_totals_for_report_3(
        df_processed_sales,
        report_year,
        report_month,
    )

    emit_progress(progress_callback, "Integrando Plan por Channel", 4, total_steps)
    mtd_plan_df, ytd_plan_df = get_plan_channel_totals_for_report_3(
        df_plan_sku,
        report_month,
    )

    emit_progress(progress_callback, "Construyendo tablas MTD y YTD de Channel", 5, total_steps)
    mtd_table = build_report_3_channel_table(
        actual_df=mtd_actual_df,
        plan_df=mtd_plan_df,
        py_df=mtd_py_df,
    )

    ytd_table = build_report_3_channel_table(
        actual_df=ytd_actual_df,
        plan_df=ytd_plan_df,
        py_df=ytd_py_df,
    )

    mtd_total_row = mtd_table[mtd_table["Channel"] == config.REPORT_3_TOTAL_LABEL]
    ytd_total_row = ytd_table[ytd_table["Channel"] == config.REPORT_3_TOTAL_LABEL]

    emit_progress(progress_callback, "Preparando resumen final de Channel", 6, total_steps)
    summary = {
        "latest_year": report_year,
        "latest_month": report_month,
        "mtd_actual_total_k": float(mtd_total_row["Actual"].sum()) / 1000,
        "mtd_plan_total_k": float(mtd_total_row["Plan"].sum()) / 1000,
        "mtd_py_total_k": float(mtd_total_row["PY"].sum()) / 1000,
        "ytd_actual_total_k": float(ytd_total_row["Actual"].sum()) / 1000,
        "ytd_plan_total_k": float(ytd_total_row["Plan"].sum()) / 1000,
        "ytd_py_total_k": float(ytd_total_row["PY"].sum()) / 1000,
    }

    return {
        "summary": summary,
        "mtd_channel_table": mtd_table,
        "ytd_channel_table": ytd_table,
    }

# ============================================================== 
# ETAPA 8: REPORTE 4 - RANKING DE CLIENTES
# ============================================================== 

# --------------------------------------------------------------
# CONSTANTES VISIBLES DEL REPORTE 4
# --------------------------------------------------------------
REPORT_4_VISIBLE_COLUMNS = [
    "Client Name",
    "Cliente",
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

REPORT_4_FLAG_COLUMNS = [
    "__is_total__",
    "__is_grand_total__",
    "__is_group_summary__",
]

REPORT_4_INTERNAL_COLUMNS = [
    "__top__",
    "__grupo__",
]

# --------------------------------------------------------------
# FUNCIÓN AUXILIAR:
# Catálogo oficial de clientes del Reporte 4
# --------------------------------------------------------------
def get_report_4_client_catalog_df() -> pd.DataFrame:
    catalog = getattr(config, "REPORT_4_CLIENT_CATALOG", [])
    df_catalog = pd.DataFrame(catalog)

    if df_catalog.empty:
        return pd.DataFrame(columns=["Cliente", "Nombre del Cliente", "Client Name", "__top__", "__grupo__"])

    df_catalog = df_catalog.copy()
    df_catalog["Cliente"] = df_catalog["code"].apply(normalize_report_4_client_code)
    df_catalog["Nombre del Cliente"] = df_catalog["source_name"].fillna("").astype(str).str.strip()
    df_catalog["Client Name"] = df_catalog["display_name"].fillna("").astype(str).str.strip()
    df_catalog["__top__"] = pd.to_numeric(df_catalog["top"], errors="coerce").fillna(999999).astype(int)
    df_catalog["__grupo__"] = df_catalog["__top__"].apply(get_report_4_group_from_top)

    df_catalog = df_catalog[["Cliente", "Nombre del Cliente", "Client Name", "__top__", "__grupo__"]].copy()
    df_catalog = df_catalog.sort_values("__top__").reset_index(drop=True)

    return df_catalog

# --------------------------------------------------------------
# FUNCIÓN AUXILIAR:
# Define grupo visual conforme al ranking fijo
# --------------------------------------------------------------
def get_report_4_group_from_top(top_position: int) -> str:
    top_position = int(top_position)

    if top_position <= 15:
        return config.REPORT_4_GROUP_TOP_15
    if top_position <= 50:
        return config.REPORT_4_GROUP_16_50
    if top_position <= 100:
        return config.REPORT_4_GROUP_51_100

    return config.REPORT_4_GROUP_OTHER

# --------------------------------------------------------------
# FUNCIÓN AUXILIAR:
# Normaliza nombre cliente para Reporte 4
# --------------------------------------------------------------
def normalize_report_4_client_name(value) -> str:
    if pd.isna(value):
        return ""

    text = re.sub(r"\s+", " ", str(value).strip())
    if not text:
        return ""

    return text.upper().replace(",", "")

# --------------------------------------------------------------
# FUNCIÓN AUXILIAR:
# Normaliza código cliente para Reporte 4
# --------------------------------------------------------------
def normalize_report_4_client_code(value) -> str:
    if pd.isna(value):
        return ""

    text = str(value).strip().upper()
    if text in {"", "NAN", "NONE", "NULL", "NAT", "(BLANK)", "BLANK", "(BLANKS)", "BLANKS"}:
        return ""

    return text

# --------------------------------------------------------------
# FUNCIÓN AUXILIAR:
# Aplica nombre corregido SOLO para códigos repetidos
# --------------------------------------------------------------
def resolve_report_4_display_name(client_name, client_code) -> str:
    normalized_code = normalize_report_4_client_code(client_code)
    overrides = getattr(config, "REPORT_4_CLIENT_NAME_OVERRIDES", {})

    if normalized_code in overrides:
        return str(overrides[normalized_code]).strip()

    if pd.isna(client_name):
        return ""

    return re.sub(r"\s+", " ", str(client_name).strip())

# --------------------------------------------------------------
# FUNCIÓN AUXILIAR:
# Detecta columna de nombre cliente en ventas
# --------------------------------------------------------------
def get_report_4_sales_client_name_column(df: pd.DataFrame) -> str | None:
    return find_first_existing_column(df, config.REPORT_4_SALES_CLIENT_NAME_CANDIDATES)

# --------------------------------------------------------------
# FUNCIÓN AUXILIAR:
# Detecta columna de código cliente en ventas
# --------------------------------------------------------------
def get_report_4_sales_client_code_column(df: pd.DataFrame) -> str | None:
    return find_first_existing_column(df, config.REPORT_4_SALES_CLIENT_CODE_CANDIDATES)

# --------------------------------------------------------------
# FUNCIÓN AUXILIAR:
# Detecta columna de nombre cliente en plan cliente
# --------------------------------------------------------------
def get_report_4_plan_client_name_column(df: pd.DataFrame) -> str | None:
    preferred_candidates = [
        "Customer name",
        "Customer Name",
        "Nombre del Cliente",
        "Nombre Cliente",
    ]

    preferred_match = find_first_existing_column(df, preferred_candidates)
    if preferred_match is not None:
        return preferred_match

    return find_first_existing_column(df, config.REPORT_4_PLAN_CLIENT_NAME_CANDIDATES)

# --------------------------------------------------------------
# FUNCIÓN AUXILIAR:
# Detecta columna de código cliente en plan cliente
# --------------------------------------------------------------
def get_report_4_plan_client_code_column(df: pd.DataFrame) -> str | None:
    preferred_candidates = [
        "Client",
        "Client Code",
        "Customer",
        "Customer Code",
        "codigo",
        "Código",
        "Codigo",
    ]

    preferred_match = find_first_existing_column(df, preferred_candidates)
    if preferred_match is not None:
        return preferred_match

    return find_first_existing_column(df, config.REPORT_4_PLAN_CLIENT_CODE_CANDIDATES)


# --------------------------------------------------------------
# FUNCIÓN AUXILIAR:
# Excluye categorías de material para Reporte 4 (solo ventas Actual/PY)
# --------------------------------------------------------------
def exclude_report_4_material_categories(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aplica la regla de negocio del Ranking de Clientes únicamente sobre ventas.

    Importante:
    - Esta exclusión NO se aplica al Plan por Cliente.
    - El Plan se toma tal cual viene en la hoja Plan2026 by Client.
    - La exclusión replica el filtro de la tabla dinámica de ventas:
      O14, O15, O16 y O17 no deben entrar en Actual ni PY.
    """
    df = df.copy()

    category_col = find_first_existing_column(
        df,
        getattr(
            config,
            "REPORT_4_MATERIAL_CATEGORY_COLUMN_CANDIDATES",
            [
                "Categoría del Material",
                "Categoria del Material",
                "Categoría Material",
                "Categoria Material",
            ],
        ),
    )

    if category_col is None:
        return df

    excluded_codes = {
        str(value).strip().upper()
        for value in getattr(config, "REPORT_4_EXCLUDED_MATERIAL_CATEGORY_CODES", [])
        if str(value).strip()
    }

    excluded_labels = {
        str(value).strip().upper()
        for value in getattr(config, "REPORT_4_EXCLUDED_MATERIAL_CATEGORY_LABELS", [])
        if str(value).strip()
    }

    def normalize_category_value(value) -> str:
        if pd.isna(value):
            return ""
        return re.sub(r"\s+", " ", str(value).strip()).upper()

    category_series = df[category_col].apply(normalize_category_value)

    # Cubre tanto valores completos tipo "O14: POP MATERIAL"
    # como valores abreviados tipo "O14".
    category_codes = category_series.str.split(":", n=1).str[0].str.strip().str.upper()

    keep_mask = ~category_series.isin(excluded_labels) & ~category_codes.isin(excluded_codes)

    return df.loc[keep_mask].copy()

# --------------------------------------------------------------
# FUNCIÓN AUXILIAR:
# Prepara ventas para Reporte 4
# --------------------------------------------------------------
def prepare_sales_for_report_4(df_processed_sales: pd.DataFrame) -> pd.DataFrame:
    df = standardize_columns(df_processed_sales)
    df = exclude_afi_affiliates(df)
    df = exclude_report_4_material_categories(df)

    client_name_col = get_report_4_sales_client_name_column(df)
    client_code_col = get_report_4_sales_client_code_column(df)
    gsnr_col = find_first_existing_column(df, [config.COL_GSNR, "GSNR"])

    required_columns = [client_code_col, client_name_col, gsnr_col, config.COL_YEAR, config.COL_MONTH]
    if any(col is None for col in required_columns):
        raise ValueError(
            "Faltan columnas requeridas en ventas para Reporte 4. "
            "Se requieren código de cliente, nombre del cliente, GSNR, Año y Mes."
        )

    df = df.copy()
    df["Cliente"] = df[client_code_col].apply(normalize_report_4_client_code)
    df["Nombre del Cliente"] = df[client_name_col].fillna("").astype(str).str.strip()
    df["Client Name"] = df.apply(
        lambda row: resolve_report_4_display_name(row["Nombre del Cliente"], row["Cliente"]),
        axis=1,
    )
    df["__gsnr__"] = clean_numeric_series(df[gsnr_col])

    df = df[df["Cliente"] != ""].copy()
    return df

# --------------------------------------------------------------
# FUNCIÓN AUXILIAR:
# Prepara plan cliente para Reporte 4
# --------------------------------------------------------------
def build_report_4_default_plan_name_to_code_overrides() -> dict[str, str]:
    """
    Equivalencias mínimas para Plan2026 by Client cuando la hoja trae
    Customer name pero deja vacío el código Client.

    Esto NO define el ranking ni cambia la estructura visual del reporte.
    Solo evita que el Plan se pierda cuando el archivo no trae código.
    """
    default_overrides = {
        "CT INTERNACIONAL DEL NOROESTE": "C02206",
        "INGRAM MICRO MEXICO": "C00304",
        "INGRAM MICRO MEXICO MXN": "C00304",
        "INGRAM MICRO MEXICO USD": "C02125",
        "TECNOLOGIA SMARTBITT": "C02454",
        "TECNOLOGIA SMARTBITT MXN": "C02454",
        "TECNOLOGIA SMARTBITT USD": "C02469",
        "TECHSMART MAYOREO": "C02158",
        "BANCO SANTANDER MEXICO S.A.": "C02355",
        "BANCO SANTANDER MEXICO S.A.,": "C02355",
        "CVA": "C02474",
        "COMERCIALIZADORA DE VALOR AGREGADO": "C02474",
        "COMERCIALIZADORA DE VALOR AGREGADO USD": "C02474",
    }

    configured_overrides = getattr(
        config,
        "REPORT_4_PLAN_CLIENT_NAME_TO_CODE_OVERRIDES",
        {},
    )

    merged_overrides = dict(default_overrides)
    if isinstance(configured_overrides, dict):
        merged_overrides.update(configured_overrides)

    return {
        normalize_report_4_client_name(name): normalize_report_4_client_code(code)
        for name, code in merged_overrides.items()
        if normalize_report_4_client_name(name) and normalize_report_4_client_code(code)
    }


# --------------------------------------------------------------
# FUNCIÓN AUXILIAR:
# Construye llave sintética para filas de Plan sin código
# --------------------------------------------------------------
def build_report_4_plan_only_client_code(row) -> str:
    """
    Cuando Plan2026 by Client trae una fila sin código y no existe una
    equivalencia por nombre, no se debe tirar esa fila porque descuadra
    el total del Plan.

    Se genera una llave interna estable para conservar el monto en el
    ranking dinámico. Esto no afecta Actual/PY, que siguen cruzando por
    código real cuando existe.
    """
    name_value = normalize_report_4_client_name(row.get("Nombre del Cliente", ""))

    extra_parts = []
    for column_name in ["Segment", "Sales Region", "Sales region short", "Channel"]:
        if column_name in row.index:
            normalized_part = normalize_report_4_client_name(row.get(column_name, ""))
            if normalized_part:
                extra_parts.append(normalized_part)

    raw_key = "_".join([part for part in [name_value] + extra_parts if part])
    raw_key = re.sub(r"[^A-Z0-9]+", "_", raw_key).strip("_")

    if not raw_key:
        raw_key = f"ROW_{row.name}"

    return f"PLAN_ONLY_{raw_key}"


# --------------------------------------------------------------
# FUNCIÓN AUXILIAR:
# Prepara plan cliente para Reporte 4
# --------------------------------------------------------------
def prepare_plan_client_for_report_4(df_plan_client: pd.DataFrame) -> pd.DataFrame:
    df = standardize_columns(df_plan_client)
    df = remove_total_like_rows(df)

    client_code_col = get_report_4_plan_client_code_column(df)
    client_name_col = get_report_4_plan_client_name_column(df)

    month_columns = get_plan_client_month_columns(df)
    if not month_columns:
        raise ValueError("No se detectaron columnas mensuales válidas en Plan por Cliente.")

    df = df.copy()

    if client_code_col is not None:
        df["Cliente"] = df[client_code_col].apply(normalize_report_4_client_code)
    else:
        df["Cliente"] = ""

    if client_name_col is not None:
        df["Nombre del Cliente"] = df[client_name_col].fillna("").astype(str).str.strip()
    else:
        df["Nombre del Cliente"] = ""

    # 1) Primero intenta completar códigos vacíos por Customer name.
    #    Esto cubre filas de Kensington y otros clientes del Plan que vienen sin Client.
    name_to_code_overrides = build_report_4_default_plan_name_to_code_overrides()

    blank_code_mask = df["Cliente"] == ""
    if blank_code_mask.any() and name_to_code_overrides:
        normalized_names = df["Nombre del Cliente"].apply(normalize_report_4_client_name)
        df.loc[blank_code_mask, "Cliente"] = normalized_names.loc[blank_code_mask].map(
            name_to_code_overrides
        ).fillna("")

    # 2) Si todavía quedan filas con Plan y sin código, NO se eliminan.
    #    Se les asigna una llave interna para que el Plan total no se pierda.
    #    Antes aquí se filtraban y por eso el Plan del Reporte 4 no cuadraba.
    blank_code_mask = df["Cliente"] == ""
    if blank_code_mask.any():
        df.loc[blank_code_mask, "Cliente"] = df.loc[blank_code_mask].apply(
            build_report_4_plan_only_client_code,
            axis=1,
        )

    df["Client Name"] = df.apply(
        lambda row: resolve_report_4_display_name(row["Nombre del Cliente"], row["Cliente"]),
        axis=1,
    )

    # Para llaves internas PLAN_ONLY, el nombre visible debe ser el Customer name del Plan.
    plan_only_mask = df["Cliente"].astype(str).str.startswith("PLAN_ONLY_")
    df.loc[plan_only_mask, "Client Name"] = df.loc[
        plan_only_mask,
        "Nombre del Cliente",
    ].fillna("").astype(str).str.strip()

    for col in month_columns.values():
        df[col] = clean_numeric_series(df[col]) * 1000

    df = df[df["Cliente"] != ""].copy()

    return df

# --------------------------------------------------------------
# FUNCIÓN AUXILIAR:
# Agrega ventas por código de cliente
# --------------------------------------------------------------
def get_sales_client_totals_for_report_4(
    df_processed_sales: pd.DataFrame,
    selected_year: int,
    selected_month: int,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    df = prepare_sales_for_report_4(df_processed_sales)
    group_columns = ["Cliente"]

    current_year_df = df[df[config.COL_YEAR] == selected_year].copy()
    previous_year_df = df[df[config.COL_YEAR] == (selected_year - 1)].copy()

    def aggregate(source_df: pd.DataFrame, month_filter: str) -> pd.DataFrame:
        if month_filter == "mtd":
            filtered = source_df[source_df[config.COL_MONTH] == selected_month].copy()
        else:
            filtered = source_df[source_df[config.COL_MONTH] <= selected_month].copy()

        if filtered.empty:
            return pd.DataFrame(columns=["Cliente", "Client Name", "Valor"])

        value_df = (
            filtered.groupby(group_columns, dropna=False)["__gsnr__"]
            .sum()
            .reset_index()
            .rename(columns={"__gsnr__": "Valor"})
        )

        name_df = (
            filtered.sort_values(["Cliente", "Client Name"])
            .groupby("Cliente", dropna=False)["Client Name"]
            .first()
            .reset_index()
        )

        return value_df.merge(name_df, on="Cliente", how="left")

    return (
        aggregate(current_year_df, "mtd"),
        aggregate(current_year_df, "ytd"),
        aggregate(previous_year_df, "mtd"),
        aggregate(previous_year_df, "ytd"),
    )

# --------------------------------------------------------------
# FUNCIÓN AUXILIAR:
# Agrega plan por código de cliente
# --------------------------------------------------------------
def get_plan_client_totals_for_report_4(
    df_plan_client: pd.DataFrame,
    latest_month: int,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    df = prepare_plan_client_for_report_4(df_plan_client)
    month_columns = get_plan_client_month_columns(df)

    if latest_month not in month_columns:
        raise ValueError(
            f"No se encontró la columna del mes {latest_month} en Plan por Cliente."
        )

    month_col = month_columns[latest_month]
    months_to_sum = [month_columns[m] for m in sorted(month_columns.keys()) if m <= latest_month]

    name_df = (
        df.sort_values(["Cliente", "Client Name"])
        .groupby("Cliente", dropna=False)["Client Name"]
        .first()
        .reset_index()
    )

    mtd_plan = (
        df.groupby("Cliente", dropna=False)[month_col]
        .sum()
        .reset_index()
        .rename(columns={month_col: "Valor"})
        .merge(name_df, on="Cliente", how="left")
    )

    ytd_plan = (
        df.assign(__ytd__=df[months_to_sum].sum(axis=1))
        .groupby("Cliente", dropna=False)["__ytd__"]
        .sum()
        .reset_index()
        .rename(columns={"__ytd__": "Valor"})
        .merge(name_df, on="Cliente", how="left")
    )

    return mtd_plan, ytd_plan

# --------------------------------------------------------------
# FUNCIÓN AUXILIAR:
# Convierte agregados por cliente a diccionario
# --------------------------------------------------------------
def aggregated_client_df_to_dict(df: pd.DataFrame) -> dict[str, float]:
    if df is None or df.empty:
        return {}

    result = {}
    for _, row in df.iterrows():
        key = normalize_report_4_client_code(row.get("Cliente", ""))
        if key:
            result[key] = float(row.get("Valor", 0.0))

    return result

# --------------------------------------------------------------
# FUNCIÓN AUXILIAR:
# Convierte agregados por cliente a diccionario de nombres
# --------------------------------------------------------------
def aggregated_client_df_to_name_dict(df: pd.DataFrame) -> dict[str, str]:
    if df is None or df.empty or "Client Name" not in df.columns:
        return {}

    result: dict[str, str] = {}

    for _, row in df.iterrows():
        key = normalize_report_4_client_code(row.get("Cliente", ""))
        label = str(row.get("Client Name", "") or "").strip()

        if key and label and key not in result:
            result[key] = label

    return result

# --------------------------------------------------------------
# FUNCIÓN AUXILIAR:
# Resuelve nombre visible del cliente para el ranking dinámico
# --------------------------------------------------------------
def resolve_report_4_dynamic_client_label(
    client_code: str,
    actual_name_dict: dict[str, str],
    plan_name_dict: dict[str, str],
    py_name_dict: dict[str, str],
) -> str:
    normalized_code = normalize_report_4_client_code(client_code)

    overrides = getattr(config, "REPORT_4_CLIENT_NAME_OVERRIDES", {})
    if normalized_code in overrides:
        return str(overrides[normalized_code]).strip()

    for name_dict in [actual_name_dict, plan_name_dict, py_name_dict]:
        label = str(name_dict.get(normalized_code, "") or "").strip()
        if label:
            return label

    return normalized_code

# --------------------------------------------------------------
# FUNCIÓN AUXILIAR:
# Construye renglón de Reporte 4
# Nota: TOP y Grupo se conservan únicamente como columnas internas
#       (__top__ y __grupo__) para poder ordenar/filtrar, pero no se muestran.
# --------------------------------------------------------------
def build_report_4_row(
    client_code: str,
    client_label: str,
    actual: float,
    plan: float,
    py: float,
    top_position=None,
    group_label: str | None = None,
    is_total: bool = False,
    is_grand_total: bool = False,
    is_group_summary: bool = False,
) -> dict:
    return {
        "Client Name": client_label,
        "Cliente": client_code,
        "Actual": float(actual),
        "Plan": float(plan),
        "PY": float(py),
        "Var VS Plan": float(actual) - float(plan),
        "%Var VS Plan": safe_divide(float(actual) - float(plan), float(plan)),
        "Var VS PY": float(actual) - float(py),
        "%Var VS PY": safe_divide(float(actual) - float(py), float(py)),
        "__top__": top_position,
        "__grupo__": "" if group_label is None else str(group_label),
        "__is_total__": is_total,
        "__is_grand_total__": is_grand_total,
        "__is_group_summary__": is_group_summary,
    }

# --------------------------------------------------------------
# FUNCIÓN AUXILIAR:
# Fuerza estructura visible uniforme en Reporte 4
# --------------------------------------------------------------
def finalize_report_4_table(df: pd.DataFrame, keep_internal: bool = False) -> pd.DataFrame:
    if df is None or df.empty:
        base_columns = REPORT_4_VISIBLE_COLUMNS + REPORT_4_FLAG_COLUMNS
        if keep_internal:
            base_columns += REPORT_4_INTERNAL_COLUMNS
        return pd.DataFrame(columns=base_columns)

    df = df.copy()

    for column_name in REPORT_4_VISIBLE_COLUMNS:
        if column_name not in df.columns:
            df[column_name] = "" if column_name in {"Cliente", "Client Name"} else 0.0

    for column_name in REPORT_4_FLAG_COLUMNS:
        if column_name not in df.columns:
            df[column_name] = False

    for column_name in REPORT_4_INTERNAL_COLUMNS:
        if column_name not in df.columns:
            df[column_name] = ""

    ordered_columns = REPORT_4_VISIBLE_COLUMNS + REPORT_4_FLAG_COLUMNS
    if keep_internal:
        ordered_columns += REPORT_4_INTERNAL_COLUMNS

    return df[ordered_columns].reset_index(drop=True)

# --------------------------------------------------------------
# FUNCIÓN AUXILIAR:
# Construye tabla detalle final respetando orden fijo
# --------------------------------------------------------------
def build_report_4_detail_table(
    actual_df: pd.DataFrame,
    plan_df: pd.DataFrame,
    py_df: pd.DataFrame,
    keep_internal: bool = True,
) -> pd.DataFrame:
    """
    Construye el detalle del Reporte 4 de forma dinámica.

    Nueva regla:
    - Ya no depende de REPORT_4_CLIENT_CATALOG.
    - Toma todos los códigos existentes en Actual, Plan o PY.
    - Ordena el ranking por Actual de mayor a menor.
    - Asigna Top dinámico: Top 1, Top 2, ... hasta el último cliente.
    - Conserva los nombres especiales definidos en REPORT_4_CLIENT_NAME_OVERRIDES.
    """
    actual_dict = aggregated_client_df_to_dict(actual_df)
    plan_dict = aggregated_client_df_to_dict(plan_df)
    py_dict = aggregated_client_df_to_dict(py_df)

    actual_name_dict = aggregated_client_df_to_name_dict(actual_df)
    plan_name_dict = aggregated_client_df_to_name_dict(plan_df)
    py_name_dict = aggregated_client_df_to_name_dict(py_df)

    client_codes = set(actual_dict.keys()) | set(plan_dict.keys()) | set(py_dict.keys())

    rows: list[dict] = []

    for client_code in client_codes:
        client_code = normalize_report_4_client_code(client_code)
        if not client_code:
            continue

        actual_value = float(actual_dict.get(client_code, 0.0))
        plan_value = float(plan_dict.get(client_code, 0.0))
        py_value = float(py_dict.get(client_code, 0.0))

        if not has_report_value(actual_value, plan_value, py_value):
            continue

        client_label = resolve_report_4_dynamic_client_label(
            client_code=client_code,
            actual_name_dict=actual_name_dict,
            plan_name_dict=plan_name_dict,
            py_name_dict=py_name_dict,
        )

        rows.append(
            build_report_4_row(
                client_code=client_code,
                client_label=client_label,
                actual=actual_value,
                plan=plan_value,
                py=py_value,
                top_position=0,
                group_label="",
            )
        )

    if not rows:
        return finalize_report_4_table(pd.DataFrame(), keep_internal=keep_internal)

    detail_df = pd.DataFrame(rows)
    detail_df = detail_df.sort_values(
        by=["Actual", "Plan", "PY", "Client Name", "Cliente"],
        ascending=[False, False, False, True, True],
        kind="mergesort",
    ).reset_index(drop=True)

    detail_df["__top__"] = range(1, len(detail_df) + 1)
    detail_df["__grupo__"] = detail_df["__top__"].apply(get_report_4_group_from_top)

    return finalize_report_4_table(detail_df, keep_internal=keep_internal)

# --------------------------------------------------------------
# FUNCIÓN AUXILIAR:
# Construye renglones resumen por bloque
# --------------------------------------------------------------
def build_report_4_group_summary_table(detail_df: pd.DataFrame, keep_internal: bool = True) -> pd.DataFrame:
    if detail_df is None or detail_df.empty:
        return finalize_report_4_table(pd.DataFrame(), keep_internal=keep_internal)

    rows: list[dict] = []
    group_order = [
        config.REPORT_4_GROUP_TOP_15,
        config.REPORT_4_GROUP_16_50,
        config.REPORT_4_GROUP_51_100,
        config.REPORT_4_GROUP_OTHER,
    ]

    for group_label in group_order:
        group_df = detail_df[detail_df["__grupo__"] == group_label].copy()
        if group_df.empty:
            continue

        total_actual = group_df["Actual"].apply(float).sum()
        total_plan = group_df["Plan"].apply(float).sum()
        total_py = group_df["PY"].apply(float).sum()

        # Para la vista ejecutiva, el Top 15 debe distinguirse claramente
        # como subtotal del bloque superior, para no confundirse con
        # Clients 16 to 50.
        client_label = group_label
        if group_label == config.REPORT_4_GROUP_TOP_15:
            client_label = getattr(
                config,
                "REPORT_4_GROUP_TOP_15_TOTAL_LABEL",
                "Total Top 15",
            )

        rows.append(
            build_report_4_row(
                client_code="",
                client_label=client_label,
                actual=total_actual,
                plan=total_plan,
                py=total_py,
                top_position="",
                group_label=group_label,
                is_total=True,
                is_group_summary=True,
            )
        )

    grand_actual = detail_df["Actual"].apply(float).sum()
    grand_plan = detail_df["Plan"].apply(float).sum()
    grand_py = detail_df["PY"].apply(float).sum()

    rows.append(
        build_report_4_row(
            client_code="",
            client_label=config.REPORT_4_TOTAL_LABEL,
            actual=grand_actual,
            plan=grand_plan,
            py=grand_py,
            top_position="",
            group_label=config.REPORT_4_TOTAL_LABEL,
            is_total=True,
            is_grand_total=True,
        )
    )

    return finalize_report_4_table(pd.DataFrame(rows), keep_internal=keep_internal)

# --------------------------------------------------------------
# FUNCIÓN AUXILIAR:
# Construye tabla ejecutiva compatible con la app actual
# --------------------------------------------------------------
def build_report_4_clients_table(
    actual_df: pd.DataFrame,
    plan_df: pd.DataFrame,
    py_df: pd.DataFrame,
) -> pd.DataFrame:
    detail_df = build_report_4_detail_table(actual_df, plan_df, py_df, keep_internal=True)
    summary_df = build_report_4_group_summary_table(detail_df, keep_internal=True)

    top15_df = detail_df[detail_df["__grupo__"] == config.REPORT_4_GROUP_TOP_15].copy()

    top15_summary_label = getattr(
        config,
        "REPORT_4_GROUP_TOP_15_TOTAL_LABEL",
        "Total Top 15",
    )

    top15_summary_df = summary_df[
        (summary_df["__grupo__"] == config.REPORT_4_GROUP_TOP_15)
        | (summary_df["Client Name"] == top15_summary_label)
        | (summary_df["Client Name"] == config.REPORT_4_GROUP_TOP_15)
    ].copy()

    other_summary_df = summary_df[
        summary_df["Client Name"].isin([
            config.REPORT_4_GROUP_16_50,
            config.REPORT_4_GROUP_51_100,
            config.REPORT_4_GROUP_OTHER,
            config.REPORT_4_TOTAL_LABEL,
        ])
    ].copy()

    final_df = pd.concat(
        [top15_df, top15_summary_df, other_summary_df],
        ignore_index=True,
    )
    return finalize_report_4_table(final_df, keep_internal=False)

# --------------------------------------------------------------
# FUNCIÓN AUXILIAR:
# Extrae un bloque visible del detalle por grupo
# --------------------------------------------------------------
def get_report_4_group_detail_table(detail_df: pd.DataFrame, group_label: str) -> pd.DataFrame:
    if detail_df is None or detail_df.empty:
        return finalize_report_4_table(pd.DataFrame(), keep_internal=False)

    filtered = detail_df[detail_df["__grupo__"] == group_label].copy()

    if filtered.empty:
        return finalize_report_4_table(filtered, keep_internal=False)

    total_actual = filtered["Actual"].apply(float).sum()
    total_plan = filtered["Plan"].apply(float).sum()
    total_py = filtered["PY"].apply(float).sum()

    total_row = build_report_4_row(
        client_code="",
        client_label=f"Total {group_label}",
        actual=total_actual,
        plan=total_plan,
        py=total_py,
        top_position="",
        group_label=group_label,
        is_total=True,
        is_group_summary=True,
    )

    filtered_with_total = pd.concat(
        [filtered, pd.DataFrame([total_row])],
        ignore_index=True,
    )

    return finalize_report_4_table(filtered_with_total, keep_internal=False)

# --------------------------------------------------------------
# FUNCIÓN PRINCIPAL:
# Construye payload de Reporte 4
# --------------------------------------------------------------
def build_report_4_top_clients_payload(
    df_processed_sales: pd.DataFrame,
    df_plan_client: pd.DataFrame,
    selected_year: int | None = None,
    selected_month: int | None = None,
    progress_callback=None,
) -> dict:
    total_steps = 8
    emit_progress(progress_callback, "Validando bases para Ranking de Clientes", 1, total_steps)
    if df_processed_sales is None or df_processed_sales.empty:
        raise ValueError("No existe base de ventas procesada.")

    if df_plan_client is None or df_plan_client.empty:
        raise ValueError("No existe archivo de plan por cliente cargado.")

    emit_progress(progress_callback, "Resolviendo periodo del Ranking", 2, total_steps)
    report_year, report_month = resolve_reporting_period(
        df_processed_sales,
        selected_year=selected_year,
        selected_month=selected_month,
    )

    emit_progress(progress_callback, "Calculando Actual y PY por cliente", 3, total_steps)
    mtd_actual_df, ytd_actual_df, mtd_py_df, ytd_py_df = get_sales_client_totals_for_report_4(
        df_processed_sales,
        report_year,
        report_month,
    )

    emit_progress(progress_callback, "Integrando Plan por cliente", 4, total_steps)
    mtd_plan_df, ytd_plan_df = get_plan_client_totals_for_report_4(
        df_plan_client,
        report_month,
    )

    emit_progress(progress_callback, "Ordenando clientes y asignando ranking", 5, total_steps)
    mtd_detail_internal = build_report_4_detail_table(
        actual_df=mtd_actual_df,
        plan_df=mtd_plan_df,
        py_df=mtd_py_df,
        keep_internal=True,
    )

    ytd_detail_internal = build_report_4_detail_table(
        actual_df=ytd_actual_df,
        plan_df=ytd_plan_df,
        py_df=ytd_py_df,
        keep_internal=True,
    )

    emit_progress(progress_callback, "Calculando bloques Top 15, 16-50, 51-100 y resto", 6, total_steps)
    mtd_summary_internal = build_report_4_group_summary_table(mtd_detail_internal, keep_internal=True)
    ytd_summary_internal = build_report_4_group_summary_table(ytd_detail_internal, keep_internal=True)

    emit_progress(progress_callback, "Construyendo tablas ejecutivas MTD y YTD", 7, total_steps)
    mtd_table = build_report_4_clients_table(
        actual_df=mtd_actual_df,
        plan_df=mtd_plan_df,
        py_df=mtd_py_df,
    )

    ytd_table = build_report_4_clients_table(
        actual_df=ytd_actual_df,
        plan_df=ytd_plan_df,
        py_df=ytd_py_df,
    )

    mtd_total_row = mtd_summary_internal[mtd_summary_internal["Client Name"] == config.REPORT_4_TOTAL_LABEL]
    ytd_total_row = ytd_summary_internal[ytd_summary_internal["Client Name"] == config.REPORT_4_TOTAL_LABEL]

    emit_progress(progress_callback, "Preparando resumen final del Ranking", 8, total_steps)
    summary = {
        "latest_year": report_year,
        "latest_month": report_month,
        "mtd_actual_total_k": float(mtd_total_row["Actual"].sum()) / 1000,
        "mtd_plan_total_k": float(mtd_total_row["Plan"].sum()) / 1000,
        "mtd_py_total_k": float(mtd_total_row["PY"].sum()) / 1000,
        "ytd_actual_total_k": float(ytd_total_row["Actual"].sum()) / 1000,
        "ytd_plan_total_k": float(ytd_total_row["Plan"].sum()) / 1000,
        "ytd_py_total_k": float(ytd_total_row["PY"].sum()) / 1000,
    }

    return {
        "summary": summary,
        # Vista ejecutiva: Top 15 + bloques resumen + Total Mexico.
        "mtd_top_clients_table": mtd_table,
        "ytd_top_clients_table": ytd_table,
        # Detalle completo visible, sin columnas TOP ni Grupo.
        "mtd_detail_table": finalize_report_4_table(mtd_detail_internal, keep_internal=False),
        "ytd_detail_table": finalize_report_4_table(ytd_detail_internal, keep_internal=False),
        # Resúmenes visibles, sin columnas TOP ni Grupo.
        "mtd_summary_table": finalize_report_4_table(mtd_summary_internal, keep_internal=False),
        "ytd_summary_table": finalize_report_4_table(ytd_summary_internal, keep_internal=False),
        # Bloques desplegables visibles, sin columnas TOP ni Grupo.
        "mtd_group_16_50_table": get_report_4_group_detail_table(mtd_detail_internal, config.REPORT_4_GROUP_16_50),
        "ytd_group_16_50_table": get_report_4_group_detail_table(ytd_detail_internal, config.REPORT_4_GROUP_16_50),
        "mtd_group_51_100_table": get_report_4_group_detail_table(mtd_detail_internal, config.REPORT_4_GROUP_51_100),
        "ytd_group_51_100_table": get_report_4_group_detail_table(ytd_detail_internal, config.REPORT_4_GROUP_51_100),
        "mtd_group_other_table": get_report_4_group_detail_table(mtd_detail_internal, config.REPORT_4_GROUP_OTHER),
        "ytd_group_other_table": get_report_4_group_detail_table(ytd_detail_internal, config.REPORT_4_GROUP_OTHER),
    }

# ==============================================================
# INTEGRACIÓN FORECAST - EXTENSIÓN CONSERVADORA
# ==============================================================
# IMPORTANTE:
# Las funciones originales anteriores se conservan completas.
# Las definiciones siguientes amplían únicamente los cálculos necesarios
# para incorporar Forecast sin eliminar las reglas históricas del archivo.
#
# Orden estándar de métricas:
# Actual | Plan | Fcst | PY | Var VS Plan | %Var VS Plan |
# Var VS Fcst | %Var VS Fcst | Var VS PY | %Var VS PY
# ==============================================================


def get_fcst_client_month_columns(df_fcst_client: pd.DataFrame) -> dict[int, str]:
    return get_plan_client_month_columns(df_fcst_client)


def get_fcst_sku_gs_columns(df_fcst_sku: pd.DataFrame) -> dict[int, str]:
    return get_plan_sku_gs_columns(df_fcst_sku)


def normalize_forecast_label(forecast_name: str | None) -> str:
    text = str(forecast_name or "Fcst").strip()
    if not text:
        return "Fcst"
    match = re.search(r"(?i)fcst\s*(\d+)\s*\+\s*(\d+)", text)
    return f"Fcst {match.group(1)}+{match.group(2)}" if match else "Fcst"


def prepare_fcst_client_like_plan(df_fcst_client: pd.DataFrame) -> pd.DataFrame:
    return standardize_columns(remove_total_like_rows(df_fcst_client))


def get_fcst_client_totals(df_fcst_client: pd.DataFrame, latest_month: int) -> tuple[float, float]:
    df = prepare_fcst_client_like_plan(df_fcst_client)
    df = exclude_base_mtd_affiliates(df)
    month_columns = get_fcst_client_month_columns(df)
    if latest_month not in month_columns:
        raise ValueError(f"No se encontró la columna del mes {latest_month} en Forecast por Cliente.")
    month_col = month_columns[latest_month]
    months_to_sum = [month_columns[m] for m in sorted(month_columns) if m <= latest_month]
    # Igual que Plan Cliente: la fuente está expresada en miles.
    mtd = clean_numeric_series(df[month_col]).sum() * 1000
    ytd = sum(clean_numeric_series(df[col]).sum() for col in months_to_sum) * 1000
    return float(mtd), float(ytd)


def get_fcst_sku_totals(df_fcst_sku: pd.DataFrame, latest_month: int) -> tuple[float, float]:
    df = standardize_columns(df_fcst_sku)
    df = exclude_base_mtd_affiliates(df)
    gs_columns = get_fcst_sku_gs_columns(df)
    if latest_month not in gs_columns:
        raise ValueError(f"No se encontró la columna GS del mes {latest_month} en Forecast por SKU.")
    month_col = gs_columns[latest_month]
    months_to_sum = [gs_columns[m] for m in sorted(gs_columns) if m <= latest_month]
    mtd = clean_numeric_series(df[month_col]).sum()
    ytd = sum(clean_numeric_series(df[col]).sum() for col in months_to_sum)
    return float(mtd), float(ytd)


def calculate_fcst_totals_summary(df_fcst_client, df_fcst_sku, latest_month: int) -> dict:
    mtd_client, ytd_client = get_fcst_client_totals(df_fcst_client, latest_month)
    mtd_sku, ytd_sku = get_fcst_sku_totals(df_fcst_sku, latest_month)
    tolerance = 1000.0
    return {
        "mtd_fcst_client": mtd_client, "mtd_fcst_sku": mtd_sku,
        "ytd_fcst_client": ytd_client, "ytd_fcst_sku": ytd_sku,
        "mtd_fcst_total": mtd_client, "ytd_fcst_total": ytd_client,
        "mtd_fcst_diff": abs(mtd_client-mtd_sku),
        "ytd_fcst_diff": abs(ytd_client-ytd_sku),
        "mtd_fcst_match": abs(mtd_client-mtd_sku) <= tolerance,
        "ytd_fcst_match": abs(ytd_client-ytd_sku) <= tolerance,
    }


def prepare_fcst_client_for_report_1(df_fcst_client: pd.DataFrame) -> pd.DataFrame:
    return prepare_plan_client_for_report_1(df_fcst_client)


def get_fcst_channel_totals_for_report_1(df_fcst_client: pd.DataFrame, latest_month: int):
    return get_plan_channel_totals_for_report_1(df_fcst_client, latest_month)


def prepare_fcst_sku_for_report_2(df_fcst_sku: pd.DataFrame) -> pd.DataFrame:
    return prepare_plan_sku_for_report_2(df_fcst_sku)


def get_fcst_segment_region_totals_for_report_2(df_fcst_sku: pd.DataFrame, selected_month: int):
    return get_plan_segment_region_totals_for_report_2(df_fcst_sku, selected_month)


def prepare_fcst_sku_for_report_2_category(df_fcst_sku: pd.DataFrame) -> pd.DataFrame:
    return prepare_plan_sku_for_report_2_category(df_fcst_sku)


def get_fcst_category_totals_for_report_2(df_fcst_sku: pd.DataFrame, selected_month: int):
    return get_plan_category_totals_for_report_2(df_fcst_sku, selected_month)


def prepare_fcst_sku_for_report_3(df_fcst_sku: pd.DataFrame) -> pd.DataFrame:
    # Misma regla de concatenado que Plan: NORTE/SUR/RETAIL usan Segmento; el resto REGION.
    return prepare_plan_sku_for_report_3(df_fcst_sku)


def get_fcst_channel_totals_for_report_3(df_fcst_sku: pd.DataFrame, selected_month: int):
    return get_plan_channel_totals_for_report_3(df_fcst_sku, selected_month)


def prepare_fcst_client_for_report_4(df_fcst_client: pd.DataFrame) -> pd.DataFrame:
    return prepare_plan_client_for_report_4(df_fcst_client)


def get_fcst_client_totals_for_report_4(df_fcst_client: pd.DataFrame, selected_month: int):
    return get_plan_client_totals_for_report_4(df_fcst_client, selected_month)


def build_horizontal_plan_table(
    mtd_actual: float, ytd_actual: float,
    mtd_plan: float, ytd_plan: float,
    mtd_fcst: float, ytd_fcst: float,
    mtd_py: float, ytd_py: float,
) -> pd.DataFrame:
    rows = []
    for period, actual, plan, fcst, py in [
        ("MTD", mtd_actual, mtd_plan, mtd_fcst, mtd_py),
        ("YTD", ytd_actual, ytd_plan, ytd_fcst, ytd_py),
    ]:
        rows.append({
            "Periodo": period, "Actual": actual, "Plan": plan, "Fcst": fcst, "PY": py,
            "Var VS Plan": actual-plan, "%Var VS Plan": safe_divide(actual-plan, plan),
            "Var VS Fcst": actual-fcst, "%Var VS Fcst": safe_divide(actual-fcst, fcst),
            "Var VS PY": actual-py, "%Var VS PY": safe_divide(actual-py, py),
        })
    return pd.DataFrame(rows)


def build_mtd_payload(
    df_processed_sales: pd.DataFrame,
    df_plan_client: pd.DataFrame, df_plan_sku: pd.DataFrame,
    df_fcst_client: pd.DataFrame, df_fcst_sku: pd.DataFrame,
    forecast_name: str | None = None,
    selected_year: int | None = None, selected_month: int | None = None,
    progress_callback=None,
) -> dict:
    total_steps = 8
    emit_progress(progress_callback, "Validando bases requeridas para Base MTD", 1, total_steps)
    required=[(df_processed_sales,"ventas procesadas"),(df_plan_client,"plan por cliente"),(df_plan_sku,"plan por SKU"),(df_fcst_client,"forecast por cliente"),(df_fcst_sku,"forecast por SKU")]
    for df,label in required:
        if df is None or df.empty: raise ValueError(f"No existe archivo de {label} cargado.")
    report_year, report_month = resolve_reporting_period(df_processed_sales, selected_year, selected_month)
    emit_progress(progress_callback, "Calculando Actual y PY", 2, total_steps)
    totals=calculate_actual_and_py_totals(df_processed_sales, report_year, report_month)
    emit_progress(progress_callback, "Conciliando Plan Cliente y Plan SKU", 3, total_steps)
    plan_summary=calculate_plan_totals_summary(df_plan_client, df_plan_sku, report_month)
    emit_progress(progress_callback, "Conciliando Forecast Cliente y Forecast SKU", 4, total_steps)
    fcst_summary=calculate_fcst_totals_summary(df_fcst_client, df_fcst_sku, report_month)
    emit_progress(progress_callback, "Calculando BTS", 5, total_steps)
    bts_totals=calculate_bts_totals(df_processed_sales, report_year, report_month)
    emit_progress(progress_callback, "Construyendo comparativos", 6, total_steps)
    client_table=build_horizontal_plan_table(totals["mtd_actual"],totals["ytd_actual"],plan_summary["mtd_plan_client"],plan_summary["ytd_plan_client"],fcst_summary["mtd_fcst_client"],fcst_summary["ytd_fcst_client"],totals["mtd_py"],totals["ytd_py"])
    sku_table=build_horizontal_plan_table(totals["mtd_actual"],totals["ytd_actual"],plan_summary["mtd_plan_sku"],plan_summary["ytd_plan_sku"],fcst_summary["mtd_fcst_sku"],fcst_summary["ytd_fcst_sku"],totals["mtd_py"],totals["ytd_py"])
    bts_table=build_bts_table(bts_totals["bts_mtd_actual"],bts_totals["bts_mtd_py"],bts_totals["bts_ytd_actual"],bts_totals["bts_ytd_py_comparable"])
    summary={"mtd_act_total_k":totals["mtd_actual"]/1000,"ytd_act_total_k":totals["ytd_actual"]/1000,"mtd_plan_total_k":plan_summary["mtd_plan_total"]/1000,"ytd_plan_total_k":plan_summary["ytd_plan_total"]/1000,"mtd_fcst_total_k":fcst_summary["mtd_fcst_total"]/1000,"ytd_fcst_total_k":fcst_summary["ytd_fcst_total"]/1000}
    bts_summary={"bts_actual_k":bts_totals["bts_actual"]/1000,"bts_py_full_k":bts_totals["bts_py_full"]/1000}
    emit_progress(progress_callback, "Preparando resumen final", 8, total_steps)
    return {"latest_year":report_year,"latest_month":report_month,"forecast_name":forecast_name or "Fcst","forecast_label":normalize_forecast_label(forecast_name),"summary":summary,"plan_summary":plan_summary,"fcst_summary":fcst_summary,"bts_summary":bts_summary,"client_table":client_table,"sku_table":sku_table,"bts_table":bts_table}


def build_report_1_row(
    office_label: str,
    actual: float,
    plan: float | None,
    fcst: float | None,
    py: float,
    is_total: bool = False,
    is_highlight: bool = False,
) -> dict:
    row = {
        "Oficina de Ventas": office_label,
        "Actual": float(actual),
        "Plan": None if plan is None else float(plan),
        "Fcst": None if fcst is None else float(fcst),
        "PY": float(py),
        "Var VS Plan": None,
        "%Var VS Plan": None,
        "Var VS Fcst": None,
        "%Var VS Fcst": None,
        "Var VS PY": float(actual) - float(py),
        "%Var VS PY": safe_divide(float(actual) - float(py), float(py)),
        "__is_total__": is_total,
        "__is_highlight__": is_highlight,
    }

    if plan is not None:
        row["Var VS Plan"] = float(actual) - float(plan)
        row["%Var VS Plan"] = safe_divide(float(actual) - float(plan), float(plan))
    if fcst is not None:
        row["Var VS Fcst"] = float(actual) - float(fcst)
        row["%Var VS Fcst"] = safe_divide(float(actual) - float(fcst), float(fcst))
    return row


def build_report_1_without_kens_table(actual_dict, plan_dict, fcst_dict, py_dict) -> pd.DataFrame:
    codes_present=set(actual_dict)|set(plan_dict)|set(fcst_dict)|set(py_dict)
    ordered_codes=get_ordered_report_1_codes(codes_present, exclude_codes={"AF","AFI"})
    rows=[]; totals={"actual":0.0,"plan":0.0,"fcst":0.0,"py":0.0}
    for code in ordered_codes:
        actual=float(actual_dict.get(code,0)); plan=float(plan_dict.get(code,0)); fcst=float(fcst_dict.get(code,0)); py=float(py_dict.get(code,0))
        if not has_report_value(actual,plan,fcst,py): continue
        totals["actual"]+=actual; totals["plan"]+=plan; totals["fcst"]+=fcst; totals["py"]+=py
        rows.append(build_report_1_row(get_channel_display_label(code),actual,plan,fcst,py))
    rows.append(build_report_1_row(config.REPORT_1_TOTAL_LABEL,totals["actual"],totals["plan"],totals["fcst"],totals["py"],is_total=True))
    return pd.DataFrame(rows)


def build_report_1_payload(df_processed_sales, df_plan_client, df_fcst_client, forecast_name: str | None = None, selected_year=None, selected_month=None, progress_callback=None) -> dict:
    total_steps=7
    emit_progress(progress_callback,"Validando bases para Reporte 1",1,total_steps)
    for df,label in [(df_processed_sales,"ventas"),(df_plan_client,"plan cliente"),(df_fcst_client,"forecast cliente")]:
        if df is None or df.empty: raise ValueError(f"No existe base de {label} cargada.")
    report_year,report_month=resolve_reporting_period(df_processed_sales,selected_year,selected_month)
    plan_mtd,plan_ytd=get_plan_channel_totals_for_report_1(df_plan_client,report_month)
    fcst_mtd,fcst_ytd=get_fcst_channel_totals_for_report_1(df_fcst_client,report_month)
    sales=filter_sales_for_report_1(df_processed_sales,segment_values=list(config.REPORT_1_SEGMENTS_WITHOUT_KENS)+[config.REPORT_1_SEGMENT_KENS])
    mtd_actual,ytd_actual,mtd_py,ytd_py=get_sales_channel_totals_for_report_1(sales,report_year,report_month)
    mtd=build_report_1_without_kens_table(mtd_actual,plan_mtd,fcst_mtd,mtd_py)
    ytd=build_report_1_without_kens_table(ytd_actual,plan_ytd,fcst_ytd,ytd_py)
    summary={"latest_year":report_year,"latest_month":report_month,"segments_without_kens_label":"ACCO + BARR + KENS","forecast_name":forecast_name or "Fcst","forecast_label":normalize_forecast_label(forecast_name)}
    return {"summary":summary,"mtd_without_kens_table":mtd,"ytd_without_kens_table":ytd}


def build_report_2_row(
    segment_label: str,
    region_label: str,
    actual: float,
    plan: float,
    fcst: float,
    py: float,
    is_total: bool = False,
    is_grand_total: bool = False,
) -> dict:
    return {
        "Segmento": segment_label,
        "Región": region_label,
        "Actual": float(actual),
        "Plan": float(plan),
        "Fcst": float(fcst),
        "PY": float(py),
        "Var VS Plan": float(actual) - float(plan),
        "%Var VS Plan": safe_divide(float(actual) - float(plan), float(plan)),
        "Var VS Fcst": float(actual) - float(fcst),
        "%Var VS Fcst": safe_divide(float(actual) - float(fcst), float(fcst)),
        "Var VS PY": float(actual) - float(py),
        "%Var VS PY": safe_divide(float(actual) - float(py), float(py)),
        "__is_total__": is_total,
        "__is_grand_total__": is_grand_total,
    }


def build_report_2_segment_region_table(actual_df, plan_df, fcst_df, py_df) -> pd.DataFrame:
    """Construye Segment x Region dejando cada subtotal DEBAJO de su detalle."""
    actual_dict = aggregated_segment_region_df_to_dict(actual_df)
    plan_dict = aggregated_segment_region_df_to_dict(plan_df)
    fcst_dict = aggregated_segment_region_df_to_dict(fcst_df)
    py_dict = aggregated_segment_region_df_to_dict(py_df)

    all_keys = set(actual_dict) | set(plan_dict) | set(fcst_dict) | set(py_dict)
    grouped = {}
    for segment, region in all_keys:
        if is_forbidden_placeholder_segment(segment):
            continue
        grouped.setdefault(segment, set()).add(region)

    rows=[]
    grand=[0.0,0.0,0.0,0.0]
    for segment in sorted(grouped, key=get_report_2_segment_sort_key):
        subtotal=[0.0,0.0,0.0,0.0]
        detail_rows=[]
        for region in sorted(grouped[segment], key=get_report_2_region_sort_key):
            key=(segment,region)
            vals=[float(d.get(key,0.0)) for d in (actual_dict,plan_dict,fcst_dict,py_dict)]
            if not has_report_value(*vals):
                continue
            detail_rows.append(build_report_2_row(segment,region,*vals))
            subtotal=[a+b for a,b in zip(subtotal,vals)]
        if not detail_rows:
            continue
        rows.extend(detail_rows)
        rows.append(build_report_2_row(segment,config.REPORT_2_TOTAL_LABEL,*subtotal,is_total=True))
        grand=[a+b for a,b in zip(grand,subtotal)]

    rows.append(build_report_2_row("Total Mexico","",*grand,is_total=True,is_grand_total=True))
    return pd.DataFrame(rows)


def build_report_2_segment_region_payload(df_processed_sales, df_plan_sku, df_fcst_sku, forecast_name: str | None = None, selected_year=None, selected_month=None, progress_callback=None) -> dict:
    for df,label in [(df_processed_sales,"ventas"),(df_plan_sku,"plan SKU"),(df_fcst_sku,"forecast SKU")]:
        if df is None or df.empty: raise ValueError(f"No existe base de {label} cargada.")
    year,month=resolve_reporting_period(df_processed_sales,selected_year,selected_month)
    sales=prepare_sales_for_report_2(df_processed_sales); plan=prepare_plan_sku_for_report_2(df_plan_sku); fcst=prepare_fcst_sku_for_report_2(df_fcst_sku)
    mtd_a,ytd_a,mtd_py,ytd_py=get_sales_segment_region_totals_for_report_2(sales,year,month)
    mtd_p,ytd_p=get_plan_segment_region_totals_for_report_2(plan,month)
    mtd_f,ytd_f=get_fcst_segment_region_totals_for_report_2(fcst,month)
    return {"summary":{"latest_year":year,"latest_month":month,"forecast_name":forecast_name or "Fcst","forecast_label":normalize_forecast_label(forecast_name)},"mtd_segment_region_table":build_report_2_segment_region_table(mtd_a,mtd_p,mtd_f,mtd_py),"ytd_segment_region_table":build_report_2_segment_region_table(ytd_a,ytd_p,ytd_f,ytd_py)}


def build_report_2_category_row(
    category_label: str,
    material_label: str,
    product_label: str,
    description_label: str,
    actual: float,
    plan: float,
    fcst: float,
    py: float,
    is_total: bool = False,
    is_grand_total: bool = False,
) -> dict:
    return {
        "Category": category_label,
        "Material": material_label,
        "Categoría del Material": product_label,
        "Descripción del Material": description_label,
        "Actual": float(actual),
        "Plan": float(plan),
        "Fcst": float(fcst),
        "PY": float(py),
        "Var VS Plan": float(actual) - float(plan),
        "%Var VS Plan": safe_divide(float(actual) - float(plan), float(plan)),
        "Var VS Fcst": float(actual) - float(fcst),
        "%Var VS Fcst": safe_divide(float(actual) - float(fcst), float(fcst)),
        "Var VS PY": float(actual) - float(py),
        "%Var VS PY": safe_divide(float(actual) - float(py), float(py)),
        "__is_total__": is_total,
        "__is_grand_total__": is_grand_total,
    }


def build_report_2_category_table(actual_df, plan_df, fcst_df, py_df) -> pd.DataFrame:
    """Construye Category dejando cada subtotal DEBAJO de sus materiales."""
    actual_dict=aggregated_category_df_to_dict(actual_df)
    plan_dict=aggregated_category_df_to_dict(plan_df)
    fcst_dict=aggregated_category_df_to_dict(fcst_df)
    py_dict=aggregated_category_df_to_dict(py_df)
    all_keys=set(actual_dict)|set(plan_dict)|set(fcst_dict)|set(py_dict)
    categories=sorted({k[0] for k in all_keys},key=get_report_2_category_sort_key)
    rows=[]; grand=[0.0,0.0,0.0,0.0]
    for category in categories:
        keys=sorted(
            [k for k in all_keys if k[0]==category],
            key=lambda k:(get_report_2_material_sort_key(k[1]),get_report_2_product_sort_key(k[2]),get_report_2_description_sort_key(k[3]))
        )
        subtotal=[0.0,0.0,0.0,0.0]; detail=[]
        for key in keys:
            vals=[float(d.get(key,0.0)) for d in (actual_dict,plan_dict,fcst_dict,py_dict)]
            if not has_report_value(*vals):
                continue
            detail.append(build_report_2_category_row(key[0],key[1],key[2],key[3],*vals))
            subtotal=[a+b for a,b in zip(subtotal,vals)]
        if not detail:
            continue
        rows.extend(detail)
        rows.append(build_report_2_category_row(category,"",config.REPORT_2_TOTAL_LABEL,"",*subtotal,is_total=True))
        grand=[a+b for a,b in zip(grand,subtotal)]
    rows.append(build_report_2_category_row("Total Mexico","","","",*grand,is_total=True,is_grand_total=True))
    return pd.DataFrame(rows)


def build_report_2_category_payload(df_processed_sales, df_plan_sku, df_fcst_sku, forecast_name: str | None = None, selected_year=None, selected_month=None, progress_callback=None) -> dict:
    for df,label in [(df_processed_sales,"ventas"),(df_plan_sku,"plan SKU"),(df_fcst_sku,"forecast SKU")]:
        if df is None or df.empty: raise ValueError(f"No existe base de {label} cargada.")
    year,month=resolve_reporting_period(df_processed_sales,selected_year,selected_month)
    sales=prepare_sales_for_report_2_category(df_processed_sales); plan=prepare_plan_sku_for_report_2_category(df_plan_sku); fcst=prepare_fcst_sku_for_report_2_category(df_fcst_sku)
    mtd_a,ytd_a,mtd_py,ytd_py=get_sales_category_totals_for_report_2(sales,year,month)
    mtd_p,ytd_p=get_plan_category_totals_for_report_2(plan,month); mtd_f,ytd_f=get_fcst_category_totals_for_report_2(fcst,month)
    return {"summary":{"latest_year":year,"latest_month":month,"forecast_name":forecast_name or "Fcst","forecast_label":normalize_forecast_label(forecast_name)},"mtd_category_table":build_report_2_category_table(mtd_a,mtd_p,mtd_f,mtd_py),"ytd_category_table":build_report_2_category_table(ytd_a,ytd_p,ytd_f,ytd_py)}


def build_report_3_row(
    channel_label: str,
    actual: float,
    plan: float,
    fcst: float,
    py: float,
    is_total: bool = False,
    is_grand_total: bool = False,
) -> dict:
    return {
        "Channel": channel_label,
        "Actual": float(actual),
        "Plan": float(plan),
        "Fcst": float(fcst),
        "PY": float(py),
        "Var VS Plan": float(actual) - float(plan),
        "%Var VS Plan": safe_divide(float(actual) - float(plan), float(plan)),
        "Var VS Fcst": float(actual) - float(fcst),
        "%Var VS Fcst": safe_divide(float(actual) - float(fcst), float(fcst)),
        "Var VS PY": float(actual) - float(py),
        "%Var VS PY": safe_divide(float(actual) - float(py), float(py)),
        "__is_total__": is_total,
        "__is_grand_total__": is_grand_total,
    }


def build_report_3_channel_table(actual_df, plan_df, fcst_df, py_df) -> pd.DataFrame:
    ad=aggregated_channel_df_to_dict(actual_df); pdict=aggregated_channel_df_to_dict(plan_df); fd=aggregated_channel_df_to_dict(fcst_df); pyd=aggregated_channel_df_to_dict(py_df)
    channels=sorted(set(ad)|set(pdict)|set(fd)|set(pyd),key=get_report_3_channel_sort_key); rows=[]; totals=[0.0]*4
    for channel in channels:
        vals=[float(d.get(channel,0)) for d in [ad,pdict,fd,pyd]]
        if not has_report_value(*vals): continue
        totals=[a+b for a,b in zip(totals,vals)]; rows.append(build_report_3_row(channel,*vals))
    rows.append(build_report_3_row("Total Mexico",*totals,is_total=True,is_grand_total=True))
    return pd.DataFrame(rows)


def build_report_3_channel_payload(df_processed_sales, df_plan_sku, df_fcst_sku, forecast_name: str | None = None, selected_year=None, selected_month=None, progress_callback=None) -> dict:
    for df,label in [(df_processed_sales,"ventas"),(df_plan_sku,"plan SKU"),(df_fcst_sku,"forecast SKU")]:
        if df is None or df.empty: raise ValueError(f"No existe base de {label} cargada.")
    year,month=resolve_reporting_period(df_processed_sales,selected_year,selected_month)
    sales=prepare_sales_for_report_3(df_processed_sales); plan=prepare_plan_sku_for_report_3(df_plan_sku); fcst=prepare_fcst_sku_for_report_3(df_fcst_sku)
    mtd_a,ytd_a,mtd_py,ytd_py=get_sales_channel_totals_for_report_3(sales,year,month)
    mtd_p,ytd_p=get_plan_channel_totals_for_report_3(plan,month); mtd_f,ytd_f=get_fcst_channel_totals_for_report_3(fcst,month)
    return {"summary":{"latest_year":year,"latest_month":month,"forecast_name":forecast_name or "Fcst","forecast_label":normalize_forecast_label(forecast_name)},"mtd_channel_table":build_report_3_channel_table(mtd_a,mtd_p,mtd_f,mtd_py),"ytd_channel_table":build_report_3_channel_table(ytd_a,ytd_p,ytd_f,ytd_py)}


def build_report_4_row(
    client_code: str, client_label: str, actual: float, plan: float, fcst: float, py: float,
    top_position="", group_label="", is_total: bool=False, is_grand_total: bool=False, is_group_summary: bool=False,
) -> dict:
    return {
        "Client Name": client_label, "Cliente": client_code,
        "Actual": float(actual), "Plan": float(plan), "Fcst": float(fcst), "PY": float(py),
        "Var VS Plan": float(actual)-float(plan), "%Var VS Plan": safe_divide(float(actual)-float(plan),float(plan)),
        "Var VS Fcst": float(actual)-float(fcst), "%Var VS Fcst": safe_divide(float(actual)-float(fcst),float(fcst)),
        "Var VS PY": float(actual)-float(py), "%Var VS PY": safe_divide(float(actual)-float(py),float(py)),
        "TOP": top_position, "Grupo": group_label,
        "__top__": top_position, "__grupo__": group_label,
        "__is_total__": is_total, "__is_grand_total__": is_grand_total, "__is_group_summary__": is_group_summary,
    }


def build_report_4_detail_table(actual_df, plan_df, fcst_df, py_df, keep_internal: bool=True) -> pd.DataFrame:
    actual_dict=aggregated_client_df_to_dict(actual_df)
    plan_dict=aggregated_client_df_to_dict(plan_df)
    fcst_dict=aggregated_client_df_to_dict(fcst_df)
    py_dict=aggregated_client_df_to_dict(py_df)
    actual_names=aggregated_client_df_to_name_dict(actual_df)
    plan_names=aggregated_client_df_to_name_dict(plan_df)
    fcst_names=aggregated_client_df_to_name_dict(fcst_df)
    py_names=aggregated_client_df_to_name_dict(py_df)
    codes=set(actual_dict)|set(plan_dict)|set(fcst_dict)|set(py_dict)
    rows=[]
    for raw_code in codes:
        code=normalize_report_4_client_code(raw_code)
        if not code:
            continue
        actual=float(actual_dict.get(code,0.0)); plan=float(plan_dict.get(code,0.0)); fcst=float(fcst_dict.get(code,0.0)); py=float(py_dict.get(code,0.0))
        if not has_report_value(actual,plan,fcst,py):
            continue
        label=resolve_report_4_dynamic_client_label(code,actual_names,plan_names,py_names)
        if (not label or label==code) and str(fcst_names.get(code,"")).strip():
            label=str(fcst_names[code]).strip()
        rows.append(build_report_4_row(code,label,actual,plan,fcst,py,top_position=0,group_label=""))
    if not rows:
        return finalize_report_4_table(pd.DataFrame(),keep_internal=keep_internal)
    df=pd.DataFrame(rows).sort_values(
        by=["Actual","Plan","Fcst","PY","Client Name","Cliente"],
        ascending=[False,False,False,False,True,True],kind="mergesort"
    ).reset_index(drop=True)
    df["__top__"]=range(1,len(df)+1)
    df["__grupo__"]=df["__top__"].apply(get_report_4_group_from_top)
    return finalize_report_4_table(df,keep_internal=keep_internal)


def build_report_4_group_summary_table(detail_df: pd.DataFrame, keep_internal: bool=True) -> pd.DataFrame:
    if detail_df is None or detail_df.empty:
        return finalize_report_4_table(pd.DataFrame(),keep_internal=keep_internal)
    required=["Actual","Plan","Fcst","PY"]
    work=detail_df.copy()
    for col in required:
        if col not in work.columns:
            work[col]=0.0
    rows=[]
    groups=[config.REPORT_4_GROUP_TOP_15,config.REPORT_4_GROUP_16_50,config.REPORT_4_GROUP_51_100,config.REPORT_4_GROUP_OTHER]
    for group in groups:
        group_df=work[work["__grupo__"]==group].copy()
        if group_df.empty:
            continue
        vals=[pd.to_numeric(group_df[c],errors="coerce").fillna(0).sum() for c in required]
        label=getattr(config,"REPORT_4_GROUP_TOP_15_TOTAL_LABEL","Total Top 15") if group==config.REPORT_4_GROUP_TOP_15 else group
        rows.append(build_report_4_row("",label,*vals,group_label=group,is_total=True,is_group_summary=True))
    vals=[pd.to_numeric(work[c],errors="coerce").fillna(0).sum() for c in required]
    rows.append(build_report_4_row("",config.REPORT_4_TOTAL_LABEL,*vals,group_label=config.REPORT_4_TOTAL_LABEL,is_total=True,is_grand_total=True))
    return finalize_report_4_table(pd.DataFrame(rows),keep_internal=keep_internal)


def build_report_4_clients_table(actual_df, plan_df, fcst_df, py_df) -> pd.DataFrame:
    detail=build_report_4_detail_table(actual_df,plan_df,fcst_df,py_df,keep_internal=True); summary=build_report_4_group_summary_table(detail,keep_internal=True)
    top=detail[detail["__grupo__"]==config.REPORT_4_GROUP_TOP_15].copy(); label=getattr(config,"REPORT_4_GROUP_TOP_15_TOTAL_LABEL","Total Top 15")
    top_summary=summary[(summary["__grupo__"]==config.REPORT_4_GROUP_TOP_15)|(summary["Client Name"]==label)].copy()
    other=summary[summary["Client Name"].isin([config.REPORT_4_GROUP_16_50,config.REPORT_4_GROUP_51_100,config.REPORT_4_GROUP_OTHER,config.REPORT_4_TOTAL_LABEL])].copy()
    return finalize_report_4_table(pd.concat([top,top_summary,other],ignore_index=True),keep_internal=False)


def get_report_4_group_detail_table(detail_df: pd.DataFrame, group_label: str) -> pd.DataFrame:
    if detail_df is None or detail_df.empty: return finalize_report_4_table(pd.DataFrame(),keep_internal=False)
    filtered=detail_df[detail_df["__grupo__"]==group_label].copy()
    if filtered.empty: return finalize_report_4_table(filtered,keep_internal=False)
    vals=[filtered[c].apply(float).sum() for c in ["Actual","Plan","Fcst","PY"]]
    total=build_report_4_row("",f"Total {group_label}",*vals,group_label=group_label,is_total=True,is_group_summary=True)
    return finalize_report_4_table(pd.concat([filtered,pd.DataFrame([total])],ignore_index=True),keep_internal=False)


def build_report_4_top_clients_payload(
    df_processed_sales,
    df_plan_client,
    df_fcst_client,
    forecast_name: str | None = None,
    selected_year=None,
    selected_month=None,
    progress_callback=None,
) -> dict:
    """
    Construye el payload completo del Ranking de Clientes con Forecast.

    Conserva:
    - Top 15 cliente por cliente.
    - Total Top 15.
    - Resumen Clients 16 to 50.
    - Resumen Clients 51 to 100.
    - Resumen Other clients.
    - Total Mexico.

    Restaura además las tablas detalle MTD/YTD de:
    - Clients 16 to 50.
    - Clients 51 to 100.
    - Other clients.
    """
    total_steps = 8

    emit_progress(
        progress_callback,
        "Validando bases para Ranking de Clientes",
        1,
        total_steps,
    )

    required_sources = [
        (df_processed_sales, "ventas"),
        (df_plan_client, "plan cliente"),
        (df_fcst_client, "forecast cliente"),
    ]

    for dataframe, label in required_sources:
        if dataframe is None or dataframe.empty:
            raise ValueError(f"No existe base de {label} cargada.")

    emit_progress(
        progress_callback,
        "Resolviendo periodo del Ranking",
        2,
        total_steps,
    )

    year, month = resolve_reporting_period(
        df_processed_sales,
        selected_year,
        selected_month,
    )

    emit_progress(
        progress_callback,
        "Calculando Actual y PY por cliente",
        3,
        total_steps,
    )

    (
        mtd_actual,
        ytd_actual,
        mtd_py,
        ytd_py,
    ) = get_sales_client_totals_for_report_4(
        df_processed_sales,
        year,
        month,
    )

    emit_progress(
        progress_callback,
        "Integrando Plan y Forecast por cliente",
        4,
        total_steps,
    )

    mtd_plan, ytd_plan = get_plan_client_totals_for_report_4(
        df_plan_client,
        month,
    )
    mtd_fcst, ytd_fcst = get_fcst_client_totals_for_report_4(
        df_fcst_client,
        month,
    )

    emit_progress(
        progress_callback,
        "Ordenando clientes y asignando ranking",
        5,
        total_steps,
    )

    mtd_detail_internal = build_report_4_detail_table(
        mtd_actual,
        mtd_plan,
        mtd_fcst,
        mtd_py,
        keep_internal=True,
    )
    ytd_detail_internal = build_report_4_detail_table(
        ytd_actual,
        ytd_plan,
        ytd_fcst,
        ytd_py,
        keep_internal=True,
    )

    emit_progress(
        progress_callback,
        "Calculando Top 15, clientes 16-50, 51-100 y resto",
        6,
        total_steps,
    )

    mtd_summary_internal = build_report_4_group_summary_table(
        mtd_detail_internal,
        keep_internal=True,
    )
    ytd_summary_internal = build_report_4_group_summary_table(
        ytd_detail_internal,
        keep_internal=True,
    )

    emit_progress(
        progress_callback,
        "Construyendo tablas ejecutivas MTD y YTD",
        7,
        total_steps,
    )

    mtd_top_clients = build_report_4_clients_table(
        mtd_actual,
        mtd_plan,
        mtd_fcst,
        mtd_py,
    )
    ytd_top_clients = build_report_4_clients_table(
        ytd_actual,
        ytd_plan,
        ytd_fcst,
        ytd_py,
    )

    def get_total_value(summary_df, column_name: str) -> float:
        if summary_df is None or summary_df.empty:
            return 0.0

        if "Client Name" not in summary_df.columns:
            return 0.0

        total_rows = summary_df[
            summary_df["Client Name"].astype(str).str.strip()
            == str(config.REPORT_4_TOTAL_LABEL).strip()
        ]

        if total_rows.empty or column_name not in total_rows.columns:
            return 0.0

        return float(
            pd.to_numeric(
                total_rows[column_name],
                errors="coerce",
            ).fillna(0).sum()
        )

    emit_progress(
        progress_callback,
        "Preparando resumen y tablas detalle",
        8,
        total_steps,
    )

    summary = {
        "latest_year": year,
        "latest_month": month,
        "forecast_name": forecast_name or "Fcst",
        "forecast_label": normalize_forecast_label(forecast_name),
        "mtd_actual_total_k": get_total_value(mtd_summary_internal, "Actual") / 1000,
        "mtd_plan_total_k": get_total_value(mtd_summary_internal, "Plan") / 1000,
        "mtd_fcst_total_k": get_total_value(mtd_summary_internal, "Fcst") / 1000,
        "mtd_py_total_k": get_total_value(mtd_summary_internal, "PY") / 1000,
        "ytd_actual_total_k": get_total_value(ytd_summary_internal, "Actual") / 1000,
        "ytd_plan_total_k": get_total_value(ytd_summary_internal, "Plan") / 1000,
        "ytd_fcst_total_k": get_total_value(ytd_summary_internal, "Fcst") / 1000,
        "ytd_py_total_k": get_total_value(ytd_summary_internal, "PY") / 1000,
    }

    return {
        "summary": summary,

        # Vista ejecutiva principal.
        "mtd_top_clients_table": mtd_top_clients,
        "ytd_top_clients_table": ytd_top_clients,

        # Detalle completo.
        "mtd_detail_table": finalize_report_4_table(
            mtd_detail_internal,
            keep_internal=False,
        ),
        "ytd_detail_table": finalize_report_4_table(
            ytd_detail_internal,
            keep_internal=False,
        ),

        # Resúmenes por bloques.
        "mtd_summary_table": finalize_report_4_table(
            mtd_summary_internal,
            keep_internal=False,
        ),
        "ytd_summary_table": finalize_report_4_table(
            ytd_summary_internal,
            keep_internal=False,
        ),

        # TABLAS DETALLE RESTAURADAS.
        "mtd_group_16_50_table": get_report_4_group_detail_table(
            mtd_detail_internal,
            config.REPORT_4_GROUP_16_50,
        ),
        "ytd_group_16_50_table": get_report_4_group_detail_table(
            ytd_detail_internal,
            config.REPORT_4_GROUP_16_50,
        ),
        "mtd_group_51_100_table": get_report_4_group_detail_table(
            mtd_detail_internal,
            config.REPORT_4_GROUP_51_100,
        ),
        "ytd_group_51_100_table": get_report_4_group_detail_table(
            ytd_detail_internal,
            config.REPORT_4_GROUP_51_100,
        ),
        "mtd_group_other_table": get_report_4_group_detail_table(
            mtd_detail_internal,
            config.REPORT_4_GROUP_OTHER,
        ),
        "ytd_group_other_table": get_report_4_group_detail_table(
            ytd_detail_internal,
            config.REPORT_4_GROUP_OTHER,
        ),
    }

# Forecast también es monetario para conversiones auxiliares.
for _forecast_col in ["Fcst", "Var VS Fcst"]:
    if _forecast_col not in DEFAULT_MONETARY_COLUMNS:
        DEFAULT_MONETARY_COLUMNS.append(_forecast_col)


# =========================================================
# CORRECCIÓN FINAL: NORMALIZACIÓN DEL CÓDIGO DE CLIENTE
# =========================================================
def normalize_report_4_client_code(value) -> str:
    """Conserva el código de cliente como texto y evita formatos tipo 123.0."""
    if pd.isna(value):
        return ""
    text = str(value).strip()
    if not text or text.lower() in {"nan", "none", "null", "nat"}:
        return ""
    if re.fullmatch(r"[-+]?\d+\.0+", text):
        text = text.split(".", 1)[0]
    return text
