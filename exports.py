# =========================================================
# EXPORTACIONES A EXCEL
# Archivo: exports.py
# =========================================================

from io import BytesIO

import pandas as pd

import config
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

# ---------------------------------------------------------
# ESTILOS BASE DE EXCEL
# ---------------------------------------------------------
THIN_BORDER = Border(
    left=Side(style="thin", color="D9DEE5"),
    right=Side(style="thin", color="D9DEE5"),
    top=Side(style="thin", color="D9DEE5"),
    bottom=Side(style="thin", color="D9DEE5"),
)

TITLE_FILL = PatternFill(fill_type="solid", fgColor="1F2A44")
GLOBAL_TITLE_FILL = PatternFill(fill_type="solid", fgColor="000000")
HEADER_NEUTRAL_FILL = PatternFill(fill_type="solid", fgColor="1F2A44")
HEADER_ACTUAL_FILL = PatternFill(fill_type="solid", fgColor="0B5A7A")
HEADER_PLAN_FILL = PatternFill(fill_type="solid", fgColor="D4A017")

HEADER_PY_FILL = PatternFill(fill_type="solid", fgColor="0B5A7A")

LABEL_FILL = PatternFill(fill_type="solid", fgColor="F8FAFC")
TOTAL_FILL = PatternFill(fill_type="solid", fgColor="F3F6FA")
HIGHLIGHT_FILL = PatternFill(fill_type="solid", fgColor="E8F3E6")
HIGHLIGHT_LABEL_FILL = PatternFill(fill_type="solid", fgColor="DCEFD8")

TITLE_FONT = Font(color="FFFFFF", bold=True, size=12)
GLOBAL_TITLE_FONT = Font(color="FFFFFF", bold=True, size=14)
HEADER_FONT = Font(color="FFFFFF", bold=True, size=10)
BODY_FONT = Font(color="1E1E1E", bold=False, size=10)
BODY_BOLD_FONT = Font(color="1E1E1E", bold=True, size=10)
NEGATIVE_FONT = Font(color="C0392B", bold=True, size=10)

CENTER_ALIGNMENT = Alignment(horizontal="center", vertical="center")
LEFT_ALIGNMENT = Alignment(horizontal="left", vertical="center")
RIGHT_ALIGNMENT = Alignment(horizontal="right", vertical="center")

# ---------------------------------------------------------
# CONFIGURACIÓN GENERAL
# ---------------------------------------------------------
DEFAULT_TABLE_SPACING_COLUMNS = 2
DEFAULT_BLOCK_SPACING_ROWS = 3
DEFAULT_SHEET_TITLE_ROW_HEIGHT = 22
DEFAULT_GLOBAL_TITLE_ROW_HEIGHT = 28
DEFAULT_HEADER_ROW_HEIGHT = 20
DEFAULT_BODY_ROW_HEIGHT = 19

PERCENT_COLUMNS = {"%Var VS Plan", "%Var VS PY", "% GM", "Weight"}

NUMERIC_COLUMNS = {
    "Actual",
    "Plan",
    "PY",
    "Var VS Plan",
    "Var VS PY",
    "GSNR",
    "Gross Margin",
    "MTD Act",
    "MTD PY",
    "MTD Plan",
    "MTD Var vs PY",
    "MTD % Var vs PY",
    "MTD Var vs Plan",
    "MTD % Var vs Plan",
    "YTD Act",
    "YTD PY",
    "YTD Plan",
    "YTD Var vs PY",
    "YTD % Var vs PY",
    "YTD Var vs Plan",
    "YTD % Var vs Plan",
}

INTERNAL_COLUMNS_PREFIX = "__"

