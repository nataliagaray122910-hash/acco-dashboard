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
    return str(column_name).strip().lower()
  
# -----------------------------------------------------------
# FUNCIÓN PRINCIPAL:
# Valida columnas requeridas
# -----------------------------------------------------------
def validate_required_columns(df, required_columns: Iterable[str]) -> tuple[bool, list[str]]:
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
    if df is None or df.empty:
        return False, ["El archivo está vacío"]

    return validate_required_columns(df, required_columns)

