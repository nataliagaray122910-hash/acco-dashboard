# ==========================================================
# CARGA DE ARCHIVOS
# Archivo: data_loader.py
# ==========================================================

from io import BytesIO
import re

import pandas as pd

# ----------------------------------------------------------
# FUNCIÓN AUXILIAR:
# Envía avances reales al componente visual de app.py
# ----------------------------------------------------------
def emit_progress(
    progress_callback,
    message: str,
    step: int,
    total_steps: int,
) -> None:
    """
    Envía el avance actual a app.py sin crear dependencias con Streamlit.

    El callback es opcional. Si no se recibe, la carga funciona exactamente
    igual que antes. Cuando app.py lo proporcione, recibirá:
    - message: nombre real de la etapa
    - step: número de etapa que comienza
    - total_steps: total de etapas del proceso
    """
    if progress_callback is None:
        return

    progress_callback(
        message=message,
        step=step,
        total_steps=total_steps,
    )

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
# Detecta dinámicamente las hojas de Forecast
# ----------------------------------------------------------
def detect_forecast_sheet_names(workbook) -> dict:
    """
    Detecta el par de hojas Forecast del archivo corporativo.

    Formatos reconocidos:
    - Fcst2+10 by Client / Fcst2+10 by SKU
    - Fcst5+7 by Client / Fcst5+7 by SKU
    - Fcst8+4 by Client / Fcst8+4 by SKU
    - Fcst10+2 by Client / Fcst10+2 by SKU
    - Fcst11+1 by Client / Fcst11+1 by SKU

    La detección se hace por patrón, por lo que no queda amarrada a un
    Forecast específico. Se exige que Client y SKU correspondan al mismo ciclo.
    """
    if workbook is None:
        raise ValueError("No se recibió un libro de Excel para detectar Forecast.")

    pattern = re.compile(
        r"^\s*Fcst\s*(\d+)\s*\+\s*(\d+)\s+by\s+(Client|SKU)\s*$",
        flags=re.IGNORECASE,
    )

    detected: dict[str, dict[str, str]] = {}

    for sheet_name in workbook.sheet_names:
        match = pattern.match(str(sheet_name))
        if not match:
            continue

        first_part = int(match.group(1))
        second_part = int(match.group(2))
        sheet_type = match.group(3).lower()
        forecast_key = f"{first_part}+{second_part}"

        detected.setdefault(forecast_key, {})
        detected[forecast_key][sheet_type] = str(sheet_name)

    complete_pairs = {
        key: value
        for key, value in detected.items()
        if "client" in value and "sku" in value
    }

    if not complete_pairs:
        found_names = [
            str(name)
            for name in workbook.sheet_names
            if str(name).strip().lower().startswith("fcst")
        ]
        found_text = ", ".join(found_names) if found_names else "ninguna"
        raise ValueError(
            "No se encontró un par válido de hojas Forecast (by Client y by SKU) "
            f"con el mismo ciclo. Hojas Forecast detectadas: {found_text}."
        )

    if len(complete_pairs) > 1:
        cycles = ", ".join(sorted(complete_pairs.keys()))
        raise ValueError(
            "Se detectó más de un ciclo Forecast completo en el mismo archivo "
            f"({cycles}). El archivo debe contener un único par activo de Forecast."
        )

    forecast_key = next(iter(complete_pairs))
    pair = complete_pairs[forecast_key]

    return {
        "forecast_name": f"Fcst{forecast_key}",
        "forecast_cycle": forecast_key,
        "forecast_client_sheet_name": pair["client"],
        "forecast_sku_sheet_name": pair["sku"],
    }


# ----------------------------------------------------------
# FUNCIÓN AUXILIAR:
# Recorta una tabla en la primera fila totalmente vacía
# ----------------------------------------------------------
def trim_at_first_fully_blank_row(df: pd.DataFrame) -> pd.DataFrame:
    """
    Conserva filas desde el inicio hasta antes de la primera fila totalmente vacía.

    Regla:
    - Si toda la fila está vacía, la lectura termina.
    - Si existe al menos un dato en la fila, la fila se conserva.
    """
    if df is None:
        return df

    df = standardize_columns(df.copy()).reset_index(drop=True)

    stop_idx = None
    for i in range(len(df)):
        row_values = df.iloc[i]
        if all(is_blank_like(value) for value in row_values):
            stop_idx = i
            break

    if stop_idx is not None:
        df = df.iloc[:stop_idx].copy()

    return df.reset_index(drop=True)