# ---------------------------------------------------------
# CONFIGURACIÓN ESPECÍFICA REPORTE 4
# ---------------------------------------------------------
REPORT_4_VISIBLE_COLUMNS = [
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

REPORT_4_HIDDEN_EXPORT_COLUMNS = {"TOP", "Grupo"}

# ---------------------------------------------------------
# HELPERS GENERALES
# ---------------------------------------------------------
def sanitize_sheet_name(sheet_name: str) -> str:
    invalid_chars = ["\\", "/", "*", "?", ":", "[", "]"]
    cleaned = str(sheet_name).strip()

    for char in invalid_chars:
        cleaned = cleaned.replace(char, "-")

    cleaned = cleaned[:31].strip()

    return cleaned or "Hoja"

def is_internal_column(column_name: str) -> bool:
    return str(column_name).startswith(INTERNAL_COLUMNS_PREFIX)

def sanitize_export_dataframe(df: pd.DataFrame | None) -> pd.DataFrame:
    """
    Limpia cualquier DataFrame antes de exportarlo.

    Reglas generales:
    - Si no existe DataFrame, regresa uno vacío.
    - Quita columnas internas que empiezan con __.
    - Conserva el resto de columnas en el orden recibido.
    """
    if df is None:
        return pd.DataFrame()

    clean_df = df.copy()
    visible_columns = [
        col for col in clean_df.columns
        if not is_internal_column(str(col))
    ]

    return clean_df[visible_columns].copy()

def prepare_report_4_export_dataframe(df: pd.DataFrame | None) -> pd.DataFrame:
    """
    Limpia las tablas del Reporte 4 para exportación.

    Reglas:
    - No exporta columnas internas.
    - No exporta TOP ni Grupo.
    - Fuerza el mismo orden visible que la app: Client Name, Cliente y métricas.
    """
    if df is None:
        return pd.DataFrame(columns=REPORT_4_VISIBLE_COLUMNS)

    clean_df = df.copy()

    for column_name in REPORT_4_HIDDEN_EXPORT_COLUMNS:
        if column_name in clean_df.columns:
            clean_df = clean_df.drop(columns=[column_name])

    internal_columns = [col for col in clean_df.columns if is_internal_column(str(col))]
    clean_df = clean_df.drop(columns=internal_columns, errors="ignore")

    for column_name in REPORT_4_VISIBLE_COLUMNS:
        if column_name not in clean_df.columns:
            clean_df[column_name] = "" if column_name in {"Client Name", "Cliente"} else 0.0

    return clean_df[REPORT_4_VISIBLE_COLUMNS].copy()

def get_first_column_name(df: pd.DataFrame) -> str | None:
    if df is None or df.empty or len(df.columns) == 0:
        return None
    return str(df.columns[0])

def safe_float(value):
    if value is None:
        return None

    try:
        numeric_value = float(value)
        if pd.isna(numeric_value):
            return None
        return numeric_value
    except (TypeError, ValueError):
        return None

def is_percent_column(column_name: str) -> bool:
    return str(column_name).strip() in PERCENT_COLUMNS

def is_numeric_column(column_name: str) -> bool:
    column_name = str(column_name).strip()
    return column_name in NUMERIC_COLUMNS or column_name in PERCENT_COLUMNS

def is_negative_number(value) -> bool:
    numeric_value = safe_float(value)
    return numeric_value is not None and numeric_value < 0

def estimate_column_width(series: pd.Series, header_text: str) -> int:
    max_length = len(str(header_text))

    for value in series.fillna("").astype(str).tolist():
        max_length = max(max_length, len(value))

    max_length = min(max_length + 2, 35)
    max_length = max(max_length, 12)

    return max_length

def excel_number_format_for_column(column_name: str) -> str:
    if is_percent_column(column_name):
        return "0.00%;[Red](0.00%)"

    if is_numeric_column(column_name):
        return "#,##0;[Red](#,##0)"

    return "@"

def scale_value_for_export(column_name: str, value):
    numeric_value = safe_float(value)

    if numeric_value is None:
        return None

    if is_percent_column(column_name):
        return numeric_value

    if is_numeric_column(column_name):
        return numeric_value / 1000

    return value

# ---------------------------------------------------------
# HELPERS DE ESTILO
# ---------------------------------------------------------
def apply_fill_if_present(cell, fill_style) -> None:
    if fill_style is not None:
        cell.fill = fill_style

def get_row_flags(original_df: pd.DataFrame, row_index: int) -> dict:
    if original_df is None or original_df.empty:
        return {
            "is_total": False,
            "is_grand_total": False,
            "is_highlight": False,
        }

    row = original_df.iloc[row_index]

    return {
        "is_total": bool(row.get("__is_total__", False)),
        "is_grand_total": bool(row.get("__is_grand_total__", False)),
        "is_highlight": bool(row.get("__is_highlight__", False)),
    }

def get_body_fill(column_name: str, row_flags: dict):
    is_total = row_flags.get("is_total", False)
    is_grand_total = row_flags.get("is_grand_total", False)
    is_highlight = row_flags.get("is_highlight", False)
    first_col = row_flags.get("first_col_name")

    if is_highlight:
        if column_name == first_col:
            return HIGHLIGHT_LABEL_FILL
        return HIGHLIGHT_FILL

    if is_total or is_grand_total:
        return TOTAL_FILL

    if column_name == first_col:
        return LABEL_FILL

    return None

def get_body_font(value, row_flags: dict):
    is_total = row_flags.get("is_total", False)
    is_grand_total = row_flags.get("is_grand_total", False)
    is_highlight = row_flags.get("is_highlight", False)

    if is_negative_number(value):
        return NEGATIVE_FONT

    if is_total or is_grand_total or is_highlight:
        return BODY_BOLD_FONT

    return BODY_FONT

def get_header_fill(column_name: str):
    column_name = str(column_name).strip()

    if column_name == "Actual":
        return HEADER_ACTUAL_FILL
    if column_name == "Plan":
        return HEADER_PLAN_FILL
    if column_name == "PY":
        return HEADER_PY_FILL

    return HEADER_NEUTRAL_FILL

def write_global_title(
    worksheet,
    report_title: str | None,
    start_row: int = 1,
    start_col: int = 1,
    width: int = 8,
) -> int:
    """
    Escribe un encabezado general del reporte en Excel.
    Devuelve la siguiente fila disponible.
    """
    if not report_title:
        return start_row

    worksheet.merge_cells(
        start_row=start_row,
        start_column=start_col,
        end_row=start_row,
        end_column=start_col + width - 1,
    )

    title_cell = worksheet.cell(row=start_row, column=start_col, value=report_title)
    title_cell.font = GLOBAL_TITLE_FONT
    title_cell.alignment = CENTER_ALIGNMENT
    title_cell.border = THIN_BORDER
    title_cell.fill = GLOBAL_TITLE_FILL

    worksheet.row_dimensions[start_row].height = DEFAULT_GLOBAL_TITLE_ROW_HEIGHT

    return start_row + 2

# ---------------------------------------------------------
# ESCRITURA DE TABLAS
# ---------------------------------------------------------
def write_table_to_worksheet(
    worksheet,
    original_df: pd.DataFrame,
    start_row: int,
    start_col: int,
    table_title: str,
) -> tuple[int, int]:
    export_df = sanitize_export_dataframe(original_df)

    if export_df is None or export_df.empty:
        title_cell = worksheet.cell(row=start_row, column=start_col, value=table_title)
        title_cell.font = TITLE_FONT
        title_cell.alignment = LEFT_ALIGNMENT
        title_cell.border = THIN_BORDER
        apply_fill_if_present(title_cell, TITLE_FILL)

        info_cell = worksheet.cell(
            row=start_row + 1,
            column=start_col,
            value="Sin información disponible",
        )
        info_cell.font = BODY_FONT
        info_cell.alignment = LEFT_ALIGNMENT
        info_cell.border = THIN_BORDER

        return start_row + 1, start_col

    num_cols = len(export_df.columns)
    first_col_name = get_first_column_name(export_df)

    title_row = start_row
    header_row = start_row + 1
    body_start_row = start_row + 2

    worksheet.merge_cells(
        start_row=title_row,
        start_column=start_col,
        end_row=title_row,
        end_column=start_col + num_cols - 1,
    )

    title_cell = worksheet.cell(row=title_row, column=start_col, value=table_title)
    title_cell.font = TITLE_FONT
    title_cell.alignment = LEFT_ALIGNMENT
    title_cell.border = THIN_BORDER
    apply_fill_if_present(title_cell, TITLE_FILL)

    worksheet.row_dimensions[title_row].height = DEFAULT_SHEET_TITLE_ROW_HEIGHT
    worksheet.row_dimensions[header_row].height = DEFAULT_HEADER_ROW_HEIGHT

    for offset, column_name in enumerate(export_df.columns):
        current_col = start_col + offset
        header_cell = worksheet.cell(
            row=header_row,
            column=current_col,
            value=str(column_name),
        )
        header_cell.font = HEADER_FONT
        header_cell.alignment = LEFT_ALIGNMENT if offset == 0 else CENTER_ALIGNMENT
        header_cell.border = THIN_BORDER
        apply_fill_if_present(header_cell, get_header_fill(column_name))

    for row_idx in range(len(export_df)):
        excel_row = body_start_row + row_idx
        worksheet.row_dimensions[excel_row].height = DEFAULT_BODY_ROW_HEIGHT

        row_flags = get_row_flags(original_df, row_idx)
        row_flags["first_col_name"] = first_col_name

        for col_idx, column_name in enumerate(export_df.columns):
            excel_col = start_col + col_idx
            raw_value = export_df.iloc[row_idx, col_idx]

            output_value = raw_value
            if is_numeric_column(column_name):
                output_value = scale_value_for_export(column_name, raw_value)

            cell = worksheet.cell(
                row=excel_row,
                column=excel_col,
                value=output_value,
            )

            cell.border = THIN_BORDER
            cell.font = get_body_font(raw_value, row_flags)

            fill_style = get_body_fill(str(column_name), row_flags)
            apply_fill_if_present(cell, fill_style)

            if col_idx == 0:
                cell.alignment = LEFT_ALIGNMENT
            else:
                cell.alignment = RIGHT_ALIGNMENT if is_numeric_column(column_name) else CENTER_ALIGNMENT

            if is_numeric_column(column_name):
                cell.number_format = excel_number_format_for_column(column_name)

    for offset, column_name in enumerate(export_df.columns):
        current_col = start_col + offset
        column_letter = get_column_letter(current_col)
        width = estimate_column_width(export_df[column_name], str(column_name))
        worksheet.column_dimensions[column_letter].width = width

    last_row = body_start_row + len(export_df) - 1
    last_col = start_col + num_cols - 1

    return last_row, last_col

def write_two_tables_side_by_side(
    worksheet,
    left_df: pd.DataFrame,
    right_df: pd.DataFrame,
    left_title: str,
    right_title: str,
    start_row: int,
    start_col: int = 1,
    spacing_columns: int = DEFAULT_TABLE_SPACING_COLUMNS,
) -> tuple[int, int]:
    left_visible_df = sanitize_export_dataframe(left_df)
    left_cols = max(len(left_visible_df.columns), 1)

    left_last_row, left_last_col = write_table_to_worksheet(
        worksheet=worksheet,
        original_df=left_df,
        start_row=start_row,
        start_col=start_col,
        table_title=left_title,
    )

    right_start_col = start_col + left_cols + spacing_columns

    right_last_row, right_last_col = write_table_to_worksheet(
        worksheet=worksheet,
        original_df=right_df,
        start_row=start_row,
        start_col=right_start_col,
        table_title=right_title,
    )

    return max(left_last_row, right_last_row), max(left_last_col, right_last_col)

# ---------------------------------------------------------
# HELPERS DE EXCEL
# ---------------------------------------------------------
def create_excel_writer_buffer():
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine="openpyxl")
    return output, writer

