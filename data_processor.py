# ===============================================================
# PROCESAMIENTO DE DATOS
# Archivo: data_processor.py
# ===============================================================

import re

import pandas as pd

import config

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
    "PY",
    "Var VS Plan",
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
def process_sales_data(df_sales: pd.DataFrame) -> pd.DataFrame:
    df = standardize_columns(df_sales)
    df = clean_sales_numeric_columns(df)
    df = add_year_month_columns(df)
    df = calculate_gsnr(df)
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
def calculate_actual_and_py_totals(
    df_processed_sales: pd.DataFrame,
    latest_year: int,
    latest_month: int,
) -> dict:
    df = df_processed_sales.copy()

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

    month_columns = get_plan_client_month_columns(df)

    if latest_month not in month_columns:
        raise ValueError(
            f"No se encontró la columna del mes {latest_month} en Plan por Cliente."
        )

    month_col = month_columns[latest_month]
    months_to_sum = [month_columns[m] for m in sorted(month_columns.keys()) if m <= latest_month]
    total_row_idx = find_first_total_row(df)

    if total_row_idx is not None:
        mtd_plan_client = clean_numeric_series(
            pd.Series([df.loc[total_row_idx, month_col]])
        ).iloc[0] * 1000

        ytd_plan_client = (
            sum(
                clean_numeric_series(pd.Series([df.loc[total_row_idx, col]])).iloc[0]
                for col in months_to_sum
            ) * 1000
        )
    else:
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
    df = df_processed_sales.copy()
    capped_month = min(latest_month, 8)

    bts_actual = df[
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

    bts_py_comparable = df[
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
        "bts_actual": float(bts_actual),
        "bts_py_comparable": float(bts_py_comparable),
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
    bts_actual: float,
    bts_py_comparable: float,
) -> pd.DataFrame:
    rows = [
        {
            "Periodo": "BTS",
            "Actual": bts_actual,
            "PY": bts_py_comparable,
            "Var VS PY": bts_actual - bts_py_comparable,
            "%Var VS PY": safe_divide(bts_actual - bts_py_comparable, bts_py_comparable),
        }
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
) -> dict:
    if df_processed_sales is None or df_processed_sales.empty:
        raise ValueError("No existe base de ventas procesada.")

    if df_plan_client is None or df_plan_client.empty:
        raise ValueError("No existe archivo de plan por cliente cargado.")

    if df_plan_sku is None or df_plan_sku.empty:
        raise ValueError("No existe archivo de plan por SKU cargado.")

    latest_year, latest_month = get_latest_actual_period_from_sales(df_processed_sales)

    if latest_year is None or latest_month is None:
        raise ValueError("No fue posible identificar el último periodo real disponible.")

    totals = calculate_actual_and_py_totals(
        df_processed_sales,
        latest_year,
        latest_month,
    )

    plan_summary = calculate_plan_totals_summary(
        df_plan_client,
        df_plan_sku,
        latest_month,
    )

    bts_totals = calculate_bts_totals(
        df_processed_sales,
        latest_year,
        latest_month,
    )

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
        bts_totals["bts_actual"],
        bts_totals["bts_py_comparable"],
    )

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
        "latest_year": latest_year,
        "latest_month": latest_month,
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
    if pd.isna(value):
        return ""

    text = str(value).strip()
    if not text:
        return ""

    if ":" in text:
        return text.split(":")[0].strip().upper()

    return text.split()[0].strip().upper()

# --------------------------------------------------------------
# FUNCIÓN AUXILIAR:
# Obtiene etiqueta visual de canal
# --------------------------------------------------------------
def get_channel_display_label(channel_code: str) -> str:
    return config.REPORT_1_CHANNEL_LABELS.get(channel_code, channel_code)

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

    mtd_grouped = {str(k): float(v) for k, v in mtd_grouped.items() if str(k).strip()}
    ytd_grouped = {str(k): float(v) for k, v in ytd_grouped.items() if str(k).strip()}

    return mtd_grouped, ytd_grouped