# ----------------------------------------------------------
# FUNCIÓN AUXILIAR:
# Recorta la tabla central de Forecast por Cliente
# ----------------------------------------------------------
def trim_forecast_client_main_table(df: pd.DataFrame) -> pd.DataFrame:
    """
    Conserva únicamente la tabla principal de Forecast by Client.

    La tabla ya se lee con encabezados desde la fila 32 de Excel (header=31).
    Se corta exactamente en la primera fila completamente vacía; cualquier fila
    que contenga al menos un dato se conserva.
    """
    return trim_at_first_fully_blank_row(df)


# ----------------------------------------------------------
# FUNCIÓN AUXILIAR:
# Recorta la tabla principal de Forecast por SKU
# ----------------------------------------------------------
def trim_forecast_sku_main_table(df: pd.DataFrame) -> pd.DataFrame:
    """
    Conserva la tabla de Forecast by SKU desde la fila 8 de Excel (header=7).

    Se corta exactamente en la primera fila completamente vacía; cualquier fila
    que contenga al menos un dato se conserva.

    Las columnas QTY y GS se cargan completas. La selección de columnas GS para
    cálculos comerciales se realizará posteriormente en data_processor.py.
    """
    return trim_at_first_fully_blank_row(df)

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
# FUNCIÓN AUXILIAR:
# Recorta filas fantasma de BASE SAP
# ----------------------------------------------------------
def trim_sales_main_table(df: pd.DataFrame) -> pd.DataFrame:
    """
    Conserva únicamente registros reales de BASE SAP.

    NO elimina:
    - filas con ceros
    - filas con NA parciales
    - registros incompletos

    SOLO elimina filas completamente vacías que Excel/Pandas puede
    interpretar como registros por formatos, fórmulas o residuos debajo
    de la tabla principal.
    """
    df = df.copy()
    df = standardize_columns(df)
    df = df.reset_index(drop=True)

    # Elimina filas completamente vacías reales.
    df = df.dropna(how="all")

    # Elimina filas donde TODAS las celdas son vacías aparentes.
    # Esto conserva cualquier fila que tenga al menos un dato real.
    df = df[
        ~df.apply(
            lambda row: all(is_blank_like(value) for value in row),
            axis=1,
        )
    ].copy()

    return df.reset_index(drop=True)

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
        return pd.read_csv(
            BytesIO(file_bytes),
            header=header,
            usecols=usecols,
            keep_default_na=False,
        )

    if extension in ("xlsx", "xls"):
        return pd.read_excel(
            BytesIO(file_bytes),
            sheet_name=sheet_name,
            header=header,
            usecols=usecols,
            keep_default_na=False,
        )

    raise ValueError(f"Tipo de archivo no soportado: {extension}")

def load_uploaded_excel_workbook(uploaded_file):
    """
    Lee una sola vez el archivo Excel cargado manualmente y devuelve un
    objeto ExcelFile reutilizable.

    Esta función evita que Streamlit Cloud tenga que abrir el mismo Excel
    tres veces para BASE SAP, Plan Cliente y Plan SKU.
    """
    if uploaded_file is None:
        raise ValueError("No se recibió ningún archivo.")

    extension = get_file_extension(uploaded_file)

    if extension not in ("xlsx", "xls"):
        raise ValueError(
            "La carga única del dashboard requiere un archivo Excel (.xlsx o .xls)."
        )

    file_bytes = uploaded_file.getvalue()
    return pd.ExcelFile(BytesIO(file_bytes))