def build_excel_bytes_from_writer(output: BytesIO, writer: pd.ExcelWriter) -> bytes:
    writer.close()
    output.seek(0)
    return output.getvalue()

def ensure_sheet_exists(writer, sheet_name: str):
    safe_sheet_name = sanitize_sheet_name(sheet_name)
    if safe_sheet_name not in writer.book.sheetnames:
        writer.book.create_sheet(title=safe_sheet_name)
    return writer.book[safe_sheet_name]

def remove_default_sheet_if_needed(writer) -> None:
    if "Sheet" in writer.book.sheetnames and len(writer.book.sheetnames) > 1:
        default_sheet = writer.book["Sheet"]
        writer.book.remove(default_sheet)

def get_report_title_from_tables(tables: dict | None, fallback: str | None = None) -> str | None:
    if isinstance(tables, dict):
        return tables.get("report_title") or tables.get("__report_title__") or fallback
    return fallback


# ---------------------------------------------------------
# EXPORTACIÓN BASE MTD / BTS
# ---------------------------------------------------------
def build_base_mtd_excel_bytes(
    client_table_df: pd.DataFrame,
    sku_table_df: pd.DataFrame,
    bts_table_df: pd.DataFrame,
    plan_summary_df: pd.DataFrame | None = None,
    report_title: str | None = None,
    sheet_name: str | None = None,
) -> bytes:
    """
    Construye el Excel individual de Base MTD.

    Incluye únicamente:
    - Comparativo MTD/YTD contra Plan Cliente.
    - Comparativo MTD/YTD contra Plan SKU.
    - Tabla BTS.

    Nota:
    plan_summary_df se conserva como parámetro para no romper las llamadas
    existentes desde app.py, pero ya no se escribe en el Excel.
    """
    output, writer = create_excel_writer_buffer()
    worksheet = ensure_sheet_exists(
        writer,
        sheet_name or getattr(config, "EXPORT_SHEET_BASE_MTD", "Base MTD"),
    )

    current_row = write_global_title(
        worksheet=worksheet,
        report_title=report_title,
        start_row=1,
        start_col=1,
        width=8,
    )

    block_last_row, _ = write_two_tables_side_by_side(
        worksheet=worksheet,
        left_df=client_table_df,
        right_df=sku_table_df,
        left_title=getattr(config, "BASE_MTD_CLIENT_TABLE_TITLE", "Base MTD vs Plan Cliente"),
        right_title=getattr(config, "BASE_MTD_SKU_TABLE_TITLE", "Base MTD vs Plan SKU"),
        start_row=current_row,
    )

    current_row = block_last_row + DEFAULT_BLOCK_SPACING_ROWS

    write_table_to_worksheet(
        worksheet=worksheet,
        original_df=bts_table_df,
        start_row=current_row,
        start_col=1,
        table_title=getattr(config, "BASE_MTD_BTS_TABLE_TITLE", "Back To School (BTS)"),
    )

    remove_default_sheet_if_needed(writer)
    return build_excel_bytes_from_writer(output, writer)


