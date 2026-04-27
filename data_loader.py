# ==========================================================
# CARGA DE ARCHIVOS
# Archivo: data_loader.py
# ==========================================================

from io import BytesIO

import pandas as pd

# ----------------------------------------------------------
# FUNCIÓN AUXILIAR:
# Detecta extensión del archivo cargado
# ----------------------------------------------------------
def get_file_extension(uploaded_file) -> str:
    """
    Obtiene la extensión del archivo cargado.
    """
    if uploaded_file is None:
        return ""

    file_name = uploaded_file.name.lower()

    if "." not in file_name:
        return ""

    return file_name.split(".")[-1]

# ----------------------------------------------------------
# FUNCIÓN AUXILIAR:
# Limpia nombres de columnas
# ----------------------------------------------------------
def standardize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Limpia espacios en los nombres de columnas.
    """
    df = df.copy()
    df.columns = [str(col).strip() for col in df.columns]
    return df

# ----------------------------------------------------------
# FUNCIÓN AUXILIAR:
# Recorta la tabla principal de Plan por Cliente
# usando el primer bloque vacío como corte
# ----------------------------------------------------------
def trim_plan_client_main_table(df: pd.DataFrame) -> pd.DataFrame:
    """
    Conserva únicamente la tabla principal de Plan2026 by Client.

    La lógica es:
    - la tabla ya viene arrancando desde header=13
    - se toman columnas A:T
    - una vez iniciada la tabla, si aparece una fila completamente vacía
      en las columnas base de identificación, se corta ahí
    - se eliminan filas sin Client real para evitar que Streamlit Cloud
      conserve filas residuales que Excel/localhost puede interpretar como vacías
    """
    df = df.copy()
    df = standardize_columns(df)

    df = df.reset_index(drop=True)

    base_cols = [
        "Segment",
        "Sales Region",
        "Sales region short",
        "Client",
        "Customer name",
        "Sales Zone",
        "Channel",
    ]

    existing_base_cols = [col for col in base_cols if col in df.columns]

    if not existing_base_cols:
        return df

    start_idx = None
    for i in range(len(df)):
        row_values = df.loc[i, existing_base_cols]
        has_data = row_values.notna().any() and (
            row_values.astype(str).str.strip().replace({"nan": "", "None": ""}) != ""
        ).any()

        if has_data:
            start_idx = i
            break

    if start_idx is None:
        return df.iloc[0:0].copy()

    df = df.iloc[start_idx:].reset_index(drop=True)

    stop_idx = None
    for i in range(len(df)):
        row_values = df.loc[i, existing_base_cols]

        cleaned = (
            row_values.astype(str)
            .str.strip()
            .replace({"nan": "", "None": ""})
        )

        if (cleaned == "").all():
            stop_idx = i
            break

    if stop_idx is not None:
        df = df.iloc[:stop_idx].copy()

    df = df.dropna(how="all")

    if "Client" in df.columns:
        client_values = (
            df["Client"]
            .astype(str)
            .str.strip()
            .replace({"nan": "", "None": "", "NaN": "", "NONE": ""})
        )
        df = df[client_values != ""].copy()

    df = df.reset_index(drop=True)

    return df

# ----------------------------------------------------------
# FUNCIÓN GENERAL:
# Lee archivo genérico
# ----------------------------------------------------------
def load_file_to_dataframe(
    uploaded_file,
    sheet_name=None,
    header=0,
    usecols=None,
):
    """
    Lee un archivo cargado y lo convierte a DataFrame.
    """
    if uploaded_file is None:
        raise ValueError("No se recibió ningún archivo.")

    extension = get_file_extension(uploaded_file)
    file_bytes = uploaded_file.getvalue()

    if extension == "csv":
        return pd.read_csv(BytesIO(file_bytes), header=header, usecols=usecols)

    if extension in ("xlsx", "xls"):
        return pd.read_excel(
            BytesIO(file_bytes),
            sheet_name=sheet_name,
            header=header,
            usecols=usecols,
        )

    raise ValueError(f"Tipo de archivo no soportado: {extension}")

# ----------------------------------------------------------
# FUNCIÓN ESPECIAL:
# Carga ventas desde BASE SAP
# ----------------------------------------------------------
def load_sales_file(uploaded_file):
    """
    Carga la hoja BASE SAP.
    """
    df = load_file_to_dataframe(
        uploaded_file,
        sheet_name="BASE SAP",
        header=5,
    )
    return standardize_columns(df)

# ----------------------------------------------------------
# FUNCIÓN ESPECIAL:
# Carga plan por cliente
# ----------------------------------------------------------
def load_plan_client_file(uploaded_file):
    """
    Carga únicamente la tabla principal de la hoja
    Plan2026 by Client.
    """
    df = load_file_to_dataframe(
        uploaded_file,
        sheet_name="Plan2026 by Client",
        header=13,
        usecols="A:T",
    )

    df = trim_plan_client_main_table(df)
    return df

# ----------------------------------------------------------
# FUNCIÓN ESPECIAL:
# Carga plan por SKU
# ----------------------------------------------------------
def load_plan_sku_file(uploaded_file):
    """
    Carga la hoja Plan2026 by SKU.
    """
    df = load_file_to_dataframe(
        uploaded_file,
        sheet_name="Plan2026 by SKU",
        header=7,
    )
    return standardize_columns(df)