def load_dashboard_excel_from_uploaded_file(
    uploaded_file,
    progress_callback=None,
) -> dict:
    """
    Lee una sola carga manual del Excel corporativo y devuelve las cinco
    bases funcionales del dashboard.

    Retorna:
    - df_sales: hoja BASE SAP
    - df_plan_client: hoja Plan2026 by Client
    - df_plan_sku: hoja Plan2026 by SKU
    - df_fcst_client: hoja Forecast dinámica by Client
    - df_fcst_sku: hoja Forecast dinámica by SKU
    - forecast_name y nombres reales de las hojas detectadas

    Las tres hojas originales conservan exactamente sus reglas de lectura.
    """
    total_steps = 11

    emit_progress(
        progress_callback,
        "Validando el archivo Excel seleccionado",
        1,
        total_steps,
    )
    if uploaded_file is None:
        raise ValueError("No se recibió ningún archivo.")

    emit_progress(
        progress_callback,
        "Abriendo el libro de Excel",
        2,
        total_steps,
    )
    workbook = load_uploaded_excel_workbook(uploaded_file)

    emit_progress(
        progress_callback,
        "Detectando las hojas Forecast activas",
        3,
        total_steps,
    )
    forecast_info = detect_forecast_sheet_names(workbook)

    emit_progress(
        progress_callback,
        "Leyendo la hoja BASE SAP",
        4,
        total_steps,
    )
    df_sales = pd.read_excel(
        workbook,
        sheet_name="BASE SAP",
        header=5,
        keep_default_na=False,
    )

    emit_progress(
        progress_callback,
        "Limpiando filas vacías de BASE SAP",
        5,
        total_steps,
    )
    df_sales = trim_sales_main_table(df_sales)

    emit_progress(
        progress_callback,
        "Leyendo y recortando Plan2026 by Client",
        6,
        total_steps,
    )
    df_plan_client = pd.read_excel(
        workbook,
        sheet_name="Plan2026 by Client",
        header=13,
        usecols="A:T",
        keep_default_na=False,
    )
    df_plan_client = trim_plan_client_main_table(df_plan_client)

    emit_progress(
        progress_callback,
        "Leyendo Plan2026 by SKU",
        7,
        total_steps,
    )
    df_plan_sku = pd.read_excel(
        workbook,
        sheet_name="Plan2026 by SKU",
        header=7,
        keep_default_na=False,
    )
    df_plan_sku = standardize_columns(df_plan_sku)

    emit_progress(
        progress_callback,
        f"Leyendo {forecast_info['forecast_client_sheet_name']}",
        8,
        total_steps,
    )
    df_fcst_client = pd.read_excel(
        workbook,
        sheet_name=forecast_info["forecast_client_sheet_name"],
        header=31,
        usecols="A:T",
        keep_default_na=False,
    )

    emit_progress(
        progress_callback,
        "Recortando la tabla principal de Forecast by Client",
        9,
        total_steps,
    )
    df_fcst_client = trim_forecast_client_main_table(df_fcst_client)

    emit_progress(
        progress_callback,
        f"Leyendo {forecast_info['forecast_sku_sheet_name']}",
        10,
        total_steps,
    )
    df_fcst_sku = pd.read_excel(
        workbook,
        sheet_name=forecast_info["forecast_sku_sheet_name"],
        header=7,
        keep_default_na=False,
    )

    emit_progress(
        progress_callback,
        "Recortando Forecast by SKU y preparando las cinco bases",
        11,
        total_steps,
    )
    df_fcst_sku = trim_forecast_sku_main_table(df_fcst_sku)

    return {
        "df_sales": df_sales,
        "df_plan_client": df_plan_client,
        "df_plan_sku": df_plan_sku,
        "df_fcst_client": df_fcst_client,
        "df_fcst_sku": df_fcst_sku,
        "forecast_name": forecast_info["forecast_name"],
        "forecast_cycle": forecast_info["forecast_cycle"],
        "forecast_client_sheet_name": forecast_info["forecast_client_sheet_name"],
        "forecast_sku_sheet_name": forecast_info["forecast_sku_sheet_name"],
    }


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

    df = trim_sales_main_table(df)
    return df

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


# ----------------------------------------------------------
# FUNCIÓN ESPECIAL:
# Carga Forecast por Cliente detectando el nombre dinámico
# ----------------------------------------------------------
def load_forecast_client_file(uploaded_file):
    """
    Detecta y carga la hoja activa FcstX+Y by Client.
    Encabezados: fila 32 de Excel.
    """
    workbook = load_uploaded_excel_workbook(uploaded_file)
    forecast_info = detect_forecast_sheet_names(workbook)

    df = pd.read_excel(
        workbook,
        sheet_name=forecast_info["forecast_client_sheet_name"],
        header=31,
        usecols="A:T",
        keep_default_na=False,
    )
    return trim_forecast_client_main_table(df)


# ----------------------------------------------------------
# FUNCIÓN ESPECIAL:
# Carga Forecast por SKU detectando el nombre dinámico
# ----------------------------------------------------------
def load_forecast_sku_file(uploaded_file):
    """
    Detecta y carga la hoja activa FcstX+Y by SKU.
    Encabezados: fila 8 de Excel.
    """
    workbook = load_uploaded_excel_workbook(uploaded_file)
    forecast_info = detect_forecast_sheet_names(workbook)

    df = pd.read_excel(
        workbook,
        sheet_name=forecast_info["forecast_sku_sheet_name"],
        header=7,
        keep_default_na=False,
    )
    return trim_forecast_sku_main_table(df)