def write_base_mtd_tables_to_workbook(
    worksheet,
    base_mtd_tables: dict,
) -> None:
    """
    Escribe Base MTD dentro del archivo global de reportes.
    """
    current_row = write_global_title(
        worksheet=worksheet,
        report_title=get_report_title_from_tables(base_mtd_tables),
        start_row=1,
        start_col=1,
        width=8,
    )

    block_last_row, _ = write_two_tables_side_by_side(
        worksheet=worksheet,
        left_df=base_mtd_tables.get("client_table"),
        right_df=base_mtd_tables.get("sku_table"),
        left_title=getattr(config, "BASE_MTD_CLIENT_TABLE_TITLE", "Base MTD vs Plan Cliente"),
        right_title=getattr(config, "BASE_MTD_SKU_TABLE_TITLE", "Base MTD vs Plan SKU"),
        start_row=current_row,
    )

    current_row = block_last_row + DEFAULT_BLOCK_SPACING_ROWS

    write_table_to_worksheet(
        worksheet=worksheet,
        original_df=base_mtd_tables.get("bts_table"),
        start_row=current_row,
        start_col=1,
        table_title=getattr(config, "BASE_MTD_BTS_TABLE_TITLE", "Back To School (BTS)"),
    )

# ---------------------------------------------------------
# EXPORTACIÓN REPORTE 1
# ---------------------------------------------------------
def build_report_1_excel_bytes(
    mtd_without_kens_df: pd.DataFrame,
    ytd_without_kens_df: pd.DataFrame,
    report_title: str | None = None,
    sheet_name: str = "Reporte 1",
) -> bytes:
    output, writer = create_excel_writer_buffer()
    worksheet = ensure_sheet_exists(writer, sheet_name)

    current_row = write_global_title(
        worksheet=worksheet,
        report_title=report_title,
        start_row=1,
        start_col=1,
        width=8,
    )

    write_two_tables_side_by_side(
        worksheet=worksheet,
        left_df=mtd_without_kens_df,
        right_df=ytd_without_kens_df,
        left_title="MTD Oficina de ventas",
        right_title="YTD Oficina de ventas",
        start_row=current_row,
    )

    remove_default_sheet_if_needed(writer)
    return build_excel_bytes_from_writer(output, writer)

