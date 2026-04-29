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
# Detecta celdas vacías reales o aparentes
# ----------------------------------------------------------
def is_blank_like(value) -> bool:
    """
    Detecta vacíos reales y vacíos aparentes que pueden venir de Excel.
    En Streamlit Cloud algunas celdas visualmente vacías pueden llegar como
    None, nan, espacios o texto equivalente.
    """
    if pd.isna(value):
        return True

    text = str(value).strip()
    return text == "" or text.lower() in {"nan", "none", "null", "nat"}

# ----------------------------------------------------------
# FUNCIÓN AUXILIAR:
# Limpia texto de celda para comparar encabezados internos
# ----------------------------------------------------------
def clean_cell_text(value) -> str:
    if is_blank_like(value):
        return ""

    return str(value).strip()

# ----------------------------------------------------------
# FUNCIÓN AUXILIAR:
# Recorta la tabla principal de Plan por Cliente
# usando el primer bloque vacío como corte y detectando
# también el inicio de tablas resumen inferiores.
# ----------------------------------------------------------
def trim_plan_client_main_table(df: pd.DataFrame) -> pd.DataFrame:
    """
    Conserva únicamente la tabla principal de Plan2026 by Client.

    La lógica es:
    - la tabla ya viene arrancando desde header=13
    - se toman columnas A:T
    - una vez iniciada la tabla, si aparece una fila completamente vacía
      en las columnas base de identificación, se corta ahí
    - como protección adicional para Streamlit Cloud, también se corta
      si detecta el inicio de una tabla inferior de resumen por Channel
      o una fila sin identificadores de cliente pero con montos mensuales.

    Esto evita que se sumen tablas de resumen ubicadas debajo de la tabla
    principal, sin eliminar filas válidas como Kensington, Ecommerce o Export,
    aunque algunas de ellas no tengan código en Client.
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

    identity_cols_without_channel = [
        "Segment",
        "Sales Region",
        "Sales region short",
        "Client",
        "Customer name",
        "Sales Zone",
    ]

    month_cols = [
        "JAN", "FEB", "MAR", "APR", "MAY", "JUN",
        "JUL", "AUG", "SEP", "OCT", "NOV", "DEC", "FY 2026p",
    ]

    existing_base_cols = [col for col in base_cols if col in df.columns]
    existing_identity_cols = [col for col in identity_cols_without_channel if col in df.columns]
    existing_month_cols = [col for col in month_cols if col in df.columns]

    if not existing_base_cols:
        return df

    start_idx = None
    for i in range(len(df)):
        row_values = df.loc[i, existing_base_cols]
        has_data = any(not is_blank_like(value) for value in row_values)

        if has_data:
            start_idx = i
            break

    if start_idx is None:
        return df.iloc[0:0].copy()

    df = df.iloc[start_idx:].reset_index(drop=True)

    stop_idx = None
    for i in range(len(df)):
        base_values = df.loc[i, existing_base_cols]
        identity_values = df.loc[i, existing_identity_cols] if existing_identity_cols else pd.Series(dtype=object)
        month_values = df.loc[i, existing_month_cols] if existing_month_cols else pd.Series(dtype=object)

        base_is_empty = all(is_blank_like(value) for value in base_values)
        identity_is_empty = all(is_blank_like(value) for value in identity_values) if existing_identity_cols else False
        months_have_data = any(not is_blank_like(value) for value in month_values) if existing_month_cols else False

        channel_text = clean_cell_text(df.loc[i, "Channel"]) if "Channel" in df.columns else ""
        jan_text = clean_cell_text(df.loc[i, "JAN"]).upper() if "JAN" in df.columns else ""
        feb_text = clean_cell_text(df.loc[i, "FEB"]).upper() if "FEB" in df.columns else ""
        mar_text = clean_cell_text(df.loc[i, "MAR"]).upper() if "MAR" in df.columns else ""

        is_repeated_channel_header = (
            identity_is_empty
            and channel_text.lower() == "channel"
            and jan_text == "JAN"
            and feb_text == "FEB"
            and mar_text == "MAR"
        )

        is_lower_summary_row = identity_is_empty and months_have_data

        if base_is_empty or is_repeated_channel_header or is_lower_summary_row:
            stop_idx = i
            break

    if stop_idx is not None:
        df = df.iloc[:stop_idx].copy()

    df = df.dropna(how="all").reset_index(drop=True)

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