# --------------------------------------------------------------
# FUNCIÓN AUXILIAR:
# Filtra ventas para reporte 1
# --------------------------------------------------------------
def filter_sales_for_report_1(
    df_processed_sales: pd.DataFrame,
    segment_values: list[str] | None = None,
    single_segment: str | None = None,
) -> pd.DataFrame:
    df = standardize_columns(df_processed_sales).copy()

    required_cols = ["Segm Neg", "Oficina de Ventas", config.COL_GSNR, config.COL_YEAR, config.COL_MONTH]
    missing = [col for col in required_cols if col not in df.columns]
    if missing:
        raise ValueError(
            f"Faltan columnas requeridas en ventas para Reporte 1: {', '.join(missing)}"
        )

    df["__segment__"] = df["Segm Neg"].astype(str).str.strip().str.upper()
    df["__channel_code__"] = df["Oficina de Ventas"].apply(extract_channel_code)
    df[config.COL_GSNR] = clean_numeric_series(df[config.COL_GSNR])

    if segment_values is not None:
        valid_segments = [str(x).strip().upper() for x in segment_values]
        df = df[df["__segment__"].isin(valid_segments)].copy()

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
        return {str(k): float(v) for k, v in values.items() if str(k).strip()}

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
# Construye tabla WITHOUT KENS
# --------------------------------------------------------------
def build_report_1_without_kens_table(
    actual_dict: dict[str, float],
    plan_dict: dict[str, float],
    py_dict: dict[str, float],
) -> pd.DataFrame:
    codes_present = set(actual_dict.keys()) | set(plan_dict.keys()) | set(py_dict.keys())
    codes_present.discard("IT")

    ordered_codes = [
        code for code in config.REPORT_1_CHANNEL_ORDER
        if code in codes_present and code != "IT"
    ]

    rows = []
    total_actual = 0.0
    total_plan = 0.0
    total_py = 0.0

    for code in ordered_codes:
        actual = float(actual_dict.get(code, 0.0))
        plan = float(plan_dict.get(code, 0.0))
        py = float(py_dict.get(code, 0.0))

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
# FUNCIÓN AUXILIAR:
# Construye tabla WITH KENS
# --------------------------------------------------------------
def build_report_1_with_kens_table(
    actual_dict: dict[str, float],
    plan_dict: dict[str, float],
    py_dict: dict[str, float],
) -> pd.DataFrame:
    detail_codes_present = set(actual_dict.keys()) | set(py_dict.keys())

    ordered_detail_codes = [
        code for code in config.REPORT_1_CHANNEL_ORDER
        if code in detail_codes_present
    ]

    rows = []

    for code in ordered_detail_codes:
        actual = float(actual_dict.get(code, 0.0))
        py = float(py_dict.get(code, 0.0))

        rows.append(
            build_report_1_row(
                office_label=get_channel_display_label(code),
                actual=actual,
                plan=None,
                py=py,
            )
        )

    total_actual = sum(float(v) for v in actual_dict.values())
    total_py = sum(float(v) for v in py_dict.values())
    total_plan = float(plan_dict.get("IT", 0.0))

    rows.append(
        build_report_1_row(
            office_label=config.REPORT_1_KENS_TOTAL_LABEL,
            actual=total_actual,
            plan=total_plan,
            py=total_py,
            is_highlight=True,
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
) -> dict:
    if df_processed_sales is None or df_processed_sales.empty:
        raise ValueError("No existe base de ventas procesada.")

    if df_plan_client is None or df_plan_client.empty:
        raise ValueError("No existe archivo de plan por cliente cargado.")

    report_year, report_month = resolve_reporting_period(
        df_processed_sales,
        selected_year=selected_year,
        selected_month=selected_month,
    )

    plan_mtd_by_channel, plan_ytd_by_channel = get_plan_channel_totals_for_report_1(
        df_plan_client,
        report_month,
    )

    sales_without_kens = filter_sales_for_report_1(
        df_processed_sales,
        segment_values=config.REPORT_1_SEGMENTS_WITHOUT_KENS,
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

    sales_kens = filter_sales_for_report_1(
        df_processed_sales,
        single_segment=config.REPORT_1_SEGMENT_KENS,
    )

    (
        mtd_actual_kens,
        ytd_actual_kens,
        mtd_py_kens,
        ytd_py_kens,
    ) = get_sales_channel_totals_for_report_1(
        sales_kens,
        report_year,
        report_month,
    )

    mtd_kens_table = build_report_1_with_kens_table(
        actual_dict=mtd_actual_kens,
        plan_dict=plan_mtd_by_channel,
        py_dict=mtd_py_kens,
    )

    ytd_kens_table = build_report_1_with_kens_table(
        actual_dict=ytd_actual_kens,
        plan_dict=plan_ytd_by_channel,
        py_dict=ytd_py_kens,
    )

    summary = {
        "latest_year": report_year,
        "latest_month": report_month,
        "segments_without_kens_label": "ACCO + BARRILITO",
        "segment_kens_label": "KENS",
    }

    return {
        "summary": summary,
        "mtd_without_kens_table": mtd_without_kens_table,
        "ytd_without_kens_table": ytd_without_kens_table,
        "mtd_kens_table": mtd_kens_table,
        "ytd_kens_table": ytd_kens_table,
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

# --------------------------------------------------------------
# FUNCIÓN AUXILIAR:
# Normaliza texto visible para Región
# --------------------------------------------------------------
def normalize_report_2_label(value) -> str:
    if pd.isna(value):
        return ""

    text = str(value).strip()
    if not text:
        return ""

    return text.upper()

# --------------------------------------------------------------
# FUNCIÓN AUXILIAR:
# Normaliza texto visible para Segmento
# GOBA se sustituye por BARRILITO
# ZZZZ se excluye después en filtros
# --------------------------------------------------------------
def normalize_report_2_segment_label(value) -> str:
    if pd.isna(value):
        return ""

    text = str(value).strip().upper()
    if not text:
        return ""

    if text == "GOBA":
        return "BARRILITO"

    return text

# --------------------------------------------------------------
# FUNCIÓN AUXILIAR:
# Normaliza Category para Reporte 2
# --------------------------------------------------------------
def normalize_report_2_category_label(value) -> str:
    if pd.isna(value):
        return ""

    text = re.sub(r"\s+", " ", str(value).strip())
    if not text:
        return ""

    upper_text = text.upper()

    if upper_text in {"#N/A", "N/A", "NA", "NAN", "NONE"}:
        return ""

    return text

# --------------------------------------------------------------
# FUNCIÓN AUXILIAR:
# Normaliza Channel para Reporte 3
# --------------------------------------------------------------
def normalize_report_3_channel_label(value) -> str:
    if pd.isna(value):
        return ""

    text = str(value).strip().upper()
    if not text:
        return ""

    if text == "GOBA":
        return "BARRILITO"

    return text

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

    return str(value).strip().upper()

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

    segment_col = find_first_existing_column(df, ["Segm Neg", "Segmento", "Segment"])
    region_col = find_first_existing_column(df, ["Región", "Region"])
    gsnr_col = find_first_existing_column(df, [config.COL_GSNR, "GSNR"])

    required_columns = [segment_col, region_col, gsnr_col, config.COL_YEAR, config.COL_MONTH]
    if any(col is None for col in required_columns):
        raise ValueError(
            "Faltan columnas requeridas en ventas para Reporte 2. "
            "Se requieren Segmento, Región, GSNR, Año y Mes."
        )

    df = df.copy()
    df["__segment__"] = df[segment_col].apply(normalize_report_2_segment_label)
    df["__region__"] = df[region_col].apply(normalize_report_2_label)
    df["__gsnr__"] = clean_numeric_series(df[gsnr_col])

    df = df[
        (df["__segment__"] != "")
        & (df["__segment__"] != "ZZZZ")
        & (df["__region__"] != "")
    ].copy()

    return df

# --------------------------------------------------------------
# FUNCIÓN AUXILIAR:
# Prepara plan SKU para Reporte 2
# --------------------------------------------------------------
def prepare_plan_sku_for_report_2(df_plan_sku: pd.DataFrame) -> pd.DataFrame:
    df = standardize_columns(df_plan_sku)
    df = exclude_afi_affiliates(df)

    segment_col = find_first_existing_column(df, ["Segmento", "Segment", "Segm Neg"])
    region_col = find_first_existing_column(df, ["Región", "Region"])

    if segment_col is None or region_col is None:
        raise ValueError(
            "Faltan columnas requeridas en Plan por SKU para Reporte 2. "
            "Se requieren Segmento y Región."
        )

    month_columns = get_plan_sku_gs_columns(df)
    if not month_columns:
        raise ValueError("No se detectaron columnas mensuales válidas en Plan por SKU.")

    df = df.copy()
    df["__segment__"] = df[segment_col].apply(normalize_report_2_segment_label)
    df["__region__"] = df[region_col].apply(normalize_report_2_label)

    for col in month_columns.values():
        df[col] = clean_numeric_series(df[col])

    df = df[
        (df["__segment__"] != "")
        & (df["__segment__"] != "ZZZZ")
        & (df["__region__"] != "")
    ].copy()

    return df

# --------------------------------------------------------------
# FUNCIÓN AUXILIAR:
# Agrega ventas Segment x Region
# --------------------------------------------------------------
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
        result[key] = float(row["Valor"])

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
        if segment_value == "ZZZZ":
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
        if segment_value == "ZZZZ":
            continue

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
) -> dict:
    if df_processed_sales is None or df_processed_sales.empty:
        raise ValueError("No existe base de ventas procesada.")

    if df_plan_sku is None or df_plan_sku.empty:
        raise ValueError("No existe archivo de plan por SKU cargado.")

    report_year, report_month = resolve_reporting_period(
        df_processed_sales,
        selected_year=selected_year,
        selected_month=selected_month,
    )

    mtd_actual_df, ytd_actual_df, mtd_py_df, ytd_py_df = get_sales_segment_region_totals_for_report_2(
        df_processed_sales,
        report_year,
        report_month,
    )

    mtd_plan_df, ytd_plan_df = get_plan_segment_region_totals_for_report_2(
        df_plan_sku,
        report_month,
    )

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
    gsnr_col = find_first_existing_column(df, [config.COL_GSNR, "GSNR"])

    required_columns = [category_col, gsnr_col, config.COL_YEAR, config.COL_MONTH]
    if any(col is None for col in required_columns):
        raise ValueError(
            "Faltan columnas requeridas en ventas para Reporte Category. "
            "Se requieren Corpo Category, GSNR, Año y Mes."
        )

    df = df.copy()
    df["__category__"] = df[category_col].apply(normalize_report_2_category_label)
    df["__gsnr__"] = clean_numeric_series(df[gsnr_col])

    df = df[df["__category__"] != ""].copy()

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

    if category_col is None:
        raise ValueError(
            "Faltan columnas requeridas en Plan por SKU para Reporte Category. "
            "Se requiere Corpo Category."
        )

    month_columns = get_plan_sku_gs_columns(df)
    if not month_columns:
        raise ValueError("No se detectaron columnas mensuales válidas en Plan por SKU.")

    df = df.copy()
    df["__category__"] = df[category_col].apply(normalize_report_2_category_label)

    for col in month_columns.values():
        df[col] = clean_numeric_series(df[col])

    df = df[df["__category__"] != ""].copy()

    return df

# --------------------------------------------------------------
# FUNCIÓN AUXILIAR:
# Agrega ventas Category
# --------------------------------------------------------------
def get_sales_category_totals_for_report_2(
    df_processed_sales: pd.DataFrame,
    selected_year: int,
    selected_month: int,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    df = prepare_sales_for_report_2_category(df_processed_sales)

    current_year_df = df[df[config.COL_YEAR] == selected_year].copy()
    previous_year_df = df[df[config.COL_YEAR] == (selected_year - 1)].copy()

    mtd_actual = (
        current_year_df[current_year_df[config.COL_MONTH] == selected_month]
        .groupby("__category__", dropna=False)["__gsnr__"]
        .sum()
        .reset_index()
        .rename(
            columns={
                "__category__": "Category",
                "__gsnr__": "Valor",
            }
        )
    )

    ytd_actual = (
        current_year_df[current_year_df[config.COL_MONTH] <= selected_month]
        .groupby("__category__", dropna=False)["__gsnr__"]
        .sum()
        .reset_index()
        .rename(
            columns={
                "__category__": "Category",
                "__gsnr__": "Valor",
            }
        )
    )

    mtd_py = (
        previous_year_df[previous_year_df[config.COL_MONTH] == selected_month]
        .groupby("__category__", dropna=False)["__gsnr__"]
        .sum()
        .reset_index()
        .rename(
            columns={
                "__category__": "Category",
                "__gsnr__": "Valor",
            }
        )
    )

    ytd_py = (
        previous_year_df[previous_year_df[config.COL_MONTH] <= selected_month]
        .groupby("__category__", dropna=False)["__gsnr__"]
        .sum()
        .reset_index()
        .rename(
            columns={
                "__category__": "Category",
                "__gsnr__": "Valor",
            }
        )
    )

    return mtd_actual, ytd_actual, mtd_py, ytd_py

# --------------------------------------------------------------
# FUNCIÓN AUXILIAR:
# Agrega plan Category
# --------------------------------------------------------------
def get_plan_category_totals_for_report_2(
    df_plan_sku: pd.DataFrame,
    latest_month: int,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    df = prepare_plan_sku_for_report_2_category(df_plan_sku)
    gs_columns = get_plan_sku_gs_columns(df)

    if latest_month not in gs_columns:
        raise ValueError(
            f"No se encontró la columna GS del mes {latest_month} en Plan por SKU."
        )

    month_col = gs_columns[latest_month]
    months_to_sum = [gs_columns[m] for m in sorted(gs_columns.keys()) if m <= latest_month]

    mtd_plan = (
        df.groupby("__category__", dropna=False)[month_col]
        .sum()
        .reset_index()
        .rename(
            columns={
                "__category__": "Category",
                month_col: "Valor",
            }
        )
    )

    ytd_plan = (
        df.assign(__ytd__=df[months_to_sum].sum(axis=1))
        .groupby("__category__", dropna=False)["__ytd__"]
        .sum()
        .reset_index()
        .rename(
            columns={
                "__category__": "Category",
                "__ytd__": "Valor",
            }
        )
    )

    return mtd_plan, ytd_plan

# --------------------------------------------------------------
# FUNCIÓN AUXILIAR:
# Convierte agregados Category a diccionario
# --------------------------------------------------------------
def aggregated_category_df_to_dict(df: pd.DataFrame) -> dict[str, float]:
    if df is None or df.empty:
        return {}

    result = {}

    for _, row in df.iterrows():
        key = normalize_report_2_category_label(row["Category"])
        result[key] = float(row["Valor"])

    return result

# --------------------------------------------------------------
# FUNCIÓN AUXILIAR:
# Llave de orden para Category
# --------------------------------------------------------------
def get_report_2_category_sort_key(category_value: str) -> str:
    return normalize_report_2_category_label(category_value).lower()

# --------------------------------------------------------------
# FUNCIÓN AUXILIAR:
# Construye renglón de Reporte Category
# --------------------------------------------------------------
def build_report_2_category_row(
    category_label: str,
    actual: float,
    plan: float,
    py: float,
    is_total: bool = False,
    is_grand_total: bool = False,
) -> dict:
    return {
        "Category": category_label,
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
# Construye tabla final Category
# --------------------------------------------------------------
def build_report_2_category_table(
    actual_df: pd.DataFrame,
    plan_df: pd.DataFrame,
    py_df: pd.DataFrame,
) -> pd.DataFrame:
    actual_dict = aggregated_category_df_to_dict(actual_df)
    plan_dict = aggregated_category_df_to_dict(plan_df)
    py_dict = aggregated_category_df_to_dict(py_df)

    all_categories = set(actual_dict.keys()) | set(plan_dict.keys()) | set(py_dict.keys())

    ordered_categories = sorted(
        all_categories,
        key=get_report_2_category_sort_key,
    )

    rows: list[dict] = []

    grand_total_actual = 0.0
    grand_total_plan = 0.0
    grand_total_py = 0.0

    for category_value in ordered_categories:
        actual_value = float(actual_dict.get(category_value, 0.0))
        plan_value = float(plan_dict.get(category_value, 0.0))
        py_value = float(py_dict.get(category_value, 0.0))

        if actual_value == 0 and plan_value == 0 and py_value == 0:
            continue

        rows.append(
            build_report_2_category_row(
                category_label=category_value,
                actual=actual_value,
                plan=plan_value,
                py=py_value,
            )
        )

        grand_total_actual += actual_value
        grand_total_plan += plan_value
        grand_total_py += py_value

    rows.append(
        build_report_2_category_row(
            category_label=config.REPORT_2_GRAND_TOTAL_LABEL,
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
) -> dict:
    if df_processed_sales is None or df_processed_sales.empty:
        raise ValueError("No existe base de ventas procesada.")

    if df_plan_sku is None or df_plan_sku.empty:
        raise ValueError("No existe archivo de plan por SKU cargado.")

    report_year, report_month = resolve_reporting_period(
        df_processed_sales,
        selected_year=selected_year,
        selected_month=selected_month,
    )

    mtd_actual_df, ytd_actual_df, mtd_py_df, ytd_py_df = get_sales_category_totals_for_report_2(
        df_processed_sales,
        report_year,
        report_month,
    )

    mtd_plan_df, ytd_plan_df = get_plan_category_totals_for_report_2(
        df_plan_sku,
        report_month,
    )

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
# Si no existe, aplica la lógica:
# NORTE / SUR / RETAIL -> Segmento
# resto -> Region
# --------------------------------------------------------------
def build_report_3_channel_series(df: pd.DataFrame) -> pd.Series:
    channel_col = find_first_existing_column(df, ["Canal", "Channel"])
    region_col = find_first_existing_column(df, ["Región", "Region"])
    segment_col = find_first_existing_column(df, ["Segmento", "Segm Neg", "Segment"])

    if channel_col is not None:
        return df[channel_col].apply(normalize_report_3_channel_label)

    if region_col is None or segment_col is None:
        raise ValueError(
            "Faltan columnas requeridas para construir Channel en Reporte 3. "
            "Se requiere Canal o bien Region y Segmento."
        )

    region_series = df[region_col].apply(normalize_report_3_channel_label)
    segment_series = df[segment_col].apply(normalize_report_3_channel_label)

    return pd.Series(
        [
            segment_value if region_value in config.REPORT_3_REGION_TO_SEGMENT else region_value
            for region_value, segment_value in zip(region_series, segment_series)
        ],
        index=df.index,
    )

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
    df["__channel__"] = build_report_3_channel_series(df)
    df["__gsnr__"] = clean_numeric_series(df[gsnr_col])

    df = df[df["__channel__"] != ""].copy()

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
    df["__channel__"] = build_report_3_channel_series(df)

    for col in month_columns.values():
        df[col] = clean_numeric_series(df[col])

    df = df[df["__channel__"] != ""].copy()

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
        result[key] = float(row["Valor"])

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
        actual_value = float(actual_dict.get(channel_value, 0.0))
        plan_value = float(plan_dict.get(channel_value, 0.0))
        py_value = float(py_dict.get(channel_value, 0.0))

        if actual_value == 0 and plan_value == 0 and py_value == 0:
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
) -> dict:
    if df_processed_sales is None or df_processed_sales.empty:
        raise ValueError("No existe base de ventas procesada.")

    if df_plan_sku is None or df_plan_sku.empty:
        raise ValueError("No existe archivo de plan por SKU cargado.")

    report_year, report_month = resolve_reporting_period(
        df_processed_sales,
        selected_year=selected_year,
        selected_month=selected_month,
    )

    mtd_actual_df, ytd_actual_df, mtd_py_df, ytd_py_df = get_sales_channel_totals_for_report_3(
        df_processed_sales,
        report_year,
        report_month,
    )

    mtd_plan_df, ytd_plan_df = get_plan_channel_totals_for_report_3(
        df_plan_sku,
        report_month,
    )

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
# ETAPA 8: REPORTE 4 - TOP 15 CLIENTS
# ==============================================================

# --------------------------------------------------------------
# FUNCIÓN AUXILIAR:
# Obtiene mapa de display_name -> regla
# --------------------------------------------------------------
def get_report_4_rules_map() -> dict[str, dict]:
    return {rule["display_name"]: rule for rule in config.REPORT_4_CLIENT_NAME_RULES}

# --------------------------------------------------------------
# FUNCIÓN AUXILIAR:
# Resuelve display name de cliente según nombre y código
# --------------------------------------------------------------
def resolve_report_4_display_name(client_name, client_code) -> str:
    normalized_name = normalize_report_4_client_name(client_name)
    normalized_code = normalize_report_4_client_code(client_code)

    for rule in config.REPORT_4_CLIENT_NAME_RULES:
        source_names = [normalize_report_4_client_name(x) for x in rule.get("source_names", [])]
        source_codes = [normalize_report_4_client_code(x) for x in rule.get("source_codes", [])]

        if normalized_name not in source_names:
            continue

        if source_codes:
            if normalized_code:
                if normalized_code in source_codes:
                    return rule["display_name"]
                continue
            else:
                return rule["display_name"]

        return rule["display_name"]

    return ""

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
# Prioriza Customer name antes que cualquier otra opción
# --------------------------------------------------------------
def get_report_4_plan_client_name_column(df: pd.DataFrame) -> str | None:
    preferred_candidates = [
        "Customer name",
        "Customer Name",
        "Nombre del Cliente",
        "Nombre Cliente",
        "Cliente",
    ]

    preferred_match = find_first_existing_column(df, preferred_candidates)
    if preferred_match is not None:
        return preferred_match

    fallback_match = find_first_existing_column(df, config.REPORT_4_PLAN_CLIENT_NAME_CANDIDATES)

    if fallback_match is not None and normalize_text(fallback_match) != normalize_text("Client"):
        return fallback_match

    return fallback_match

# --------------------------------------------------------------
# FUNCIÓN AUXILIAR:
# Detecta columna de código cliente en plan cliente
# Prioriza Client como código
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
# Prepara ventas para Reporte 4
# --------------------------------------------------------------
def prepare_sales_for_report_4(df_processed_sales: pd.DataFrame) -> pd.DataFrame:
    df = standardize_columns(df_processed_sales)
    df = exclude_afi_affiliates(df)

    client_name_col = get_report_4_sales_client_name_column(df)
    client_code_col = get_report_4_sales_client_code_column(df)
    gsnr_col = find_first_existing_column(df, [config.COL_GSNR, "GSNR"])

    required_columns = [client_name_col, gsnr_col, config.COL_YEAR, config.COL_MONTH]
    if any(col is None for col in required_columns):
        raise ValueError(
            "Faltan columnas requeridas en ventas para Reporte 4. "
            "Se requieren Nombre del Cliente, GSNR, Año y Mes."
        )

    df = df.copy()
    df["__client_name_raw__"] = df[client_name_col]
    df["__client_code_raw__"] = df[client_code_col] if client_code_col is not None else ""
    df["__display_name__"] = df.apply(
        lambda row: resolve_report_4_display_name(
            row["__client_name_raw__"],
            row["__client_code_raw__"],
        ),
        axis=1,
    )
    df["__gsnr__"] = clean_numeric_series(df[gsnr_col])

    df = df[df["__display_name__"] != ""].copy()

    return df

# --------------------------------------------------------------
# FUNCIÓN AUXILIAR:
# Prepara plan cliente para Reporte 4
# --------------------------------------------------------------
def prepare_plan_client_for_report_4(df_plan_client: pd.DataFrame) -> pd.DataFrame:
    df = standardize_columns(df_plan_client)
    df = remove_total_like_rows(df)

    client_name_col = get_report_4_plan_client_name_column(df)
    client_code_col = get_report_4_plan_client_code_column(df)

    if client_name_col is None:
        raise ValueError(
            "Faltan columnas requeridas en Plan por Cliente para Reporte 4. "
            "Se requiere una columna de nombre como 'Customer name'."
        )

    month_columns = get_plan_client_month_columns(df)
    if not month_columns:
        raise ValueError("No se detectaron columnas mensuales válidas en Plan por Cliente.")

    df = df.copy()

    if (
        client_code_col is not None
        and client_name_col is not None
        and normalize_text(client_code_col) == normalize_text(client_name_col)
    ):
        rescue_name_col = find_first_existing_column(df, ["Customer name", "Customer Name"])
        if rescue_name_col is not None:
            client_name_col = rescue_name_col

    df["__client_name_raw__"] = df[client_name_col]
    df["__client_code_raw__"] = df[client_code_col] if client_code_col is not None else ""

    df["__display_name__"] = df.apply(
        lambda row: resolve_report_4_display_name(
            row["__client_name_raw__"],
            row["__client_code_raw__"],
        ),
        axis=1,
    )

    for col in month_columns.values():
        df[col] = clean_numeric_series(df[col]) * 1000

    df = df[df["__display_name__"] != ""].copy()

    return df

# --------------------------------------------------------------
# FUNCIÓN AUXILIAR:
# Agrega ventas Top 15 Clients
# --------------------------------------------------------------
def get_sales_client_totals_for_report_4(
    df_processed_sales: pd.DataFrame,
    selected_year: int,
    selected_month: int,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    df = prepare_sales_for_report_4(df_processed_sales)

    current_year_df = df[df[config.COL_YEAR] == selected_year].copy()
    previous_year_df = df[df[config.COL_YEAR] == (selected_year - 1)].copy()

    mtd_actual = (
        current_year_df[current_year_df[config.COL_MONTH] == selected_month]
        .groupby("__display_name__", dropna=False)["__gsnr__"]
        .sum()
        .reset_index()
        .rename(
            columns={
                "__display_name__": "Client Name",
                "__gsnr__": "Valor",
            }
        )
    )

    ytd_actual = (
        current_year_df[current_year_df[config.COL_MONTH] <= selected_month]
        .groupby("__display_name__", dropna=False)["__gsnr__"]
        .sum()
        .reset_index()
        .rename(
            columns={
                "__display_name__": "Client Name",
                "__gsnr__": "Valor",
            }
        )
    )

    mtd_py = (
        previous_year_df[previous_year_df[config.COL_MONTH] == selected_month]
        .groupby("__display_name__", dropna=False)["__gsnr__"]
        .sum()
        .reset_index()
        .rename(
            columns={
                "__display_name__": "Client Name",
                "__gsnr__": "Valor",
            }
        )
    )

    ytd_py = (
        previous_year_df[previous_year_df[config.COL_MONTH] <= selected_month]
        .groupby("__display_name__", dropna=False)["__gsnr__"]
        .sum()
        .reset_index()
        .rename(
            columns={
                "__display_name__": "Client Name",
                "__gsnr__": "Valor",
            }
        )
    )

    return mtd_actual, ytd_actual, mtd_py, ytd_py

# --------------------------------------------------------------
# FUNCIÓN AUXILIAR:
# Agrega plan Top 15 Clients
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

    mtd_plan = (
        df.groupby("__display_name__", dropna=False)[month_col]
        .sum()
        .reset_index()
        .rename(
            columns={
                "__display_name__": "Client Name",
                month_col: "Valor",
            }
        )
    )

    ytd_plan = (
        df.assign(__ytd__=df[months_to_sum].sum(axis=1))
        .groupby("__display_name__", dropna=False)["__ytd__"]
        .sum()
        .reset_index()
        .rename(
            columns={
                "__display_name__": "Client Name",
                "__ytd__": "Valor",
            }
        )
    )

    return mtd_plan, ytd_plan

# --------------------------------------------------------------
# FUNCIÓN AUXILIAR:
# Convierte agregados Client a diccionario
# --------------------------------------------------------------
def aggregated_client_df_to_dict(df: pd.DataFrame) -> dict[str, float]:
    if df is None or df.empty:
        return {}

    result = {}

    for _, row in df.iterrows():
        key = str(row["Client Name"]).strip()
        result[key] = float(row["Valor"])

    return result

# --------------------------------------------------------------
# FUNCIÓN AUXILIAR:
# Llave de orden para Client Name
# --------------------------------------------------------------
def get_report_4_client_sort_key(client_value: str) -> tuple[int, str]:
    normalized_value = str(client_value).strip()

    if normalized_value in config.REPORT_4_TOP_CLIENTS_ORDER:
        return config.REPORT_4_TOP_CLIENTS_ORDER.index(normalized_value), normalized_value

    return len(config.REPORT_4_TOP_CLIENTS_ORDER), normalized_value

# --------------------------------------------------------------
# FUNCIÓN AUXILIAR:
# Construye renglón de Reporte 4
# --------------------------------------------------------------
def build_report_4_row(
    client_label: str,
    actual: float,
    plan: float,
    py: float,
    is_total: bool = False,
    is_grand_total: bool = False,
) -> dict:
    return {
        "Client Name": client_label,
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
# Construye tabla final Top 15 Clients
# --------------------------------------------------------------
def build_report_4_clients_table(
    actual_df: pd.DataFrame,
    plan_df: pd.DataFrame,
    py_df: pd.DataFrame,
) -> pd.DataFrame:
    actual_dict = aggregated_client_df_to_dict(actual_df)
    plan_dict = aggregated_client_df_to_dict(plan_df)
    py_dict = aggregated_client_df_to_dict(py_df)

    ordered_clients = list(config.REPORT_4_TOP_CLIENTS_ORDER)

    rows: list[dict] = []

    grand_total_actual = 0.0
    grand_total_plan = 0.0
    grand_total_py = 0.0

    for client_value in ordered_clients:
        actual_value = float(actual_dict.get(client_value, 0.0))
        plan_value = float(plan_dict.get(client_value, 0.0))
        py_value = float(py_dict.get(client_value, 0.0))

        rows.append(
            build_report_4_row(
                client_label=client_value,
                actual=actual_value,
                plan=plan_value,
                py=py_value,
            )
        )

        grand_total_actual += actual_value
        grand_total_plan += plan_value
        grand_total_py += py_value

    rows.append(
        build_report_4_row(
            client_label=config.REPORT_4_TOTAL_LABEL,
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
# Construye payload de Reporte 4 - Top 15 Clients
# --------------------------------------------------------------
def build_report_4_top_clients_payload(
    df_processed_sales: pd.DataFrame,
    df_plan_client: pd.DataFrame,
    selected_year: int | None = None,
    selected_month: int | None = None,
) -> dict:
    if df_processed_sales is None or df_processed_sales.empty:
        raise ValueError("No existe base de ventas procesada.")

    if df_plan_client is None or df_plan_client.empty:
        raise ValueError("No existe archivo de plan por cliente cargado.")

    report_year, report_month = resolve_reporting_period(
        df_processed_sales,
        selected_year=selected_year,
        selected_month=selected_month,
    )

    mtd_actual_df, ytd_actual_df, mtd_py_df, ytd_py_df = get_sales_client_totals_for_report_4(
        df_processed_sales,
        report_year,
        report_month,
    )

    mtd_plan_df, ytd_plan_df = get_plan_client_totals_for_report_4(
        df_plan_client,
        report_month,
    )

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

    mtd_total_row = mtd_table[mtd_table["Client Name"] == config.REPORT_4_TOTAL_LABEL]
    ytd_total_row = ytd_table[ytd_table["Client Name"] == config.REPORT_4_TOTAL_LABEL]

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
        "mtd_top_clients_table": mtd_table,
        "ytd_top_clients_table": ytd_table,
    }