# ---------------------------------------------------------
# EXPORTACIÓN REPORTE 2 - SEGMENT X REGION
# ---------------------------------------------------------
def build_report_2_segment_excel_bytes(
    mtd_segment_df: pd.DataFrame,
    ytd_segment_df: pd.DataFrame,
    report_title: str | None = None,
    sheet_name: str = "Reporte 2 - Segment",
) -> bytes:
    output, writer = create_excel_writer_buffer()
    worksheet = ensure_sheet_exists(writer, sheet_name)

    current_row = write_global_title(
        worksheet=worksheet,
        report_title=report_title,
        start_row=1,
        start_col=1,
        width=8,
    )

    write_two_tables_side_by_side(
        worksheet=worksheet,
        left_df=mtd_segment_df,
        right_df=ytd_segment_df,
        left_title="MTD Segment x Region",
        right_title="YTD Segment x Region",
        start_row=current_row,
    )

    remove_default_sheet_if_needed(writer)
    return build_excel_bytes_from_writer(output, writer)

# ---------------------------------------------------------
# EXPORTACIÓN REPORTE 2 - CATEGORY
# ---------------------------------------------------------
def build_report_2_category_excel_bytes(
    mtd_category_df: pd.DataFrame,
    ytd_category_df: pd.DataFrame,
    report_title: str | None = None,
    sheet_name: str = "Reporte 2 - Category",
) -> bytes:
    output, writer = create_excel_writer_buffer()
    worksheet = ensure_sheet_exists(writer, sheet_name)

    current_row = write_global_title(
        worksheet=worksheet,
        report_title=report_title,
        start_row=1,
        start_col=1,
        width=9,
    )

    write_two_tables_side_by_side(
        worksheet=worksheet,
        left_df=mtd_category_df,
        right_df=ytd_category_df,
        left_title="MTD Category",
        right_title="YTD Category",
        start_row=current_row,
    )

    remove_default_sheet_if_needed(writer)
    return build_excel_bytes_from_writer(output, writer)

