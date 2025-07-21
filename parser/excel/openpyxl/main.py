import os
import pandas as pd
from openpyxl import load_workbook, Workbook
from openpyxl.utils.dataframe import dataframe_to_rows
from openpyxl.worksheet.table import Table
from openpyxl.utils import get_column_letter, range_boundaries


from parser.excel.openpyxl.excel_formatting import (
    add_dropdown,
    apply_bold_headers,
    apply_currency_formatting,
    apply_conditional_formatting,
    order_sheets,
    resize_columns,
)

def delete_sheet_in_excel_file(filepath: str, sheet_name: str = "MasterData"):
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"{filepath} does not exist.")

    workbook = load_workbook(filepath)
    if sheet_name in workbook.sheetnames:
        workbook.remove(workbook[sheet_name])
        print(f"Worksheet {sheet_name} removed from {filepath}.")


def update_excel_file(
    df: pd.DataFrame,
    filepath: str,
    category_list: list,
    category_colour_map: dict,
    account_colour_map: dict,
) -> None:
    df["Year"] = df["Date"].dt.strftime("%Y")
    df["Month"] = df["Date"].dt.strftime("%m")
    df["Date"] = df["Date"].dt.date

    sheet_name = "MasterData"
    table_name = "Table1"  # Ensure this is the actual table name in your Excel sheet

    if os.path.exists(filepath):
        workbook = load_workbook(filepath)
        if sheet_name in workbook.sheetnames:
            ws = workbook[sheet_name]
        else:
            ws = workbook.create_sheet(sheet_name)
            ws.append(list(df.columns))  # Add header
    else:
        workbook = Workbook()
        if "Sheet" in workbook.sheetnames:
            workbook.remove(workbook["Sheet"])
        ws = workbook.create_sheet(sheet_name)
        ws.append(list(df.columns))  # Add header

    # Get existing table (if any)
    if table_name in ws.tables:
        table = ws.tables[table_name]
    else:
        table = None
    # Determine starting row
    if table:
        min_col, min_row, max_col, max_row = range_boundaries(table.ref)
        start_row = max_row + 1
    else:
        # Table doesn't exist yet — create header
        start_row = ws.max_row + 1
        min_col = 1
        max_col = len(df.columns)

    # Append new rows
    for row in dataframe_to_rows(df, index=False, header=False):
        if all(cell == "" or cell is None for cell in row):
            continue
        ws.append(row)

    # Update table range (or create one)
    end_row = ws.max_row
    end_col_letter = get_column_letter(max_col)

    if table:
        new_ref = f"A1:{end_col_letter}{end_row}"
        table.ref = new_ref
    else:
        from openpyxl.worksheet.table import Table, TableStyleInfo
        table = Table(displayName=table_name, ref=f"A1:{end_col_letter}{end_row}")
        style = TableStyleInfo(name="TableStyleMedium9", showRowStripes=True)
        table.tableStyleInfo = style
        ws.add_table(table)

    # Reapply formatting
    apply_conditional_formatting(ws, "Category", category_colour_map)
    apply_conditional_formatting(ws, "Account", account_colour_map)
    apply_currency_formatting(ws, ["Amount", "Amount In", "Amount Out"])
    apply_bold_headers(ws)
    resize_columns(ws)
    add_dropdown(ws, category_list)

    workbook.save(filepath)