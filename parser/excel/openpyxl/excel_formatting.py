"""
parser/excel/openpyxl/excel_formatting.py
"""

import random
from openpyxl.styles import Font, PatternFill
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.formatting.rule import FormulaRule


# ─── HELPERS ────────────────────────────────────────────────────────────────


def get_col_idx(worksheet, col_name: str) -> int | None:
    header = [cell.value for cell in worksheet[1]]
    if col_name not in header:
        return None
    return header.index(col_name) + 1


def generate_distinct_colors(n: int) -> list[str]:
    random.seed(42)
    colors = set()
    while len(colors) < n:
        r = lambda: random.randint(50, 200)
        colors.add(f"{r():02X}{r():02X}{r():02X}")
    return list(colors)


# ─── FORMATTING ─────────────────────────────────────────────────────────────


def apply_conditional_formatting(
    worksheet, col_name: str, value_to_color: dict[str, str]
) -> None:
    col_idx = get_col_idx(worksheet, col_name)
    if not col_idx:
        return
    col_letter = worksheet.cell(row=1, column=col_idx).column_letter
    max_row = worksheet.max_row

    for value, color in value_to_color.items():
        formula = f"${col_letter}2:${col_letter}{max_row}"
        rule = FormulaRule(
            formula=[f'${col_letter}2="{value}"'],
            fill=PatternFill(start_color=color, end_color=color, fill_type="solid"),
        )
        worksheet.conditional_formatting.add(
            f"{col_letter}2:{col_letter}{max_row}", rule
        )


def apply_currency_formatting(worksheet, columns: list[str]) -> None:
    for col_name in columns:
        col_idx = get_col_idx(worksheet, col_name)
        if not col_idx:
            continue
        for row in worksheet.iter_rows(min_row=2, min_col=col_idx, max_col=col_idx):
            for cell in row:
                if isinstance(cell.value, (int, float)):
                    cell.number_format = "£#,##0.00"


def apply_bold_headers(worksheet) -> None:
    for cell in worksheet[1]:
        cell.font = Font(bold=True)


def resize_columns(worksheet) -> None:
    for column_cells in worksheet.columns:
        max_len = max(
            len(str(cell.value)) if cell.value else 0 for cell in column_cells
        )
        worksheet.column_dimensions[column_cells[0].column_letter].width = max_len + 2


# ─── DATA VALIDATION / DROPDOWNS ────────────────────────────────────────────


def add_dropdown(
    worksheet, options: list[str], col_name="Category", hidden_sheet_name="Dropdowns"
) -> None:
    from openpyxl.utils import get_column_letter

    col_idx = get_col_idx(worksheet, col_name)
    if not col_idx:
        return
    col_letter = get_column_letter(col_idx)

    wb = worksheet.parent

    # Create or get hidden sheet for dropdown data
    if hidden_sheet_name not in wb.sheetnames:
        hidden_ws = wb.create_sheet(hidden_sheet_name)
        hidden_ws.sheet_state = "hidden"
    else:
        hidden_ws = wb[hidden_sheet_name]

    # Write options to hidden sheet column
    col = len(hidden_ws[1]) + 1  # Next empty column
    for row_idx, option in enumerate(options, start=1):
        hidden_ws.cell(row=row_idx, column=col, value=option)

    col_letter_hidden = get_column_letter(col)
    max_row = len(options)
    range_ref = (
        f"{hidden_sheet_name}!${col_letter_hidden}$1:${col_letter_hidden}${max_row}"
    )

    # Add data validation
    dv = DataValidation(type="list", formula1=f"={range_ref}", allow_blank=True)
    dv.add(f"{col_letter}2:{col_letter}{worksheet.max_row}")
    worksheet.add_data_validation(dv)


# ─── SHEET ORDERING ────────────────────────────────────────────────────────


def order_sheets(workbook, ordered_sheet_names: list[str]) -> None:
    for idx, name in enumerate(ordered_sheet_names):
        if name in workbook.sheetnames:
            workbook.move_sheet(workbook[name], idx)