# ---------------------------------------------------------
# EXPORTACIÓN REPORTE 3
# ---------------------------------------------------------
def build_report_3_excel_bytes(
    mtd_channel_df: pd.DataFrame,
    ytd_channel_df: pd.DataFrame,
    report_title: str | None = None,
    sheet_name: str = "Reporte 3",
) -> bytes:
    output, writer = create_excel_writer_buffer()
    worksheet = ensure_sheet_exists(writer, sheet_name)

    current_row = write_global_title(
        worksheet=worksheet,
        report_title=report_title,
        start_row=1,
        start_col=1,
        width=8,
    )

    write_two_tables_side_by_side(
        worksheet=worksheet,
        left_df=mtd_channel_df,
        right_df=ytd_channel_df,
        left_title="MTD Channel",
        right_title="YTD Channel",
        start_row=current_row,
    )

    remove_default_sheet_if_needed(writer)
    return build_excel_bytes_from_writer(output, writer)

# ---------------------------------------------------------
# EXPORTACIÓN REPORTE 4
# ---------------------------------------------------------
def build_report_4_excel_bytes(
    mtd_top_clients_df: pd.DataFrame,
    ytd_top_clients_df: pd.DataFrame,
    report_title: str | None = None,
    sheet_name: str = "Reporte 4",
) -> bytes:
    output, writer = create_excel_writer_buffer()
    worksheet = ensure_sheet_exists(writer, sheet_name)

    mtd_export_df = prepare_report_4_export_dataframe(mtd_top_clients_df)
    ytd_export_df = prepare_report_4_export_dataframe(ytd_top_clients_df)

    current_row = write_global_title(
        worksheet=worksheet,
        report_title=report_title,
        start_row=1,
        start_col=1,
        width=len(REPORT_4_VISIBLE_COLUMNS),
    )

    write_two_tables_side_by_side(
        worksheet=worksheet,
        left_df=mtd_export_df,
        right_df=ytd_export_df,
        left_title="MTD Ranking Clients",
        right_title="YTD Ranking Clients",
        start_row=current_row,
    )

    remove_default_sheet_if_needed(writer)
    return build_excel_bytes_from_writer(output, writer)

