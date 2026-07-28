# ===========================================================
# VALIDADORES DE ESTRUCTURA
# Archivo: validators.py
# ===========================================================

from typing import Iterable

# -----------------------------------------------------------
# FUNCIÓN AUXILIAR:
# Normaliza nombres de columnas
# -----------------------------------------------------------
def normalize_column_name(column_name: str) -> str:
    """
    Limpia y normaliza nombres de columnas para comparación.
    """
    return str(column_name).strip().lower()

# -----------------------------------------------------------
# FUNCIÓN PRINCIPAL:
# Valida columnas requeridas
# -----------------------------------------------------------
def validate_required_columns(df, required_columns: Iterable[str]) -> tuple[bool, list[str]]:
    """
    Verifica si el DataFrame contiene las columnas requeridas.

    Retorna:
    - bool: True si todo está correcto
    - list: columnas faltantes
    """
    if df is None:
        return False, ["El DataFrame es None"]

    current_columns = [normalize_column_name(col) for col in df.columns]
    required_normalized = [normalize_column_name(col) for col in required_columns]

    missing_columns = [
        original_col
        for original_col, normalized_col in zip(required_columns, required_normalized)
        if normalized_col not in current_columns
    ]

    is_valid = len(missing_columns) == 0
    return is_valid, missing_columns

# -----------------------------------------------------------
# FUNCIÓN AUXILIAR:
# Valida si un DataFrame está listo para procesamiento
# -----------------------------------------------------------
def validate_dataframe_for_processing(df, required_columns: Iterable[str]) -> tuple[bool, list[str]]:
    """
    Verifica que el DataFrame no esté vacío y tenga estructura mínima.
    """
    if df is None:
        return False, ["No se recibió ningún archivo"]

    if df.empty:
        return False, ["El archivo está vacío"]

    return validate_required_columns(df, required_columns)

# -----------------------------------------------------------
# FUNCIÓN AUXILIAR:
# Valida múltiples DataFrames a la vez
# -----------------------------------------------------------
def validate_multiple_dataframes(dataframes: dict) -> tuple[bool, dict]:
    """
    Permite validar múltiples DataFrames en conjunto.

    Parámetro:
    dataframes = {
        "ventas": (df_sales, required_columns_sales),
        "plan_cliente": (df_plan_client, required_columns_plan_client),
        ...
    }

    Retorna:
    - bool: True si todos son válidos
    - dict: errores por cada dataframe
    """
    results = {}
    all_valid = True

    for name, (df, required_columns) in dataframes.items():
        is_valid, errors = validate_dataframe_for_processing(df, required_columns)
        results[name] = {
            "is_valid": is_valid,
            "errors": errors
        }

        if not is_valid:
            all_valid = False

    return all_valid, results