# ---------------------------------------------------------
# EXPORTACIÓN GLOBAL
# ---------------------------------------------------------
def build_full_reports_excel_bytes(
    base_mtd_tables: dict | None = None,
    report_1_tables: dict | None = None,
    report_2_segment_tables: dict | None = None,
    report_2_category_tables: dict | None = None,
    report_3_tables: dict | None = None,
    report_4_tables: dict | None = None,
) -> bytes:
    output, writer = create_excel_writer_buffer()
    workbook_created = False

    if base_mtd_tables:
        ws = ensure_sheet_exists(
            writer,
            getattr(config, "EXPORT_SHEET_BASE_MTD", "Base MTD"),
        )

        write_base_mtd_tables_to_workbook(
            worksheet=ws,
            base_mtd_tables=base_mtd_tables,
        )

        workbook_created = True

    if report_1_tables:
        ws = ensure_sheet_exists(writer, "Reporte 1")

        current_row = write_global_title(
            worksheet=ws,
            report_title=get_report_title_from_tables(report_1_tables),
            start_row=1,
            start_col=1,
            width=8,
        )

        write_two_tables_side_by_side(
            worksheet=ws,
            left_df=report_1_tables["mtd_without_kens"],
            right_df=report_1_tables["ytd_without_kens"],
            left_title="MTD Oficina de ventas",
            right_title="YTD Oficina de ventas",
            start_row=current_row,
        )

        workbook_created = True

    if report_2_segment_tables:
        ws = ensure_sheet_exists(writer, "Reporte 2 - Segment")

        current_row = write_global_title(
            worksheet=ws,
            report_title=get_report_title_from_tables(report_2_segment_tables),
            start_row=1,
            start_col=1,
            width=8,
        )

        write_two_tables_side_by_side(
            worksheet=ws,
            left_df=report_2_segment_tables["mtd"],
            right_df=report_2_segment_tables["ytd"],
            left_title="MTD Segment x Region",
            right_title="YTD Segment x Region",
            start_row=current_row,
        )

        workbook_created = True

    if report_2_category_tables:
        ws = ensure_sheet_exists(writer, "Reporte 2 - Category")

        current_row = write_global_title(
            worksheet=ws,
            report_title=get_report_title_from_tables(report_2_category_tables),
            start_row=1,
            start_col=1,
            width=9,
        )

        write_two_tables_side_by_side(
            worksheet=ws,
            left_df=report_2_category_tables["mtd"],
            right_df=report_2_category_tables["ytd"],
            left_title="MTD Category",
            right_title="YTD Category",
            start_row=current_row,
        )

        workbook_created = True

    if report_3_tables:
        ws = ensure_sheet_exists(writer, "Reporte 3")

        current_row = write_global_title(
            worksheet=ws,
            report_title=get_report_title_from_tables(report_3_tables),
            start_row=1,
            start_col=1,
            width=8,
        )

        write_two_tables_side_by_side(
            worksheet=ws,
            left_df=report_3_tables["mtd"],
            right_df=report_3_tables["ytd"],
            left_title="MTD Channel",
            right_title="YTD Channel",
            start_row=current_row,
        )

        workbook_created = True

    if report_4_tables:
        ws = ensure_sheet_exists(writer, "Reporte 4")

        current_row = write_global_title(
            worksheet=ws,
            report_title=get_report_title_from_tables(report_4_tables),
            start_row=1,
            start_col=1,
            width=len(REPORT_4_VISIBLE_COLUMNS),
        )

        write_two_tables_side_by_side(
            worksheet=ws,
            left_df=prepare_report_4_export_dataframe(report_4_tables["mtd"]),
            right_df=prepare_report_4_export_dataframe(report_4_tables["ytd"]),
            left_title="MTD Ranking Clients",
            right_title="YTD Ranking Clients",
            start_row=current_row,
        )

        workbook_created = True

    if not workbook_created:
        ws = ensure_sheet_exists(writer, "Reportes")
        ws.cell(row=1, column=1, value="No hay reportes construidos para exportar.")

    remove_default_sheet_if_needed(writer)
    return build_excel_bytes_from_writer(output, writer)